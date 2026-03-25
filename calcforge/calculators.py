"""Calculator registry and high-level calculator workflows for MCP CalcForge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import quote, urlencode

from sympy import Derivative, Integral, MatrixBase, sympify

from calcforge import algebra, arithmetic, geometry, stats


DEFAULT_CALC_URL_BASE = "https://calcforge.app/calculator"
DEFAULT_CAS_GUI_URL = "https://calcforge.app/cas"


@dataclass(frozen=True)
class CalculatorDefinition:
    """Declarative metadata and runtime behavior for a single calculator."""

    calculator_id: str
    category: str
    description: str
    input_schema: dict[str, Any]
    evaluator: Callable[[dict[str, Any]], Any]


def _evaluate_add(inputs: dict[str, Any]) -> Any:
    return arithmetic.add(inputs["a"], inputs["b"])


def _evaluate_subtract(inputs: dict[str, Any]) -> Any:
    return arithmetic.subtract(inputs["a"], inputs["b"])


def _evaluate_multiply(inputs: dict[str, Any]) -> Any:
    return arithmetic.multiply(inputs["a"], inputs["b"])


def _evaluate_divide(inputs: dict[str, Any]) -> Any:
    return arithmetic.divide(inputs["a"], inputs["b"])


def _evaluate_percentage_of(inputs: dict[str, Any]) -> Any:
    return arithmetic.percentage_of(inputs["value"], inputs["percent"])


def _evaluate_circle_area(inputs: dict[str, Any]) -> Any:
    return geometry.circle_area(inputs["radius"])


def _evaluate_solve_quadratic(inputs: dict[str, Any]) -> Any:
    return list(algebra.solve_quadratic(inputs["a"], inputs["b"], inputs["c"]))


def _evaluate_mean(inputs: dict[str, Any]) -> Any:
    return stats.mean(inputs["numbers"])


_CALCULATORS: dict[str, CalculatorDefinition] = {
    "add": CalculatorDefinition(
        calculator_id="add",
        category="arithmetic",
        description="Add two numbers.",
        input_schema={
            "type": "object",
            "required": ["a", "b"],
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
        },
        evaluator=_evaluate_add,
    ),
    "subtract": CalculatorDefinition(
        calculator_id="subtract",
        category="arithmetic",
        description="Subtract b from a.",
        input_schema={
            "type": "object",
            "required": ["a", "b"],
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
        },
        evaluator=_evaluate_subtract,
    ),
    "multiply": CalculatorDefinition(
        calculator_id="multiply",
        category="arithmetic",
        description="Multiply two numbers.",
        input_schema={
            "type": "object",
            "required": ["a", "b"],
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
        },
        evaluator=_evaluate_multiply,
    ),
    "divide": CalculatorDefinition(
        calculator_id="divide",
        category="arithmetic",
        description="Divide a by b.",
        input_schema={
            "type": "object",
            "required": ["a", "b"],
            "properties": {"a": {"type": "number"}, "b": {"type": "number", "not": {"const": 0}}},
        },
        evaluator=_evaluate_divide,
    ),
    "percentage_of": CalculatorDefinition(
        calculator_id="percentage_of",
        category="arithmetic",
        description="Calculate percent percent of value.",
        input_schema={
            "type": "object",
            "required": ["value", "percent"],
            "properties": {"value": {"type": "number"}, "percent": {"type": "number"}},
        },
        evaluator=_evaluate_percentage_of,
    ),
    "circle_area": CalculatorDefinition(
        calculator_id="circle_area",
        category="geometry",
        description="Calculate a circle area from radius.",
        input_schema={
            "type": "object",
            "required": ["radius"],
            "properties": {"radius": {"type": "number", "exclusiveMinimum": 0}},
        },
        evaluator=_evaluate_circle_area,
    ),
    "solve_quadratic": CalculatorDefinition(
        calculator_id="solve_quadratic",
        category="algebra",
        description="Solve a*x**2 + b*x + c = 0.",
        input_schema={
            "type": "object",
            "required": ["a", "b", "c"],
            "properties": {
                "a": {"type": "number", "not": {"const": 0}},
                "b": {"type": "number"},
                "c": {"type": "number"},
            },
        },
        evaluator=_evaluate_solve_quadratic,
    ),
    "mean": CalculatorDefinition(
        calculator_id="mean",
        category="statistics",
        description="Calculate the arithmetic mean.",
        input_schema={
            "type": "object",
            "required": ["numbers"],
            "properties": {
                "numbers": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 1,
                }
            },
        },
        evaluator=_evaluate_mean,
    ),
}


def list_calculators(category: str | None = None) -> list[dict[str, Any]]:
    """List available calculator metadata, optionally filtered by category."""
    calculators = _CALCULATORS.values()
    if category is not None:
        calculators = [calc for calc in calculators if calc.category == category]

    return [
        {
            "calculator_id": calc.calculator_id,
            "category": calc.category,
            "description": calc.description,
        }
        for calc in calculators
    ]


def get_calculator_schema(calculator_id: str) -> dict[str, Any]:
    """Return the input JSON schema for a registered calculator."""
    calculator = _CALCULATORS.get(calculator_id)
    if calculator is None:
        raise ValueError(f"Unknown calculator_id: {calculator_id}")
    return calculator.input_schema


def generate_prefilled_url(calculator_id: str, inputs: dict[str, Any], base_url: str = DEFAULT_CALC_URL_BASE) -> str:
    """Build a prefilled calculator URL for GUI handoff or bookmarking."""
    query_payload = {"calculator": calculator_id, **{key: str(value) for key, value in inputs.items()}}
    return f"{base_url}?{urlencode(query_payload)}"


def calculate(calculator_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
    """Run a registered calculator and return result plus prefilled URL."""
    calculator = _CALCULATORS.get(calculator_id)
    if calculator is None:
        raise ValueError(f"Unknown calculator_id: {calculator_id}")

    result = calculator.evaluator(inputs)
    return {
        "calculator_id": calculator_id,
        "result": result,
        "prefilled_url": generate_prefilled_url(calculator_id, inputs),
    }


def _build_cas_handoff_url(expression: str) -> str:
    return f"{DEFAULT_CAS_GUI_URL}?expr={quote(expression)}"


def calculate_cas(expressions: list[str], precision: int = 15) -> dict[str, Any]:
    """Evaluate CAS expressions in MCP-only numeric mode.

    Expressions with symbols or unsupported advanced features return
    GUI handoff details instead of server-side results.
    """
    outputs: list[dict[str, Any]] = []
    unsupported_types = (Integral, Derivative, MatrixBase)

    for expression in expressions:
        try:
            parsed = sympify(expression)
            if parsed.free_symbols:
                outputs.append(
                    {
                        "expression": expression,
                        "status": "handoff",
                        "reason": "Expression contains symbols; headless mode is numeric-only.",
                        "handoff_url": _build_cas_handoff_url(expression),
                    }
                )
                continue
            if parsed.has(*unsupported_types):
                outputs.append(
                    {
                        "expression": expression,
                        "status": "handoff",
                        "reason": "Expression uses unsupported symbolic features.",
                        "handoff_url": _build_cas_handoff_url(expression),
                    }
                )
                continue

            numeric_result = parsed.evalf(precision)
            outputs.append(
                {
                    "expression": expression,
                    "status": "ok",
                    "result": str(numeric_result),
                }
            )
        except Exception as exc:  # noqa: BLE001 - return handoff for unsupported or invalid expressions.
            outputs.append(
                {
                    "expression": expression,
                    "status": "handoff",
                    "reason": f"Unsupported or invalid expression: {exc}",
                    "handoff_url": _build_cas_handoff_url(expression),
                }
            )

    return {
        "mode": "headless_numeric",
        "results": outputs,
    }


def calculate_cas_headless(expressions: list[str], precision: int = 15) -> dict[str, Any]:
    """Alias of :func:`calculate_cas` for explicit headless naming."""
    return calculate_cas(expressions, precision=precision)
