from __future__ import annotations

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount

from app.mcp.discovery import build_discovery_payload
from app.mcp.server import create_mcp_server


MCP_HTTP_PATH = "/api/v1/mcp"


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


def create_combined_http_app(path: str = MCP_HTTP_PATH) -> Starlette:
    mcp = create_mcp_server()
    mcp_http_app = mcp.http_app(path=path, transport="streamable-http")

    app = Starlette(
        routes=[Mount("/", app=mcp_http_app)],
        middleware=[Middleware(DiscoveryGetMiddleware, path=path)],
        lifespan=mcp_http_app.router.lifespan_context,
    )
    app.state.fastmcp_server = mcp
    app.state.path = path
    return app


def run_discovery_http_server(host: str = "127.0.0.1", port: int = 8090) -> None:
    import uvicorn

    uvicorn.run(create_combined_http_app(), host=host, port=port)


if __name__ == "__main__":
    run_discovery_http_server()
