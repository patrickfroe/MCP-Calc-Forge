from __future__ import annotations

from pathlib import Path


def test_faq_page_contains_required_main_sections() -> None:
    faq = Path('docs/faq.md').read_text(encoding='utf-8')

    assert '# FAQ für Anwender: MCP-Calc-Forge' in faq
    assert '## 1) Allgemeines' in faq
    assert '## 2) Nutzung' in faq
    assert '## 3) Verfügbare Berechnungen' in faq
    assert '## 4) Eingaben und Fehler' in faq
    assert '## 5) Fachliche Hinweise' in faq
    assert '## 6) Beispiele' in faq


def test_faq_page_mentions_all_registered_tools() -> None:
    faq = Path('docs/faq.md').read_text(encoding='utf-8')

    for tool_name in (
        'calculate_expression',
        'list_calculations',
        'get_calculation_details',
        'execute_calculation',
    ):
        assert tool_name in faq


def test_faq_page_lists_key_existing_calculations() -> None:
    faq = Path('docs/faq.md').read_text(encoding='utf-8')

    for calculation_id in (
        'vat_calculation',
        'percentage_change',
        'currency_conversion_static',
        'loan_annuity_payment',
        'break_even_units',
    ):
        assert calculation_id in faq
