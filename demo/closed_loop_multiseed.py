#!/usr/bin/env python3
"""POST HOC (final review of 2026-10-21, docs/REVIEW_2026-10-21.md): the closed loop comparison of
demo/closed_loop_posthoc.py repeated over several independent slip fields, naive policy, 30 m and 10 m maps, with
paired differences (replan minus retry, replan minus open loop) and seeded bootstrap 95 % intervals over pairs and
seeds. Everything else is as in demo/closed_loop_posthoc.py. SIMULATED BY ME on PUBLISHED lidar; the true rover is a
model. Output: results/closed_loop/posthoc_multiseed/.

    PYTHONPATH=src python3 demo/closed_loop_multiseed.py [--seeds 5]
"""
from __future__ import annotations
import argparse, csv, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import closed_loop as CL  # noqa: E402
import closed_loop_posthoc as PH  # noqa: E402
from closed_loop import PL, TV, SG, TC, horn_gradient, apply_range_set, nominal_params  # noqa: E402

OUT = os.path.join(CL.OUT, "posthoc_multiseed")
MODES = ("open", "retry", "replan")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--seeds", type=int, default=5); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    apply_range_set("original"); nominal = nominal_params()
    log = open(os.path.join(OUT, "run_log.txt"), "w")
    def say(m):
        print(m, flush=True); log.write(m + "\n"); log.flush()
    say(f"POST HOC multi seed closed loop {time.strftime('%Y-%m-%d %H:%M:%S')}; seeds {a.seeds}; naive policy; 30 and 10 m")
    draws = TC.lhs_draws(256, TV.SEED)
    models = {k: SG.fit(float(k), "base", 1.0) for k in (10, 30)}
    runs = []
    for site in CL.SITES:
        fname, win, _ = TV.SITES[site]
        z1, _ = TV.load_window(fname, win); z1 = np.where(np.isnan(z1), np.nanmean(z1), z1)
        maps = {k: PL.build_map(z1, k, draws, models[k]) for k in (30, 10)}
        dem30, _, cls30, _ = maps[30]
        sl30 = np.degrees(np.arctan(np.hypot(*horn_gradient(dem30.z, 30.0, 30.0))))
        cand = np.argwhere((cls30 == 0) & (sl30 < 5.0))
        cand = cand[(cand[:, 0] > 2) & (cand[:, 0] < cls30.shape[0] - 3) & (cand[:, 1] > 2) & (cand[:, 1] < cls30.shape[1] - 3)]
        rng = np.random.default_rng(PL.SEED_OD); pairs = []; tries = 0
        while len(pairs) < PL.N_PAIRS and tries < 50000:
            tries += 1
            p1, p2 = cand[rng.integers(len(cand))], cand[rng.integers(len(cand))]
            if np.hypot(*(p1 - p2)) * 30 >= PL.MIN_SEP:
                pairs.append((p1, p2))
        for k, (dem, eg, cls, pf) in maps.items():
            g0 = PL.policy_graph(eg, cls, pf, "naive", nominal)
            for s in range(a.seeds):
                for n, (p1, p2) in enumerate(pairs):
                    field = np.random.default_rng(CL.SEED + 5000 + 100 * s + n).normal(0.0, CL.SCATTER, z1.shape).astype(np.float32)
                    sa = tuple(int(x) for x in ((p1 + 0.5) * 30 / k).astype(int)); sb = tuple(int(x) for x in ((p2 + 0.5) * 30 / k).astype(int))
                    for mode in MODES:
                        r, _, _ = PH.run_pair(g0, dem.shape[1], k, sa, sb, z1, field, CL.SEED + 7000 + 100 * s + n, mode)
                        runs.append({"site": site, "posting_m": k, "seed": s, "pair": n, "mode": mode, "entrapped": int(r["outcome"] == "entrapped"),
                                     "routed": int(r["outcome"] != "not routed")})
                say(f"{site} {k} m seed {s}: " + ", ".join(f"{m} {sum(x['entrapped'] for x in runs if x['site'] == site and x['posting_m'] == k and x['seed'] == s and x['mode'] == m)}" for m in MODES))
    with open(os.path.join(OUT, "runs.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(runs[0])); w.writeheader(); w.writerows(runs)
    summ = []
    brng = np.random.default_rng(20261021)
    for site in CL.SITES:
        for k in (30, 10):
            sub = {m: np.array([[x["entrapped"] for x in runs if x["site"] == site and x["posting_m"] == k and x["seed"] == s and x["mode"] == m]
                                for s in range(a.seeds)], dtype=float) for m in MODES}   # seeds x pairs
            row = {"site": site, "posting_m": k, "seeds": a.seeds, "pairs": sub["open"].shape[1]}
            for m in MODES:
                row[f"entrapped_share_{m}"] = round(float(sub[m].mean()), 4)
            for name, x, y in (("replan_minus_retry", "replan", "retry"), ("replan_minus_open", "replan", "open")):
                d = sub[x] - sub[y]
                boots = [d[brng.integers(0, d.shape[0], d.shape[0])][:, brng.integers(0, d.shape[1], d.shape[1])].mean() for _ in range(2000)]
                row[name] = round(float(d.mean()), 4)
                row[name + "_ci95"] = f"{np.percentile(boots, 2.5):.4f} to {np.percentile(boots, 97.5):.4f}"
            summ.append(row); say(str(row))
    with open(os.path.join(OUT, "summary.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summ[0])); w.writeheader(); w.writerows(summ)
    say(f"done {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
