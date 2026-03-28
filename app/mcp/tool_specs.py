from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.mcp.tools.calculate_expression import calculate_expression_tool
from app.mcp.tools.execute_calculation import execute_calculation_tool
from app.mcp.tools.get_calculation_details import get_calculation_details_tool
from app.mcp.tools.list_calculations import list_calculations_tool

ToolHandler = Callable[..., dict[str, object]]


@dataclass(frozen=True)
class MCPToolSpec:
    name: str
    description: str
    input_schema: dict[str, object]
    output_schema: dict[str, object]
    handler: ToolHandler


def calculate_expression_handler(expression: str) -> dict[str, object]:
    return calculate_expression_tool(expression=expression)


def list_calculations_handler() -> dict[str, object]:
    return list_calculations_tool()


def get_calculation_details_handler(calculation_id: str) -> dict[str, object]:
    return get_calculation_details_tool(calculation_id=calculation_id)


def execute_calculation_handler(calculation_id: str, input: dict[str, object]) -> dict[str, object]:
    return execute_calculation_tool(calculation_id=calculation_id, inputs=input)


TOOL_SPECS: tuple[MCPToolSpec, ...] = (
    MCPToolSpec(
        name="calculate_expression",
        description=(
            "Safely evaluate arithmetic expressions with numbers, parentheses and operators +, -, *, /. "
            "No names or function calls are allowed."
        ),
        input_schema={
            "type": "object",
            "title": "CalculateExpressionInput",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Expression string using numbers, parentheses and + - * / operators",
                    "minLength": 1,
                    "maxLength": 500,
                }
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "title": "CalculateExpressionOutput",
            "properties": {
                "ok": {"type": "boolean"},
                "result": {
                    "type": "object",
                    "properties": {"value": {"type": "number"}},
                    "required": ["value"],
                    "additionalProperties": False,
                },
                "error": {"type": "object"},
            },
            "required": ["ok"],
            "additionalProperties": True,
        },
        handler=calculate_expression_handler,
    ),
    MCPToolSpec(
        name="list_calculations",
        description="List all available named calculations with IDs, descriptions and LLM usage hints.",
        input_schema={
            "type": "object",
            "title": "ListCalculationsInput",
            "properties": {},
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "title": "ListCalculationsOutput",
            "properties": {
                "ok": {"type": "boolean"},
                "result": {
                    "type": "object",
                    "properties": {
                        "calculations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "llm_usage_hint": {"type": "string"},
                                },
                                "required": ["id", "name", "description", "llm_usage_hint"],
                                "additionalProperties": False,
                            },
                        }
                    },
                    "required": ["calculations"],
                    "additionalProperties": False,
                },
                "error": {"type": "object"},
            },
            "required": ["ok"],
            "additionalProperties": True,
        },
        handler=list_calculations_handler,
    ),
    MCPToolSpec(
        name="get_calculation_details",
        description=(
            "Get metadata, input field requirements and examples for a specific calculation by calculation_id."
        ),
        input_schema={
            "type": "object",
            "title": "GetCalculationDetailsInput",
            "properties": {
                "calculation_id": {
                    "type": "string",
                    "description": "Unique identifier of the calculation",
                    "minLength": 1,
                }
            },
            "required": ["calculation_id"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "title": "GetCalculationDetailsOutput",
            "properties": {
                "ok": {"type": "boolean"},
                "result": {"type": "object"},
                "error": {"type": "object"},
            },
            "required": ["ok"],
            "additionalProperties": True,
        },
        handler=get_calculation_details_handler,
    ),
    MCPToolSpec(
        name="execute_calculation",
        description=(
            "Execute a named calculation with structured input values. "
            "Use get_calculation_details first to discover required fields and constraints."
        ),
        input_schema={
            "type": "object",
            "title": "ExecuteCalculationInput",
            "properties": {
                "calculation_id": {
                    "type": "string",
                    "description": "Unique identifier of the calculation",
                    "minLength": 1,
                },
                "input": {
                    "type": "object",
                    "description": "Structured input values for the selected calculation",
                },
            },
            "required": ["calculation_id", "input"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "title": "ExecuteCalculationOutput",
            "properties": {
                "ok": {"type": "boolean"},
                "calculation_id": {"type": "string"},
                "result": {},
                "error": {"type": "object"},
            },
            "required": ["ok"],
            "additionalProperties": True,
        },
        handler=execute_calculation_handler,
    ),
)
