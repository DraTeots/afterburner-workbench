#!/usr/bin/env python3
"""Sign check of the beam geometry: abconv against Pythia8's eicBeamShape (crossing angle -0.025 rad).

For each event: the interaction point (abconv: the event shift; Pythia8: the first vertex) and the two
beam particles (status 4). With hadron bunch position z_h and lepton bunch position z_e, both codes give
  t = (z_e - z_h) / 2,  z = (z_e + z_h) / 2   ->   z_e = z + t,  z_h = z - t,
the IP x follows x ~ (theta/2) * z_e (bunch crossing at half the crossing angle theta), and the crab kick
tilts each beam in proportion to its own particle's bunch position. A slope's sign therefore shows which
crossing angle the vertex and the kicks were built with, independent of the beams' mean direction.

Runs inside eic_xl (numpy):  signs.py <out_dir> <setup>:<abconv hepmc>:<pythia8 hepmc> [...]
"""
import sys
from pathlib import Path

import numpy as np


def read(path, n=None):
    ip, b1, b2 = [], [], []
    cur = None

    def close():
        if cur and cur["ip"] is not None and len(cur["beams"]) == 2:
            ip.append(cur["ip"]); b1.append(cur["beams"][0]); b2.append(cur["beams"][1])

    with open(path) as fh:
        for line in fh:
            if line.startswith("E "):
                close()
                if n and len(ip) >= n:
                    cur = None
                    break
                p = line.split()
                cur = {"ip": tuple(map(float, p[p.index("@") + 1:])) if "@" in p else None, "beams": []}
            elif cur is None:
                continue
            elif line.startswith("V ") and cur["ip"] is None:
                p = line.split()
                cur["ip"] = tuple(map(float, p[p.index("@") + 1:])) if "@" in p else None
            elif line.startswith("P "):
                p = line.split()
                if p[-1] == "4":
                    cur["beams"].append(tuple(map(float, p[3:8])))  # pdg, px, py, pz, e
    close()
    ip, b1, b2 = np.array(ip), np.array(b1), np.array(b2)
    # order the beams by PDG id: proton (2212) and electron (11)
    swap = b1[:, 0] == 11
    pr = np.where(swap[:, None], b2, b1)
    el = np.where(swap[:, None], b1, b2)
    return ip, pr, el


def slope(y, x):
    """Least-squares slope dy/dx, its standard error, and the correlation coefficient."""
    x = x - x.mean(); y = y - y.mean()
    b = (x * y).sum() / (x * x).sum()
    r = (x * y).sum() / np.sqrt((x * x).sum() * (y * y).sum())
    se = np.sqrt(((y - b * x) ** 2).sum() / (len(x) - 2) / (x * x).sum())
    return b, se, r


def quantities(ip, pr, el):
    x, y, z, t = ip.T
    ang_p = np.arctan2(pr[:, 1], pr[:, 3])            # proton horizontal angle [rad]
    ang_e = np.arctan2(el[:, 1], -el[:, 3])           # electron horizontal angle (along -z) [rad]
    return {
        "proton angle mean [mrad]": (1e3 * ang_p.mean(), None, None),
        "electron angle mean [mrad]": (1e3 * ang_e.mean(), None, None),
        "dx/d(z+t)  IP x vs lepton bunch position [mrad]": tuple(1e3 * v if i < 2 else v
                                                                  for i, v in enumerate(slope(x, z + t))),
        "dx/dz  IP x vs IP z [mrad]": tuple(1e3 * v if i < 2 else v for i, v in enumerate(slope(x, z))),
        "d(proton angle)/d(z−t) crab, hadron bunch position [µrad/mm]": tuple(
            1e6 * v if i < 2 else v for i, v in enumerate(slope(ang_p, z - t))),
        "d(electron angle)/d(z+t) crab, lepton bunch position [µrad/mm]": tuple(
            1e6 * v if i < 2 else v for i, v in enumerate(slope(ang_e, z + t))),
    }


def main():
    out = Path(sys.argv[1])
    md = ["# Beam-geometry signs: abconv vs Pythia8 eicBeamShape (θ = −25 mrad)", ""]
    for spec in sys.argv[2:]:
        setup, fab, fpy = spec.split(":")
        qa = quantities(*read(fab))
        qp = quantities(*read(fpy))
        md += [f"## {setup}", "", f"abconv: `{fab}`; Pythia8: `{fpy}`", "",
               "| quantity | abconv | Pythia8 + eicBeamShape | same sign |", "|---|---|---|---|"]
        for k in qa:
            a, p = qa[k], qp[k]
            fa = f"{a[0]:+.4g}" + (f" ± {a[1]:.2g} (r {a[2]:+.2f})" if a[1] is not None else "")
            fp = f"{p[0]:+.4g}" + (f" ± {p[1]:.2g} (r {p[2]:+.2f})" if p[1] is not None else "")
            sig = (lambda q: abs(q[0]) > 3 * q[1]) if a[1] is not None else (lambda q: abs(q[0]) > 0.01)
            verdict = ("yes" if np.sign(a[0]) == np.sign(p[0]) else "**no**") if sig(a) and sig(p) else "zero within noise"
            md.append(f"| {k} | {fa} | {fp} | {verdict} |")
        md.append("")
    (out / "signs.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
