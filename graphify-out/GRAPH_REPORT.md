# Graph Report - repo-ad  (2026-11-17)

## Corpus Check
- 6 files · ~10,411 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 106 nodes · 233 edges · 10 communities (6 shown, 4 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cfad5aa4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schnappschuss.py
- json
- fetch.py
- main
- bewertung.py
- texte
- name_wahl
- dcf_wert
- nachricht
- schaetz_faktor

## God Nodes (most connected - your core abstractions)
1. `main()` - 18 edges
2. `bewerte()` - 16 edges
3. `texte()` - 9 edges
4. `main()` - 9 edges
5. `grunddaten()` - 8 edges
6. `de()` - 7 edges
7. `main()` - 7 edges
8. `bewerten()` - 7 edges
9. `kurse_und_trends()` - 6 edges
10. `trefferquote()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `de()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 5 → community 3_
- `bewerte()` --calls--> `name_wahl()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 6 → community 4_
- `name_wahl()` --calls--> `re`  [EXTRACTED]
  bewertung.py →   _Bridges community 6 → community 1_
- `main()` --calls--> `kurzname()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 4 → community 3_
- `lade()` --calls--> `json`  [EXTRACTED]
  bewertung.py →   _Bridges community 3 → community 1_

## Import Cycles
- None detected.

## Communities (10 total, 4 thin omitted)

### Community 0 - "schnappschuss.py"
Cohesion: 0.19
Nodes (8): git(), letzte_je_tag(), main(), bewerten(), gruppe(), main(), schnappschuss(), trefferquote()

### Community 1 - "json"
Cohesion: 0.22
Nodes (8): abfragen(), firma(), fx_tabelle(), main(), hat_kurs(), lies(), main(), yahoo()

### Community 2 - "fetch.py"
Cohesion: 0.24
Nodes (9): basis(), dividende_anteil(), fcf_aus_cashflow(), fcf_zeile(), grunddaten(), jetzt(), kurse_und_trends(), main() (+1 more)

### Community 3 - "main"
Cohesion: 0.15
Nodes (9): boersentage_bis(), feinwertung(), fx_von(), kuerzel_verdacht(), lade(), main(), kurs_von(), lade_daten() (+1 more)

### Community 4 - "bewertung.py"
Cohesion: 0.23
Nodes (7): bewerte(), branche(), eur_von(), hype(), kurzname(), r2(), rf()

### Community 5 - "texte"
Cohesion: 0.24
Nodes (7): datum_de(), de(), geld(), kurs_text(), liste_text(), pz(), texte()

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `schnappschuss.py`, `json`, `fetch.py`, `bewertung.py`, `texte`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `bewerte()` connect `bewertung.py` to `main`, `texte`, `name_wahl`, `dcf_wert`, `nachricht`, `schaetz_faktor`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `name_wahl()` connect `name_wahl` to `json`, `bewertung.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._