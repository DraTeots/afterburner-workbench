#!/usr/bin/env python3
"""Displaced-vertex consistency in HepMC3 text files (afterburner PR #38 review).

For every decayed particle (status 2) with an explicit end vertex (its own position), the displacement
d = end vertex - production vertex must point along the particle's momentum, and its time must be
dt = |d| / beta. A frame transformation applied to momenta but not to positions breaks both.
Prints, per file, the angle between d and p (all decays, and the forward ones with theta < 0.1 rad),
and the median of dt * beta / |d|.

Runs inside eic_xl (numpy):  vertices.py <label>=<file.hepmc> [...]   (first 20000 events)
"""
import sys

import numpy as np

N_EVENTS = 20000
MIN_DISPLACEMENT = 1.0  # mm


def decays(path):
    rows = []
    n = 0

    def flush(ev):
        if ev is None:
            return
        epos, vpos, vin, parts = ev
        end = {}
        for vid, plist in vin.items():
            if vid in vpos and len(plist) == 1:
                end[plist[0]] = vpos[vid]

        def vertex(vid, depth):
            """HepMC3 GenVertex::position(): an unset vertex takes its first incoming particle's
            production position, else the event position."""
            if vid in vpos:
                return vpos[vid]
            for k in vin.get(vid, []):
                if k in parts and depth < 50:
                    return prod(k, depth + 1)
            return epos

        def prod(pid, depth=0):
            f = parts[pid][0]
            if f < 0:
                return vertex(f, depth)
            if f in end:
                return end[f]
            return prod(f, depth + 1) if f in parts and depth < 50 else epos

        for pid, (f, pdg, p4, status) in parts.items():
            if pid not in end or status != 2:  # decayed particles only (beams are status 4)
                continue
            a, b = np.array(prod(pid)), np.array(end[pid])
            d = b[:3] - a[:3]
            L = np.linalg.norm(d)
            if L < MIN_DISPLACEMENT:
                continue
            p = np.array(p4[:3]); pm = np.linalg.norm(p)
            cosang = np.clip(d @ p / (L * pm), -1, 1)
            beta = pm / p4[3]
            rows.append((pdg, np.arccos(cosang), np.arccos(np.clip(p[2] / pm, -1, 1)),
                         (b[3] - a[3]) * beta / L, L))

    ev = None
    with open(path) as fh:
        for line in fh:
            if line.startswith("E "):
                flush(ev)
                n += 1
                if n > N_EVENTS:
                    ev = None
                    break
                q = line.split()
                epos = tuple(map(float, q[q.index("@") + 1:])) if "@" in q else (0.0, 0.0, 0.0, 0.0)
                ev = (epos, {}, {}, {})
            elif ev is None:
                continue
            elif line.startswith("V "):
                q = line.split()
                vid = int(q[1])
                ins = q[3].strip("[]")
                ev[2][vid] = [int(x) for x in ins.split(",") if x]
                if "@" in q:
                    ev[1][vid] = tuple(map(float, q[q.index("@") + 1:]))
            elif line.startswith("P "):
                q = line.split()
                ev[3][int(q[1])] = (int(q[2]), int(q[3]), tuple(map(float, q[4:8])), int(q[-1]))
    flush(ev)
    return np.array(rows)


def main():
    print("| file | decays (|d| > 1 mm) | angle(d, p) median [mrad] | 90 % [mrad] | forward (θ < 0.1) median [mrad] | "
          "forward 90 % [mrad] | dt·β/|d| median | Λ decays |")
    print("|---|---|---|---|---|---|---|---|")
    for spec in sys.argv[1:]:
        label, path = spec.rsplit("=", 1)
        r = decays(path)
        ang, theta, tr, pdg = r[:, 1], r[:, 2], r[:, 3], r[:, 0]
        fw = theta < 0.1
        print(f"| {label} | {len(r)} | {1e3 * np.median(ang):.3f} | {1e3 * np.quantile(ang, 0.9):.3f} | "
              f"{1e3 * np.median(ang[fw]):.3f} | {1e3 * np.quantile(ang[fw], 0.9):.3f} | {np.median(tr):.4f} | "
              f"{int((np.abs(pdg) == 3122).sum())} |")


if __name__ == "__main__":
    main()
