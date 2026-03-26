# Ziel
Implementiere einen MCP-Server in Python für Berechnungen.

# Stack
- Python 3.10+
- bestehende Architektur und Konventionen des Repos beibehalten
- keine Business-Logik in MCP-Tool-Handlern

# Architekturregeln
- Berechnungen werden zentral in einer Registry verwaltet
- jede Berechnung liegt als eigenes Modul unter app/calculations/catalog/
- Validierung und Ausführung sind getrennt
- Expression-Auswertung ist getrennt von benannten Berechnungen
- kein eval() für Expressions

# Qualitätsregeln
- für jede neue Berechnung mindestens ein Unit-Test
- Fehler immer im einheitlichen Fehlerformat zurückgeben
- nur minimal notwendige Änderungen vornehmen
- bei komplexeren Tasks zuerst einen Plan erstellen

# Done when
- 4 MCP-Tools vorhanden
- mindestens 3 Beispielberechnungen implementiert
- Tests für Happy Paths und Fehlerfälle vorhanden
- README erklärt Registrierung neuer Berechnungen
