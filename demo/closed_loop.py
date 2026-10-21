#!/usr/bin/env python3
"""Stage 23 (docs/PREDICTIONS.md): a closed loop demonstration. A simulated rover follows routes planned on the 30 m
and 10 m three class maps of stage 17, drives over the one metre lidar surface, estimates its own slip online from
wheel odometry against noisy position fixes, and replans around ground where the estimate shows high slip.

    PYTHONPATH=src python3 demo/closed_loop.py

SIMULATED BY ME on PUBLISHED USGS 3DEP lidar. Nothing here is a field result; the "true" rover is itself a model:
  * true slip: the exponential slip model of src/dunerover/slipmodel.py with the stage 15 posterior medians
    (phi 36.93 deg, f_r 0.129, i0 0.627; results/model_validation/.../posterior_exp.json), evaluated on the uphill
    grade of the lidar surface over a 3 m baseline along the direction of travel (grades steeper downhill than minus
    f_r are set to minus f_r, where the traction demand is zero, ASSUMPTION; docstring corrected 2026-10-21 after the review,
    code unchanged), plus a run to run scatter N(0, 0.05) per metre (ASSUMPTION), clipped to 0 to 1;
  * entrapment: true slip of 0.95 or more on 3 consecutive metres;
  * position fixes every true metre with independent Gaussian noise of 0.3 m per axis (ASSUMPTION, a non RTK receiver);
  * slip estimate: 1 minus the fix to fix distance over the last 10 m of travel divided by the odometry distance over
    the same window (odometry assumed exact; wheel radius known);
  * replanning (closed loop only): when the estimate reaches 0.5, the map cells on the next 15 m of the planned route are
    removed from the graph and a new route is planned from the current cell (at most 10 replans); with no route the
    rover stops (counted as "stopped", not as entrapment).
Open loop = the same route driven without replanning. Same origin destination pairs, maps and policies as stage 17.
Outputs: results/closed_loop/summary.csv, runs.csv, estimator.csv, run_log.txt, figures/.
"""
from __future__ import annotations
import csv, json, os, sys, time
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dunerover.terrain import horn_gradient  # noqa: E402
from dunerover.slipmodel import SlipParams, slip, apply_range_set, nominal_params  # noqa: E402
from dunerover import subgrid as SG, threeclass as TC  # noqa: E402
import terrain_validation_lidar as TV  # noqa: E402
import planner_lidar as PL  # noqa: E402

OUT = os.path.join(ROOT, "results", "closed_loop")
SITES = ("WhiteSands", "Kelso")
TRUE = SlipParams(phi_deg=36.93, f_r=0.129, i0=0.627)
SEED = 20261023
SCATTER, GNSS_SD, WINDOW, TRIGGER, LOOKAHEAD, MAX_REPLANS = 0.05, 0.3, 10, 0.5, 15.0, 10
STUCK_SLIP, STUCK_RUN, BASELINE = 0.95, 3, 3.0


def resample(rc, k):
    """Route cells (row, col) at posting k to one metre points on the lidar grid, with the index of the cell of each point."""
    pts = (rc + 0.5) * k
    out, cell = [pts[0]], [0]
    for i, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
        n = max(int(np.ceil(np.hypot(*(b - a)))), 1)
        out += [a + (b - a) * j / n for j in range(1, n + 1)]; cell += [i + 1] * n
    return np.array(out), np.array(cell)


def true_slip_along(sp, z1, rng):
    ri = np.clip(np.round(sp[:, 0]).astype(int), 0, z1.shape[0] - 1); ci = np.clip(np.round(sp[:, 1]).astype(int), 0, z1.shape[1] - 1)
    z = z1[ri, ci]
    s_along = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(sp[:, 0]), np.diff(sp[:, 1])))])
    grade = np.zeros(len(z))
    j = 0
    for i in range(len(z)):
        while j < len(z) - 1 and s_along[j] - s_along[i] < BASELINE:
            j += 1
        if s_along[j] > s_along[i]:
            grade[i] = (z[j] - z[i]) / (s_along[j] - s_along[i])
    tan_up = np.clip(grade, -TRUE.f_r, None)
    s = np.minimum(slip(tan_up, 0.0, TRUE), 1.0)
    return np.clip(s + rng.normal(0.0, SCATTER, len(s)), 0.0, 1.0)


def drive(sp, s_true, rng, closed, trigger_cb=None):
    """Drive the one metre points; return (outcome, metres driven, index reached, estimator samples)."""
    odo, fixes, est, run = [], [], [], 0
    for i in range(len(sp) - 1):
        st = s_true[i]
        run = run + 1 if st >= STUCK_SLIP else 0
        if run >= STUCK_RUN:
            return "entrapped", i, i, est
        odo.append(1.0 / max(1.0 - st, 1e-3))
        fixes.append(sp[i + 1] + rng.normal(0.0, GNSS_SD, 2))
        if len(fixes) > WINDOW:
            d = float(np.hypot(*(fixes[-1] - fixes[-1 - WINDOW])))
            o = float(np.sum(odo[-WINDOW:]))
            s_hat = 1.0 - d / o
            s_win = 1.0 - WINDOW / o
            est.append((i, s_hat, s_win))
            if closed and s_hat >= TRIGGER and trigger_cb is not None:
                return "trigger", i, i, est
    return "arrived", len(sp) - 1, len(sp) - 1, est


def run_pair(g0, nc, k, sa, sb, z1, rng_seed, closed):
    rng = np.random.default_rng(rng_seed)
    g = g0.copy(); cur = sa; total, replans, est_all = 0.0, 0, []
    while True:
        rc = PL.route(g, nc, cur, sb)
        if rc is None:
            return {"outcome": "stopped (no route)" if replans else "not routed", "metres": total, "replans": replans}, est_all
        sp, cell = resample(rc, k)
        s_true = true_slip_along(sp, z1, rng)
        out, metres, idx, est = drive(sp, s_true, rng, closed and replans < MAX_REPLANS, trigger_cb=True)
        est_all += est; total += metres
        if out != "trigger":
            return {"outcome": out, "metres": total, "replans": replans}, est_all
        # block the cells of the next LOOKAHEAD metres of the route and replan from the current cell
        replans += 1
        here = rc[cell[idx]]
        ahead = cell[idx:min(idx + int(LOOKAHEAD), len(cell))]
        blocked = {int(rc[c][0] * nc + rc[c][1]) for c in ahead if tuple(rc[c]) != tuple(here)}
        g = g.tolil()
        for b in blocked:
            g[:, b] = 0
        g = g.tocsr(); g.eliminate_zeros()
        cur = (int(here[0]), int(here[1]))
        if cur == tuple(sb):
            return {"outcome": "arrived", "metres": total, "replans": replans}, est_all


def main():
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    apply_range_set("original")
    nominal = nominal_params()
    log = open(os.path.join(OUT, "run_log.txt"), "w")
    def say(m):
        print(m, flush=True); log.write(m + "\n"); log.flush()
    say(f"stage 23 run {time.strftime('%Y-%m-%d %H:%M:%S')}; true rover {TRUE}; seed {SEED}")
    draws = TC.lhs_draws(256, TV.SEED)
    models = {k: SG.fit(float(k), "base", 1.0) for k in (10, 30)}
    runs, ests = [], []
    for site in SITES:
        fname, win, desc = TV.SITES[site]
        z1, _ = TV.load_window(fname, win)
        z1 = np.where(np.isnan(z1), np.nanmean(z1), z1)
        maps = {k: PL.build_map(z1, k, draws, models[k]) for k in (30, 10)}
        dem30, _, cls30, _ = maps[30]
        sl30 = np.degrees(np.arctan(np.hypot(*horn_gradient(dem30.z, 30.0, 30.0))))
        cand = np.argwhere((cls30 == 0) & (sl30 < 5.0))
        cand = cand[(cand[:, 0] > 2) & (cand[:, 0] < cls30.shape[0] - 3) & (cand[:, 1] > 2) & (cand[:, 1] < cls30.shape[1] - 3)]
        rng = np.random.default_rng(PL.SEED_OD); pairs = []; tries = 0
        while len(pairs) < PL.N_PAIRS and tries < 50000:   # the stage 17 pairs
            tries += 1
            a, b = cand[rng.integers(len(cand))], cand[rng.integers(len(cand))]
            if np.hypot(*(a - b)) * 30 >= PL.MIN_SEP:
                pairs.append((a, b))
        for k, (dem, eg, cls, pf) in maps.items():
            nc = dem.shape[1]
            for pol in ("naive", "conservative"):
                g0 = PL.policy_graph(eg, cls, pf, pol, nominal)
                for n, (a, b) in enumerate(pairs):
                    sa = tuple(int(x) for x in ((a + 0.5) * 30 / k).astype(int)); sb = tuple(int(x) for x in ((b + 0.5) * 30 / k).astype(int))
                    for mode in ("open", "closed"):
                        r, est = run_pair(g0, nc, k, sa, sb, z1, SEED + n, mode == "closed")
                        runs.append({"site": site, "posting_m": k, "policy": pol, "pair": n, "mode": mode, **r})
                        ests += [{"site": site, "posting_m": k, "policy": pol, "pair": n, "mode": mode, "step": e[0], "s_hat": e[1], "s_window_true": e[2]} for e in est]
                for mode in ("open", "closed"):
                    rr = [r for r in runs if r["site"] == site and r["posting_m"] == k and r["policy"] == pol and r["mode"] == mode]
                    say(f"{site} {k} m {pol} {mode}: " + ", ".join(f"{o} {sum(r['outcome'] == o for r in rr)}" for o in sorted({r['outcome'] for r in rr})))
    summ = []
    for site in SITES:
        for k in (30, 10):
            for pol in ("naive", "conservative"):
                for mode in ("open", "closed"):
                    rr = [r for r in runs if r["site"] == site and r["posting_m"] == k and r["policy"] == pol and r["mode"] == mode]
                    started = [r for r in rr if r["outcome"] != "not routed"]
                    arr = [r for r in started if r["outcome"] == "arrived"]
                    summ.append({"site": site, "posting_m": k, "policy": pol, "mode": mode, "pairs": len(rr), "routed": len(started),
                                 "entrapped_share": round(np.mean([r["outcome"] == "entrapped" for r in started]), 3) if started else "",
                                 "arrived_share": round(len(arr) / len(started), 3) if started else "",
                                 "stopped_share": round(np.mean([r["outcome"].startswith("stopped") for r in started]), 3) if started else "",
                                 "mean_metres_arrived": round(float(np.mean([r["metres"] for r in arr])), 1) if arr else "",
                                 "mean_replans": round(float(np.mean([r["replans"] for r in started])), 2) if started else ""})
    for fn, rows in (("runs.csv", runs), ("summary.csv", summ)):
        with open(os.path.join(OUT, fn), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(dict.fromkeys(k_ for r in rows for k_ in r))); w.writeheader(); w.writerows(rows)
    est_rows = []
    for site in SITES:
        e = [x for x in ests if x["site"] == site and x["step"] >= 20]
        err = np.abs(np.array([x["s_hat"] - x["s_window_true"] for x in e]))
        est_rows.append({"site": site, "samples": len(e), "median_abs_error": round(float(np.median(err)), 4), "p90_abs_error": round(float(np.percentile(err, 90)), 4)})
    with open(os.path.join(OUT, "estimator.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(est_rows[0])); w.writeheader(); w.writerows(est_rows)
    say("estimator: " + json.dumps(est_rows))
    _figures(summ, ests)
    say(f"done {time.strftime('%Y-%m-%d %H:%M:%S')}")


def _figures(summ, ests):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), facecolor="#fffafb")
    for ax, site in zip(axes, SITES):
        ax.set_facecolor("#fffafb")
        labels, opn, cls = [], [], []
        for k in (30, 10):
            for pol in ("naive", "conservative"):
                o = [r for r in summ if r["site"] == site and r["posting_m"] == k and r["policy"] == pol and r["mode"] == "open"][0]
                c = [r for r in summ if r["site"] == site and r["posting_m"] == k and r["policy"] == pol and r["mode"] == "closed"][0]
                labels.append(f"{k} m\n{pol}"); opn.append(o["entrapped_share"] or 0); cls.append(c["entrapped_share"] or 0)
        x = np.arange(len(labels))
        ax.bar(x - 0.18, opn, 0.34, color="#c9769a", label="open loop")
        ax.bar(x + 0.18, cls, 0.34, color="#5b3a78", label="closed loop, replanning on estimated slip")
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8); ax.set_ylabel("share of routed pairs entrapped"); ax.set_title(site, fontsize=10)
        ax.legend(frameon=False, fontsize=7)
    fig.text(0.01, 0.01, "SIMULATED BY ME on PUBLISHED USGS 3DEP lidar; the true rover is a slip model, not a measured vehicle.", fontsize=7)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(os.path.join(OUT, "figures", "fig_closed_loop_entrapment.png"), dpi=140); plt.close(fig)
    e = [x for x in ests if x["step"] >= 20]
    if e:
        fig, ax = plt.subplots(figsize=(4.6, 4.2), facecolor="#fffafb"); ax.set_facecolor("#fffafb")
        tv = np.array([x["s_window_true"] for x in e]); sh = np.array([x["s_hat"] for x in e])
        idx = np.random.default_rng(1).choice(len(e), size=min(4000, len(e)), replace=False)
        ax.scatter(tv[idx], sh[idx], s=3, color="#c9769a", alpha=0.4, linewidths=0)
        ax.plot([0, 1], [0, 1], color="#5b3a78", lw=1); ax.axhline(TRIGGER, color="#7a1f45", ls=":", lw=1)
        ax.set_xlabel("true slip over the last 10 m"); ax.set_ylabel("estimated slip (odometry against fixes)")
        ax.set_title("Online slip estimate, 0.3 m position noise", fontsize=9)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, "figures", "fig_slip_estimator.png"), dpi=140); plt.close(fig)


if __name__ == "__main__":
    main()
