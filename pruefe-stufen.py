#!/usr/bin/env python3
"""Wächter gegen einen Fehler, der zweimal passiert ist (.map div, .steps b):
eine Regel mit Elementselektor überstimmt die .sN-Stufenklassen, und die
Übersicht bleibt grau, obwohl die Daten stimmen."""
import re, sys

s   = open('artifact.html', encoding='utf-8').read()
css = re.search(r'<style>(.*?)</style>', s, re.S).group(1)
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)   # Kommentare raus, sonst
                                                    # kleben sie am Selektor
js  = re.search(r'<script>(.*?)</script>', s, re.S).group(1)

def spez(sel):
    ids = len(re.findall(r'#[\w-]+', sel))
    kl  = len(re.findall(r'\.[\w-]+|\[[^\]]+\]|:[\w-]+\(', sel))
    el  = len(re.findall(r'(?:^|[\s>+~])([a-z]+[0-9]?)(?![\w-])', sel))
    return (ids, kl, el)

# Container, in denen das JS Stufenklassen vergibt
CONTAINER = ['.map', '.steps', '.legend']
STUFE = spez('.s5')

# Setzt die Regel wirklich eine Hintergrundfarbe (und nicht bloß eine Transition)?
def setzt_hintergrund(body):
    for d in body.split(';'):
        name, _, wert = d.partition(':')
        if name.strip() in ('background', 'background-color') and wert.strip():
            return True
    return False

# Nur das letzte Segment zählt: es muss ein blanker Elementname sein
# (.map .hd oder .steps div:hover zielen nicht auf die farbtragenden Elemente).
def endet_auf_element(sel):
    letztes = re.split(r'[\s>+~]+', sel.strip())[-1]
    return bool(re.fullmatch(r'[a-z]+[0-9]?', letztes))

schuldig = []
for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
    sel, body = m.group(1).strip(), m.group(2)
    if sel.startswith('@') or sel.startswith(':root'): continue
    if re.match(r'\s*\.s\d', sel): continue
    if not setzt_hintergrund(body): continue
    if spez(sel) <= STUFE: continue
    for teil in sel.split(','):
        teil = teil.strip()
        if any(teil.startswith(c) for c in CONTAINER) and endet_auf_element(teil):
            schuldig.append((teil, spez(teil)))

print(f"Stufenklassen werden vergeben in: {', '.join(CONTAINER)}")
print(f"Spezifität einer .sN-Regel: {STUFE}")
if schuldig:
    print("\n✗ Diese Regeln übermalen die Stufenfarbe:")
    for sel, sp in schuldig: print(f"    {sel}  {sp}")
    sys.exit(1)
print("✓ keine Regel übermalt die Stufenfarben")

# Gegenprobe: greift der Wächter überhaupt?
probe = css + "\n.steps b{background:var(--s0)}"
treffer = [t.strip() for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', probe)
           for t in m.group(1).split(',')
           if setzt_hintergrund(m.group(2)) and not re.match(r'\s*\.s\d', t.strip())
           and spez(t.strip()) > STUFE
           and any(t.strip().startswith(c) for c in CONTAINER)
           and endet_auf_element(t.strip())]
print("Gegenprobe (künstlicher Fehler eingebaut):",
      "erkannt ✓" if treffer else "NICHT erkannt ✗")
