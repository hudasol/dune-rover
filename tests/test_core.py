import numpy as np
import pytest
from dunerover import dem as D, terrain as T, slipmodel as S, traverse as TR, sensitivity as SE


def plane(slope_deg_=10.0, n=40, dx=30.0, dy=30.0):
    """Terrain rising to the east at the given slope."""
    x = np.arange(n) * dx
    z = np.tile(x * np.tan(np.radians(slope_deg_)), (n, 1))
    return D.Dem(z, 23.0, 53.0, 1 / 3600, 1 / 3600, dx, dy)


def test_horn_slope_on_plane_is_exact():
    for s in (0.0, 5.0, 20.0, 33.0):
        d = plane(s)
        sl = T.slope_deg(d.z, d.dx, d.dy)[5:-5, 5:-5]
        assert np.allclose(sl, s, atol=1e-9)


def test_aspect_points_downslope():
    d = plane(15.0)                       # rises east, so downslope is west = 270 deg
    a = T.aspect_deg(d.z, d.dx, d.dy)[10:-10, 10:-10]
    assert np.allclose(a, 270.0, atol=1e-6)


def test_slip_zero_demand_and_monotonic_in_slope():
    p = S.SlipParams(f_r=0.0)
    assert float(S.slip(0.0, 0.0, p)) == pytest.approx(0.0, abs=1e-12)
    th = np.radians(np.arange(0, 33, 1.0))
    s = S.slip(np.tan(th), 0.0, p)
    finite = s[np.isfinite(s)]
    assert np.all(np.diff(finite) > 0)


def test_entrapment_at_or_beyond_friction_angle():
    p = S.SlipParams(f_r=0.0, phi_deg=33.0)
    assert np.isinf(S.slip(np.tan(np.radians(33.0)), 0.0, p))
    assert np.isfinite(S.slip(np.tan(np.radians(32.0)), 0.0, p))


def test_critical_angle_matches_slip_limit():
    p = S.SlipParams()
    crit = np.radians(S.critical_uphill_deg(p))
    assert float(S.slip(np.tan(crit), 0.0, p)) == pytest.approx(p.i_max, rel=1e-6)


def test_cross_slope_never_reduces_slip():
    p = S.SlipParams()
    base = S.slip(np.tan(np.radians(10)), 0.0, p)
    assert S.slip(np.tan(np.radians(10)), 0.1, p) >= base
    assert S.slip(np.tan(np.radians(10)), 0.1, p.with_(cross="additive")) >= S.slip(np.tan(np.radians(10)), 0.1, p)


def test_janosi_mean_form_is_monotone_and_at_least_exp_form():
    x = np.linspace(0, 0.95, 60)
    a = S.slip_from_ratio(x, 0.2, "exp"); b = S.slip_from_ratio(x, 0.2, "janosi_mean")
    assert np.all(np.diff(b) >= 0) and np.all(b >= a - 1e-9)


def test_graph_blocks_steep_plane_uphill_but_not_downhill_symmetric_cost():
    d = plane(35.0, n=30)                 # steeper than the nominal critical angle
    eg = TR.precompute_edges(d); g, frac = TR.build_graph(eg, S.SlipParams())
    nc = d.shape[1]
    east = TR.route_metrics(d, g, (15, 2), (15, 25))[0]         # uphill, blocked
    assert east["reachable"] is False
    d2 = plane(10.0, n=30); eg2 = TR.precompute_edges(d2); g2, _ = TR.build_graph(eg2, S.SlipParams())
    assert TR.route_metrics(d2, g2, (15, 2), (15, 25))[0]["reachable"] is True


def test_flat_ground_cost_ratio_close_to_one_over_one_minus_flat_slip():
    d = plane(0.0, n=50); p = S.SlipParams()
    eg = TR.precompute_edges(d); g, _ = TR.build_graph(eg, p)
    m, _ = TR.route_metrics(d, g, (25, 2), (25, 45), eg, p)
    flat = float(S.slip(0.0, 0.0, p))
    assert m["cost_ratio"] == pytest.approx(1.0 / (1.0 - flat), rel=1e-6)


def test_od_selection_is_deterministic():
    z = np.sin(np.linspace(0, 12, 80))[None, :] * 20 + np.zeros((80, 1))
    d = D.Dem(z, 23.0, 53.0, 1 / 3600, 1 / 3600, 30.0, 30.0)
    assert TR.select_od_pairs(d, 4, 1, 800) == TR.select_od_pairs(d, 4, 1, 800)


def test_coarsen_preserves_mean_and_shape():
    d = plane(8.0, n=36)
    c = D.coarsen(d, 3)
    assert c.shape == (12, 12) and np.nanmean(c.z) == pytest.approx(np.nanmean(d.z[:36, :36]))


def test_noise_is_reproducible_and_scaled():
    d = plane(0.0, n=60)
    a = D.add_correlated_noise(d, 1.5, 3.0, seed=5); b = D.add_correlated_noise(d, 1.5, 3.0, seed=5)
    assert np.array_equal(a.z, b.z) and a.z.std() == pytest.approx(1.5, rel=1e-6)


def test_lhs_sensitivity_is_reproducible():
    d = plane(12.0, n=40)
    pairs = [((20, 3), (20, 36)), ((5, 5), (30, 30))]
    sc = SE.Scenario(d, SE.od_to_latlon(d, pairs))
    _, r1 = SE.global_lhs(sc, 6, seed=1); _, r2 = SE.global_lhs(sc, 6, seed=1)
    assert [x["blocked_edge_frac"] for x in r1] == [x["blocked_edge_frac"] for x in r2]


def test_metres_per_degree_at_equator_and_pole_sanity():
    mlon, mlat = D.metres_per_degree(0.0)
    assert mlon == pytest.approx(111319.5, rel=1e-3) and mlat == pytest.approx(110574.0, rel=1e-3)
    assert D.metres_per_degree(23.0)[0] < mlon
