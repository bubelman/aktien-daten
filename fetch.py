"""Holt täglich kostenlose Yahoo-Finance-Daten (über yfinance) für die Aktien-Liste
und schreibt sie nach data/aktien.json. Läuft per GitHub Actions."""
import json, math, time, datetime as dt
import yfinance as yf

TICKERS = open("tickers.txt").read().split()

def num(x):
    try:
        x = float(x)
        return None if math.isnan(x) or math.isinf(x) else x
    except Exception:
        return None

def one(sym):
    t = yf.Ticker(sym)
    out = {"ticker": sym}
    info = {}
    try:
        info = t.info or {}
    except Exception as e:
        out["fehler_info"] = str(e)[:120]
    g = info.get
    out.update(
        name=g("shortName"), waehrung=g("currency"), kurs=num(g("currentPrice") or g("regularMarketPrice")),
        hoch_52w=num(g("fiftyTwoWeekHigh")), tief_52w=num(g("fiftyTwoWeekLow")),
        kursziel_mittel=num(g("targetMeanPrice")), kursziel_median=num(g("targetMedianPrice")),
        kursziel_hoch=num(g("targetHighPrice")), kursziel_tief=num(g("targetLowPrice")),
        analysten=g("numberOfAnalystOpinions"), empfehlung=g("recommendationKey"),
        eps_forward=num(g("forwardEps")), kgv_forward=num(g("forwardPE")), peg_yahoo=num(g("trailingPegRatio")),
        roe=num(g("returnOnEquity")), operative_marge=num(g("operatingMargins")),
        freier_cashflow=num(g("freeCashflow")), marktwert=num(g("marketCap")),
        ebitda=num(g("ebitda")), schulden=num(g("totalDebt")), cash=num(g("totalCash")),
        sektor=g("sector"), branche=g("industry"),
    )
    if out["freier_cashflow"] and out["marktwert"]:
        out["fcf_rendite"] = out["freier_cashflow"] / out["marktwert"]
    if out["ebitda"] and out["ebitda"] > 0 and out["schulden"] is not None and out["cash"] is not None:
        out["nettoschulden_ebitda"] = (out["schulden"] - out["cash"]) / out["ebitda"]
    # Gewinnschätzungen: laufendes Jahr (0y) und nächstes Jahr (+1y)
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
    # Revisionen: Schätzung nächstes Jahr heute gegen vor 30 Tagen
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
    # Termin der nächsten Quartalszahlen
    try:
        cal = t.calendar
        d = cal.get("Earnings Date") if isinstance(cal, dict) else None
        if d:
            out["zahlen_am"] = str(d[0] if isinstance(d, (list, tuple)) else d)[:10]
    except Exception:
        pass
    # Trend und Schwankung aus 1 Jahr Tageskursen
    try:
        h = t.history(period="14mo", interval="1d", auto_adjust=True)["Close"].dropna()
        if len(h) >= 200:
            c = float(h.iloc[-1]); sma = float(h.iloc[-200:].mean()); r6 = c / float(h.iloc[-127]) - 1
            rets = h.pct_change().dropna().iloc[-252:]
            out.update(sma200=sma, veraenderung_6m=r6, schwankung=float(rets.std() * math.sqrt(252)),
                       trend=("steigend" if c > sma and r6 > 0 else "fallend" if c < sma and r6 < 0 else "seitwärts"))
    except Exception as e:
        out["fehler_verlauf"] = str(e)[:120]
    return out

rows = []
for s in TICKERS:
    for versuch in range(3):
        try:
            rows.append(one(s)); break
        except Exception as e:
            if versuch == 2:
                rows.append({"ticker": s, "fehler": str(e)[:200]})
            time.sleep(5)
    time.sleep(1.5)

stand = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
ok = sum(1 for r in rows if r.get("kurs"))
json.dump({"stand": stand, "quelle": "Yahoo Finance über yfinance (inoffiziell)", "anzahl": len(rows), "mit_kurs": ok, "aktien": rows},
          open("data/aktien.json", "w"), ensure_ascii=False, indent=1)
print(f"{ok}/{len(rows)} Aktien mit Kurs, Stand {stand}")
