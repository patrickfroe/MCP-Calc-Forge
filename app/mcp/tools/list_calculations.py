from __future__ import annotations

from app.calculations.registry import CalculationRegistry, get_registry


def _build_human_summary(calculations: list[dict[str, object]]) -> str:
    count = len(calculations)
    preview_names = ", ".join(str(item["id"]) for item in calculations[:5])
    if count > 5:
        preview_names = f"{preview_names}, …"
    return f"{count} calculations available: {preview_names}" if count else "No calculations available."


def list_calculations_tool(registry: CalculationRegistry | None = None) -> dict[str, object]:
    active_registry = registry or get_registry()
    calculations = [
        {
            "id": definition.id,
            "name": definition.name,
            "description": definition.description,
            "llm_usage_hint": definition.llm_usage_hint,
        }
        for definition in active_registry.list_calculations()
    ]
    structured_content = {"calculations": calculations}
    return {
        "ok": True,
        "result": structured_content,
        "structuredContent": structured_content,
        "content": [{"type": "text", "text": _build_human_summary(calculations)}],
    }
