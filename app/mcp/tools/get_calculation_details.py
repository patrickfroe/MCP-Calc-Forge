from __future__ import annotations

from app.calculations.registry import CalculationRegistry, get_registry
from app.validation.errors import error_response

UI_RESOURCE_URI = "ui://calculations/list"


def _build_human_summary(details: dict[str, object]) -> str:
    calc_id = str(details.get("id", "unknown"))
    name = str(details.get("name", ""))
    return f"Details für '{name or calc_id}' ({calc_id}) geladen. Nutze die eingebettete UI für Formular und Ausführung."


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
        error_payload["_meta"] = {"ui": {"resourceUri": UI_RESOURCE_URI}}
        error_payload["content"] = [
            {
                "type": "text",
                "text": (
                    f"Calculation '{calculation_id}' wurde nicht gefunden. "
                    "Nutze `list_calculations`, um verfügbare IDs zu sehen."
                ),
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
        "_meta": {"ui": {"resourceUri": UI_RESOURCE_URI}},
    }
