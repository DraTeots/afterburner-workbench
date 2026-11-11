#!/usr/bin/env python3
"""Afterburner vs Pythia8 beam effects: abconv's validation histograms and the seed check.

For each energy produced by run-energy.sh it reads abconv's histograms (directory `after`) of
  nominal      head-on Pythia8, no beam effects,
  afterburner  the same head-on file after abconv with the IP6 preset,
  pythia8      Pythia8 with eicBeamShape beam effects (same steering file and seed),
writes one figure per energy (overlays and the afterburner/pythia8 ratio) and a table of
mean, standard deviation and a two-sample chi2 per histogram. The seed check compares, event
by event, the beam four-vectors and the interaction point of two abconv runs on head-on files
made with different Pythia8 seeds, and the same for the two Pythia8 beam-effects files.

Runs inside eic_xl (uproot, numpy, matplotlib):  compare.py <out_dir> <energy> [<energy> ...]
Writes <out_dir>/plots/<energy>_comparison.png, <out_dir>/summary.csv, <out_dir>/summary.md.
"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import uproot  # noqa: E402

# name, panel label, unit, scale from the stored unit. Beam 1 is the first status-4 particle (the proton in
# Pythia8 output, which abconv 0.2.1's Histogrammer assumes). vtxY/Z/T are beam 1's end vertex; vertex x uses
# vtx2X, beam 2's end vertex (the same interaction point), because vtxX has 0.1 mm bins against sigma ~0.13 mm
# and abconv leaves its 2D vertex histograms empty.
HISTS = [
    ("vtx2X", "vertex x", "mm", 1.0),
    ("vtxY", "vertex y", "mm", 1.0),
    ("vtxZ", "vertex z", "mm", 1.0),
    ("vtxT", "vertex t", "mm/c", 1.0),
    ("atan2PxPz1", "proton beam atan2(px, pz)", "mrad", 1e3),
    ("atan2PyPz1", "proton beam atan2(py, pz)", "mrad", 1e3),
    ("atan2PxPz2", "electron beam atan2(px, −pz)", "mrad", 1e3),
    ("atan2PyPz2", "electron beam atan2(py, −pz)", "mrad", 1e3),
    ("partEta", "final-state η", "", 1.0),
    ("partPhi", "final-state φ", "rad", 1.0),
]
SAMPLES = ("nominal", "afterburner", "pythia8")
# Palette: two categorical slots of the dataviz reference palette (validated light), muted ink for context.
COLOR = {"afterburner": "#2a78d6", "pythia8": "#eb6834", "nominal": "#898781"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e1e0d9"
LABEL = {"nominal": "head-on Pythia8 (no effects)", "afterburner": "head-on + abconv",
         "pythia8": "Pythia8 + eicBeamShape"}


def load(path, name, scale):
    h = uproot.open(path)[f"after/{name}"]
    v = h.values(flow=True)
    return v[1:-1].astype(float), h.axis().edges() * scale, float(v[0]), float(v[-1])


def stats(c, e):
    x = 0.5 * (e[1:] + e[:-1])
    n = c.sum()
    m = (c * x).sum() / n
    return n, m, np.sqrt((c * (x - m) ** 2).sum() / n)


def chi2(a, b):
    """Two-sample chi2 / ndf of the shapes (unequal totals). Final-state entries are not
    independent (many particles per event), so for eta and phi it overstates the significance."""
    na, nb = a.sum(), b.sum()
    k = (a + b) > 0
    num = (a[k] / na - b[k] / nb) ** 2
    den = a[k] / na**2 + b[k] / nb**2
    return float((num / den).sum()), int(k.sum() - 1)


def display(c_list, e, name):
    """Rebinned view around the beam-effects samples: mean ± 5σ, about 60 bins."""
    if name in ("partEta", "partPhi"):
        lo, hi = e[0], e[-1]
    else:
        lo = min(stats(c, e)[1] - 5 * stats(c, e)[2] for c in c_list)
        hi = max(stats(c, e)[1] + 5 * stats(c, e)[2] for c in c_list)
        lo, hi = max(lo, e[0]), min(hi, e[-1])
    i0 = max(int(np.searchsorted(e, lo, side="right")) - 1, 0)
    i1 = min(int(np.searchsorted(e, hi, side="left")), len(e) - 1)
    f = max((i1 - i0) // 60, 1)
    i1 = i0 + ((i1 - i0) // f) * f
    return i0, i1, f


def rebin(c, i0, i1, f):
    return c[i0:i1].reshape(-1, f).sum(axis=1)


def read_events(path, n):
    """First n events of a HepMC3 text file: event shift (E line @), first vertex position,
    four-momenta of the status-4 particles."""
    out, cur = [], None
    with open(path) as fh:
        for line in fh:
            if line.startswith("E "):
                if cur is not None:
                    out.append(cur)
                    if len(out) >= n:
                        return out
                p = line.split()
                cur = {"shift": tuple(map(float, p[p.index("@") + 1:])) if "@" in p else None,
                       "vtx": None, "beams": []}
            elif cur is None:
                continue
            elif line.startswith("V ") and cur["vtx"] is None:
                p = line.split()
                cur["vtx"] = tuple(map(float, p[p.index("@") + 1:])) if "@" in p else None
            elif line.startswith("P "):
                p = line.split()
                if p[-1] == "4":
                    cur["beams"].append(tuple(map(float, p[4:8])))
    if cur is not None and len(out) < n:
        out.append(cur)
    return out


def ip(ev):
    return ev["shift"] if ev["shift"] is not None else ev["vtx"]


def same(a, b):
    """Equal up to rounding: the head-on Pythia8 beams of two seeds already differ at 1e-14."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    return a.shape == b.shape and bool(np.allclose(a, b, rtol=1e-9, atol=1e-9))


def seed_check(d, n):
    rows = []
    for what, f1, f2 in (("abconv on two head-on files (Pythia8 seeds s, s+1)",
                          "seedcheck_ab_s1.hepmc", "seedcheck_ab_s2.hepmc"),
                         ("Pythia8 + eicBeamShape, seeds s and s+1",
                          "py8_full.hepmc", "py8_full_s2.hepmc")):
        a, b = read_events(d / f1, n), read_events(d / f2, n)
        m = min(len(a), len(b))
        same_ip = sum(same(ip(a[i]), ip(b[i])) for i in range(m))
        same_beams = sum(same(a[i]["beams"], b[i]["beams"]) for i in range(m))
        spread = np.std([ip(a[i])[2] for i in range(m)])
        rows.append({"comparison": what, "events": m, "same_ip": same_ip, "same_beams": same_beams,
                     "ip_z_std_mm": float(spread)})
    return rows


def figure(d, energy, run, out_png):
    data = {s: {h[0]: load(d / f"{s}.hist.root", h[0], h[3]) for h in HISTS} for s in SAMPLES}
    fig = plt.figure(figsize=(22, 10.5), facecolor="#fcfcfb")
    gs = fig.add_gridspec(5, 5, height_ratios=[3, 1, 0.75, 3, 1], hspace=0.08, wspace=0.28)
    rows = []
    for k, (name, label, unit, _) in enumerate(HISTS):
        r, col = 3 * (k // 5), k % 5
        ax, axr = fig.add_subplot(gs[r, col]), fig.add_subplot(gs[r + 1, col])
        e = data["pythia8"][name][1]
        i0, i1, f = display([data[s][name][0] for s in ("afterburner", "pythia8")], e, name)
        edges = e[i0:i1 + 1:f]
        vals = {}
        for s in SAMPLES:
            c, _, under, over = data[s][name]
            n, m, sd = stats(c, e)
            rows.append({"energy": energy, "hist": name, "sample": s, "entries": int(n), "mean": m,
                         "std": sd, "outside_range": (under + over) / (n + under + over)})
            rb = rebin(c, i0, i1, f)
            vals[s] = rb
            dens = rb / c.sum() / np.diff(edges)
            if s == "nominal" and name not in ("partEta", "partPhi"):
                continue  # a delta at zero: no shape to show
            ax.stairs(dens, edges, baseline=None, color=COLOR[s], lw=1.6 if s != "nominal" else 1.2,
                      ls="--" if s == "nominal" else "-", label=LABEL[s])
        x2, ndf = chi2(data["afterburner"][name][0], data["pythia8"][name][0])
        rows.append({"energy": energy, "hist": name, "sample": "chi2/ndf ab vs py8",
                     "entries": ndf, "mean": x2 / max(ndf, 1), "std": float("nan"), "outside_range": float("nan")})
        a, p = vals["afterburner"], vals["pythia8"]
        na, npy = data["afterburner"][name][0].sum(), data["pythia8"][name][0].sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = (a / na) / (p / npy)
            err = ratio * np.sqrt(1 / a + 1 / p)
        xc = 0.5 * (edges[1:] + edges[:-1])
        ok = (a > 0) & (p > 0)
        axr.errorbar(xc[ok], ratio[ok], yerr=err[ok], fmt="o", ms=2.5, color=COLOR["afterburner"],
                     ecolor=COLOR["afterburner"], elinewidth=0.8)
        axr.axhline(1.0, color=INK2, lw=0.8)
        axr.set_ylim(0.5, 1.5)
        ax.set_title(label, fontsize=10, color=INK, loc="left")
        axr.set_xlabel(f"{label} [{unit}]" if unit else label, fontsize=9, color=INK2)
        if col == 0:
            ax.set_ylabel("density", fontsize=9, color=INK2)
            axr.set_ylabel("ab / py8", fontsize=9, color=INK2)
        ax.tick_params(labelbottom=False)
        for a_ in (ax, axr):
            a_.set_xlim(edges[0], edges[-1])
            a_.grid(True, color=GRID, lw=0.6)
            a_.set_axisbelow(True)
            a_.tick_params(labelsize=8, colors=INK2)
            for sp in a_.spines.values():
                sp.set_color("#c3c2b7")
        if k == 8:  # the only panels with all three samples
            fig.legend(*ax.get_legend_handles_labels(), loc="upper right", ncol=3, fontsize=9,
                       frameon=False, bbox_to_anchor=(0.99, 0.965))
        sd_a = [r_ for r_ in rows if r_["hist"] == name and r_["sample"] == "afterburner"][0]["std"]
        sd_p = [r_ for r_ in rows if r_["hist"] == name and r_["sample"] == "pythia8"][0]["std"]
        ax.text(0.98, 0.95, f"σ ab/py8 = {sd_a / sd_p:.3f}\nχ²/ndf = {x2 / max(ndf, 1):.2f}",
                transform=ax.transAxes, ha="right", va="top", fontsize=8, color=INK2)
    fig.suptitle(f"{energy}: afterburner (abconv {run['preset']}) on head-on Pythia8 vs Pythia8 with "
                 f"eicBeamShape beam effects — {run['n_events']} events each, seed {run['seed']}, {run['image']}",
                 fontsize=12, color=INK, x=0.01, ha="left")
    fig.savefig(out_png, dpi=110, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return rows


def main():
    out = Path(sys.argv[1])
    (out / "plots").mkdir(parents=True, exist_ok=True)
    all_rows, md = [], ["# Afterburner vs Pythia8 beam effects", ""]
    for energy in sys.argv[2:]:
        d = out / energy
        run = dict(kv.split("=", 1) for kv in (d / "run.txt").read_text().split())
        rows = figure(d, energy, run, out / "plots" / f"{energy}_comparison.png")
        all_rows += rows
        md += [f"## {energy}", "", "`" + " ".join(f"{k}={v}" for k, v in run.items()) + "`", "",
               "| histogram (unit as in the figure) | nominal | afterburner mean ± σ | pythia8 mean ± σ | σ ab/py8 | "
               "(mean ab − py8)/σ py8 | χ²/ndf | outside range ab / py8 |",
               "|---|---|---|---|---|---|---|---|"]
        for name, _, _, _ in HISTS:
            g = {r["sample"]: r for r in rows if r["hist"] == name}
            a, p, nm, c = g["afterburner"], g["pythia8"], g["nominal"], g["chi2/ndf ab vs py8"]
            nom = "δ at 0" if name not in ("partEta", "partPhi") else f"{nm['mean']:.4g} ± {nm['std']:.4g}"
            md.append(f"| {name} | {nom} | {a['mean']:.4g} ± {a['std']:.4g} | "
                      f"{p['mean']:.4g} ± {p['std']:.4g} | {a['std'] / p['std']:.3f} | "
                      f"{(a['mean'] - p['mean']) / p['std']:+.3f} | {c['mean']:.2f} ({c['entries']}) | "
                      f"{a['outside_range']:.2e} / {p['outside_range']:.2e} |")
        sc = seed_check(d, int(run["n_seed_check"]))
        md += ["", "Seed check (event by event, first events of each file):", "",
               "| comparison | events | same interaction point | same beam four-vectors (rel. 1e-9) | σ(z) of the IP [mm] |",
               "|---|---|---|---|---|"]
        for r in sc:
            md.append(f"| {r['comparison']} | {r['events']} | {r['same_ip']} | {r['same_beams']} | "
                      f"{r['ip_z_std_mm']:.1f} |")
            all_rows.append({"energy": energy, "hist": "seed_check", "sample": r["comparison"],
                             "entries": r["events"], "mean": r["same_ip"], "std": r["same_beams"],
                             "outside_range": r["ip_z_std_mm"]})
        md.append("")
    with open(out / "summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(all_rows[0]))
        w.writeheader()
        w.writerows(all_rows)
    (out / "summary.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
