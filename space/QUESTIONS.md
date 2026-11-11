# Questions

Format and protocol: `work-common.md`, FIX / DECIDE / ASK / PARK / STOP. Answer inline after `ANSWER:`.

## Q1 2026-11-11 — Submodules of the workbench [closed 2026-11-11]
- Found: the user asked for afterburner, "pythia with beam effects" and generator_benchmarks as submodules at the root.
- Options: A) eicSimuBeamEffects only B) eicSimuBeamEffects and the Pythia8 source. Recommendation: A.
- ANSWER: A (in chat) → D-user-1

## Q2 2026-11-11 — Where the benchmark branch goes (DraTeots has no push access to eic/generator_benchmarks) [closed 2026-11-11]
- Options: A) a branch on eic/generator_benchmarks B) a fork under DraTeots C) a local branch, no push. Recommendation: A, then B.
- ANSWER: "direct clone, local branches. pushes as PRs." → D-user-2

## Q3 2026-11-11 — Scope of "issues" [closed 2026-11-11]
- Options: A) the study's flaws and the tracker items on presets and energies B) every open issue C) the study's flaws only. Recommendation: A.
- ANSWER: A → D-user-3

## Q4 2026-11-11 — Fix shape for the mirrored IP crossing term (F2) [closed 2026-11-11]
- Options: A) turn the IP, x → −x B) the root fix (no convention flip). Recommendation: A.
- ANSWER: B → D-user-4

## Q5 2026-11-11 — Reference for the vertical luminous width (F5) [closed 2026-11-11]
- Options: A) record, keep abconv's β*·ε, ask the machine group B) match the CDR table C) β*·ε is right. Recommendation: A.
- ANSWER: "Record and prepare an issue. All PRs and work must be separated. The root fix must be based on Dmitry K PR. All findings will go to new issues and PRs" → D-user-5, D-user-6

## Q6 2026-11-11 — Relation of the repairs to PR #38 [closed 2026-11-11]
- Options: A) build on PR #38 B) independent. Recommendation: A.
- ANSWER: A → D-user-4
