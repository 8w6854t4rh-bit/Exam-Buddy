# Exam Buddy – Hinweise für Claude

Lern-App für Auszubildende, zuerst Automobilkaufleute (Teil 1 = Zwischenprüfung, Teil 2 = Abschlussprüfung). Im Aufbau, nur in der Vorschau: Verkäufer/-in und Kaufleute im Einzelhandel. Besitzer: Jérôme Drouvin. Ziel: App Store und Verkauf. Die App ist live und wird von Kollegen zum Lernen genutzt.

## Wichtigste Regeln

1. **Lernstand der Nutzer nie gefährden.** Der Fortschritt liegt im `localStorage` (Schlüssel `ak-trainer-v1` bzw. `ak-trainer-ap1`, dazu `eb-…`) und ist **über Array-Positionen** an Karten, Quizfragen usw. gebunden. Einträge in `data.json` deshalb **nie löschen, umsortieren oder dazwischen einfügen**. Fehlerhafte Einträge an Ort und Stelle ersetzen, neue nur hinten anhängen.
2. `data.json` (Deutsch) und `data_en.json` (Englisch) sind **positionsgleich**. Jede Änderung an einem Eintrag in beiden Dateien machen.
3. Riskante Umbauten nur in der **Vorschau** (`PV=true`). Bis nach der Abschlussprüfung (um den 24.11.2026) nichts live schalten, was Lernstand oder Ablauf der Kollegen verändert.
4. Jede Veröffentlichung: `APPV` in `quellen/app.html` und `VERSION` in `sw.js` gemeinsam hochzählen (`exam-buddy-vNN`), sonst holen installierte Apps das Update nicht.
5. Inhalte immer in eigenen Worten. Keine Original-IHK-Aufgaben, keine Schulbuchseiten, keine Daten echter Personen.
6. Kein Tracking ohne passenden Absatz in der Datenschutzerklärung (`LT.datenschutz` in `app.html`). Impressum und Datenschutz müssen in höchstens zwei Schritten erreichbar bleiben.

## Aufbau

- `quellen/app.html`: die eigentliche App, eine Datei mit Vanilla-JS. Platzhalter `/*GEN*/`, `/*DATA*/`, `/*DATAEN*/`, `/*UIEN*/` füllt der Build.
- `quellen/generatoren.html`: liefert die Rechen-Generatoren (`const G=[…]`).
- `quellen/data.json`, `quellen/data_en.json`: Karten, Quiz, Buchungen, Zuordnungen, Wissen, Lernfelder.
- `quellen/ui_en.json`: englische Oberflächentexte als Vorlagen, Zahlen als `{0}`, `{1}`.
- `quellen/build.py`: baut `quellen/out/index.html` (live, auch für claude.ai), `quellen/out/preview.html` (Vorschau mit Speicher-Präfix `pv-`) und `index.html` in der Repo-Wurzel (GitHub-Pages-PWA mit Manifest, Icons und Service Worker).
- `index.html`, `sw.js`, `manifest.webmanifest`, `icons/`: werden von GitHub Pages ausgeliefert. `index.html` nie direkt bearbeiten, immer über `python3 quellen/build.py`.

Code-Grundbausteine in `app.html`: `$()` baut Elemente, `R()` rendert in `#app`, `go(hash)` navigiert, `route()`, Ansichten in `V`, Titel in `TITLE`, Zustand in `S`. `const PV=false;/*PVFLAG*/` schaltet die Vorschau. `BERUFE`, `BER`, `AB`, `BTR` gehören zur Berufsauswahl (nur Vorschau). Das KI-Modul (`KI`, `kiAsk`, `kiGrade`, `kiUpload`, `vFreigabe`, `vGemeinsam`) läuft nur in der Vorschau und nur auf claude.ai, weil es `window.claude.use('sample'|'db'|'user')` braucht.

## Fachliche Festlegungen

- Wirtschaftlicher Totalschaden: Reparaturkosten > Wiederbeschaffungswert − Restwert. Die Kasko-Besonderheit steht nur im Wissen, nicht in den Aufgaben.
- Werkstattindex wie im IHK-Lösungsschlüssel (Sommer 2026, 5.5/5.6): Selbstkosten = produktive Löhne × (1 + Gemeinkostenzuschlag), Gewinn und Wagnis **beide auf die Selbstkosten** (nicht nacheinander), Soll-Index = Soll-Lohnerlöse ÷ produktive Löhne, Ist-Index = Ist-Lohnerlöse ÷ produktive Löhne, 3 Nachkommastellen.
- Buchungssätze in Prüfungen wie im IHK-Lösungsschlüssel: je richtigem Soll- bzw. Habeneintrag (Konto und Betrag) 1 Punkt, Punkte = Anzahl der Einträge. Falsche Einträge geben 0 Punkte, ein überzähliger Eintrag bleibt ohne Abzug, ab dem zweiten überzähligen Eintrag kostet jeder 1 Punkt (`bHits`).
- Quiz nur mit Aufgaben, die im Kopf lösbar sind. Rechenlastige Fragen gehören in den Rechnen-Bereich. Bestehende Quizfragen dieser Art werden über `QRECH` (Positionen in `D.quiz`) aus Quiz und Prüfungen herausgenommen, nicht gelöscht. Quizfragen mit Zahlen in Frage und Antworten (`qCalc`) zeigen zusätzlich einen zugeklappten Taschenrechner, im Quiz, im Lernplan-Test und in Prüfungen.
- Konten immer mit Namen nennen („7000 VAK Neuwagen an 3000 Bestand Neuwagen“), nie nur die Nummer. Die Azubis müssen den Kontenrahmen nicht auswendig können.
- Handelskalkulation vorwärts, rückwärts und Differenzkalkulation werden wie in der IHK-Prüfung im Kalkulationsschema gelöst (`tab` im Generator, `kSchema`/`kCheck` in `app.html`): Bezeichnungen und Prozentsätze sind vorgegeben, jedes Euro-Feld wird geprüft (Toleranz 5 Cent), in der Prüfung gibt es Punkte anteilig je richtigem Feld.
- BAB im IHK-Schema (Rechenart „BAB vollständig (IHK-Schema)“, `bab` im Generator, `babGrid`/`babCheck` in `app.html`): Raster Kostenarten × Verwaltung/Neuwagen/Teile/Werkstatt, Verteilung nach Belegen, Fläche oder Schlüssel, Summen, Umlage der Verwaltung als Hilfskostenstelle nach Verkaufserlösen, Zuschlagssätze auf VAK bzw. produktive Löhne. Euro auf ±0,50, Prozent auf ±0,01. Nur im Rechnen-Bereich: Generatoren mit viertem Element `'nox'` werden in Prüfungen mit gemischten Rechenaufgaben nicht gezogen.
- Rechenwege mit Prozentsätzen zusätzlich als Dezimalzahl zeigen (0,03 % = 0,0003), damit sie im Taschenrechner nachrechenbar sind.
- WiSo im IHK-Stil: alle WiSo-Quizfragen haben fünf Antworten mit typischen Fallen („stets“, „ausschließlich“, falsche Fristen). Zusatz in `q[5]` (`data_en.json`: `x[3]` mit englischer Grafik): `firma:1` zeigt die Unternehmensbeschreibung der Autohaus Nordring GmbH (`D.firma`), `f` eine Grafik (`t:'tab'|'txt'|'line'|'bar'`, `qFig`/`qSvg`), `nocalc:1` unterdrückt den Taschenrechner. WiSo-Prüfung: 27 Ankreuz- (höchstens 2 Zahlenfragen, `maxCalc`), 3 Zuordnungs-/Reihenfolge- (`D.zu` mit `g:'WiSo'`) und 3 Rechenaufgaben = 33 Aufgaben, 100 Punkte.
- FF-Prüfung wie der IHK-Aufgabensatz: 5 Situationsaufgaben aus `D.ffs` (`data.json`/`data_en.json` Schlüssel `ffs`, positionsgleich, nur anhängen), je Bereich eine zufällige: A Neuwagen 20, B Vertrieb und Markt 12, C Gebrauchtwagen 18, D Finanzierung und Leasing 30, E Versicherung und Garantie 20 Punkte. Jede Situation hat Teilaufgaben `p` mit `k:'o'` (offen, Musterlösung mit Punkteschema, Selbstbewertung in ganzen Punkten) oder `k:'c'` (Rechnen mit `a`, `u`, `d`, Rechenweg `s`), optional Unterlage `f` (wie `qFig`). Neue Situationen müssen die Punktsumme ihres Bereichs genau treffen. `EX.FF.scen`, `scenItems()` in `app.html`.
- Karten-Fragen im IHK-Stil mit Operator in der Sie-Form („Nennen Sie …“, „Erklären Sie …“, „Unterscheiden Sie …“, „Beurteilen Sie …“), keine Stichwort-Fragen. Die Prüfungen nehmen ihre offenen Fragen direkt aus den Karten.
- Gewichtung KUP-Testprüfung wie in den echten Prüfungen 2023–2025: Personal 25 (mit Entgeltabrechnung), Buchführung 30, Kalkulation/KLR/Werkstatt 30, Controlling 15.
- „Kurz erklärt“ (Reiter im Wissen, Route `#kurz`): eine Folie pro Thema in `D.kurz` (`data.json`/`data_en.json` Schlüssel `kurz`, positionsgleich, nur anhängen). Felder: `t` Titel, `s` Untertitel, `g` Grundidee, `b`/`c` Beispiel und Rechnung, `op`/`f` IHK-Frage, `x` Prüfungsfalle, `a` Musterantwort, `m` Merkformel, `k` Karten-Positionen, `r` Rechenarten. Über `k` und `r` erscheint auf Karten und Rechenaufgaben der Knopf „Kurz erklärt“ (`kzPill`, `kurzSheet`). Nicht in Teil 1. Die Reihenfolge in Liste und Weiter/Zurück folgt den Themen (`kzOrd()`), neue Folien also einfach hinten anhängen. `kzFor`/`kzGen` nehmen die erste passende Folie, eine Karte bzw. Rechenart deshalb nur einer Folie zuordnen.
- Laufende und abgegebene Prüfungen liegen unter `eb-exam` (bzw. `eb-exam-ap1`) und speichern ihre Blocknamen in `E.bl`. Neue Blockeinteilungen in `EX` sind damit unkritisch, ältere Prüfungen ohne `E.bl` nutzen `exBl()` mit Ersatznamen. Wirft `vExam` trotzdem einen Fehler, verwirft `route()` die gespeicherte Prüfung und zeigt die Auswahl mit Hinweis.
- Der Hinweis „Neue Aufgaben verfügbar“ (`cvNow()`) reagiert nur auf neue Rechenarten oder Bildgeschichten. Neue Karten und Quizfragen landen automatisch in den Plan-Aufgaben.

## Testen

`quellen/tests/` enthält Playwright-Tests (Chrome unter `/usr/bin/google-chrome`): `crawl*.py` (alle Seiten auf Deutsch und Englisch, Teil 1 und 2), `exfull.py` (alle Prüfungen), `genall.py` (alle Generatoren), `monkey.py` (Zufallsklicks), `kitest.py` (KI-Funktionen mit simuliertem Claude). Die Pfade darin zeigen noch auf die alte Arbeitsumgebung (`/home/claude/out/…`, `/home/claude/exam-buddy/…`). Vor dem ersten Lauf auf `quellen/out/` bzw. die Repo-Wurzel anpassen. Vor jeder Veröffentlichung mindestens die Crawls und `exfull.py` laufen lassen, Erwartung: `errors []`.

## Veröffentlichen

1. `python3 quellen/build.py`, Tests, Commit (Nachricht auf Deutsch: „Version NN: …“), Push auf `main`. Damit ist GitHub Pages aktuell.
2. Die claude.ai-Fassungen werden aus einer claude.ai-Sitzung mit Artefakt-Werkzeugen veröffentlicht: Live-Artefakt „Prüfungstrainer Automobilkaufleute“ (öffentlich) mit `quellen/out/index.html`, Vorschau-Artefakt „Exam Buddy – Vorschau Redesign und Berufsauswahl“ (privat, mit KI-Funktionen) mit `quellen/out/preview.html`.

## Kontakt und Betrieb

- Support- und Einsendeadresse: support@ExamBuddy04.onmicrosoft.com (Microsoft 365).
- Geplante Aufgaben: tägliche Postfach-Prüfung (18:37 Uhr), Meldung neuer Einsendungen aus der Vorschau (9:17 bis 21:17 Uhr, alle 3 Stunden), Erinnerungen am 25.11. (Vorschau live schalten, Postanschrift für Impressum) und 26.11. (eigene Domain).
- Weitere Übergabe-Notizen stehen im claude.ai-Projekt „Exam Buddy“.
