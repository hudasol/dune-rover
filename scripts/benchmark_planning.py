#!/usr/bin/env python3
"""Stage 26 (docs/PREDICTIONS.md): the shipped planner (dunerover.planner) with its own policies and swapped hazard
layers, scored on dune scale face patches in the one metre lidar of six dune fields.

    PYTHONPATH=src python3 scripts/benchmark_planning.py          # after scripts/benchmark_detection.py

Inputs: data/raw/lidar/ and the stage 25 score cache data/cache/benchmark_scores.npz.
Outputs: results/benchmark/planning/ (routes.csv, summary.csv, tests.csv, endpoints.csv, summary.json, run_log.txt) and
data/cache/benchmark_routes.npz (route geometry for the figures).
SIMULATED BY ME (maps, routes, outcomes) on PUBLISHED elevation data. Deterministic.
"""
from __future__ import annotations
import csv, json, os, sys, time
import numpy as np
from scipy.stats import binomtest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dunerover import benchmark as B, planner as PL  # noqa: E402
import benchmark_detection as BD  # noqa: E402

OUT = os.path.join(ROOT, "results", "benchmark", "planning")
ROUTE_CACHE = os.path.join(ROOT, "data", "cache", "benchmark_routes.npz")
SEED = 20261027
N_PAIRS, MIN_SEP_M, EDGE_CELLS = 100, 1000.0, 3
FLAT_DEG, FLAT_DEG_RELAXED, MIN_CANDIDATES = 20.0, 25.0, 200
N_BOOT = 2000
HAZARDS = ("DET", "DET-cal", "SLOPE-cal", "BICUBIC-cal", "GBM", "CNN", "ORACLE")
CAUTIOUS = ("conservative", "risk_weighted")
PROFILES = ("assumed", "published-posterior")       # the second is exploratory (no prediction)


def endpoints(s1, void, shape30, rng):
    """Truth only: centres of 30 m cells away from the edge whose posts are all valid and gentle, pairs >= 1000 m apart."""
    smax = B.block(s1, 30, "max")[:shape30[0], :shape30[1]]
    vany = B.block(void, 30, "any")[:shape30[0], :shape30[1]]
    inner = np.zeros(shape30, bool)
    inner[EDGE_CELLS:-EDGE_CELLS, EDGE_CELLS:-EDGE_CELLS] = True
    thr = FLAT_DEG
    cand = np.argwhere(inner & ~vany & (smax < thr))
    if len(cand) < MIN_CANDIDATES:
        thr = FLAT_DEG_RELAXED
        cand = np.argwhere(inner & ~vany & (smax < thr))
    pairs, tries = [], 0
    while len(pairs) < N_PAIRS and tries < 200000 and len(cand) > 1:
        tries += 1
        a, b = cand[rng.integers(len(cand))], cand[rng.integers(len(cand))]
        if np.hypot(*(a - b)) * 30.0 >= MIN_SEP_M:
            pairs.append(((a + 0.5) * 30.0, (b + 0.5) * 30.0))      # metres (row, col) from the north west corner
    return pairs, thr, len(cand)


def cell_of(pt_m, k, shape):
    r, c = int(pt_m[0] // k), int(pt_m[1] // k)
    return min(r, shape[0] - 1), min(c, shape[1] - 1)


def boot_ci(values_by_site, n_boot, seed, stat=np.mean):
    """Bootstrap of pairs within sites: values_by_site is a list of arrays (one per site), pooled statistic."""
    rng = np.random.default_rng(seed)
    allv = np.concatenate(values_by_site) if values_by_site else np.array([])
    if allv.size == 0:
        return float("nan"), float("nan"), float("nan")
    out = []
    for _ in range(n_boot):
        out.append(stat(np.concatenate([v[rng.integers(0, len(v), len(v))] for v in values_by_site if len(v)])))
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(stat(allv)), float(lo), float(hi)


def mcnemar(a: np.ndarray, b: np.ndarray):
    """Exact McNemar on paired booleans; returns (a only, b only, p)."""
    n01 = int((a & ~b).sum()); n10 = int((~a & b).sum())
    p = binomtest(n01, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0
    return n01, n10, float(p)


def holm(ps):
    order = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0.0
    for i, j in enumerate(order):
        run = max(run, min(1.0, (m - i) * ps[j])); adj[j] = run
    return adj


def main():
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(OUT, "run_log.txt"), "w")

    def say(m):
        print(m, flush=True); log.write(m + "\n"); log.flush()
    cache = np.load(BD.CACHE)
    say(f"stage 26 run started {time.strftime('%Y-%m-%d %H:%M:%S')}; numpy {np.__version__}; seed {SEED}; {N_PAIRS} pairs per site")
    rows, ends, geo = [], [], {}
    rng = np.random.default_rng(SEED)
    for site, (fname, win, _tile) in BD.SITES.items():
        t0 = time.time()
        z1, _, _, _ = BD.load_lidar_window(fname, win)
        void = np.isnan(z1)
        z1f = B.fill_nearest(z1)
        steep, s1 = B.steep_posts(z1, void)
        patch = B.face_patches(steep)
        shape30 = cache[f"{site}|I30|y"].shape
        pairs, thr, ncand = endpoints(s1, void, shape30, rng)
        say(f"{site}: {len(pairs)} pairs from {ncand} candidate cells (gentle below {thr:g} deg); face patch posts {patch.mean():.4f}")
        for n, (a, b) in enumerate(pairs):
            ends.append({"site": site, "pair": n, "start_row_m": a[0], "start_col_m": a[1], "goal_row_m": b[0], "goal_col_m": b[1],
                         "straight_m": round(float(np.hypot(*(a - b))), 1), "gentle_threshold_deg": thr})
        surfaces = {"I10": (B.block(z1f, 10), 10), "I30": (B.block(z1f, 30), 30),
                    "G30": (cache[f"{site}|G30|z"].astype(float), 30), "I5": (B.block(z1f, 5), 5)}
        for prof_name in PROFILES:
            prof = PL.builtin_profile(prof_name)
            crit = prof.critical_uphill_deg()

            def run(inp, k, policy, hazard, a):
                g = PL.policy_graph(a, policy)
                nr, nc = a.classes.shape
                S = [cell_of(p[0], k, (nr, nc)) for p in pairs]; T = [cell_of(p[1], k, (nr, nc)) for p in pairs]
                rcs = B.routes_from(g, nc, S, T)
                for n, (rc, (pa, pb)) in enumerate(zip(rcs, pairs)):
                    row = {"site": site, "profile": prof_name, "input": inp, "policy": policy, "hazard": hazard, "pair": n,
                           "straight_m": round(float(np.hypot(*(pa - pb))), 1), "routed": rc is not None}
                    if rc is not None:
                        row.update(B.score_route(rc, k, patch, z1f, crit))
                        row["length_ratio"] = round(row["length_m"] / row["straight_m"], 3)
                        if prof_name == "assumed" and n < 8:
                            geo[f"{site}|{inp}|{policy}|{hazard}|{n}"] = rc.astype(np.int32)
                    rows.append(row)

            for inp in ("I10", "I30", "G30"):
                zc, k = surfaces[inp]
                a = PL.assess(PL.raster_from_array(zc, float(k)), profile=prof, n_draws=128)
                assert a.classes.shape == cache[f"{site}|{inp}|y"].shape, (site, inp, a.classes.shape)
                run(inp, k, "naive", "none", a)
                for hz in HAZARDS:
                    key = f"{site}|{inp}|{'y' if hz == 'ORACLE' else hz}"
                    if key not in cache:
                        continue
                    h = cache[key].astype(float)
                    ah = B.with_hazard(a, h)
                    for pol in CAUTIOUS:
                        run(inp, k, pol, hz, ah)
                if prof_name == "assumed":
                    nr, nc = a.classes.shape
                    for n, (pa, pb) in enumerate(pairs):
                        rc = B.grid_shortest((nr, nc), cell_of(pa, k, (nr, nc)), cell_of(pb, k, (nr, nc)))
                        row = {"site": site, "profile": prof_name, "input": inp, "policy": "shortest", "hazard": "none", "pair": n,
                               "straight_m": round(float(np.hypot(*(pa - pb))), 1), "routed": True}
                        row.update(B.score_route(rc, k, patch, z1f, crit)); row["length_ratio"] = round(row["length_m"] / row["straight_m"], 3)
                        rows.append(row)
            zc, k = surfaces["I5"]
            a5 = PL.assess(PL.raster_from_array(zc, 5.0), profile=prof, n_draws=128)
            h5 = B.block(patch, 5, "any")[:a5.classes.shape[0], :a5.classes.shape[1]].astype(float)
            run("I5", 5, "conservative", "ORACLE-5", B.with_hazard(a5, h5))
        say(f"{site}: done in {time.time() - t0:.0f} s")

    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(os.path.join(OUT, "routes.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    with open(os.path.join(OUT, "endpoints.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ends[0])); w.writeheader(); w.writerows(ends)
    np.savez_compressed(ROUTE_CACHE, **geo)

    # pooled summaries with intervals (bootstrap of pairs within sites)
    sites = list(BD.SITES)
    combos = sorted({(r["profile"], r["input"], r["policy"], r["hazard"]) for r in rows})
    summ = []
    for (pf, inp, pol, hz) in combos:
        rr = [r for r in rows if (r["profile"], r["input"], r["policy"], r["hazard"]) == (pf, inp, pol, hz)]
        by = lambda f: [np.array([f(r) for r in rr if r["site"] == s], float) for s in sites]
        routed = by(lambda r: r["routed"])
        success = by(lambda r: r["routed"] and not r["unsafe"])
        unsafe_r = [np.array([r["unsafe"] for r in rr if r["site"] == s and r["routed"]], float) for s in sites]
        up_r = [np.array([r["uphill_events"] > 0 for r in rr if r["site"] == s and r["routed"]], float) for s in sites]
        lr = [np.array([r["length_ratio"] for r in rr if r["site"] == s and r["routed"]], float) for s in sites]
        km = sum(r["length_m"] for r in rr if r["routed"]) / 1000.0
        ent = sum(r["patch_entries"] for r in rr if r["routed"])
        out = {"profile": pf, "input": inp, "policy": pol, "hazard": hz, "pairs": len(rr)}
        for name, vals in (("routed", routed), ("mission_success", success), ("unsafe_of_routed", unsafe_r),
                           ("uphill_of_routed", up_r), ("length_ratio", lr)):
            m, lo, hi = boot_ci(vals, N_BOOT, SEED)
            out.update({name: round(m, 4), name + "_lo": round(lo, 4), name + "_hi": round(hi, 4)})
        out["patch_entries_per_km"] = round(ent / km, 3) if km else ""
        for s, u in zip(sites, unsafe_r):
            out[f"unsafe_{s}"] = round(float(u.mean()), 3) if len(u) else ""
        summ.append(out)
    keys = []
    for r in summ:
        keys += [k for k in r if k not in keys]
    with open(os.path.join(OUT, "summary.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(summ)

    # paired McNemar tests on mission success, Holm within each profile and input
    tests = []
    def vec(pf, inp, pol, hz):
        d = {(r["site"], r["pair"]): (r["routed"] and not r["unsafe"]) for r in rows
             if (r["profile"], r["input"], r["policy"], r["hazard"]) == (pf, inp, pol, hz)}
        return d
    for pf in PROFILES:
        for inp in ("I10", "I30", "G30"):
            block_tests = []
            base_naive = vec(pf, inp, "naive", "none")
            for pol in CAUTIOUS:
                base_det = vec(pf, inp, pol, "DET")
                for hz in HAZARDS:
                    cur = vec(pf, inp, pol, hz)
                    if not cur:
                        continue
                    for ref_name, ref in (("naive", base_naive), (f"{pol} DET", base_det)):
                        if ref is cur or (ref_name.endswith("DET") and hz == "DET"):
                            continue
                        keys_ = sorted(set(cur) & set(ref))
                        a_ = np.array([cur[k_] for k_ in keys_]); b_ = np.array([ref[k_] for k_ in keys_])
                        n01, n10, p = mcnemar(a_, b_)
                        block_tests.append({"profile": pf, "input": inp, "policy": pol, "hazard": hz, "reference": ref_name,
                                            "pairs": len(keys_), "success_method": round(float(a_.mean()), 4), "success_reference": round(float(b_.mean()), 4),
                                            "difference": round(float(a_.mean() - b_.mean()), 4), "method_only": n01, "reference_only": n10, "p": p})
            if block_tests:
                adj = holm(np.array([t["p"] for t in block_tests]))
                for t, q in zip(block_tests, adj):
                    t["p_holm"] = round(float(q), 5); t["p"] = round(t["p"], 5); t["significant_holm"] = bool(q < 0.05)
                tests += block_tests
    with open(os.path.join(OUT, "tests.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tests[0])); w.writeheader(); w.writerows(tests)
    json.dump({"label": "SIMULATED BY ME (maps, routes, outcomes) on PUBLISHED elevation data (USGS 3DEP lidar; Copernicus GLO-30)",
               "stage": 26, "seed": SEED, "pairs_per_site": N_PAIRS, "min_separation_m": MIN_SEP_M, "n_boot": N_BOOT,
               "hazards": HAZARDS, "policies": ["naive", *CAUTIOUS, "shortest"], "profiles": PROFILES,
               "critical_uphill_deg": {p: round(PL.builtin_profile(p).critical_uphill_deg(), 2) for p in PROFILES},
               "finished": time.strftime("%Y-%m-%d %H:%M:%S")}, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
    say(f"done {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
