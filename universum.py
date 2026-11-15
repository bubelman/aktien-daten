"""Erweitert tickers.txt um die Mitglieder großer Aktien-Indizes (Listen von Wikipedia).
Läuft per GitHub Actions (universum.yml), weil die Rechner dort freies Internet haben.

  python universum.py          Indizes lesen, Kürzel in Yahoo-Schreibweise umwandeln, neue Kürzel mit
                               Yahoo prüfen (gibt es einen Kurs?) und gültige an tickers.txt anhängen.
Bestehende Kürzel bleiben immer drin. Bericht: data/universum.json (je Index: gefunden, neu, ungültig).
"""
import io, json, os, re, sys, time, datetime as dt
import pandas as pd
import requests
import yfinance as yf

# (Name, Wikipedia-Seite, Yahoo-Endung; "" = USA)
INDIZES = [
    ("S&P 500", "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", ""),
    ("S&P MidCap 400", "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies", ""),
    ("Nasdaq-100", "https://en.wikipedia.org/wiki/Nasdaq-100", ""),
    ("DAX", "https://en.wikipedia.org/wiki/DAX", ".DE"),
    ("MDAX", "https://en.wikipedia.org/wiki/MDAX", ".DE"),
    ("SDAX", "https://en.wikipedia.org/wiki/SDAX", ".DE"),
    ("TecDAX", "https://en.wikipedia.org/wiki/TecDAX", ".DE"),
    ("FTSE 100", "https://en.wikipedia.org/wiki/FTSE_100_Index", ".L"),
    ("FTSE 250", "https://en.wikipedia.org/wiki/FTSE_250_Index", ".L"),
    ("CAC 40", "https://en.wikipedia.org/wiki/CAC_40", ".PA"),
    ("SBF 120", "https://en.wikipedia.org/wiki/SBF_120", ".PA"),
    ("AEX", "https://en.wikipedia.org/wiki/AEX_index", ".AS"),
    ("AMX", "https://en.wikipedia.org/wiki/AMX_index", ".AS"),
    ("IBEX 35", "https://en.wikipedia.org/wiki/IBEX_35", ".MC"),
    ("FTSE MIB", "https://en.wikipedia.org/wiki/FTSE_MIB", ".MI"),
    ("SMI", "https://en.wikipedia.org/wiki/Swiss_Market_Index", ".SW"),
    ("SMI MID", "https://en.wikipedia.org/wiki/SMI_MID", ".SW"),
    ("OMX Stockholm 30", "https://en.wikipedia.org/wiki/OMX_Stockholm_30", ".ST"),
    ("OMX Copenhagen 25", "https://en.wikipedia.org/wiki/OMX_Copenhagen_25", ".CO"),
    ("OBX", "https://en.wikipedia.org/wiki/OBX_Index", ".OL"),
    ("BEL 20", "https://en.wikipedia.org/wiki/BEL_20", ".BR"),
    ("OMX Helsinki 25", "https://en.wikipedia.org/wiki/OMX_Helsinki_25", ".HE"),
    # 15.11.2026 (Levin: „mehr neu hinzufügen“): kleinere US-Firmen und weitere Länder
    ("S&P SmallCap 600", "https://en.wikipedia.org/wiki/List_of_S%26P_600_companies", ""),
    ("S&P/TSX 60", "https://en.wikipedia.org/wiki/S%26P/TSX_60", ".TO"),
    ("Nikkei 225", "https://en.wikipedia.org/wiki/Nikkei_225", ".T"),
    ("S&P/ASX 50", "https://en.wikipedia.org/wiki/S%26P/ASX_50", ".AX"),
    ("Hang Seng", "https://en.wikipedia.org/wiki/Hang_Seng_Index", ".HK"),
]
ENDUNGEN = {".DE", ".L", ".PA", ".AS", ".MC", ".MI", ".SW", ".ST", ".CO", ".OL", ".BR", ".HE", ".VI", ".LS", ".IR", ".F",
            ".TO", ".AX", ".HK", ".T"}
SPALTE = re.compile(r"ticker|symbol|epic|^code$|kürzel", re.I)
GUELTIG = re.compile(r"^[A-Z0-9][A-Z0-9\-&]{0,11}(\.[A-Z]{1,2})?$")
UA = {"User-Agent": "aktien-daten/1.0 (https://github.com/bubelman/aktien-daten; Bildungsprojekt)"}


def yahoo(v, endung):
    v = re.sub(r"\[.*?\]", "", str(v)).strip().upper()
    if not v or v in ("NAN", "—", "-"):
        return None
    if ":" in v:  # z. B. "EPA: AI" oder "XETRA:SAP"
        v = v.split(":")[-1].strip()
    v = v.split()[0] if endung == "" else v
    if re.fullmatch(r"\d+\.0", v):  # Zahlen-Kürzel, die pandas als Kommazahl gelesen hat (Japan, Hongkong)
        v = v[:-2]
    if endung == ".HK" and v.isdigit():
        v = v.zfill(4)  # Yahoo schreibt Hongkong vierstellig: 0700.HK
    if endung in (".T", ".HK") and not re.fullmatch(r"[0-9][0-9A-Z]{3}", v):
        return None  # dort sind nur Zahlen-Codes gültig (z. B. 7203, 130A)
    m = re.match(r"^(.*?)(\.[A-Z]{1,2})$", v)
    if m and m.group(2) in ENDUNGEN:
        basis, eigene = m.group(1), m.group(2)
        return (basis.replace(".", "-").replace(" ", "-") + eigene) if GUELTIG.match(basis.replace(".", "-").replace(" ", "-") + eigene) else None
    v = v.rstrip(".")
    v = v.replace(".", "-").replace(" ", "-").replace("/", "-")
    v = v + endung
    return v if GUELTIG.match(v) else None


def lies(url, endung):
    html = requests.get(url, headers=UA, timeout=30).text
    tabellen = pd.read_html(io.StringIO(html))
    beste, info = [], []
    for t in tabellen:
        if isinstance(t.columns, pd.MultiIndex):
            t.columns = [" ".join(str(x) for x in c if "Unnamed" not in str(x)) for c in t.columns]
        spalten = [c for c in t.columns if SPALTE.search(str(c))]
        info.append([str(c) for c in t.columns][:8])
        for c in spalten:
            werte = [yahoo(v, endung) for v in t[c].tolist()]
            werte = [w for w in werte if w]
            if len(werte) > len(beste):
                beste = werte
    return list(dict.fromkeys(beste)), info


def hat_kurs(syms):
    ok = set()
    for i in range(0, len(syms), 150):
        teil = syms[i:i + 150]
        for versuch in range(3):
            try:
                df = yf.download(teil, period="10d", interval="1d", group_by="ticker", threads=True, progress=False,
                                 auto_adjust=True)
                break
            except Exception as e:
                print("Prüfabruf fehlgeschlagen:", e); df = None; time.sleep(20)
        if df is None:
            continue
        for s in teil:
            try:
                h = (df[s]["Close"] if len(teil) > 1 else df["Close"]).dropna()
                if len(h):
                    ok.add(s)
            except Exception:
                pass
        time.sleep(3)
    return ok


def main():
    alt = open("tickers.txt").read().split()
    alt_set = set(alt)
    # gesperrte Kürzel (übernommen, ETF, falsche Börse …) nicht wieder aufnehmen
    if os.path.exists("tickers_gesperrt.txt"):
        alt_set |= {z.split()[0] for z in open("tickers_gesperrt.txt", encoding="utf-8")
                    if z.strip() and not z.startswith("#")}
    bericht, kandidaten = {"stand": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "indizes": {}}, []
    for name, url, endung in INDIZES:
        try:
            syms, info = lies(url, endung)
        except Exception as e:
            bericht["indizes"][name] = {"fehler": str(e)[:200]}
            print(name, "Fehler:", e)
            continue
        neu = [s for s in syms if s not in alt_set and s not in kandidaten]
        kandidaten += neu
        bericht["indizes"][name] = {"gefunden": len(syms), "neu": len(neu), "beispiele": syms[:5],
                                    **({"tabellen": info[:10]} if len(syms) < 10 else {})}
        print(f"{name}: {len(syms)} gefunden, {len(neu)} neu")
        time.sleep(1)
    ok = hat_kurs(kandidaten) if kandidaten else set()
    gut = [s for s in kandidaten if s in ok]
    bericht["neu_gueltig"] = len(gut)
    bericht["ungueltig"] = [s for s in kandidaten if s not in ok]
    bericht["vorher"], bericht["nachher"] = len(alt), len(alt) + len(gut)
    if "--trocken" not in sys.argv and gut:
        open("tickers.txt", "w").write("\n".join(alt + gut) + "\n")
    json.dump(bericht, open("data/universum.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(gut)} neue Kürzel gültig, {len(bericht['ungueltig'])} ohne Kurs; jetzt {bericht['nachher']} Aktien")


if __name__ == "__main__":
    main()
