from app.calculations.models import CalculationDefinition, CalculationExample, InputField

CALCULATION = CalculationDefinition(
    id="percentage_of",
    name="Percentage Of",
    description="Berechnet, wie viel Prozent ein Teilwert von einem Gesamtwert ist.",
    llm_usage_hint="Nutze diese Berechnung bei Fragen wie 'Wieviel Prozent sind X von Y?'.",
    input_fields=(
        InputField(name="part", field_type="number", description="Teilwert", min_value=0),
        InputField(name="whole", field_type="number", description="Gesamtwert", min_value=0.0000001),
    ),
    examples=(
        CalculationExample(title="Rabattanteil", input={"part": 15, "whole": 60}),
    ),
)
