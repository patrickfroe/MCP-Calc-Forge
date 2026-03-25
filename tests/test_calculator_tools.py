from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import calcforge.calculators as calculators


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
