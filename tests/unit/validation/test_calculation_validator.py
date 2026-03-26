from app.calculations.models import CalculationDefinition, CalculationExample, InputField
from app.validation.calculation_validator import CalculationValidator


def _build_definition() -> CalculationDefinition:
    return CalculationDefinition(
        id="custom",
        name="Custom",
        description="desc",
        llm_usage_hint="hint",
        input_fields=(
            InputField(name="amount", field_type="number", description="Amount", min_value=0, max_value=10),
            InputField(name="mode", field_type="string", description="Mode", allowed_values=("a", "b")),
        ),
        examples=(CalculationExample(title="ex", input={"amount": 5, "mode": "a"}),),
    )


def test_validator_happy_path() -> None:
    validator = CalculationValidator()

    errors = validator.validate(_build_definition(), {"amount": 8, "mode": "b"})

    assert errors == ()


def test_validator_missing_required_field() -> None:
    validator = CalculationValidator()

    errors = validator.validate(_build_definition(), {"amount": 3})

    assert errors[0].code == "required"
    assert errors[0].field == "mode"


def test_validator_invalid_type() -> None:
    validator = CalculationValidator()

    errors = validator.validate(_build_definition(), {"amount": "3", "mode": "a"})

    assert errors[0].code == "invalid_type"
    assert errors[0].field == "amount"


def test_validator_out_of_range() -> None:
    validator = CalculationValidator()

    errors = validator.validate(_build_definition(), {"amount": 99, "mode": "a"})

    assert errors[0].code == "out_of_range"


def test_validator_invalid_enum() -> None:
    validator = CalculationValidator()

    errors = validator.validate(_build_definition(), {"amount": 5, "mode": "x"})

    assert errors[0].code == "invalid_enum"
