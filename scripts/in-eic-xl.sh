#!/usr/bin/env bash
# Runs one shell command inside the local eic_xl image (docker).
# The workbench is bound read-only and the data area read-write, both at their host paths;
# files are written as the calling user, and the command starts in the data area.
#   scripts/in-eic-xl.sh 'abconv --version'
# EIC_XL_IMAGE and WORKBENCH_DATA override the image and the data area.
set -euo pipefail
IMAGE=${EIC_XL_IMAGE:-eicweb/eic_xl:26.11.0-stable}
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DATA=${WORKBENCH_DATA:-/data/afterburner-workbench}
mkdir -p "$DATA"
exec docker run --rm -u "$(id -u):$(id -g)" -e HOME=/tmp -e WORKBENCH_DATA="$DATA" \
  -v "$REPO:$REPO:ro" -v "$DATA:$DATA" -w "$DATA" \
  "$IMAGE" bash -lc "$*" 2> >(grep -v "^stty: 'standard input'" >&2)
