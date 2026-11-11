# beam-validation — afterburner vs Pythia8 beam effects

This rebuilds the validation that `afterburner/python/comparison.ipynb` ran in 2021, using the versions that
eic_xl 26.11.0-stable ships. It is the record of the 2026-11-07 study (dis-autoresearch findings F7–F10, the
PR #38 review). The runnable successor for all common energies and beam regimes is
`generator_benchmarks/benchmarks/afterburner/` (branch `afterburner-benchmark`, Snakemake, eic benchmark
conventions).

Three samples per beam energy, all from one Pythia8 NC DIS steering file of eicSimuBeamEffects
(hiDiv, 10 < Q² < 100 GeV²) and the same Pythia8 seed:

| sample | how |
|---|---|
| nominal | Pythia8 head-on: the steering file with `Beams:allowMomentumSpread = off` and `Beams:allowVertexSpread = off` |
| afterburner | the head-on file after `abconv -p <IP6 preset>` |
| pythia8 | Pythia8 with `eicBeamShape` beam effects, crossing angle −25 mrad, high divergence |

abconv's own histogrammer (`--ab-off` for nominal and pythia8) fills the histograms for all three. In 2021
the head-on and beam-effects files were generated separately; the README blamed the low-η difference on
that. Here both come from one steering file and one seed, so that cause is gone.

The seed check (F7) adds a second, small pair of files with seed + 1. abconv runs on the first events of
both head-on files, and the event-by-event comparison counts identical interaction points and beam
four-vectors. abconv's smearer is seeded with 1 (`Afterburner.cc` line 31), so every abconv run repeats
the same sequence. Pythia8's `eicBeamShape` draws from Pythia8's generator, which follows `Random:seed`.

## Versions

| piece | version in eic_xl 26.11.0-stable | source |
|---|---|---|
| Pythia8 | 8.316, plain pythia.org tarball (spack applies no patch above 8.312) GitLab `Pythia8/releases` tag `pythia8316`; headers and `Version.xml` identical to the image's (not a submodule here) |
| eicSimuBeamEffects | 1.1 (`runBeamShapeHepMC`) | `eicSimuBeamEffects` at v1.1 (bb31207) |
| afterburner (abconv) | 0.2.1 (prints "0.1.3" for `--version`) | `afterburner` tag v0.2.1 (740f635); the submodule tracks main (32c9429), which differs from v0.2.1 only in `Histogrammer.cc` and `.gitignore` |

## Setups

| setup | steering file | abconv preset | note |
|---|---|---|---|
| 10x100 | `dis_eicBeam_hiDiv_10x100_10to100` | `ip6_hidiv_100x10` | the parameter set abconv gave the 9x100 sample; `eicBeamShape` has no 9x100 |
| 9x130 | `dis_eicBeam_hiDiv_9x130_10to100` | `ip6_ep_130x9` | the sample's preset (`ip6_ep_130x10`, same parameters), which is abconv's high-acceptance set, against eicBeamShape's high divergence: the optics differ (F8) |
| 9x130-hiacc | `dis_eicBeam_hiAcc_10x100` at 9x130 energies, eicBeamShape config 2 | `ip6_ep_130x9` | matched optics; no hiAcc 9x130 steering file exists, and eicBeamShape copies 10x100 for 9x130 |

## Run

Docker with the local image `eicweb/eic_xl:26.11.0-stable` (no farm). Outputs go to
`/data/afterburner-workbench/beam-validation/` (`BEAMVAL_OUT` overrides this). The outputs of the
2026-11-07 study are in `/data/dis-autoresearch/beam-validation/`.

```bash
beam-validation/in-eic-xl.sh "bash $PWD/beam-validation/run-energy.sh 10x100 50000 1001 2000"
```

```bash
beam-validation/in-eic-xl.sh "bash $PWD/beam-validation/run-energy.sh 9x130 50000 1001 2000"
```

```bash
beam-validation/in-eic-xl.sh "bash $PWD/beam-validation/run-energy.sh 9x130-hiacc 50000 1001 2000"
```

```bash
beam-validation/in-eic-xl.sh "python3 $PWD/beam-validation/compare.py /data/afterburner-workbench/beam-validation 10x100 9x130 9x130-hiacc"
```

The arguments of `run-energy.sh` are: setup, events, Pythia8 seed, events in the seed check.
`compare.py` writes `plots/<energy>_comparison.png`, `summary.md` and `summary.csv`.

## Further checks

| script | what it checks |
|---|---|
| `signs.py` | the signs of the beam geometry, event by event: beam angles, IP x against z + ct (bunch crossing), beam angle against bunch position (crab kick); abconv against Pythia8 (F9) |
| `sample_signs.py` | the same slopes in the meson-structure 2026-11 sample's CSV under `/data/meson-structure-2026-11/` (run with `uv run --with numpy --with polars`) |
| `vertices.py` | displaced decay vertices against their parent's momentum, and dt·β/\|d\|; used to review afterburner PR #38 |
| `abconv-signtest.patch`, `signtest.py` | abconv v0.2.1 with the crossing angles (`AB_XH`, `AB_XV`) and the root fix of the convention flip (`AB_ROOTFIX`: `evt.boost(−β)`, `−acos`) from the environment, default output event-identical to v0.2.1; the table of beam angles, IP slopes, crab slopes and energy shifts per variant (F9) |
| `pr38-comment.md` | the review text for PR #38, for the user to post |

## Reading the table

- σ ab/py8: the ratio of standard deviations. Mean difference: in units of Pythia8's σ.
- χ²/ndf: the two-sample shape test. Final-state η and φ fill one entry per particle, and particles in one
  event are correlated, so their χ² overstates the significance.
- Histogrammer (0.2.1) takes the first status-4 particle as the hadron beam. Pythia8 writes the proton first;
  afterburner main changed this to select by PDG id.
