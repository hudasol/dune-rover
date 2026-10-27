#!/usr/bin/env python3
"""Stage 25 (docs/PREDICTIONS.md): the slip face detector against baselines on six lidar dune fields, on block mean
surfaces at 10 and 30 m (I10, I30) and on the real Copernicus GLO-30 product (G30).

    PYTHONPATH=src python3 scripts/benchmark_detection.py            # full registered run
    PYTHONPATH=src python3 scripts/benchmark_detection.py --no-cnn   # without the convolutional baseline

Inputs (git ignored): data/raw/lidar/ (scripts/fetch_lidar.sh) and data/raw/glo30_us/ (scripts/fetch_data.sh).
Outputs: results/benchmark/detection/ (metrics.csv, paired_differences.csv, macro.csv, summary.json, run_log.txt) and
the per cell score cache data/cache/benchmark_scores.npz used by stage 26 and the paper figures.
SIMULATED BY ME (every detector) scored against PUBLISHED elevation data. Deterministic.
"""
from __future__ import annotations
import csv, hashlib, json, os, sys, time
import numpy as np
import tifffile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover import benchmark as B, planner as PL, subgrid as SG  # noqa: E402

RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "results", "benchmark", "detection")
CACHE = os.path.join(ROOT, "data", "cache", "benchmark_scores.npz")
SEED = 20261027
N_BOOT = 1000
BLOCK_M = 300.0
TAU = 0.20
INPUTS = {"I10": 10, "I30": 30, "G30": 30}
# stage 12 windows (scripts/terrain_validation_lidar.py) and stage 20 windows (config/lidar_sites_phase4.json)
SITES = {
    "Dumont": ("USGS_1M_11_x56y395_CA_FEMAR9Southeast_D24.tif", (564900, 567900, 3943500, 3948300), "Copernicus_DSM_COG_10_N35_00_W117_00_DEM.tif"),
    "WhiteSands": ("USGS_1M_13_x37y364_NM_WhiteSandsNM_2020_D20.tif", (378400, 379900, 3630400, 3634600), "Copernicus_DSM_COG_10_N32_00_W107_00_DEM.tif"),
    "Kelso": ("USGS_1M_11_x61y387_CA_FEMAR9Southeast_D24.tif", (615000, 618600, 3862400, 3865100), "Copernicus_DSM_COG_10_N34_00_W116_00_DEM.tif"),
}
_P4 = {"GreatSandDunes": "Copernicus_DSM_COG_10_N37_00_W106_00_DEM.tif", "Algodones": "Copernicus_DSM_COG_10_N32_00_W116_00_DEM.tif",
       "LittleSahara": "Copernicus_DSM_COG_10_N39_00_W113_00_DEM.tif"}
for _k, _v in json.load(open(os.path.join(ROOT, "config", "lidar_sites_phase4.json"))).items():
    if not _k.startswith("_"):
        SITES[_k] = (_v[0], tuple(_v[1]), _P4[_k])
SCORE_METHODS = ("DET", "SLOPE", "TRI", "ROUGH", "BICUBIC", "GBM", "CNN")     # ranked for AUC
PROB_METHODS = ("DET", "DET-cal", "SLOPE-cal", "TRI-cal", "ROUGH-cal", "BICUBIC-cal", "GBM", "CNN")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def load_lidar_window(fname, win):
    """One metre window; returns (z with NaN voids, easting and northing of the window's north west corner, EPSG)."""
    with tifffile.TiffFile(os.path.join(RAW, "lidar", fname)) as tf:
        p = tf.pages[0]
        keys, _ = PL._geokeys(p)
        tie = p.tags["ModelTiepointTag"].value; sc = p.tags["ModelPixelScaleTag"].value
        e0, n0, d = float(tie[3]), float(tie[4]), float(sc[0])
        assert d == 1.0 and keys.get(1025, 1) == 1, (fname, d, keys.get(1025))
        e_min, e_max, n_min, n_max = win
        c0, c1 = int(round((e_min - e0) / d)), int(round((e_max - e0) / d))
        r0, r1 = int(round((n0 - n_max) / d)), int(round((n0 - n_min) / d))
        z = p.asarray()[r0:r1, c0:c1].astype(np.float64)
    z[~np.isfinite(z) | (z < -1000)] = np.nan
    return z, e0 + c0 * d, n0 - r0 * d, int(keys.get(3072))


def glo30_grid(tile, e_corner, n_corner, epsg, shape30):
    """GLO-30 interpolated bilinearly at the centres of the 30 m cells of the window."""
    from pyproj import Transformer
    r = PL.read_raster(os.path.join(RAW, "glo30_us", tile))
    rr, cc = np.indices(shape30)
    E = e_corner + (cc + 0.5) * 30.0; N = n_corner - (rr + 0.5) * 30.0
    lon, lat = Transformer.from_crs(epsg, 4326, always_xy=True).transform(E, N)
    g = B.sample_geographic(r, lon, lat)
    return g, float(np.isnan(g).mean())


def scores_for(zc, d, k):
    """Unsupervised scores and the learned features of one coarse surface."""
    det = PL.face_detector(float(d)).predict(SG.features_2d(zc, float(d), float(d)))
    return {"DET": det, "SLOPE": B.slope_deg(zc, d), "TRI": B.tri(zc, d), "ROUGH": B.plane_roughness(zc, d, 3),
            "BICUBIC": B.bicubic_max_slope(zc, k)}, B.feature_stack(zc, d)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-cnn", action="store_true", help="skip the convolutional baseline (registered as dropped first if time runs short)")
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    log = open(os.path.join(OUT, "run_log.txt"), "w")

    def say(m):
        print(m, flush=True); log.write(m + "\n"); log.flush()
    import scipy, sklearn
    vers = {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__, "scikit-learn": sklearn.__version__}
    if not args.no_cnn:
        import torch
        vers["torch"] = torch.__version__
    say(f"stage 25 run started {time.strftime('%Y-%m-%d %H:%M:%S')}; versions {vers}; seed {SEED}; bootstrap {args.n_boot} x {BLOCK_M:g} m blocks")

    data = {}       # (site, input) -> dict
    meta = {}
    for site, (fname, win, tile) in SITES.items():
        t0 = time.time()
        z1, ec, nc_, epsg = load_lidar_window(fname, win)
        void = np.isnan(z1)
        z1f = B.fill_nearest(z1)
        steep, _ = B.steep_posts(z1, void)
        steep36, _ = B.steep_posts(z1, void, hi_deg=36.0)
        meta[site] = {"lidar_file": fname, "lidar_sha256": sha256(os.path.join(RAW, "lidar", fname)), "window_utm": list(win), "epsg": epsg,
                      "shape_1m": list(z1.shape), "void_share": float(void.mean()), "glo30_file": tile,
                      "glo30_sha256": sha256(os.path.join(RAW, "glo30_us", tile))}
        for inp, k in INPUTS.items():
            y = B.cell_truth(steep, k); y36 = B.cell_truth(steep36, k)
            if inp == "G30":
                zc, gvoid = glo30_grid(tile, ec, nc_, epsg, y.shape)
                meta[site]["glo30_void_share"] = gvoid
                zc = B.fill_nearest(zc)
            else:
                zc = B.block(z1f, k)
            zc = zc[:y.shape[0], :y.shape[1]]
            sc, F = scores_for(zc, float(k), k)
            data[(site, inp)] = {"z": zc, "y": y, "y36": y36, "scores": sc, "F": F, "k": k}
        say(f"{site}: {z1.shape} posts, voids {void.mean():.4f}, GLO-30 voids {meta[site]['glo30_void_share']:.4f}, "
            f"prevalence I10 {data[(site, 'I10')]['y'].mean():.3f} I30 {data[(site, 'I30')]['y'].mean():.3f} ({time.time() - t0:.0f} s)")

    sites = list(SITES)
    # leave one site out: calibrations, gradient boosting, convolutional network
    for inp in INPUTS:
        for held in sites:
            tr = [data[(s, inp)] for s in sites if s != held]
            te = data[(held, inp)]
            ytr = np.concatenate([d["y"].ravel() for d in tr])
            for m in ("DET", "SLOPE", "TRI", "ROUGH", "BICUBIC"):
                cal = B.Platt("logit" if m == "DET" else "identity").fit(np.concatenate([d["scores"][m].ravel() for d in tr]), ytr)
                te["scores"][m + "-cal"] = cal.predict(te["scores"][m])
            t0 = time.time()
            gbm = B.gbm_fit(np.concatenate([d["F"].reshape(-1, d["F"].shape[-1]) for d in tr]), ytr)
            te["scores"]["GBM"] = B.gbm_predict(gbm, te["F"])
            msg = f"{inp} held out {held}: GBM {time.time() - t0:.0f} s"
            if not args.no_cnn:
                from dunerover import benchmark_cnn as C
                t0 = time.time()
                crop = 64 if INPUTS[inp] == 10 else 32
                net = C.fit([(C.channels(d["z"], float(d["k"])), d["y"]) for d in tr], crop)
                te["scores"]["CNN"] = C.predict(net, C.channels(te["z"], float(te["k"])))
                msg += f", CNN {time.time() - t0:.0f} s"
            say(msg)

    methods = [m for m in SCORE_METHODS if args.no_cnn is False or m != "CNN"]
    probs = [m for m in PROB_METHODS if args.no_cnn is False or m != "CNN"]
    rows, diffs = [], []
    for (site, inp), d in data.items():
        y = d["y"].ravel(); k = d["k"]
        ids = B.block_ids(d["y"].shape, int(round(BLOCK_M / k)))
        ranked = {m: B.RankedScore(d["scores"][m], y) for m in methods}
        boots = {m: [] for m in methods}
        for w in B.block_bootstrap_weights(ids, args.n_boot, SEED):
            for m in methods:
                boots[m].append(ranked[m].auc(w))
        boots = {m: np.array(v) for m, v in boots.items()}
        for m in sorted(set(methods) | set(probs), key=lambda x: (x not in methods, x)):
            s = d["scores"][m].ravel()
            r = {"site": site, "input": inp, "method": m, "cells": int(y.size), "prevalence": round(float(y.mean()), 4)}
            if m in methods:
                lo, hi = np.nanpercentile(boots[m], [2.5, 97.5])
                r.update({"auc": round(ranked[m].auc(), 4), "auc_lo": round(float(lo), 4), "auc_hi": round(float(hi), 4),
                          "ap": round(B.average_precision(s, y), 4), "recall_at_fpr10": round(B.recall_at_fpr(s, y, 0.10), 4),
                          "auc_28_36": round(B.auc(s, d["y36"].ravel()), 4)})
            if m in probs:
                r.update({"brier": round(B.brier(s, y), 4), "brier_climatology": round(float(y.mean() * (1 - y.mean())), 4),
                          "miss_at_0.20": round(float((s[y] < TAU).mean()), 4) if y.any() else "",
                          "flagged_at_0.20": round(float((s >= TAU).mean()), 4), "mean_probability": round(float(s.mean()), 4)})
            rows.append(r)
        for ref in ("DET", "SLOPE"):
            for m in methods:
                if m == ref:
                    continue
                dd = boots[m] - boots[ref]
                lo, hi = np.nanpercentile(dd, [2.5, 97.5])
                diffs.append({"site": site, "input": inp, "method": m, "reference": ref,
                              "auc_difference": round(ranked[m].auc() - ranked[ref].auc(), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
                              "significant": bool(lo > 0 or hi < 0)})
        say(f"{site} {inp}: " + ", ".join(f"{m} {ranked[m].auc():.3f}" for m in methods))

    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(os.path.join(OUT, "metrics.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    with open(os.path.join(OUT, "paired_differences.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(diffs[0])); w.writeheader(); w.writerows(diffs)
    macro = []
    for inp in INPUTS:
        for m in sorted(set(methods) | set(probs)):
            rr = [r for r in rows if r["input"] == inp and r["method"] == m]
            out = {"input": inp, "method": m, "sites": len(rr)}
            for key in ("auc", "ap", "recall_at_fpr10", "auc_28_36", "brier", "miss_at_0.20", "flagged_at_0.20"):
                v = [r[key] for r in rr if key in r and r[key] != ""]
                if v:
                    out[key] = round(float(np.mean(v)), 4)
            macro.append(out)
    keys = []
    for r in macro:
        keys += [k for k in r if k not in keys]
    with open(os.path.join(OUT, "macro.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(macro)
    np.savez_compressed(CACHE, **{f"{s}|{i}|{m}": v.astype(np.float32) for (s, i), d in data.items() for m, v in d["scores"].items()},
                        **{f"{s}|{i}|y": d["y"] for (s, i), d in data.items()}, **{f"{s}|{i}|z": d["z"].astype(np.float32) for (s, i), d in data.items()})
    json.dump({"label": "SIMULATED BY ME (detectors and baselines) scored against PUBLISHED elevation (USGS 3DEP lidar, public domain; Copernicus GLO-30)",
               "stage": 25, "seed": SEED, "n_boot": args.n_boot, "block_m": BLOCK_M, "tau": TAU, "inputs": INPUTS, "versions": vers,
               "gbm_params": B.GBM_PARAMS, "cnn": None if args.no_cnn else "registered design, benchmark_cnn.py", "sites": meta,
               "finished": time.strftime("%Y-%m-%d %H:%M:%S")}, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
    say(f"done {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
