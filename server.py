"""Root entrypoint forwarding to the Python MCP calculation server."""

from __future__ import annotations

from app.mcp.server import mcp


if __name__ == "__main__":
    mcp.run(transport="stdio")
