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
ADEQ_TOL = 0.15       # fixed |predicted - observed| tolerance used only if no pilot data are given (assumption, plan section 7)
TOL_SIGMA_MULT = 3.0  # tolerance = max(TOL_SIGMA_MULT x pilot sigma, TOL_FLOOR): decision rule fixed before the main block (assumption)
TOL_FLOOR = 0.05
UNINFORMATIVE_TOL = 0.30   # if 3 x pilot sigma exceeds this the experiment cannot discriminate and is reported as uninformative
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
    out["block"] = np.array([r.get("block", "") for r in rows])
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


def pilot_sigma(d: dict, bin_width: float = 5.0) -> tuple[float, str]:
    """Pooled within-bin standard deviation of observed slip over the pilot block.

    Uses rows with block == 'pilot' (at least 8 rows, bins with at least 2 runs).  Falls back, flagged, to all runs.
    The within-bin spread also contains the effect of the plus or minus 2 deg slope tolerance, so it slightly
    overstates pure run-to-run noise (conservative: a wider tolerance).
    """
    s = observed_slip(d)
    centres = np.round(d["slope_deg"] / bin_width) * bin_width
    blk = d.get("block")
    mask = (np.asarray(blk) == "pilot") if blk is not None else np.zeros(len(s), dtype=bool)
    src = "pilot block"
    if mask.sum() < 8:
        mask = np.ones(len(s), dtype=bool); src = "FALLBACK: all runs (no or too small pilot block)"
    ss, dof = 0.0, 0
    for c in np.unique(centres[mask]):
        v = s[mask & (centres == c)]
        if v.size >= 2:
            ss += float(np.sum((v - v.mean()) ** 2)); dof += v.size - 1
    if dof == 0:
        raise ValueError("cannot estimate pilot sigma: need at least two runs in some slope bin")
    return float(np.sqrt(ss / dof)), src


def tolerance_from_pilot(sigma: float) -> float:
    return max(TOL_SIGMA_MULT * sigma, TOL_FLOOR)


def entrapment_slope_model(f_r, i0, phi_deg) -> float:
    th = np.arange(0.0, 45.0, 0.05)
    s = model_slip(th, f_r, i0, phi_deg)
    idx = np.where(s >= ENTRAP_SLIP)[0]
    return float(th[idx[0]]) if idx.size else float("nan")


def entrapment_slope_observed(slope, entrapped, bin_width=5.0):
    """Mean measured slope of the runs in the lowest slope bin in which at least half the runs were entrapped; NaN if none.

    (An earlier version returned the bin centre, which rounded a 28 deg bin to 30 deg and made a correct model fail
    the 3 deg entrapment criterion; fixed before the synthetic power study was run.)
    """
    slope = np.asarray(slope); entrapped = np.asarray(entrapped)
    centres = np.round(slope / bin_width) * bin_width
    for c in np.unique(centres):
        m = centres == c
        if entrapped[m].mean() >= 0.5:
            return float(slope[m].mean())
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
    tol: float = ADEQ_TOL
    sigma_pilot: float = float("nan")
    sigma_source: str = "fixed tolerance, no pilot"
    informative: bool = True


def analyse(d: dict, n_boot: int = 2000, seed: int = 20261014, tol: float | None = None, use_pilot: bool = True) -> Result:
    """Pre-registered analysis.  Tolerance: explicit `tol`, else 3 x pilot sigma (floor 0.05) if a pilot block exists, else 0.15."""
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
    sig, src = float("nan"), "fixed tolerance, no pilot"
    if tol is None:
        if use_pilot and "block" in d and (np.asarray(d["block"]) == "pilot").sum() >= 8:
            sig, src = pilot_sigma(d); tol = tolerance_from_pilot(sig)
        else:
            tol = ADEQ_TOL
    else:
        src = "tolerance given explicitly"
    informative = bool(np.isnan(sig) or TOL_SIGMA_MULT * sig <= UNINFORMATIVE_TOL)
    within = float(np.mean(np.abs(err) <= tol))
    const = float(np.mean(s[cal]))
    mae_const = float(np.mean(np.abs(const - s[test])))
    # threshold baseline: predicts slip 0 below the model's i_max angle and 1 above it
    th = float(np.degrees(np.arctan(max(np.tan(np.radians(phi)) - f_r, 0.0))))
    mae_thr = float(np.mean(np.abs(np.where(slope[test] > th, 1.0, 0.0) - s[test])))
    ep = entrapment_slope_model(f_r, i0, phi)
    eo = entrapment_slope_observed(slope, d["entrapped"])
    adequate = bool(within >= ADEQ_FRAC and np.isfinite(ep) and np.isfinite(eo) and abs(ep - eo) <= ADEQ_ENTRAP_DEG)
    # pass/fail is reported either way; an uninformative experiment is flagged so a pass is not over-read
    rng = np.random.default_rng(seed)
    idx = np.flatnonzero(test)
    boots = {"mae": [], "rmse": []}
    for _ in range(n_boot):
        b = rng.choice(idx, size=idx.size, replace=True)
        e = model_slip(slope[b], f_r, i0, phi) - s[b]
        boots["mae"].append(np.mean(np.abs(e)))
        boots["rmse"].append(np.sqrt(np.mean(e ** 2)))
    ci = {k: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) for k, v in boots.items()}
    return Result(f_r, i0, int(cal.sum()), int(test.sum()), mae, rmse, cal_slope, within, mae_const, mae_thr, ep, eo, adequate, ci, float(tol), sig, src, informative)


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


def truth_slip(kind: str, th, f_r=0.14, i0=0.22, phi=33.0):
    """True mean slip for SYNTHETIC data.  'model' = the analysis model; 'janosi_mean' = a different shear-law form
    (mild structural error); 'collapse' = exponential law below 20 deg, slip 0.85 from 22 deg upward with a linear
    blend in between (the model is WRONG by construction: stands in for avalanche or bearing failure)."""
    th = np.maximum(np.asarray(th, dtype=float), 0.0)
    if kind == "model":
        return np.minimum(slip(np.tan(np.radians(th)), 0.0, SlipParams(phi_deg=phi, f_r=f_r, i0=i0)), 1.0)
    if kind == "janosi_mean":
        return np.minimum(slip(np.tan(np.radians(th)), 0.0, SlipParams(phi_deg=phi, f_r=f_r, i0=i0, form="janosi_mean")), 1.0)
    if kind == "collapse":
        base = np.minimum(slip(np.tan(np.radians(th)), 0.0, SlipParams(phi_deg=phi, f_r=f_r, i0=i0)), 1.0)
        w = np.clip((th - 20.0) / 2.0, 0.0, 1.0)
        return (1 - w) * base + w * 0.85
    raise ValueError(f"unknown truth kind {kind!r}")


def synthetic_runs(seed: int = 7, f_r=0.14, i0=0.22, phi=33.0, sigma=0.06, runs_per_bin=6, kind: str = "model"):
    """SYNTHETIC data generated from a known truth plus noise, used only to test this code.  The first 3 runs in
    each of the 5, 10, 15 and 20 deg bins carry block == 'pilot' (as in the field plan)."""
    rng = np.random.default_rng(seed)
    slopes, v, om, r, ent, blk = [], [], [], [], [], []
    for b in (0, 5, 10, 15, 20, 25, 28):
        for j in range(runs_per_bin):
            th = b + rng.uniform(-1.5, 1.5)
            s_true = float(truth_slip(kind, max(th, 0.0), f_r, i0, phi))
            s_obs = min(max(s_true + rng.normal(0, sigma), -0.05), 1.0) if np.isfinite(s_true) else 1.0
            trapped = s_obs >= ENTRAP_SLIP
            omega, reff = 3.0, 0.1
            slopes.append(th); om.append(omega); r.append(reff); ent.append(trapped)
            v.append(0.0 if trapped else (1.0 - s_obs) * omega * reff)
            blk.append("pilot" if (b in (5, 10, 15, 20) and j < 3) else "main")
    n = len(slopes)
    return {"run_id": [f"S{i:03d}" for i in range(n)], "slope_deg": np.array(slopes), "v_true_mps": np.array(v),
            "wheel_omega_rad_s": np.array(om), "r_eff_m": np.array(r), "entrapped": np.array(ent), "phi_deg": np.full(n, phi),
            "block": np.array(blk)}


# ---------------------------------------------------------------------------------------------------------------
# Pre-data predictions (PLANNED): prior predictive slip on the ladder, and the error band of the protocol
# ---------------------------------------------------------------------------------------------------------------
LADDER = (0, 5, 10, 15, 20, 25)


def prior_predictive(slopes=LADDER, n=4000, seed=20261017, phi_range=(28.0, 38.0), f_range=None, i0_range=None):
    """Slip at each slope under the ASSUMPTION ranges (no data used).  Returns dict slope -> (p05, p50, p95, P(slip>=0.8)) and
    the entrapment-slope sample (deg at which slip first reaches ENTRAP_SLIP)."""
    f_range = f_range or (PARAM_TABLE["f_r"][1], PARAM_TABLE["f_r"][2])
    i0_range = i0_range or (PARAM_TABLE["i0"][1], PARAM_TABLE["i0"][2])
    rng = np.random.default_rng(seed)
    phi = rng.uniform(*phi_range, n); f = rng.uniform(*f_range, n); i0 = rng.uniform(*i0_range, n)
    out = {}
    for th in slopes:
        s = np.array([model_slip(th, f[k], i0[k], phi[k]) for k in range(n)])
        out[th] = (float(np.percentile(s, 5)), float(np.percentile(s, 50)), float(np.percentile(s, 95)), float(np.mean(s >= ENTRAP_SLIP)))
    ent = np.array([entrapment_slope_model(f[k], i0[k], phi[k]) for k in range(n)])
    return out, ent


def protocol_error_band(slopes=(15, 20, 25), sigma=0.06, n=400, seed=20261018, phi_range=(28.0, 38.0), phi_known=False):
    """Calibrate-on-gentle-then-predict protocol run on SYNTHETIC truths drawn from the prior: distribution of
    (predicted - true mean slip) at each steep slope.  5 runs at each of 0, 5, 10 deg; friction angle taken as known
    (phi_known=True, the soil-test case) or as its midpoint 33 deg when unknown."""
    rng = np.random.default_rng(seed)
    errs = {th: [] for th in slopes}
    for _ in range(n):
        phi = rng.uniform(*phi_range); f = rng.uniform(PARAM_TABLE["f_r"][1], PARAM_TABLE["f_r"][2]); i0 = rng.uniform(PARAM_TABLE["i0"][1], PARAM_TABLE["i0"][2])
        th_c = np.repeat([0.0, 5.0, 10.0], 5) + rng.uniform(-1.5, 1.5, 15)
        th_c = np.maximum(th_c, 0.0)
        s_obs = np.clip(model_slip(th_c, f, i0, phi) + rng.normal(0, sigma, 15), -0.05, 1.0)
        keep = s_obs < ENTRAP_SLIP
        if keep.sum() < 5:
            continue
        phi_used = phi if phi_known else 33.0
        fh, ih = calibrate(th_c[keep], s_obs[keep], phi_used)
        for th in slopes:
            errs[th].append(float(model_slip(th, fh, ih, phi_used) - model_slip(th, f, i0, phi)))
    return {th: (float(np.percentile(v, 5)), float(np.percentile(v, 50)), float(np.percentile(v, 95)), len(v)) for th, v in errs.items()}
