#!/usr/bin/env bash
# LIIGAn yöajo pelikoneella: päivittää lukitut stromot mainista, ajaa jonon,
# tekee raportin ja vie tilastot haaraan tulokset/<aika>. Windowsin ajastin käynnistää.
set -uo pipefail
source "$HOME/.local/bin/env"
cd "$HOME/stromo4-tutkimus" || exit 1
mkdir -p data/research/liiga
exec >>data/research/liiga/yoajo.log 2>&1
echo "=== $(date -Is) yöajo alkaa"
if pgrep -f "research.replay" >/dev/null; then
  echo "Toinen ajo on jo käynnissä; ohitetaan tämä yö."
  exit 0
fi
git -C "$HOME/stromo-builder" checkout -q main && git -C "$HOME/stromo-builder" pull -q --ff-only
python3 "$HOME/stromo-builder/liiga/liiga.py" yo
echo "=== $(date -Is) yöajo päättyi"
