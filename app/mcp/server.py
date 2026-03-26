from __future__ import annotations

import logging
import os
import sys

from fastmcp import FastMCP

from app.mcp.tools.evaluate_expression import evaluate_expression_tool
from app.mcp.tools.execute_calculation import execute_calculation_tool
from app.mcp.tools.get_calculation_details import get_calculation_details_tool
from app.mcp.tools.list_calculations import list_calculations_tool


LOGGER = logging.getLogger("app.mcp.server")
if not LOGGER.handlers:
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False


def create_mcp_server() -> FastMCP:
    mcp = FastMCP("MCP Calc Forge")

    @mcp.tool(name="evaluate_expression")
    def evaluate_expression(expression: str) -> dict[str, object]:
        return evaluate_expression_tool(expression=expression)

    @mcp.tool(name="list_calculations")
    def list_calculations() -> dict[str, object]:
        return list_calculations_tool()

    @mcp.tool(name="get_calculation_details")
    def get_calculation_details(calculation_id: str) -> dict[str, object]:
        return get_calculation_details_tool(calculation_id=calculation_id)

    @mcp.tool(name="execute_calculation")
    def execute_calculation(calculation_id: str, inputs: dict[str, object]) -> dict[str, object]:
        return execute_calculation_tool(calculation_id=calculation_id, inputs=inputs)

    return mcp


mcp = create_mcp_server()


if __name__ == "__main__":
    LOGGER.info("Starting MCP server")
    port = int(os.getenv("FASTMCP_PORT", "8080"))
    LOGGER.info("Configured FASTMCP_PORT=%s (stdio transport ignores port)", port)
    mcp.run(transport="stdio")
