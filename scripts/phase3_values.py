#!/usr/bin/env python3
"""Numbers of the 2026-10-20 work (stages 12 to 18), read from the result files, for the report, the brief, the
proposals and the manuscript.  Every value is formatted text; a missing result file gives the text "not run".

    python3 scripts/phase3_values.py     # prints the dictionary
"""
from __future__ import annotations
import csv, json, os, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NR = "not run"


def _rd(p):
    p = os.path.join(ROOT, p)
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []


def _js(p):
    p = os.path.join(ROOT, p)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def pct(x, nd=1):
    return f"{100 * float(x):.{nd}f} %"


def f2(x, nd=2):
    return f"{float(x):.{nd}f}"


def values() -> dict:
    v = {}
    # evidence table and verification
    ev = _rd("research/evidence.csv")
    p3 = ("PLN", "TM3", "MOB", "SND", "DUN", "MAP", "ENV")
    v["p3_rows_total"] = len(ev)
    v["p3_rows_new"] = sum(r["id"].startswith(p3) for r in ev)
    v["p3_sources_total"] = len({r["source_url"] for r in ev})
    v["p3_sources_new"] = len({r["source_url"] for r in ev if r["id"].startswith(p3)})
    st = _js("research/verification_stats.json") or {}
    g = st.get("new rows of the 2026-10-20 evidence expansion, phase 5")
    if g:
        v["p5_n"] = g["n"]; v["p5_material"] = g["material_error"]; v["p5_minor"] = g["minor_error"]; v["p5_unverifiable"] = g["unverifiable"]
        v["p5_material_rate"] = pct(g["material_rate"]); v["p5_material_ci"] = f"{100*g['material_wilson95'][0]:.1f} to {100*g['material_wilson95'][1]:.1f} %" if g["material_wilson95"] else "n/a"
        v["p5_any_rate"] = pct(g["any_rate"])
    cur = st.get("CURRENT TABLE, latest verdict per row")
    if cur:
        v["cur_n"] = cur["n"]; v["cur_material"] = cur["material_error"]; v["cur_material_rate"] = pct(cur["material_rate"])
    vt = {}
    for r in ev:
        vt[r["validation_type"]] = vt.get(r["validation_type"], 0) + 1
    v["p3_vtype_line"] = ", ".join(f"{vt[k]} {k}" for k in sorted(vt, key=lambda k: -vt[k]))
    # stage 12: lidar
    for r in _rd("results/terrain_validation/metrics.csv"):
        s, k = r["site"], r["posting_m"]
        v[f"tv_auc_{s}_{k}"] = f2(r["auc"]); v[f"tv_fs_{s}_{k}"] = pct(r["face_rate_in_traversable"]); v[f"tv_rate_{s}_{k}"] = pct(r["true_face_rate"])
        v[f"tv_p_{s}_{k}"] = pct(r["mean_predicted_face_probability"]); v[f"tv_trav_{s}_{k}"] = pct(r["share_traversable"])
        v[f"tv_unkface_{s}_{k}"] = pct(r["face_rate_in_unknown"])
    for r in _rd("results/terrain_validation/slope_gap.csv"):
        v[f"tv_gap_{r['site']}"] = f"{float(r['median_gap_deg']):.1f}"
        v[f"tv_max1m_{r['site']}"] = f"{float(r['median_max_1m_slope_in_face_cells_deg']):.1f}"
    # stage 13: wind
    w = _rd("results/wind_azimuth/face_vs_wind.csv")
    v["wind_hits"] = f"{sum(r['hit'] == 'True' for r in w)} of {len(w)}" if w else NR
    for r in w:
        v[f"wind_diff_{r['site']}"] = f"{float(r['angular_difference_deg']):.0f}"; v[f"wind_R_{r['site']}"] = f2(r["face_resultant_length_R"])
        v[f"wind_hit_{r['site']}"] = "hit" if r["hit"] == "True" else "miss"
    # stage 14: chrono
    sw = [r for r in _rd("results/chrono_scm/sweep.csv") if r["slip"] != ""]
    def ch(w_, s_, sl):
        m = [r for r in sw if r["wheel"].startswith(w_) and r["soil"].startswith(s_) and float(r["slope_deg"]) == sl]
        return f2(m[0]["slip"]) if m else NR
    v["ch_w1s1_125"] = ch("W1", "S1", 12.5); v["ch_w1s1_20"] = ch("W1", "S1", 20.0); v["ch_w1s1_30"] = ch("W1", "S1", 30.0)
    v["ch_w1s2_20"] = ch("W1", "S2", 20.0)
    cmp_ = _rd("results/chrono_scm/comparison.csv")
    if cmp_:
        import math
        rm = []
        for wn in ("W1", "W2"):
            for sn in ("S1", "S2"):
                d = [float(r["chrono_slip_capped"]) - float(r["bekker_wong_nominal"]) for r in cmp_ if r["wheel"].startswith(wn) and r["soil"].startswith(sn)]
                rm.append(math.sqrt(sum(x * x for x in d) / len(d)))
        v["ch_vs_bw_lo"] = f2(min(rm)); v["ch_vs_bw_hi"] = f2(max(rm))
        dm = [(float(r["chrono_slip_capped"]) - float(r["dumont_cubic"])) ** 2 for r in cmp_ if r["wheel"].startswith("W1") and r["soil"].startswith("S1") and r["dumont_cubic"] != ""]
        v["ch_vs_dumont_rmse_grid"] = f2(math.sqrt(sum(dm) / len(dm)))
    # stage 15: model families
    for part in ("part_exp_existing_mohr_coulomb_ratio_logistic_empirical", "part_bekker_wong", ""):
        s = _js(os.path.join("results/model_validation", part, "summary.json"))
        if s:
            for fam, d in s["families"].items():
                v[f"mv_{fam}_heldout"] = f2(d["median_heldout_rmse"]); v[f"mv_{fam}_cover"] = f2(d["pooled_coverage90"])
                v[f"mv_{fam}_fit"] = f2(d["median_fit_rmse"]); v[f"mv_{fam}_nominal"] = f2(d["median_nominal_rmse"])
                v[f"mv_{fam}_survives"] = "passes" if d["survives"] else "fails"
        for r in _rd(os.path.join("results/model_validation", part, "nominal.csv")):
            if r["curve"] == "heverly2013_fig12_scarecrow_dumont":
                v[f"mv_{r['family']}_dumont_nominal"] = f2(r["rmse_nominal"])
    ho = [float(v[k]) for k in v if k.startswith("mv_") and k.endswith("_heldout")]
    if ho:
        v["mv_heldout_min"] = f2(min(ho)); v["mv_heldout_max"] = f2(max(ho)); v["mv_nfamilies"] = len(ho)
    pe = _js("results/model_validation/part_exp_existing_mohr_coulomb_ratio_logistic_empirical/posterior_exp.json")
    if pe:
        q = pe["quantiles_5_50_95"]
        for k in ("phi_deg", "f_r", "i0", "s"):
            v[f"post_{k}"] = f"{q[k][1]:.2f} ({q[k][0]:.2f} to {q[k][2]:.2f})"
        v["post_ncurves"] = len(pe["curves"])
    # stage 16: question 8, Sobol; stage 15 posterior map
    for d, key in (("subgrid_widened_i0_fr_mobile", "q8"), ("subgrid_posterior_2026_10_20", "post"), ("subgrid", "orig"), ("subgrid_widened_i0", "wi0"), ("subgrid_widened_i0_fr", "wfr")):
        for r in _rd(f"results/{d}/class_shares.csv"):
            if r["block"] == "1":
                v[f"{key}_unk_{r['area'][0]}"] = pct(r["UNKNOWN (total)"])
    for r in _rd("results/sobol_map/sobol_indices.csv"):
        v[f"sob_{r['range_set']}_{r['parameter']}_ST"] = f2(r["ST"])
    # stage 17: planner
    for r in _rd("results/planner/policy_summary.csv"):
        v[f"pl_{r['site']}_{r['posting_m']}_{r['policy']}"] = pct(r["share_routed_failing_on_truth"], 1) if r["share_routed_failing_on_truth"] else NR
        v[f"pl_routed_{r['site']}_{r['posting_m']}_{r['policy']}"] = pct(r["share_routed"], 0)
        v[f"pl_fpk_{r['site']}_{r['posting_m']}_{r['policy']}"] = f"{float(r['face_contacts_per_km']):.0f}" if r["face_contacts_per_km"] else NR
    for r in _rd("results/planner/posthoc_baseline_10m/policy_summary.csv"):
        v[f"pl10_{r['site']}_{r['posting_m']}_{r['policy']}"] = pct(r["share_routed_failing_on_truth"], 1) if r["share_routed_failing_on_truth"] else NR
    # stage 18: rule options
    for r in _rd("results/field_kit/rule_options_2026-10-20.csv"):
        v[f"ro_{r['rule'].split('_')[0] if r['rule'] == 'current' else r['rule'].split('_')[1]}_{r['truth']}_{r['sigma']}"] = pct(r["accepted_rate"], 0)
    return v


if __name__ == "__main__":
    for k, val in sorted(values().items()):
        print(k, "=", val)
