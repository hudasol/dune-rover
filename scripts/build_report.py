#!/usr/bin/env python3
"""Assemble docs/REPORT.md from hand-written sections (docs/src/*.md) plus tables generated from
research/evidence.csv, research/raw/uae_facts.csv and results/*.  Deterministic; no network.

Run from the repository root:  python3 scripts/build_report.py
"""
from __future__ import annotations
import csv, json, os, re, sys, statistics
from collections import OrderedDict
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover.slipmodel import PARAM_TABLE  # noqa: E402


def rd(path):
    with open(os.path.join(ROOT, path), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def esc(s, n=None):
    s = (s or "").replace("\n", " ").replace("|", "/").strip()
    if n and len(s) > n:
        s = s[: n - 1].rstrip() + "…"
    return s


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def f(x, nd=4):
    return f"{float(x):.{nd}f}"


def t_params():
    rows = []
    for k, (nom, lo, hi, status, basis) in PARAM_TABLE.items():
        rows.append([f"`{k}`", nom, f"{lo} to {hi}", esc(status), esc(basis)])
    rows.append(["`noise_sigma_m` (sensitivity only)", "0", "0 to 2 m", "ASSUMPTION", "Spatially correlated DEM error, correlation length 3 posts; no measured value for dune DEM error was retrieved."])
    return md_table(["Parameter", "Nominal", "Range", "Status", "Basis"], rows)


def t_slopestats():
    rows = []
    for r in rd("results/slope_stats.csv"):
        rows.append([r["area"], f"{float(r['posting_m']):.1f}", r["block"], f"{float(r['relief_m']):.0f}", f"{float(r['max_slope_deg']):.1f}",
                     *[f"{float(r['pct_gt_%d' % k]):.3g}" for k in (10, 15, 20, 25, 30)]])
    return md_table(["Window", "Posting, m", "Block", "Relief, m", "Max slope, deg", "% cells >10", ">15", ">20", ">25", ">30"], rows)


def t_nominal():
    S = json.load(open(os.path.join(ROOT, "results/summary.json")))
    routes = rd("results/routes_nominal.csv")
    rows = []
    for a, d in S["areas"].items():
        rr = [r for r in routes if r["area"] == a]
        lr = statistics.median(float(r["length_ratio"]) for r in rr)
        cr = statistics.median(float(r["cost_ratio"]) for r in rr)
        mu = max(float(r["max_uphill_deg"]) for r in rr)
        rows.append([a, f"{d['shape'][0]} x {d['shape'][1]}", f"{d['blocked_edge_frac']*100:.2f} %", f"{d['reach_frac']:.4f}",
                     f"{cr:.3f}", f"{lr:.3f}", f"{mu:.1f}", f"{d['n_od']} ({d['unreachable_od']} unreachable)"])
    return md_table(["Window", "Grid (rows x cols)", "Blocked edges", "Reachable share", "Median cost ratio", "Median length ratio",
                     "Steepest uphill on any route, deg", "Origin destination pairs"], rows)


def t_oat():
    rows_all = rd("results/sensitivity_oat.csv")
    A = OrderedDict((r["case"], r) for r in rows_all if r["area"] == "A_south_Liwa")
    B = {r["case"]: r for r in rows_all if r["area"] == "B_RubAlKhali_megadunes"}
    nomA = float(A["nominal"]["blocked_edge_frac"])
    rows = []
    for c, r in A.items():
        b = B[c]
        rows.append([c, f(r["blocked_edge_frac"], 4), f"{float(r['blocked_edge_frac'])/nomA:.2f}x" if c != "nominal" else "1",
                     f(r["median_cost_ratio"], 3), f(b["blocked_edge_frac"], 4), f(b["median_cost_ratio"], 3), f"{float(r['crit_uphill_deg']):.1f}"])
    return md_table(["Case", "A-south blocked share", "x nominal", "A-south median cost ratio", "B blocked share", "B median cost ratio",
                     "Critical uphill, deg"], rows)


def t_lhs_rank():
    S = json.load(open(os.path.join(ROOT, "results/summary.json")))
    names = {"phi_deg": "friction angle phi", "f_r": "resistance f_r", "i0": "slip scale i0", "i_max": "slip limit i_max", "noise_sigma_m": "DEM noise"}
    rows = []
    for k, nm in names.items():
        row = [nm]
        for core in ("A_core", "B_core"):
            for m in ("blocked_edge_frac", "median_cost_ratio", "crit_uphill_deg"):
                row.append(f"{S['sensitivity']['rank'][core][m]['spearman'][k]:+.2f}")
        rows.append(row)
    return md_table(["Assumption", "A: blocked share", "A: cost ratio", "A: critical uphill", "B: blocked share", "B: cost ratio", "B: critical uphill"], rows)


def t_lhs_pct():
    import numpy as np
    rows = []
    for core in ("A_core", "B_core"):
        d = rd(f"results/sensitivity_lhs_{core}.csv")
        for m, lab, nd in (("blocked_edge_frac", "blocked share", 4), ("median_cost_ratio", "median cost ratio", 3), ("reach_frac", "reachable share", 4), ("crit_uphill_deg", "critical uphill, deg", 1)):
            v = np.array([float(r[m]) for r in d])
            p = np.percentile(v, [0, 5, 50, 95, 100])
            rows.append([core, lab, *[f"{x:.{nd}f}" for x in p]])
    return md_table(["Core window", "Output", "min", "5 %", "median", "95 %", "max"], rows)


def t_anchor():
    rows = []
    for r in rd("results/anchor_check.csv"):
        lo, hi = float(r["published_slip_lo"]), float(r["published_slip_hi"])
        pub = f"{lo:.2f}" if lo == hi else f"{lo:.2f} to {hi:.2f} ({r['bound']})"
        rows.append([r["evidence_id"], f"{float(r['slope_deg']):.1f}", r["validation_type"], pub, f"{float(r['nominal_model_slip']):.2f}",
                     f"{float(r['envelope_min']):.2f} to {float(r['envelope_max']):.2f}", "yes" if r["envelope_overlaps_published"] == "True" else "NO",
                     esc(r["definition_warning"], 120)])
    return md_table(["Row", "Slope, deg", "Published validation", "Published slip", "Model nominal (SIM)", "Model envelope min to max (SIM)", "Envelope overlaps", "Definition warning"], rows)


# ---------------------------------------------------------------- stage 5 anchors (results/anchors, simulation only)
def t_anchor_dumont():
    S = json.load(open(os.path.join(ROOT, "results/anchors/summary.json"), encoding="utf-8"))["dumont"]
    rows = []
    for k in ("4.0", "10.0", "12.5", "16.0", "20.0", "21.0"):
        rows.append([k, f"{S['dumont_slip_at'][k]:.2f}", f"{S['nominal_slip_at'][k]:.2f}", f"{S['p95_slip_at'][k]:.2f}"])
    return md_table(["Slope, deg", "Dumont cubic (PUBLISHED fit, FLD-HV13-1)", "Model, nominal (SIMULATED)", "Model, 95th percentile of draws (SIMULATED)"], rows)


def t_anchor_ishigami():
    rows = []
    for r in rd("results/anchors/ishigami2009_comparison.csv"):
        rows.append([r["published_row"], f"{float(r['side_slope_deg']):.0f}", f"{r['published_value']} ({r['bound'].replace('_', ' ')})", esc(r["published_kind"], 90),
                     r["variant"], f"{float(r['model_min']):.2f} to {float(r['model_max']):.2f}", "yes" if r["model_envelope_compatible"] == "True" else "NO",
                     "yes" if r["scored"] == "True" else "no"])
    return md_table(["Row", "Side slope, deg", "Published", "What it is", "Model variant", "Model min to max (SIMULATED)", "Compatible", "Scored"], rows)


RANGE_SETS_RUN = (("original", "results", "results/subgrid", "results/anchors"),
                  ("widened_i0", "results/widened_i0", "results/subgrid_widened_i0", "results/anchors_widened_i0"),
                  ("widened_i0_fr", "results/widened_i0_fr", "results/subgrid_widened_i0_fr", "results/anchors_widened_i0_fr"))


def _j(path):
    return json.load(open(os.path.join(ROOT, path, "summary.json"), encoding="utf-8"))


def _ranges_txt(sm):
    pr = sm["parameters"]
    return f"i0 {pr['i0']['low']:g} to {pr['i0']['high']:g} (nominal {pr['i0']['nominal']:g}); f_r {pr['f_r']['low']:g} to {pr['f_r']['high']:g}"


def t_rs_phase1():
    rows = []
    for name, p1, _, _ in RANGE_SETS_RUN:
        sm = _j(p1); c = sm["crit_uphill_deg_across_lhs"]; ar = sm["areas"]
        rows.append([name, _ranges_txt(sm), f"{sm['nominal_critical_uphill_deg']:.1f}", f"{c['p05']:.1f} / {c['median']:.1f} / {c['p95']:.1f}",
                     f"{100*ar['A_south_Liwa']['blocked_edge_frac']:.2f} %", f"{100*ar['B_RubAlKhali_megadunes']['blocked_edge_frac']:.2f} %"])
    return md_table(["Range set", "Ranges", "Nominal climbing limit, deg", "Climbing limit across draws, 5th / median / 95th, deg",
                     "Blocked edges, A south (nominal)", "Blocked edges, B (nominal)"], rows)


def t_rs_phase2():
    data = {name: rd(f"{p2}/class_shares.csv") for name, _, p2, _ in RANGE_SETS_RUN}
    rows = []
    for i, r in enumerate(data["original"]):
        cells = [_area_letter(r["area"]), f"{float(r['posting_m']):.0f}"]
        for name, _, _, _ in RANGE_SETS_RUN:
            q = data[name][i]; assert q["area"] == r["area"] and q["posting_m"] == r["posting_m"]
            cells.append(f"{100*float(q['UNKNOWN (total)']):.1f} % / {100*float(q['BLOCKED']):.2f} %")
        rows.append(cells)
    return md_table(["Area", "Posting, m"] + [f"UNKNOWN / BLOCKED, {n}" for n, *_ in RANGE_SETS_RUN], rows)


def t_rs_anchor():
    rows = []
    for name, _, _, an in RANGE_SETS_RUN:
        sm = _j(an); d = sm["dumont"]; f = sm["dumont_posthoc_fit"]; e = sm["ishigami2009"]["envelopes"]
        rows.append([name, f"{d['nominal_cross50_deg']:.1f}", f"{d['median_cross50_deg']:.1f}", f"{d['dumont_cross50_deg']:.1f}",
                     pct(d["frac_dumont_inside_p05_p95"]), d["dumont_above_p95_deg"], f"{f['rmse']:.3f}",
                     f"{e['b1_10deg']['model_min']:.2f} to {e['b1_10deg']['model_max']:.2f}", f"{e['b2_10deg']['model_min']:.2f} to {e['b2_10deg']['model_max']:.2f}",
                     f"{e['b1_5deg']['model_min']:.2f} to {e['b1_5deg']['model_max']:.2f}"])
    return md_table(["Range set", "Nominal crosses 50 % at, deg", "Median of draws crosses 50 % at, deg", "Dumont crosses 50 % at, deg (PUBLISHED fit)",
                     "Dumont inside 5 to 95 % band", "Dumont above the band, deg", "POST HOC fit RMSE", "Ishigami b1 at 10 deg (measured about 0.5)", "Ishigami b2 (i0 0.81) at 10 deg",
                     "Ishigami b1 at 5 deg (his model: above 0.6)"], rows)


def t_power_rule():
    rows = [[r["truth"], r["sigma"], r["replicates"], pct(r["verdict_adequate_rate"], 0), pct(r["verdict_slip_ok_entrapment_not_reached_rate"], 0),
             pct(r["verdict_not_adequate_rate"], 0), pct(r["entrapment_not_reached_share"], 0), pct(r["flagged_uninformative_rate"], 0)]
            for r in rd("results/field_kit/power_study_2026-10-15_rule_2026-10-18.csv")]
    return md_table(["Synthetic truth", "Noise sigma", "Replicates", "Adequate", "Slip within tolerance, entrapment not reached", "Not adequate",
                     "Entrapment not reached", "Flagged uninformative"], rows)


def rs_values(v):
    for name, p1, p2, an in RANGE_SETS_RUN:
        key = {"original": "o", "widened_i0": "w", "widened_i0_fr": "wf"}[name]
        for r in rd(f"{p2}/class_shares.csv"):
            if float(r["posting_m"]) < 40:
                v[f"rs_{key}_unk_{_area_letter(r['area'])}"] = pct(r["UNKNOWN (total)"])
        sm = _j(an); v[f"rs_{key}_nomcross"] = f"{sm['dumont']['nominal_cross50_deg']:.1f}"; v[f"rs_{key}_medcross"] = f"{sm['dumont']['median_cross50_deg']:.1f}"
        v[f"rs_{key}_b1_10"] = f"{sm['ishigami2009']['envelopes']['b1_10deg']['model_min']:.2f} to {sm['ishigami2009']['envelopes']['b1_10deg']['model_max']:.2f}"
        v[f"rs_{key}_rmse"] = f"{sm['dumont_posthoc_fit']['rmse']:.3f}"
        v[f"rs_{key}_crit_med"] = f"{_j(p1)['crit_uphill_deg_across_lhs']['median']:.1f}"
    pr = {(r["truth"], r["sigma"]): r for r in rd("results/field_kit/power_study_2026-10-15_rule_2026-10-18.csv")}
    m, c, d = pr[("model", "0.03")], pr[("collapse", "0.03")], pr[("dumont", "0.03")]
    v["pr_model_adeq"] = pct(m["verdict_adequate_rate"]); v["pr_model_nr"] = pct(m["verdict_slip_ok_entrapment_not_reached_rate"])
    v["pr_model_not"] = pct(m["verdict_not_adequate_rate"]); v["pr_model_nrshare"] = pct(m["entrapment_not_reached_share"])
    v["pr_collapse_adeq"] = pct(c["verdict_adequate_rate"]); v["pr_dumont_adeq"] = pct(d["verdict_adequate_rate"])
    v["pr_janosi10_adeq"] = pct(pr[("janosi_mean", "0.1")]["verdict_adequate_rate"])
    return v


def anchor_values(v):
    S = json.load(open(os.path.join(ROOT, "results/anchors/summary.json"), encoding="utf-8"))
    d, fit, ish = S["dumont"], S["dumont_posthoc_fit"], S["ishigami2009"]
    v["an_d_cross"] = f"{d['dumont_cross50_deg']:.1f}"; v["an_nom_cross"] = f"{d['nominal_cross50_deg']:.1f}"
    v["an_med_cross"] = f"{d['median_cross50_deg']:.1f}"; v["an_p95_cross"] = f"{d['p95_cross50_deg']:.1f}"
    v["an_frac_mm"] = pct(d["frac_dumont_inside_min_max"]); v["an_frac_band"] = pct(d["frac_dumont_inside_p05_p95"])
    v["an_above_band"] = d["dumont_above_p95_deg"]; v["an_n_within"] = d["n_draws_within_0.10_everywhere"]; v["an_ndraw"] = d["n_draws"]
    v["an_fit_rmse"] = f"{fit['rmse']:.3f}"; v["an_fit_max"] = f"{fit['max_abs_error']:.2f}"; v["an_fit_cross"] = f"{fit['fitted_cross50_deg']:.1f}"
    v["an_fit_phi"] = f"{fit['phi_deg']:.1f}"; v["an_fit_fr"] = f"{fit['f_r']:.3f}"; v["an_fit_i0"] = f"{fit['i0']:.2f}"
    v["an_i0low"] = f"{ish['i0_lower_bound_from_table_I']:.2f}"
    for r in rd("results/dumont_prior/class_shares_30m.csv"):
        a = _area_letter(r["area"]); var = "base" if r["variant"].startswith("baseline") else ("unc" if "unclipped" in r["variant"] else "clip")
        v[f"dp_{a}_{var}_unk"] = f"{100*float(r['UNKNOWN (total)']):.2f} %"; v[f"dp_{a}_{var}_blk"] = f"{100*float(r['BLOCKED']):.2f} %"
    fi = rd("results/dumont_prior/dumont_fitted_i0.csv")[0]
    v["dp_i0_med"] = f"{float(fi['i0_median']):.2f}"; v["dp_i0_above"] = pct(fi["share_i0_above_0.40"], 0); v["dp_rmse"] = f"{float(fi['fit_rmse_median']):.2f}"
    e = ish["envelopes"]
    for k in ("b1_5deg", "b1_10deg", "b2_5deg", "b2_10deg"):
        v[f"an_{k}"] = f"{e[k]['model_min']:.2f} to {e[k]['model_max']:.2f}"
    return v


# ---------------------------------------------------------------- phase 2 tables and values (all read from files)
def pct(x, nd=1):
    return f"{100*float(x):.{nd}f} %"


def _area_letter(a):
    return a.split("_")[0]


def t_subgrid_params():
    from dunerover.subgrid import SUBGRID_PARAMS
    rows = []
    for k, (lo, hi, status, basis) in SUBGRID_PARAMS.items():
        rng = f"{lo} to {hi}" if hi is not None else str(lo)
        rows.append([f"`{k}`", rng, esc(status, 70), esc(basis, 230)])
    return md_table(["Sub grid quantity", "Range used", "Status", "Basis (morphology row ids in research/phase2/phase2_morphology.csv)"], rows)


def t_class_shares():
    rows = []
    for r in rd("results/subgrid/class_shares.csv"):
        rows.append([r["area"], r["posting_m"], pct(r["TRAVERSABLE"]), pct(r["BLOCKED"], 2), pct(r["UNKNOWN (total)"]),
                     pct(r["UNKNOWN (assumption sensitive)"]), pct(r["UNKNOWN (sub-grid face risk)"]), pct(r["UNKNOWN (both)"])])
    return md_table(["Area", "Posting, m", "TRAVERSABLE", "BLOCKED", "UNKNOWN total", "UNKNOWN: assumption sensitive only", "UNKNOWN: sub-grid face risk only", "UNKNOWN: both"], rows)


def t_robust():
    rows = [[r["area"], r["posting_m"], pct(r["unanimous_share"], 2), pct(r["sensitive_share"], 2), pct(r["always_passable_share(q=1)"], 2), pct(r["never_passable_share(q=0)"], 2)]
            for r in rd("results/subgrid/robustness_to_assumed_parameters.csv")]
    return md_table(["Area", "Posting, m", "Robust: same verdict in at least 95 % of draws", "Sensitive to the four assumptions", "Passable in all 256 draws", "Passable in no draw"], rows)


def t_scen():
    rows = []
    for r in rd("results/subgrid/subgrid_prior_sensitivity.csv"):
        if float(r["posting_m"]) < 40:
            rows.append([r["area"], esc(r["scenario"], 60), r["pi"], pct(r["UNKNOWN (total)"]), pct(r["mean_face_probability"])])
    return md_table(["Area (30 m)", "Sub grid variant", "pi (share of crests with an active face)", "UNKNOWN total", "Mean face probability"], rows)


def t_cc_map():
    rows = []
    for r in rd("results/subgrid/coverage_vs_certainty_map.csv"):
        if float(r["posting_m"]) < 40:
            rows.append([r["area"], r["tau"], pct(r["coverage"]), pct(r["expected_certainty_traversable"])])
    return md_table(["Area (30 m)", "Face probability threshold tau", "Coverage (not UNKNOWN)", "Model expected certainty of TRAVERSABLE cells (1 minus mean face probability)"], rows)


def t_cc_synth():
    rows = []
    for r in rd("results/subgrid/detector_skill.csv"):
        if r["tested_on"].endswith("(coverage vs certainty)") and r["tau"] in ("0.05", "0.1", "0.2", "0.5") and abs(float(r["posting_m"]) - round(float(r["posting_m"]))) < 0.5 and r["posting_m"] in ("29.6", "59.2", "88.8"):
            rows.append([r["posting_m"], r["tau"], pct(r["coverage"]), pct(r["certainty"]), pct(r["missed_face_rate_among_declared"])])
    return md_table(["Posting, m", "tau", "Coverage (declared face free)", "Certainty (truly face free among declared)", "Missed face rate among declared"], rows)


def t_detector():
    rows = []
    for r in rd("results/subgrid/detector_skill.csv"):
        if not r["tested_on"].endswith("(coverage vs certainty)") and r["posting_m"] in ("29.6", "59.2", "88.8"):
            rows.append([r["posting_m"], r["tested_on"], pct(r["face_rate"]), f"{float(r['auc']):.3f}", f"{float(r['brier']):.3f}", f"{float(r['brier_climatology']):.3f}"])
    return md_table(["Posting, m", "Held out synthetic ensemble (detector trained on base, pi 1.0)", "Face rate", "AUC", "Brier", "Brier of always predicting the base rate"], rows)


def t_reach():
    rows = [[r["area"], r["posting_m"], f"{float(r['reachable_phase1_rule'])*100:.0f} %", f"{float(r['reachable_unknown_impassable'])*100:.0f} %", f"{float(r['endpoints_not_traversable'])*100:.0f} %"]
            for r in rd("results/subgrid/reachability_unknown_impassable.csv")]
    return md_table(["Area", "Posting, m", "Pairs reachable (phase 1 rule, 10 pairs)", "Pairs reachable with UNKNOWN impassable", "Endpoints not TRAVERSABLE"], rows)


def t_power(fn="results/field_kit/power_study.csv"):
    rows = [[r["truth"], r["sigma"], r["replicates"], pct(r["adequate_rate"], 0), pct(r["failure_rate"], 0), pct(r["flagged_uninformative_rate"], 0), f"{float(r['median_tolerance']):.3f}"]
            for r in rd(fn)]
    return md_table(["Synthetic truth", "Noise sigma", "Replicates", "Called adequate", "Failed", "Flagged uninformative (3 x pilot sigma above 0.30)", "Median tolerance"], rows)


def t_ladder():
    import glob
    fn = sorted(glob.glob(os.path.join(ROOT, "docs/predictions/slope_ladder_predictions_*.csv")))[0]
    rows = []
    for r in csv.DictReader(open(fn, newline="", encoding="utf-8")):
        band = (f"{float(r['protocol_error_p05_sigma0.06']):+.2f} to {float(r['protocol_error_p95_sigma0.06']):+.2f}" if r.get("protocol_error_p05_sigma0.06") else "n/a (calibration slope)")
        rows.append([r["slope_deg"], r["role"], f"{float(r['prior_p05_phi_unknown']):.2f} to {float(r['prior_p95_phi_unknown']):.2f} (median {float(r['prior_p50_phi_unknown']):.2f})",
                     f"{float(r['prior_p05_phi_33pm2']):.2f} to {float(r['prior_p95_phi_33pm2']):.2f}", f"{float(r['prior_P_entrapment_phi_unknown'])*100:.0f} %", band])
    return md_table(["Slope, deg", "Role", "Prior predictive slip, 5 to 95 % (phi 28 to 38)", "Same with phi 33 plus or minus 2", "P(slip at least 0.8), phi unknown", "Protocol error band (predicted minus true), sigma 0.06"], rows), os.path.basename(fn)


def t_ladder_rev():
    rows = []
    for r in rd("docs/predictions/slope_ladder_predictions_2026-10-15.csv"):
        if "cross slope" in r["role"]:
            continue
        dv = f"{float(r['published_dumont_slip_FLD_HV13_1']):.2f}" if r["published_dumont_slip_FLD_HV13_1"] else "outside 4 to 21 deg"
        rows.append([r["slope_deg"], esc(r["role"], 120), f"plus or minus {float(r['tolerance_deg']):.0f}",
                     f"{float(r['prior_p05_phi_unknown']):.2f} to {float(r['prior_p95_phi_unknown']):.2f}", dv,
                     f"{float(r['planning_range_lo']):.2f} to {float(r['planning_range_hi']):.2f}"])
    return md_table(["Slope, deg", "Role", "Tolerance, deg", "Model prior 5 to 95 % (SIMULATED, unchanged)", "Dumont cubic (PUBLISHED, heavier vehicle)", "Planning range (PLANNED)"], rows)


def t_pred_tally():
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from tally_predictions import tally
    rows = [[k, c["HIT"], c["MIXED"], c["MISSED"], c["PENDING"]] for k, c in tally().items()]
    return md_table(["Stage", "HIT", "MIXED (part hit)", "MISSED", "pending"], rows)


def t_verif():
    st = json.load(open(os.path.join(ROOT, "research/verification_stats.json")))
    rows = []
    for name, d in st.items():
        mat = (f"{100*d['material_rate']:.1f} % (Wilson 95 % CI {100*d['material_wilson95'][0]:.1f} to {100*d['material_wilson95'][1]:.1f} %)" if d["material_wilson95"]
               else f"0 % (exact 95 % upper bound {100*d['material_upper95_exact']:.1f} %)")
        rows.append([name, d["n"], d["correct"], d["minor_error"], d["material_error"], mat, f"{100*d['any_rate']:.1f} % (Wilson 95 % CI {100*d['any_wilson95'][0]:.1f} to {100*d['any_wilson95'][1]:.1f} %)"])
    return md_table(["Group", "n", "correct", "minor", "material", "material rate", "any discrepancy rate"], rows)


def values(ev):
    """Named numbers for the narrative, all computed from files."""
    v = {}
    st = json.load(open(os.path.join(ROOT, "research/verification_stats.json")))
    al = st["CURRENT TABLE, latest verdict per row"]; ph2 = st["remaining rows, phase 2 full re-check"]
    ext = st["ALL 170 ROWS"]; cs = st["CURRENT SUPPLEMENTARY ROWS, latest verdict per row"]
    v["ver_ext_n"] = ext["n"]; v["ver_ext_material"] = ext["material_error"]; v["ver_ext_material_rate"] = pct(ext["material_rate"])
    v["ver_ext_any"] = ext["minor_error"] + ext["material_error"]; v["ver_ext_any_rate"] = pct(ext["any_rate"])
    v["ver_cs_n"] = cs["n"]; v["ver_cs_material"] = cs["material_error"]; v["ver_cs_material_rate"] = pct(cs["material_rate"])
    v["ver_cs_any"] = cs["minor_error"] + cs["material_error"]; v["ver_cs_any_rate"] = pct(cs["any_rate"])
    o144 = st["ALL 144 ROWS"]; sup = st["supplementary rows from supplied PDFs, phase 3"]
    v["ver_144_material"] = o144["material_error"]; v["ver_144_material_rate"] = pct(o144["material_rate"])
    v["ver_sup_n"] = sup["n"]; v["ver_sup_material"] = sup["material_error"]; v["ver_sup_material_rate"] = pct(sup["material_rate"])
    v["ver_sup_any"] = sup["minor_error"] + sup["material_error"]; v["ver_sup_any_rate"] = pct(sup["any_rate"])
    v["ver_all_n"] = al["n"]; v["ver_all_material"] = al["material_error"]; v["ver_all_minor"] = al["minor_error"]
    v["ver_all_material_rate"] = pct(al["material_rate"]); v["ver_all_any"] = al["minor_error"] + al["material_error"]; v["ver_all_any_rate"] = pct(al["any_rate"])
    v["ver_all_material_ci"] = f"{100*al['material_wilson95'][0]:.1f} to {100*al['material_wilson95'][1]:.1f} %"
    v["ver_ph1_n"] = st["random sample, phase 1 (n=30 of 137 unflagged)"]["n"] + st["flagged sample, phase 1"]["n"]
    v["ver_ph2_material"] = ph2["material_error"]; v["ver_ph2_n"] = ph2["n"]; v["ver_ph2_material_rate"] = pct(ph2["material_rate"])
    c = {}
    for r in ev:
        c[r["validation_type"]] = c.get(r["validation_type"], 0) + 1
    v["ntests"] = sum(open(os.path.join(ROOT, "tests", f), encoding="utf-8").read().count("\ndef test_") + (1 if open(os.path.join(ROOT, "tests", f), encoding="utf-8").read().startswith("def test_") else 0)
                      for f in sorted(os.listdir(os.path.join(ROOT, "tests"))) if f.startswith("test_") and f.endswith(".py"))
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from tally_predictions import tally
    tl = tally(); v["npred"] = sum(sum(c.values()) for c in tl.values())
    s1 = json.load(open(os.path.join(ROOT, "results/summary.json"), encoding="utf-8"))
    v["crit_nom"] = f"{s1['nominal_critical_uphill_deg']:.1f}"; v["crit_p05"] = f"{s1['crit_uphill_deg_across_lhs']['p05']:.1f}"
    v["crit_p95"] = f"{s1['crit_uphill_deg_across_lhs']['p95']:.1f}"
    v["pred_stage_line"] = "; ".join(f"{k.lower()}: {c['HIT']} hit, {c['MIXED']} mixed, {c['MISSED']} missed" + (f", {c['PENDING']} pending" if c["PENDING"] else "") for k, c in tl.items())
    v["vtype_line"] = f"Of {len(ev)} rows: " + ", ".join(f"{c[k]} {k}" for k in ("lab", "field", "simulation-only", "sim-vs-lab", "sim-vs-field") if k in c) + (f", {c['lab and field']} lab and field (one row mixing a prepared yard and a natural site)" if "lab and field" in c else "") + (f", {c['none']} none (an unreferenced capability statement kept for the record)" if "none" in c else "")
    for r in rd("results/subgrid/class_shares.csv"):
        a = _area_letter(r["area"]); k = {"29": 30, "30": 30, "59": 60, "60": 60, "88": 90, "89": 90}[r["posting_m"].split(".")[0]]
        v[f"unk_{a}_{k}"] = pct(r["UNKNOWN (total)"]); v[f"trav_{a}_{k}"] = pct(r["TRAVERSABLE"]); v[f"blk_{a}_{k}"] = pct(r["BLOCKED"], 2)
    for r in rd("results/subgrid/robustness_to_assumed_parameters.csv"):
        a = _area_letter(r["area"]); k = {"29": 30, "30": 30, "59": 60, "60": 60, "88": 90, "89": 90}[r["posting_m"].split(".")[0]]
        v[f"uni_{a}_{k}"] = pct(r["unanimous_share"]); v[f"sens_{a}_{k}"] = pct(r["sensitive_share"], 2)
    for r in rd("results/subgrid/subgrid_prior_sensitivity.csv"):
        if float(r["posting_m"]) < 40 and r["scenario"].startswith("POST HOC"):
            v[f"unk3_{_area_letter(r['area'])}_30"] = pct(r["UNKNOWN (total)"])
        if float(r["posting_m"]) < 40 and r["scenario"] == "base" and r["pi"] == "0.3":
            v[f"unkpi03_{_area_letter(r['area'])}_30"] = pct(r["UNKNOWN (total)"])
    return rs_values(anchor_values(v))


def appendix_a(ev):
    head = ["ID", "Vehicle or wheel", "Terrain", "Slope, deg", "Method family", "Metric", "Value", "Validation", "Source", "Location", "Retrieved", "Comparability warning"]
    rows = []
    for r in ev:
        rows.append([r["id"], esc(r["vehicle_or_wheel"], 70), esc(r["terrain_description"], 70), esc(r["slope_deg"], 20), esc(r["method_family"], 18),
                     esc(r["metric"], 60), esc((r["value"] + " " + r["unit"]).strip(), 60), r["validation_type"],
                     f"[link]({r['source_url']})" if r["source_url"].startswith("http") else esc(r["source_url"], 40), esc(r["passage_or_location"], 50),
                     r["retrieval_date"].replace("-", "\u2011"), esc(r["comparability_warning"], 160)])
    return md_table(head, rows)


def appendix_b(uae):
    rows = [[r["id"], esc(r["fact"], 220), f"[link]({r['source_url']})" if r["source_url"].startswith("http") else esc(r["source_url"], 40),
             esc(r["verification_status"], 40)] for r in uae]
    return md_table(["ID", "Fact", "Source", "Status"], rows)


def appendix_c(ev):
    by = OrderedDict()
    for r in ev:
        by.setdefault(r["source_url"], {"title": r["source_title"], "ids": []})["ids"].append(r["id"])
    rows = []
    for i, (u, d) in enumerate(by.items(), 1):
        ids = d["ids"]
        idtxt = ", ".join(ids) if len(ids) <= 6 else ", ".join(ids[:6]) + f" (+{len(ids)-6})"
        rows.append([i, esc(d["title"], 150), f"[{urlparse(u).netloc}]({u})" if u.startswith("http") else esc(u, 60), idtxt])
    return md_table(["#", "Title", "URL", "Evidence rows"], rows), len(by)


def main():
    ev = rd("research/evidence.csv")
    uae = rd("research/raw/uae_facts.csv")
    body = ""
    for fn in sorted(os.listdir(os.path.join(ROOT, "docs/src"))):
        if re.match(r"\d\d_.*\.md$", fn):
            body += open(os.path.join(ROOT, "docs/src", fn), encoding="utf-8").read() + "\n"
    sp = os.path.join(ROOT, "docs/src/second_pass.txt")
    second = open(sp, encoding="utf-8").read().strip() if os.path.exists(sp) else "Pending at the time of building this file."
    ladder_tab, ladder_file = t_ladder()
    vals = values(ev)
    import phase3_values as P3, build_manuscript as BM   # 2026-10-20 values and tables (stages 12 to 18)
    vals.update(P3.values()); vals = BM.extra_values(vals)
    for tmpl, outp in (("docs/src/brief_template.md", "docs/EXECUTIVE_BRIEF.md"), ("docs/src/readme_template.md", "README.md"),
                       ("docs/src/proposal_edge_template.md", "docs/PROPOSAL_EDGE.md"),
                       ("docs/src/proposal_robotics_template.md", "docs/PROPOSAL_ROBOTICS.md"),
                       ("docs/src/completeness_template.md", "docs/COMPLETENESS.md")):
        t = open(os.path.join(ROOT, tmpl), encoding="utf-8").read()
        for k, v in vals.items():
            t = t.replace("{{VAL:%s}}" % k, str(v))
        if "{{VAL:score_overall}}" in t:   # unweighted mean of the scores in the last column of the completeness table
            sc = [int(m) for m in re.findall(r"\| (\d+) \|\n", t)]
            t = t.replace("{{VAL:score_overall}}", f"{sum(sc) / len(sc):.1f}")
        left = re.findall(r"\{\{[^}]*\}\}", t)
        if left:
            raise SystemExit(f"unresolved placeholders in {tmpl}: {sorted(set(left))}")
        open(os.path.join(ROOT, outp), "w", encoding="utf-8").write(t)
        print("wrote", outp)
    tabs = {"params": t_params(), "slopestats": t_slopestats(), "nominal": t_nominal(), "oat": t_oat(), "lhs_rank": t_lhs_rank(),
            "lhs_pct": t_lhs_pct(), "anchor": t_anchor(), "subgrid_params": t_subgrid_params(), "class_shares": t_class_shares(), "robust": t_robust(),
            "scen": t_scen(), "cc_map": t_cc_map(), "cc_synth": t_cc_synth(), "detector": t_detector(), "reach": t_reach(), "power": t_power(),
            "ladder": ladder_tab, "pred_tally": t_pred_tally(), "verif": t_verif(),
            "anchor_dumont": t_anchor_dumont(), "anchor_ishigami": t_anchor_ishigami(),
            "ladder_rev": t_ladder_rev(), "power_rev": t_power("results/field_kit/power_study_2026-10-15.csv"),
            "rs_phase1": t_rs_phase1(), "rs_phase2": t_rs_phase2(), "rs_anchor": t_rs_anchor(), "power_rule": t_power_rule(),
            "families": BM.t_families(), "lidar": BM.t_lidar()}
    sg = os.path.join(ROOT, "docs/src/subgrid_section.md")
    body = body.replace("{{INCLUDE:subgrid}}", open(sg, encoding="utf-8").read() if os.path.exists(sg) else "")
    p3s = os.path.join(ROOT, "docs/src/phase3_section.md")
    body = body.replace("{{INCLUDE:phase3}}", open(p3s, encoding="utf-8").read() if os.path.exists(p3s) else "")
    an = os.path.join(ROOT, "docs/src/anchors_section.md")
    body = body.replace("{{INCLUDE:anchors}}", open(an, encoding="utf-8").read() if os.path.exists(an) else "")
    for k, v in tabs.items():
        body = body.replace("{{TABLE:%s}}" % k, v)
    body = body.replace("{{LADDER_FILE}}", ladder_file)
    for k, v in vals.items():
        body = body.replace("{{VAL:%s}}" % k, str(v))
    left = re.findall(r"\{\{(?:VAL|TABLE|INCLUDE)[^}]*\}\}", body)
    if left:
        raise SystemExit(f"unresolved placeholders: {sorted(set(left))}")
    body = body.replace("{{SECOND_PASS}}", second)
    c_tab, n_src = appendix_c(ev)
    app = ["\n---\n\n## Appendix A. Evidence table (all PUBLISHED; condensed, full fields in `research/evidence.csv`)\n",
           f"{len(ev)} rows. Validation types: " + ", ".join(f"{k} {v}" for k, v in sorted(
               {t: sum(1 for r in ev if r['validation_type'] == t) for t in {r['validation_type'] for r in ev}}.items())) +
           ". Values are as printed in the source; read the comparability warning before comparing any two rows. Verification status of each row is in the CSV (column `verification`).\n",
           appendix_a(ev),
           "\n\n## Appendix B. UAE facts (from `research/raw/uae_facts.csv`)\n", appendix_b(uae),
           f"\n\n## Appendix C. Sources ({n_src} distinct URLs; retrieval dates " + ", ".join(sorted({r['retrieval_date'] for r in ev})) + ", per row in `research/evidence.csv`)\n", c_tab, "\n"]
    out = body + "\n".join(app)
    path = os.path.join(ROOT, "docs/REPORT.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(out)
    print("wrote", path, len(out), "chars;", len(out.split()), "words")


if __name__ == "__main__":
    main()
