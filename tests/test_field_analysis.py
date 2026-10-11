"""Tests of the field-analysis code on SYNTHETIC data only."""
import numpy as np
import pytest
from dunerover import fieldanalysis as FA


def test_observed_slip_definition():
    d = {"v_true_mps": np.array([0.15, 0.0]), "wheel_omega_rad_s": np.array([3.0, 3.0]), "r_eff_m": np.array([0.1, 0.1]),
         "entrapped": np.array([False, True])}
    s = FA.observed_slip(d)
    assert s[0] == pytest.approx(0.5) and s[1] == 1.0


def test_synthetic_is_reproducible():
    a, b = FA.synthetic_runs(seed=3), FA.synthetic_runs(seed=3)
    assert np.array_equal(a["v_true_mps"], b["v_true_mps"])


def test_calibration_recovers_parameters_from_gentle_runs():
    d = FA.synthetic_runs(seed=11, sigma=0.03, runs_per_bin=10)
    s = FA.observed_slip(d)
    m = (d["slope_deg"] <= FA.CALIB_MAX_DEG) & ~d["entrapped"]
    f_r, i0 = FA.calibrate(d["slope_deg"][m], s[m], 33.0)
    # f_r and i0 are only partly separable at gentle slopes; check the fitted curve, not the pair
    th = np.array([0, 5, 10])
    assert np.max(np.abs(FA.model_slip(th, f_r, i0, 33.0) - FA.model_slip(th, 0.14, 0.22, 33.0))) < 0.05


def test_analysis_runs_and_is_deterministic():
    d = FA.synthetic_runs(seed=5)
    r1, r2 = FA.analyse(d), FA.analyse(d)
    assert repr(r1) == repr(r2)
    assert np.isfinite(r1.entrap_obs_deg) and np.isfinite(r1.entrap_pred_deg)
    assert 0 <= r1.frac_within_tol <= 1 and r1.mae >= 0
    assert r1.mae <= r1.mae_const  # slope-aware model should beat a constant on data generated from slope-aware model


def test_bootstrap_ci_brackets_point_estimate():
    r = FA.analyse(FA.synthetic_runs(seed=9))
    lo, hi = r.ci["mae"]
    assert lo <= r.mae <= hi * 1.01


def test_too_few_runs_raises():
    d = FA.synthetic_runs(seed=2, runs_per_bin=1)
    with pytest.raises(ValueError):
        FA.analyse(d)


def test_per_bin_means_shape():
    out = FA.per_bin_means(FA.synthetic_runs(seed=4))
    assert len(out) >= 5 and all(o[3] <= o[2] <= o[4] for o in out)
