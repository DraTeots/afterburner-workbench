PHASE0 NOT STARTED — workbench set up 2026-11-11; next run starts Phase 0, Step 0
## LIVE
- nothing running
## RESUME
- Start Phase 0 (`afterburner-loop.md`, Phases): build R1 (main) and R2 (PR #38), run the full workload for R0–R2.
- Before any benchmark run: `git -C generator_benchmarks checkout afterburner-benchmark` (local branch, 2a87b52, unpushed; the gitlink stays at upstream main 1a92e6b).
- Already built: `/data/afterburner-workbench/build/main/` (main 32c9429). CI selection against it: `/data/afterburner-workbench/bench/main-ci/` (83 of 114).
- 2026-11-07 outputs (container abconv): `/data/dis-autoresearch/beam-validation/` (study, sign test, PR #38 builds), `/data/dis-autoresearch/generator-benchmarks-test/` (full workload, 260 of 361).
## Waiting on the user
- nothing blocking
## Pointers
- ledger space/LEDGER.md; history space/notes/runlog.md; decisions space/notes/DECISIONS.md; findings space/reports/FINDINGS.md
