from __future__ import annotations

from app.calculations.registry import CalculationRegistry, get_registry


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
    return {"ok": True, "result": {"calculations": calculations}}
