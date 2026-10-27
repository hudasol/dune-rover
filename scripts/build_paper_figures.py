#!/usr/bin/env python3
"""Figures of the conference paper (paper/figures/*.pdf), from the stage 25 and 26 result files and score cache.

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


def fig_auc():
    rows = read(os.path.join(DET, "metrics.csv"))
    methods = [m for m in METHOD_ORDER if any(r["method"] == m for r in rows)]
    fig, ax = plt.subplots(figsize=(3.45, 2.5))
    for j, (inp, (col, mk, lab)) in enumerate(INPUT_STYLE.items()):
        for i, m in enumerate(methods):
            v = np.array([float(r["auc"]) for r in rows if r["input"] == inp and r["method"] == m])
            if not len(v):
                continue
            y = i + (j - 1) * 0.24
            ax.plot([v.min(), v.max()], [y, y], color=col, lw=1.0, alpha=0.8, solid_capstyle="round")
            ax.scatter(v, np.full(len(v), y), s=5, color=col, alpha=0.55, linewidths=0, zorder=2)
            ax.scatter([v.mean()], [y], s=26, marker=mk, color=col, edgecolors=INK, linewidths=0.5, zorder=3,
                       label=lab if i == 0 else None)
    ax.set_yticks(range(len(methods))); ax.set_yticklabels([METHOD_LABEL[m] for m in methods])
    ax.invert_yaxis()
    ax.axvline(0.5, color="#B8A8B0", lw=0.6, ls=":")
    ax.set_xlabel("AUC against one metre lidar truth (six fields)")
    ax.set_xlim(0.45, 1.0)
    ax.grid(axis="x", color="#EFE3E8", lw=0.5); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=3, frameon=False, fontsize=6.3, handletextpad=0.2, columnspacing=0.9)
    fig.tight_layout(pad=0.3)
    fig.savefig(os.path.join(FIG, "fig_auc.pdf"), metadata={"CreationDate": None}, bbox_inches="tight", pad_inches=0.02); plt.close(fig)


def fig_map(site="Kelso"):
    import benchmark_detection as BD
    cache = np.load(os.path.join(ROOT, "data", "cache", "benchmark_scores.npz"))
    routes = np.load(os.path.join(ROOT, "data", "cache", "benchmark_routes.npz"))
    fname, win, _ = BD.SITES[site]
    z1, _, _, _ = BD.load_lidar_window(fname, win)
    void = np.isnan(z1); z1f = B.fill_nearest(z1)
    steep, _ = B.steep_posts(z1, void)
    patch = B.face_patches(steep)
    hs = hillshade(z1f, 1.0, 1.0)
    ext = [0, z1.shape[1], z1.shape[0], 0]
    pink = LinearSegmentedColormap.from_list("pk", ["#FBF3F6", "#E58AAE", "#D0336E", "#5B3A78"])
    fig, axes = plt.subplots(1, 4, figsize=(7.1, 1.75), gridspec_kw={"wspace": 0.04})
    ax = axes[0]
    ax.imshow(hs, cmap="gray", extent=ext, interpolation="nearest")
    ov = np.ma.masked_where(~patch, np.ones_like(hs))
    ax.imshow(ov, cmap=ListedColormap(["#D0336E"]), extent=ext, alpha=0.85, interpolation="nearest")
    ax.set_title("(a) lidar and face patches", fontsize=7)
    for ax, key, title in ((axes[1], "DET", "(b) detector (ours), 30 m"), (axes[2], "GBM", "(c) gradient boosting, 30 m")):
        p = cache[f"{site}|I30|{key}"]
        ax.imshow(hs, cmap="gray", extent=ext, interpolation="nearest")
        im = ax.imshow(p, cmap=pink, vmin=0, vmax=1, extent=[0, p.shape[1] * 30, p.shape[0] * 30, 0], alpha=0.75, interpolation="nearest")
        ax.set_title(title, fontsize=7)
    ax = axes[3]
    ax.imshow(hs, cmap="gray", extent=ext, interpolation="nearest")
    ax.imshow(ov, cmap=ListedColormap(["#D0336E"]), extent=ext, alpha=0.6, interpolation="nearest")
    for inp, k, col, lw in (("I30", 30, "#E58AAE", 1.4), ("I10", 10, "#5B3A78", 1.0)):
        for n in range(8):
            key = f"{site}|{inp}|conservative|DET|{n}"
            if key in routes:
                rc = (routes[key] + 0.5) * k
                ax.plot(rc[:, 1], rc[:, 0], color=col, lw=lw, label=(f"{inp[1:]} m map" if n == 0 else None))
    ax.set_title("(d) conservative routes", fontsize=7)
    ax.legend(loc="upper left", fontsize=5.3, frameon=True, framealpha=0.9, handlelength=1.2, borderpad=0.3, labelspacing=0.2)
    for ax in axes:
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_xlim(0, z1.shape[1]); ax.set_ylim(z1.shape[0], 0)
    cax = axes[2].inset_axes([0.55, 0.06, 0.4, 0.05])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal", ticks=[0, 0.5, 1])
    cb.set_label("face probability", fontsize=5.5, labelpad=1); cb.ax.tick_params(labelsize=5, length=2, pad=1)
    axes[0].plot([100, 1100], [z1.shape[0] - 120] * 2, color=INK, lw=2.2)
    axes[0].text(600, z1.shape[0] - 230, "1 km", color=INK, ha="center", va="bottom", fontsize=6.5,
                 bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    axes[0].annotate("N", xy=(z1.shape[1] - 250, 150), xytext=(z1.shape[1] - 250, 650), ha="center", fontsize=6.5, color=INK,
                     arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8), bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))
    fig.savefig(os.path.join(FIG, "fig_map.pdf"), metadata={"CreationDate": None}, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(os.path.join(FIG, "fig_map.png"), dpi=170, bbox_inches="tight", pad_inches=0.02, facecolor="white"); plt.close(fig)


def fig_planning():
    rows = [r for r in read(os.path.join(PLN, "summary.csv")) if r["profile"] == "assumed"]
    cfg = [("shortest", "none", "Shortest path"), ("naive", "none", "Slip model only"),
           ("conservative", "SLOPE-cal", "Gate: slope (cal.)"), ("conservative", "DET", "Gate: detector (ours)"),
           ("conservative", "GBM", "Gate: boosting*"), ("conservative", "CNN", "Gate: network*"),
           ("risk_weighted", "DET", "Weight: detector (ours)"), ("risk_weighted", "BICUBIC-cal", "Weight: interpolation (cal.)"),
           ("risk_weighted", "GBM", "Weight: boosting*"), ("conservative", "ORACLE", "Gate: oracle labels")]
    fig, ax = plt.subplots(figsize=(3.45, 3.0))
    metric = "mission_success"
    for j, inp in enumerate(("I10", "I30", "G30")):
        col, mk, lab = INPUT_STYLE[inp]
        for i, (pol, hz, _) in enumerate(cfg):
            r = next((r for r in rows if r["input"] == inp and r["policy"] == pol and r["hazard"] == hz), None)
            if r is None or r.get(metric, "") == "":
                continue
            y = i + (j - 1) * 0.25
            m, lo, hi = float(r[metric]), float(r[metric + "_lo"]), float(r[metric + "_hi"])
            ax.plot([lo, hi], [y, y], color=col, lw=1.0)
            ax.scatter([m], [y], s=18, marker=mk, color=col, edgecolors=INK, linewidths=0.4, zorder=3, label=lab if i == 0 else None)
    ph = read(os.path.join(ROOT, "results", "benchmark", "posthoc", "summary.csv"))
    yi = len(cfg)
    for j, inp in enumerate(("I10", "I30", "G30")):
        col, mk, lab = INPUT_STYLE[inp]
        r = next((r for r in ph if r["input"] == inp and r["policy"] == "conservative" and r["hazard"] == "ORACLE-ANY"), None)
        if r:
            ax.scatter([float(r["success_p10"])], [yi + (j - 1) * 0.25], s=18, marker=mk, facecolors="white", edgecolors=col, linewidths=1.0, zorder=3)
    cfg = cfg + [("conservative", "ORACLE-ANY", "Gate: face map (post hoc)")]
    o5 = next((r for r in rows if r["policy"] == "conservative" and r["hazard"] == "ORACLE-5"), None)
    if o5:
        ax.axvline(float(o5[metric]), color="#5B3A78", lw=0.7, ls="--")
        ax.text(float(o5[metric]) - 0.01, 0.2, "face map on a 5 m grid", rotation=90, ha="right", va="top", fontsize=6, color="#5B3A78")
    ax.set_yticks(range(len(cfg))); ax.set_yticklabels([c[2] for c in cfg]); ax.invert_yaxis()
    ax.set_xlim(0, 1.02); ax.set_xlabel("mission success (route exists and crosses no face patch)")
    ax.grid(axis="x", color="#EFE3E8", lw=0.5); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=3, frameon=False, fontsize=6.3, handletextpad=0.2, columnspacing=0.9)
    fig.savefig(os.path.join(FIG, "fig_planning.pdf"), metadata={"CreationDate": None}, bbox_inches="tight", pad_inches=0.02); plt.close(fig)


def main():
    os.makedirs(FIG, exist_ok=True)
    fig_auc()
    if os.path.exists(os.path.join(PLN, "summary.csv")):
        fig_planning()
        fig_map()
    print("figures in", FIG)


if __name__ == "__main__":
    main()
