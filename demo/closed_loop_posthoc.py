#!/usr/bin/env python3
"""POST HOC variant of stage 23, written after the midpoint review of 2026-10-21 (docs/REVIEW_2026-10-21.md, items 1
and 2). The registered run (demo/closed_loop.py, results/closed_loop/) is unchanged. The review found that in the
registered loop most of the gain came from restarting: the slip scatter was redrawn on every attempt, the rover was put
back at a cell centre, the entrapment counter was reset, and many triggers blocked no cell. This variant removes those
effects and adds a control:

  * the true slip scatter is a field fixed in space (one N(0, 0.05) value per one metre post, drawn once per pair), so a
    second attempt over the same ground meets the same slip;
  * the rover stays where it is when it stops: the new route starts at its real position;
  * the entrapment counter carries over between attempts;
  * a replan always blocks at least the next cell of the route (and every cell on the next 15 m);
  * modes: "open" (no reaction), "retry" (stop on the trigger and plan again from the real position without blocking
    anything: the control), "replan" (stop, block, plan again);
  * estimator sensitivity: the slip estimate is also computed with odometry noise of 2 % per metre (ASSUMPTION, for
    wheel radius change and sinkage), beside the exact odometry of the registered design.
Everything else (maps, pairs, true slip law, thresholds, position noise) is as in demo/closed_loop.py.
SIMULATED BY ME on PUBLISHED USGS 3DEP lidar. Output: results/closed_loop/posthoc_fixed_field/.

    PYTHONPATH=src python3 demo/closed_loop_posthoc.py
"""
from __future__ import annotations
import csv, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import closed_loop as CL  # noqa: E402
from closed_loop import PL, TV, SG, TC, horn_gradient, slip, apply_range_set, nominal_params  # noqa: E402

OUT = os.path.join(CL.OUT, "posthoc_fixed_field")
ODO_NOISE = 0.02


def path_points(start_xy, rc, k):
    """One metre points from the rover's real position through the centres of the route cells after the first."""
    centres = (rc + 0.5) * k
    pts = [np.asarray(start_xy, float)] + [c for c in centres[1:]]
    if len(pts) == 1:
        return np.array(pts), np.array([0])
    out, cell = [pts[0]], [0]
    for i, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
        n = max(int(np.ceil(np.hypot(*(b - a)))), 1)
        out += [a + (b - a) * j / n for j in range(1, n + 1)]; cell += [i + 1] * n
    return np.array(out), np.array(cell)


def slip_along(sp, z1, field):
    ri = np.clip(np.round(sp[:, 0]).astype(int), 0, z1.shape[0] - 1); ci = np.clip(np.round(sp[:, 1]).astype(int), 0, z1.shape[1] - 1)
    z = z1[ri, ci]
    s_along = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(sp[:, 0]), np.diff(sp[:, 1])))])
    grade = np.zeros(len(z)); j = 0
    for i in range(len(z)):
        while j < len(z) - 1 and s_along[j] - s_along[i] < CL.BASELINE:
            j += 1
        if s_along[j] > s_along[i]:
            grade[i] = (z[j] - z[i]) / (s_along[j] - s_along[i])
    s = np.minimum(slip(np.clip(grade, -CL.TRUE.f_r, None), 0.0, CL.TRUE), 1.0)
    return np.clip(s + field[ri, ci], 0.0, 1.0)


def run_pair(g0, nc, k, sa, sb, z1, field, seed, mode):
    rng = np.random.default_rng(seed)
    g = g0.copy(); cur_xy = (np.array(sa) + 0.5) * k; total, replans, stuck_run = 0.0, 0, 0
    est, est_noisy, blocked_total = [], [], 0
    while True:
        cur_cell = tuple(int(x) for x in np.clip(cur_xy // k, 0, None))
        rc = PL.route(g, nc, cur_cell, sb)
        if rc is None:
            return {"outcome": "stopped (no route)" if replans else "not routed", "metres": total, "replans": replans, "cells_blocked": blocked_total}, est, est_noisy
        sp, cell = path_points(cur_xy, rc, k)
        s_true = slip_along(sp, z1, field)
        odo, odo_n, fixes, trig = [], [], [], None
        for i in range(len(sp) - 1):
            stuck_run = stuck_run + 1 if s_true[i] >= CL.STUCK_SLIP else 0
            if stuck_run >= CL.STUCK_RUN:
                return {"outcome": "entrapped", "metres": total + i, "replans": replans, "cells_blocked": blocked_total}, est, est_noisy
            o = 1.0 / max(1.0 - s_true[i], 1e-3)
            odo.append(o); odo_n.append(o * (1.0 + rng.normal(0.0, ODO_NOISE)))
            fixes.append(sp[i + 1] + rng.normal(0.0, CL.GNSS_SD, 2))
            if len(fixes) > CL.WINDOW:
                d = float(np.hypot(*(fixes[-1] - fixes[-1 - CL.WINDOW])))
                ow, own = float(np.sum(odo[-CL.WINDOW:])), float(np.sum(odo_n[-CL.WINDOW:]))
                s_hat, s_win = 1.0 - d / ow, 1.0 - CL.WINDOW / ow
                est.append(s_hat - s_win); est_noisy.append((1.0 - d / own) - s_win)
                if mode != "open" and replans < CL.MAX_REPLANS and s_hat >= CL.TRIGGER:
                    trig = i + 1; break
        if trig is None:
            return {"outcome": "arrived", "metres": total + len(sp) - 1, "replans": replans, "cells_blocked": blocked_total}, est, est_noisy
        total += trig; replans += 1; cur_xy = sp[trig]
        if mode == "replan":
            here = tuple(int(x) for x in cur_xy // k)
            ahead = {tuple(rc[c]) for c in cell[trig:min(trig + int(CL.LOOKAHEAD), len(cell))]}
            nxt = [tuple(r) for r in rc if tuple(r) != here]
            ahead |= set(nxt[:1])   # always at least the next cell of the route
            ahead.discard(here); ahead.discard(tuple(sb))
            g = g.tolil()
            for r_, c_ in ahead:
                g[:, int(r_ * nc + c_)] = 0
            g = g.tocsr(); g.eliminate_zeros(); blocked_total += len(ahead)


def main():
    os.makedirs(OUT, exist_ok=True)
    apply_range_set("original"); nominal = nominal_params()
    log = open(os.path.join(OUT, "run_log.txt"), "w")
    def say(m):
        print(m, flush=True); log.write(m + "\n"); log.flush()
    say(f"stage 23 POST HOC variant {time.strftime('%Y-%m-%d %H:%M:%S')}: fixed slip field, real position, counter carried over, at least one cell blocked; odometry noise {ODO_NOISE}")
    draws = TC.lhs_draws(256, TV.SEED)
    models = {k: SG.fit(float(k), "base", 1.0) for k in (10, 30)}
    runs, err = [], {}
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
            a, b = cand[rng.integers(len(cand))], cand[rng.integers(len(cand))]
            if np.hypot(*(a - b)) * 30 >= PL.MIN_SEP:
                pairs.append((a, b))
        for k, (dem, eg, cls, pf) in maps.items():
            nc = dem.shape[1]
            for pol in ("naive", "conservative"):
                g0 = PL.policy_graph(eg, cls, pf, pol, nominal)
                for n, (a, b) in enumerate(pairs):
                    field = np.random.default_rng(CL.SEED + 1000 + n).normal(0.0, CL.SCATTER, z1.shape).astype(np.float32)
                    sa = tuple(int(x) for x in ((a + 0.5) * 30 / k).astype(int)); sb = tuple(int(x) for x in ((b + 0.5) * 30 / k).astype(int))
                    for mode in ("open", "retry", "replan"):
                        r, e, en = run_pair(g0, nc, k, sa, sb, z1, field, CL.SEED + n, mode)
                        runs.append({"site": site, "posting_m": k, "policy": pol, "pair": n, "mode": mode, **r})
                        err.setdefault(site, ([], []))[0].extend(e); err[site][1].extend(en)
                for mode in ("open", "retry", "replan"):
                    rr = [r for r in runs if r["site"] == site and r["posting_m"] == k and r["policy"] == pol and r["mode"] == mode]
                    say(f"{site} {k} m {pol} {mode}: " + ", ".join(f"{o} {sum(r['outcome'] == o for r in rr)}" for o in sorted({r['outcome'] for r in rr})))
    summ = []
    for site in CL.SITES:
        for k in (30, 10):
            for pol in ("naive", "conservative"):
                for mode in ("open", "retry", "replan"):
                    rr = [r for r in runs if r["site"] == site and r["posting_m"] == k and r["policy"] == pol and r["mode"] == mode]
                    st = [r for r in rr if r["outcome"] != "not routed"]
                    summ.append({"site": site, "posting_m": k, "policy": pol, "mode": mode, "routed": len(st),
                                 "entrapped_share": round(float(np.mean([r["outcome"] == "entrapped" for r in st])), 3) if st else "",
                                 "arrived_share": round(float(np.mean([r["outcome"] == "arrived" for r in st])), 3) if st else "",
                                 "stopped_share": round(float(np.mean([r["outcome"].startswith("stopped") for r in st])), 3) if st else "",
                                 "mean_replans": round(float(np.mean([r["replans"] for r in st])), 2) if st else "",
                                 "mean_cells_blocked": round(float(np.mean([r["cells_blocked"] for r in st])), 2) if st else ""})
    for fn, rows in (("runs.csv", runs), ("summary.csv", summ)):
        with open(os.path.join(OUT, fn), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(dict.fromkeys(x for r in rows for x in r))); w.writeheader(); w.writerows(rows)
    est = [{"site": s, "median_abs_error_exact_odometry": round(float(np.median(np.abs(e))), 4), "median_abs_error_odometry_noise_2pct": round(float(np.median(np.abs(en))), 4),
            "p90_abs_error_odometry_noise_2pct": round(float(np.percentile(np.abs(en), 90)), 4),
            "analytic_median_low_slip": round(0.6745 * CL.GNSS_SD * np.sqrt(2) / CL.WINDOW, 4)} for s, (e, en) in err.items()]
    with open(os.path.join(OUT, "estimator.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(est[0])); w.writeheader(); w.writerows(est)
    say("estimator: " + json.dumps(est)); say(f"done {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
