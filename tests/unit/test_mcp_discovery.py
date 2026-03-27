from __future__ import annotations

import json
from threading import Thread
from urllib.request import urlopen

from http.server import ThreadingHTTPServer

from app.mcp.discovery import build_discovery_payload
from app.mcp.discovery_http import DiscoveryRequestHandler


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
        assert tool["description"]
        assert isinstance(tool["inputSchema"], dict)


def test_discovery_http_endpoint_returns_discovery_json() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DiscoveryRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        host, port = server.server_address
        with urlopen(f"http://{host}:{port}/discovery") as response:
            assert response.status == 200
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["name"] == "mcp-calc-forge"
        assert len(payload["tools"]) >= 4
        assert all("inputSchema" in tool for tool in payload["tools"])
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)
