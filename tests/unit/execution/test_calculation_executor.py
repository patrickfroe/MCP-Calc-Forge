from app.calculations.registry import get_registry
from app.execution.calculation_executor import CalculationExecutor


def test_execute_calculation_happy_path() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation(
        "discount_calculation", {"original_price": 100, "discount_percentage": 15}
    )

    assert payload["ok"] is True
    assert payload["calculation_id"] == "discount_calculation"
    assert payload["result"]["final_price"] == 85


def test_execute_calculation_unknown_id() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation("does_not_exist", {"x": 1})

    assert payload["ok"] is False
    assert payload["error"]["code"] == "UNKNOWN_CALCULATION_ID"


def test_execute_calculation_returns_validation_error() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation("percentage_of_value", {"base_value": 20})

    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["details"][0]["code"] == "required"


def test_execute_calculation_validates_before_execution() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation("weighted_average", {"values": [], "weights": [1]})

    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["details"][0]["field"] == "values"


def test_execute_calculation_handles_runtime_validation_error() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation("percentage_change", {"old_value": 0, "new_value": 5})

    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["details"][0]["code"] == "invalid_value"


def test_execute_calculation_rejects_break_even_invalid_margin() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation(
        "break_even_units",
        {"fixed_costs": 1000, "price_per_unit": 30, "variable_cost_per_unit": 30},
    )

    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"


def test_execute_calculation_rejects_loan_months_below_one() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation(
        "loan_annuity_payment",
        {"loan_amount": 1000, "annual_interest_rate": 6, "months": 0},
    )

    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["details"][0]["field"] == "months"


def test_execute_calculation_rejects_currency_enum() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation(
        "currency_conversion_static",
        {"amount": 100, "exchange_rate": 1.08, "source_currency": "EUR", "target_currency": "JPY"},
    )

    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["details"][0]["code"] == "invalid_enum"


def test_execute_calculation_rejects_average_empty_list() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation("average", {"values": []})

    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["details"][0]["field"] == "values"


def test_execute_calculation_rejects_rule_of_three_with_zero_a() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation("rule_of_three", {"a": 0, "b": 4, "c": 5})

    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["details"][0]["code"] == "invalid_value"


def test_execute_calculation_returns_full_object_for_vat_calculation() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation("vat_calculation", {"net_amount": 100, "vat_rate": 19})

    assert payload["ok"] is True
    assert payload["result"] == {
        "net_amount": 100.0,
        "vat_rate": 19.0,
        "vat_amount": 19.0,
        "gross_amount": 119.0,
    }
