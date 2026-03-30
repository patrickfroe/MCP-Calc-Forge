from __future__ import annotations

from app.calculations.registry import CalculationRegistry, get_registry
from app.mcp.tools.get_calculation_details import get_calculation_details_tool


def ui_get_calculation_preview_tool(
    calculation_id: str,
    registry: CalculationRegistry | None = None,
) -> dict[str, object]:
    details_response = get_calculation_details_tool(calculation_id=calculation_id, registry=registry or get_registry())
    if not details_response.get("ok"):
        return details_response

    details = details_response["result"]
    input_fields = details["input_fields"]
    preview = {
        "id": details["id"],
        "name": details["name"],
        "description": details["description"],
        "required_inputs": [field["name"] for field in input_fields if field["required"]],
        "input_count": len(input_fields),
        "example_count": len(details["examples"]),
    }

    return {
        "ok": True,
        "result": preview,
        "structuredContent": preview,
        "content": [
            {
                "type": "text",
                "text": (
                    f"Preview for {preview['id']}: "
                    f"{preview['input_count']} input(s), {preview['example_count']} example(s)."
                ),
            }
        ],
    }
