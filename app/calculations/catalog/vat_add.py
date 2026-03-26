from app.calculations.models import CalculationDefinition, CalculationExample, InputField

CALCULATION = CalculationDefinition(
    id="vat_add",
    name="VAT Add",
    description="Addiert die Mehrwertsteuer auf einen Nettobetrag.",
    llm_usage_hint="Nutze diese Berechnung, wenn Netto- in Bruttobeträge überführt werden sollen.",
    input_fields=(
        InputField(name="net_amount", field_type="number", description="Nettobetrag", min_value=0),
        InputField(name="vat_rate", field_type="number", description="Steuersatz in Prozent", min_value=0, max_value=100),
    ),
    examples=(
        CalculationExample(title="Standard MwSt", input={"net_amount": 100, "vat_rate": 19}),
    ),
)
