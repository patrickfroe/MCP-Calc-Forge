from __future__ import annotations

import json
from starlette.testclient import TestClient

from app.mcp.discovery import build_discovery_payload
from app.mcp.discovery_http import MCP_HTTP_PATH, create_combined_http_app


def test_build_discovery_payload_contains_server_metadata_and_tool_schemas() -> None:
    payload = build_discovery_payload()

    assert payload["name"] == "mcp-calc-forge"
    assert payload["version"] == "0.1.0"
    assert payload["description"] == "MCP server for calculation tools"

    tools = payload["tools"]
    assert isinstance(tools, list)

    by_name = {tool["name"]: tool for tool in tools}
    assert {
        "evaluate_expression",
        "list_calculations",
        "get_calculation_details",
        "execute_calculation",
    }.issubset(by_name.keys())

    for tool in tools:
        assert tool["name"]
        assert tool["description"]
        assert isinstance(tool["inputSchema"], dict)

    assert by_name["execute_calculation"]["inputSchema"]["required"] == ["calculation_id", "input"]


def test_discovery_http_endpoint_returns_discovery_json() -> None:
    app = create_combined_http_app()
    with TestClient(app) as client:
        response = client.get(MCP_HTTP_PATH)
        assert response.status_code == 200
        payload = json.loads(response.text)

        assert payload["name"] == "mcp-calc-forge"
        assert len(payload["tools"]) >= 4
        assert all("name" in tool and "description" in tool and "inputSchema" in tool for tool in payload["tools"])


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
    assert '"jsonrpc":"2.0"' in response.text
    assert '"result"' in response.text
