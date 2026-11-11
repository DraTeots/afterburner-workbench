#!/usr/bin/env bash
# Run one shell command inside the local eic_xl image.
# The repository is bound read-only and the output area read-write, both at their host paths;
# files are written as the calling user.
#   beam-validation/in-eic-xl.sh 'abconv --version'
set -euo pipefail
IMAGE=${EIC_XL_IMAGE:-eicweb/eic_xl:26.11.0-stable}
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
OUT=${BEAMVAL_OUT:-/data/afterburner-workbench/beam-validation}
mkdir -p "$OUT"
exec docker run --rm -u "$(id -u):$(id -g)" -e HOME=/tmp \
  -v "$REPO:$REPO:ro" -v "$OUT:$OUT" -w "$OUT" \
  "$IMAGE" bash -lc "$*" 2> >(grep -v "^stty: 'standard input'" >&2)
