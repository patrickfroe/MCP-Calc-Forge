# UI-Testanleitung (Browser) für die MCP-Integration

## 1) Zweck der Anleitung

Diese Anleitung beschreibt **praxisnah und Schritt für Schritt**, wie die vorhandene UI-Resource `ui://calculations/list` des Projekts im Browser getestet wird.

Getestet werden insbesondere:

- die Erreichbarkeit des MCP-HTTP-Endpoints `GET/POST /api/v1/mcp`
- die Auslieferung der UI-Resource über MCP (`resources/read`)
- das tatsächliche Frontend-Verhalten der HTML-View (`list_calculations.html`) bei `tool-result`-Events
- die Interaktion zwischen UI und Host (`tool-call-request` für `get_calculation_details`)

Zielgruppe:

- Entwickler
- QA/technische Tester
- Integratoren, die die View in einer Host-Umgebung einbetten

---

## 2) Voraussetzungen

### 2.1 Benötigte Software

- Python **3.10+**
- `pip`
- optional, aber empfohlen: virtuelle Umgebung (`venv`)
- `curl` für MCP-HTTP-Checks
- ein moderner Browser mit DevTools (Chrome/Edge/Firefox)

### 2.2 Projektabhängigkeiten installieren

Aus dem Repo-Root (`/workspace/MCP-Calc-Forge`):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2.3 Relevante Umgebungsvariablen (optional)

Standardmäßig sind folgende Schutzmechanismen **deaktiviert** und für lokale UI-Tests nicht nötig:

- `MCP_AUTH_ENABLED`
- `MCP_ABUSE_GUARD_ENABLED`
- `MCP_RATE_LIMIT_ENABLED`
- `MCP_TIMEOUT_ENABLED`
- `MCP_ORIGIN_VALIDATION_ENABLED`

Wenn einer dieser Schalter in deiner Umgebung gesetzt ist, kann das erwartetes Testverhalten ändern (z. B. `401`, `403`, `429`, `413`, `504`).

### 2.4 Browser-Voraussetzungen

- JavaScript muss aktiviert sein.
- Zugriff auf DevTools (Network + Console).
- Für lokale Iframe-Tests sollte `about:blank` oder eine lokale Testseite geöffnet werden können.

---

## 3) Projekt lokal starten

### 3.1 Startbefehl (HTTP-Server)

Aus dem Repo-Root:

```bash
source .venv/bin/activate
python -m app.mcp.discovery_http
```

### 3.2 Woran man erkennt, dass der Server läuft

In der Konsole erscheint u. a.:

- `Uvicorn running on http://127.0.0.1:8090`

**Default-Port:** `8090`

### 3.3 Endpoint-Erreichbarkeit prüfen (`/api/v1/mcp`)

```bash
curl -s http://127.0.0.1:8090/api/v1/mcp | python -m json.tool
```

Erwartung:

- JSON mit `name`, `version`, `description`, `tools`
- in `tools` u. a.:
  - `list_calculations`
  - `get_calculation_details`
  - `ui_get_calculation_preview`
- Tool-Meta enthält `resourceUri: "ui://calculations/list"` für die UI-relevanten Tools.

---

## 4) UI im Browser öffnen

Für lokale Tests gibt es eine direkte Preview-Route:

- `GET /ui/preview`
- Beispiel: `http://127.0.0.1:8090/ui/preview`

Die Route rendert dieselbe UI wie die MCP-Resource `ui://calculations/list`, damit Rendering und Interaktionen im Browser schneller geprüft werden können.

### 4.1 UI-HTML über MCP laden (technischer Vorcheck)

1) MCP-Session erzeugen (`initialize`) und `mcp-session-id` aus Response-Header lesen:

```bash
curl -i -N -X POST http://127.0.0.1:8090/api/v1/mcp \
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

2) Mit derselben `mcp-session-id` die Resource lesen:

```bash
curl -N -X POST http://127.0.0.1:8090/api/v1/mcp \
  -H "mcp-session-id: <SESSION_ID>" \
  -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc":"2.0",
    "id":2,
    "method":"resources/read",
    "params":{"uri":"ui://calculations/list"}
  }'
```

Erwartung:

- `result.contents[0].mimeType = "text/html"`
- `result.contents[0].text` enthält HTML mit `Waiting for tool result…`, `tool-result`, `tool-call-request`.

### 4.2 Direkter Browser-Aufruf über die Preview-Route

Nach dem Start des Servers kann die UI direkt geöffnet werden:

- `http://127.0.0.1:8090/ui/preview`

Hinweis: Die View bleibt host-orientiert (`window.parent.postMessage(...)`) und ist daher weiterhin kompatibel zur MCP-Host-Integration. Für schnelle lokale Render-/DOM-Checks ist die Preview-Route aber der einfachste Einstieg.

---

## 5) Schritt-für-Schritt-Testablauf

### Schritt 1: Discovery prüfen

**Aktion:** `GET /api/v1/mcp` aufrufen.

**Erwartung:** Discovery JSON enthält alle Tool-Schemas + UI-Meta.

**Erfolgskriterium:** `resourceUri` für `list_calculations`, `get_calculation_details`, `ui_get_calculation_preview` ist vorhanden.

### Schritt 2: MCP-Session initialisieren

**Aktion:** `initialize` per `POST /api/v1/mcp` senden.

**Erwartung:** SSE-Response mit `result.protocolVersion`; Header enthält `mcp-session-id`.

**Erfolgskriterium:** gültige Session-ID extrahierbar.

### Schritt 3: UI-Resource lesen

**Aktion:** `resources/read` für `ui://calculations/list` mit `mcp-session-id` senden.

**Erwartung:** HTML-Dokument (`mimeType: text/html`) wird geliefert.

**Erfolgskriterium:** HTML enthält IDs `status`, `calculation-list`, `details` und JS-Message-Handling.

### Schritt 4: `list_calculations` aufrufen

**Aktion:**

```bash
curl -N -X POST http://127.0.0.1:8090/api/v1/mcp \
  -H "mcp-session-id: <SESSION_ID>" \
  -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc":"2.0",
    "id":3,
    "method":"tools/call",
    "params":{"name":"list_calculations","arguments":{}}
  }'
```

**Erwartung:** `structuredContent.result.calculations` ist befüllt.

**Erfolgskriterium:** mehrere Calculator-Einträge (inkl. `loan_annuity_payment`, `currency_conversion_static`).

### Schritt 5: UI mit Tool-Result füttern

**Aktion:** In der Browser-Console der geöffneten UI ein `tool-result` senden (bei Top-Level-Test an `window`, bei Host-Test an das iframe-Fenster):

```js
window.postMessage({
  type: "tool-result",
  toolName: "list_calculations",
  structuredContent: {
    calculations: [
      { id: "loan_annuity_payment", name: "Loan Annuity Payment" },
      { id: "currency_conversion_static", name: "Currency Conversion Static" }
    ]
  }
}, "*");
```

**Erwartung:** UI listet Buttons im Format `<id>: <name>`.

**Erfolgskriterium:** Status wechselt auf `N calculation(s) loaded.`

### Schritt 6: Detailabruf via UI-Interaktion testen

**Aktion:** In der UI auf einen Calculator-Button klicken.

**Erwartung:** UI sendet an Host:

```json
{
  "type": "tool-call-request",
  "toolName": "get_calculation_details",
  "arguments": { "calculation_id": "..." }
}
```

**Erfolgskriterium:** In einem Host-Test empfängt der Host das Event unverändert; im Top-Level-Test kann das Event per Console-Listener sichtbar gemacht werden:

```js
window.addEventListener("message", (event) => console.log("message", event.data));
```

### Schritt 7: Detaildaten zurück an UI senden

**Aktion:** Host (oder im Top-Level-Test manuell per Console) sendet Ergebnis als `tool-result` zurück:

```js
window.postMessage({
  type: "tool-result",
  toolName: "get_calculation_details",
  structuredContent: {
    id: "loan_annuity_payment",
    name: "Loan Annuity Payment",
    description: "Berechnet die konstante Kreditrate eines Annuitätendarlehens."
  }
}, "*");
```

**Erwartung:** Bereich „Calculation details“ wird sichtbar; JSON wird im `<pre>` angezeigt.

**Erfolgskriterium:** `details-name` und `details-json` sind mit Daten gefüllt.

---

## 6) Testfälle (manuell)

### 6.1 Positive Testfälle

1. **Seite/Resource lädt korrekt**
   - `resources/read` liefert HTML.
2. **UI-Komponente wird angezeigt**
   - Headline „Calculations“, Statuszeile, Liste und versteckter Detailbereich vorhanden.
3. **Calculator-Daten erscheinen**
   - Nach `tool-result` mit `list_calculations`: Liste ist befüllt.
4. **Eingaben/Interaktion möglich**
   - Klick auf Listeneintrag erzeugt `tool-call-request`.
5. **Ergebnisse werden angezeigt**
   - Nach `tool-result` für `get_calculation_details`: Detailsektion sichtbar und JSON dargestellt.

### 6.2 Negative Testfälle

1. **Ungültige Session**
   - `tools/call` ohne `mcp-session-id` → Fehler `Bad Request: Missing session ID`.
2. **Ungültige Calculation-ID**
   - `get_calculation_details` mit unbekannter ID → einheitliches Fehlerobjekt (`ok=false`, `error`).
3. **Leeres/fehlerhaftes Payload in Host-Message**
   - `tool-result` ohne erwartete Struktur → UI darf nicht crashen; Liste bleibt leer bzw. unverändert.

---

## 7) Fehlersuche / Troubleshooting

### Problem: Server startet nicht

Prüfen:

- venv aktiv?
- `pip install -r requirements.txt` erfolgreich?
- Port 8090 bereits belegt?

Hilfreich:

```bash
lsof -i :8090
```

### Problem: `GET /api/v1/mcp` antwortet nicht

Prüfen:

- läuft `python -m app.mcp.discovery_http` wirklich?
- richtiger Host/Port (`127.0.0.1:8090`)?

### Problem: `POST /api/v1/mcp` liefert 401/403/429/413/504

Prüfen, ob Security-/Guard-Middleware per Env aktiv ist:

- Auth: `MCP_AUTH_ENABLED`, `MCP_AUTH_TOKEN`
- Origin-Validation: `MCP_ORIGIN_VALIDATION_ENABLED`, `MCP_ALLOWED_ORIGINS`
- Rate Limit: `MCP_RATE_LIMIT_ENABLED`
- Payload Limit: `MCP_ABUSE_GUARD_ENABLED`, `MCP_MAX_REQUEST_BYTES`
- Timeout: `MCP_TIMEOUT_ENABLED`

### Problem: UI bleibt leer

Prüfen:

- Wurde tatsächlich ein `tool-result`-Event an die iframe-View gesendet?
- Kommt `structuredContent` oder `result` im erwarteten Objekt an?
- Stimmt `event.source === window.parent` (UI akzeptiert nur Parent-Messages)?

### Problem: CORS/CSP/Iframe/Asset-Themen

- Die UI-Resource deklariert restriktive Default-CSP-Meta (`connectDomains=[]`, `resourceDomains=[]`).
- Da die UI als Resource-Text geliefert wird, gibt es keine separaten Asset-Requests aus dem Projekt.
- Bei Host-seitiger Einbettung sind Host-CSP/Iframe-Regeln zu prüfen.

---

## 8) Browser-Checks (DevTools)

### 8.1 Network

- Request `GET http://127.0.0.1:8090/api/v1/mcp` → `200`, JSON-Discovery.
- Request `POST http://127.0.0.1:8090/api/v1/mcp` (`initialize`) → `200`, `content-type: text/event-stream`, Header `mcp-session-id`.
- Nachfolgende `POST`-Requests mit `mcp-session-id` funktionieren (`resources/read`, `tools/call`).

### 8.2 Console

Achte auf:

- JavaScript-Fehler in der eingebetteten UI.
- Host-seitige `postMessage`-Flüsse (`tool-result` rein, `tool-call-request` raus).

### 8.3 Erwartete MCP-Responses

- `initialize`: SSE-Message mit `result.protocolVersion` und `capabilities`.
- `resources/read`: HTML-Inhalt + UI-Metadaten.
- `tools/call(list_calculations)`: strukturierte Liste von Berechnungen.
- `tools/call(get_calculation_details)`: Detailobjekt oder standardisiertes Fehlerobjekt.

### 8.4 Woran man die korrekte Serveranbindung erkennt

- `mcp-session-id` wird aus `initialize` übernommen.
- Requests ohne Session schlagen fehl, mit Session erfolgreich.
- UI reagiert sichtbar auf echte Tool-Ergebnisse.

---

## 9) Erwartetes Gesamtergebnis

Ein erfolgreicher Browser-Test ist erreicht, wenn:

- Discovery + MCP-POST auf `/api/v1/mcp` funktionieren.
- `ui://calculations/list` als HTML gelesen werden kann.
- die UI-Liste nach `tool-result` sichtbar gefüllt wird.
- Klick auf einen Eintrag den Detail-Tool-Call anfordert.
- Detaildaten danach sichtbar gerendert werden.
- Fehlerfälle kontrolliert und nachvollziehbar bleiben.

---

## 10) Schneller Smoke-Test (2–5 Minuten)

1. Server starten:

```bash
source .venv/bin/activate
python -m app.mcp.discovery_http
```

2. Discovery prüfen:

```bash
curl -s http://127.0.0.1:8090/api/v1/mcp | python -m json.tool | head -n 40
```

3. `initialize` senden und `mcp-session-id` notieren.

4. Mit dieser Session `tools/call(list_calculations)` ausführen.

5. Prüfen, dass `calculations` nicht leer ist und mindestens `loan_annuity_payment` vorkommt.

6. Optional: `resources/read` für `ui://calculations/list` und im Output nach `tool-result` suchen.

Wenn alle sechs Punkte erfüllt sind, ist die UI-/MCP-Grundintegration funktionsfähig.
