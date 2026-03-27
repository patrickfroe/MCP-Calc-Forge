from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.mcp.tools.evaluate_expression import evaluate_expression_tool
from app.mcp.tools.execute_calculation import execute_calculation_tool
from app.mcp.tools.get_calculation_details import get_calculation_details_tool
from app.mcp.tools.list_calculations import list_calculations_tool

ToolHandler = Callable[..., dict[str, object]]


@dataclass(frozen=True)
class MCPToolSpec:
    name: str
    description: str
    input_schema: dict[str, object]
    handler: ToolHandler


def evaluate_expression_handler(expression: str) -> dict[str, object]:
    return evaluate_expression_tool(expression=expression)


def list_calculations_handler() -> dict[str, object]:
    return list_calculations_tool()


def get_calculation_details_handler(calculation_id: str) -> dict[str, object]:
    return get_calculation_details_tool(calculation_id=calculation_id)


def execute_calculation_handler(calculation_id: str, inputs: dict[str, object]) -> dict[str, object]:
    return execute_calculation_tool(calculation_id=calculation_id, inputs=inputs)


TOOL_SPECS: tuple[MCPToolSpec, ...] = (
    MCPToolSpec(
        name="evaluate_expression",
        description="Evaluate a mathematical expression safely",
        input_schema={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate",
                }
            },
            "required": ["expression"],
        },
        handler=evaluate_expression_handler,
    ),
    MCPToolSpec(
        name="list_calculations",
        description="List all available named calculations",
        input_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        handler=list_calculations_handler,
    ),
    MCPToolSpec(
        name="get_calculation_details",
        description="Get metadata and input requirements for a named calculation",
        input_schema={
            "type": "object",
            "properties": {
                "calculation_id": {
                    "type": "string",
                    "description": "Unique id of the registered calculation",
                }
            },
            "required": ["calculation_id"],
        },
        handler=get_calculation_details_handler,
    ),
    MCPToolSpec(
        name="execute_calculation",
        description="Execute a named calculation with validated inputs",
        input_schema={
            "type": "object",
            "properties": {
                "calculation_id": {
                    "type": "string",
                    "description": "Unique id of the registered calculation",
                },
                "inputs": {
                    "type": "object",
                    "description": "Input payload expected by the selected calculation",
                },
            },
            "required": ["calculation_id", "inputs"],
        },
        handler=execute_calculation_handler,
    ),
)
