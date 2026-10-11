"""8-neighbour directed traversability graph and least-cost routing.  SIMULATION ONLY."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

from .dem import Dem
from .terrain import horn_gradient
from .slipmodel import SlipParams, slip, edge_cost

# (d_row, d_col); rows run south, columns run east
DIRS = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]


@dataclass
class EdgeGeometry:
    """Parameter-independent edge quantities for one DEM: computed once, reused for every parameter set."""
    shape: tuple[int, int]
    src: list      # per direction: flat indices of source cells
    dst: list
    dist: list     # horizontal distance, m
    tan_a: list    # signed along-heading slope (rise/run), uphill positive
    tan_c: list    # |cross-slope| (rise/run)


def precompute_edges(dem: Dem) -> EdgeGeometry:
    z = dem.z
    nr, nc = z.shape
    ge, gn = horn_gradient(np.nan_to_num(z, nan=np.nanmean(z)), dem.dx, dem.dy)
    idx = np.arange(nr * nc).reshape(nr, nc)
    src_l, dst_l, dist_l, ta_l, tc_l = [], [], [], [], []
    for dr, dc in DIRS:
        rs = slice(max(0, -dr), nr - max(0, dr))
        cs = slice(max(0, -dc), nc - max(0, dc))
        rd = slice(rs.start + dr, rs.stop + dr)
        cd = slice(cs.start + dc, cs.stop + dc)
        d = float(np.hypot(dc * dem.dx, dr * dem.dy))
        he, hn = dc * dem.dx / d, -dr * dem.dy / d      # unit heading (east, north)
        dz = z[rd, cd] - z[rs, cs]
        gE = 0.5 * (ge[rs, cs] + ge[rd, cd])
        gN = 0.5 * (gn[rs, cs] + gn[rd, cd])
        cross = np.abs(gE * hn - gN * he)
        valid = np.isfinite(dz)
        s_idx, d_idx = idx[rs, cs], idx[rd, cd]
        src_l.append(s_idx[valid].ravel()); dst_l.append(d_idx[valid].ravel())
        dist_l.append(np.full(valid.sum(), d)); ta_l.append((dz / d)[valid].ravel()); tc_l.append(cross[valid].ravel())
    return EdgeGeometry((nr, nc), src_l, dst_l, dist_l, ta_l, tc_l)


def build_graph(eg: EdgeGeometry, p: SlipParams):
    """Return (csr graph of passable edges with travel cost, fraction of edges passable)."""
    rows, cols, vals = [], [], []
    n_all = n_ok = 0
    for s, d, dist, ta, tc in zip(eg.src, eg.dst, eg.dist, eg.tan_a, eg.tan_c):
        sl = slip(ta, tc, p)
        cost = edge_cost(dist, sl, p.i_max)
        ok = np.isfinite(cost)
        n_all += ok.size; n_ok += int(ok.sum())
        rows.append(s[ok]); cols.append(d[ok]); vals.append(cost[ok])
    n = eg.shape[0] * eg.shape[1]
    g = csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))
    return g, n_ok / max(n_all, 1)


def passable_heading_fraction(eg: EdgeGeometry, p: SlipParams) -> np.ndarray:
    """Per-cell fraction of the 8 headings that are passable (cells at the edge/with NaN neighbours count missing as impassable)."""
    n = eg.shape[0] * eg.shape[1]
    cnt = np.zeros(n)
    for s, ta, tc, dist in zip(eg.src, eg.tan_a, eg.tan_c, eg.dist):
        ok = slip(ta, tc, p) <= p.i_max
        cnt[s[ok]] += 1
    return (cnt / len(DIRS)).reshape(eg.shape)


def route_metrics(dem: Dem, graph, src_rc, dst_rc, eg: EdgeGeometry | None = None, p: SlipParams | None = None):
    """Least-cost route between two cells. Returns dict (None-valued if unreachable) and the path."""
    nr, nc = dem.shape
    s, t = src_rc[0] * nc + src_rc[1], dst_rc[0] * nc + dst_rc[1]
    dist, pred = dijkstra(graph, directed=True, indices=s, return_predecessors=True)
    straight = float(np.hypot((dst_rc[1] - src_rc[1]) * dem.dx, (dst_rc[0] - src_rc[0]) * dem.dy))
    if not np.isfinite(dist[t]):
        return {"reachable": False, "straight_m": straight}, None
    path = [t]
    while path[-1] != s:
        path.append(int(pred[path[-1]]))
    path = np.array(path[::-1])
    rc = np.column_stack(np.divmod(path, nc))
    out = {"reachable": True, "straight_m": straight, "cost": float(dist[t]), "cost_ratio": float(dist[t] / straight)}
    if p is not None:
        z = dem.z
        seg_d = np.hypot(np.diff(rc[:, 1]) * dem.dx, np.diff(rc[:, 0]) * dem.dy)
        out["length_m"] = float(seg_d.sum())
        out["length_ratio"] = float(seg_d.sum() / straight)
        ta = np.diff(z[rc[:, 0], rc[:, 1]]) / seg_d
        out["max_uphill_deg"] = float(np.degrees(np.arctan(max(ta.max(), 0.0))))
        out["max_downhill_deg"] = float(np.degrees(np.arctan(max(-ta.min(), 0.0))))
    return out, rc


def reachability(dem: Dem, graph, src_rcs, dst_rcs):
    """Single call over several sources: reachable area fraction, OD cost ratios, unreachable count."""
    nr, nc = dem.shape
    sidx = [r * nc + c for r, c in src_rcs]
    D = dijkstra(graph, directed=True, indices=sidx)
    reach_frac = float(np.mean(np.isfinite(D)))
    ratios, unreach = [], 0
    for k, (src, dst) in enumerate(zip(src_rcs, dst_rcs)):
        t = dst[0] * nc + dst[1]
        straight = float(np.hypot((dst[1] - src[1]) * dem.dx, (dst[0] - src[0]) * dem.dy))
        if np.isfinite(D[k, t]):
            ratios.append(D[k, t] / straight)
        else:
            unreach += 1
    return reach_frac, ratios, unreach


def select_od_pairs(dem: Dem, n_pairs: int, seed: int, min_sep_m: float, max_slope_deg: float = 5.0, low_quantile: float = 0.35):
    """Deterministically pick origin/destination cells on gentle low ground (interdune flats)."""
    from .terrain import slope_deg
    sl = slope_deg(np.nan_to_num(dem.z, nan=np.nanmean(dem.z)), dem.dx, dem.dy)
    z = dem.z
    cand = np.argwhere((sl < max_slope_deg) & (z <= np.nanquantile(z, low_quantile)))
    # keep away from the window border so routes are not squeezed against it
    cand = cand[(cand[:, 0] > 5) & (cand[:, 0] < dem.shape[0] - 5) & (cand[:, 1] > 5) & (cand[:, 1] < dem.shape[1] - 5)]
    rng = np.random.default_rng(seed)
    pairs, tries = [], 0
    while len(pairs) < n_pairs and tries < 20000:
        tries += 1
        a, b = cand[rng.integers(len(cand))], cand[rng.integers(len(cand))]
        if np.hypot((a[1] - b[1]) * dem.dx, (a[0] - b[0]) * dem.dy) >= min_sep_m:
            pairs.append((tuple(int(v) for v in a), tuple(int(v) for v in b)))
    if len(pairs) < n_pairs:
        raise RuntimeError("could not find enough origin/destination pairs; relax constraints")
    return pairs
