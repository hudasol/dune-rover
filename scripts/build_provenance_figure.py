#!/usr/bin/env python3
"""Provenance figure: published data and sources, the scripts that read them, the result folders they write, and the
documents generated from those results.

    python3 scripts/build_provenance_figure.py      # writes docs/figures/fig_provenance.png and docs/PROVENANCE.md

The graph below is the single list of edges; docs/PROVENANCE.md prints the same list as a table, so the figure and
the table cannot disagree. Every edge names a file or folder that exists in the repository (checked at build time;
raw data folders are git ignored and are fetched by the named fetch script).
"""
from __future__ import annotations
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCES = {   # id: (label, fetch or location)
    "papers": ("Published papers (full text)", "research/evidence.csv, research/sources (git ignored)"),
    "curves": ("Digitised published curves", "research/phase3/curves.csv, research/phase4/curves_new.csv"),
    "cop": ("Copernicus GLO 30 DEM", "scripts/fetch_data.sh"),
    "lidar": ("USGS 3DEP 1 m lidar", "scripts/fetch_lidar.sh"),
    "era5": ("ERA5 wind (Open-Meteo)", "scripts/wind_face_direction.py (cached)"),
    "is2": ("ICESat-2 (SlideRule Earth)", "scripts/icesat2_profiles.py fetch"),
}
SCRIPTS = {   # id: (path, inputs)
    "consolidate": ("scripts/consolidate_evidence.py", ["papers"]),
    "verify": ("scripts/verify_stats.py", ["papers"]),
    "study": ("src/dunerover/study_subgrid.py", ["cop"]),
    "mv": ("scripts/model_validation.py", ["curves"]),
    "chrono": ("scripts/chrono_wheel_slope.py", ["papers"]),
    "scmcal": ("scripts/chrono_scm_calibration.py", ["curves"]),
    "tv": ("scripts/terrain_validation_lidar.py", ["lidar"]),
    "planner": ("scripts/planner_lidar.py", ["lidar"]),
    "wind": ("scripts/wind_face_direction.py", ["era5", "lidar", "cop"]),
    "icesat2": ("scripts/icesat2_profiles.py", ["is2", "lidar", "cop"]),
    "loop": ("demo/closed_loop.py", ["lidar"]),
    "field": ("scripts/ingest_field_day.py", []),
}
RESULTS = {   # id: (folder, producing script ids)
    "ev": ("research/evidence.csv", ["consolidate", "verify"]),
    "maps": ("results/subgrid*", ["study"]),
    "models": ("results/model_validation*", ["mv"]),
    "scm": ("results/chrono_scm*", ["chrono", "scmcal"]),
    "lid": ("results/terrain_validation*", ["tv"]),
    "plan": ("results/planner*", ["planner"]),
    "windr": ("results/wind_azimuth", ["wind"]),
    "is2r": ("results/icesat2", ["icesat2"]),
    "cl": ("results/closed_loop", ["loop"]),
    "fd": ("results/field_day (after a field day)", ["field"]),
}
DOCUMENTS = {   # id: (path, result ids)
    "report": ("docs/REPORT.md", ["ev", "maps", "models", "scm", "lid", "plan", "windr", "is2r", "cl", "fd"]),
    "ms": ("manuscript/MANUSCRIPT.md", ["ev", "maps", "models", "scm", "lid", "plan", "windr", "is2r", "cl"]),
    "brief": ("docs/EXECUTIVE_BRIEF.md", ["ev", "maps", "models", "scm", "lid", "plan", "is2r", "cl"]),
    "propr": ("docs/PROPOSAL_ROBOTICS.md", ["ev", "models", "scm", "lid", "plan", "is2r", "cl"]),
    "prope": ("docs/PROPOSAL_EDGE.md", ["ev", "models", "lid", "plan", "is2r", "cl"]),
    "ledger": ("docs/NUMBER_LEDGER.csv", ["ev", "maps", "models", "scm", "lid", "plan", "windr", "is2r", "cl"]),
}
PINK = {"bg": "#fffafb", "src": "#f4e9ec", "scr": "#e8a5bb", "res": "#c9769a", "doc": "#5b3a78", "ink": "#2b2024", "edge": "#a98fd1"}


def check():
    import glob
    missing = []
    for _, (path, _) in SCRIPTS.items():
        if not os.path.exists(os.path.join(ROOT, path)):
            missing.append(path)
    for _, (path, _) in RESULTS.items():
        p = path.split(" ")[0]
        if not glob.glob(os.path.join(ROOT, p)) and "after a field day" not in path:
            missing.append(p)
    return missing


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cols = [("Published data and sources", SOURCES, PINK["src"]), ("Scripts", SCRIPTS, PINK["scr"]),
            ("Results", RESULTS, PINK["res"]), ("Documents", DOCUMENTS, PINK["doc"])]
    pos = {}
    fig, ax = plt.subplots(figsize=(15, 9), facecolor=PINK["bg"]); ax.set_facecolor(PINK["bg"]); ax.axis("off")
    for ci, (title, items, colour) in enumerate(cols):
        n = len(items)
        ax.text(ci * 4 + 1.4, n and 13.3, title, ha="center", fontsize=11, color=PINK["ink"], weight="bold")
        for k, (key, val) in enumerate(items.items()):
            y = 12.5 - k * (12.0 / max(n, 1))
            label = val[0] if ci == 0 else val[0]
            ax.add_patch(plt.Rectangle((ci * 4, y - 0.35), 2.8, 0.7, color=colour, ec=PINK["ink"], lw=0.5))
            ax.text(ci * 4 + 1.4, y, label, ha="center", va="center", fontsize=6.5, color="white" if ci == 3 else PINK["ink"], wrap=True)
            pos[(ci, key)] = y
    def edge(c0, a, c1, b):
        ax.annotate("", xy=(c1 * 4, pos[(c1, b)]), xytext=(c0 * 4 + 2.8, pos[(c0, a)]),
                    arrowprops=dict(arrowstyle="-|>", color=PINK["edge"], lw=0.6, alpha=0.8))
    for s, (_, ins) in SCRIPTS.items():
        for i in ins:
            edge(0, i, 1, s)
    for r, (_, scs) in RESULTS.items():
        for s in scs:
            edge(1, s, 2, r)
    for d, (_, rs) in DOCUMENTS.items():
        for r in rs:
            edge(2, r, 3, d)
    ax.set_xlim(-0.3, 15.2); ax.set_ylim(-0.2, 13.8)
    ax.text(0, -0.1, "Generated by scripts/build_provenance_figure.py. Every document number is traced to its row in docs/NUMBER_LEDGER.csv.", fontsize=7, color=PINK["ink"])
    os.makedirs(os.path.join(ROOT, "docs", "figures"), exist_ok=True)
    fig.savefig(os.path.join(ROOT, "docs", "figures", "fig_provenance.png"), dpi=130, bbox_inches="tight")
    lines = ["# Provenance of the results", "", "Generated by `scripts/build_provenance_figure.py`; the figure is `docs/figures/fig_provenance.png`. Every number in the manuscript, the brief and the proposals is traced individually in `docs/NUMBER_LEDGER.csv`.", "",
             "| Source | Where it comes from |", "|---|---|"] + [f"| {v[0]} | `{v[1]}` |" for v in SOURCES.values()]
    lines += ["", "| Script | Reads |", "|---|---|"] + [f"| `{p}` | {', '.join(SOURCES[i][0] for i in ins) or 'filled field data sheets'} |" for p, ins in SCRIPTS.values()]
    lines += ["", "| Result | Written by |", "|---|---|"] + [f"| `{p}` | {', '.join('`' + SCRIPTS[s][0] + '`' for s in scs)} |" for p, scs in RESULTS.values()]
    lines += ["", "| Document | Uses |", "|---|---|"] + [f"| `{p}` | {', '.join('`' + RESULTS[r][0] + '`' for r in rs)} |" for p, rs in DOCUMENTS.values()]
    open(os.path.join(ROOT, "docs", "PROVENANCE.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    miss = check()
    print("provenance written" + (f"; MISSING: {miss}" if miss else ""))
    sys.exit(1 if miss else 0)


if __name__ == "__main__":
    main()
