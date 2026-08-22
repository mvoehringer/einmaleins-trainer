# Einmaleins-Trainer

Kleine Web-App zum Üben des kleinen Einmaleins (1×1 bis 10×10) für die 3. Klasse.
Läuft im Browser, merkt sich den Fortschritt und trainiert gezielt die Lücken.

**→ [App öffnen](https://mvoehringer.github.io/einmaleins-trainer/)**
Auf dem iPhone in Safari öffnen → Teilen → *Zum Home-Bildschirm*.

## Wie es funktioniert

Nicht „richtig oder falsch", sondern **wie schnell**. Wer 7×8 nach acht Sekunden
richtig hat, hat gerechnet statt abgerufen — das zählt weniger. Unter 5 Sekunden
gilt als auswendig gewusst.

| Antwort | Farbstufen |
|---|---|
| richtig, unter 5 s | +2 |
| richtig, aber gerechnet | +1 |
| falsch | −3 (nie unter null) |

Die Landkarte zeigt in zehn Stufen, was schon sitzt. Fünf schnelle Treffer
füllen ein Feld. Davon getrennt läuft die Wiedervorlage nach Leitner-Boxen
(1 · 2 · 4 · 8 · 16 Runden Pause), die entscheidet, *wann* eine Aufgabe drankommt.

Eine Runde sind 20 Aufgaben, rund vier Minuten. Falsch beantwortete Aufgaben
kommen drei Aufgaben später nochmal — innerhalb derselben Runde.

## Dateien

| | |
|---|---|
| `index.html` | die ganze App: HTML, CSS, JS. Keine Abhängigkeiten, kein Build |
| `artifact.html` | daraus erzeugt für die Veröffentlichung als Claude-Artifact |
| `build-artifact.sh` | erzeugt sie; `--check` prüft, ob beide synchron sind |
| `manifest.json`, `sw.js`, `icon.png` | Installation als App, Offline-Betrieb |
| `Plans/` | pädagogisches Konzept und Umsetzungsplan |

`index.html` ist die einzige Quelle — Änderungen immer dort, danach `./build-artifact.sh`.

## Tests

`index.html#test` im Browser öffnen: 38 Selbst-Tests laufen durch, das Ergebnis
steht auf der Seite und in der Konsole. Kein Test-Runner, keine Installation.

## Fortschritt

Liegt im `localStorage` des Browsers, pro Gerät getrennt. „Sicherungskopie kopieren"
auf der Startseite legt den Stand als JSON in die Zwischenablage.
