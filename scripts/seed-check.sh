#!/usr/bin/env bash
# Checks abconv's beam-effects seed on two head-on HepMC3 files (A and B, e.g. Pythia8 seeds s and s+1):
#   - the base abconv gives A and B the same interaction points (the fixed seed);
#   - the tested abconv with --seed 1 writes the base's events byte for byte, and the seed into the run info;
#   - without --seed every run draws its own seed: A and B get different interaction points;
#   - --seed <drawn seed> reproduces a run byte for byte;
#   - one --seed on A and B repeats the interaction points, as documented.
#   scripts/seed-check.sh <abconv tested> <abconv base> <head-on A.hepmc> <head-on B.hepmc> <out dir> [preset]
# The out dir must be under the data area (the container writes there). Prints one line per check.
set -euo pipefail
TESTED=${1:?usage}; BASE=${2:?usage}; INPUT_A=${3:?usage}; INPUT_B=${4:?usage}; OUT=${5:?usage}
PRESET=${6:-ip6_hidiv_100x10}
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
mkdir -p "$OUT"

# run <abconv> <input> <output base> [abconv options...]: abconv's stdout goes to <output base>.log
run() {
  local abconv=$1 input=$2 output=$3; shift 3
  "$REPO/scripts/in-eic-xl.sh" "$abconv -p $PRESET -f hepmc3 --plot-off -o $OUT/$output $* $input > $OUT/$output.log 2>&1"
}

# same_ip_fraction <file 1> <file 2>: of the events both files have (in order), the fraction with identical
# interaction points (the E line after @)
same_ip_fraction() {
  paste -d '|' <(grep '^E ' "$1" | sed 's/.*@//') <(grep '^E ' "$2" | sed 's/.*@//') |
    awk -F '|' '$1 != "" && $2 != "" {n++; if ($1 == $2) same++} END {printf "%d of %d (%.3f)", same, n, same / n}'
}

# same_beams_fraction <file 1> <file 2>: the same for the beam four-vectors (P lines with status 4:
# P id parent pdg px py pz e m status), equal within 1e-9 GeV: head-on Pythia8 beams differ between events
# at the 1e-15 rounding level, so exact text comparison would call identical configurations different.
beams_per_event() {
  awk '/^E / {if (n) print line; line = ""; n++} /^P / && $NF == 4 {line = line " " $5 " " $6 " " $7 " " $8} END {print line}' "$1"
}
same_beams_fraction() {
  paste -d '|' <(beams_per_event "$1") <(beams_per_event "$2") |
    awk -F '|' '$1 != "" && $2 != "" {
      n++; count_1 = split($1, first, " "); count_2 = split($2, second, " "); equal = (count_1 == count_2)
      for (i = 1; i <= count_1 && equal; i++) { difference = first[i] - second[i]; if (difference > 1e-9 || difference < -1e-9) equal = 0 }
      same += equal
    } END {printf "%d of %d (%.3f)", same, n, same / n}'
}

events() { sed -n '/^E /,$p' "$1"; }
drawn_seed() { sed -n 's/^Random seed \([0-9]*\) was drawn.*/\1/p' "$1"; }

run "$BASE" "$INPUT_A" base_a
run "$BASE" "$INPUT_B" base_b
run "$TESTED" "$INPUT_A" seed1_a --seed 1
run "$TESTED" "$INPUT_A" random_a
run "$TESTED" "$INPUT_A" random_a_again
run "$TESTED" "$INPUT_B" random_b
SEED_A=$(drawn_seed "$OUT/random_a.log")
run "$TESTED" "$INPUT_A" reproduce_a --seed "$SEED_A"
run "$TESTED" "$INPUT_A" seed7_a --seed 7
run "$TESTED" "$INPUT_B" seed7_b --seed 7

echo "base, same IP on A and B:                 $(same_ip_fraction "$OUT/base_a.hepmc" "$OUT/base_b.hepmc")"
echo "base, same beams on A and B:              $(same_beams_fraction "$OUT/base_a.hepmc" "$OUT/base_b.hepmc")"
if cmp -s <(events "$OUT/base_a.hepmc") <(events "$OUT/seed1_a.hepmc"); then echo "--seed 1 events vs base:                  identical"
else echo "--seed 1 events vs base:                  DIFFERENT"; fi
echo "--seed 1 run info lines added:            $(diff <(grep '^A ' "$OUT/base_a.hepmc") <(grep '^A ' "$OUT/seed1_a.hepmc") | grep '^>' | tr '\n' ' ')"
echo "drawn seeds A, A again, B:                $SEED_A $(drawn_seed "$OUT/random_a_again.log") $(drawn_seed "$OUT/random_b.log")"
echo "no --seed, same IP on A twice:            $(same_ip_fraction "$OUT/random_a.hepmc" "$OUT/random_a_again.hepmc")"
echo "no --seed, same IP on A and B:            $(same_ip_fraction "$OUT/random_a.hepmc" "$OUT/random_b.hepmc")"
echo "no --seed, same beams on A and B:         $(same_beams_fraction "$OUT/random_a.hepmc" "$OUT/random_b.hepmc")"
if cmp -s "$OUT/random_a.hepmc" "$OUT/reproduce_a.hepmc"; then echo "--seed $SEED_A vs the run that drew it:   byte-identical"
else echo "--seed $SEED_A vs the run that drew it:   DIFFERENT"; fi
echo "--seed 7, same IP on A and B:             $(same_ip_fraction "$OUT/seed7_a.hepmc" "$OUT/seed7_b.hepmc")"
echo "run info seed of the drawn run:           $(grep '^A ab_random_seed' "$OUT/random_a.hepmc")"
