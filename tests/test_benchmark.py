"""Unit tests of the stage 25 and 26 benchmark code on synthetic surfaces (no lidar needed)."""
import numpy as np
import pytest

from dunerover import benchmark as B
from dunerover import planner as PL


def _ramp(nr=40, nc=40, d=1.0, deg=10.0):
    x = np.arange(nc) * d
    return np.tile(np.tan(np.radians(deg)) * x, (nr, 1))


def test_tri_and_roughness_on_planes():
    z = _ramp(deg=20.0)
    inner = (slice(2, -2), slice(2, -2))
    assert np.allclose(B.plane_roughness(z, 1.0, 3)[inner], 0.0, atol=1e-6)
    assert np.allclose(B.plane_roughness(z, 1.0, 5)[inner], 0.0, atol=1e-6)
    t = np.tan(np.radians(20.0))
    # 3 neighbours each side at +-t (left, right, and 4 diagonals at +-t), 2 at 0: sqrt(6 t^2)
    assert np.allclose(B.tri(z, 1.0)[inner], np.sqrt(6) * t)


def test_roughness_matches_lstsq():
    rng = np.random.default_rng(1)
    z = rng.normal(size=(9, 9))
    r = B.plane_roughness(z, 2.0, 3)
    win = z[3:6, 3:6].ravel()
    yy, xx = np.mgrid[-1:2, -1:2]
    A = np.column_stack([np.ones(9), xx.ravel(), yy.ravel()])
    coef, *_ = np.linalg.lstsq(A, win, rcond=None)
    rms = np.sqrt(np.mean((win - A @ coef) ** 2))
    assert r[4, 4] == pytest.approx(rms / 2.0)


def test_feature_stack_shape_and_finite():
    z = np.random.default_rng(0).normal(size=(30, 25)).cumsum(0)
    F = B.feature_stack(z, 30.0)
    assert F.shape == (30, 25, len(B.FEATURE_NAMES))
    assert np.isfinite(F).all()


def test_face_patches_drop_small_groups():
    st = np.zeros((20, 20), bool)
    st[2:4, 2:7] = True        # 10 posts: kept
    st[10, 10] = True          # isolated: dropped
    st[15:17, 15:18] = True    # 6 posts: dropped
    p = B.face_patches(st)
    assert p[2:4, 2:7].all() and not p[10, 10] and not p[15:17, 15:18].any()


def test_cell_truth_counts_posts():
    st = np.zeros((20, 20), bool)
    st[0:10, 0] = True
    lab = B.cell_truth(st, 10)
    assert lab[0, 0] and not lab[1, 0] and not lab[0, 1]


def test_weighted_auc_matches_sklearn():
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(3)
    s = np.round(rng.normal(size=500), 1)          # ties on purpose
    y = rng.random(500) < 0.3
    w = rng.integers(0, 4, 500).astype(float)
    rs = B.RankedScore(s, y)
    assert rs.auc() == pytest.approx(roc_auc_score(y, s))
    assert rs.auc(w) == pytest.approx(roc_auc_score(y, s, sample_weight=w))


def test_block_bootstrap_is_deterministic_and_blockwise():
    ids = B.block_ids((10, 10), 5)
    assert len(np.unique(ids)) == 4
    w1 = list(B.block_bootstrap_weights(ids, 3, 7)); w2 = list(B.block_bootstrap_weights(ids, 3, 7))
    for a, b in zip(w1, w2):
        assert np.array_equal(a, b)
        # every cell of a block carries the same weight
        for g in np.unique(ids):
            assert len(np.unique(a[ids.ravel() == g])) == 1


def test_recall_at_fpr():
    s = np.r_[np.arange(100), np.arange(100, 110)].astype(float)
    y = np.r_[np.zeros(100, bool), np.ones(10, bool)]
    assert B.recall_at_fpr(s, y, 0.10) == 1.0


def test_platt_recovers_probability():
    rng = np.random.default_rng(0)
    s = rng.normal(size=4000)
    y = rng.random(4000) < 1 / (1 + np.exp(-2 * s))
    p = B.Platt().fit(s, y).predict(np.array([0.0, 1.0]))
    assert p[0] == pytest.approx(0.5, abs=0.05) and p[1] == pytest.approx(1 / (1 + np.exp(-2)), abs=0.05)


def test_bicubic_on_a_plane_keeps_its_slope():
    z = _ramp(nr=12, nc=12, d=10.0, deg=15.0)
    m = B.bicubic_max_slope(z, 10)
    assert np.allclose(m[2:-2, 2:-2], 15.0, atol=0.2)


def test_score_route_detects_patch_and_counts_entries():
    patch = np.zeros((100, 100), bool)
    patch[:, 50:53] = True                       # a wall of face posts across the window
    z = np.zeros((100, 100))
    rc = np.array([[5, 0], [5, 9]])              # 10 m cells: from x=5 to x=95 m along row 55 m
    r = B.score_route(rc, 10, patch, z, 25.5)
    assert r["unsafe"] and r["patch_entries"] == 1 and r["length_m"] == pytest.approx(90.0)
    rc2 = np.array([[5, 0], [5, 4]])
    assert not B.score_route(rc2, 10, patch, z, 25.5)["unsafe"]


def test_score_route_uphill_events_on_a_steep_ramp():
    z = np.tile(np.arange(200) * np.tan(np.radians(30.0)), (20, 1))
    rc = np.array([[0, 0], [0, 19]])
    r = B.score_route(rc, 10, np.zeros_like(z, bool), z, 25.5)
    assert r["uphill_events"] > 0
    assert B.score_route(rc[::-1], 10, np.zeros_like(z, bool), z, 25.5)["uphill_events"] == 0


def test_grid_shortest_reaches_goal():
    p = B.grid_shortest((10, 10), (0, 0), (3, 7))
    assert tuple(p[-1]) == (3, 7) and len(p) == 8


def test_with_hazard_reclassifies_and_keeps_nodata():
    z = np.random.default_rng(2).normal(scale=0.5, size=(12, 12)).cumsum(1)
    a = PL.assess(PL.raster_from_array(z, 30.0), n_draws=16)
    a.classes[0, 0] = 5
    h = np.zeros_like(a.face_prob); h[5, 5] = 0.9
    b = B.with_hazard(a, h)
    assert b.classes[0, 0] == 5 and b.face_prob[5, 5] == 0.9
    assert b.classes[5, 5] in (3, 4, 1)          # face risk becomes UNKNOWN (or stays BLOCKED)
    assert a.face_prob is not b.face_prob


def test_routes_from_matches_planner():
    z = np.zeros((15, 15))
    a = PL.assess(PL.raster_from_array(z, 10.0), n_draws=16)
    g = PL.policy_graph(a, "naive")
    out = B.routes_from(g, 15, [(0, 0), (0, 0)], [(14, 14), (0, 5)])
    assert tuple(out[0][-1]) == (14, 14) and len(out[0]) == 15
    assert tuple(out[1][-1]) == (0, 5)


def test_cnn_trains_and_predicts_shape():
    pytest.importorskip("torch")
    from dunerover import benchmark_cnn as C
    rng = np.random.default_rng(0)
    z = rng.normal(size=(40, 40)).cumsum(0)
    x = C.channels(z, 10.0)
    y = B.slope_tan(z, 10.0) > 0.2
    net = C.fit([(x, y)], crop=32, steps=3)
    p = C.predict(net, x)
    assert p.shape == (40, 40) and np.all((p >= 0) & (p <= 1))
