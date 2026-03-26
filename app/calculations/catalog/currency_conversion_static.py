from __future__ import annotations

from app.calculations.models import CalculationDefinition, CalculationExample, InputField


_ALLOWED_CURRENCIES = ("EUR", "USD", "GBP", "CHF")


def execute(payload: dict[str, object]) -> dict[str, float | str]:
    amount = float(payload["amount"])
    exchange_rate = float(payload["exchange_rate"])
    source_currency = str(payload["source_currency"])
    target_currency = str(payload["target_currency"])

    converted_amount = amount * exchange_rate
    return {
        "converted_amount": converted_amount,
        "source_currency": source_currency,
        "target_currency": target_currency,
        "exchange_rate": exchange_rate,
    }


CALCULATION = CalculationDefinition(
    id="currency_conversion_static",
    name="Currency Conversion Static",
    description="Rechnet einen Betrag mit manuell übergebenem Wechselkurs um.",
    llm_usage_hint="Verwenden, wenn ein Betrag mit einem bereits bekannten Wechselkurs umgerechnet werden soll, ohne Live-API.",
    input_fields=(
        InputField(name="amount", field_type="number", description="Betrag"),
        InputField(name="exchange_rate", field_type="number", description="Wechselkurs", min_value=0.0000001),
        InputField(
            name="source_currency",
            field_type="string",
            description="Ausgangswährung",
            allowed_values=_ALLOWED_CURRENCIES,
        ),
        InputField(
            name="target_currency",
            field_type="string",
            description="Zielwährung",
            allowed_values=_ALLOWED_CURRENCIES,
        ),
    ),
    output_description="Objekt mit converted_amount, source_currency, target_currency und exchange_rate.",
    output_type="object",
    examples=(
        CalculationExample(
            title="EUR nach USD",
            input={"amount": 100, "exchange_rate": 1.08, "source_currency": "EUR", "target_currency": "USD"},
        ),
    ),
    execute=execute,
)
