#!/usr/bin/env python3
"""Stage 27 (docs/PREDICTIONS.md): detection against the planning target, across resolutions, products and imagery.

    PYTHONPATH=src python3 scripts/benchmark_stage27.py prepare        # once: per site cache from lidar, products, imagery
    PYTHONPATH=src python3 scripts/benchmark_stage27.py A B C D E F G H I

Parts follow the registered design: A matched label (and 10 m scores aggregated to 30 m), B label sensitivity,
C resolution sweep and patch scaling, D real products on their own grids, E imagery, F learned super resolution,
G learned model variants, H reference rules, I correlogram and site level tests.
Inputs: data/raw/lidar, data/raw/glo30_us, data/raw/extra (scripts/fetch_benchmark_extra.py), data/cache/benchmark_scores.npz.
Outputs: results/benchmark/stage27/*.csv, run_log.txt; cache data/cache/stage27/.
SIMULATED BY ME (every detector) scored against PUBLISHED elevation data and imagery. Deterministic.
"""
from __future__ import annotations
import csv, itertools, json, os, sys, time
import numpy as np
from scipy.ndimage import (uniform_filter, maximum_filter, minimum_filter, zoom, label as nd_label)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dunerover import benchmark as B, planner as PL, subgrid as SG  # noqa: E402
from dunerover.terrain import horn_gradient  # noqa: E402
import benchmark_detection as BD  # noqa: E402

OUT = os.path.join(ROOT, "results", "benchmark", "stage27")
CDIR = os.path.join(ROOT, "data", "cache", "stage27")
EXTRA = os.path.join(ROOT, "data", "raw", "extra")
SEED = 20261028
N_BOOT = 1000
BLOCK_M = 300.0
POSTINGS = (2, 5, 10, 15, 20, 30, 60)
CAP_ROWS = 400_000
SITES = list(BD.SITES)
UNSUP = ("DET", "SLOPE", "TRI", "ROUGH", "BICUBIC")
LOG = None


def say(m):
    print(m, flush=True)
    if LOG:
        LOG.write(m + "\n"); LOG.flush()


def write(name, rows):
    if not rows:
        return
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(os.path.join(OUT, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)


def done_rows(name):
    """Rows of a finished chunk (checkpoint), or None."""
    p = os.path.join(CDIR, "chunks", name + ".csv")
    return list(csv.DictReader(open(p))) if os.path.exists(p) else None


def save_rows(name, rows):
    os.makedirs(os.path.join(CDIR, "chunks"), exist_ok=True)
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(os.path.join(CDIR, "chunks", name + ".csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)


def numeric(rows):
    for r in rows:
        for k in ("auc", "ap", "prevalence", "posting_m"):
            if r.get(k, "") not in ("", None):
                r[k] = float(r[k])
    return rows


def cpath(site):
    return os.path.join(CDIR, f"{site}.npz")


# ---------------------------------------------------------------------------------------------------------------------
# features and scores
# ---------------------------------------------------------------------------------------------------------------------
def aspect_rule(z, dx, dy):
    ge, gn = horn_gradient(z, dx, dy)
    s = np.degrees(np.arctan(np.hypot(ge, gn)))
    a = np.arctan2(-ge, -gn)
    w = ge ** 2 + gn ** 2
    a0 = np.arctan2((w * np.sin(a)).sum(), (w * np.cos(a)).sum())
    return s * (1 + np.cos(a - a0)) / 2


def bicubic_aniso(z, dx, dy):
    """Steepest slope of the surface interpolated with a cubic spline to about one metre, per cell (any spacing)."""
    ky, kx = max(1, int(round(dy))), max(1, int(round(dx)))
    zf = zoom(z, (ky, kx), order=3, mode="nearest", grid_mode=True)
    ge, gn = horn_gradient(zf, dx / kx, dy / ky)
    s = np.degrees(np.arctan(np.hypot(ge, gn)))
    nr, nc = z.shape
    return s[:nr * ky, :nc * kx].reshape(nr, ky, nc, kx).max(axis=(1, 3))


def unsup_scores(z, dx, dy=None):
    dy = dx if dy is None else dy
    d = float(np.sqrt(dx * dy))
    ge, gn = horn_gradient(z, dx, dy)
    det = PL.face_detector(round(d, 1)).predict(SG.features_2d(z, float(dx), float(dy)))
    return {"DET": det, "SLOPE": np.degrees(np.arctan(np.hypot(ge, gn))), "TRI": B.tri(z, d), "ROUGH": B.plane_roughness(z, d, 3),
            "BICUBIC": bicubic_aniso(z, dx, dy), "ASPECT": aspect_rule(z, dx, dy)}


def extra_features(z, d, bic):
    s = B.slope_tan(z, d)
    return np.stack([bic, B.tpi(z, d, 31), B.relief(z, d, 15), B.slope_tan(uniform_filter(z, 3, mode="nearest"), d),
                     maximum_filter(s, 5, mode="nearest")], axis=-1)


def loso_gbm(F_by_site, y_by_site, params=None, cap=None, seed=0):
    """Leave one site out gradient boosting. Returns {site: probability grid}."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    params = params or B.GBM_PARAMS
    out = {}
    for held in SITES:
        X = np.concatenate([F_by_site[s].reshape(-1, F_by_site[s].shape[-1]) for s in SITES if s != held])
        y = np.concatenate([y_by_site[s].ravel() for s in SITES if s != held])
        if cap and len(y) > cap:
            idx = np.random.default_rng(seed).choice(len(y), cap, replace=False)
            X, y = X[idx], y[idx]
        m = HistGradientBoostingClassifier(**params).fit(X, y.astype(bool))
        F = F_by_site[held]
        out[held] = m.predict_proba(F.reshape(-1, F.shape[-1]))[:, 1].reshape(F.shape[:-1])
    return out


def loso_platt(score_by_site, y_by_site, transform="identity"):
    out = {}
    for held in SITES:
        s = np.concatenate([score_by_site[x].ravel() for x in SITES if x != held])
        y = np.concatenate([y_by_site[x].ravel() for x in SITES if x != held])
        out[held] = B.Platt(transform).fit(s, y).predict(score_by_site[held])
    return out


def loso_cnn(z_by_site, y_by_site, d, crop, steps=None):
    from dunerover import benchmark_cnn as C
    out = {}
    for held in SITES:
        t0 = time.time()
        tr = [(C.channels(z_by_site[s], float(d)), y_by_site[s]) for s in SITES if s != held]
        net = C.fit(tr, crop, steps=steps or C.STEPS)
        out[held] = C.predict(net, C.channels(z_by_site[held], float(d)))
        say(f"  CNN held out {held}: {time.time() - t0:.0f} s")
    return out


def metric_row(site, inp, method, score, y, label, **extra):
    y = np.asarray(y, bool).ravel(); s = np.asarray(score, float).ravel()
    return {"site": site, "input": inp, "label": label, "method": method, "cells": int(y.size), "prevalence": round(float(y.mean()), 4),
            "auc": round(B.auc(s, y), 4), "ap": round(B.average_precision(s, y), 4), **extra}


def macro(rows, keys=("input", "label", "method"), vals=("auc", "ap")):
    out = []
    for k in sorted({tuple(r[x] for x in keys) for r in rows}):
        rr = [r for r in rows if tuple(r[x] for x in keys) == k]
        o = dict(zip(keys, k)); o["sites"] = len(rr)
        for v in vals:
            xs = [r[v] for r in rr if r.get(v) not in ("", None) and np.isfinite(r[v])]
            o[v] = round(float(np.mean(xs)), 4) if xs else ""
        out.append(o)
    return out


def boot_auc(scores: dict, y, k, ref_methods=("BICUBIC", "DET"), n_boot=N_BOOT, block_m=BLOCK_M, seed=SEED):
    """Block bootstrap intervals for each AUC and the paired differences against the reference methods."""
    y = np.asarray(y, bool)
    ids = B.block_ids(y.shape, max(1, int(round(block_m / k))))
    ranked = {m: B.RankedScore(s, y.ravel()) for m, s in scores.items()}
    boots = {m: [] for m in scores}
    for w in B.block_bootstrap_weights(ids, n_boot, seed):
        for m in scores:
            boots[m].append(ranked[m].auc(w))
    boots = {m: np.array(v) for m, v in boots.items()}
    ci = {m: np.nanpercentile(b, [2.5, 97.5]) for m, b in boots.items()}
    diffs = []
    for ref in ref_methods:
        if ref not in scores:
            continue
        for m in scores:
            if m == ref:
                continue
            dd = boots[m] - boots[ref]
            lo, hi = np.nanpercentile(dd, [2.5, 97.5]); blo, bhi = np.nanpercentile(dd, [100 * 0.025 / 6, 100 - 100 * 0.025 / 6])
            diffs.append({"method": m, "reference": ref, "auc_difference": round(ranked[m].auc() - ranked[ref].auc(), 4),
                          "lo": round(float(lo), 4), "hi": round(float(hi), 4), "significant": bool(lo > 0 or hi < 0),
                          "lo_bonferroni6": round(float(blo), 4), "hi_bonferroni6": round(float(bhi), 4),
                          "significant_bonferroni6": bool(blo > 0 or bhi < 0)})
    return ci, diffs


def sign_flip_p(diffs):
    d = np.asarray(diffs, float)
    obs = abs(d.mean())
    stats = [abs((d * np.array(sg)).mean()) for sg in itertools.product((1, -1), repeat=len(d))]
    return float(np.mean([s >= obs - 1e-12 for s in stats]))


def holm(ps):
    ps = np.asarray(ps, float); order = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0.0
    for i, j in enumerate(order):
        run = max(run, min(1.0, (m - i) * ps[j])); adj[j] = run
    return adj


# ---------------------------------------------------------------------------------------------------------------------
# prepare: everything that needs the one metre lidar, the products or the imagery, cached per site
# ---------------------------------------------------------------------------------------------------------------------
def patch_lengths(lab, n):
    """Major axis length (4 sqrt of the largest eigenvalue of the coordinate covariance) of each labelled patch."""
    r, c = np.nonzero(lab)
    ids = lab[r, c]
    cnt = np.bincount(ids, minlength=n + 1).astype(float)
    sr = np.bincount(ids, r, n + 1); sc = np.bincount(ids, c, n + 1)
    srr = np.bincount(ids, r * r.astype(float), n + 1); scc = np.bincount(ids, c * c.astype(float), n + 1)
    src = np.bincount(ids, r * c.astype(float), n + 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        mr, mc = sr / cnt, sc / cnt
        vrr = srr / cnt - mr ** 2 + 1 / 12; vcc = scc / cnt - mc ** 2 + 1 / 12; vrc = src / cnt - mr * mc
        tr, det = vrr + vcc, vrr * vcc - vrc ** 2
        lam = tr / 2 + np.sqrt(np.maximum(tr ** 2 / 4 - det, 0))
    return 4 * np.sqrt(lam), cnt


def native_product(path, e0, n0, shape1, epsg):
    """Native grid crop of a product, and the map from each one metre post (row, col) to a native cell."""
    import rasterio
    from pyproj import Transformer
    with rasterio.open(path) as ds:
        z = ds.read(1).astype(float); t = ds.transform; nod = ds.nodata
    z[(z < -1000) | ~np.isfinite(z) | ((z == nod) if nod is not None else False)] = np.nan
    tr = Transformer.from_crs(epsg, 4326, always_xy=True)
    rr = np.arange(shape1[0]); cc = np.arange(shape1[1])
    # posts are mapped through a coarse lattice (every 25 m) and bilinear interpolation of lon and lat (exact to mm)
    step = 25
    gr = np.arange(0, shape1[0] + step, step); gc = np.arange(0, shape1[1] + step, step)
    GE, GN = np.meshgrid(e0 + gc + 0.5, n0 - gr - 0.5)
    lon, lat = tr.transform(GE, GN)
    from scipy.interpolate import RegularGridInterpolator
    f_lon = RegularGridInterpolator((gr, gc), lon); f_lat = RegularGridInterpolator((gr, gc), lat)
    out_r = np.empty(shape1, np.int32); out_c = np.empty(shape1, np.int32)
    for i0 in range(0, shape1[0], 500):
        R, Cc = np.meshgrid(rr[i0:i0 + 500], cc, indexing="ij")
        pts = np.column_stack([R.ravel(), Cc.ravel()])
        lo, la = f_lon(pts), f_lat(pts)
        col = np.floor((lo - t.c) / t.a).astype(np.int32); row = np.floor((la - t.f) / t.e).astype(np.int32)
        out_r[i0:i0 + 500] = row.reshape(R.shape); out_c[i0:i0 + 500] = col.reshape(R.shape)
    lat_c = t.f + t.e * (z.shape[0] / 2)
    from pyproj import Geod
    g = Geod(ellps="WGS84")
    lon_c = t.c + t.a * (z.shape[1] / 2)
    dx = g.inv(lon_c, lat_c, lon_c + t.a, lat_c)[2]; dy = g.inv(lon_c, lat_c, lon_c, lat_c - t.e)[2]
    return z, out_r, out_c, abs(dx), abs(dy)


def prepare():
    import tifffile, rasterio
    os.makedirs(CDIR, exist_ok=True)
    cache25 = np.load(BD.CACHE)
    man = json.load(open(os.path.join(EXTRA, "MANIFEST.json")))
    meta = {}
    for site, (fname, win, tile) in BD.SITES.items():
        t0 = time.time()
        z1, e0, n0, epsg = BD.load_lidar_window(fname, win)
        void = np.isnan(z1); z1f = B.fill_nearest(z1)
        steep, s1 = B.steep_posts(z1, void)
        lab, npatch = nd_label(steep, structure=np.ones((3, 3), int))
        sizes = np.bincount(lab.ravel()); keep = sizes >= B.MIN_POSTS; keep[0] = False
        patch = keep[lab]
        # relabel kept patches 1..n
        newid = np.zeros(len(sizes), np.int32); newid[keep] = np.arange(1, keep.sum() + 1)
        plab = newid[lab]; n = int(keep.sum())
        L, cnt = patch_lengths(plab, n)
        C = {"patch_len_m": L[1:].astype(np.float32), "patch_posts": cnt[1:].astype(np.int32)}
        for d in POSTINGS:
            C[f"z{d}"] = B.block(z1f, d).astype(np.float32)
            C[f"any{d}"] = B.block(patch, d, "any")
            # (patch, cell) pairs at this posting, for the scaling analysis
            nr, nc = C[f"z{d}"].shape
            pr, pc = np.nonzero(plab[:nr * d, :nc * d])
            pid = plab[pr, pc]
            cell = (pr // d) * nc + (pc // d)
            pair = np.unique(pid.astype(np.int64) * (nr * nc) + cell)
            C[f"pairs{d}"] = pair
        for nmin in (10, 50, 100, 300):
            C[f"cell30_n{nmin}"] = B.cell_truth(steep, 30, nmin)
        for deg in (30, 32):
            st2, _ = B.steep_posts(z1, void, lo_deg=deg)
            C[f"any30_deg{deg}"] = B.block(B.face_patches(st2), 30, "any")
        C["G30"] = cache25[f"{site}|G30|z"].astype(np.float32)
        # native products
        prods = {"R10": os.path.join(EXTRA, "3dep13", f"{site}.tif"), "N30": os.path.join(EXTRA, "nasadem", f"{site}.tif"),
                 "G30n": os.path.join(BD.RAW, "glo30_us", tile)}
        for p, path in prods.items():
            if p == "G30n":
                # crop the local GLO-30 tile to the window plus a margin on its own grid
                g30c = os.path.join(CDIR, f"{site}_glo30_crop.tif")
                if not os.path.exists(g30c):
                    from rasterio.windows import from_bounds
                    from rasterio.warp import transform_bounds
                    with rasterio.open(path) as ds:
                        bb = transform_bounds(f"EPSG:{epsg}", ds.crs, win[0], win[2], win[1], win[3], densify_pts=21)
                        w = from_bounds(bb[0] - 0.01, bb[1] - 0.01, bb[2] + 0.01, bb[3] + 0.01, ds.transform).round_offsets().round_lengths()
                        a = ds.read(1, window=w); prof = ds.profile.copy()
                        prof.update(height=a.shape[0], width=a.shape[1], transform=ds.window_transform(w), driver="GTiff")
                        for k in ("blockxsize", "blockysize", "tiled", "compress", "interleave"):
                            prof.pop(k, None)
                        with rasterio.open(g30c, "w", **prof) as dst:
                            dst.write(a, 1)
                path = g30c
            zn, pr_, pc_, dx, dy = native_product(path, e0, n0, z1.shape, epsg)
            inside = (pr_ >= 0) & (pr_ < zn.shape[0]) & (pc_ >= 0) & (pc_ < zn.shape[1])
            flat = np.where(inside, pr_ * zn.shape[1] + pc_, -1).ravel()
            ok = flat >= 0
            ncell = zn.size
            posts = np.bincount(flat[ok], minlength=ncell)
            anyp = np.bincount(flat[ok], patch.ravel()[ok].astype(float), minlength=ncell) > 0
            nv = np.bincount(flat[ok], (~void).ravel()[ok].astype(float), minlength=ncell)
            valid = (posts >= 0.9 * dx * dy) & (nv >= 0.9 * posts) & np.isfinite(zn).ravel()
            C[f"{p}_z"] = zn.astype(np.float32); C[f"{p}_any"] = anyp.reshape(zn.shape); C[f"{p}_valid"] = valid.reshape(zn.shape)
            C[f"{p}_dxdy"] = np.array([dx, dy])
            meta.setdefault(site, {})[p] = {"shape": list(zn.shape), "dx_m": round(dx, 2), "dy_m": round(dy, 2),
                                             "valid_cells": int(valid.sum()), "void_share": round(float(np.isnan(zn).mean()), 4)}
        # imagery: Sentinel-2 on the 10 m grid, NAIP on the one metre grid
        with rasterio.open(os.path.join(EXTRA, "s2", f"{site}.tif")) as ds:
            s2 = ds.read().astype(float)              # blue, green, red, nir
        nr10, nc10 = C["z10"].shape
        s2 = s2[:, :nr10, :nc10]
        bright = s2[:3].mean(0)
        ndvi = (s2[3] - s2[2]) / np.maximum(s2[3] + s2[2], 1e-6)
        gy, gx = np.gradient(bright)
        S10 = np.stack([s2[0], s2[1], s2[2], s2[3], bright, ndvi, bright - uniform_filter(bright, 3, mode="nearest"), np.hypot(gx, gy)], -1)
        S10 = np.nan_to_num(S10)
        C["S2_10"] = S10.astype(np.float32)
        k3 = 3
        nr30, nc30 = C["z30"].shape
        blk = S10[:nr30 * k3, :nc30 * k3].reshape(nr30, k3, nc30, k3, -1)
        C["S2_30"] = np.concatenate([blk.mean((1, 3)), blk.min((1, 3)), blk.max((1, 3)), blk.std((1, 3))], -1).astype(np.float32)
        with rasterio.open(os.path.join(EXTRA, "naip", f"{site}.tif")) as ds:
            na = ds.read().astype(float)
        na = na[:, :z1.shape[0], :z1.shape[1]]
        nb = na[:3].mean(0)
        med = np.nanmedian(nb)
        gy, gx = np.gradient(np.nan_to_num(nb))
        gm = np.hypot(gx, gy)
        dark = (nb < 0.7 * med).astype(float)
        for d in (10, 30):
            nr, nc = C[f"z{d}"].shape
            def blk(a):
                return a[:nr * d, :nc * d].reshape(nr, d, nc, d)
            nbb = blk(nb)
            feats = [np.nanmean(nbb, (1, 3)), np.nanstd(nbb, (1, 3)), np.nanpercentile(nbb, 10, axis=(1, 3)), np.nanpercentile(nbb, 90, axis=(1, 3))]
            feats += [np.nanmean(blk(na[b]), (1, 3)) for b in range(4)]
            feats += [blk(dark).mean((1, 3)), blk(gm).mean((1, 3))]
            C[f"NAIP_{d}"] = np.nan_to_num(np.stack(feats, -1)).astype(np.float32)
        meta.setdefault(site, {}).update({"patches": n, "patch_posts_share": round(float(patch.mean()), 4), "epsg": epsg,
                                          "s2": man.get(f"S2|{site}", {}).get("source"), "naip": man.get(f"NAIP|{site}", {}).get("source")})
        np.savez_compressed(cpath(site), **C)
        say(f"prepare {site}: {n} patches, {time.time() - t0:.0f} s; " + json.dumps({k: v for k, v in meta[site].items() if k in ('R10', 'N30', 'G30n')}))
        del z1, z1f, steep, s1, lab, plab, patch
    json.dump(meta, open(os.path.join(OUT, "prepare_meta.json"), "w"), indent=1)


def load_all():
    return {s: dict(np.load(cpath(s))) for s in SITES}


# ---------------------------------------------------------------------------------------------------------------------
# parts
# ---------------------------------------------------------------------------------------------------------------------
def part_A(D):
    """Matched label on I10, I30, G30 with intervals; 10 m scores aggregated to 30 m."""
    rows, diffs = [], []
    store = {}
    for inp, k in (("I10", 10), ("I30", 30), ("G30", 30)):
        zs = {s: (D[s]["z10"] if inp == "I10" else D[s]["z30"] if inp == "I30" else B.fill_nearest(D[s]["G30"].astype(float))).astype(float) for s in SITES}
        ys = {s: D[s][f"any{k}"][:zs[s].shape[0], :zs[s].shape[1]] for s in SITES}
        sc = {s: unsup_scores(zs[s], float(k)) for s in SITES}
        F = {s: B.feature_stack(zs[s], float(k)) for s in SITES}
        t0 = time.time()
        gbm = loso_gbm(F, ys)
        say(f"A {inp}: GBM {time.time() - t0:.0f} s")
        cnn = loso_cnn(zs, ys, k, 64 if k == 10 else 32)
        cal = {m: loso_platt({s: sc[s][m] for s in SITES}, ys, "logit" if m == "DET" else "identity") for m in ("DET", "SLOPE", "BICUBIC")}
        for s in SITES:
            scores = {m: sc[s][m] for m in UNSUP}
            scores["GBM"] = gbm[s]; scores["CNN"] = cnn[s]
            ci, dd = boot_auc(scores, ys[s], k)
            for m, v in scores.items():
                rows.append(metric_row(s, inp, m, v, ys[s], "L-ANY", auc_lo=round(float(ci[m][0]), 4), auc_hi=round(float(ci[m][1]), 4)))
            for x in dd:
                diffs.append({"site": s, "input": inp, "label": "L-ANY", **x})
            store[(s, inp)] = {**scores, **{m + "-cal": cal[m][s] for m in cal}, "y": ys[s]}
        say(f"A {inp}: " + ", ".join(f"{m} {np.mean([r['auc'] for r in rows if r['input'] == inp and r['method'] == m]):.3f}" for m in (*UNSUP, 'GBM', 'CNN')))
    # 10 m scores aggregated to 30 m (maximum of the nine children), scored on I30 L-ANY
    for s in SITES:
        y30 = store[(s, "I30")]["y"]
        nr, nc = y30.shape
        for m in ("DET", "BICUBIC", "GBM", "CNN"):
            v = store[(s, "I10")][m]
            agg = v[:nr * 3, :nc * 3].reshape(nr, 3, nc, 3).max((1, 3))
            rows.append(metric_row(s, "I10to30", m, agg, y30, "L-ANY"))
    write("A_metrics.csv", rows); write("A_paired_differences.csv", diffs); write("A_macro.csv", macro(rows))
    # hazard layers for stage 28 (probabilities, leave one site out on L-ANY)
    np.savez_compressed(os.path.join(CDIR, "layers_L-ANY.npz"),
                        **{f"{s}|{i}|{m}": v.astype(np.float32) for (s, i), d in store.items() for m, v in d.items()
                           if m in ("DET", "DET-cal", "SLOPE-cal", "BICUBIC-cal", "GBM", "CNN", "y")})
    return store


def part_B(D):
    rows = []
    zs = {s: D[s]["z30"].astype(float) for s in SITES}
    sc = {s: unsup_scores(zs[s], 30.0) for s in SITES}
    F = {s: B.feature_stack(zs[s], 30.0) for s in SITES}
    labels = {f"L-CELL n{n}": f"cell30_n{n}" for n in (10, 50, 100, 300)}
    labels.update({"L-ANY 28deg": "any30", "L-ANY 30deg": "any30_deg30", "L-ANY 32deg": "any30_deg32"})
    for lname, key in labels.items():
        ys = {s: D[s][key][:zs[s].shape[0], :zs[s].shape[1]] for s in SITES}
        gbm = loso_gbm(F, ys)
        for s in SITES:
            for m in UNSUP:
                rows.append(metric_row(s, "I30", m, sc[s][m], ys[s], lname))
            rows.append(metric_row(s, "I30", "GBM", gbm[s], ys[s], lname))
        say(f"B {lname}: " + ", ".join(f"{m} {np.mean([r['auc'] for r in rows if r['label'] == lname and r['method'] == m]):.3f}" for m in (*UNSUP, 'GBM')))
    write("B_metrics.csv", rows); write("B_macro.csv", macro(rows))


def part_C(D):
    rows, scal = [], []
    for d in POSTINGS:
        t0 = time.time()
        pr, ps = done_rows(f"C_{d}"), done_rows(f"Cs_{d}")
        if pr is not None and ps is not None:
            rows += numeric(pr)
            for r in ps:
                r["patches"] = int(r["patches"]); r["detected"] = int(r["detected"]); r["posting_m"] = int(float(r["posting_m"]))
            scal += ps; continue
        n0, m0 = len(rows), len(scal)
        zs = {s: D[s][f"z{d}"].astype(float) for s in SITES}
        ys = {s: D[s][f"any{d}"][:zs[s].shape[0], :zs[s].shape[1]] for s in SITES}
        sc = {}
        for s in SITES:
            ge, gn = horn_gradient(zs[s], d, d)
            sc[s] = {"SLOPE": np.degrees(np.arctan(np.hypot(ge, gn))), "BICUBIC": B.bicubic_max_slope(zs[s], d)[:zs[s].shape[0], :zs[s].shape[1]],
                     "DET": PL.face_detector(float(d)).predict(SG.features_2d(zs[s], float(d), float(d)))}
        F = {s: B.feature_stack(zs[s], float(d)).astype(np.float32) for s in SITES}
        gbm = loso_gbm(F, ys, cap=CAP_ROWS)
        del F
        for s in SITES:
            sc[s]["GBM"] = gbm[s]
            y = ys[s]
            nr, nc = y.shape
            pairs = D[s][f"pairs{d}"]
            ncell = nr * nc
            pid = (pairs // ncell).astype(np.int64); cell = (pairs % ncell).astype(np.int64)
            L = D[s]["patch_len_m"]
            for m, v in sc[s].items():
                rows.append(metric_row(s, f"B{d}", m, v, y, "L-ANY", posting_m=d))
                neg = np.sort(v[~y].ravel())
                thr = neg[min(len(neg) - 1, int(np.floor(0.9 * len(neg))))] if len(neg) else np.inf
                flagged = (v.ravel() > thr)
                det = np.bincount(pid - 1, flagged[cell].astype(float), minlength=len(L)) > 0
                touched = np.bincount(pid - 1, minlength=len(L)) > 0
                ratio = L / d
                for lo, hi in ((0, 0.5), (0.5, 1), (1, 2), (2, 4), (4, 8), (8, np.inf)):
                    sel = touched & (ratio >= lo) & (ratio < hi)
                    scal.append({"site": s, "posting_m": d, "method": m, "ratio_bin": f"{lo:g} to {hi:g}", "patches": int(sel.sum()),
                                 "detected": int((det & sel).sum())})
        save_rows(f"C_{d}", rows[n0:]); save_rows(f"Cs_{d}", scal[m0:])
        say(f"C {d} m ({time.time() - t0:.0f} s): " + ", ".join(f"{m} {np.mean([r['auc'] for r in rows if r['input'] == f'B{d}' and r['method'] == m]):.3f}" for m in ('SLOPE', 'BICUBIC', 'DET', 'GBM')))
    write("C_metrics.csv", rows); write("C_macro.csv", macro(rows, keys=("input", "posting_m", "method")))
    pooled = []
    for (d, m, b) in sorted({(r["posting_m"], r["method"], r["ratio_bin"]) for r in scal}, key=lambda x: (x[0], x[1], float(x[2].split()[0]))):
        rr = [r for r in scal if (r["posting_m"], r["method"], r["ratio_bin"]) == (d, m, b)]
        n = sum(r["patches"] for r in rr); k = sum(r["detected"] for r in rr)
        pooled.append({"posting_m": d, "method": m, "ratio_bin": b, "patches": n, "recall": round(k / n, 4) if n else ""})
    write("C_scaling_by_site.csv", scal); write("C_scaling.csv", pooled)


def part_D(D):
    rows = []
    for p in ("R10", "N30", "G30n"):
        prev = done_rows(f"D_{p}")
        if prev is not None:
            rows += numeric(prev); continue
        n0 = len(rows)
        zs, ys, va, F, sc = {}, {}, {}, {}, {}
        for s in SITES:
            z = D[s][f"{p}_z"].astype(float)
            z = B.fill_nearest(z)
            dx, dy = D[s][f"{p}_dxdy"]
            zs[s] = z; ys[s] = D[s][f"{p}_any"]; va[s] = D[s][f"{p}_valid"]
            sc[s] = unsup_scores(z, float(dx), float(dy))
            F[s] = B.feature_stack(z, float(np.sqrt(dx * dy)))
        # GBM trained on the valid cells of the other sites
        Fv = {s: F[s][va[s]][None] for s in SITES}; yv = {s: ys[s][va[s]][None] for s in SITES}
        gbm = loso_gbm(Fv, yv)
        for s in SITES:
            v = va[s]
            for m in ("DET", "SLOPE", "TRI", "BICUBIC"):
                rows.append(metric_row(s, p, m, sc[s][m][v], ys[s][v], "L-ANY", dx_m=round(float(D[s][f'{p}_dxdy'][0]), 2), dy_m=round(float(D[s][f'{p}_dxdy'][1]), 2)))
            rows.append(metric_row(s, p, "GBM", gbm[s].ravel(), ys[s][v], "L-ANY"))
        save_rows(f"D_{p}", rows[n0:])
        say(f"D {p}: " + ", ".join(f"{m} {np.mean([r['auc'] for r in rows if r['input'] == p and r['method'] == m]):.3f}" for m in ('DET', 'SLOPE', 'TRI', 'BICUBIC', 'GBM')))
    write("D_metrics.csv", rows); write("D_macro.csv", macro(rows))


def part_E(D):
    rows = []
    for inp, k in (("I10", 10), ("I30", 30)):
        zs = {s: D[s][f"z{k}"].astype(float) for s in SITES}
        ys = {s: D[s][f"any{k}"][:zs[s].shape[0], :zs[s].shape[1]] for s in SITES}
        Fd = {s: B.feature_stack(zs[s], float(k)) for s in SITES}
        Fs2 = {s: D[s][f"S2_{k}"][:zs[s].shape[0], :zs[s].shape[1]] for s in SITES}
        Fna = {s: D[s][f"NAIP_{k}"][:zs[s].shape[0], :zs[s].shape[1]] for s in SITES}
        sets = {"GBM": Fd, "IMG-S2": Fs2, "IMG-NAIP": Fna,
                "DEM+S2": {s: np.concatenate([Fd[s], Fs2[s]], -1) for s in SITES},
                "DEM+NAIP": {s: np.concatenate([Fd[s], Fna[s]], -1) for s in SITES}}
        store = {}
        for name, F in sets.items():
            store[name] = loso_gbm(F, ys)
            for s in SITES:
                rows.append(metric_row(s, inp, name, store[name][s], ys[s], "L-ANY"))
        say(f"E {inp}: " + ", ".join(f"{m} {np.mean([r['auc'] for r in rows if r['input'] == inp and r['method'] == m]):.3f}" for m in sets))
        np.savez_compressed(os.path.join(CDIR, f"layers_imagery_{inp}.npz"), **{f"{s}|{m}": store[m][s].astype(np.float32) for m in ("DEM+S2", "DEM+NAIP") for s in SITES})
    write("E_metrics.csv", rows); write("E_macro.csv", macro(rows))


def part_F(D):
    import torch, torch.nn as nn
    from dunerover import benchmark_cnn as C
    torch.set_num_threads(2)
    K = 6        # 30 m to 5 m

    def inp_channels(zb):
        return np.stack([(zb - uniform_filter(zb, 7, mode="nearest")) / 5.0, B.slope_tan(zb, 5.0)]).astype(np.float32)

    def net():
        layers, cin = [], 2
        for dil in (1, 2, 4, 8):
            layers += [nn.Conv2d(cin, 32, 3, padding=dil, dilation=dil, padding_mode="reflect"), nn.ReLU()]; cin = 32
        layers.append(nn.Conv2d(32, 1, 1))
        return nn.Sequential(*layers)
    data = {}
    for s in SITES:
        z30 = D[s]["z30"].astype(float); z5 = D[s]["z5"].astype(float)
        zb = zoom(z30, K, order=3, mode="nearest", grid_mode=True)
        nr, nc = min(zb.shape[0], z5.shape[0]), min(zb.shape[1], z5.shape[1])
        data[s] = (inp_channels(zb[:nr, :nc]), ((z5[:nr, :nc] - zb[:nr, :nc]) / 5.0).astype(np.float32), zb[:nr, :nc])
    rows = []
    for held in SITES:
        t0 = time.time()
        prev = done_rows(f"F_{held}")
        if prev is not None:
            rows += numeric(prev); continue
        n0 = len(rows)
        torch.manual_seed(0); rng = np.random.default_rng(0)
        m = net(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); lossf = nn.L1Loss()
        tr = [data[s] for s in SITES if s != held]
        sizes = np.array([t[1].size for t in tr], float); pp = sizes / sizes.sum()
        crop = 96
        for _ in range(3000):
            xs, ys = [], []
            for _ in range(16):
                x, y, _ = tr[rng.choice(len(tr), p=pp)]
                r = rng.integers(0, y.shape[0] - crop + 1); c = rng.integers(0, y.shape[1] - crop + 1)
                xb, yb = x[:, r:r + crop, c:c + crop], y[r:r + crop, c:c + crop]
                q = rng.integers(0, 4)
                xb, yb = np.rot90(xb, q, axes=(1, 2)), np.rot90(yb, q)
                if rng.random() < 0.5:
                    xb, yb = xb[:, :, ::-1], yb[:, ::-1]
                # a quarter turn of the input changes the meaning of nothing: both channels are rotation invariant
                xs.append(np.ascontiguousarray(xb)); ys.append(np.ascontiguousarray(yb))
            opt.zero_grad()
            loss = lossf(m(torch.from_numpy(np.stack(xs))), torch.from_numpy(np.stack(ys))[:, None])
            loss.backward(); opt.step()
        for inp in ("I30", "G30"):
            z30 = D[held]["z30"].astype(float) if inp == "I30" else B.fill_nearest(D[held]["G30"].astype(float))
            zb = zoom(z30, K, order=3, mode="nearest", grid_mode=True)
            with torch.no_grad():
                res = m(torch.from_numpy(inp_channels(zb)[None])).numpy()[0, 0] * 5.0
            zsr = zb + res
            ge, gn = horn_gradient(zsr, 5.0, 5.0)
            sl = np.degrees(np.arctan(np.hypot(ge, gn)))
            nr, nc = z30.shape
            score = sl[:nr * K, :nc * K].reshape(nr, K, nc, K).max((1, 3))
            y = D[held]["any30"][:nr, :nc]
            rows.append(metric_row(held, inp, "SR", score, y, "L-ANY"))
            rows.append(metric_row(held, inp, "BICUBIC", B.bicubic_max_slope(z30, 30)[:nr, :nc], y, "L-ANY"))
            np.save(os.path.join(CDIR, f"SR_{held}_{inp}.npy"), score.astype(np.float32))
        save_rows(f"F_{held}", rows[n0:])
        say(f"F held out {held}: {time.time() - t0:.0f} s; " + ", ".join(f"{r['input']} {r['method']} {r['auc']:.3f}" for r in rows if r['site'] == held))
    write("F_metrics.csv", rows); write("F_macro.csv", macro(rows))


def part_G(D):
    from sklearn.ensemble import HistGradientBoostingClassifier
    rows = []
    for inp, k in (("I10", 10), ("I30", 30), ("G30", 30)):
        prev = done_rows(f"G_{inp}")
        if prev is not None:
            rows += numeric(prev); continue
        n0 = len(rows)
        zs = {s: (D[s][f"z{k}"] if inp != "G30" else B.fill_nearest(D[s]["G30"].astype(float))).astype(float) for s in SITES}
        ys = {s: D[s][f"any{k}"][:zs[s].shape[0], :zs[s].shape[1]] for s in SITES}
        F = {s: B.feature_stack(zs[s], float(k)) for s in SITES}
        bic = {s: B.bicubic_max_slope(zs[s], k)[:zs[s].shape[0], :zs[s].shape[1]] for s in SITES}
        Fp = {s: np.concatenate([F[s], extra_features(zs[s], float(k), bic[s])], -1) for s in SITES}
        variants = {"GBM": loso_gbm(F, ys), "GBM-noDET": loso_gbm({s: F[s][..., :12] for s in SITES}, ys), "GBM+": loso_gbm(Fp, ys)}
        if inp in ("I10", "I30"):
            grid = [dict(learning_rate=lr, max_leaf_nodes=nl, max_iter=it, random_state=0) for lr in (0.05, 0.1) for nl in (15, 63) for it in (200, 600)]
            tuned, chosen = {}, {}
            t0 = time.time()
            for held in SITES:
                inner = [s for s in SITES if s != held]
                best = None
                for prm in grid:
                    aucs = []
                    for v in inner:
                        X = np.concatenate([F[s].reshape(-1, F[s].shape[-1]) for s in inner if s != v])
                        y = np.concatenate([ys[s].ravel() for s in inner if s != v])
                        mdl = HistGradientBoostingClassifier(**prm).fit(X, y)
                        aucs.append(B.auc(mdl.predict_proba(F[v].reshape(-1, F[v].shape[-1]))[:, 1], ys[v].ravel()))
                    if best is None or np.mean(aucs) > best[0]:
                        best = (float(np.mean(aucs)), prm)
                X = np.concatenate([F[s].reshape(-1, F[s].shape[-1]) for s in inner]); y = np.concatenate([ys[s].ravel() for s in inner])
                mdl = HistGradientBoostingClassifier(**best[1]).fit(X, y)
                tuned[held] = mdl.predict_proba(F[held].reshape(-1, F[held].shape[-1]))[:, 1].reshape(ys[held].shape)
                chosen[held] = {k_: v_ for k_, v_ in best[1].items() if k_ != "random_state"}
            variants["GBM-tuned"] = tuned
            say(f"G {inp}: tuning {time.time() - t0:.0f} s; chosen {json.dumps(chosen)}")
        if inp == "I30":
            variants["CNN-long"] = loso_cnn(zs, ys, k, 32, steps=6000)
        for name, pred in variants.items():
            for s in SITES:
                extra = {"chosen": json.dumps(chosen[s])} if name == "GBM-tuned" else {}
                rows.append(metric_row(s, inp, name, pred[s], ys[s], "L-ANY", **extra))
        np.savez_compressed(os.path.join(CDIR, f"G_{inp}.npz"), **{f"{s}|{n}": v[s].astype(np.float32) for n, v in variants.items() for s in SITES})
        save_rows(f"G_{inp}", rows[n0:])
        say(f"G {inp}: " + ", ".join(f"{m} {np.mean([r['auc'] for r in rows if r['input'] == inp and r['method'] == m]):.3f}" for m in variants))
    write("G_metrics.csv", rows); write("G_macro.csv", macro(rows))


def part_H(D):
    rows = []
    for inp, k in (("I10", 10), ("I30", 30), ("G30", 30)):
        for s in SITES:
            z = (D[s][f"z{k}"] if inp != "G30" else B.fill_nearest(D[s]["G30"].astype(float))).astype(float)
            y = D[s][f"any{k}"][:z.shape[0], :z.shape[1]]
            ge, gn = horn_gradient(z, k, k)
            rows.append(metric_row(s, inp, "SLOPE", np.degrees(np.arctan(np.hypot(ge, gn))), y, "L-ANY"))
            rows.append(metric_row(s, inp, "ASPECT", aspect_rule(z, k, k), y, "L-ANY"))
            rows.append({"site": s, "input": inp, "label": "L-ANY", "method": "PREVALENCE", "cells": int(y.size), "prevalence": round(float(y.mean()), 4),
                         "auc": 0.5, "ap": round(float(y.mean()), 4)})
    write("H_metrics.csv", rows); write("H_macro.csv", macro(rows))


def part_I(D):
    rows = []
    ranges = {}
    for s in SITES:
        y = D[s]["any10"].astype(float)
        y = y - y.mean(); v = (y ** 2).mean()
        rng_m = None
        for h in range(3, 151, 3):
            c1 = (y[:, :-h] * y[:, h:]).mean() / v; c2 = (y[:-h] * y[h:]).mean() / v
            c = 0.5 * (c1 + c2)
            rows.append({"site": s, "lag_m": h * 10, "correlation": round(float(c), 4)})
            if rng_m is None and c < 0.1:
                rng_m = h * 10
        ranges[s] = rng_m
    write("I_correlogram.csv", rows)
    say(f"I correlogram range (m): {ranges}")
    big = max(v or 1500 for v in ranges.values())
    # site level tests and the larger block bootstrap on the main I30 comparisons (needs parts A, F, G, E)
    A = {(r["site"], r["input"], r["method"]): r["auc"] for r in csv.DictReader(open(os.path.join(OUT, "A_metrics.csv")))}
    extra = {}
    for f in ("F_metrics.csv", "G_metrics.csv", "E_metrics.csv"):
        p = os.path.join(OUT, f)
        if os.path.exists(p):
            for r in csv.DictReader(open(p)):
                if r["input"] == "I30":
                    extra[(r["site"], r["method"])] = float(r["auc"])
    tests = []
    comps = [("DET", A), ("GBM", A), ("CNN", A)] + [(m, None) for m in ("SR", "GBM+", "DEM+S2", "DEM+NAIP")]
    for m, src in comps:
        try:
            d = [(float(A[(s, "I30", m)]) if src is not None else extra[(s, m)]) - float(A[(s, "I30", "BICUBIC")]) for s in SITES]
        except KeyError:
            continue
        tests.append({"comparison": f"{m} minus BICUBIC (I30, L-ANY)", "per_site": " ".join(f"{x:+.3f}" for x in d),
                      "mean": round(float(np.mean(d)), 4), "positive_sites": int(sum(x > 0 for x in d)), "p_sign_flip": round(sign_flip_p(d), 4)})
    adj = holm([t["p_sign_flip"] for t in tests]) if tests else []
    for t, q in zip(tests, adj):
        t["p_holm"] = round(float(q), 4)
    write("I_site_tests.csv", tests)
    # larger blocks for the main I30 comparisons when the range exceeds 300 m
    out = []
    if big > BLOCK_M:
        L = np.load(os.path.join(CDIR, "layers_L-ANY.npz"))
        for s in SITES:
            z = D[s]["z30"].astype(float)
            y = D[s]["any30"][:z.shape[0], :z.shape[1]]
            sc = unsup_scores(z, 30.0)
            scores = {"BICUBIC": sc["BICUBIC"], "DET": sc["DET"], "SLOPE": sc["SLOPE"], "GBM": L[f"{s}|I30|GBM"], "CNN": L[f"{s}|I30|CNN"]}
            ci, dd = boot_auc(scores, y, 30, ref_methods=("BICUBIC",), block_m=float(big))
            for x in dd:
                out.append({"site": s, "block_m": big, **x})
        write("I_larger_blocks.csv", out)
    json.dump({"correlogram_range_m": ranges, "block_m_used_for_sensitivity": big}, open(os.path.join(OUT, "I_summary.json"), "w"), indent=1)


def main():
    global LOG
    os.makedirs(OUT, exist_ok=True); os.makedirs(CDIR, exist_ok=True)
    parts = sys.argv[1:] or ["prepare", "A", "B", "C", "D", "E", "F", "G", "H", "I"]
    LOG = open(os.path.join(OUT, "run_log.txt"), "a")
    import sklearn, scipy
    say(f"stage 27 {' '.join(parts)} started {time.strftime('%Y-%m-%d %H:%M:%S')}; numpy {np.__version__}, scipy {scipy.__version__}, "
        f"scikit-learn {sklearn.__version__}; seed {SEED}")
    if "prepare" in parts:
        prepare()
    D = load_all() if any(p != "prepare" for p in parts) else None
    for p in parts:
        if p == "prepare":
            continue
        t0 = time.time()
        globals()[f"part_{p}"](D)
        say(f"part {p} done in {time.time() - t0:.0f} s ({time.strftime('%H:%M:%S')})")
    say(f"stage 27 {' '.join(parts)} finished {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
