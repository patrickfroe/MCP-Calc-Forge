from __future__ import annotations

import asyncio
import logging
import os
import time
from collections import defaultdict, deque
import sys

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Mount, Route

from app.mcp.discovery import build_discovery_payload
from app.mcp.server import create_mcp_server
from app.mcp.ui_resources import get_ui_resource_specs


MCP_HTTP_PATH = "/api/v1/mcp"
UI_PREVIEW_PATH = "/ui/preview"
LOGGER = logging.getLogger("app.mcp.discovery_http")
if not LOGGER.handlers:
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


class DiscoveryGetMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Starlette, path: str = MCP_HTTP_PATH) -> None:
        super().__init__(app)
        self._path = path

    async def dispatch(self, request: Request, call_next) -> Response:
        accepts = request.headers.get("accept", "")
        is_discovery_get = (
            request.url.path == self._path
            and request.method == "GET"
            and "text/event-stream" not in accepts
        )
        if is_discovery_get:
            return JSONResponse(build_discovery_payload())

        return await call_next(request)


class MCPAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Starlette, token: str, path: str = MCP_HTTP_PATH) -> None:
        super().__init__(app)
        self._token = token
        self._path = path

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == self._path and request.method == "POST":
            expected = f"Bearer {self._token}"
            provided = request.headers.get("authorization", "")
            if provided != expected:
                return JSONResponse(
                    {"ok": False, "error": {"code": "UNAUTHORIZED", "message": "Missing or invalid bearer token."}},
                    status_code=401,
                )
        return await call_next(request)


class MCPAbuseGuardMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Starlette, max_request_bytes: int, path: str = MCP_HTTP_PATH) -> None:
        super().__init__(app)
        self._max_request_bytes = max_request_bytes
        self._path = path

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == self._path and request.method == "POST":
            content_length = request.headers.get("content-length")
            if content_length and content_length.isdigit() and int(content_length) > self._max_request_bytes:
                return JSONResponse(
                    {"ok": False, "error": {"code": "PAYLOAD_TOO_LARGE", "message": "Request payload too large."}},
                    status_code=413,
                )

            body = await request.body()
            if len(body) > self._max_request_bytes:
                return JSONResponse(
                    {"ok": False, "error": {"code": "PAYLOAD_TOO_LARGE", "message": "Request payload too large."}},
                    status_code=413,
                )
        return await call_next(request)


class MCPRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Starlette,
        max_requests: int,
        window_seconds: int,
        path: str = MCP_HTTP_PATH,
    ) -> None:
        super().__init__(app)
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._path = path
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _client_key(self, request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for", "").strip()
        if forwarded_for:
            return forwarded_for.split(",")[0].strip() or "unknown"
        client = request.client
        if client and client.host:
            return client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == self._path and request.method == "POST":
            key = self._client_key(request)
            now = time.time()
            threshold = now - self._window_seconds
            queue = self._hits[key]

            while queue and queue[0] < threshold:
                queue.popleft()

            if len(queue) >= self._max_requests:
                return JSONResponse(
                    {"ok": False, "error": {"code": "RATE_LIMITED", "message": "Too many requests."}},
                    status_code=429,
                )

            queue.append(now)

        return await call_next(request)


class MCPTimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Starlette, timeout_seconds: float, path: str = MCP_HTTP_PATH) -> None:
        super().__init__(app)
        self._timeout_seconds = timeout_seconds
        self._path = path

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == self._path and request.method == "POST":
            try:
                return await asyncio.wait_for(call_next(request), timeout=self._timeout_seconds)
            except asyncio.TimeoutError:
                return JSONResponse(
                    {"ok": False, "error": {"code": "TIMEOUT", "message": "Request timed out."}},
                    status_code=504,
                )
        return await call_next(request)


class MCPRequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Starlette, path: str = MCP_HTTP_PATH) -> None:
        super().__init__(app)
        self._path = path

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path != self._path:
            return await call_next(request)

        started = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - started) * 1000, 2)
        client_host = request.client.host if request.client and request.client.host else "unknown"
        LOGGER.info(
            "mcp_http_request method=%s path=%s status=%s duration_ms=%s client=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            client_host,
        )
        return response


class MCPOriginValidationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Starlette, allowed_origins: set[str], path: str = MCP_HTTP_PATH) -> None:
        super().__init__(app)
        self._allowed_origins = allowed_origins
        self._path = path

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == self._path and request.method == "POST":
            origin = request.headers.get("origin")
            if origin and origin not in self._allowed_origins:
                return JSONResponse(
                    {"ok": False, "error": {"code": "ORIGIN_NOT_ALLOWED", "message": "Origin is not allowed."}},
                    status_code=403,
                )
        return await call_next(request)


def create_combined_http_app(path: str = MCP_HTTP_PATH) -> Starlette:
    mcp = create_mcp_server()
    mcp_http_app = mcp.http_app(path=path, transport="streamable-http")
    middleware = [Middleware(DiscoveryGetMiddleware, path=path)]

    auth_enabled = _is_truthy(os.getenv("MCP_AUTH_ENABLED", "false"))
    auth_token = os.getenv("MCP_AUTH_TOKEN", "")
    if auth_enabled:
        if not auth_token:
            raise ValueError("MCP_AUTH_ENABLED is true but MCP_AUTH_TOKEN is not set.")
        middleware.append(Middleware(MCPAuthMiddleware, token=auth_token, path=path))

    abuse_guard_enabled = _is_truthy(os.getenv("MCP_ABUSE_GUARD_ENABLED", "false"))
    max_request_bytes = int(os.getenv("MCP_MAX_REQUEST_BYTES", "65536"))
    if abuse_guard_enabled:
        if max_request_bytes <= 0:
            raise ValueError("MCP_MAX_REQUEST_BYTES must be > 0 when MCP_ABUSE_GUARD_ENABLED is true.")
        middleware.append(Middleware(MCPAbuseGuardMiddleware, max_request_bytes=max_request_bytes, path=path))

    rate_limit_enabled = _is_truthy(os.getenv("MCP_RATE_LIMIT_ENABLED", "false"))
    max_requests = int(os.getenv("MCP_RATE_LIMIT_REQUESTS", "60"))
    window_seconds = int(os.getenv("MCP_RATE_LIMIT_WINDOW_SECONDS", "60"))
    if rate_limit_enabled:
        if max_requests <= 0:
            raise ValueError("MCP_RATE_LIMIT_REQUESTS must be > 0 when MCP_RATE_LIMIT_ENABLED is true.")
        if window_seconds <= 0:
            raise ValueError("MCP_RATE_LIMIT_WINDOW_SECONDS must be > 0 when MCP_RATE_LIMIT_ENABLED is true.")
        middleware.append(
            Middleware(
                MCPRateLimitMiddleware,
                max_requests=max_requests,
                window_seconds=window_seconds,
                path=path,
            )
        )

    timeout_enabled = _is_truthy(os.getenv("MCP_TIMEOUT_ENABLED", "false"))
    timeout_seconds = float(os.getenv("MCP_REQUEST_TIMEOUT_SECONDS", "10"))
    if timeout_enabled:
        if timeout_seconds <= 0:
            raise ValueError("MCP_REQUEST_TIMEOUT_SECONDS must be > 0 when MCP_TIMEOUT_ENABLED is true.")
        middleware.append(Middleware(MCPTimeoutMiddleware, timeout_seconds=timeout_seconds, path=path))

    request_logging_enabled = _is_truthy(os.getenv("MCP_REQUEST_LOG_ENABLED", "true"))
    if request_logging_enabled:
        middleware.append(Middleware(MCPRequestLoggingMiddleware, path=path))

    origin_validation_enabled = _is_truthy(os.getenv("MCP_ORIGIN_VALIDATION_ENABLED", "false"))
    raw_allowed_origins = os.getenv("MCP_ALLOWED_ORIGINS", "")
    allowed_origins = {item.strip() for item in raw_allowed_origins.split(",") if item.strip()}
    if origin_validation_enabled:
        if not allowed_origins:
            raise ValueError("MCP_ALLOWED_ORIGINS must be set when MCP_ORIGIN_VALIDATION_ENABLED is true.")
        middleware.append(Middleware(MCPOriginValidationMiddleware, allowed_origins=allowed_origins, path=path))

    ui_preview_html = _build_ui_preview_html()
    app = Starlette(
        routes=[
            Route(UI_PREVIEW_PATH, endpoint=_ui_preview_route(ui_preview_html), methods=["GET"]),
            Mount("/", app=mcp_http_app),
        ],
        middleware=middleware,
        lifespan=mcp_http_app.router.lifespan_context,
    )
    app.state.fastmcp_server = mcp
    app.state.path = path
    return app


def _build_ui_preview_html() -> str:
    for resource in get_ui_resource_specs():
        if resource.uri == "ui://calculations/list":
            return resource.loader()
    raise ValueError("UI resource ui://calculations/list is not registered.")


def _ui_preview_route(ui_preview_html: str):
    async def _endpoint(_: Request) -> Response:
        return HTMLResponse(ui_preview_html)

    return _endpoint


def run_discovery_http_server(host: str = "127.0.0.1", port: int = 8090) -> None:
    import uvicorn

    uvicorn.run(create_combined_http_app(), host=host, port=port)


if __name__ == "__main__":
    run_discovery_http_server()
