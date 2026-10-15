#!/usr/bin/env python3
"""POST HOC diagnostic (not pre registered), SIMULATED BY ME on synthetic data only.

Why does a correct model fail the adequacy rule under the 2026-10-15 ladder (docs/PREDICTIONS.md, L6-3)?  For the
first 60 replicates of the stage 3 and stage 6 power studies (truth = model, sigma 0.03, same seeds), record whether the
observed entrapment slope is defined and the share of held out runs within the tolerance.  Writes
results/field_kit/diagnostic_entrapment_2026-10-15.csv.  Usage: PYTHONPATH=src python3 scripts/diagnose_ladder_entrapment.py
"""
import csv, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover import fieldanalysis as FA

N = 60
rows = []
for design, bw in (("2026-10-12", 5.0), ("2026-10-15", 2.5)):
    undefined, within, adequate = [], [], []
    for k in range(N):
        r = FA.analyse(FA.synthetic_runs(seed=30000 + k, sigma=0.03, kind="model", design=design), n_boot=5, bin_width=bw)
        undefined.append(not np.isfinite(r.entrap_obs_deg)); within.append(r.frac_within_tol); adequate.append(r.adequate)
    rows.append({"label": "POST HOC diagnostic, SIMULATED BY ME, synthetic data only", "design": design, "truth": "model", "sigma": 0.03,
                 "replicates": N, "share_observed_entrapment_undefined": float(np.mean(undefined)),
                 "median_frac_within_tol": float(np.median(within)), "adequate_rate": float(np.mean(adequate)),
                 "true_entrapment_slope_deg": FA.entrapment_slope_model(0.14, 0.22, 33.0)})
out = os.path.join(ROOT, "results", "field_kit", "diagnostic_entrapment_2026-10-15.csv")
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows:
    print(r)
