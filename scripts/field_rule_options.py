#!/usr/bin/env python3
"""Stage 18 (docs/PREDICTIONS.md): alternative field adequacy rules, evaluated as OPTIONS for Huda (question 7).
The current rule (stage 10) stays in force; nothing here changes src/dunerover/fieldanalysis.py.

    PYTHONPATH=src python3 scripts/field_rule_options.py [--reps 300]

SIMULATED BY ME, synthetic data only. Output: results/field_kit/rule_options_2026-10-20.csv.
"""
import argparse, csv, os, sys, time
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover import fieldanalysis as FA  # noqa: E402


def options(d, r):
    """Verdict of each option ('accepted' or 'rejected') from the data d and the stage 10 result r."""
    slope = d["slope_deg"]; s = FA.observed_slip(d); phi = float(np.median(d["phi_deg"]))
    test = slope > FA.CALIB_MAX_DEG
    pred = FA.model_slip(slope, r.f_r, r.i0, phi)
    err = pred - s
    entrap_ok = r.entrap_status in ("pass", "not reached")
    out = {"current": "accepted" if r.verdict_2026_10_18 != "not adequate" else "rejected"}
    sig = r.sigma_pilot if np.isfinite(r.sigma_pilot) else 0.0
    tol_a = max(2.0 * sig, 0.03)
    out["option_A_stricter_tolerance"] = "accepted" if (np.mean(np.abs(err[test]) <= tol_a) >= FA.ADEQ_FRAC and entrap_ok) else "rejected"
    steep = slope >= 15.0; steeper = slope >= 17.5
    ok_b = steep.sum() > 0 and np.mean(np.abs(err[steep]) <= r.tol) >= FA.ADEQ_FRAC and (steeper.sum() == 0 or abs(np.mean(err[steeper])) <= 0.5 * r.tol)
    out["option_B_steep_runs"] = "accepted" if (ok_b and entrap_ok) else "rejected"
    out["option_C_calibration_slope"] = "accepted" if (r.slip_pass and 0.8 <= r.cal_slope <= 1.25 and entrap_ok) else "rejected"
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--reps", type=int, default=300); a = ap.parse_args()
    rows, t0 = [], time.time()
    for kind in ("model", "janosi_mean", "collapse", "dumont"):
        for sigma in (0.03, 0.06, 0.10):
            acc = {}
            n = 0
            for k in range(a.reps):
                d = FA.synthetic_runs(seed=30000 + k, sigma=sigma, kind=kind, design="2026-10-15")
                try:
                    r = FA.analyse(d, n_boot=20, bin_width=2.5)
                except Exception:
                    continue
                n += 1
                for name, v in options(d, r).items():
                    acc.setdefault(name, []).append(v == "accepted")
            for name, v in acc.items():
                rows.append({"label": "SIMULATED BY ME, synthetic data only; options for question 7, current rule in force", "truth": kind, "sigma": sigma,
                             "rule": name, "replicates": n, "accepted_rate": round(float(np.mean(v)), 4)})
            print(kind, sigma, {k: round(float(np.mean(v)), 3) for k, v in acc.items()}, f"[{time.time()-t0:.0f}s]", flush=True)
    with open(os.path.join(ROOT, "results", "field_kit", "rule_options_2026-10-20.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
