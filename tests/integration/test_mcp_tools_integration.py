from __future__ import annotations

import asyncio

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.mcp.server import create_mcp_server
from app.mcp.tools.evaluate_expression import evaluate_expression_tool
from app.mcp.tools.execute_calculation import execute_calculation_tool
from app.mcp.tools.get_calculation_details import get_calculation_details_tool
from app.mcp.tools.list_calculations import list_calculations_tool


def test_mcp_server_registers_all_four_tools() -> None:
    server = create_mcp_server()

    tools = asyncio.run(server.list_tools())
    names = {tool.name for tool in tools}

    assert names == {
        "evaluate_expression",
        "list_calculations",
        "get_calculation_details",
        "execute_calculation",
    }


def test_list_calculations_and_get_details_end_to_end() -> None:
    list_payload = list_calculations_tool()
    assert list_payload["ok"] is True
    assert len(list_payload["result"]["calculations"]) >= 3

    details_payload = get_calculation_details_tool("vat_add")
    assert details_payload["ok"] is True
    assert details_payload["result"]["id"] == "vat_add"


def test_execute_calculation_and_expression_end_to_end() -> None:
    calc_payload = execute_calculation_tool("percentage_of", {"part": 20, "whole": 80})
    assert calc_payload["ok"] is True
    assert calc_payload["result"]["percentage"] == 25

    expr_payload = evaluate_expression_tool("(2 + 3) * 5")
    assert expr_payload["ok"] is True
    assert expr_payload["result"]["value"] == 25


def test_tools_return_structured_errors() -> None:
    unknown_payload = get_calculation_details_tool("missing")
    assert unknown_payload["ok"] is False
    assert unknown_payload["error"]["code"] == "UNKNOWN_CALCULATION_ID"

    invalid_expr_payload = evaluate_expression_tool("__import__('os')")
    assert invalid_expr_payload["ok"] is False
    assert invalid_expr_payload["error"]["code"] == "INVALID_EXPRESSION"
