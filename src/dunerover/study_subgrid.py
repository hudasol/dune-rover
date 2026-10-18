"""Phase 2 study: sub-grid slip face probability, three class maps, Monte Carlo robustness, three areas.

    python -m dunerover.study_subgrid --data data/raw --out results/subgrid

Everything written is SIMULATION ONLY, model-assumption dependent.  Seeds: Monte Carlo draws 20261014
(area A), 20261015 (B), 20261016 (C); detector training 20261014; detector test 777; OD selection 20261011.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, platform, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from . import SIM_LABEL, __version__
from .dem import load_tile, crop, coarsen
from .slipmodel import SlipParams, apply_range_set, nominal_params
from . import traverse as TR
from . import subgrid as SG
from . import threeclass as TC
from .sensitivity import od_to_latlon

OD_SEED = 20261011
N_DRAWS = 256
TILES = {"A": "Copernicus_DSM_COG_10_N23_00_E053_00_DEM.tif", "B": "Copernicus_DSM_COG_10_N22_00_E054_00_DEM.tif",
         "C": "Copernicus_DSM_COG_10_N20_00_E052_00_DEM.tif"}
AREAS = {  # name: (tile, lat_min, lat_max, lon_min, lon_max, od_sep_m, mc_seed, description)
    "A_south_Liwa": ("A", 23.02, 23.17, 53.55, 53.95, 15000, 20261014, "Liwa, UAE: large crescentic and star dunes (phase 1 window A south)"),
    "B_RubAlKhali_megadunes": ("B", 22.20, 22.50, 54.20, 54.60, 15000, 20261015, "Rub' al Khali, UAE: megadunes (phase 1 window B)"),
    "C_RubAlKhali_linear": ("C", 20.40, 20.55, 52.30, 52.70, 15000, 20261016, "Rub' al Khali, Saudi Arabia (not UAE): linear dunes; added in phase 2 as a morphology contrast"),
}
PALETTE = {0: "#a9cdbd", 1: "#7a1f45", 2: "#a98fd1", 3: "#ee7aa8", 4: "#5b3a78"}
SCENARIO_GRID = [("base", 1.0), ("base", 0.6), ("base", 0.3), ("gentle", 1.0), ("steep", 1.0)]
TAUS = [0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 0.80]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path, rows):
    keys = []
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)


def _style():
    plt.rcParams.update({"figure.facecolor": "#fffafb", "axes.facecolor": "#fffafb", "axes.edgecolor": "#d8c3cb", "axes.labelcolor": "#4a3a40",
                         "xtick.color": "#4a3a40", "ytick.color": "#4a3a40", "text.color": "#2b2024", "axes.spines.top": False,
                         "axes.spines.right": False, "axes.grid": True, "grid.color": "#f0e1e6", "grid.linewidth": 0.6, "font.size": 9,
                         "axes.titlesize": 10, "axes.titleweight": "bold", "legend.frameon": False})


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw"); ap.add_argument("--out", default="results/subgrid"); ap.add_argument("--n-draws", type=int, default=N_DRAWS)
    ap.add_argument("--range-set", default="original", help="parameter range set from slipmodel.RANGE_SETS (default: original)")
    a = ap.parse_args(argv)
    apply_range_set(a.range_set)
    os.makedirs(os.path.join(a.out, "figures"), exist_ok=True)
    _style(); t0 = time.time()
    tiles = {k: load_tile(os.path.join(a.data, f)) for k, f in TILES.items()}
    nominal = nominal_params()
    models: dict = {}

    def model_for(dm, scn, pi, sampling="box", fp=1):
        key = (round(dm, 1), scn, pi, sampling, fp)
        if key not in models:
            models[key] = SG.fit(round(dm, 1), scn, pi, sampling, footprint=fp)
        return models[key]

    summary = {"label": SIM_LABEL, "range_set": a.range_set, "version": __version__, "python": platform.python_version(), "n_draws": a.n_draws,
               "seeds": {"od": OD_SEED, "mc": {k: v[6] for k, v in AREAS.items()}, "detector_train": 20261014, "detector_test": 777},
               "inputs": {k: {"file": f, "sha256": sha256(os.path.join(a.data, f))} for k, f in TILES.items()},
               "rules": {"pass_headings": TC.PASS_HEADINGS, "q_lo": TC.Q_LO, "q_hi": TC.Q_HI, "tau": TC.TAU, "face_truth_deg": SG.FACE_TRUTH_DEG},
               "areas": {}}
    shares_rows, scen_rows, cc_map_rows, reach_rows, robust_rows, det_rows = [], [], [], [], [], []
    keep = {}; dms = set()
    for name, (tk, la0, la1, lo0, lo1, sep, seed, desc) in AREAS.items():
        base = crop(tiles[tk], la0, la1, lo0, lo1)
        pairs = TR.select_od_pairs(base, 10, OD_SEED, sep)
        od_ll = od_to_latlon(base, pairs)
        summary["areas"][name] = {"description": desc, "shape_30m": list(base.shape), "relief_m": float(np.nanmax(base.z) - np.nanmin(base.z))}
        draws = TC.lhs_draws(a.n_draws, seed)
        for k in (1, 2, 3):
            dem = coarsen(base, k); dm = 0.5 * (dem.dx + dem.dy); dms.add(round(dm, 1))
            eg = TR.precompute_edges(dem)
            q = TC.q_pass(eg, draws)
            F = SG.features_2d(np.nan_to_num(dem.z, nan=np.nanmean(dem.z)), dem.dx, dem.dy)
            m0 = model_for(dm, "base", 1.0)
            p0 = m0.predict(F)
            cls = TC.classify(q, p0)
            sh = TC.shares(cls)
            row = {"area": name, "posting_m": round(dm, 1), "block": k, "cells": int(cls.size), "model": "base, pi=1.0", **sh}
            shares_rows.append(row)
            # robustness to the four assumed parameters (slope based only, no sub-grid)
            uni = float(((q <= TC.Q_LO) | (q >= TC.Q_HI)).mean())
            robust_rows.append({"area": name, "posting_m": round(dm, 1), "unanimous_share": uni, "sensitive_share": 1 - uni,
                                "always_passable_share(q=1)": float((q >= 1.0).mean()), "never_passable_share(q=0)": float((q <= 0.0).mean()),
                                "q_pass_median": float(np.median(q)), "q_pass_p05": float(np.percentile(q, 5))})
            # sub-grid prior sensitivity
            for scn, pi in SCENARIO_GRID:
                p = model_for(dm, scn, pi).predict(F)
                c2 = TC.classify(q, p)
                scen_rows.append({"area": name, "posting_m": round(dm, 1), "scenario": scn, "pi": pi, **TC.shares(c2), "mean_face_probability": float(p.mean())})
            # POST HOC variant (added after the baseline result was seen): a face within one post of the cell counts
            pf3 = model_for(dm, "base", 1.0, "box", 3).predict(F)
            scen_rows.append({"area": name, "posting_m": round(dm, 1), "scenario": "POST HOC: face within +/-1 post (3-post footprint)", "pi": 1.0,
                              **TC.shares(TC.classify(q, pf3)), "mean_face_probability": float(pf3.mean())})
            if k == 1:   # point sampling variant
                pp = model_for(dm, "base", 1.0, "point").predict(F)
                scen_rows.append({"area": name, "posting_m": round(dm, 1), "scenario": "base, point sampling", "pi": 1.0, **TC.shares(TC.classify(q, pp)),
                                  "mean_face_probability": float(pp.mean())})
            for r in TC.coverage_certainty_map(q, p0, TAUS):
                cc_map_rows.append({"area": name, "posting_m": round(dm, 1), **r})
            # reachability with UNKNOWN impassable (nominal parameters)
            src = [dem.rowcol(*x[0]) for x in od_ll]; dst = [dem.rowcol(*x[1]) for x in od_ll]
            reach_open, _ = None, None
            from scipy.sparse.csgraph import dijkstra
            g, frac = TR.build_graph(eg, nominal)
            nc = dem.shape[1]
            D = dijkstra(g, directed=True, indices=[r * nc + c for r, c in src])
            reach_open = float(np.mean([np.isfinite(D[i, d[0] * nc + d[1]]) for i, d in enumerate(dst)]))
            reach_closed, bad_end = TC.reachability_unknown_impassable(eg, cls, nominal, (src, dst), nc)
            reach_rows.append({"area": name, "posting_m": round(dm, 1), "pairs": len(src), "reachable_phase1_rule": reach_open,
                               "reachable_unknown_impassable": reach_closed, "endpoints_not_traversable": bad_end})
            if k == 1:
                keep[name] = (dem, cls, q, p0)
            print(f"{name} {dm:.1f} m  TRAV {sh['TRAVERSABLE']:.3f} BLOCKED {sh['BLOCKED']:.4f} UNKNOWN {sh['UNKNOWN (total)']:.3f}  [{time.time()-t0:.0f}s]", flush=True)
    # detector skill (synthetic truth), per posting present in the study, base prior and cross-prior tests
    for dm in sorted(dms):
        m = model_for(dm, "base", 1.0)
        for tscn, tpi in (("base", 1.0), ("gentle", 1.0), ("steep", 1.0), ("base", 0.3)):
            e = SG.evaluate_detector(m, scn=tscn, pi=tpi)
            det_rows.append({"posting_m": dm, "trained_on": "base pi=1.0", "tested_on": f"{tscn} pi={tpi}", "face_rate": e["face_rate"], "auc": e["auc"],
                             "brier": e["brier"], "brier_climatology": e["brier_climatology"]})
        for r in SG.coverage_certainty(m, TAUS):
            det_rows.append({"posting_m": dm, "trained_on": "base pi=1.0", "tested_on": "base pi=1.0 (coverage vs certainty)", **r})
        summary.setdefault("reliability", {})[str(dm)] = SG.evaluate_detector(m)["reliability"]
    # figures
    _fig_maps(keep, a.out)
    _fig_unknown_by_resolution(shares_rows, a.out)
    _fig_coverage(cc_map_rows, det_rows, a.out)
    _fig_reliability(summary["reliability"], a.out)
    write_csv(os.path.join(a.out, "class_shares.csv"), shares_rows)
    write_csv(os.path.join(a.out, "robustness_to_assumed_parameters.csv"), robust_rows)
    write_csv(os.path.join(a.out, "subgrid_prior_sensitivity.csv"), scen_rows)
    write_csv(os.path.join(a.out, "coverage_vs_certainty_map.csv"), cc_map_rows)
    write_csv(os.path.join(a.out, "detector_skill.csv"), det_rows)
    write_csv(os.path.join(a.out, "reachability_unknown_impassable.csv"), reach_rows)
    summary["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(a.out, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print("done", summary["seconds"], "s")


def _foot(fig):
    fig.text(0.01, 0.005, SIM_LABEL + ". Copernicus GLO-30 (c) DLR/Airbus; processing by this repo.", fontsize=7, color="#4a3a40")


def _fig_maps(keep, out):
    fig, axs = plt.subplots(len(keep), 1, figsize=(11, 3.6 * len(keep)), layout="constrained")
    cm = ListedColormap([PALETTE[i] for i in range(5)])
    for ax, (name, (dem, cls, q, p)) in zip(np.atleast_1d(axs), keep.items()):
        ax.imshow(cls, cmap=cm, vmin=-0.5, vmax=4.5, interpolation="nearest", aspect="equal")
        sh = TC.shares(cls)
        ax.set_title(f"{name}, 30 m: TRAVERSABLE {100*sh['TRAVERSABLE']:.1f} %, BLOCKED {100*sh['BLOCKED']:.2f} %, UNKNOWN {100*sh['UNKNOWN (total)']:.1f} %")
        ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    np.atleast_1d(axs)[0].legend(handles=[Patch(color=PALETTE[i], label=TC.CODES[i]) for i in range(5)], ncols=3, loc="upper center", bbox_to_anchor=(0.5, 1.35))
    _foot(fig); fig.savefig(os.path.join(out, "figures", "fig_three_class_maps.png"), dpi=110); plt.close(fig)


def _fig_unknown_by_resolution(rows, out):
    fig, ax = plt.subplots(figsize=(7.5, 4), layout="constrained")
    areas = list(dict.fromkeys(r["area"] for r in rows)); w = 0.25
    cols = ["#e8a5bb", "#c9769a", "#8a3a63"]
    x = np.arange(len(areas))
    for i, k in enumerate((1, 2, 3)):
        vals = [100 * next(r["UNKNOWN (total)"] for r in rows if r["area"] == ar and r["block"] == k) for ar in areas]
        ax.bar(x + (i - 1) * w, vals, w, label=f"{[30, 60, 90][i]} m (block mean {k})", color=cols[i])
        for xi, v in zip(x + (i - 1) * w, vals): ax.text(xi, v + 1, f"{v:.0f}", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels([a.replace("_", " ") for a in areas], fontsize=8); ax.set_ylabel("UNKNOWN share of cells, %"); ax.set_ylim(0, 105)
    ax.set_title("UNKNOWN share by DEM posting"); ax.legend()
    _foot(fig); fig.savefig(os.path.join(out, "figures", "fig_unknown_by_resolution.png"), dpi=110); plt.close(fig)


def _fig_coverage(cc_map, det, out):
    fig, axs = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    cols = {"A_south_Liwa": "#c9769a", "B_RubAlKhali_megadunes": "#8a3a63", "C_RubAlKhali_linear": "#6fa28f"}
    for ar, c in cols.items():
        rr = [r for r in cc_map if r["area"] == ar and r["posting_m"] < 40]
        axs[0].plot([r["tau"] for r in rr], [100 * r["coverage"] for r in rr], marker="o", color=c, label=ar.replace("_", " "))
    axs[0].set_xlabel("face probability threshold tau"); axs[0].set_ylabel("coverage (not UNKNOWN), %"); axs[0].set_title("Real maps at 30 m: coverage versus tau"); axs[0].legend(fontsize=7)
    for dm, ls in ((29.7, "-"), (59.4, "--"), (89.1, ":")):
        rr = [r for r in det if r["tested_on"].endswith("(coverage vs certainty)") and abs(r["posting_m"] - dm) < 1.6]
        if rr:
            axs[1].plot([100 * r["coverage"] for r in rr], [100 * r["certainty"] for r in rr], marker="o", ls=ls, color="#a8325e", label=f"{rr[0]['posting_m']} m")
    axs[1].set_xlabel("coverage on synthetic truth, %"); axs[1].set_ylabel("certainty: declared face-free cells that are truly face-free, %"); axs[1].set_title("Synthetic ensemble (known truth)"); axs[1].legend()
    _foot(fig); fig.savefig(os.path.join(out, "figures", "fig_coverage_vs_certainty.png"), dpi=110); plt.close(fig)


def _fig_reliability(rel, out):
    fig, ax = plt.subplots(figsize=(4.6, 4.4), layout="constrained")
    for (dm, r), c in zip(rel.items(), ["#c9769a", "#8a3a63", "#6fa28f", "#e8a5bb"]):
        if r:
            ax.plot([x[0] for x in r], [x[1] for x in r], marker="o", color=c, label=f"{dm} m")
    ax.plot([0, 1], [0, 1], color="#999", lw=1)
    ax.set_xlabel("predicted face probability"); ax.set_ylabel("observed face frequency (synthetic)"); ax.set_title("Detector reliability, held out"); ax.legend(fontsize=7)
    _foot(fig); fig.savefig(os.path.join(out, "figures", "fig_detector_reliability.png"), dpi=110); plt.close(fig)


if __name__ == "__main__":
    main()
