from app.calculations.catalog.break_even_units import execute as execute_break_even_units
from app.calculations.catalog.compound_interest import execute as execute_compound_interest
from app.calculations.catalog.currency_conversion_static import execute as execute_currency_conversion_static
from app.calculations.catalog.discount_calculation import execute as execute_discount_calculation
from app.calculations.catalog.gross_margin import execute as execute_gross_margin
from app.calculations.catalog.loan_annuity_payment import execute as execute_loan_annuity_payment
from app.calculations.catalog.markup_calculation import execute as execute_markup_calculation
from app.calculations.catalog.percentage_change import execute as execute_percentage_change
from app.calculations.catalog.simple_interest import execute as execute_simple_interest
from app.calculations.catalog.weighted_average import execute as execute_weighted_average


def test_discount_calculation_happy_path() -> None:
    result = execute_discount_calculation({"original_price": 100, "discount_percentage": 15})

    assert result == {"discount_amount": 15.0, "final_price": 85.0}


def test_percentage_change_happy_path() -> None:
    result = execute_percentage_change({"old_value": 80, "new_value": 100})

    assert result == {"change_amount": 20.0, "change_percentage": 25.0, "direction": "increase"}


def test_percentage_change_zero_old_value_raises_error() -> None:
    try:
        execute_percentage_change({"old_value": 0, "new_value": 100})
    except ValueError as error:
        assert str(error) == "old_value must not be zero"
    else:
        raise AssertionError("expected ValueError")


def test_compound_interest_happy_path() -> None:
    result = execute_compound_interest(
        {"principal": 1000, "annual_rate": 5, "years": 2, "compoundings_per_year": 1}
    )

    assert result == {"final_amount": 1102.5, "interest_amount": 102.5}


def test_simple_interest_happy_path() -> None:
    result = execute_simple_interest({"principal": 1000, "rate": 5, "time_period": 3})

    assert result == {"interest_amount": 150.0, "final_amount": 1150.0}


def test_markup_calculation_happy_path() -> None:
    result = execute_markup_calculation({"cost": 80, "markup_percentage": 25})

    assert result == {"markup_amount": 20.0, "selling_price": 100.0}


def test_gross_margin_happy_path() -> None:
    result = execute_gross_margin({"revenue": 150, "cost": 90})

    assert result == {"gross_profit": 60.0, "margin_percentage": 40.0}


def test_weighted_average_happy_path() -> None:
    result = execute_weighted_average({"values": [1, 2, 3], "weights": [1, 1, 2]})

    assert result == 2.25


def test_weighted_average_mismatched_lengths_raise_error() -> None:
    try:
        execute_weighted_average({"values": [1, 2], "weights": [1]})
    except ValueError as error:
        assert str(error) == "values and weights must have the same length"
    else:
        raise AssertionError("expected ValueError")


def test_weighted_average_zero_sum_weights_raise_error() -> None:
    try:
        execute_weighted_average({"values": [1, 2], "weights": [1, -1]})
    except ValueError as error:
        assert str(error) == "sum(weights) must not be zero"
    else:
        raise AssertionError("expected ValueError")


def test_break_even_units_happy_path() -> None:
    result = execute_break_even_units(
        {"fixed_costs": 1000, "price_per_unit": 50, "variable_cost_per_unit": 30}
    )

    assert result == 50


def test_break_even_units_invalid_unit_margin_raises_error() -> None:
    try:
        execute_break_even_units({"fixed_costs": 1000, "price_per_unit": 30, "variable_cost_per_unit": 30})
    except ValueError as error:
        assert str(error) == "price_per_unit must be greater than variable_cost_per_unit"
    else:
        raise AssertionError("expected ValueError")


def test_loan_annuity_payment_happy_path() -> None:
    result = execute_loan_annuity_payment({"loan_amount": 10000, "annual_interest_rate": 6, "months": 24})

    assert round(result["monthly_payment"], 2) == 443.21
    assert round(result["total_payment"], 2) == 10636.95
    assert round(result["total_interest"], 2) == 636.95


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
