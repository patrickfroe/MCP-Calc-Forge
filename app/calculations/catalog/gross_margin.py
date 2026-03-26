from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> dict[str, float]:
    revenue = float(payload["revenue"])
    cost = float(payload["cost"])

    gross_profit = revenue - cost
    margin_percentage = (gross_profit / revenue) * 100
    return {
        "gross_profit": gross_profit,
        "margin_percentage": margin_percentage,
    }


CALCULATION = CalculationDefinition(
    id="gross_margin",
    name="Gross Margin",
    description="Berechnet Bruttogewinn und Margenquote.",
    llm_usage_hint="Verwenden, wenn aus Umsatz und Kosten die Marge und der Gewinn berechnet werden sollen.",
    input_fields=(
        InputField(name="revenue", field_type="number", description="Umsatz", min_value=0.0000001),
        InputField(name="cost", field_type="number", description="Kosten", min_value=0),
    ),
    output_description="Objekt mit gross_profit und margin_percentage.",
    output_type="object",
    examples=(
        CalculationExample(
            title="Marge bei Umsatz 150 und Kosten 90",
            input={"revenue": 150, "cost": 90},
        ),
    ),
    execute=execute,
)
