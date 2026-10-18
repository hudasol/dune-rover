#!/usr/bin/env python3
"""Stage 11 diagnostic (docs/PREDICTIONS.md): share of Monte Carlo draws in which the vehicle cannot move on level ground.

SIMULATED BY ME, simulation only, model assumption dependent.  A draw is immobile on level ground when its slip at zero
slope already exceeds its planning limit i_max, that is f_r / tan(phi) >= 1 - exp(-i_max / i0).  Uses the phase 2 draws
(threeclass.lhs_draws, 256 per area, seeds of areas A, B, C) under each range set.  No elevation data needed.
Usage: PYTHONPATH=src python3 scripts/diagnose_level_ground.py
"""
import csv, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover.slipmodel import RANGE_SETS, use_range_set, slip  # noqa: E402
from dunerover import threeclass as TC  # noqa: E402
from dunerover.study_subgrid import AREAS, N_DRAWS  # noqa: E402

rows = []
for rs in RANGE_SETS:
    with use_range_set(rs):
        for name, spec in AREAS.items():
            draws = TC.lhs_draws(N_DRAWS, spec[6])
            stuck = [float(slip(0.0, 0.0, p)) > p.i_max for p in draws]
            rows.append({"label": "SIMULATED BY ME, diagnostic", "range_set": rs, "area": name, "draws": len(draws),
                         "share_immobile_on_level": float(np.mean(stuck))})
out = os.path.join(ROOT, "results", "range_set_diagnostics")
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "immobile_on_level.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows:
    print(r["range_set"], r["area"], f"{100*r['share_immobile_on_level']:.1f} %")
