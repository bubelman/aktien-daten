"""Neue Aktien automatisch finden – ohne KI, also ohne Tokens (Levin, 16.11.2026: „mehr Aktien und weniger verbrauchen“).
Läuft per GitHub Actions (universum.yml, sonntags). Fragt den Aktien-Filter von Yahoo nach allen Firmen je Börse,
sortiert nach Börsenwert, und nimmt neue mit Börsenwert über GRENZE_EUR auf.

  python screener.py --trocken   nur Bericht data/screener.json, tickers.txt bleibt
  python screener.py             gültige neue Kürzel an tickers.txt anhängen
"""
import datetime as dt, json, os, re, sys, time
import yfinance as yf
from yfinance import EquityQuery as Q

GRENZE_EUR = 1e9
# Region (Yahoo), Haupt-Börsen (Yahoo-Code), Endung des Kürzels
BOERSEN = [
    ("us", ["NMS", "NYQ", "NGM", "NCM"], ""), ("de", ["GER"], ".DE"), ("gb", ["LSE"], ".L"),
    ("fr", ["PAR"], ".PA"), ("nl", ["AMS"], ".AS"), ("es", ["MCE"], ".MC"), ("it", ["MIL"], ".MI"),
    ("ch", ["EBS"], ".SW"), ("se", ["STO"], ".ST"), ("dk", ["CPH"], ".CO"), ("no", ["OSL"], ".OL"),
    ("fi", ["HEL"], ".HE"), ("be", ["BRU"], ".BR"), ("at", ["VIE"], ".VI"), ("jp", ["JPX"], ".T"),
    ("ca", ["TOR"], ".TO"), ("au", ["ASX"], ".AX"), ("hk", ["HKG"], ".HK"),
]


def fx_tabelle():
    try:
        fx = json.load(open("data/aktien.json")).get("fx_eur") or {}
    except Exception:
        fx = {}
    fx = {k: float(v) for k, v in fx.items() if v}
    fx["EUR"] = 1.0
    if "GBP" in fx:
        fx["GBp"] = fx["GBP"] * 100  # Pence
    return fx


def firma(n):
    """Wie in bewertung.py: Firmenname vereinfachen, damit Zweitlistings (z. B. Apple in Frankfurt) auffallen."""
    n = re.sub(r"[^a-z0-9 ]", " ", (n or "").lower())
    n = re.sub(r"\b(the|plc|ag|se|sa|nv|n v|inc|corp|corporation|ltd|limited|holding|holdings|group|asa|ab|a s|s a|s p a|spa)\b", " ", n)
    return " ".join(n.split())


def abfragen(region, boersen):
    q = Q("and", [Q("eq", ["region", region]), Q("is-in", ["exchange", *boersen])])
    alle, offset = [], 0
    while offset < 3000:
        for versuch in range(3):
            try:
                r = yf.screen(q, sortField="intradaymarketcap", sortAsc=False, size=250, offset=offset)
                break
            except Exception as e:
                print(region, "Fehler:", e); r = None; time.sleep(10)
        quotes = (r or {}).get("quotes") or []
        alle += quotes
        if len(quotes) < 250:
            break
        offset += 250
        time.sleep(2)
    return alle


def main():
    trocken = "--trocken" in sys.argv
    fx = fx_tabelle()
    alt = open("tickers.txt").read().split()
    vorhanden = set(alt)
    if os.path.exists("tickers_gesperrt.txt"):
        vorhanden |= {z.split()[0] for z in open("tickers_gesperrt.txt", encoding="utf-8") if z.strip() and not z.startswith("#")}
    bericht = {"stand": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "grenze_eur": GRENZE_EUR,
               "boersen": {}, "neu": []}
    try:
        bekannt = {firma(x.get("name_lang") or x.get("name")) for x in json.load(open("data/aktien.json"))["aktien"]}
    except Exception:
        bekannt = set()
    bekannt.discard("")
    kandidaten = {}  # Firma -> (Handelswert in EUR pro Tag, Kürzel, Name, Börsenwert Mrd. €, Region)
    for region, boersen, endung in BOERSEN:
        quotes = abfragen(region, boersen)
        gross, ohne_fx = 0, 0
        for z in quotes:
            s, mc, cur = z.get("symbol"), z.get("marketCap"), z.get("currency")
            if not s or not mc or z.get("quoteType") not in (None, "EQUITY"):
                continue
            if (endung and not s.endswith(endung)) or (not endung and "." in s) or (endung == ".L" and s[0].isdigit()):
                continue
            if cur not in fx:
                ohne_fx += 1; continue
            eur = mc / fx[cur]
            if eur < GRENZE_EUR:
                continue
            gross += 1
            name = z.get("longName") or z.get("shortName") or ""
            f = firma(name)
            if not f or f in bekannt or s in vorhanden:
                continue
            wert = (z.get("averageDailyVolume3Month") or 0) * (z.get("regularMarketPrice") or 0) / fx[cur]
            if f not in kandidaten or wert > kandidaten[f][0]:
                kandidaten[f] = (wert, s, name, round(eur / 1e9, 1), region)
        bericht["boersen"][region] = {"gefunden": len(quotes), "ueber_grenze": gross, "ohne_wechselkurs": ohne_fx}
        print(region, len(quotes), "gefunden,", gross, "über Grenze")
    neu = [k[1] for k in sorted(kandidaten.values(), key=lambda k: -k[3])]
    for f, (w, s, name, mrd, region) in kandidaten.items():
        bericht["boersen"][region].setdefault("neu", 0)
        bericht["boersen"][region]["neu"] += 1
    bericht["beispiele"] = [[k[1], k[2], k[3]] for k in sorted(kandidaten.values(), key=lambda k: -k[3])[:60]]
    bericht["neu"] = neu
    bericht["vorher"], bericht["nachher"] = len(alt), len(alt) + len(neu)
    if not trocken and neu:
        open("tickers.txt", "w").write("\n".join(alt + neu) + "\n")
    json.dump(bericht, open("data/screener.json", "w"), ensure_ascii=False, indent=1)
    print(len(neu), "neue Kürzel", "(trocken)" if trocken else "")


if __name__ == "__main__":
    main()
