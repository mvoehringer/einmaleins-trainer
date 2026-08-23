#!/bin/sh
# index.html ist die einzige Quelle. artifact.html wird daraus erzeugt:
# derselbe <style>- und <script>-Inhalt, nur ohne doctype/html/head/body —
# diesen Rahmen setzt der Artifact-Host selbst.
#
#   ./build-artifact.sh          neu erzeugen
#   ./build-artifact.sh --check  nur prüfen, ob artifact.html aktuell ist

set -e
cd "$(dirname "$0")"

build() {
  { grep -m1 '<title>' index.html
    sed -n '/^<body>$/,/^<\/body>$/p' index.html | sed '1d;$d'
  }
}

# Vergleicht nur den tragenden Teil — der Rahmen unterscheidet sich absichtlich.
core() { sed -n '/^<style>$/,/^<\/style>$/p;/^<script>$/,/^<\/script>$/p' "$1" | shasum | cut -d' ' -f1; }

if [ "$1" = "--check" ]; then
  [ -f artifact.html ] || { echo "artifact.html fehlt — ./build-artifact.sh ausführen"; exit 1; }
  if [ "$(core index.html)" = "$(core artifact.html)" ]; then
    echo "artifact.html ist aktuell ✓"
  else
    echo "VERALTET: artifact.html weicht von index.html ab — ./build-artifact.sh ausführen"; exit 1
  fi
  exit 0
fi

build > artifact.html
[ "$(core index.html)" = "$(core artifact.html)" ] || { echo "Build fehlgeschlagen"; exit 1; }
python3 pruefe-stufen.py > /dev/null || { python3 pruefe-stufen.py; exit 1; }
echo "artifact.html erzeugt ✓ ($(wc -l < artifact.html | tr -d ' ') Zeilen)"
