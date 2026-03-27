from __future__ import annotations

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.mcp.server import create_mcp_server
from app.mcp.tools.calculate_expression import calculate_expression_tool
from app.mcp.tools.execute_calculation import execute_calculation_tool
from app.mcp.tools.get_calculation_details import get_calculation_details_tool
from app.mcp.tools.list_calculations import list_calculations_tool


def test_mcp_server_registers_all_four_tools() -> None:
    server = create_mcp_server()

    tools = asyncio.run(server.list_tools())
    names = {tool.name for tool in tools}

    assert names == {
        "calculate_expression",
        "list_calculations",
        "get_calculation_details",
        "execute_calculation",
    }


def test_list_calculations_and_get_details_end_to_end() -> None:
    list_payload = list_calculations_tool()
    assert list_payload["ok"] is True
    assert len(list_payload["result"]["calculations"]) == 14

    details_payload = get_calculation_details_tool("loan_annuity_payment")
    assert details_payload["ok"] is True
    assert details_payload["result"]["id"] == "loan_annuity_payment"
    assert details_payload["result"]["output_type"] == "object"


def test_execute_calculation_and_expression_end_to_end() -> None:
    calc_payload = execute_calculation_tool(
        "currency_conversion_static",
        {"amount": 100, "exchange_rate": 1.08, "source_currency": "EUR", "target_currency": "USD"},
    )
    assert calc_payload["ok"] is True
    assert calc_payload["result"]["converted_amount"] == 108

    expr_payload = calculate_expression_tool("(2 + 3) * 5")
    assert expr_payload["ok"] is True
    assert expr_payload["result"]["value"] == 25


def test_tools_return_structured_errors() -> None:
    unknown_payload = get_calculation_details_tool("missing")
    assert unknown_payload["ok"] is False
    assert unknown_payload["error"]["code"] == "UNKNOWN_CALCULATION_ID"

    invalid_calc_payload = execute_calculation_tool(
        "currency_conversion_static",
        {"amount": 100, "exchange_rate": 1.08, "source_currency": "EUR", "target_currency": "JPY"},
    )
    assert invalid_calc_payload["ok"] is False
    assert invalid_calc_payload["error"]["code"] == "VALIDATION_ERROR"

    invalid_expr_payload = calculate_expression_tool("__import__('os')")
    assert invalid_expr_payload["ok"] is False
    assert invalid_expr_payload["error"]["code"] == "INVALID_EXPRESSION"


def test_execute_calculation_tool_returns_object_shape_for_vat_calculation() -> None:
    payload = execute_calculation_tool("vat_calculation", {"net_amount": 250, "vat_rate": 20})

    assert payload["ok"] is True
    assert payload["result"] == {
        "net_amount": 250.0,
        "vat_rate": 20.0,
        "vat_amount": 50.0,
        "gross_amount": 300.0,
    }


def test_execute_calculation_tool_returns_validation_error_for_average_empty_list() -> None:
    payload = execute_calculation_tool("average", {"values": []})

    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["details"][0]["field"] == "values"
