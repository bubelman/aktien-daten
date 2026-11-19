# Notizen zum Projekt „Aktien-Liste“ (für Claude)

Diese Datei fasst zusammen, was Levin im Chat gewünscht und entschieden hat. Jede geplante Aufgabe
(auch die Nachtschicht) liest sie zuerst. Neue Entscheidungen hier unten im Protokoll ergänzen.

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
- 19.11.2026 (Nachtschicht 21:41, 2 kleine Hilfs-Agenten zum Lesen von Webseiten): **Fehler behoben: JBS mit KGV 1,6 statt ~9** (Commit 4b75afe).
  Yahoo nennt Dollar als Berichtswährung, die Jahresschätzungen stehen aber in Real (7,23 statt 1,27 $ für 2027 laut
  stockanalysis.com/stocks/jbs/forecast/, Stand 22.10.). schaetz_faktor prüft jetzt auch bei gleicher Währung gegen forwardEps
  (3- bis 20-fach höher, KGV < 3, mit forwardEps 3–60 → „Währung unklar“). Test: nur JBS fällt raus (2692 → 2691), keine Punkte
  geändert, Feinwert höchstens ±0,1. **PHYS.TO, PSLV.TO gesperrt** (Gold-/Silber-Fonds vom Screener, Commit 71b0f7b). Londoner Fonds
  (TMPL.L, TRY.L, VEIL.L, WWH.L, TFIF.L) bleiben, bis Levin zu Vorschlag (b) antwortet. Prüfung: Fehlercode 0, "pruefung" leer,
  kuerzel_verdacht leer, **Morgenabruf 19.11. vollständig** (3056 Aktien, 3050 mit Kurs vom 19.11., nur 2 ohne Grunddaten),
  2691 bewertet (mit Fix). Alte Kurse: NWE, ITGR (16.11.), BBBY, TCBI, ACT.DE, PCRX (18.11.) – beobachten. ANT: „Gewinn nicht positiv“
  (Schätzung 2027 −0,12 $), wie erwartet. runs zeigt noch stray_write vom 18.11. 16:55 (vor dem Fix, Seite seitdem nicht geöffnet).
- 19.11.2026 17:40 (Chat): Anthropic (ANT, Nasdaq, Börsengang 19.11.2026, Ausgabepreis 83 $) auf Levins Wunsch in tickers.txt und config/meine aufgenommen. Neu an der Börse: wenig Kursverlauf und evtl. noch keine Analystenschätzungen – kann anfangs „nicht bewertet“ sein.
- 18.11.2026 (Nachtschicht 21:41, Budget 7 %, 2 Agenten): **A10 Teil 3 erledigt** (Commit 2db5d80): vorhersagekraft.py misst den
  Information Coefficient (Rangkorrelation Punkte/Feinwert ↔ Kursänderung nach 1 und 5 Börsentagen) und die Rendite je Fünftel, getrennt
  „rückwirkend“ (bis 13.11.) und „echt“ (ab 15.11.); nur Standardbibliothek (schnappschuss.yml installiert keine Pakete), gegen alphalens
  0.5.1/scipy gegengeprüft. Läuft täglich in schnappschuss.py (Fehler brechen nicht ab). Sonntagsdatei 15.11. = Handelstag 13.11.
  Ergebnis Stand 17.11.: rückwirkend Punkte IC −0,033 (1 Tag, 11 Tage) / −0,061 (5 Tage, 8 Tage), Feinwert −0,023 / −0,020; echt: zu wenige
  Tage. Piotroski und Schätzungs-Trend stehen nicht im Verlauf → noch nicht messbar (Idee: in schnappschuss.py mit speichern).
  **A5.4** (Commit c7ac787): stray_write bei #alle-region – Länder-Optionen jetzt fest im HTML. Reiter „So wird gerechnet“: Tabelle
  „Vorhersagekraft“; trefferquote_zeilen.json hat dafür Zeilen mit art=vorhersagekraft. Datensatz „trefferquote“ neu hochgeladen (Version 3,
  Stand 17.11.). Seite Version 30, Kopie in dashboard/index.html. Prüf-Agent: Satz „Das ist keine Anlageberatung.“ stand noch in der Fußzeile
  der Seite → entfernt. Prüfung: Fehlercode 0, "pruefung" leer, 2437 bewertet, liste/alle unverändert. 164 Aktien ohne Grunddaten (v. a. die
  150 neuen vom Screener 18.11., Yahoo-Drosselung) → kuerzel_verdacht zeigt 166 Fälle; kein Kürzelfehler. Lauf 3:41: Morgenabruf 19.11. prüfen.
- 18.11.2026 18:20 (Chat): Satz „Das ist keine Anlageberatung.“ aus allen 6 geplanten Aufgaben gestrichen (Levin: „ja kannst du machen“). Gilt auch für neue Skills.
- 18.11.2026 (Chat): **Datenfehler behoben.** Der Morgenabruf 18.11. 5:29 bekam von Yahoo für ~1.500 Aktien leere Grunddaten
  (wohl gedrosselt, mit den neuen Piotroski-Abrufen) und überschrieb die guten Werte → nur 1.241 statt 2.437 bewertet; „Meine
  Aktien aktualisieren“ hat alle.json um 7:33/13:33 nicht hochgeladen. Repariert: Grunddaten vom Vortag für 1.343 Aktien zurück
  (Commit 9c24892), fetch.py behält bei leeren Antworten die Vortagswerte (Feld grunddaten_vom_vortag), Piotroski nur 300 je Lauf.
  Dashboard von Hand neu hochgeladen (alle 2.437, 649 mit Piotroski). Nachtschicht: prüfen, ob der Morgenabruf 19.11. vollständig ist.
- 18.11.2026 (Nachtschicht 3:41, strenger Sparmodus, 0 Agenten): **Zahlen-Check NVIDIA (Q3 GJ 2027, 17.11.)**: Umsatz 115,8 Mrd. $
  (+103 %, Erwartung 108,8), Gewinn je Aktie bereinigt 2,68 $ (Erwartung 2,47), Ausblick Q4 130 Mrd. $ ±3 % (Erwartung 125,3), Rückkauf
  +150 Mrd. $; nachbörslich +1,3 % bis über +4 % (nvidianews.nvidia.com, coindesk.com, fool.com). Programm: NVDA 3 Punkte, Feinwert 61,6,
  Abstand 64 % (Schätzungen noch vor den Zahlen). Prüfung: Fehlercode 0, "pruefung" leer, kuerzel_verdacht leer, 315 ausgefallen
  (124 ohne Gewinn, 83 ohne Kursziel). Daten: Kurse Di 17.11. 21:19 UTC (US-Schluss da), 2748 von 2754 mit Stand 17.11.; BBBY, TCBI, NWE,
  ACT.DE, ITGR, PCRX nur Stand 16.11. (beobachten). Keine Code-Änderung.
- 17.11.2026 (Nachtschicht 21:41, strenger Sparmodus): **A8 erledigt** (Commit 6917ccf): data/verlauf/2026-11-17.json → 2026-11-16.json
  (Feld datum), schnappschuss.py nimmt den US-Handelstag aus "stand" in aktien.json statt der Uhr; Trefferquote neu (Stand 16.11.).
  **A9 erledigt, kein Datenfehler:** 0881.HK (Zhongsheng) fällt seit Monaten (4,67 HKD am 20.08. → 2,35 am 12.10., ohne Split laut
  stockanalysis.com/quote/hkg/0881/history/; Verlust 2025, Dividende gestoppt laut webull.com/news/14650939927446528), heute 1,82 HKD.
  Die Prüfung meldete heute 1816.HK (CGN Power): Fehlalarm durch Rundung bei Kursen unter 1 € (0,396 → 0,40 €, Mitte 0,436 → 0,43 €).
  pruefe_zeile rechnet die Rundung von Kurs UND fairer Mitte jetzt in die Toleranz ein. Test: Fehlercode 0, "pruefung" leer, 2438 statt
  2437 bewertet (1816.HK dazu), Punkte aller Aktien und Levins Aktien unverändert. **A7:** neuer Workflow kurse-wecker.yml – die letzte
  Abendrunde startet einen Wecker (ohne Gruppe "daten"), der bis zum nächsten Börsentag 4:30 UTC wartet (nach 5,5 h startet er sich
  selbst neu) und dann die Kurse-Schleife startet. Damit hängt der Morgen nicht mehr an GitHubs Zeitplänen (Mo/Di fielen alle aus,
  Screener lief 6,5 h zu spät). Wecker heute von Hand gestartet. .HK/.T stehen am Di-Abend auf 17.11. (A7-Test ok). Test: Mi 18.11. Kurse-Commit gegen 4:30–5:30 UTC?
- 17.11.2026 (Nachtschicht 3:41, strenger Sparmodus, 0 Agenten): **Fehler behoben: Nordea (NDA-SE.ST) mit KGV 121 statt 10,9.**
  Kurs in Kronen, aber auch Yahoos forwardEps in Euro (1,37) → Gewinn wurde nicht umgerechnet; Abstand −39 % statt +11 %. Die
  richtige Zeile aus Helsinki (NDA-FI.HE, KGV 10,9) fiel als „doppelt“ raus. schaetz_faktor prüft jetzt mit Kurs und Kursziel gegen
  (nur bei großem Wechselkurs-Faktor, KGV ohne Umrechnung > 60, mit Umrechnung 3–60). Test: nur NDA-SE.ST geändert (Feinwert bei
  94 Aktien ±0,1), Levins Aktien gleich, Fehlercode 0, "pruefung" leer, 2303 von 2604 bewertet. Daten: US-Schluss Mo 16.11. da,
  .HK/.T mit Stand 16.11. (Fix A7 wirkt). BBBY, TCBI, NWE, ACT.DE seit Fr 13.11. ohne neuen Kurs → beobachten (Übernahme?).
- 16.11.2026 (Nachtschicht 21:41, strenger Sparmodus, 0 Agenten): **Fehler behoben: Kurse aus Hongkong und Tokio fielen jeden
  Abend auf den Vortag zurück.** Nach Mitternacht Ortszeit (ab ca. 15–16 Uhr UTC) liefert Yahoo den letzten Handelstag dort nicht
  mehr; 0700.HK z. B. 12:18 UTC 390,40 HKD (Mo), ab 16:18 UTC wieder 386,60 (Fr). Am Abend standen alle 105 .HK und 69 .T auf Freitag.
  fetch.py überschreibt jetzt keinen Kurs mehr mit einem älteren (Test mit Ersatzdaten). **A7:** kurse-schleife.yml hat zusätzliche
  Starthilfen 4:43, 6:43, 8:43 UTC (Mo–Fr) und Mo 6:29 UTC. Prüfung: bewertung.py Fehlercode 0, "pruefung" leer, kuerzel_verdacht leer,
  2302 von 2604 bewertet. Auffällig, aber laut Quellen kein Datenfehler: Kioxia (285A.T) KGV 2,7 – Split 3:1 am 01.10.2026 und −39 %
  in 30 Tagen (boerse-express.com).
- 16.11.2026 (Chat, Levin: „mehr Aktien rein und weniger verbrauchen“): **screener.py + screener.yml** – jeden Abend 22:47
  fragt GitHub den Aktien-Filter von Yahoo ab (18 Börsen), nimmt Firmen über 1 Mrd. € Börsenwert und mind. 1 Mio. € Handel/Tag,
  ohne Zweitlistings (Firmenname, höchster Handelswert = Heimatbörse), die größten 150 pro Abend, danach Grunddaten.
  Kostet keine Tokens. Erster Lauf: +150 (2454 → 2604), es gibt noch rund 2.500 weitere Kandidaten (data/screener.json).
- 16.11.2026 (Chat): **ETFs wieder entfernt** auf Levins Wunsch („mach die ETF weg, das ist unnötig“): Reiter ETFs, Datensatz
  etfs, etf.py, etfs.txt, etf.yml, data/etfs.json gelöscht. Keine ETFs mehr aufnehmen. Seite: Quellen-Links vertragen jetzt auch Text
  statt Liste (Fehler „(urls || []).forEach is not a function“ in runs).
- 30.10.2026: Musterdepots A (Top-Treffer) und B (alle 50) gestartet.
- 01.11.2026: ~600 Aktien statt 187; Feinwert und Rang; neues Design; danach auf Levins Wunsch nur noch
  „Meine Aktien“, 50er-Liste läuft unsichtbar weiter, **Depots gestoppt** (Daten bleiben gespeichert).
- 01.11.2026: Fix Währung der Gewinnschätzungen (SAP, Sanofi, BAT, Petrobras, Qiagen, Prosus, SK Hynix).
- 10.11.2026: Zahlen-Check an Zahlentagen (config/zahlencheck).
- 11.11.2026: GitHub-Zeitpläne robuster; Kenvue entfernt; dritter Bewertungsweg (DCF); freier Cashflow in
  richtiger Währung; Kurs-Alarm; Spanne schmaler.
- 13.11.2026: Mehr Währungen (Pfund/Pence, Franken, Kronen); Favoriten von Morgan Stanley, Goldman Sachs,
  Deutscher Bank aufgenommen. Levin wünscht „die 10 besten Aktien, auch außerhalb der Liste“ (nur zum
  Beobachten, kein Kauf). Nachtschicht eingerichtet (21:41 und 3:41). Daten-Schleife statt Zeitplan.
- 14.11.2026: Plätze aus Dashboard und Nachrichten entfernt (Levins Wunsch).
- 14.11.2026: Nachtschicht jetzt jeden Tag (auch Wochenende). Aktien-Scout eingerichtet; bewertung.py schreibt
  dafür `alle.json`. Erste Analyse mit drei Agenten (NVIDIA vor den Zahlen am 17.11.).
- 14.11.2026: Levin will, dass Agenten News lesen und die News in die Bewertung einfließen → Nachrichten-Punkte
  (siehe „Wie gerechnet wird“), Aufgabe „News-Agenten“, Anzeige mit Links in der Detailansicht. Erster Eintrag:
  NVIDIA sehr negativ (Chefrücktritt, Ermittlungen). bewertung.py lädt news.json notfalls von GitHub.
- 14.11.2026: **Fehler behoben: freier Cashflow.** Yahoos info-Feld "freeCashflow" ist der „Levered FCF“
  (NVIDIA 41,8 statt ~127 Mrd. $). fetch.py nimmt jetzt die letzten 4 Quartale aus der Kapitalflussrechnung
  (Feld "fcf_quelle"; alter Wert in "fcf_levered"). Betrifft Cashflow-Punkte und DCF bei allen Aktien.
- 14.11.2026: Levin will mehr Aktien als 630. universum.py (+ universum.yml) liest Index-Listen von Wikipedia
  (S&P 500/400, DAX, MDAX, FTSE 100/250, CAC 40, AEX, AMX, IBEX, FTSE MIB, SMI, SMI MID, OMXS30, OMXC25, OBX,
  BEL 20, OMXH25), prüft Kürzel bei Yahoo: 635 → 1703 Aktien. Lücken: Nasdaq-100, SDAX, TecDAX, SBF 120 (keine
  Kürzel-Spalte auf Wikipedia). Die S&P-400-Tabelle enthielt auch frühere Mitglieder (noch gehandelt).
  Doppelte Firmen (Zweitlisting) wertet bewertung.py nur einmal. Ergebnis 14.11. abends: 1703 Aktien, 1452 bewertet (nach Nachtschicht: 1715 Aktien, 1496 bewertet).
  Datenabruf-Fehler: zwei gleichzeitige Abrufe → Konflikt in aktien.json, ein ganzer Abruf verworfen. Behoben:
  grunddaten.yml und kurse-schleife.yml legen die neue Datei jetzt immer auf den neuesten Stand von main.
- 14.11.2026: Levin will alle Aktien sehen und jede Nacht neue dazu: Dashboard-Reiter „Alle Aktien“
  (Datensatz `alle` aus alle.json, Feld "aufgenommen" für NEU), Nachtschicht nimmt jede Nacht bis zu 15 neue
  Aktien auf (zuerst Lücken: Nasdaq-100, SDAX, TecDAX, SBF 120, STOXX 600), sonntags universum.yml.
- 14.11.2026 (Nachtschicht 21:41): **Auftrag A1 erledigt** (Commit 03c9adf, 1d8011a): bewertung.py schreibt zu jeder
  Aktie "warum" (woher die Punkte kommen, faire Mitte) und "finanzen" (Kurs, Börsenwert, Umsatz, Marge, freier
  Cashflow, Nettoschulden, Dividende, nächste Zahlen) – nur aus den Zahlen der Zeile, Banken ohne Cashflow/Schulden.
  Neue Euro-Felder (marktwert_eur, umsatz_eur, nettoschulden_eur, fcf_eur, dividende_pct …). fetch.py holt Umsatz,
  Margen, Dividende (Prozent/Anteil vereinheitlicht). Dashboard: Detailansicht mit „Warum diese Bewertung“ und
  „Finanzielle Lage“, 5 neue Zahlen, Karten mit erstem Gegen-/Pro-Punkt. Punkte und Reihenfolge unverändert.
  alle.json ohne leere Felder und kompakt (2,2 MB mit Umsatz/Dividende). grunddaten.yml: Eingabe „voll“ erzwingt
  Vollabruf (lief 14.11. 20:58–21:42 UTC, Umsatz bei 1625, Dividende bei 1712 Aktien). Dashboard-Daten danach neu
  hochgeladen. Stichprobe Dividende: NVIDIA 0,6 % passt zur Erhöhung im Mai 2026 (fool.com); EchoStar (SATS) 15 % prüfen.
- 14.11.2026 (Nachtschicht): Fehler behoben (Commit a18e7e5): London-Aktien mit Dollar-Bericht (AstraZeneca, Shell,
  HSBC, Rio Tinto, BP, Glencore, Diageo …) fielen mit „Währung der Gewinnschätzung unklar“ raus, weil Yahoos
  forwardEps dort in Pfund steht (Kurs in Pence). Jetzt 1452 → 1487 bewertet, keine andere Aktie geändert.
- 14.11.2026 (Nachtschicht): 12 neue Aktien: ALAB, CCEP, TEAM, TRI, ALNY, TTD, GFS (Nasdaq-100-Lücke), TKMS.DE,
  R3NK.DE, IOS.DE, ELG.DE, SIX2.DE (TecDAX/SDAX/MDAX-Lücke). 10 bewertet; TEAM und ALNY: „Wachstum unplausibel“.
  Nasdaq-100 aktuell (seit 22.06.2026): ALAB, CRWV, NBIS, RKLB, TER neu; CHTR, CTSH, INSM, VRSK, ZS raus.
  CRWV, NBIS, RKLB ohne Gewinn → nicht aufgenommen. Noch offen: SDAX-Rest (z. B. 1U1, KWS, DUE, DRW3, WAC).
- 15.11.2026 (Nachtschicht 3:41): **15 neue Aktien** (SDAX-Lücke, Börsenwert laut boerse.de 13.11.): SPG, FIE, OHB, 1SXP,
  OBCK, SZU, DMP, TNIE, VH2, ACT, WAC, GYC, YSN, SFQ, S92 (.DE) – Commit 2d0f45a. Kürzel korrigiert: SATS → ECHO
  (EchoStar, neues Kürzel seit 24.06.2026; SATS zeigte ein Vorzugspapier mit 15 % „Dividende“), FAGR.AS → FAGR.BR.
  Entfernt: ROKU (von Fox übernommen, 06.11.2026), SIX/ULTI/TIME (ETFs), INCR (zu klein), INGA.BR (doppelt).
  SPY bleibt (Vergleichswert der Depots). universum.yml (sonntags) gestartet.
- 15.11.2026 (Nachtschicht, Arbeitsweise): **Kürzel-Verdacht** (Commit 6d7b98d): bericht.json hat "kuerzel_verdacht" –
  kein neuer Kurs seit mehr als 3 Börsentagen (Übernahme/neues Kürzel) oder weder Börsenwert noch Schätzungen (ETF,
  Vorzugspapier, falsche Börse). Test: findet alle 7 Fälle dieser Nacht (+ JCH.L und 2 Fonds aus London); Punkte und
  Listen byte-gleich. universum.py nimmt Kürzel aus `tickers_gesperrt.txt` nicht wieder auf (Kürzel + Datum + Grund).
- 15.11.2026 (Nachtschicht 21:41, Sparmodus, 6 Agenten): **A2 + A4.1 erledigt** (Commits a856429 + Korrektur): Seite am PC neu
  (Titel je Reiter, Detail rechts mitlaufend ab 1100 px, Detail ohne Doppelungen, „Mehr Spalten“, Tabelle einklappbar, ruhigere
  Karten), Reiter „ETFs“ (Datensatz etfs), Trefferquote im Reiter „So wird gerechnet“ (Datensatz trefferquote). stray_write-Ursache:
  dash.draw('alle_mehr') innerhalb eines anderen draw + 10 data-draw-Elemente mit „—“ im HTML → behoben, lokal 0 Funde.
  Seite Version 25, Kopie in dashboard/index.html. **A3.1 erledigt** (c86544e): rueckwirkend.py füllt data/verlauf für 11 Börsentage
  (30.10.–13.11., "rueckwirkend": true, nur Nachrichten des jeweiligen Tages), trefferquote.json + trefferquote_zeilen.json
  (Liste fürs Dashboard). Ausreißer-Grenze von ±80 % auf +150 %/−75 % (AppLovin +81 % war echt). **A5.1 erledigt** (ccc7c4c):
  BRWM.L, JCH.L, SDP.L, SOI.L, VAS.AX, NYR.BR, INDV (Fusion mit SUPN), LXP (Übernahme Brookfield/CPP) gesperrt; ECHO stand doppelt.
  **23 neue Aktien** (SDAX: 1U1, KWS, DUE, AOF, HBH, KTN, VBK, DEQ; SBF 120: ALO, AMUN, BOL, GET, LI, RXL, SW, EDEN, BIM, SCR, AKE,
  GFC, IPN, TE, DIM), **11 neue ETFs** (XEON, EUNH, EUN5, XCS6, ZPRR, XDEW, 2B7K, ZPRG, DFEN, IQQI, IQQ6; DFEN.DE = VanEck Defense,
  das richtige Kürzel statt DFNS.DE – erst nach etf.yml bestätigt). LI/RXL/SW/GFC.PA: Yahoo-Seite nicht gefunden → nach Grunddaten prüfen.
  Edenred: Übernahme-Spekulation (marketscreener) – beobachten. Aufgaben-Texte ändern (A3.3/A4.2/A5.2/A5.3) ging NICHT: update_trigger
  in der geplanten Aufgabe nicht erlaubt → Levin muss es im Chat freigeben.
  Nach dem Grunddaten-Abruf (21:10 UTC): alle 23 neuen Aktien mit Daten, 22 bewertet (2141 → 2163; ALO.PA „Wachstum 664 %
  unplausibel“), kuerzel_verdacht leer; alle 46 ETFs gültig, Datensatz etfs von Hand neu hochgeladen. "runs" zeigt noch den alten
  Stand (Seite seit dem Upload nicht geöffnet) → Aufpasser/nächster Lauf prüft, ob stray_write weg ist.
- 19.11.2026 (Nachtschicht 3:41, ohne Agenten): **Kioxia (285A.T) Datenfehler behoben**: Aktiensplit 3:1 (newsquawk), Yahoo-Kurs schon
  nach dem Split (8.025 ¥), Kursziel (35.850 ¥) und Gewinnschätzungen noch davor → KGV 1,6, Abstand +541 %, 6 Punkte (falsch).
  bewertung.py: Liste SPLIT_NOCH_ALT – Aktie fällt raus, solange Kursziel > 75 % des Split-Faktors über dem Kurs (kommt von selbst
  zurück, wenn Yahoo anpasst). Test: nur 285A.T fehlt (2437 → 2436), keine Punkte geändert, pruefung leer.
  Offen: 160 Kürzel ohne Grunddaten (150 vom Screener 18.11., 10 vom 17.11.) – Ursache: Morgenabruf 18.11. leer. Lauf 21:41: prüfen, ob
  der Morgenabruf 19.11. sie gefüllt hat; Fonds (PHYS.TO, TMPL.L, TRY.L, VEIL.L, WWH.L, TFIF.L) dann sperren. Idee: Split automatisch
  erkennen (yfinance-Splits im Grunddaten-Abruf, Kursziel/Kurs ≈ Faktor).
- 16.11.2026 19:15 Aufpasser: alles läuft (Kurse, Grunddaten, News, Dashboard 18:35, Programm ok). stray_write noch da → A5.4 offen.
- 17.11.2026 09:13 Aufpasser: Kurse, Grunddaten, Dashboard (07:34) ok. Schnappschuss-Datum falsch → A8; Prüfung 0881.HK → A9. News ohne neuen Stand (Sparmodus, nichts fällig).
- 17.11.2026 13:16 Aufpasser: Kurse-Schleife lief Di nicht (letzter Kurse-Commit Mo 21:18 UTC, alle Starthilfen ab 4:43 UTC fehlten). Von Hand gestartet (Lauf 44081738530). Dashboard 10:36, Grunddaten ok. A9 und stray_write (A5.4) weiter offen.
- 18.11.2026 23:14 Aufpasser: alles läuft (Kurse 22:19, Grunddaten, News, Dashboard 21:34, Programm ok). Abgelaufenen STRENGEN SPARMODUS (bis Mi 18.11. 21:00) gelöscht; es gilt das BUDGET Nachtschicht. stray_write in runs stammt von 17:55 (vor A5.4), Seite seitdem nicht geöffnet.
- 19.11.2026 (Scout 11:48): 1 neue Aktie: PTRN (Pattern Group, Hochstufung auf Kaufen durch Jefferies 12.11., Börsenwert ca. 3,6 Mrd. $,
  mit Gewinn; insidermonkey.com, stockanalysis.com). BABA ausgelassen (9988.HK schon drin). Hype-Liste: 10 Aktien (neu ANT, PANW, TJX, BRBR).
- 16.11.2026 (Scout 11:48): 2 neue Aktien: NU (Nu Holdings, Rekordquartal, +11,75 % am 13.11., bigmoves.substack.com), EWBC
  (East West Bancorp, neue Kaufempfehlung Hovde 10.11., behindthemarkets.com). Hype-Liste: 8 Aktien in data/hype.json.
- 16.11.2026 (Aufpasser 9:18): Kurse-Schleife lief Montag früh nicht (geplante Starts 5:11 und 7:11 UTC fehlten, letzter Lauf Fr 13.11.). Von Hand gestartet (Lauf 43830295701). Keine Code-Änderung.
- 13.11.2026 (Nachtschicht 21:41): Kurse-Schleife war nach dem Push (18:51 UTC) nie gelaufen – letzte
  Starthilfe 18:11 UTC lag davor, also keine Kurse nach 18:48 UTC. Von Hand gestartet (Lauf 43504676163),
  damit der US-Schluss vom Freitag noch kommt. Keine Code-Änderung.

## Gegenprüfung mit dem Internet (Nachtschicht, reihum)
- NVDA: 13.11.2026 – Gewinn FY2027 9,32 $ / FY2028 15,85 $ passt zu stockanalysis.com (9,31 / 15,91).
  Kursziel-Median Yahoo 282 $, stockanalysis 315 $ (Stand dort 06.11., vor dem Kursrutsch) → −10 %, Ursache
  vermutlich veralteter Vergleichswert.
- AVGO: 14.11.2026 – Gewinn FY2026 Yahoo 11,66 $ / vcpscanner.com 11,68 $ (passt). Kurs Yahoo 347 $ (13.11.),
  dort 364 $ (12.11.) → Tagesbewegung. Kursziel-Durchschnitt (Yahoo 529 $) noch ohne zweite Quelle.
- SAP: 15.11.2026 – Kursziel-Durchschnitt Yahoo 284,50 $ / stockanalysis.com 280,83 $ (passt). Gewinn 2026/2027 Yahoo
  8,06/9,53 $ (ADR, in Dollar) = 7,29/8,62 € / stockanalysis 7,16/8,44 € bereinigt (+2 %, passt).
- ENR.DE: 15.11.2026 – Kurs 131,28 €, Kursziel-Durchschnitt 192,21 € (28 Analysten), Gewinn GJ 2028 8,48 € – alles gleich wie
  marketscreener. Achtung: Geschäftsjahr endet im September, eps_forward = GJ 2028 (in ~2 Jahren).
- IFX.DE: 15.11.2026 – Kurs 49,875 € passt. Kursziel 80,79 € / marketscreener 86,08 € (−6 %, Quelle wohl vor den Zahlen).
  Gewinn GJ 2028 Yahoo 3,88 € / marketscreener 3,31 € (+17 %): Yahoo bereinigt, marketscreener nahe IFRS (Infineon GJ 2026:
  bereinigt 1,73 € gegen IFRS 1,15 €) und veraltet (02.10.). Bekannte Grenze „bereinigt“.
- NVDA: 18.11.2026 – Kurs 155,46 $ (Schluss 17.11.) passt zu fool.com. Kursziel-Median Yahoo jetzt 255 $ (Mittel 268 $, 54 Analysten),
  Gewinn FY2028 15,84 $ (noch vor den Zahlen). Nach den Zahlen neu prüfen.
- AVGO: 19.11.2026 – Kursziel-Durchschnitt Yahoo 528 $ (47 Analysten) / tikr.com 533 $ (https://www.tikr.com/blog/is-rothschild-co-redburn-wrong-to-give-up-on-broadcom-wall-street-still-sees-533) → passt (−1 %).
- NVDA: 19.11.2026 – Yahoo nach den Zahlen: Gewinn FY2028 16,54 $ (vorher 15,84), Kursziel-Median 245 $ (55 Analysten), Kurs 147,51 $.
  Zweite Quelle nicht erreichbar (chartmill gesperrt, Twelve Data nur im teuren Tarif) → noch offen.
- Als Nächstes: NVDA zweite Quelle (z. B. stockanalysis.com/stocks/nvda/forecast/), dann SAP.

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
- A3.2 langer Rückblick-Test mit Kursdaten (yfinance im GitHub-Workflow) – ab Do 19.11. (nach Sparmodus).
- Hinweis: Yahoo ist aus der Cloud-Umgebung der Aufgaben gesperrt (403); yfinance geht nur im GitHub-Workflow.

### A5 (Rest)
- A5.2/A5.3 siehe A6. A5.4 (stray_write) behoben – nach dem nächsten Öffnen der Seite in data/users/me "runs" bestätigen.
- A5.4 noch offen (vom Aufpasser, 16.11.2026 19:15): Seite wurde am 16.11. um 17:45 Uhr geöffnet, data/users/me "runs" zeigt weiter
  drawings: stray_write (count 1). Ursache weiter suchen und beheben; Test: runs ohne Warnung nach dem nächsten Öffnen.
- Stand 18.11. 21:41: behoben (Länder-Auswahl fest im HTML, Seite Version 30). Offen nur der Test: nach dem nächsten Öffnen
  data/users/me "runs"/"check" ohne stray_write? Dann A5 löschen. (Falls weiter gemeldet: Branchen-Auswahl #alle-sektor wird in
  dash.onData gefüllt – dann ebenfalls in eine draw-Funktion verschieben.)

### A7 (vom Aufpasser, 16.11.2026): Kurse-Schleife startet montags nicht
- Stand 16.11. 21:41: zusätzliche Starthilfen eingebaut (siehe Protokoll). Offen nur noch der Test: Mo 23.11. Kurse-Commit vor 9 Uhr Berlin?
  Dann diesen Auftrag löschen. Zusätzlich prüfen: Di 17.11. abends .HK/.T mit Stand 17.11. (nicht 16.11.).
- Aufpasser 17.11. 13:16: auch Di 17.11. kein einziger Start (weder 4:43–12:11 UTC geplant). Starthilfen reichen nicht – Ursache suchen
  (evtl. concurrency "daten" mit Grunddaten-Lauf 4:16–5:26 UTC verwirft wartende Läufe; nach Grunddaten Kurse-Schleife anstoßen?).
- Stand 17.11. 21:41: Wecker (kurse-wecker.yml) eingebaut, siehe Protokoll. Test: Mi 18.11. und Mo 23.11. Kurse vor 6:30 UTC? Dann löschen.

## Chef – Plan
### 18.11.2026 (Mi) – Aufträge für heute Nacht (Budget 7 %, höchstens 2 Agenten)
Lage: 2904 Aktien im Programm (alle mit Kurs), Dashboard 2437 bewertet (nach der Reparatur heute). Wecker (A7) wirkt: Mi erster Kurse-Commit
4:35 UTC. Trefferquote (Stand 17.11., rückwirkend, 2,5 Wochen): Aktien mit mehr Punkten lagen bisher eher schlechter (7–10 Punkte −9,5 %,
n=3; unter 3 Punkte +0,3 %) – sagt bei so wenigen Tagen fast nichts. "Chef wieder einschalten" lief nicht (Sitzung weg) → Sparmodus-Ende hier vermerkt.
1. A10 Teil 3 (alphalens / Vorhersagekraft) – geplanter Start heute; Teile 1–2 waren schon fertig. Erfolg: "vorhersagekraft" in trefferquote.json, im Reiter sichtbar.
2. A5.4 stray_write (Ort jetzt bekannt: #alle-region) + Kopie dashboard/index.html aktualisieren. Erfolg: runs ohne drawings.
3. Lauf 3:41: prüfen, ob der Morgenabruf 19.11. vollständig ist (Grunddaten nicht leer, ~2400+ bewertet) – steht schon im Protokoll.
An Levin gefragt: A6 (Aufgaben-Texte Nachtschicht + Meine Aktien) freigeben – Nachtschicht-Text sagt noch „drei Läufe“, „Hälfte der Tokens“,
„noch mehr Agenten“ und widerspricht dem 7-%-Budget.
Später (ab Do, je eine Nacht): A3.2 langer Rückblick-Test; Japan/Nikkei 225 (bitte prüfen, ob der Screener .T schon füllt, bevor recherchiert wird).
### 15.11.2026 (So, erster Chef-Lauf) – kurz
Plan: A6-Textänderungen, A2/A4.1 Seite, A3.1 Verlauf rückwirkend, Japan, NVIDIA-Zahlen-Check. Erledigt: A2, A4.1, A3.1, A5.1, NVIDIA-Check (18.11.),
ETFs (später auf Levins Wunsch wieder entfernt). Offen: A6 (Freigabe), A5.4. Vorschläge an Levin noch ohne Antwort: (a) Sondereffekt-Regel mit
Rückblick-Test, (b) Londoner Fonds ohne Kursziel sperren.

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
- SDAX noch offen (Börsenwert prüfen): 1U1, KWS, DUE, AOF, HBH, KTN, VBK, DEQ; danach SBF 120 und STOXX 600.
- Noch „Währung unklar“: SHC.L, ABB.ST, EQT.ST, HEXA-B.ST (forwardEps passt zu keiner Umrechnung, Abweichung 25–60 %).
- 15.11.2026: Universum um S&P 600, TSX 60, ASX 50, Hang Seng erweitert (1724 → 2438); Nikkei 225 ohne
  Kürzel-Tabelle auf Wikipedia → Nachtschicht füllt aus anderer Quelle. Neue Währungen JPY, CAD, AUD, HKD.
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
- Seit 15.11.2026 (Levin: „noch mehr Agenten, damit es noch besser ist“): die Nachtschicht arbeitet als Team –
  Recherche je Region, Gegenprüfung, Code- und Seiten-Agenten mit eigener Arbeitskopie, Nachrichten; nur die
  Leitung pusht. Zum Schluss prüft ein frischer Prüf-Agent alle Änderungen des Laufs.
  Ausgebaut („noch mehr Agenten, das soll richtig gut sein“): 6 Recherche-Agenten nach Region, Kürzel-Prüfer,
  2–4 Daten-Qualitäts-Agenten, 2 Gegenprüfer (Levins Aktien, Top 10), je Verbesserung ein Code-Agent, Rückblick-
  Test, Seiten-Agent + Seiten-Tester, Nachrichten-Agenten, Skill-Agent, 2 unabhängige Prüf-Agenten am Schluss.
  News-Agenten: Levins Aktien + bis 60 weitere, ein Agent je ~10 Aktien, dazu ein Prüf-Agent.
- Seit 15.11.2026 (Levin: „du kannst die Hälfte meiner wöchentlichen Tokens in der Nachtschicht verbrauchen, damit
  es richtig gut ist“): gründlich und tief arbeiten (Lauf 0:41 am selben Abend wieder gestrichen). Richtwert: höchstens
  etwa die Hälfte von Levins Wochenlimit. Den echten Verbrauch sieht nur Levin in seinen Claude-Einstellungen. Sagt er,
  es wird zu viel: weniger Agenten, Lauf 0:41 nur bei offenen großen Aufträgen.
- Grenze (Levin, 15.11.2026): alle Aufgaben zusammen höchstens **75 % von Levins Wochenlimit** (neu jeden Mittwoch).
  Den Zähler sieht nur Levin (Einstellungen → Nutzung). Er schreibt die Zahl in den Chat, sie wird hier eingetragen.
  Ab 60 %: Sparmodus wie unten. Ab 75 %: Nachtschicht nur noch Schritt 1 (Prüfen), keine Agenten, bis Mittwoch.
  Letzte Zahl: 42 % am So 15.11. 19:22; die Nacht 15./16.11. hat laut Levin etwa 20 % verbraucht → etwa 62 % (Mo 16.11.).
  Diese Zahl gilt für die Woche bis Mi 18.11.; seit Mi 18.11. neue Woche, noch keine neue Zahl von Levin.
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
