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
    payload = calculators.calculate("bmi", {"primary_value": 1.8, "secondary_value": 81})
    assert payload["result"]["bmi"] == 25.0


def test_placeholder_handler_for_interactive_calculator() -> None:
    payload = calculators.calculate("cas", {"session_id": "s1", "payload": {"latex": "x^2"}})
    assert payload["error"]["code"] == "unimplemented_handler"
