"""MCP server entrypoint for MCP CalcForge.

This module wires the unified calculator registry into FastMCP tools and
exposes an HTTP JSON-RPC endpoint.
"""

from __future__ import annotations

import os
from typing import Any

from fastmcp import FastMCP

from calcforge import calculators

mcp = FastMCP("MCP CalcForge")


@mcp.tool()
def list_calculators(category: str | None = None) -> list[dict[str, Any]]:
    """List registered calculators, optionally filtered by category."""
    return calculators.list_calculators(category)


@mcp.tool()
def _get_calculator_schema(slug: str) -> dict[str, Any]:
    """Get the input schema for a calculator identified by slug."""
    return calculators._get_calculator_schema(slug)


@mcp.tool()
def calculate(slug: str, inputs: dict[str, Any]) -> dict[str, Any]:
    """Run a calculation by slug using validated inputs."""
    return calculators.calculate(slug, inputs)


if __name__ == "__main__":
    port = int(os.getenv("FASTMCP_PORT", "8080"))
    mcp.run(transport="http", host="127.0.0.1", port=port)
