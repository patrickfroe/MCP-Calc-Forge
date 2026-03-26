from app.calculations.registry import get_registry


EXPECTED_IDS = {"percentage_of_value", "vat_calculation", "average", "rule_of_three"}


def test_registry_provides_four_calculations() -> None:
    registry = get_registry()

    definitions = registry.list_calculations()

    assert len(definitions) == 4
    assert {item.id for item in definitions} == EXPECTED_IDS


def test_each_calculation_has_required_metadata_fields() -> None:
    registry = get_registry()

    for definition in registry.list_calculations():
        assert definition.id
        assert definition.name
        assert definition.description
        assert definition.llm_usage_hint
        assert definition.input_fields
        assert definition.output_description
        assert definition.output_type
        assert definition.examples
        assert callable(definition.execute)


def test_registry_get_returns_calculation_by_id() -> None:
    registry = get_registry()

    vat_calc = registry.get("vat_calculation")

    assert vat_calc is not None
    assert vat_calc.id == "vat_calculation"
