# aktien-daten

Holt Mo–Fr kostenlose Aktiendaten von Yahoo Finance (über die inoffizielle Bibliothek yfinance)
und speichert sie in `data/aktien.json`. Claude liest die Datei für Levins Dashboard „Aktien-Liste“.

- Aktien: `tickers.txt` (eine pro Zeile; rund 600: S&P 500, große Euro-Aktien, weitere große US-Werte)
- Programm: `fetch.py`
- Grunddaten (Kursziele, Gewinnschätzungen, Kennzahlen): `.github/workflows/grunddaten.yml`, Mo–Fr mehrere
  Versuche zwischen 1:41 und 5:41 UTC (der erste, der durchkommt, holt alles; ca. 15 Minuten) und bei jeder
  Änderung an `tickers.txt` oder `fetch.py`
- Kurse und Trends: `.github/workflows/kurse-schleife.yml` – ein Lauf bleibt bis zu 5,5 Stunden aktiv, holt stündlich
  um :17 die Kurse und startet am Ende selbst den nächsten (Mo–Fr bis 21 Uhr UTC), weil GitHub geplante Läufe oft
  auslässt. `taeglich.yml` nur noch zum manuellen Start.
- Manuell starten: Actions → Workflow wählen → Run workflow

Nur Spielgeld-Simulation, keine Anlageberatung.

## Bewertung

`bewertung.py` rechnet aus `data/aktien.json` die Liste der 50 besten Aktien und das Musterdepot (feste Regeln:
PEG, Kursziel-Abstand, Kapitalrendite, freier Cashflow, Schulden, Analystenzahl, langer und kurzer Trend, Schätzungs-Änderungen;
Reihenfolge: erst Punkte, bei Gleichstand der Feinwert 0–100 (Rang jeder Kennzahl unter allen bewerteten Aktien);
Top-Treffer nur ohne Abwärtstrend, höchstens 2 je Branche, keine Speicherchip-Zykliker; kein Kauf kurz vor Quartalszahlen).
Die geplante Aufgabe in Claude lädt diese Datei und führt sie bei jedem Lauf aus.
