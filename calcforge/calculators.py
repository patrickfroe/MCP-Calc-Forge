"""Unified calculator registry, schema resolution, and execution."""

from __future__ import annotations

from typing import Any, Callable

JSON = dict[str, Any]


class CalculatorValidationError(ValueError):
    """Raised when calculator inputs fail schema validation."""


def _error_response(code: str, message: str, details: dict[str, Any] | None = None) -> JSON:
    payload: JSON = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


def _number_field(label: str, *, default: float | None = None, minimum: float | None = 0.0, help_text: str) -> JSON:
    field: JSON = {
        "type": "number",
        "label": label,
        "help": help_text,
    }
    if default is not None:
        field["default"] = default
    if minimum is not None:
        field["minimum"] = minimum
    return field


def _common_form_schema(name: str) -> JSON:
    return {
        "type": "object",
        "title": f"{name} Inputs",
        "required": ["primary_value"],
        "properties": {
            "primary_value": _number_field(
                "Primary value",
                help_text="Main numeric value used by this calculator.",
                minimum=0,
            ),
            "secondary_value": _number_field(
                "Secondary value",
                default=0,
                help_text="Optional second numeric value.",
            ),
            "rate": _number_field(
                "Rate (%)",
                default=0,
                help_text="Percentage/rate input when relevant.",
                minimum=0,
            ),
            "periods": {
                "type": "integer",
                "label": "Periods",
                "help": "Number of periods/terms used in the calculation.",
                "default": 1,
                "minimum": 1,
            },
            "mode": {
                "type": "string",
                "label": "Mode",
                "help": "Select calculation mode.",
                "default": "standard",
                "enum": ["standard", "advanced"],
            },
        },
        "additionalProperties": False,
    }


def _interactive_schema(name: str, tool_type: str) -> JSON:
    return {
        "type": "object",
        "title": f"{name} Session Payload",
        "required": ["session_id", "payload"],
        "properties": {
            "session_id": {
                "type": "string",
                "label": "Session ID",
                "help": "Client-managed session identifier.",
                "minLength": 1,
            },
            "payload": {
                "type": "object",
                "label": "Payload",
                "help": f"Structured request payload for the {tool_type} workspace.",
                "additionalProperties": True,
            },
        },
        "additionalProperties": False,
    }


def _validate_against_schema(schema: JSON, inputs: JSON) -> None:
    if not isinstance(inputs, dict):
        raise CalculatorValidationError("inputs must be an object")

    required = schema.get("required", [])
    properties = schema.get("properties", {})

    for key in required:
        if key not in inputs:
            raise CalculatorValidationError(f"missing required input: {key}")

    if not schema.get("additionalProperties", True):
        unknown = sorted(set(inputs) - set(properties))
        if unknown:
            raise CalculatorValidationError(f"unknown inputs: {', '.join(unknown)}")

    for key, value in inputs.items():
        if key not in properties:
            continue
        spec = properties[key]
        expected = spec.get("type")

        if expected == "number" and not isinstance(value, (int, float)):
            raise CalculatorValidationError(f"invalid input type for {key}: expected number")
        if expected == "integer" and not isinstance(value, int):
            raise CalculatorValidationError(f"invalid input type for {key}: expected integer")
        if expected == "string" and not isinstance(value, str):
            raise CalculatorValidationError(f"invalid input type for {key}: expected string")
        if expected == "object" and not isinstance(value, dict):
            raise CalculatorValidationError(f"invalid input type for {key}: expected object")

        if isinstance(value, (int, float)):
            min_val = spec.get("minimum")
            max_val = spec.get("maximum")
            if min_val is not None and value < min_val:
                raise CalculatorValidationError(f"{key} must be >= {min_val}")
            if max_val is not None and value > max_val:
                raise CalculatorValidationError(f"{key} must be <= {max_val}")

        if isinstance(value, str):
            min_len = spec.get("minLength")
            if min_len is not None and len(value) < min_len:
                raise CalculatorValidationError(f"{key} length must be >= {min_len}")
            choices = spec.get("enum")
            if choices and value not in choices:
                raise CalculatorValidationError(f"{key} must be one of: {', '.join(choices)}")


def _placeholder_handler(slug: str) -> Callable[[JSON], JSON]:
    def _handler(_: JSON) -> JSON:
        return _error_response(
            "unimplemented_handler",
            f"Calculator '{slug}' is registered and schema-validated but not yet executable.",
            {"slug": slug},
        )

    return _handler


def _bmi_handler(inputs: JSON) -> JSON:
    height_m = float(inputs["primary_value"])
    weight_kg = float(inputs.get("secondary_value", 0))
    if height_m <= 0 or weight_kg <= 0:
        return _error_response("invalid_input", "primary_value(height m) and secondary_value(weight kg) must be > 0")
    bmi = weight_kg / (height_m**2)
    return {"bmi": round(bmi, 2)}


def _percentage_handler(inputs: JSON) -> JSON:
    base = float(inputs["primary_value"])
    rate = float(inputs.get("rate", 0))
    return {"value": base * rate / 100.0}


# Source-of-truth calculator metadata from the provided registry seed list.
# NOTE: This repository migration keeps registry discovery centralized.
CALCULATOR_META: list[JSON] = [
    {"slug": "mortgage_payment", "name": "Mortgage Payment Calculator", "category": "finance", "description": "Calculate monthly mortgage payments including principal, interest, taxes, insurance, PMI, and HOA. View full amortization schedule.", "route": "/finance/mortgage", "type": "form"},
    {"slug": "compound_interest", "name": "Compound Interest Calculator", "category": "finance", "description": "Calculate how your savings or investments grow over time with compound interest. See the effect of different compounding frequencies.", "route": "/finance/compound-interest", "type": "form"},
    {"slug": "bmi", "name": "BMI Calculator", "category": "health", "description": "Calculate your Body Mass Index (BMI) using height and weight. Provides BMI category and healthy weight range.", "route": "/health/bmi", "type": "form"},
    {"slug": "tip_calculator", "name": "Tip Calculator", "category": "travel", "description": "Calculate restaurant tips and split the bill among multiple people. Supports custom tip percentages.", "route": "/travel/tip", "type": "form"},
    {"slug": "percentage", "name": "Percentage Calculator", "category": "math", "description": "Perform common percentage operations: find a percentage of a value, calculate what percentage one number is of another, and find percentage change.", "route": "/math/percentage", "type": "form"},
    {"slug": "cash_out_refinance", "name": "Cash-Out Refinance Comparison Calculator", "category": "finance", "description": "Compare current mortgage vs cash-out refinance payment and long-term cost.", "route": "/finance/cash-out-refinance", "type": "form"},
    {"slug": "mortgage_buydown", "name": "Mortgage Buydown Calculator", "category": "finance", "description": "Estimate rate buydown savings and break-even timeline from points paid.", "route": "/finance/mortgage-buydown", "type": "form"},
    {"slug": "rental_property", "name": "Rental Property Calculator", "category": "finance", "description": "Evaluate rental property metrics including NOI, cap rate, cash flow, and cash-on-cash return.", "route": "/finance/rental-property", "type": "form"},
    {"slug": "vo2_max", "name": "VO2 Max Estimator", "category": "health", "description": "Estimate VO2 max from resting and maximum heart rate.", "route": "/health/vo2-max", "type": "form"},
    {"slug": "race_predictor", "name": "Running Race Predictor", "category": "health", "description": "Predict race times at common distances using a known result and Riegel scaling.", "route": "/health/race-predictor", "type": "form"},
    {"slug": "target_heart_rate", "name": "Target Heart Rate Workout Planner", "category": "health", "description": "Compute target training zone and total time in zone for a planned workout.", "route": "/health/target-heart-rate", "type": "form"},
    {"slug": "menstrual_cycle", "name": "Menstrual Cycle Tracker", "category": "health", "description": "Estimate next period and fertile windows using min/max cycle lengths for irregular cycles.", "route": "/health/menstrual-cycle", "type": "form"},
    {"slug": "medication_schedule", "name": "Medication Schedule Checker", "category": "health", "description": "Check timing overlap risk between two repeating medication schedules.", "route": "/health/medication-schedule", "type": "form"},
    {"slug": "matrix_calculator", "name": "Matrix Calculator", "category": "math", "description": "Compute determinant, inverse, and eigenvalues for a 2x2 matrix.", "route": "/math/matrix-calculator", "type": "form"},
    {"slug": "unit_dimension_checker", "name": "Unit Dimension Checker", "category": "math", "description": "Verify dimensional consistency by comparing exponents of kg, m, and s on both sides.", "route": "/math/unit-dimension-checker", "type": "form"},
    {"slug": "linear_regression", "name": "Linear Regression Calculator", "category": "math", "description": "Fit a simple linear regression line and return slope, intercept, and R².", "route": "/math/linear-regression", "type": "form"},
    {"slug": "base_converter", "name": "Number Base Converter", "category": "math", "description": "Convert a decimal integer into binary, octal, and hexadecimal formats.", "route": "/math/base-converter", "type": "form"},
    {"slug": "contractor_vs_employee", "name": "Contractor vs Employee Cost Calculator", "category": "business", "description": "Compare annual employer cost for W-2 employee vs contractor arrangement.", "route": "/business/contractor-vs-employee", "type": "form"},
    {"slug": "cas", "name": "Math Workspace (CAS)", "category": "math", "description": "General-purpose computational math environment with symbolic algebra, calculus, equation solving, and interactive plotting. Supports LaTeX input.", "route": "/math/cas", "type": "cas"},
    {"slug": "rpn", "name": "RPN Calculator", "category": "math", "description": "42S-style scientific RPN calculator with a four-level stack, programmable commands, and shareable sessions.", "route": "/math/rpn-calculator", "type": "rpn"},
]


HANDLERS: dict[str, Callable[[JSON], JSON]] = {
    "bmi": _bmi_handler,
    "percentage": _percentage_handler,
}


CALCULATOR_REGISTRY: dict[str, JSON] = {}
for meta in CALCULATOR_META:
    tool_type = meta["type"]
    schema = _common_form_schema(meta["name"]) if tool_type == "form" else _interactive_schema(meta["name"], tool_type)
    CALCULATOR_REGISTRY[meta["slug"]] = {
        "meta": meta,
        "schema": schema,
        "handler": HANDLERS.get(meta["slug"], _placeholder_handler(meta["slug"])),
    }


def list_calculators(category: str | None = None) -> list[JSON]:
    items = [entry["meta"] for entry in CALCULATOR_REGISTRY.values()]
    if category is None:
        return sorted(items, key=lambda x: x["slug"])
    return sorted([i for i in items if i["category"] == category], key=lambda x: x["slug"])


def _get_calculator_schema(slug: str) -> JSON:
    entry = CALCULATOR_REGISTRY.get(slug)
    if entry is None:
        return _error_response("unknown_slug", f"Unknown calculator slug: {slug}", {"slug": slug})
    return {"slug": slug, "schema": entry["schema"]}


def calculate(slug: str, inputs: dict[str, Any]) -> JSON:
    entry = CALCULATOR_REGISTRY.get(slug)
    if entry is None:
        return _error_response("unknown_slug", f"Unknown calculator slug: {slug}", {"slug": slug})

    try:
        _validate_against_schema(entry["schema"], inputs)
    except CalculatorValidationError as exc:
        message = str(exc)
        code = "missing_required_inputs" if message.startswith("missing required") else "invalid_input_type"
        return _error_response(code, message, {"slug": slug})

    result = entry["handler"](inputs)
    if isinstance(result, dict) and "error" in result:
        return result
    return {"slug": slug, "result": result}
