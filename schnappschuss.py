"""Speichert jeden Tag einen kleinen Schnappschuss aller Bewertungen (data/verlauf/JJJJ-MM-TT.json) und rechnet
die Trefferquote: Wie haben sich Aktien seit früheren Schnappschüssen entwickelt – je nach Punkten?
Levin, 15.11.2026: „geht noch besser“ → erst messen, ob die Bewertung funktioniert.

  python schnappschuss.py       (läuft per GitHub Actions, schnappschuss.yml)

Schreibt data/verlauf/<heute>.json, data/trefferquote.json und data/trefferquote_zeilen.json (Zeilen fürs Dashboard).
rueckwirkend.py nutzt bewerten(), schnappschuss() und trefferquote() für Tage vor dem 15.11.2026.
"""
import datetime as dt, glob, json, os, subprocess, sys, tempfile

HEUTE = dt.datetime.now(dt.timezone.utc).date()
ORDNER = "data/verlauf"
FELDER = ["punkte", "feinwert", "kurs_eur", "abstand_pct", "top"]
ZEITRAEUME = (("1 Woche", 7), ("1 Monat", 30), ("3 Monate", 91), ("6 Monate", 182), ("1 Jahr", 365))
GRUPPEN = ("7–10", "5–6", "3–4", "unter 3")
AUSREISSER_HOCH = 1.5   # mehr als +150 %: eher Datenfehler (Pence/Pfund) – melden, nicht zählen
AUSREISSER_TIEF = -0.75  # mehr als −75 %: eher Datenfehler (Pence/Pfund, Split ab 4:1) – melden, nicht zählen
# (bis 15.11. war die Grenze ±80 %; dadurch fiel AppLovin mit echten +81 % heraus)
HINWEIS_RUECK = ("Rückblick mit heutigen Regeln auf alte Yahoo-Daten (rueckwirkend), kein echter Test aus der "
                 "Vergangenheit; wenige Wochen sagen wenig.")


def bewerten(yahoo="data/aktien.json", jetzt=None, news=None, hype=None):
    """bewertung.py auf eine Yahoo-Datei, mit leerem alt-Ordner und ohne Depots. Gibt alle.json (Liste) zurück.
    news/hype: Pfade; None = Standard von bewertung.py (Dateien neben der Yahoo-Datei)."""
    tmp = tempfile.mkdtemp()
    alt = os.path.join(tmp, "alt"); neu = os.path.join(tmp, "neu"); os.makedirs(alt)
    jetzt = jetzt or dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    befehl = [sys.executable, "bewertung.py", "--yahoo", yahoo, "--alt", alt, "--neu", neu,
              "--jetzt", jetzt, "--ohne-depots", "--keine-trades"]
    if news:
        befehl += ["--news", news]
    subprocess.run(befehl, check=True, stdout=subprocess.DEVNULL)
    return json.load(open(os.path.join(neu, "alle.json")))


def schnappschuss(alle, datum, **extra):
    """Baut den Schnappschuss {datum, felder, aktien: {Kürzel: [Punkte, Feinwert, Kurs €, Abstand, Top]}}."""
    snap = {r["ticker"]: [r["punkte"], r["feinwert"], r["kurs_eur"], r["abstand_pct"], bool(r.get("top_bedingungen"))]
            for r in alle}
    return {"datum": datum, **extra, "felder": FELDER, "aktien": snap}


def gruppe(p):
    return "7–10" if p >= 7 else "5–6" if p >= 5 else "3–4" if p >= 3 else "unter 3"


def trefferquote(ende):
    """Rechnet data/trefferquote.json und data/trefferquote_zeilen.json. ende = Schnappschuss mit den
    Schlusskursen (normal der von heute). Für jeden Zeitraum der jüngste Schnappschuss, der mindestens so alt ist."""
    stand = dt.date.fromisoformat(ende["datum"])
    jetzt = ende["aktien"]
    dateien = sorted(glob.glob(f"{ORDNER}/????-??-??.json"))
    ergebnis = {"stand": stand.isoformat(), "zeitraeume": {}, "ausreisser": []}
    zeilen = []
    mittel = lambda xs: round(sum(xs) / len(xs) * 100, 1) if xs else None
    genutzt = {}
    for name, tage in ZEITRAEUME:
        alt = [d for d in dateien if (stand - dt.date.fromisoformat(os.path.basename(d)[:10])).days >= tage]
        if alt:
            genutzt[name] = alt[-1]
    # so lange es noch keinen Monat Daten gibt: zusätzlich ab dem ältesten Schnappschuss
    if dateien and "1 Monat" not in genutzt and (stand - dt.date.fromisoformat(os.path.basename(dateien[0])[:10])).days > 0 \
            and dateien[0] not in genutzt.values():
        genutzt["seit Beginn"] = dateien[0]
    for name, datei in genutzt.items():
        a = json.load(open(datei))
        rueck = bool(a.get("rueckwirkend"))
        grp, top = {}, {"ja": [], "nein": []}
        for t, (p, fw, k0, ab, tp) in a["aktien"].items():
            k1 = (jetzt.get(t) or [None] * 5)[2]
            if not k0 or not k1:  # kein Kurs am Anfang oder am Ende: überspringen
                continue
            ret = k1 / k0 - 1
            if ret > AUSREISSER_HOCH or ret < AUSREISSER_TIEF:
                ergebnis["ausreisser"].append(dict(zeitraum=name, seit=a["datum"], ticker=t,
                                                   kurs_eur_vorher=k0, kurs_eur_jetzt=k1, aenderung_pct=round(ret * 100)))
                continue
            grp.setdefault(gruppe(p), []).append(ret)
            top["ja" if tp else "nein"].append(ret)
        alle_r = [x for v in grp.values() for x in v]
        z = {
            "seit": a["datum"],
            "rueckwirkend": rueck,
            "nach_punkten": {g: {"anzahl": len(grp[g]), "mittel_pct": mittel(grp[g])} for g in GRUPPEN if g in grp},
            "top_bedingungen": {k: {"anzahl": len(v), "mittel_pct": mittel(v)} for k, v in top.items()},
            "alle": {"anzahl": len(alle_r), "mittel_pct": mittel(alle_r)},
        }
        ergebnis["zeitraeume"][name] = z
        reihe = [(f"{g} Punkte", grp.get(g, [])) for g in GRUPPEN] + [("alle Aktien", alle_r),
                 ("Top-Bedingungen erfüllt", top["ja"]), ("Top-Bedingungen nicht erfüllt", top["nein"])]
        for g, v in reihe:
            zeilen.append(dict(zeitraum=name, seit=a["datum"], gruppe=g, anzahl=len(v), schnitt_pct=mittel(v), rueckwirkend=rueck))
    if any(z["rueckwirkend"] for z in ergebnis["zeitraeume"].values()):
        ergebnis["hinweis"] = HINWEIS_RUECK
    elif ergebnis["zeitraeume"]:
        ergebnis["hinweis"] = "Wenige Wochen sagen wenig."
    if not zeilen:  # das Dashboard kann keine leere Datei lesen
        zeilen = [dict(zeitraum="", seit=None, gruppe="noch keine Daten", anzahl=0, schnitt_pct=None, rueckwirkend=False)]
    json.dump(ergebnis, open("data/trefferquote.json", "w"), ensure_ascii=False, indent=1)
    json.dump(zeilen, open("data/trefferquote_zeilen.json", "w"), ensure_ascii=False, indent=1)
    return ergebnis


def main():
    os.makedirs(ORDNER, exist_ok=True)
    s = schnappschuss(bewerten(), HEUTE.isoformat())
    json.dump(s, open(f"{ORDNER}/{HEUTE.isoformat()}.json", "w"), separators=(",", ":"))
    ergebnis = trefferquote(s)
    print(json.dumps(ergebnis, ensure_ascii=False)[:600])


if __name__ == "__main__":
    main()
