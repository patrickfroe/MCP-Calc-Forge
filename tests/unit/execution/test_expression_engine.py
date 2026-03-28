from app.execution.expression_engine import ExpressionEngine


def test_expression_engine_evaluates_valid_expression() -> None:
    engine = ExpressionEngine()

    payload = engine.evaluate("(2 + 3) * 4 / 2")

    assert payload["ok"] is True
    assert payload["result"]["value"] == 10.0


def test_expression_engine_rejects_unsafe_expression() -> None:
    engine = ExpressionEngine()

    payload = engine.evaluate("__import__('os').system('echo hi')")

    assert payload["ok"] is False
    assert payload["error"]["code"] == "INVALID_EXPRESSION"
    assert payload["error"]["details"]


def test_expression_engine_rejects_division_by_zero() -> None:
    engine = ExpressionEngine()

    payload = engine.evaluate("1 / 0")

    assert payload["ok"] is False
    assert payload["error"]["code"] == "INVALID_EXPRESSION"


def test_expression_engine_rejects_non_finite_result() -> None:
    engine = ExpressionEngine()

    payload = engine.evaluate("1e308 * 1e308")

    assert payload["ok"] is False
    assert payload["error"]["code"] == "INVALID_EXPRESSION"
