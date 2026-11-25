"""Vorhersagekraft der Bewertung (Auftrag A10 Teil 3, 18.11.2026): Sagen Punkte/Feinwert von heute die Kursänderung
der nächsten 1 bzw. 5 Handelstage voraus?

Information Coefficient (IC) = Spearman-Rangkorrelation zwischen Faktor am Tag t und Rendite t → t+1 bzw. t+5
Handelstage, je Tag ein IC; dazu Mittelwert, Anzahl Tage, Anteil Tage mit IC > 0, und mittlere Rendite je Fünftel.

Bewusst ohne alphalens/pandas/scipy, nur Standardbibliothek: schnappschuss.yml installiert keine Pakete
(schnappschuss.py und bewertung.py laufen nur mit der Standardbibliothek), und eine neue schwere Abhängigkeit
soll den täglichen Lauf nicht gefährden. Lokal mit alphalens-reloaded 0.5.1 / scipy gegengeprüft.

Wird von schnappschuss.trefferquote() aufgerufen (Schlüssel "vorhersagekraft" in data/trefferquote.json).
Allein: python vorhersagekraft.py   (gibt nur aus, schreibt nichts)

Regeln:
- Handelstag eines Schnappschusses = "datum"; fällt es aufs Wochenende, der Freitag davor (2026-11-15.json vom
  Sonntag enthält die Freitagskurse vom 13.11., nur mit anderem Euro-Kurs → kein eigener Handelstag).
- Teil nach dem Schnappschuss am Tag t: "rueckwirkend" (Dateien mit "rueckwirkend": true, bis 13.11.) oder "echt".
  Der Endkurs (t+h) kommt aus dem Schnappschuss h Handelstage später, egal aus welchem Teil (Kurs ist Kurs).
- Handelstage = vorhandene Schnappschüsse in Reihenfolge (fehlt ein Tag, zählt der nächste vorhandene).
- Rendite aus kurs_eur, d. h. inkl. Wechselkursänderung; Ausreißer (> +150 % / < −75 %) fallen weg wie in
  schnappschuss.trefferquote().
"""
import datetime as dt, glob, json, os

ORDNER = "data/verlauf"
FAKTOREN = ("punkte", "feinwert", "piotroski", "revision_90t_pct")
# piotroski und revision_90t_pct (Schätzungs-Trend 90 Tage) stehen erst ab dem Schnappschuss vom 25.11.2026 im Verlauf;
# solange es für sie keinen einzigen Tag gibt, erscheinen sie nicht (keine leeren Zeilen im Dashboard).
NUR_MIT_DATEN = ("piotroski", "revision_90t_pct")
HORIZONTE = (1, 5)
AUSREISSER_HOCH, AUSREISSER_TIEF = 1.5, -0.75  # wie schnappschuss.py
MIN_AKTIEN = 30   # weniger Aktien an einem Tag: kein IC für diesen Tag
MIN_TAGE = 3      # weniger Tage: "zu wenige Tage" statt Mittelwert
HINWEIS = ("Erst 2–3 Wochen Daten: das sagt fast nichts, Zufall überwiegt. IC nahe 0 = kein Zusammenhang, "
           "über 0,05 wäre gut (Rangkorrelation Faktor heute ↔ Rendite danach). Rendite in Euro inkl. Wechselkurs; "
           "„rueckwirkend“ = heutige Regeln auf alte Daten, kein echter Test.")


def handelstag(datum):
    d = dt.date.fromisoformat(datum)
    return d - dt.timedelta(days=max(0, d.weekday() - 4))


def raenge(xs):
    """Ränge 1..n, bei Gleichstand Durchschnittsrang (wie scipy.stats.rankdata)."""
    o = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and xs[o[j + 1]] == xs[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(xs, ys):
    rx, ry = raenge(xs), raenge(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    return sxy / (sxx * syy) ** 0.5 if sxx and syy else None


def fuenftel(xs):
    """Fünftel 1 (niedrigster Faktor) bis 5; Gleichstände nach Reihenfolge aufgeteilt (wie pandas.qcut auf rank(first))."""
    o = sorted(range(len(xs)), key=lambda i: xs[i])
    q = [0] * len(xs)
    for pos, i in enumerate(o):
        q[i] = pos * 5 // len(xs) + 1
    return q


def tage_laden(ordner=ORDNER):
    """[(Handelstag, Teil, {Kürzel: [Werte]}, felder)], nach Handelstag sortiert; pro Handelstag und Teil eine Datei."""
    je = {}
    for f in sorted(glob.glob(f"{ordner}/????-??-??.json")):
        s = json.load(open(f))
        teil = "rueckwirkend" if s.get("rueckwirkend") else "echt"
        je[(handelstag(s.get("datum") or os.path.basename(f)[:10]), teil)] = (s["aktien"], s["felder"])
    return sorted((t, teil, a, fe) for (t, teil), (a, fe) in je.items())


def berechnen(ordner=ORDNER):
    tage = tage_laden(ordner)
    folge = sorted({t for t, *_ in tage})  # Handelstage
    kurse = {}  # Handelstag → {Kürzel: kurs_eur}; echte Schnappschüsse haben Vorrang
    for t, teil, a, fe in sorted(tage, key=lambda x: x[1] == "echt"):
        ik = fe.index("kurs_eur")
        kurse.setdefault(t, {}).update({k: v[ik] for k, v in a.items() if v[ik]})
    erg = {"hinweis": HINWEIS, "handelstage": [t.isoformat() for t in folge],
           "regeln": dict(min_aktien_je_tag=MIN_AKTIEN, min_tage=MIN_TAGE, ausreisser_pct=[-75, 150],
                          faktoren=list(FAKTOREN),
                          hinweis_faktoren="piotroski und revision_90t_pct (Schätzungs-Trend) erst ab 25.11.2026 im Verlauf; "
                                           "Piotroski teils aus weniger als 9 Prüfpunkten"),
           "teile": {}, "zeilen": [], "fuenftel_zeilen": []}
    sammel = {}  # (teil, faktor, h) → {"ic": [(tag, ic, n)], "q": {1..5: [Tagesmittel]}}
    for t, teil, a, fe in tage:
        i = folge.index(t)
        for h in HORIZONTE:
            if i + h >= len(folge):
                continue
            ende = kurse[folge[i + h]]
            ik = fe.index("kurs_eur")
            for fak in FAKTOREN:
                if fak not in fe:
                    continue
                ifk = fe.index(fak)
                xs, ys = [], []
                for k, v in a.items():
                    k0, k1, x = v[ik], ende.get(k), v[ifk]
                    if not k0 or not k1 or x is None:
                        continue
                    r = k1 / k0 - 1
                    if r > AUSREISSER_HOCH or r < AUSREISSER_TIEF:
                        continue
                    xs.append(x); ys.append(r)
                if len(xs) < MIN_AKTIEN:
                    continue
                ic = spearman(xs, ys)
                if ic is None:
                    continue
                s = sammel.setdefault((teil, fak, h), {"ic": [], "q": {q: [] for q in range(1, 6)}})
                s["ic"].append((t.isoformat(), ic, len(xs)))
                qs = fuenftel(xs)
                for q in range(1, 6):
                    v = [y for y, qq in zip(ys, qs) if qq == q]
                    s["q"][q].append(sum(v) / len(v))
    for teil in ("rueckwirkend", "echt"):
        for fak in FAKTOREN:
            for h in HORIZONTE:
                s = sammel.get((teil, fak, h), {"ic": [], "q": {}})
                if fak in NUR_MIT_DATEN and not s["ic"]:
                    continue
                ics = [x[1] for x in s["ic"]]
                genug = len(ics) >= MIN_TAGE
                eintrag = {
                    "tage": len(ics),
                    "ic_mittel": round(sum(ics) / len(ics), 3) if genug else "zu wenige Tage",
                    "anteil_positiv": round(sum(x > 0 for x in ics) / len(ics), 2) if genug else None,
                    "ic_je_tag": [dict(tag=d, ic=round(ic, 3), aktien=n) for d, ic, n in s["ic"]],
                    "fuenftel_rendite_pct": ({str(q): round(sum(v) / len(v) * 100, 2) for q, v in s["q"].items()}
                                             if genug else "zu wenige Tage"),
                }
                erg["teile"].setdefault(teil, {}).setdefault(fak, {})[f"{h} Tag" if h == 1 else f"{h} Tage"] = eintrag
                erg["zeilen"].append(dict(teil=teil, faktor=fak, tage_vorne=h, ic_mittel=eintrag["ic_mittel"],
                                          tage=len(ics), anteil_positiv=eintrag["anteil_positiv"]))
                if genug:
                    erg["fuenftel_zeilen"].append(dict(teil=teil, faktor=fak, tage_vorne=h,
                                                       **{f"q{q}_pct": v for q, v in eintrag["fuenftel_rendite_pct"].items()}))
    return erg


if __name__ == "__main__":
    e = berechnen()
    print(json.dumps({k: e[k] for k in ("handelstage", "zeilen", "fuenftel_zeilen")}, ensure_ascii=False, indent=1))
