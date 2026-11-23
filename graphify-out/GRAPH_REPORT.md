# Graph Report - aktien-daten  (2026-11-23)

## Corpus Check
- 8 files · ~13,543 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 144 nodes · 302 edges · 9 communities (8 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d1a3ba79`
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
- vorhersagekraft.py

## God Nodes (most connected - your core abstractions)
1. `main()` - 20 edges
2. `bewerte()` - 18 edges
3. `grunddaten()` - 11 edges
4. `texte()` - 9 edges
5. `main()` - 9 edges
6. `de()` - 8 edges
7. `main()` - 8 edges
8. `main()` - 7 edges
9. `bewerten()` - 7 edges
10. `main()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `de()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 5 → community 3_
- `bewerte()` --calls--> `name_wahl()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 1 → community 4_
- `bewerte()` --calls--> `kurzname()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 3 → community 4_
- `bewerte()` --calls--> `fx_von()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 7 → community 4_
- `lade()` --calls--> `json`  [EXTRACTED]
  bewertung.py →   _Bridges community 3 → community 0_

## Import Cycles
- None detected.

## Communities (9 total, 1 thin omitted)

### Community 0 - "json"
Cohesion: 0.18
Nodes (9): git(), letzte_je_tag(), main(), bewerten(), datenstand_datum(), gruppe(), main(), schnappschuss() (+1 more)

### Community 1 - "universum.py"
Cohesion: 0.20
Nodes (5): name_wahl(), hat_kurs(), lies(), main(), yahoo()

### Community 2 - "fetch.py"
Cohesion: 0.15
Nodes (14): basis(), dividende_anteil(), fcf_aus_cashflow(), fcf_zeile(), grunddaten(), grunddaten_sicher(), jetzt(), kurse_und_trends() (+6 more)

### Community 3 - "main"
Cohesion: 0.17
Nodes (8): feinwertung(), kuerzel_verdacht(), kurzname(), lade(), main(), lade_daten(), pruefe_zeile(), split_verdacht()

### Community 4 - "bewertung.py"
Cohesion: 0.13
Nodes (11): bewerte(), branche(), dcf_wert(), eur_von(), hype(), nachricht(), r2(), rf() (+3 more)

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
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `json`, `fetch.py`, `bewertung.py`, `texte`, `fx_von`, `vorhersagekraft.py`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Should `bewertung.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12648221343873517 - nodes in this community are weakly interconnected._
- **Why does `bewerte()` connect `bewertung.py` to `universum.py`, `main`, `texte`, `fx_von`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `name_wahl()` connect `universum.py` to `bewertung.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._