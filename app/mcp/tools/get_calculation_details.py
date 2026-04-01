from __future__ import annotations

from app.calculations.registry import CalculationRegistry, get_registry
from app.validation.errors import error_response


def _build_human_summary(details: dict[str, object]) -> str:
    input_fields = details.get("input_fields", [])
    examples = details.get("examples", [])
    calc_id = details.get("id", "unknown")
    name = details.get("name", "")
    return (
        f"Details for {calc_id} ({name}): "
        f"{len(input_fields)} input field(s), {len(examples)} example(s)."
    )


def get_calculation_details_tool(
    calculation_id: str,
    registry: CalculationRegistry | None = None,
) -> dict[str, object]:
    active_registry = registry or get_registry()
    definition = active_registry.get(calculation_id)
    if definition is None:
        error_payload = error_response(
            code="UNKNOWN_CALCULATION_ID",
            message=f"Unbekannte calculation_id '{calculation_id}'.",
        )
        error_payload["content"] = [
            {
                "type": "text",
                "text": f"Calculation '{calculation_id}' was not found.",
            }
        ]
        return error_payload

    details = {
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
        "output_description": definition.output_description,
        "output_type": definition.output_type,
        "examples": [{"title": example.title, "input": example.input} for example in definition.examples],
    }

    return {
        "ok": True,
        "result": details,
        "structuredContent": details,
        "content": [{"type": "text", "text": _build_human_summary(details)}],
    }
