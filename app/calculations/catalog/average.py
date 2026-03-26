from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> float:
    raw_values = payload["values"]
    if not isinstance(raw_values, list):
        raise ValueError("values must be a list")
    if not raw_values:
        raise ValueError("values must not be empty")
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in raw_values):
        raise ValueError("values must contain only numbers")

    values = [float(value) for value in raw_values]
    return sum(values) / len(values)


CALCULATION = CalculationDefinition(
    id="average",
    name="Average",
    description="Berechnet den Durchschnitt aus mehreren Zahlen.",
    llm_usage_hint="Verwenden, wenn aus mehreren Zahlen ein Mittelwert berechnet werden soll.",
    input_fields=(
        InputField(name="values", field_type="number_list", description="Liste numerischer Werte"),
    ),
    output_description="Numerischer Durchschnittswert.",
    output_type="number",
    examples=(
        CalculationExample(title="Mittelwert von 2,4,6", input={"values": [2, 4, 6]}),
    ),
    execute=execute,
)
