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


def grunddaten(sym):
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
    except Exception as e:
        out["fehler_trend"] = str(e)[:120]
    try:
        cal = t.calendar
        d = cal.get("Earnings Date") if isinstance(cal, dict) else None
        if d:
            out["zahlen_am"] = str(d[0] if isinstance(d, (list, tuple)) else d)[:10]
    except Exception:
        pass
    out["grunddaten_stand"] = jetzt()
    return out


def kurse_und_trends(rows):
    """Ein Sammelabruf: 14 Monate Tageskurse für alle Aktien -> Kurs, 52-Wochen-Spanne, Trends, Schwankung."""
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
            c = float(h.iloc[-1])  # auch bei kurzer Historie (z. B. Neuling an der Börse) den Kurs aktualisieren
            j = h.iloc[-252:]
            r.update(kurs=c, hoch_52w=float(j.max()), tief_52w=float(j.min()), kurs_stand=str(h.index[-1])[:10])
            frisch.add(s)
            for k in ("sma200", "veraenderung_6m", "schwankung", "trend", "sma50", "veraenderung_1m", "kurztrend"):
                r.pop(k, None)
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
    if "--voll-wenn-alt" in sys.argv:
        # GitHub startet geplante Läufe oft Stunden zu spät oder gar nicht. Darum gibt es mehrere Versuche
        # am Morgen; nur der erste des Tages holt die Grunddaten, die anderen nur Kurse. Neue Kürzel in
        # tickers.txt (noch ohne Grunddaten) erzwingen ebenfalls einen Vollabruf.
        heute = dt.datetime.now(dt.timezone.utc).date().isoformat()
        neu = [t for t in TICKERS if t not in alt_by]
        voll = not str(alt.get("grunddaten_stand") or "").startswith(heute) or bool(neu)
        print("Vollabruf" if voll else "Grunddaten von heute schon da: nur Kurse")

    if voll:
        rows = []
        for n, s in enumerate(TICKERS, 1):
            for versuch in range(3):
                try:
                    rows.append(grunddaten(s)); break
                except Exception as e:
                    if versuch == 2:
                        rows.append(alt_by.get(s) or {"ticker": s, "fehler": str(e)[:200]})
                    time.sleep(5)
            if n % 50 == 0:
                print(f"{n}/{len(TICKERS)} Grunddaten")
            time.sleep(0.8)
        grund_stand = jetzt()
    else:
        rows = [alt_by.get(s) or {"ticker": s} for s in TICKERS]
        grund_stand = alt.get("grunddaten_stand")

    frisch = kurse_und_trends(rows)

    try:
        eurusd = float(yf.Ticker("EURUSD=X").history(period="5d")["Close"].dropna().iloc[-1])
    except Exception:
        eurusd = alt.get("eurusd")
    # Euro-Kurse weiterer Währungen (1 € = x), für Aktien aus London, der Schweiz und Skandinavien
    fx_eur = dict(alt.get("fx_eur") or {})
    fx_eur["USD"] = eurusd
    for c in ("GBP", "CHF", "DKK", "SEK", "NOK"):
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
