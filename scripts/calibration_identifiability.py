#!/usr/bin/env python3
"""Design check for the field plan (SIMULATED-BY-ME, synthetic data generated from the model itself).

Question: if the model were exactly right, how well could runs at <= 10 (or <= 15) degrees calibrate it
to predict slip at steeper slopes, for a given run-to-run noise sigma and number of runs per slope bin?
Writes results/field_plan_identifiability.csv.  Seeds 0..59 for the synthetic replicates.
"""
import csv, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from dunerover import fieldanalysis as FA

rows = []
for sigma in (0.03, 0.06, 0.10):
    for rpb in (5, 10):
        for cmax in (10, 15):
            mae, floor, bad = [], [], 0
            for sd in range(60):
                d = FA.synthetic_runs(seed=sd, sigma=sigma, runs_per_bin=rpb)
                s = FA.observed_slip(d); sl = d["slope_deg"]
                cal = (sl <= cmax) & ~d["entrapped"]; test = sl > cmax
                f_r, i0 = FA.calibrate(sl[cal], s[cal], 33.0)
                e = np.abs(FA.model_slip(sl[test], f_r, i0, 33.0) - s[test])
                mae.append(e.mean()); floor.append(np.abs(FA.model_slip(sl[test], 0.14, 0.22, 33.0) - s[test]).mean())
                bad += int((e <= FA.ADEQ_TOL).mean() >= FA.ADEQ_FRAC)
            rows.append(dict(sigma=sigma, runs_per_bin=rpb, calibrate_up_to_deg=cmax, median_heldout_mae=round(float(np.median(mae)), 3),
                             p90_heldout_mae=round(float(np.percentile(mae, 90)), 3), median_mae_true_params=round(float(np.median(floor)), 3),
                             share_replicates_within_tol_for_80pct_runs=round(bad / 60, 2)))
os.makedirs("results", exist_ok=True)
with open("results/field_plan_identifiability.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
