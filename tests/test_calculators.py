from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import calcforge.calculators as calculators


def test_list_calculators_comes_from_registry() -> None:
    items = calculators.list_calculators()
    assert len(items) == len(calculators.CALCULATOR_META)
    assert any(item["slug"] == "cas" for item in items)


def test_schema_lookup_returns_unknown_slug_error() -> None:
    payload = calculators.get_calculator_schema("add")


def test_unknown_slug_errors() -> None:
    schema_payload = calculators.get_calculator_schema("add")
    calc_payload = calculators.calculate("add", {"primary_value": 1})

    assert schema_payload["error"]["code"] == "unknown_slug"
    assert calc_payload["error"]["code"] == "unknown_slug"


def test_calculate_bmi() -> None:
    payload = calculators.calculate("bmi", {"height_m": 1.8, "weight_kg": 81})
    assert payload["result"]["results"]["bmi"] == 25.0


def test_all_calculators_have_executable_logic() -> None:
    samples = {
        "mortgage_payment": {"loan_amount": 300000, "annual_rate": 6.5, "loan_term_years": 30},
        "compound_interest": {"initial_principal": 10000, "annual_rate": 7, "compoundings_per_year": 12, "years": 10, "periodic_contribution": 100},
        "bmi": {"height_m": 1.75, "weight_kg": 72},
        "tip_calculator": {"bill_amount": 120, "tip_percent": 18, "people": 3},
        "percentage": {"mode": "percent_change", "value_a": 80, "value_b": 92},
        "cash_out_refinance": {"current_balance": 250000, "current_rate": 6.9, "current_years_remaining": 24, "new_rate": 6.0, "new_term_years": 30, "cash_out_amount": 20000},
        "mortgage_buydown": {"loan_amount": 400000, "base_rate": 6.5, "reduced_rate": 6.0, "loan_term_years": 30, "points_paid": 1.5},
        "rental_property": {"property_value": 350000, "monthly_rent": 2500, "vacancy_rate": 5, "annual_operating_expenses": 7000, "annual_debt_service": 12000, "cash_invested": 90000},
        "vo2_max": {"resting_hr": 58, "max_hr": 185},
        "race_predictor": {"known_distance_km": 10, "known_time_minutes": 48},
        "target_heart_rate": {"age": 35, "resting_hr": 60, "intensity_low": 60, "intensity_high": 80, "workout_minutes": 40},
        "menstrual_cycle": {"last_period_start": "2026-03-01", "min_cycle_length": 27, "max_cycle_length": 33},
        "medication_schedule": {"med_a_every_hours": 8, "med_b_every_hours": 12, "horizon_hours": 48, "overlap_window_minutes": 30},
        "matrix_calculator": {"m11": 4, "m12": 2, "m21": 1, "m22": 3},
        "unit_dimension_checker": {"left_kg": 1, "left_m": 1, "left_s": -2, "right_kg": 1, "right_m": 1, "right_s": -2},
        "linear_regression": {"x_values_csv": "1,2,3,4", "y_values_csv": "2,4,6,8"},
        "base_converter": {"decimal_value": 255},
        "contractor_vs_employee": {"employee_base_pay": 120000, "employee_benefits_percent": 20, "employee_payroll_tax_percent": 8, "contractor_hourly_rate": 90, "annual_hours": 1900},
        "cas": {"session_id": "s1", "payload": {"expression": "2+2*5"}},
        "rpn": {"session_id": "s2", "payload": {"tokens": [2, 3, "+", 4, "*"]}},
    }

    for slug, sample in samples.items():
        payload = calculators.calculate(slug, sample)
        assert payload.get("error") is None, f"{slug}: {payload}"
        assert payload["slug"] == slug
        assert "result" in payload
