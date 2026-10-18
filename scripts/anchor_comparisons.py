#!/usr/bin/env python3
"""Compare the slip model with two published anchors (stage 5, pre registered in docs/PREDICTIONS.md).

    PYTHONPATH=src python3 scripts/anchor_comparisons.py

UNLIKE VEHICLES AND SOILS. Nothing here changes the model or its parameters; the post hoc fit is labelled
as such and reported after the untuned result.  Every number written is SIMULATED BY ME (simulation only,
model assumption dependent) except the published inputs, which are copied from verified evidence rows:

  (a) Dumont Dunes, Heverly et al. 2013, Sec 6.3 (FLD-HV13-1, FLD-HV13-2): cubic fit of slip (%) against
      slope (deg), valid about 4 to 21 deg, Scarecrow rover, soil parameters not reported.
  (b) Ishigami et al. 2009, Table I and Sec 3.2.2, 4.3, 6.3 (TM-IS09-1 to TM-IS09-5): Toyoura sand model
      inputs, 13.5 kg rover traversing 5 and 10 deg side slopes in a tilting bed.

Outputs: results/anchors/*.csv, summary.json, run_log.txt, figures/*.png.  Deterministic (fixed seeds).
"""
from __future__ import annotations
import csv, json, os, sys, time
import numpy as np
from scipy.stats import qmc
from scipy.optimize import least_squares
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover import SIM_LABEL  # noqa: E402
from dunerover.slipmodel import PARAM_TABLE, SlipParams, slip, apply_range_set, nominal_params  # noqa: E402

OUT = os.path.join(ROOT, "results", "anchors")
RANGE_SET = "original"
SEED_DUMONT, SEED_ISHIGAMI, N_DRAW = 20261020, 20261021, 4000
UNLIKE = "Comparison of unlike vehicles and soils"

# ---- published inputs (PUBLISHED, verified rows) ------------------------------------------------------------
DUMONT_C = (26.197, -8.849, 1.281, -0.034)          # FLD-HV13-1, slip % = c0 + c1 s + c2 s^2 + c3 s^3, s in deg
DUMONT_RANGE = (4.0, 21.0)                          # stated validity, "approximately 4 and 21 degrees"
DUMONT_TEXT = [(12.5, "below 50 %"), (16.0, "about 75 %"), (20.0, "about 90 %")]   # Sec 6.3 text
ISH_PHI, ISH_KX, ISH_R = 38.0, 0.07, 0.055          # Table I: friction angle (deg), kx (m), wheel radius (m)
ISH_I0_LOW = ISH_KX / (ISH_R * np.pi / 2)           # K / largest contact arc (quarter circumference): lower bound on i0
ISH_POINTS = [  # slope (deg, side slope), published value, kind, row, scored, bound
    (10.0, 0.5, "measured slip ratio, about 0.5, feed forward control, case B", "TM-IS09-3", True, "point"),
    (5.0, 0.6, "Ishigami model: slip ratio must exceed 0.6 for positive thrust (model to model)", "TM-IS09-2", True, "lower_bound"),
    (5.0, 0.4, "feedback control kept slip ratio below 0.4 (controlled, not scored)", "TM-IS09-5", False, "upper_bound"),
    (10.0, 0.4, "feedback control kept slip ratio below 0.4 (controlled, not scored)", "TM-IS09-5", False, "upper_bound"),
]

PINK = {"bg": "#fffafb", "pearl": "#f7dbe5", "sakura": "#e8a5bb", "rose": "#c9769a", "deep": "#a8325e",
        "wine": "#8a3a63", "plum": "#5b3a78", "sage": "#6fa28f", "ink": "#2b2024", "muted": "#4a3a40"}


def dumont(s):
    s = np.asarray(s, dtype=float)
    return (DUMONT_C[0] + DUMONT_C[1] * s + DUMONT_C[2] * s ** 2 + DUMONT_C[3] * s ** 3) / 100.0


def model_slip(slope_deg, phi, f_r, i0, cross=False):
    """Model slip capped at 1 (entrapment -> 1).  Direct ascent unless cross=True (side slope, heading along the contour)."""
    t = np.tan(np.radians(slope_deg))
    along, side = (0.0, t) if cross else (t, 0.0)
    return float(min(slip(along, side, SlipParams(phi_deg=phi, f_r=f_r, i0=i0)), 1.0))


def model_grid(slopes, P, cross=False):
    """Vectorised model slip for draws P (dict of arrays) on a slope grid -> array (n_draw, n_slope), capped at 1."""
    t = np.tan(np.radians(np.asarray(slopes)))[None, :]
    fr, i0 = P["f_r"][:, None], P["i0"][:, None]
    mu = np.tan(np.radians(P["phi_deg"]))[:, None]
    d = np.hypot(fr, t) if cross else np.abs(t + fr)
    x = d / mu
    s = np.where(x < 1, -i0 * np.log1p(-np.clip(x, 0, 0.999999)), np.inf)
    return np.minimum(s, 1.0)


def lhs(keys, seed, fixed=None):
    u = qmc.LatinHypercube(d=len(keys), seed=seed).random(N_DRAW)
    P = {k: PARAM_TABLE[k][1] + u[:, i] * (PARAM_TABLE[k][2] - PARAM_TABLE[k][1]) for i, k in enumerate(keys)}
    for k, v in (fixed or {}).items():
        P[k] = np.full(N_DRAW, float(v))
    return P


def crossing(x, y, level=0.5):
    """First x where y reaches level (linear interpolation); None if never."""
    y = np.asarray(y)
    idx = np.where(y >= level)[0]
    if len(idx) == 0:
        return None
    k = idx[0]
    if k == 0:
        return float(x[0])
    return float(x[k - 1] + (level - y[k - 1]) * (x[k] - x[k - 1]) / (y[k] - y[k - 1]))


def runs(mask, x):
    """Contiguous slope intervals where mask is True, as text."""
    out, start = [], None
    for i, m in enumerate(mask):
        if m and start is None:
            start = x[i]
        if (not m or i == len(mask) - 1) and start is not None:
            end = x[i] if m else x[i - 1]
            out.append(f"{start:.1f} to {end:.1f}"); start = None
    return "; ".join(out) if out else "none"


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


def style():
    plt.rcParams.update({"figure.facecolor": PINK["bg"], "axes.facecolor": PINK["bg"], "axes.edgecolor": "#d8c3cb",
                         "axes.labelcolor": PINK["muted"], "xtick.color": PINK["muted"], "ytick.color": PINK["muted"],
                         "text.color": PINK["ink"], "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                         "grid.color": "#f0e1e6", "grid.linewidth": 0.6, "font.size": 9, "axes.titlesize": 10,
                         "axes.titleweight": "bold", "legend.frameon": False})


def foot(fig, note):
    fig.text(0.01, 0.04, note, fontsize=7, color=PINK["muted"], va="bottom")
    fig.text(0.01, 0.012, SIM_LABEL + ". Published curves and points as printed in the cited rows.", fontsize=7, color=PINK["muted"])


# ---- (a) Dumont Dunes ----------------------------------------------------------------------------------------
def compare_dumont(log):
    s = np.round(np.arange(DUMONT_RANGE[0], DUMONT_RANGE[1] + 1e-9, 0.1), 1)
    d = dumont(s)
    P = lhs(("phi_deg", "f_r", "i0"), SEED_DUMONT)
    S = model_grid(s, P)
    nom = nominal_params()
    nominal = np.array([model_slip(v, nom.phi_deg, nom.f_r, nom.i0) for v in s])
    lo, hi = S.min(0), S.max(0)
    p05, p50, p95 = np.percentile(S, [5, 50, 95], axis=0)
    in_mm, in_band = (d >= lo) & (d <= hi), (d >= p05) & (d <= p95)
    within01 = np.all(np.abs(S - d[None, :]) <= 0.10, axis=1)
    rows = [{"slope_deg": f"{v:.1f}", "dumont_slip": f"{d[i]:.4f}", "model_nominal": f"{nominal[i]:.4f}", "model_min": f"{lo[i]:.4f}",
             "model_p05": f"{p05[i]:.4f}", "model_p50": f"{p50[i]:.4f}", "model_p95": f"{p95[i]:.4f}", "model_max": f"{hi[i]:.4f}",
             "dumont_inside_min_max": bool(in_mm[i]), "dumont_inside_p05_p95": bool(in_band[i])} for i, v in enumerate(s)]
    write_csv(os.path.join(OUT, "dumont_curve_comparison.csv"), rows)
    # wide grid for crossings beyond the Dumont validity range (model only)
    sw = np.round(np.arange(0.0, 40.0 + 1e-9, 0.1), 1)
    Sw = model_grid(sw, P)
    nomw = np.array([model_slip(v, nom.phi_deg, nom.f_r, nom.i0) for v in sw])
    p05w, p50w, p95w = np.percentile(Sw, [5, 50, 95], axis=0)
    above = d > p95
    first_above = float(s[np.where(above)[0][0]]) if above.any() else None
    # rounding of c3: +/- 0.0005 at 21 deg, in percentage points
    c3_round_pp = 0.0005 * 21.0 ** 3
    summ = {
        "first_line": UNLIKE + ": Scarecrow (340 kg, six 50 cm grousered wheels) at Dumont Dunes against a lumped slip law with assumed parameters; Dumont soil parameters are not reported.",
        "slope_grid": "4.0 to 21.0 deg, step 0.1 (171 points)",
        "n_draws": N_DRAW, "seed": SEED_DUMONT, "ranges": {k: PARAM_TABLE[k][1:3] for k in ("phi_deg", "f_r", "i0")},
        "dumont_cross50_deg": crossing(s, d), "nominal_cross50_deg": crossing(sw, nomw), "median_cross50_deg": crossing(sw, p50w),
        "p95_cross50_deg": crossing(sw, p95w), "p05_cross50_deg": crossing(sw, p05w),
        "frac_dumont_inside_min_max": float(in_mm.mean()), "frac_dumont_inside_p05_p95": float(in_band.mean()),
        "dumont_outside_min_max_deg": runs(~in_mm, s), "dumont_above_p95_deg": runs(above, s), "dumont_below_p05_deg": runs(d < p05, s),
        "first_slope_dumont_above_p95_deg": first_above,
        "frac_draws_within_0.10_everywhere": float(within01.mean()), "n_draws_within_0.10_everywhere": int(within01.sum()),
        "nominal_slip_at": {str(v): round(float(nominal[list(s).index(v)]), 4) for v in (4.0, 10.0, 12.5, 16.0, 20.0, 21.0)},
        "dumont_slip_at": {str(v): round(float(dumont(v)), 4) for v in (4.0, 10.0, 12.5, 16.0, 20.0, 21.0)},
        "p95_slip_at": {str(v): round(float(p95[list(s).index(v)]), 4) for v in (4.0, 10.0, 12.5, 16.0, 20.0, 21.0)},
        "c3_rounding_effect_at_21deg_pp": c3_round_pp,
    }
    log.append(f"(a) Dumont: inside min to max {100*in_mm.mean():.1f} %, inside 5 to 95 % band {100*in_band.mean():.1f} %, "
               f"50 % crossing Dumont {summ['dumont_cross50_deg']:.2f} deg, nominal {summ['nominal_cross50_deg']:.2f} deg, median {summ['median_cross50_deg']:.2f} deg")
    return s, d, nominal, lo, hi, p05, p50, p95, summ


def posthoc_fit(s, d, log):
    """POST HOC: bounded least squares of (phi, f_r, i0) to the Dumont grid. Multi start on a fixed 3 x 3 x 3 grid."""
    keys = ("phi_deg", "f_r", "i0")
    lb = np.array([PARAM_TABLE[k][1] for k in keys]); ub = np.array([PARAM_TABLE[k][2] for k in keys])

    def res(p):
        return np.array([model_slip(v, p[0], p[1], p[2]) for v in s]) - d
    best = None
    for a in np.linspace(0.2, 0.8, 3):
        for b in np.linspace(0.2, 0.8, 3):
            for c in np.linspace(0.2, 0.8, 3):
                x0 = lb + np.array([a, b, c]) * (ub - lb)
                r = least_squares(res, x0, bounds=(lb, ub), diff_step=1e-3)
                if best is None or r.cost < best.cost:
                    best = r
    p = best.x
    rmse = float(np.sqrt(np.mean(res(p) ** 2)))
    at_bound = [k for k, v, l, u in zip(keys, p, lb, ub) if min(v - l, u - v) <= 1e-3 * (u - l)]
    fitted = np.array([model_slip(v, *p) for v in s])
    out = {"label": "POST HOC recalibration test, not a validation; the untuned comparison comes first",
           "phi_deg": float(p[0]), "f_r": float(p[1]), "i0": float(p[2]), "rmse": rmse,
           "max_abs_error": float(np.max(np.abs(fitted - d))), "parameters_at_bound": at_bound,
           "fitted_cross50_deg": crossing(s, fitted)}
    write_csv(os.path.join(OUT, "dumont_posthoc_fit.csv"),
              [{"slope_deg": f"{v:.1f}", "dumont_slip": f"{d[i]:.4f}", "posthoc_fitted_model_slip": f"{fitted[i]:.4f}"} for i, v in enumerate(s)])
    log.append(f"(a, POST HOC) fit phi {p[0]:.2f}, f_r {p[1]:.3f}, i0 {p[2]:.3f}, RMSE {rmse:.4f}, at bound: {at_bound or 'none'}")
    return fitted, out


def fig_dumont(s, d, nominal, lo, hi, p05, p50, p95, fitted, summ, fit):
    style()
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.22)
    ax.fill_between(s, lo, hi, color=PINK["pearl"], lw=0, label="model, min to max of 4000 draws (SIMULATED)")
    ax.fill_between(s, p05, p95, color=PINK["sakura"], alpha=0.75, lw=0, label="model, 5 to 95 % of draws (SIMULATED)")
    ax.plot(s, nominal, color=PINK["deep"], lw=2, label="model, nominal parameters (SIMULATED)")
    ax.plot(s, p50, color=PINK["wine"], lw=1.2, ls="--", label="model, median of draws (SIMULATED)")
    ax.plot(s, fitted, color=PINK["sage"], lw=1.2, ls=":", label=f"POST HOC fit to Dumont, SIMULATED (RMSE {fit['rmse']:.3f})")
    ax.plot(s, d, color=PINK["plum"], lw=2.4, label="Dumont Dunes cubic fit, Heverly et al. 2013 (PUBLISHED, FLD-HV13-1)")
    for x, txt in DUMONT_TEXT:
        ax.plot(x, dumont(x), "o", color=PINK["plum"], ms=5, mec="white", mew=0.8)
        ax.annotate(f"text: {txt}", (x, dumont(x)), xytext=(-70 if x > 19 else 4, -14), textcoords="offset points", fontsize=7, color=PINK["plum"])
    ax.axhline(0.5, color="#d8c3cb", lw=0.8)
    ax.set_xlim(4, 21); ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("slope, deg (Dumont: rover tilt on direct upslope drives; model: direct ascent slope)")
    ax.set_ylabel("slip (fraction; 1 = no progress)")
    fig.suptitle(UNLIKE + ": model envelope against the Dumont Dunes slip curve", fontsize=10, fontweight="bold", x=0.08, ha="left")
    ax.set_title(f"Dumont crosses 50 % slip at {summ['dumont_cross50_deg']:.1f} deg, the nominal model at {summ['nominal_cross50_deg']:.1f} deg; "
                 f"{100*summ['frac_dumont_inside_p05_p95']:.0f} % of the Dumont curve lies in the 5 to 95 % band",
                 fontsize=8.5, fontweight="normal", loc="left")
    ax.legend(loc="upper left", fontsize=7)
    foot(fig, "Scarecrow, 340 kg, 50 cm grousered wheels, 8 runs; Dumont soil parameters not reported; fit valid about 4 to 21 deg only.\n"
              f"Range set {RANGE_SET}: phi {PARAM_TABLE['phi_deg'][1]:g} to {PARAM_TABLE['phi_deg'][2]:g} deg, f_r {PARAM_TABLE['f_r'][1]:g} to {PARAM_TABLE['f_r'][2]:g}, "
              f"i0 {PARAM_TABLE['i0'][1]:g} to {PARAM_TABLE['i0'][2]:g} (assumptions); nominal i0 {PARAM_TABLE['i0'][0]:g}.")
    fig.savefig(os.path.join(OUT, "figures", "fig_dumont_vs_model.png"), dpi=140); plt.close(fig)


# ---- (b) Ishigami 2009 ---------------------------------------------------------------------------------------
def compare_ishigami(log):
    P1 = lhs(("f_r", "i0"), SEED_ISHIGAMI, fixed={"phi_deg": ISH_PHI})
    frs = np.linspace(PARAM_TABLE["f_r"][1], PARAM_TABLE["f_r"][2], N_DRAW)
    P2 = {"phi_deg": np.full(N_DRAW, ISH_PHI), "f_r": frs, "i0": np.full(N_DRAW, ISH_I0_LOW)}
    slopes = np.array([5.0, 10.0])
    rows, res = [], {}
    for name, P, desc in (("b1", P1, f"phi 38 (Table I); f_r {PARAM_TABLE['f_r'][1]:g} to {PARAM_TABLE['f_r'][2]:g} and i0 {PARAM_TABLE['i0'][1]:g} to {PARAM_TABLE['i0'][2]:g} assumed ({RANGE_SET}); 4000 Latin hypercube draws"),
                          ("b2", P2, f"phi 38 (Table I); i0 = kx / (r pi / 2) = {ISH_I0_LOW:.3f} (lower bound); f_r {PARAM_TABLE['f_r'][1]:g} to {PARAM_TABLE['f_r'][2]:g} assumed ({RANGE_SET}), 4000 even steps")):
        S = model_grid(slopes, P, cross=True)
        for j, sl in enumerate(slopes):
            col = S[:, j]
            nomv = model_slip(sl, ISH_PHI, nominal_params().f_r, nominal_params().i0 if name == "b1" else ISH_I0_LOW, cross=True)
            r = {"variant": name, "variant_description": desc, "side_slope_deg": sl, "model_min": round(float(col.min()), 4),
                 "model_p05": round(float(np.percentile(col, 5)), 4), "model_p50": round(float(np.median(col)), 4),
                 "model_p95": round(float(np.percentile(col, 95)), 4), "model_max": round(float(col.max()), 4),
                 "model_at_nominal_f_r_0.12": round(nomv, 4)}
            rows.append(r); res[(name, sl)] = r
    write_csv(os.path.join(OUT, "ishigami2009_model_envelopes.csv"), rows)
    cmp_rows = []
    for sl, val, kind, rid, scored, bound in ISH_POINTS:
        for name in ("b1", "b2"):
            r = res[(name, sl)]
            ok = {"point": r["model_min"] <= val <= r["model_max"], "lower_bound": r["model_max"] >= val,
                  "upper_bound": r["model_min"] <= val}[bound]
            cmp_rows.append({"published_row": rid, "side_slope_deg": sl, "published_value": val, "bound": bound, "published_kind": kind,
                             "scored": scored, "variant": name, "model_min": r["model_min"], "model_max": r["model_max"],
                             "model_envelope_compatible": bool(ok), "gap_published_minus_model_max": round(val - r["model_max"], 4)})
    write_csv(os.path.join(OUT, "ishigami2009_comparison.csv"), cmp_rows)
    summ = {"first_line": UNLIKE + ": a 13.5 kg four wheel rover traversing 5 and 10 deg side slopes in a tilting bed of Toyoura sand, with steering held to keep a straight line, against a lumped slip law that has no steering or lateral slip; Table I gives no motion resistance and no contact length.",
            "i0_lower_bound_from_table_I": ISH_I0_LOW, "seed_b1": SEED_ISHIGAMI, "n_draws": N_DRAW,
            "envelopes": {f"{k[0]}_{k[1]:.0f}deg": v for k, v in res.items()},
            "comparisons": cmp_rows}
    for r in cmp_rows:
        log.append(f"(b) {r['variant']} {r['side_slope_deg']:.0f} deg: published {r['published_value']} ({r['published_row']}), model {r['model_min']:.3f} to {r['model_max']:.3f}, compatible {r['model_envelope_compatible']} ({r['bound']})")
    return res, summ


def fig_ishigami(res, summ):
    style()
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.22)
    off = {"b1": -0.35, "b2": 0.35}
    lab = {"b1": "model, phi 38 (Table I), f_r and i0 assumed (SIMULATED)", "b2": f"model, phi 38, i0 = {ISH_I0_LOW:.2f} from Table I kx, f_r assumed (SIMULATED)"}
    colr = {"b1": PINK["sakura"], "b2": PINK["rose"]}
    for name in ("b1", "b2"):
        for sl in (5.0, 10.0):
            r = res[(name, sl)]
            x = sl + off[name]
            ax.plot([x, x], [r["model_min"], r["model_max"]], color=colr[name], lw=7, solid_capstyle="butt", label=lab[name] if sl == 5.0 else None)
            ax.plot([x - 0.18, x + 0.18], [r["model_p50"]] * 2, color=PINK["wine"], lw=1.5)
    for sl, val, kind, rid, scored, _ in ISH_POINTS:
        if scored and rid == "TM-IS09-3":
            ax.plot(sl, val, "D", color=PINK["plum"], ms=8, mec="white", label="measured slip ratio about 0.5, case B (PUBLISHED, TM-IS09-3)")
        elif scored:
            ax.plot(sl, val, "^", color=PINK["deep"], ms=8, mec="white", label="Ishigami model: slip must exceed 0.6 (PUBLISHED model output, TM-IS09-2)")
        else:
            ax.plot([sl - 0.6, sl + 0.6], [val, val], color=PINK["sage"], lw=1.2, ls="--", label="feedback control kept slip below 0.4 (controlled, not scored)" if sl == 5.0 else None)
    ax.set_xlim(3, 12); ax.set_ylim(0, 1.0); ax.set_xticks([5, 10])
    ax.set_xlabel("side slope angle, deg (traversal across the slope)"); ax.set_ylabel("slip ratio (model: lumped slip)")
    fig.suptitle(UNLIKE + ": model with Ishigami 2009 Table I on side slopes", fontsize=10, fontweight="bold", x=0.08, ha="left")
    ax.set_title("bars: model min to max over draws; tick: median", fontsize=8.5, fontweight="normal", loc="left")
    ax.legend(loc="upper left", fontsize=7)
    foot(fig, "13.5 kg rover, wheel radius 5.5 cm, 8 cm Toyoura sand bed. Ishigami's slip is a wheel slip ratio under steering; the model's is a lumped demand slip.\n"
              "Table I gives no motion resistance and no contact length, so f_r is assumed and i0 = 0.81 is a lower bound.")
    fig.savefig(os.path.join(OUT, "figures", "fig_ishigami2009_vs_model.png"), dpi=140); plt.close(fig)


def main():
    global OUT, RANGE_SET
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--range-set", default="original", help="slipmodel.RANGE_SETS name (default original)")
    RANGE_SET = ap.parse_args().range_set
    apply_range_set(RANGE_SET)
    if RANGE_SET != "original":
        OUT = os.path.join(ROOT, "results", f"anchors_{RANGE_SET}")
    t0 = time.time()
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    log = [SIM_LABEL, UNLIKE + f" in both parts. Range set {RANGE_SET}. Pre registered in docs/PREDICTIONS.md (stage 5; widened sets stage 9).",
           f"numpy {np.__version__}, matplotlib {matplotlib.__version__}, seeds {SEED_DUMONT} and {SEED_ISHIGAMI}, {N_DRAW} draws"]
    s, d, nominal, lo, hi, p05, p50, p95, sd = compare_dumont(log)
    fitted, fit = posthoc_fit(s, d, log)
    fig_dumont(s, d, nominal, lo, hi, p05, p50, p95, fitted, sd, fit)
    res, si = compare_ishigami(log)
    fig_ishigami(res, si)
    summary = {"label": SIM_LABEL, "range_set": RANGE_SET, "ranges": {k: PARAM_TABLE[k][:3] for k in ("phi_deg", "f_r", "i0")}, "dumont": sd, "dumont_posthoc_fit": fit, "ishigami2009": si}
    json.dump(summary, open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8"), indent=1, default=str)
    log.append(f"run time {time.time()-t0:.1f} s")
    open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8").write("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
