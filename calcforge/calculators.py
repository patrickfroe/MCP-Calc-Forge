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


def _error_response(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


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


def _evaluate_to_fraction(inputs: dict[str, Any]) -> Any:
    from calcforge import arithmetic

    return str(arithmetic.to_fraction(inputs["value"]))


def _evaluate_circle_area(inputs: dict[str, Any]) -> Any:
    from calcforge import geometry

    return geometry.circle_area(inputs["radius"])


def _evaluate_circle_circumference(inputs: dict[str, Any]) -> Any:
    from calcforge import geometry

    return geometry.circle_circumference(inputs["radius"])


def _evaluate_rectangle_area(inputs: dict[str, Any]) -> Any:
    from calcforge import geometry

    return geometry.rectangle_area(inputs["a"], inputs["b"])


def _evaluate_rectangle_perimeter(inputs: dict[str, Any]) -> Any:
    from calcforge import geometry

    return geometry.rectangle_perimeter(inputs["a"], inputs["b"])


def _evaluate_triangle_area(inputs: dict[str, Any]) -> Any:
    from calcforge import geometry

    return geometry.triangle_area(inputs["base"], inputs["height"])


def _evaluate_sphere_volume(inputs: dict[str, Any]) -> Any:
    from calcforge import geometry

    return geometry.sphere_volume(inputs["radius"])


def _evaluate_cylinder_volume(inputs: dict[str, Any]) -> Any:
    from calcforge import geometry

    return geometry.cylinder_volume(inputs["radius"], inputs["height"])


def _evaluate_cone_volume(inputs: dict[str, Any]) -> Any:
    from calcforge import geometry

    return geometry.cone_volume(inputs["radius"], inputs["height"])


def _evaluate_pyramid_volume(inputs: dict[str, Any]) -> Any:
    from calcforge import geometry

    return geometry.pyramid_volume(inputs["base_area"], inputs["height"])


def _evaluate_solve_quadratic(inputs: dict[str, Any]) -> Any:
    from calcforge import algebra

    return list(algebra.solve_quadratic(inputs["a"], inputs["b"], inputs["c"]))


def _evaluate_solve_linear_system(inputs: dict[str, Any]) -> Any:
    from calcforge import algebra

    return algebra.solve_linear_system(inputs["equations"], inputs["variables"])


def _evaluate_factor_polynomial(inputs: dict[str, Any]) -> Any:
    from calcforge import algebra

    return algebra.factor_polynomial(inputs["expr"])


def _evaluate_find_roots(inputs: dict[str, Any]) -> Any:
    from calcforge import algebra

    return algebra.find_roots(inputs["expr"])


def _evaluate_mean(inputs: dict[str, Any]) -> Any:
    from calcforge import stats

    return stats.mean(inputs["numbers"])


def _evaluate_std_dev(inputs: dict[str, Any]) -> Any:
    from calcforge import stats

    return stats.std_dev(inputs["numbers"])


def _evaluate_gcd(inputs: dict[str, Any]) -> Any:
    from calcforge import stats

    return stats.gcd(inputs["a"], inputs["b"])


def _evaluate_lcm(inputs: dict[str, Any]) -> Any:
    from calcforge import stats

    return stats.lcm(inputs["a"], inputs["b"])


def _evaluate_prime_factors(inputs: dict[str, Any]) -> Any:
    from calcforge import stats

    return stats.prime_factors(inputs["n"])


def _evaluate_log_base(inputs: dict[str, Any]) -> Any:
    from calcforge import utils

    return utils.log_base(inputs["x"], inputs["base"])


def _evaluate_power(inputs: dict[str, Any]) -> Any:
    from calcforge import utils

    return utils.power(inputs["base"], inputs["exponent"])


def _evaluate_to_scientific_notation(inputs: dict[str, Any]) -> Any:
    from calcforge import utils

    return utils.to_scientific_notation(inputs["x"], inputs.get("precision", 3))


def _evaluate_to_binary(inputs: dict[str, Any]) -> Any:
    from calcforge import utils

    return utils.to_binary(inputs["n"])


def _evaluate_from_binary(inputs: dict[str, Any]) -> Any:
    from calcforge import utils

    return utils.from_binary(inputs["bin_str"])


def _shared_number_ab_schema() -> dict[str, dict[str, Any]]:
    return {
        "a": {"type": "number", "label": "A", "required": True},
        "b": {"type": "number", "label": "B", "required": True},
    }


_CALCULATORS: dict[str, CalculatorDefinition] = {
    "add": CalculatorDefinition("add", "Addition Calculator", "arithmetic", "Add two numbers.", "/arithmetic/add", "form", _shared_number_ab_schema(), _evaluate_add),
    "subtract": CalculatorDefinition("subtract", "Subtraction Calculator", "arithmetic", "Subtract b from a.", "/arithmetic/subtract", "form", _shared_number_ab_schema(), _evaluate_subtract),
    "multiply": CalculatorDefinition("multiply", "Multiplication Calculator", "arithmetic", "Multiply two numbers.", "/arithmetic/multiply", "form", _shared_number_ab_schema(), _evaluate_multiply),
    "divide": CalculatorDefinition(
        "divide",
        "Division Calculator",
        "arithmetic",
        "Divide a by b.",
        "/arithmetic/divide",
        "form",
        {
            "a": {"type": "number", "label": "A", "required": True},
            "b": {"type": "number", "label": "B", "required": True, "not": {"const": 0}},
        },
        _evaluate_divide,
    ),
    "percentage_of": CalculatorDefinition(
        "percentage_of",
        "Percentage Calculator",
        "arithmetic",
        "Calculate percent percent of value.",
        "/arithmetic/percentage",
        "form",
        {
            "value": {"type": "number", "label": "Value", "required": True},
            "percent": {"type": "number", "label": "Percent", "required": True},
        },
        _evaluate_percentage_of,
    ),
    "to_fraction": CalculatorDefinition(
        "to_fraction",
        "Fraction Converter",
        "arithmetic",
        "Convert a number to reduced fraction representation.",
        "/arithmetic/to-fraction",
        "form",
        {"value": {"type": "number", "label": "Value", "required": True}},
        _evaluate_to_fraction,
    ),
    "circle_area": CalculatorDefinition(
        "circle_area",
        "Circle Area Calculator",
        "geometry",
        "Calculate a circle area from radius.",
        "/geometry/circle-area",
        "form",
        {"radius": {"type": "number", "label": "Radius", "required": True, "exclusiveMinimum": 0}},
        _evaluate_circle_area,
    ),
    "circle_circumference": CalculatorDefinition(
        "circle_circumference",
        "Circle Circumference Calculator",
        "geometry",
        "Calculate a circle circumference from radius.",
        "/geometry/circle-circumference",
        "form",
        {"radius": {"type": "number", "label": "Radius", "required": True, "exclusiveMinimum": 0}},
        _evaluate_circle_circumference,
    ),
    "rectangle_area": CalculatorDefinition(
        "rectangle_area",
        "Rectangle Area Calculator",
        "geometry",
        "Calculate the area of a rectangle.",
        "/geometry/rectangle-area",
        "form",
        _shared_number_ab_schema(),
        _evaluate_rectangle_area,
    ),
    "rectangle_perimeter": CalculatorDefinition(
        "rectangle_perimeter",
        "Rectangle Perimeter Calculator",
        "geometry",
        "Calculate the perimeter of a rectangle.",
        "/geometry/rectangle-perimeter",
        "form",
        _shared_number_ab_schema(),
        _evaluate_rectangle_perimeter,
    ),
    "triangle_area": CalculatorDefinition(
        "triangle_area",
        "Triangle Area Calculator",
        "geometry",
        "Calculate the area of a triangle.",
        "/geometry/triangle-area",
        "form",
        {
            "base": {"type": "number", "label": "Base", "required": True},
            "height": {"type": "number", "label": "Height", "required": True},
        },
        _evaluate_triangle_area,
    ),
    "sphere_volume": CalculatorDefinition(
        "sphere_volume",
        "Sphere Volume Calculator",
        "geometry",
        "Calculate the volume of a sphere.",
        "/geometry/sphere-volume",
        "form",
        {"radius": {"type": "number", "label": "Radius", "required": True, "exclusiveMinimum": 0}},
        _evaluate_sphere_volume,
    ),
    "cylinder_volume": CalculatorDefinition(
        "cylinder_volume",
        "Cylinder Volume Calculator",
        "geometry",
        "Calculate the volume of a cylinder.",
        "/geometry/cylinder-volume",
        "form",
        {
            "radius": {"type": "number", "label": "Radius", "required": True, "exclusiveMinimum": 0},
            "height": {"type": "number", "label": "Height", "required": True, "exclusiveMinimum": 0},
        },
        _evaluate_cylinder_volume,
    ),
    "cone_volume": CalculatorDefinition(
        "cone_volume",
        "Cone Volume Calculator",
        "geometry",
        "Calculate the volume of a cone.",
        "/geometry/cone-volume",
        "form",
        {
            "radius": {"type": "number", "label": "Radius", "required": True, "exclusiveMinimum": 0},
            "height": {"type": "number", "label": "Height", "required": True, "exclusiveMinimum": 0},
        },
        _evaluate_cone_volume,
    ),
    "pyramid_volume": CalculatorDefinition(
        "pyramid_volume",
        "Pyramid Volume Calculator",
        "geometry",
        "Calculate the volume of a pyramid.",
        "/geometry/pyramid-volume",
        "form",
        {
            "base_area": {"type": "number", "label": "Base Area", "required": True, "exclusiveMinimum": 0},
            "height": {"type": "number", "label": "Height", "required": True, "exclusiveMinimum": 0},
        },
        _evaluate_pyramid_volume,
    ),
    "solve_quadratic": CalculatorDefinition(
        "solve_quadratic",
        "Quadratic Equation Calculator",
        "algebra",
        "Solve a*x**2 + b*x + c = 0.",
        "/algebra/solve-quadratic",
        "form",
        {
            "a": {"type": "number", "label": "A", "required": True, "not": {"const": 0}},
            "b": {"type": "number", "label": "B", "required": True},
            "c": {"type": "number", "label": "C", "required": True},
        },
        _evaluate_solve_quadratic,
    ),
    "solve_linear_system": CalculatorDefinition(
        "solve_linear_system",
        "Linear System Solver",
        "algebra",
        "Solve a linear equation system and map variables to values.",
        "/algebra/solve-linear-system",
        "form",
        {
            "equations": {"type": "array", "label": "Equations", "required": True, "items": {"type": "string"}, "minItems": 1},
            "variables": {"type": "array", "label": "Variables", "required": True, "items": {"type": "string"}, "minItems": 1},
        },
        _evaluate_solve_linear_system,
    ),
    "factor_polynomial": CalculatorDefinition(
        "factor_polynomial",
        "Polynomial Factorization Calculator",
        "algebra",
        "Factor a polynomial expression.",
        "/algebra/factor-polynomial",
        "form",
        {"expr": {"type": "string", "label": "Expression", "required": True, "minLength": 1}},
        _evaluate_factor_polynomial,
    ),
    "find_roots": CalculatorDefinition(
        "find_roots",
        "Polynomial Roots Calculator",
        "algebra",
        "Find roots for a univariate polynomial expression.",
        "/algebra/find-roots",
        "form",
        {"expr": {"type": "string", "label": "Expression", "required": True, "minLength": 1}},
        _evaluate_find_roots,
    ),
    "mean": CalculatorDefinition(
        "mean",
        "Mean Calculator",
        "statistics",
        "Calculate the arithmetic mean.",
        "/statistics/mean",
        "form",
        {"numbers": {"type": "array", "label": "Numbers", "required": True, "items": {"type": "number"}, "minItems": 1}},
        _evaluate_mean,
    ),
    "std_dev": CalculatorDefinition(
        "std_dev",
        "Standard Deviation Calculator",
        "statistics",
        "Calculate the population standard deviation.",
        "/statistics/std-dev",
        "form",
        {"numbers": {"type": "array", "label": "Numbers", "required": True, "items": {"type": "number"}, "minItems": 1}},
        _evaluate_std_dev,
    ),
    "gcd": CalculatorDefinition(
        "gcd",
        "Greatest Common Divisor Calculator",
        "statistics",
        "Return the greatest common divisor of two integers.",
        "/statistics/gcd",
        "form",
        {
            "a": {"type": "integer", "label": "A", "required": True},
            "b": {"type": "integer", "label": "B", "required": True},
        },
        _evaluate_gcd,
    ),
    "lcm": CalculatorDefinition(
        "lcm",
        "Least Common Multiple Calculator",
        "statistics",
        "Return the least common multiple of two integers.",
        "/statistics/lcm",
        "form",
        {
            "a": {"type": "integer", "label": "A", "required": True},
            "b": {"type": "integer", "label": "B", "required": True},
        },
        _evaluate_lcm,
    ),
    "prime_factors": CalculatorDefinition(
        "prime_factors",
        "Prime Factorization Calculator",
        "statistics",
        "Return the prime factors of n.",
        "/statistics/prime-factors",
        "form",
        {"n": {"type": "integer", "label": "N", "required": True, "minimum": 2}},
        _evaluate_prime_factors,
    ),
    "log_base": CalculatorDefinition(
        "log_base",
        "Logarithm Base Calculator",
        "utility",
        "Compute logarithm of x with custom base.",
        "/utility/log-base",
        "form",
        {
            "x": {"type": "number", "label": "X", "required": True, "exclusiveMinimum": 0},
            "base": {"type": "number", "label": "Base", "required": True, "exclusiveMinimum": 0, "not": {"const": 1}},
        },
        _evaluate_log_base,
    ),
    "power": CalculatorDefinition(
        "power",
        "Power Calculator",
        "utility",
        "Raise base to exponent.",
        "/utility/power",
        "form",
        {
            "base": {"type": "number", "label": "Base", "required": True},
            "exponent": {"type": "number", "label": "Exponent", "required": True},
        },
        _evaluate_power,
    ),
    "to_scientific_notation": CalculatorDefinition(
        "to_scientific_notation",
        "Scientific Notation Formatter",
        "utility",
        "Format a number in scientific notation.",
        "/utility/scientific-notation",
        "form",
        {
            "x": {"type": "number", "label": "Number", "required": True},
            "precision": {"type": "integer", "label": "Precision", "required": False, "minimum": 0},
        },
        _evaluate_to_scientific_notation,
    ),
    "to_binary": CalculatorDefinition(
        "to_binary",
        "Binary Converter",
        "utility",
        "Convert an integer to binary string.",
        "/utility/to-binary",
        "form",
        {"n": {"type": "integer", "label": "Number", "required": True}},
        _evaluate_to_binary,
    ),
    "from_binary": CalculatorDefinition(
        "from_binary",
        "Binary Parser",
        "utility",
        "Convert a binary string to integer.",
        "/utility/from-binary",
        "form",
        {"bin_str": {"type": "string", "label": "Binary String", "required": True, "minLength": 1}},
        _evaluate_from_binary,
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


def _get_calculator(slug: str) -> CalculatorDefinition | None:
    return _CALCULATORS.get(slug)


def list_calculators(category: str | None = None) -> list[dict[str, Any]]:
    """List available calculator metadata, optionally filtered by category."""
    calculators = _CALCULATORS.values()
    if category is not None:
        calculators = [calc for calc in calculators if calc.category == category]
    return [_metadata(calc) for calc in calculators]


def _get_calculator_schema(slug: str) -> dict[str, Any]:
    """Return the input schema wrapper for a registered calculator slug."""
    calculator = _get_calculator(slug)
    if calculator is None:
        return _error_response("unknown_slug", f"Unknown calculator slug: {slug}", {"slug": slug})
    return {"calculator": slug, "schema": calculator.schema}


def _validate_value(field_name: str, schema: dict[str, Any], value: Any) -> str | None:
    expected_type = schema.get("type")

    if expected_type == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return f"Invalid input type for '{field_name}': expected number"
    elif expected_type == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            return f"Invalid input type for '{field_name}': expected integer"
    elif expected_type == "string":
        if not isinstance(value, str):
            return f"Invalid input type for '{field_name}': expected string"
    elif expected_type == "array":
        if not isinstance(value, list):
            return f"Invalid input type for '{field_name}': expected array"
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            return f"Invalid input for '{field_name}': requires at least {min_items} items"
        item_schema = schema.get("items", {})
        item_type = item_schema.get("type")
        for item in value:
            if item_type == "number" and (isinstance(item, bool) or not isinstance(item, (int, float))):
                return f"Invalid input type for '{field_name}': expected array of numbers"
            if item_type == "string" and not isinstance(item, str):
                return f"Invalid input type for '{field_name}': expected array of strings"
        return None

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        exclusive_minimum = schema.get("exclusiveMinimum")
        exclusive_maximum = schema.get("exclusiveMaximum")
        const_not = schema.get("not", {}).get("const") if isinstance(schema.get("not"), dict) else None

        if isinstance(minimum, (int, float)) and value < minimum:
            return f"Invalid input for '{field_name}': must be >= {minimum}"
        if isinstance(maximum, (int, float)) and value > maximum:
            return f"Invalid input for '{field_name}': must be <= {maximum}"
        if isinstance(exclusive_minimum, (int, float)) and value <= exclusive_minimum:
            return f"Invalid input for '{field_name}': must be > {exclusive_minimum}"
        if isinstance(exclusive_maximum, (int, float)) and value >= exclusive_maximum:
            return f"Invalid input for '{field_name}': must be < {exclusive_maximum}"
        if const_not is not None and value == const_not:
            return f"Invalid input for '{field_name}': value {const_not} is not allowed"

    if isinstance(value, str):
        min_length = schema.get("minLength")
        max_length = schema.get("maxLength")
        if isinstance(min_length, int) and len(value) < min_length:
            return f"Invalid input for '{field_name}': minimum length is {min_length}"
        if isinstance(max_length, int) and len(value) > max_length:
            return f"Invalid input for '{field_name}': maximum length is {max_length}"

    return None


def _validate_inputs(calculator: CalculatorDefinition, inputs: Any) -> dict[str, Any] | None:
    if not isinstance(inputs, dict):
        return _error_response("invalid_input_type", "Invalid input type for 'inputs': expected object")

    for field_name, field_schema in calculator.schema.items():
        required = field_schema.get("required", False)
        if required and field_name not in inputs:
            return _error_response(
                "missing_required_input",
                f"Missing required input: {field_name}",
                {"field": field_name},
            )
        if field_name not in inputs:
            continue

        error_message = _validate_value(field_name, field_schema, inputs[field_name])
        if error_message is not None:
            return _error_response("invalid_input_value", error_message, {"field": field_name})

    return None


def generate_prefilled_url(slug: str, inputs: dict[str, Any], base_url: str = DEFAULT_CALC_URL_BASE) -> str:
    """Build a prefilled calculator URL for GUI handoff or bookmarking."""
    query_payload = {"calculator": slug, **{key: str(value) for key, value in inputs.items()}}
    return f"{base_url}?{urlencode(query_payload)}"


def calculate(slug: str, inputs: dict[str, Any]) -> dict[str, Any]:
    """Run a registered calculator and return a structured result payload."""
    calculator = _get_calculator(slug)
    if calculator is None:
        return _error_response("unknown_slug", f"Unknown calculator slug: {slug}", {"slug": slug})

    validation_error = _validate_inputs(calculator, inputs)
    if validation_error is not None:
        return validation_error

    try:
        result = calculator.evaluator(inputs)
    except Exception as exc:  # noqa: BLE001 - normalize runtime failures for MCP clients.
        return _error_response("calculation_error", str(exc), {"slug": slug})

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
