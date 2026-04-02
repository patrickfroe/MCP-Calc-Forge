from __future__ import annotations

from app.calculations.registry import get_registry
from app.execution.calculation_executor import CalculationExecutor

UI_RESOURCE_URI = "ui://calculations/list"


def execute_calculation_tool(
    calculation_id: str,
    inputs: dict[str, object],
    executor: CalculationExecutor | None = None,
) -> dict[str, object]:
    active_executor = executor or CalculationExecutor(get_registry())
    payload = active_executor.execute_calculation(calculation_id, inputs)
    payload["_meta"] = {"ui": {"resourceUri": UI_RESOURCE_URI}}
    payload["structuredContent"] = {
        "ok": payload.get("ok"),
        "calculation_id": payload.get("calculation_id"),
        "result": payload.get("result"),
        "error": payload.get("error"),
    }
    if payload.get("ok"):
        payload["content"] = [
            {
                "type": "text",
                "text": f"Berechnung '{calculation_id}' ausgeführt. Ergebnis in der UI anzeigen.",
            }
        ]
        return payload

    error_message = str(payload.get("error", {}).get("message", "Berechnung fehlgeschlagen."))
    payload["content"] = [{"type": "text", "text": error_message}]
    return payload
