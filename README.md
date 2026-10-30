# aktien-daten

Holt Mo–Fr zweimal täglich kostenlose Aktiendaten von Yahoo Finance (über die inoffizielle Bibliothek yfinance)
und speichert sie in `data/aktien.json`. Claude liest die Datei für Levins Dashboard „Aktien-Liste“.

- Aktien: `tickers.txt` (eine pro Zeile)
- Programm: `fetch.py`
- Zeitplan: `.github/workflows/taeglich.yml` (manuell starten: Actions → „Aktien-Daten holen“ → Run workflow)

Nur Spielgeld-Simulation, keine Anlageberatung.
