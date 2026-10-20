"""Tests of the model families (stage 15)."""
import numpy as np
import pytest
from dunerover.models import FAMILIES
from dunerover.slipmodel import SlipParams, slip

W1 = {"radius_m": 0.25, "width_m": 0.40, "load_N": 556.0, "soil_set": "toyoura_ishigami2007"}
SL = np.arange(0.0, 30.1, 2.5)


def test_every_family_has_bounds_containing_nominal():
    for f in FAMILIES.values():
        th = f.nominal(W1)
        for p in f.params:
            assert p.low <= th[p.name] <= p.high, (f.name, p.name)


@pytest.mark.parametrize("name", list(FAMILIES))
def test_slip_in_unit_interval_and_monotone(name):
    f = FAMILIES[name]
    y = f.predict(SL, "direct ascent", W1, f.nominal(W1))
    assert np.all((y >= 0) & (y <= 1))
    assert np.all(np.diff(y) >= -1e-3)


def test_exp_family_reproduces_existing_model():
    f = FAMILIES["exp_existing"]
    th = {"phi_deg": 33.0, "f_r": 0.12, "i0": 0.20}
    t = np.tan(np.radians(SL))
    ref = np.minimum(slip(t, np.zeros_like(t), SlipParams()), 1.0)
    assert np.allclose(f.predict(SL, "direct ascent", {}, th), ref)


def test_bekker_wong_large_wheel_climbs_gentle_slopes_and_entraps_steep():
    f = FAMILIES["bekker_wong"]
    y = f.predict(SL, "direct ascent", W1, f.nominal(W1))
    assert y[0] < 0.25 and y[-1] == 1.0


def test_bekker_wong_does_not_claim_side_slopes():
    f = FAMILIES["bekker_wong"]
    assert not f.applies("side slope")
    with pytest.raises(ValueError):
        f.predict(SL, "side slope", W1, f.nominal(W1))


def test_logistic_half_at_s50():
    f = FAMILIES["logistic_empirical"]
    assert abs(f.predict([12.0], "direct ascent", {}, {"s50_deg": 12.0, "w_deg": 3.0})[0] - 0.5) < 1e-9
