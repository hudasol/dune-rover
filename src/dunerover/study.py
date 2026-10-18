"""Run the full simulation study.  Every output is SIMULATION ONLY, model-assumption dependent.

    python -m dunerover.study --data data/raw --out results

Fixed seeds: OD selection 20261011, Latin hypercube 20261012 (core A) / 20261013 (core B).
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, platform, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import qmc

from . import SIM_LABEL, __version__
from .dem import load_tile, crop, coarsen
from .terrain import slope_deg, hillshade
from .slipmodel import SlipParams, PARAM_TABLE, slip, critical_uphill_deg, apply_range_set, nominal_params
from . import traverse as TR
from . import sensitivity as SE

OD_SEED, LHS_SEED_A, LHS_SEED_B = 20261011, 20261012, 20261013
TILES = {"A": "Copernicus_DSM_COG_10_N23_00_E053_00_DEM.tif", "B": "Copernicus_DSM_COG_10_N22_00_E054_00_DEM.tif"}
AREAS = {  # name: (tile key, lat_min, lat_max, lon_min, lon_max, od_min_sep_m)
    "A_south_Liwa": ("A", 23.02, 23.17, 53.55, 53.95, 15000),
    "A_north_Liwa": ("A", 23.25, 23.45, 53.55, 53.95, 15000),
    "B_RubAlKhali_megadunes": ("B", 22.20, 22.50, 54.20, 54.60, 15000),
}
CORES = {"A_core": ("A", 23.06, 23.13, 53.62, 53.78, 6000, LHS_SEED_A),
         "B_core": ("B", 22.28, 22.35, 54.30, 54.46, 6000, LHS_SEED_B)}
BLUE, ORANGE, AQUA, GREY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b"


def _style():
    plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c3",
                         "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                         "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.grid": True, "grid.color": "#ecebe7", "grid.linewidth": 0.6, "font.size": 9,
                         "axes.titlesize": 10, "axes.titleweight": "bold", "legend.frameon": False})


def _foot(fig, bottom=0.06):
    try:
        fig.get_layout_engine().set(rect=(0, bottom, 1, 1 - bottom))
    except Exception:
        pass
    fig.text(0.01, 0.005, SIM_LABEL + ". Copernicus GLO-30 (c) DLR/Airbus; processing by this repo.", fontsize=7, color="#52514e")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def slope_stats(dem, ks=(1, 2, 3)):
    rows = []
    for k in ks:
        d = coarsen(dem, k)
        sl = slope_deg(np.nan_to_num(d.z, nan=np.nanmean(d.z)), d.dx, d.dy)
        rows.append({"posting_m": round(float(np.hypot(d.dx, d.dy) / np.sqrt(2)), 1), "block": k, "cells": int(sl.size),
                     "relief_m": float(np.nanmax(d.z) - np.nanmin(d.z)), "max_slope_deg": float(sl.max()),
                     **{f"pct_gt_{a}": float(100 * (sl > a).mean()) for a in (10, 15, 20, 25, 30)}})
    return rows


def anchor_check(path_csv, n_draw=4000, seed=7):
    """Compare model slip with published anchor points. DESCRIPTIVE ONLY: nothing is fitted to them."""
    b = SE.bounds()
    u = qmc.LatinHypercube(d=4, seed=seed).random(n_draw)
    P = {k: b[k][0] + u[:, i] * (b[k][1] - b[k][0]) for i, k in enumerate(("phi_deg", "f_r", "i0", "i_max"))}
    nominal = nominal_params()
    out = []
    with open(path_csv, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            th = np.radians(0.5 * (float(r["slope_deg_lo"]) + float(r["slope_deg_hi"])))
            lo, hi = float(r["slip_lo"]), float(r["slip_hi"])
            # draw-level slip with the SAME formula as the model, capped at 1 (entrapment -> slip 1)
            mu = np.tan(np.radians(P["phi_deg"]))
            x = np.abs(np.tan(th) + P["f_r"]) / mu
            s = np.where(x < 1, -P["i0"] * np.log1p(-np.clip(x, 0, 0.999999)), np.inf)
            s = np.minimum(s, 1.0)
            sn = float(min(slip(np.tan(th), 0.0, nominal), 1.0))
            inside = bool(s.min() <= hi and s.max() >= lo)
            compat = float(np.mean((s >= lo - 0.1) & (s <= hi + 0.1)))
            gap = 0.0 if lo <= sn <= hi else min(abs(sn - lo), abs(sn - hi))
            out.append({"evidence_id": r["evidence_id"], "slope_deg": float(np.degrees(th)), "published_slip_lo": lo,
                        "published_slip_hi": hi, "bound": r["bound"], "validation_type": r["validation_type"],
                        "nominal_model_slip": sn, "nominal_abs_gap": gap, "envelope_min": float(s.min()),
                        "envelope_max": float(s.max()), "envelope_overlaps_published": inside,
                        "frac_param_draws_within_0.1": compat, "definition_warning": r["definition_warning"]})
    return out


def write_csv(path, rows):
    if not rows:
        return
    keys = list(rows[0].keys())
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw"); ap.add_argument("--out", default="results")
    ap.add_argument("--n-lhs", type=int, default=256); ap.add_argument("--only-area-figures", action="store_true"); ap.add_argument("--anchors", default="data/anchor_points.csv")
    ap.add_argument("--range-set", default="original", help="parameter range set from slipmodel.RANGE_SETS (default: original)")
    a = ap.parse_args(argv)
    apply_range_set(a.range_set)
    os.makedirs(os.path.join(a.out, "figures"), exist_ok=True)
    if a.only_area_figures:
        rerender_area_figures(a.data, a.out); return
    _style(); t0 = time.time()
    tiles = {k: load_tile(os.path.join(a.data, f)) for k, f in TILES.items()}
    nominal = nominal_params()
    summary = {"label": SIM_LABEL, "range_set": a.range_set, "version": __version__, "python": platform.python_version(),
               "seeds": {"od": OD_SEED, "lhs_A_core": LHS_SEED_A, "lhs_B_core": LHS_SEED_B},
               "inputs": {k: {"file": TILES[k], "sha256": sha256(os.path.join(a.data, TILES[k]))} for k in TILES},
               "parameters": {k: {"nominal": v[0], "low": v[1], "high": v[2], "status": v[3], "basis": v[4]} for k, v in PARAM_TABLE.items()},
               "nominal_critical_uphill_deg": critical_uphill_deg(nominal), "areas": {}, "sensitivity": {}}
    summary["parameters"]["noise_sigma_m"] = {"nominal": 0.0, "low": SE.NOISE_RANGE[0], "high": SE.NOISE_RANGE[1],
                                              "status": "ASSUMPTION", "basis": "spatially correlated DEM error, correlation 3 posts"}
    # ---- per-area nominal study --------------------------------------------------------------
    slope_rows, route_rows, oat_rows = [], [], []
    area_cache = {}
    for name, (tk, la0, la1, lo0, lo1, sep) in AREAS.items():
        dem = crop(tiles[tk], la0, la1, lo0, lo1)
        pairs = TR.select_od_pairs(dem, 10, OD_SEED, sep)
        sc = SE.Scenario(dem, SE.od_to_latlon(dem, pairs))
        eg = TR.precompute_edges(dem); g, fok = TR.build_graph(eg, nominal)
        for r in slope_stats(dem): r["area"] = name; slope_rows.append(r)
        reach, ratios, unreach = TR.reachability(dem, g, [p[0] for p in pairs], [p[1] for p in pairs])
        paths = []
        for k, (s_rc, d_rc) in enumerate(pairs):
            m, rc = TR.route_metrics(dem, g, s_rc, d_rc, eg, nominal); m.update(area=name, od=k); route_rows.append(m)
            if rc is not None and k < 3: paths.append(rc)
        summary["areas"][name] = {"shape": list(dem.shape), "dx_m": dem.dx, "dy_m": dem.dy, "blocked_edge_frac": 1 - fok,
                                  "reach_frac": reach, "median_cost_ratio": float(np.median(ratios)) if ratios else None,
                                  "unreachable_od": unreach, "n_od": len(pairs)}
        for r in SE.oat(sc, nominal): r["area"] = name; oat_rows.append(r)
        area_cache[name] = (dem, eg, g, paths)
        print(f"[{time.time()-t0:6.1f}s] {name}: blocked {1-fok:.4f}, cost ratio {summary['areas'][name]['median_cost_ratio']}")
    write_csv(os.path.join(a.out, "slope_stats.csv"), slope_rows)
    write_csv(os.path.join(a.out, "routes_nominal.csv"), route_rows)
    write_csv(os.path.join(a.out, "sensitivity_oat.csv"), oat_rows)
    # ---- global sensitivity on cores ---------------------------------------------------------
    lhs_all, rank_out = {}, {}
    for name, (tk, la0, la1, lo0, lo1, sep, seed) in CORES.items():
        dem = crop(tiles[tk], la0, la1, lo0, lo1)
        pairs = TR.select_od_pairs(dem, 8, OD_SEED, sep)
        sc = SE.Scenario(dem, SE.od_to_latlon(dem, pairs))
        _, rows = SE.global_lhs(sc, a.n_lhs, seed)
        lhs_all[name] = rows; rank_out[name] = SE.rank_sensitivity(rows)
        write_csv(os.path.join(a.out, f"sensitivity_lhs_{name}.csv"), rows)
        print(f"[{time.time()-t0:6.1f}s] LHS {name} done")
    summary["sensitivity"] = {"n_lhs": a.n_lhs, "rank": rank_out,
                              "oat_nominal_by_area": {r["area"]: {k: r[k] for k in SE.METRICS} for r in oat_rows if r["case"] == "nominal"}}
    # ---- published anchors -------------------------------------------------------------------
    anc = anchor_check(a.anchors)
    write_csv(os.path.join(a.out, "anchor_check.csv"), anc)
    summary["anchor_check"] = {"n": len(anc), "n_nominal_within_published": int(sum(r["nominal_abs_gap"] == 0 for r in anc)),
                               "median_nominal_abs_gap": float(np.median([r["nominal_abs_gap"] for r in anc])),
                               "n_envelope_overlaps": int(sum(r["envelope_overlaps_published"] for r in anc))}
    # crit-angle spread across the assumption space
    crit = np.array([r["crit_uphill_deg"] for rows in lhs_all.values() for r in rows])
    summary["crit_uphill_deg_across_lhs"] = {"min": float(crit.min()), "p05": float(np.percentile(crit, 5)), "median": float(np.median(crit)),
                                             "p95": float(np.percentile(crit, 95)), "max": float(crit.max())}
    # ---- figures -----------------------------------------------------------------------------
    figure_area(area_cache["A_south_Liwa"], "A_south_Liwa", nominal, a.out)
    figure_area(area_cache["B_RubAlKhali_megadunes"], "B_RubAlKhali_megadunes", nominal, a.out)
    figure_slope_hist(tiles, summary, a.out)
    figure_envelope(anc, a.out)
    figure_oat(oat_rows, a.out)
    figure_rank(rank_out, a.out)
    summary["runtime_s"] = round(time.time() - t0, 1)
    with open(os.path.join(a.out, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print("done in", summary["runtime_s"], "s")


def figure_area(cache, name, p, out):
    dem, eg, g, paths = cache
    ext = [0, dem.shape[1] * dem.dx / 1000, 0, dem.shape[0] * dem.dy / 1000]
    z = np.nan_to_num(dem.z, nan=np.nanmean(dem.z))
    hs, sl = hillshade(z, dem.dx, dem.dy), slope_deg(z, dem.dx, dem.dy)
    frac = TR.passable_heading_fraction(eg, p)
    crit = critical_uphill_deg(p)
    fig, ax = plt.subplots(2, 2, figsize=(13, 8.2), constrained_layout=True)
    ax = ax.ravel()
    ax[0].imshow(hs, cmap="gray", extent=ext); ax[0].set_title("a  Hillshade, Copernicus GLO-30")
    im = ax[1].imshow(sl, cmap="YlOrBr", vmin=0, vmax=35, extent=ext); ax[1].set_title(f"b  Slope, 30 m DEM (Horn); contour = {crit:.1f} deg")
    ax[1].contour(np.linspace(0, ext[1], sl.shape[1]), np.linspace(ext[3], 0, sl.shape[0]), sl, [crit], colors=[INK], linewidths=0.5)
    fig.colorbar(im, ax=ax[1], shrink=0.85, label="slope, deg")
    ax[2].imshow(hs, cmap="gray", extent=ext)
    blocked = np.ma.masked_where(frac >= 1.0, 1 - frac)
    im2 = ax[2].imshow(blocked, cmap="Oranges", vmin=0, vmax=1, extent=ext, alpha=0.95, interpolation="nearest")
    fig.colorbar(im2, ax=ax[2], shrink=0.85, label="share of 8 headings blocked")
    ax[2].set_title("c  Cells with any heading blocked (nominal model)")
    ax[3].imshow(hs, cmap="gray", extent=ext, alpha=0.9)
    cols = [BLUE, AQUA, ORANGE]
    for i, rc in enumerate(paths):
        xs, ys = rc[:, 1] * dem.dx / 1000, (dem.shape[0] - rc[:, 0]) * dem.dy / 1000
        ax[3].plot(xs, ys, color=cols[i], lw=1.6, label=f"route {i + 1}")
        ax[3].plot(xs[[0, -1]], ys[[0, -1]], "o", color=cols[i], ms=6, mec="white", mew=0.9)
    ax[3].legend(loc="upper right", fontsize=8, framealpha=0.9)
    ax[3].set_title("d  Three least-cost routes (nominal model)")
    for x in ax: x.set_xlabel("east, km"); x.set_ylabel("north, km"); x.grid(False)
    fig.suptitle(f"{name.replace('_', ' ')}: {SIM_LABEL}", fontsize=10, color="#52514e")
    _foot(fig); fig.savefig(os.path.join(out, "figures", f"fig_area_{name}.png"), dpi=140); plt.close(fig)


def rerender_area_figures(data, out):
    """Re-draw only the per-area map figures (same seeds and parameters as the full study)."""
    _style()
    tiles = {k: load_tile(os.path.join(data, f)) for k, f in TILES.items()}
    nominal = nominal_params()
    for name in ("A_south_Liwa", "B_RubAlKhali_megadunes"):
        tk, la0, la1, lo0, lo1, sep = AREAS[name]
        dem = crop(tiles[tk], la0, la1, lo0, lo1)
        pairs = TR.select_od_pairs(dem, 10, OD_SEED, sep)
        eg = TR.precompute_edges(dem); g, _ = TR.build_graph(eg, nominal)
        paths = [TR.route_metrics(dem, g, a, b, eg, nominal)[1] for a, b in pairs[:3]]
        figure_area((dem, eg, g, [p for p in paths if p is not None]), name, nominal, out)


def figure_slope_hist(tiles, summary, out):
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8), constrained_layout=True, sharey=True)
    cs = {1: BLUE, 2: ORANGE, 3: AQUA}; lab = {1: "30 m", 2: "60 m (block mean)", 3: "90 m (block mean)"}
    for ax, name in zip(axs, ("A_south_Liwa", "B_RubAlKhali_megadunes")):
        tk, la0, la1, lo0, lo1, _ = AREAS[name]
        dem = crop(tiles[tk], la0, la1, lo0, lo1)
        for k in (1, 2, 3):
            d = coarsen(dem, k); sl = slope_deg(np.nan_to_num(d.z, nan=np.nanmean(d.z)), d.dx, d.dy)
            h, e = np.histogram(sl.ravel(), bins=np.arange(0, 41, 1), weights=np.full(sl.size, 100.0 / sl.size))
            ax.step(e[:-1], np.maximum(h, 1e-4), where="post", color=cs[k], lw=1.6, label=lab[k])
        ax.axvspan(summary["crit_uphill_deg_across_lhs"]["p05"], summary["crit_uphill_deg_across_lhs"]["p95"], color=GREY, alpha=0.18, lw=0)
        ax.axvspan(32, 35, color=INK, alpha=0.08, lw=0)
        ax.set_yscale("log"); ax.set_xlabel("slope, deg"); ax.set_title(name.replace("_", " "))
        ax.text(0.97, 0.95, "grey band: critical uphill slope,\n5-95 % of assumption space\ndark band: published angle of repose 32-35 deg", transform=ax.transAxes, ha="right", va="top", fontsize=7, color="#52514e")
    axs[0].set_ylabel("% of cells per 1 deg bin"); axs[0].legend(loc="upper right")
    fig.suptitle(f"Slope distribution vs DEM posting: {SIM_LABEL}", fontsize=10, color="#52514e")
    _foot(fig); fig.savefig(os.path.join(out, "figures", "fig_slope_histograms.png"), dpi=140); plt.close(fig)


def figure_envelope(anc, out):
    b = SE.bounds(); u = qmc.LatinHypercube(d=4, seed=3).random(3000)
    P = {k: b[k][0] + u[:, i] * (b[k][1] - b[k][0]) for i, k in enumerate(("phi_deg", "f_r", "i0", "i_max"))}
    th = np.arange(0, 36, 0.5); S = np.empty((len(u), len(th)))
    for j, t in enumerate(np.radians(th)):
        x = np.abs(np.tan(t) + P["f_r"]) / np.tan(np.radians(P["phi_deg"]))
        S[:, j] = np.minimum(np.where(x < 1, -P["i0"] * np.log1p(-np.clip(x, 0, 0.999999)), np.inf), 1.0)
    fig, ax = plt.subplots(figsize=(8, 4.6), constrained_layout=True)
    ax.fill_between(th, np.percentile(S, 5, 0), np.percentile(S, 95, 0), color=BLUE, alpha=0.18, lw=0, label="model, 5-95 % of assumption space")
    ax.plot(th, [min(float(slip(np.tan(np.radians(t)), 0, nominal_params())), 1) for t in th], color=BLUE, lw=2, label="model, nominal parameters")
    for r in anc:
        c, m = (ORANGE, "o") if r["validation_type"] == "field" else (AQUA, "s")
        ax.plot([r["slope_deg"]] * 2, [r["published_slip_lo"], r["published_slip_hi"]], color=c, lw=1.6)
        ax.plot(r["slope_deg"], 0.5 * (r["published_slip_lo"] + r["published_slip_hi"]), m, color=c, ms=6, mec="white", mew=0.8)
    ax.plot([], [], "o", color=ORANGE, label="published, field (Mars rovers)"); ax.plot([], [], "s", color=AQUA, label="published, lab beds")
    ax.set_xlabel("direct-ascent slope, deg"); ax.set_ylabel("slip (1 = no progress)"); ax.set_ylim(-0.02, 1.05)
    ax.set_title("Published slip at similar slopes spans nearly 0 to 1; no single curve fits"); ax.legend(loc="upper left", fontsize=8)
    fig.text(0.01, 0.045, "Comparison only, nothing fitted. Slip definitions, gravity, wheels and soils differ between points (see data/anchor_points.csv).", fontsize=7, color="#52514e")
    _foot(fig, 0.10); fig.savefig(os.path.join(out, "figures", "fig_slip_vs_slope_envelope.png"), dpi=140); plt.close(fig)


def figure_oat(rows, out):
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), constrained_layout=True)
    for ax, (metric, title) in zip(axs, (("blocked_edge_frac", "Blocked share of edges (area A south)"), ("median_cost_ratio", "Median route cost / straight distance (area A south)"))):
        sub = [r for r in rows if r["area"] == "A_south_Liwa"]
        nom = [r for r in sub if r["case"] == "nominal"][0][metric]
        items = [(f"{r['case']}", r[metric]) for r in sub if r["case"] != "nominal"]
        items.sort(key=lambda t: abs(t[1] - nom))
        y = np.arange(len(items))
        ax.barh(y, [v - nom for _, v in items], left=nom, color=[BLUE if v >= nom else ORANGE for _, v in items], height=0.55)
        ax.axvline(nom, color=INK, lw=0.8); ax.set_yticks(y); ax.set_yticklabels([n for n, _ in items], fontsize=7.5)
        ax.set_title(title); ax.set_xlabel(metric.replace("_", " "))
    fig.suptitle(f"One-at-a-time sensitivity, change from nominal (vertical line): {SIM_LABEL}", fontsize=10, color="#52514e")
    _foot(fig); fig.savefig(os.path.join(out, "figures", "fig_sensitivity_oat.png"), dpi=140); plt.close(fig)


def figure_rank(rank_out, out):
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.9), constrained_layout=True, sharey=True)
    labels = {"phi_deg": "friction angle", "f_r": "motion resistance", "i0": "slip scale i0", "i_max": "slip limit", "noise_sigma_m": "DEM noise"}
    for ax, metric in zip(axs, ("blocked_edge_frac", "median_cost_ratio")):
        y = np.arange(len(SE.CONTINUOUS)); w = 0.38
        for j, (core, c) in enumerate((("A_core", BLUE), ("B_core", ORANGE))):
            d = rank_out[core].get(metric, {})
            v = [d.get("spearman", {}).get(k, 0.0) for k in SE.CONTINUOUS]
            ax.barh(y + (j - 0.5) * w, v, height=w, color=c, label=core.replace("_", " "))
        ax.axvline(0, color=INK, lw=0.8); ax.set_yticks(y); ax.set_yticklabels([labels[k] for k in SE.CONTINUOUS])
        ax.set_xlabel("Spearman rank correlation"); ax.set_title(metric.replace("_", " ")); ax.set_xlim(-1, 1)
    axs[0].legend(loc="upper right")
    fig.suptitle(f"Global sensitivity (Latin hypercube): {SIM_LABEL}", fontsize=10, color="#52514e")
    _foot(fig); fig.savefig(os.path.join(out, "figures", "fig_sensitivity_rank.png"), dpi=140); plt.close(fig)


if __name__ == "__main__":
    main()
