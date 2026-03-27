import pytest

from app.calculations.catalog.average import execute as execute_average
from app.calculations.catalog.break_even_units import execute as execute_break_even_units
from app.calculations.catalog.compound_interest import execute as execute_compound_interest
from app.calculations.catalog.currency_conversion_static import execute as execute_currency_conversion_static
from app.calculations.catalog.discount_calculation import execute as execute_discount_calculation
from app.calculations.catalog.gross_margin import execute as execute_gross_margin
from app.calculations.catalog.loan_annuity_payment import execute as execute_loan_annuity_payment
from app.calculations.catalog.markup_calculation import execute as execute_markup_calculation
from app.calculations.catalog.percentage_change import execute as execute_percentage_change
from app.calculations.catalog.percentage_of_value import execute as execute_percentage_of_value
from app.calculations.catalog.rule_of_three import execute as execute_rule_of_three
from app.calculations.catalog.simple_interest import execute as execute_simple_interest
from app.calculations.catalog.vat_calculation import execute as execute_vat_calculation
from app.calculations.catalog.weighted_average import execute as execute_weighted_average


def test_discount_calculation_happy_path() -> None:
    result = execute_discount_calculation({"original_price": 100, "discount_percentage": 15})

    assert result == {"discount_amount": 15.0, "final_price": 85.0}


def test_discount_calculation_full_discount_sets_final_price_to_zero() -> None:
    result = execute_discount_calculation({"original_price": 250, "discount_percentage": 100})

    assert result == {"discount_amount": 250.0, "final_price": 0.0}


def test_percentage_change_happy_path() -> None:
    result = execute_percentage_change({"old_value": 80, "new_value": 100})

    assert result == {"change_amount": 20.0, "change_percentage": 25.0, "direction": "increase"}


def test_percentage_change_detects_decrease() -> None:
    result = execute_percentage_change({"old_value": 100, "new_value": 70})

    assert result == {"change_amount": -30.0, "change_percentage": -30.0, "direction": "decrease"}


def test_percentage_change_detects_no_change() -> None:
    result = execute_percentage_change({"old_value": 42, "new_value": 42})

    assert result == {"change_amount": 0.0, "change_percentage": 0.0, "direction": "no_change"}


def test_percentage_change_zero_old_value_raises_error() -> None:
    with pytest.raises(ValueError, match="old_value must not be zero"):
        execute_percentage_change({"old_value": 0, "new_value": 100})


def test_compound_interest_happy_path() -> None:
    result = execute_compound_interest(
        {"principal": 1000, "annual_rate": 5, "years": 2, "compoundings_per_year": 1}
    )

    assert result == {"final_amount": 1102.5, "interest_amount": 102.5}


def test_compound_interest_with_zero_rate_keeps_principal() -> None:
    result = execute_compound_interest(
        {"principal": 1000, "annual_rate": 0, "years": 5, "compoundings_per_year": 12}
    )

    assert result == {"final_amount": 1000.0, "interest_amount": 0.0}


def test_simple_interest_happy_path() -> None:
    result = execute_simple_interest({"principal": 1000, "rate": 5, "time_period": 3})

    assert result == {"interest_amount": 150.0, "final_amount": 1150.0}


def test_simple_interest_with_zero_time_has_no_interest() -> None:
    result = execute_simple_interest({"principal": 1000, "rate": 7, "time_period": 0})

    assert result == {"interest_amount": 0.0, "final_amount": 1000.0}


def test_markup_calculation_happy_path() -> None:
    result = execute_markup_calculation({"cost": 80, "markup_percentage": 25})

    assert result == {"markup_amount": 20.0, "selling_price": 100.0}


def test_markup_calculation_with_zero_markup_returns_cost_as_selling_price() -> None:
    result = execute_markup_calculation({"cost": 80, "markup_percentage": 0})

    assert result == {"markup_amount": 0.0, "selling_price": 80.0}


def test_gross_margin_happy_path() -> None:
    result = execute_gross_margin({"revenue": 150, "cost": 90})

    assert result == {"gross_profit": 60.0, "margin_percentage": 40.0}


def test_gross_margin_with_loss_returns_negative_margin() -> None:
    result = execute_gross_margin({"revenue": 100, "cost": 130})

    assert result == {"gross_profit": -30.0, "margin_percentage": -30.0}


def test_weighted_average_happy_path() -> None:
    result = execute_weighted_average({"values": [1, 2, 3], "weights": [1, 1, 2]})

    assert result == 2.25


def test_weighted_average_supports_negative_weights_when_sum_not_zero() -> None:
    result = execute_weighted_average({"values": [10, 30], "weights": [-1, 2]})

    assert result == 50.0


def test_weighted_average_mismatched_lengths_raise_error() -> None:
    with pytest.raises(ValueError, match="values and weights must have the same length"):
        execute_weighted_average({"values": [1, 2], "weights": [1]})


def test_weighted_average_zero_sum_weights_raise_error() -> None:
    with pytest.raises(ValueError, match="sum\\(weights\\) must not be zero"):
        execute_weighted_average({"values": [1, 2], "weights": [1, -1]})


def test_break_even_units_happy_path() -> None:
    result = execute_break_even_units(
        {"fixed_costs": 1000, "price_per_unit": 50, "variable_cost_per_unit": 30}
    )

    assert result == 50


def test_break_even_units_zero_fixed_costs_returns_zero_units() -> None:
    result = execute_break_even_units({"fixed_costs": 0, "price_per_unit": 30, "variable_cost_per_unit": 20})

    assert result == 0.0


def test_break_even_units_invalid_unit_margin_raises_error() -> None:
    with pytest.raises(ValueError, match="price_per_unit must be greater than variable_cost_per_unit"):
        execute_break_even_units({"fixed_costs": 1000, "price_per_unit": 30, "variable_cost_per_unit": 30})


def test_loan_annuity_payment_happy_path() -> None:
    result = execute_loan_annuity_payment({"loan_amount": 10000, "annual_interest_rate": 6, "months": 24})

    assert round(result["monthly_payment"], 2) == 443.21
    assert round(result["total_payment"], 2) == 10636.95
    assert round(result["total_interest"], 2) == 636.95


def test_loan_annuity_payment_zero_interest_rate() -> None:
    result = execute_loan_annuity_payment({"loan_amount": 1200, "annual_interest_rate": 0, "months": 12})

    assert result == {"monthly_payment": 100.0, "total_payment": 1200.0, "total_interest": 0.0}


def test_currency_conversion_static_happy_path() -> None:
    result = execute_currency_conversion_static(
        {"amount": 100, "exchange_rate": 1.08, "source_currency": "EUR", "target_currency": "USD"}
    )

    assert result == {
        "converted_amount": 108.0,
        "source_currency": "EUR",
        "target_currency": "USD",
        "exchange_rate": 1.08,
    }


def test_currency_conversion_static_negative_amount_supported_for_reverse_booking() -> None:
    result = execute_currency_conversion_static(
        {"amount": -50, "exchange_rate": 1.1, "source_currency": "EUR", "target_currency": "USD"}
    )

    assert result["converted_amount"] == pytest.approx(-55.0)


def test_average_happy_path() -> None:
    result = execute_average({"values": [2, 4, 6]})

    assert result == 4.0


def test_average_raises_error_on_empty_list() -> None:
    with pytest.raises(ValueError, match="values must not be empty"):
        execute_average({"values": []})


def test_average_raises_error_when_list_contains_non_numeric_values() -> None:
    with pytest.raises(ValueError, match="values must contain only numbers"):
        execute_average({"values": [1, "x"]})


def test_vat_calculation_happy_path() -> None:
    result = execute_vat_calculation({"net_amount": 100, "vat_rate": 19})

    assert result == {"net_amount": 100.0, "vat_rate": 19.0, "vat_amount": 19.0, "gross_amount": 119.0}


def test_vat_calculation_handles_zero_rate() -> None:
    result = execute_vat_calculation({"net_amount": 100, "vat_rate": 0})

    assert result == {"net_amount": 100.0, "vat_rate": 0.0, "vat_amount": 0.0, "gross_amount": 100.0}


def test_percentage_of_value_happy_path() -> None:
    result = execute_percentage_of_value({"base_value": 200, "percentage": 12.5})

    assert result == 25.0


def test_percentage_of_value_handles_negative_percentage() -> None:
    result = execute_percentage_of_value({"base_value": 200, "percentage": -10})

    assert result == -20.0


def test_rule_of_three_happy_path() -> None:
    result = execute_rule_of_three({"a": 2, "b": 4, "c": 5})

    assert result == 10.0


def test_rule_of_three_raises_on_zero_denominator() -> None:
    with pytest.raises(ValueError, match="a must not be zero"):
        execute_rule_of_three({"a": 0, "b": 4, "c": 5})
