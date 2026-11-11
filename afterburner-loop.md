# Afterburner repairs — program file

This program repairs the flaws of the EIC afterburner (`abconv`, eic/afterburner) that the 2026-11-07
beam-validation study and the generator_benchmarks afterburner benchmark found, and the tracker issues on
presets and beam energies. Every repair is its own branch, its own issue and its own PR (D-user-6). The
reference model is Pythia8 with eicBeamShape (eicSimuBeamEffects), the model abconv was validated against
in 2021.

This file is both the setup file and the loop file of `work-common.md`. Read it first, then
`work-common.md`.

## Names

| variable | value |
|---|---|
| `{repo}` | `~/dev/afterburner-workbench` (github.com/DraTeots/afterburner-workbench) |
| `{space}` | `{repo}/space` |
| `{ledger}` | `{space}/LEDGER.md` |
| `{data}` | `/data/afterburner-workbench` (builds under `build/<label>/`, benchmark runs under `bench/<label>/`) |
| `{memory}` | `~/.claude/projects/-home-romanov-dev-afterburner-workbench/memory/` |
| `{git}` | `on` when the start line holds `please-git`, otherwise `off` (`work-common.md`, Git) |
| `{online}` | `yes` when the start line holds `online` |
| image | `eicweb/eic_xl:26.11.0-stable`, local docker; abconv 0.2.1, Pythia8 8.316, eicSimuBeamEffects 1.1 inside |
| container wrapper | `scripts/in-eic-xl.sh '<command>'`: workbench read-only, `{data}` read-write |

No farm. Everything runs on the local machine (24 cores).

## Code tree

| path | what | pin |
|---|---|---|
| `afterburner/` | eic/afterburner, the code under study | gitlink upstream main 32c9429. Tag v0.2.1 (740f635) is the version eic_xl 26.11 builds; it differs from main only in `Histogrammer.cc` and `.gitignore`. PR #38's head: `git -C afterburner fetch origin refs/pull/38/head:refs/remotes/origin/pr38` (5c0b59f, on v0.2.1, merges cleanly into main) |
| `eicSimuBeamEffects/` | Pythia8 + eicBeamShape, the reference model (read only) | v1.1 (bb31207), the version eic_xl 26.11 ships |
| `generator_benchmarks/` | eic/generator_benchmarks; `benchmarks/afterburner/` is the ruler | gitlink upstream main 1a92e6b. The benchmark lives on the local branch `afterburner-benchmark` (2a87b52), unpushed: check it out before any run |
| `beam-validation/` | the 2026-11-07 study: sign checks, displaced-vertex check, the sign-test patch, the PR #38 review | — |
| `scripts/` | `in-eic-xl.sh`, `build-abconv.sh`, `run-benchmark.sh` | — |
| `docs/` | explainer page on the frame flip (F2) and its root fix; `make_figure_data.py` writes its numbers and the σ(t0) table | — |

To build abconv from a tree and run the ruler against it:

```bash
scripts/build-abconv.sh main
```

```bash
scripts/run-benchmark.sh main-full /data/afterburner-workbench/build/main/abconv/abconv --config AFTERBURNER_SETUPS=all AFTERBURNER_N_EVENTS=20000
```

`build-abconv.sh <label> [tree]` builds the afterburner submodule's working tree by default; for another
branch, check it out in a git worktree under `{data}/src/<label>` and pass that path. The image's own
abconv runs with `container` in place of the binary path.

## Ruler

**Workload.** The generator_benchmarks afterburner benchmark: all 19 setups (`setups.yml`), 20 000 events
per Pythia8 sample, Pythia8 seed 1, steering files of eicSimuBeamEffects v1.1, run by
`scripts/run-benchmark.sh` as above (about 5 minutes). The CI selection (6 setups, 2000 events, about
1 minute) is the quick check during development; a verdict always comes from the full workload.

**Reading a row.** Headline numbers come from a run's `results/afterburner.json` (pass count, every test)
and `results/afterburner/summary.md` (per setup and check group), never from arithmetic in chat.

**Reference rows** (Phase 0 records them in `{space}/reports/phase0_reference.md`):

| row | abconv | known so far |
|---|---|---|
| R0 | the image's abconv 0.2.1 (`container`) | 260 of 361 checks pass (2026-11-07, full workload) |
| R1 | upstream main 32c9429, built | CI selection 83 of 114 (2026-11-11) |
| R2 | PR #38 head 5c0b59f, built | — |

**Accepting a branch.** A repair branch is ACCEPTED when all four hold, measured on the full workload:

1. its target checks (the work-item table below) pass in every setup;
2. every check that passes on the branch's base row passes on the branch;
3. the outputs the branch must leave alone are unchanged, named in its ledger entry before the work
   starts (for example: every `P` line of the HepMC3 output byte-identical to the base row);
4. the build passes in the image without new compiler warnings in the files it changes.

Otherwise it is REJECTED, with its row recorded. A check whose reference the user has not settled (F5, the
vertical luminous width) is waived from criterion 2 by a line in the branch's ledger entry.

**Frozen by statement after Phase 0:** the benchmark's checks, tolerances and verdict rule
(`benchmarks/afterburner/scripts/geometry.py` `CHECKS`, `scripts/verdict.py`), the workload above, and the
reference rows. A change to the benchmark is its own branch in generator_benchmarks and re-runs R0–R2 in
the same step. Nothing enforces the freeze; this statement does.

## Work items

Branch names are in the afterburner submodule unless the item says otherwise. Each item also gets an issue
draft and a PR description draft under `{space}/issues/<item>.md`.

| item | finding / issue | branch | base | target checks | must stay unchanged |
|---|---|---|---|---|---|
| seed | F1 | `fix/smear-seed` | main | seed: not repeated | with the default seed, the output byte-identical to R1 |
| IP frame | F2, F6 | `fix/ip6-frame` | PR #38 (`origin/pr38`, D-user-4) | IP crossing slope; displaced vertices stay aligned | beam directions, divergences, crab kicks (sign and size); the energy split reverses (F6), stated in the PR |
| energy spread | F3 | `feat/beam-energy-spread` | main | energy spread, both beams | everything except the beam energies |
| version | F7 | `fix/version-string` | main | `abconv --version` prints the project's version | the output byte-identical to R1 |
| vertical width | F5 | none | — | — | issue draft only (D-user-5) |
| pythia8 crossing angle | F9 | `fix/pythia8-crossing-angle` in generator_benchmarks | generator_benchmarks main | eicBeamShape runs at −0.025 | — |
| tracker | #16, #17, #34, #5, #4 | one branch each, named in Phase 2 | main | per issue, in its ledger entry | per issue |

The root fix of F2 (D-user-4), from the 2026-11-07 direct test (`beam-validation/abconv-signtest.patch`,
`signtest.py`; imported entry of dis F9):

- pass −β to `GenEvent::boost` in `Converter.cc`, so that it acts as `HepBoost(+β)`;
- use `−acos` at `// TODO back to -acos?` (`Afterburner.cc` line 380);
- set every IP6 preset to `crossing_angle_hor = −25e-3`, `crossing_angle_ver = −100e-6` (the vertical sign
  changes too: `rotateX(+θ)` tilts +z toward −y);
- PR #38's vertex transform then takes `HepBoost(+boost)`, to keep following the momenta.

Expected on 10x100: beams −25.0 / +0.10 mrad, IP slope about −12.3 mrad, proton crab slope −0.70 µrad/mm,
energy split −0.78e-4 (hadron) / +2.34e-4 (electron). Changing only the presets mirrors the beams and
leaves the IP mirrored; that is no fix.

## Phases

The user reviews each phase's report before the next starts.

### Phase 0 — reference rows and reproducers

- **Step 0.** Build R1 and R2 (`scripts/build-abconv.sh main`; PR #38 in a worktree under `{data}/src/pr38`).
  Run the full workload for R0, R1 and R2. Record the three summary tables, pass counts and versions in
  `{space}/reports/phase0_reference.md`. R0 must give 260 of 361; if it does not, the ruler is broken
  (`work-common.md`, decision table).
- Write a minimal reproducer per OPEN finding (command, expected and observed numbers) into
  `{space}/reports/phase0_findings.md`, and update FINDINGS.md.
- Read the in-scope tracker issues (#16, #17, #34, #5, #4) with their comments, and the open PRs (#30, #36,
  #38, #39); list per item the code it touches and any overlap with the work items.
- Done 2026-11-11: the collision-time-from-vertex fit (σ(t0) from nothing, z, z and y, z and x, with x
  resolution, and the cross-applied estimator) is `docs/make_figure_data.py`; the table is key `t0_ps` of
  `docs/figure-data.js`. The replies built on it (`Elke_answer.md`, `docs/t0-from-vertex.html`) stay out of git.
- **Done:** R0–R2 recorded, every finding with a benchmark check reproduces on R1, reproducers written,
  tracker survey written, ledger outcome appended.

### Phase 1 — repairs of the study's findings

This phase may repair the code under study, under the acceptance rule above. Per item, in the order seed,
IP frame, energy spread, version, pythia8 crossing angle:

1. write the item's ledger entry: base, target checks, the outputs that must stay unchanged;
2. create the branch from its base (with `{git}` off: a patch under `{space}/notes/patches/` instead);
3. build, run the full workload, record the row in `{space}/reports/phase1_repairs.md`;
4. ACCEPTED or REJECTED by the rule; update the finding's line in FINDINGS.md;
5. write `{space}/issues/<item>.md`: the issue text (finding, reproducer, numbers) and the PR description
   (change, benchmark row against its base, what it leaves unchanged).

The vertical-width item writes its issue draft only. Design choices inside a repair (an option's name, a
default value, where a parameter lives) are DECIDE; a choice that changes physics output by default is a
question.

**Done:** every item ACCEPTED or REJECTED with its row, every issue and PR draft written, FINDINGS.md
current, report written.

### Phase 2 — tracker issues on presets and beam energies

Issues #16 (new energy configs not added everywhere), #17 (presets not in help), #34 (early-science beam
energy ranges), #5 (eA collision energies), #4 (full list of beam effects in the readme) (D-user-3). Per
issue the Phase 1 procedure. A new or changed preset with a matching eicBeamShape steering file also gets
a setup in the benchmark's `setups.yml`, on the benchmark's branch, and its row. Out of scope: #1, #11,
#12, #27 and PR #30, #31, #35.

**Done:** as Phase 1.

## Upstream

- PR #38 is Dmitry Kalinkin's. The IP-frame branch builds on it and its PR description says so.
- The PR #38 review (`beam-validation/pr38-comment.md`) is posted by the user.
- Issues and PRs open on GitHub only when the user asks for the item in chat (`work-common.md`, Git).
- eic/afterburner accepts branch pushes from DraTeots; eic/generator_benchmarks does not (a PR from a
  fork).

## Disk

A full run writes about 9 GB of HepMC3 text under `{data}/bench/<label>/sim_output/`. The rows' tables are
in `results/`, which stays. Delete a recorded row's `sim_output/` when `/data` falls below 100 GB free; it
regenerates from the workload.
