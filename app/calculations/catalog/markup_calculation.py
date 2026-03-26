from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> dict[str, float]:
    cost = float(payload["cost"])
    markup_percentage = float(payload["markup_percentage"])

    markup_amount = cost * (markup_percentage / 100)
    selling_price = cost + markup_amount
    return {
        "markup_amount": markup_amount,
        "selling_price": selling_price,
    }


CALCULATION = CalculationDefinition(
    id="markup_calculation",
    name="Markup Calculation",
    description="Berechnet Aufschlagbetrag und Verkaufspreis.",
    llm_usage_hint="Verwenden, wenn aus Kosten und gewünschtem Aufschlag der Verkaufspreis berechnet werden soll.",
    input_fields=(
        InputField(name="cost", field_type="number", description="Kosten", min_value=0),
        InputField(name="markup_percentage", field_type="number", description="Aufschlag in Prozent", min_value=0),
    ),
    output_description="Objekt mit markup_amount und selling_price.",
    output_type="object",
    examples=(
        CalculationExample(
            title="25% Aufschlag auf 80",
            input={"cost": 80, "markup_percentage": 25},
        ),
    ),
    execute=execute,
)
