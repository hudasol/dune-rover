#!/usr/bin/env python3
"""Stage 28 (docs/PREDICTIONS.md): planning comparisons at every operating point, degraded face maps and a closed loop
with local sensing, scored on face patches in the one metre lidar of six dune fields.

    PYTHONPATH=src python3 scripts/benchmark_stage28.py A C      # after scripts/benchmark_stage27.py prepare A E
    PYTHONPATH=src python3 scripts/benchmark_stage28.py summary
    PYTHONPATH=src python3 scripts/benchmark_stage28.py E         # closed loop

A: sweeps of the face threshold (conservative) and the risk weight (risk weighted) for every hazard layer, with the
refusal breakdown (part B) and the footprint and descent scoring (part D) recorded for every route. C: degraded face maps.
E: closed loop with local sensing. summary: held out operating points, two stage bootstrap, sign flip tests.
Outputs: results/benchmark/stage28/ (summary tables, run_log.txt); full route tables in data/cache/stage28/ (git ignored).
SIMULATED BY ME (maps, routes, outcomes) on PUBLISHED elevation data and imagery. Deterministic.
"""
from __future__ import annotations
import csv, itertools, json, os, sys, time
import numpy as np
from scipy.ndimage import uniform_filter, maximum_filter
from scipy.sparse import csr_matrix, diags

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dunerover import benchmark as B, planner as PL, threeclass as TC  # noqa: E402
from dunerover.slipmodel import slip as _slip, edge_cost  # noqa: E402
from dunerover.terrain import horn_gradient  # noqa: E402
import benchmark_detection as BD  # noqa: E402
import benchmark_planning as BP  # noqa: E402

OUT = os.path.join(ROOT, "results", "benchmark", "stage28")
CDIR = os.path.join(ROOT, "data", "cache", "stage28")
L27 = os.path.join(ROOT, "data", "cache", "stage27")
SEED = 20261028
TAUS = (0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9)
WEIGHTS = (1, 2, 5, 10, 20, 50, 100)
LAYERS = ("DET", "DET-cal", "SLOPE-cal", "BICUBIC-cal", "GBM", "CNN", "DEM+S2", "FACEMAP")
COMBOS = (("published-posterior", "E1"), ("published-posterior", "E2"), ("assumed", "E1"))
SITES = list(BD.SITES)
DESCENT_CUT = -np.tan(np.radians(PL.DOWNHILL_CUT_DEG))
LOG = None


def say(m):
    print(m, flush=True)
    if LOG:
        LOG.write(m + "\n"); LOG.flush()


def write(path, rows):
    if not rows:
        return
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)


# ---------------------------------------------------------------------------------------------------------------------
# truth, endpoints, graphs, scoring
# ---------------------------------------------------------------------------------------------------------------------
def site_truth(site):
    fname, win, _ = BD.SITES[site]
    z1, _, _, _ = BD.load_lidar_window(fname, win)
    void = np.isnan(z1); z1f = B.fill_nearest(z1)
    steep, _ = B.steep_posts(z1, void)
    patch = B.face_patches(steep)
    ge, gn = horn_gradient(uniform_filter(z1f, 5, mode="nearest"), 1.0, 1.0)
    return {"z1f": z1f, "void": void, "patch": patch, "patch_fp": maximum_filter(patch, 3, mode="constant"),
            "down_r": gn.astype(np.float32), "down_c": (-ge).astype(np.float32)}


def endpoints_E1(site):
    ends = [e for e in csv.DictReader(open(os.path.join(ROOT, "results", "benchmark", "planning", "endpoints.csv"))) if e["site"] == site]
    return [(np.array([float(e["start_row_m"]), float(e["start_col_m"])]), np.array([float(e["goal_row_m"]), float(e["goal_col_m"])])) for e in ends]


def endpoints_E2(z30, rng):
    """No truth: centres of 30 m cells at least 3 cells from the edge with a coarse slope below 15 deg, pairs at least
    1000 m apart, each cell used once."""
    s = B.slope_deg(z30, 30.0)
    inner = np.zeros(z30.shape, bool); inner[3:-3, 3:-3] = True
    cand = [tuple(x) for x in np.argwhere(inner & (s < 15.0))]
    used, pairs, tries = set(), [], 0
    while len(pairs) < 100 and tries < 200000:
        tries += 1
        a, b = cand[rng.integers(len(cand))], cand[rng.integers(len(cand))]
        if a in used or b in used or a == b:
            continue
        if np.hypot(a[0] - b[0], a[1] - b[1]) * 30.0 >= 1000.0:
            used.update((a, b)); pairs.append(((np.array(a) + 0.5) * 30.0, (np.array(b) + 0.5) * 30.0))
    return pairs


def base_graph(a, descent_rule):
    """Edge costs of the nominal slip model; optionally without descents of 28 deg or more. Returns (graph, stats)."""
    p = a.profile.nominal_params()
    rows, cols, vals = [], [], []
    n_fin = n_cut = 0
    for s, d, dist, ta, tc in zip(a.eg.src, a.eg.dst, a.eg.dist, a.eg.tan_a, a.eg.tan_c):
        cost = edge_cost(dist, _slip(ta, tc, p), p.i_max)
        ok = np.isfinite(cost)
        n_fin += int(ok.sum())
        if descent_rule:
            cut = ok & ~(np.asarray(ta) > DESCENT_CUT)
            n_cut += int(cut.sum())
            ok &= np.asarray(ta) > DESCENT_CUT
        rows.append(s[ok]); cols.append(d[ok]); vals.append(cost[ok])
    n = a.classes.size
    g = csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))
    return g, {"finite_edges": n_fin, "removed_by_descent_rule": n_cut}


def masked(g, keep, face=None, w=0.0):
    k = diags(keep.ravel().astype(float))
    g2 = (k @ g @ k).tocsr()
    if w:
        g2 = g2.multiply(1.0 + w * face.ravel()[None, :]).tocsr()
    g2.eliminate_zeros()
    return g2


def samples(rc, k, step=0.5):
    pts = (np.asarray(rc, float) + 0.5) * k
    out = [pts[:1]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(int(np.ceil(np.hypot(*(b - a)) / step)), 1)
        out.append(a + (b - a) * (np.arange(1, n + 1)[:, None] / n))
    return np.concatenate(out)


def score(pts_m, T):
    """Score a polyline given as samples (metres, row and column from the north west corner) on the lidar truth."""
    sp = pts_m
    shp = T["patch"].shape
    ri = np.clip(np.floor(sp[:, 0]).astype(int), 0, shp[0] - 1); ci = np.clip(np.floor(sp[:, 1]).astype(int), 0, shp[1] - 1)
    on = T["patch"][ri, ci]; on_fp = T["patch_fp"][ri, ci]
    seg = np.hypot(np.diff(sp[:, 0]), np.diff(sp[:, 1]))
    length = float(seg.sum())
    r = {"length_m": round(length, 1), "unsafe": bool(on.any()), "unsafe_fp": bool(on_fp.any()),
         "m_on_face": round(0.5 * float(on.sum()), 1), "entries": int(on[0]) + int((on[1:] & ~on[:-1]).sum())}
    if on.any():
        d = np.diff(sp, axis=0); d = np.vstack([d[:1], d])
        nrm = np.maximum(np.hypot(d[:, 0], d[:, 1]), 1e-9)
        dr, dc = T["down_r"][ri, ci], T["down_c"][ri, ci]
        gm = np.maximum(np.hypot(dr, dc), 1e-9)
        cosang = (d[:, 0] * dr + d[:, 1] * dc) / (nrm * gm)
        oc = cosang[on]
        r["contact_descent"] = int((oc >= np.cos(np.radians(30))).sum())
        r["contact_climb"] = int((oc <= -np.cos(np.radians(30))).sum())
        r["contact_traverse"] = int(on.sum()) - r["contact_descent"] - r["contact_climb"]
    return r


def run_config(g, k, shape, pairs, T, keep=None):
    nr, nc = shape
    S = [BP.cell_of(p[0], k, shape) for p in pairs]; Tg = [BP.cell_of(p[1], k, shape) for p in pairs]
    rcs = B.routes_from(g, nc, S, Tg)
    out = []
    for n, (rc, (pa, pb), s, t) in enumerate(zip(rcs, pairs, S, Tg)):
        row = {"pair": n, "straight_m": round(float(np.hypot(*(pa - pb))), 1), "routed": rc is not None}
        if keep is not None:
            row["start_ok"] = bool(keep[s[0] * nc + s[1]]); row["goal_ok"] = bool(keep[t[0] * nc + t[1]])
        if rc is not None:
            row.update(score(samples(rc, k), T)); row["length_ratio"] = round(row["length_m"] / row["straight_m"], 3)
        out.append(row)
    return out


# ---------------------------------------------------------------------------------------------------------------------
# parts A (with B and D) and C
# ---------------------------------------------------------------------------------------------------------------------
def layers_for(site, inp):
    L = np.load(os.path.join(L27, "layers_L-ANY.npz"))
    out = {m: L[f"{site}|{inp}|{m}"].astype(float) for m in ("DET", "DET-cal", "SLOPE-cal", "BICUBIC-cal", "GBM", "CNN")}
    out["FACEMAP"] = L[f"{site}|{inp}|y"].astype(float)
    if inp in ("I10", "I30"):
        I = np.load(os.path.join(L27, f"layers_imagery_{inp}.npz"))
        out["DEM+S2"] = I[f"{site}|DEM+S2"].astype(float)
    return out


def surfaces(site, T):
    c25 = np.load(BD.CACHE)
    return {"I10": (B.block(T["z1f"], 10), 10), "I30": (B.block(T["z1f"], 30), 30), "G30": (c25[f"{site}|G30|z"].astype(float), 30)}


def part_A(sites=None):
    os.makedirs(CDIR, exist_ok=True)
    stats = []
    for site in (sites or SITES):
        rng2 = np.random.default_rng([SEED, SITES.index(site)])
        t0 = time.time()
        T = site_truth(site)
        surf = surfaces(site, T)
        E = {"E1": endpoints_E1(site), "E2": endpoints_E2(surf["I30"][0], rng2)}
        json.dump({k: [[list(map(float, a)), list(map(float, b))] for a, b in v] for k, v in E.items()},
                  open(os.path.join(CDIR, f"endpoints_{site}.json"), "w"))
        rows = []
        for prof_name in ("published-posterior", "assumed"):
            prof = PL.builtin_profile(prof_name)
            ends = [e for (pf, e) in COMBOS if pf == prof_name]
            for inp, (zc, k) in surf.items():
                a = PL.assess(PL.raster_from_array(zc, float(k)), profile=prof, n_draws=128)
                shape = a.classes.shape
                g_naive, _ = base_graph(a, False)
                g_cut, st = base_graph(a, True)
                stats.append({"site": site, "profile": prof_name, "input": inp, **st,
                              "share_removed": round(st["removed_by_descent_rule"] / max(st["finite_edges"], 1), 5)})
                hz = layers_for(site, inp)
                nodata = a.classes == 5
                for e in ends:
                    pairs = E[e]
                    base = dict(site=site, profile=prof_name, endpoints=e, input=inp)
                    for r in run_config(masked(g_naive, ~nodata), k, shape, pairs, T):
                        rows.append({**base, "layer": "none", "policy": "naive", "param": "", **r})
                    for lay, h in hz.items():
                        h = h[:shape[0], :shape[1]]
                        for tau in TAUS:
                            cls = TC.classify(a.q_pass, h, tau); cls[nodata] = 5
                            keep = (cls == 0).ravel()
                            for r in run_config(masked(g_cut, keep), k, shape, pairs, T, keep):
                                rows.append({**base, "layer": lay, "policy": "conservative", "param": tau, **r})
                        cls = TC.classify(a.q_pass, h, 0.2); cls[nodata] = 5
                        keep = ((cls != 1) & (cls != 5)).ravel()
                        for w in WEIGHTS:
                            for r in run_config(masked(g_cut, keep, h, float(w)), k, shape, pairs, T, keep):
                                rows.append({**base, "layer": lay, "policy": "risk_weighted", "param": w, **r})
                say(f"A {site} {prof_name} {inp}: {time.time() - t0:.0f} s")
        write(os.path.join(CDIR, f"routes_A_{site}.csv"), rows)
        say(f"A {site}: {len(rows)} routes in {time.time() - t0:.0f} s")
        del T
        write(os.path.join(CDIR, f"descent_rule_{site}.csv"), [x for x in stats if x["site"] == site])


def shifted(mask, dr, dc):
    out = np.zeros_like(mask)
    nr, nc = mask.shape
    rs, rd = (slice(0, nr - dr), slice(dr, nr)) if dr >= 0 else (slice(-dr, nr), slice(0, nr + dr))
    cs, cd = (slice(0, nc - dc), slice(dc, nc)) if dc >= 0 else (slice(-dc, nc), slice(0, nc + dc))
    out[rd, cd] = mask[rs, cs]
    return out


def part_C(sites=None):
    prof = PL.builtin_profile("published-posterior")
    for site in (sites or SITES):
        rows = []
        t0 = time.time()
        T = site_truth(site)
        surf = surfaces(site, T)
        E = json.load(open(os.path.join(CDIR, f"endpoints_{site}.json")))
        maps = {"FACEMAP": T["patch"]}
        for s_m in (5, 10, 30):
            for ang in range(0, 360, 45):
                dr = int(round(-s_m * np.cos(np.radians(ang)))); dc = int(round(s_m * np.sin(np.radians(ang))))
                maps[f"shift{s_m}_{ang}"] = shifted(T["patch"], dr, dc)
        surveys = {}
        for s_m in (2, 5):
            zs = B.block(T["z1f"], s_m)
            st = B.slope_deg(zs, float(s_m)) >= B.FACE_DEG
            surveys[f"survey{s_m}"] = (B.face_patches(st, int(np.ceil(10.0 / s_m ** 2))), s_m)
        for inp in ("I10", "I30"):
            zc, k = surf[inp]
            a = PL.assess(PL.raster_from_array(zc, float(k)), profile=prof, n_draws=128)
            shape = a.classes.shape; nodata = a.classes == 5
            g_cut, _ = base_graph(a, True)
            fm = {n: B.block(m, k, "any")[:shape[0], :shape[1]].astype(float) for n, m in maps.items()}
            for n, (m, s_m) in surveys.items():
                fm[n] = B.block(m, k // s_m, "any")[:shape[0], :shape[1]].astype(float)
            for name, h in fm.items():
                cls = TC.classify(a.q_pass, h, 0.5); cls[nodata] = 5
                for pol, keep, w in (("conservative", (cls == 0).ravel(), 0.0), ("risk_weighted", ((cls != 1) & (cls != 5)).ravel(), 5.0)):
                    g = masked(g_cut, keep, h, w)
                    for e in ("E1", "E2"):
                        pairs = [(np.array(p), np.array(q)) for p, q in E[e]]
                        for r in run_config(g, k, shape, pairs, T, keep):
                            rows.append({"site": site, "endpoints": e, "input": inp, "map": name, "policy": pol, **r})
        write(os.path.join(CDIR, f"routes_C_{site}.csv"), rows)
        say(f"C {site}: {time.time() - t0:.0f} s")
        del T


# ---------------------------------------------------------------------------------------------------------------------
# summaries: held out operating points, two stage bootstrap, sign flip
# ---------------------------------------------------------------------------------------------------------------------
def _f(x):
    return x in (True, "True", "true", 1, "1")


def load_routes(name):
    rows = []
    for site in SITES:
        rows += list(csv.DictReader(open(os.path.join(CDIR, f"{name}_{site}.csv"))))
    for r in rows:
        r["routed"] = _f(r["routed"])
        r["success"] = r["routed"] and not _f(r.get("unsafe", ""))
        r["success_fp"] = r["routed"] and not _f(r.get("unsafe_fp", ""))
    return rows


def two_stage(diff_by_site, n_boot=4000, seed=SEED):
    rng = np.random.default_rng(seed)
    sites = [np.asarray(d, float) for d in diff_by_site if len(d)]
    out = []
    for _ in range(n_boot):
        pick = [sites[i] for i in rng.integers(0, len(sites), len(sites))]
        out.append(np.mean(np.concatenate([d[rng.integers(0, len(d), len(d))] for d in pick])))
    return [float(x) for x in np.percentile(out, [2.5, 97.5])]


def sign_flip_p(d):
    d = np.asarray(d, float); obs = abs(d.mean())
    return float(np.mean([abs((d * np.array(s)).mean()) >= obs - 1e-12 for s in itertools.product((1, -1), repeat=len(d))]))


def agg(rr):
    n = len(rr); routed = [r for r in rr if r["routed"]]
    km = sum(float(r["length_m"]) for r in routed) / 1000.0
    unsafe = [r for r in routed if _f(r["unsafe"])]
    desc_only = [r for r in unsafe if int(r.get("contact_descent") or 0) > 0 and int(r.get("contact_climb") or 0) == 0 and int(r.get("contact_traverse") or 0) == 0]
    return {"pairs": n, "routed": round(len(routed) / n, 4) if n else "", "mission_success": round(sum(r["success"] for r in rr) / n, 4) if n else "",
            "success_footprint": round(sum(r["success_fp"] for r in rr) / n, 4) if n else "",
            "unsafe_of_routed": round(len(unsafe) / len(routed), 4) if routed else "",
            "unsafe_fp_of_routed": round(sum(_f(r["unsafe_fp"]) for r in routed) / len(routed), 4) if routed else "",
            "m_on_face_per_km": round(sum(float(r["m_on_face"]) for r in routed) / km, 2) if km else "",
            "length_ratio": round(float(np.mean([float(r["length_ratio"]) for r in routed])), 3) if routed else "",
            "unsafe_descent_only": round(len(desc_only) / len(unsafe), 4) if unsafe else ""}


def summary():
    rows = load_routes("routes_A")
    key = lambda r: (r["profile"], r["endpoints"], r["input"], r["layer"], r["policy"], r["param"])
    groups = {}
    for r in rows:
        groups.setdefault(key(r), []).append(r)
    sweep = []
    for k_, rr in sorted(groups.items()):
        sweep.append(dict(zip(("profile", "endpoints", "input", "layer", "policy", "param"), k_), **agg(rr)))
    write(os.path.join(OUT, "A_sweep.csv"), sweep)
    # per site success for every setting
    by_site = {}
    for r in rows:
        by_site.setdefault(key(r) + (r["site"],), []).append(r)
    # refusal breakdown (B) for every gated setting
    refus = []
    for k_, rr in sorted(groups.items()):
        if k_[4] == "naive":
            continue
        un = [r for r in rr if not r["routed"]]
        if not un:
            continue
        s_ok = [_f(r["start_ok"]) for r in un]; g_ok = [_f(r["goal_ok"]) for r in un]
        refus.append(dict(zip(("profile", "endpoints", "input", "layer", "policy", "param"), k_), unrouted=len(un),
                          start_refused=sum((not a) and b for a, b in zip(s_ok, g_ok)), goal_refused=sum(a and (not b) for a, b in zip(s_ok, g_ok)),
                          both_refused=sum((not a) and (not b) for a, b in zip(s_ok, g_ok)), disconnected=sum(a and b for a, b in zip(s_ok, g_ok))))
    write(os.path.join(OUT, "B_refusals.csv"), refus)
    # held out operating point per layer and policy (and jointly over both policies)
    held = []
    pair_success = {}
    for (pf, e) in COMBOS:
        for inp in ("I10", "I30", "G30"):
            naive = {(r["site"], r["pair"]): r["success"] for r in rows if key(r) == (pf, e, inp, "none", "naive", "")}
            if not naive:
                continue
            for lay in LAYERS:
                for pols in (("conservative",), ("risk_weighted",), ("conservative", "risk_weighted")):
                    cands = [(p, prm) for (pf_, e_, i_, l_, p, prm) in groups if (pf_, e_, i_, l_) == (pf, e, inp, lay) and p in pols]
                    if not cands:
                        continue
                    chosen, succ = {}, {}
                    for s in SITES:
                        def pooled(c):
                            rr = [r for x in SITES if x != s for r in by_site.get((pf, e, inp, lay, c[0], c[1], x), [])]
                            return np.mean([r["success"] for r in rr]) if rr else -1
                        best = max(cands, key=lambda c: (pooled(c), -TAUS.index(float(c[1])) if c[0] == "conservative" else 0))
                        chosen[s] = best
                        for r in by_site[(pf, e, inp, lay, best[0], best[1], s)]:
                            succ[(s, r["pair"])] = r
                    d_by_site = [[float(succ[(s, p)]["success"]) - float(naive[(s, p)]) for (s2, p) in naive if s2 == s] for s in SITES]
                    per_site = [float(np.mean(d)) for d in d_by_site]
                    lo, hi = two_stage(d_by_site)
                    a_ = agg(list(succ.values()))
                    name = "+".join(pols)
                    held.append({"profile": pf, "endpoints": e, "input": inp, "layer": lay, "policies": name,
                                 "chosen": " ".join(f"{s}:{c[0][:4]}{c[1]}" for s, c in chosen.items()), **a_,
                                 "naive_success": round(float(np.mean(list(naive.values()))), 4),
                                 "difference": round(float(np.mean(sum(d_by_site, []))), 4), "diff_lo": round(lo, 4), "diff_hi": round(hi, 4),
                                 "positive_sites": int(sum(x > 0 for x in per_site)), "p_sign_flip": round(sign_flip_p(per_site), 4)})
                    pair_success[(pf, e, inp, lay, name)] = {k2: v["success"] for k2, v in succ.items()}
    write(os.path.join(OUT, "A_held_out.csv"), held)
    # naive summaries by endpoint set (P28-5) and footprint (P28-6)
    base = []
    for (pf, e) in COMBOS:
        for inp in ("I10", "I30", "G30"):
            rr = groups.get((pf, e, inp, "none", "naive", ""), [])
            if rr:
                base.append({"profile": pf, "endpoints": e, "input": inp, **agg(rr)})
    write(os.path.join(OUT, "A_naive.csv"), base)
    say(f"summary A: {len(sweep)} settings, {len(held)} held out rows")
    stats = [r for s_ in SITES for r in csv.DictReader(open(os.path.join(CDIR, f"descent_rule_{s_}.csv")))]
    write(os.path.join(OUT, "D_descent_rule.csv"), stats)
    if all(os.path.exists(os.path.join(CDIR, f"routes_C_{s_}.csv")) for s_ in SITES):
        rc = load_routes("routes_C")
        g = {}
        for r in rc:
            nm = r["map"].split("_")[0]
            g.setdefault((r["endpoints"], r["input"], nm, r["policy"]), []).append(r)
        write(os.path.join(OUT, "C_degraded.csv"), [dict(zip(("endpoints", "input", "map", "policy"), k_), **agg(v)) for k_, v in sorted(g.items())])


# ---------------------------------------------------------------------------------------------------------------------
# E: closed loop with local sensing on a 5 m grid
# ---------------------------------------------------------------------------------------------------------------------
def closed_loop(a, h, k, T, pairs, R, w=5.0, max_steps=4000):
    """Global prior from the coarse assessment a (risk weighted, weight w, face probability h), local 5 m grid, sensing
    radius R metres on the lidar face patches. Returns one dict per pair."""
    from scipy.ndimage import zoom
    from scipy.sparse.csgraph import dijkstra
    from dunerover.dem import Dem
    from dunerover import traverse as TR
    f = k // 5
    zc = a.raster.z
    z5 = zoom(zc, f, order=1, mode="nearest", grid_mode=True)
    nr, nc = z5.shape
    dem = Dem(z5, 0.0, 0.0, 1.0, 1.0, 5.0, 5.0, source="closed loop")
    eg = TR.precompute_edges(dem)
    p = a.profile.nominal_params()
    cls5 = np.repeat(np.repeat(a.classes, f, 0), f, 1)[:nr, :nc]
    h5 = np.repeat(np.repeat(h, f, 0), f, 1)[:nr, :nc].astype(float)
    face5 = B.block(T["patch"], 5, "any")[:nr, :nc]
    src, dst, cost = [], [], []
    for s, d, dist, ta, tc in zip(eg.src, eg.dst, eg.dist, eg.tan_a, eg.tan_c):
        c = edge_cost(dist, _slip(ta, tc, p), p.i_max)
        ok = np.isfinite(c) & (np.asarray(ta) > DESCENT_CUT)
        src.append(s[ok]); dst.append(d[ok]); cost.append(c[ok])
    src = np.concatenate(src); dst = np.concatenate(dst); cost = np.concatenate(cost)
    allowed0 = ((cls5 != 1) & (cls5 != 5)).ravel()
    rr_, cc_ = np.indices((nr, nc))
    out = []
    for n, (pa, pb) in enumerate(pairs):
        s0 = (min(int(pa[0] // 5), nr - 1), min(int(pa[1] // 5), nc - 1)); g0 = (min(int(pb[0] // 5), nr - 1), min(int(pb[1] // 5), nc - 1))
        # crop to the pair's bounding box plus 300 m
        m = 60
        r0, r1 = max(0, min(s0[0], g0[0]) - m), min(nr, max(s0[0], g0[0]) + m + 1)
        c0, c1 = max(0, min(s0[1], g0[1]) - m), min(nc, max(s0[1], g0[1]) + m + 1)
        sr, sc = np.divmod(src, nc); dr_, dc_ = np.divmod(dst, nc)
        inb = (sr >= r0) & (sr < r1) & (sc >= c0) & (sc < c1) & (dr_ >= r0) & (dr_ < r1) & (dc_ >= c0) & (dc_ < c1)
        lnc = c1 - c0
        ls = (sr[inb] - r0) * lnc + (sc[inb] - c0); ld = (dr_[inb] - r0) * lnc + (dc_[inb] - c0)
        gidx = dst[inb]
        base_cost = cost[inb]
        ncell = (r1 - r0) * lnc
        known_face = np.zeros(ncell, bool); known_free = np.zeros(ncell, bool)
        allowed = allowed0.reshape(nr, nc)[r0:r1, c0:c1].ravel().copy()
        hl = h5[r0:r1, c0:c1].ravel(); facel = face5[r0:r1, c0:c1].ravel()
        RR, CC = rr_[r0:r1, c0:c1].ravel(), cc_[r0:r1, c0:c1].ravel()
        cur = (s0[0] - r0) * lnc + (s0[1] - c0); goal = (g0[0] - r0) * lnc + (g0[1] - c0)
        allowed[cur] = True

        def sense(cell):
            r, c = divmod(cell, lnc)
            dist = np.hypot((RR - (r + r0)) * 5.0, (CC - (c + c0)) * 5.0)
            near = dist <= R
            known_face[near & facel] = True; known_free[near & ~facel] = True

        def plan():
            ok = allowed[ls] & allowed[ld] & ~known_face[ld]
            pen = np.where(known_free[ld], 1.0, 1.0 + w * hl[ld])
            g = csr_matrix((base_cost[ok] * pen[ok], (ls[ok], ld[ok])), shape=(ncell, ncell))
            dist, pred = dijkstra(g, directed=True, indices=cur, return_predecessors=True)
            if not np.isfinite(dist[goal]):
                return None
            path = [goal]
            while path[-1] != cur:
                path.append(int(pred[path[-1]]))
            return path[::-1]
        sense(cur)
        path = plan(); driven = [cur]; replans = 0; status = "stuck"
        steps = 0
        while path is not None and steps < max_steps:
            if cur == goal:
                status = "reached"; break
            nxt = path[1]
            cur = nxt; driven.append(cur); path = path[1:]; steps += 1
            sense(cur)
            if known_face[path].any():
                replans += 1
                path = plan()
        if cur == goal:
            status = "reached"
        rc = np.array([divmod(c, lnc) for c in driven]) + np.array([r0, c0])
        sc_ = score(samples(rc, 5), T)
        straight = float(np.hypot(*(pa - pb)))
        out.append({"pair": n, "status": status, "success": status == "reached" and not sc_["unsafe"], "replans": replans,
                    "driven_m": sc_["length_m"], "length_ratio": round(sc_["length_m"] / straight, 3), "unsafe": sc_["unsafe"],
                    "m_on_face": sc_["m_on_face"]})
    return out


E_LAYERS = ("none", "DET", "BICUBIC-cal", "GBM", "FACEMAP")
# amended before part E was run (register note after stage 28): 20 pairs per site; the radius and vehicle
# sensitivities on the E1 endpoints and I30 only; crop margin 300 m
E_CONFIGS = ([("published-posterior", inp, 20.0, e) for inp in ("I30", "I10") for e in ("E1", "E2")]
             + [("published-posterior", "I30", R, "E1") for R in (10.0, 30.0)]
             + [("assumed", "I30", 20.0, "E1")])


def part_E(sites=None, n_pairs=20, tag="E"):
    rows = []
    for site in (sites or SITES):
        t0 = time.time()
        T = site_truth(site)
        surf = surfaces(site, T)
        E = json.load(open(os.path.join(CDIR, f"endpoints_{site}.json")))
        assessed = {}
        for prof_name, inp, R, e in E_CONFIGS:
            if (prof_name, inp) not in assessed:
                zc, k = surf[inp]
                assessed[(prof_name, inp)] = (PL.assess(PL.raster_from_array(zc, float(k)), profile=PL.builtin_profile(prof_name), n_draws=128), k)
            a, k = assessed[(prof_name, inp)]
            hz = layers_for(site, inp)
            pairs = [(np.array(p), np.array(q)) for p, q in E[e][:n_pairs]]
            for lay in E_LAYERS:
                h = np.zeros(a.classes.shape) if lay == "none" else hz[lay][:a.classes.shape[0], :a.classes.shape[1]]
                for r in closed_loop(a, h, k, T, pairs, R):
                    rows.append({"site": site, "profile": prof_name, "input": inp, "layer": lay, "radius_m": R, "endpoints": e, **r})
            say(f"{tag} {site} {prof_name} {inp} R {R:g} {e}: {time.time() - t0:.0f} s")
        write(os.path.join(CDIR, f"routes_{tag}_{site}.csv"), [r for r in rows if r["site"] == site])
        del T
    # summary
    g = {}
    for r in rows:
        g.setdefault((r["profile"], r["endpoints"], r["input"], r["layer"], r["radius_m"]), []).append(r)
    summ = []
    for k_, rr in sorted(g.items(), key=lambda x: str(x[0])):
        summ.append(dict(zip(("profile", "endpoints", "input", "layer", "radius_m"), k_), pairs=len(rr),
                         success=round(np.mean([r["success"] for r in rr]), 4), stuck=round(np.mean([r["status"] == "stuck" for r in rr]), 4),
                         unsafe=round(np.mean([r["unsafe"] for r in rr]), 4),
                         length_ratio_reached=round(float(np.mean([r["length_ratio"] for r in rr if r["status"] == "reached"] or [np.nan])), 3),
                         replans=round(float(np.mean([r["replans"] for r in rr])), 2)))
    write(os.path.join(OUT, f"{tag}_closed_loop.csv"), summ)


def summary_E():
    rows = load_routes("routes_E")
    for r in rows:
        r["success"] = _f(r["success"]); r["unsafe"] = _f(r["unsafe"])
    g = {}
    for r in rows:
        g.setdefault((r["profile"], r["endpoints"], r["input"], r["layer"], r["radius_m"]), []).append(r)
    summ = []
    for k_, rr in sorted(g.items(), key=lambda x: str(x[0])):
        reached = [float(r["length_ratio"]) for r in rr if r["status"] == "reached"]
        summ.append(dict(zip(("profile", "endpoints", "input", "layer", "radius_m"), k_), pairs=len(rr),
                         success=round(float(np.mean([r["success"] for r in rr])), 4), stuck=round(float(np.mean([r["status"] == "stuck" for r in rr])), 4),
                         unsafe=round(float(np.mean([r["unsafe"] for r in rr])), 4),
                         length_ratio_reached=round(float(np.mean(reached)), 3) if reached else "",
                         replans=round(float(np.mean([float(r["replans"]) for r in rr])), 2)))
    # differences against the slip only prior with the same sensing (two stage bootstrap over sites and pairs)
    for row in summ:
        if row["layer"] == "none":
            continue
        k0 = (row["profile"], row["endpoints"], row["input"], "none", row["radius_m"])
        base = {(r["site"], r["pair"]): r["success"] for r in g.get(k0, [])}
        cur = {(r["site"], r["pair"]): r["success"] for r in g[(row["profile"], row["endpoints"], row["input"], row["layer"], row["radius_m"])]}
        d = [[float(cur[(s_, p)]) - float(base[(s_, p)]) for (s2, p) in cur if s2 == s_ and (s_, p) in base] for s_ in SITES]
        lo, hi = two_stage(d)
        row.update(diff_vs_slip_only=round(float(np.mean(sum(d, []))), 4), diff_lo=round(lo, 4), diff_hi=round(hi, 4))
    write(os.path.join(OUT, "E_closed_loop.csv"), summ)


def main():
    global LOG
    os.makedirs(OUT, exist_ok=True); os.makedirs(CDIR, exist_ok=True)
    LOG = open(os.path.join(OUT, "run_log.txt"), "a")
    parts = sys.argv[1:]
    say(f"stage 28 {' '.join(parts)} started {time.strftime('%Y-%m-%d %H:%M:%S')}; numpy {np.__version__}; seed {SEED}")
    for p in parts:
        t0 = time.time()
        name, _, sites = p.partition(":")
        fn = {"A": part_A, "C": part_C, "summary": summary, "E": part_E, "summaryE": summary_E}[name]
        fn(sites.split(",")) if sites else fn()
        say(f"part {p} done in {time.time() - t0:.0f} s ({time.strftime('%H:%M:%S')})")


if __name__ == "__main__":
    main()
