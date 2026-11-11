# Afterburner findings imported from dis-autoresearch (2026-11-07)

The full entries of dis-autoresearch findings F7–F10, copied verbatim from
`~/dev/dis-autoresearch/space-v1/reports/phase0_findings.md`. That program studied a meson-structure
sample processed by abconv, so "this program", the decision numbers (D-user-*, D-default-*), Q numbers and
`space/...` paths below belong to dis-autoresearch. In this workbench the findings carry new numbers;
`FINDINGS.md` maps them (dis F7 → F1, F9 → F2, F10 → F3; F8 stays context).

## F7 — the beam effects repeat in every file: 500 beam and vertex configurations, each used 80 times

- Component: meson-structure `simulation-pipeline/simulation_pipeline/10_create_afterburner_jobs.py` line 35 runs
  `abconv <preset> <input> --output <output>`; abconv offers no seed option. In eic/afterburner (`submodules/afterburner`
  at v0.2.1 = 740f635, the version eic_xl 26.11 builds; main 32c9429 has the same line) `Afterburner.cc` line 31 constructs the smearer as `_smear(1)`: the GSL mt19937 seed is hard-coded to 1.
  `AfterburnerConfig::random_seed` (= 1) is declared but never used, and `ArgumentProcessor.cc` has no seed flag. Every
  abconv run therefore draws the same sequence of vertices and beam kicks. The 2026-11 campaign reuses the 2026-07
  afterburner files (`configs/config-msf-26-11.yaml`, `signal_2026_07`).
- Evidence: 9x100 and 9x130, 40 000 events each: 500 distinct proton-beam and 500 distinct electron-beam four-vectors.
  Event i has the same beams and the same primary vertex (x, y, z, t) in every one of the 80 stems; the physics (x_B,
  Q², the Λ) is distinct in all 40 000. Gradient boosting on 16 stems predicts the proton-beam tilt from the true
  vertex with R² 0.997 in random 5-fold cross-validation, and 0.57 with the vertex smeared by 30 µm, 50 µm and 30 ps.
  With the folds grouped by event index (configurations unseen in training) R² is −0.24 (true vertex) and −0.22
  (smeared); a linear fit on the 500 configurations gives 0.018 horizontal and −0.014 vertical. So all of it is
  memorization; the physical vertex–tilt link (linear correlation −0.20 with vertex z, crab crossing) shrinks the
  tilt spread by about 1 %.
- Severity for this program: the split by stem puts every configuration in train, validation and test. A hits model
  sees the vertex through the tracks and can memorize each configuration's beam tilt. Against the true-beam −t
  (D-user-9) it could then pass the 0.032 GeV² beam limit by memorization, which no new sample would reproduce; the
  same holds, smaller, for x, Q², y through the electron-beam tilt. The nominal-beam truth is immune.
- Fix (upstream): eic/afterburner seeds the smearer from `random_seed` and abconv exposes it as an option; the
  pipeline then passes a distinct seed per file. Any production that runs abconv once per file is affected the same way. Here: Q15 (split by event index so that no configuration is shared).
- Upstream (checked 2026-11-07): not reported. None of eic/afterburner's 14 issues and 25 PRs (numbers 1–39, bodies,
  comments and reviews) mentions the seed or the random generator. `_smear(1)` dates from v0.1.0 (4d0e5a4,
  2021-10-15) and is on all 20 branches, none of which gives abconv a seed option. No open PR touches it, and a
  search of the eic organization for "afterburner seed" and "abconv seed" finds nothing. eic_xl 26.11.0-stable builds
  afterburner 0.2.1 (740f635), which differs from main only in `Histogrammer.cc` and `.gitignore`.
- Side check: the 2026-07 jobs (eic_xl 26.06) gave 9x100 the preset `ip6_hidiv_100x10` and 9x130 `ip6_ep_130x10`.
  The 9 GeV presets `ip6_hidiv_100x9` and `ip6_ep_130x9` set the same 18 parameters to the same values, so this
  has no effect.
- Reproduced on fresh inputs (2026-11-07, `beam-validation/`, eic_xl 26.11.0-stable): abconv 0.2.1 run on two head-on
  Pythia8 files with different seeds gives the same interaction point and the same beam four-vectors (to 1e-9
  relative) in 2000 of 2000 events, in all three setups (10x100, 9x130, 9x130-hiacc). Pythia8 with eicBeamShape, seeds s and s+1, shares
  none of 2000. `space/reports/beam-validation.md` holds the full afterburner vs Pythia8 comparison.
- Status: OPEN (2026-11-07).
- Status line (2026-11-07): here the stem split stays and no guard is added (D-user-13: this sample is a test run; the real run is regenerated). Status: OPEN upstream.

- F6 status line (2026-11-07): under the generator truth (D-user-9) the bin −t ∈ [1.8, 2.0) holds 140 events at 9x100 and 131 at
  9x130, all below 1.804 GeV²; on the nominal truth 718 and 798, which the beam spread moves there. Status: OPEN.

## F8 — the two energies carry different beam optics: 9x100 high divergence, 9x130 high acceptance

- Component: meson-structure `simulation-pipeline/simulation_pipeline/10_create_afterburner_jobs.py` lines 44–58 give
  9x100 `--preset=ip6_hidiv_100x10` and 9x130 `--preset=ip6_ep_130x10`. In eic/afterburner v0.2.1
  (`submodules/afterburner`) `ip6_ep_130x10` = `ip6_ep_130x9` = `ip6_hiacc_100x10`: all 18 parameters are equal.
- Evidence: the presets have equal emittances. β* (proton h/v, electron h/v) is 630/57 and 960/120 mm at high
  divergence, 940/85 and 1430/180 mm at high acceptance. The divergences are 220/220 and 145/105 µrad against
  180/180 and 118/86 µrad. In `beam-validation/` (`space/reports/beam-validation.md`), abconv at 9x130 compared
  with eicBeamShape's high-divergence 9x130 (a copy of its 10x100) gives beam-angle widths of 0.82 of
  Pythia8's, vertex x 12 % wider and vertex y 33 % wider. Compared with eicBeamShape in high acceptance at
  9x130, every width agrees within 3 % (χ²/ndf ≈ 1).
- Severity for this program: low. Within one energy nothing changes. Across energies, the beam-effects rows
  (0.032 GeV² at 9x100, 0.035 at 9x130) differ in optics as well as in energy. The proton pT spread from
  divergence is similar (100 GeV × 220 µrad = 22 MeV against 130 GeV × 180 µrad = 23 MeV), and the IP is 12 %
  (x) and 22 % (y) larger at 9x130. A campaign generated with eicBeamShape's high-divergence 9x130 steering files
  carries the 10x100 high-divergence optics instead.
- Fix: a choice for the regenerated sample (D-user-13): which optics 9x130 should carry. Q16.
- Status: OPEN (2026-11-07).

## F9 — the interaction point is tilted as for a +25 mrad crossing while the beams leave at −25 mrad

- Component: eic/afterburner (`submodules/afterburner` v0.2.1; PR #38 does not change it). The presets configure
  `crossing_angle_hor = 25e-3` and `crossing_angle_ver = 100e-6`. abconv's momenta come out as that geometry turned by
  180° about z: the proton beam at −25.0 mrad horizontally and +0.10 mrad vertically, the ePIC convention. This comes from
  `GenEvent::boost(β)` acting as `HepBoost(−β)` and from the direction of the alignment rotation (`// TODO back to -acos?`).
  The bunch-crossing IP (`generate_vertx_with_bunch_interaction`, line for line eicBeamShape's: `x_int =
  z_bunch_int·tan(θ/2)` with `z_bunch_int = cos(θ/2)·t_int`, then `RotY(θ/2)`, so x = (θ/2)(z + ct); eicBeamShape runs it
  with θ = −0.025, abconv with +25e-3) is built in the configured +25 mrad frame and set by `shift_position_to()` without that turn. The user recalls spotting the sign
  when the afterburner was created (ported from sPHENIX Fun4All) and reporting it at a beam group meeting; the output
  matched Pythia8, so it was kept "to fix later, if ever needed". Commit 19aa392 (2021-10-17, "boost rotate order")
  reordered the boost and rotation and flipped the crab sign to match.
- Evidence (`beam-validation/signs.py`, `sample_signs.py`): IP x against the lepton bunch position z + ct has slope
  +12.71 ± 0.10 mrad (r +0.67) in abconv v0.2.1 and in PR #38 at 10x100 (+12.75 at 9x130 hiAcc), against −12.48 ± 0.06
  mrad (r −0.67) in Pythia8 + eicBeamShape (crossing −0.025, one sign throughout). The sample gives +13.34 ±
  0.62 (9x100) and +13.53 ± 0.76 mrad (9x130), 500 events; every stem gives the same numbers, since abconv repeats its
  500 beam configurations in every file (F7). The proton beam angle (−25.0 mrad) and the crab slope of the proton angle
  against z − ct (−0.71 against −0.70 µrad/mm; sample −0.58 and −0.48) agree in sign. The expected sign follows from the
  geometry alone: with crab crossing both bunches lie on the bisector, at −θ/2 for a proton beam at −θ, and an electron
  moving along −z keeps its x, so it collides at x = −(θ/2)(z + ct), z + ct being its position in the bunch. The sign does
  not hinge on the time convention: IP x against IP z alone is +0.25 ± 0.03 mrad (abconv) against −0.27 ± 0.02
  (Pythia8), IP x against t +0.27 against −0.23.
- Direct test (2026-11-07, `beam-validation/abconv-signtest.patch`, `signtest.py`; outputs
  `/data/dis-autoresearch/beam-validation/signtest/`): v0.2.1 with the crossing angles and the two convention signs from
  the environment, default output event-identical to v0.2.1, on the same 20 000 head-on 10x100 events. Presets
  −25e-3 / −100e-6: beams +25.0 / −0.10 mrad, IP slope −12.29, proton crab +0.70 (the IP again opposite to the beams).
  `evt.boost(−β)` with `−acos` and presets −25e-3 / −100e-6: beams −25.0 / +0.10, IP −12.29, crab −0.70 / +1.08,
  energy split −0.78e-4 / +2.34e-4: every sign as Pythia8. The same with +100e-6 puts the proton at −0.10 mrad vertical.
  The runs share abconv's random numbers, so the two IP slopes share their noise ((12.71 + 12.29)/2 = 12.50).
- Severity for this program: low. The crossing term in IP x is about 0.09 mm at 1σ (12.5 mrad × 7 mm electron bunch).
  Nothing in the kinematics depends on it. A model that reads the vertex sees a mirrored x–(z + ct) correlation, which
  real data will not show. Upstream it affects anything that uses the luminous-region shape or the IP x–t correlation.
- Fix (upstream): turn the IP like the momenta (x → −x; the IP's y has no crossing term), or remove the convention
  flip at its root (`evt.boost(−β)`, `−acos` at the TODO, presets at −25e-3 / −100e-6, the vertical sign too because
  `rotateX(+θ)` tilts +z toward −y; PR #38's vertex transform then takes `HepBoost(+boost)`). Changing only the presets
  moves the beams to +25 mrad and leaves the IP mirrored. (Corrected 2026-11-07: the first draft of the review said
  +100e-6 for the vertical preset.) The user posts the review on PR #38 (`beam-validation/pr38-comment.md`).
- Related, same sign: the head-on → crossing boost changes the beam energies by θ²/4 in total. abconv gives the proton
  +2.35e-4 (100.0044 → 100.0279 GeV) and the electron −0.78e-4, both energies, matching the HepMC3 boost sign
  (with `HepBoost(+β)` the split reverses: measured −0.78e-4 / +2.34e-4 in the direct test).
- Status: OPEN (2026-11-07).

## F10 — abconv applies no beam energy spread

- Component: eic/afterburner v0.2.1. Its effects are crossing angle, divergence, crab kick and vertex spread; the
  configuration has no momentum-spread parameter. Pythia8's eicBeamShape smears the beam momenta
  (`Beams:sigmapzA = 0.00097`, `sigmapzB = 0.00058` in the high-divergence 10x100 steering file).
- Evidence: in the sample (stem 1), the beam energies vary by 4.2e-6 (proton) and 1.6e-6 (electron) relative, which is
  only the per-event boost, against 1e-3 and 6e-4 in eicBeamShape. The 1D comparison in `beam-validation/` compares
  angles and vertices, not energies, so it does not show this.
- Severity for this program: low. The true per-event beam carries no energy spread, so the beam-effects rows
  (0.032 / 0.035 GeV² on −t) omit its share. x_L = E_Λ/E_p moves by 1e-3 relative at most.
- Fix: upstream, an energy-spread option in abconv; here, nothing for the test sample (D-user-13).
- Status: OPEN (2026-11-07).
