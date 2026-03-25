"""Unified calculator registry, schema resolution, and execution."""

from __future__ import annotations

from datetime import date, timedelta
import math
from typing import Any, Callable

JSON = dict[str, Any]


class CalculatorValidationError(ValueError):
    """Raised when calculator inputs fail schema validation."""


def _error_response(code: str, message: str, details: dict[str, Any] | None = None) -> JSON:
    payload: JSON = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


def _number_field(
    label: str,
    *,
    default: float | None = None,
    minimum: float | None = None,
    maximum: float | None = None,
    help_text: str,
) -> JSON:
    field: JSON = {
        "type": "number",
        "label": label,
        "help": help_text,
    }
    if default is not None:
        field["default"] = default
    if minimum is not None:
        field["minimum"] = minimum
    if maximum is not None:
        field["maximum"] = maximum
    return field


def _int_field(label: str, *, default: int | None = None, minimum: int | None = None, maximum: int | None = None, help_text: str) -> JSON:
    field: JSON = {"type": "integer", "label": label, "help": help_text}
    if default is not None:
        field["default"] = default
    if minimum is not None:
        field["minimum"] = minimum
    if maximum is not None:
        field["maximum"] = maximum
    return field


def _validate_against_schema(schema: JSON, inputs: JSON) -> None:
    if not isinstance(inputs, dict):
        raise CalculatorValidationError("inputs must be an object")

    required = schema.get("required", [])
    properties = schema.get("properties", {})

    for key in required:
        if key not in inputs:
            raise CalculatorValidationError(f"missing required input: {key}")

    if not schema.get("additionalProperties", True):
        unknown = sorted(set(inputs) - set(properties))
        if unknown:
            raise CalculatorValidationError(f"unknown inputs: {', '.join(unknown)}")

    for key, value in inputs.items():
        if key not in properties:
            continue
        spec = properties[key]
        expected = spec.get("type")

        if expected == "number" and not isinstance(value, (int, float)):
            raise CalculatorValidationError(f"invalid input type for {key}: expected number")
        if expected == "integer" and not isinstance(value, int):
            raise CalculatorValidationError(f"invalid input type for {key}: expected integer")
        if expected == "string" and not isinstance(value, str):
            raise CalculatorValidationError(f"invalid input type for {key}: expected string")
        if expected == "object" and not isinstance(value, dict):
            raise CalculatorValidationError(f"invalid input type for {key}: expected object")

        if isinstance(value, (int, float)):
            min_val = spec.get("minimum")
            max_val = spec.get("maximum")
            if min_val is not None and value < min_val:
                raise CalculatorValidationError(f"{key} must be >= {min_val}")
            if max_val is not None and value > max_val:
                raise CalculatorValidationError(f"{key} must be <= {max_val}")

        if isinstance(value, str):
            min_len = spec.get("minLength")
            if min_len is not None and len(value) < min_len:
                raise CalculatorValidationError(f"{key} length must be >= {min_len}")
            choices = spec.get("enum")
            if choices and value not in choices:
                raise CalculatorValidationError(f"{key} must be one of: {', '.join(choices)}")


def _full_mortgage_schedule(principal: float, annual_rate: float, years: int, monthly_extra: float = 0.0) -> tuple[float, float, list[JSON]]:
    n = years * 12
    r = annual_rate / 12.0 / 100.0
    if r == 0:
        payment = principal / n
    else:
        payment = principal * (r * (1 + r) ** n) / (((1 + r) ** n) - 1)

    bal = principal
    month = 0
    total_interest = 0.0
    schedule: list[JSON] = []
    while bal > 0 and month < n + 240:
        month += 1
        interest = bal * r
        principal_paid = max(0.0, payment - interest) + monthly_extra
        if principal_paid > bal:
            principal_paid = bal
        total_payment = principal_paid + interest
        bal -= principal_paid
        total_interest += interest
        schedule.append(
            {
                "month": month,
                "payment": round(total_payment, 2),
                "principal": round(principal_paid, 2),
                "interest": round(interest, 2),
                "balance": round(max(0.0, bal), 2),
            }
        )
    return payment, total_interest, schedule


def _mortgage_payment_handler(inputs: JSON) -> JSON:
    loan_amount = float(inputs["loan_amount"])
    annual_rate = float(inputs["annual_rate"])
    years = int(inputs["loan_term_years"])
    taxes = float(inputs.get("annual_property_tax", 0.0))
    insurance = float(inputs.get("annual_insurance", 0.0))
    pmi = float(inputs.get("monthly_pmi", 0.0))
    hoa = float(inputs.get("monthly_hoa", 0.0))

    payment_pi, total_interest, schedule = _full_mortgage_schedule(loan_amount, annual_rate, years)
    monthly_total = payment_pi + (taxes / 12.0) + (insurance / 12.0) + pmi + hoa

    return {
        "inputs": inputs,
        "assumptions": ["Fixed-rate fully amortizing loan."],
        "results": {
            "monthly_principal_interest": round(payment_pi, 2),
            "monthly_total_payment": round(monthly_total, 2),
            "total_interest": round(total_interest, 2),
            "total_cost": round(loan_amount + total_interest + taxes * years + insurance * years + (pmi + hoa) * years * 12, 2),
        },
        "breakdown": {
            "monthly": {
                "principal_interest": round(payment_pi, 2),
                "property_tax": round(taxes / 12.0, 2),
                "insurance": round(insurance / 12.0, 2),
                "pmi": round(pmi, 2),
                "hoa": round(hoa, 2),
            }
        },
        "schedule": schedule,
        "warnings": [],
    }


def _compound_interest_handler(inputs: JSON) -> JSON:
    p = float(inputs["initial_principal"])
    r = float(inputs["annual_rate"]) / 100.0
    n = int(inputs["compoundings_per_year"])
    years = float(inputs["years"])
    contrib = float(inputs.get("periodic_contribution", 0.0))
    periods = int(n * years)

    fv_principal = p * ((1 + r / n) ** periods)
    if r == 0:
        fv_contrib = contrib * periods
    else:
        fv_contrib = contrib * ((((1 + r / n) ** periods) - 1) / (r / n))
    fv = fv_principal + fv_contrib
    contributed = p + contrib * periods

    timeline = []
    for yr in range(1, int(math.floor(years)) + 1):
        pt = int(yr * n)
        val = p * ((1 + r / n) ** pt)
        if r == 0:
            val += contrib * pt
        else:
            val += contrib * ((((1 + r / n) ** pt) - 1) / (r / n))
        timeline.append({"year": yr, "value": round(val, 2)})

    return {
        "inputs": inputs,
        "results": {
            "future_value": round(fv, 2),
            "total_contributed": round(contributed, 2),
            "investment_gains": round(fv - contributed, 2),
        },
        "schedule": timeline,
        "warnings": [],
    }


def _bmi_handler(inputs: JSON) -> JSON:
    height_m = float(inputs["height_m"])
    weight_kg = float(inputs["weight_kg"])
    bmi = weight_kg / (height_m**2)
    if bmi < 18.5:
        category = "underweight"
    elif bmi < 25:
        category = "normal"
    elif bmi < 30:
        category = "overweight"
    else:
        category = "obesity"
    min_w = 18.5 * (height_m**2)
    max_w = 24.9 * (height_m**2)
    return {
        "inputs": inputs,
        "results": {
            "bmi": round(bmi, 2),
            "category": category,
            "healthy_weight_range_kg": [round(min_w, 1), round(max_w, 1)],
        },
        "warnings": [],
    }


def _tip_handler(inputs: JSON) -> JSON:
    bill = float(inputs["bill_amount"])
    tip_rate = float(inputs["tip_percent"]) / 100.0
    people = int(inputs.get("people", 1))
    tip = bill * tip_rate
    total = bill + tip
    return {
        "inputs": inputs,
        "results": {
            "tip_amount": round(tip, 2),
            "total_amount": round(total, 2),
            "per_person": round(total / people, 2),
        },
        "warnings": [],
    }


def _percentage_handler(inputs: JSON) -> JSON:
    mode = inputs["mode"]
    a = float(inputs["value_a"])
    b = float(inputs.get("value_b", 0.0))
    if mode == "percent_of":
        result = a * b / 100.0
    elif mode == "is_what_percent":
        if b == 0:
            return _error_response("invalid_input", "value_b must be non-zero for is_what_percent")
        result = (a / b) * 100.0
    else:
        if a == 0:
            return _error_response("invalid_input", "value_a must be non-zero for percent_change")
        result = ((b - a) / a) * 100.0
    return {"inputs": inputs, "results": {"mode": mode, "value": round(result, 4)}, "warnings": []}


def _cash_out_refinance_handler(inputs: JSON) -> JSON:
    cur_payment, cur_interest, _ = _full_mortgage_schedule(float(inputs["current_balance"]), float(inputs["current_rate"]), int(inputs["current_years_remaining"]))
    new_principal = float(inputs["current_balance"]) + float(inputs.get("cash_out_amount", 0.0)) + float(inputs.get("closing_costs", 0.0))
    new_payment, new_interest, _ = _full_mortgage_schedule(new_principal, float(inputs["new_rate"]), int(inputs["new_term_years"]))
    return {
        "inputs": inputs,
        "results": {
            "current_payment_pi": round(cur_payment, 2),
            "new_payment_pi": round(new_payment, 2),
            "monthly_delta": round(new_payment - cur_payment, 2),
            "lifetime_interest_delta": round(new_interest - cur_interest, 2),
            "cash_received": round(float(inputs.get("cash_out_amount", 0.0)), 2),
        },
        "warnings": [],
    }


def _mortgage_buydown_handler(inputs: JSON) -> JSON:
    principal = float(inputs["loan_amount"])
    base_rate = float(inputs["base_rate"])
    reduced_rate = float(inputs["reduced_rate"])
    years = int(inputs["loan_term_years"])
    points = float(inputs["points_paid"])
    base_payment, _, _ = _full_mortgage_schedule(principal, base_rate, years)
    reduced_payment, _, _ = _full_mortgage_schedule(principal, reduced_rate, years)
    upfront_cost = principal * (points / 100.0)
    monthly_savings = base_payment - reduced_payment
    break_even = (upfront_cost / monthly_savings) if monthly_savings > 0 else None
    return {
        "inputs": inputs,
        "results": {
            "upfront_cost": round(upfront_cost, 2),
            "monthly_savings": round(monthly_savings, 2),
            "break_even_months": round(break_even, 1) if break_even is not None else None,
        },
        "warnings": [] if break_even is not None else ["Reduced rate does not produce monthly savings."],
    }


def _rental_property_handler(inputs: JSON) -> JSON:
    annual_rent = float(inputs["monthly_rent"]) * 12
    annual_exp = float(inputs.get("annual_operating_expenses", 0.0))
    vacancy = float(inputs.get("vacancy_rate", 0.0)) / 100.0
    noi = annual_rent * (1 - vacancy) - annual_exp
    property_value = float(inputs["property_value"])
    debt_service = float(inputs.get("annual_debt_service", 0.0))
    cash_flow = noi - debt_service
    cash_invested = float(inputs.get("cash_invested", 0.0))
    coc = (cash_flow / cash_invested * 100.0) if cash_invested > 0 else None
    return {
        "inputs": inputs,
        "results": {
            "noi": round(noi, 2),
            "cap_rate_percent": round((noi / property_value) * 100.0, 3),
            "annual_cash_flow": round(cash_flow, 2),
            "cash_on_cash_return_percent": round(coc, 3) if coc is not None else None,
        },
        "warnings": [] if coc is not None else ["cash_invested is 0; cash-on-cash return omitted."],
    }


def _vo2_max_handler(inputs: JSON) -> JSON:
    resting = float(inputs["resting_hr"])
    max_hr = float(inputs["max_hr"])
    vo2 = 15.3 * (max_hr / resting)
    return {"inputs": inputs, "results": {"vo2_max": round(vo2, 2), "units": "ml/kg/min"}, "warnings": []}


def _race_predictor_handler(inputs: JSON) -> JSON:
    known_distance = float(inputs["known_distance_km"])
    known_time = float(inputs["known_time_minutes"])
    exponent = 1.06
    target_distances = [5, 10, 21.097, 42.195]
    preds = []
    for dist in target_distances:
        t = known_time * ((dist / known_distance) ** exponent)
        preds.append({"distance_km": dist, "predicted_minutes": round(t, 2)})
    return {"inputs": inputs, "assumptions": ["Riegel exponent 1.06"], "results": {"predictions": preds}, "warnings": []}


def _target_heart_rate_handler(inputs: JSON) -> JSON:
    age = int(inputs["age"])
    resting = float(inputs["resting_hr"])
    intensity_low = float(inputs["intensity_low"])
    intensity_high = float(inputs["intensity_high"])
    workout_minutes = int(inputs["workout_minutes"])
    max_hr = 220 - age
    hrr = max_hr - resting
    low = resting + hrr * (intensity_low / 100.0)
    high = resting + hrr * (intensity_high / 100.0)
    return {
        "inputs": inputs,
        "results": {
            "target_zone_bpm": [round(low), round(high)],
            "time_in_zone_minutes": workout_minutes,
        },
        "warnings": [] if intensity_low <= intensity_high else ["intensity_low greater than intensity_high."],
    }


def _menstrual_cycle_handler(inputs: JSON) -> JSON:
    last_period = date.fromisoformat(inputs["last_period_start"])
    min_cycle = int(inputs["min_cycle_length"])
    max_cycle = int(inputs["max_cycle_length"])
    next_start_earliest = last_period + timedelta(days=min_cycle)
    next_start_latest = last_period + timedelta(days=max_cycle)
    fertile_start = next_start_earliest - timedelta(days=19)
    fertile_end = next_start_latest - timedelta(days=10)
    return {
        "inputs": inputs,
        "assumptions": ["Fertile window estimated as days 10-19 before next period."],
        "results": {
            "next_period_window": [next_start_earliest.isoformat(), next_start_latest.isoformat()],
            "fertile_window": [fertile_start.isoformat(), fertile_end.isoformat()],
        },
        "warnings": [],
    }


def _medication_schedule_handler(inputs: JSON) -> JSON:
    interval_a = int(inputs["med_a_every_hours"])
    interval_b = int(inputs["med_b_every_hours"])
    horizon = int(inputs["horizon_hours"])
    overlap_window = int(inputs.get("overlap_window_minutes", 30))
    overlaps = []
    for ta in range(0, horizon + 1, interval_a):
        for tb in range(0, horizon + 1, interval_b):
            if abs((ta - tb) * 60) <= overlap_window:
                overlaps.append({"med_a_hour": ta, "med_b_hour": tb, "delta_minutes": abs((ta - tb) * 60)})
    risk = "high" if len(overlaps) >= 4 else "moderate" if overlaps else "low"
    return {"inputs": inputs, "results": {"overlaps": overlaps, "risk_level": risk}, "warnings": ["Informational only, not medical advice."]}


def _matrix_calculator_handler(inputs: JSON) -> JSON:
    a = float(inputs["m11"])
    b = float(inputs["m12"])
    c = float(inputs["m21"])
    d = float(inputs["m22"])
    det = a * d - b * c
    trace = a + d
    disc = trace**2 - 4 * det
    if disc >= 0:
        e1 = (trace + math.sqrt(disc)) / 2
        e2 = (trace - math.sqrt(disc)) / 2
    else:
        real = trace / 2
        imag = math.sqrt(-disc) / 2
        e1 = f"{real:.4f}+{imag:.4f}i"
        e2 = f"{real:.4f}-{imag:.4f}i"

    inverse = None
    warnings: list[str] = []
    if det != 0:
        inverse = [[d / det, -b / det], [-c / det, a / det]]
    else:
        warnings.append("Matrix is singular; inverse does not exist.")
    return {"inputs": inputs, "results": {"determinant": round(det, 6), "inverse": inverse, "eigenvalues": [e1, e2]}, "warnings": warnings}


def _unit_dimension_checker_handler(inputs: JSON) -> JSON:
    left = [int(inputs["left_kg"]), int(inputs["left_m"]), int(inputs["left_s"])]
    right = [int(inputs["right_kg"]), int(inputs["right_m"]), int(inputs["right_s"])]
    diffs = [l - r for l, r in zip(left, right)]
    return {
        "inputs": inputs,
        "results": {
            "is_consistent": diffs == [0, 0, 0],
            "delta_exponents": {"kg": diffs[0], "m": diffs[1], "s": diffs[2]},
        },
        "warnings": [],
    }


def _linear_regression_handler(inputs: JSON) -> JSON:
    xs = [float(x.strip()) for x in inputs["x_values_csv"].split(",") if x.strip()]
    ys = [float(y.strip()) for y in inputs["y_values_csv"].split(",") if y.strip()]
    if len(xs) != len(ys) or len(xs) < 2:
        return _error_response("invalid_input", "x_values_csv and y_values_csv must have the same length >= 2")
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    den = sum((x - x_mean) ** 2 for x in xs)
    if den == 0:
        return _error_response("invalid_input", "x values must not all be identical")
    slope = num / den
    intercept = y_mean - slope * x_mean
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - (ss_res / ss_tot) if ss_tot else 1.0
    return {"inputs": inputs, "results": {"slope": round(slope, 6), "intercept": round(intercept, 6), "r_squared": round(r2, 6)}, "warnings": []}


def _base_converter_handler(inputs: JSON) -> JSON:
    value = int(inputs["decimal_value"])
    return {
        "inputs": inputs,
        "results": {
            "binary": format(value, "b"),
            "octal": format(value, "o"),
            "hex": format(value, "X"),
        },
        "warnings": [],
    }


def _contractor_vs_employee_handler(inputs: JSON) -> JSON:
    salary = float(inputs["employee_base_pay"])
    benefits = float(inputs.get("employee_benefits_percent", 0.0)) / 100.0
    payroll_tax = float(inputs.get("employee_payroll_tax_percent", 0.0)) / 100.0
    contractor_rate = float(inputs["contractor_hourly_rate"])
    annual_hours = float(inputs["annual_hours"])

    employee_total = salary * (1 + benefits + payroll_tax)
    contractor_total = contractor_rate * annual_hours
    return {
        "inputs": inputs,
        "results": {
            "employee_total_cost": round(employee_total, 2),
            "contractor_total_cost": round(contractor_total, 2),
            "delta_contract_minus_employee": round(contractor_total - employee_total, 2),
        },
        "warnings": [],
    }


def _cas_handler(inputs: JSON) -> JSON:
    payload = inputs["payload"]
    expr = payload.get("expression") or payload.get("latex")
    if not isinstance(expr, str) or not expr.strip():
        return _error_response("invalid_input", "payload.expression or payload.latex must be a non-empty string")

    sanitized = expr.replace("^", "**")
    allowed = {"__builtins__": {}}
    namespace = {"pi": math.pi, "e": math.e, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log}
    try:
        value = eval(sanitized, allowed, namespace)
    except Exception as exc:  # noqa: BLE001
        return _error_response("evaluation_error", f"Unable to evaluate expression: {exc}")
    return {
        "results": {"expression": expr, "numeric_result": value},
        "warnings": ["CAS mode supports numeric-safe subset, not full symbolic algebra."],
    }


def _rpn_handler(inputs: JSON) -> JSON:
    payload = inputs["payload"]
    tokens = payload.get("tokens", [])
    if not isinstance(tokens, list):
        return _error_response("invalid_input", "payload.tokens must be a list")
    stack: list[float] = []
    for token in tokens:
        if isinstance(token, (int, float)):
            stack.append(float(token))
            continue
        if token in {"+", "-", "*", "/"}:
            if len(stack) < 2:
                return _error_response("invalid_input", "RPN stack underflow")
            b = stack.pop()
            a = stack.pop()
            if token == "+":
                stack.append(a + b)
            elif token == "-":
                stack.append(a - b)
            elif token == "*":
                stack.append(a * b)
            else:
                if b == 0:
                    return _error_response("invalid_input", "division by zero in RPN")
                stack.append(a / b)
        else:
            return _error_response("invalid_input", f"unsupported token: {token}")

    return {"results": {"stack": [round(v, 10) for v in stack], "top": stack[-1] if stack else None}, "warnings": []}


# Source-of-truth calculator metadata from the provided registry seed list.
CALCULATOR_META: list[JSON] = [
    {"slug": "mortgage_payment", "name": "Mortgage Payment Calculator", "category": "finance", "description": "Calculate monthly mortgage payments including principal, interest, taxes, insurance, PMI, and HOA. View full amortization schedule.", "route": "/finance/mortgage", "type": "form"},
    {"slug": "compound_interest", "name": "Compound Interest Calculator", "category": "finance", "description": "Calculate how your savings or investments grow over time with compound interest. See the effect of different compounding frequencies.", "route": "/finance/compound-interest", "type": "form"},
    {"slug": "bmi", "name": "BMI Calculator", "category": "health", "description": "Calculate your Body Mass Index (BMI) using height and weight. Provides BMI category and healthy weight range.", "route": "/health/bmi", "type": "form"},
    {"slug": "tip_calculator", "name": "Tip Calculator", "category": "travel", "description": "Calculate restaurant tips and split the bill among multiple people. Supports custom tip percentages.", "route": "/travel/tip", "type": "form"},
    {"slug": "percentage", "name": "Percentage Calculator", "category": "math", "description": "Perform common percentage operations: find a percentage of a value, calculate what percentage one number is of another, and find percentage change.", "route": "/math/percentage", "type": "form"},
    {"slug": "cash_out_refinance", "name": "Cash-Out Refinance Comparison Calculator", "category": "finance", "description": "Compare current mortgage vs cash-out refinance payment and long-term cost.", "route": "/finance/cash-out-refinance", "type": "form"},
    {"slug": "mortgage_buydown", "name": "Mortgage Buydown Calculator", "category": "finance", "description": "Estimate rate buydown savings and break-even timeline from points paid.", "route": "/finance/mortgage-buydown", "type": "form"},
    {"slug": "rental_property", "name": "Rental Property Calculator", "category": "finance", "description": "Evaluate rental property metrics including NOI, cap rate, cash flow, and cash-on-cash return.", "route": "/finance/rental-property", "type": "form"},
    {"slug": "vo2_max", "name": "VO2 Max Estimator", "category": "health", "description": "Estimate VO2 max from resting and maximum heart rate.", "route": "/health/vo2-max", "type": "form"},
    {"slug": "race_predictor", "name": "Running Race Predictor", "category": "health", "description": "Predict race times at common distances using a known result and Riegel scaling.", "route": "/health/race-predictor", "type": "form"},
    {"slug": "target_heart_rate", "name": "Target Heart Rate Workout Planner", "category": "health", "description": "Compute target training zone and total time in zone for a planned workout.", "route": "/health/target-heart-rate", "type": "form"},
    {"slug": "menstrual_cycle", "name": "Menstrual Cycle Tracker", "category": "health", "description": "Estimate next period and fertile windows using min/max cycle lengths for irregular cycles.", "route": "/health/menstrual-cycle", "type": "form"},
    {"slug": "medication_schedule", "name": "Medication Schedule Checker", "category": "health", "description": "Check timing overlap risk between two repeating medication schedules.", "route": "/health/medication-schedule", "type": "form"},
    {"slug": "matrix_calculator", "name": "Matrix Calculator", "category": "math", "description": "Compute determinant, inverse, and eigenvalues for a 2x2 matrix.", "route": "/math/matrix-calculator", "type": "form"},
    {"slug": "unit_dimension_checker", "name": "Unit Dimension Checker", "category": "math", "description": "Verify dimensional consistency by comparing exponents of kg, m, and s on both sides.", "route": "/math/unit-dimension-checker", "type": "form"},
    {"slug": "linear_regression", "name": "Linear Regression Calculator", "category": "math", "description": "Fit a simple linear regression line and return slope, intercept, and R².", "route": "/math/linear-regression", "type": "form"},
    {"slug": "base_converter", "name": "Number Base Converter", "category": "math", "description": "Convert a decimal integer into binary, octal, and hexadecimal formats.", "route": "/math/base-converter", "type": "form"},
    {"slug": "contractor_vs_employee", "name": "Contractor vs Employee Cost Calculator", "category": "business", "description": "Compare annual employer cost for W-2 employee vs contractor arrangement.", "route": "/business/contractor-vs-employee", "type": "form"},
    {"slug": "cas", "name": "Math Workspace (CAS)", "category": "math", "description": "General-purpose computational math environment with symbolic algebra, calculus, equation solving, and interactive plotting. Supports LaTeX input.", "route": "/math/cas", "type": "cas"},
    {"slug": "rpn", "name": "RPN Calculator", "category": "math", "description": "42S-style scientific RPN calculator with a four-level stack, programmable commands, and shareable sessions.", "route": "/math/rpn-calculator", "type": "rpn"},
]


SCHEMAS: dict[str, JSON] = {
    "mortgage_payment": {"type": "object", "required": ["loan_amount", "annual_rate", "loan_term_years"], "properties": {"loan_amount": _number_field("Loan Amount", minimum=1, help_text="Principal balance."), "annual_rate": _number_field("Annual Interest Rate", minimum=0, help_text="Nominal annual rate in percent."), "loan_term_years": _int_field("Loan Term Years", minimum=1, help_text="Amortization term in years."), "annual_property_tax": _number_field("Annual Property Tax", default=0, minimum=0, help_text="Annual tax."), "annual_insurance": _number_field("Annual Insurance", default=0, minimum=0, help_text="Annual homeowners insurance."), "monthly_pmi": _number_field("Monthly PMI", default=0, minimum=0, help_text="Monthly PMI."), "monthly_hoa": _number_field("Monthly HOA", default=0, minimum=0, help_text="Monthly HOA fee.")}, "additionalProperties": False},
    "compound_interest": {"type": "object", "required": ["initial_principal", "annual_rate", "compoundings_per_year", "years"], "properties": {"initial_principal": _number_field("Initial Principal", minimum=0, help_text="Starting amount."), "annual_rate": _number_field("Annual Rate", help_text="Annual return in percent."), "compoundings_per_year": _int_field("Compounds Per Year", minimum=1, help_text="Compounding frequency."), "years": _number_field("Years", minimum=0, help_text="Duration."), "periodic_contribution": _number_field("Contribution Per Compounding Period", default=0, minimum=0, help_text="Contribution added once per compounding period.")}, "additionalProperties": False},
    "bmi": {"type": "object", "required": ["height_m", "weight_kg"], "properties": {"height_m": _number_field("Height (m)", minimum=0.5, maximum=3.0, help_text="Height in meters."), "weight_kg": _number_field("Weight (kg)", minimum=1, maximum=500, help_text="Weight in kilograms.")}, "additionalProperties": False},
    "tip_calculator": {"type": "object", "required": ["bill_amount", "tip_percent"], "properties": {"bill_amount": _number_field("Bill", minimum=0, help_text="Pre-tip bill amount."), "tip_percent": _number_field("Tip %", minimum=0, help_text="Tip rate percentage."), "people": _int_field("People", default=1, minimum=1, help_text="Number of people splitting bill.")}, "additionalProperties": False},
    "percentage": {"type": "object", "required": ["mode", "value_a"], "properties": {"mode": {"type": "string", "enum": ["percent_of", "is_what_percent", "percent_change"], "label": "Mode", "help": "Percentage operation mode."}, "value_a": _number_field("Value A", help_text="Primary value."), "value_b": _number_field("Value B", default=0, help_text="Secondary value."),}, "additionalProperties": False},
    "cash_out_refinance": {"type": "object", "required": ["current_balance", "current_rate", "current_years_remaining", "new_rate", "new_term_years"], "properties": {"current_balance": _number_field("Current Balance", minimum=1, help_text="Current principal."), "current_rate": _number_field("Current Rate", minimum=0, help_text="Current annual rate."), "current_years_remaining": _int_field("Current Years Remaining", minimum=1, help_text="Remaining amortization."), "cash_out_amount": _number_field("Cash Out", default=0, minimum=0, help_text="Extra cash taken."), "closing_costs": _number_field("Closing Costs", default=0, minimum=0, help_text="Refi closing costs."), "new_rate": _number_field("New Rate", minimum=0, help_text="New annual rate."), "new_term_years": _int_field("New Term", minimum=1, help_text="New term in years.")}, "additionalProperties": False},
    "mortgage_buydown": {"type": "object", "required": ["loan_amount", "base_rate", "reduced_rate", "loan_term_years", "points_paid"], "properties": {"loan_amount": _number_field("Loan Amount", minimum=1, help_text="Principal."), "base_rate": _number_field("Base Rate", minimum=0, help_text="Unbought rate."), "reduced_rate": _number_field("Reduced Rate", minimum=0, help_text="Bought-down rate."), "loan_term_years": _int_field("Term Years", minimum=1, help_text="Loan term."), "points_paid": _number_field("Points Paid", minimum=0, help_text="Points as percent of principal.")}, "additionalProperties": False},
    "rental_property": {"type": "object", "required": ["property_value", "monthly_rent"], "properties": {"property_value": _number_field("Property Value", minimum=1, help_text="Market value."), "monthly_rent": _number_field("Monthly Rent", minimum=0, help_text="Gross monthly rent."), "vacancy_rate": _number_field("Vacancy Rate", default=0, minimum=0, maximum=100, help_text="Vacancy rate percent."), "annual_operating_expenses": _number_field("Operating Expenses", default=0, minimum=0, help_text="Annual operating expenses."), "annual_debt_service": _number_field("Debt Service", default=0, minimum=0, help_text="Annual debt service."), "cash_invested": _number_field("Cash Invested", default=0, minimum=0, help_text="Total initial cash invested.")}, "additionalProperties": False},
    "vo2_max": {"type": "object", "required": ["resting_hr", "max_hr"], "properties": {"resting_hr": _number_field("Resting HR", minimum=20, maximum=140, help_text="Resting heart rate."), "max_hr": _number_field("Max HR", minimum=80, maximum=240, help_text="Maximum heart rate.")}, "additionalProperties": False},
    "race_predictor": {"type": "object", "required": ["known_distance_km", "known_time_minutes"], "properties": {"known_distance_km": _number_field("Known Distance", minimum=0.1, help_text="Known race distance in km."), "known_time_minutes": _number_field("Known Time", minimum=0.1, help_text="Known race time in minutes.")}, "additionalProperties": False},
    "target_heart_rate": {"type": "object", "required": ["age", "resting_hr", "intensity_low", "intensity_high", "workout_minutes"], "properties": {"age": _int_field("Age", minimum=10, maximum=100, help_text="Age in years."), "resting_hr": _number_field("Resting HR", minimum=20, maximum=140, help_text="Resting heart rate."), "intensity_low": _number_field("Low Intensity", minimum=30, maximum=100, help_text="Low intensity % of HRR."), "intensity_high": _number_field("High Intensity", minimum=30, maximum=100, help_text="High intensity % of HRR."), "workout_minutes": _int_field("Workout Minutes", minimum=1, help_text="Planned minutes in zone.")}, "additionalProperties": False},
    "menstrual_cycle": {"type": "object", "required": ["last_period_start", "min_cycle_length", "max_cycle_length"], "properties": {"last_period_start": {"type": "string", "label": "Last Period Start", "help": "ISO date (YYYY-MM-DD).", "minLength": 10}, "min_cycle_length": _int_field("Min Cycle Length", minimum=15, maximum=60, help_text="Minimum cycle days."), "max_cycle_length": _int_field("Max Cycle Length", minimum=15, maximum=60, help_text="Maximum cycle days.")}, "additionalProperties": False},
    "medication_schedule": {"type": "object", "required": ["med_a_every_hours", "med_b_every_hours", "horizon_hours"], "properties": {"med_a_every_hours": _int_field("Medication A Interval", minimum=1, help_text="Hours between doses."), "med_b_every_hours": _int_field("Medication B Interval", minimum=1, help_text="Hours between doses."), "horizon_hours": _int_field("Horizon", minimum=1, help_text="Schedule horizon in hours."), "overlap_window_minutes": _int_field("Overlap Window", default=30, minimum=0, help_text="Minutes considered overlap.")}, "additionalProperties": False},
    "matrix_calculator": {"type": "object", "required": ["m11", "m12", "m21", "m22"], "properties": {"m11": _number_field("m11", help_text="Matrix cell"), "m12": _number_field("m12", help_text="Matrix cell"), "m21": _number_field("m21", help_text="Matrix cell"), "m22": _number_field("m22", help_text="Matrix cell")}, "additionalProperties": False},
    "unit_dimension_checker": {"type": "object", "required": ["left_kg", "left_m", "left_s", "right_kg", "right_m", "right_s"], "properties": {"left_kg": _int_field("Left kg", help_text="kg exponent left."), "left_m": _int_field("Left m", help_text="m exponent left."), "left_s": _int_field("Left s", help_text="s exponent left."), "right_kg": _int_field("Right kg", help_text="kg exponent right."), "right_m": _int_field("Right m", help_text="m exponent right."), "right_s": _int_field("Right s", help_text="s exponent right.")}, "additionalProperties": False},
    "linear_regression": {"type": "object", "required": ["x_values_csv", "y_values_csv"], "properties": {"x_values_csv": {"type": "string", "label": "X values", "help": "Comma-separated numeric list.", "minLength": 3}, "y_values_csv": {"type": "string", "label": "Y values", "help": "Comma-separated numeric list.", "minLength": 3}}, "additionalProperties": False},
    "base_converter": {"type": "object", "required": ["decimal_value"], "properties": {"decimal_value": _int_field("Decimal Integer", minimum=0, help_text="Integer value to convert.")}, "additionalProperties": False},
    "contractor_vs_employee": {"type": "object", "required": ["employee_base_pay", "contractor_hourly_rate", "annual_hours"], "properties": {"employee_base_pay": _number_field("Employee Base Pay", minimum=0, help_text="Annual base pay."), "employee_benefits_percent": _number_field("Benefits %", default=0, minimum=0, help_text="Benefits load as percentage."), "employee_payroll_tax_percent": _number_field("Payroll Tax %", default=0, minimum=0, help_text="Employer payroll tax percentage."), "contractor_hourly_rate": _number_field("Contractor Hourly Rate", minimum=0, help_text="Contractor hourly bill rate."), "annual_hours": _number_field("Annual Hours", minimum=0, help_text="Annual contractor billable hours.")}, "additionalProperties": False},
}


def _interactive_schema(name: str, tool_type: str) -> JSON:
    return {
        "type": "object",
        "title": f"{name} Payload",
        "required": ["payload"],
        "properties": {
            "payload": {
                "type": "object",
                "label": "Payload",
                "help": f"Structured request payload for the {tool_type} workspace.",
                "additionalProperties": True,
            },
        },
        "additionalProperties": False,
    }


HANDLERS: dict[str, Callable[[JSON], JSON]] = {
    "mortgage_payment": _mortgage_payment_handler,
    "compound_interest": _compound_interest_handler,
    "bmi": _bmi_handler,
    "tip_calculator": _tip_handler,
    "percentage": _percentage_handler,
    "cash_out_refinance": _cash_out_refinance_handler,
    "mortgage_buydown": _mortgage_buydown_handler,
    "rental_property": _rental_property_handler,
    "vo2_max": _vo2_max_handler,
    "race_predictor": _race_predictor_handler,
    "target_heart_rate": _target_heart_rate_handler,
    "menstrual_cycle": _menstrual_cycle_handler,
    "medication_schedule": _medication_schedule_handler,
    "matrix_calculator": _matrix_calculator_handler,
    "unit_dimension_checker": _unit_dimension_checker_handler,
    "linear_regression": _linear_regression_handler,
    "base_converter": _base_converter_handler,
    "contractor_vs_employee": _contractor_vs_employee_handler,
    "cas": _cas_handler,
    "rpn": _rpn_handler,
}


CALCULATOR_REGISTRY: dict[str, JSON] = {}
for meta in CALCULATOR_META:
    slug = meta["slug"]
    tool_type = meta["type"]
    schema = SCHEMAS[slug] if tool_type == "form" else _interactive_schema(meta["name"], tool_type)
    CALCULATOR_REGISTRY[slug] = {
        "meta": meta,
        "schema": schema,
        "handler": HANDLERS[slug],
    }


def list_calculators(category: str | None = None) -> list[JSON]:
    items = [entry["meta"] for entry in CALCULATOR_REGISTRY.values()]
    if category is None:
        return sorted(items, key=lambda x: x["slug"])
    return sorted([i for i in items if i["category"] == category], key=lambda x: x["slug"])


def get_calculator_schema(slug: str) -> JSON:
    entry = CALCULATOR_REGISTRY.get(slug)
    if entry is None:
        return _error_response("unknown_slug", f"Unknown calculator slug: {slug}", {"slug": slug})
    return {"slug": slug, "schema": entry["schema"]}

def calculate(slug: str, inputs: dict[str, Any]) -> JSON:
    entry = CALCULATOR_REGISTRY.get(slug)
    if entry is None:
        return _error_response("unknown_slug", f"Unknown calculator slug: {slug}", {"slug": slug})

    try:
        _validate_against_schema(entry["schema"], inputs)
    except CalculatorValidationError as exc:
        message = str(exc)
        code = "missing_required_inputs" if message.startswith("missing required") else "invalid_input_type"
        return _error_response(code, message, {"slug": slug})

    try:
        result = entry["handler"](inputs)
    except ValueError as exc:
        return _error_response("invalid_input", str(exc), {"slug": slug})
    if isinstance(result, dict) and "error" in result:
        return result
    return {"slug": slug, "result": result}
