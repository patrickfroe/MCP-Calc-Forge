from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> dict[str, float]:
    net_amount = float(payload["net_amount"])
    vat_rate = float(payload["vat_rate"])
    vat_amount = net_amount * (vat_rate / 100)
    gross_amount = net_amount + vat_amount
    return {
        "net_amount": net_amount,
        "vat_rate": vat_rate,
        "vat_amount": vat_amount,
        "gross_amount": gross_amount,
    }


CALCULATION = CalculationDefinition(
    id="vat_calculation",
    name="VAT Calculation",
    description="Berechnet Nettobetrag, Mehrwertsteuerbetrag und Bruttobetrag.",
    llm_usage_hint="Verwenden, wenn aus Nettobetrag und Steuersatz Steuerbetrag und Bruttobetrag berechnet werden sollen.",
    input_fields=(
        InputField(name="net_amount", field_type="number", description="Nettobetrag", min_value=0),
        InputField(name="vat_rate", field_type="number", description="Mehrwertsteuersatz in Prozent", min_value=0),
    ),
    output_description="Objekt mit net_amount, vat_rate, vat_amount und gross_amount.",
    output_type="object",
    examples=(
        CalculationExample(title="20% MwSt auf 100", input={"net_amount": 100, "vat_rate": 20}),
    ),
    execute=execute,
)
