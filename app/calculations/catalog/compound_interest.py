from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> dict[str, float]:
    principal = float(payload["principal"])
    annual_rate = float(payload["annual_rate"])
    years = float(payload["years"])
    compoundings_per_year = int(payload.get("compoundings_per_year", 1))

    final_amount = principal * (1 + (annual_rate / 100) / compoundings_per_year) ** (
        compoundings_per_year * years
    )
    interest_amount = final_amount - principal

    return {
        "final_amount": final_amount,
        "interest_amount": interest_amount,
    }


CALCULATION = CalculationDefinition(
    id="compound_interest",
    name="Compound Interest",
    description="Berechnet Endkapital und Zinsertrag mit Zinseszins.",
    llm_usage_hint="Verwenden, wenn Kapital mit Zinseszins über eine Laufzeit berechnet werden soll.",
    input_fields=(
        InputField(name="principal", field_type="number", description="Startkapital", min_value=0),
        InputField(name="annual_rate", field_type="number", description="Jahreszins in Prozent", min_value=0),
        InputField(name="years", field_type="number", description="Laufzeit in Jahren", min_value=0),
        InputField(
            name="compoundings_per_year",
            field_type="integer",
            description="Anzahl Zinsperioden pro Jahr",
            required=False,
            min_value=1,
        ),
    ),
    output_description="Objekt mit final_amount und interest_amount.",
    output_type="object",
    examples=(
        CalculationExample(
            title="Zinseszins über 2 Jahre",
            input={"principal": 1000, "annual_rate": 5, "years": 2, "compoundings_per_year": 1},
        ),
    ),
    execute=execute,
)
