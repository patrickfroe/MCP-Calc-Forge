from app.validation.expression_validator import ExpressionValidator


def test_expression_validator_accepts_valid_math_expression() -> None:
    validator = ExpressionValidator()

    errors = validator.validate("(2 + 3) * 4 - 1 / 2")

    assert errors == ()


def test_expression_validator_rejects_names() -> None:
    validator = ExpressionValidator()

    errors = validator.validate("x + 1")

    assert errors
    assert errors[0].code == "unsafe_expression"


def test_expression_validator_rejects_functions() -> None:
    validator = ExpressionValidator()

    errors = validator.validate("abs(-3)")

    assert errors
    assert errors[0].code == "unsafe_expression"


def test_expression_validator_rejects_attributes() -> None:
    validator = ExpressionValidator()

    errors = validator.validate("math.pi")

    assert errors
    assert errors[0].code == "unsafe_expression"


def test_expression_validator_rejects_invalid_syntax() -> None:
    validator = ExpressionValidator()

    errors = validator.validate("2 +")

    assert errors
    assert errors[0].code == "invalid_expression"
