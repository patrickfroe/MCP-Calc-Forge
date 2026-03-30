from __future__ import annotations

import logging
import os
import sys

from fastmcp import FastMCP

from app.mcp.discovery import SERVER_DESCRIPTION, SERVER_NAME
from app.mcp.tool_specs import TOOL_SPECS
from app.mcp.ui_resources import register_ui_resources


LOGGER = logging.getLogger("app.mcp.server")
if not LOGGER.handlers:
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False


def create_mcp_server() -> FastMCP:
    mcp = FastMCP(SERVER_NAME)

    for spec in TOOL_SPECS:
        mcp.tool(
            spec.handler,
            name=spec.name,
            description=spec.description,
            output_schema=spec.output_schema,
            meta=spec.meta or None,
        )

    register_ui_resources(mcp)

    return mcp


mcp = create_mcp_server()


if __name__ == "__main__":
    LOGGER.info("Starting MCP server")
    port = int(os.getenv("FASTMCP_PORT", "8080"))
    LOGGER.info("Configured FASTMCP_PORT=%s (stdio transport ignores port)", port)
    LOGGER.info("Server description: %s", SERVER_DESCRIPTION)
    mcp.run(transport="stdio")
