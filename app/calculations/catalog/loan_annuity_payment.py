from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


def execute(payload: dict[str, object]) -> dict[str, float]:
    loan_amount = float(payload["loan_amount"])
    annual_interest_rate = float(payload["annual_interest_rate"])
    months = int(payload["months"])

    monthly_rate = (annual_interest_rate / 100) / 12
    if monthly_rate == 0:
        monthly_payment = loan_amount / months
    else:
        monthly_payment = loan_amount * monthly_rate / (1 - (1 + monthly_rate) ** (-months))

    total_payment = monthly_payment * months
    total_interest = total_payment - loan_amount

    return {
        "monthly_payment": monthly_payment,
        "total_payment": total_payment,
        "total_interest": total_interest,
    }


CALCULATION = CalculationDefinition(
    id="loan_annuity_payment",
    name="Loan Annuity Payment",
    description="Berechnet die konstante Kreditrate eines Annuitätendarlehens.",
    llm_usage_hint="Verwenden, wenn für einen Kreditbetrag mit Zinssatz und Laufzeit die regelmäßige Rate berechnet werden soll.",
    input_fields=(
        InputField(name="loan_amount", field_type="number", description="Kreditbetrag", min_value=0),
        InputField(
            name="annual_interest_rate",
            field_type="number",
            description="Jahreszins in Prozent",
            min_value=0,
        ),
        InputField(name="months", field_type="integer", description="Laufzeit in Monaten", min_value=1),
    ),
    output_description="Objekt mit monthly_payment, total_payment und total_interest.",
    output_type="object",
    examples=(
        CalculationExample(
            title="Kreditrate für 10.000 über 24 Monate",
            input={"loan_amount": 10000, "annual_interest_rate": 6, "months": 24},
        ),
    ),
    execute=execute,
)
