"""Analysis of FIELD runs, as pre-registered in docs/FIELD_VALIDATION_PLAN.md.  PLANNED.

This module has only ever been run on SYNTHETIC data (tests/test_field_analysis.py).  It has never
seen a field measurement.  Input: one row per run (see docs/field_log_template.csv).
"""
from __future__ import annotations
import csv
from dataclasses import dataclass
import numpy as np
from scipy.optimize import least_squares

from .slipmodel import SlipParams, slip, PARAM_TABLE

ENTRAP_SLIP = 0.8     # slip level treated as entrapment in the plan (assumption)
CALIB_MAX_DEG = 10.0  # runs at or below this slope are used for calibration
ADEQ_TOL = 0.15       # |predicted - observed| tolerance (assumption, plan section 7)
ADEQ_FRAC = 0.80
ADEQ_ENTRAP_DEG = 3.0

REQUIRED = ["run_id", "slope_deg", "v_true_mps", "wheel_omega_rad_s", "r_eff_m", "entrapped", "phi_deg"]


def load_runs(path: str) -> dict:
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    miss = [c for c in REQUIRED if rows and c not in rows[0]]
    if miss:
        raise ValueError(f"missing columns: {miss}")
    out = {"run_id": [r["run_id"] for r in rows]}
    for c in ("slope_deg", "v_true_mps", "wheel_omega_rad_s", "r_eff_m", "phi_deg"):
        out[c] = np.array([float(r[c]) for r in rows])
    out["entrapped"] = np.array([int(float(r["entrapped"])) for r in rows], dtype=bool)
    return out


def observed_slip(d: dict) -> np.ndarray:
    """Longitudinal slip 1 - v_true/(omega r_eff); entrapped runs are set to 1."""
    s = 1.0 - d["v_true_mps"] / (d["wheel_omega_rad_s"] * d["r_eff_m"])
    s = np.clip(s, -0.2, 1.0)
    return np.where(d["entrapped"], 1.0, s)


def model_slip(slope_deg, f_r, i0, phi_deg, i_max=0.5):
    p = SlipParams(phi_deg=float(phi_deg), f_r=float(f_r), i0=float(i0), i_max=i_max)
    s = slip(np.tan(np.radians(np.asarray(slope_deg, dtype=float))), 0.0, p)
    return np.minimum(s, 1.0)


def calibrate(slope, s_obs, phi_deg):
    """Fit f_r and i0 by bounded least squares on calibration runs, friction angle fixed from soil tests.

    Bounds are the assumption ranges of the simulation study (PARAM_TABLE).  Without bounds, f_r and i0 trade
    off at gentle slopes and the steep-slope prediction can fail badly (see scripts/calibration_identifiability.py).
    Replace the bounds with ranges from your own tow and plate tests when you have them.
    """
    lo = [PARAM_TABLE["f_r"][1], PARAM_TABLE["i0"][1]]
    hi = [PARAM_TABLE["f_r"][2], PARAM_TABLE["i0"][2]]

    def resid(x):
        return model_slip(slope, x[0], x[1], phi_deg) - s_obs
    best = None
    for f0 in (0.08, 0.15, 0.22):
        for i00 in (0.1, 0.2, 0.35):
            r = least_squares(resid, [f0, i00], bounds=(lo, hi))
            if best is None or r.cost < best.cost:
                best = r
    return float(best.x[0]), float(best.x[1])


def entrapment_slope_model(f_r, i0, phi_deg) -> float:
    th = np.arange(0.0, 45.0, 0.05)
    s = model_slip(th, f_r, i0, phi_deg)
    idx = np.where(s >= ENTRAP_SLIP)[0]
    return float(th[idx[0]]) if idx.size else float("nan")


def entrapment_slope_observed(slope, entrapped, bin_width=5.0):
    """Lowest slope bin (centre) in which at least half of the runs were entrapped; NaN if none."""
    centres = np.round(np.asarray(slope) / bin_width) * bin_width
    for c in np.unique(centres):
        m = centres == c
        if entrapped[m].mean() >= 0.5:
            return float(c)
    return float("nan")


@dataclass
class Result:
    f_r: float
    i0: float
    n_calib: int
    n_test: int
    mae: float
    rmse: float
    cal_slope: float
    frac_within_tol: float
    mae_const: float
    mae_threshold: float
    entrap_pred_deg: float
    entrap_obs_deg: float
    adequate: bool
    ci: dict


def analyse(d: dict, n_boot: int = 2000, seed: int = 20261014) -> Result:
    slope = d["slope_deg"]
    s = observed_slip(d)
    phi = float(np.median(d["phi_deg"]))
    cal = slope <= CALIB_MAX_DEG
    test = ~cal
    if cal.sum() < 5 or test.sum() < 3:
        raise ValueError("need at least 5 calibration runs (<= 10 deg) and 3 held-out runs")
    f_r, i0 = calibrate(slope[cal & ~d["entrapped"]], s[cal & ~d["entrapped"]], phi)
    pred = model_slip(slope[test], f_r, i0, phi)
    err = pred - s[test]
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    A = np.vstack([pred, np.ones_like(pred)]).T
    cal_slope = float(np.linalg.lstsq(A, s[test], rcond=None)[0][0])
    within = float(np.mean(np.abs(err) <= ADEQ_TOL))
    const = float(np.mean(s[cal]))
    mae_const = float(np.mean(np.abs(const - s[test])))
    # threshold baseline: predicts slip 0 below the model's i_max angle and 1 above it
    th = float(np.degrees(np.arctan(max(np.tan(np.radians(phi)) - f_r, 0.0))))
    mae_thr = float(np.mean(np.abs(np.where(slope[test] > th, 1.0, 0.0) - s[test])))
    ep = entrapment_slope_model(f_r, i0, phi)
    eo = entrapment_slope_observed(slope, d["entrapped"])
    adequate = bool(within >= ADEQ_FRAC and np.isfinite(ep) and np.isfinite(eo) and abs(ep - eo) <= ADEQ_ENTRAP_DEG)
    rng = np.random.default_rng(seed)
    idx = np.flatnonzero(test)
    boots = {"mae": [], "rmse": []}
    for _ in range(n_boot):
        b = rng.choice(idx, size=idx.size, replace=True)
        e = model_slip(slope[b], f_r, i0, phi) - s[b]
        boots["mae"].append(np.mean(np.abs(e)))
        boots["rmse"].append(np.sqrt(np.mean(e ** 2)))
    ci = {k: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) for k, v in boots.items()}
    return Result(f_r, i0, int(cal.sum()), int(test.sum()), mae, rmse, cal_slope, within, mae_const, mae_thr, ep, eo, adequate, ci)


def per_bin_means(d: dict, n_boot: int = 2000, seed: int = 20261015, bin_width: float = 5.0):
    """Per-slope-bin mean slip with seeded bootstrap 95 % interval."""
    s = observed_slip(d)
    centres = np.round(d["slope_deg"] / bin_width) * bin_width
    rng = np.random.default_rng(seed)
    out = []
    for c in np.unique(centres):
        v = s[centres == c]
        bm = [np.mean(rng.choice(v, size=v.size, replace=True)) for _ in range(n_boot)]
        out.append((float(c), int(v.size), float(v.mean()), float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))))
    return out


def synthetic_runs(seed: int = 7, f_r=0.14, i0=0.22, phi=33.0, sigma=0.06, runs_per_bin=6):
    """SYNTHETIC data generated from the model itself plus noise, used only to test this code."""
    rng = np.random.default_rng(seed)
    slopes, v, om, r, ent = [], [], [], [], []
    for b in (0, 5, 10, 15, 20, 25, 28):
        for _ in range(runs_per_bin):
            th = b + rng.uniform(-1.5, 1.5)
            s_true = float(model_slip(max(th, 0.0), f_r, i0, phi))
            s_obs = min(max(s_true + rng.normal(0, sigma), -0.05), 1.0) if np.isfinite(s_true) else 1.0
            trapped = s_obs >= ENTRAP_SLIP
            omega, reff = 3.0, 0.1
            slopes.append(th); om.append(omega); r.append(reff); ent.append(trapped)
            v.append(0.0 if trapped else (1.0 - s_obs) * omega * reff)
    n = len(slopes)
    return {"run_id": [f"S{i:03d}" for i in range(n)], "slope_deg": np.array(slopes), "v_true_mps": np.array(v),
            "wheel_omega_rad_s": np.array(om), "r_eff_m": np.array(r), "entrapped": np.array(ent), "phi_deg": np.full(n, phi)}
