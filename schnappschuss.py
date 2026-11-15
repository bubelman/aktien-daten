"""Speichert jeden Tag einen kleinen Schnappschuss aller Bewertungen (data/verlauf/JJJJ-MM-TT.json) und rechnet
die Trefferquote: Wie haben sich Aktien seit früheren Schnappschüssen entwickelt – je nach Punkten?
Levin, 15.11.2026: „geht noch besser“ → erst messen, ob die Bewertung funktioniert.

  python schnappschuss.py       (läuft per GitHub Actions, schnappschuss.yml)
"""
import datetime as dt, glob, json, os, subprocess, sys, tempfile

HEUTE = dt.datetime.now(dt.timezone.utc).date()
ORDNER = "data/verlauf"


def bewerten():
    tmp = tempfile.mkdtemp()
    alt = os.path.join(tmp, "alt"); neu = os.path.join(tmp, "neu"); os.makedirs(alt)
    jetzt = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    subprocess.run([sys.executable, "bewertung.py", "--yahoo", "data/aktien.json", "--alt", alt, "--neu", neu,
                    "--jetzt", jetzt, "--ohne-depots", "--keine-trades"], check=True, stdout=subprocess.DEVNULL)
    return json.load(open(os.path.join(neu, "alle.json")))


def gruppe(p):
    return "7–10" if p >= 7 else "5–6" if p >= 5 else "3–4" if p >= 3 else "unter 3"


def main():
    os.makedirs(ORDNER, exist_ok=True)
    alle = bewerten()
    snap = {r["ticker"]: [r["punkte"], r["feinwert"], r["kurs_eur"], r["abstand_pct"], bool(r.get("top_bedingungen"))]
            for r in alle}
    json.dump({"datum": HEUTE.isoformat(), "felder": ["punkte", "feinwert", "kurs_eur", "abstand_pct", "top"],
               "aktien": snap}, open(f"{ORDNER}/{HEUTE.isoformat()}.json", "w"), separators=(",", ":"))

    # Trefferquote: für jeden Zeitraum den ältesten Schnappschuss, der mindestens so alt ist
    dateien = sorted(glob.glob(f"{ORDNER}/????-??-??.json"))
    ergebnis = {"stand": HEUTE.isoformat(), "zeitraeume": {}}
    for name, tage in (("1 Woche", 7), ("1 Monat", 30), ("3 Monate", 91), ("6 Monate", 182), ("1 Jahr", 365)):
        alt = [d for d in dateien if (HEUTE - dt.date.fromisoformat(os.path.basename(d)[:10])).days >= tage]
        if not alt:
            continue
        a = json.load(open(alt[-1]))
        grp, top = {}, {"ja": [], "nein": []}
        for t, (p, fw, k0, ab, tp) in a["aktien"].items():
            if t not in snap or not k0:
                continue
            ret = snap[t][2] / k0 - 1
            grp.setdefault(gruppe(p), []).append(ret)
            top["ja" if tp else "nein"].append(ret)
        mittel = lambda xs: round(sum(xs) / len(xs) * 100, 1) if xs else None
        ergebnis["zeitraeume"][name] = {
            "seit": a["datum"],
            "nach_punkten": {g: {"anzahl": len(v), "mittel_pct": mittel(v)} for g, v in sorted(grp.items())},
            "top_bedingungen": {k: {"anzahl": len(v), "mittel_pct": mittel(v)} for k, v in top.items()},
            "alle": {"anzahl": sum(len(v) for v in grp.values()), "mittel_pct": mittel([x for v in grp.values() for x in v])},
        }
    json.dump(ergebnis, open("data/trefferquote.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(ergebnis, ensure_ascii=False)[:600])


if __name__ == "__main__":
    main()
