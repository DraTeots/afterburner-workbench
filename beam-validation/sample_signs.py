"""The same sign check on the meson-structure sample: beam rows (generator status 4) of mc_particles.

Prints the proton beam angle, the slope of the interaction-point x against the lepton bunch position
z + c·t (abconv's IP construction, see signs.py) and the crab slope of the proton angle against z − c·t.
  uv run --with numpy --with polars beam-validation/sample_signs.py [stem number, default 1]
"""
import sys
import zipfile

import numpy as np
import polars as pl

C = 299.792458  # mm/ns
STEM = int(sys.argv[1]) if len(sys.argv) > 1 else 1


def slope(y, x):
    x = x - x.mean(); y = y - y.mean()
    b = (x * y).sum() / (x * x).sum()
    r = (x * y).sum() / np.sqrt((x * x).sum() * (y * y).sum())
    se = np.sqrt(((y - b * x) ** 2).sum() / (len(x) - 2) / (x * x).sum())
    return b, se, r


for energy in ("9x100", "9x130"):
    f = f"/data/meson-structure-2026-11/csv-reco/{energy}/msf_{energy}_1000evt_{STEM:04d}.mc_particles.csv.zip"
    with zipfile.ZipFile(f) as z:
        df = pl.read_csv(z.open(z.namelist()[0]))
    p = df.filter((pl.col("prt_gen_status") == 4) & (pl.col("prt_pdg") == 2212)).sort("evt")
    x, z, t = (p[c].to_numpy() for c in ("prt_vtx_pos_x", "prt_vtx_pos_z", "prt_vtx_time"))
    t = t * C
    ang = np.arctan2(p["prt_mom_x"].to_numpy(), p["prt_mom_z"].to_numpy())
    b1, s1, r1 = slope(x, z + t)
    b2, s2, r2 = slope(ang, z - t)
    print(f"{energy} stem {STEM}: {len(x)} events | proton angle {1e3 * ang.mean():+.3f} mrad | "
          f"dx/d(z+t) {1e3 * b1:+.2f} ± {1e3 * s1:.2f} mrad (r {r1:+.2f}) | "
          f"d(proton angle)/d(z−t) {1e6 * b2:+.3f} ± {1e6 * s2:.3f} µrad/mm (r {r2:+.2f})")
