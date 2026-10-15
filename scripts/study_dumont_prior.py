#!/usr/bin/env python3
"""Stage 7 stretch study: the Dumont Dunes curve as a prior for the slip scale i0.  Pre registered in docs/PREDICTIONS.md.

SIMULATED BY ME, simulation only, model assumption dependent.  A sensitivity study, not a change to the model or to the
phase 2 results.  It treats a published curve for a different, heavier vehicle on a different dune (Heverly et al. 2013,
FLD-HV13-1) as if it fixed the slip scale of the rover the map is for, which is an unsupported assumption under test.

For each area (30 m only) and each of the phase 2 Latin hypercube draws (same seeds), i0 is replaced by the value in
I0_SEARCH that best fits the Dumont cubic (direct ascent, 4 to 21 deg) given that draw's phi and f_r; i_max is kept.
Variants: baseline (phase 2 draws), Dumont unclipped, Dumont clipped to the assumed i0 range.

Usage: PYTHONPATH=src python3 scripts/study_dumont_prior.py [--data data/raw] [--out results/dumont_prior]
"""
from __future__ import annotations
import argparse, csv, json, os, sys, time
import numpy as np
from scipy.optimize import minimize_scalar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover import SIM_LABEL  # noqa: E402
from dunerover.dem import load_tile, crop, coarsen  # noqa: E402
from dunerover.slipmodel import PARAM_TABLE  # noqa: E402
from dunerover import traverse as TR, subgrid as SG, threeclass as TC  # noqa: E402
from dunerover.study_subgrid import TILES, AREAS, N_DRAWS  # noqa: E402

I0_SEARCH = (0.05, 3.0)
I0_RANGE = (PARAM_TABLE["i0"][1], PARAM_TABLE["i0"][2])
S = np.round(np.arange(4.0, 21.0 + 1e-9, 0.1), 1)
DUMONT = (26.197 - 8.849 * S + 1.281 * S ** 2 - 0.034 * S ** 3) / 100.0     # PUBLISHED fit, FLD-HV13-1
TAN = np.tan(np.radians(S))


def model_curve(phi, f_r, i0):
    x = (TAN + f_r) / np.tan(np.radians(phi))
    return np.minimum(np.where(x < 1, -i0 * np.log1p(-np.clip(x, 0, 0.999999)), np.inf), 1.0)


def dumont_i0(phi, f_r):
    """i0 in I0_SEARCH minimising the squared difference to the Dumont curve (bounded scalar search, then a grid check)."""
    sse = lambda i0: float(np.sum((model_curve(phi, f_r, i0) - DUMONT) ** 2))
    r = minimize_scalar(sse, bounds=I0_SEARCH, method="bounded", options={"xatol": 1e-4})
    grid = np.linspace(*I0_SEARCH, 600)
    g = grid[int(np.argmin([sse(v) for v in grid]))]
    return float(r.x if sse(r.x) <= sse(g) else g), float(min(sse(r.x), sse(g)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", default=os.path.join(ROOT, "data", "raw"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "dumont_prior")); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); t0 = time.time()
    tiles = {k: load_tile(os.path.join(a.data, f)) for k, f in TILES.items()}
    share_rows, i0_rows, log = [], [], [SIM_LABEL, "Stage 7 (docs/PREDICTIONS.md). Comparison input: Dumont Dunes cubic, a different and heavier vehicle."]
    for name, (tk, la0, la1, lo0, lo1, sep, seed, desc) in AREAS.items():
        dem = coarsen(crop(tiles[tk], la0, la1, lo0, lo1), 1)
        dm = 0.5 * (dem.dx + dem.dy)
        eg = TR.precompute_edges(dem)
        F = SG.features_2d(np.nan_to_num(dem.z, nan=np.nanmean(dem.z)), dem.dx, dem.dy)
        p0 = SG.fit(round(dm, 1), "base", 1.0, "box", footprint=1).predict(F)
        base = TC.lhs_draws(N_DRAWS, seed)
        fits = [dumont_i0(p.phi_deg, p.f_r) for p in base]
        unclipped = [p.with_(i0=f[0]) for p, f in zip(base, fits)]
        clipped = [p.with_(i0=float(np.clip(f[0], *I0_RANGE))) for p, f in zip(base, fits)]
        i0s = np.array([f[0] for f in fits]); rmse = np.sqrt(np.array([f[1] for f in fits]) / len(S))
        i0_rows.append({"area": name, "draws": N_DRAWS, "i0_p05": float(np.percentile(i0s, 5)), "i0_median": float(np.median(i0s)),
                        "i0_p95": float(np.percentile(i0s, 95)), "share_i0_above_0.40": float(np.mean(i0s > I0_RANGE[1])),
                        "share_at_search_bound_3.0": float(np.mean(i0s > I0_SEARCH[1] - 1e-3)),
                        "fit_rmse_median": float(np.median(rmse)), "fit_rmse_max": float(rmse.max())})
        for label, draws in (("baseline (phase 2 draws)", base), ("Dumont prior, unclipped", unclipped), ("Dumont prior, clipped to 0.05 to 0.40", clipped)):
            q = TC.q_pass(eg, draws)
            sh = TC.shares(TC.classify(q, p0))
            share_rows.append({"label": "SIMULATED BY ME", "area": name, "posting_m": round(dm, 1), "variant": label, **sh})
            log.append(f"{name} {label}: UNKNOWN {100*sh['UNKNOWN (total)']:.2f} %, BLOCKED {100*sh['BLOCKED']:.2f} %, TRAVERSABLE {100*sh['TRAVERSABLE']:.2f} %")
        log.append(f"{name} fitted i0: median {np.median(i0s):.3f}, 5 to 95 % {np.percentile(i0s,5):.3f} to {np.percentile(i0s,95):.3f}")
    for fn, rows in (("class_shares_30m.csv", share_rows), ("dumont_fitted_i0.csv", i0_rows)):
        with open(os.path.join(a.out, fn), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump({"label": SIM_LABEL, "stage": 7, "i0_search": I0_SEARCH, "i0_assumed_range": I0_RANGE, "n_draws": N_DRAWS,
               "seeds": {k: v[6] for k, v in AREAS.items()}, "shares": share_rows, "fitted_i0": i0_rows},
              open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8"), indent=1)
    log.append(f"run time {time.time()-t0:.0f} s")
    open(os.path.join(a.out, "run_log.txt"), "w", encoding="utf-8").write("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
