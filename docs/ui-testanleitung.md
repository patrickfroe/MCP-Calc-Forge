# UI-Testanleitung (MCP Apps Integration)

Diese Anleitung beschreibt, wie die aktuelle UI-Integration (`ui://calculations/list`) manuell und automatisiert getestet werden kann.

## 1) Voraussetzungen

- Python 3.10+
- Abhängigkeiten installiert:

```bash
pip install -r requirements.txt
```

## 2) Automatisierte Tests ausführen

Empfohlen für schnellen Regressionscheck:

```bash
PYTHONPATH=. pytest tests/unit/test_mcp_ui_resources.py tests/unit/test_mcp_discovery.py tests/integration/test_mcp_tools_integration.py
```

Was damit abgedeckt ist:

- UI-Resource-Registrierung (`ui://...`)
- UI-Metadaten (CSP, Display Modes, Theming, Host Context, Lifecycle-Hinweise)
- Tool-Metadaten inkl. app-only Visibility für `ui_get_calculation_preview`
- `list_calculations` mit `result` + `structuredContent` + `content`

## 3) Server lokal starten

### STDIO-Server

```bash
python -m app.mcp.server
```

### HTTP-Endpoint (Discovery + MCP)

```bash
python -m app.mcp.discovery_http
```

Danach ist der MCP-Endpoint unter `http://127.0.0.1:8090/api/v1/mcp` erreichbar.

## 4) Discovery prüfen (UI-Metadaten sichtbar?)

```bash
curl -s http://127.0.0.1:8090/api/v1/mcp | python -m json.tool
```

Erwartung:

- Tool `list_calculations` enthält `_meta.ui.resourceUri = ui://calculations/list`
- Tool `get_calculation_details` enthält dieselbe `resourceUri`
- Tool `ui_get_calculation_preview` hat `visibility = ["app"]`

## 5) MCP-Initialize prüfen

```bash
curl -N -X POST http://127.0.0.1:8090/api/v1/mcp \
  -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"initialize",
    "params":{
      "protocolVersion":"2025-03-26",
      "capabilities":{},
      "clientInfo":{"name":"ui-test-client","version":"1.0"}
    }
  }'
```

Erwartung: JSON-RPC-Result wird als SSE-Event zurückgegeben.

## 6) Tool-Calls manuell testen

### 6.1 `list_calculations`

```bash
curl -N -X POST http://127.0.0.1:8090/api/v1/mcp \
  -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc":"2.0",
    "id":2,
    "method":"tools/call",
    "params":{
      "name":"list_calculations",
      "arguments":{}
    }
  }'
```

Erwartung:

- `result.calculations` vorhanden (Legacy-Contract)
- `structuredContent.calculations` vorhanden (UI-Kontext)
- `content[0].type = "text"` vorhanden (modellfreundliche Kurzfassung)

### 6.2 `ui_get_calculation_preview` (app-only helper)

```bash
curl -N -X POST http://127.0.0.1:8090/api/v1/mcp \
  -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc":"2.0",
    "id":3,
    "method":"tools/call",
    "params":{
      "name":"ui_get_calculation_preview",
      "arguments":{"calculation_id":"loan_annuity_payment"}
    }
  }'
```

Erwartung:

- `ok=true`
- kompaktes Preview-Objekt in `result` und `structuredContent`
- `content` enthält textuelle Kurzbeschreibung

## 7) Manuelle UI-Verhaltensprüfung (Host-seitig)

Die bereitgestellte HTML-View erwartet Host-Messages vom Typ `tool-result` und kann selbst `tool-call-request` für `get_calculation_details` senden.

Manuell zu verifizieren:

1. Host rendert `ui://calculations/list` in einer iframe-View.
2. Nach einem `list_calculations`-Result wird die Liste der Berechnungen angezeigt.
3. Klick auf einen Eintrag sendet ein `tool-call-request`-Event (`get_calculation_details`).
4. Host führt Tool-Call aus und liefert `tool-result` zurück.
5. Detailbereich wird mit Ergebnisdaten aktualisiert.

## 8) Fehlersuche (typische Ursachen)

- **`ModuleNotFoundError: app` bei pytest**
  - Tests mit `PYTHONPATH=. pytest ...` starten.
- **Keine SSE-Antwort bei POST**
  - `accept: application/json, text/event-stream` setzen.
- **401 / 403 Fehler**
  - Prüfen, ob Auth oder Origin-Validation via Environment aktiviert wurde.
