from app.calculations.catalog.average import execute as execute_average
from app.calculations.catalog.percentage_of_value import execute as execute_percentage_of_value
from app.calculations.catalog.rule_of_three import execute as execute_rule_of_three
from app.calculations.catalog.vat_calculation import execute as execute_vat_calculation


def test_percentage_of_value_happy_path() -> None:
    assert execute_percentage_of_value({"base_value": 200, "percentage": 10}) == 20


def test_vat_calculation_happy_path() -> None:
    result = execute_vat_calculation({"net_amount": 100, "vat_rate": 20})
    assert result == {
        "net_amount": 100,
        "vat_rate": 20,
        "vat_amount": 20,
        "gross_amount": 120,
    }


def test_average_happy_path() -> None:
    assert execute_average({"values": [2, 4, 6]}) == 4


def test_average_invalid_values_raise_error() -> None:
    try:
        execute_average({"values": [2, "x", 6]})
    except ValueError as error:
        assert str(error) == "values must contain only numbers"
    else:
        raise AssertionError("expected ValueError")


def test_rule_of_three_happy_path() -> None:
    assert execute_rule_of_three({"a": 2, "b": 4, "c": 5}) == 10


def test_rule_of_three_zero_a_raises_error() -> None:
    try:
        execute_rule_of_three({"a": 0, "b": 4, "c": 5})
    except ValueError as error:
        assert str(error) == "a must not be zero"
    else:
        raise AssertionError("expected ValueError")
