#!/usr/bin/env bash
# Builds abconv from an afterburner source tree inside eic_xl, out of source, under the data area.
#   scripts/build-abconv.sh <label> [source tree, default: the afterburner submodule's working tree]
# The binary lands in $WORKBENCH_DATA/build/<label>/abconv/abconv; logs beside it (cmake.log, make.log).
# The source tree must be readable inside the container: the workbench (bound read-only) or the data area.
set -euo pipefail
LABEL=${1:?usage: build-abconv.sh <label> [source tree]}
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SRC=$(cd "${2:-$REPO/afterburner}" && pwd)
DATA=${WORKBENCH_DATA:-/data/afterburner-workbench}
B=$DATA/build/$LABEL
mkdir -p "$B"
git -C "$SRC" log -1 --format='%H %s' > "$B/source.txt" 2>/dev/null || echo "$SRC (not a git tree)" > "$B/source.txt"
git -C "$SRC" diff --stat >> "$B/source.txt" 2>/dev/null || true
"$REPO/scripts/in-eic-xl.sh" "cmake -S $SRC/cpp -B $B -DCMAKE_BUILD_TYPE=Release > $B/cmake.log 2>&1 && cmake --build $B -j\$(( \$(nproc) - 2 )) > $B/make.log 2>&1 && $B/abconv/abconv --version > $B/version.txt 2>&1; rc=\$?; echo build rc=\$rc; exit \$rc"
echo "$B/abconv/abconv"
