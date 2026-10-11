"""Three class map (TRAVERSABLE, BLOCKED, UNKNOWN) with Monte Carlo over the four assumed parameters
and the sub-grid slip face probability.  SIMULATION ONLY, model-assumption dependent.

Rules (fixed before the first run, see docs/PREDICTIONS.md, stage 2):
  * A cell is "passable" for one parameter draw if at least PASS_HEADINGS of its 8 headings are passable.
  * q_pass = share of draws in which the cell is passable.
  * BLOCKED   : q_pass <= Q_LO.
  * TRAVERSABLE: q_pass >= Q_HI and sub-grid face probability < tau.
  * UNKNOWN   : everything else.  Causes: assumption sensitive (q_pass between Q_LO and Q_HI),
                sub-grid face risk (q_pass >= Q_HI but face probability >= tau), or both.
"""
from __future__ import annotations
import numpy as np
from scipy.stats import qmc
from scipy.sparse import diags

from .slipmodel import SlipParams
from . import traverse as TR
from . import subgrid as SG
from .sensitivity import bounds

PASS_HEADINGS = 4
Q_LO, Q_HI = 0.05, 0.95
TAU = 0.20
CODES = {0: "TRAVERSABLE", 1: "BLOCKED", 2: "UNKNOWN (assumption sensitive)", 3: "UNKNOWN (sub-grid face risk)", 4: "UNKNOWN (both)"}


def lhs_draws(n: int, seed: int) -> list[SlipParams]:
    b = bounds()
    keys = ("phi_deg", "f_r", "i0", "i_max")
    u = qmc.LatinHypercube(d=4, seed=seed).random(n)
    return [SlipParams(**{k: b[k][0] + u[j, i] * (b[k][1] - b[k][0]) for i, k in enumerate(keys)}) for j in range(n)]


def q_pass(eg: TR.EdgeGeometry, draws: list[SlipParams]) -> np.ndarray:
    """Share of parameter draws for which each cell has at least PASS_HEADINGS passable headings.

    Uses the closed form of the exponential slip law: slip <= i_max  <=>  demand/mu_max <= 1 - exp(-i_max/i0).
    (Checked against slipmodel.slip in tests.)  Exponential form and circle cross-slope rule only.
    """
    n = eg.shape[0] * eg.shape[1]
    acc = np.zeros(n)
    tans = [(np.asarray(ta), np.asarray(tc)) for ta, tc in zip(eg.tan_a, eg.tan_c)]
    for p in draws:
        xc = 1.0 - np.exp(-p.i_max / p.i0)
        thr = xc * p.mu_max
        cnt = np.zeros(n, dtype=np.int8)
        for s, (ta, tc) in zip(eg.src, tans):
            ok = np.hypot(np.abs(ta + p.f_r), tc) <= thr
            cnt[s[ok]] += 1
        acc += cnt >= PASS_HEADINGS
    return (acc / len(draws)).reshape(eg.shape)


def classify(q: np.ndarray, pface: np.ndarray, tau: float = TAU, q_lo: float = Q_LO, q_hi: float = Q_HI) -> np.ndarray:
    blocked = q <= q_lo
    robust = q >= q_hi
    amb = ~blocked & ~robust
    risky = pface >= tau
    cls = np.full(q.shape, 0, dtype=np.int8)
    cls[blocked] = 1
    cls[amb & ~risky] = 2
    cls[robust & risky] = 3
    cls[amb & risky] = 4
    return cls


def shares(cls: np.ndarray) -> dict:
    n = cls.size
    return {CODES[k]: float((cls == k).sum() / n) for k in CODES} | {"UNKNOWN (total)": float(np.isin(cls, (2, 3, 4)).sum() / n)}


def reachability_unknown_impassable(eg: TR.EdgeGeometry, cls: np.ndarray, nominal: SlipParams, od_cells, nc: int):
    """Nominal-parameter graph restricted to TRAVERSABLE cells.  Returns (share of pairs reachable, share of endpoints not TRAVERSABLE)."""
    from scipy.sparse.csgraph import dijkstra
    g, _ = TR.build_graph(eg, nominal)
    ok = (cls.ravel() == 0).astype(float)
    D = diags(ok)
    g2 = (D @ g @ D).tocsr(); g2.eliminate_zeros()
    src, dst = od_cells
    if not src:
        return float("nan"), float("nan")
    dist = dijkstra(g2, directed=True, indices=[r * nc + c for r, c in src])
    reach = [bool(np.isfinite(dist[k, d[0] * nc + d[1]])) for k, d in enumerate(dst)]
    bad_end = [cls[r, c] != 0 for r, c in src] + [cls[r, c] != 0 for r, c in dst]
    return float(np.mean(reach)), float(np.mean(bad_end))


def coverage_certainty_map(q: np.ndarray, pface: np.ndarray, taus) -> list[dict]:
    """On the real map: coverage = share of cells not UNKNOWN; expected_certainty = 1 - mean face probability over
    TRAVERSABLE cells (model expectation, not a measured accuracy)."""
    out = []
    for t in taus:
        c = classify(q, pface, t)
        trav = c == 0
        out.append({"tau": float(t), "coverage": float(np.isin(c, (0, 1)).mean()), "traversable": float(trav.mean()),
                    "blocked": float((c == 1).mean()),
                    "expected_certainty_traversable": float(1.0 - pface[trav].mean()) if trav.any() else float("nan")})
    return out
