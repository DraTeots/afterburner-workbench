#!/usr/bin/env python3
"""Numbers and profiles for docs/abconv-frame-flip.html, and the collision-time (t0) table from the vertex.

Reads 20 000 events of 10x100 high-divergence NC DIS from the 2026-11-07 beam-validation outputs:
  pythia8  Pythia8 + eicBeamShape, crossing angle -0.025 (the reference)
  abconv   abconv v0.2.1 on the head-on file of the same steering and seed (preset ip6_hidiv_100x10)
  flip     the same with the presets negated (-25e-3 / -100e-6), nothing else changed
  rootfix  presets negated, GenEvent::boost(-beta) and -acos at the TODO (beam-validation/abconv-signtest.patch)
and writes docs/figure-data.js (window.FIGURE_DATA): the page's rows and profiles, and the σ(t0) table (key t0_ps).

  uv run --with numpy docs/make_figure_data.py [beam-validation output dir, default /data/dis-autoresearch/beam-validation]
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "beam-validation"))
from signs import read, slope  # noqa: E402

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "/data/dis-autoresearch/beam-validation")
N = 20000
MM_TO_PS = 1e9 / 299792458.0  # 1 mm / c in ps
FILES = {
    "pythia8": SRC / "10x100/py8_full.hepmc",
    "abconv": SRC / "signtest/default.hepmc",
    "flip": SRC / "signtest/flip.hepmc",
    "rootfix": SRC / "signtest/rootfix.hepmc",
}
E0 = {"p": 100.0, "e": 10.0}
rng = np.random.default_rng(7)


def profile(y, x, edges):
    """Mean of y and its error in bins of x."""
    idx = np.digitize(x, edges) - 1
    mean, err, centre = [], [], []
    for b in range(len(edges) - 1):
        sel = idx == b
        if sel.sum() < 20:
            continue
        centre.append(0.5 * (edges[b] + edges[b + 1]))
        mean.append(y[sel].mean())
        err.append(y[sel].std(ddof=1) / np.sqrt(sel.sum()))
    return {"x": centre, "y": mean, "err": err}


def fit(columns, target):
    """Least-squares linear fit target ~ 1 + columns; returns coefficients."""
    a = np.column_stack([np.ones(len(target))] + columns)
    coef, *_ = np.linalg.lstsq(a, target, rcond=None)
    return coef


def residual_ps(coef, columns, target):
    a = np.column_stack([np.ones(len(target))] + columns)
    return float(np.std(target - a @ coef) * MM_TO_PS)


samples = {}
for name, path in FILES.items():
    ip, pr, el = read(path, N)
    x, y, z, ct = ip.T
    samples[name] = dict(x=x, y=y, z=z, ct=ct, pr=pr, el=el)
    print(f"{name}: {len(x)} events from {path}", file=sys.stderr)

out = {"n_events": N, "setup": "10x100 high divergence, NC DIS 10 < Q2 < 100 GeV2", "rows": {}, "profiles": {}}
edges_e = np.linspace(-21, 21, 15)          # electron bunch position z + ct [mm], sigma 7 mm
edges_h = np.linspace(-150, 150, 13)        # hadron bunch position z - ct [mm], sigma 70 mm
for name, s in samples.items():
    x, y, z, ct, pr, el = s["x"], s["y"], s["z"], s["ct"], s["pr"], s["el"]
    e_pos, h_pos = z + ct, z - ct
    ph = np.arctan2(pr[:, 1], pr[:, 3]); pv = np.arctan2(pr[:, 2], pr[:, 3])
    eh = np.arctan2(el[:, 1], -el[:, 3])
    b_x, se_x, r_x = slope(x, e_pos)
    b_c, se_c, _ = slope(ph, h_pos)
    out["rows"][name] = {
        "proton_h_mrad": 1e3 * ph.mean(), "proton_v_mrad": 1e3 * pv.mean(), "electron_h_mrad": 1e3 * eh.mean(),
        "ip_slope_mrad": 1e3 * b_x, "ip_slope_err": 1e3 * se_x, "ip_r": r_x,
        "crab_urad_per_mm": 1e6 * b_c, "crab_err": 1e6 * se_c,
        "dE_p": pr[:, 4].mean() / E0["p"] - 1, "dE_e": el[:, 4].mean() / E0["e"] - 1,
        "r_x_ct": float(np.corrcoef(x, ct)[0, 1]),
    }
    out["profiles"][name] = {
        "ip_x_um_vs_e_mm": profile(1e3 * x, e_pos, edges_e),
        "proton_h_urad_vs_h_mm": profile(1e6 * (ph - ph.mean()), h_pos, edges_h),
    }

# Collision time from the vertex (t0): residual rms of linear fits of ct on vertex coordinates
t0 = {}
for name in ("pythia8", "abconv"):
    s = samples[name]
    x, y, z, ct = s["x"], s["y"], s["z"], s["ct"]
    row = {"nothing": float(np.std(ct) * MM_TO_PS)}
    for label, cols in {"z": [z], "z_y": [z, y], "z_x": [z, x]}.items():
        row[label] = residual_ps(fit(cols, ct), cols, ct)
    for res_um in (30, 100):
        xs = x + rng.normal(0, res_um * 1e-3, len(x))
        row[f"z_x_{res_um}um"] = residual_ps(fit([z, xs], ct), [z, xs], ct)
    row["coef_z_x"] = list(map(float, fit([z, x], ct)))
    t0[name] = row
p8, ab = samples["pythia8"], samples["abconv"]
t0["abconv_fit_on_pythia8"] = residual_ps(fit([ab["z"], ab["x"]], ab["ct"]), [p8["z"], p8["x"]], p8["ct"])
t0["pythia8_fit_on_abconv"] = residual_ps(fit([p8["z"], p8["x"]], p8["ct"]), [ab["z"], ab["x"]], ab["ct"])
out["t0_ps"] = t0

# A thin random subsample of Pythia8 events for the scatter panels (x against ct and against z + ct)
pick = rng.choice(len(p8["x"]), 1200, replace=False)
out["scatter_pythia8"] = {"x_um": (1e3 * p8["x"][pick]).round(1).tolist(), "ct_mm": p8["ct"][pick].round(2).tolist(),
                          "e_mm": (p8["z"] + p8["ct"])[pick].round(2).tolist(), "z_mm": p8["z"][pick].round(2).tolist()}
out["widths"] = {name: {"x_um": float(1e3 * s["x"].std()), "y_um": float(1e3 * s["y"].std()), "z_mm": float(s["z"].std()),
                        "ct_mm": float(s["ct"].std()), "e_mm": float((s["z"] + s["ct"]).std()), "h_mm": float((s["z"] - s["ct"]).std())}
                 for name, s in samples.items()}


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return round(float(o), 6)
    return o


(HERE / "figure-data.js").write_text("// Written by docs/make_figure_data.py; do not edit.\nwindow.FIGURE_DATA = "
                                    + json.dumps(clean(out), separators=(",", ":")) + ";\n")
print(json.dumps(clean({"rows": out["rows"], "t0_ps": t0, "widths": out["widths"]}), indent=1))
