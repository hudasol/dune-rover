#!/usr/bin/env python3
"""Stage 12 (docs/PREDICTIONS.md): score the sub grid slip face detector and the three class map against real
one metre lidar dune surfaces degraded to 5, 10 and 30 m.

    PYTHONPATH=src python3 scripts/terrain_validation_lidar.py

Inputs (git ignored, public domain, USGS 3DEP one metre bare earth DEMs; see docs/DATA_AND_LICENSES.md):
  data/raw/lidar/USGS_1M_11_x56y395_CA_FEMAR9Southeast_D24.tif   Dumont Dunes, California, UTM 11N
  data/raw/lidar/USGS_1M_13_x37y364_NM_WhiteSandsNM_2020_D20.tif White Sands, New Mexico, UTM 13N
  data/raw/lidar/USGS_1M_11_x61y387_CA_FEMAR9Southeast_D24.tif   Kelso Dunes, California, UTM 11N
Outputs: results/terrain_validation/ (metrics.csv, slope_gap.csv, summary.json, run_log.txt, figures/).

The detector and the map are used unchanged (subgrid.fit with the base prior, threeclass with the original range set).
The truth is the one metre slope; it is PUBLISHED elevation data processed by me, from North American dune fields,
not Arabian ones.  Everything predicted is SIMULATED BY ME.  Deterministic (fixed seeds).
"""
from __future__ import annotations
import csv, hashlib, json, os, sys, time
import numpy as np
import tifffile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover.dem import Dem  # noqa: E402
from dunerover.terrain import horn_gradient  # noqa: E402
from dunerover import traverse as TR, subgrid as SG, threeclass as TC  # noqa: E402
from dunerover.slipmodel import apply_range_set  # noqa: E402

RAW = os.path.join(ROOT, "data", "raw", "lidar")
OUT = os.path.join(ROOT, "results", "terrain_validation")
SEED = 20261020
POSTINGS = (5, 10, 30)
MIN_POSTS = 10          # truth: at least this many one metre posts at FACE_TRUTH_DEG or steeper inside the footprint
# Windows (UTM easting min, easting max, northing min, northing max), chosen from a 20 m slope image before any metric.
# Kelso: the first committed northing (3872400 to 3875100) lay outside the tile because the image axis was read from the
# wrong origin; corrected to the same image region (3862400 to 3865100) before any Kelso metric was computed.
SITES = {
    "Dumont": ("USGS_1M_11_x56y395_CA_FEMAR9Southeast_D24.tif", (564900, 567900, 3943500, 3948300), "Dumont Dunes, California (UTM 11N); Heverly et al. 2013 anchor site"),
    "WhiteSands": ("USGS_1M_13_x37y364_NM_WhiteSandsNM_2020_D20.tif", (378400, 379900, 3630400, 3634600), "White Sands, New Mexico (UTM 13N); western edge of the gypsum dune field"),
    "Kelso": ("USGS_1M_11_x61y387_CA_FEMAR9Southeast_D24.tif", (615000, 618600, 3862400, 3865100), "Kelso Dunes, California (UTM 11N); main ridge and surroundings"),
}
PINK = {"bg": "#fffafb", "sakura": "#e8a5bb", "rose": "#c9769a", "deep": "#a8325e", "plum": "#5b3a78", "sage": "#6fa28f", "ink": "#2b2024"}
CLASS_COLORS = {0: "#a9cdbd", 1: "#7a1f45", 2: "#a98fd1", 3: "#ee7aa8", 4: "#5b3a78"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def load_window(fname, win):
    p = tifffile.TiffFile(os.path.join(RAW, fname)).pages[0]
    tie = p.tags["ModelTiepointTag"].value; sc = p.tags["ModelPixelScaleTag"].value
    e0, n0, d = float(tie[3]), float(tie[4]), float(sc[0])
    e_min, e_max, n_min, n_max = win
    c0, c1 = int(round((e_min - e0) / d)), int(round((e_max - e0) / d))
    r0, r1 = int(round((n0 - n_max) / d)), int(round((n0 - n_min) / d))
    z = p.asarray()[r0:r1, c0:c1].astype(np.float64)
    z[z < -1000] = np.nan
    return z, d


def block(a, k, how="mean"):
    nr, nc = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    b = a[:nr, :nc].reshape(nr // k, k, nc // k, k)
    return {"mean": b.mean(axis=(1, 3)), "sum": b.sum(axis=(1, 3)), "max": b.max(axis=(1, 3))}[how]


def main():
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    apply_range_set("original")
    log = open(os.path.join(OUT, "run_log.txt"), "w")
    def say(s):
        print(s, flush=True); log.write(s + "\n")
    say(f"stage 12 run started {time.strftime('%Y-%m-%d %H:%M:%S')}; numpy {np.__version__}; seed {SEED}; windows {json.dumps({k: v[1] for k, v in SITES.items()})}")
    draws = TC.lhs_draws(256, SEED)
    models = {d: SG.fit(float(d), "base", 1.0) for d in POSTINGS}
    rows, gaps, summary = [], [], {"label": "SIMULATED BY ME (detector and map) scored against PUBLISHED lidar elevation (USGS 3DEP, public domain)",
                                   "seed": SEED, "min_posts": MIN_POSTS, "face_truth_deg": SG.FACE_TRUTH_DEG, "sites": {}}
    keep = {}
    for site, (fname, win, desc) in SITES.items():
        z1, d1 = load_window(fname, win)
        assert d1 == 1.0, d1
        nanshare = float(np.isnan(z1).mean())
        z1 = np.where(np.isnan(z1), np.nanmean(z1), z1)
        ge, gn = horn_gradient(z1, 1.0, 1.0)
        s1 = np.degrees(np.arctan(np.hypot(ge, gn)))
        steep = (s1 >= SG.FACE_TRUTH_DEG).astype(float)
        summary["sites"][site] = {"description": desc, "file": fname, "sha256": sha256(os.path.join(RAW, fname)), "window_utm": win,
                                  "shape_1m": list(z1.shape), "nodata_share": nanshare, "relief_m": float(z1.max() - z1.min()),
                                  "share_1m_posts_steeper_than_truth": float(steep.mean())}
        for k in POSTINGS:
            zc = block(z1, k)
            dem = Dem(zc, 0.0, 0.0, 1.0, 1.0, float(k), float(k), source=f"{fname}|block_mean_{k}")
            eg = TR.precompute_edges(dem)
            q = TC.q_pass(eg, draws)
            F = SG.features_2d(zc, float(k), float(k))
            p = models[k].predict(F)
            cls = TC.classify(q, p)
            cnt = block(steep, k, "sum")
            y = cnt >= MIN_POSTS
            y_any = cnt >= 1
            gce, gcn = horn_gradient(zc, float(k), float(k))
            sc = np.degrees(np.arctan(np.hypot(gce, gcn)))
            smax = block(s1, k, "max")
            unk = np.isin(cls, (2, 3, 4)); trav = cls == 0; blk = cls == 1
            def rate(mask, t):
                return float(t[mask].mean()) if mask.any() else float("nan")
            r = {"site": site, "posting_m": k, "cells": int(cls.size), "true_face_rate": float(y.mean()), "true_face_rate_any_post": float(y_any.mean()),
                 "mean_predicted_face_probability": float(p.mean()), "auc": SG.auc(p.ravel(), y.ravel()), "auc_any_post": SG.auc(p.ravel(), y_any.ravel()),
                 "brier": float(np.mean((p - y) ** 2)), "brier_climatology": float(y.mean() * (1 - y.mean())),
                 "share_traversable": float(trav.mean()), "share_blocked": float(blk.mean()), "share_unknown": float(unk.mean()),
                 "face_rate_in_traversable": rate(trav, y), "face_rate_in_unknown": rate(unk, y), "face_rate_in_blocked": rate(blk, y),
                 "face_rate_any_post_in_traversable": rate(trav, y_any),
                 "median_coarse_slope_deg": float(np.median(sc)), "p95_coarse_slope_deg": float(np.percentile(sc, 95))}
            rows.append(r)
            if k == 30:
                g = (smax - sc)[y]
                gaps.append({"site": site, "posting_m": k, "face_cells": int(y.sum()), "median_gap_deg": float(np.median(g)) if g.size else float("nan"),
                             "p10_gap_deg": float(np.percentile(g, 10)) if g.size else float("nan"), "p90_gap_deg": float(np.percentile(g, 90)) if g.size else float("nan"),
                             "median_max_1m_slope_in_face_cells_deg": float(np.median(smax[y])) if g.size else float("nan"),
                             "median_30m_slope_in_face_cells_deg": float(np.median(sc[y])) if g.size else float("nan")})
                keep[site] = (cls, y, s1)
            say(f"{site} {k} m: cells {cls.size}, face rate {r['true_face_rate']:.3f}, mean p {r['mean_predicted_face_probability']:.3f}, AUC {r['auc']:.3f}, "
                f"TRAV {r['share_traversable']:.3f} UNK {r['share_unknown']:.3f} BLK {r['share_blocked']:.3f}, false safe {r['face_rate_in_traversable']:.3f}, "
                f"face in UNKNOWN {r['face_rate_in_unknown']:.3f}")
    for fn, rr in (("metrics.csv", rows), ("slope_gap.csv", gaps)):
        with open(os.path.join(OUT, fn), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rr[0])); w.writeheader(); w.writerows(rr)
    with open(os.path.join(OUT, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    # figure: 30 m class map with true face cells outlined, one panel per site
    fig, axes = plt.subplots(1, len(keep), figsize=(4.2 * len(keep), 5.2), facecolor=PINK["bg"])
    cmap = ListedColormap([CLASS_COLORS[i] for i in range(5)])
    for ax, (site, (cls, y, s1)) in zip(np.atleast_1d(axes), keep.items()):
        ax.imshow(cls, cmap=cmap, vmin=-0.5, vmax=4.5, interpolation="nearest")
        ax.contour(y.astype(float), levels=[0.5], colors=PINK["ink"], linewidths=0.5)
        ax.set_title(f"{site}, 30 m", color=PINK["ink"], fontsize=10); ax.set_xticks([]); ax.set_yticks([])
    fig.text(0.01, 0.01, "Colours: green TRAVERSABLE, wine BLOCKED, lilac and pink UNKNOWN. Black outline: 30 m cells with a face of 28 deg or more in the one metre lidar.\n"
             "SIMULATED BY ME (map) against PUBLISHED lidar (USGS 3DEP). North American dunes, not Arabian. Original range set.", fontsize=7, color=PINK["ink"])
    fig.savefig(os.path.join(OUT, "figures", "fig_lidar_class_maps_30m.png"), dpi=130, bbox_inches="tight")
    # figure: AUC by posting
    fig, ax = plt.subplots(figsize=(5.5, 3.6), facecolor=PINK["bg"]); ax.set_facecolor(PINK["bg"])
    for site, col in zip(SITES, (PINK["deep"], PINK["rose"], PINK["plum"])):
        rr = [r for r in rows if r["site"] == site]
        ax.plot([r["posting_m"] for r in rr], [r["auc"] for r in rr], "o-", color=col, label=site, lw=2, ms=8)
    ax.axhline(0.92, color=PINK["sakura"], ls="--", lw=1, label="synthetic AUC at 30 m")
    ax.set_xlabel("DEM posting (m)"); ax.set_ylabel("AUC against lidar truth"); ax.set_ylim(0.4, 1.0); ax.legend(frameon=False, fontsize=8)
    ax.set_title("Slip face detector on real dunes", color=PINK["ink"], fontsize=10)
    fig.savefig(os.path.join(OUT, "figures", "fig_lidar_auc_by_posting.png"), dpi=130, bbox_inches="tight")
    say(f"done {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
