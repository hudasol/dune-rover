#!/usr/bin/env python3
"""Stage 15 (docs/PREDICTIONS.md): calibrate and validate the slip model families on the published curves.

    PYTHONPATH=src python3 scripts/model_validation.py [--quick]

Input: research/phase3/curves.csv (PUBLISHED points, digitised or tabulated, with uncertainty and conditions).
Every prediction, fit and score written here is SIMULATED BY ME.  Deterministic: fixed seeds listed below.

Steps for every family in dunerover.models.FAMILIES and every slip against slope curve the family applies to:
  1. nominal: published or nominal parameters, no fitting;
  2. per curve fit: best fit to that curve alone (how well the family's SHAPE can match, not a prediction);
  3. leave one study out (LOSO): parameters calibrated on all other studies, then the held out study is predicted;
  4. two way transfer: calibrated on the Dumont curve, predict the Ishigami curves, and the reverse (where present).
Calibration: Gaussian likelihood with per point sigma^2 = y_unc^2 + s^2, s a fitted model error (0.01 to 0.40);
uniform priors on the family bounds (log uniform where marked).  Cheap families: affine invariant MCMC (emcee, MIT
licence).  Bekker Wong: maximum a posteriori (2 starts, 150 iterations) plus an 8 sample bootstrap over curves for intervals (MCMC too slow).
Outputs: results/model_validation/*.csv, summary.json, posterior_exp.json, run_log.txt, figures/.
"""
from __future__ import annotations
import argparse, csv, json, os, re, sys, time
from collections import defaultdict
import numpy as np
from scipy.optimize import minimize
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover.models import FAMILIES, EXTRA_FAMILIES  # noqa: E402

OUT = os.path.join(ROOT, "results", "model_validation")
CURVES = os.path.join(ROOT, "research", "phase3", "curves.csv")
SEED = 20261022
S_BOUNDS = (0.01, 0.40)
BAR_RMSE, BAR_COVER = 0.15, 0.80      # validation bar fixed in stage 15
PINK = ["#a8325e", "#c9769a", "#5b3a78", "#e8a5bb", "#6fa28f", "#8a3a63", "#d98fae", "#7d5fa6"]


def num(v):
    m = re.match(r"^\s*(-?\d+(?:\.\d+)?(?:[eE]-?\d+)?)", str(v))
    return float(m.group(1)) if m else float("nan")


def load_curves(path=CURVES):
    by = defaultdict(list)
    for r in csv.DictReader(open(path, encoding="utf-8")):
        by[r["curve_id"]].append(r)
    curves = []
    for cid, rows in by.items():
        r0 = rows[0]
        xn, yn = r0["x_name"].strip().lower(), r0["y_name"].strip().lower()
        if "slope" not in xn or not ("slip" in yn or "slippage" in yn) or "lateral" in yn:
            continue   # only longitudinal slip against slope (lateral slippage is a different quantity)
        scale = 0.01 if r0["y_unit"].strip().lower() in ("percent", "%") else 1.0
        x = np.array([num(r["x"]) for r in rows]); y = np.array([num(r["y"]) for r in rows]) * scale
        yu = np.array([num(r["y_unc"]) for r in rows]) * scale
        yu = np.where(np.isfinite(yu), yu, 0.03)
        ok = np.isfinite(x) & np.isfinite(y)
        kind = r0["slope_kind"].strip().lower()
        kind = "direct ascent" if kind.startswith("direct") else "side slope" if kind.startswith("side") else "emulated by pull" if "pull" in kind else kind
        d, w, load = num(r0["wheel_diameter_m"]), num(r0["wheel_width_m"]), num(r0["load_per_wheel_N"])
        rho = num(r0["bulk_density_kg_m3"].split(" ")[0]) if r0["bulk_density_kg_m3"].strip() else float("nan")
        ctx = {"radius_m": d / 2 if np.isfinite(d) else None, "width_m": w if np.isfinite(w) else None,
               "load_N": load if np.isfinite(load) else None, "soil_set": "fjs1_ishigami2007",
               "density_kg_m3": rho if np.isfinite(rho) and 800 < rho < 2500 else None}   # used only by the stage 22 families
        curves.append({"id": cid, "source": r0["source_key"], "x": x[ok], "y": np.clip(y[ok], 0.0, 1.0), "yu": yu[ok], "kind": kind,
                       "ctx": ctx, "test_type": r0["test_type"], "comparable": r0["comparable_to_dune_sand"], "gravity": r0["gravity_g"],
                       "method": r0["method"], "vehicle": r0["vehicle"]})
    return curves


def usable(fam, c):
    if not fam.applies(c["kind"]):
        return False
    if fam.name == "bekker_wong":
        return all(c["ctx"][k] for k in ("radius_m", "width_m", "load_N"))
    if getattr(fam, "needs", None):   # stage 22 families
        return all(c["ctx"].get(k) for k in fam.needs)
    return True


# ---- parameter transforms ------------------------------------------------------------------------------------------
def to_u(fam, th):
    return np.array([np.log(th[p.name]) if p.log else th[p.name] for p in fam.params])


def from_u(fam, u):
    return {p.name: float(np.exp(v)) if p.log else float(v) for p, v in zip(fam.params, u)}


def u_bounds(fam):
    return [(np.log(p.low), np.log(p.high)) if p.log else (p.low, p.high) for p in fam.params]


def neg_log_post(vec, fam, curves):
    u, s = vec[:-1], vec[-1]
    for (lo, hi), v in zip(u_bounds(fam) + [S_BOUNDS], list(u) + [s]):
        if not lo <= v <= hi:
            return np.inf
    th = from_u(fam, u)
    nll = 0.0
    for c in curves:
        pred = fam.predict(c["x"], c["kind"], c["ctx"], th)
        var = c["yu"] ** 2 + s ** 2
        nll += 0.5 * np.sum((c["y"] - pred) ** 2 / var + np.log(2 * np.pi * var)) / len(c["x"])   # each curve weighs the same
    return nll


def fit_map(fam, curves, seed, starts=6):
    if fam.name == "bekker_wong":
        starts = min(starts, 2)   # the Bekker Wong solver is slow; fewer starts, fewer iterations (disclosed in the stage 15 entry)
    rng = np.random.default_rng(seed)
    b = u_bounds(fam) + [S_BOUNDS]
    x0s = [np.append(to_u(fam, fam.nominal(curves[0]["ctx"])), 0.1)] + [np.array([rng.uniform(lo, hi) for lo, hi in b]) for _ in range(starts - 1)]
    best = None
    for x0 in x0s:
        r = minimize(neg_log_post, x0, args=(fam, curves), method="Nelder-Mead", options={"maxiter": 150 if fam.name == "bekker_wong" else 2000, "xatol": 1e-4, "fatol": 1e-6})
        if best is None or r.fun < best.fun:
            best = r
    return best.x


def sample_posterior(fam, curves, seed, quick=False):
    """Returns an array of parameter vectors (u space plus s) representing the posterior."""
    xmap = fit_map(fam, curves, seed)
    if fam.name == "bekker_wong":
        rng = np.random.default_rng(seed + 1)
        out = [xmap]
        for _ in range(4 if quick else 8):           # bootstrap over curves
            pick = [curves[k] for k in rng.integers(0, len(curves), len(curves))]
            r = minimize(neg_log_post, xmap, args=(fam, pick), method="Nelder-Mead", options={"maxiter": 80})
            out.append(r.x)
        return np.array(out)
    import emcee
    nd = len(xmap); nw = max(16, 4 * nd)
    rng = np.random.default_rng(seed + 2)
    p0 = xmap + 1e-3 * rng.standard_normal((nw, nd))
    b = u_bounds(fam) + [S_BOUNDS]
    for k, (lo, hi) in enumerate(b):
        p0[:, k] = np.clip(p0[:, k], lo + 1e-9, hi - 1e-9)
    sam = emcee.EnsembleSampler(nw, nd, lambda v: -neg_log_post(v, fam, curves) * sum(len(c["x"]) for c in curves) / max(len(curves), 1))
    np.random.seed(seed + 3)
    sam.run_mcmc(p0, 300 if quick else 1500, progress=False)
    return sam.get_chain(discard=100 if quick else 500, thin=10, flat=True)


def predictive(fam, post, c, rng, n=200):
    idx = rng.integers(0, len(post), min(n, len(post)) if fam.name != "bekker_wong" else len(post))
    preds = []
    for k in idx:
        th = from_u(fam, post[k][:-1]); s = post[k][-1]
        mu = fam.predict(c["x"], c["kind"], c["ctx"], th)
        preds.append(np.clip(mu + rng.standard_normal(mu.shape) * np.sqrt(s ** 2 + c["yu"] ** 2), 0, 1))
        preds.append(np.clip(mu, 0, 1))  # also keep the mean prediction
    P = np.array(preds)
    mean = np.array(preds[1::2]).mean(axis=0)
    lo, hi = np.percentile(np.array(preds[0::2]), [5, 95], axis=0)
    return mean, lo, hi


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--quick", action="store_true")
    ap.add_argument("--families", default=",".join(FAMILIES), help="comma separated subset; outputs get a suffix when a subset is run")
    ap.add_argument("--extra-curves", default="", help="stage 21: an additional curve file in the same format (research/phase4/curves_new.csv)")
    ap.add_argument("--out", default="", help="output folder (default results/model_validation)")
    ap.add_argument("--group-sources", default="", help="POST HOC (review of 2026-10-21): comma separated a=b pairs; source a is held out together with b (same test campaign)")
    a = ap.parse_args()
    fams = [{**FAMILIES, **EXTRA_FAMILIES}[n] for n in a.families.split(",")]
    global OUT
    if a.out:
        OUT = os.path.join(ROOT, a.out)
    if len(fams) < len(FAMILIES):
        OUT = os.path.join(OUT, "part_" + "_".join(f.name for f in fams))
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    log = open(os.path.join(OUT, "run_log.txt"), "w")
    def say(m):
        print(m, flush=True); log.write(m + "\n"); log.flush()
    curves = load_curves() + (load_curves(os.path.join(ROOT, a.extra_curves)) if a.extra_curves else [])
    if a.group_sources:   # POST HOC: hold out test campaigns rather than publications
        gmap = dict(x.split("=") for x in a.group_sources.split(","))
        for c in curves:
            c["source"] = gmap.get(c["source"], c["source"])
    say(f"stage 15 run {time.strftime('%Y-%m-%d %H:%M:%S')}; {len(curves)} slip against slope curves from {len({c['source'] for c in curves})} sources; seed {SEED}")
    for c in curves:
        say(f"  {c['id']}: {c['kind']}, {len(c['x'])} points, {c['x'].min():.1f} to {c['x'].max():.1f} deg, {c['test_type']}, comparable {c['comparable']}")
    rng = np.random.default_rng(SEED)
    nominal_rows, fit_rows, loso_rows, transfer_rows = [], [], [], []
    for fam in fams:
        cs_all = [c for c in curves if usable(fam, c)]
        cs = [c for c in cs_all if c["method"] != "published_fit"]   # a published fit duplicates the digitised points of the same figure
        # 1. nominal (published fits included, for reference)
        for c in cs_all:
            pred = fam.predict(c["x"], c["kind"], c["ctx"], fam.nominal(c["ctx"]))
            nominal_rows.append({"family": fam.name, "curve": c["id"], "source": c["source"], "points": len(c["x"]), "rmse_nominal": round(rmse(pred, c["y"]), 4)})
        # 2. per curve fit
        for c in cs:
            x = fit_map(fam, [c], SEED, starts=3 if a.quick else 6)
            th = from_u(fam, x[:-1])
            pred = fam.predict(c["x"], c["kind"], c["ctx"], th)
            fit_rows.append({"family": fam.name, "curve": c["id"], "source": c["source"], "points": len(c["x"]), "rmse_fit": round(rmse(pred, c["y"]), 4),
                             **{k: round(v, 4) for k, v in th.items()}, "s": round(float(x[-1]), 4)})
        say(f"{fam.name}: nominal and per curve fits done on {len(cs)} curves")
        # 3. leave one study out
        sources = sorted({c["source"] for c in cs})
        for src in sources:
            train = [c for c in cs if c["source"] != src]; test = [c for c in cs if c["source"] == src]
            if not train:
                continue
            post = sample_posterior(fam, train, SEED, a.quick)
            for c in test:
                mean, lo, hi = predictive(fam, post, c, rng)
                loso_rows.append({"family": fam.name, "held_out_source": src, "curve": c["id"], "points": len(c["x"]), "train_curves": len(train),
                                  "rmse_heldout": round(rmse(mean, c["y"]), 4), "coverage90": round(float(np.mean((c["y"] >= lo) & (c["y"] <= hi))), 3),
                                  "mean_interval_width": round(float(np.mean(hi - lo)), 3)})
            say(f"{fam.name}: LOSO held out {src}: " + ", ".join(f"{r['curve']} rmse {r['rmse_heldout']:.3f} cover {r['coverage90']:.2f}" for r in loso_rows if r["family"] == fam.name and r["held_out_source"] == src))
        # 4. two way transfer: Dumont curve and Ishigami (or Takehana, Toyoura) curves
        dum = [c for c in cs if "dumont" in c["id"] and "sinkage" not in c["id"]]
        ish = [c for c in cs if c["source"].startswith(("ishigami", "takehana", "yoshida"))]
        for name, tr, te in (("Dumont to Toyoura lab curves", dum, ish), ("Toyoura lab curves to Dumont", ish, dum)):
            if tr and te:
                post = sample_posterior(fam, tr, SEED + 7, a.quick)
                for c in te:
                    mean, lo, hi = predictive(fam, post, c, rng)
                    transfer_rows.append({"family": fam.name, "direction": name, "curve": c["id"], "rmse": round(rmse(mean, c["y"]), 4),
                                          "coverage90": round(float(np.mean((c["y"] >= lo) & (c["y"] <= hi))), 3)})
        if fam.name == "exp_existing":   # posterior on the curves comparable to dune sand, for a posterior range set
            comp = [c for c in cs if c["comparable"].strip().lower() in ("yes", "partly") and c["kind"] == "direct ascent"]
            post = sample_posterior(fam, comp, SEED + 11, a.quick)
            q = {p.name: [float(np.exp(v)) if p.log else float(v) for v in np.percentile(post[:, k], [5, 50, 95])] for k, p in enumerate(fam.params)}
            q["s"] = [float(v) for v in np.percentile(post[:, -1], [5, 50, 95])]
            json.dump({"curves": [c["id"] for c in comp], "quantiles_5_50_95": q, "samples": int(len(post))}, open(os.path.join(OUT, "posterior_exp.json"), "w"), indent=1)
            say(f"exp_existing posterior on {len(comp)} comparable direct ascent curves: {json.dumps(q)}")
    for fn, rows in (("nominal.csv", nominal_rows), ("per_curve_fit.csv", fit_rows), ("loso.csv", loso_rows), ("transfer.csv", transfer_rows)):
        if rows:
            keys = []
            for r in rows:
                keys += [k for k in r if k not in keys]
            with open(os.path.join(OUT, fn), "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    # verdicts against the stage 15 bar
    summ = {"bar": {"median_heldout_rmse_max": BAR_RMSE, "pooled_coverage90_min": BAR_COVER}, "families": {}}
    for fam in fams:
        rr = [r for r in loso_rows if r["family"] == fam.name]
        if not rr:
            continue
        med = float(np.median([r["rmse_heldout"] for r in rr]))
        cov = float(np.sum([r["coverage90"] * r["points"] for r in rr]) / np.sum([r["points"] for r in rr]))
        summ["families"][fam.name] = {"heldout_curves": len(rr), "median_heldout_rmse": round(med, 4), "pooled_coverage90": round(cov, 3),
                                      "median_nominal_rmse": round(float(np.median([r["rmse_nominal"] for r in nominal_rows if r["family"] == fam.name])), 4),
                                      "median_fit_rmse": round(float(np.median([r["rmse_fit"] for r in fit_rows if r["family"] == fam.name])), 4),
                                      "survives": bool(med <= BAR_RMSE and cov >= BAR_COVER)}
        say(f"VERDICT {fam.name}: {summ['families'][fam.name]}")
    json.dump(summ, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
    _figure(curves, fit_rows)
    say(f"done {time.strftime('%Y-%m-%d %H:%M:%S')}")


def _figure(curves, fit_rows):
    sl = [c for c in curves if c["kind"] in ("direct ascent", "emulated by pull", "side slope")]
    n = len(sl); cols = 4; rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(3.4 * cols, 2.6 * rows), facecolor="#fffafb", squeeze=False)
    xx = np.linspace(0, 35, 71)
    for ax, c in zip(axes.ravel(), sl):
        ax.set_facecolor("#fffafb")
        ax.errorbar(c["x"], c["y"], yerr=c["yu"], fmt="o", ms=3, color="#2b2024", ecolor="#d8c3cb", lw=0.8)
        for k, fam in enumerate(FAMILIES.values()):
            r = [f for f in fit_rows if f["family"] == fam.name and f["curve"] == c["id"]]
            if r and usable(fam, c):
                th = {p.name: r[0][p.name] for p in fam.params}
                ax.plot(xx, fam.predict(xx, c["kind"], c["ctx"], th), color=PINK[k], lw=1.4, label=fam.name)
        ax.set_title(c["id"][:38], fontsize=7); ax.set_ylim(-0.05, 1.05); ax.set_xlim(0, 35); ax.tick_params(labelsize=7)
    for ax in axes.ravel()[n:]:
        ax.axis("off")
    axes[0, 0].legend(fontsize=6, frameon=False)
    fig.text(0.01, 0.0, "Points: PUBLISHED curves (research/phase3/curves.csv) with digitisation uncertainty. Lines: per curve best fits, SIMULATED BY ME; a good fit shows shape capacity, not predictive skill.", fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "figures", "fig_family_fits.png"), dpi=120, bbox_inches="tight")


if __name__ == "__main__":
    main()
