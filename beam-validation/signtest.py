"""Sign test of abconv variants built with abconv-signtest.patch (AB_XH, AB_XV, AB_ROOTFIX): beam angles (h, v),
IP slopes with and without the time axis, crab slopes, beam energy shifts (head-on beams 100 and 10 GeV).
Runs with numpy (uv run, or inside eic_xl): signtest.py label=file.hepmc ..."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from signs import read, slope  # noqa: E402

E0 = {"p": 100.0, "e": 10.0}
print("| file | p h [mrad] | p v [mrad] | e h [mrad] | e v [mrad] | dx/d(z+t) [mrad] | dx/dz | dx/dt | dx/d(z−t) "
      "| dy/d(z+t) | p crab [µrad/mm] | e crab | ΔE/E p | ΔE/E e |")
print("|---|" + "---|" * 13)
for spec in sys.argv[1:]:
    label, path = spec.rsplit("=", 1)
    ip, pr, el = read(path)
    x, y, z, t = ip.T
    ph = np.arctan2(pr[:, 1], pr[:, 3]); pv = np.arctan2(pr[:, 2], pr[:, 3])
    eh = np.arctan2(el[:, 1], -el[:, 3]); ev = np.arctan2(el[:, 2], -el[:, 3])

    def s(a, b, k=1e3):
        v, e, _ = slope(a, b)
        return f"{k * v:+.3f} ± {k * e:.3f}"

    print(f"| {label} | {1e3 * ph.mean():+.3f} | {1e3 * pv.mean():+.4f} | {1e3 * eh.mean():+.4f} | {1e3 * ev.mean():+.4f} | "
          f"{s(x, z + t)} | {s(x, z)} | {s(x, t)} | {s(x, z - t)} | {s(y, z + t)} | {s(ph, z - t, 1e6)} | {s(eh, z + t, 1e6)} | "
          f"{pr[:, 4].mean() / E0['p'] - 1:+.3e} | {el[:, 4].mean() / E0['e'] - 1:+.3e} |")
