"""Tests for the sub grid detector and the three class rules.  SIMULATION ONLY code; tests check mechanics, not realism."""
import numpy as np
from dunerover import subgrid as SG
from dunerover import threeclass as TC
from dunerover.slipmodel import SlipParams, slip

def test_features_1d_equal_2d_for_extruded_profile():
    rng = np.random.default_rng(1); d = 30.0
    for _ in range(5):
        z1 = np.cumsum(rng.normal(0, 1, SG.NPOST)) * 2
        f1 = SG.features_1d(z1[None, :], d)[0]
        f2 = SG.features_2d(np.tile(z1, (19, 1)), d, d)[9, SG.NPOST // 2]
        assert np.allclose(f1, f2)

def test_no_active_faces_means_no_truth():
    F, y, _ = SG.synth(2000, 30.0, 5, "base", pi=0.0)
    assert not y.any()

def test_all_faces_wide_cell_always_hits_when_cell_wider_than_wavelength():
    F, y, meta = SG.synth(4000, 90.0, 6, "base", pi=1.0)
    assert y[meta["lam"] <= 90.0].all()

def test_detector_has_skill_and_flat_ground_is_safe():
    m = SG.fit(30.0, n=20000)
    e = SG.evaluate_detector(m, n=8000)
    assert e["auc"] > 0.8 and e["brier"] < e["brier_climatology"]
    flat = np.zeros((30, 30))
    assert SG.FaceModel.predict(m, SG.features_2d(flat, 30.0, 30.0)).max() < TC.TAU   # a logistic fit gives about 0.09 on perfectly flat ground, below tau

def test_closed_form_pass_rule_matches_slip_model():
    rng = np.random.default_rng(2)
    for _ in range(20):
        p = SlipParams(phi_deg=rng.uniform(28, 38), f_r=rng.uniform(0.05, 0.25), i0=rng.uniform(0.05, 0.4), i_max=rng.uniform(0.4, 0.7))
        ta = rng.uniform(-0.8, 0.8, 500); tc = rng.uniform(0, 0.5, 500)
        thr = (1 - np.exp(-p.i_max / p.i0)) * p.mu_max
        closed = np.hypot(np.abs(ta + p.f_r), tc) <= thr
        direct = slip(ta, tc, p) <= p.i_max
        assert (closed == direct).mean() > 0.999

def test_classify_codes():
    q = np.array([0.0, 0.5, 1.0, 1.0, 0.5])
    p = np.array([0.0, 0.0, 0.0, 0.9, 0.9])
    assert list(TC.classify(q, p)) == [1, 2, 0, 3, 4]
    sh = TC.shares(TC.classify(q, p))
    assert abs(sh["UNKNOWN (total)"] - 0.6) < 1e-9

def test_mc_is_reproducible_and_steep_cell_blocked():
    from dunerover.dem import Dem
    from dunerover import traverse as TR
    z = np.zeros((20, 20)); z[:, 10:] = np.arange(10)[None, :] * 30 * np.tan(np.radians(40))   # 40 deg ramp east
    dem = Dem(z, 24.0, 53.0, 1 / 3600, 1 / 3600, 30.0, 30.0)
    eg = TR.precompute_edges(dem)
    d1, d2 = TC.lhs_draws(32, 11), TC.lhs_draws(32, 11)
    q1, q2 = TC.q_pass(eg, d1), TC.q_pass(eg, d2)
    assert np.array_equal(q1, q2)
    assert q1[10, 14] <= TC.Q_LO or q1[10, 14] < 0.5     # on the 40 degree ramp few headings pass
    assert q1[10, 3] >= 0.95                              # flat ground passes
