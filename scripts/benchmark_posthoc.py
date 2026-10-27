#!/usr/bin/env python3
"""POST HOC analyses of stages 25 and 26 (docs/PREDICTIONS.md, note after stage 26; decided after the runs, in response
to the review of 2026-10-28). Not registered predictions; reported as post hoc.

    PYTHONPATH=src python3 scripts/benchmark_posthoc.py     # after benchmark_detection.py and benchmark_planning.py

(i) same rule oracle on the 10 m and 30 m grids; (ii) exposure per km; (iii) patch size sensitivity; (iv) site clustered
intervals for route comparisons; (v) BICUBIC against GBM and CNN in AUC; (vi) GLO-30 shift against the lidar.
Outputs: results/benchmark/posthoc/ (routes.csv, summary.csv, clustered_differences.csv, auc_bicubic.csv, glo30_shift.csv,
run_log.txt). SIMULATED BY ME on PUBLISHED elevation data. Deterministic.
"""
from __future__ import annotations
import csv, os, sys, time
import numpy as np
from scipy.ndimage import shift as nd_shift

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dunerover import benchmark as B, planner as PL  # noqa: E402
import benchmark_detection as BD  # noqa: E402
import benchmark_planning as BP  # noqa: E402

OUT = os.path.join(ROOT, "results", "benchmark", "posthoc")
SEED = 20261028
PATCH_MIN = (10, 100, 500)
CONFIGS = [("naive", "none"), ("shortest", "none")] + [(p, h) for h in ("DET", "DET-cal", "SLOPE-cal", "BICUBIC-cal", "GBM", "CNN", "ORACLE", "ORACLE-ANY")
                                                        for p in ("conservative", "risk_weighted")]


def write(path, rows):
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)


def samples(rc, k, step=0.5):
    pts = (np.asarray(rc, float) + 0.5) * k
    out = [pts[:1]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(int(np.ceil(np.hypot(*(b - a)) / step)), 1)
        out.append(a + (b - a) * (np.arange(1, n + 1)[:, None] / n))
    return np.concatenate(out)


def score(rc, k, masks, shape):
    sp = samples(rc, k)
    ri = np.clip(np.floor(sp[:, 0]).astype(int), 0, shape[0] - 1); ci = np.clip(np.floor(sp[:, 1]).astype(int), 0, shape[1] - 1)
    length = float(np.hypot(np.diff(sp[:, 0]), np.diff(sp[:, 1])).sum())
    r = {"length_m": round(length, 1)}
    for m, P in masks.items():
        on = P[ri, ci]
        r[f"unsafe_p{m}"] = bool(on.any())
        r[f"entries_p{m}"] = int(on[0]) + int((on[1:] & ~on[:-1]).sum())
        r[f"m_on_face_p{m}"] = round(0.5 * float(on.sum()), 1)
    return r


def two_stage_ci(diff_by_site, n_boot=4000, seed=SEED):
    rng = np.random.default_rng(seed)
    sites = [d for d in diff_by_site if len(d)]
    out = []
    for _ in range(n_boot):
        pick = [sites[i] for i in rng.integers(0, len(sites), len(sites))]
        out.append(np.mean(np.concatenate([d[rng.integers(0, len(d), len(d))] for d in pick])))
    return np.percentile(out, [2.5, 97.5])


def main():
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(OUT, "run_log.txt"), "w")

    def say(m):
        print(m, flush=True); log.write(m + "\n"); log.flush()
    say(f"POST HOC run started {time.strftime('%Y-%m-%d %H:%M:%S')}; numpy {np.__version__}; seed {SEED}")
    cache = np.load(BD.CACHE)
    prof = PL.builtin_profile("assumed")
    ends = list(csv.DictReader(open(os.path.join(ROOT, "results", "benchmark", "planning", "endpoints.csv"))))
    rows, shifts = [], []
    for site, (fname, win, _t) in BD.SITES.items():
        t0 = time.time()
        z1, _, _, _ = BD.load_lidar_window(fname, win)
        void = np.isnan(z1); z1f = B.fill_nearest(z1)
        steep, _ = B.steep_posts(z1, void)
        masks = {m: B.face_patches(steep, m) for m in PATCH_MIN}
        pairs = [(np.array([float(e["start_row_m"]), float(e["start_col_m"])]), np.array([float(e["goal_row_m"]), float(e["goal_col_m"])]))
                 for e in ends if e["site"] == site]
        for inp, k in (("I10", 10), ("I30", 30), ("G30", 30)):
            zc = B.block(z1f, k) if inp != "G30" else cache[f"{site}|G30|z"].astype(float)
            a = PL.assess(PL.raster_from_array(zc, float(k)), profile=prof, n_draws=128)
            nr, nc = a.classes.shape
            S = [BP.cell_of(p[0], k, (nr, nc)) for p in pairs]; T = [BP.cell_of(p[1], k, (nr, nc)) for p in pairs]
            for pol, hz in CONFIGS:
                if pol == "shortest":
                    rcs = [B.grid_shortest((nr, nc), s, t) for s, t in zip(S, T)]
                else:
                    if hz == "none":
                        aa = a
                    elif hz == "ORACLE":
                        aa = B.with_hazard(a, cache[f"{site}|{inp}|y"].astype(float))
                    elif hz == "ORACLE-ANY":
                        aa = B.with_hazard(a, B.block(masks[10], k, "any")[:nr, :nc].astype(float))
                    else:
                        aa = B.with_hazard(a, cache[f"{site}|{inp}|{hz}"].astype(float))
                    rcs = B.routes_from(PL.policy_graph(aa, pol), nc, S, T)
                for n, rc in enumerate(rcs):
                    row = {"site": site, "input": inp, "policy": pol, "hazard": hz, "pair": n, "routed": rc is not None}
                    if rc is not None:
                        row.update(score(rc, k, masks, z1.shape))
                    rows.append(row)
        # (vi) GLO-30 shift against the 30 m lidar block mean, in cells (positive rows south, positive columns east)
        a30, g30 = cache[f"{site}|I30|z"].astype(float), cache[f"{site}|G30|z"].astype(float)
        best = None
        for dr in np.arange(-2.0, 2.01, 0.25):
            for dc in np.arange(-2.0, 2.01, 0.25):
                d = (nd_shift(g30, (dr, dc), order=1, mode="nearest") - a30)[4:-4, 4:-4]
                rms = float(np.sqrt(np.mean((d - np.median(d)) ** 2)))
                if best is None or rms < best[0]:
                    best = (rms, dr, dc)
        d0 = (g30 - a30)[4:-4, 4:-4]
        shifts.append({"site": site, "rms_m_no_shift": round(float(np.sqrt(np.mean((d0 - np.median(d0)) ** 2))), 2), "rms_m_best": round(best[0], 2),
                       "best_shift_rows_cells": best[1], "best_shift_cols_cells": best[2], "best_shift_m": round(30.0 * float(np.hypot(best[1], best[2])), 1)})
        say(f"{site}: done in {time.time() - t0:.0f} s; GLO-30 best shift {shifts[-1]['best_shift_m']} m")
    write(os.path.join(OUT, "routes.csv"), rows)
    write(os.path.join(OUT, "glo30_shift.csv"), shifts)

    # (ii), (iii) summaries
    sites = list(BD.SITES)
    summ = []
    for inp in ("I10", "I30", "G30"):
        for pol, hz in CONFIGS:
            rr = [r for r in rows if r["input"] == inp and r["policy"] == pol and r["hazard"] == hz]
            ok = [r for r in rr if r["routed"]]
            km = sum(r["length_m"] for r in ok) / 1000.0
            out = {"input": inp, "policy": pol, "hazard": hz, "pairs": len(rr), "routed": round(len(ok) / len(rr), 4)}
            for m in PATCH_MIN:
                out[f"success_p{m}"] = round(sum(1 for r in ok if not r[f"unsafe_p{m}"]) / len(rr), 4)
                out[f"unsafe_all_pairs_p{m}"] = round(sum(1 for r in ok if r[f"unsafe_p{m}"]) / len(rr), 4)
            out["m_on_face_per_km"] = round(sum(r["m_on_face_p10"] for r in ok) / km, 1) if km else ""
            out["entries_per_km"] = round(sum(r["entries_p10"] for r in ok) / km, 2) if km else ""
            summ.append(out)
    write(os.path.join(OUT, "summary.csv"), summ)

    # (iv) clustered intervals for mission success differences (patch rule 10 m2)
    def vec(inp, pol, hz):
        d = {}
        for r in rows:
            if r["input"] == inp and r["policy"] == pol and r["hazard"] == hz:
                d[(r["site"], r["pair"])] = float(r["routed"] and not r["unsafe_p10"])
        return d
    comps = []
    for inp in ("I10", "I30", "G30"):
        base = vec(inp, "naive", "none")
        for pol, hz in CONFIGS:
            if hz == "none":
                continue
            cur = vec(inp, pol, hz)
            dd = [np.array([cur[(s, n)] - base[(s, n)] for (s2, n) in base if s2 == s]) for s in sites]
            lo, hi = two_stage_ci(dd)
            per_site = [float(d.mean()) for d in dd]
            comps.append({"input": inp, "policy": pol, "hazard": hz, "reference": "naive", "difference": round(float(np.mean(np.concatenate(dd))), 4),
                          "lo_two_stage": round(float(lo), 4), "hi_two_stage": round(float(hi), 4),
                          "sites_positive": sum(v > 0 for v in per_site), "sites_negative": sum(v < 0 for v in per_site),
                          "per_site": " ".join(f"{v:+.2f}" for v in per_site)})
    write(os.path.join(OUT, "clustered_differences.csv"), comps)

    # (v) BICUBIC against GBM and CNN, paired block bootstrap AUC differences (same design as stage 25)
    auc_rows = []
    for inp, k in BD.INPUTS.items():
        for site in sites:
            y = cache[f"{site}|{inp}|y"].ravel()
            ids = B.block_ids(cache[f"{site}|{inp}|y"].shape, int(round(BD.BLOCK_M / k)))
            rk = {m: B.RankedScore(cache[f"{site}|{inp}|{m}"].ravel(), y) for m in ("BICUBIC", "GBM", "CNN")}
            bs = {m: [] for m in rk}
            for w in B.block_bootstrap_weights(ids, 1000, BD.SEED):
                for m in rk:
                    bs[m].append(rk[m].auc(w))
            for ref in ("GBM", "CNN"):
                d = np.array(bs["BICUBIC"]) - np.array(bs[ref])
                lo, hi = np.nanpercentile(d, [2.5, 97.5])
                auc_rows.append({"input": inp, "site": site, "reference": ref, "auc_difference": round(rk["BICUBIC"].auc() - rk[ref].auc(), 4),
                                 "lo": round(float(lo), 4), "hi": round(float(hi), 4), "significant": bool(lo > 0 or hi < 0)})
    write(os.path.join(OUT, "auc_bicubic.csv"), auc_rows)
    say(f"done {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
