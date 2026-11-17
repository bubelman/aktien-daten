"""Bewertung der Aktien-Liste und Musterdepot – feste Regeln, damit jeder Lauf gleich rechnet.

Aufruf:
  python3 bewertung.py --yahoo aktien.json --alt ALT_ORDNER --neu NEU_ORDNER --jetzt 2026-10-30T21:33:00+01:00

Faire Spanne aus drei Wegen: Gewinn × faires KGV, Cashflow-Rechnung (DCF) und Kursziel der Analysten;
faire Mitte = mittlerer der drei Werte, Spanne von halbem Weg zum unteren bis halbem Weg zum oberen Wert. Reihenfolge: erst Punkte (max. 10), bei Gleichstand der Feinwert (0–100, Rang jeder Kennzahl unter allen
bewerteten Aktien). Bewertet werden Dollar- und Euro-Aktien.

ALT_ORDNER enthält die aktuellen Dateien des Dashboards:
  liste.json, aenderungen.json, depot.json, depot_trades.json, depot_verlauf.json, depot50.json (fehlt sie: Start mit 10.000 €)
NEU_ORDNER bekommt die neuen Dateien + bericht.json (Zusammenfassung, wichtige Ereignisse, Prüfergebnis).

Optional: --meine meine_aktien.txt (Levins eigene Aktien, ein Kürzel pro Zeile) schreibt meine.json mit
denselben Regeln; --ohne-depots rechnet und schreibt die (gestoppten) Musterdepots nicht.
--kurse kurse.json  ({"TICKER": kurs_in_usd, ..., "EURUSD": 1.116}) überschreibt Kurse,
wenn die Yahoo-Datei älter ist. --keine-trades verbietet Depot-Käufe/-Verkäufe (z. B. bei Datenzweifeln).

Nur Spielgeld-Simulation, keine Anlageberatung.
"""
import argparse, datetime as dt, json, math, os, re, sys

START_GELD = 10000.0
GEBUEHR = 1.0
ANZAHL = 50
TOP_MAX = 5
BEOBACHTEN_MAX = 10
PRO_BRANCHE = 2
ZYKLIKER = {"MU", "SNDK", "WDC", "STX", "SKHY"}
SPY_STUECK = 14.7752  # Vergleichsdepot, gekauft am 30.10.2026 zu 755,25 $ bei 1 € = 1,11601 $
SPY_START = round(SPY_STUECK * 755.25 / 1.11601, 2)  # tatsächlicher Startwert (9.998,99 €, Stück gerundet)
NAMEN = {'MC.PA': 'LVMH', 'ITX.MC': 'Inditex', 'BMW.DE': 'BMW', 'BBVA.MC': 'BBVA', 'SAN.MC': 'Banco Santander', 'BNP.PA': 'BNP Paribas', 'OR.PA': "L'Oréal", 'RMS.PA': 'Hermès', 'DG.PA': 'Vinci', 'SU.PA': 'Schneider Electric', 'AI.PA': 'Air Liquide', 'EL.PA': 'EssilorLuxottica', 'CS.PA': 'AXA', 'RI.PA': 'Pernod Ricard', 'BN.PA': 'Danone', 'SAF.PA': 'Safran', 'SGO.PA': 'Saint-Gobain', 'ACA.PA': 'Crédit Agricole', 'HO.PA': 'Thales', 'AM.PA': 'Dassault Aviation', 'DSY.PA': 'Dassault Systèmes', 'STMPA.PA': 'STMicroelectronics', 'IBE.MC': 'Iberdrola', 'MUV2.DE': 'Munich Re', 'DB1.DE': 'Deutsche Börse', 'DTE.DE': 'Deutsche Telekom', 'DBK.DE': 'Deutsche Bank', 'HNR1.DE': 'Hannover Rück', 'SRT3.DE': 'Sartorius', 'FME.DE': 'Fresenius Medical Care', 'SHL.DE': 'Siemens Healthineers', 'ENR.DE': 'Siemens Energy', 'P911.DE': 'Porsche', 'VOW3.DE': 'Volkswagen', 'G1A.DE': 'GEA', 'MTX.DE': 'MTU Aero Engines', 'HEI.DE': 'Heidelberg Materials', 'AD.AS': 'Ahold Delhaize', 'PRX.AS': 'Prosus', 'INGA.AS': 'ING', 'WKL.AS': 'Wolters Kluwer', 'ASM.AS': 'ASM International', 'BESI.AS': 'BE Semiconductor', 'KNEBV.HE': 'Kone', 'ENEL.MI': 'Enel', 'ISP.MI': 'Intesa Sanpaolo', 'ENI.MI': 'Eni', 'TTE.PA': 'TotalEnergies', 'ORA.PA': 'Orange', 'VIE.PA': 'Veolia', 'ENGI.PA': 'Engie', 'KER.PA': 'Kering', 'CAP.PA': 'Capgemini', 'AIR.PA': 'Airbus', 'ADS.DE': 'Adidas', 'BAS.DE': 'BASF', 'BAYN.DE': 'Bayer', 'BEI.DE': 'Beiersdorf', 'BNR.DE': 'Brenntag', 'CBK.DE': 'Commerzbank', 'CON.DE': 'Continental', 'DTG.DE': 'Daimler Truck', 'DHL.DE': 'DHL Group', 'EOAN.DE': 'E.ON', 'FRE.DE': 'Fresenius', 'HEN3.DE': 'Henkel', 'IFX.DE': 'Infineon', 'MBG.DE': 'Mercedes-Benz', 'MRK.DE': 'Merck KGaA', 'QIA.DE': 'Qiagen', 'RHM.DE': 'Rheinmetall', 'RWE.DE': 'RWE', 'SIE.DE': 'Siemens', 'SY1.DE': 'Symrise', 'VNA.DE': 'Vonovia', 'ZAL.DE': 'Zalando', 'HAG.DE': 'Hensoldt', 'ALV.DE': 'Allianz', 'UCG.MI': 'UniCredit', 'STLAM.MI': 'Stellantis', 'ADYEN.AS': 'Adyen', 'HEIA.AS': 'Heineken', 'NOKIA.HE': 'Nokia', 'UCB.BR': 'UCB', 'BRK-B': 'Berkshire Hathaway', 'PBR': 'Petrobras', 'LLY': 'Eli Lilly', 'TRV': 'Travelers', 'FWONK': 'Liberty Formula One', 'SLR.MC': 'Solaria', 'STMN.SW': 'Straumann', 'G24.DE': 'Scout24', 'CCH.L': 'Coca-Cola HBC', 'NSIS-B.CO': 'Novonesis', 'ENT.L': 'Entain', 'LONN.SW': 'Lonza', 'TKA.DE': 'Thyssenkrupp', 'MRL.MC': 'Merlin Properties', 'TPRO.MI': 'Technoprobe', 'NG.L': 'National Grid', 'ICG.L': 'ICG', 'SYENS.BR': 'Syensqo', 'ADP.PA': 'Groupe ADP', 'IMCD.AS': 'IMCD', 'SPIE.PA': 'SPIE', 'DT': 'Dynatrace', 'LPLA': 'LPL Financial', 'TRU': 'TransUnion', 'BF-B': 'Brown-Forman', 'GOOGL': 'Alphabet'}  # feste Kurznamen, vor allem für Euro-Aktien

BRANCHEN = [  # (Suchwort in Yahoo-Industry/Sector, deutsche Branche)
    ("Semiconductor", "Halbleiter & Speicher"), ("Computer Hardware", "Hardware & Netzwerk"),
    ("Communication Equipment", "Hardware & Netzwerk"), ("Electronic Components", "Hardware & Netzwerk"),
    ("Software", "Software"), ("Information Technology", "Software"),
    ("Internet Retail", "Handel & Reisen"), ("Solar", "Energie"), ("Scientific & Technical", "Hardware & Netzwerk"),
    ("Consumer Electronics", "Hardware & Netzwerk"), ("Aerospace", "Luftfahrt & Rüstung"),
    ("Internet", "Internet & Medien"), ("Entertainment", "Internet & Medien"), ("Media", "Internet & Medien"),
    ("Telecom", "Telekom"), ("Gold", "Gold"), ("Silver", "Gold"), ("Copper", "Rohstoffe"), ("Steel", "Rohstoffe"),
    ("Oil", "Energie"), ("Gas", "Energie"), ("Uranium", "Energie"),
    ("Utilities", "Versorger"), ("REIT", "Immobilien"), ("Real Estate", "Immobilien"),
    ("Bank", "Finanzen"), ("Insurance", "Finanzen"), ("Capital Markets", "Finanzen"), ("Credit", "Finanzen"),
    ("Drug", "Gesundheit"), ("Biotech", "Gesundheit"), ("Medical", "Gesundheit"), ("Health", "Gesundheit"),
    ("Diagnostics", "Gesundheit"),
    ("Retail", "Handel & Reisen"), ("Travel", "Handel & Reisen"), ("Lodging", "Handel & Reisen"),
    ("Restaurants", "Handel & Reisen"), ("Resorts", "Handel & Reisen"), ("Auto", "Handel & Reisen"),
    ("Home Improvement", "Handel & Reisen"), ("Discount", "Handel & Reisen"), ("Internet Retail", "Handel & Reisen"),
    ("Beverages", "Konsumgüter"), ("Tobacco", "Konsumgüter"), ("Household", "Konsumgüter"),
    ("Packaged Foods", "Konsumgüter"), ("Confectioners", "Konsumgüter"), ("Personal", "Konsumgüter"),
    ("Chemicals", "Rohstoffe"), ("Building Materials", "Rohstoffe"),
]
SEKTOR_FALLBACK = {"Technology": "Software", "Communication Services": "Internet & Medien",
                   "Consumer Cyclical": "Handel & Reisen", "Consumer Defensive": "Konsumgüter",
                   "Healthcare": "Gesundheit", "Industrials": "Industrie & Energie", "Energy": "Energie",
                   "Basic Materials": "Rohstoffe", "Utilities": "Versorger", "Real Estate": "Immobilien",
                   "Financial Services": "Finanzen"}


def branche(r):
    ind = (r.get("branche") or "") + " " + (r.get("sektor") or "")
    for key, name in BRANCHEN:
        if key.lower() in ind.lower():
            return name
    return SEKTOR_FALLBACK.get(r.get("sektor"), "Sonstige")


def de(x, nd=1):
    """Zahl im deutschen Format, z. B. 1.234,5"""
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def rf(x):
    """Faire Werte: unter 10 € auf 0,01 €, unter 100 € auf 0,1 € genau, sonst ganze Euro."""
    return round(x, 2) if x < 10 else round(x, 1) if x < 100 else round(x)


def name_wahl(kurz, lang):
    """Yahoo-Kurznamen aus London/Skandinavien sind oft abgeschnitten und in GROSSBUCHSTABEN
    („FORESIGHT GROUP HOLDINGS LIMITE“): dann lieber den langen Namen nehmen bzw. normal schreiben."""
    def laut(x):
        b = [c for c in (x or "") if c.isalpha()]
        return len(b) >= 4 and sum(c.isupper() for c in b) / len(b) > 0.8
    if kurz and not laut(kurz):
        return kurz
    if lang and not laut(lang):
        return lang
    x = kurz or lang or ""
    x = re.sub(r"\b(ORD|ORDINARY|SHS|SHARES)\b.*$", "", x).strip()
    return " ".join(w if (len(w) <= 3 and w.isalpha() and w not in ("THE", "AND", "OF")) else w.capitalize() for w in x.split())


def kurzname(n):
    import re
    n = (n or "").split(" - ")[0]
    n = re.sub(r"^The ", "", n)
    n = re.sub(r",? (and|&) (Company|Co\.?)$", "", n)
    muster = (r",? (Inc\.?|Incorporated|Corporation|Corp\.?|Co\.|Company|Holdings?|plc|PLC|N\.V\.?|NV|S\.A\.?|SA|S\.p\.A\.|SpA|"
              r"Ltd\.?|Limited|Group|Technologies|Platforms|AG|SE|S\.E\.|Aktiengesellschaft|KGaA|& Co\.|Oyj|ASA|"
              r"Société Européenne|Societas Europaea|Vz|O\.N\.|NA|Ord\.?|ORD)$")
    while True:
        m = re.sub(muster, "", n).strip(" ,")
        if m == n:
            return n
        n = m


def r2(x):
    return None if x is None else round(x, 2)


FX_EUR = {}  # 1 € = x Fremdwährung, aus aktien.json ("fx_eur"); wird in main() gesetzt


def fx_von(y, fx):
    """Teiler von der Kurswährung in Euro (Kurs / Teiler = Euro). Dollar über fx, Euro 1, Pence = Pfund × 100,
    Franken/Kronen über FX_EUR. Unbekannte Währung: None."""
    w = y.get("waehrung") or "USD"
    if w == "USD":
        return fx
    if w == "EUR":
        return 1.0
    if w in ("GBp", "GBX"):
        return FX_EUR["GBP"] * 100 if FX_EUR.get("GBP") else None
    return FX_EUR.get(w)


def lade(p, default):
    try:
        return json.load(open(p))
    except Exception:
        return default


def boersentage_bis(heute, ziel):
    """Zahl der Börsentage (Mo–Fr) von heute bis ziel (heute = 0)."""
    if ziel < heute:
        return -1
    n, d = 0, heute
    while d < ziel:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


FONDS_WOERTER = re.compile(r"\b(ETF|ETN|Fund|Series [A-Z]|Preferred|Pfd)\b", re.I)


def kuerzel_verdacht(ydata, stand):
    """Findet Kürzel, die wahrscheinlich nicht mehr stimmen. Rückgabe {Kürzel: Grund}.
    - letzter Kurs mehr als 3 Börsentage älter als der Datenstand (z. B. ROKU nach der Übernahme durch Fox,
      SATS nach dem Wechsel zu ECHO)
    - weder Börsenwert noch Gewinnschätzung noch Analysten (ETF, Vorzugspapier oder falsche Börse:
      SIX, ULTI, TIME, SATS, FAGR.AS, INGA.BR am 15.11.2026) oder kein Sektor und ein Fonds-Wort im Namen"""
    try:
        bis = dt.date.fromisoformat((stand or "")[:10])
    except ValueError:
        return {}
    v = {}
    for t, y in ydata.items():
        if t == "SPY":  # Vergleichswert, absichtlich ein ETF
            continue
        ks = (y.get("kurs_stand") or "")[:10]
        if ks:
            try:
                n = boersentage_bis(dt.date.fromisoformat(ks), bis)
            except ValueError:
                n = -1
            if n > 3:
                v[t] = f"kein neuer Kurs seit {ks} ({n} Börsentage) – Übernahme oder neues Kürzel?"
                continue
        name = (y.get("name") or "").strip()
        if not y.get("marktwert") and not y.get("eps_forward") and not y.get("analysten"):
            v[t] = f"weder Börsenwert noch Schätzungen, Name „{name}“ – Fonds, Vorzugspapier oder falsches Kürzel?"
        elif not y.get("sektor") and FONDS_WOERTER.search(name):
            v[t] = f"kein Sektor, Name „{name}“ – Fonds statt Aktie?"
    return v


def schaetz_faktor(y, e1, f):
    """Yahoo liefert Gewinnschätzungen bei ausländischen Aktien mal in der Kurswährung, mal in der
    Berichtswährung (z. B. SAP-ADR in Dollar, ASML-ADR in Euro, PDD in Yuan). Yahoos forwardEps ist immer
    in der Kurswährung. Darum: Passt die Schätzung schon zu forwardEps, wird nicht umgerechnet (Faktor 1);
    passt sie erst nach Umrechnung, wird umgerechnet; passt keins von beiden auf 25 % genau: unklar (None)."""
    if f == 1.0:
        return 1.0
    fe = y.get("eps_forward")
    if not fe or not e1 or fe <= 0 or e1 <= 0:
        return f  # kein Vergleich möglich: wie bisher umrechnen
    if y.get("waehrung") in ("GBp", "GBX") and f > 20 and fe * 100 / e1 > 0:
        # London-Aktien mit Bericht in Dollar/Euro (AstraZeneca, Shell, HSBC, Rio Tinto …): Yahoos forwardEps
        # steht dort in Pfund, der Kurs in Pence. Darum in Pence vergleichen (Fehler gefunden 14.11.2026).
        # Nur wenn der normale Vergleich nichts findet (sonst bleibt alles wie bisher).
        r1, r100 = fe / e1, fe * 100 / e1
        if min(abs(math.log(r1)), abs(math.log(r1 / f))) > math.log(1.25) and abs(math.log(r100 / f)) <= math.log(1.25):
            return f
    r = fe / e1
    d1, df = abs(math.log(r)), abs(math.log(r / f)) if f and f > 0 else 99
    if min(d1, df) > math.log(1.25):
        return None
    if d1 <= df:
        # Gegenprobe mit Kurs und Kursziel (Fehler gefunden 17.11.2026): Bei manchen Aktien steht auch forwardEps
        # in der Berichtswährung, nicht in der Kurswährung (Nordea in Stockholm: Kurs in Kronen, forwardEps 1,37 €).
        # Dann ergäbe Faktor 1 ein KGV über 60 (Nordea 121), mit Umrechnung ein normales. Nur bei großem Faktor.
        kurs, ziel = y.get("kurs"), y.get("kursziel_median") or y.get("kursziel_mittel")
        if kurs and ziel and (f > 3 or f < 1 / 3) and kurs / e1 > 60 and ziel / e1 > 60 \
                and 3 <= kurs / (e1 * f) <= 60 and 3 <= ziel / (e1 * f) <= 80:
            return f
        return 1.0
    return f


DCF_ZINS, DCF_ENDWACHSTUM = 0.09, 0.025  # Abzinsung 9 % pro Jahr, ewiges Wachstum 2,5 %


def dcf_wert(fcf_je_aktie, wachstum):
    """Einfache Cashflow-Rechnung (DCF) je Aktie: Jahre 1–5 wachsen mit `wachstum`, Jahre 6–10 sinkt das
    Wachstum gleichmäßig auf 2,5 %, danach ewig 2,5 %; alles mit 9 % pro Jahr abgezinst."""
    wert, cf, g = 0.0, fcf_je_aktie, wachstum
    for jahr in range(1, 11):
        if jahr > 5:
            g = wachstum + (DCF_ENDWACHSTUM - wachstum) * (jahr - 5) / 5
        cf *= 1 + g
        wert += cf / (1 + DCF_ZINS) ** jahr
    wert += cf * (1 + DCF_ENDWACHSTUM) / (DCF_ZINS - DCF_ENDWACHSTUM) / (1 + DCF_ZINS) ** 10
    return wert


NEWS = {}  # aus data/news.json (News-Agenten), wird in main() gesetzt
HYPE = {}  # aus data/hype.json (Aktien-Scout): viel Aufmerksamkeit; gibt KEINE Punkte, nur eine Markierung
HYPE_TAGE = 3
NEWS_PKT = {"positiv": 1, "neutral": 0, "negativ": -1, "sehr negativ": -2}
NEWS_TAGE = 7


def nachricht(t, heute):
    """Gültige Nachrichten-Einschätzung der News-Agenten: höchstens 7 Tage alt, mit mindestens einer Quelle."""
    n = NEWS.get(t)
    if not n or n.get("urteil") not in NEWS_PKT or not n.get("quellen"):
        return None
    try:
        alter = (heute - dt.date.fromisoformat(str(n.get("datum"))[:10])).days if heute else 0
    except ValueError:
        return None
    return n if 0 <= alter <= NEWS_TAGE else None


def hype(t, heute):
    h = HYPE.get(t)
    if not h or not h.get("grund") or not h.get("quellen"):
        return None
    try:
        alter = (heute - dt.date.fromisoformat(str(h.get("datum"))[:10])).days if heute else 0
    except ValueError:
        return None
    return h if 0 <= alter <= HYPE_TAGE else None


def eur_von(betrag, w, fx):
    """Betrag in Währung w in Euro (Dollar über fx, Euro 1, Pence über Pfund × 100, sonst FX_EUR).
    Unbekannte Währung (z. B. Yuan, Taiwan-Dollar): None – dann den Betrag lieber weglassen."""
    if betrag is None:
        return None
    w = w or "USD"
    q = fx if w == "USD" else 1.0 if w == "EUR" else (FX_EUR["GBP"] * 100 if FX_EUR.get("GBP") else None) \
        if w in ("GBp", "GBX") else FX_EUR.get(w)
    return betrag / q if q else None


def geld(x):
    """Großer Euro-Betrag kurz: 3,4 Bio. €, 160 Mrd. €, 12,5 Mrd. €, 830 Mio. €."""
    a = abs(x)
    if a >= 1e12:
        return f"{de(x / 1e12, 1)} Bio. €"
    if a >= 1e9:
        return f"{de(x / 1e9, 0 if a >= 1e11 else 1)} Mrd. €"
    if a >= 1e6:
        return f"{de(x / 1e6, 0)} Mio. €"
    return f"{de(x, 0)} €"


def kurs_text(x):
    return f"{de(x, 0 if x >= 100 else 2)} €"


def pz(x, nd=0):
    """Prozent mit Vorzeichen, z. B. +12 % oder -3,2 %."""
    x = round(x, nd) + 0.0  # -0,0 vermeiden
    return ("+" if x > 0 else "") + de(x, nd) + " %"


def liste_text(teile):
    return teile[0] if len(teile) == 1 else ", ".join(teile[:-1]) + " und " + teile[-1]


def datum_de(s):
    try:
        return dt.date.fromisoformat(str(s)[:10]).strftime("%d.%m.%Y")
    except ValueError:
        return None


def texte(z, x):
    """Zwei kurze Texte zu einer Aktie, nur aus den Zahlen der Zeile (Auftrag A1, Levin 14.11.2026):
    "warum" = woher die Punkte kommen, "finanzen" = Kurs, Größe, Umsatz, Marge, Cashflow, Schulden, Termine.
    x = Rohwerte aus bewerte(). Keine Empfehlung, kein Platz."""
    dafuer, dagegen = [], []
    kgv, gp, peg, hoch = z["kgv"], z["wachstum_pct"], x["peg"], x["hoch"]
    if peg < 0.6:
        dafuer.append(f"sehr günstig: KGV {de(kgv)} bei {de(gp, 0)} % erwartetem Gewinnwachstum")
    elif peg < 1:
        dafuer.append(f"günstig: KGV {de(kgv)} bei {de(gp, 0)} % erwartetem Gewinnwachstum")
    if hoch > 0.2:
        dafuer.append(f"Kursziel der Analysten {de(hoch * 100, 0)} % über dem Kurs")
    if x["roe"] is not None and x["roe"] > 0.15:
        dafuer.append(f"Eigenkapitalrendite {de(x['roe'] * 100, 0)} %")
    if x["fcf"] is not None and x["fcf"] > 0.015:
        dafuer.append(f"freier Cashflow {de(x['fcf'] * 100, 1)} % des Börsenwerts")
    if x["nde"] is not None and x["nde"] < 1.5:
        dafuer.append("mehr Geld als Schulden" if x["nde"] < 0 else "wenig Schulden")
    if z["trend"] == "steigend":
        dafuer.append("Kurs langfristig steigend")
    if z["kurztrend"] == "steigend":
        dafuer.append("kurzfristig steigend")
    if z["revision_pkt"] > 0:
        dafuer.append("Analysten heben Schätzungen an")
    nk = str(x.get("news_kurz") or "").strip()
    if z["nachrichten_pkt"] > 0:
        dafuer.append("gute Nachrichten" + (f" ({nk})" if nk else ""))
    if z["nachrichten_pkt"] < 0:
        dagegen.append(("sehr negative" if z["nachrichten_pkt"] <= -2 else "negative") + " Nachrichten" + (f" ({nk})" if nk else ""))
    if z["trend"] == "fallend":
        dagegen.append("Kurs langfristig fallend")
    if z["kurztrend"] == "fallend":
        dagegen.append("kurzfristig fallend")
    if z["revision_pkt"] < 0:
        dagegen.append("Analysten senken Schätzungen")
    if x["zyk"]:
        dagegen.append("Speicherchips: Gewinn vermutlich nahe der Spitze (2 Punkte Abzug)")
    if z["analysten"] < 5:
        dagegen.append(f"nur {z['analysten']} Analysten")
    # ohne Abzug, erklärt aber fehlende Punkte
    if peg >= 1:
        g0 = round(gp)
        dagegen.append(f"KGV {de(kgv)} bei nur {de(gp, 0)} % erwartetem Gewinnwachstum" if g0 > 0
                       else "Gewinn soll kaum wachsen" if g0 == 0 else f"Gewinn soll sinken ({pz(gp)})")
    if hoch <= 0.2:
        dagegen.append(f"Kursziel der Analysten {de(-hoch * 100, 0)} % unter dem Kurs" if hoch < 0
                       else f"Kursziel der Analysten nur {de(hoch * 100, 0)} % über dem Kurs")
    if x["nde"] is not None and x["nde"] > 3:
        dagegen.append(f"hohe Schulden ({de(x['nde'])}× EBITDA)")
    if x["fcf"] is not None and x["fcf"] < 0.01:
        dagegen.append("kaum freier Cashflow")
    s = [f"{z['aktie']} bekommt {z['punkte']} von 10 Punkten."]
    if dafuer:
        s.append("Dafür: " + liste_text(dafuer[:6]) + ".")
    if dagegen:
        s.append("Dagegen: " + liste_text(dagegen[:4]) + ".")
    m, k, ab = z["fair_mitte_eur"], z["kurs_eur"], z["abstand_pct"]
    if ab == 0:
        s.append(f"Die faire Mitte ({kurs_text(m)}) liegt etwa beim Kurs ({kurs_text(k)}).")
    else:
        s.append(f"Die faire Mitte ({kurs_text(m)}) liegt {de(abs(ab), 0)} % {'über' if ab > 0 else 'unter'} dem Kurs ({kurs_text(k)}).")
    warum = " ".join(s)

    f = []
    teil = []
    if z.get("veraenderung_1m_pct") is not None:
        teil.append(f"1 Monat {pz(z['veraenderung_1m_pct'], 1)}")
    if z.get("veraenderung_6m_pct") is not None:
        teil.append(f"6 Monate {pz(z['veraenderung_6m_pct'], 1)}")
    uh = z.get("unter_hoch_pct")
    if uh is not None:
        teil.append("nahe am Jahreshoch" if uh >= -2 else f"{de(-uh, 0)} % unter dem Jahreshoch")
    f.append(f"Kurs {kurs_text(z['kurs_eur'])}" + (f" ({', '.join(teil)})." if teil else "."))
    teil = []
    if z.get("marktwert_eur"):
        teil.append(f"Börsenwert {geld(z['marktwert_eur'])}")
    if z.get("umsatz_eur"):
        u = f"Umsatz {geld(z['umsatz_eur'])} im Jahr"
        if z.get("umsatz_wachstum_pct") is not None:
            u += f" ({pz(z['umsatz_wachstum_pct'])} im letzten Quartal zum Vorjahr)"
        teil.append(u)
    if z.get("operative_marge_pct") is not None:
        teil.append(f"operative Marge {de(round(z['operative_marge_pct']) + 0.0, 0)} %")
    if teil:
        f.append(", ".join(teil) + ".")
    teil = []
    finanz = x.get("finanz")  # Banken/Versicherungen: Cashflow und Schulden sagen dort wenig, darum weglassen
    if z.get("fcf_eur") is not None and not finanz:
        teil.append(f"Freier Cashflow {geld(z['fcf_eur'])} im Jahr")
    ns = None if finanz else z.get("nettoschulden_eur")
    if ns is not None:
        if ns < 0:
            teil.append(f"Nettoliquidität {geld(-ns)}")
        else:
            teil.append(f"Nettoschulden {geld(ns)}" + (f" ({de(x['nde'])}× EBITDA)" if x["nde"] is not None and x["nde"] > 0 else ""))
    dv = z.get("dividende_pct")
    if dv is not None:
        teil.append("keine Dividende" if dv == 0 else f"Dividende {de(dv, 1)} %")
    if teil:
        f.append(teil[0][0].upper() + ", ".join(teil)[1:] + ".")
    za = z.get("zahlen_am")
    if za and x.get("heute") and str(za)[:10] >= x["heute"].isoformat() and datum_de(za):
        f.append(f"Nächste Zahlen am {datum_de(za)}.")
    return warum, " ".join(f)


def bewerte(y, fx, alt_by, heute=None):
    """Rechnet eine Aktie aus den Yahoo-Daten. Gibt (zeile, fehlergrund) zurück."""
    t = y["ticker"]
    kurs, ziel = y.get("kurs"), y.get("kursziel_median") or y.get("kursziel_mittel")
    e0, e1, f = y.get("eps_0y"), y.get("eps_+1y"), y.get("eps_faktor")
    fx_bericht = f if (y.get("finanz_waehrung") and y.get("finanz_waehrung") != y.get("waehrung")) else 1.0
    if not kurs or kurs <= 0:
        return None, "kein Kurs"
    if not ziel:
        return None, "kein Kursziel"
    if not e0 or not e1 or f is None:
        return None, "keine Gewinnschätzung"
    q = fx_von(y, fx)
    if q is None:
        return None, f"Kurs in {y.get('waehrung')} (kein Wechselkurs)"
    if heute and y.get("kurs_stand"):
        try:
            if (heute - dt.date.fromisoformat(y["kurs_stand"])).days > 5:
                return None, f"Kurs veraltet ({y['kurs_stand']})"
        except ValueError:
            pass
    f = schaetz_faktor(y, e1, f)
    if f is None:
        return None, "Währung der Gewinnschätzung unklar"
    e0, e1 = e0 * f, e1 * f
    if e1 <= 0 or e0 <= 0:
        return None, "Gewinn nicht positiv"
    if y.get("waehrung") in ("GBp", "GBX") and not (1 <= kurs / e1 <= 200):
        f_alt = (y.get("eps_faktor") or 1.0) if f == 1.0 else 1.0
        e0b, e1b = e0 / f * f_alt, e1 / f * f_alt
        if e1b > 0 and 3 <= kurs / e1b <= 100:
            e0, e1, f = e0b, e1b, f_alt
    kurs_eur, ziel_eur, eps1_eur = kurs / q, ziel / q, e1 / q
    kgv = kurs / e1
    wachstum = e1 / e0 - 1
    if not (1 <= kgv <= 200):
        return None, f"KGV {kgv:.0f} unplausibel"
    if not (-0.5 <= wachstum <= 2.0):
        return None, f"Wachstum {wachstum*100:.0f} % unplausibel"
    gp = wachstum * 100
    peg = kgv / gp if gp > 0 else 99.0
    zyk = t in ZYKLIKER
    fair_kgv = 10 if zyk else max(12, min(25, gp))
    fair_peg = eps1_eur * fair_kgv

    # Freier Cashflow: kommt in der Berichtswährung (z. B. SAP in Euro, PDD in Yuan), der Börsenwert in der
    # Kurswährung. Darum erst umrechnen, dann vergleichen.
    fcf_roh, mcap = y.get("freier_cashflow"), y.get("marktwert")
    if mcap and y.get("anzahl_aktien") and (y.get("waehrung") in ("GBp", "GBX")):
        r_mc = mcap / (y["anzahl_aktien"] * kurs)
        if 0.005 < r_mc < 0.02:  # Börsenwert in Pfund, Kurs in Pence
            mcap *= 100
    fcf = None
    cf_wert = None
    if fcf_roh is not None and mcap and mcap > 0 and fx_bericht:
        fcf_q = fcf_roh * fx_bericht
        fcf = fcf_q / mcap
        finanz = (y.get("sektor") == "Financial Services")  # bei Banken/Versicherungen sagt der Cashflow wenig
        if fcf_q > 0 and not finanz:
            g_cf = 0.0 if zyk else max(0.0, min(0.15, wachstum / 2))  # vorsichtig: halbes erwartetes Gewinnwachstum, höchstens 15 %
            cf_wert = dcf_wert(fcf_q / (mcap / kurs), g_cf) / q
    werte = sorted([fair_peg, ziel_eur] + ([cf_wert] if cf_wert else []))
    if len(werte) == 3:
        # faire Mitte = mittlerer Wert; Spanne von halbem Weg zum unteren bis halbem Weg zum oberen Wert,
        # damit ein einzelner Ausreißer die Spanne nicht riesig macht
        a3, b3, c3 = werte
        mitte, lo, hi = b3, (a3 + b3) / 2, (b3 + c3) / 2
    else:
        lo, hi = werte[0], werte[-1]
        mitte = (lo + hi) / 2
    abstand = mitte / kurs_eur - 1
    hoch = ziel_eur / kurs_eur - 1

    an = y.get("analysten") or 0
    roe, nde = y.get("roe"), y.get("nettoschulden_ebitda")
    trend = y.get("trend")
    rev = y.get("revision_30t")
    bew = (2 if peg < 0.6 else 1 if peg < 1 else 0) + (2 if hoch > 0.4 else 1 if hoch > 0.2 else 0)
    qual = (1 if roe is not None and roe > 0.15 else 0) + (1 if fcf is not None and fcf > 0.015 else 0) \
        + (1 if nde is not None and nde < 1.5 else 0) - (1 if an < 5 else 0) - (2 if zyk else 0)
    trend_pkt = 1 if trend == "steigend" else -1 if trend == "fallend" else 0
    rev_pkt = 1 if rev is not None and rev > 0.02 else -1 if rev is not None and rev < -0.02 else 0
    kurz = y.get("kurztrend")
    kurz_pkt = 1 if kurz == "steigend" else -1 if kurz == "fallend" else 0
    nw = nachricht(t, heute)
    hy = hype(t, heute)
    news_pkt = NEWS_PKT[nw["urteil"]] if nw else 0
    punkte = min(10, bew + qual + trend_pkt + rev_pkt + kurz_pkt + news_pkt)

    haken = []
    if news_pkt < 0:
        haken.append(("sehr negative Nachrichten" if news_pkt <= -2 else "negative Nachrichten") + (": " + str(nw["kurz"]).replace(", ", " und ").replace(",", " ") if nw.get("kurz") else ""))
    if trend == "fallend":
        haken.append("Kurs im Abwärtstrend")
    elif kurz == "fallend":
        haken.append("kurzfristig fallend")
    sw = y.get("schwankung")
    if sw and sw > 0.6:
        haken.append("schwankt sehr stark")
    if zyk:
        haken.append("Speicherchips: Gewinn vermutlich nahe der Spitze, nie Top")
    if nde is not None and nde > 3:
        haken.append(f"hohe Schulden ({nde:.1f}× EBITDA)".replace(".", ","))
    if fcf is not None and fcf < 0.01:
        haken.append("kaum freier Cashflow")
    if an < 5:
        haken.append(f"nur {an} Analysten")
    if rev_pkt < 0:
        haken.append("Analysten senken Schätzungen")
    if cf_wert and cf_wert < kurs_eur * 0.7:
        haken.append("Cashflow-Rechnung deutlich unter Kurs")
    if f != 1.0:
        haken.append(f"Gewinn aus {y.get('finanz_waehrung')} umgerechnet")
    if kgv > 40:
        haken.append(f"KGV {kgv:.0f}")

    unter_hoch = (kurs / y["hoch_52w"] - 1) if y.get("hoch_52w") else None
    a = alt_by.get(t, {})
    zeile = dict(
        ticker=t, aktie=NAMEN.get(t) or kurzname(a.get("aktie") or (y.get("name_lang") if fx_von(y, fx) == 1.0 else None) or name_wahl(y.get("name"), y.get("name_lang")) or t), status="", punkte=int(punkte),
        kurs_eur=r2(kurs_eur), kgv=round(kgv, 1), wachstum_pct=round(gp, 1), peg=r2(peg),
        fair_lo_eur=rf(lo), fair_hi_eur=rf(hi), fair_mitte_eur=rf(mitte), abstand_pct=round(abstand * 100),
        kursziel_eur=round(ziel_eur, 1), haken=", ".join(haken[:3]), seit=a.get("seit"), stand=None,
        id=a.get("id"), daten_stand=None, sektor=branche(y), trend=trend, trend_pkt=trend_pkt, revision_pkt=rev_pkt,
        unter_hoch_pct=None if unter_hoch is None else round(unter_hoch * 100),
        schwankung_pct=None if sw is None else round(sw * 100), zahlen_am=y.get("zahlen_am"),
        kurztrend=kurz, kurztrend_pkt=kurz_pkt, veraenderung_1m_pct=None if y.get("veraenderung_1m") is None else round(y["veraenderung_1m"] * 100, 1),
        analysten=an, bewertungs_pkt=bew, qualitaets_pkt=qual,
        wert_kgv_eur=rf(fair_peg), wert_cf_eur=None if cf_wert is None else rf(cf_wert),
        fcf_rendite_pct=None if fcf is None else round(fcf * 100, 1), waehrung=y.get("waehrung") or "USD", feinwert=None, rang=None,
        nachrichten_pkt=news_pkt, nachrichten_urteil=nw["urteil"] if nw else None, nachrichten=nw.get("grund") if nw else None,
        nachrichten_quellen=(nw.get("quellen") or [])[:3] if nw else None, nachrichten_datum=nw.get("datum") if nw else None,
        hype=(hy or {}).get("grund"), hype_quellen=((hy or {}).get("quellen") or [])[:3] or None, hype_datum=(hy or {}).get("datum"),
        # nur Info, keine Punkte (Levin, 17.11.2026): Piotroski 0–9, Schätzungs-Trend 90 Tage, Momentum 12-1 Monate
        piotroski=y.get("piotroski"), piotroski_von=y.get("piotroski_von"),
        revision_30t_pct=None if y.get("revision_30t") is None else round(y["revision_30t"] * 100, 1),
        revision_90t_pct=None if y.get("revision_90t") is None else round(y["revision_90t"] * 100, 1),
        momentum_12m_pct=None if y.get("momentum_12m") is None else round(y["momentum_12m"] * 100),
    )
    # Finanzielle Lage in Euro (Auftrag A1). Börsenwert ist in der Kurswährung (Pence schon korrigiert),
    # Umsatz, Cashflow und Schulden in der Berichtswährung.
    rw = y.get("finanz_waehrung") or y.get("waehrung")
    def pct(v, nd=1):
        return None if v is None else round(v * 100, nd)
    schulden, cash = y.get("schulden"), y.get("cash")
    hoch52, tief52 = y.get("hoch_52w"), y.get("tief_52w")
    dv = y.get("dividende")
    zeile.update(
        marktwert_eur=None if not mcap else round(mcap / q),
        umsatz_eur=None if not y.get("umsatz") or eur_von(y["umsatz"], rw, fx) is None else round(eur_von(y["umsatz"], rw, fx)),
        umsatz_wachstum_pct=pct(y.get("umsatz_wachstum")), operative_marge_pct=pct(y.get("operative_marge")),
        gewinnmarge_pct=pct(y.get("gewinnmarge")), roe_pct=pct(roe),
        nettoschulden_eur=None if schulden is None or cash is None or eur_von(schulden - cash, rw, fx) is None else round(eur_von(schulden - cash, rw, fx)),
        fcf_eur=None if fcf_roh is None or eur_von(fcf_roh, rw, fx) is None else round(eur_von(fcf_roh, rw, fx)),
        dividende_pct=None if dv is None or not (0 <= dv < 0.3) else round(dv * 100, 2),
        hoch_52w_eur=None if not hoch52 else r2(hoch52 / q), tief_52w_eur=None if not tief52 else r2(tief52 / q),
        veraenderung_6m_pct=pct(y.get("veraenderung_6m")),
    )
    zeile["warum"], zeile["finanzen"] = texte(zeile, dict(peg=peg, hoch=hoch, roe=roe, fcf=fcf, nde=nde, zyk=zyk,
                                                          news_kurz=(nw or {}).get("kurz"), heute=heute,
                                                          finanz=y.get("sektor") == "Financial Services"))
    # Rohwerte für die Feinwertung (werden vor dem Speichern entfernt)
    sma = y.get("sma200")
    zeile["_roh"] = dict(abstand=abstand, peg=peg, hoch=hoch, roe=roe, fcf=fcf, nde=nde, marge=y.get("operative_marge"),
                         r6=y.get("veraenderung_6m"), r1m=y.get("veraenderung_1m"), sma=(kurs / sma - 1) if sma else None, rev=rev)
    return zeile, None


# Feinwertung 0–100: Rang jeder Kennzahl unter allen bewerteten Aktien (0 = schlechteste, 1 = beste).
# Entscheidet bei gleichen Punkten über die Reihenfolge. Fehlt ein Wert, zählt die Mitte (0,5).
FEIN = [  # (Gewicht, [(Kennzahl, +1 = höher ist besser / -1 = niedriger ist besser)])
    (0.35, [("abstand", 1), ("peg", -1), ("hoch", 1)]),                 # Bewertung
    (0.30, [("roe", 1), ("fcf", 1), ("nde", -1), ("marge", 1)]),        # Qualität
    (0.20, [("r6", 1), ("r1m", 1), ("sma", 1)]),                        # Trend
    (0.15, [("rev", 1)]),                                                # Schätzungen der Analysten
]


def feinwertung(zeilen):
    rang = {}
    for _, teile in FEIN:
        for k, richtung in teile:
            werte = sorted(z["_roh"][k] * richtung for z in zeilen if z["_roh"].get(k) is not None)
            n = len(werte)
            rang[k] = (werte, n)
    import bisect
    for z in zeilen:
        summe = 0.0
        for gewicht, teile in FEIN:
            ps = []
            for k, richtung in teile:
                werte, n = rang[k]
                v = z["_roh"].get(k)
                if v is None or n < 2:
                    ps.append(0.5)
                    continue
                v *= richtung
                lo, hi = bisect.bisect_left(werte, v), bisect.bisect_right(werte, v)
                ps.append(((lo + hi - 1) / 2) / (n - 1))
            summe += gewicht * sum(ps) / len(ps)
        z["feinwert"] = round(summe * 100, 1)


def pruefe_zeile(z):
    p = []
    if not z["kurs_eur"] or z["kurs_eur"] <= 0:
        p.append("Kurs")
    if not (z["fair_lo_eur"] <= z["fair_mitte_eur"] + 1 and z["fair_mitte_eur"] <= z["fair_hi_eur"] + 1):
        p.append("faire Spanne")
    if not (-8 <= z["punkte"] <= 10):
        p.append("Punkte")
    if z["punkte"] != min(10, z["bewertungs_pkt"] + z["qualitaets_pkt"] + z["trend_pkt"] + z["revision_pkt"] + z["kurztrend_pkt"] + z["nachrichten_pkt"]):
        p.append("Punktesumme")
    ab = round((z["fair_mitte_eur"] / z["kurs_eur"] - 1) * 100)
    # Toleranz: Kurs (0,01 €) und faire Mitte (rf) sind gerundet – bei Kursen unter 1 € macht das mehrere Prozent aus
    # (17.11.2026: 1816.HK Kurs 0,396 → 0,40 €, Mitte 0,436 → 0,43 €: echt +10 %, aus gerundeten Werten +7 %).
    k, m = max(z["kurs_eur"], 0.01), z["fair_mitte_eur"]
    fehler_m = 0.005 if m < 10 else 0.05 if m < 100 else 0.5
    rundung = 100 * (fehler_m + 0.005 * max(m, 0) / k) / k + 1
    if abs(ab - z["abstand_pct"]) > max(2, abs(z["abstand_pct"]) * 0.02 + rundung):
        p.append("Abstand")
    if z["unter_hoch_pct"] is not None and z["unter_hoch_pct"] > 1:
        p.append("Jahreshoch")
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yahoo", required=True)
    ap.add_argument("--alt", required=True)
    ap.add_argument("--neu", required=True)
    ap.add_argument("--jetzt", required=True)
    ap.add_argument("--kurse")
    ap.add_argument("--keine-trades", action="store_true")
    ap.add_argument("--meine", help="Datei mit Levins eigenen Aktien (ein Kürzel pro Zeile)")
    ap.add_argument("--ohne-depots", action="store_true", help="Musterdepots gestoppt: nicht rechnen, nicht schreiben")
    ap.add_argument("--news", help="Nachrichten der News-Agenten (Standard: news.json neben der Yahoo-Datei)")
    a = ap.parse_args()

    jetzt = dt.datetime.fromisoformat(a.jetzt)
    heute = jetzt.date()
    heute_s = heute.isoformat()
    Y = json.load(open(a.yahoo))
    ydata = {r["ticker"]: r for r in Y["aktien"]}
    fx = Y.get("eurusd") or 1.116
    FX_EUR.update(Y.get("fx_eur") or {})
    def lade_daten(name, pfad):
        """news.json / hype.json neben der Yahoo-Datei; fehlt sie (geplante Aufgaben laden oft nur aktien.json),
        direkt von GitHub holen."""
        d = lade(pfad or os.path.join(os.path.dirname(os.path.abspath(a.yahoo)), name), None)
        if d is None and not pfad:
            try:
                import urllib.request
                with urllib.request.urlopen(f"https://raw.githubusercontent.com/bubelman/aktien-daten/main/data/{name}", timeout=20) as r:
                    d = json.loads(r.read().decode("utf-8"))
            except Exception as e:
                print(f"Hinweis: {name} nicht geladen –", str(e)[:80], file=sys.stderr)
        return (d or {}).get("aktien") or {}
    NEWS.update(lade_daten("news.json", a.news))
    HYPE.update(lade_daten("hype.json", None))
    if a.kurse:
        K = json.load(open(a.kurse))
        fx = K.get("EURUSD") or fx
        for t, k in K.items():
            if t in ydata and k and (ydata[t].get("waehrung") or "USD") == "USD":
                ydata[t]["kurs"] = k
                ydata[t].pop("kurs_stand", None)
    alt = lade(os.path.join(a.alt, "liste.json"), [])
    alt_by = {r["ticker"]: r for r in alt}
    log = lade(os.path.join(a.alt, "aenderungen.json"), [])
    depot = lade(os.path.join(a.alt, "depot.json"), [])
    trades = lade(os.path.join(a.alt, "depot_trades.json"), [])
    verlauf = lade(os.path.join(a.alt, "depot_verlauf.json"), [])
    wichtig, pruef, neu_log = [], [], []

    # 0. Kürzel-Verdacht: Aktien ohne frischen Kurs (Übernahme, Börsenrückzug, neues Kürzel) und Kürzel ohne
    #    Firmendaten (ETF, Vorzugspapier oder falsches Kürzel). Nur Hinweis für die Nachtschicht, ändert keine Punkte.
    verdacht = kuerzel_verdacht(ydata, Y.get("stand"))

    # 1. Alle Aktien bewerten
    zeilen, ausfall = [], {}
    for t, y in ydata.items():
        if t == "SPY":
            continue
        z, grund = bewerte(y, fx, alt_by, heute)
        if z is None:
            ausfall[t] = grund
            continue
        fehler = pruefe_zeile(z)
        if fehler:
            pruef.append(f"{t}: {', '.join(fehler)}")
            continue
        # Kurs-Sprung gegen den letzten Stand (Split oder Datenfehler?)
        o = alt_by.get(t)
        if o and o.get("kurs_eur"):
            q = z["kurs_eur"] / o["kurs_eur"]
            if q < 0.6 or q > 1.6:
                z["haken"] = (z["haken"] + ", " if z["haken"] else "") + "Kurssprung prüfen"
                z["pruefung_offen"] = True
                pruef.append(f"{t}: Kurs {o['kurs_eur']} → {z['kurs_eur']} € (Faktor {q:.2f})")
        zeilen.append(z)

    # Doppelte Firmen (z. B. US-Zweitlisting und Heimatbörse) nur einmal werten: Levins Kürzel zuerst,
    # sonst die Notierung mit den meisten Analysten (bei Gleichstand die Heimatbörse, nicht USD).
    meine_set = set(open(a.meine).read().replace(",", " ").split()) if a.meine and os.path.exists(a.meine) else set()
    def firma(t):
        n = (ydata.get(t, {}).get("name_lang") or "").lower()
        n = re.sub(r"[^a-z0-9 ]", " ", n)
        n = re.sub(r"\b(the|plc|ag|se|sa|nv|n v|inc|corp|corporation|ltd|limited|holding|holdings|group|asa|ab|a s|s a|s p a|spa)\b", " ", n)
        return " ".join(n.split())
    gruppen = {}
    for z in zeilen:
        f = firma(z["ticker"])
        if f:
            gruppen.setdefault(f, []).append(z)
    weg = set()
    for f, zs in gruppen.items():
        if len(zs) < 2:
            continue
        zs.sort(key=lambda z: (z["ticker"] not in meine_set, -(z.get("analysten") or 0), z.get("waehrung") == "USD"))
        for z in zs[1:]:
            if z["ticker"] not in meine_set:
                weg.add(z["ticker"]); ausfall[z["ticker"]] = f"doppelt (gleiche Firma wie {zs[0]['ticker']})"
    zeilen = [z for z in zeilen if z["ticker"] not in weg]

    # 2. Rangliste: erst Punkte, bei Gleichstand die Feinwertung; 50 behalten
    feinwertung(zeilen)
    for z in zeilen:
        z.pop("_roh", None)
        if not (0 <= z["feinwert"] <= 100):
            pruef.append(f"{z['ticker']}: Feinwert {z['feinwert']}")
    zeilen.sort(key=lambda r: (-r["punkte"], -r["feinwert"], -r["abstand_pct"]))
    for i, z in enumerate(zeilen, 1):
        z["rang"] = i
        z["bewertet"] = len(zeilen)
    liste = zeilen[:ANZAHL]
    drin = {r["ticker"] for r in liste}

    # 3. Status
    top, je_branche = [], {}
    for r in liste:
        if len(top) >= TOP_MAX:
            break
        if r["abstand_pct"] > 15 and r["trend"] in ("steigend", "seitwärts") and not r.get("pruefung_offen") \
                and r["ticker"] not in ZYKLIKER \
                and je_branche.get(r["sektor"], 0) < PRO_BRANCHE:
            top.append(r["ticker"])
            je_branche[r["sektor"]] = je_branche.get(r["sektor"], 0) + 1
    beob = 0
    for r in liste:
        if r["seit"] is None:
            r["seit"] = heute_s
        tage = boersentage_bis(dt.date.fromisoformat(r["seit"]), heute)
        if r["ticker"] in top:
            r["status"] = "Top"
        elif r["ticker"] not in alt_by or (tage <= 3 and alt_by[r["ticker"]].get("status") == "Neu"):
            r["status"] = "Neu"
        elif r["punkte"] >= 4 and r["abstand_pct"] > 0 and beob < BEOBACHTEN_MAX:
            r["status"] = "Beobachten"
            beob += 1
        else:
            r["status"] = "Geprüft"
        r["stand"] = jetzt.isoformat()
        r["daten_stand"] = Y.get("stand", "")[:10]
        r.pop("pruefung_offen", None)

    # 4. Änderungsprotokoll für die Liste
    def logz(aktie, aend, grund):
        neu_log.append(dict(datum=heute_s, aktie=aktie, aenderung=aend, grund=grund))

    for r in liste:
        o = alt_by.get(r["ticker"])
        if not o:
            logz(r["aktie"], "aufgenommen", f"{r['punkte']} Punkte, Abstand {r['abstand_pct']:+d} %, Trend {r['trend']}")
        elif o.get("status") != r["status"]:
            logz(r["aktie"], f"von {o.get('status')} zu {r['status']}", f"{r['punkte']} Punkte, Abstand {r['abstand_pct']:+d} %, Trend {r['trend']}")
            if r["status"] == "Top":
                wichtig.append(f"Neuer Top-Treffer: {r['aktie']} ({r['punkte']} Punkte, Abstand {r['abstand_pct']:+d} %)")
        if o and o.get("trend") and o.get("trend") != r["trend"] and (r["status"] == "Top" or o.get("status") == "Top"):
            logz(r["aktie"], f"Trend {o.get('trend')} → {r['trend']}", f"Kurs {r['kurs_eur']} €")
    for t, o in alt_by.items():
        if t not in drin:
            grund = ausfall.get(t, "keine Yahoo-Daten")
            z = next((x for x in zeilen if x["ticker"] == t), None)
            logz(o.get("aktie", t), "entfernt", f"nur {z['punkte']} Punkte" if z else f"keine Bewertung möglich ({grund})")

    by_now = {r["ticker"]: r for r in liste}

    # 4b. Meine Aktien: Levins eigene Auswahl, bewertet mit denselben Regeln
    meine_t = []
    if a.meine and os.path.exists(a.meine):
        for t in open(a.meine).read().replace(",", " ").split():
            t = t.strip().upper()
            if t and t not in meine_t:
                meine_t.append(t)
    alle_z = {r["ticker"]: r for r in zeilen}
    meine_alt = {r.get("ticker"): r for r in lade(os.path.join(a.alt, "meine.json"), [])}
    meine = []
    for t in meine_t:
        z = alle_z.get(t)
        if z:
            m = dict(z)
            m["in_top50"] = t in drin
            m["top_bedingungen"] = bool(z["abstand_pct"] > 15 and z["trend"] in ("steigend", "seitwärts") and t not in ZYKLIKER)
            m["grund"] = None
            m["stand"] = jetzt.isoformat()
            m["daten_stand"] = Y.get("stand", "")[:10]
            meine.append(m)
            o = meine_alt.get(t)
            if o and o.get("punkte") is not None and abs(m["punkte"] - o["punkte"]) >= 2:
                wichtig.append(f"Deine Aktie {m['aktie']}: {o['punkte']} → {m['punkte']} Punkte")
            if o and o.get("kurs_eur") and m.get("kurs_eur"):
                ch = (m["kurs_eur"] / o["kurs_eur"] - 1) * 100
                if abs(ch) >= 5:
                    wichtig.append(f"Deine Aktie {m['aktie']}: Kurs {'+' if ch > 0 else ''}{de(ch)} % seit dem letzten Lauf ({de(o['kurs_eur'], 2)} → {de(m['kurs_eur'], 2)} €)")
            if o and o.get("top_bedingungen") is not None and o["top_bedingungen"] != m["top_bedingungen"]:
                wichtig.append(f"Deine Aktie {m['aktie']} erfüllt die Top-Bedingungen {'jetzt' if m['top_bedingungen'] else 'nicht mehr'}")
            if m.get("zahlen_am"):
                try:
                    if boersentage_bis(heute, dt.date.fromisoformat(m["zahlen_am"])) == 1:
                        wichtig.append(f"Deine Aktie {m['aktie']} hat am nächsten Börsentag Quartalszahlen")
                except ValueError:
                    pass
        else:
            y = ydata.get(t)
            name = NAMEN.get(t) or kurzname((y or {}).get("name_lang") or (y or {}).get("name") or t)
            grund = ausfall.get(t) or ("noch nicht in den Daten – Claude muss sie erst aufnehmen" if not y else "keine Bewertung möglich")
            meine.append(dict(ticker=t, aktie=name, grund=grund, punkte=None, rang=None, stand=jetzt.isoformat(), bewertet=len(zeilen)))
    meine.sort(key=lambda r: (r.get("rang") is None, r.get("rang") or 0))
    if not meine:  # das Dashboard kann keine leere Datei lesen
        meine = [dict(ticker="", aktie="", leer=True, grund="Noch keine Aktien ausgewählt", stand=jetzt.isoformat(), bewertet=len(zeilen))]

    if not a.ohne_depots:
        # 5. Musterdepot
        cash_row = next((p for p in depot if p.get("ticker") == "CASH"), None)
        cash = cash_row["wert_eur"] if cash_row else (verlauf[-1]["cash_eur"] if verlauf else START_GELD)
        pos = [p for p in depot if p.get("ticker") != "CASH"]
        by_now = {r["ticker"]: r for r in liste}
        alle = {r["ticker"]: r for r in zeilen}

        def kurs_von(t, fallback):
            if t in alle:
                return alle[t]["kurs_eur"]
            y = ydata.get(t)
            q = fx_von(y, fx) if y else None
            return round(y["kurs"] / q, 2) if y and y.get("kurs") and q else fallback

        zeit = jetzt.isoformat()
        if not a.keine_trades:
            # Verkaufen, was nicht mehr Top ist
            bleiben = []
            for p in pos:
                if p["ticker"] in top:
                    bleiben.append(p)
                    continue
                k = kurs_von(p["ticker"], p["kurs_eur"])
                erloes = round(p["stueck"] * k, 2)
                cash = round(cash + erloes - GEBUEHR, 2)
                g = (k / p["kaufkurs_eur"] - 1) * 100
                r = alle.get(p["ticker"])
                grund = ("Abwärtstrend" if r and r["trend"] == "fallend" else
                         f"nicht mehr Top: {r['punkte']} Punkte, Abstand {r['abstand_pct']:+d} %" if r else "nicht mehr in der Liste")
                trades.append(dict(zeit=zeit, aktion="Verkauf", ticker=p["ticker"], aktie=p["aktie"], stueck=p["stueck"], kurs_eur=k,
                                   betrag_eur=erloes, gebuehr_eur=GEBUEHR, grund=f"{grund}; Ergebnis {'+' if g >= 0 else ''}{de(g)} %"))
                logz(p["aktie"], "Musterdepot: Verkauf", f"{grund}, {'+' if g >= 0 else ''}{de(g)} %")
                wichtig.append(f"Musterdepot verkauft {p['aktie']} zu {de(k, 2)} € ({'+' if g >= 0 else ''}{de(g)} %)")
            pos = bleiben
            # Kaufen: neue Top-Treffer
            halten = {p["ticker"] for p in pos}
            kaufen, verschoben = [], []
            for t in top:
                if t in halten:
                    continue
                r = by_now[t]
                if r.get("zahlen_am"):
                    try:
                        n = boersentage_bis(heute, dt.date.fromisoformat(r["zahlen_am"]))
                    except ValueError:
                        n = -1
                    if 0 <= n <= 2:
                        verschoben.append(r)
                        continue
                kaufen.append(r)
            for r in verschoben:
                logz(r["aktie"], "Musterdepot: Kauf verschoben", f"Quartalszahlen am {r['zahlen_am']}")
            if kaufen:
                wert = cash + sum(p["stueck"] * kurs_von(p["ticker"], p["kurs_eur"]) for p in pos)
                ziel = wert / TOP_MAX
                je = min(ziel, cash / len(kaufen))
                for r in kaufen:
                    betrag = je - GEBUEHR
                    if betrag <= 10:
                        continue
                    st = math.floor(betrag / r["kurs_eur"] * 10000) / 10000
                    kosten = round(st * r["kurs_eur"], 2)
                    cash = round(cash - kosten - GEBUEHR, 2)
                    pos.append(dict(ticker=r["ticker"], aktie=r["aktie"], stueck=st, kaufkurs_eur=r["kurs_eur"], kaufdatum=heute_s,
                                    kurs_eur=r["kurs_eur"], wert_eur=kosten, gewinn_eur=0.0, gewinn_pct=0.0, id=r.get("id")))
                    gr = f"neuer Top-Treffer: {r['punkte']} Punkte, Abstand {r['abstand_pct']:+d} %, Trend {r['trend']}"
                    trades.append(dict(zeit=zeit, aktion="Kauf", ticker=r["ticker"], aktie=r["aktie"], stueck=st, kurs_eur=r["kurs_eur"],
                                       betrag_eur=kosten, gebuehr_eur=GEBUEHR, grund=gr))
                    logz(r["aktie"], "Musterdepot: Kauf", f"{de(st, 4)} Stück zu {de(r['kurs_eur'], 2)} €")
                    wichtig.append(f"Musterdepot kauft {r['aktie']} für {de(kosten, 0)} € ({de(r['kurs_eur'], 2)} € je Aktie)")
        # Bewerten
        for p in pos:
            k = kurs_von(p["ticker"], p["kurs_eur"])
            p["kurs_eur"] = k
            p["wert_eur"] = round(p["stueck"] * k, 2)
            p["gewinn_eur"] = round(p["wert_eur"] - p["stueck"] * p["kaufkurs_eur"], 2)
            p["gewinn_pct"] = round((k / p["kaufkurs_eur"] - 1) * 100, 2)
            o = next((x for x in depot if x.get("ticker") == p["ticker"]), None)
            if o and o.get("kurs_eur") and abs(k / o["kurs_eur"] - 1) > 0.05:
                ch = (k / o["kurs_eur"] - 1) * 100
                wichtig.append(f"{p['aktie']} im Depot bewegt sich {'+' if ch >= 0 else ''}{de(ch)} %")
            if p["ticker"] in by_now and by_now[p["ticker"]].get("zahlen_am"):
                try:
                    if boersentage_bis(heute, dt.date.fromisoformat(by_now[p["ticker"]]["zahlen_am"])) == 1:
                        wichtig.append(f"{p['aktie']} (im Depot) hat am nächsten Börsentag Quartalszahlen")
                except ValueError:
                    pass
        if cash < -0.005:
            print("FEHLER: Bargeld negativ", file=sys.stderr)
            sys.exit(2)

        # 5b. Depot B: alle 50 Aktien der Liste zu gleichen Teilen (Vergleich: bringt die Top-5-Auswahl etwas?)
        d50 = lade(os.path.join(a.alt, "depot50.json"), None)
        if not d50:
            cash50, pos50 = START_GELD, []
        else:
            c50 = next((p for p in d50 if p.get("ticker") == "CASH"), None)
            cash50 = c50["wert_eur"] if c50 else 0.0
            pos50 = [p for p in d50 if p.get("ticker") != "CASH"]
        n_v = n_k = 0
        if not a.keine_trades:
            bleiben50 = []
            for p in pos50:
                if p["ticker"] in drin:
                    bleiben50.append(p)
                    continue
                k = kurs_von(p["ticker"], p["kurs_eur"])
                cash50 = round(cash50 + p["stueck"] * k - GEBUEHR, 2)
                n_v += 1
            pos50 = bleiben50
            halten50 = {p["ticker"] for p in pos50}
            neue50 = [r for r in liste if r["ticker"] not in halten50]
            if neue50:
                wert50 = cash50 + sum(p["stueck"] * kurs_von(p["ticker"], p["kurs_eur"]) for p in pos50)
                je50 = min(wert50 / ANZAHL, cash50 / len(neue50))
                for r in neue50:
                    betrag = je50 - GEBUEHR
                    if betrag <= 5:
                        continue
                    st = math.floor(betrag / r["kurs_eur"] * 10000) / 10000
                    kosten = round(st * r["kurs_eur"], 2)
                    cash50 = round(cash50 - kosten - GEBUEHR, 2)
                    pos50.append(dict(ticker=r["ticker"], aktie=r["aktie"], stueck=st, kaufkurs_eur=r["kurs_eur"], kaufdatum=heute_s,
                                      kurs_eur=r["kurs_eur"], wert_eur=kosten, gewinn_eur=0.0, gewinn_pct=0.0, id=r.get("id")))
                    n_k += 1
            if n_v or n_k:
                logz("Depot B (alle 50)", "Umschichtung", f"{n_v} verkauft, {n_k} gekauft (je 1 € Gebühr)")
        for p in pos50:
            k = kurs_von(p["ticker"], p["kurs_eur"])
            p["kurs_eur"] = k
            p["wert_eur"] = round(p["stueck"] * k, 2)
            p["gewinn_eur"] = round(p["wert_eur"] - p["stueck"] * p["kaufkurs_eur"], 2)
            p["gewinn_pct"] = round((k / p["kaufkurs_eur"] - 1) * 100, 2)
        if cash50 < -0.005:
            print("FEHLER: Bargeld Depot B negativ", file=sys.stderr)
            sys.exit(2)
        wert50 = round(sum(p["wert_eur"] for p in pos50) + cash50, 2)
        depot50_neu = sorted(pos50, key=lambda p: -p["gewinn_pct"]) + [dict(ticker="CASH", aktie="Bargeld", stueck=None, kaufkurs_eur=None,
                             kaufdatum=None, kurs_eur=None, wert_eur=round(cash50, 2), gewinn_eur=None, gewinn_pct=None, id=None)]
        investiert = round(sum(p["wert_eur"] for p in pos), 2)
        wert = round(investiert + cash, 2)
        spy = ydata.get("SPY", {}).get("kurs")
        if spy:
            vgl = round(SPY_STUECK * spy / fx, 2)
        else:
            vgl = verlauf[-1].get("vergleich_eur") if verlauf else None
        verlauf.append(dict(zeit=zeit, wert_eur=wert, cash_eur=round(cash, 2), investiert_eur=investiert,
                            rendite_pct=round((wert / START_GELD - 1) * 100, 2), positionen=len(pos),
                            vergleich_eur=vgl, vergleich_pct=None if vgl is None else round((vgl / SPY_START - 1) * 100, 2),
                            wert50_eur=wert50, rendite50_pct=round((wert50 / START_GELD - 1) * 100, 2)))
        depot_neu = pos + [dict(ticker="CASH", aktie="Bargeld", stueck=None, kaufkurs_eur=None, kaufdatum=None, kurs_eur=None,
                                wert_eur=round(cash, 2), gewinn_eur=None, gewinn_pct=None, id=None)]

    # 6. Abschlussprüfung
    assert len(liste) == ANZAHL, "nicht 50 Zeilen"
    assert len({r["ticker"] for r in liste}) == ANZAHL, "doppelte Ticker"
    assert [r["rang"] for r in liste] == list(range(1, ANZAHL + 1)), "Rang"
    assert all((a["punkte"], a["feinwert"]) >= (b["punkte"], b["feinwert"]) for a, b in zip(liste, liste[1:])), "Reihenfolge"
    assert sum(1 for r in liste if r["status"] == "Top") <= TOP_MAX
    assert all(r["trend"] != "fallend" for r in liste if r["status"] == "Top")
    if not a.ohne_depots:
        assert {p["ticker"] for p in pos} <= set(top) or a.keine_trades
        assert abs(sum(p["wert_eur"] for p in depot_neu) - wert) < 0.02
        assert trades and trades[0].get("aktion") == "Start"
        assert abs(sum(p["wert_eur"] for p in depot50_neu) - wert50) < 0.02
        assert {p["ticker"] for p in pos50} <= drin or a.keine_trades
    assert meine and len({r["ticker"] for r in meine}) == len(meine), "Meine Aktien doppelt"

    os.makedirs(a.neu, exist_ok=True)
    # Alle bewerteten Aktien (Dashboard-Reiter „Alle Aktien“ und Aktien-Scout). "aufgenommen" = Tag, an dem die
    # Aktie zum ersten Mal bewertet wurde (aus alt/alle.json übernommen; fehlt die Datei, bleibt es leer).
    alt_alle = lade(os.path.join(a.alt, "alle.json"), None)
    alt_auf = {r["ticker"]: r.get("aufgenommen") for r in (alt_alle or [])}
    alle = []
    for z in zeilen:
        z["top_bedingungen"] = bool(z["abstand_pct"] > 15 and z["trend"] in ("steigend", "seitwärts") and z["ticker"] not in ZYKLIKER)
        # leere Felder und Werte, die nur in den Texten stehen, weglassen: alle.json soll unter ~2 MB bleiben
        r = {k: v for k, v in z.items() if k not in ("id", "daten_stand", "status", "seit", "stand", "hoch_52w_eur",
                                                     "tief_52w_eur", "gewinnmarge_pct", "roe_pct", "fcf_eur",
                                                     "veraenderung_6m_pct", "umsatz_wachstum_pct") and v is not None}
        r["aufgenommen"] = alt_auf.get(z["ticker"]) if z["ticker"] in alt_auf else (heute_s if alt_alle is not None else None)
        r["in_meine"] = z["ticker"] in meine_set
        alle.append(r)
    if alle:
        alle[0]["stand"] = jetzt.isoformat()
    out = {"liste.json": liste, "aenderungen.json": (log + neu_log)[-300:], "meine.json": meine, "alle.json": alle}
    if not a.ohne_depots:
        out.update({"depot.json": depot_neu, "depot_trades.json": trades, "depot_verlauf.json": verlauf[-2000:], "depot50.json": depot50_neu})
    for n, d in out.items():
        json.dump(d, open(os.path.join(a.neu, n), "w"), ensure_ascii=False, separators=(",", ":") if n == "alle.json" else None)
    statuswechsel = sum(1 for r in liste if alt_by.get(r["ticker"], {}).get("status") not in (None, r["status"]))
    bericht = dict(
        stand_yahoo=Y.get("stand"), eurusd=fx, bewertet=len(zeilen), ausgefallen=ausfall, pruefung=pruef, kuerzel_verdacht=verdacht,
        top=[dict(ticker=t, aktie=by_now[t]["aktie"], kurs_eur=by_now[t]["kurs_eur"], fair=f"{de(by_now[t]['fair_lo_eur'], 0)}–{de(by_now[t]['fair_hi_eur'], 0)} €",
                  punkte=by_now[t]["punkte"], trend=by_now[t]["trend"], zahlen_am=by_now[t]["zahlen_am"]) for t in top],
        depot=None if a.ohne_depots else dict(wert_eur=wert, rendite_pct=verlauf[-1]["rendite_pct"], vergleich_pct=verlauf[-1]["vergleich_pct"],
                   bargeld_eur=round(cash, 2), positionen=[p["ticker"] for p in pos]),
        depot_b=None if a.ohne_depots else dict(wert_eur=wert50, rendite_pct=verlauf[-1]["rendite50_pct"], positionen=len(pos50), verkauft=n_v, gekauft=n_k),
        meine=[dict(ticker=r["ticker"], aktie=r["aktie"], punkte=r.get("punkte"), rang=r.get("rang"), grund=r.get("grund")) for r in meine if not r.get("leer")],
        statuswechsel=statuswechsel, aenderungen=len(neu_log), wichtig=wichtig,
    )
    json.dump(bericht, open(os.path.join(a.neu, "bericht.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(bericht, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
