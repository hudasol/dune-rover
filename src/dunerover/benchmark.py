"""Baselines, truth and metrics for the stage 25 and 26 benchmark (docs/PREDICTIONS.md).

Stage 25 scores slip face detectors on coarse elevation models (10 m and 30 m block means of one metre lidar, and the
Copernicus GLO-30 product) against the lidar itself. Stage 26 plans routes with the shipped planner, swapping the
hazard layer, and scores them on dune scale face patches in the lidar. Everything here is SIMULATED BY ME; the inputs
are PUBLISHED elevation data.

Baselines (scores per coarse cell; larger means more likely to hold a face):
  slope      coarse Horn slope (the classical slope costmap input)
  tri        terrain ruggedness index (Riley et al. 1999), divided by the posting
  rough      root mean square residual of a plane fitted to the 3 x 3 neighbourhood (GESTALT style roughness)
  bicubic    steepest slope of the surface interpolated to one metre with a cubic spline
  gbm        gradient boosted trees on 14 terrain features, trained leave one site out on lidar labels
  cnn        small dilated fully convolutional network, leave one site out (benchmark_cnn.py, optional torch)
"""
from __future__ import annotations
import numpy as np
from scipy.ndimage import (label as nd_label, maximum_filter, minimum_filter, uniform_filter, zoom,
                           distance_transform_edt, map_coordinates)

from .terrain import horn_gradient
from . import subgrid as SG

FACE_DEG = SG.FACE_TRUTH_DEG          # 28 deg
MIN_POSTS = 10                        # stage 12 truth: at least 10 steep one metre posts per cell / per patch
FEATURE_NAMES = ("slope_tan", "tri", "rough3", "rough5", "curv_profile", "curv_plan", "tpi3", "tpi7", "tpi15",
                 "relief3", "relief7", "max_slope3", "det_convexity", "det_slope_break")
GBM_PARAMS = dict(learning_rate=0.05, max_iter=300, max_leaf_nodes=31, random_state=0)


# ---------------------------------------------------------------------------------------------------------------------
# grids and truth
# ---------------------------------------------------------------------------------------------------------------------
def fill_nearest(z: np.ndarray) -> np.ndarray:
    void = ~np.isfinite(z)
    if not void.any():
        return z
    idx = distance_transform_edt(void, return_distances=False, return_indices=True)
    return z[tuple(idx)]


def block(a: np.ndarray, k: int, how: str = "mean") -> np.ndarray:
    if k == 1:
        return a.astype(float)
    nr, nc = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    b = a[:nr, :nc].reshape(nr // k, k, nc // k, k)
    return {"mean": b.mean(axis=(1, 3)), "sum": b.sum(axis=(1, 3)), "max": b.max(axis=(1, 3)), "any": b.any(axis=(1, 3))}[how]


def slope_tan(z: np.ndarray, d: float) -> np.ndarray:
    ge, gn = horn_gradient(z, d, d)
    return np.hypot(ge, gn)


def slope_deg(z: np.ndarray, d: float) -> np.ndarray:
    return np.degrees(np.arctan(slope_tan(z, d)))


def steep_posts(z1: np.ndarray, void: np.ndarray, lo_deg: float = FACE_DEG, hi_deg: float | None = None):
    """Steep one metre posts (voids filled with the nearest valid post for the slope, never steep). Returns (steep, slope)."""
    s1 = slope_deg(fill_nearest(z1), 1.0)
    st = s1 >= lo_deg
    if hi_deg is not None:
        st &= s1 <= hi_deg
    return st & ~void, s1


def cell_truth(steep: np.ndarray, k: int, min_posts: int = MIN_POSTS) -> np.ndarray:
    """Primary label of stage 12: at least min_posts steep posts inside the k x k footprint."""
    return block(steep.astype(np.int32), k, "sum") >= min_posts


def face_patches(steep: np.ndarray, min_posts: int = MIN_POSTS) -> np.ndarray:
    """Posts of 8 connected steep groups with at least min_posts posts (dune scale faces; isolated posts dropped)."""
    lab, n = nd_label(steep, structure=np.ones((3, 3), dtype=int))
    if n == 0:
        return np.zeros_like(steep, dtype=bool)
    sizes = np.bincount(lab.ravel())
    keep = sizes >= min_posts
    keep[0] = False
    return keep[lab]


# ---------------------------------------------------------------------------------------------------------------------
# terrain features of a coarse surface
# ---------------------------------------------------------------------------------------------------------------------
def tri(z: np.ndarray, d: float) -> np.ndarray:
    """Terrain ruggedness index (Riley et al. 1999): sqrt of the sum of squared differences to the 8 neighbours, / d."""
    zp = np.pad(z, 1, mode="edge")
    acc = np.zeros_like(z, dtype=float)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr or dc:
                acc += (zp[1 + dr:1 + dr + z.shape[0], 1 + dc:1 + dc + z.shape[1]] - z) ** 2
    return np.sqrt(acc) / d


def plane_roughness(z: np.ndarray, d: float, size: int = 3) -> np.ndarray:
    """RMS residual of the least squares plane z = a + b x + c y over a size x size window, divided by d.

    For a symmetric window the plane fit separates: b and c are moment ratios and the residual follows from the
    windowed means, so the whole grid is computed with uniform filters (no loop over cells).
    """
    h = size // 2
    off = np.arange(-h, h + 1, dtype=float)
    sxx = float((off ** 2).mean())                     # mean of x^2 over the window (same for y)
    zp = np.pad(z, h, mode="edge")
    n = size * size
    m = uniform_filter(zp, size, mode="nearest")[h:-h or None, h:-h or None]
    mzz = uniform_filter(zp * zp, size, mode="nearest")[h:-h or None, h:-h or None]
    # windowed sums of x z and y z (x along columns, y along rows) by explicit shifts (small windows)
    mxz = np.zeros_like(z, dtype=float); myz = np.zeros_like(z, dtype=float)
    for i, dy in enumerate(off):
        for j, dx in enumerate(off):
            sl = zp[i:i + z.shape[0], j:j + z.shape[1]]
            mxz += dx * sl; myz += dy * sl
    mxz /= n; myz /= n
    b = mxz / sxx; c = myz / sxx
    var_res = mzz - m ** 2 - (b ** 2 + c ** 2) * sxx
    return np.sqrt(np.clip(var_res, 0, None)) / d


def curvatures(z: np.ndarray, d: float):
    """Profile and plan curvature (1/m, times d to be dimensionless)."""
    zp = np.pad(z, 1, mode="edge")
    zc = zp[1:-1, 1:-1]
    zx = (zp[1:-1, 2:] - zp[1:-1, :-2]) / (2 * d)
    zy = (zp[2:, 1:-1] - zp[:-2, 1:-1]) / (2 * d)
    zxx = (zp[1:-1, 2:] - 2 * zc + zp[1:-1, :-2]) / d ** 2
    zyy = (zp[2:, 1:-1] - 2 * zc + zp[:-2, 1:-1]) / d ** 2
    zxy = (zp[2:, 2:] - zp[2:, :-2] - zp[:-2, 2:] + zp[:-2, :-2]) / (4 * d * d)
    g2 = np.maximum(zx ** 2 + zy ** 2, 1e-12)
    prof = (zx ** 2 * zxx + 2 * zx * zy * zxy + zy ** 2 * zyy) / (g2 * np.sqrt(1 + g2) ** 3)
    plan = (zy ** 2 * zxx - 2 * zx * zy * zxy + zx ** 2 * zyy) / (g2 ** 1.5)
    return prof * d, np.clip(plan * d, -50, 50)


def tpi(z: np.ndarray, d: float, size: int) -> np.ndarray:
    return (z - uniform_filter(z, size, mode="nearest")) / d


def relief(z: np.ndarray, d: float, size: int) -> np.ndarray:
    return (maximum_filter(z, size, mode="nearest") - minimum_filter(z, size, mode="nearest")) / d


def feature_stack(z: np.ndarray, d: float) -> np.ndarray:
    """The 14 registered features (FEATURE_NAMES), shape (rows, cols, 14)."""
    s = slope_tan(z, d)
    det = SG.features_2d(z, d, d)
    prof, plan = curvatures(z, d)
    cols = [s, tri(z, d), plane_roughness(z, d, 3), plane_roughness(z, d, 5), prof, plan,
            tpi(z, d, 3), tpi(z, d, 7), tpi(z, d, 15), relief(z, d, 3), relief(z, d, 7),
            maximum_filter(s, 3, mode="nearest"), det[..., 1], det[..., 2]]
    return np.stack(cols, axis=-1)


def bicubic_max_slope(zc: np.ndarray, k: int) -> np.ndarray:
    """Steepest slope (deg) of the coarse surface interpolated to one metre with a cubic spline, per coarse cell."""
    zf = zoom(zc, k, order=3, mode="nearest", grid_mode=True)
    return block(slope_deg(zf, 1.0), k, "max")


# ---------------------------------------------------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------------------------------------------------
class RankedScore:
    """A score vector prepared once for fast weighted AUC (ties count one half)."""

    def __init__(self, score: np.ndarray, y: np.ndarray):
        score = np.asarray(score, float).ravel(); y = np.asarray(y, bool).ravel()
        self.order = np.argsort(score, kind="mergesort")
        s = score[self.order]
        self.y = y[self.order]
        # group id of each sorted element (equal scores share a group)
        self.grp = np.concatenate([[0], np.cumsum(s[1:] != s[:-1])])
        self.ngrp = int(self.grp[-1]) + 1 if len(s) else 0

    def auc(self, w: np.ndarray | None = None) -> float:
        """Weighted AUC; w are per element weights in the ORIGINAL order (bootstrap counts)."""
        ww = np.ones(len(self.y)) if w is None else np.asarray(w, float)[self.order]
        wp = np.where(self.y, ww, 0.0); wn = np.where(self.y, 0.0, ww)
        gp = np.bincount(self.grp, wp, self.ngrp); gn = np.bincount(self.grp, wn, self.ngrp)
        P, N = gp.sum(), gn.sum()
        if P <= 0 or N <= 0:
            return float("nan")
        below = np.concatenate([[0.0], np.cumsum(gn)[:-1]])
        return float((gp * (below + 0.5 * gn)).sum() / (P * N))


def auc(score, y) -> float:
    return RankedScore(score, y).auc()


def average_precision(score, y) -> float:
    from sklearn.metrics import average_precision_score
    y = np.asarray(y, bool).ravel()
    if y.all() or not y.any():
        return float("nan")
    return float(average_precision_score(y, np.asarray(score, float).ravel()))


def recall_at_fpr(score, y, fpr: float = 0.10) -> float:
    """Share of true face cells flagged when the threshold flags at most fpr of the cells without a face."""
    score = np.asarray(score, float).ravel(); y = np.asarray(y, bool).ravel()
    neg = np.sort(score[~y])
    if len(neg) == 0 or not y.any():
        return float("nan")
    thr = neg[min(len(neg) - 1, int(np.floor((1 - fpr) * len(neg))))]
    return float((score[y] > thr).mean())


def brier(p, y) -> float:
    return float(np.mean((np.asarray(p, float).ravel() - np.asarray(y, float).ravel()) ** 2))


def block_ids(shape, cells_per_block: int) -> np.ndarray:
    r, c = np.indices(shape)
    nbc = int(np.ceil(shape[1] / cells_per_block))
    return (r // cells_per_block) * nbc + (c // cells_per_block)


def block_bootstrap_weights(ids: np.ndarray, n_boot: int, seed: int):
    """Yield per cell weights (how often its block was drawn) for n_boot block bootstrap resamples."""
    ids = ids.ravel()
    ub, inv = np.unique(ids, return_inverse=True)
    rng = np.random.default_rng(seed)
    for _ in range(n_boot):
        cnt = np.bincount(rng.integers(0, len(ub), len(ub)), minlength=len(ub))
        yield cnt[inv].astype(float)


# ---------------------------------------------------------------------------------------------------------------------
# calibration and learned baselines
# ---------------------------------------------------------------------------------------------------------------------
def _logit(p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


class Platt:
    """Logistic calibration of one score (fitted leave one site out by the caller)."""

    def __init__(self, transform: str = "identity"):
        self.transform = transform

    def _x(self, s):
        s = np.asarray(s, float).ravel()
        return (_logit(s) if self.transform == "logit" else s)[:, None]

    def fit(self, s, y):
        from sklearn.linear_model import LogisticRegression
        x = self._x(s)
        self.mu, self.sd = float(x.mean()), float(x.std() or 1.0)
        self.m = LogisticRegression(C=1e6, max_iter=1000).fit((x - self.mu) / self.sd, np.asarray(y, bool).ravel())
        return self

    def predict(self, s):
        shp = np.shape(s)
        return self.m.predict_proba((self._x(s) - self.mu) / self.sd)[:, 1].reshape(shp)


def gbm_fit(X: np.ndarray, y: np.ndarray):
    from sklearn.ensemble import HistGradientBoostingClassifier
    return HistGradientBoostingClassifier(**GBM_PARAMS).fit(X, np.asarray(y, bool))


def gbm_predict(model, F: np.ndarray) -> np.ndarray:
    shp = F.shape[:-1]
    return model.predict_proba(F.reshape(-1, F.shape[-1]))[:, 1].reshape(shp)


# ---------------------------------------------------------------------------------------------------------------------
# coarse grid of a real product
# ---------------------------------------------------------------------------------------------------------------------
def sample_geographic(raster, lon: np.ndarray, lat: np.ndarray) -> np.ndarray:
    """Bilinear interpolation of a geographic raster (planner.Raster, post centres) at longitude and latitude."""
    r = (raster.y0 - np.asarray(lat)) / raster.py
    c = (np.asarray(lon) - raster.x0) / raster.px
    return map_coordinates(raster.z, [r, c], order=1, mode="nearest")


# ---------------------------------------------------------------------------------------------------------------------
# planning with a swapped hazard layer, and scoring on the lidar
# ---------------------------------------------------------------------------------------------------------------------
def with_hazard(a, h: np.ndarray):
    """A copy of a planner Assessment whose face probability is h, reclassified with the product's own rule."""
    import copy
    from . import threeclass as TC
    b = copy.copy(a)
    b.face_prob = np.asarray(h, float)
    cls = TC.classify(a.q_pass, b.face_prob, a.tau)
    cls[a.classes == 5] = 5
    b.classes = cls
    return b


def routes_from(g, nc: int, sources: list, targets: list):
    """Shortest routes for several (source, target) cell pairs on a csr graph; None where unreachable."""
    from scipy.sparse.csgraph import dijkstra
    src = [s[0] * nc + s[1] for s in sources]
    uniq = sorted(set(src))
    dist, pred = dijkstra(g, directed=True, indices=uniq, return_predecessors=True)
    row = {s: i for i, s in enumerate(uniq)}
    out = []
    for s, t in zip(src, targets):
        i, tt = row[s], t[0] * nc + t[1]
        if not np.isfinite(dist[i, tt]):
            out.append(None); continue
        path = [tt]
        while path[-1] != s:
            path.append(int(pred[i, path[-1]]))
        out.append(np.column_stack(np.divmod(np.array(path[::-1]), nc)))
    return out


def grid_shortest(shape, s, t):
    """8 connected shortest grid path ignoring terrain (diagonal steps first, then straight), as (row, col) cells."""
    r, c = s
    out = [(r, c)]
    while (r, c) != tuple(t):
        r += int(np.sign(t[0] - r)); c += int(np.sign(t[1] - c))
        out.append((r, c))
    return np.array(out)


def score_route(rc: np.ndarray, k: int, patch: np.ndarray, z1f: np.ndarray, crit_deg: float,
                step: float = 0.5, baseline: float = 10.0) -> dict:
    """Score a route of coarse cells (posting k m) on the one metre truth: polyline through cell centres sampled every
    `step` m at the nearest post. unsafe = any sample on a face patch post."""
    pts = (np.asarray(rc, float) + 0.5) * k                     # metres from the window's north west corner (row, col)
    samples = [pts[:1]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(int(np.ceil(np.hypot(*(b - a)) / step)), 1)
        samples.append(a + (b - a) * (np.arange(1, n + 1)[:, None] / n))
    sp = np.concatenate(samples)
    ri = np.clip(np.floor(sp[:, 0]).astype(int), 0, patch.shape[0] - 1)
    ci = np.clip(np.floor(sp[:, 1]).astype(int), 0, patch.shape[1] - 1)
    on = patch[ri, ci]
    entries = int(on[0]) + int((on[1:] & ~on[:-1]).sum())
    seg = np.hypot(np.diff(sp[:, 0]), np.diff(sp[:, 1]))
    s_along = np.concatenate([[0.0], np.cumsum(seg)])
    length = float(s_along[-1])
    z = z1f[ri, ci]
    j = np.searchsorted(s_along, s_along + baseline)
    ok = j < len(z)
    i_idx = np.nonzero(ok)[0]
    rise = z[j[ok]] - z[i_idx]
    run = s_along[j[ok]] - s_along[i_idx]
    up = int((np.degrees(np.arctan2(rise, run)) > crit_deg).sum()) if len(i_idx) else 0
    return {"unsafe": bool(entries > 0), "patch_entries": entries, "length_m": round(length, 1), "uphill_events": up}
