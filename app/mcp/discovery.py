from __future__ import annotations

from app import __version__
from app.mcp.tool_specs import TOOL_SPECS

SERVER_NAME = "mcp-calc-forge"
SERVER_DESCRIPTION = "MCP server for calculation tools"


def build_discovery_payload() -> dict[str, object]:
    return {
        "name": SERVER_NAME,
        "version": __version__,
        "description": SERVER_DESCRIPTION,
        "tools": [
            {
                "name": spec.name,
                "description": spec.description,
                "inputSchema": spec.input_schema,
            }
            for spec in TOOL_SPECS
        ],
    }
