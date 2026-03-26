from app.calculations.registry import get_registry


EXPECTED_IDS = {
    "percentage_of_value",
    "vat_calculation",
    "average",
    "rule_of_three",
    "discount_calculation",
    "percentage_change",
    "compound_interest",
    "simple_interest",
    "weighted_average",
    "gross_margin",
    "markup_calculation",
    "break_even_units",
    "loan_annuity_payment",
    "currency_conversion_static",
}


def test_registry_provides_all_catalog_calculations() -> None:
    registry = get_registry()

    definitions = registry.list_calculations()

    assert len(definitions) == len(EXPECTED_IDS)
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

    discount_calc = registry.get("discount_calculation")

    assert discount_calc is not None
    assert discount_calc.id == "discount_calculation"
