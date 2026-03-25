from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import calcforge.calculators as calculators
import pytest


def test_list_calculators_with_category_filter() -> None:
    arithmetic_only = calculators.list_calculators(category="arithmetic")

    assert arithmetic_only
    assert all(entry["category"] == "arithmetic" for entry in arithmetic_only)
    assert all(entry["slug"] for entry in arithmetic_only)


def test_calculate_returns_result_and_prefilled_url() -> None:
    payload = calculators.calculate("add", {"a": 2, "b": 5})

    assert payload["result"] == 7
    assert payload["prefilled_url"].startswith("https://calcforge.app/calculator?")
    assert "calculator=add" in payload["prefilled_url"]
    assert payload["calculator"] == "add"


def test_calculate_validation_errors() -> None:
    try:
        calculators.calculate("unknown", {})
    except ValueError as error:
        assert str(error) == "Unknown calculator slug: unknown"
    else:
        raise AssertionError("Expected ValueError for unknown slug")

    try:
        calculators.calculate("add", {"a": 1})
    except ValueError as error:
        assert str(error) == "Missing required input: b"
    else:
        raise AssertionError("Expected ValueError for missing required input")

    try:
        calculators.calculate("add", {"a": "1", "b": 2})
    except ValueError as error:
        assert str(error) == "Invalid input type for 'a': expected number"
    else:
        raise AssertionError("Expected ValueError for invalid input type")


def test_calculate_cas_numeric_and_handoff() -> None:
    pytest.importorskip("sympy")
    response = calculators.calculate_cas(["2+3", "x+1"])

    assert response["mode"] == "headless_numeric"
    assert response["results"][0]["status"] == "ok"
    assert response["results"][0]["result"].startswith("5")
    assert response["results"][1]["status"] == "handoff"
    assert response["results"][1]["handoff_url"].startswith("https://calcforge.app/cas?")


def test_calculate_cas_headless_alias() -> None:
    pytest.importorskip("sympy")
    assert calculators.calculate_cas_headless(["3*3"]) == calculators.calculate_cas(["3*3"])
