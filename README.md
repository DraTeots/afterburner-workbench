# afterburner-workbench

Workbench for repairing the EIC afterburner (`abconv`, [eic/afterburner](https://github.com/eic/afterburner))
against Pythia8 with eicBeamShape ([eic/eicSimuBeamEffects](https://github.com/eic/eicSimuBeamEffects)).

| path | content |
|---|---|
| `afterburner/` | submodule eic/afterburner (main) |
| `eicSimuBeamEffects/` | submodule eic/eicSimuBeamEffects (v1.1), the reference model |
| `generator_benchmarks/` | submodule eic/generator_benchmarks; the afterburner benchmark is on the local branch `afterburner-benchmark` |
| `beam-validation/` | the 2026-11-07 afterburner-vs-Pythia8 study: sign checks, displaced vertices, PR #38 review |
| `scripts/` | run a command in eic_xl, build abconv, run the benchmark against a built abconv |
| `space/` | findings, decisions, questions, reports of the repair program |
| `afterburner-loop.md`, `work-common.md` | the program file and the common rules of an autonomous run |

## Setup

To clone with the submodules:

```bash
git clone --recurse-submodules https://github.com/DraTeots/afterburner-workbench
```

Everything runs inside the `eicweb/eic_xl:26.11.0-stable` image through docker; outputs go to
`/data/afterburner-workbench` (`WORKBENCH_DATA` overrides it).

To build abconv from the afterburner submodule:

```bash
scripts/build-abconv.sh main
```

To run the benchmark's CI selection against that build:

```bash
scripts/run-benchmark.sh main-ci /data/afterburner-workbench/build/main/abconv/abconv
```

The benchmark branch `afterburner-benchmark` exists only in the original checkout until its PR is
opened; a fresh clone has generator_benchmarks at upstream main, without the benchmark.

The summary lands in `/data/afterburner-workbench/bench/main-ci/results/afterburner/summary.md`.
`generator_benchmarks/benchmarks/afterburner/README.md` describes the checks, setups and options.
