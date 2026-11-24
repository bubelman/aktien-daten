"""Rückblick-Test der Trend-Punkte (Auftrag A13 vom Chef, 22.11.2026; = A3.2).

Frage: Hatten Aktien mit steigendem Trend in den letzten 3 Jahren danach wirklich bessere Renditen?
Nur die Kurs-Regeln lassen sich ehrlich über Jahre testen (alte Analystenschätzungen gibt es nicht).

Die Trend-Regeln sind genau wie in fetch.py (kurse_und_trends) und bewertung.py (trend_pkt, kurz_pkt):
- Trend lang:  Kurs > SMA200 und 6 Monate (126 Börsentage) im Plus -> steigend (+1);
               Kurs < SMA200 und 6 Monate im Minus -> fallend (-1); sonst seitwärts (0).
- Trend kurz:  Kurs > SMA50 und 1 Monat (21 Börsentage) im Plus -> steigend (+1); umgekehrt fallend (-1).
Je Monatsende (letzter Handelstag der Aktie im Monat) werden beide Trends berechnet und mit der Rendite bis zum
Monatsende 1 bzw. 3 Monate später verglichen. Keine Regeländerung – nur Messung.

Aufruf im GitHub-Workflow rueckblick.yml (nur von Hand): python rueckblick_trend.py
Lokal ohne Yahoo (Test mit Zufallskursen): python rueckblick_trend.py --test
Ergebnis: data/rueckblick_trend.json
"""
import argparse
import json
import math
import random
import statistics
import sys
import time
from datetime import datetime, timezone

MAX_AKTIEN = 800
JAHRE = 3


def stichprobe(pfad="tickers.txt", max_n=MAX_AKTIEN):
    """Feste Stichprobe: alle .DE-Aktien, dann US-Aktien (ohne Punkt im Kürzel) in der Reihenfolge von tickers.txt."""
    ts = [z.strip() for z in open(pfad, encoding="utf-8") if z.strip() and not z.startswith("#")]
    de = [t for t in ts if t.endswith(".DE")]
    us = [t for t in ts if "." not in t]
    return de + us[:max(0, max_n - len(de))]


def trend(c, sma, r):
    return 1 if c > sma and r > 0 else -1 if c < sma and r < 0 else 0


def signale(datum, kurse):
    """datum, kurse: Listen gleicher Länge (aufsteigend). Gibt je Monatsende ein Signal mit Folgerenditen zurück."""
    n = len(kurse)
    ende = [i for i in range(n) if i == n - 1 or datum[i][:7] != datum[i + 1][:7]]
    # das letzte Element ist nur dann ein Monatsende, wenn der Monat schon vorbei ist – sonst weglassen
    if ende and ende[-1] == n - 1:
        ende = ende[:-1]
    out = []
    for k, i in enumerate(ende):
        if i < 199:
            continue
        c = kurse[i]
        sma200 = sum(kurse[i - 199:i + 1]) / 200
        r6 = c / kurse[i - 126] - 1
        sma50 = sum(kurse[i - 49:i + 1]) / 50
        r1m = c / kurse[i - 21] - 1
        s = dict(monat=datum[i][:7], lang=trend(c, sma200, r6), kurz=trend(c, sma50, r1m))
        for m, schritt in (("r1", 1), ("r3", 3)):
            j = ende[k + schritt] if k + schritt < len(ende) else None
            s[m] = kurse[j] / c - 1 if j is not None else None
        out.append(s)
    return out


def spearman(x, y):
    def raenge(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for q in range(i, j + 1):
                r[o[q]] = (i + j) / 2
            i = j + 1
        return r
    if len(x) < 10:
        return None
    rx, ry = raenge(x), raenge(y)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    sx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    sy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / (sx * sy)


def auswerten(alle_signale):
    """alle_signale: {ticker: [signal, ...]} -> Ergebnis-Dict."""
    zeilen = [dict(s, ticker=t) for t, ss in alle_signale.items() for s in ss]
    erg = {}
    for m in ("r1", "r3"):
        z = [s for s in zeilen if s[m] is not None]
        # Monatsmittel aller Aktien (gleich gewichtet) als Vergleich; Mehrrendite = Rendite − Monatsmittel
        mittel = {}
        for s in z:
            mittel.setdefault(s["monat"], []).append(s[m])
        mittel = {k: statistics.fmean(v) for k, v in mittel.items()}
        gruppen = {}
        for name, key in (("lang", lambda s: s["lang"]), ("kurz", lambda s: s["kurz"]),
                          ("summe", lambda s: s["lang"] + s["kurz"])):
            g = {}
            for s in z:
                g.setdefault(key(s), []).append(s)
            gruppen[name] = {}
            for wert in sorted(g):
                v = g[wert]
                mehr = [s[m] - mittel[s["monat"]] for s in v]
                gruppen[name][str(wert)] = dict(
                    n=len(v),
                    rendite_mittel_pct=round(statistics.fmean(s[m] for s in v) * 100, 2),
                    rendite_median_pct=round(statistics.median(s[m] for s in v) * 100, 2),
                    mehrrendite_mittel_pct=round(statistics.fmean(mehr) * 100, 2),
                    besser_als_mittel_pct=round(sum(1 for x in mehr if x > 0) / len(v) * 100, 1),
                )
        # IC je Monat (Rangkorrelation Trend-Summe ↔ Rendite), dann Mittel und t-Wert über die Monate
        ics = []
        for monat in sorted(mittel):
            v = [s for s in z if s["monat"] == monat]
            ic = spearman([s["lang"] + s["kurz"] for s in v], [s[m] for s in v])
            if ic is not None:
                ics.append(ic)
        ic_info = dict(monate=len(ics))
        if len(ics) >= 2:
            sd = statistics.stdev(ics)
            ic_info.update(mittel=round(statistics.fmean(ics), 4),
                           t_wert=round(statistics.fmean(ics) / (sd / math.sqrt(len(ics))), 2) if sd else None,
                           anteil_positiv_pct=round(sum(1 for x in ics if x > 0) / len(ics) * 100, 1))
        erg["1_monat" if m == "r1" else "3_monate"] = dict(
            alle=dict(n=len(z), rendite_mittel_pct=round(statistics.fmean(s[m] for s in z) * 100, 2) if z else None),
            gruppen=gruppen, ic_trend_summe=ic_info)
    monate = sorted({s["monat"] for s in zeilen})
    return dict(monate_von=monate[0] if monate else None, monate_bis=monate[-1] if monate else None,
                signale=len(zeilen), aktien=len(alle_signale), ergebnis=erg)


def laden_yahoo(tickers):
    import yfinance as yf
    daten, fehlt = {}, []
    for i in range(0, len(tickers), 200):
        teil = tickers[i:i + 200]
        df = None
        for versuch in range(3):
            try:
                df = yf.download(teil, period=f"{JAHRE + 1}y", interval="1d", auto_adjust=True, group_by="ticker",
                                 threads=True, progress=False)
                break
            except Exception as e:
                print("Sammelabruf fehlgeschlagen:", e)
                time.sleep(20)
        for s in teil:
            try:
                h = (df[s]["Close"] if len(teil) > 1 else df["Close"]).dropna()
            except Exception:
                h = None
            if h is None or len(h) < 260:
                fehlt.append(s)
                continue
            daten[s] = ([str(d)[:10] for d in h.index], [float(x) for x in h.values])
        time.sleep(3)
    return daten, fehlt


def laden_test(n=120, tage=1000, seed=7):
    """Zufallskurse für den lokalen Test: die Hälfte der Aktien mit Momentum (Trend setzt sich fort)."""
    rnd = random.Random(seed)
    from datetime import date, timedelta
    tag, datum = date(2022, 11, 1), []
    while len(datum) < tage:
        if tag.weekday() < 5:
            datum.append(tag.isoformat())
        tag += timedelta(days=1)
    daten = {}
    for k in range(n):
        p, drift, kurse = 100.0, 0.0, []
        for _ in range(tage):
            if k % 2 == 0:
                drift = 0.98 * drift + rnd.gauss(0, 0.0004)
            p *= math.exp(drift + rnd.gauss(0, 0.015))
            kurse.append(p)
        daten[f"T{k}"] = (datum, kurse)
    return daten, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true", help="Zufallskurse statt Yahoo (nur zum Prüfen des Programms)")
    ap.add_argument("--aus", default="data/rueckblick_trend.json")
    a = ap.parse_args()
    if a.test:
        daten, fehlt = laden_test()
        tickers = list(daten)
    else:
        tickers = stichprobe()
        daten, fehlt = laden_yahoo(tickers)
    alle = {}
    for t, (datum, kurse) in daten.items():
        # nur die letzten JAHRE Jahre auswerten (das Jahr davor braucht SMA200 und 6 Monate als Vorlauf)
        ss = signale(datum, kurse)
        grenze = f"{int(datum[-1][:4]) - JAHRE}{datum[-1][4:7]}"
        alle[t] = [s for s in ss if s["monat"] > grenze]
    erg = auswerten(alle)
    erg.update(
        stand=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        test_mit_zufallskursen=bool(a.test),
        stichprobe=dict(gewollt=len(tickers), mit_kursen=len(daten), ohne_kurse=len(fehlt), ohne_kurse_liste=fehlt[:100],
                        auswahl=f"alle .DE-Aktien und US-Aktien aus tickers.txt (Reihenfolge der Datei), höchstens {MAX_AKTIEN}"),
        regeln="Trend lang: Kurs vs. SMA200 und 6 Monate; Trend kurz: Kurs vs. SMA50 und 1 Monat (wie fetch.py/bewertung.py). "
               "Gruppen: +1 steigend, 0 seitwärts, -1 fallend; 'summe' = lang + kurz (-2 bis +2), so wie sie in die Punkte eingehen.",
        grenzen=[
            "Überlebende-Verzerrung: nur Aktien, die es heute noch gibt (Pleiten und Übernahmen fehlen). Das schönt alle Gruppen, "
            "fallende Trends vermutlich am meisten.",
            "Keine Handelskosten, keine Steuern, keine Dividenden außer über bereinigte Kurse (auto_adjust).",
            f"Nur {JAHRE} Jahre und nur USA/Deutschland – ein einziger Marktverlauf, kein Beweis für die Zukunft.",
            "Renditen überlappen beim 3-Monats-Test (jeden Monat neu gemessen) – der t-Wert wirkt dadurch zu hoch.",
            "Getestet sind nur die Trend-Punkte, nicht die übrigen Punkte (dafür fehlen alte Analystendaten).",
            "Keine Regeländerung: das Ergebnis ist nur eine Messung.",
        ],
    )
    with open(a.aus, "w", encoding="utf-8") as f:
        json.dump(erg, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: erg[k] for k in ("aktien", "signale", "monate_von", "monate_bis")}, ensure_ascii=False))
    print(json.dumps(erg["ergebnis"]["1_monat"]["gruppen"]["summe"], ensure_ascii=False))
    if not a.test and len(daten) < 0.5 * len(tickers):
        print("Zu wenige Kurse geladen – Ergebnis unsicher", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
