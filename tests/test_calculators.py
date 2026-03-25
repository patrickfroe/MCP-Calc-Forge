from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import calcforge.calculators as calculators


def test_list_calculators_returns_empty_list() -> None:
    assert calculators.list_calculators() == []
    assert calculators.list_calculators(category="arithmetic") == []


def test_schema_lookup_returns_unknown_slug_error() -> None:
    payload = calculators.get_calculator_schema("add")

    assert payload["error"]["code"] == "unknown_slug"
    assert payload["error"]["details"]["slug"] == "add"


def test_calculate_returns_unknown_slug_error() -> None:
    payload = calculators.calculate("add", {"a": 1, "b": 2})

    assert payload["error"]["code"] == "unknown_slug"
    assert payload["error"]["details"]["slug"] == "add"
