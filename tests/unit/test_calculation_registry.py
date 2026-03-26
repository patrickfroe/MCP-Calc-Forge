from app.calculations.registry import get_registry


EXPECTED_IDS = {"percentage_of", "vat_add", "simple_interest"}


def test_registry_provides_three_calculations() -> None:
    registry = get_registry()

    definitions = registry.list_calculations()

    assert len(definitions) == 3
    assert {item.id for item in definitions} == EXPECTED_IDS


def test_each_calculation_has_required_metadata_fields() -> None:
    registry = get_registry()

    for definition in registry.list_calculations():
        assert definition.id
        assert definition.name
        assert definition.description
        assert definition.llm_usage_hint
        assert definition.input_fields
        assert definition.examples


def test_registry_get_returns_calculation_by_id() -> None:
    registry = get_registry()

    vat_calc = registry.get("vat_add")

    assert vat_calc is not None
    assert vat_calc.id == "vat_add"
