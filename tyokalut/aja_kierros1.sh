#!/usr/bin/env bash
# Kierroksen 1 kehitysjakson ajot omistajan koneella (WSL), peräkkäin.
# Käyttö STROMO4-tutkimuskansiossa:  bash ~/stromo-builder/tyokalut/aja_kierros1.sh
# Ajot näkyvät tutkimussivulla (data/research/runs/k1-*). Valmiit ohitetaan,
# joten keskeytyksen jälkeen sama komento jatkaa siitä mihin jäi.
set -uo pipefail
BUILDER=${BUILDER:-$HOME/stromo-builder}
PAIR=BTC-USDT
START=2025-11-01
END=2026-07-31
CHECK_DAY=2026-01-02
RUNS=data/research/runs
LOG=$RUNS/k1-ajot.log
[[ -f research/replay.py ]] || { echo "Aja STROMO4-tutkimuskansiossa (~/stromo4-tutkimus)." >&2; exit 1; }
mkdir -p "$RUNS"
git -C "$BUILDER" pull -q --ff-only || { echo "STROMO-BUILDERin päivitys epäonnistui." >&2; exit 1; }
lukitus=$(git -C "$BUILDER" rev-parse --short HEAD)

# tekijä/tiedosto parametri=arvo (tyhjä = vain oletus). Vuorotellen tekijöittäin.
AJOT=(
  "claude/uupumus liike_sigma=2"
  "gpt/virtakaannos virtaraja=95"
  "claude/isot_liput maara_p=50"
  "gpt/virtapaine_jatkuu virtaraja=97"
  "claude/likviditeettihaku jakso=14400"
  "gpt/pienkauppa_ylireagointi kaupparaja=92"
  "claude/uupumus liike_sigma=2.5"
  "gpt/virtakaannos virtaraja=97"
  "claude/isot_liput maara_p=35"
  "gpt/virtapaine_jatkuu virtaraja=98"
  "claude/likviditeettihaku jakso=86400"
  "gpt/pienkauppa_ylireagointi kaupparaja=94"
  "omistaja/absorptio ikkuna=600"
  "omistaja/absorptio ikkuna=300"
  "omistaja/absorptio ikkuna=1200"
  "omistaja/pyyhkaisy persentiili=99.9"
  "omistaja/pyyhkaisy persentiili=99.5"
)

echo "$(date -Is) aloitus, STROMO-BUILDER $lukitus" | tee -a "$LOG"
for rivi in "${AJOT[@]}"; do
  read -r polku param <<<"$rivi"
  tiedosto="$BUILDER/stromot/$polku.py"
  nimi=${polku//\//-}
  id="k1-$nimi-${param//[=.]/_}"
  if [[ -f "$RUNS/$id/summary.md" ]]; then
    echo "ohitetaan valmis $id" | tee -a "$LOG"; continue
  fi
  echo "$(date -Is) tarkistus $id" | tee -a "$LOG"
  if ! uv run --group research python -m research.check_stromo "$tiedosto" \
      --day "$CHECK_DAY" --pair "$PAIR" --param "$param" >>"$LOG" 2>&1; then
    echo "$(date -Is) TARKISTUS EPÄONNISTUI $id – ks. loki, jatketaan seuraavaan" | tee -a "$LOG"
    continue
  fi
  echo "$(date -Is) ajo $id" | tee -a "$LOG"
  if uv run --group research python -m research.replay --stromo "$nimi" --stromo-file "$tiedosto" \
      --pair "$PAIR" --start "$START" --end "$END" --param "$param" --output "$RUNS/$id" >>"$LOG" 2>&1; then
    echo "$(date -Is) valmis $id" | tee -a "$LOG"
  else
    echo "$(date -Is) AJO EPÄONNISTUI $id – ks. loki" | tee -a "$LOG"
  fi
done
echo "$(date -Is) kaikki käsitelty" | tee -a "$LOG"
