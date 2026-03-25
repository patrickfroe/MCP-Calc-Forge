"""Calculator registry and high-level calculator workflows for MCP CalcForge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import quote, urlencode

DEFAULT_CALC_URL_BASE = "https://calcforge.app/calculator"
DEFAULT_CAS_GUI_URL = "https://calcforge.app/cas"


@dataclass(frozen=True)
class CalculatorDefinition:
    """Declarative metadata and runtime behavior for a single calculator."""

    slug: str
    name: str
    category: str
    description: str
    route: str
    type: str
    schema: dict[str, dict[str, Any]]
    evaluator: Callable[[dict[str, Any]], Any]


def _evaluate_add(inputs: dict[str, Any]) -> Any:
    from calcforge import arithmetic

    return arithmetic.add(inputs["a"], inputs["b"])


def _evaluate_subtract(inputs: dict[str, Any]) -> Any:
    from calcforge import arithmetic

    return arithmetic.subtract(inputs["a"], inputs["b"])


def _evaluate_multiply(inputs: dict[str, Any]) -> Any:
    from calcforge import arithmetic

    return arithmetic.multiply(inputs["a"], inputs["b"])


def _evaluate_divide(inputs: dict[str, Any]) -> Any:
    from calcforge import arithmetic

    return arithmetic.divide(inputs["a"], inputs["b"])


def _evaluate_percentage_of(inputs: dict[str, Any]) -> Any:
    from calcforge import arithmetic

    return arithmetic.percentage_of(inputs["value"], inputs["percent"])


def _evaluate_circle_area(inputs: dict[str, Any]) -> Any:
    from calcforge import geometry

    return geometry.circle_area(inputs["radius"])


def _evaluate_solve_quadratic(inputs: dict[str, Any]) -> Any:
    from calcforge import algebra

    return list(algebra.solve_quadratic(inputs["a"], inputs["b"], inputs["c"]))


def _evaluate_mean(inputs: dict[str, Any]) -> Any:
    from calcforge import stats

    return stats.mean(inputs["numbers"])


_CALCULATORS: dict[str, CalculatorDefinition] = {
    "add": CalculatorDefinition(
        slug="add",
        name="Addition Calculator",
        category="arithmetic",
        description="Add two numbers.",
        route="/arithmetic/add",
        type="form",
        schema={
            "a": {"type": "number", "label": "A", "required": True},
            "b": {"type": "number", "label": "B", "required": True},
        },
        evaluator=_evaluate_add,
    ),
    "subtract": CalculatorDefinition(
        slug="subtract",
        name="Subtraction Calculator",
        category="arithmetic",
        description="Subtract b from a.",
        route="/arithmetic/subtract",
        type="form",
        schema={
            "a": {"type": "number", "label": "A", "required": True},
            "b": {"type": "number", "label": "B", "required": True},
        },
        evaluator=_evaluate_subtract,
    ),
    "multiply": CalculatorDefinition(
        slug="multiply",
        name="Multiplication Calculator",
        category="arithmetic",
        description="Multiply two numbers.",
        route="/arithmetic/multiply",
        type="form",
        schema={
            "a": {"type": "number", "label": "A", "required": True},
            "b": {"type": "number", "label": "B", "required": True},
        },
        evaluator=_evaluate_multiply,
    ),
    "divide": CalculatorDefinition(
        slug="divide",
        name="Division Calculator",
        category="arithmetic",
        description="Divide a by b.",
        route="/arithmetic/divide",
        type="form",
        schema={
            "a": {"type": "number", "label": "A", "required": True},
            "b": {
                "type": "number",
                "label": "B",
                "required": True,
                "not": {"const": 0},
            },
        },
        evaluator=_evaluate_divide,
    ),
    "percentage_of": CalculatorDefinition(
        slug="percentage_of",
        name="Percentage Calculator",
        category="arithmetic",
        description="Calculate percent percent of value.",
        route="/arithmetic/percentage",
        type="form",
        schema={
            "value": {"type": "number", "label": "Value", "required": True},
            "percent": {"type": "number", "label": "Percent", "required": True},
        },
        evaluator=_evaluate_percentage_of,
    ),
    "circle_area": CalculatorDefinition(
        slug="circle_area",
        name="Circle Area Calculator",
        category="geometry",
        description="Calculate a circle area from radius.",
        route="/geometry/circle-area",
        type="form",
        schema={
            "radius": {
                "type": "number",
                "label": "Radius",
                "required": True,
                "exclusiveMinimum": 0,
            }
        },
        evaluator=_evaluate_circle_area,
    ),
    "solve_quadratic": CalculatorDefinition(
        slug="solve_quadratic",
        name="Quadratic Equation Calculator",
        category="algebra",
        description="Solve a*x**2 + b*x + c = 0.",
        route="/algebra/solve-quadratic",
        type="form",
        schema={
            "a": {"type": "number", "label": "A", "required": True, "not": {"const": 0}},
            "b": {"type": "number", "label": "B", "required": True},
            "c": {"type": "number", "label": "C", "required": True},
        },
        evaluator=_evaluate_solve_quadratic,
    ),
    "mean": CalculatorDefinition(
        slug="mean",
        name="Mean Calculator",
        category="statistics",
        description="Calculate the arithmetic mean.",
        route="/statistics/mean",
        type="form",
        schema={
            "numbers": {
                "type": "array",
                "label": "Numbers",
                "required": True,
                "items": {"type": "number"},
                "minItems": 1,
            }
        },
        evaluator=_evaluate_mean,
    ),
}


def _metadata(calculator: CalculatorDefinition) -> dict[str, Any]:
    return {
        "slug": calculator.slug,
        "name": calculator.name,
        "category": calculator.category,
        "description": calculator.description,
        "route": calculator.route,
        "type": calculator.type,
    }


def _get_calculator(slug: str) -> CalculatorDefinition:
    calculator = _CALCULATORS.get(slug)
    if calculator is None:
        raise ValueError(f"Unknown calculator slug: {slug}")
    return calculator


def list_calculators(category: str | None = None) -> list[dict[str, Any]]:
    """List available calculator metadata, optionally filtered by category."""
    calculators = _CALCULATORS.values()
    if category is not None:
        calculators = [calc for calc in calculators if calc.category == category]

    return [_metadata(calc) for calc in calculators]


def _get_calculator_schema(slug: str) -> dict[str, Any]:
    """Return the input schema wrapper for a registered calculator slug."""
    calculator = _get_calculator(slug)
    return {"calculator": slug, "schema": calculator.schema}


def get_calculator_schema(calculator_id: str) -> dict[str, Any]:
    """Backward-compatible alias for schema retrieval."""
    return _get_calculator_schema(calculator_id)


def _validate_scalar_type(field_name: str, expected_type: str, value: Any) -> None:
    if expected_type == "number" and not isinstance(value, (int, float)):
        raise ValueError(f"Invalid input type for '{field_name}': expected number")
    if expected_type == "string" and not isinstance(value, str):
        raise ValueError(f"Invalid input type for '{field_name}': expected string")


def _validate_inputs(calculator: CalculatorDefinition, inputs: dict[str, Any]) -> None:
    if not isinstance(inputs, dict):
        raise ValueError("Invalid input type for 'inputs': expected object")

    for field_name, field_schema in calculator.schema.items():
        required = field_schema.get("required", False)
        if required and field_name not in inputs:
            raise ValueError(f"Missing required input: {field_name}")
        if field_name not in inputs:
            continue

        value = inputs[field_name]
        expected_type = field_schema.get("type")

        if expected_type == "array":
            if not isinstance(value, list):
                raise ValueError(f"Invalid input type for '{field_name}': expected array")
            min_items = field_schema.get("minItems")
            if isinstance(min_items, int) and len(value) < min_items:
                raise ValueError(f"Invalid input for '{field_name}': requires at least {min_items} items")
            item_type = field_schema.get("items", {}).get("type")
            if item_type == "number" and any(not isinstance(item, (int, float)) for item in value):
                raise ValueError(f"Invalid input type for '{field_name}': expected array of numbers")
            continue

        if expected_type in {"number", "string"}:
            _validate_scalar_type(field_name, expected_type, value)


def generate_prefilled_url(slug: str, inputs: dict[str, Any], base_url: str = DEFAULT_CALC_URL_BASE) -> str:
    """Build a prefilled calculator URL for GUI handoff or bookmarking."""
    query_payload = {"calculator": slug, **{key: str(value) for key, value in inputs.items()}}
    return f"{base_url}?{urlencode(query_payload)}"


def calculate(slug: str, inputs: dict[str, Any]) -> dict[str, Any]:
    """Run a registered calculator and return a structured result payload."""
    calculator = _get_calculator(slug)
    _validate_inputs(calculator, inputs)

    result = calculator.evaluator(inputs)
    return {
        "calculator": slug,
        "result": result,
        "prefilled_url": generate_prefilled_url(slug, inputs),
    }


def _build_cas_handoff_url(expression: str) -> str:
    return f"{DEFAULT_CAS_GUI_URL}?expr={quote(expression)}"


def calculate_cas(expressions: list[str], precision: int = 15) -> dict[str, Any]:
    """Evaluate CAS expressions in MCP-only numeric mode.

    Expressions with symbols or unsupported advanced features return
    GUI handoff details instead of server-side results.
    """
    outputs: list[dict[str, Any]] = []
    from sympy import Derivative, Integral, MatrixBase, sympify

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
