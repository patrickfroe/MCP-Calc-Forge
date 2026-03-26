from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> dict[str, float]:
    principal = float(payload["principal"])
    rate = float(payload["rate"])
    time_period = float(payload["time_period"])

    interest_amount = principal * (rate / 100) * time_period
    final_amount = principal + interest_amount
    return {
        "interest_amount": interest_amount,
        "final_amount": final_amount,
    }


CALCULATION = CalculationDefinition(
    id="simple_interest",
    name="Simple Interest",
    description="Berechnet lineare Verzinsung ohne Zinseszins.",
    llm_usage_hint="Verwenden, wenn für einen Betrag einfache lineare Zinsen ohne Wiederverzinsung berechnet werden sollen.",
    input_fields=(
        InputField(name="principal", field_type="number", description="Startkapital", min_value=0),
        InputField(name="rate", field_type="number", description="Zinssatz in Prozent", min_value=0),
        InputField(name="time_period", field_type="number", description="Laufzeit", min_value=0),
    ),
    output_description="Objekt mit interest_amount und final_amount.",
    output_type="object",
    examples=(
        CalculationExample(
            title="3 Jahre lineare Verzinsung",
            input={"principal": 1000, "rate": 5, "time_period": 3},
        ),
    ),
    execute=execute,
)
