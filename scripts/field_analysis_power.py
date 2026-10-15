#!/usr/bin/env python3
"""Synthetic power and false-alarm study of the pre-registered field analysis.  SIMULATED-BY-ME, synthetic data only.

For each truth generator (model, janosi_mean, collapse) and noise sigma, run the analysis with the tolerance set from
the pilot block (3 x pilot sigma, floor 0.05) on many synthetic replicate datasets and report how often the model is
called adequate.  `collapse` is a case where the model is wrong by construction; a good rule fails it.

Design, predictions and seeds were fixed in docs/PREDICTIONS.md (stage 3) before this script was run.  The revised
ladder (--design 2026-10-15, stage 6) adds the truth `dumont` (the published Dumont Dunes curve used as a synthetic truth)
and writes power_study_2026-10-15.csv; the default design reproduces the stage 3 file power_study.csv.
Usage: PYTHONPATH=src python3 scripts/field_analysis_power.py [--reps 300] [--out results/field_kit] [--design 2026-10-12|2026-10-15]
"""
import argparse, csv, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from dunerover import fieldanalysis as FA

ap = argparse.ArgumentParser(); ap.add_argument("--reps", type=int, default=300); ap.add_argument("--out", default="results/field_kit")
ap.add_argument("--design", default="2026-10-12", choices=("2026-10-12", "2026-10-15"))
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
rows = []; t0 = time.time()
kinds = ("model", "janosi_mean", "collapse") + (("dumont",) if a.design != "2026-10-12" else ())
bw = 5.0 if a.design == "2026-10-12" else 2.5
for kind in kinds:
    for sigma in (0.03, 0.06, 0.10):
        adeq, uninf, tols, within, mae = [], [], [], [], []
        for k in range(a.reps):
            d = FA.synthetic_runs(seed=30000 + k, sigma=sigma, kind=kind, design=a.design)
            try:
                r = FA.analyse(d, n_boot=20, bin_width=bw)
            except Exception as e:      # too few calibration runs after entrapment removal, etc.
                continue
            adeq.append(r.adequate); uninf.append(not r.informative); tols.append(r.tol); within.append(r.frac_within_tol); mae.append(r.mae)
        n = len(adeq)
        rows.append({"truth": kind, "sigma": sigma, "replicates": n, "adequate_rate": float(np.mean(adeq)), "failure_rate": 1 - float(np.mean(adeq)),
                     "flagged_uninformative_rate": float(np.mean(uninf)), "median_tolerance": float(np.median(tols)),
                     "median_frac_within_tol": float(np.median(within)), "median_mae": float(np.median(mae))})
        print(rows[-1], f"[{time.time()-t0:.0f}s]", flush=True)
fn = "power_study.csv" if a.design == "2026-10-12" else f"power_study_{a.design}.csv"
with open(os.path.join(a.out, fn), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
