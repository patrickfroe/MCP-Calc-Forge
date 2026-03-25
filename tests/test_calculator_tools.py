from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server import CALCULATOR_TOOL_NAMES, get_calculator_schema, list_calculators


def test_list_calculators_returns_all_calculator_tools() -> None:
    assert list_calculators() == CALCULATOR_TOOL_NAMES
    assert "list_calculators" not in list_calculators()
    assert "get_calculator_schema" not in list_calculators()


def test_get_calculator_schema_for_tool_with_defaults() -> None:
    schema = get_calculator_schema("to_scientific_notation")

    assert schema["name"] == "to_scientific_notation"
    assert schema["returns"] == "str"
    assert schema["parameters"] == [
        {"name": "x", "type": "float", "required": True, "default": None},
        {"name": "precision", "type": "int", "required": False, "default": 3},
    ]


def test_get_calculator_schema_raises_for_unknown_tool() -> None:
    try:
        get_calculator_schema("unknown")
    except ValueError as error:
        assert "Unknown calculator 'unknown'." == str(error)
    else:
        raise AssertionError("Expected ValueError for unknown calculator")
