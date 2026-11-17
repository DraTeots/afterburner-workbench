#!/usr/bin/env bash
# Builds eicSimuBeamEffects' Pythia8 programs (runBeamShapeHepMC, runBeamShape, libeicBeamShape) inside eic_xl from a
# copy of a source tree: its CMake writes bin/ and lib/ into the source tree, which is read-only in the container.
#   scripts/build-eicsim.sh <label> [source tree, default: the eicSimuBeamEffects submodule's working tree]
# Copy and build land in $WORKBENCH_DATA/eicsim/<label>/ (Pythia8/bin/runBeamShapeHepMC, Pythia8/lib/, steerFiles).
set -euo pipefail
LABEL=${1:?usage: build-eicsim.sh <label> [source tree]}
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SRC=$(cd "${2:-$REPO/eicSimuBeamEffects}" && pwd)
DATA=${WORKBENCH_DATA:-/data/afterburner-workbench}
B=$DATA/eicsim/$LABEL
mkdir -p "$B"
rsync -a --delete --exclude=.git --exclude=build --exclude=bin --exclude=lib "$SRC/" "$B/"
"$REPO/scripts/in-eic-xl.sh" "cd $B/Pythia8 && cmake -S . -B build -DCMAKE_BUILD_TYPE=Release > cmake.log 2>&1 && cmake --build build -j8 > make.log 2>&1; rc=\$?; echo build rc=\$rc; ls bin lib 2>/dev/null; exit \$rc"
echo "$B/Pythia8/bin/runBeamShapeHepMC"
