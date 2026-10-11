#!/usr/bin/env python3
"""CLI for the pre-registered field analysis (PLANNED; tested on synthetic data only).

Usage:  python3 scripts/analyze_field_runs.py runs.csv [--out results_field]
        python3 scripts/analyze_field_runs.py --synthetic          # demo on SYNTHETIC data
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from dataclasses import asdict
from dunerover import fieldanalysis as FA

ap = argparse.ArgumentParser()
ap.add_argument("csv", nargs="?")
ap.add_argument("--synthetic", action="store_true")
ap.add_argument("--out", default=None)
a = ap.parse_args()
if a.synthetic:
    d, label = FA.synthetic_runs(), "SYNTHETIC DATA - code demonstration, not a measurement"
elif a.csv:
    d, label = FA.load_runs(a.csv), "field measurement, one vehicle, one site (fill in vehicle, wheels, soil, site)"
else:
    ap.error("give a CSV or --synthetic")
res = FA.analyse(d)
out = {"label": label, "result": asdict(res), "per_bin": FA.per_bin_means(d)}
print(json.dumps(out, indent=2))
if a.out:
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "field_analysis.json"), "w"), indent=2)
