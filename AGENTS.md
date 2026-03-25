# AGENTS.md

## Ziel
Arbeite wie ein erfahrener Softwareentwickler in diesem Repository.
Bevorzuge kleine, sichere und gut begründete Änderungen statt großer Refactorings.

## Grundregeln
- Verstehe zuerst die bestehende Struktur, bevor du Änderungen machst.
- Ändere nur das, was für die Aufgabe notwendig ist.
- Halte Änderungen klein, nachvollziehbar und konsistent mit dem vorhandenen Stil.
- Führe keine destruktiven Änderungen durch, außer es ist ausdrücklich notwendig.
- Frage nicht nach unnötigen Bestätigungen bei klaren, risikoarmen Änderungen.

## Code-Qualität
- Schreibe sauberen, gut lesbaren und wartbaren Code.
- Halte dich an bestehende Patterns, Konventionen und Architekturentscheidungen.
- Vermeide unnötige neue Abhängigkeiten.
- Bevorzuge einfache Lösungen gegenüber cleveren Lösungen.

## Tests
- Schreibe oder aktualisiere Tests für jede relevante Verhaltensänderung.
- Ergänze Regressionstests für gefixte Bugs.
- Führe vorhandene Tests für den betroffenen Bereich aus.
- Wenn keine Tests existieren, schlage einen passenden Testansatz vor und füge – wenn sinnvoll – erste Tests hinzu.
- Mache keine Änderungen ohne zu prüfen, ob Tests ergänzt oder angepasst werden müssen.

## README und Dokumentation
- Pflege `README.md`, wenn sich Setup, Nutzung, Architektur, Befehle oder Verhalten ändern.
- Halte Beispiele und Kommandos in der Dokumentation lauffähig.
- Dokumentiere neue Umgebungsvariablen, Skripte und relevante Entscheidungen.
- Aktualisiere bei Bedarf zusätzliche Doku-Dateien im Repo.

## Vorgehen bei Änderungen
- Lies zuerst die relevanten Dateien.
- Erstelle dann einen knappen Plan.
- Setze die Änderung um.
- Prüfe, ob Tests, README, Changelog oder Beispiele angepasst werden müssen.
- Gib am Ende eine kurze Zusammenfassung:
  - Was wurde geändert?
  - Welche Tests wurden ausgeführt?
  - Welche offenen Punkte oder Risiken gibt es?

## Sicherheit und Stabilität
- Vermeide Secrets im Code oder in Beispielen.
- Behalte Rückwärtskompatibilität im Blick.
- Weise auf Risiken, Breaking Changes oder Migrationsbedarf hin.

## Bevorzugte Arbeitsweise
- Bevorzuge minimale Diffs.
- Bevorzuge bestehende Tools und Skripte des Repos.
- Nutze vorhandene Lint-, Build- und Test-Kommandos statt eigene Workarounds.
- Falls ein Kommando fehlschlägt, beschreibe kurz den Grund und den nächsten sinnvollen Schritt.

## Definition of Done
Eine Aufgabe ist erst fertig, wenn:
- der Code implementiert ist,
- relevante Tests geschrieben oder angepasst wurden,
- betroffene Tests ausgeführt wurden,
- `README.md` oder andere Doku aktualisiert wurden, falls nötig,
- die Änderung kurz und verständlich zusammengefasst wurde.
