#!/usr/bin/env python3
"""Stage 31 (docs/PREDICTIONS.md): POST HOC analyses after the fourth blind review.

    OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/benchmark_stage31.py a b c e f [site,site,...]
    OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/benchmark_stage31.py summary

(a) sensor variants of the line of sight closed loop (eye height, range noise, per view detection); (b) closed loop with
the weight chosen on the other five sites; (c) vehicle success, other labels, pair distance and route overlap for every
cell of the planning table; (d) site level inference (in the summary); (e) AW3D30 and FABDEM; (f) a U-Net baseline;
(g) summaries without new runs. Per site chunks in data/cache/stage31/, outputs in results/benchmark/stage31/.
POST HOC, SIMULATED BY ME on PUBLISHED data.
"""
from __future__ import annotations
import csv, json, os, sys, time
import numpy as np
from scipy import stats as SS
from scipy.ndimage import uniform_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dunerover import benchmark as B, planner as PL  # noqa: E402
import benchmark_detection as BD  # noqa: E402
import benchmark_stage27 as S27  # noqa: E402
import benchmark_stage28 as S28  # noqa: E402
import benchmark_stage29 as S29  # noqa: E402
import benchmark_stage30 as S30  # noqa: E402

OUT = os.path.join(ROOT, "results", "benchmark", "stage31")
CDIR = os.path.join(ROOT, "data", "cache", "stage31")
C30 = os.path.join(ROOT, "data", "cache", "stage30")
L27 = os.path.join(ROOT, "data", "cache", "stage27")
EXTRA = os.path.join(ROOT, "data", "raw", "extra")
SITES = list(BD.SITES)
W10 = S30.W10
POST = S29.POST
SEED = 20261029
LOG = None
PLAN_LAYERS = ("none", "SLOPE-cal", "BICUBIC-cal", "DET", "GBM", "CNN", "DEM+S2", "FACEMAP")
PLAN_COLS = (("E1", "I10"), ("E2", "I10"), ("E1", "I30"), ("E2", "I30"), ("E1", "G30"))


def say(m):
    print(m, flush=True)
    if LOG:
        LOG.write(m + "\n"); LOG.flush()


def write(path, rows):
    S28.write(path, rows)


def read(path):
    return list(csv.DictReader(open(path)))


def chunk(name):
    return os.path.join(CDIR, name + ".csv")


def ok_(r, key="unsafe"):
    return r["routed"] in (True, "True") and r[key] in (False, "False")


def feas_(r):
    return ok_(r) and r["feasible"] in (True, "True")


# ---------------------------------------------------------------------------------------------------------------------
# (a) sensor variants and (b) held out weight in the line of sight closed loop
# ---------------------------------------------------------------------------------------------------------------------
P4 = ("none", "BICUBIC-cal", "GBM", "FACEMAP")
A_CONFIGS = ([(f"eye{e:g}", lay) for e in (0.5, 1.5) for lay in P4]
             + [(f"noise{s:g}", lay) for s in (0.05, 0.15) for lay in P4]
             + [("obs0.8", lay) for lay in ("none", "GBM", "FACEMAP")])
B_CONFIGS = [("I30", lay, w) for lay in ("BICUBIC-cal", "GBM", "FACEMAP") for w in (1, 20, 100)] + \
            [("I10", lay, w) for lay in ("BICUBIC-cal", "FACEMAP") for w in (1, 20, 100)]


def noisy_face5(T, sigma, site):
    rng = np.random.default_rng([SEED, SITES.index(site), int(round(sigma * 1000))])
    z = T["z1f"] + rng.normal(0.0, sigma, T["z1f"].shape)
    z[T["void"]] = np.nan
    steep, _ = B.steep_posts(z, T["void"])
    return B.block(B.face_patches(steep), 5, "any")


def part_a(sites, n_pairs=20):
    for site in sites:
        T = S29.truth(site); surf = S28.surfaces(site, T); E = S29.endpoints(site)
        pairs = E["E1"][:n_pairs]
        zc, k = surf["I30"]
        a = PL.assess(PL.raster_from_array(zc, float(k)), profile=POST, n_draws=128)
        hz = S28.layers_for(site, "I30"); shape = a.classes.shape
        vis1 = S30.visibility_fn(T["z1f"])
        sensed = {}
        for name, lay in A_CONFIGS:
            ck = chunk(f"a_{site}_{name}_{lay}")
            if os.path.exists(ck):
                continue
            t0 = time.time()
            h = np.zeros(shape) if lay == "none" else hz[lay][:shape[0], :shape[1]]
            kw = dict(visibility=vis1, margin=120, seed=SEED)
            if name.startswith("eye"):
                kw["visibility"] = S30.visibility_fn(T["z1f"], eye=float(name[3:]))
            elif name.startswith("noise"):
                sg = float(name[5:])
                if sg not in sensed:
                    sensed[sg] = noisy_face5(T, sg, site)
                kw["sensed_face5"] = sensed[sg]
            else:
                kw.update(p_detect=0.8, p_mode="observation")
            rows = [{"site": site, "variant": name, "layer": lay, **r} for r in S28.closed_loop(a, h, k, T, pairs, 20.0, **kw)]
            write(ck, rows); say(f"a {site} {name} {lay}: {time.time() - t0:.0f} s")


def part_b(sites, n_pairs=20):
    for site in sites:
        T = S29.truth(site); surf = S28.surfaces(site, T); E = S29.endpoints(site)
        pairs = E["E1"][:n_pairs]
        vis = S30.visibility_fn(T["z1f"])
        assessed = {}
        for inp, lay, w in B_CONFIGS:
            ck = chunk(f"b_{site}_{inp}_{lay}_{w}")
            if os.path.exists(ck):
                continue
            t0 = time.time()
            if inp not in assessed:
                zc, k = surf[inp]
                assessed[inp] = (PL.assess(PL.raster_from_array(zc, float(k)), profile=POST, n_draws=128), k, S28.layers_for(site, inp))
            a, k, hz = assessed[inp]
            shape = a.classes.shape
            h = hz[lay][:shape[0], :shape[1]]
            rows = [{"site": site, "input": inp, "layer": lay, "w": w, **r}
                    for r in S28.closed_loop(a, h, k, T, pairs, 20.0, w=float(w), visibility=vis, margin=120, seed=SEED)]
            write(ck, rows); say(f"b {site} {inp} {lay} w={w}: {time.time() - t0:.0f} s")


def s30_chunk(site, inp, lay):
    return os.path.join(C30, f"a_{site}_{inp}_E1_{lay}_1.csv")


# ---------------------------------------------------------------------------------------------------------------------
# (c) vehicle success for every cell of the planning table
# ---------------------------------------------------------------------------------------------------------------------
def route_rows(g, k, shape, pairs, T, labs, z5, gr, gc, p, base, keep_cells=False):
    S = [S28.BP.cell_of(q[0], k, shape) for q in pairs]; Tg = [S28.BP.cell_of(q[1], k, shape) for q in pairs]
    out, cells = [], []
    for n, (rc, (pa, pb)) in enumerate(zip(B.routes_from(g, shape[1], S, Tg), pairs)):
        row = {**base, "pair": n, "straight_m": round(float(np.hypot(*(pa - pb))), 1), "routed": rc is not None}
        if rc is not None:
            sp = S28.samples(rc, k)
            sc = S28.score(sp, T)
            ri = np.clip(sp[:, 0].astype(int), 0, T["p10"].shape[0] - 1); ci = np.clip(sp[:, 1].astype(int), 0, T["p10"].shape[1] - 1)
            feas, bad_m = S30.vehicle_score(rc, k, z5, gr, gc, p, S28.DESCENT_CUT)
            row.update({"unsafe": sc["unsafe"], "length_m": sc["length_m"], "feasible": feas, "infeasible_m": bad_m,
                        **{f"unsafe_{m}": bool(labs[m][ri, ci].any()) for m in labs}})
            cells.append({int(r_) * shape[1] + int(c_) for r_, c_ in rc})
        else:
            cells.append(set())
        out.append(row)
    return (out, cells) if keep_cells else out


def overlap(cells):
    cells = [c for c in cells if c]
    if len(cells) < 2:
        return "", ""
    from collections import Counter
    cnt = Counter(x for c in cells for x in c)
    shared = float(np.mean([np.mean([cnt[x] > 1 for x in c]) for c in cells]))
    jac = [len(a & b) / len(a | b) for i, a in enumerate(cells) for b in cells[i + 1:]]
    return round(shared, 4), round(float(np.mean(jac)), 4)


def part_c(sites):
    ch = S29.chosen_settings()
    p = POST.nominal_params()
    for site in sites:
        ck = chunk(f"c_{site}")
        if os.path.exists(ck):
            continue
        t0 = time.time()
        T = S29.truth(site); surf = S28.surfaces(site, T); E = S29.endpoints(site)
        rl = S30.robust_labels(T)
        labs = {"P300": T["p300"], "L60": rl["L60"], "H": rl["H"], "M": rl["M"]}
        z5 = B.block(T["z1f"], 5); gr, gc = np.gradient(z5, 5.0)
        rows, ov = [], []
        for inp in ("I10", "I30", "G30"):
            zc, k = surf[inp]
            a = PL.assess(PL.raster_from_array(zc, float(k)), profile=POST, n_draws=128)
            shape = a.classes.shape; nodata = a.classes == 5
            g0, _ = S28.base_graph(a, False); g1, _ = S28.base_graph(a, True)
            hz = S28.layers_for(site, inp)
            for e in [x for x, i in PLAN_COLS if i == inp]:
                for lay in PLAN_LAYERS:
                    if lay != "none" and (lay not in hz or (e, inp, lay, site) not in ch):
                        continue
                    if lay == "none":
                        g = S28.masked(g0, ~nodata)
                    else:
                        pol, prm = ch[(e, inp, lay, site)]
                        g = S29.graph_for(a, g1, hz[lay][:shape[0], :shape[1]], pol, prm, nodata)
                    base = {"site": site, "endpoints": e, "input": inp, "layer": lay}
                    rr, cells = route_rows(g, k, shape, E[e], T, labs, z5, gr, gc, p, base, keep_cells=True)
                    rows += rr
                    if lay == "none" and inp == "I30" and e == "E1":
                        sh, jc = overlap(cells)
                        ov.append({"site": site, "routes": sum(bool(c) for c in cells), "share_of_cells_shared": sh, "mean_pairwise_jaccard": jc})
        write(ck, rows); write(chunk(f"c_overlap_{site}"), ov)
        say(f"c {site}: {time.time() - t0:.0f} s")


# ---------------------------------------------------------------------------------------------------------------------
# (e) AW3D30 and FABDEM
# ---------------------------------------------------------------------------------------------------------------------
PRODUCTS = {"A30": "aw3d30", "F30": "fabdem"}


def product_grids():
    from pyproj import Transformer
    import fetch_benchmark_extra as FX
    c25 = np.load(BD.CACHE)
    out = {}
    for s in SITES:
        _, win, _ = BD.SITES[s]
        _, epsg, _ = FX.site_geometry(s)
        shape30 = c25[f"{s}|G30|z"].shape
        rr, cc = np.indices(shape30)
        Ee = win[0] + (cc + 0.5) * 30.0; Nn = win[3] - (rr + 0.5) * 30.0
        lon, lat = Transformer.from_crs(epsg, 4326, always_xy=True).transform(Ee, Nn)
        for pn, folder in PRODUCTS.items():
            r = PL.read_raster(os.path.join(EXTRA, folder, f"{s}.tif"))
            g = B.sample_geographic(r, lon, lat)
            out[(s, pn)] = (B.fill_nearest(g), float(np.isnan(g).mean()))
    return out


def part_e(sites):
    D = {s: dict(np.load(os.path.join(L27, f"{s}.npz"))) for s in SITES}
    G = product_grids()
    Y = {s: D[s]["any30"] for s in SITES}
    det, bic, meta = [], {}, []
    for pn in PRODUCTS:
        Fz, ys = {}, {}
        for s in SITES:
            z, void = G[(s, pn)]
            nr, nc = min(z.shape[0], Y[s].shape[0]), min(z.shape[1], Y[s].shape[1])
            sc = S27.unsup_scores(z, 30.0)
            for m in ("SLOPE", "BICUBIC", "DET"):
                det.append(S27.metric_row(s, pn, m, sc[m][:nr, :nc], Y[s][:nr, :nc], "L-ANY"))
            bic[(s, pn)] = sc["BICUBIC"][:nr, :nc]
            Fz[s] = B.feature_stack(z, 30.0)[:nr, :nc]; ys[s] = Y[s][:nr, :nc]
            meta.append({"site": s, "product": pn, "void_share": round(void, 4), "integer_valued": bool(np.allclose(z, np.round(z)))})
        gbm = S27.loso_gbm(Fz, ys)
        for s in SITES:
            det.append(S27.metric_row(s, pn, "GBM", gbm[s], ys[s], "L-ANY"))
    for r in det:
        r["auc"] = float(r["auc"]); r["ap"] = float(r["ap"])
    write(os.path.join(OUT, "e_products_detection_by_site.csv"), det)
    write(os.path.join(OUT, "e_products_detection.csv"), S27.macro(det))
    write(os.path.join(OUT, "e_products_meta.csv"), meta)
    p = POST.nominal_params()
    for pn in PRODUCTS:
        cal = S27.loso_platt({s: bic[(s, pn)] for s in SITES}, {s: Y[s][:bic[(s, pn)].shape[0], :bic[(s, pn)].shape[1]] for s in SITES})
        for site in sites:
            ck = chunk(f"e_{site}_{pn}")
            if os.path.exists(ck):
                continue
            T = S29.truth(site); E = S29.endpoints(site)
            z5 = B.block(T["z1f"], 5); gr, gc = np.gradient(z5, 5.0)
            z = G[(site, pn)][0]
            a = PL.assess(PL.raster_from_array(z, 30.0), profile=POST, n_draws=128)
            shape = a.classes.shape; nodata = a.classes == 5
            g0, _ = S28.base_graph(a, False); g1, _ = S28.base_graph(a, True)
            rows = route_rows(S28.masked(g0, ~nodata), 30, shape, E["E1"], T, {}, z5, gr, gc, p, {"site": site, "input": pn, "layer": "none", "w": 0})
            h = np.zeros(shape); hh = cal[site]; h[:hh.shape[0], :hh.shape[1]] = hh[:shape[0], :shape[1]]
            for w in W10:
                rows += route_rows(S29.graph_for(a, g1, h, "risk_weighted", w, nodata), 30, shape, E["E1"], T, {}, z5, gr, gc, p,
                                   {"site": site, "input": pn, "layer": "BICUBIC-cal", "w": w})
            write(ck, rows); say(f"e {site} {pn}")


# ---------------------------------------------------------------------------------------------------------------------
# (f) U-Net on I30
# ---------------------------------------------------------------------------------------------------------------------
def unet_channels(z):
    return np.stack([(z - uniform_filter(z, 7, mode="nearest")) / 30.0, B.slope_tan(z, 30.0),
                     B.bicubic_max_slope(z, 30)[:z.shape[0], :z.shape[1]] / 45.0]).astype(np.float32)


def unet():
    import torch, torch.nn as nn

    def block(ci, co):
        return nn.Sequential(nn.Conv2d(ci, co, 3, padding=1, padding_mode="reflect"), nn.BatchNorm2d(co), nn.ReLU(),
                             nn.Conv2d(co, co, 3, padding=1, padding_mode="reflect"), nn.BatchNorm2d(co), nn.ReLU())

    class U(nn.Module):
        def __init__(self):
            super().__init__()
            self.e1, self.e2, self.b = block(3, 32), block(32, 64), block(64, 128)
            self.u2, self.d2 = nn.ConvTranspose2d(128, 64, 2, 2), block(128, 64)
            self.u1, self.d1 = nn.ConvTranspose2d(64, 32, 2, 2), block(64, 32)
            self.o = nn.Conv2d(32, 1, 1); self.pool = nn.MaxPool2d(2)

        def forward(self, x):
            a = self.e1(x); b = self.e2(self.pool(a)); c = self.b(self.pool(b))
            d = self.d2(torch.cat([self.u2(c), b], 1))
            return self.o(self.d1(torch.cat([self.u1(d), a], 1)))
    return U()


def unet_predict(m, x):
    import torch
    m.eval()
    H, W = x.shape[1:]
    ph, pw = (-H) % 4, (-W) % 4
    xp = np.pad(x, ((0, 0), (0, ph), (0, pw)), mode="reflect")
    with torch.no_grad():
        out = torch.sigmoid(m(torch.from_numpy(xp[None]))).numpy()[0, 0][:H, :W]
    m.train()
    return out


def unet_train(train, steps, val=None, every=500, patience=4, crop=32, seed=0):
    import torch
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    m = unet(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); lossf = torch.nn.BCEWithLogitsLoss()
    sizes = np.array([y.size for _, y in train], float); pp = sizes / sizes.sum()
    best, best_step, best_state, bad = -1.0, 0, None, 0
    for step in range(1, steps + 1):
        xs, ys = [], []
        for _ in range(16):
            x, y = train[rng.choice(len(train), p=pp)]
            r = rng.integers(0, y.shape[0] - crop + 1); c = rng.integers(0, y.shape[1] - crop + 1)
            xb, yb = x[:, r:r + crop, c:c + crop], y[r:r + crop, c:c + crop]
            q = rng.integers(0, 4); xb, yb = np.rot90(xb, q, axes=(1, 2)), np.rot90(yb, q)
            if rng.random() < 0.5:
                xb, yb = xb[:, :, ::-1], yb[:, ::-1]
            xs.append(np.ascontiguousarray(xb)); ys.append(np.ascontiguousarray(yb))
        opt.zero_grad()
        loss = lossf(m(torch.from_numpy(np.stack(xs))), torch.from_numpy(np.stack(ys).astype(np.float32))[:, None])
        loss.backward(); opt.step()
        if val is not None and step % every == 0:
            auc = B.auc(unet_predict(m, val[0]).ravel(), val[1].ravel())
            if auc > best + 1e-6:
                best, best_step, bad = auc, step, 0
                best_state = {k_: v.clone() for k_, v in m.state_dict().items()}
            else:
                bad += 1
                if bad >= patience:
                    break
    if val is not None:
        m.load_state_dict(best_state)
    return m, best_step, best


def part_f(sites):
    import torch
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "1")))
    D = {s: dict(np.load(os.path.join(L27, f"{s}.npz"))) for s in SITES}
    data = {}
    for s in SITES:
        z = D[s]["z30"].astype(float); y = D[s]["any30"]
        nr, nc = min(z.shape[0], y.shape[0]), min(z.shape[1], y.shape[1])
        data[s] = (unet_channels(z[:nr, :nc]), y[:nr, :nc].astype(bool))
    os.makedirs(CDIR, exist_ok=True)
    for held in SITES:
        npy = os.path.join(CDIR, f"UNET_{held}.npy")
        if os.path.exists(npy):
            continue
        t0 = time.time()
        trs = [s for s in SITES if s != held]
        vs = SITES[(SITES.index(held) + 1) % len(SITES)]
        _, n_best, v_auc = unet_train([data[s] for s in trs if s != vs], 6000, val=data[vs])   # cap amended from 12000 (register note)
        m, _, _ = unet_train([data[s] for s in trs], max(n_best, 500))
        np.save(npy, unet_predict(m, data[held][0]).astype(np.float32))
        json.dump({"validation_site": vs, "steps": n_best, "validation_auc": round(float(v_auc), 4)}, open(npy + ".json", "w"))
        say(f"f UNET held out {held}: validation {vs} AUC {v_auc:.3f} at {n_best} steps; {time.time() - t0:.0f} s")
    det = []
    for s in SITES:
        det.append(S27.metric_row(s, "I30", "UNET", np.load(os.path.join(CDIR, f"UNET_{s}.npy")), data[s][1], "L-ANY",
                                  **json.load(open(os.path.join(CDIR, f"UNET_{s}.npy.json")))))
    for r in det:
        r["auc"] = float(r["auc"]); r["ap"] = float(r["ap"])
    write(os.path.join(OUT, "f_unet_detection_by_site.csv"), det)
    write(os.path.join(OUT, "f_unet_detection.csv"), S27.macro(det))
    p = POST.nominal_params()
    for site in sites:
        ck = chunk(f"f_{site}")
        if os.path.exists(ck):
            continue
        T = S29.truth(site); surf = S28.surfaces(site, T); E = S29.endpoints(site)
        z5 = B.block(T["z1f"], 5); gr, gc = np.gradient(z5, 5.0)
        zc, k = surf["I30"]
        a = PL.assess(PL.raster_from_array(zc, float(k)), profile=POST, n_draws=128)
        shape = a.classes.shape; nodata = a.classes == 5
        g1, _ = S28.base_graph(a, True)
        h = np.zeros(shape); hh = np.load(os.path.join(CDIR, f"UNET_{site}.npy")); h[:hh.shape[0], :hh.shape[1]] = hh[:shape[0], :shape[1]]
        rows = []
        for e in ("E1", "E2"):
            for w in W10:
                rows += route_rows(S29.graph_for(a, g1, h, "risk_weighted", w, nodata), k, shape, E[e], T, {}, z5, gr, gc, p,
                                   {"site": site, "endpoints": e, "input": "I30", "layer": "UNET", "w": w})
        write(ck, rows); say(f"f plan {site}")


# ---------------------------------------------------------------------------------------------------------------------
# (d) site level inference and summaries
# ---------------------------------------------------------------------------------------------------------------------
def site_level(per_site_diffs):
    d = np.asarray(per_site_diffs, float)
    m = float(d.mean())
    if len(d) < 2:
        return m, "", "", ""
    half = float(SS.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d)))
    return m, m - half, m + half, S28.sign_flip_p(d)


def cl_rows(rows, key=lambda r: True):
    return {(r["site"], int(r["pair"])): float(r["success"] == "True") for r in rows if key(r)}


def cl_summary(label, mine, base):
    keys = [k_ for k_ in base if k_ in mine]
    n = len(keys)
    per = [np.mean([mine[k_] - base[k_] for k_ in keys if k_[0] == s]) for s in SITES if any(k_[0] == s for k_ in keys)]
    m, lo, hi, p = site_level(per) if per else ("", "", "", "")
    return {**label, "pairs": n, "success": round(float(np.mean([mine[k_] for k_ in keys])), 4) if n else "",
            "base_success": round(float(np.mean([base[k_] for k_ in keys])), 4) if n else "",
            "diff": round(m, 4) if per else "", "site_lo": round(lo, 4) if lo != "" else "", "site_hi": round(hi, 4) if hi != "" else "",
            "sign_flip_p": round(p, 4) if p != "" else "", "sites_positive": int(sum(x > 0 for x in per))}


def summary_a():
    out = []
    ref = {}
    for site in SITES:
        for lay in P4:
            pth = s30_chunk(site, "I30", lay)
            if os.path.exists(pth):
                ref.setdefault(lay, []).extend(read(pth))
    base0 = cl_rows(ref.get("none", []))
    for lay in P4:
        out.append(cl_summary({"variant": "registered eye 1 m", "layer": lay}, cl_rows(ref.get(lay, [])), base0))
    for p08 in ("none", "GBM", "FACEMAP"):
        rows = [r for s in SITES for r in (read(os.path.join(C30, f"a_{s}_I30_E1_{p08}_0.8.csv")) if os.path.exists(os.path.join(C30, f"a_{s}_I30_E1_{p08}_0.8.csv")) else [])]
        b08 = [r for s in SITES for r in (read(os.path.join(C30, f"a_{s}_I30_E1_none_0.8.csv")) if os.path.exists(os.path.join(C30, f"a_{s}_I30_E1_none_0.8.csv")) else [])]
        out.append(cl_summary({"variant": "stage 30 p 0.8 once per pair", "layer": p08}, cl_rows(rows), cl_rows(b08)))
    for name in sorted({n for n, _ in A_CONFIGS}):
        rows = [r for s in SITES for lay in P4 if os.path.exists(chunk(f"a_{s}_{name}_{lay}")) for r in read(chunk(f"a_{s}_{name}_{lay}"))]
        base = cl_rows([r for r in rows if r["layer"] == "none"])
        for lay in sorted({r["layer"] for r in rows}, key=P4.index):
            rr = [r for r in rows if r["layer"] == lay]
            row = cl_summary({"variant": name, "layer": lay}, cl_rows(rr), base)
            row.update({"unsafe": round(float(np.mean([r["unsafe"] == "True" for r in rr])), 4),
                        "gave_up": round(float(np.mean([r["status"] == "gave_up" for r in rr])), 4),
                        "stuck": round(float(np.mean([r["status"] == "stuck" for r in rr])), 4),
                        "replans": round(float(np.mean([float(r["replans"]) for r in rr])), 2)})
            out.append(row)
    write(os.path.join(OUT, "a_sensor_variants.csv"), out)


def summary_b():
    out = []
    for inp, lays in (("I30", ("BICUBIC-cal", "GBM", "FACEMAP")), ("I10", ("BICUBIC-cal", "FACEMAP"))):
        base = cl_rows([r for s in SITES if os.path.exists(s30_chunk(s, inp, "none")) for r in read(s30_chunk(s, inp, "none"))])
        for lay in lays:
            by = {}
            for s in SITES:
                if os.path.exists(s30_chunk(s, inp, lay)):
                    by[(s, 5)] = read(s30_chunk(s, inp, lay))
                for w in (1, 20, 100):
                    if os.path.exists(chunk(f"b_{s}_{inp}_{lay}_{w}")):
                        by[(s, w)] = read(chunk(f"b_{s}_{inp}_{lay}_{w}"))
            if not by:
                continue
            succ = {k_: [float(r["success"] == "True") for r in v] for k_, v in by.items()}
            _, choice = S29.held_out(succ, sorted({w for _, w in succ}))
            chosen = [r for s in SITES if (s, choice[s]) in by for r in by[(s, choice[s])]]
            row = cl_summary({"input": inp, "layer": lay}, cl_rows(chosen), base)
            row["chosen"] = " ".join(f"{s}:{choice[s]:g}" for s in SITES)
            for w in (1, 5, 20, 100):
                rr = [r for s in SITES for r in by.get((s, w), [])]
                row[f"success_w{w}"] = round(float(np.mean([r["success"] == "True" for r in rr])), 4) if rr else ""
            out.append(row)
    write(os.path.join(OUT, "b_closed_loop_held_out_weight.csv"), out)


def summary_c():
    rows = [r for s in SITES if os.path.exists(chunk(f"c_{s}")) for r in read(chunk(f"c_{s}"))]
    if not rows:
        return
    out, persite = [], []
    for e, inp in PLAN_COLS:
        base = [r for r in rows if r["endpoints"] == e and r["input"] == inp and r["layer"] == "none"]
        bm = {(r["site"], r["pair"]): r for r in base}
        for lay in PLAN_LAYERS:
            rr = [r for r in rows if r["endpoints"] == e and r["input"] == inp and r["layer"] == lay]
            if not rr:
                continue
            row = {"endpoints": e, "input": inp, "layer": lay, "pairs": len(rr),
                   "mission_success": round(float(np.mean([ok_(r) for r in rr])), 4),
                   "vehicle_success": round(float(np.mean([feas_(r) for r in rr])), 4),
                   "feasible_share_of_successes": round(sum(feas_(r) for r in rr) / max(sum(ok_(r) for r in rr), 1), 4)}
            for m in ("P300", "L60", "H", "M"):
                row[f"success_{m}"] = round(float(np.mean([ok_(r, f"unsafe_{m}") for r in rr])), 4)
            for end, fn in (("mission", ok_), ("vehicle", feas_)):
                per = [np.mean([float(fn(r)) - float(fn(bm[(r["site"], r["pair"])])) for r in rr if r["site"] == s]) for s in SITES
                       if any(r["site"] == s for r in rr)]
                m_, lo, hi, p = site_level(per)
                row.update({f"{end}_diff": round(m_, 4), f"{end}_site_lo": round(lo, 4) if lo != "" else "",
                            f"{end}_site_hi": round(hi, 4) if hi != "" else "", f"{end}_sign_flip_p": round(p, 4) if p != "" else "",
                            f"{end}_sites_positive": int(sum(x > 0 for x in per))})
            out.append(row)
            for s in SITES:
                rs = [r for r in rr if r["site"] == s]
                if rs:
                    persite.append({"endpoints": e, "input": inp, "layer": lay, "site": s,
                                    "mission_success": round(float(np.mean([ok_(r) for r in rs])), 4),
                                    "vehicle_success": round(float(np.mean([feas_(r) for r in rs])), 4)})
    write(os.path.join(OUT, "c_vehicle_all_cells.csv"), out)
    write(os.path.join(OUT, "c_vehicle_by_site.csv"), persite)
    # pair distance tertiles (pooled edges per endpoint set)
    tert = []
    for e, inp in PLAN_COLS:
        rr0 = [r for r in rows if r["endpoints"] == e and r["input"] == inp and r["layer"] == "none"]
        if not rr0:
            continue
        edges = np.percentile([float(r["straight_m"]) for r in rr0], [100 / 3, 200 / 3])
        for lay in ("none", "BICUBIC-cal", "FACEMAP"):
            rr = [r for r in rows if r["endpoints"] == e and r["input"] == inp and r["layer"] == lay]
            for t, (lo, hi) in enumerate(((0, edges[0]), (edges[0], edges[1]), (edges[1], 1e12))):
                rt = [r for r in rr if lo <= float(r["straight_m"]) < hi]
                if rt:
                    tert.append({"endpoints": e, "input": inp, "layer": lay, "tertile": t + 1, "from_m": round(lo), "to_m": round(hi) if hi < 1e11 else "",
                                 "pairs": len(rt), "mission_success": round(float(np.mean([ok_(r) for r in rt])), 4),
                                 "vehicle_success": round(float(np.mean([feas_(r) for r in rt])), 4)})
    write(os.path.join(OUT, "c_by_pair_distance.csv"), tert)
    ov = [r for s in SITES if os.path.exists(chunk(f"c_overlap_{s}")) for r in read(chunk(f"c_overlap_{s}"))]
    write(os.path.join(OUT, "c_route_overlap.csv"), ov)


def summary_d():
    """Detection intervals for SR and DEM+S2 on I30 (per site block bootstrap, 300 m blocks)."""
    L = np.load(os.path.join(L27, "layers_L-ANY.npz")); I = np.load(os.path.join(L27, "layers_imagery_I30.npz"))
    D = {s: dict(np.load(os.path.join(L27, f"{s}.npz"))) for s in SITES}
    out = []
    for s in SITES:
        sr = np.load(os.path.join(L27, f"SR_{s}_I30.npy")).astype(float)
        bic = L[f"{s}|I30|BICUBIC-cal"].astype(float); ds2 = I[f"{s}|DEM+S2"].astype(float)
        y = D[s]["any30"]
        nr = min(y.shape[0], sr.shape[0], bic.shape[0], ds2.shape[0]); nc = min(y.shape[1], sr.shape[1], bic.shape[1], ds2.shape[1])
        sc = {"BICUBIC": bic[:nr, :nc], "SR": sr[:nr, :nc], "DEM+S2": ds2[:nr, :nc]}
        ci, diffs = S27.boot_auc(sc, y[:nr, :nc], 30, ref_methods=("BICUBIC",), n_boot=1000, block_m=300.0)
        for m in ("SR", "DEM+S2"):
            dd = next(d for d in diffs if d["method"] == m)
            out.append({"site": s, "method": m, "auc": round(B.auc(sc[m].ravel(), y[:nr, :nc].ravel()), 4),
                        "lo": round(float(ci[m][0]), 4), "hi": round(float(ci[m][1]), 4),
                        "bicubic_auc": round(B.auc(sc["BICUBIC"].ravel(), y[:nr, :nc].ravel()), 4),
                        "diff_vs_bicubic": dd["auc_difference"], "diff_lo": dd["lo"], "diff_hi": dd["hi"]})
    write(os.path.join(OUT, "d_detection_intervals_sr_dems2.csv"), out)
    # site level inference for the stage 30 line of sight closed loop
    rows = []
    a30 = {}
    for s in SITES:
        for inp, e, lay, pd in S30.A_CONFIGS:
            pth = os.path.join(C30, f"a_{s}_{inp}_{e}_{lay}_{pd:g}.csv")
            if os.path.exists(pth):
                a30.setdefault((inp, e, pd, lay), []).extend(read(pth))
    for (inp, e, pd, lay), rr in sorted(a30.items()):
        if lay == "none" or (inp, e, pd, "none") not in a30:
            continue
        rows.append(cl_summary({"input": inp, "endpoints": e, "p_detect": pd, "layer": lay}, cl_rows(rr), cl_rows(a30[(inp, e, pd, "none")])))
    write(os.path.join(OUT, "d_site_level_line_of_sight.csv"), rows)


def summary_e():
    out = []
    for pn in PRODUCTS:
        rows = [r for s in SITES if os.path.exists(chunk(f"e_{s}_{pn}")) for r in read(chunk(f"e_{s}_{pn}"))]
        if not rows:
            continue
        nv = [r for r in rows if r["layer"] == "none"]
        out.append({"input": pn, "layer": "none", "mission_success": round(float(np.mean([ok_(r) for r in nv])), 4),
                    "vehicle_success": round(float(np.mean([feas_(r) for r in nv])), 4), "chosen": ""})
        by = {}
        for r in rows:
            if r["layer"] == "BICUBIC-cal":
                by.setdefault((r["site"], float(r["w"])), []).append(r)
        succ = {k_: [float(ok_(r)) for r in v] for k_, v in by.items()}
        m, choice = S29.held_out(succ, sorted({w for _, w in succ}))
        ch = [r for s in SITES for r in by[(s, choice[s])]]
        out.append({"input": pn, "layer": "BICUBIC-cal", "mission_success": round(m, 4),
                    "vehicle_success": round(float(np.mean([feas_(r) for r in ch])), 4), "chosen": " ".join(f"{s}:{choice[s]:g}" for s in SITES)})
    write(os.path.join(OUT, "e_products_planning.csv"), out)


def summary_f():
    rows = [r for s in SITES if os.path.exists(chunk(f"f_{s}")) for r in read(chunk(f"f_{s}"))]
    if not rows:
        return
    base = {}
    for s in SITES:
        if os.path.exists(chunk(f"c_{s}")):
            for r in read(chunk(f"c_{s}")):
                if r["input"] == "I30" and r["layer"] == "none":
                    base[(r["endpoints"], r["site"], r["pair"])] = r
    out = []
    for e in ("E1", "E2"):
        by = {}
        for r in rows:
            if r["endpoints"] == e:
                by.setdefault((r["site"], float(r["w"])), []).append(r)
        succ = {k_: [float(ok_(r)) for r in v] for k_, v in by.items()}
        m, choice = S29.held_out(succ, sorted({w for _, w in succ}))
        ch = [r for s in SITES for r in by[(s, choice[s])]]
        per = [np.mean([float(ok_(r)) - float(ok_(base[(e, s, r["pair"])])) for r in ch if r["site"] == s]) for s in SITES]
        m_, lo, hi, p = site_level(per)
        out.append({"endpoints": e, "layer": "UNET", "mission_success": round(m, 4), "vehicle_success": round(float(np.mean([feas_(r) for r in ch])), 4),
                    "slip_only": round(float(np.mean([ok_(base[(e, r['site'], r['pair'])]) for r in ch])), 4),
                    "diff": round(m_, 4), "site_lo": round(lo, 4), "site_hi": round(hi, 4), "sign_flip_p": round(p, 4),
                    "chosen": " ".join(f"{s}:{choice[s]:g}" for s in SITES)})
    write(os.path.join(OUT, "f_unet_planning.csv"), out)


def summary_g():
    # (1) edge of the grid
    out = []
    for r in read(os.path.join(ROOT, "results", "benchmark", "stage28", "A_held_out.csv")):
        if r["profile"] != "published-posterior" or r["policies"] != "conservative+risk_weighted":
            continue
        toks = [t.split(":")[1] for t in r["chosen"].split()]
        edge = sum(t in ("risk1", "risk100", "cons0.02", "cons0.9") for t in toks)
        out.append({"source": "stage 28 registered grid", "endpoints": r["endpoints"], "input": r["input"], "layer": r["layer"],
                    "sites_at_edge": edge, "chosen": r["chosen"]})
    for r in read(os.path.join(ROOT, "results", "benchmark", "stage30", "d_extended_weight_grid.csv")):
        toks = [t.split(":")[1] for t in r["chosen"].split()]
        out.append({"source": "stage 30 weight grid to 1000", "endpoints": r["endpoints"], "input": r["input"], "layer": r["layer"],
                    "sites_at_edge": sum(float(t) in (1.0, 1000.0) for t in toks), "chosen": r["chosen"]})
    write(os.path.join(OUT, "g_grid_edges.csv"), out)
    # (2) sensitivity vehicle
    sv = []
    for r in read(os.path.join(ROOT, "results", "benchmark", "stage28", "A_held_out.csv")):
        if r["policies"] == "conservative+risk_weighted":
            sv.append({k_: r[k_] for k_ in ("profile", "endpoints", "input", "layer", "mission_success", "naive_success", "difference", "diff_lo", "diff_hi")})
    for r in read(os.path.join(ROOT, "results", "benchmark", "stage28", "A_naive.csv")):
        sv.append({"profile": r["profile"], "endpoints": r["endpoints"], "input": r["input"], "layer": "none", "mission_success": r["mission_success"]})
    write(os.path.join(OUT, "g_sensitivity_vehicle.csv"), sv)
    # (3) dates
    man = json.load(open(os.path.join(EXTRA, "MANIFEST.json")))
    lid = {r["site"]: r for r in read(os.path.join(ROOT, "results", "benchmark", "stage25", "sites.csv"))} \
        if os.path.exists(os.path.join(ROOT, "results", "benchmark", "stage25", "sites.csv")) else {}
    import fetch_benchmark_extra as FX
    dt = []
    for s in SITES:
        dt.append({"site": s, "lidar_year": FX.LIDAR_YEAR[s], "s2_date": str(man.get(f"S2|{s}", {}).get("date", ""))[:10],
                   "naip_year": man.get(f"NAIP|{s}", {}).get("year", ""), "lidar_file": BD.SITES[s][0], **({"lidar_meta": json.dumps(lid[s])} if s in lid else {})})
    write(os.path.join(OUT, "g_dates.csv"), dt)


def main():
    global LOG
    os.makedirs(OUT, exist_ok=True); os.makedirs(CDIR, exist_ok=True)
    args = sys.argv[1:]
    sites = SITES
    if args and "," in args[-1] or (args and args[-1] in SITES):
        sites = args[-1].split(","); args = args[:-1]
    LOG = open(os.path.join(OUT, "run_log.txt"), "a")
    say(f"stage 31 {' '.join(args)} on {','.join(sites)} started {time.strftime('%Y-%m-%d %H:%M:%S')}")
    for part in args:
        t0 = time.time()
        if part == "summary":
            summary_a(); summary_b(); summary_c(); summary_d(); summary_e(); summary_f(); summary_g()
        else:
            {"a": part_a, "b": part_b, "c": part_c, "e": part_e, "f": part_f}[part](sites)
        say(f"part {part} done in {time.time() - t0:.0f} s ({time.strftime('%H:%M:%S')})")


if __name__ == "__main__":
    main()
