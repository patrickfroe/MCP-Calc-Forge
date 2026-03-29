# FAQ für Anwender: MCP-Calc-Forge

Diese FAQ beantwortet typische Fragen zur Nutzung von MCP-Calc-Forge auf Basis der aktuell registrierten Tools und Berechnungen.

## 1) Allgemeines

### Was kann ich mit dieser App berechnen?
Sie können entweder:
- freie mathematische Ausdrücke rechnen (`calculate_expression`), oder
- einen vordefinierten Calculator mit fachlichen Eingabefeldern ausführen (`execute_calculation`).

### Für wen ist die App gedacht?
Für Anwenderinnen und Anwender, die wiederholbare Berechnungen brauchen, z. B. in Vertrieb, Controlling und Finanzplanung.

### Was ist der Unterschied zwischen direkter Berechnung und vordefinierten Calculatoren?
- **Direkte Berechnung:** Sie geben einen Ausdruck wie `(2 + 3) * 5` ein und erhalten einen Zahlenwert.
- **Vordefinierte Calculatoren:** Sie wählen einen fachlichen Rechner (z. B. MwSt., Break-even) mit festen Eingabefeldern und erhalten ein strukturiertes Ergebnis.

## 2) Nutzung

### Wie starte ich eine Berechnung?
Empfohlener Ablauf:
1. `list_calculations` aufrufen.
2. Passenden Calculator auswählen.
3. `get_calculation_details` aufrufen, um Pflichtfelder und Grenzen zu sehen.
4. `execute_calculation` mit `calculation_id` und `input` ausführen.

Für freie Mathematik nutzen Sie direkt `calculate_expression`.

### Wie wähle ich den richtigen Calculator aus?
Vergleichen Sie Name und Beschreibung aus `list_calculations`. Prüfen Sie anschließend mit `get_calculation_details`, ob Eingaben und Ergebnisformat zu Ihrem Anwendungsfall passen.

### Welche Eingaben muss ich machen?
Das hängt vom Calculator ab. Pflichtfelder, Datentypen, Min-/Max-Grenzen und Beispiele erhalten Sie über `get_calculation_details`.

### Wie bekomme ich mein Ergebnis?
Bei Erfolg enthält die Antwort `ok = true` und das Ergebnis im Feld `result`.

## 3) Verfügbare Berechnungen

### Welche Calculatoren gibt es aktuell?
Aktuell sind diese Calculatoren registriert:
- `percentage_of_value`
- `vat_calculation`
- `average`
- `rule_of_three`
- `discount_calculation`
- `percentage_change`
- `compound_interest`
- `simple_interest`
- `weighted_average`
- `gross_margin`
- `markup_calculation`
- `break_even_units`
- `loan_annuity_payment`
- `currency_conversion_static`

### Wofür ist jeder Calculator gedacht, welche Eingaben sind typisch und welche Ergebnisse kommen zurück?
- **`percentage_of_value`:** Prozentwert aus Grundwert und Prozentsatz; Eingaben `base_value`, `percentage`; Ergebnis: Zahl.
- **`vat_calculation`:** Netto/Steuer/Brutto; Eingaben `net_amount`, `vat_rate`; Ergebnis: Objekt mit Steuer- und Bruttobetrag.
- **`average`:** Mittelwert aus einer Liste; Eingabe `values`; Ergebnis: Zahl.
- **`rule_of_three`:** Proportionale Umrechnung (Dreisatz); Eingaben `a`, `b`, `c`; Ergebnis: Zahl.
- **`discount_calculation`:** Rabattbetrag und Endpreis; Eingaben `original_price`, `discount_percentage`; Ergebnis: Objekt mit `discount_amount`, `final_price`.
- **`percentage_change`:** Veränderung alt/neu; Eingaben `old_value`, `new_value`; Ergebnis: Objekt mit absoluter/prozentualer Änderung und Richtung.
- **`compound_interest`:** Zinseszinsrechnung; Eingaben `principal`, `annual_rate`, `years`, optional `compoundings_per_year`; Ergebnis: Objekt mit Endbetrag und Zinsen.
- **`simple_interest`:** Lineare Zinsrechnung; Eingaben `principal`, `rate`, `time_period`; Ergebnis: Objekt mit Zinsen und Endbetrag.
- **`weighted_average`:** Gewichteter Durchschnitt; Eingaben `values`, `weights`; Ergebnis: Zahl.
- **`gross_margin`:** Bruttogewinn und Marge; Eingaben `revenue`, `cost`; Ergebnis: Objekt mit Gewinn und Marge.
- **`markup_calculation`:** Aufschlagkalkulation; Eingaben `cost`, `markup_percentage`; Ergebnis: Objekt mit Aufschlag und Verkaufspreis.
- **`break_even_units`:** Break-even-Menge; Eingaben `fixed_costs`, `price_per_unit`, `variable_cost_per_unit`; Ergebnis: Zahl.
- **`loan_annuity_payment`:** Monatliche Kreditrate; Eingaben `loan_amount`, `annual_interest_rate`, `months`; Ergebnis: Objekt mit Monatsrate, Gesamtkosten, Gesamtzinsen.
- **`currency_conversion_static`:** Währungsumrechnung mit manuellem Kurs; Eingaben `amount`, `exchange_rate`, `source_currency`, `target_currency`; Ergebnis: Objekt mit umgerechnetem Betrag und Kursinfos.

## 4) Eingaben und Fehler

### Was passiert, wenn Eingaben fehlen?
Dann wird die Berechnung mit `ok = false` abgelehnt. Die Antwort enthält ein strukturiertes Fehlerobjekt im Feld `error` mit Hinweisen zu fehlenden Feldern.

### Welche Werteformate werden erwartet?
Je nach Calculator z. B.:
- Zahlen (`number`),
- Ganzzahlen (`integer`, z. B. `months`),
- Listen von Zahlen (`number_list`, z. B. `values`),
- Strings für Währungscodes (`EUR`, `USD`, `GBP`, `CHF`).

### Was bedeuten Fehlermeldungen?
Fehler sind einheitlich strukturiert (`code`, `message`, `details`).
- `VALIDATION_ERROR`: Eingaben passen nicht zum Schema oder zu Grenzwerten.
- `UNKNOWN_CALCULATION_ID`: Die angegebene `calculation_id` ist nicht registriert.
- `INVALID_EXPRESSION`: Der Ausdruck ist ungültig oder enthält nicht erlaubte Elemente.

### Warum wird meine Berechnung abgelehnt?
Häufige Gründe:
- Pflichtfeld fehlt,
- Datentyp stimmt nicht,
- Grenzwert verletzt (z. B. Rabatt > 100),
- fachliche Bedingung verletzt (z. B. `old_value = 0` bei `percentage_change`),
- ungültiger Ausdruck oder Division durch 0 bei `calculate_expression`.

## 5) Fachliche Hinweise

### Wie werden Prozentwerte interpretiert?
Als Prozentzahl, nicht als Dezimalbruch. Beispiel: `20` bedeutet 20 %.

### Wie werden Währungen behandelt?
`currency_conversion_static` verwendet nur den mitgegebenen Wechselkurs. Es gibt keine Live-Kursabfrage.

### Wie werden Listenwerte verarbeitet?
Bei `average` und `weighted_average` müssen Listen numerisch sein. Leere Listen oder unpassende Längen (`values`/`weights`) führen zu Validierungsfehlern.

### Gibt es Besonderheiten bei Rundung oder Grenzwerten?
Berechnungen laufen mit `float`. Eine globale kaufmännische Rundung wird nicht zentral erzwungen. Falls nötig, runden Sie das Ergebnis im Client passend zum Anwendungsfall.

## 6) Beispiele

### Beispiel 1: MwSt. berechnen
- Tool: `execute_calculation`
- `calculation_id`: `vat_calculation`
- Eingabe: `{ "net_amount": 250, "vat_rate": 20 }`
- Ergebnis: `vat_amount = 50`, `gross_amount = 300`

### Beispiel 2: Veränderung zwischen zwei Werten
- Tool: `execute_calculation`
- `calculation_id`: `percentage_change`
- Eingabe: `{ "old_value": 80, "new_value": 100 }`
- Ergebnis: `change_amount = 20`, `change_percentage = 25`, `direction = "increase"`

### Beispiel 3: Freie Mathematik
- Tool: `calculate_expression`
- Eingabe: `(2 + 3) * 5`
- Ergebnis: `25`

### Beispiel 4: Statische Währungsumrechnung
- Tool: `execute_calculation`
- `calculation_id`: `currency_conversion_static`
- Eingabe: `{ "amount": 100, "exchange_rate": 1.08, "source_currency": "EUR", "target_currency": "USD" }`
- Ergebnis: `converted_amount = 108`
