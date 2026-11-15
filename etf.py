"""ETF-Daten für das Dashboard (Levin, 15.11.2026: ETFs extra, nicht bei den Aktien).
Läuft per GitHub Actions (etf.yml). Liest etfs.txt, holt bei Yahoo Kurse (5 Jahre) und Fondsdaten und schreibt
data/etfs.json. Nur Kennzahlen aus den Daten, keine Punkte (eine ETF-Bewertung kommt nur nach Levins Ja).

Kennzahlen: Rendite 1 Monat, 6 Monate, 1 Jahr, 3 und 5 Jahre pro Jahr (mit Ausschüttungen, angepasste Kurse),
Schwankung 1 Jahr (pro Jahr), größter Rückgang 5 Jahre, Trend (Kurs zur 200-Tage-Linie), Kosten (TER), Fondsgröße.
"""
import datetime as dt, json, math, time
import yfinance as yf


def lies_liste():
    out = []
    for z in open("etfs.txt", encoding="utf-8"):
        z = z.strip()
        if not z or z.startswith("#"):
            continue
        t, _, g = z.partition("|")
        out.append((t.strip(), g.strip() or "Sonstige"))
    return list(dict(out).items())


def zahl(x):
    try:
        x = float(x)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def rund(x, n=1):
    return None if x is None else round(x, n)


def kennzahlen(h):
    c = h["Close"].dropna()
    if len(c) < 30:
        return None
    k, d = float(c.iloc[-1]), c.index[-1]

    def rendite(tage, pa=False):
        alt = c[c.index <= d - dt.timedelta(days=tage)]
        if not len(alt):
            return None
        r = k / float(alt.iloc[-1])
        return ((r ** (365 / tage) - 1) if pa else (r - 1)) * 100

    j = c[c.index > d - dt.timedelta(days=365)]
    lr = (j / j.shift(1)).dropna().apply(math.log)
    vola = float(lr.std()) * math.sqrt(252) * 100 if len(lr) > 100 else None
    dd = float((c / c.cummax() - 1).min()) * 100
    sma200 = float(c.iloc[-200:].mean()) if len(c) >= 200 else None
    sma50 = float(c.iloc[-50:].mean()) if len(c) >= 50 else None
    if sma200 is None:
        trend = None
    elif k > sma200 and (sma50 or 0) > sma200:
        trend = "aufwärts"
    elif k < sma200 and sma50 is not None and sma50 < sma200:
        trend = "abwärts"
    else:
        trend = "seitwärts"
    return {"kurs": rund(k, 2), "kurs_stand": d.date().isoformat(),
            "r_1m": rund(rendite(30)), "r_6m": rund(rendite(182)), "r_1j": rund(rendite(365)),
            "r_3j_pa": rund(rendite(3 * 365, True)), "r_5j_pa": rund(rendite(5 * 365, True)),
            "vola_1j": rund(vola), "max_rueckgang_5j": rund(dd),
            "abstand_200": rund((k / sma200 - 1) * 100) if sma200 else None, "trend": trend,
            "jahre_daten": rund((d - c.index[0]).days / 365, 1)}


def main():
    liste = lies_liste()
    ergebnis, ungueltig = [], []
    for t, gruppe in liste:
        try:
            tk = yf.Ticker(t)
            h = tk.history(period="5y", interval="1d", auto_adjust=True)
            info = {}
            for versuch in range(2):
                try:
                    info = tk.info or {}
                    break
                except Exception:
                    time.sleep(5)
            if info.get("quoteType") not in (None, "ETF"):
                ungueltig.append({"ticker": t, "grund": f"kein ETF ({info.get('quoteType')})"}); continue
            kz = kennzahlen(h) if len(h) else None
            if not kz:
                ungueltig.append({"ticker": t, "grund": "keine Kurse bei Yahoo"}); continue
            ter = zahl(info.get("netExpenseRatio"))
            if ter is None:
                ter = zahl(info.get("annualReportExpenseRatio"))
                ter = ter * 100 if ter is not None and ter < 0.05 else ter
            groesse = zahl(info.get("totalAssets"))
            rendite = zahl(info.get("yield"))
            ergebnis.append({
                "ticker": t, "name": info.get("longName") or info.get("shortName") or t, "gruppe": gruppe,
                "anbieter": info.get("fundFamily"), "waehrung": info.get("currency") or "EUR",
                "ter_pct": rund(ter, 2), "groesse_mrd": rund(groesse / 1e9, 2) if groesse else None,
                "ausschuettung_pct": rund(rendite * 100 if rendite is not None and rendite < 1 else rendite, 2),
                "yahoo_kategorie": info.get("category"), **kz})
        except Exception as e:
            ungueltig.append({"ticker": t, "grund": str(e)[:120]})
        time.sleep(1)
    out = {"stand": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "hinweis": "Nur Kennzahlen aus Yahoo-Daten, keine Punkte. Renditen mit Ausschüttungen (angepasste Kurse). "
                      "Fehlende Werte (z. B. Kosten) liefert Yahoo für manche europäische ETFs nicht.",
           "anzahl": len(ergebnis), "etfs": ergebnis, "ungueltig": ungueltig}
    json.dump(out, open("data/etfs.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(ergebnis)} ETFs, {len(ungueltig)} ungültig: {ungueltig}")


if __name__ == "__main__":
    main()
