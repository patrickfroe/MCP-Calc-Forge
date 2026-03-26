from app.calculations.registry import get_registry
from app.execution.calculation_executor import CalculationExecutor


def test_execute_calculation_happy_path() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation("vat_add", {"net_amount": 100, "vat_rate": 19})

    assert payload["ok"] is True
    assert payload["calculation_id"] == "vat_add"
    assert payload["result"]["gross_amount"] == 119


def test_execute_calculation_unknown_id() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation("does_not_exist", {"x": 1})

    assert payload["ok"] is False
    assert payload["error"]["code"] == "UNKNOWN_CALCULATION_ID"


def test_execute_calculation_returns_validation_error() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation("percentage_of", {"part": 20})

    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["details"][0]["code"] == "required"


def test_execute_calculation_validates_before_execution() -> None:
    executor = CalculationExecutor(get_registry())

    payload = executor.execute_calculation("percentage_of", {"part": 10, "whole": 0})

    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["details"][0]["field"] == "whole"
