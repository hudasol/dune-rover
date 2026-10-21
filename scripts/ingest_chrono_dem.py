#!/usr/bin/env python3
"""Ingest the output of notebooks/chrono_dem_gpu.ipynb (run by Huda on a free GPU) into results/chrono_dem/.

    python3 scripts/ingest_chrono_dem.py [data/raw/chrono_dem/chrono_dem_results.csv]

Writes results/chrono_dem/slip_vs_slope.csv (the rows, with the source file's SHA-256) and a figure that compares the
particle simulation with the Project Chrono SCM sweep of stage 14 (results/chrono_scm/sweep.csv) and the published
Dumont cubic (Heverly et al. 2013, Sec. 6.3). The wheels differ (DEM: VIPER type mesh, radius 0.25 m; SCM W1:
Scarecrow like), so the comparison is qualitative. SIMULATED BY ME; until the notebook has been run, nothing is written.
"""
import csv, hashlib, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "raw", "chrono_dem", "chrono_dem_results.csv")
OUT = os.path.join(ROOT, "results", "chrono_dem")
CUBIC = (26.197, -8.849, 1.281, -0.034)


def main():
    if not os.path.exists(SRC):
        sys.exit(f"{SRC} not found: run notebooks/chrono_dem_gpu.ipynb on a free GPU first")
    sha = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
    rows = list(csv.DictReader(open(SRC)))
    need = {"slope_deg", "slip", "n_spheres", "deme_version"}
    if not rows or not need <= set(rows[0]):
        sys.exit(f"unexpected columns in {SRC}: need {sorted(need)}")
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    with open(os.path.join(OUT, "slip_vs_slope.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) + ["source_sha256"]); w.writeheader()
        w.writerows([{**r, "source_sha256": sha} for r in rows])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.6, 3.8), facecolor="#fffafb"); ax.set_facecolor("#fffafb")
    ax.plot([float(r["slope_deg"]) for r in rows], [float(r["slip"]) for r in rows], "o-", color="#a8325e", label="DEM-Engine, VIPER type wheel (SIMULATED BY ME)")
    scm = [r for r in csv.DictReader(open(os.path.join(ROOT, "results", "chrono_scm", "sweep.csv"))) if r["wheel"].startswith("W1") and r["soil"].startswith("S1") and r["slip"]]
    ax.plot([float(r["slope_deg"]) for r in scm], [min(float(r["slip"]), 1) for r in scm], "s--", color="#5b3a78", label="Chrono SCM, W1 and S1 (stage 14)")
    xs = [x / 2 for x in range(8, 43)]
    ax.plot(xs, [sum(c * x ** i for i, c in enumerate(CUBIC)) / 100 for x in xs], color="#6fa28f", label="Dumont cubic (PUBLISHED)")
    ax.set_xlabel("slope, deg"); ax.set_ylabel("slip"); ax.set_ylim(-0.05, 1.05); ax.legend(frameon=False, fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "figures", "fig_dem_vs_scm.png"), dpi=140)
    print(f"ingested {len(rows)} slopes from {SRC} (sha256 {sha[:16]})")


if __name__ == "__main__":
    main()
