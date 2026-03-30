# MCP-Calc-Forge

Python-MCP-Server für Berechnungen mit klar getrennter Architektur:

- **Calculation Registry** für zentrale Verwaltung aller benannten Berechnungen
- **Calculation Catalog** mit einzelnen Modulen unter `app/calculations/catalog/`
- **Validation Layer** für Eingabeprüfung und einheitliche Fehler
- **Execution Layer** für Ausführung benannter Berechnungen
- **Expression Engine** getrennt von benannten Berechnungen
- **MCP Tool Layer** mit genau vier Tools

## Nutzerdokumentation

- Für eine anwendungsorientierte Übersicht (für Endnutzer/Fachanwender) siehe `docs/nutzeruebersicht.md`.
- Für eine kompakte FAQ-Seite (typische Anwenderfragen) siehe `docs/faq.md`.

## MCP-Tools

Der Server registriert fünf Tools:

1. `calculate_expression`
2. `list_calculations`
3. `get_calculation_details`
4. `ui_get_calculation_preview` (app-only helper)
5. `execute_calculation`

Implementierung: `app/mcp/server.py`.

### Tool-Contract Hinweise

- `calculate_expression` akzeptiert nur Zahlen, Klammern und die Operatoren `+ - * /` (keine Namen/Funktionsaufrufe).
- Das Feld `expression` ist im Schema als nicht-leerer String mit maximal 500 Zeichen definiert.
- `execute_calculation` sollte nach `get_calculation_details` verwendet werden, um Pflichtfelder und Constraints vorab zu kennen.

### MCP Apps Visibility (aktueller Stand)

- `list_calculations`: `visibility=["model","app"]`, verknüpft mit `ui://calculations/list`
- `get_calculation_details`: `visibility=["model","app"]`, verknüpft mit `ui://calculations/list`
- `ui_get_calculation_preview`: `visibility=["app"]`, verknüpft mit `ui://calculations/list` als UI-Helfer ohne eigene Business-Logik.

### MCP Apps Progressive Enhancement & UI Lifecycle

- **Progressive Enhancement:** Tools bleiben ohne UI vollständig nutzbar; UI-bezogene Felder (`meta`, `structuredContent`, `content`) sind additive Erweiterungen.
- **Host-Rendered View:** `ui://calculations/list` ist als Host-View gedacht und erwartet Tool-Result-Events.
- **Interaktivität:** Die View kann über Host-Messages Tool-Aufrufe anfordern (z. B. `get_calculation_details`), ohne Business-Logik im Frontend zu duplizieren.
- **Theming / Host Context / Display Modes:** Die UI-Resource-Metadaten deklarieren Host-Theme-Unterstützung, Locale/Timezone-Context und unterstützte Display-Modes.
- **Lifecycle-Hinweise:** Metadaten enthalten deklarative Init/Update/Teardown-Events für Host-Integration.

### Numerik-Policy

- Berechnungen verwenden Python-`float` für numerische Ausführung.
- Eingaben müssen endliche Zahlen sein: `NaN`, `Infinity` und `-Infinity` werden als Validierungsfehler abgelehnt.
- Auch Expressions müssen einen endlichen numerischen Wert liefern (kein `Infinity`).
- Rundung erfolgt nicht global zentral; falls nötig, sollte die konsumierende Anwendung Ergebnisse fachlich passend runden.

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
    tool_specs.py            # zentrale Tool-Metadaten (Name/Beschreibung/Schema)
    discovery.py             # Discovery-JSON aus zentralen Tool-Metadaten
    discovery_http.py        # gemeinsamer HTTP-Endpoint /api/v1/mcp (GET Discovery, POST MCP)
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


## HTTP Endpoint für Discovery + MCP

Zusätzlich zur normalen MCP-Nutzung (STDIO) gibt es einen gemeinsamen HTTP-Endpoint:

- `GET /api/v1/mcp` liefert die Discovery-JSON mit `name`, `version`, `description`, `tools[]`
- `POST /api/v1/mcp` verarbeitet MCP-JSON-RPC-Anfragen (Streamable HTTP)
- Tool-Metadaten werden zentral in `app/mcp/tool_specs.py` gepflegt und sowohl für MCP-Registrierung als auch Discovery wiederverwendet.
- Discovery enthält pro Tool sowohl `inputSchema` als auch `outputSchema`.
- Falls ein Client `Accept: text/event-stream` nutzt, wird der Request an den MCP-Transport weitergereicht (keine Discovery-JSON).

### Protokollverhalten (HTTP)

- MCP-POST-Requests sollen `Accept: application/json, text/event-stream` senden.
- `initialize` liefert die vereinbarte `protocolVersion` sowie Server-Capabilities im JSON-RPC-Result.
- Ungültige Request-Parameter werden als JSON-RPC-Fehler `-32602` zurückgegeben.
- Malformed JSON wird mit Parse-Error `-32700` beantwortet.

Start des HTTP-Servers (lokal):

```bash
python -m app.mcp.discovery_http
```

Optionale Authentifizierung für `POST /api/v1/mcp` kann per Environment-Variablen aktiviert werden:

```bash
export MCP_AUTH_ENABLED=true
export MCP_AUTH_TOKEN="change-me"
python -m app.mcp.discovery_http
```

Wenn `MCP_AUTH_ENABLED=true` gesetzt ist, muss der Header `Authorization: Bearer <MCP_AUTH_TOKEN>` bei MCP-POST-Requests mitgesendet werden.

Optionale Abuse-Guard (Request-Größe) per Environment-Variablen:

```bash
export MCP_ABUSE_GUARD_ENABLED=true
export MCP_MAX_REQUEST_BYTES=65536
```

Optionale Rate-Limitierung per Environment-Variablen:

```bash
export MCP_RATE_LIMIT_ENABLED=true
export MCP_RATE_LIMIT_REQUESTS=60
export MCP_RATE_LIMIT_WINDOW_SECONDS=60
```

Optionale Timeout-Guardrail per Environment-Variablen:

```bash
export MCP_TIMEOUT_ENABLED=true
export MCP_REQUEST_TIMEOUT_SECONDS=10
```

Request-Logging für den MCP-HTTP-Endpoint ist standardmäßig aktiv (`MCP_REQUEST_LOG_ENABLED=true`) und kann optional deaktiviert werden:

```bash
export MCP_REQUEST_LOG_ENABLED=false
```

Optionale Origin-Allowlist-Validierung:

```bash
export MCP_ORIGIN_VALIDATION_ENABLED=true
export MCP_ALLOWED_ORIGINS="https://app.example.com,https://admin.example.com"
```

## Voraussetzungen

- Python 3.10+
- `fastmcp`
- Abhängigkeiten sind in `requirements.txt` auf getestete Versionen gepinnt.

Installation:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Server starten

```bash
python -m app.mcp.server
```


## Tests

```bash
pytest
```
