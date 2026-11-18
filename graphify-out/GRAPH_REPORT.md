# Graph Report - aktien-daten  (2026-11-18)

## Corpus Check
- 7 files · ~11,823 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 123 nodes · 264 edges · 11 communities (8 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9c24892d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schnappschuss.py
- universum.py
- fetch.py
- main
- bewerte
- bewertung.py
- json
- dcf_wert
- name_wahl
- datetime
- rf

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
- `bewerte()` --calls--> `rf()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 10 → community 4_
- `bewerte()` --calls--> `name_wahl()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 8 → community 4_
- `name_wahl()` --calls--> `re`  [EXTRACTED]
  bewertung.py →   _Bridges community 8 → community 1_
- `bewerte()` --calls--> `kurzname()`  [EXTRACTED]
  bewertung.py → bewertung.py  _Bridges community 3 → community 4_

## Import Cycles
- None detected.

## Communities (11 total, 3 thin omitted)

### Community 0 - "schnappschuss.py"
Cohesion: 0.19
Nodes (8): git(), letzte_je_tag(), main(), bewerten(), gruppe(), main(), schnappschuss(), trefferquote()

### Community 1 - "universum.py"
Cohesion: 0.27
Nodes (4): hat_kurs(), lies(), main(), yahoo()

### Community 2 - "fetch.py"
Cohesion: 0.17
Nodes (13): basis(), dividende_anteil(), fcf_aus_cashflow(), fcf_zeile(), grunddaten(), grunddaten_sicher(), jetzt(), kurse_und_trends() (+5 more)

### Community 3 - "main"
Cohesion: 0.20
Nodes (8): feinwertung(), fx_von(), kurzname(), lade(), main(), kurs_von(), lade_daten(), pruefe_zeile()

### Community 4 - "bewerte"
Cohesion: 0.17
Nodes (7): bewerte(), branche(), eur_von(), hype(), nachricht(), r2(), schaetz_faktor()

### Community 5 - "bewertung.py"
Cohesion: 0.27
Nodes (7): datum_de(), de(), geld(), kurs_text(), liste_text(), pz(), texte()

### Community 6 - "json"
Cohesion: 0.23
Nodes (7): abfragen(), firma(), fx_tabelle(), heimat(), laender(), main(), zweitlisting()

### Community 9 - "datetime"
Cohesion: 0.29
Nodes (3): boersentage_bis(), kuerzel_verdacht(), datenstand_datum()

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `schnappschuss.py`, `fetch.py`, `bewerte`, `bewertung.py`, `json`, `datetime`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `bewerte()` connect `bewerte` to `main`, `bewertung.py`, `dcf_wert`, `name_wahl`, `rf`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `name_wahl()` connect `name_wahl` to `universum.py`, `bewerte`, `bewertung.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._