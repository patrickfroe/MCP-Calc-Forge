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
from app.mcp.tools.ui_get_calculation_preview import ui_get_calculation_preview_tool


def test_mcp_server_registers_all_four_tools() -> None:
    server = create_mcp_server()

    tools = asyncio.run(server.list_tools())
    resources = asyncio.run(server.list_resources())
    names = {tool.name for tool in tools}
    by_name = {tool.name: tool for tool in tools}
    resources_by_uri = {str(resource.uri): resource for resource in resources}

    assert names == {
        "calculate_expression",
        "list_calculations",
        "get_calculation_details",
        "ui_get_calculation_preview",
        "execute_calculation",
    }
    assert by_name["list_calculations"].meta == {
        "_meta": {"ui": {"resourceUri": "ui://calculations/list", "visibility": ["model", "app"]}}
    }
    assert by_name["get_calculation_details"].meta == {
        "_meta": {"ui": {"resourceUri": "ui://calculations/list", "visibility": ["model", "app"]}}
    }
    assert by_name["ui_get_calculation_preview"].meta == {
        "_meta": {"ui": {"resourceUri": "ui://calculations/list", "visibility": ["app"]}}
    }
    assert by_name["execute_calculation"].output_schema["properties"]["calculation_id"]["type"] == "string"
    assert "ui://calculations/list" in resources_by_uri
    resource_ui_meta = resources_by_uri["ui://calculations/list"].meta["_meta"]["ui"]
    assert resource_ui_meta["csp"] == {"connectDomains": [], "resourceDomains": []}
    assert resource_ui_meta["displayModes"] == ["inline", "fullscreen"]
    assert resource_ui_meta["theming"] == {"supportsHostTheme": True}


def test_list_calculations_and_get_details_end_to_end() -> None:
    list_payload = list_calculations_tool()
    assert list_payload["ok"] is True
    assert len(list_payload["result"]["calculations"]) == 14
    assert list_payload["structuredContent"] == list_payload["result"]
    assert list_payload["content"][0]["type"] == "text"
    assert "calculations available" in list_payload["content"][0]["text"]

    details_payload = get_calculation_details_tool("loan_annuity_payment")
    assert details_payload["ok"] is True
    assert details_payload["result"]["id"] == "loan_annuity_payment"
    assert details_payload["result"]["output_type"] == "object"


def test_list_calculations_progressive_enhancement_keeps_legacy_result_contract() -> None:
    payload = list_calculations_tool()
    legacy_result = payload["result"]

    assert "calculations" in legacy_result
    assert isinstance(legacy_result["calculations"], list)
    first = legacy_result["calculations"][0]
    assert {"id", "name", "description", "llm_usage_hint"}.issubset(first.keys())


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


def test_ui_get_calculation_preview_app_only_helper() -> None:
    payload = ui_get_calculation_preview_tool("loan_annuity_payment")
    assert payload["ok"] is True
    assert payload["result"]["id"] == "loan_annuity_payment"
    assert payload["structuredContent"]["id"] == "loan_annuity_payment"
    assert payload["content"][0]["type"] == "text"


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
