from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> float:
    fixed_costs = float(payload["fixed_costs"])
    price_per_unit = float(payload["price_per_unit"])
    variable_cost_per_unit = float(payload["variable_cost_per_unit"])

    if price_per_unit <= variable_cost_per_unit:
        raise ValueError("price_per_unit must be greater than variable_cost_per_unit")

    return fixed_costs / (price_per_unit - variable_cost_per_unit)


CALCULATION = CalculationDefinition(
    id="break_even_units",
    name="Break Even Units",
    description="Berechnet die Break-even-Menge.",
    llm_usage_hint="Verwenden, wenn aus Fixkosten, Stückpreis und variablen Stückkosten die Break-even-Menge berechnet werden soll.",
    input_fields=(
        InputField(name="fixed_costs", field_type="number", description="Fixkosten", min_value=0),
        InputField(name="price_per_unit", field_type="number", description="Preis pro Stück"),
        InputField(
            name="variable_cost_per_unit",
            field_type="number",
            description="Variable Kosten pro Stück",
        ),
    ),
    output_description="Numerische Break-even-Menge.",
    output_type="number",
    examples=(
        CalculationExample(
            title="Break-even bei 1000 Fixkosten",
            input={"fixed_costs": 1000, "price_per_unit": 50, "variable_cost_per_unit": 30},
        ),
    ),
    execute=execute,
)
