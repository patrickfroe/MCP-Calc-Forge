from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import calcforge.calculators as calculators
import pytest
from importlib.util import find_spec


def test_list_calculators_returns_standardized_metadata() -> None:
    entries = calculators.list_calculators()

    assert entries
    assert all(
        set(entry.keys()) == {"slug", "name", "category", "description", "route", "type"}
        for entry in entries
    )


def test_get_calculator_schema_by_slug() -> None:
    schema_payload = calculators._get_calculator_schema("add")

    assert schema_payload["calculator"] == "add"
    assert "a" in schema_payload["schema"]
    assert schema_payload["schema"]["a"]["required"] is True


def test_get_calculator_schema_returns_json_error_for_unknown_tool() -> None:
    schema_payload = calculators._get_calculator_schema("unknown")

    assert schema_payload["error"]["code"] == "unknown_slug"
    assert schema_payload["error"]["details"]["slug"] == "unknown"


CALCULATION_SCENARIOS = {
    "add": {"inputs": {"a": 2, "b": 3}, "expected": 5},
    "subtract": {"inputs": {"a": 9, "b": 4}, "expected": 5},
    "multiply": {"inputs": {"a": 3, "b": 7}, "expected": 21},
    "divide": {"inputs": {"a": 8, "b": 2}, "expected": 4.0},
    "percentage_of": {"inputs": {"value": 200, "percent": 12.5}, "expected": 25.0},
    "to_fraction": {"inputs": {"value": 0.5}, "expected": "1/2"},
    "circle_area": {"inputs": {"radius": 2}, "expected": pytest.approx(12.566370614359172)},
    "circle_circumference": {"inputs": {"radius": 2}, "expected": pytest.approx(12.566370614359172)},
    "rectangle_area": {"inputs": {"a": 3, "b": 4}, "expected": 12},
    "rectangle_perimeter": {"inputs": {"a": 3, "b": 4}, "expected": 14},
    "triangle_area": {"inputs": {"base": 10, "height": 5}, "expected": 25.0},
    "sphere_volume": {"inputs": {"radius": 3}, "expected": pytest.approx(113.09733552923254)},
    "cylinder_volume": {"inputs": {"radius": 3, "height": 2}, "expected": pytest.approx(56.548667764616276)},
    "cone_volume": {"inputs": {"radius": 3, "height": 2}, "expected": pytest.approx(18.849555921538755)},
    "pyramid_volume": {"inputs": {"base_area": 9, "height": 6}, "expected": 18.0},
    "solve_quadratic": {"inputs": {"a": 1, "b": -3, "c": 2}, "expected": [1, 2], "requires_sympy": True},
    "solve_linear_system": {
        "inputs": {"equations": ["x + y = 3", "x - y = 1"], "variables": ["x", "y"]},
        "expected": {"x": 2, "y": 1},
        "requires_sympy": True,
    },
    "factor_polynomial": {"inputs": {"expr": "x**2-4"}, "expected": "(x - 2)*(x + 2)", "requires_sympy": True},
    "find_roots": {"inputs": {"expr": "x**2 - 4"}, "expected": [-2, 2], "requires_sympy": True},
    "mean": {"inputs": {"numbers": [1, 2, 3, 4]}, "expected": 2.5},
    "std_dev": {"inputs": {"numbers": [1, 2, 3, 4]}, "expected": pytest.approx(1.118033988749895)},
    "gcd": {"inputs": {"a": 18, "b": 24}, "expected": 6},
    "lcm": {"inputs": {"a": 6, "b": 8}, "expected": 24},
    "prime_factors": {"inputs": {"n": 84}, "expected": [2, 2, 3, 7]},
    "log_base": {"inputs": {"x": 8, "base": 2}, "expected": 3.0},
    "power": {"inputs": {"base": 2, "exponent": 5}, "expected": 32.0},
    "to_scientific_notation": {"inputs": {"x": 1230, "precision": 3}, "expected": "1.230e+03"},
    "to_binary": {"inputs": {"n": 5}, "expected": "0b101"},
    "from_binary": {"inputs": {"bin_str": "101"}, "expected": 5},
}


def test_calculation_scenarios_cover_all_calculators() -> None:
    calculator_slugs = {entry["slug"] for entry in calculators.list_calculators()}
    scenario_slugs = set(CALCULATION_SCENARIOS)

    assert scenario_slugs == calculator_slugs


@pytest.mark.parametrize("slug,scenario", CALCULATION_SCENARIOS.items())
def test_full_flow_list_schema_calculate_for_each_calculator(slug: str, scenario: dict[str, object]) -> None:
    listed_slugs = {entry["slug"] for entry in calculators.list_calculators()}
    assert slug in listed_slugs

    schema_payload = calculators._get_calculator_schema(slug)
    assert schema_payload["calculator"] == slug
    assert schema_payload["schema"]

    inputs = scenario["inputs"]
    result_payload = calculators.calculate(slug, inputs)

    if scenario.get("requires_sympy") and find_spec("sympy") is None:
        assert result_payload["error"]["code"] == "calculation_error"
        return

    assert result_payload["calculator"] == slug
    assert result_payload["result"] == scenario["expected"]
    assert result_payload["prefilled_url"].startswith("https://calcforge.app/calculator?")
