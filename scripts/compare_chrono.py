#!/usr/bin/env python3
"""Stage 14 comparison: Chrono SCM single wheel slip against the Dumont cubic (PUBLISHED), the nominal original slip
model and the Bekker Wong family with the same wheel and soil set (both SIMULATED BY ME).

    PYTHONPATH=src python3 scripts/compare_chrono.py

Note: the Soil Contact Model in Chrono uses the same Bekker pressure sinkage and Janosi shear laws as the Bekker Wong
family, so agreement between them is a check of implementation, not independent validation of the physics.
Outputs: results/chrono_scm/comparison.csv, figures/fig_chrono_vs_published.png.
"""
import csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover.models import FAMILIES  # noqa: E402

OUT = os.path.join(ROOT, "results", "chrono_scm")
WHEELS = {"W1_scarecrow_like": (0.25, 0.40, 556.0), "W2_ishigami_like": (0.055, 0.064, 29.8)}
SOILS = {"S1_toyoura_ishigami2007": "toyoura_ishigami2007", "S2_dem_calibrated_zhang2024": "dem_calibrated_zhang2024"}


def dumont(s):
    return (26.197 - 8.849 * s + 1.281 * s ** 2 - 0.034 * s ** 3) / 100.0


def main():
    rows = [r for r in csv.DictReader(open(os.path.join(OUT, "sweep.csv"))) if r["slip"] != ""]
    out = []
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), facecolor="#fffafb")
    for ax, wheel in zip(axes, WHEELS):
        R, b, W = WHEELS[wheel]
        for soil, col in zip(SOILS, ("#a8325e", "#5b3a78")):
            rr = [r for r in rows if r["wheel"] == wheel and r["soil"] == soil]
            x = np.array([float(r["slope_deg"]) for r in rr]); y = np.minimum(np.array([float(r["slip"]) for r in rr]), 1.0)
            ctx = {"radius_m": R, "width_m": b, "load_N": W, "soil_set": SOILS[soil]}
            f = FAMILIES["bekker_wong"]; bw = f.predict(x, "direct ascent", ctx, f.nominal(ctx))
            ex = FAMILIES["exp_existing"].predict(x, "direct ascent", {}, FAMILIES["exp_existing"].nominal())
            for xi, yi, bi, ei in zip(x, y, bw, ex):
                out.append({"wheel": wheel, "soil": soil, "slope_deg": xi, "chrono_slip_capped": round(float(yi), 4), "bekker_wong_nominal": round(float(bi), 4),
                            "exp_existing_nominal": round(float(ei), 4), "dumont_cubic": round(float(dumont(xi)), 4) if 4 <= xi <= 21 else ""})
            ax.plot(x, y, "o-", color=col, lw=2, ms=4, label=f"Chrono SCM, {soil.split('_')[0]}")
            ax.plot(x, bw, "--", color=col, lw=1.2, label=f"Bekker Wong family, {soil.split('_')[0]}")
        xs = np.linspace(4, 21, 50)
        ax.plot(xs, dumont(xs), color="#6fa28f", lw=2.5, label="Dumont cubic (PUBLISHED, Scarecrow)")
        ax.plot(np.linspace(0, 30, 61), FAMILIES["exp_existing"].predict(np.linspace(0, 30, 61), "direct ascent", {}, FAMILIES["exp_existing"].nominal()),
                ":", color="#2b2024", lw=1.5, label="existing model, nominal")
        ax.set_title(wheel, fontsize=10); ax.set_xlabel("slope (deg)"); ax.set_ylabel("slip (capped at 1)"); ax.set_ylim(-0.02, 1.05); ax.set_facecolor("#fffafb")
    axes[0].legend(fontsize=7, frameon=False)
    fig.text(0.01, -0.02, "Chrono and both models SIMULATED BY ME with PUBLISHED wheel sizes and soil sets; smooth wheels; the Dumont curve is for a grousered wheel in natural dune sand.", fontsize=7.5)
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    fig.savefig(os.path.join(OUT, "figures", "fig_chrono_vs_published.png"), dpi=130, bbox_inches="tight")
    with open(os.path.join(OUT, "comparison.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    for wheel in WHEELS:
        for soil in SOILS:
            rr = [o for o in out if o["wheel"] == wheel and o["soil"] == soil]
            d = np.array([o["chrono_slip_capped"] - o["bekker_wong_nominal"] for o in rr])
            print(wheel, soil, "Chrono minus Bekker Wong: rmse", round(float(np.sqrt(np.mean(d ** 2))), 3))


if __name__ == "__main__":
    main()
