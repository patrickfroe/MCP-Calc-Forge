from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> dict[str, float]:
    original_price = float(payload["original_price"])
    discount_percentage = float(payload["discount_percentage"])

    discount_amount = original_price * (discount_percentage / 100)
    final_price = original_price - discount_amount
    return {
        "discount_amount": discount_amount,
        "final_price": final_price,
    }


CALCULATION = CalculationDefinition(
    id="discount_calculation",
    name="Discount Calculation",
    description="Berechnet Rabattbetrag und Endpreis aus Ausgangspreis und Rabattprozentsatz.",
    llm_usage_hint="Verwenden, wenn aus einem Ausgangspreis und einem Rabattprozentsatz der Nachlass und der reduzierte Endpreis berechnet werden sollen.",
    input_fields=(
        InputField(name="original_price", field_type="number", description="Ausgangspreis", min_value=0),
        InputField(
            name="discount_percentage",
            field_type="number",
            description="Rabattprozentsatz",
            min_value=0,
            max_value=100,
        ),
    ),
    output_description="Objekt mit discount_amount und final_price.",
    output_type="object",
    examples=(
        CalculationExample(
            title="15% Rabatt auf 100",
            input={"original_price": 100, "discount_percentage": 15},
        ),
    ),
    execute=execute,
)
