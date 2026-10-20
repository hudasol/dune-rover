#!/usr/bin/env python3
"""Stage 17 (docs/PREDICTIONS.md): naive, conservative and risk weighted route planning on 30 m and 10 m maps,
scored against the one metre lidar surface of the three stage 12 dune fields.

    PYTHONPATH=src python3 scripts/planner_lidar.py

SIMULATED BY ME (maps, routes, events) on PUBLISHED USGS 3DEP elevation (public domain). Deterministic.
Outputs: results/planner/routes.csv, policy_summary.csv, run_log.txt, figures/.
"""
from __future__ import annotations
import csv, os, sys, time
import numpy as np
from scipy.sparse import diags
from scipy.sparse.csgraph import dijkstra
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dunerover.dem import Dem  # noqa: E402
from dunerover.terrain import horn_gradient  # noqa: E402
from dunerover import traverse as TR, subgrid as SG, threeclass as TC  # noqa: E402
from dunerover.slipmodel import apply_range_set, nominal_params, critical_uphill_deg  # noqa: E402
import terrain_validation_lidar as TV  # noqa: E402

OUT = os.path.join(ROOT, "results", "planner")
SEED_OD, N_PAIRS, MIN_SEP = 20261024, 40, 1000.0
RISK_W = 5.0
POLICIES = ("naive", "conservative", "risk_weighted")


def build_map(z1, k, draws, model):
    zc = TV.block(z1, k)
    dem = Dem(zc, 0.0, 0.0, 1.0, 1.0, float(k), float(k))
    eg = TR.precompute_edges(dem)
    q = TC.q_pass(eg, draws)
    p = model.predict(SG.features_2d(zc, float(k), float(k)))
    return dem, eg, TC.classify(q, p), p


def policy_graph(eg, cls, pface, policy, nominal):
    g, _ = TR.build_graph(eg, nominal)
    if policy == "naive":
        return g
    if policy == "conservative":
        keep = (cls.ravel() == 0).astype(float)
        D = diags(keep); g2 = (D @ g @ D).tocsr(); g2.eliminate_zeros(); return g2
    keep = (cls.ravel() != 1).astype(float)
    D = diags(keep); g2 = (D @ g @ D).tocsr()
    g2 = g2.multiply(1.0 + RISK_W * pface.ravel()[None, :]).tocsr()   # cost scaled by the face probability of the cell entered
    g2.eliminate_zeros(); return g2


def route(g, nc, s_rc, t_rc):
    s, t = s_rc[0] * nc + s_rc[1], t_rc[0] * nc + t_rc[1]
    dist, pred = dijkstra(g, directed=True, indices=s, return_predecessors=True)
    if not np.isfinite(dist[t]):
        return None
    path = [t]
    while path[-1] != s:
        path.append(int(pred[path[-1]]))
    return np.column_stack(np.divmod(np.array(path[::-1]), nc))


def truth_events(rc, k, z1, s1, crit_deg, baseline=3.0):
    """Resample the route at 1 m on the lidar surface; count uphill events and face contacts."""
    pts = (rc + 0.5) * k                                      # cell centres in one metre post coordinates (row, col)
    samples = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(int(np.ceil(np.hypot(*(b - a)))), 1)
        samples += [a + (b - a) * j / n for j in range(1, n + 1)]
    sp = np.array(samples)
    ri = np.clip(np.round(sp[:, 0]).astype(int), 0, z1.shape[0] - 1); ci = np.clip(np.round(sp[:, 1]).astype(int), 0, z1.shape[1] - 1)
    z = z1[ri, ci]
    seg = np.hypot(np.diff(sp[:, 0]), np.diff(sp[:, 1]))
    s_along = np.concatenate([[0.0], np.cumsum(seg)])
    up = 0
    j = 0
    for i in range(len(z)):
        while j < len(z) and s_along[j] - s_along[i] < baseline:
            j += 1
        if j >= len(z):
            break
        if np.degrees(np.arctan((z[j] - z[i]) / (s_along[j] - s_along[i]))) > crit_deg:
            up += 1
    contacts = int((s1[ri, ci] >= SG.FACE_TRUTH_DEG).sum())
    return up, contacts, float(s_along[-1])


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=float, default=3.0, help="grade baseline in m; 3 is the pre registered value, others are POST HOC")
    args = ap.parse_args()
    global OUT
    if args.baseline != 3.0:
        OUT = os.path.join(OUT, f"posthoc_baseline_{args.baseline:g}m")
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    apply_range_set("original")
    nominal = nominal_params(); crit = critical_uphill_deg(nominal)
    log = open(os.path.join(OUT, "run_log.txt"), "w")
    def say(m):
        print(m, flush=True); log.write(m + "\n"); log.flush()
    say(f"stage 17 run {time.strftime('%Y-%m-%d %H:%M:%S')}; grade baseline {args.baseline} m{' (POST HOC)' if args.baseline != 3.0 else ''}; critical uphill {crit:.2f} deg; risk weight {RISK_W}; OD seed {SEED_OD}")
    draws = TC.lhs_draws(256, TV.SEED)
    models = {k: SG.fit(float(k), "base", 1.0) for k in (10, 30)}
    rows, keepfig = [], {}
    for site, (fname, win, desc) in TV.SITES.items():
        z1, _ = TV.load_window(fname, win)
        z1 = np.where(np.isnan(z1), np.nanmean(z1), z1)
        ge, gn = horn_gradient(z1, 1.0, 1.0); s1 = np.degrees(np.arctan(np.hypot(ge, gn)))
        maps = {k: build_map(z1, k, draws, models[k]) for k in (30, 10)}
        dem30, _, cls30, _ = maps[30]
        sl30 = np.degrees(np.arctan(np.hypot(*horn_gradient(dem30.z, 30.0, 30.0))))
        cand = np.argwhere((cls30 == 0) & (sl30 < 5.0))
        cand = cand[(cand[:, 0] > 2) & (cand[:, 0] < cls30.shape[0] - 3) & (cand[:, 1] > 2) & (cand[:, 1] < cls30.shape[1] - 3)]
        rng = np.random.default_rng(SEED_OD); pairs = []; tries = 0
        while len(pairs) < N_PAIRS and tries < 50000:
            tries += 1
            a, b = cand[rng.integers(len(cand))], cand[rng.integers(len(cand))]
            if np.hypot(*(a - b)) * 30 >= MIN_SEP:
                pairs.append((a, b))
        for k, (dem, eg, cls, pf) in maps.items():
            nc = dem.shape[1]
            for pol in POLICIES:
                g = policy_graph(eg, cls, pf, pol, nominal)
                for n, (a, b) in enumerate(pairs):
                    sa = tuple(((a + 0.5) * 30 / k).astype(int)); sb = tuple(((b + 0.5) * 30 / k).astype(int))
                    rc = route(g, nc, sa, sb)
                    straight = float(np.hypot(*(np.array(sa) - np.array(sb))) * k)
                    if rc is None:
                        rows.append({"site": site, "posting_m": k, "policy": pol, "pair": n, "routed": False, "straight_m": round(straight, 1)}); continue
                    up, contacts, length = truth_events(rc, k, z1, s1, crit, args.baseline)
                    unk = float(np.isin(cls[rc[:, 0], rc[:, 1]], (2, 3, 4)).mean())
                    rows.append({"site": site, "posting_m": k, "policy": pol, "pair": n, "routed": True, "straight_m": round(straight, 1),
                                 "length_m": round(length, 1), "uphill_events": up, "face_contacts": contacts, "fails_on_truth": bool(up > 0),
                                 "share_cells_unknown": round(unk, 3)})
                    if k == 30 and n < 6:
                        keepfig.setdefault((site, pol), []).append(rc)
                rr = [r for r in rows if r["site"] == site and r["posting_m"] == k and r["policy"] == pol]
                ok = [r for r in rr if r["routed"]]
                say(f"{site} {k} m {pol}: routed {len(ok)}/{len(rr)}, fail on truth {np.mean([r['fails_on_truth'] for r in ok]) if ok else float('nan'):.3f}")
            if k == 30:
                keepfig[(site, "_cls")] = cls
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(os.path.join(OUT, "routes.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    summ = []
    for site in TV.SITES:
        for k in (30, 10):
            for pol in POLICIES:
                rr = [r for r in rows if r["site"] == site and r["posting_m"] == k and r["policy"] == pol]; ok = [r for r in rr if r["routed"]]
                km = sum(r["length_m"] for r in ok) / 1000 if ok else float("nan")
                summ.append({"site": site, "posting_m": k, "policy": pol, "pairs": len(rr), "share_routed": round(len(ok) / len(rr), 3),
                             "share_routed_failing_on_truth": round(float(np.mean([r["fails_on_truth"] for r in ok])), 3) if ok else "",
                             "face_contacts_per_km": round(sum(r["face_contacts"] for r in ok) / km, 2) if ok else "",
                             "mean_length_over_straight": round(float(np.mean([r["length_m"] / r["straight_m"] for r in ok])), 3) if ok else "",
                             "mean_share_cells_unknown": round(float(np.mean([r["share_cells_unknown"] for r in ok])), 3) if ok else ""})
    with open(os.path.join(OUT, "policy_summary.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summ[0])); w.writeheader(); w.writerows(summ)
    fig, axes = plt.subplots(1, 3, figsize=(13, 5.5), facecolor="#fffafb")
    cmap = ListedColormap(["#a9cdbd", "#7a1f45", "#a98fd1", "#ee7aa8", "#5b3a78"])
    for ax, site in zip(axes, TV.SITES):
        ax.imshow(keepfig[(site, "_cls")], cmap=cmap, vmin=-0.5, vmax=4.5, interpolation="nearest")
        for pol, col in zip(POLICIES, ("#2b2024", "#6fa28f", "#e8a5bb")):
            for rc in keepfig.get((site, pol), []):
                ax.plot(rc[:, 1], rc[:, 0], color=col, lw=1.2)
        ax.set_title(f"{site}, 30 m: naive (ink), conservative (sage), risk weighted (pink)", fontsize=8); ax.set_xticks([]); ax.set_yticks([])
    fig.text(0.01, 0.01, "First six routes per policy over the 30 m three class map. SIMULATED BY ME on PUBLISHED USGS 3DEP lidar.", fontsize=8)
    fig.savefig(os.path.join(OUT, "figures", "fig_routes_30m.png"), dpi=120, bbox_inches="tight")
    say(f"done {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
