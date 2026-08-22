# Einmaleins-Trainer — Konzept & Umsetzungsplan

## Context

Für eine 8-jährige (3. Klasse) soll das kleine Einmaleins (1×1 bis 10×10) **auswendig** sitzen —
nicht ausgerechnet, sondern abgerufen. Ziel ist Automatisierung: Antwort in unter ~5 Sekunden,
ohne Abzählen oder Hochrechnen über die Reihe.

Die App soll im Browser laufen, den Fortschritt pro Aufgabe merken und gezielt die Lücken
trainieren statt stumpf alle 100 Fakten gleich oft abzufragen.

Repo ist leer (kein Commit) — grüne Wiese.

**Entscheidungen (mit dem User geklärt):** Zahlen eintippen (kein Multiple Choice),
Handy + Laptop, eine einzelne `index.html` ohne Build-Schritt.

---

## Teil 1: Pädagogisches Konzept

Sechs Prinzipien, die den Algorithmus und das UI bestimmen. Jedes hat eine direkte
Entsprechung im Code.

### 1. Abruf statt Wiedererkennen
Antwort wird **eingetippt**, nie ausgewählt. Multiple Choice lässt sich durch Plausibilitäts-Raten
lösen und trainiert das Gedächtnis nachweislich schwächer.

### 2. Zeit ist das eigentliche Beherrschungs-Signal
Der zentrale Punkt der ganzen App: **„richtig" reicht nicht.** Ein Kind, das 7×8 in 9 Sekunden
richtig löst, hat 7×7=49, +7 gerechnet — es hat den Fakt *nicht* auswendig. Bewertung:

| Antwort | Bewertung | Folge |
|---|---|---|
| richtig, < 5 s | **automatisiert** | Box hoch |
| richtig, 5–8 s | ok, aber gerechnet | Box bleibt |
| richtig, > 8 s | gerechnet | Box bleibt, gilt nicht als Erfolg |
| falsch | Lücke | Box zurück auf 1 |

Die Zeit wird gemessen und ausgewertet, dem Kind aber **nie als Countdown oder Wettrennen
angezeigt**. Sichtbarer Zeitdruck erzeugt Mathe-Angst und blockiert genau den Abruf,
den wir trainieren wollen. Der Timer ist ein Messgerät, kein Gegner.

### 3. Leitner-Boxen (leichtgewichtiges Spaced Repetition)
100 Fakten sind zu wenig für SM-2-Komplexität. 5 Boxen reichen:

```
Box 1: jede Session      (Lücke — hart trainieren)
Box 2: jede 2. Session
Box 3: alle 4 Sessions
Box 4: alle 8 Sessions
Box 5: alle 16 Sessions  (sitzt — nur noch auffrischen)
```

Aufstieg nur bei **richtig UND schnell** (siehe 2). Bei Fehler: zurück auf Box 1.
Das ist die „Lücken gezielt trainieren"-Mechanik in ihrer einfachsten funktionierenden Form.

### 4. Interleaving, nicht reihenweise
Nicht „die ganze 7er-Reihe der Reihe nach" — das trainiert Weiterzählen (7, 14, 21, …),
nicht Abruf. Aufgaben kommen **gemischt**. Es gibt einen optionalen „Reihe üben"-Modus
für die Neueinführung einer Reihe, aber der Standard-Modus ist gemischt.

### 5. Die schweren 20 kennen
Nicht alle 100 Fakten sind gleich schwer. `×1, ×2, ×5, ×10` sind fast geschenkt.
Wirklich hart ist eine kleine Gruppe: **6×7, 7×8, 6×8, 7×9, 8×9, 4×7, 3×8, 6×9, 4×8, 3×7**
und ihre Vertauschungen. Die App kennt diese Gewichtung von Anfang an (Startbox nach
Schwierigkeit vorbelegt), damit die erste Session nicht mit 1×3 und 10×5 verschwendet wird.

Kommutativität: `3×7` und `7×3` sind **eigene Items**. Kinder übertragen das nicht
automatisch — beide Richtungen müssen sitzen.

### 6. Fehler sind harmlos, aber sie kommen wieder
Bei Fehler: kein rotes Kreuz, kein Ton, kein Punktabzug. Ruhige Anzeige der richtigen
Antwort („7 × 8 = **56**"), und dieselbe Aufgabe kommt **3–4 Aufgaben später nochmal**
in derselben Session (Korrektur-Wiederholung) — das ist der wirksamste Einzelmechanismus
gegen Wiederholungsfehler.

### Session-Design
- **20 Aufgaben, ~4 Minuten.** Kurz und täglich schlägt lang und selten.
- Erste 2 Aufgaben bewusst leicht (Einstieg mit Erfolgserlebnis).
- Nach 2 schweren Aufgaben eine leichte einstreuen (Frust-Bremse).
- Am Ende: alle in dieser Session falsch beantworteten Fakten nochmal.
- Abschluss-Screen: „18 von 20 richtig · 3 neue Aufgaben sitzen jetzt" + Streak-Zähler.

### Fortschritt sichtbar machen
Ein **10×10-Gitter als Landkarte** — jede Zelle in der Farbe ihrer Box (grau → grün).
Das Kind sieht auf einen Blick, wie viel schon „erobert" ist, und es ist gleichzeitig
die Eltern-Ansicht: welche Fakten sitzen, welche nicht.

Keine Punkte-Ökonomie, keine Coins, keine Shop-Mechanik — das lenkt auf die Belohnung
statt auf den Inhalt.

---

## Teil 2: Umsetzung

### Architektur

**Eine Datei: `index.html`.** Vanilla JS, kein Framework, kein Build, kein npm.
Öffnet per Doppelklick, läuft offline, funktioniert auf Handy und Laptop.
Fortschritt in `localStorage`.

Begründung: der komplette Zustand sind 100 kleine Objekte und der komplette
UI-Zustand ist „welche Aufgabe steht gerade da". Dafür braucht es kein React.

```
Kopfrechen/
└── index.html      # alles: HTML, CSS, JS
```

### Datenmodell (localStorage, Key `einmaleins.v1`)

```js
{
  facts: {
    "7x8": { box: 1, lastSession: 12, times: [4200, 3100], wrong: 3 },
    ...   // 100 Einträge, a×b für a,b ∈ 1..10
  },
  session: 14,        // laufende Session-Nummer, treibt die Box-Fälligkeit
  streak: 5,          // Tage in Folge
  lastDay: "2026-08-22"
}
```

`times` nur die letzten ~5 Werte (Ringpuffer) — reicht für „wird schneller?".

### Kernfunktionen

| Funktion | Aufgabe |
|---|---|
| `loadState()` / `saveState()` | localStorage, mit Fallback auf Startzustand |
| `seedFacts()` | 100 Fakten anlegen, Startbox nach Schwierigkeit (leicht → Box 3, hart → Box 1) |
| `dueFacts()` | alle Fakten mit `session - lastSession >= interval(box)` |
| `pickNext()` | wählt die nächste Aufgabe: fällig zuerst, Fehler-Queue eingeschoben, Frust-Bremse |
| `grade(fact, answer, ms)` | die Tabelle aus Prinzip 2 → Box hoch / bleibt / zurück auf 1 |
| `renderGrid()` | 10×10-Fortschrittsgitter, Zellfarbe = Box |

`pickNext()` ist die einzige nicht-triviale Logik und bekommt den Test.

### UI — drei Screens

**1. Start**
Großer Button „Los geht's". Darunter das 10×10-Gitter und der Streak.
Klein: „Reihe üben" (Auswahl 1–10) für gezieltes Reihen-Training.

**2. Aufgabe**

```
┌─────────────────────┐
│  ●●●●●○○○○○  6/20   │   Fortschrittspunkte, kein Timer
│                     │
│      7 × 8          │   sehr groß
│      = 5_           │
│                     │
│   ┌───┬───┬───┐     │   großes Touch-Zahlenpad
│   │ 1 │ 2 │ 3 │     │   (Desktop: Tastatur tut es auch,
│   │ 4 │ 5 │ 6 │     │    Enter = ✓, Backspace = ⌫)
│   │ 7 │ 8 │ 9 │     │
│   │ ⌫ │ 0 │ ✓ │     │
│   └───┴───┴───┘     │
└─────────────────────┘
```

Richtig → kurzes grünes Aufblitzen, sofort weiter.
Falsch → ruhig „7 × 8 = **56**", 2 s stehen lassen, weiter.

**3. Ende**
„18 von 20 · 3 Aufgaben sitzen jetzt neu · 🔥 6 Tage in Folge" + aktualisiertes Gitter.

### Gestaltung
- Ein Bildschirm, kein Scrollen — weder auf dem Handy noch auf dem Laptop.
- Zahlen sehr groß, Touch-Ziele mind. 60 px.
- Ruhige, freundliche Farben; grün/grau statt rot/grün (Farbfehlsichtigkeit + Rot=Gefahr-Assoziation).
- `user-select: none`, `touch-action: manipulation` gegen versehentliches Markieren/Zoomen.
- Zahlenpad-Layout Telefon-Stil (1 oben), passend zur Ziffernblock-Erwartung von Kindern.

### Umsetzungsschritte

1. `index.html`-Grundgerüst: State, `seedFacts()`, Aufgaben-Screen, Zahlenpad, Tastatur.
   → **Lauffähig: Aufgaben kommen zufällig, Antwort wird geprüft.**
2. Leitner-Logik: `grade()` mit Zeitschwellen, `dueFacts()`, `pickNext()` mit Fehler-Queue
   und Frust-Bremse. localStorage-Persistenz.
3. Session-Rahmen: 20 Aufgaben, Nachhol-Runde für Fehler, Ende-Screen, Streak.
4. Fortschrittsgitter + Start-Screen + „Reihe üben".
5. Selbst-Test (siehe unten).

### Verifikation

**Automatisch** — eine `test.html` neben der App (ponytail: keine Test-Runner-Installation,
öffnen im Browser, Konsole zeigt Ergebnis). Die Funktionen aus `index.html` werden dafür
über `window.__einmaleins` zugänglich gemacht. Geprüft wird:

- `grade()`: richtig+schnell steigt auf, richtig+langsam bleibt, falsch fällt auf Box 1
- `dueFacts()`: Box 5 ist nach 3 Sessions nicht fällig, nach 16 schon
- `pickNext()`: liefert nie zweimal direkt dieselbe Aufgabe; falsch beantwortete Aufgabe
  taucht innerhalb der nächsten 5 Aufgaben wieder auf
- `seedFacts()`: genau 100 Fakten, 7×8 startet in einer niedrigeren Box als 2×5

**Manuell** — eine echte Session durchspielen:
1. `index.html` im Browser öffnen, 20 Aufgaben lösen, dabei 2 bewusst falsch beantworten
   → beide müssen in der Session nochmal kommen.
2. Bei einer Aufgabe absichtlich ~10 s warten und richtig antworten → Gitterfarbe darf
   sich nicht verbessern.
3. Seite neu laden → Gitter und Streak sind identisch (localStorage hält).
4. Auf dem Handy öffnen → alles auf einem Bildschirm, kein Zoom nötig, Zahlenpad
   mit dem Daumen erreichbar.

---

## Bewusst weggelassen

- **Kein Framework/Build** — 100 Fakten und ein Screen brauchen kein React.
  Nachrüsten, wenn die App mal mehrere Rechenarten und Nutzerprofile bekommt.
- **Kein SM-2/Anki-Algorithmus** — 5 Leitner-Boxen reichen bei 100 Items.
- **Kein Backend/Login** — localStorage genügt, solange auf einem Gerät geübt wird.
  Ein „Fortschritt exportieren"-Button (JSON in die Zwischenablage) ist die
  Zwei-Zeilen-Versicherung gegen Datenverlust und kommt in Schritt 4 mit rein.
- **Kein Sound** — nachrüstbar, aber oft eher störend beim Üben (und am Tisch neben anderen).
- **Nur Multiplikation** — Division (56 : 7) ist der naheliegende nächste Schritt,
  läuft auf demselben Datenmodell, aber erst wenn das Einmaleins sitzt.
