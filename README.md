# aktien-daten

Holt Mo–Fr zweimal täglich kostenlose Aktiendaten von Yahoo Finance (über die inoffizielle Bibliothek yfinance)
und speichert sie in `data/aktien.json`. Claude liest die Datei für Levins Dashboard „Aktien-Liste“.

- Aktien: `tickers.txt` (eine pro Zeile)
- Programm: `fetch.py`
- Zeitplan: `.github/workflows/taeglich.yml` (manuell starten: Actions → „Aktien-Daten holen“ → Run workflow)

Nur Spielgeld-Simulation, keine Anlageberatung.

## Bewertung

`bewertung.py` rechnet aus `data/aktien.json` die Liste der 50 besten Aktien und das Musterdepot (feste Regeln:
PEG, Kursziel-Abstand, Kapitalrendite, freier Cashflow, Schulden, Analystenzahl, Trend, Schätzungs-Änderungen;
Top-Treffer nur ohne Abwärtstrend, höchstens 2 je Branche, keine Speicherchip-Zykliker; kein Kauf kurz vor Quartalszahlen).
Die geplante Aufgabe in Claude lädt diese Datei und führt sie bei jedem Lauf aus.
