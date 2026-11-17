"""Holt kostenlose Yahoo-Finance-Daten (über yfinance) für die Aktien-Liste und schreibt data/aktien.json.
Läuft per GitHub Actions.

  python fetch.py --voll   Grunddaten (Kursziele, Gewinnschätzungen, Kennzahlen) für alle Aktien
                           aus tickers.txt neu holen, danach die Kurse. Dauert ca. 40 Minuten, 1x am Morgen.
  python fetch.py          Nur Kurse und Trends neu holen (ein Sammelabruf, 1–3 Minuten). Grunddaten
                           bleiben aus dem letzten Vollabruf.
"""
import json, math, sys, time, datetime as dt
import yfinance as yf

DATEI = "data/aktien.json"
TICKERS = open("tickers.txt").read().split()


def num(x):
    try:
        x = float(x)
        return None if math.isnan(x) or math.isinf(x) else x
    except Exception:
        return None


def jetzt():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def basis(w):
    """Währung ohne Pence-Schreibweise: ('GBP', 100) für GBp/GBX, sonst (w, 1)."""
    return ("GBP", 100.0) if w in ("GBp", "GBX") else (w, 1.0)


def fcf_zeile(df):
    """Freier Cashflow je Periode aus einer yfinance-Kapitalflussrechnung (Spalten = Perioden, neueste zuerst)."""
    if df is None or df.empty:
        return None
    if "Free Cash Flow" in df.index:
        return df.loc["Free Cash Flow"]
    if "Operating Cash Flow" in df.index and "Capital Expenditure" in df.index:
        return df.loc["Operating Cash Flow"] + df.loc["Capital Expenditure"]  # Investitionen sind negativ
    return None


def fcf_aus_cashflow(t):
    try:
        z = fcf_zeile(t.quarterly_cashflow)
        if z is not None:
            w = [num(x) for x in z.iloc[:4]]
            if len(w) == 4 and all(x is not None for x in w):
                return sum(w), "4 Quartale"
    except Exception:
        pass
    try:
        z = fcf_zeile(t.cashflow)
        if z is not None and len(z) and num(z.iloc[0]) is not None:
            return num(z.iloc[0]), "Geschäftsjahr"
    except Exception:
        pass
    return None, None


PIO_MAX = 700        # so viele Piotroski-Werte höchstens je Lauf neu rechnen (3 Abrufe je Aktie); Rest rollt nach
PIO_TAGE = 7         # Piotroski-Wert hält eine Woche (Jahresabschlüsse ändern sich selten)
_pio_zaehler = [0]


def _zeile(df, *namen):
    for n in namen:
        if df is not None and n in df.index:
            return [num(x) for x in df.loc[n].tolist()]
    return None


def piotroski(t):
    """Piotroski-F-Wert (0–9) aus den Jahresabschlüssen (Levin, 17.11.2026; nur Info, keine Punkte).
    Neun Prüfungen, je 1 Punkt: Gewinn > 0, operativer Cashflow > 0, Gesamtkapitalrendite steigt, Cashflow > Gewinn,
    Verschuldung (langfristige Schulden / Bilanzsumme) sinkt, Liquidität (Umlaufvermögen / kurzfr. Schulden) steigt,
    keine neuen Aktien, Bruttomarge steigt, Kapitalumschlag (Umsatz / Bilanzsumme) steigt.
    Rückgabe (Wert, Zahl der prüfbaren Punkte); None, wenn weniger als 7 Prüfungen möglich sind."""
    ist, bil, cfl = t.income_stmt, t.balance_sheet, t.cashflow
    ni = _zeile(ist, "Net Income", "Net Income Common Stockholders")
    rev = _zeile(ist, "Total Revenue", "Operating Revenue")
    gp = _zeile(ist, "Gross Profit")
    ta = _zeile(bil, "Total Assets")
    ltd = _zeile(bil, "Long Term Debt", "Long Term Debt And Capital Lease Obligation")
    ca = _zeile(bil, "Current Assets")
    cl = _zeile(bil, "Current Liabilities")
    sh = _zeile(bil, "Ordinary Shares Number", "Share Issued")
    cfo = _zeile(cfl, "Operating Cash Flow", "Cash Flow From Continuing Operating Activities")
    g = lambda r, i: r[i] if r and len(r) > i and r[i] is not None else None
    tests = []
    def test(bed):
        tests.append(bed)
    n0, c0, a0, a1, a2 = g(ni, 0), g(cfo, 0), g(ta, 0), g(ta, 1), g(ta, 2)
    test(None if n0 is None else n0 > 0)
    test(None if c0 is None else c0 > 0)
    n1 = g(ni, 1)
    roa0 = n0 / (a1 or a0) if n0 is not None and (a1 or a0) else None
    roa1 = n1 / (a2 or a1) if n1 is not None and (a2 or a1) else None
    test(None if roa0 is None or roa1 is None else roa0 > roa1)
    test(None if n0 is None or c0 is None else c0 > n0)
    l0, l1 = (g(ltd, 0) or 0.0) if ltd else None, (g(ltd, 1) or 0.0) if ltd else None
    test(None if l0 is None or not a0 or not a1 else l0 / a0 < l1 / a1 or (l0 == 0 and l1 == 0))
    cr0 = g(ca, 0) / g(cl, 0) if g(ca, 0) and g(cl, 0) else None
    cr1 = g(ca, 1) / g(cl, 1) if g(ca, 1) and g(cl, 1) else None
    test(None if cr0 is None or cr1 is None else cr0 > cr1)
    test(None if g(sh, 0) is None or g(sh, 1) is None else g(sh, 0) <= g(sh, 1) * 1.005)
    gm0 = g(gp, 0) / g(rev, 0) if g(gp, 0) is not None and g(rev, 0) else None
    gm1 = g(gp, 1) / g(rev, 1) if g(gp, 1) is not None and g(rev, 1) else None
    test(None if gm0 is None or gm1 is None else gm0 > gm1)
    at0 = g(rev, 0) / (a1 or a0) if g(rev, 0) and (a1 or a0) else None
    at1 = g(rev, 1) / (a2 or a1) if g(rev, 1) and (a2 or a1) else None
    test(None if at0 is None or at1 is None else at0 > at1)
    gueltig = [x for x in tests if x is not None]
    if len(gueltig) < 7:
        return None, len(gueltig)
    return sum(gueltig), len(gueltig)


def dividende_anteil(dy, trailing):
    """Dividendenrendite als Anteil (0,025 = 2,5 %). Yahoo liefert "dividendYield" inzwischen meist in Prozent
    (0,41 = 0,41 %), früher als Anteil; "trailingAnnualDividendYield" ist immer ein Anteil. Darum: die
    Schreibweise nehmen, die näher am Vorjahreswert liegt; ohne Vergleich gilt alles über 0,2 als Prozent."""
    dy, tr = num(dy), num(trailing)
    if dy is None:
        return tr
    if dy <= 0:
        return 0.0
    if tr and tr > 0:
        return dy if abs(math.log(dy / tr)) < abs(math.log(dy / 100 / tr)) else dy / 100
    return dy / 100 if dy > 0.2 else dy


def grunddaten(sym, alt_r=None):
    t = yf.Ticker(sym)
    out = {"ticker": sym}
    info = {}
    try:
        info = t.info or {}
    except Exception as e:
        out["fehler_info"] = str(e)[:120]
    g = info.get
    out.update(
        name=g("shortName") or g("longName"), name_lang=g("longName"), waehrung=g("currency"), kurs=num(g("currentPrice") or g("regularMarketPrice")),
        hoch_52w=num(g("fiftyTwoWeekHigh")), tief_52w=num(g("fiftyTwoWeekLow")),
        kursziel_mittel=num(g("targetMeanPrice")), kursziel_median=num(g("targetMedianPrice")),
        kursziel_hoch=num(g("targetHighPrice")), kursziel_tief=num(g("targetLowPrice")),
        analysten=g("numberOfAnalystOpinions"), empfehlung=g("recommendationKey"),
        eps_forward=num(g("forwardEps")), kgv_forward=num(g("forwardPE")), peg_yahoo=num(g("trailingPegRatio")),
        roe=num(g("returnOnEquity")), operative_marge=num(g("operatingMargins")),
        freier_cashflow=num(g("freeCashflow")), marktwert=num(g("marketCap")),
        ebitda=num(g("ebitda")), schulden=num(g("totalDebt")), cash=num(g("totalCash")),
        sektor=g("sector"), branche=g("industry"), finanz_waehrung=g("financialCurrency"),
        # für den Text „Finanzielle Lage“ (Auftrag A1, 14.11.2026); Umsatz in der Berichtswährung
        umsatz=num(g("totalRevenue")), umsatz_wachstum=num(g("revenueGrowth")), gewinnmarge=num(g("profitMargins")),
        bruttomarge=num(g("grossMargins")), kgv_trailing=num(g("trailingPE")),
        dividende=dividende_anteil(g("dividendYield"), g("trailingAnnualDividendYield")),
    )
    # Gewinnschätzungen sind in der Berichtswährung (z. B. PDD in Yuan); Faktor in die Kurswährung
    out["eps_faktor"] = 1.0
    out["anzahl_aktien"] = num(g("sharesOutstanding"))
    fw, kw = out.get("finanz_waehrung"), out.get("waehrung")
    if fw and kw and fw != kw:
        # Pence (GBp/GBX) = Pfund/100: London-Aktien notieren in Pence, berichten aber in Pfund
        (fwb, fwm), (kwb, kwm) = basis(fw), basis(kw)
        if fwb == kwb:
            out["eps_faktor"] = kwm / fwm
        else:
            try:
                fx = yf.Ticker(f"{fwb}{kwb}=X").history(period="5d")["Close"].dropna()
                out["eps_faktor"] = float(fx.iloc[-1]) * kwm / fwm if len(fx) else None
            except Exception:
                out["eps_faktor"] = None
    # Yahoos "freeCashflow" in info ist der „Levered Free Cash Flow“ (eigene Herleitung, bei NVIDIA 41,8 statt
    # ~127 Mrd. $). Darum: freier Cashflow = Summe der letzten 4 Quartale (operativer Cashflow minus Investitionen)
    # aus der Kapitalflussrechnung; Ersatz: letztes Geschäftsjahr; erst dann der Wert aus info.
    out["fcf_levered"] = out["freier_cashflow"]
    fcf, quelle = fcf_aus_cashflow(t)
    if fcf is not None:
        out["freier_cashflow"], out["fcf_quelle"] = fcf, quelle
    else:
        out["fcf_quelle"] = "info (levered)"
    if out["freier_cashflow"] and out["marktwert"]:
        out["fcf_rendite"] = out["freier_cashflow"] / out["marktwert"]
    if out["ebitda"] and out["ebitda"] > 0 and out["schulden"] is not None and out["cash"] is not None:
        out["nettoschulden_ebitda"] = (out["schulden"] - out["cash"]) / out["ebitda"]
    try:
        ee = t.earnings_estimate
        if ee is not None and len(ee):
            for per in ("0q", "+1q", "0y", "+1y"):
                if per in ee.index:
                    r = ee.loc[per]
                    out[f"eps_{per}"] = num(r.get("avg"))
                    out[f"analysten_{per}"] = num(r.get("numberOfAnalysts"))
            if out.get("eps_0y") and out.get("eps_+1y") and out["eps_0y"] > 0:
                out["wachstum_naechstes_jahr"] = out["eps_+1y"] / out["eps_0y"] - 1
    except Exception as e:
        out["fehler_schaetzung"] = str(e)[:120]
    try:
        tr = t.eps_trend
        if tr is not None and "+1y" in tr.index:
            r = tr.loc["+1y"]
            cur, ago = num(r.get("current")), num(r.get("30daysAgo"))
            out["eps_naechstes_jahr_jetzt"], out["eps_naechstes_jahr_vor30"] = cur, ago
            if cur and ago:
                out["revision_30t"] = cur / ago - 1
            ago90 = num(r.get("90daysAgo"))
            if cur and ago90:
                out["revision_90t"] = cur / ago90 - 1
    except Exception as e:
        out["fehler_trend"] = str(e)[:120]
    try:
        cal = t.calendar
        d = cal.get("Earnings Date") if isinstance(cal, dict) else None
        if d:
            out["zahlen_am"] = str(d[0] if isinstance(d, (list, tuple)) else d)[:10]
    except Exception:
        pass
    # Piotroski-Wert nur einmal pro Woche neu rechnen (spart Abrufe); sonst den alten übernehmen
    alt_r = alt_r or {}
    alt_pio = str(alt_r.get("piotroski_stand") or "")
    frisch = alt_pio and (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(alt_pio)).days < PIO_TAGE
    if frisch or _pio_zaehler[0] >= PIO_MAX:
        for k in ("piotroski", "piotroski_von", "piotroski_stand"):
            if k in alt_r:
                out[k] = alt_r[k]
    else:
        _pio_zaehler[0] += 1
        try:
            w, von = piotroski(t)
            out["piotroski"], out["piotroski_von"], out["piotroski_stand"] = w, von, jetzt()
        except Exception as e:
            out["fehler_piotroski"] = str(e)[:120]
    out["grunddaten_stand"] = jetzt()
    return out


KURS_FELDER = ("kurs", "hoch_52w", "tief_52w", "kurs_stand", "sma200", "veraenderung_6m", "schwankung", "trend",
               "sma50", "veraenderung_1m", "kurztrend", "momentum_12m")


def kurse_und_trends(rows, alt_by=None):
    """Ein Sammelabruf: 14 Monate Tageskurse für alle Aktien -> Kurs, 52-Wochen-Spanne, Trends, Schwankung.

    Schutz gegen Rückschritt: Nach Mitternacht Ortszeit (Hongkong/Tokio, ab ca. 15–16 Uhr UTC) liefert Yahoo für
    asiatische Börsen den letzten Handelstag nicht mehr mit; der Kurs fiel dann jeden Abend auf den Vortag zurück
    (gesehen am 16.11.2026: 105 .HK und 69 .T mit Stand Freitag statt Montag). Ist der neue Kurs älter als der
    gespeicherte, bleiben die gespeicherten Kursfelder stehen."""
    alt_by = alt_by or {}
    syms = [r["ticker"] for r in rows]
    frisch = set()
    for i in range(0, len(syms), 200):
        teil = syms[i:i + 200]
        for versuch in range(3):
            try:
                df = yf.download(teil, period="14mo", interval="1d", auto_adjust=True, group_by="ticker",
                                 threads=True, progress=False)
                break
            except Exception as e:
                print("Sammelabruf fehlgeschlagen:", e)
                df = None
                time.sleep(20)
        if df is None:
            continue
        for s in teil:
            try:
                h = (df[s]["Close"] if len(teil) > 1 else df["Close"]).dropna()
            except Exception:
                continue
            if len(h) < 1:
                continue
            r = next(x for x in rows if x["ticker"] == s)
            alt_r = alt_by.get(s) or {}
            if str(h.index[-1])[:10] < str(alt_r.get("kurs_stand") or ""):
                for k in KURS_FELDER:
                    if k in alt_r:
                        r[k] = alt_r[k]
                frisch.add(s)
                continue
            c = float(h.iloc[-1])  # auch bei kurzer Historie (z. B. Neuling an der Börse) den Kurs aktualisieren
            j = h.iloc[-252:]
            r.update(kurs=c, hoch_52w=float(j.max()), tief_52w=float(j.min()), kurs_stand=str(h.index[-1])[:10])
            frisch.add(s)
            for k in ("sma200", "veraenderung_6m", "schwankung", "trend", "sma50", "veraenderung_1m", "kurztrend", "momentum_12m"):
                r.pop(k, None)
            if len(h) >= 253:
                # Momentum 12 Monate ohne den letzten Monat (übliche Forschungs-Definition, „12-1“); nur Info
                r["momentum_12m"] = float(h.iloc[-22]) / float(h.iloc[-253]) - 1
            if len(h) >= 200:
                sma = float(h.iloc[-200:].mean()); r6 = c / float(h.iloc[-127]) - 1
                rets = h.pct_change().dropna().iloc[-252:]
                r.update(sma200=sma, veraenderung_6m=r6, schwankung=float(rets.std() * math.sqrt(252)),
                         trend=("steigend" if c > sma and r6 > 0 else "fallend" if c < sma and r6 < 0 else "seitwärts"))
                sma50 = float(h.iloc[-50:].mean()); r1m = c / float(h.iloc[-22]) - 1
                r.update(sma50=sma50, veraenderung_1m=r1m,
                         kurztrend=("steigend" if c > sma50 and r1m > 0 else "fallend" if c < sma50 and r1m < 0 else "seitwärts"))
        time.sleep(3)
    return frisch


def main():
    voll = "--voll" in sys.argv
    try:
        alt = json.load(open(DATEI))
    except Exception:
        alt = {"aktien": []}
    alt_by = {r["ticker"]: r for r in alt.get("aktien", [])}
    nur_neu = None
    if "--voll-wenn-alt" in sys.argv:
        # GitHub startet geplante Läufe oft Stunden zu spät oder gar nicht. Darum gibt es mehrere Versuche
        # am Morgen; nur der erste des Tages holt die Grunddaten, die anderen nur Kurse. Neue Kürzel in
        # tickers.txt (noch ohne Grunddaten) erzwingen ebenfalls einen Vollabruf.
        heute = dt.datetime.now(dt.timezone.utc).date().isoformat()
        neu = [t for t in TICKERS if t not in alt_by]
        voll = not str(alt.get("grunddaten_stand") or "").startswith(heute)
        if not voll and neu:
            nur_neu = set(neu)  # Grunddaten von heute da: nur die neuen Kürzel nachholen
        print("Vollabruf" if voll else f"Grunddaten von heute da: {len(neu)} neue Kürzel nachholen" if neu else "Grunddaten von heute schon da: nur Kurse")

    if voll or nur_neu:
        rows = []
        for n, s in enumerate(TICKERS, 1):
            if nur_neu is not None and s not in nur_neu:
                rows.append(alt_by.get(s) or {"ticker": s}); continue
            for versuch in range(3):
                try:
                    rows.append(grunddaten(s, alt_by.get(s))); break
                except Exception as e:
                    if versuch == 2:
                        rows.append(alt_by.get(s) or {"ticker": s, "fehler": str(e)[:200]})
                    time.sleep(5)
            if n % 50 == 0:
                print(f"{n}/{len(TICKERS)} Grunddaten")
            time.sleep(0.8)
        grund_stand = jetzt() if voll else alt.get("grunddaten_stand")
    else:
        rows = [alt_by.get(s) or {"ticker": s} for s in TICKERS]
        grund_stand = alt.get("grunddaten_stand")

    frisch = kurse_und_trends(rows, alt_by)

    try:
        eurusd = float(yf.Ticker("EURUSD=X").history(period="5d")["Close"].dropna().iloc[-1])
    except Exception:
        eurusd = alt.get("eurusd")
    # Euro-Kurse weiterer Währungen (1 € = x), für Aktien aus London, der Schweiz und Skandinavien
    fx_eur = dict(alt.get("fx_eur") or {})
    fx_eur["USD"] = eurusd
    for c in ("GBP", "CHF", "DKK", "SEK", "NOK", "JPY", "CAD", "AUD", "HKD"):
        try:
            fx_eur[c] = float(yf.Ticker(f"EUR{c}=X").history(period="5d")["Close"].dropna().iloc[-1])
        except Exception:
            pass

    stand = jetzt()
    json.dump({"stand": stand, "grunddaten_stand": grund_stand, "eurusd": eurusd, "fx_eur": fx_eur,
               "quelle": "Yahoo Finance über yfinance (inoffiziell)", "anzahl": len(rows), "mit_kurs": len(frisch),
               "aktien": rows}, open(DATEI, "w"), ensure_ascii=False, indent=1)
    print(f"{len(frisch)}/{len(rows)} Aktien mit frischem Kurs, Stand {stand}, Grunddaten {grund_stand}")


if __name__ == "__main__":
    main()
