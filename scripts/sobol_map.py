#!/usr/bin/env python3
"""Stage 16 (docs/PREDICTIONS.md): global (Sobol) sensitivity of the 30 m map to the four assumed slip parameters.

    PYTHONPATH=src python3 scripts/sobol_map.py

Output for one parameter draw: Y = share of cells of area A (Liwa, 30 m) with at least 4 of 8 passable headings, the
quantity whose variation across draws makes a cell UNKNOWN.  First order and total Sobol indices by the Saltelli
sampling scheme with the Jansen estimators, base sample N = 256 (Sobol sequence, scrambled, seed 20261023), 200
bootstrap resamples for 95 % intervals.  Range sets: original, widened_i0, posterior_2026_10_20 (if defined).
SIMULATED BY ME, simulation only, model assumption dependent.  Outputs: results/sobol_map/.
"""
from __future__ import annotations
import csv, json, os, sys, time
import numpy as np
from scipy.stats import qmc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover.dem import load_tile, crop  # noqa: E402
from dunerover.slipmodel import SlipParams, RANGE_SETS, use_range_set  # noqa: E402
from dunerover.sensitivity import bounds  # noqa: E402
from dunerover.study_subgrid import AREAS, TILES  # noqa: E402
from dunerover import traverse as TR, threeclass as TC  # noqa: E402

OUT = os.path.join(ROOT, "results", "sobol_map")
KEYS = ("phi_deg", "f_r", "i0", "i_max")
N, SEED, NBOOT = 256, 20261023, 200


def passable_share(eg, p):
    xc = 1.0 - np.exp(-p.i_max / p.i0)
    thr = xc * p.mu_max
    cnt = np.zeros(eg.shape[0] * eg.shape[1], dtype=np.int8)
    for s, ta, tc in zip(eg.src, eg.tan_a, eg.tan_c):
        ok = np.hypot(np.abs(ta + p.f_r), tc) <= thr
        cnt[s[ok]] += 1
    return float((cnt >= TC.PASS_HEADINGS).mean())


def main():
    os.makedirs(OUT, exist_ok=True)
    tk, la0, la1, lo0, lo1 = AREAS["A_south_Liwa"][:5]
    dem = crop(load_tile(os.path.join(ROOT, "data", "raw", TILES[tk])), la0, la1, lo0, lo1)
    eg = TR.precompute_edges(dem)
    rows, log = [], open(os.path.join(OUT, "run_log.txt"), "a")
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--sets", default="original,widened_i0,posterior_2026_10_20"); a = ap.parse_args()
    sets = [s for s in a.sets.split(",") if s in RANGE_SETS]
    prev = os.path.join(OUT, "sobol_indices.csv")
    if os.path.exists(prev):   # keep the rows of range sets not re run
        rows = [r for r in csv.DictReader(open(prev)) if r["range_set"] not in sets]
    for rs in sets:
        with use_range_set(rs):
            b = bounds()
            lo = np.array([b[k][0] for k in KEYS]); hi = np.array([b[k][1] for k in KEYS])
            base = qmc.Sobol(d=8, scramble=True, seed=SEED).random(N)
            A = lo + base[:, :4] * (hi - lo); B = lo + base[:, 4:] * (hi - lo)
            f = lambda X: np.array([passable_share(eg, SlipParams(**dict(zip(KEYS, x)))) for x in X])
            t0 = time.time()
            fA, fB = f(A), f(B)
            fAB = []
            for i in range(4):
                ABi = A.copy(); ABi[:, i] = B[:, i]; fAB.append(f(ABi))
            rng = np.random.default_rng(SEED)
            def indices(ix):
                a, bb = fA[ix], fB[ix]
                var = np.var(np.concatenate([a, bb]))
                S1 = [(var - 0.5 * np.mean((bb - fAB[i][ix]) ** 2)) / var for i in range(4)]
                ST = [0.5 * np.mean((a - fAB[i][ix]) ** 2) / var for i in range(4)]
                return np.array(S1), np.array(ST), var
            S1, ST, var = indices(np.arange(N))
            boots = [indices(rng.integers(0, N, N)) for _ in range(NBOOT)]
            for i, k in enumerate(KEYS):
                b1 = np.percentile([bt[0][i] for bt in boots], [2.5, 97.5]); bt_ = np.percentile([bt[1][i] for bt in boots], [2.5, 97.5])
                rows.append({"range_set": rs, "parameter": k, "low": float(lo[i]), "high": float(hi[i]), "S1": round(float(S1[i]), 4),
                             "S1_ci95_low": round(float(b1[0]), 4), "S1_ci95_high": round(float(b1[1]), 4), "ST": round(float(ST[i]), 4),
                             "ST_ci95_low": round(float(bt_[0]), 4), "ST_ci95_high": round(float(bt_[1]), 4),
                             "Y_mean": round(float(np.mean(np.concatenate([fA, fB]))), 4), "Y_sd": round(float(np.sqrt(var)), 4)})
            msg = f"{rs}: Y mean {np.mean(fA):.3f} sd {np.sqrt(var):.3f}; " + ", ".join(f"{k} S1 {S1[i]:.2f} ST {ST[i]:.2f}" for i, k in enumerate(KEYS)) + f" [{time.time()-t0:.0f} s]"
            print(msg, flush=True); log.write(msg + "\n")
    with open(os.path.join(OUT, "sobol_indices.csv"), "w", newline="") as fh:   # rows of earlier range sets first, then the new ones
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    json.dump({"N": N, "seed": SEED, "bootstrap": NBOOT, "output": "share of area A cells (30 m) with at least 4 of 8 passable headings",
               "range_sets": sets}, open(os.path.join(OUT, "summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
