from __future__ import annotations

import json
from starlette.testclient import TestClient

from app.mcp.discovery import build_discovery_payload
from app.mcp.discovery_http import MCP_HTTP_PATH, UI_PREVIEW_PATH, create_combined_http_app
from app.mcp.tool_specs import TOOL_SPECS
from app.mcp.ui_resources import get_ui_resource_specs


def _extract_sse_data_payload(response_text: str) -> dict[str, object]:
    for line in response_text.splitlines():
        if line.startswith("data: "):
            return json.loads(line[len("data: ") :])
    raise AssertionError("No SSE data payload found")


def _initialize_session(client: TestClient) -> str:
    request_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "pytest-client", "version": "1.0"},
        },
    }
    response = client.post(
        MCP_HTTP_PATH,
        json=request_body,
        headers={"accept": "application/json, text/event-stream"},
    )
    assert response.status_code == 200
    session_id = response.headers.get("mcp-session-id")
    assert session_id
    return session_id


def test_build_discovery_payload_contains_server_metadata_and_tool_schemas() -> None:
    payload = build_discovery_payload()

    assert payload["name"] == "mcp-calc-forge"
    assert payload["version"] == "0.1.0"
    assert payload["description"] == "MCP server for calculation tools"

    tools = payload["tools"]
    assert isinstance(tools, list)

    by_name = {tool["name"]: tool for tool in tools}
    assert {
        "calculate_expression",
        "list_calculations",
        "get_calculation_details",
        "ui_get_calculation_preview",
        "execute_calculation",
    }.issubset(by_name.keys())

    for tool in tools:
        assert tool["name"]
        assert tool["description"]
        assert isinstance(tool["inputSchema"], dict)
        assert isinstance(tool["outputSchema"], dict)

    assert "evaluate_expression" not in by_name
    assert by_name["calculate_expression"]["inputSchema"]["title"] == "CalculateExpressionInput"
    assert by_name["calculate_expression"]["inputSchema"]["properties"]["expression"]["maxLength"] == 500
    assert by_name["calculate_expression"]["meta"]["ui"]["resourceUri"] == "ui://calculations/list"
    assert by_name["calculate_expression"]["_meta"]["ui"]["resourceUri"] == "ui://calculations/list"
    assert by_name["calculate_expression"]["meta"]["ui"]["visibility"] == ["model", "app"]
    assert by_name["execute_calculation"]["inputSchema"]["required"] == ["calculation_id", "input"]
    assert by_name["execute_calculation"]["inputSchema"]["additionalProperties"] is False
    assert by_name["execute_calculation"]["meta"]["ui"]["resourceUri"] == "ui://calculations/list"
    assert by_name["execute_calculation"]["_meta"]["ui"]["resourceUri"] == "ui://calculations/list"
    assert by_name["execute_calculation"]["meta"]["ui"]["visibility"] == ["model", "app"]
    assert by_name["get_calculation_details"]["inputSchema"]["additionalProperties"] is False
    assert by_name["calculate_expression"]["inputSchema"]["additionalProperties"] is False
    assert by_name["list_calculations"]["meta"]["ui"]["resourceUri"] == "ui://calculations/list"
    assert by_name["list_calculations"]["_meta"]["ui"]["resourceUri"] == "ui://calculations/list"
    assert by_name["list_calculations"]["meta"]["ui"]["visibility"] == ["model", "app"]
    assert by_name["get_calculation_details"]["meta"]["ui"]["resourceUri"] == "ui://calculations/list"
    assert by_name["get_calculation_details"]["_meta"]["ui"]["resourceUri"] == "ui://calculations/list"
    assert by_name["get_calculation_details"]["meta"]["ui"]["visibility"] == ["model", "app"]
    assert by_name["ui_get_calculation_preview"]["meta"]["ui"]["resourceUri"] == "ui://calculations/list"
    assert by_name["ui_get_calculation_preview"]["_meta"]["ui"]["resourceUri"] == "ui://calculations/list"
    assert by_name["ui_get_calculation_preview"]["meta"]["ui"]["visibility"] == ["app"]
    assert by_name["list_calculations"]["outputSchema"]["properties"]["result"]["properties"]["calculations"]["items"][
        "required"
    ] == ["id", "name", "description", "llm_usage_hint"]


def test_discovery_http_endpoint_returns_discovery_json() -> None:
    app = create_combined_http_app()
    with TestClient(app) as client:
        response = client.get(MCP_HTTP_PATH)
        assert response.status_code == 200
        payload = json.loads(response.text)

        assert payload["name"] == "mcp-calc-forge"
        assert len(payload["tools"]) >= 4
        assert all(
            "name" in tool and "description" in tool and "inputSchema" in tool and "outputSchema" in tool
            for tool in payload["tools"]
        )
        names = {tool["name"] for tool in payload["tools"]}
        assert "calculate_expression" in names
        assert "evaluate_expression" not in names


def test_ui_preview_route_returns_calculation_list_html() -> None:
    app = create_combined_http_app()
    with TestClient(app) as client:
        response = client.get(UI_PREVIEW_PATH)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    html = response.text
    assert "<h1>Calculations</h1>" in html
    assert "Waiting for tool result" in html
    assert "tool-call-request" in html
    assert "get_calculation_details" in html


def test_mcp_post_requests_are_processed_on_same_endpoint() -> None:
    app = create_combined_http_app()
    request_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "pytest-client", "version": "1.0"},
        },
    }

    with TestClient(app) as client:
        response = client.post(
            MCP_HTTP_PATH,
            json=request_body,
            headers={"accept": "application/json, text/event-stream"},
        )

    assert response.status_code == 200
    payload = _extract_sse_data_payload(response.text)
    assert payload["jsonrpc"] == "2.0"
    assert "result" in payload
    result = payload["result"]
    assert result["protocolVersion"] == "2025-03-26"
    assert "capabilities" in result
    assert "tools" in result["capabilities"]
    assert "resources" in result["capabilities"]
    assert "prompts" in result["capabilities"]


def test_mcp_resources_read_returns_registered_ui_html() -> None:
    app = create_combined_http_app()
    with TestClient(app) as client:
        session_id = _initialize_session(client)
        response = client.post(
            MCP_HTTP_PATH,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "resources/read",
                "params": {"uri": "ui://calculations/list"},
            },
            headers={
                "accept": "application/json, text/event-stream",
                "mcp-session-id": session_id,
            },
        )

    assert response.status_code == 200
    payload = _extract_sse_data_payload(response.text)
    contents = payload["result"]["contents"]
    assert len(contents) == 1
    assert contents[0]["uri"] == "ui://calculations/list"
    assert contents[0]["mimeType"] == "text/html"
    assert "<h1>Calculations</h1>" in contents[0]["text"]
    assert "tool-result" in contents[0]["text"]


def test_mcp_resources_read_unknown_ui_uri_returns_jsonrpc_error() -> None:
    app = create_combined_http_app()
    with TestClient(app) as client:
        session_id = _initialize_session(client)
        response = client.post(
            MCP_HTTP_PATH,
            json={
                "jsonrpc": "2.0",
                "id": 22,
                "method": "resources/read",
                "params": {"uri": "ui://missing/view"},
            },
            headers={
                "accept": "application/json, text/event-stream",
                "mcp-session-id": session_id,
            },
        )

    assert response.status_code == 200
    payload = _extract_sse_data_payload(response.text)
    assert payload["jsonrpc"] == "2.0"
    assert payload["id"] == 22
    assert payload["error"]["code"] == -32002
    assert "Resource not found" in payload["error"]["message"]
    assert "ui://missing/view" in payload["error"]["message"]


def test_each_tool_ui_resource_uri_is_registered_with_matching_ui_html_mimetype() -> None:
    tool_ui_uris = {
        str(spec.meta["ui"]["resourceUri"])
        for spec in TOOL_SPECS
        if isinstance(spec.meta, dict)
        and isinstance(spec.meta.get("ui"), dict)
        and "resourceUri" in spec.meta["ui"]
    }
    registered_by_uri = {resource.uri: resource for resource in get_ui_resource_specs()}

    assert tool_ui_uris
    for uri in tool_ui_uris:
        assert uri in registered_by_uri, f"Tool references missing resource URI: {uri}"
        resource = registered_by_uri[uri]
        assert resource.mime_type == "text/html"
        assert resource.loader().lstrip().lower().startswith("<!doctype html>")


def test_mcp_ui_flow_initialize_tool_call_and_resource_read_is_consistent() -> None:
    app = create_combined_http_app()
    with TestClient(app) as client:
        session_id = _initialize_session(client)
        tools_list = client.post(
            MCP_HTTP_PATH,
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/list",
                "params": {},
            },
            headers={
                "accept": "application/json, text/event-stream",
                "mcp-session-id": session_id,
            },
        )
        tools_call = client.post(
            MCP_HTTP_PATH,
            json={
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "list_calculations", "arguments": {}},
            },
            headers={
                "accept": "application/json, text/event-stream",
                "mcp-session-id": session_id,
            },
        )
        resources_read = client.post(
            MCP_HTTP_PATH,
            json={
                "jsonrpc": "2.0",
                "id": 5,
                "method": "resources/read",
                "params": {"uri": "ui://calculations/list"},
            },
            headers={
                "accept": "application/json, text/event-stream",
                "mcp-session-id": session_id,
            },
        )

    assert tools_list.status_code == 200
    tools_list_payload = _extract_sse_data_payload(tools_list.text)
    by_name = {tool["name"]: tool for tool in tools_list_payload["result"]["tools"]}
    assert by_name["list_calculations"]["_meta"]["ui"]["resourceUri"] == "ui://calculations/list"

    assert tools_call.status_code == 200
    tools_call_payload = _extract_sse_data_payload(tools_call.text)
    tool_result = tools_call_payload["result"]
    structured = tool_result["structuredContent"]["structuredContent"]
    assert "calculations" in structured
    assert isinstance(structured["calculations"], list)

    assert resources_read.status_code == 200
    resources_payload = _extract_sse_data_payload(resources_read.text)
    html = resources_payload["result"]["contents"][0]["text"]
    assert "Waiting for tool result" in html
    assert "tool-call-request" in html


def test_mcp_post_initialize_with_invalid_params_returns_jsonrpc_error() -> None:
    app = create_combined_http_app()
    request_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {},
    }

    with TestClient(app) as client:
        response = client.post(
            MCP_HTTP_PATH,
            json=request_body,
            headers={"accept": "application/json, text/event-stream"},
        )

    assert response.status_code == 200
    payload = _extract_sse_data_payload(response.text)
    assert payload["jsonrpc"] == "2.0"
    assert payload["error"]["code"] == -32602


def test_mcp_post_with_malformed_json_returns_parse_error() -> None:
    app = create_combined_http_app()

    with TestClient(app) as client:
        response = client.post(
            MCP_HTTP_PATH,
            content='{"jsonrpc":',
            headers={
                "content-type": "application/json",
                "accept": "application/json, text/event-stream",
            },
        )

    assert response.status_code == 400
    payload = json.loads(response.text)
    assert payload["jsonrpc"] == "2.0"
    assert payload["error"]["code"] == -32700


def test_mcp_post_requests_work_without_auth_when_auth_disabled(monkeypatch) -> None:
    monkeypatch.delenv("MCP_AUTH_ENABLED", raising=False)
    monkeypatch.delenv("MCP_AUTH_TOKEN", raising=False)
    app = create_combined_http_app()
    request_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "pytest-client", "version": "1.0"},
        },
    }

    with TestClient(app) as client:
        response = client.post(
            MCP_HTTP_PATH,
            json=request_body,
            headers={"accept": "application/json, text/event-stream"},
        )

    assert response.status_code == 200
    assert '"result"' in response.text


def test_mcp_post_requests_require_auth_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("MCP_AUTH_ENABLED", "true")
    monkeypatch.setenv("MCP_AUTH_TOKEN", "secret-token")
    app = create_combined_http_app()
    request_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "pytest-client", "version": "1.0"},
        },
    }

    with TestClient(app) as client:
        unauthorized = client.post(
            MCP_HTTP_PATH,
            json=request_body,
            headers={"accept": "application/json, text/event-stream"},
        )
        authorized = client.post(
            MCP_HTTP_PATH,
            json=request_body,
            headers={
                "accept": "application/json, text/event-stream",
                "authorization": "Bearer secret-token",
            },
        )

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200


def test_create_combined_http_app_fails_when_auth_enabled_without_token(monkeypatch) -> None:
    monkeypatch.setenv("MCP_AUTH_ENABLED", "true")
    monkeypatch.delenv("MCP_AUTH_TOKEN", raising=False)

    try:
        create_combined_http_app()
    except ValueError as error:
        assert "MCP_AUTH_TOKEN" in str(error)
    else:
        raise AssertionError("Expected ValueError when MCP_AUTH_ENABLED=true without MCP_AUTH_TOKEN")


def test_mcp_post_requests_are_rejected_when_abuse_guard_payload_limit_is_exceeded(monkeypatch) -> None:
    monkeypatch.setenv("MCP_ABUSE_GUARD_ENABLED", "true")
    monkeypatch.setenv("MCP_MAX_REQUEST_BYTES", "20")
    monkeypatch.delenv("MCP_RATE_LIMIT_ENABLED", raising=False)
    monkeypatch.delenv("MCP_AUTH_ENABLED", raising=False)
    app = create_combined_http_app()
    request_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "pytest-client", "version": "1.0"},
        },
    }

    with TestClient(app) as client:
        response = client.post(
            MCP_HTTP_PATH,
            json=request_body,
            headers={"accept": "application/json, text/event-stream"},
        )

    assert response.status_code == 413


def test_mcp_post_requests_are_rate_limited_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("MCP_RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("MCP_RATE_LIMIT_REQUESTS", "1")
    monkeypatch.setenv("MCP_RATE_LIMIT_WINDOW_SECONDS", "60")
    monkeypatch.delenv("MCP_ABUSE_GUARD_ENABLED", raising=False)
    monkeypatch.delenv("MCP_AUTH_ENABLED", raising=False)
    app = create_combined_http_app()
    request_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "pytest-client", "version": "1.0"},
        },
    }

    with TestClient(app) as client:
        first = client.post(
            MCP_HTTP_PATH,
            json=request_body,
            headers={"accept": "application/json, text/event-stream"},
        )
        second = client.post(
            MCP_HTTP_PATH,
            json=request_body,
            headers={"accept": "application/json, text/event-stream"},
        )

    assert first.status_code == 200
    assert second.status_code == 429


def test_create_combined_http_app_fails_when_timeout_enabled_with_invalid_seconds(monkeypatch) -> None:
    monkeypatch.setenv("MCP_TIMEOUT_ENABLED", "true")
    monkeypatch.setenv("MCP_REQUEST_TIMEOUT_SECONDS", "0")

    try:
        create_combined_http_app()
    except ValueError as error:
        assert "MCP_REQUEST_TIMEOUT_SECONDS" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError when MCP_TIMEOUT_ENABLED=true and MCP_REQUEST_TIMEOUT_SECONDS <= 0"
        )


def test_mcp_post_requests_work_when_request_logging_is_disabled(monkeypatch) -> None:
    monkeypatch.setenv("MCP_REQUEST_LOG_ENABLED", "false")
    app = create_combined_http_app()
    request_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "pytest-client", "version": "1.0"},
        },
    }

    with TestClient(app) as client:
        response = client.post(
            MCP_HTTP_PATH,
            json=request_body,
            headers={"accept": "application/json, text/event-stream"},
        )

    assert response.status_code == 200


def test_mcp_post_requests_reject_disallowed_origin_when_origin_validation_enabled(monkeypatch) -> None:
    monkeypatch.setenv("MCP_ORIGIN_VALIDATION_ENABLED", "true")
    monkeypatch.setenv("MCP_ALLOWED_ORIGINS", "https://allowed.example")
    app = create_combined_http_app()
    request_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "pytest-client", "version": "1.0"},
        },
    }

    with TestClient(app) as client:
        response = client.post(
            MCP_HTTP_PATH,
            json=request_body,
            headers={
                "accept": "application/json, text/event-stream",
                "origin": "https://blocked.example",
            },
        )

    assert response.status_code == 403


def test_mcp_post_requests_allow_configured_origin_when_origin_validation_enabled(monkeypatch) -> None:
    monkeypatch.setenv("MCP_ORIGIN_VALIDATION_ENABLED", "true")
    monkeypatch.setenv("MCP_ALLOWED_ORIGINS", "https://allowed.example")
    app = create_combined_http_app()
    request_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "pytest-client", "version": "1.0"},
        },
    }

    with TestClient(app) as client:
        response = client.post(
            MCP_HTTP_PATH,
            json=request_body,
            headers={
                "accept": "application/json, text/event-stream",
                "origin": "https://allowed.example",
            },
        )

    assert response.status_code == 200


def test_create_combined_http_app_fails_when_origin_validation_enabled_without_allowlist(monkeypatch) -> None:
    monkeypatch.setenv("MCP_ORIGIN_VALIDATION_ENABLED", "true")
    monkeypatch.delenv("MCP_ALLOWED_ORIGINS", raising=False)

    try:
        create_combined_http_app()
    except ValueError as error:
        assert "MCP_ALLOWED_ORIGINS" in str(error)
    else:
        raise AssertionError("Expected ValueError when origin validation is enabled without allowed origins")
