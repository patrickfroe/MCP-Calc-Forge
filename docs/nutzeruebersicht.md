# Nutzerübersicht: MCP-Calc-Forge

## Kurzfassung für Anwender

MCP-Calc-Forge ist ein Berechnungsservice, der Ihnen zwei Wege bietet:

1. **Direkte mathematische Ausdrücke rechnen** (z. B. `(2 + 3) * 5`).
2. **Vordefinierte Fachrechner nutzen** (z. B. MwSt., Rabatt, Zins, Break-even, Währungsumrechnung).

Typischer Ablauf:
- Rechner auswählen,
- Eingabewerte senden,
- Ergebnis als strukturierte Antwort erhalten,
- bei fehlerhaften Eingaben eine klare Fehlermeldung mit Feldhinweisen bekommen.

---


## FAQ

- Eine kompakte Fragen-und-Antworten-Seite für Anwender finden Sie in `docs/faq.md`.

---

## 1) Kurze Einführung

### Was kann die Applikation?
Die Applikation führt Berechnungen über MCP-Tools aus. Sie unterstützt sowohl freie mathematische Expressions als auch fest definierte Rechner mit klaren Eingabefeldern und validierten Ergebnissen.

### Für wen ist sie gedacht?
Für fachliche Nutzerinnen und Nutzer, die reproduzierbare Berechnungen brauchen, z. B. in:
- Einkauf/Vertrieb (Rabatt, Aufschlag, Marge),
- Finanzen (Zinsen, Kreditrate),
- Controlling (Break-even, Durchschnitt),
- allgemeiner Prozent- und Verhältnisrechnung.

---

## 2) Hauptfunktionen

### A) Direkte mathematische Berechnungen
Tool: **`calculate_expression`**

- Rechnet mathematische Ausdrücke mit `+`, `-`, `*`, `/` und Klammern.
- Beispiel: `(2 + 3) * 5` → `25`.

### B) Vordefinierte Berechnungen / Calculatoren
Tool: **`execute_calculation`**

- Führt einen ausgewählten Rechner über `calculation_id` aus.
- Die Eingaben werden als Objekt im Feld `input` übergeben.

### C) Abruf von Berechnungsdetails
Tool: **`get_calculation_details`**

- Liefert zu einer `calculation_id`:
  - Beschreibung,
  - erwartete Eingabefelder,
  - Datentypen,
  - Pflicht-/Optionalfelder,
  - Min-/Max-Grenzen,
  - Beispielinputs.

### D) Verfügbare Berechnungen auflisten
Tool: **`list_calculations`**

- Liefert eine Liste aller aktuell registrierten Rechner.

### Kategorien (fachlich gruppiert)
- **Prozent & Preis**: Prozentwert, MwSt., Rabatt, Aufschlag, prozentuale Veränderung.
- **Durchschnitt & Verhältnisse**: Durchschnitt, gewichteter Durchschnitt, Dreisatz.
- **Finanzen**: einfacher Zins, Zinseszins, Kreditrate.
- **Unternehmen/Controlling**: Bruttomarge, Break-even.
- **Währung**: statische Umrechnung mit manuellem Wechselkurs.

---

## 3) Verfügbare Berechnungen

> Hinweis: Die IDs unten sind die Werte, die Sie bei `execute_calculation` als `calculation_id` verwenden.

### 1. Prozentwert berechnen (`percentage_of_value`)
- **Zweck:** Prozentwert aus Grundwert und Prozentsatz.
- **Typische Eingaben:** `base_value`, `percentage`.
- **Typisches Ergebnis:** eine Zahl (Prozentwert).
- **Beispiel:** 10 % von 200 → 20.

### 2. Mehrwertsteuer (`vat_calculation`)
- **Zweck:** Netto, Steuerbetrag und Brutto berechnen.
- **Typische Eingaben:** `net_amount` (>= 0), `vat_rate` (>= 0).
- **Typisches Ergebnis:** Objekt mit `net_amount`, `vat_rate`, `vat_amount`, `gross_amount`.
- **Beispiel:** 20 % auf 100 → Steuer 20, Brutto 120.

### 3. Durchschnitt (`average`)
- **Zweck:** Mittelwert aus Zahlenliste.
- **Typische Eingaben:** `values` als nicht-leere Zahlenliste.
- **Typisches Ergebnis:** eine Zahl.
- **Beispiel:** [2, 4, 6] → 4.

### 4. Dreisatz (`rule_of_three`)
- **Zweck:** Proportionale Zielgröße nach Dreisatz.
- **Typische Eingaben:** `a`, `b`, `c` (mit `a != 0`).
- **Typisches Ergebnis:** eine Zahl.
- **Beispiel:** 2 : 4 = 5 : x → x = 10.

### 5. Rabatt (`discount_calculation`)
- **Zweck:** Rabattbetrag und Endpreis.
- **Typische Eingaben:** `original_price` (>= 0), `discount_percentage` (0 bis 100).
- **Typisches Ergebnis:** Objekt mit `discount_amount`, `final_price`.
- **Beispiel:** 15 % auf 100 → Rabatt 15, Endpreis 85.

### 6. Prozentuale Veränderung (`percentage_change`)
- **Zweck:** Absolute und prozentuale Änderung zwischen altem und neuem Wert.
- **Typische Eingaben:** `old_value`, `new_value` (mit `old_value != 0`).
- **Typisches Ergebnis:** Objekt mit `change_amount`, `change_percentage`, `direction` (`increase`/`decrease`/`no_change`).
- **Beispiel:** 80 auf 100 → +20 und +25 %.

### 7. Zinseszins (`compound_interest`)
- **Zweck:** Endkapital und Zinsertrag mit Zinseszins.
- **Typische Eingaben:** `principal` (>= 0), `annual_rate` (>= 0), `years` (>= 0), optional `compoundings_per_year` (Ganzzahl >= 1).
- **Typisches Ergebnis:** Objekt mit `final_amount`, `interest_amount`.
- **Beispiel:** 1.000 bei 5 % für 2 Jahre (jährlich) → Endkapital > 1.100.

### 8. Einfacher Zins (`simple_interest`)
- **Zweck:** Lineare Verzinsung ohne Wiederverzinsung.
- **Typische Eingaben:** `principal` (>= 0), `rate` (>= 0), `time_period` (>= 0).
- **Typisches Ergebnis:** Objekt mit `interest_amount`, `final_amount`.
- **Beispiel:** 1.000 bei 5 % für 3 Jahre → Zinsen 150, Endbetrag 1.150.

### 9. Gewichteter Durchschnitt (`weighted_average`)
- **Zweck:** Durchschnitt mit unterschiedlich starken Gewichten.
- **Typische Eingaben:** `values` und `weights` als Zahlenlisten gleicher Länge; Summe der Gewichte darf nicht 0 sein.
- **Typisches Ergebnis:** eine Zahl.
- **Beispiel:** Werte [1,2,3], Gewichte [1,1,2] → 2,25.

### 10. Bruttomarge (`gross_margin`)
- **Zweck:** Bruttogewinn und Margenquote.
- **Typische Eingaben:** `revenue` (> 0), `cost` (>= 0).
- **Typisches Ergebnis:** Objekt mit `gross_profit`, `margin_percentage`.
- **Beispiel:** Umsatz 150, Kosten 90 → Gewinn 60, Marge 40 %.

### 11. Aufschlag (`markup_calculation`)
- **Zweck:** Aufschlagbetrag und Verkaufspreis.
- **Typische Eingaben:** `cost` (>= 0), `markup_percentage` (>= 0).
- **Typisches Ergebnis:** Objekt mit `markup_amount`, `selling_price`.
- **Beispiel:** 25 % auf 80 → Aufschlag 20, Verkaufspreis 100.

### 12. Break-even-Menge (`break_even_units`)
- **Zweck:** Stückzahl für Kostendeckung.
- **Typische Eingaben:** `fixed_costs` (>= 0), `price_per_unit`, `variable_cost_per_unit` mit `price_per_unit > variable_cost_per_unit`.
- **Typisches Ergebnis:** eine Zahl (erforderliche Menge).
- **Beispiel:** 1.000 Fixkosten, Preis 50, variable Kosten 30 → 50 Stück.

### 13. Kreditrate (Annuität) (`loan_annuity_payment`)
- **Zweck:** Konstante monatliche Rate eines Kredits.
- **Typische Eingaben:** `loan_amount` (>= 0), `annual_interest_rate` (>= 0), `months` (Ganzzahl >= 1).
- **Typisches Ergebnis:** Objekt mit `monthly_payment`, `total_payment`, `total_interest`.
- **Beispiel:** 10.000 bei 6 % über 24 Monate → monatliche Rate + Gesamtkosten.

### 14. Währungsumrechnung mit statischem Kurs (`currency_conversion_static`)
- **Zweck:** Umrechnung mit manuell vorgegebenem Kurs (ohne Live-Daten).
- **Typische Eingaben:** `amount`, `exchange_rate` (> 0), `source_currency`, `target_currency`.
- **Erlaubte Währungen:** `EUR`, `USD`, `GBP`, `CHF`.
- **Typisches Ergebnis:** Objekt mit `converted_amount`, `source_currency`, `target_currency`, `exchange_rate`.
- **Beispiel:** 100 EUR bei 1,08 → 108 USD.

---

## 4) Nutzung aus Anwendersicht

### Schritt-für-Schritt

1. **Rechner finden**
   - Erst `list_calculations` aufrufen und passenden Rechner anhand Name/Beschreibung wählen.

2. **Eingaben prüfen**
   - Mit `get_calculation_details` prüfen, welche Felder Pflicht sind, welche Datentypen gelten und welche Grenzen existieren.

3. **Berechnung ausführen**
   - `execute_calculation` mit `calculation_id` und `input` senden.

4. **Ergebnis lesen**
   - Bei Erfolg: `ok = true`, Ergebnis in `result`.
   - Bei Fehler: `ok = false`, Details in `error` (inklusive Feldhinweisen).

### Mini-Beispiel (Ablauf)

- Auswahl: `vat_calculation`
- Input: `{ "net_amount": 250, "vat_rate": 20 }`
- Ergebnis: `{ "net_amount": 250.0, "vat_rate": 20.0, "vat_amount": 50.0, "gross_amount": 300.0 }`

---

## 5) Wichtige Hinweise

### Validierung und häufige Eingabefehler
- Pflichtfelder müssen vorhanden sein.
- Datentypen müssen passen (z. B. `months` als Ganzzahl).
- Listenfelder (`number_list`) dürfen nicht leer sein und müssen nur Zahlen enthalten.
- Viele Felder haben Grenzwerte (z. B. Rabatt max. 100).
- Bei unzulässigen Werten erhalten Sie ein strukturiertes Fehlerobjekt (`code`, `message`, `details`).

### Hinweise zu Prozenten, Währungen und Rundung
- **Prozentwerte** werden als normale Prozentzahlen übergeben (z. B. `20` für 20 %).
- **Währungsumrechnung** nutzt den übergebenen Kurs; es gibt **keine** Live-Kursabfrage.
- **Rundung:** Ergebnisse werden rechnerisch als Fließkommazahlen zurückgegeben; eine kaufmännische Rundung auf 2 Stellen müssen Sie bei Bedarf in Ihrem Client vornehmen.

### Grenzen der Expression-Berechnung
- Erlaubt sind nur Zahlen, Grundrechenarten und Vorzeichen.
- Nicht erlaubt sind Namen, Funktionsaufrufe und Attribute.
- Division durch 0 liefert einen Fehler.

---

## 6) Konkrete Anwendungsbeispiele

### Beispiel A: Angebotskalkulation im Vertrieb
1. Mit `markup_calculation` Verkaufspreis aus Kosten und Aufschlag berechnen.
2. Mit `discount_calculation` optionalen Rabatt simulieren.
3. Mit `gross_margin` prüfen, wie sich die Marge verändert.

### Beispiel B: Finanzplanung
1. `simple_interest` für lineare Zinsrechnung.
2. `compound_interest` für Zinseszins-Effekt.
3. `loan_annuity_payment` für monatliche Kreditbelastung.

### Beispiel C: Reporting/Controlling
1. `weighted_average` für KPI-Mittelwerte mit Gewichten.
2. `percentage_change` zur Entwicklung zwischen zwei Perioden.
3. `break_even_units` zur Abschätzung der nötigen Absatzmenge.

---

## Kompakte Tool-Referenz

- **`list_calculations`**: zeigt alle verfügbaren Rechner.
- **`get_calculation_details`**: zeigt Eingaben, Grenzen und Beispielwerte eines Rechners.
- **`execute_calculation`**: führt den gewählten Rechner aus.
- **`calculate_expression`**: rechnet einen freien mathematischen Ausdruck.
