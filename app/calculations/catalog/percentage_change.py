from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> dict[str, float | str]:
    old_value = float(payload["old_value"])
    new_value = float(payload["new_value"])

    if old_value == 0:
        raise ValueError("old_value must not be zero")

    change_amount = new_value - old_value
    change_percentage = (change_amount / old_value) * 100

    direction = "no_change"
    if change_amount > 0:
        direction = "increase"
    elif change_amount < 0:
        direction = "decrease"

    return {
        "change_amount": change_amount,
        "change_percentage": change_percentage,
        "direction": direction,
    }


CALCULATION = CalculationDefinition(
    id="percentage_change",
    name="Percentage Change",
    description="Berechnet absolute und prozentuale Veränderung zwischen altem und neuem Wert.",
    llm_usage_hint="Verwenden, wenn eine Veränderung zwischen zwei Werten berechnet und zusätzlich prozentual ausgedrückt werden soll.",
    input_fields=(
        InputField(name="old_value", field_type="number", description="Alter Wert"),
        InputField(name="new_value", field_type="number", description="Neuer Wert"),
    ),
    output_description="Objekt mit change_amount, change_percentage und direction.",
    output_type="object",
    examples=(
        CalculationExample(
            title="Anstieg von 80 auf 100",
            input={"old_value": 80, "new_value": 100},
        ),
    ),
    execute=execute,
)
