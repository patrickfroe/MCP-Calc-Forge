from __future__ import annotations

import json

from starlette.testclient import TestClient

from app.mcp.discovery_http import MCP_HTTP_PATH, create_combined_http_app


def _extract_sse_data_payload(response_text: str) -> dict[str, object]:
    for line in response_text.splitlines():
        if line.startswith("data: "):
            return json.loads(line[len("data: ") :])
    raise AssertionError("No SSE data payload found")


def _initialize_session(client: TestClient) -> str | None:
    response = client.post(
        MCP_HTTP_PATH,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "pytest-app-renderer-client", "version": "1.0"},
            },
        },
        headers={"accept": "application/json, text/event-stream"},
    )
    assert response.status_code == 200
    return response.headers.get("mcp-session-id")


def _post_rpc(
    client: TestClient,
    session_id: str | None,
    request_id: int,
    method: str,
    params: dict[str, object],
) -> dict[str, object]:
    headers = {"accept": "application/json, text/event-stream"}
    if session_id:
        headers["mcp-session-id"] = session_id
    response = client.post(
        MCP_HTTP_PATH,
        json={"jsonrpc": "2.0", "id": request_id, "method": method, "params": params},
        headers=headers,
    )
    assert response.status_code == 200
    payload = _extract_sse_data_payload(response.text)
    assert "result" in payload
    return payload["result"]


def test_app_renderer_contract_tools_resources_and_tool_results_are_coherent() -> None:
    app = create_combined_http_app()

    with TestClient(app) as client:
        session_id = _initialize_session(client)

        tools_result = _post_rpc(client, session_id, 2, "tools/list", {})
        tools_by_name = {tool["name"]: tool for tool in tools_result["tools"]}

        assert tools_by_name["calculate_expression"]["_meta"]["ui"]["resourceUri"] == "ui://calculations/list"
        assert tools_by_name["calculate_expression"]["_meta"]["ui"]["visibility"] == ["model", "app"]
        assert tools_by_name["list_calculations"]["_meta"]["ui"]["resourceUri"] == "ui://calculations/list"
        assert tools_by_name["get_calculation_details"]["_meta"]["ui"]["resourceUri"] == "ui://calculations/list"
        assert tools_by_name["get_calculation_details"]["_meta"]["ui"]["visibility"] == ["app"]
        assert tools_by_name["execute_calculation"]["_meta"]["ui"]["resourceUri"] == "ui://calculations/list"
        assert tools_by_name["execute_calculation"]["_meta"]["ui"]["visibility"] == ["app"]
        assert tools_by_name["ui_get_calculation_preview"]["_meta"]["ui"]["visibility"] == ["app"]

        list_call_result = _post_rpc(
            client,
            session_id,
            3,
            "tools/call",
            {"name": "list_calculations", "arguments": {}},
        )
        list_structured = list_call_result["structuredContent"]["structuredContent"]
        assert isinstance(list_structured["calculations"], list)
        assert list_call_result["content"][0]["type"] == "text"

        details_call_result = _post_rpc(
            client,
            session_id,
            4,
            "tools/call",
            {"name": "get_calculation_details", "arguments": {"calculation_id": "loan_annuity_payment"}},
        )
        details_result = details_call_result["structuredContent"]["result"]
        assert details_result["id"] == "loan_annuity_payment"

        resources_result = _post_rpc(
            client,
            session_id,
            5,
            "resources/read",
            {"uri": "ui://calculations/list"},
        )
        html = resources_result["contents"][0]["text"]
        assert resources_result["contents"][0]["mimeType"] == "text/html;profile=mcp-app"
        assert "Calculations" in html
        assert "tool-call-request" in html
        assert "get_calculation_details" in html
        assert "execute_calculation" in html
        assert "execution-form" in html
