"""Füllt data/verlauf rückwirkend aus der Git-Geschichte von data/aktien.json (Auftrag A3.1, 15.11.2026).

Für jeden Börsentag (Mo–Fr) vor --bis die LETZTE Version von data/aktien.json dieses Tages (Commit-Zeit in UTC)
holen, mit den heutigen Regeln (bewertung.py) bewerten und als data/verlauf/<Datum>.json mit "rueckwirkend": true
speichern. Danach data/trefferquote.json und data/trefferquote_zeilen.json neu rechnen (Schlusskurse aus dem
jüngsten vorhandenen Schnappschuss, der dabei nicht verändert wird).

Ehrlich: Das ist ein Rückblick mit heutigen Regeln, kein echter Test aus der Vergangenheit.
- Nachrichten: nur die data/news.json, die im selben Commit lag (bewertung.py zählt nur Einträge, die höchstens
  7 Tage alt und nicht aus der Zukunft sind); gab es keine, dann keine Nachrichten. hype.json: leer (gibt keine Punkte).
- Wechselkurse: die aus der jeweiligen Datei (eurusd, fx_eur). Fehlt fx_eur (vor dem 13.11.), fallen Aktien in
  Pfund, Franken, Kronen usw. weg (bewertung.py: „kein Wechselkurs“).
- Fehlende Felder → bewertung.py lässt die Aktie weg; stürzt bewertung.py bei einem alten Format ab, wird der Tag
  übersprungen.
Bestehende Schnappschüsse ohne "rueckwirkend" werden nie überschrieben.

  git fetch --unshallow origin   (falls flach geklont)
  python rueckwirkend.py [--bis 2026-11-15] [--ref origin/main]
"""
import argparse, datetime as dt, glob, json, os, subprocess, sys, tempfile

import schnappschuss as S


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def letzte_je_tag(ref, bis):
    """{Datum: Commit} – letzte Version von data/aktien.json je Börsentag vor bis (Commit-Zeit in UTC)."""
    tage = {}
    for zeile in git("log", "--format=%H %cI", ref, "--", "data/aktien.json").splitlines():
        c, zeit = zeile.split()
        z = dt.datetime.fromisoformat(zeit).astimezone(dt.timezone.utc)
        d = z.date()
        if d >= bis or d.weekday() >= 5:
            continue
        if d not in tage or z > tage[d][1]:
            tage[d] = (c, z)
    return dict(sorted(tage.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bis", default="2026-11-15", help="nur Tage davor (erster echter Schnappschuss)")
    ap.add_argument("--ref", default="origin/main")
    a = ap.parse_args()
    if git("rev-parse", "--is-shallow-repository").strip() == "true":
        sys.exit("Repo ist flach geklont: erst git fetch --unshallow origin")
    os.makedirs(S.ORDNER, exist_ok=True)
    for d, (c, zeit) in letzte_je_tag(a.ref, dt.date.fromisoformat(a.bis)).items():
        ziel = f"{S.ORDNER}/{d.isoformat()}.json"
        if os.path.exists(ziel) and not json.load(open(ziel)).get("rueckwirkend"):
            print(d, "echter Schnappschuss vorhanden – bleibt"); continue
        tmp = tempfile.mkdtemp()
        yahoo = os.path.join(tmp, "aktien.json")
        try:
            Y = json.loads(git("show", f"{c}:data/aktien.json"))
            if not Y.get("aktien"):
                print(d, c[:7], "keine Aktien in der Datei – übersprungen"); continue
            json.dump(Y, open(yahoo, "w"))
            try:  # Nachrichten so, wie sie damals im Repo lagen
                news = json.loads(git("show", f"{c}:data/news.json"))
            except subprocess.CalledProcessError:
                news = {"aktien": {}}
            json.dump(news, open(os.path.join(tmp, "news.json"), "w"))
            json.dump({"aktien": {}}, open(os.path.join(tmp, "hype.json"), "w"))  # sonst holt bewertung.py die heutige
            alle = S.bewerten(yahoo, jetzt=zeit.isoformat(timespec="seconds"), news=os.path.join(tmp, "news.json"))
        except (subprocess.CalledProcessError, ValueError, OSError) as e:
            print(d, c[:7], "bewertung.py fehlgeschlagen – übersprungen:", str(e)[:120]); continue
        s = S.schnappschuss(alle, d.isoformat(), rueckwirkend=True, commit=c[:12], daten_stand=Y.get("stand"))
        json.dump(s, open(ziel, "w"), separators=(",", ":"))
        print(d, c[:7], zeit.isoformat(timespec="minutes"), f"{len(Y['aktien'])} Aktien in der Datei, {len(alle)} bewertet",
              f"Nachrichten: {len(news.get('aktien') or {})}")
    dateien = sorted(glob.glob(f"{S.ORDNER}/????-??-??.json"))
    ende = json.load(open(dateien[-1]))
    e = S.trefferquote(ende)
    print(json.dumps(e, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
