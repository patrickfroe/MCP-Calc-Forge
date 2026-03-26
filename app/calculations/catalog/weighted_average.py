from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> float:
    raw_values = payload["values"]
    raw_weights = payload["weights"]

    if not isinstance(raw_values, list) or not isinstance(raw_weights, list):
        raise ValueError("values and weights must be lists")
    if len(raw_values) != len(raw_weights):
        raise ValueError("values and weights must have the same length")

    values = [float(value) for value in raw_values]
    weights = [float(weight) for weight in raw_weights]
    weight_sum = sum(weights)
    if weight_sum == 0:
        raise ValueError("sum(weights) must not be zero")

    return sum(value * weight for value, weight in zip(values, weights)) / weight_sum


CALCULATION = CalculationDefinition(
    id="weighted_average",
    name="Weighted Average",
    description="Berechnet den gewichteten Durchschnitt aus Werten und Gewichten.",
    llm_usage_hint="Verwenden, wenn Werte mit unterschiedlicher Gewichtung in einen Durchschnitt eingehen sollen.",
    input_fields=(
        InputField(name="values", field_type="number_list", description="Werte"),
        InputField(name="weights", field_type="number_list", description="Gewichte"),
    ),
    output_description="Numerischer gewichteter Durchschnitt.",
    output_type="number",
    examples=(
        CalculationExample(
            title="Gewichteter Durchschnitt",
            input={"values": [1, 2, 3], "weights": [1, 1, 2]},
        ),
    ),
    execute=execute,
)
