from __future__ import annotations

from app.calculations.registry import CalculationRegistry, get_registry
from app.validation.errors import error_response

UI_RESOURCE_URI = "ui://calculations/list"


def _build_human_summary(details: dict[str, object]) -> str:
    calc_id = str(details.get("id", "unknown"))
    name = str(details.get("name", ""))
    description = str(details.get("description", "")).strip()
    usage_hint = str(details.get("llm_usage_hint", "")).strip()
    input_fields = details.get("input_fields", [])
    examples = details.get("examples", [])

    lines = [f"### {name or 'Calculation'}", f"- **ID:** `{calc_id}`"]
    if description:
        lines.append(f"- **Beschreibung:** {description}")
    if usage_hint:
        lines.append(f"- **Wann verwenden:** {usage_hint}")

    if isinstance(input_fields, list) and input_fields:
        lines.append("- **Eingabefelder:**")
        for field in input_fields[:5]:
            if not isinstance(field, dict):
                continue
            field_name = str(field.get("name", "unknown"))
            field_type = str(field.get("field_type", "unknown"))
            required = "required" if bool(field.get("required")) else "optional"
            field_description = str(field.get("description", "")).strip()
            field_line = f"  - `{field_name}` ({field_type}, {required})"
            if field_description:
                field_line = f"{field_line}: {field_description}"
            lines.append(field_line)
        if len(input_fields) > 5:
            lines.append(f"  - … und {len(input_fields) - 5} weitere(s)")

    if isinstance(examples, list) and examples:
        lines.append("- **Beispiele:**")
        for example in examples[:2]:
            if not isinstance(example, dict):
                continue
            title = str(example.get("title", "Beispiel"))
            lines.append(f"  - {title}")
        if len(examples) > 2:
            lines.append(f"  - … und {len(examples) - 2} weitere(s)")

    return "\n".join(lines)


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
                    f"### Calculation nicht gefunden\n"
                    f"- **ID:** `{calculation_id}`\n"
                    "- Bitte verwende `list_calculations`, um verfügbare IDs zu sehen."
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
