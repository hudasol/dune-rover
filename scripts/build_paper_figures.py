#!/usr/bin/env python3
"""Figures of the conference paper and its supplement (paper/figures/*.pdf), from the stage 27 and 28 result files and caches.

    PYTHONPATH=src python3 scripts/build_paper_figures.py

Palette checked with a colour vision deficiency validator (plum, rose and sakura, with marker shapes as a second cue).
SIMULATED BY ME on PUBLISHED elevation data.
"""
from __future__ import annotations
import csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dunerover import benchmark as B  # noqa: E402
from dunerover.terrain import hillshade  # noqa: E402

FIG = os.path.join(ROOT, "paper", "figures")
DET = os.path.join(ROOT, "results", "benchmark", "detection")
PLN = os.path.join(ROOT, "results", "benchmark", "planning")
INK, PEARL = "#2B2024", "#FBF3F6"
INPUT_STYLE = {"I10": ("#7B4FA0", "o", "10 m block mean"), "I30": ("#D0336E", "s", "30 m block mean"),
               "G30": ("#E58AAE", "^", "GLO-30 (real)")}
METHOD_ORDER = ("DET", "SLOPE", "TRI", "ROUGH", "BICUBIC", "GBM", "CNN")
METHOD_LABEL = {"DET": "Detector (ours)", "SLOPE": "Slope", "TRI": "Ruggedness (TRI)", "ROUGH": "Plane roughness",
                "BICUBIC": "Cubic interpolation", "GBM": "Gradient boosting*", "CNN": "Convolutional net*"}
SITE_LABEL = {"Dumont": "Dumont", "WhiteSands": "White Sands", "Kelso": "Kelso", "GreatSandDunes": "Great Sand Dunes",
              "Algodones": "Algodones", "LittleSahara": "Little Sahara"}

plt.rcParams.update({"font.family": "serif", "font.size": 7.5, "axes.edgecolor": "#6E5763", "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK, "axes.linewidth": 0.6, "pdf.fonttype": 42})


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def fig_map(site="Kelso"):
    """Example site for the supplement: lidar face patches, two 30 m hazard layers and routes of two planners."""
    import json
    import matplotlib.patheffects as pe
    import benchmark_detection as BD
    import benchmark_stage28 as S28
    from dunerover import planner as PL
    L = np.load(os.path.join(ROOT, "data", "cache", "stage27", "layers_L-ANY.npz"))
    fname, win, _ = BD.SITES[site]
    z1, _, _, _ = BD.load_lidar_window(fname, win)
    void = np.isnan(z1); z1f = B.fill_nearest(z1)
    steep, _ = B.steep_posts(z1, void)
    patch = B.face_patches(steep)
    hs = hillshade(z1f, 1.0, 1.0)
    ext = [0, z1.shape[1], z1.shape[0], 0]
    plum = "#6A3D8F"
    pink = LinearSegmentedColormap.from_list("pk", ["#FBF3F6", "#E58AAE", "#C2185B", "#4A2A66"])
    fig, axes = plt.subplots(1, 4, figsize=(7.1, 2.6), gridspec_kw={"wspace": 0.05})
    ov = np.ma.masked_where(~patch, np.ones_like(hs))
    axes[0].imshow(hs, cmap="gray", extent=ext, interpolation="nearest")
    axes[0].imshow(ov, cmap=ListedColormap([plum]), extent=ext, alpha=0.9, interpolation="nearest")
    axes[0].set_title("(a) lidar, face patches", fontsize=7)
    for ax, key_, title in ((axes[1], "BICUBIC-cal", "(b) interpolation, 30 m"), (axes[2], "GBM", "(c) boosting, 30 m")):
        p = L[f"{site}|I30|{key_}"]
        ax.imshow(hs, cmap="gray", extent=ext, interpolation="nearest")
        im = ax.imshow(p, cmap=pink, vmin=0, vmax=1, extent=[0, p.shape[1] * 30, p.shape[0] * 30, 0], alpha=0.8, interpolation="nearest")
        ax.set_title(title, fontsize=7)
    ax = axes[3]
    ax.imshow(hs, cmap="gray", extent=ext, interpolation="nearest")
    ax.imshow(ov, cmap=ListedColormap([plum]), extent=ext, alpha=0.9, interpolation="nearest")
    zc = B.block(z1f, 30)
    a = PL.assess(PL.raster_from_array(zc, 30.0), profile=PL.builtin_profile("published-posterior"), n_draws=128)
    pairs = S28.endpoints_E1(site)[:6]
    shape = a.classes.shape
    g0, _ = S28.base_graph(a, False); g1, _ = S28.base_graph(a, True)
    h = L[f"{site}|I30|GBM"].astype(float)[:shape[0], :shape[1]]
    keep = ((a.classes != 1) & (a.classes != 5)).ravel()
    S = [S28.BP.cell_of(q[0], 30, shape) for q in pairs]; T = [S28.BP.cell_of(q[1], 30, shape) for q in pairs]
    for g, col, ls, lab in ((S28.masked(g0, a.classes != 5), "#E58AAE", "--", "slip model only"), (S28.masked(g1, keep, h, 100.0), "#C2185B", "-", "boosting, weight")):
        for n, rc in enumerate(B.routes_from(g, shape[1], S, T)):
            if rc is None:
                continue
            xy = (rc + 0.5) * 30
            ax.plot(xy[:, 1], xy[:, 0], color=col, lw=1.3, ls=ls, label=lab if n == 0 else None,
                    path_effects=[pe.Stroke(linewidth=2.4, foreground="white"), pe.Normal()])
    ax.set_title("(d) 30 m routes", fontsize=7)
    ax.legend(loc="upper left", fontsize=5.5, frameon=True, framealpha=0.9, handlelength=1.6, borderpad=0.3, labelspacing=0.2)
    for ax in axes:
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_xlim(0, z1.shape[1]); ax.set_ylim(z1.shape[0], 0)
    fig.canvas.draw()
    p1, p2 = axes[1].get_position(), axes[2].get_position()
    cax = fig.add_axes([p1.x0 + 0.1 * (p2.x1 - p1.x0), p1.y0 - 0.07, 0.8 * (p2.x1 - p1.x0), 0.025])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal", ticks=[0, 0.5, 1])
    cb.set_label("face probability", fontsize=6, labelpad=1); cb.ax.tick_params(labelsize=5.5, length=2, pad=1)
    axes[0].plot([100, 1100], [z1.shape[0] - 120] * 2, color=INK, lw=2.2)
    axes[0].text(600, z1.shape[0] - 230, "1 km", color=INK, ha="center", va="bottom", fontsize=6.5,
                 bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    axes[0].annotate("N", xy=(z1.shape[1] - 250, 150), xytext=(z1.shape[1] - 250, 650), ha="center", fontsize=6.5, color=INK,
                     arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8), bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))
    fig.savefig(os.path.join(FIG, "fig_map.pdf"), metadata={"CreationDate": None}, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(os.path.join(FIG, "fig_map.png"), dpi=170, bbox_inches="tight", pad_inches=0.02, facecolor="white"); plt.close(fig)


S27 = os.path.join(ROOT, "results", "benchmark", "stage27")
S28 = os.path.join(ROOT, "results", "benchmark", "stage28")
SWEEP_STYLE = {"SLOPE": ("#8A7A82", "v", "Slope"), "DET": ("#E58AAE", "^", "Synthetic detector"),
               "BICUBIC": ("#C2185B", "s", "Cubic interpolation"), "GBM": ("#6A3D8F", "o", "Gradient boosting*")}


def fig_resolution():
    """(a) macro mean AUC against the posting; (b) pooled patch recall against face length over grid spacing."""
    mac = read(os.path.join(S27, "C_macro.csv"))
    sca = read(os.path.join(S27, "C_scaling.csv"))
    fig, axs = plt.subplots(1, 2, figsize=(3.45, 1.75), gridspec_kw={"wspace": 0.42})
    ax = axs[0]
    for m, (col, mk, lab) in SWEEP_STYLE.items():
        rr = sorted([r for r in mac if r["method"] == m], key=lambda r: float(r["posting_m"]))
        x = [float(r["posting_m"]) for r in rr]; y = [float(r["auc"]) for r in rr]
        ax.plot(x, y, color=col, lw=1.0); ax.scatter(x, y, s=10, marker=mk, color=col, edgecolors=INK, linewidths=0.3, zorder=3, label=lab)
    from matplotlib.ticker import NullFormatter
    ax.set_xscale("log"); ax.set_xticks([2, 5, 10, 30, 60]); ax.set_xticklabels(["2", "5", "10", "30", "60"]); ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("grid spacing (m)"); ax.set_ylabel("mean AUC (face map label)")
    ax.set_ylim(0.5, 1.0); ax.grid(color="#EFE3E8", lw=0.5); ax.set_axisbelow(True)
    ax.text(0.03, 0.04, "(a)", transform=ax.transAxes, fontsize=7, ha="left", va="bottom")
    ax = axs[1]
    bins = ["0 to 0.5", "0.5 to 1", "1 to 2", "2 to 4", "4 to 8", "8 to inf"]
    centres = [0.35, 0.7, 1.4, 2.8, 5.6, 11.3]
    by_site = read(os.path.join(S27, "C_scaling_by_site.csv"))
    shades = {10: ("#E58AAE", "o"), 20: ("#C2185B", "s"), 30: ("#9C6ADE", "^"), 60: ("#6A3D8F", "D")}
    for d, (col, mk) in shades.items():
        x, y = [], []
        for b_, c in zip(bins, centres):
            rr = [r for r in by_site if r["method"] == "GBM" and int(float(r["posting_m"])) == d and r["ratio_bin"] == b_]
            n = sum(int(r["patches"]) for r in rr)
            if n >= 50:
                x.append(c); y.append(sum(int(r["detected"]) for r in rr) / n)
        ax.plot(x, y, color=col, lw=1.0); ax.scatter(x, y, s=10, marker=mk, color=col, edgecolors=INK, linewidths=0.3, zorder=3, label=f"{d} m")
    ax.set_xscale("log"); ax.set_xticks([0.5, 1, 2, 4, 8]); ax.set_xticklabels(["0.5", "1", "2", "4", "8"]); ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("face length / grid spacing"); ax.set_ylabel("faces found (boosting*)")
    ax.set_ylim(0.3, 1.02); ax.grid(color="#EFE3E8", lw=0.5); ax.set_axisbelow(True)
    ax.text(0.03, 0.96, "(b)", transform=ax.transAxes, fontsize=7, ha="left", va="top")
    ax.legend(loc="lower right", fontsize=5.6, frameon=False, handletextpad=0.15, labelspacing=0.2)
    for a in axs:
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    axs[0].legend(loc="lower center", bbox_to_anchor=(1.15, 1.10), ncol=4, frameon=False, fontsize=5.6, handletextpad=0.15, columnspacing=0.7)
    fig.savefig(os.path.join(FIG, "fig_resolution.pdf"), metadata={"CreationDate": None}, bbox_inches="tight", pad_inches=0.02); plt.close(fig)


FRONT_STYLE = {"none": ("#8A7A82", "D", "Slip model only"), "DET": ("#E58AAE", "^", "Synthetic detector"),
               "BICUBIC-cal": ("#C2185B", "s", "Cubic interpolation"), "GBM": ("#6A3D8F", "o", "Gradient boosting*"),
               "DEM+S2": ("#9C6ADE", "P", "Boosting + Sentinel-2*"), "FACEMAP": (INK, "*", "Face map (upper bound)")}


def fig_frontier():
    """Mission success against the risk weight of the weight policy, per hazard layer (gate results are in the text)."""
    from matplotlib.ticker import NullFormatter
    rows = [r for r in read(os.path.join(S28, "A_sweep.csv")) if r["profile"] == "published-posterior" and r["endpoints"] == "E1"]
    fig, axs = plt.subplots(1, 2, figsize=(3.45, 1.95), sharey=True, gridspec_kw={"wspace": 0.08})
    for ax, inp in zip(axs, ("I10", "I30")):
        nv = next(r for r in rows if r["input"] == inp and r["policy"] == "naive")
        ax.axhline(float(nv["mission_success"]), color="#8A7A82", lw=0.9, ls="--", label="Slip model only" if inp == "I10" else None)
        for lay, (col, mk, lab) in FRONT_STYLE.items():
            if lay == "none":
                continue
            rr = sorted([r for r in rows if r["input"] == inp and r["layer"] == lay and r["policy"] == "risk_weighted"], key=lambda r: float(r["param"]))
            if not rr:
                continue
            x = [float(r["param"]) for r in rr]; y = [float(r["mission_success"]) for r in rr]
            ax.plot(x, y, color=col, lw=0.9)
            ax.scatter(x, y, s=9 if lay != "FACEMAP" else 16, marker=mk, color=col, edgecolors=INK, linewidths=0.25, zorder=3, label=lab if inp == "I10" else None)
        ax.set_xscale("log"); ax.set_xticks([1, 10, 100]); ax.set_xticklabels(["1", "10", "100"]); ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_title("10 m map" if inp == "I10" else "30 m map", fontsize=7)
        ax.set_xlabel("risk weight $w$"); ax.set_ylim(0, 0.9)
        ax.grid(color="#EFE3E8", lw=0.5); ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axs[0].set_ylabel("mission success")
    axs[0].legend(loc="lower center", bbox_to_anchor=(1.04, 1.12), ncol=3, frameon=False, fontsize=5.6, handletextpad=0.15, columnspacing=0.7)
    fig.savefig(os.path.join(FIG, "fig_frontier.pdf"), metadata={"CreationDate": None}, bbox_inches="tight", pad_inches=0.02); plt.close(fig)

def main():
    os.makedirs(FIG, exist_ok=True)
    if os.path.exists(os.path.join(ROOT, "data", "cache", "stage27", "layers_L-ANY.npz")):
        fig_map()
    if os.path.exists(os.path.join(S27, "C_macro.csv")):
        fig_resolution()
    if os.path.exists(os.path.join(S28, "A_sweep.csv")):
        fig_frontier()
    print("figures in", FIG)


if __name__ == "__main__":
    main()
