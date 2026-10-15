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


# ---- wrong-model and tolerance-rule tests (SYNTHETIC data with known ground truth) ----
def _rate(kind, sigma, n=12, **kw):
    ok = 0
    for k in range(n):
        d = FA.synthetic_runs(seed=500 + k, sigma=sigma, kind=kind)
        ok += FA.analyse(d, n_boot=10, **kw).adequate
    return ok / n


def test_pilot_sigma_tracks_true_noise():
    for sigma in (0.03, 0.10):
        est = [FA.pilot_sigma(FA.synthetic_runs(seed=900 + k, sigma=sigma))[0] for k in range(20)]
        # within-bin spread includes the plus or minus 1.5 deg slope jitter, so it is somewhat above sigma
        assert sigma * 0.8 < np.median(est) < sigma * 2.2


def test_tolerance_rule_and_floor():
    assert FA.tolerance_from_pilot(0.10) == pytest.approx(0.30)
    assert FA.tolerance_from_pilot(0.005) == FA.TOL_FLOOR
    r = FA.analyse(FA.synthetic_runs(seed=3), n_boot=10)
    assert r.tol == pytest.approx(FA.tolerance_from_pilot(r.sigma_pilot)) and r.sigma_source == "pilot block"
    assert FA.analyse(FA.synthetic_runs(seed=3), n_boot=10, tol=0.15).tol == 0.15


def _blatant_wrong(seed):
    """Truth: slip 0.9 on every slope above 10 deg (completely different from the model); gentle slopes follow the model."""
    d = FA.synthetic_runs(seed=seed, sigma=0.02)
    hi = d["slope_deg"] > 10.5
    om, rr = d["wheel_omega_rad_s"], d["r_eff_m"]
    d["v_true_mps"] = np.where(hi, 0.1 * om * rr, d["v_true_mps"]); d["entrapped"] = np.where(hi, False, d["entrapped"])
    return d


def test_blatantly_wrong_model_is_always_failed():
    assert not any(FA.analyse(_blatant_wrong(700 + k), n_boot=10).adequate for k in range(10))


def test_model_right_with_tiny_noise_is_mostly_passed():
    assert _rate("model", 0.01) >= 0.5   # not 1.0: calibration trade-off between f_r and i0 limits even noise-free passes


def test_observed_entrapment_slope_is_mean_slope_not_bin_centre():
    sl = np.array([28.0, 28.5, 29.0, 10.0]); tr = np.array([True, True, True, False])
    assert FA.entrapment_slope_observed(sl, tr) == pytest.approx(28.5)


def test_high_noise_experiment_is_flagged_uninformative():
    r = FA.analyse(FA.synthetic_runs(seed=8, sigma=0.20), n_boot=10)
    assert not r.informative


def test_truth_generators_differ_where_expected():
    th = np.array([5.0, 15.0, 25.0])
    m, j, c = (FA.truth_slip(k, th) for k in ("model", "janosi_mean", "collapse"))
    assert np.allclose(m[0], c[0]) and c[2] == pytest.approx(0.85) and not np.allclose(m, j)


def test_prior_predictive_and_protocol_band_are_deterministic():
    a, ea = FA.prior_predictive(n=200, seed=1); b, eb = FA.prior_predictive(n=200, seed=1)
    assert a == b and np.array_equal(np.nan_to_num(ea), np.nan_to_num(eb))
    assert a[0][1] < a[25][1]


# ---- revised ladder (2026-10-15, docs/PREDICTIONS.md stage 6) ----------------------------------------------------
def test_new_design_records_target_bins_and_tight_jitter():
    d = FA.synthetic_runs(seed=3, design="2026-10-15")
    assert set(np.unique(d["bin_deg"])) == set(FA.LADDER_2026_10_15)
    mid = (d["bin_deg"] >= 10) & (d["bin_deg"] <= 20)
    assert np.all(np.abs(d["slope_deg"][mid] - d["bin_deg"][mid]) <= 1.0)


def test_old_design_is_unchanged_by_the_new_option():
    a, b = FA.synthetic_runs(seed=11), FA.synthetic_runs(seed=11, design="2026-10-12")
    assert "bin_deg" not in a and np.array_equal(a["slope_deg"], b["slope_deg"])


def test_pilot_sigma_uses_target_bins_when_given():
    d = FA.synthetic_runs(seed=5, sigma=0.05, design="2026-10-15")
    sig, src = FA.pilot_sigma(d, 2.5)
    assert src == "pilot block" and 0.02 < sig < 0.10


def test_blatantly_wrong_model_is_always_failed_new_design():
    def wrong(seed):
        d = FA.synthetic_runs(seed=seed, sigma=0.02, design="2026-10-15")
        hi = d["slope_deg"] > 10.5
        d["v_true_mps"] = np.where(hi, 0.1 * d["wheel_omega_rad_s"] * d["r_eff_m"], d["v_true_mps"]); d["entrapped"] = np.where(hi, False, d["entrapped"])
        return d
    assert not any(FA.analyse(wrong(700 + k), n_boot=10, bin_width=2.5).adequate for k in range(10))


def test_dumont_truth_follows_the_published_text():
    t = FA.truth_slip("dumont", np.array([2.0, 12.4, 16.0, 20.0, 23.0]))
    assert t[0] == pytest.approx(0.10) and t[1] < 0.5 and abs(t[2] - 0.75) < 0.03 and abs(t[3] - 0.90) < 0.02 and t[4] == 1.0
