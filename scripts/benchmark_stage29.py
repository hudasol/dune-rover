#!/usr/bin/env python3
"""Stage 29 (docs/PREDICTIONS.md): POST HOC analyses after the second blind review.

    OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/benchmark_stage29.py a b c d e f [site,site,...]

(a) patch size of the truth; (b) planning on 5 m block means and with the SR and CNN-long layers; (c) degraded face maps
at a held out weight; (d) closed loop with line of sight sensing; (e) survey coverage; (f) GLO-30 at sites without
migration. Outputs: results/benchmark/stage29/*.csv and run_log.txt; per site chunks in data/cache/stage29/.
POST HOC, SIMULATED BY ME on PUBLISHED data. Deterministic.
"""
from __future__ import annotations
import csv, json, os, sys, time
import numpy as np
from scipy.ndimage import maximum_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dunerover import benchmark as B, planner as PL, threeclass as TC  # noqa: E402
import benchmark_detection as BD  # noqa: E402
import benchmark_stage28 as S28  # noqa: E402

OUT = os.path.join(ROOT, "results", "benchmark", "stage29")
CDIR = os.path.join(ROOT, "data", "cache", "stage29")
SITES = list(BD.SITES)
WGRID = (1, 2, 5, 10, 20, 50, 100, 1000)
POST = PL.builtin_profile("published-posterior")
LOG = None


def say(m):
    print(m, flush=True)
    if LOG:
        LOG.write(m + "\n"); LOG.flush()


def write(path, rows):
    S28.write(path, rows)


def truth(site):
    fname, win, _ = BD.SITES[site]
    z1, _, _, _ = BD.load_lidar_window(fname, win)
    void = np.isnan(z1); z1f = B.fill_nearest(z1)
    steep, _ = B.steep_posts(z1, void)
    from scipy.ndimage import uniform_filter
    from dunerover.terrain import horn_gradient
    ge, gn = horn_gradient(uniform_filter(z1f, 5, mode="nearest"), 1.0, 1.0)
    T = {"z1f": z1f, "void": void, "steep": steep, "down_r": gn.astype(np.float32), "down_c": (-ge).astype(np.float32)}
    for m in (10, 100, 300):
        T[f"p{m}"] = B.face_patches(steep, m)
    T["patch"] = T["p10"]; T["patch_fp"] = maximum_filter(T["p10"], 3, mode="constant")
    return T


def endpoints(site):
    E = json.load(open(os.path.join(S28.CDIR, f"endpoints_{site}.json")))
    return {k: [(np.array(a), np.array(b)) for a, b in v] for k, v in E.items()}


def chosen_settings():
    """Held out operating point per (endpoints, input, layer, site) from stage 28 (posterior, both policies)."""
    out = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "results", "benchmark", "stage28", "A_held_out.csv"))):
        if r["profile"] != "published-posterior" or r["policies"] != "conservative+risk_weighted":
            continue
        for tok in r["chosen"].split():
            s, c = tok.split(":")
            pol = "conservative" if c.startswith("cons") else "risk_weighted"
            out[(r["endpoints"], r["input"], r["layer"], s)] = (pol, float(c[4:]))
    return out


def graph_for(a, g_cut, h, pol, prm, nodata):
    if pol == "conservative":
        cls = TC.classify(a.q_pass, h, prm); cls[nodata] = 5
        return S28.masked(g_cut, (cls == 0).ravel())
    cls = TC.classify(a.q_pass, h, 0.2); cls[nodata] = 5
    return S28.masked(g_cut, ((cls != 1) & (cls != 5)).ravel(), h, float(prm))


def score_multi(rc, k, T, masks):
    sp = S28.samples(rc, k)
    shp = T["p10"].shape
    ri = np.clip(np.floor(sp[:, 0]).astype(int), 0, shp[0] - 1); ci = np.clip(np.floor(sp[:, 1]).astype(int), 0, shp[1] - 1)
    return {f"unsafe_p{m}": bool(T[f"p{m}"][ri, ci].any()) for m in masks}


# ---------------------------------------------------------------------------------------------------------------------
def part_a(sites):
    ch = chosen_settings()
    for site in sites:
        t0 = time.time()
        T = truth(site); surf = S28.surfaces(site, T); E = endpoints(site)
        rows = []
        for inp in ("I10", "I30"):
            zc, k = surf[inp]
            a = PL.assess(PL.raster_from_array(zc, float(k)), profile=POST, n_draws=128)
            shape = a.classes.shape; nodata = a.classes == 5
            g0, _ = S28.base_graph(a, False); g1, _ = S28.base_graph(a, True)
            hz = S28.layers_for(site, inp)
            for e in ("E1", "E2"):
                pairs = E[e]
                S = [S28.BP.cell_of(p[0], k, shape) for p in pairs]; Tg = [S28.BP.cell_of(p[1], k, shape) for p in pairs]
                cfgs = [("none", None, None)]
                for lay in ("BICUBIC-cal", "GBM", "DEM+S2", "FACEMAP"):
                    pol, prm = ch[(e, inp, lay, site)]
                    if lay == "FACEMAP":
                        for m in (10, 100, 300):
                            cfgs.append((f"FACEMAP{m}", pol, prm))
                    else:
                        cfgs.append((lay, pol, prm))
                for lay, pol, prm in cfgs:
                    if lay == "none":
                        g = S28.masked(g0, ~nodata)
                    else:
                        if lay.startswith("FACEMAP"):
                            h = B.block(T[f"p{lay[7:]}"], k, "any")[:shape[0], :shape[1]].astype(float)
                        else:
                            h = hz[lay][:shape[0], :shape[1]]
                        g = graph_for(a, g1, h, pol, prm, nodata)
                    for n, rc in enumerate(B.routes_from(g, shape[1], S, Tg)):
                        row = {"site": site, "endpoints": e, "input": inp, "layer": lay, "pair": n, "routed": rc is not None}
                        if rc is not None:
                            row.update(score_multi(rc, k, T, (10, 100, 300)))
                        rows.append(row)
        os.makedirs(CDIR, exist_ok=True); write(os.path.join(CDIR, f"a_{site}.csv"), rows)
        say(f"a {site}: {time.time() - t0:.0f} s")


def summary_a():
    rows = [r for s in SITES if os.path.exists(os.path.join(CDIR, f"a_{s}.csv")) for r in csv.DictReader(open(os.path.join(CDIR, f"a_{s}.csv")))]
    out = []
    keys = sorted({(r["endpoints"], r["input"], r["layer"]) for r in rows})
    for e, inp, lay in keys:
        rr = [r for r in rows if (r["endpoints"], r["input"], r["layer"]) == (e, inp, lay)]
        for m in (10, 100, 300):
            for excl in (False, True):
                sel = [r for r in rr if not (excl and r["site"] == "Dumont")]
                succ = [r["routed"] == "True" and r.get(f"unsafe_p{m}") == "False" for r in sel]
                out.append({"endpoints": e, "input": inp, "layer": lay, "min_patch_posts": m, "without_dumont": excl, "pairs": len(sel),
                            "mission_success": round(float(np.mean(succ)), 4)})
    write(os.path.join(OUT, "a_patch_size.csv"), out)


# ---------------------------------------------------------------------------------------------------------------------
def held_out(rows_by_site_setting, settings):
    """Pick the setting with the best pooled success on the other sites; return pooled success and the choice."""
    succ, choice = [], {}
    for s in SITES:
        best = max(settings, key=lambda w: (np.mean([x for o in SITES if o != s for x in rows_by_site_setting.get((o, w), [])] or [-1]), -w))
        choice[s] = best
        succ += rows_by_site_setting.get((s, best), [])
    return float(np.mean(succ)), choice


def part_b(sites):
    from dunerover import benchmark as BB
    import benchmark_stage27 as S27
    L27 = os.path.join(ROOT, "data", "cache", "stage27")
    D = {s: dict(np.load(os.path.join(L27, f"{s}.npz"))) for s in SITES}
    # BICUBIC on 5 m and SR on 30 m, calibrated leave one site out on the face map label
    bic5 = {s: BB.bicubic_max_slope(D[s]["z5"].astype(float), 5)[:D[s]["z5"].shape[0], :D[s]["z5"].shape[1]] for s in SITES}
    y5 = {s: D[s]["any5"][:bic5[s].shape[0], :bic5[s].shape[1]] for s in SITES}
    cal5 = S27.loso_platt(bic5, y5)
    sr = {s: np.load(os.path.join(L27, f"SR_{s}_I30.npy")).astype(float) for s in SITES}
    y30 = {s: D[s]["any30"][:sr[s].shape[0], :sr[s].shape[1]] for s in SITES}
    calsr = S27.loso_platt(sr, y30)
    G = np.load(os.path.join(L27, "G_I30.npz"))
    for site in sites:
        t0 = time.time()
        T = truth(site); E = endpoints(site)
        rows = []
        for inp, k, layers in (("I5", 5, {"BICUBIC-cal": cal5[site], "FACEMAP": y5[site].astype(float)}),
                               ("I30", 30, {"SR-cal": calsr[site], "CNN-long": G[f"{site}|CNN-long"].astype(float)})):
            zc = B.block(T["z1f"], k)
            a = PL.assess(PL.raster_from_array(zc, float(k)), profile=POST, n_draws=128)
            shape = a.classes.shape; nodata = a.classes == 5
            g0, _ = S28.base_graph(a, False); g1, _ = S28.base_graph(a, True)
            pairs = E["E1"]
            S = [S28.BP.cell_of(p[0], k, shape) for p in pairs]; Tg = [S28.BP.cell_of(p[1], k, shape) for p in pairs]
            cfgs = [("none", 0)] + [(lay, w) for lay in layers for w in WGRID]
            for lay, w in cfgs:
                g = S28.masked(g0, ~nodata) if lay == "none" else graph_for(a, g1, layers[lay][:shape[0], :shape[1]], "risk_weighted", w, nodata)
                for n, rc in enumerate(B.routes_from(g, shape[1], S, Tg)):
                    row = {"site": site, "input": inp, "layer": lay, "w": w, "pair": n, "routed": rc is not None}
                    if rc is not None:
                        row.update(S28.score(S28.samples(rc, k), T)); row["length_ratio"] = round(row["length_m"] / float(np.hypot(*(pairs[n][0] - pairs[n][1]))), 3)
                    rows.append(row)
            say(f"b {site} {inp}: {time.time() - t0:.0f} s")
        os.makedirs(CDIR, exist_ok=True); write(os.path.join(CDIR, f"b_{site}.csv"), rows)


def summary_b():
    rows = [r for s in SITES if os.path.exists(os.path.join(CDIR, f"b_{s}.csv")) for r in csv.DictReader(open(os.path.join(CDIR, f"b_{s}.csv")))]
    out = []
    for inp in ("I5", "I30"):
        naive = {(r["site"], r["pair"]): (r["routed"] == "True" and r["unsafe"] == "False") for r in rows if r["input"] == inp and r["layer"] == "none"}
        out.append({"input": inp, "layer": "none", "mission_success": round(float(np.mean(list(naive.values()))), 4), "chosen": "", "difference": "", "diff_lo": "", "diff_hi": ""})
        for lay in sorted({r["layer"] for r in rows if r["input"] == inp and r["layer"] != "none"}):
            by = {}
            for r in rows:
                if r["input"] == inp and r["layer"] == lay:
                    by.setdefault((r["site"], float(r["w"])), []).append(r["routed"] == "True" and r["unsafe"] == "False")
            m, choice = held_out(by, sorted({w for _, w in by}))
            pair_s = {}
            for r in rows:
                if r["input"] == inp and r["layer"] == lay and float(r["w"]) == choice[r["site"]]:
                    pair_s[(r["site"], r["pair"])] = r["routed"] == "True" and r["unsafe"] == "False"
            d = [[float(pair_s[(s, p)]) - float(naive[(s, p)]) for (s2, p) in naive if s2 == s] for s in SITES]
            lo, hi = S28.two_stage(d)
            out.append({"input": inp, "layer": lay, "mission_success": round(m, 4), "chosen": " ".join(f"{s}:{choice[s]:g}" for s in SITES),
                        "difference": round(float(np.mean(sum(d, []))), 4), "diff_lo": round(lo, 4), "diff_hi": round(hi, 4)})
    write(os.path.join(OUT, "b_planning.csv"), out)


# ---------------------------------------------------------------------------------------------------------------------
def part_c(sites):
    for site in sites:
        t0 = time.time()
        T = truth(site); surf = S28.surfaces(site, T); E = endpoints(site)
        maps = {"FACEMAP": T["p10"]}
        for s_m in (5, 10, 30):
            for ang in range(0, 360, 45):
                dr = int(round(-s_m * np.cos(np.radians(ang)))); dc = int(round(s_m * np.sin(np.radians(ang))))
                maps[f"shift{s_m}_{ang}"] = S28.shifted(T["p10"], dr, dc)
        rows = []
        for inp in ("I10", "I30"):
            zc, k = surf[inp]
            a = PL.assess(PL.raster_from_array(zc, float(k)), profile=POST, n_draws=128)
            shape = a.classes.shape; nodata = a.classes == 5
            g1, _ = S28.base_graph(a, True)
            pairs = E["E1"]
            S = [S28.BP.cell_of(p[0], k, shape) for p in pairs]; Tg = [S28.BP.cell_of(p[1], k, shape) for p in pairs]
            for name, m in maps.items():
                h = B.block(m, k, "any")[:shape[0], :shape[1]].astype(float)
                for w in WGRID:
                    g = graph_for(a, g1, h, "risk_weighted", w, nodata)
                    for n, rc in enumerate(B.routes_from(g, shape[1], S, Tg)):
                        row = {"site": site, "input": inp, "map": name, "w": w, "pair": n, "routed": rc is not None}
                        if rc is not None:
                            row.update(S28.score(S28.samples(rc, k), T))
                        rows.append(row)
            say(f"c {site} {inp}: {time.time() - t0:.0f} s")
        os.makedirs(CDIR, exist_ok=True); write(os.path.join(CDIR, f"c_{site}.csv"), rows)


def summary_c():
    rows = [r for s in SITES if os.path.exists(os.path.join(CDIR, f"c_{s}.csv")) for r in csv.DictReader(open(os.path.join(CDIR, f"c_{s}.csv")))]
    out = []
    for inp in ("I10", "I30"):
        for fam in ("FACEMAP", "shift5", "shift10", "shift30"):
            by = {}
            for r in rows:
                if r["input"] == inp and r["map"].split("_")[0] == fam:
                    by.setdefault((r["site"], float(r["w"])), []).append(r["routed"] == "True" and r["unsafe"] == "False")
            m, choice = held_out(by, sorted({w for _, w in by}))
            out.append({"input": inp, "map": fam, "mission_success": round(m, 4), "chosen": " ".join(f"{s}:{choice[s]:g}" for s in SITES)})
    write(os.path.join(OUT, "c_degraded_held_out.csv"), out)


# ---------------------------------------------------------------------------------------------------------------------
def part_d(sites, n_pairs=20, R=20.0, eye=1.0, target=0.2):
    """Closed loop of stage 28 part E with line of sight sensing and a 600 m crop margin (I30, E1, posterior)."""
    import types
    for site in sites:
        t0 = time.time()
        T = truth(site); surf = S28.surfaces(site, T); E = endpoints(site)
        z1f = T["z1f"]
        zc, k = surf["I30"]
        a = PL.assess(PL.raster_from_array(zc, float(k)), profile=POST, n_draws=128)
        hz = S28.layers_for(site, "I30")
        rows = []

        def visible(rr, cc, cells_r, cells_c):
            """Line of sight from (rr, cc) (5 m cell indices) to the centres of the given 5 m cells on the 1 m surface."""
            y0, x0 = (rr + 0.5) * 5.0, (cc + 0.5) * 5.0
            h0 = z1f[min(int(y0), z1f.shape[0] - 1), min(int(x0), z1f.shape[1] - 1)] + eye
            y1, x1 = (cells_r + 0.5) * 5.0, (cells_c + 0.5) * 5.0
            iy1 = np.clip(y1.astype(int), 0, z1f.shape[0] - 1); ix1 = np.clip(x1.astype(int), 0, z1f.shape[1] - 1)
            h1 = z1f[iy1, ix1] + target
            ok = np.ones(len(y1), bool)
            for f in np.linspace(0.05, 0.95, 19):
                ys = y0 + f * (y1 - y0); xs = x0 + f * (x1 - x0)
                zt = z1f[np.clip(ys.astype(int), 0, z1f.shape[0] - 1), np.clip(xs.astype(int), 0, z1f.shape[1] - 1)]
                ok &= zt < h0 + f * (h1 - h0)
            return ok
        for lay in ("none", "GBM", "FACEMAP"):
            h = np.zeros(a.classes.shape) if lay == "none" else hz[lay][:a.classes.shape[0], :a.classes.shape[1]]
            pairs = E["E1"][:n_pairs]
            for r in S28.closed_loop(a, h, k, T, pairs, R, visibility=visible, margin=120):
                rows.append({"site": site, "layer": lay, **r})
            say(f"d {site} {lay}: {time.time() - t0:.0f} s")
        os.makedirs(CDIR, exist_ok=True); write(os.path.join(CDIR, f"d_{site}.csv"), rows)


def summary_d():
    rows = [r for s in SITES if os.path.exists(os.path.join(CDIR, f"d_{s}.csv")) for r in csv.DictReader(open(os.path.join(CDIR, f"d_{s}.csv")))]
    out = []
    for lay in ("none", "GBM", "FACEMAP"):
        rr = [r for r in rows if r["layer"] == lay]
        if not rr:
            continue
        n = len(rr)
        out.append({"layer": lay, "pairs": n, "success": round(sum(r["success"] == "True" for r in rr) / n, 4),
                    "unsafe": round(sum(r["unsafe"] == "True" for r in rr) / n, 4),
                    "stuck_at_start": round(sum(r["status"] == "stuck" and r["replans"] == "0" for r in rr) / n, 4),
                    "stuck_after_replans": round(sum(r["status"] == "stuck" and r["replans"] != "0" for r in rr) / n, 4),
                    "gave_up": round(sum(r["status"] == "gave_up" for r in rr) / n, 4),
                    "replans": round(float(np.mean([float(r["replans"]) for r in rr])), 2)})
    write(os.path.join(OUT, "d_closed_loop_line_of_sight.csv"), out)


# ---------------------------------------------------------------------------------------------------------------------
def part_e(sites):
    out = []
    for site in sites:
        T = truth(site)
        P = T["p10"]
        for s_m in (2, 5):
            zs = B.block(T["z1f"], s_m)
            sp = B.face_patches(B.slope_deg(zs, float(s_m)) >= B.FACE_DEG, int(np.ceil(10.0 / s_m ** 2)))
            up = np.repeat(np.repeat(sp, s_m, 0), s_m, 1)
            n, m = min(up.shape[0], P.shape[0]), min(up.shape[1], P.shape[1])
            out.append({"site": site, "survey_m": s_m, "face_posts_covered": round(float((up[:n, :m] & P[:n, :m]).sum() / P[:n, :m].sum()), 4)})
        say(f"e {site}")
    write(os.path.join(OUT, "e_survey_coverage.csv"), out)


def part_f(_sites):
    out = []
    D = list(csv.DictReader(open(os.path.join(ROOT, "results", "benchmark", "stage27", "D_metrics.csv"))))
    H = list(csv.DictReader(open(os.path.join(ROOT, "results", "benchmark", "stage28", "A_held_out.csv"))))
    still = ("Dumont", "Kelso")
    for m in ("BICUBIC", "GBM", "DET", "SLOPE"):
        a = [float(r["auc"]) for r in D if r["input"] == "G30n" and r["method"] == m and r["site"] in still]
        b = [float(r["auc"]) for r in D if r["input"] == "G30n" and r["method"] == m and r["site"] not in still]
        out.append({"analysis": "detection G30n AUC", "layer": m, "sites_without_shift": round(float(np.mean(a)), 4), "other_sites": round(float(np.mean(b)), 4)})
    rows = []
    for s in SITES:
        rows += [r for r in csv.DictReader(open(os.path.join(S28.CDIR, f"routes_A_{s}.csv"))) if r["profile"] == "published-posterior" and r["endpoints"] == "E1" and r["input"] in ("G30", "I30")]
    ch = chosen_settings()
    for inp in ("I30", "G30"):
        for lay in ("none", "BICUBIC-cal", "GBM", "FACEMAP"):
            def succ(group):
                v = []
                for r in rows:
                    if r["input"] != inp or r["site"] not in group:
                        continue
                    if lay == "none":
                        if r["policy"] == "naive":
                            v.append(r["routed"] == "True" and r["unsafe"] == "False")
                    else:
                        pol, prm = ch[("E1", inp, lay, r["site"])]
                        if r["layer"] == lay and r["policy"] == pol and float(r["param"]) == prm:
                            v.append(r["routed"] == "True" and r["unsafe"] == "False")
                return round(float(np.mean(v)), 4) if v else ""
            out.append({"analysis": f"planning {inp} mission success (E1, held out)", "layer": lay,
                        "sites_without_shift": succ(still), "other_sites": succ([s for s in SITES if s not in still])})
    write(os.path.join(OUT, "f_glo30_migration.csv"), out)


def main():
    global LOG
    os.makedirs(OUT, exist_ok=True); os.makedirs(CDIR, exist_ok=True)
    LOG = open(os.path.join(OUT, "run_log.txt"), "a")
    args = sys.argv[1:]
    sites = SITES
    if args and "," in args[-1] or (args and args[-1] in SITES):
        sites = args[-1].split(","); args = args[:-1]
    say(f"stage 29 {' '.join(args)} on {','.join(sites)} started {time.strftime('%Y-%m-%d %H:%M:%S')}")
    for p in args:
        t0 = time.time()
        globals()[f"part_{p}"](sites)
        say(f"part {p} done in {time.time() - t0:.0f} s ({time.strftime('%H:%M:%S')})")
    for p, fn in (("a", summary_a), ("b", summary_b), ("c", summary_c), ("d", summary_d)):
        if p in args:
            fn()


if __name__ == "__main__":
    main()
