from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> float:
    base_value = float(payload["base_value"])
    percentage = float(payload["percentage"])
    return base_value * (percentage / 100)


CALCULATION = CalculationDefinition(
    id="percentage_of_value",
    name="Percentage Of Value",
    description="Berechnet den Prozentwert aus Grundwert und Prozentsatz.",
    llm_usage_hint="Verwenden, wenn aus Grundwert und Prozentsatz der Prozentwert berechnet werden soll.",
    input_fields=(
        InputField(name="base_value", field_type="number", description="Grundwert"),
        InputField(name="percentage", field_type="number", description="Prozentsatz"),
    ),
    output_description="Numerischer Prozentwert.",
    output_type="number",
    examples=(
        CalculationExample(title="10% von 200", input={"base_value": 200, "percentage": 10}),
    ),
    execute=execute,
)
