#!/usr/bin/env python3
"""Stage 24 (docs/PREDICTIONS.md): calibrate Project Chrono SCM soil parameters on the Dumont Dunes curve up to
12.5 degrees only, then predict the steeper slopes (15, 17.5 and 20 degrees) before comparing them with the curve.

    /opt/mm/chrono/bin/python scripts/chrono_scm_calibration.py

Wheel W1 of stage 14 (Scarecrow like: radius 0.25 m, width 0.40 m, load 556 N; FLD-HV13-5a). Soil: the stage 14 set
S1 (Ishigami et al. 2007 Table I: Kphi, Kc, n) with cohesion set to 0 Pa for dry dune sand (ASSUMPTION) and two
parameters calibrated on a grid: the Janosi shear modulus K in {0.036, 0.08, 0.15, 0.3, 0.6} m and the friction
angle phi in {28, 32, 37.2} deg. Target: the published Dumont cubic fit (Heverly et al. 2013, Sec. 6.3,
research/phase3/tabulated/heverly2013_sec6_3_cubic_fit_dumont.json) at 5, 10 and 12.5 deg; the grid point with the
smallest root mean square error is chosen, then run at 15, 17.5 and 20 deg. SIMULATED BY ME; deterministic.
Outputs: results/chrono_scm_calibration/grid.csv, prediction.csv, summary.json, run_log.txt.
"""
from __future__ import annotations
import csv, json, math, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import chrono_wheel_slope as CW  # noqa: E402

OUT = os.path.join(ROOT, "results", "chrono_scm_calibration")
K_GRID = (0.036, 0.08, 0.15, 0.3, 0.6)
PHI_GRID = (28.0, 32.0, 37.2)
CAL_SLOPES = (5.0, 10.0, 12.5)
PRED_SLOPES = (15.0, 17.5, 20.0)
CUBIC = (26.197, -8.849, 1.281, -0.034)   # slip in percent against slope in deg, Heverly et al. 2013 Sec. 6.3


def dumont(s):
    return sum(c * s ** i for i, c in enumerate(CUBIC)) / 100.0


def main():
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(OUT, "run_log.txt"), "w")
    def say(m):
        print(m, flush=True); log.write(m + "\n"); log.flush()
    kphi, kc, n, _, _, _, _ = CW.SOILS["S1_toyoura_ishigami2007"]
    say(f"stage 24 started {time.strftime('%Y-%m-%d %H:%M:%S')}; base soil S1 with cohesion 0; K grid {K_GRID}; phi grid {PHI_GRID}")
    grid = []
    for K in K_GRID:
        for phi in PHI_GRID:
            CW.SOILS["CAL"] = (kphi, kc, n, 0.0, phi, K, "stage 24 calibration grid point")
            sl = {}
            for s in CAL_SLOPES:
                r = CW.run(s, "W1_scarecrow_like", "CAL"); sl[s] = r["slip"]
            rmse = math.sqrt(sum((sl[s] - dumont(s)) ** 2 for s in CAL_SLOPES) / len(CAL_SLOPES))
            grid.append({"K_m": K, "phi_deg": phi, **{f"slip_{s:g}": sl[s] for s in CAL_SLOPES}, "rmse_cal": round(rmse, 4)})
            say(f"K {K} phi {phi}: " + ", ".join(f"{s:g} deg {sl[s]:.3f}" for s in CAL_SLOPES) + f"; rmse {rmse:.3f}")
    with open(os.path.join(OUT, "grid.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(grid[0])); w.writeheader(); w.writerows(grid)
    best = min(grid, key=lambda g: g["rmse_cal"])
    CW.SOILS["CAL"] = (kphi, kc, n, 0.0, best["phi_deg"], best["K_m"], "stage 24 best grid point")
    pred = []
    for s in PRED_SLOPES:
        r = CW.run(s, "W1_scarecrow_like", "CAL")
        pred.append({"slope_deg": s, "chrono_slip": r["slip"], "dumont_cubic": round(dumont(s), 4), "error": round(r["slip"] - dumont(s), 4)})
        say(f"prediction {s} deg: chrono {r['slip']:.3f} against Dumont {dumont(s):.3f}")
    with open(os.path.join(OUT, "prediction.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pred[0])); w.writeheader(); w.writerows(pred)
    rmse_pred = math.sqrt(sum(p["error"] ** 2 for p in pred) / len(pred))
    json.dump({"label": "SIMULATED BY ME against a PUBLISHED curve", "best": best, "rmse_prediction": round(rmse_pred, 4),
               "cal_slopes": CAL_SLOPES, "pred_slopes": PRED_SLOPES, "k_grid": K_GRID, "phi_grid": PHI_GRID},
              open(os.path.join(OUT, "summary.json"), "w"), indent=1)
    say(f"best K {best['K_m']} phi {best['phi_deg']} (calibration rmse {best['rmse_cal']:.3f}); prediction rmse {rmse_pred:.3f}; done {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
