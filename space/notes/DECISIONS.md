# Decisions

## User

- D-user-1 (2026-11-11, user, Q1): the workbench's submodules are afterburner, eicSimuBeamEffects ("pythia with beam effects") and generator_benchmarks, at the repository root ("No need for creating submodules folder"); no Pythia8 source.
- D-user-2 (2026-11-11, user, Q2): "direct clone, local branches. pushes as PRs." The submodules clone the eic repositories; work stays on local branches; a branch leaves the machine only as a PR.
- D-user-3 (2026-11-11, user, Q3): scope = the study's findings plus the tracker issues on presets and energies (#16, #17, #34, #5, #4).
- D-user-4 (2026-11-11, user, Q4, Q6): F2 gets the root fix (no convention flip), and "The root fix must be based on Dmitry K PR" (#38); the repairs build on PR #38.
- D-user-5 (2026-11-11, user, Q5): the vertical luminous width (F5): "Record and prepare an issue."
- D-user-6 (2026-11-11, user, Q5): "All PRs and work must be separated. All findings will go to new issues and PRs": one finding, one branch, one issue, one PR.
- D-user-7 (2026-11-08, user, dis-autoresearch session): the missing beam energy spread stays a failing benchmark check ("Keep as check").

## Defaults

- D-default-1 (2026-11-11, agent, setup): afterburner submodule at upstream main (32c9429), the base of the repair branches; eicSimuBeamEffects at v1.1, the version eic_xl 26.11 ships.
- D-default-2 (2026-11-11, agent, setup): generator_benchmarks' gitlink stays at upstream main (1a92e6b); the benchmark is commit 2a87b52 on the local branch `afterburner-benchmark`, so that a clone of the workbench stays fetchable (D-user-2).
- D-default-3 (2026-11-11, agent, setup): findings renumbered F1–F10 for this program; FINDINGS.md cites the dis-autoresearch numbers.
- D-default-4 (2026-11-11, agent, setup): the benchmark runs in a copy under `{data}/bench/<label>/` (`scripts/run-benchmark.sh`), because its Snakefiles use paths relative to the working directory and the workbench is bound read-only in the container; abconv builds go to `{data}/build/<label>/` (`scripts/build-abconv.sh`).
