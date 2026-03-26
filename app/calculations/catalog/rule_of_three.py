from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> float:
    a = float(payload["a"])
    b = float(payload["b"])
    c = float(payload["c"])
    if a == 0:
        raise ValueError("a must not be zero")
    return (b * c) / a


CALCULATION = CalculationDefinition(
    id="rule_of_three",
    name="Rule Of Three",
    description="Berechnet einen proportionalen Zielwert nach dem Dreisatz.",
    llm_usage_hint="Verwenden, wenn ein proportionaler Zusammenhang nach dem Dreisatz berechnet werden soll.",
    input_fields=(
        InputField(name="a", field_type="number", description="Startwert a"),
        InputField(name="b", field_type="number", description="Zielwert b"),
        InputField(name="c", field_type="number", description="Vergleichswert c"),
    ),
    output_description="Numerischer Ergebniswert des Dreisatzes.",
    output_type="number",
    examples=(
        CalculationExample(title="2 verhält sich zu 4 wie 5 zu x", input={"a": 2, "b": 4, "c": 5}),
    ),
    execute=execute,
)
