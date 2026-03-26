# MCP-Server Konzept für Berechnungen in einem ChatBot

## Phase 1: Verständnis und Annahmen

### Zielverständnis
Der MCP-Server soll als strukturierte Berechnungsplattform für ein LLM dienen. Neben einer freien Ausdrucksberechnung (Expression Calculator) soll das LLM über Metadaten geführt werden:
1. verfügbare Berechnungen entdecken,
2. Details (Input/Output/Regeln) einer Berechnung verstehen,
3. Berechnung mit validierten Inputs ausführen.

Damit wird aus „unscharfen“ LLM-Requests eine kontrollierte, nachvollziehbare und erweiterbare Tool-Nutzung.

### Explizite Annahmen
- **A1 (Protokoll):** Der Server wird über MCP-Tools angebunden (z. B. stdio oder HTTP-Bridge), Tool-IO ist JSON-basiert.
- **A2 (Numerik):** Für fachliche Berechnungen werden Dezimalwerte bevorzugt (`Decimal`) statt binärer Floating-Point-Arithmetik.
- **A3 (Währung):** Währungsberechnungen im MVP ohne Live-Kurse; Umrechnung über übergebene oder statische Raten.
- **A4 (Rechte):** Kein separates AuthN/AuthZ im MVP; Aufruf stammt aus vertrauenswürdigem Bot-Backend.
- **A5 (Versionierung):** Berechnungsdefinitionen erhalten Versionsfelder, damit Breaking Changes kontrolliert sind.
- **A6 (Internationalisierung):** Input-Formate intern normiert (Punkt als Dezimaltrenner), sprachliche Varianten werden im Bot-Layer vorverarbeitet.

### Kritische Einordnung
Die gewünschte Tool-Trennung ist sehr sinnvoll für LLMs, weil sie Discovery, Schema-Verständnis und Execution trennt. Dadurch sinken Halluzinationen, da das Modell nicht „raten“ muss, welche Inputs nötig sind.

---

## Phase 2: Architektur- und Konzeptphase

## 1) Zusammenfassung

Der MCP-Server stellt berechnungsbezogene Tools bereit, die einem ChatBot erlauben, mathematische und fachliche Operationen sicher, reproduzierbar und strukturiert auszuführen. Der zentrale Mehrwert für ein LLM ist die Kombination aus **Tool-Discovery**, **maschinell lesbaren Input/Output-Schemas** und **strikter Validierung**.

**Nutzen für ChatBot + LLM:**
- robuste Tool-Auswahl statt freier Interpretation,
- weniger Inputfehler durch klare Parametrisierung,
- höhere Antwortqualität durch deterministische Rechenergebnisse,
- bessere Wartbarkeit durch registrierte, versionierte Berechnungen.

## 2) Fachliches Zielbild

### Warum die Trennung der Tools sinnvoll ist
- **List Available Calculations:** liefert den Suchraum („Was kann ich?“).
- **Get Calculation Details:** liefert genaue „Bedienungsanleitung“ inkl. Schema.
- **Execute Named Calculation:** führt strikt validiert aus.

Diese Entkopplung ist LLM-gerecht: Das Modell kann zuerst recherchieren, dann strukturieren, dann ausführen.

### Bewertung der Tool-Struktur für LLMs
**Sehr gut geeignet**, wenn:
- Metadaten präzise sind,
- Felder stabil benannt sind,
- Fehlermodell konsistent ist,
- Beispiele je Berechnung hinterlegt sind.

### Verbesserungen
1. **Tool E: Validate Calculation Input (optional):** Nur validieren, nicht ausführen (hilft beim Auto-Repair durch LLM).
2. **Capability-Flags pro Berechnung:** z. B. `supports_batch`, `is_deterministic`.
3. **Schema-Version pro Berechnung:** verhindert stille Breaking Changes.
4. **Idempotenz-Metadaten:** klare Aussage, ob gleiche Inputs immer gleiche Outputs liefern.

## 3) Architekturkonzept

### Zielarchitektur (logisch)
- **MCP Interface Layer**
  - Exponiert Tools A-D
  - Transformiert MCP-Requests in interne Commands
- **Tool Registry**
  - Verzeichnis aller Berechnungen (ID → Definition)
- **Calculation Metadata Store**
  - Enthält Input/Output-Schema, Regeln, Beispiele, LLM-Hinweise
- **Input Validation Layer**
  - Typ-, Format-, Bereichs- und Pflichtfeldprüfung
- **Execution Engine**
  - Dispatch auf konkrete Executor-Funktionen
- **Error & Result Mapper**
  - Einheitliches Response-/Fehlerformat
- **Logging/Observability**
  - strukturierte Logs, Metriken, Traces

### Rollen der Kernbausteine
- **Tool Registry:** zentrale Lookup-Instanz, verhindert verstreute Definitionen.
- **Calculation Metadata:** maschinell nutzbare Verträge für LLM und Backend.
- **Input Validation:** Schutz vor fachlich und technisch ungültigen Inputs.
- **Execution Engine:** entkoppelt Tool-Aufruf von konkreter Berechnungslogik.
- **Error Handling:** einheitliche Codes für Recoverability.
- **Logging/Observability:** Debugging, Qualitätssicherung, Betriebssicht.

### Erweiterbarkeit (neue Berechnung)
Neue Berechnung = neues Definitionsobjekt + Executor-Funktion + Registrierung + Tests. Keine Änderung an zentralen Tool-Endpunkten nötig.

## 4) Tool-Design

## Tool A: `expression_calculator`
**Zweck:** direkte Auswertung einer mathematischen Expression.

**Input (JSON):**
```json
{
  "expression": "2 + 3 * 4",
  "precision": 6,
  "locale": "en-US"
}
```

**Output (JSON):**
```json
{
  "ok": true,
  "result": {
    "value": "14",
    "type": "decimal",
    "normalized_expression": "2+3*4"
  },
  "error": null,
  "meta": {
    "duration_ms": 2,
    "request_id": "req_123"
  }
}
```

**Fehlerfälle:** ungültiger Parser-Token, verbotene Operatoren, Division durch 0, Ausdruck zu lang/komplex.

---

## Tool B: `list_available_calculations`
**Zweck:** verfügbare Berechnungen discovern.

**Input:** optional Filter
```json
{
  "category": "finance",
  "search": "vat",
  "limit": 50,
  "offset": 0
}
```

**Output:**
```json
{
  "ok": true,
  "result": {
    "items": [
      {
        "calculation_id": "vat_add",
        "name": "MwSt aufschlagen",
        "description": "Berechnet Bruttopreis aus Nettopreis und Steuersatz.",
        "llm_usage_hint": "Nutzen, wenn Nutzer netto + Steuersatz nennt und brutto will.",
        "version": "1.0.0"
      }
    ],
    "total": 1
  },
  "error": null
}
```

**Fehlerfälle:** ungültige Pagination-Parameter.

---

## Tool C: `get_calculation_details`
**Zweck:** schema-genaue Details einer Berechnung liefern.

**Input:**
```json
{
  "calculation_id": "vat_add",
  "version": "1.0.0"
}
```

**Output (gekürzt):**
```json
{
  "ok": true,
  "result": {
    "id": "vat_add",
    "name": "MwSt aufschlagen",
    "description": "Berechnet brutto aus netto und MwSt-Satz.",
    "llm_usage_hint": "Verwenden für Netto->Brutto.",
    "input_schema": {
      "type": "object",
      "required": ["net_amount", "vat_rate_percent"],
      "properties": {
        "net_amount": {"type": "string", "format": "currency"},
        "vat_rate_percent": {"type": "string", "format": "percent"},
        "rounding_mode": {"type": "string", "enum": ["HALF_UP", "BANKERS"]}
      }
    },
    "validation_rules": [
      {"rule": "net_amount >= 0"},
      {"rule": "0 <= vat_rate_percent <= 100"}
    ],
    "output_schema": {
      "type": "object",
      "properties": {
        "gross_amount": {"type": "string", "format": "currency"},
        "vat_amount": {"type": "string", "format": "currency"}
      }
    },
    "examples": [
      {
        "input": {"net_amount": "100.00", "vat_rate_percent": "19"},
        "output": {"gross_amount": "119.00", "vat_amount": "19.00"}
      }
    ]
  },
  "error": null
}
```

**Fehlerfälle:** unbekannte `calculation_id`, nicht unterstützte Version.

---

## Tool D: `execute_named_calculation`
**Zweck:** ausgewählte Berechnung mit Inputs ausführen.

**Input:**
```json
{
  "calculation_id": "vat_add",
  "version": "1.0.0",
  "inputs": {
    "net_amount": "100.00",
    "vat_rate_percent": "19"
  }
}
```

**Output:**
```json
{
  "ok": true,
  "result": {
    "calculation_id": "vat_add",
    "version": "1.0.0",
    "output": {
      "gross_amount": "119.00",
      "vat_amount": "19.00"
    }
  },
  "error": null,
  "meta": {
    "duration_ms": 3,
    "request_id": "req_124"
  }
}
```

**Fehlerfälle:** Validierungsfehler, Executor-Fehler, Timeout, numerische Ausnahme.

## 5) Berechnungsmodell

### Internes Modell (Vorschlag)
```json
{
  "id": "string",
  "version": "string",
  "name": "string",
  "description": "string",
  "category": "string",
  "llm_usage_hint": "string",
  "input_schema": {},
  "output_schema": {},
  "validation_rules": [],
  "executor_reference": "string",
  "examples": [],
  "tags": ["string"],
  "is_active": true
}
```

### Drei konkrete Beispielobjekte
```json
[
  {
    "id": "percentage_of",
    "version": "1.0.0",
    "name": "Prozentwert berechnen",
    "description": "Berechnet p% von einem Grundwert.",
    "category": "math",
    "llm_usage_hint": "Wenn gefragt wird: 'Wie viel sind X% von Y?'.",
    "input_schema": {
      "type": "object",
      "required": ["base_value", "percent"],
      "properties": {
        "base_value": {"type": "string", "format": "decimal"},
        "percent": {"type": "string", "format": "percent"}
      }
    },
    "output_schema": {
      "type": "object",
      "properties": {"value": {"type": "string", "format": "decimal"}}
    },
    "validation_rules": ["base_value finite", "percent finite"],
    "executor_reference": "executors.percentage_of",
    "examples": [{"input": {"base_value": "250", "percent": "12"}, "output": {"value": "30"}}],
    "tags": ["percent"],
    "is_active": true
  },
  {
    "id": "vat_add",
    "version": "1.0.0",
    "name": "MwSt aufschlagen",
    "description": "Berechnet Brutto und Steueranteil aus Netto und Steuersatz.",
    "category": "finance",
    "llm_usage_hint": "Für Netto->Brutto-Berechnungen.",
    "input_schema": {
      "type": "object",
      "required": ["net_amount", "vat_rate_percent"],
      "properties": {
        "net_amount": {"type": "string", "format": "currency"},
        "vat_rate_percent": {"type": "string", "format": "percent"}
      }
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "gross_amount": {"type": "string", "format": "currency"},
        "vat_amount": {"type": "string", "format": "currency"}
      }
    },
    "validation_rules": ["net_amount >= 0", "0 <= vat_rate_percent <= 100"],
    "executor_reference": "executors.vat_add",
    "examples": [{"input": {"net_amount": "100", "vat_rate_percent": "19"}, "output": {"gross_amount": "119", "vat_amount": "19"}}],
    "tags": ["vat", "tax"],
    "is_active": true
  },
  {
    "id": "simple_interest",
    "version": "1.0.0",
    "name": "Einfache Zinsrechnung",
    "description": "Berechnet Zinsbetrag und Endkapital ohne Zinseszins.",
    "category": "finance",
    "llm_usage_hint": "Wenn Kapital, Zinssatz und Laufzeit linear gerechnet werden sollen.",
    "input_schema": {
      "type": "object",
      "required": ["principal", "annual_rate_percent", "years"],
      "properties": {
        "principal": {"type": "string", "format": "currency"},
        "annual_rate_percent": {"type": "string", "format": "percent"},
        "years": {"type": "string", "format": "decimal"}
      }
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "interest_amount": {"type": "string", "format": "currency"},
        "total_amount": {"type": "string", "format": "currency"}
      }
    },
    "validation_rules": ["principal >= 0", "years >= 0"],
    "executor_reference": "executors.simple_interest",
    "examples": [{"input": {"principal": "1000", "annual_rate_percent": "5", "years": "2"}, "output": {"interest_amount": "100", "total_amount": "1100"}}],
    "tags": ["interest"],
    "is_active": true
  }
]
```

## 6) Beispiel-Berechnungen (mind. 10)

1. **percentage_of** – Prozentwert von Grundwert.
2. **percentage_change** – prozentuale Änderung von alt zu neu.
3. **simple_interest** – lineare Zinsen.
4. **compound_interest** – Zinseszins.
5. **vat_add** – Netto + MwSt → Brutto.
6. **vat_extract** – Brutto → Netto + Steueranteil.
7. **rule_of_three** – Dreisatz linear.
8. **area_rectangle** – Fläche Rechteck.
9. **average_mean** – arithmetisches Mittel.
10. **discount_price** – Preis nach Rabatt.
11. **growth_rate_cagr** – durchschnittliche Wachstumsrate.
12. **currency_convert_static** – Umrechnung mit statischem Kurs.

**Kurzschema je Berechnung:**
- Zweck klar benennen.
- Eingaben inklusive Typ/Format (z. B. decimal, percent, currency).
- Ausgabe strukturiert (z. B. Wert + Einheitenfelder).

## 7) Validierung und Fehlerbehandlung

### Validierungsstrategie (mehrstufig)
1. **Syntaktisch:** JSON-Struktur, Pflichtfelder vorhanden.
2. **Typisiert:** Datentyp/Format (decimal, percent, enum).
3. **Semantisch:** Wertebereiche, Domänenregeln.
4. **Laufzeitnah:** rechnerische Ausnahmen (z. B. Division durch 0).

### Einheitliches Fehlermodell
```json
{
  "ok": false,
  "result": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed",
    "details": [
      {
        "field": "vat_rate_percent",
        "issue": "must be between 0 and 100",
        "provided": "140"
      }
    ],
    "retryable": false
  },
  "meta": {
    "request_id": "req_125",
    "duration_ms": 1
  }
}
```

### Empfohlene Fehlercodes
- `UNKNOWN_CALCULATION_ID`
- `UNSUPPORTED_VERSION`
- `INVALID_EXPRESSION`
- `VALIDATION_ERROR`
- `DIVISION_BY_ZERO`
- `EXECUTION_TIMEOUT`
- `INTERNAL_EXECUTION_ERROR`

## 8) LLM-Optimierung

### Tool-Beschreibungen
- Aktiv formulieren: *„Use this tool when…“*
- Konkrete Triggerwörter: „brutto“, „rabatt“, „wachstum“, „zins“.
- Negative Abgrenzung: „Nicht verwenden für…“.

### Best Practices
- **Eindeutige Namen:** `execute_named_calculation` statt generisch `calculate`.
- **Präzise Parameter:** Feldnamen fachlich, stabil, ohne Synonymchaos.
- **Beispiele pro Tool:** mind. 2 positive + 1 negatives Beispiel.
- **Strikte Schemas:** keine impliziten Defaults ohne Dokumentation.
- **Minimale Ambiguität:** Prozent immer als Zahl ohne `%`-Zeichen (z. B. `19`).

## 9) Sicherheits- und Qualitätsaspekte

### Risiken und Gegenmaßnahmen
- **Expression Injection / unsichere Eval-Nutzung:**
  - niemals `eval` verwenden,
  - Whitelist-basierter Parser/AST,
  - nur erlaubte Operatoren/Funktionen.
- **Unerwartete Datentypen:**
  - strikte Schema-Validierung,
  - Coercion nur kontrolliert.
- **Numerische Grenzfälle:**
  - `Decimal`, Präzisions- und Rundungsregeln,
  - Grenzen für Magnitude/Scale.
- **Missbrauch (teure Berechnung):**
  - Timeouts,
  - Max Expression Length,
  - Max AST Depth,
  - Rate-Limits im Gateway.

### Betrieb
- Audit-Logging (wer/wann/was/Ergebniscode),
- Metriken (Fehlerraten, Latenz p95/p99, Top-Calculations),
- Health/Readiness Checks.

---

## Phase 3: Umsetzungsplan mit konkreten Implementierungsschritten

## 10) Schritt-für-Schritt-Implementierungsplan

1. **Projekt-Grundlage schaffen**
   - Ziel: MCP-Server-Rahmen lauffähig.
   - Aufgabe: Server-Entry, Tool-Registrierung, Basiskonfiguration.
   - Ergebnis: Server startet und listet Dummy-Tools.
   - Tests: Smoke-Test Start + Tool-Discovery.

2. **Domänenmodell definieren**
   - Ziel: stabiles internes Berechnungsmodell.
   - Aufgabe: `CalculationDefinition`, Schema-Objekte, Fehlerobjekte.
   - Ergebnis: typsichere Datenstrukturen.
   - Tests: Modell-Serialisierung.

3. **Tool Registry implementieren**
   - Ziel: Berechnungen zentral registrieren/laden.
   - Aufgabe: In-Memory-Registry mit Lookup nach `id+version`.
   - Ergebnis: deterministic Lookup.
   - Tests: existent/nicht existent/version mismatch.

4. **Tool B + C umsetzen (Discovery first)**
   - Ziel: LLM kann Fähigkeiten verstehen.
   - Aufgabe: `list_available_calculations`, `get_calculation_details`.
   - Ergebnis: strukturierte Metadatenantworten.
   - Tests: Filter/Pagination/NotFound.

5. **Validierungsschicht bauen**
   - Ziel: robuste Inputprüfung.
   - Aufgabe: Required/Type/Format/Range/Enum Validatoren.
   - Ergebnis: einheitliche `VALIDATION_ERROR` Details.
   - Tests: positive + negative Cases je Regel.

6. **Execution Engine + Dispatch**
   - Ziel: executor_reference -> Funktion.
   - Aufgabe: Executor-Interface, Dispatcher, Timeout-Handling.
   - Ergebnis: standardisierter Execution-Flow.
   - Tests: erfolgreicher Dispatch, Timeout, interne Exceptions.

7. **Tool D implementieren**
   - Ziel: named calculation ausführen.
   - Aufgabe: Request -> Registry -> Validation -> Executor -> Response.
   - Ergebnis: End-to-End funktionsfähig.
   - Tests: Happy Path + alle Kernfehler.

8. **Tool A implementieren (Expression)**
   - Ziel: sichere Ad-hoc-Rechnung.
   - Aufgabe: sicherer Parser/AST, Operator-Whitelist, Limits.
   - Ergebnis: keine unsichere Codeausführung.
   - Tests: gültige Expressions, Parserfehler, Division durch 0, Komplexitätslimit.

9. **Beispiel-Berechnungen integrieren**
   - Ziel: fachlicher Nutzen im MVP.
   - Aufgabe: 10+ Berechnungen als Definition + Executor.
   - Ergebnis: breites nutzbares Toolset.
   - Tests: Regressionstests je Berechnung.

10. **Observability + Fehlerstandards finalisieren**
   - Ziel: produktionsnahe Qualität.
   - Aufgabe: strukturierte Logs, request_id, Metriken.
   - Ergebnis: nachvollziehbarer Betrieb.
   - Tests: Log-Felder, Fehlercode-Konsistenz.

11. **Dokumentation & Beispiele**
   - Ziel: implementierbar und nutzbar.
   - Aufgabe: README, Tool-Beispiele, Inputformate.
   - Ergebnis: onboarding-fähige Doku.
   - Tests: Doku-Beispiele per Integrationstest.

## 11) Konkrete Implementierungsvorbereitung

### Empfohlene Projektstruktur
```text
mcp-calc-server/
  src/
    server.py
    tools/
      expression_calculator.py
      list_calculations.py
      get_calculation_details.py
      execute_named_calculation.py
    domain/
      models.py
      errors.py
      formats.py
    registry/
      calculation_registry.py
      definitions/
        finance.py
        math.py
    validation/
      validator.py
      rules.py
    executors/
      finance.py
      math.py
      expression_engine.py
    observability/
      logging.py
      metrics.py
  tests/
    unit/
    integration/
  README.md
```

### Interfaces/Funktionen (Vorschlag)
- `CalculationRegistry.register(definition)`
- `CalculationRegistry.get(id, version=None)`
- `Validator.validate(input_schema, validation_rules, inputs)`
- `ExecutionEngine.execute(definition, inputs, context)`
- `ToolHandlers.*` für A-D

### Registrierung neuer Berechnung
1. Definition in `registry/definitions/*.py` hinzufügen.
2. Executor in `executors/*.py` implementieren.
3. `executor_reference` auf Funktion mappen.
4. Unit- und Integrationstests ergänzen.
5. ggf. README-Beispiel ergänzen.

## 12) MVP-Empfehlung

### Zuerst liefern
- Tools: **B, C, D** zuerst, danach A.
- Berechnungen zuerst:
  1) `percentage_of`
  2) `vat_add`
  3) `discount_price`
  4) `average_mean`
  5) `rule_of_three`

### Später
- komplexere Finanzmodelle,
- Batch-Execution,
- Live-Währungskurse,
- Mehrsprachige Format-Normalisierung,
- Policy-/Role-Modelle.

## 13) Abschlussbewertung

- **Erweiterbarkeit:** hoch (Registry + deklarative Definitionen).
- **Wartbarkeit:** hoch (klare Layer, einheitliches Fehlermodell).
- **LLM-Tauglichkeit:** sehr hoch (Discovery + Details + Ausführung).
- **Sicherheit:** gut bis sehr gut bei sicherem Expression-Parser + Limits.
- **Umsetzungsaufwand:** mittel; MVP in kurzen Iterationen realistisch.

## Umsetzung mit Codex – konkrete nächste Prompts

1. **Prompt 1 – Architektur-Scaffold**
   > Erstelle im bestehenden Repo ein minimales MCP-Server-Scaffold mit den vier Tools `expression_calculator`, `list_available_calculations`, `get_calculation_details`, `execute_named_calculation`. Implementiere zunächst nur Platzhalter-Responses, aber bereits mit einheitlichem Response-Envelope (`ok`, `result`, `error`, `meta`).

2. **Prompt 2 – Domänenmodell & Registry**
   > Implementiere ein typsicheres Berechnungsmodell (`CalculationDefinition`) inkl. `input_schema`, `output_schema`, `validation_rules`, `examples` und baue eine in-memory `CalculationRegistry` mit `register`, `get`, `list` und Versionierung.

3. **Prompt 3 – Validierung & Fehlermodell**
   > Implementiere eine generische Validierungsschicht für Required/Type/Format/Range/Enum und ein einheitliches Fehlermodell mit Codes (`VALIDATION_ERROR`, `UNKNOWN_CALCULATION_ID`, `DIVISION_BY_ZERO`, ...). Ergänze Unit-Tests für positive und negative Fälle.

4. **Prompt 4 – Erste echte Berechnungen**
   > Implementiere die Berechnungen `percentage_of`, `vat_add`, `discount_price`, `average_mean`, `rule_of_three` inklusive Executor-Funktionen, Registrierung, Detail-Metadaten und Integrationstests über `execute_named_calculation`.

5. **Prompt 5 – Sichere Expression Engine + Härtung**
   > Implementiere `expression_calculator` mit sicherer AST-basierter Auswertung (kein eval), Operator-Whitelist, Limits für Ausdruckslänge/AST-Tiefe sowie Timeout-Schutz. Ergänze Logging/Metriken und aktualisiere README mit Nutzungsbeispielen.
