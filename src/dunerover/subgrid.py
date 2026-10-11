"""Sub-grid slip face detector.  SIMULATION ONLY, model-assumption dependent.

Problem: a 30 m elevation model cannot resolve a slip face (run of about 1.4 to 1.7 times its height,
so a few metres to tens of metres).  This module estimates, for each DEM cell, the PROBABILITY that an
unresolved active slip face lies inside the cell, from four features the DEM does see: slope, crest
convexity, slope break and local relief.

Method
------
1. Forward-simulate ideal straight-crested asymmetric dunes (stoss, brink, active face, apron, flat
   interdune), sample them the way a DEM does (box mean or point sample at the posting d), and record
   the DEM features and the TRUE answer (is a face of 28 deg or more inside the cell footprint).
2. Fit a logistic regression P(face | features) on that synthetic ensemble, separately for each posting.
3. Apply it to the real DEM features.

Every range below that is not marked "published" is an ASSUMPTION and is listed in SUBGRID_PARAMS.
The detector is only as good as the synthetic dunes are realistic; it has been validated against
synthetic truth only, never against a real lidar or drone profile (none was retrieved).
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.optimize import minimize
from scipy.ndimage import maximum_filter, minimum_filter

FACE_TRUTH_DEG = 28.0   # a face at least this steep inside the cell counts as "face present"

# name: (low, high, status, basis).  Morphology ids refer to research/phase2/phase2_morphology.csv
SUBGRID_PARAMS = {
    "stoss_slope_deg": (6.0, 20.0, "published (barchan and transverse dunes, small and medium)",
                        "PM01 (barchan 8 to 20), PM02/PM06 (transverse about 6). No distribution for dunes of tens of metres was found, so extrapolated."),
    "face_slope_deg": (29.5, 32.5, "published (lidar, two US fields)",
                       "PM18: sharp peak at 32.5 deg (White Sands) and 29.5 deg (Great Sand Dunes). Not shown to hold in Arabia."),
    "face_height_fraction": (0.2, 1.0, "partly published, mostly ASSUMPTION",
                             "PM08: 0.54 to 1.0 for six transverse dunes of 7 to 10 m. The 0.2 lower end is an assumption for tall compound dunes (no source found)."),
    "dune_height_m": (5.0, 120.0, "published range, log-uniform is an ASSUMPTION",
                      "PM29 to PM35: Rub' al Khali dunes from under 5 m to over 155 m; 50 to 130 m for the linear and star types."),
    "interdune_flat_ratio": (0.0, 2.0, "ASSUMPTION", "Flat interdune width as a multiple of the dune footprint; no source used."),
    "apron_slope": ("equal to stoss slope", None, "ASSUMPTION", "Slope of the slip face base below the face; no source."),
    "no_face_lee_slope_deg": (10.0, 25.0, "ASSUMPTION", "Lee slope when the face is inactive; the morphology search found no source for it (PM20)."),
    "p_active_face (pi)": (0.3, 1.0, "ASSUMPTION", "Share of dune crests with an active face; no source found. Baseline 1.0 (worst case)."),
}
SCENARIOS = {  # name: overrides of the baseline box, for the sensitivity of the result to the sub-grid assumptions
    "base": {},
    "gentle": {"stoss": (6.0, 12.0), "fh": (0.2, 0.7)},
    "steep": {"stoss": (14.0, 20.0), "fh": (0.7, 1.0)},
}
FEATURES = ["tan_slope", "convexity", "slope_break", "relief_over_d"]
NPOST = 11   # profile length in posts; centre cell is index 5; 7-post relief window is 2..8


def _ranges(scn: str):
    base = {"stoss": SUBGRID_PARAMS["stoss_slope_deg"][:2], "fh": SUBGRID_PARAMS["face_height_fraction"][:2]}
    base.update(SCENARIOS[scn])
    return base


def _profile_z(x, lam, Ls, Rf, Hf, H, Ra, G, has_face, tl_lee):
    """Elevation of a periodic dune profile at positions x (array shape (n, m)); parameters shape (n, 1).

    One period, downwind: stoss rise (Ls) to height H at the brink, active face down by Hf over Rf, apron
    down to zero over Ra, flat interdune of width G.  If has_face is False the lee is one uniform slope
    tl_lee over the whole lee height with the same total run Rf+Ra.
    """
    u = np.mod(x, lam)
    z = np.zeros_like(u)
    # segment boundaries
    b1 = Ls
    b2 = Ls + Rf
    b3 = Ls + Rf + Ra
    stoss = u < b1
    face = (u >= b1) & (u < b2)
    apron = (u >= b2) & (u < b3)
    z = np.where(stoss, H * u / np.maximum(Ls, 1e-9), z)
    z_face = H - Hf * (u - b1) / np.maximum(Rf, 1e-9)
    z_apron = (H - Hf) * (1.0 - (u - b2) / np.maximum(Ra, 1e-9))
    z = np.where(face, z_face, z)
    z = np.where(apron, z_apron, z)
    # no-face lee: straight line from brink to base across face+apron
    lee = (u >= b1) & (u < b3)
    z_lee = H * (1.0 - (u - b1) / np.maximum(Rf + Ra, 1e-9))
    z = np.where(lee & ~has_face, z_lee, z)
    return z


def synth(n: int, d: float, seed: int, scn: str = "base", pi: float = 1.0, sampling: str = "box", footprint: int = 1):
    """Draw n synthetic cells.  Returns (features (n,4), truth (n,) bool, meta dict).

    footprint = number of posts across the window in which a face counts as "inside the cell" (1 = the cell itself,
    the pre-registered definition; 3 = the cell and one post on each side, a post hoc sensitivity variant).
    """
    rng = np.random.default_rng(seed)
    r = _ranges(scn)
    H = np.exp(rng.uniform(np.log(SUBGRID_PARAMS["dune_height_m"][0]), np.log(SUBGRID_PARAMS["dune_height_m"][1]), n))
    a = np.radians(rng.uniform(*r["stoss"], n))
    th = np.radians(rng.uniform(*SUBGRID_PARAMS["face_slope_deg"][:2], n))
    fh = rng.uniform(*r["fh"], n)
    has_face = rng.random(n) < pi
    lee_a = np.radians(rng.uniform(*SUBGRID_PARAMS["no_face_lee_slope_deg"][:2], n))
    Ls = H / np.tan(a)
    Hf = fh * H
    Rf = Hf / np.tan(th)
    Ra = (H - Hf) / np.tan(a)
    # no-face case: lee run set by the lee slope over the full height (replaces face + apron run)
    run_lee_nf = H / np.tan(lee_a)
    Rf = np.where(has_face, Rf, 0.5 * run_lee_nf)
    Ra = np.where(has_face, Ra, 0.5 * run_lee_nf)
    G = rng.uniform(*SUBGRID_PARAMS["interdune_flat_ratio"][:2], n) * (Ls + Rf + Ra)
    lam = Ls + Rf + Ra + G
    phase = rng.uniform(0, 1, n) * lam
    # fine sampling inside each post: nf sub-samples per post for box mean
    nf = 12 if sampling == "box" else 1
    off = (np.arange(nf) + 0.5) / nf - 0.5 if nf > 1 else np.zeros(1)
    xp = (np.arange(NPOST) - NPOST // 2) * d
    X = phase[:, None, None] + xp[None, :, None] + off[None, None, :] * d      # (n, post, sub)
    X = X.reshape(n, -1)
    P = lambda v: v[:, None]
    z = _profile_z(X, P(lam), P(Ls), P(Rf), P(Hf), P(H), P(Ra), P(G), P(has_face), P(lee_a))
    z = z.reshape(n, NPOST, nf).mean(axis=2)
    # truth: a face interval [Ls, Ls+Rf] (mod lam) overlaps the centre-cell footprint [phase - d/2, phase + d/2]
    wd = footprint * d
    a0 = np.mod(phase - 0.5 * wd, lam)
    hit = np.zeros(n, dtype=bool)
    for k in (-1, 0, 1):
        f0, f1 = Ls + k * lam, Ls + Rf + k * lam
        hit |= (a0 < f1) & (a0 + wd > f0)
    hit |= wd >= lam
    truth = has_face & hit & (np.degrees(th) >= FACE_TRUTH_DEG)
    return features_1d(z, d), truth, {"H": H, "lam": lam}


def features_1d(z: np.ndarray, d: float) -> np.ndarray:
    """Features of a (n, NPOST) block of DEM posts, centre index NPOST//2."""
    c = NPOST // 2
    s = lambda j: (z[:, j + 1] - z[:, j - 1]) / (2 * d)          # central-difference slope at post j (tan)
    s5 = s(c)
    tan_slope = np.abs(s5)
    convex = -(z[:, c + 1] - 2 * z[:, c] + z[:, c - 1]) / d
    brk = np.maximum(np.abs(s(c - 1) - s5), np.abs(s(c + 1) - s5))
    relief = z[:, c - 3:c + 4].max(axis=1) - z[:, c - 3:c + 4].min(axis=1)
    return np.column_stack([tan_slope, np.abs(convex), brk, relief / d])


def features_2d(z: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """Same four features on a real DEM, shape (rows, cols, 4).  Slope direction taken as the steepest descent."""
    zp = np.pad(z, 2, mode="edge")
    nr, nc = z.shape
    # Horn-like 3x3 weighted gradient on the unpadded cells
    a, b, c_ = zp[1:-3, 1:-3], zp[1:-3, 2:-2], zp[1:-3, 3:-1]
    d_, f = zp[2:-2, 1:-3], zp[2:-2, 3:-1]
    g, h, i = zp[3:-1, 1:-3], zp[3:-1, 2:-2], zp[3:-1, 3:-1]
    gx = ((c_ + 2 * f + i) - (a + 2 * d_ + g)) / (8 * dx)
    gy = ((g + 2 * h + i) - (a + 2 * b + c_)) / (8 * dy)
    tan_s = np.hypot(gx, gy)
    # second derivatives by central differences
    zc = zp[2:-2, 2:-2]
    zxx = (zp[2:-2, 3:-1] - 2 * zc + zp[2:-2, 1:-3]) / dx ** 2
    zyy = (zp[3:-1, 2:-2] - 2 * zc + zp[1:-3, 2:-2]) / dy ** 2
    zxy = (zp[3:-1, 3:-1] - zp[3:-1, 1:-3] - zp[1:-3, 3:-1] + zp[1:-3, 1:-3]) / (4 * dx * dy)
    g2 = np.maximum(gx ** 2 + gy ** 2, 1e-12)
    # curvature along the gradient direction (profile curvature, 1/m); convexity in tan units per post
    kprof = (gx ** 2 * zxx + 2 * gx * gy * zxy + gy ** 2 * zyy) / g2
    dm = 0.5 * (dx + dy)
    convex = np.abs(kprof) * dm
    # slope break: largest difference of the SIGNED slope component along one reference direction u between the
    # cell and its 8 neighbours (u = gradient direction of the steepest cell in the 3 x 3 block).  A crest, where
    # the slope changes sign, scores high; a uniform slope scores zero.
    gxp, gyp = np.pad(gx, 1, mode="edge"), np.pad(gy, 1, mode="edge")
    gmag = np.hypot(gxp, gyp)
    best = np.zeros((nr, nc)); ux = np.ones((nr, nc)); uy = np.zeros((nr, nc))
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            sl = (slice(1 + dr, 1 + dr + nr), slice(1 + dc, 1 + dc + nc))
            m = gmag[sl] > best
            best = np.where(m, gmag[sl], best)
            nrm = np.maximum(gmag[sl], 1e-12)
            ux = np.where(m, gxp[sl] / nrm, ux); uy = np.where(m, gyp[sl] / nrm, uy)
    sc = gx * ux + gy * uy
    brk = np.zeros_like(sc)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr or dc:
                sl = (slice(1 + dr, 1 + dr + nr), slice(1 + dc, 1 + dc + nc))
                brk = np.maximum(brk, np.abs(gxp[sl] * ux + gyp[sl] * uy - sc))
    relief = maximum_filter(z, size=7, mode="nearest") - minimum_filter(z, size=7, mode="nearest")
    return np.stack([tan_s, convex, brk, relief / dm], axis=-1)


def _expand(F: np.ndarray) -> np.ndarray:
    """Transform: log1p of each feature plus all pairwise products (degree-2), standardised later."""
    L = np.log1p(F * np.array([10.0, 10.0, 10.0, 1.0]))   # scales chosen only to spread the range, not tuned on data
    cols = [L[:, i] for i in range(L.shape[1])]
    for i in range(L.shape[1]):
        for j in range(i, L.shape[1]):
            cols.append(L[:, i] * L[:, j])
    return np.column_stack(cols)


@dataclass
class FaceModel:
    mu: np.ndarray
    sd: np.ndarray
    w: np.ndarray
    b: float
    d: float
    scn: str
    pi: float
    sampling: str
    footprint: int = 1

    def predict(self, F: np.ndarray) -> np.ndarray:
        shp = F.shape[:-1]
        X = (_expand(F.reshape(-1, F.shape[-1])) - self.mu) / self.sd
        z = X @ self.w + self.b
        return (1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))).reshape(shp)


def fit(d: float, scn: str = "base", pi: float = 1.0, sampling: str = "box", n: int = 60000, seed: int = 20261014, l2: float = 1e-3, footprint: int = 1) -> FaceModel:
    F, y, _ = synth(n, d, seed, scn, pi, sampling, footprint)
    X = _expand(F); mu, sd = X.mean(0), X.std(0) + 1e-9; X = (X - mu) / sd
    y = y.astype(float)

    def loss(theta):
        w, b = theta[:-1], theta[-1]
        z = X @ w + b
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))
        ll = -np.mean(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)) + l2 * np.sum(w * w)
        gz = (p - y) / len(y)
        return ll, np.append(X.T @ gz + 2 * l2 * w, gz.sum())

    res = minimize(loss, np.zeros(X.shape[1] + 1), jac=True, method="L-BFGS-B", options={"maxiter": 500})
    return FaceModel(mu, sd, res.x[:-1], float(res.x[-1]), d, scn, pi, sampling, footprint)


def auc(score: np.ndarray, y: np.ndarray) -> float:
    from scipy.stats import rankdata
    y = y.astype(bool)
    n1, n0 = y.sum(), (~y).sum()
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = rankdata(score)
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def evaluate_detector(m: FaceModel, n: int = 30000, seed: int = 777, scn: str | None = None, pi: float | None = None) -> dict:
    """Held-out synthetic skill.  scn/pi default to the training ones; pass others to test robustness to the prior."""
    F, y, _ = synth(n, m.d, seed, scn or m.scn, m.pi if pi is None else pi, m.sampling, m.footprint)
    p = m.predict(F)
    bins = np.linspace(0, 1, 11)
    rel = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        k = (p >= lo) & (p < hi if hi < 1 else p <= hi)
        if k.sum() > 20:
            rel.append((float(p[k].mean()), float(y[k].mean()), int(k.sum())))
    return {"n": n, "face_rate": float(y.mean()), "auc": auc(p, y), "brier": float(np.mean((p - y) ** 2)),
            "brier_climatology": float(np.mean((y.mean() - y) ** 2)), "reliability": rel}


def coverage_certainty(m: FaceModel, taus, n: int = 30000, seed: int = 778) -> list[dict]:
    """On synthetic truth: cells declared face-free when p < tau.  coverage = share declared; certainty = share of those truly face-free."""
    F, y, _ = synth(n, m.d, seed, m.scn, m.pi, m.sampling, m.footprint)
    p = m.predict(F)
    out = []
    for t in taus:
        k = p < t
        out.append({"tau": float(t), "coverage": float(k.mean()), "certainty": float(1.0 - y[k].mean()) if k.any() else float("nan"),
                    "missed_face_rate_among_declared": float(y[k].mean()) if k.any() else float("nan")})
    return out
