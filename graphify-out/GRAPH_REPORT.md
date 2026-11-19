# Graph Report - aktien-daten  (2026-11-19)

## Corpus Check
- 8 files · ~12,933 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 134 nodes · 286 edges · 10 communities (8 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6284c021`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- json
- universum.py
- fetch.py
- main
- bewertung.py
- texte
- screener.py
- fx_von
- name_wahl
- vorhersagekraft.py

## God Nodes (most connected - your core abstractions)
1. `main()` - 18 edges
2. `bewerte()` - 16 edges
3. `grunddaten()` - 10 edges
4. `texte()` - 9 edges
5. `main()` - 9 edges
6. `main()` - 8 edges
7. `de()` - 7 edges
8. `main()` - 7 edges
9. `bewerten()` - 7 edges
10. `main()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `de()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 5 → community 3_
- `bewerte()` --calls--> `name_wahl()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 8 → community 4_
- `name_wahl()` --calls--> `re`  [EXTRACTED]
  bewertung.py →   _Bridges community 8 → community 1_
- `bewerte()` --calls--> `kurzname()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 3 → community 4_
- `bewerte()` --calls--> `fx_von()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 7 → community 4_

## Import Cycles
- None detected.

## Communities (10 total, 2 thin omitted)

### Community 0 - "json"
Cohesion: 0.18
Nodes (9): git(), letzte_je_tag(), main(), bewerten(), datenstand_datum(), gruppe(), main(), schnappschuss() (+1 more)

### Community 1 - "universum.py"
Cohesion: 0.27
Nodes (4): hat_kurs(), lies(), main(), yahoo()

### Community 2 - "fetch.py"
Cohesion: 0.17
Nodes (13): basis(), dividende_anteil(), fcf_aus_cashflow(), fcf_zeile(), grunddaten(), grunddaten_sicher(), jetzt(), kurse_und_trends() (+5 more)

### Community 3 - "main"
Cohesion: 0.22
Nodes (7): feinwertung(), kuerzel_verdacht(), kurzname(), lade(), main(), lade_daten(), pruefe_zeile()

### Community 4 - "bewertung.py"
Cohesion: 0.16
Nodes (9): bewerte(), branche(), dcf_wert(), eur_von(), hype(), nachricht(), r2(), rf() (+1 more)

### Community 5 - "texte"
Cohesion: 0.24
Nodes (7): datum_de(), de(), geld(), kurs_text(), liste_text(), pz(), texte()

### Community 6 - "screener.py"
Cohesion: 0.23
Nodes (7): abfragen(), firma(), fx_tabelle(), heimat(), laender(), main(), zweitlisting()

### Community 9 - "vorhersagekraft.py"
Cohesion: 0.21
Nodes (7): boersentage_bis(), berechnen(), fuenftel(), handelstag(), raenge(), spearman(), tage_laden()

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `json`, `fetch.py`, `bewertung.py`, `texte`, `fx_von`, `vorhersagekraft.py`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `bewerte()` connect `bewertung.py` to `name_wahl`, `main`, `texte`, `fx_von`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `name_wahl()` connect `name_wahl` to `universum.py`, `bewertung.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._