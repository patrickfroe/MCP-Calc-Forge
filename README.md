# MCP-Calc-Forge

Python-MCP-Server für Berechnungen mit klar getrennter Architektur:

- **Calculation Registry** für zentrale Verwaltung aller benannten Berechnungen
- **Calculation Catalog** mit einzelnen Modulen unter `app/calculations/catalog/`
- **Validation Layer** für Eingabeprüfung und einheitliche Fehler
- **Execution Layer** für Ausführung benannter Berechnungen
- **Expression Engine** getrennt von benannten Berechnungen
- **MCP Tool Layer** mit genau vier Tools

## MCP-Tools

Der Server registriert vier Tools:

1. `evaluate_expression`
2. `list_calculations`
3. `get_calculation_details`
4. `execute_calculation`

Implementierung: `app/mcp/server.py`.

## Projektstruktur

```text
app/
  calculations/
    catalog/                 # einzelne Berechnungen als Module
    models.py                # Definitionen (InputField, CalculationDefinition, ...)
    registry.py              # zentrale Registry
  validation/
    calculation_validator.py # Validierung benannter Berechnungen
    expression_validator.py  # Validierung von Expressions
    errors.py                # einheitliches Fehlerformat
  execution/
    calculation_executor.py  # Ausführung benannter Berechnungen
    expression_engine.py     # sichere Expression-Auswertung (ohne eval)
  mcp/
    tools/                   # Tool-Handler (ohne Business-Logik)
    server.py                # MCP-Server + Tool-Registrierung
```

## Neue Berechnung registrieren

1. Neues Modul in `app/calculations/catalog/` anlegen.
2. `CALCULATION = CalculationDefinition(...)` definieren mit:
   - `id`, `name`, `description`, `llm_usage_hint`
   - `input_fields`, `output_description`, `output_type`, `examples`
   - `execute`-Funktion mit der eigentlichen Business-Logik
3. Berechnung in `app/calculations/catalog/__init__.py` zu `ALL_CALCULATIONS` hinzufügen.
4. Unit-Tests für Happy Path und Fehlerfälle ergänzen.

## Voraussetzungen

- Python 3.10+
- `fastmcp`

Installation:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Server starten

```bash
python server.py
```

`server.py` delegiert an den MCP-Server unter `app/mcp/server.py`.

## Tests

```bash
pytest
```
