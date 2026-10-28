#!/usr/bin/env python3
"""Runtime of the planner on one benchmark window (review finding M15): assessment of the map (128 parameter draws,
posterior vehicle) and 100 routes with the weight policy, on one processor core.

    OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/benchmark_runtime.py

Output: results/benchmark/runtime.csv (wall clock seconds, median of three repeats; machine dependent).
"""
from __future__ import annotations
import csv, os, platform, sys, time
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dunerover import benchmark as B, planner as PL  # noqa: E402
import benchmark_stage28 as S  # noqa: E402


def main(site="Kelso"):
    T = S.site_truth(site)
    surf = S.surfaces(site, T)
    pairs = S.endpoints_E1(site)
    rows = []
    for inp in ("I30", "I10"):
        zc, k = surf[inp]
        ta, tr = [], []
        for _ in range(3):
            t0 = time.perf_counter()
            a = PL.assess(PL.raster_from_array(zc, float(k)), profile=PL.builtin_profile("published-posterior"), n_draws=128)
            ta.append(time.perf_counter() - t0)
            g, _ = S.base_graph(a, True)
            keep = ((a.classes != 1) & (a.classes != 5)).ravel()
            sh = a.classes.shape
            t0 = time.perf_counter()
            B.routes_from(S.masked(g, keep, a.face_prob, 5.0), sh[1], [S.BP.cell_of(p[0], k, sh) for p in pairs], [S.BP.cell_of(p[1], k, sh) for p in pairs])
            tr.append(time.perf_counter() - t0)
        rows.append({"site": site, "input": inp, "grid": f"{sh[0]} x {sh[1]}", "area_km2": round(sh[0] * sh[1] * k * k / 1e6, 1),
                     "assess_s": round(float(np.median(ta)), 2), "routes_100_s": round(float(np.median(tr)), 2),
                     "machine": f"{platform.machine()}, {os.environ.get('OMP_NUM_THREADS', 'all')} thread(s)"})
        print(rows[-1], flush=True)
    with open(os.path.join(ROOT, "results", "benchmark", "runtime.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
