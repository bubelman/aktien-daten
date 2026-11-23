# Notizen zum Projekt „Aktien-Liste“ (für Claude)

Diese Datei fasst zusammen, was Levin im Chat gewünscht und entschieden hat. Jede geplante Aufgabe
(auch die Nachtschicht) liest sie zuerst. Neue Entscheidungen hier unten im Protokoll ergänzen.
Ältere Einträge (Protokoll vor dem 20.11., alte Gegenprüfungen, alte Chef-Pläne, erledigte Teile von Aufträgen): NOTIZEN_ARCHIV.md (nur bei Bedarf lesen).

## TOKEN SPAREN – gilt für ALLE Aufgaben (Levin, 15.11.2026)
Levin: „sehr tokensparend, dass wir immer noch gründlich und gut machen, aber nicht so viele Tokens, dass wenn
einer keine Arbeit hat, er sich abschaltet“. Darum:
1. **Erst kurz schauen, ob es Arbeit gibt.** Wenn nicht: sofort aufhören, nur eine Zeile („Aufpasser: alles ok“,
   „Scout: nichts Neues“, „News: keine neuen Nachrichten“). Keine Agenten, kein Bericht an Levin.
2. **Agenten nur für echte Arbeit.** Kein Agent auf Vorrat, keine Rolle „nur zur Sicherheit“. Jeder Agent bekommt
   eine kleine, klare Aufgabe und hört sofort auf, wenn er fertig ist oder nichts findet („nichts gefunden“ reicht).
   Lieber 2 gute Agenten als 10 halbe.
3. **Große Dateien nicht in den Kopf laden.** alle.json, aktien.json, bericht.json usw. mit Python auswerten und nur
   die Ergebnisse ansehen. Nichts doppelt lesen, was schon im Repository liegt.
4. **Kurz schreiben.** Berichte, Commits und Agent-Antworten knapp.
5. **Gründlich bleibt Pflicht:** Tests, Gegenprüfung und Quellen nie weglassen. Gespart wird bei Leerlauf, nicht
   bei der Qualität.

## Code-Karte (graphify, seit 17.11.2026)
graphify-out/GRAPH_REPORT.md zeigt, wie das Programm aufgebaut ist (Funktionen, wer ruft wen, Gruppen). Wird bei jeder
Code-Änderung automatisch neu gebaut (graph.yml, ohne KI). **Token sparen:** Bevor eine Aufgabe große Dateien wie
bewertung.py liest, erst GRAPH_REPORT.md ansehen; für Details `pip install graphifyy --break-system-packages`, dann
`graphify explain "bewerte"` oder `graphify path "main" "dcf_wert"` (liest graphify-out/graph.json) und danach nur die
nötigen Stellen der Datei lesen. Interaktive Karte: graphify-out/graph.html.

## Wer und was
- Levin (Leipzig), Einsteiger an der Börse. Will einen „Wall-Street-Computer“: Aktien gründlich und so
  zuverlässig wie möglich bewerten, automatisch, mit kostenlosen Quellen. „Ich möchte das Beste, was geht.“
- Dashboard „Aktien-Liste“: https://claude.ai/artifact/A5Tm8Qr9ZCixo8Cg62Kf6h (Artifact vom Typ Dashboard).
  Reiter: „Meine Aktien“ (Levins Auswahl in `config/meine`), „Alle Aktien“ (alle bewerteten, Datensatz `alle`,
  mit Suche, Filtern und „NEU“-Markierung für 7 Tage) und „So wird gerechnet“.
- Repository: bubelman/aktien-daten (öffentlich). Daten: `data/aktien.json`, Programm: `bewertung.py`,
  Abruf: `fetch.py`, Aktien: `tickers.txt`.

## Levins Regeln für Antworten (immer einhalten)
- Deutsch, kurze einfache Sätze, nicht nach KI klingend. Ein nächster Schritt nach dem anderen.
- Aufgaben komplett in einem Durchgang erledigen, nicht nach jedem Schritt nachfragen.
- Beträge in Euro. Keine Kauf- oder Verkaufsempfehlung, nie sagen, eine Aktie sei sicher.
  Den Satz „Das ist keine Anlageberatung.“ NICHT mehr schreiben – weder im Chat noch in automatischen Berichten
  (Levin, 18.11.2026: „du musst das nicht immer schreiben“, für Berichte: „ja kannst du machen“).
- **Nicht halluzinieren** („ist wichtig“): nur Zahlen aus dem Programm oder aus Quellen mit Link.
  Wichtige Zahlen mit einer zweiten Quelle gegenprüfen; Abweichungen offen sagen.
- Ehrlich über Grenzen sein (inoffizielle Daten, Schätzungen sind Meinungen, Regeln nicht über Jahre getestet).
- Nie echte Käufe/Verkäufe ausführen; nur Spielgeld-Simulationen.
- **Keine Plätze (Rang) zeigen oder nennen** (Levin, 14.11.2026). Stattdessen Punkte und Feinwert.
  Intern sortiert das Programm weiter nach Punkten und Feinwert.

## Wie gerechnet wird (Kurzfassung, Details in bewertung.py)
- Rund 1700 Aktien: S&P 500 und 400, große und mittlere Index-Aktien aus Europa (Deutschland, London,
  Frankreich, Holland, Spanien, Italien, Schweiz, Skandinavien, Belgien), Favoriten von Banken. Währungen: USD, EUR, GBp/GBP, CHF, DKK, SEK, NOK (Kurse über `fx_eur` in aktien.json).
- Punkte (max. 10): PEG, Kursziel-Abstand, ROE, freier Cashflow, Nettoschulden, Analystenzahl,
  Trend lang (SMA200 + 6 Monate), Trend kurz (SMA50 + 1 Monat), Revisionen; Zykliker −2;
  Nachrichten aus data/news.json (positiv +1, negativ −1, sehr negativ −2; 7 Tage gültig, nur mit Quelle).
- Platz: Punkte, bei Gleichstand Feinwert 0–100 (Rang jeder Kennzahl unter allen).
- Faire Spanne aus drei Wegen: Gewinn × faires KGV, Cashflow-DCF (9 % Zins, 2,5 % Endwachstum, halbes
  Gewinnwachstum max. 15 %), Kursziel-Median. Mitte = mittlerer Wert; Spanne von halbem Weg zum unteren bis
  halbem Weg zum oberen Wert (Levin fand die volle Spanne zu groß).
- Top-Bedingungen: Abstand > 15 %, langer Trend nicht fallend, kein Zykliker.
- Währung der Gewinnschätzungen wird je Aktie über forwardEps erkannt (Fehler bei SAP & Co. am 01.11. behoben).

## Abläufe
- GitHub: `kurse-schleife.yml` – ein Lauf bleibt bis 5,5 h aktiv, holt stündlich um :17 die Kurse (am ersten
  Lauf des Tages auch die Grunddaten) und startet am Ende selbst den nächsten (Mo–Fr bis 21 Uhr UTC). Grund:
  GitHub ließ geplante Läufe massiv aus (nur 2–3 Kurs-Abrufe am Tag). Starthilfen 5:11–18:11 UTC.
- Geplante Aufgabe „Meine Aktien aktualisieren“: Börsentage 7:33, 13:33, 21:33 (Berlin; seit 17.11. nur noch 3-mal, Levin).
  Kurs-Alarm ab ±5 %, Zahlen-Check an Zahlentagen, Wochenbericht montags.
- Screener (GitHub, ohne KI): jeden Abend 22:47 bis 150 neue Aktien, siehe Protokoll 16.11.
- Nachtschicht: jeden Tag 21:41 und 3:41 (Berlin), prüft alles und verbessert. Der Lauf 0:41 ist auf Levins Wunsch
  wieder gestrichen (15.11.2026, 19:31). Große Aufgaben machen die Läufe 21:41 und 3:41; was nicht fertig wird, macht
  der nächste Lauf weiter. Steht in der Aufgabe noch etwas von 0:41, gilt das nicht mehr.
  Ausnahme (Levin, 15.11.2026: „außer es ist irgendwas richtig Wichtiges, so wie NVIDIA-Zahlen oder andere aus meinen
  Aktien“): Hat eine von Levins Aktien am Vorabend Zahlen gemeldet (US-Zahlen kommen meist ca. 22 Uhr), macht der
  Lauf 3:41 einen gründlichen Zahlen-Check: Umsatz und Gewinn gegen Erwartung, Ausblick, erste Reaktion, mit Quellen;
  danach bewertung.py und kurzer Bericht an Levin. Dafür gilt der Sparmodus nicht (bis 3 Agenten). Termine: config/zahlencheck
  und Quartalstermine (z. B. NVIDIA Di 17.11.2026 abends → Check Mi 18.11. 3:41).
- Aktien-Scout: Börsentage 11:48 (Berlin; seit 17.11. nur noch 1-mal, Levin), siehe Abschnitt „Aktien-Scout“.
- Aufpasser (seit 15.11.): täglich 9:13 und 23:13 (Berlin; seit 17.11. nur noch 2-mal, Levin). Prüft Aufgaben, GitHub-Läufe, Daten, Dashboard;
  behebt Kleines selbst (Workflows neu starten, Dashboard-Daten neu schreiben), Größeres als Auftrag für die Nachtschicht.
  Seit 15.11. auch Token-Wächter: prüft Laufzeiten der Aufgaben, setzt/löscht den Sparmodus nach Levins Zahl,
  schreibt bei Leerlauf-Arbeit einen Auftrag „Token sparen bei …“ für die Nachtschicht.
- Chef (seit 15.11.): seit 17.11. nur noch mittwochs und sonntags 20:27 (Levin, Tokens sparen), sonntags mit großem Bericht.
  Schaut auf das ganze System („Firma“), plant die nächsten 1–2 Wochen, schreibt
  Aufträge für die Nachtschicht (Abschnitt „Chef – Plan“), schickt Levin den Chef-Bericht; Regeländerungen, mehr
  Kosten und neue Aufgaben nur nach Levins Ja.
- News-Agenten: Börsentage 6:51 und 20:51 (seit 17.11. schlank, Levin: „nur immer die besten Aktien“): Levins Aktien +
  die 15 mit den meisten Punkten, höchstens 2 Agenten, Nachprüfung selbst, data/news.json pushen.

## Aktien-Scout (Levin, 14.11.2026: „einen, der die ganze Zeit nach neuen guten Aktien sucht“)
- Liest `alle.json` (alle bewerteten Aktien, schreibt bewertung.py seit 14.11.) und meldet bis zu 5 Kandidaten:
  Top-Bedingungen erfüllt, mindestens 5 Punkte, nicht in „Meine Aktien“, höchstens 2 je Sektor.
- Schon Gemeldetes (ArtifactData `config/scout`, Feld "gemeldet") erst nach 30 Tagen oder +2 Punkten wieder.
- Kurzer Faktencheck je Kandidat (Übernahme, Skandal, Gewinnwarnung → nicht melden).
- Im Lauf 11:48 zusätzlich: Hochstufungen und Favoritenlisten großer Banken der letzten 7 Tage suchen; bis zu
  3 neue Aktien in tickers.txt aufnehmen (Börsenwert > 2 Mrd. €, mit Gewinn, Kürzel geprüft), Grund in
  `config/scout` "aufgenommen" und hier im Protokoll.
- Nimmt nie selbst Aktien in „Meine Aktien“ auf; nur wenn Levin es sagt.
- Hype (Levin, 14.11.2026: „auch nach denen mit dem besten Hype“): jeder Lauf sucht bis zu 10 Aktien mit viel
  Aufmerksamkeit (Trend-Listen, Reddit/Stocktwits, starke Kursbewegung) → data/hype.json (3 Tage gültig, mit
  Quelle). Gibt KEINE Punkte, nur 🔥 im Dashboard (Filter „nur Hype“). Meldung immer mit „Hype gibt keine Punkte
  und kann schnell kippen.“
- Mehrere Agenten: Levin möchte, dass für größere Aufgaben mehrere Agenten parallel arbeiten (14.11.2026),
  z. B. Zahlen, Nachrichten und unabhängige Gegenprüfung getrennt. Ihre Funde immer selbst nachprüfen.

## Entscheidungen (Protokoll)
- 23.11.2026 (Nachtschicht 21:41, 1 Recherche-Agent, 1 Prüf-Agent): **A12 erledigt** – Splits automatisch: fetch.py speichert split_datum/split_faktor
  aus Yahoos info (lastSplitFactor/lastSplitDate, kein Zusatz-Abruf, nur letzte 60 Tage); bewertung.py lässt die Aktie aus, solange Kursziel/Kurs
  > 0,75 × Faktor (Zusammenlegung: < Wurzel(Faktor)), SPLIT_NOCH_ALT bleibt als Handliste. Neu in bericht.json "split_verdacht" (Kursziel > 3 × Kurs ohne
  bekannten Split, nur Hinweis): heute 22, davon 8 bewertet. Recherche-Agent: keine nicht angepassten Splits, meist echte Kurseinbrüche mit veralteten
  Kurszielen (0881.HK, NUS, 6809.HK, 0148.HK, 1377.HK); unklar 3986.HK, 2476.HK, 5706.T (Split 1:10 im Sept., Kurs bei Yahoo 1120 vs. 2602 JPY am 14.10.
  bei marketscreener, forwardEps 601 passt nicht zu +1y 176 → beobachten). Test: mit echten Daten alle/liste/meine gleich, "pruefung" leer, 3192 bewertet;
  Ersatzdaten (285A.T Faktor 3, SNDK Faktor 8) siehe Commit. Felder kommen mit dem nächsten Grunddaten-Lauf (Di früh). **A7 erledigt**: Mi 18.11. 4:35 UTC und
  Mo 23.11. 4:33 UTC Kurse vor 6:30. **TCBI → TXCP** (Wechsel an die Texas Stock Exchange; finviz.com/news/419237). Levins Aktien: ENR.DE 7, NVDA 6, AVGO 5,
  SAP 4, IFX.DE 4 Punkte, ANT nicht bewertet (KGV 2352).
- 23.11.2026 (Nachtschicht 3:41, Mo, ohne Agenten): nur Prüfung, keine Code-Änderung. bewertung.py Fehlercode 0, "pruefung" leer, kuerzel_verdacht leer,
  3056 bewertet, 444 ausgefallen (186 ohne Gewinn, 110 ohne Kursziel, 37 doppelt). Daten: 3501 Aktien mit Grunddaten (So 22.11. 4:34 UTC), alle mit Kurs vom 20.11.
  (Wochenende). Screener Mo 2:05 UTC +150 Kürzel (3651 in tickers.txt); Grunddaten-Lauf dafür läuft seit 2:05 UTC. Levins Aktien: ENR.DE 6, NVDA 5, AVGO 5, SAP 5,
  IFX.DE 4 Punkte, ANT nicht bewertet (KGV 2453). Keine Zahlen am Vorabend. runs fehlt weiter → A5.4-Test offen. A7-Test (Kurse vor 6:30 UTC) prüft Lauf Di 3:41.
- 22.11.2026 (Nachtschicht 21:41, 1 Prüf-Agent): **A11 erledigt** – NOTIZEN.md entschlackt: Protokoll vor 20.11., alte Gegenprüfungen,
  alte Chef-Pläne, ältere Teile von A5/A7, A11-Text und überholte Zeilen (Team-/Token-Regeln 15.11., Wochenlimit-Zahl, SDAX offen) wörtlich nach
  NOTIZEN_ARCHIV.md. 503 → 294 Zeilen, 55 → 30 KB (−46 %). Ziel „unter 230“ nicht erreicht: allein die Teile, die laut A11 bleiben
  (Regeln, Aufträge, Protokoll ab 20.11.), sind ~280 Zeilen. Zusammengefasst: A5 (3 Absätze → 1), Team-/Token-Regeln 15.11. (→ 1 Hinweis). Prüfung: Fehlercode 0, "pruefung" leer,
  3057 bewertet, 444 ausgefallen, kuerzel_verdacht leer. Kurse: 3501 mit Stand 20.11. **PCRX entfernt und gesperrt** (Übernahme durch Viatris abgeschlossen, pulse2.com; Kurs nur bis 18.11.). Levins Aktien: ENR.DE 6,
  NVDA 5, AVGO 5, SAP 5, IFX.DE 4 Punkte, ANT nicht bewertet.
- 22.11.2026 (Nachtschicht 3:41, So, ohne Agenten): nur Prüfung, keine Code-Änderung. bewertung.py Fehlercode 0, "pruefung" leer, kuerzel_verdacht leer,
  2932 bewertet (wie Sa). Daten: 3352 Aktien mit Grunddaten (Sa 21.11. 5:29 UTC), 3333 mit Kurs vom 20.11., 19 mit 19.11./18.11. (u. a. TCBI, ACT.DE, PCRX,
  REC.MI; Wochenende, unter 3 Börsentagen). Screener So 1:43 UTC +150 Kürzel (3502 in tickers.txt); Grunddaten-Lauf dafür läuft noch (seit 1:43 UTC).
  universum.yml gestartet (Sonntag). Levins Aktien wie Sa (ENR.DE 6, NVDA 5, AVGO 5, SAP 5, IFX.DE 4, ANT nicht bewertet). Keine Zahlen am Vorabend.
  runs unverändert (20.11. 18:15, stray_write #alle-sektor vor dem Fix) → A5.4-Test weiter offen. IFX.DE: zweite Quelle für Kursziel-Durchschnitt wieder nicht gefunden.
- 21.11.2026 (Nachtschicht 21:41, 1 Prüf-Agent, 1 Hilfs-Agent zum Lesen von Webseiten): **Fehler behoben: falsche „doppelt“-Treffer** (Commit ab0feed).
  DOM.L (Domino's Pizza Group, UK) fiel als „gleiche Firma wie DPZ“ raus, FBNC (First Bancorp, North Carolina) als „wie FBP“ (First BanCorp.,
  Puerto Rico). firma() streicht „group“ nicht mehr; zwei US-Kürzel gelten nur bei ähnlichem Kürzel als gleiche Firma (GOOG/GOOGL, FOX/FOXA,
  LLYVA/LLYVK). Test: 2930 → 2932 bewertet, keine Punkte/fairen Mitten geändert, Feinwert max ±0,1, "pruefung" leer; Prüf-Agent: keine Funde.
  Daten: Grunddaten Sa 21.11. 5:29 UTC, 3352 Aktien, 3333 mit Kurs vom 20.11. (Rest 19.11., PCRX 18.11.); 150 Screener-Aktien vom 21.11. alle mit
  Daten, 127 bewertet. kuerzel_verdacht leer, 421 ausgefallen (175 ohne Gewinn, 99 ohne Kursziel). **SKHY KGV 2,5 kein Umrechnungsfehler**: 1 ADR = 1/10
  Aktie (morningstar.com/en-gb/stocks/sk-hynix-adrs-begin-trading-under-new-ticker), Börsenwert und Gewinn je ADR passen zusammen; niedriges KGV wie
  MU/SNDK (Speicher-Boom, Schätzung 2027). Levins Aktien: ENR.DE 6, NVDA 5, AVGO 5, SAP 5, IFX.DE 4 Punkte, ANT nicht bewertet (KGV 2453).
  runs unverändert seit 20.11. 18:15 (Seite seitdem nicht geöffnet) → A5.4-Test weiter offen. FMP gibt für Nicht-US-Aktien nichts (Tarif).
- 21.11.2026 (Nachtschicht 3:41, ohne Agenten, 1 Hilfs-Agent zum Lesen einer Webseite): **BKH entfernt und gesperrt** (Black Hills, seit der Fusion
  16.11. Bright Horizon Energy = HZN; BKH-Kurs nur bis 19.11.; stockanalysis.com/stocks/hzn/ führt Black Hills unter HZN). HZN fiel bisher als
  „doppelt (gleiche Firma wie BKH)“ raus und wurde mit veralteten BKH-Zahlen gezeigt. Test: nur BKH → HZN getauscht (1 Punkt, Feinwert 39,1),
  sonst keine Punkte/fairen Mitten geändert, Fehlercode 0, "pruefung" leer, 2803 bewertet, 398 ausgefallen (167 ohne Gewinn, 92 ohne Kursziel).
  **SNDK kein Datenfehler**: Aktiensplit 8:1 am 20.11. (stock3.com/news/sandisk-aktiensplit-81-das-aendert-sich-am-20-november-im-depot-17399975);
  Yahoo hat Kurs, Kursziel (2050 → 256,25 $) und Schätzung +1y schon angepasst, nur eps_forward/Börsenwert noch alt → KGV 2,2 war auch vorher ~2,6.
  Daten: Kurse Fr 20.11. 21:19 UTC (US-Schluss da), 3197 von 3203 mit Stand 20.11.; BBBY, TCBI, REC.MI, ACT.DE, BKH 19.11., PCRX 18.11. (beobachten).
  Levins Aktien (zum 19.11.): AVGO 7 → 5 Punkte (Kurs −12 %), ENR.DE 6, NVDA 5, SAP 5, IFX.DE 4, ANT nicht bewertet. Keine Zahlen am Vorabend; nächste: AVGO 09.12.
- 20.11.2026 (Nachtschicht 21:41, 2 kleine Hilfs-Agenten zum Lesen von Webseiten): **A5.4 Rest behoben**: runs meldete nach dem Öffnen
  (20.11. 18:15 UTC) stray_write jetzt bei #alle-sektor (Region ist weg). Branchen-Auswahl steht fest im HTML (17 Branchen aus bewertung.py),
  Füllen in dash.onData gestrichen. Lokal getestet (1440/390 px, 18 Optionen, Filter Halbleiter 75 Zeilen = alle.json, keine Konsolenfehler).
  Seite Version 31, Kopie in dashboard/index.html. **CDI.PA gesperrt** (Christian Dior SE, Holding von LVMH; Yahoo ohne Börsenwert/Schätzungen).
  Prüfung: Fehlercode 0, "pruefung" leer, 2803 bewertet, 400 ausgefallen (167 ohne Gewinn, 93 ohne Kursziel), liste/alle bis auf "stand" gleich.
  Daten: 3204 Aktien, alle mit Grunddaten, 3198 mit Kurs vom 20.11.; HZN, UMI.BR, PTRN mit Daten. **Ausverkauf Chips 20.11.** (Stand 20:19 UTC):
  NVDA −12,8 %, AVGO −12,3 %, ANT −9,7 % (zum Vortag; Ursache laut finance.yahoo.com: Chip-Sektor nach dem Anthropic-Börsengang, Sorge um
  KI-Finanzierung, Abgang Jensen Huang). GILD „Gewinn nicht positiv“: Yahoo-Schätzung 2026 −0,99 $ (2027 +10,15 $) – nicht weiter geprüft.
- 20.11.2026 (Nachtschicht 3:41, ohne Agenten): **NWE und ITGR entfernt** (seit 16.11. ohne Kurs): NorthWestern ist mit Black Hills zu
  Bright Horizon Energy verschmolzen (16.11., wowt.com), Integer von KKR übernommen (biopharmawatch.com). Nachfolger **HZN** (Bright Horizon
  Energy, laut upstox.com/us-stocks/hzn-share-price/ und panabee.com) aufgenommen – nach dem Grunddaten-Abruf prüfen, ob Yahoo Daten liefert.
  Prüfung: Fehlercode 0, "pruefung" leer, kuerzel_verdacht leer, 2691 bewertet, 362 ausgefallen (147 ohne Gewinn, 88 ohne Kursziel).
  Daten: US-Schluss 19.11. da (3048 von 3054 mit Stand 19.11.; BBBY, TCBI, ACT.DE, PCRX Stand 18.11. – beobachten). Commit „Daten (Morgenlauf)
  22:19 UTC“ war nur der Grunddaten-Lauf nach dem Push von tickers.txt (Grunddaten schon da → nur Kurse), kein Fehler. Levins Aktien: keine Zahlen
  am Vorabend, nächste: AVGO 09.12. ANT (Börsengang 19.11., Schluss 97,17 $) noch nicht bewertet (Gewinnschätzung 2027 −0,12 $).
- 20.11.2026 (Scout 11:48): 1 neue Aktie: UMI.BR (Umicore, Hochstufung auf Kaufen durch Kepler Cheuvreux 19.11., Börsenwert ca. 4,9 Mrd. €,
  mit Gewinn; dailytradealert.com, investing.com). Hype-Liste: 8 Aktien (neu INTU, ROST; erneuert ANT, APP, AMD). KTB ausgelassen (Lee-Verkauf, Zahlen im Umbruch).
- 23.11.2026 (Scout 11:48): 1 neue Aktie: AVAH (Aveanna Healthcare, Truist stuft am 23.11. auf Kaufen hoch, Ziel 15 $; Börsenwert ca. 2,2 Mrd. €;
  investing.com, stockanalysis.com; Gewinn nicht mit Quelle bestätigt, Programm prüft). Hype-Liste: 9 Aktien (neu NVDA, GPN, INSM, GAP; erneuert ANT).

## Gegenprüfung mit dem Internet (Nachtschicht, reihum)
- ENR.DE: 15.11.2026 – Kurs 131,28 €, Kursziel-Durchschnitt 192,21 € (28 Analysten), Gewinn GJ 2028 8,48 € – alles gleich wie
  marketscreener. Achtung: Geschäftsjahr endet im September, eps_forward = GJ 2028 (in ~2 Jahren).
- AVGO: 19.11.2026 – Kursziel-Durchschnitt Yahoo 528 $ (47 Analysten) / tikr.com 533 $ (https://www.tikr.com/blog/is-rothschild-co-redburn-wrong-to-give-up-on-broadcom-wall-street-still-sees-533) → passt (−1 %).
- NVDA: 20.11.2026 – zweite Quelle FMP (Financial Modeling Prep): Gewinn FY2028 16,59 $ / Yahoo 16,61 $ (passt). Kursziel-Median FMP 255 $ /
  Yahoo 240 $ (−6 %), Mittel FMP 275,86 $ / Yahoo 246,67 $ (−11 %): Yahoo hat wohl schon gesenkte Ziele nach dem Kursrutsch, FMP ältere.
- SAP: 21.11.2026 – Kurs 198,93 $ (Schluss 20.11.) passt genau zu marketscreener.com (ae.marketscreener.com/quote/stock/SAP-SE-14320/consensus/).
  Kursziel-Durchschnitt Yahoo 284,50 $ (12 Analysten, ADR) = 259 € / marketscreener 243,54 € (29 Analysten) → +6 %, unter 10 %. Gewinnschätzung dort nicht lesbar (Login).
- IFX.DE: 21.11.2026 – Yahoo Kurs 45,44 € (20.11.), Kursziel-Mittel 80,79 € (24 Analysten), Gewinn +1y 3,88 €. Zweite Quelle für den
  Durchschnitt nicht gefunden (FMP nur US; Suche brachte nur Einzelziele, z. B. Jefferies 74 €). → noch offen.
- Als Nächstes: IFX.DE (zweite Quelle), dann ENR.DE.

## Offene Aufträge von Levin (die Nachtschicht erledigt sie zuerst, danach ins Protokoll verschieben)

### A6 (15.11.2026, Nachtschicht): Aufgaben-Texte ändern – braucht Levins Freigabe im Chat
Die geplante Nachtschicht darf update_trigger nicht ausführen („Permission denied … Scheduled Task Write“). Darum offen:
1. „Meine Aktien aktualisieren“ (trig_01CkcqBfDNXG1orD3A9WFXB8), ein Aufruf, ganzer Text:
   - „rund 1.700“ → „rund 2.400“ (zwei Stellen); Reiter „So wird gerechnet (mit Trefferquote)“ nennen.
   - Erlaubte Datensätze: liste, aenderungen, meine, alle, trefferquote.
   - Schritt 1: auch datasets/trefferquote lesen (version).
   - Schritt 4: ist "stand" in data/trefferquote.json neuer als updated.at von datasets/trefferquote → data/trefferquote_zeilen.json als
     trefferquote.json hochladen; nie leere Liste; sonst nicht anfassen. (A3.3)
   - Wochenbericht: eine Zeile zur Trefferquote mit Hinweis „wenige Wochen sagen wenig; vor dem 15.11. rückwirkend“. (A3.4)
2. „Nachtschicht Aktien“ (trig_01S5nJRTnMwn8cKRnQR1DUfy): „DREI LÄUFE PRO NACHT“ → zwei Läufe (21:41 alles inkl. großer Aufgaben;
   3:41 alles, dazu US-Schluss, Termine, Zahlen-Check nach Zahlen von Levins Aktien); alle anderen Erwähnungen von 0:41 streichen. (A5.2)
Bis dahin: Trefferquote im Dashboard nur so aktuell wie der letzte Upload von Hand (15.11. abends).
Wer es mit Levin im Chat macht: danach diesen Auftrag löschen.

### A3 (Rest): Trefferquote
- A3.2 langer Rückblick-Test mit Kursdaten (yfinance im GitHub-Workflow) – jetzt genau beschrieben als A13 (Chef, 22.11.).
- Hinweis: Yahoo ist aus der Cloud-Umgebung der Aufgaben gesperrt (403); yfinance geht nur im GitHub-Workflow.

### A5 (Rest): stray_write-Test
- A5.4 behoben (Länder- und Branchen-Auswahl fest im HTML, Seite Version 31). Offen nur der Test: nach dem nächsten Öffnen der Seite
  data/users/me "runs" ohne stray_write? Dann A5 löschen. A5.2/A5.3 siehe A6.

### A13 (22.11.2026, vom Chef): langer Rückblick-Test der Trend-Punkte (= A3.2, seit 19.11. offen) – ab Di 24.11., 2 Nächte
Grund: Trefferquote bisher gegen die Punkte (Stand 20.11.: 7–10 Punkte −13,9 % in 1 Woche, n=7; unter 3 Punkte −4,9 %; IC Punkte
5 Tage −0,078). 3 Wochen sagen fast nichts. Nur die Kurs-Regeln lassen sich ehrlich über Jahre testen (alte Analystenschätzungen gibt es nicht).
1. Neues Skript rueckblick_trend.py + Workflow rueckblick.yml (nur von Hand starten, workflow_dispatch): yfinance-Kurse 3 Jahre für eine
   feste Stichprobe (z. B. alle US- und .DE-Aktien aus tickers.txt, höchstens 800, Abrufe gebündelt mit yf.download).
2. Je Monatsende: Trend lang (SMA200 + 6 Monate) und Trend kurz (SMA50 + 1 Monat) genau wie bewertung.py (Funktion dort lesen,
   nicht neu erfinden) → Rendite der nächsten 1 und 3 Monate je Gruppe; IC; Vergleich mit allen. Ergebnis data/rueckblick_trend.json.
3. Ehrliche Grenzen ins Ergebnis schreiben (Überlebende-Verzerrung: nur heutige Aktien; keine Kosten; Zeitraum).
4. Reiter „So wird gerechnet“: nur wenn einfach, eine kleine Tabelle; sonst nur NOTIZEN.md und Bericht.
Keine Regeländerung. Ergebnis an den Chef (Abschnitt Chef-Plan), der Levin ggf. einen Vorschlag macht.
Nebenbei (klein): schnappschuss.py speichert zusätzlich Piotroski und Schätzungs-Trend je Aktie in data/verlauf (Idee vom 18.11.),
damit vorhersagekraft.py sie später messen kann.

### A14 (22.11.2026, vom Chef): Vorschlag „Wachstum unplausibel“ vorbereiten – ab Do 26.11., nur Zweig
Grund: 444 Aktien fallen heute raus, davon rund 76 wegen „Wachstum … unplausibel“ (z. B. MRK +222 %, PANW −54 %) – oft Sonderkosten
im Vorjahr. Das ist eine Bewertungsregel → nur auf Zweig vorschlag/wachstum vorbereiten, nicht auf main.
1. Liste aller Fälle mit Gewinn letztes Jahr, Schätzung +1y, +2y; wie viele hätten mit Wachstum aus +1y→+2y (statt Ist→+1y) ein plausibles
   Wachstum? 2. Variante auf dem Zweig, Vergleich: wie viele mehr bewertet, welche Punkte, Levins Aktien unverändert?
3. Ergebnis in 3 Sätzen im Chef-Plan; Levin entscheidet über den Chef.

## Chef – Plan
### 22.11.2026 (So) – Plan für die nächsten 2 Wochen (Budget Nachtschicht 7 % je Nacht, 21:41 je 1 Auftrag)
Lage: 3502 Aktien im Programm (alle mit Kurs), 3057 bewertet (Testlauf 22.11. 20:35 mit den 150 neuen von So), Fehlercode 0, pruefung leer,
kuerzel_verdacht leer. Woche: +~1050 Kürzel (2454 am 16.11. → 3502), Screener hat noch 1685 Kandidaten (~11 Abende). Japan schon 286 .T
(Nikkei-Lücke durch Screener weitgehend gefüllt → keine eigene Recherche mehr nötig). Fehler gefunden und behoben: JBS, Kioxia, Nordea-Art,
DOM.L/FBNC „doppelt“, BKH/NWE/ITGR (Fusionen). Dashboard: Daten Fr 20.11. 21:36 (Wochenende ok); Datensatz trefferquote seit 18.11. nicht neu
(A6 fehlt). data/users/me "runs" für den Chef nicht vorhanden → A5.4-Test nur möglich, wenn Levins Sitzung es schreibt.
Aufgaben: alle letzten Läufe SUCCEEDED. Thanksgiving Do 26.11.: US-Börse zu, Fr 27.11. kurz → fehlende US-Kurse dann kein Fehler.
1. A11 Notizen entschlacken (So) – Erfolg: < 230 Zeilen, weniger Tokens je Lauf.
2. A12 Splits automatisch (Mo) – Erfolg: kein falscher Split-Treffer mehr von Hand.
3. A13 Rückblick-Test Trend (Di–Mi) – Erfolg: data/rueckblick_trend.json mit 3 Jahren.
4. A14 Vorschlag Wachstum (Do–Fr, Zweig) – Erfolg: Zahl zusätzlich bewerteter Aktien, Entscheidung für Levin.
5. Tests: A7 (Mo 23.11. Kurse vor 6:30 UTC?) – Lauf 3:41 Di prüft.
An Levin gefragt: (1) A6 freigeben (Aufgaben-Texte), (2) ~65 Londoner Fonds ohne Kursziel sperren.
Stand Chef-Aufträge 18.11.: A10 Teil 3 erledigt (18.11.), A5.4 behoben (Test offen), Morgenabruf 19.11. geprüft (ok). A3.2 nicht begonnen → jetzt A13.


## Bekannte Grenzen und offene Ideen
- Yahoo-Schätzungen sind oft „bereinigt“ (ohne Sonderkosten); andere Quellen nennen niedrigere Gewinne
  (z. B. Infineon). Analysten können optimistischer sein als die Firma (z. B. Siemens Energy 2027).
- Sonderkosten verzerren manchmal das Wachstum → Aktie fällt raus („Wachstum unplausibel“, z. B. Merck).
- Firmen ohne Gewinn (Quantencomputer) sind nicht bewertbar.
- Sehr hohe Abstände (z. B. TUI +342 %, bpost, CNX, Jazz): wenn Gewinn × faires KGV und DCF beide weit über dem
  Kursziel liegen, wird die Mitte sehr hoch. Oft steckt ein Sondereffekt im freien Cashflow (Kundenanzahlungen bei
  Reise- und Postfirmen). Idee für die Nachtschicht: Vorschlag mit Rückblick-Test (z. B. Mitte höchstens doppelt so
  hoch wie das Kursziel oder Cashflow-Rendite über 15 % als Sondereffekt behandeln).
- Rund 70 Londoner Investmentfonds (Investment Trusts aus dem FTSE 250, z. B. SMT.L, FCIT.L) haben kein Kursziel und
  werden nie bewertet. Idee: in tickers_gesperrt.txt verschieben (mit Levin klären, ob er sie sehen will).
- ML.PA (Michelin): Yahoo liefert seit dem 14.11. keine Gewinnschätzung und Börsenwert 0 → fällt raus (beobachten).
- Noch „Währung unklar“: SHC.L, ABB.ST, EQT.ST, HEXA-B.ST (forwardEps passt zu keiner Umrechnung, Abweichung 25–60 %).
- Ideen: Rückblick-Test der Trend-Regeln mit Kursdaten; Kurs-Gegenprüfung mit Twelve Data; Hinweis, wenn
  Analystenschätzung deutlich über dem Firmenausblick liegt.

## Regeln für die Nachtschicht
- Darf ohne Rückfrage: Datenfehler und Abstürze beheben, Prüfungen ergänzen, Texte/Erklärungen verbessern,
  neue Aktien aufnehmen (seit 15.11. ohne Obergrenze, Levins Wünsche vom 14./15.11.2026; Regeln in der Aufgabe, Schritt 2b). Vor jedem Push: `bewertung.py` mit aktuellen Daten laufen
  lassen (Fehlercode 0, "pruefung" leer oder erklärt) und mit dem Stand vorher vergleichen.
- Darf NICHT ohne Levins Ja: Punkte-Regeln, Gewichte, faire-Spanne-Methode oder Top-Bedingungen ändern;
  Depots wieder starten; Aktien in „Meine Aktien“ aufnehmen oder entfernen. Solche Ideen nur vorschlagen.
- Jede Änderung hier im Protokoll eintragen. Keine Zahlen erfinden.
- Seit 14.11.2026 (Levins Wunsch): jede Nacht Verbesserungen der Arbeitsweise (mit Test vorher/nachher);
  seit 15.11. („jeden Tag die Sachen verbessern“, „immer so viel machen, wie er findet“): keine feste Obergrenze
  mehr für Verbesserungen und neue Aktien – alles, was sich sauber prüfen lässt; höchstens 2 Regel-Vorschläge je Bericht.
  Regeländerungen (Punkte, Gewichte, faire Spanne, Top-Bedingungen) nur auf Zweig `vorschlag/<name>` mit
  Rückblick-Test vorbereiten und nach Levins Ja übernehmen. „zurück“ von Levin = git revert.
- Seit 15.11.2026 (Levins Ja): die Dashboard-Seite darf jede Nacht verbessert werden (schöner, übersichtlicher,
  vor allem am PC) – immer mit lokalem Test (PC und Handy), keine Funktion entfernen, im Bericht sagen, was neu ist;
  „zurück“ von Levin = vorherige Version von files/index.html wiederherstellen (vorher Kopie im Repository unter
  dashboard/index.html ablegen und mit committen).
- Seit 15.11.2026 (Levin: „noch mehr Agenten, das soll richtig gut sein“, „die Hälfte meiner wöchentlichen Tokens“): Team mit vielen
  Agenten und tiefes Arbeiten – heute durch das BUDGET NACHTSCHICHT unten begrenzt. Weiter gilt: Code- und Seiten-Agenten
  mit eigener Arbeitskopie, nur die Leitung pusht. Voller Wortlaut in NOTIZEN_ARCHIV.md.
- Grenze (Levin, 15.11.2026): alle Aufgaben zusammen höchstens **75 % von Levins Wochenlimit** (neu jeden Mittwoch).
  Den Zähler sieht nur Levin (Einstellungen → Nutzung). Er schreibt die Zahl in den Chat, sie wird hier eingetragen.
  Ab 60 %: Sparmodus wie unten. Ab 75 %: Nachtschicht nur noch Schritt 1 (Prüfen), keine Agenten, bis Mittwoch.
- **BUDGET NACHTSCHICHT (Levin, 18.11.2026: „mach es zu 7 % runter“; vorher 10 %): etwa 7 % von Levins Wochenlimit pro Nacht** (beide Läufe zusammen).
  Gilt vor der Aufgabe und ersetzt dort „Hälfte der Wochen-Tokens“, „noch mehr Agenten“ und „keine feste Obergrenze“.
  Zum Vergleich: die Nacht 15./16.11. (5 Agenten, Aufträge A2, A3, A4, neue Aktien und ETFs) kostete etwa 20 %. Darum:
  • Lauf 21:41 macht die Arbeit: höchstens 2 Agenten, nur der wichtigste Auftrag bzw. 1–2 Verbesserungen, Rest bleibt für
    die nächste Nacht. Ziel: nach etwa 30 Minuten fertig.
  • Lauf 3:41 nur Schritt 1 (Prüfen) ohne Agenten, etwa 15 Minuten. Ausnahme: Zahlen-Check nach Zahlen von Levins
    Aktien (bis 3 Agenten).
  • Ein Prüf-Agent am Schluss statt zwei. Neue Aktien sucht seit 16.11. screener.py automatisch (ohne KI): keine
    Recherche-Agenten mehr, nur prüfen, ob die neuen Kürzel Daten bekommen (sonst in tickers_gesperrt.txt).
  • Levin schickt ab und zu seine Zahl; liegt eine Nacht klar über 7 %, weiter kürzen.
- Höchstens ein Skill pro Nacht (propose_skills, sonst skills/<name>/SKILL.md), nur wenn er wirklich hilft.

## Skills
- (noch keine von der Nachtschicht vorgeschlagen; 14.11.: bewusst keiner, A1 hatte Vorrang)
- 15.11.: keiner (kein Werkzeug propose_skills; für die NVIDIA-Zahlen am 17.11. gibt es schon equity-research:earnings-preview).
