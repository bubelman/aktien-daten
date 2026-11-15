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
  Immer mit „Das ist keine Anlageberatung.“ enden.
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
- Geplante Aufgabe „Meine Aktien aktualisieren“: Börsentage 7:33, 10:33, 13:33, 18:33, 21:33 (Berlin).
  Kurs-Alarm ab ±5 %, Zahlen-Check an Zahlentagen, Wochenbericht montags.
- Nachtschicht: jeden Tag 21:41 und 3:41 (Berlin), prüft alles und verbessert. Der Lauf 0:41 ist auf Levins Wunsch
  wieder gestrichen (15.11.2026, 19:31). Große Aufgaben machen die Läufe 21:41 und 3:41; was nicht fertig wird, macht
  der nächste Lauf weiter. Steht in der Aufgabe noch etwas von 0:41, gilt das nicht mehr.
- Aktien-Scout: Börsentage 11:48 und 18:48 (Berlin), siehe Abschnitt „Aktien-Scout“.
- Aufpasser (seit 15.11.): täglich 9:13, 13:13, 19:13, 23:13 (Berlin). Prüft Aufgaben, GitHub-Läufe, Daten, Dashboard;
  behebt Kleines selbst (Workflows neu starten, Dashboard-Daten neu schreiben), Größeres als Auftrag für die Nachtschicht.
  Seit 15.11. auch Token-Wächter: prüft Laufzeiten der Aufgaben, setzt/löscht den Sparmodus nach Levins Zahl,
  schreibt bei Leerlauf-Arbeit einen Auftrag „Token sparen bei …“ für die Nachtschicht.
- Chef (seit 15.11., auf Levins Wunsch „öfter“): täglich 20:27 (vor der Nachtschicht), sonntags mit großem Bericht.
  Schaut auf das ganze System („Firma“), plant die nächsten 1–2 Wochen, schreibt
  Aufträge für die Nachtschicht (Abschnitt „Chef – Plan“), schickt Levin den Chef-Bericht; Regeländerungen, mehr
  Kosten und neue Aufgaben nur nach Levins Ja.
- News-Agenten: Börsentage 6:51, 12:51, 20:51 (Berlin). 3 Agenten parallel prüfen Levins Aktien + bis zu
  30 weitere (Top-Bedingungen zuerst), Ergebnis selbst nachprüfen, data/news.json pushen.

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
- IFX.DE, ENR.DE: noch nicht geprüft (als Nächstes, in dieser Reihenfolge).

## Offene Aufträge von Levin (die Nachtschicht erledigt sie zuerst, danach ins Protokoll verschieben)

### A2 (15.11.2026, ab Nachtschicht 15.11. 21:41): Dashboard am PC schöner und übersichtlicher
Levin: „es soll auf PC und es soll schöner und übersichtlicher“, „du machst es einfach in der Nachtschicht schöner“.
Seite: ArtifactData collection "files", doc_id "index.html", Feld "text" (immer die aktuelle Version lesen!).
Beobachtungen am PC (1440 px, 15.11. abends):
1. Überschrift heißt immer „Meine Aktien“, auch im Reiter „Alle Aktien“ → neutraler Titel (z. B. „Aktien-Liste“)
   oder Titel je Reiter; der Einleitungssatz ist lang.
2. Detailansicht liegt ganz unten; nach Klick muss man weit scrollen. Besser ab ca. 1100 px Breite zwei Spalten:
   links Liste/Karten/Tabelle, rechts die Detailansicht fest mitlaufend (position: sticky; eigene Scrollleiste).
   Auf schmalen Bildschirmen bleibt alles untereinander. Kein automatisches Scrollen zum Detail am PC.
3. Detailansicht doppelt sich (Name und Kurs stehen unter den Texten nochmal). Neu ordnen, eine Spalte:
   Kopf (Name, Kürzel, Branche, Punkte, Feinwert, 🔥/NEU), Kurs + Abstand groß, faire Spanne mit Beschriftung,
   „Warum diese Bewertung“, „Finanzielle Lage“, Haken, Punkte-Balken, Nachrichten, Hype, Zahlenliste in 2 Spalten.
4. Tabelle „Alle Aktien“ ist breiter als der Bildschirm (seitlich scrollen). Standard: wenige Spalten (Aktie,
   Punkte, Feinwert, Kurs, Abstand, Trend, Land, Branche) und ein Knopf „Mehr Spalten“ für den Rest.
5. „Meine Aktien“: Karten und Tabelle zeigen fast dasselbe → Tabelle einklappbar („Tabelle zeigen“), Karten
   ruhiger (weniger Chips), KPI-Leiste kompakter.
6. Insgesamt: ruhigere Abstände, klare Überschriften, gleiche Schriftgrößen; Farben nur für gut/schlecht.
   Alle bestehenden Funktionen müssen bleiben (Suche, Filter, Sortieren, NEU, 🔥, ★, Texte, Nachrichten, Links,
   „Mehr zeigen“). data-draw/data-source/data-field-Markierungen beibehalten; Elemente mit data-draw leer lassen.
Vorgehen: lokal mit Ersatz für window.dash und echten meine.json/alle.json in Chromium testen (1440 px und
390 px), Bildschirmfotos ansehen, keine Konsolenfehler; dann hochladen, data/users/me "runs" prüfen (keine
"stray_write"/"not_empty"-Warnungen). Im Bericht kurz sagen, was anders ist. Danach weitere Nächte: weiter
verbessern (siehe Regeln für die Nachtschicht).

### A3 (15.11.2026, ab Nachtschicht 15.11. 21:41): Trefferquote – funktioniert die Bewertung?
Levin: „geht noch besser“. Grundlage seit 15.11.: schnappschuss.py + schnappschuss.yml (Börsentage 22:37 UTC)
speichern data/verlauf/JJJJ-MM-TT.json (Punkte, Feinwert, Kurs €, Abstand, Top je Aktie) und rechnen
data/trefferquote.json (Kursentwicklung seit 1 Woche/1/3/6/12 Monaten je Punktegruppe und mit/ohne Top-Bedingungen).
1. Rückwirkend füllen: aus der Git-Geschichte von data/aktien.json (Daten seit Ende Oktober) für jeden Börsentag
   die letzte Version holen, bewertung.py darauf laufen lassen (heutige Regeln; fehlende Felder → Aktie überspringen)
   und als data/verlauf/<Datum>.json speichern, mit Feld "rueckwirkend": true. Ehrlich kennzeichnen: das ist ein
   Rückblick mit heutigen Regeln, kein echter Test aus der Vergangenheit.
2. Zusätzlich mit Kursdaten (yfinance im GitHub-Workflow, z. B. einmaliger Workflow) einen längeren Rückblick-Test
   der Trend- und Bewertungsregeln vorbereiten, wenn machbar – nur als Auswertung, keine Regeländerung.
3. Dashboard: neuer kleiner Bereich (z. B. im Reiter „So wird gerechnet“ oder eigener Reiter „Trefferquote“):
   Tabelle/Balken „Aktien mit 7–10 / 5–6 / 3–4 / unter 3 Punkten: im Schnitt X % seit <Datum>“, Vergleich mit allen
   Aktien, Hinweis „wenige Wochen sagen wenig“. Dafür einen Datensatz "trefferquote" anlegen (Datei aus
   data/trefferquote.json hochladen, datasets/trefferquote) und in der Aufgabe „Meine Aktien aktualisieren“ ergänzen,
   dass sie die Datei bei jedem Lauf mit hochlädt (update_trigger, ganzer Text plus Ergänzung).
4. Wochenbericht montags: eine Zeile zur Trefferquote.

## Chef – Plan
- (der Chef trägt hier ab 15.11.2026 jeden Abend seinen Plan ein)

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
  Letzte Zahl: 42 % am So 15.11. 19:22.
- **SPARMODUS bis Mittwoch 18.11.2026** (Levin am 15.11. um 19:22: schon 42 % vom Wochenlimit verbraucht, Mittwoch
  wird es neu). Gilt vor allen anderen Regeln hier und in der Aufgabe:
  • Lauf 21:41: Aufträge A2/A3 und neue Aktien ja, aber höchstens 5 Agenten gleichzeitig und nur 1 Prüf-Agent am Schluss.
  • Lauf 3:41: nur Schritt 1 (Prüfen) und Fehler beheben, keine neuen großen Arbeiten, höchstens 2 Agenten.
  • Ab Nachtschicht Mittwoch 18.11. 21:41 wieder voller Betrieb. Diesen Punkt dann aus den Notizen löschen.
- Höchstens ein Skill pro Nacht (propose_skills, sonst skills/<name>/SKILL.md), nur wenn er wirklich hilft.

## Skills
- (noch keine von der Nachtschicht vorgeschlagen; 14.11.: bewusst keiner, A1 hatte Vorrang)
- 15.11.: keiner (kein Werkzeug propose_skills; für die NVIDIA-Zahlen am 17.11. gibt es schon equity-research:earnings-preview).
