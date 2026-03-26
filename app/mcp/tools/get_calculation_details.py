from __future__ import annotations

from app.calculations.registry import CalculationRegistry, get_registry
from app.validation.errors import error_response


def get_calculation_details_tool(
    calculation_id: str,
    registry: CalculationRegistry | None = None,
) -> dict[str, object]:
    active_registry = registry or get_registry()
    definition = active_registry.get(calculation_id)
    if definition is None:
        return error_response(
            code="UNKNOWN_CALCULATION_ID",
            message=f"Unbekannte calculation_id '{calculation_id}'.",
        )

    return {
        "ok": True,
        "result": {
            "id": definition.id,
            "name": definition.name,
            "description": definition.description,
            "llm_usage_hint": definition.llm_usage_hint,
            "input_fields": [
                {
                    "name": field.name,
                    "field_type": field.field_type,
                    "description": field.description,
                    "required": field.required,
                    "min_value": field.min_value,
                    "max_value": field.max_value,
                    "allowed_values": list(field.allowed_values),
                }
                for field in definition.input_fields
            ],
            "examples": [{"title": example.title, "input": example.input} for example in definition.examples],
        },
    }
