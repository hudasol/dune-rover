#!/usr/bin/env python3
"""Named numbers of the stage 25 and 26 benchmark for the README, the brief and the proposals (prefix bm_).

Read by scripts/build_manuscript.py (extra_values) and traced by scripts/build_number_ledger.py. Missing result files
give no values (the templates then fail loudly). SIMULATED BY ME on PUBLISHED elevation data.
"""
from __future__ import annotations
import csv, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DET = os.path.join(ROOT, "results", "benchmark", "detection")
PLN = os.path.join(ROOT, "results", "benchmark", "planning")


def _read(p):
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh))


def values() -> dict:
    v = {}
    mp = os.path.join(DET, "metrics.csv")
    if os.path.exists(mp):
        met = _read(mp)
        sites = sorted({r["site"] for r in met})
        v["bm_n_sites"] = len(sites)
        for inp in ("I10", "I30", "G30"):
            for m in ("DET", "SLOPE", "TRI", "ROUGH", "BICUBIC", "GBM", "CNN"):
                a = [float(r["auc"]) for r in met if r["input"] == inp and r["method"] == m and r.get("auc", "")]
                if a:
                    tag = f"{inp.lower()}_{m.lower()}"
                    v[f"bm_auc_{tag}_mean"] = f"{np.mean(a):.2f}"
                    v[f"bm_auc_{tag}_min"] = f"{min(a):.2f}"
                    v[f"bm_auc_{tag}_max"] = f"{max(a):.2f}"
            for m in ("DET", "GBM", "CNN"):
                miss = [float(r["miss_at_0.20"]) for r in met if r["input"] == inp and r["method"] == m and r.get("miss_at_0.20", "")]
                if miss:
                    v[f"bm_miss_{inp.lower()}_{m.lower()}_min"] = f"{100 * min(miss):.0f} %"
                    v[f"bm_miss_{inp.lower()}_{m.lower()}_max"] = f"{100 * max(miss):.0f} %"
    sp = os.path.join(PLN, "summary.csv")
    if os.path.exists(sp):
        for r in _read(sp):
            if r["profile"] != "assumed":
                continue
            tag = f"{r['input'].lower()}_{r['policy']}_{r['hazard'].lower().replace('-', '')}"
            for k, short in (("unsafe_of_routed", "unsafe"), ("mission_success", "success"), ("routed", "routed")):
                if r.get(k, ""):
                    v[f"bm_{short}_{tag}"] = f"{100 * float(r[k]):.0f} %"
        ep = os.path.join(PLN, "endpoints.csv")
        if os.path.exists(ep):
            v["bm_pairs"] = len(_read(ep))
    return v


if __name__ == "__main__":
    for k, val in sorted(values().items()):
        print(k, val)
