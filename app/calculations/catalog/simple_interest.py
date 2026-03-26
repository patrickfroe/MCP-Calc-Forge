from app.calculations.models import CalculationDefinition, CalculationExample, InputField

CALCULATION = CalculationDefinition(
    id="simple_interest",
    name="Simple Interest",
    description="Berechnet einfache Zinsen ohne Zinseszins.",
    llm_usage_hint="Nutze diese Berechnung für lineare Zinsfragen über feste Laufzeiten.",
    input_fields=(
        InputField(name="principal", field_type="number", description="Startkapital", min_value=0),
        InputField(name="annual_rate", field_type="number", description="Jahreszins in Prozent", min_value=0),
        InputField(name="years", field_type="number", description="Laufzeit in Jahren", min_value=0),
    ),
    examples=(
        CalculationExample(
            title="3 Jahre Anlage",
            input={"principal": 5000, "annual_rate": 4.5, "years": 3},
        ),
    ),
)
