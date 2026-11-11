# afterburner-workbench

Repairs of the EIC afterburner (`abconv`) against Pythia8 + eicBeamShape, run as a phase-gated loop. Two
protocol files: `afterburner-loop.md` (everything specific to this program: code tree, ruler, work items,
phases) and `work-common.md` (the rules of every run).

## Start line

`Read afterburner-loop.md and work-common.md. Run.` Add `online` when you will answer in chat during the
run; add `please-git` when commits are allowed this run.

## Three rules

1. **The ruler is the benchmark.** `generator_benchmarks/benchmarks/afterburner` (local branch
   `afterburner-benchmark`), full workload, run by `scripts/run-benchmark.sh`. A repair is ACCEPTED only by
   the rule in `afterburner-loop.md`, Ruler.
2. **One finding, one branch, one issue, one PR.** Never two findings on one branch. Issues and PRs are
   drafted under `space/issues/` and open on GitHub only when the user asks for that item in chat.
3. **Questions only about physics, scope and upstream.** A doubt about a tool, a threshold, an option name
   or code is yours: DECIDE it, record it in `space/notes/DECISIONS.md`, keep working.

## Where to look

- Resume: `space/STATUS.md`. Questions: `space/QUESTIONS.md`. Phases: `space/LEDGER.md`. Decisions:
  `space/notes/DECISIONS.md`. Findings: `space/reports/FINDINGS.md`.
- The study that found the flaws: `beam-validation/README.md`, `space/reports/beam-validation-2026-11-07.md`,
  `space/reports/imported-dis-autoresearch-findings.md`.

## Git

No commits, pushes or branch changes unless the user's chat message contains `please-git`. Submodule
branches leave the machine only as PRs; gitlinks point only at commits their URLs serve
(`work-common.md`, Git).
