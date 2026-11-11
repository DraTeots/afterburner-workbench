#!/usr/bin/env bash
# Runs the generator_benchmarks afterburner benchmark inside eic_xl against one abconv.
#   scripts/run-benchmark.sh <label> <abconv> [snakemake arguments...]
#     <abconv>  "container" for the image's abconv, or the path of a built binary (scripts/build-abconv.sh)
# The Snakefiles use paths relative to the working directory, so the benchmark runs in a copy:
# $WORKBENCH_DATA/bench/<label>/ (code re-synced on every call; sim_output/ and results/ stay).
# Snakemake does not track the abconv binary: after a rebuild, use a new label or pass --forcerun afterburner_abconv.
# Example, the full matrix: scripts/run-benchmark.sh main-full $DATA/build/main/abconv/abconv \
#   --config AFTERBURNER_SETUPS=all AFTERBURNER_N_EVENTS=20000
set -euo pipefail
LABEL=${1:?usage: run-benchmark.sh <label> <abconv|container> [snakemake args]}
ABCONV=${2:?usage: run-benchmark.sh <label> <abconv|container> [snakemake args]}
shift 2
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DATA=${WORKBENCH_DATA:-/data/afterburner-workbench}
W=$DATA/bench/$LABEL
# The benchmark lives on the submodule's local branch afterburner-benchmark; `git submodule update` resets the
# checkout to upstream main, where Snakemake would only report "no rule afterburner".
[ -f "$REPO/generator_benchmarks/benchmarks/afterburner/Snakefile" ] || {
  echo "generator_benchmarks has no benchmarks/afterburner: run git -C $REPO/generator_benchmarks checkout afterburner-benchmark" >&2; exit 2; }
mkdir -p "$W"
rsync -a --delete --exclude=.git --exclude=sim_output --exclude=results --exclude=logs --exclude=.snakemake \
  "$REPO/generator_benchmarks/" "$W/"
git -C "$REPO/generator_benchmarks" log -1 --format='generator_benchmarks %H %D' > "$W/source.txt"
if [ "$ABCONV" = container ]; then
  PATHSET=""
else
  ABCONV=$(cd "$(dirname "$ABCONV")" && pwd)/$(basename "$ABCONV")
  [ -x "$ABCONV" ] || { echo "not an executable: $ABCONV" >&2; exit 2; }
  PATHSET="export PATH=$(dirname "$ABCONV"):\$PATH;"
  echo "abconv $ABCONV" >> "$W/source.txt"
fi
ARGS=""
[ $# -gt 0 ] && ARGS=$(printf ' %q' "$@")   # printf with no arguments would emit one empty target
"$REPO/scripts/in-eic-xl.sh" "$PATHSET cd $W && echo abconv: \$(command -v abconv) && snakemake --cores \$(( \$(nproc) - 2 )) afterburner$ARGS"
echo "results: $W/results/afterburner/summary.md"
