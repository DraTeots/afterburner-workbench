#!/usr/bin/env bash
# Runs inside eic_xl (via in-eic-xl.sh). For one beam energy:
#   1. Pythia8 NC DIS from the eicSimuBeamEffects steering file, twice with the same seed:
#      with eicBeamShape beam effects (py8_full) and head-on (momentum and vertex spread off: py8_headon);
#   2. abconv on the head-on file with the IP6 preset (afterburner), and abconv --ab-off on both
#      Pythia8 files (nominal, pythia8): abconv's validation histograms for the three samples;
#   3. the seed check: a second, small pair of files with another Pythia8 seed, and abconv on the
#      first events of each head-on file, written as HepMC3 text for an event-by-event comparison.
#   run-energy.sh <setup> [n_events] [seed] [n_seed_check]     setup: 10x100 | 9x130 | 9x130-hiacc
set -euo pipefail
E=$1; N=${2:-50000}; SEED=${3:-1001}; NS=${4:-2000}
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
STEER_DIR=$REPO/eicSimuBeamEffects/Pythia8/steerFiles
CONFIG=1        # eicBeamShape: 1 = high divergence, 2 = high acceptance
EXTRA=""        # steering lines appended after the file (later settings win)
case $E in
  # 10x100 high divergence: the parameter set abconv gave the 9x100 sample
  # (ip6_hidiv_100x10 = ip6_hidiv_100x9); eicBeamShape has no 9x100.
  10x100) STEER=dis_eicBeam_hiDiv_10x100_10to100; HAD=100; LEP=10; PRESET=ip6_hidiv_100x10 ;;
  # 9x130 high divergence on the Pythia8 side (eicBeamShape copies 10x100 hiDiv) against
  # ip6_ep_130x9 (= ip6_ep_130x10, used by the 9x130 sample), which is abconv's high-acceptance set.
  9x130)  STEER=dis_eicBeam_hiDiv_9x130_10to100;  HAD=130; LEP=9;  PRESET=ip6_ep_130x9 ;;
  # 9x130 matched: eicBeamShape high acceptance. No hiAcc 9x130 steering file exists; the hiAcc
  # 10x100 file at 9x130 energies is the copy eicBeamShape itself makes for 9x130.
  9x130-hiacc) STEER=dis_eicBeam_hiAcc_10x100; HAD=130; LEP=9; PRESET=ip6_ep_130x9; CONFIG=2
               EXTRA=$'Beams:eA = 130\nBeams:eB = 9\nPhaseSpace:Q2Min = 10.0\nPhaseSpace:Q2Max = 100.0\n' ;;
  *) echo "unknown setup $E (10x100 | 9x130 | 9x130-hiacc)" >&2; exit 2 ;;
esac
XANGLE=-0.025   # IP6 crossing angle in rad; negative at IP6 (eicSimuBeamEffects README)
mkdir -p "$E/logs" && cd "$E"

steer() {  # steer <out.cmnd> <n_events> <seed> <headon 0|1>
  { cat "$STEER_DIR/$STEER"
    printf '\n! beam-validation overrides\nMain:numberOfEvents = %d\nRandom:setSeed = on\nRandom:seed = %d\n' "$2" "$3"
    printf '%s' "$EXTRA"
    if [ "$4" = 1 ]; then printf 'Beams:allowMomentumSpread = off\nBeams:allowVertexSpread = off\n'; fi
  } > "$1"
}
steer full.cmnd     "$N"  "$SEED"       0
steer headon.cmnd   "$N"  "$SEED"       1
steer full_s2.cmnd  "$NS" "$((SEED+1))" 0
steer headon_s2.cmnd "$NS" "$((SEED+1))" 1

for s in full headon full_s2 headon_s2; do
  runBeamShapeHepMC $s.cmnd $CONFIG $HAD $LEP $XANGLE py8_$s.qa.root py8_$s.hepmc > logs/py8_$s.log 2>&1 &
done
wait

abconv py8_headon.hepmc -p $PRESET -f none -o afterburner > logs/ab_afterburner.log 2>&1 &
abconv py8_headon.hepmc --ab-off -f none -o nominal      > logs/ab_nominal.log 2>&1 &
abconv py8_full.hepmc   --ab-off -f none -o pythia8      > logs/ab_pythia8.log 2>&1 &
abconv py8_headon.hepmc    -p $PRESET -l "$NS" -f hepmc3 --plot-off -o seedcheck_ab_s1 > logs/ab_seedcheck_s1.log 2>&1 &
abconv py8_headon_s2.hepmc -p $PRESET -l "$NS" -f hepmc3 --plot-off -o seedcheck_ab_s2 > logs/ab_seedcheck_s2.log 2>&1 &
wait

printf 'energy=%s n_events=%s seed=%s n_seed_check=%s steer=%s preset=%s xangle=%s config=%s image=%s\n' \
  "$E" "$N" "$SEED" "$NS" "$STEER" "$PRESET" "$XANGLE" "$CONFIG" "${EIC_XL_IMAGE:-eicweb/eic_xl:26.11.0-stable}" > run.txt
ls -la
