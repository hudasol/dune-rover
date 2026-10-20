#!/usr/bin/env python3
"""Diagnostic (not pre registered; run after an informal check showed the gap): does the repository's Bekker Wong
family reproduce Ishigami et al. 2007 Fig. 11 (drawbar pull against slip, FJS-1 simulant, wheel radius 0.09 m, width
0.11 m, load 64.7 N) with the parameter values of their Table I?

    PYTHONPATH=src python3 scripts/check_bw_ishigami2007.py

The published curve has a 5 deg slip angle; the family models straight driving and omits the paper's slip sinkage
parameter (lambda 0.90 to 1.10 in Table I), so a gap is expected; the size of the gap is the point.
Output: results/model_validation/bw_vs_ishigami2007.csv.  SIMULATED BY ME against PUBLISHED points.
"""
import csv, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover.models.bekker_wong import _forces, SOIL_SETS  # noqa: E402

R, B, W = 0.09, 0.11, 64.7


def dp_at(i, k_mult=1.0):
    kc, kphi, n, c, phi, K, a0, a1, _ = SOIL_SETS["fjs1_ishigami2007"]
    lo, hi = 1e-7, 0.999 * R
    for _ in range(40):
        m = 0.5 * (lo + hi)
        fz, _ = _forces(np.array([m]), np.array([i]), R, B, kc * k_mult, kphi * k_mult, n, c, phi, K, a0, a1)
        lo, hi = (lo, m) if fz[0] > W else (m, hi)
    fz, dp = _forces(np.array([m]), np.array([i]), R, B, kc * k_mult, kphi * k_mult, n, c, phi, K, a0, a1)
    return float(dp[0]), float(m)


rows = [r for r in csv.DictReader(open(os.path.join(ROOT, "research", "phase3", "curves.csv"), encoding="utf-8")) if r["curve_id"].startswith("ishigami2007_fig11")]
out = []
for r in rows:
    i, dpm = float(r["x"]), float(r["y"])
    d1, z1 = dp_at(i); d10, z10 = dp_at(i, 10.0)
    out.append({"slip": i, "published_dp_N": dpm, "family_dp_N": round(d1, 2), "family_sinkage_mm": round(z1 * 1000, 1),
                "family_dp_N_k_mult_10": round(d10, 2), "family_sinkage_mm_k_mult_10": round(z10 * 1000, 1)})
os.makedirs(os.path.join(ROOT, "results", "model_validation"), exist_ok=True)
with open(os.path.join(ROOT, "results", "model_validation", "bw_vs_ishigami2007.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for o in out:
    print(o)
