"""One-at-a-time and global (Latin hypercube) sensitivity of traversability outputs.  SIMULATION ONLY."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.stats import qmc, spearmanr, rankdata

from .dem import Dem, coarsen, add_correlated_noise
from .slipmodel import SlipParams, PARAM_TABLE, critical_uphill_deg, nominal_params
from . import traverse as TR

NOISE_RANGE = (0.0, 2.0)   # m, ASSUMPTION; upper end taken from the published GLO-30 relative-accuracy order (about 2 m)
NOISE_CORR_POSTS = 3.0     # ASSUMPTION
CONTINUOUS = ["phi_deg", "f_r", "i0", "i_max", "noise_sigma_m"]
METRICS = ["blocked_edge_frac", "reach_frac", "median_cost_ratio", "unreachable_od_frac", "crit_uphill_deg"]


def bounds():
    b = {k: (PARAM_TABLE[k][1], PARAM_TABLE[k][2]) for k in ("phi_deg", "f_r", "i0", "i_max")}
    b["noise_sigma_m"] = NOISE_RANGE
    return b


@dataclass
class Scenario:
    """A DEM variant plus origin/destination cells (lat/lon fixed once, mapped to each variant)."""
    base: Dem
    od_latlon: list   # [((lat,lon),(lat,lon)), ...]

    def variant(self, block: int = 1, noise_sigma: float = 0.0, seed: int = 0) -> Dem:
        d = coarsen(self.base, block)
        return add_correlated_noise(d, noise_sigma, NOISE_CORR_POSTS / block, seed)

    def od_cells(self, dem: Dem):
        src, dst = [], []
        for (a, b) in self.od_latlon:
            src.append(dem.rowcol(*a)); dst.append(dem.rowcol(*b))
        return src, dst


def od_to_latlon(dem: Dem, pairs):
    return [(dem.latlon(*a), dem.latlon(*b)) for a, b in pairs]


def evaluate(sc: Scenario, p: SlipParams, block: int = 1, noise_sigma: float = 0.0, seed: int = 0, eg_cache: dict | None = None) -> dict:
    key = (block, round(noise_sigma, 6), seed)
    if eg_cache is not None and key in eg_cache:
        dem, eg = eg_cache[key]
    else:
        dem = sc.variant(block, noise_sigma, seed)
        eg = TR.precompute_edges(dem)
        if eg_cache is not None:
            eg_cache.clear(); eg_cache[key] = (dem, eg)
    g, frac_ok = TR.build_graph(eg, p)
    src, dst = sc.od_cells(dem)
    reach, ratios, unreach = TR.reachability(dem, g, src, dst)
    return {
        "blocked_edge_frac": 1.0 - frac_ok,
        "reach_frac": reach,
        "median_cost_ratio": float(np.median(ratios)) if ratios else float("nan"),
        "unreachable_od_frac": unreach / len(src),
        "crit_uphill_deg": critical_uphill_deg(p),
    }


def oat(sc: Scenario, nominal: SlipParams | None = None) -> list[dict]:
    """One-at-a-time: each assumption to its low and high bound, plus structural and DEM variants."""
    nominal = nominal or nominal_params()
    rows = []
    cache: dict = {}
    base = evaluate(sc, nominal, eg_cache=cache); base.update(case="nominal", factor="-", setting="-"); rows.append(base)
    for k in ("phi_deg", "f_r", "i0", "i_max"):
        lo, hi = PARAM_TABLE[k][1], PARAM_TABLE[k][2]
        for tag, v in (("low", lo), ("high", hi)):
            r = evaluate(sc, nominal.with_(**{k: v}), eg_cache=cache); r.update(case=f"{k}={v}", factor=k, setting=tag); rows.append(r)
    for form in ("janosi_mean",):
        r = evaluate(sc, nominal.with_(form=form), eg_cache=cache); r.update(case=f"form={form}", factor="slip_law_form", setting=form); rows.append(r)
    r = evaluate(sc, nominal.with_(cross="additive"), eg_cache=cache); r.update(case="cross=additive", factor="cross_slope_rule", setting="additive"); rows.append(r)
    for blk in (2, 3):
        r = evaluate(sc, nominal, block=blk); r.update(case=f"dem_block={blk}", factor="dem_posting", setting=f"{blk}x coarser (block mean)"); rows.append(r)
    for sig in (1.0, 2.0):
        r = evaluate(sc, nominal, noise_sigma=sig, seed=11); r.update(case=f"dem_noise={sig} m", factor="dem_noise", setting=f"sigma {sig} m"); rows.append(r)
    return rows


def global_lhs(sc: Scenario, n: int, seed: int) -> tuple[np.ndarray, list[dict]]:
    """Latin hypercube over the five continuous assumptions. Returns unit-cube design and metric rows."""
    b = bounds()
    sampler = qmc.LatinHypercube(d=len(CONTINUOUS), seed=seed)
    u = sampler.random(n)
    rows = []
    for j in range(n):
        vals = {k: b[k][0] + u[j, i] * (b[k][1] - b[k][0]) for i, k in enumerate(CONTINUOUS)}
        p = SlipParams(phi_deg=vals["phi_deg"], f_r=vals["f_r"], i0=vals["i0"], i_max=vals["i_max"])
        m = evaluate(sc, p, noise_sigma=vals["noise_sigma_m"], seed=1000 + j)
        m.update(vals)
        rows.append(m)
    return u, rows


def rank_sensitivity(rows: list[dict]) -> dict:
    """Spearman rho of each metric against each input, and standardised rank-regression coefficients."""
    out = {}
    X = np.column_stack([rankdata([r[k] for r in rows]) for k in CONTINUOUS])
    X = (X - X.mean(0)) / X.std(0)
    for m in METRICS:
        y = np.array([r[m] for r in rows], dtype=float)
        if not np.all(np.isfinite(y)) or np.ptp(y) == 0:
            out[m] = {"note": "constant or undefined across samples"}
            continue
        ry = rankdata(y); ry = (ry - ry.mean()) / ry.std()
        rho = {k: float(spearmanr([r[k] for r in rows], y)[0]) for k in CONTINUOUS}
        beta, *_ = np.linalg.lstsq(X, ry, rcond=None)
        r2 = 1.0 - float(np.sum((ry - X @ beta) ** 2) / np.sum(ry ** 2))
        out[m] = {"spearman": rho, "rank_regression_coef": dict(zip(CONTINUOUS, map(float, beta))), "r2_rank_regression": r2}
    return out
