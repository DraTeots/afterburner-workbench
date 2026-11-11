Some history first, because this PR touches the code where it comes from.

When the afterburner was written, its boost and rotation part was taken over from the sPHENIX Fun4All afterburner (PHHepMCGenHelper). The presets configure +25 mrad: `crossing_angle_hor = 25e-3` and `crossing_angle_ver = 100e-6`, applied as `rotateY(+25e-3).rotateX(+100e-6)` to +z, which points the proton at +25 mrad horizontally and −0.10 mrad vertically. The beams nonetheless leave abconv at −25 mrad horizontally and +0.10 mrad vertically, which is the configured geometry turned by 180° about z. Two conventions combine to do this: `GenEvent::boost(β)` acts as `HepBoost(−β)`, as this PR notes, and the alignment rotation is applied in the direction that matches it (the `// TODO back to -acos?` line). I spotted this sign mistake when the afterburner was being created and reported it at a beam group meeting. The output was in full agreement with Pythia8 + eicBeamShape (crossing angle −0.025), so the group decided to proceed as it was and fix it later, if that was ever needed. With this PR it starts to matter, so here is a review with numbers.

**Test.** eic_xl:26.11.0-stable; this PR's head (5c0b59f, on v0.2.1) and v0.2.1, both built in the image. The local v0.2.1 build reproduces the image's abconv event for event. Input: Pythia8 8.316 NC DIS 10x100, head-on, 20 000 events with its own decays at displaced vertices, carrying times. That gives 11 924 decays with |d| > 1 mm, 3 498 of them Λ. Preset `ip6_hidiv_100x10`. For every decayed particle (status 2) I measure the angle between the displacement d = end − production vertex and the particle's momentum, and dt·β/|d|.

| file | angle(d, p), median | 90 % | forward (θ < 0.1), median | dt·β/\|d\|, median |
|---|---|---|---|---|
| Pythia8 head-on (input) | 0.000 mrad | 0.000 | 0.000 | 1.0000 |
| Pythia8 + eicBeamShape (−0.025) | 0.000 | 0.000 | 0.000 | 1.0000 |
| abconv v0.2.1 | **24.96** | 25.64 | 25.05 | 1.0000 |
| abconv this PR | **0.000** | 0.000 | 0.000 | 1.0000 |
| this PR, input vertex times set to 0 | 12.58 | 14.27 | 12.55 | 0.0001 |

**What the PR gets right:**
- Displaced vertices become exactly consistent with the momenta again, at every angle. The `HepBoost(−boost)` sign is right; with the opposite sign about 25 mrad would remain.
- Momenta and event positions are byte-identical to v0.2.1 (every `P` and `E` line). Only displaced vertex positions change.
- Removing the vertex-rotation block in `Afterburner.cc` changes nothing, since it was a no-op (`final_3vertex = init_3vertex`).
- Simulation is protected, as you say. In the meson-structure 2026-07 k-Λ campaign the Λ is stable at generator level and Geant4 decays it, and the Λ decay vertices align with the Λ momentum to 0.000 mrad (500 Λ per energy, median decay length 3.8 m at 9x100 and 4.1 m at 9x130).

**Suggestion on times.** The result depends on the generator's vertex times. With dt = 0 the boost part drops out and half the error stays: 12.6 mrad against 25.0 before. That is better than now, but silent. Displaced vertices whose dt disagrees with |d|·E/|p| of the parent could be detected, with either a warning or a time derived from the parent's momentum before transforming.

**What the PR does not cover: the primary vertex.** `ab_result.vertex`, the bunch-crossing IP from `generate_vertx_with_bunch_interaction()`, is still built in the configured +25 mrad frame. That function is line for line eicBeamShape's: `x_int = z_bunch_int·tan(θ/2)` with `z_bunch_int = cos(θ/2)·t_int`, then `RotY(θ/2)`, which gives x = (θ/2)(z + ct). eicBeamShape runs it with θ = −0.025, abconv with θ = +25e-3. The result goes into `shift_position_to()` without the 180° turn the momenta get, so the luminous region is tilted as for a +25 mrad crossing while the beams are at −25 mrad.

The right sign follows from the geometry alone. With crab crossing, both bunches are tilted onto the bisector of the two beams, at −θ/2 for a proton beam at −θ. An electron moving along −z keeps its x, so it collides at x = −(θ/2)(z + ct), where z + ct is its position in its bunch. Measured as the slope of IP x against z + ct:

| | IP x vs z + ct | proton angle vs z − ct (crab) | proton angle |
|---|---|---|---|
| abconv v0.2.1 and this PR, 10x100 | **+12.71 ± 0.10 mrad** (r = +0.67) | −0.71 µrad/mm | −25.0 mrad |
| Pythia8 + eicBeamShape (−0.025), 10x100 | **−12.48 ± 0.06 mrad** (r = −0.67) | −0.70 µrad/mm | −25.0 mrad |
| meson-structure 2026-07 campaign (abconv), 9x100 / 9x130, 500 events | **+13.3 ± 0.6 / +13.5 ± 0.8 mrad** | −0.58 / −0.48 µrad/mm | −25.0 mrad |

The sign does not hinge on the time convention: IP x against IP z alone has slope +0.25 ± 0.03 mrad in abconv and −0.27 ± 0.02 mrad in Pythia8, and IP x against t has +0.27 against −0.23.

**Direct test.** I built v0.2.1 with the crossing angles and the two convention signs taken from the environment. Its default output is event-identical to v0.2.1. I ran it on the same 20 000 head-on events, and the runs share abconv's random numbers:

| abconv | proton angle, h / v | IP x vs z + ct | proton crab slope | ΔE/E proton / electron |
|---|---|---|---|---|
| as now: presets +25e-3 / +100e-6 | −25.0 / +0.10 mrad | **+12.71** ± 0.10 mrad | −0.71 µrad/mm | +2.34e-4 / −0.78e-4 |
| presets −25e-3 / −100e-6 | +25.0 / −0.10 | **−12.29** ± 0.10 | +0.70 | +2.34e-4 / −0.78e-4 |
| `evt.boost(−β)` and `−acos`, presets −25e-3 / −100e-6 | −25.0 / +0.10 | **−12.29** ± 0.10 | −0.70 | −0.78e-4 / +2.34e-4 |
| Pythia8 + eicBeamShape (−0.025) | −25.0 / +0.10 | **−12.48** ± 0.06 | −0.70 | ≈ 0 |

The IP slope always takes the sign of the configured angle, and the beams take the opposite one. Because the runs share their random numbers, the two abconv IP slopes share their noise: (12.71 + 12.29)/2 = 12.50.

The beam angles and the crab kicks agree in sign with Pythia8; only the IP is mirrored. In size this is small (the crossing term in x is about 0.09 mm at 1σ), but it is a sign error in the luminous-region shape and in the x–t correlation. A fix could go into this PR or a follow-up, in one of two ways:
- give the IP the same turn as the momenta, x → −x (the IP's y has no crossing term);
- remove the convention flip at its root, as in the third row: pass −β to `GenEvent::boost` (so that it acts as `HepBoost(+β)`), use `−acos` at the TODO, and set the presets to −25e-3 / −100e-6. The vertical preset changes sign too, because `rotateX(+θ)` tilts +z toward −y; with +100e-6 the proton would leave at −0.10 mrad. Beams, crab kicks and the IP are then all built in the ePIC frame. This PR's vertex transform would then need `HepBoost(+boost)`, to keep following the momenta.

Changing only the presets moves the beams to +25 mrad and leaves the IP mirrored (second row), so that alone is not a fix.

**For the record, the same boost sign also decides which beam takes the energy change.** Going from head-on to a crossing angle, the relative energy shifts of the two beams must add up to θ²/4 = 1.56e-4, since s is invariant. Today the proton gets +2.34e-4 and the electron −0.78e-4. The campaign shows the same +2.35e-4 on the proton (100.0044 → 100.0279 GeV mean at 100 GeV, the same at 130 GeV) and −0.78e-4 on the electron. With `HepBoost(+β)`, the root fix above, the split reverses: −0.78e-4 on the proton and +2.34e-4 on the electron. Neither is wrong for physics, but it is worth knowing when comparing beam energies.

I can share the scripts (`vertices.py` for the vertex table, `signs.py` and `signtest.py` for the IP and crab slopes) and the test patch; the scripts run on plain HepMC3 text files.
