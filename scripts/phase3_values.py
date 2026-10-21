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
    v["ver_p4_n"] = sum(not r["id"].startswith(p3) for r in ev)
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
    tvm = _rd("results/terrain_validation/metrics.csv")
    for k in ("5", "10", "30"):
        rr = [r for r in tvm if r["posting_m"] == k]
        if rr:
            fs = [float(r["face_rate_in_traversable"]) for r in rr]; au = [float(r["auc"]) for r in rr]
            miss = [float(r["share_traversable"]) * float(r["face_rate_in_traversable"]) / float(r["true_face_rate"]) for r in rr]
            v[f"tv_fs_min_{k}"] = pct(min(fs)); v[f"tv_fs_max_{k}"] = pct(max(fs)); v[f"tv_auc_min_{k}"] = f2(min(au)); v[f"tv_auc_max_{k}"] = f2(max(au))
            v[f"tv_miss_min_{k}"] = pct(min(miss), 0); v[f"tv_miss_max_{k}"] = pct(max(miss), 0)
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
    names = {"exp_existing": "exponential", "bekker_wong": "Bekker Wong", "mohr_coulomb_ratio": "Mohr Coulomb ratio", "logistic_empirical": "logistic"}
    fams = [k[3:-9] for k in v if k.startswith("mv_") and k.endswith("_survives")]
    if fams:
        v["mv_verdict_line"] = "; ".join(f"{names.get(f, f)} {v['mv_' + f + '_survives']} (held out median {v['mv_' + f + '_heldout']})" for f in fams)
        v["score_model"] = "4" if any(v["mv_" + f + "_survives"] == "passes" for f in fams) else "3"
    pe = _js("results/model_validation/part_exp_existing_mohr_coulomb_ratio_logistic_empirical/posterior_exp.json")
    if pe:
        q = pe["quantiles_5_50_95"]
        for k in ("phi_deg", "f_r", "i0", "s"):
            v[f"post_{k}"] = f"{q[k][1]:.2f} ({q[k][0]:.2f} to {q[k][2]:.2f})"
        v["post_ncurves"] = len(pe["curves"])
    # stage 16: question 8, Sobol; stage 15 posterior map
    for d, key in (("subgrid_posterior_2026_10_20_mobile_posthoc", "postm"), ("subgrid_widened_i0_fr_mobile", "q8"), ("subgrid_posterior_2026_10_20", "post"), ("subgrid", "orig"), ("subgrid_widened_i0", "wi0"), ("subgrid_widened_i0_fr", "wfr")):
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
    for r in _rd("results/planner/matched_pairs.csv"):   # POST HOC matched pairs (only pairs the conservative policy routed)
        b = "3" if r["grade_baseline"].startswith("3") else "10"
        for pol in ("naive", "conservative", "risk_weighted"):
            if r[f"{pol}_fail_share"] != "":
                v[f"pm{b}_{r['site']}_{r['posting_m']}_{pol}"] = pct(r[f"{pol}_fail_share"], 1)
        v[f"pm_n_{r['site']}_{r['posting_m']}"] = r["pairs_routed_by_conservative"]
    # stage 18: rule options
    for r in _rd("results/field_kit/rule_options_2026-10-20.csv"):
        tag = r["rule"].split("_")[0] if r["rule"] == "current" else r["rule"].split("_")[1]
        v[f"ro_{tag}_{r['truth']}_{r['sigma']}"] = pct(r["accepted_rate"], 0)
        v[f"ro_{tag}_{r['truth']}_rej_{r['sigma']}"] = pct(1 - float(r["accepted_rate"]), 0)
    v.update(phase4_values())
    return v


def phase4_values() -> dict:
    """Numbers of the 2026-10-21 work (stages 19 to 24 and the phase 4 evidence and curves)."""
    v = {}
    ev = _rd("research/evidence.csv")
    v["scl_n"] = sum(r["id"].startswith("SCL") for r in ev)
    st = _js("research/verification_stats.json") or {}
    g = st.get("new rows of 2026-10-21 (scaling law sources), phase 6")
    if g:
        v["p6_n"] = g["n"]; v["p6_material"] = g["material_error"]; v["p6_minor"] = g["minor_error"]
    cur = st.get("CURRENT TABLE, latest verdict per row")
    if cur:
        v["cur_material_ci"] = f"{100*cur['material_wilson95'][0]:.1f} to {100*cur['material_wilson95'][1]:.1f} %" if cur.get("material_wilson95") else "n/a"
    # phase 4 curves and their independent redigitisation
    c4 = _rd("research/phase4/curves_new.csv")
    if c4:
        v["p4_ncurves"] = len({r["curve_id"] for r in c4}); v["p4_npoints"] = len(c4); v["p4_nsources"] = len({r["source_key"] for r in c4})
    rd = [r for r in _rd("research/phase4/redigitise_agreement.csv") if r["status"] == "compared"]
    if rd:
        v["redig_n"] = len(rd); v["redig_pts"] = sum(int(r["points_original"]) for r in rd); v["redig_matched"] = sum(int(r["matched_within_1deg"]) for r in rd)
        v["redig_extra"] = sum(int(r["points_verifier"]) - int(r["matched_within_1deg"]) for r in rd)
        v["redig_med"] = f"{statistics.median(float(r['median_abs_dslip_ratio']) for r in rd):.4f}"
        v["redig_max_med"] = f"{max(float(r['median_abs_dslip_ratio']) for r in rd):.4f}"
    # stage 21: replication on the expanded curve set; stage 22: scaling law families
    for part in ("part_exp_existing_mohr_coulomb_ratio_logistic_empirical", "part_bekker_wong", "part_mobility_pull_mobility_logistic"):
        s = _js(os.path.join("results/model_validation_phase4", part, "summary.json"))
        if s:
            for fam, d in s["families"].items():
                v[f"mv4_{fam}_heldout"] = f2(d["median_heldout_rmse"]); v[f"mv4_{fam}_cover"] = f2(d["pooled_coverage90"])
                v[f"mv4_{fam}_n"] = d["heldout_curves"]; v[f"mv4_{fam}_survives"] = "passes" if d["survives"] else "fails"
    sg = _js("results/model_validation_phase4_posthoc_grouped/part_exp_existing_mohr_coulomb_ratio_logistic_empirical/summary.json")
    if sg:
        hg = [d["median_heldout_rmse"] for d in sg["families"].values()]
        v["mvg_heldout_min"] = f2(min(hg)); v["mvg_heldout_max"] = f2(max(hg))
    if "mv4_bekker_wong_heldout" in v:
        v["mv4_bw_sentence"] = (f"On the {v['mv4_bekker_wong_n']} held out curves with wheel size, width and load, the Bekker Wong family reached "
                                f"{v['mv4_bekker_wong_heldout']} with coverage {v['mv4_bekker_wong_cover']}.")
    else:
        v["mv4_bw_sentence"] = "The Bekker Wong family was not rerun to completion on the expanded set within the session (its calibration is slow), so its stage 15 result stands alone."
    ho = [float(v[k]) for k in v if k.startswith("mv4_") and k.endswith("_heldout") and "mobility" not in k]
    if ho:
        v["mv4_heldout_min"] = f2(min(ho)); v["mv4_heldout_max"] = f2(max(ho))
    mob = [float(v[k]) for k in v if k.startswith("mv4_mobility") and k.endswith("_heldout")]
    if mob:
        v["mob_heldout_min"] = f2(min(mob)); v["mob_heldout_max"] = f2(max(mob))
    lg = _rd("results/model_validation_phase4/part_exp_existing_mohr_coulomb_ratio_logistic_empirical/loso.csv")
    mo = _rd("results/model_validation_phase4/part_mobility_pull_mobility_logistic/loso.csv")
    if lg:
        v["mv4_nsources"] = len({r["held_out_source"] for r in lg if r["family"] == "exp_existing"})
    if lg and mo:
        ids = {r["curve"] for r in mo if r["family"] == "mobility_pull"}
        v["mob_logistic_same"] = f2(statistics.median(float(r["rmse_heldout"]) for r in lg if r["family"] == "logistic_empirical" and r["curve"] in ids))
    pe = _js("results/model_validation_phase4/part_exp_existing_mohr_coulomb_ratio_logistic_empirical/posterior_exp.json")
    if pe:
        q = pe["quantiles_5_50_95"]
        v["post4_i0"] = f"{q['i0'][1]:.2f} ({q['i0'][0]:.2f} to {q['i0'][2]:.2f})"; v["post4_ncurves"] = len(pe["curves"])
    # stage 20: three more lidar fields, and the six fields together
    rows4 = _rd("results/terrain_validation_phase4/metrics.csv"); rows3 = _rd("results/terrain_validation/metrics.csv")
    def miss(r):
        return float(r["share_traversable"]) * float(r["face_rate_in_traversable"]) / float(r["true_face_rate"])
    for r in rows4:
        s, k = r["site"], r["posting_m"]
        v[f"lid4_auc_{s}_{k}"] = f2(r["auc"]); v[f"lid4_fs_{s}_{k}"] = pct(r["face_rate_in_traversable"]); v[f"lid4_miss_{s}_{k}"] = pct(miss(r), 0)
    for k in ("5", "10", "30"):
        for tag, rr in (("lid4", [r for r in rows4 if r["posting_m"] == k]), ("lid6", [r for r in rows3 + rows4 if r["posting_m"] == k])):
            if rr:
                v[f"{tag}_fs_min_{k}"] = pct(min(float(r["face_rate_in_traversable"]) for r in rr)); v[f"{tag}_fs_max_{k}"] = pct(max(float(r["face_rate_in_traversable"]) for r in rr))
                v[f"{tag}_miss_min_{k}"] = pct(min(miss(r) for r in rr), 0); v[f"{tag}_miss_max_{k}"] = pct(max(miss(r) for r in rr), 0)
                v[f"{tag}_auc_min_{k}"] = f2(min(float(r["auc"]) for r in rr)); v[f"{tag}_auc_max_{k}"] = f2(max(float(r["auc"]) for r in rr))
                v[f"{tag}_nsites"] = len(rr)
    for r in _rd("results/planner_phase4/policy_summary.csv"):
        v[f"pl4_{r['site']}_{r['posting_m']}_{r['policy']}"] = pct(r["share_routed_failing_on_truth"], 1) if r["share_routed_failing_on_truth"] else NR
    # stage 23: closed loop
    for r in _rd("results/closed_loop/summary.csv"):
        v[f"cl_{r['site']}_{r['posting_m']}_{r['policy']}_{r['mode']}"] = pct(r["entrapped_share"], 1) if r["entrapped_share"] else NR
    for r in _rd("results/closed_loop/estimator.csv"):
        v[f"cl_est_{r['site']}"] = f"{float(r['median_abs_error']):.3f}"
    for r in _rd("results/closed_loop/posthoc_fixed_field/summary.csv"):   # POST HOC variant after the midpoint review
        v[f"clph_{r['site']}_{r['posting_m']}_{r['policy']}_{r['mode']}"] = pct(r["entrapped_share"], 1) if r["entrapped_share"] else NR
    for r in _rd("results/closed_loop/posthoc_fixed_field/estimator.csv"):
        v[f"clph_est_{r['site']}"] = f"{float(r['median_abs_error_odometry_noise_2pct']):.3f}"
    ros = _js("results/closed_loop/ros2_smoke_test.json")
    if ros:
        v["ros_outcome"] = ros["outcome"]; v["ros_replans"] = ros["replans"]; v["ros_metres"] = ros["metres_driven"]
    # stage 24: SCM calibration
    sc = _js("results/chrono_scm_calibration/summary.json")
    if sc:
        v["scm_best_K"] = f"{sc['best']['K_m']:g}"; v["scm_best_phi"] = f"{sc['best']['phi_deg']:g}"
        v["scm_cal_rmse"] = f2(sc["best"]["rmse_cal"]); v["scm_pred_rmse"] = f2(sc["rmse_prediction"])
    for r in _rd("results/chrono_scm_calibration/prediction.csv"):
        sk = f"{float(r['slope_deg']):g}".replace(".", "p")
        v[f"scm_pred_{sk}"] = f2(r["chrono_slip"]); v[f"scm_dumont_{sk}"] = f2(r["dumont_cubic"])
    # stage 19: ICESat-2
    for r in _rd("results/icesat2/validation_metrics.csv"):
        if r.get("status") == "ok":
            s, L = r["site"], r["length_m"]
            v[f"is2_r_{s}_{L}"] = f2(r["pearson_r"]); v[f"is2_mad_{s}_{L}"] = f"{float(r['median_abs_diff_deg']):.1f}"
            v[f"is2_ratio_{s}_{L}"] = f2(r["median_ratio_steep"]); v[f"is2_n_{s}_{L}"] = r["valid_segments"]; v[f"is2_steep_{s}_{L}"] = r["steep_segments_lidar_20deg"]
            v[f"is2_pass_{s}_{L}"] = "passes" if r["method_passes"] == "True" else "fails"
    for r in _rd("results/icesat2/arabia_metrics.csv"):
        if r.get("status") == "ok":
            a, L = r["area"], r["length_m"]
            for k in ("valid_segments", "face_segments", "face_segments_28deg", "segments_ge_20deg", "runs_ge_20deg", "face_threshold_deg", "passes"):
                v[f"is2_{k}_{a}_{L}"] = r[k]
            for k in ("faces_in_traversable_original", "faces_in_unknown_original", "faces_in_traversable_posterior", "all_in_traversable_original"):
                v[f"is2_{k}_{a}_{L}"] = pct(r[k], 0) if r[k] not in ("", "nan") else NR
            for k in ("max_abs_slope_deg", "median_is2_minus_cop_on_faces_deg", "p95_abs_is2_deg", "p95_abs_cop_deg", "median_run_raw_max_deg", "median_run_corr_max_deg",
                      "median_run_corr_max_dip_minus30_deg", "median_run_corr_max_dip_plus30_deg"):
                v[f"is2_{k}_{a}_{L}"] = f"{float(r[k]):.1f}" if r[k] not in ("", "nan") else NR
            v["is2_method"] = "validated" if r["method_validated"] == "True" else "not validated"
            if L == "10" and r.get("posthoc_face_share_above_40deg", "") not in ("", "nan"):
                v[f"is2_ph_above40_{a}"] = pct(r["posthoc_face_share_above_40deg"], 0)
                v[f"is2_ph_trav2840_{a}"] = pct(r["posthoc_faces_28_40_in_traversable_original"], 0)
    for r in _rd("results/icesat2/validation_metrics.csv"):
        if r.get("status") == "ok" and r["length_m"] == "10":
            v[f"is2_ph_n28_{r['site']}"] = r.get("posthoc_is2_segments_28deg", "")
            v[f"is2_ph_near_{r['site']}"] = f"{float(r['posthoc_median_steepest_lidar_within_10m_of_is2_28deg']):.1f}" if r.get("posthoc_median_steepest_lidar_within_10m_of_is2_28deg") else NR
    if "is2_faces_in_traversable_original_A_10" in v:
        gaps = sorted(float(v[f"is2_median_is2_minus_cop_on_faces_deg_{a}_10"]) for a in "ABC")
        v["is2_gap_min"], v["is2_gap_max"] = f"{gaps[0]:.1f}", f"{gaps[-1]:.1f}"
        ft = sorted(v[f"is2_faces_in_traversable_original_{a}_10"] for a in "ABC")
        v["is2_ftrav_min"], v["is2_ftrav_max"] = ft[0], ft[-1]
        v["is2_summary_line"] = (f"Over Liwa and the Rub' al Khali, {v['is2_faces_in_traversable_original_A_10']}, {v['is2_faces_in_traversable_original_B_10']} and "
                                 f"{v['is2_faces_in_traversable_original_C_10']} of the ICESat-2 segments steeper than 28 degrees fell in cells the 30 m map calls TRAVERSABLE, "
                                 f"and 30 m slopes understated them by a median of {gaps[0]:.1f} to {gaps[-1]:.1f} degrees; "
                                 "the ICESat-2 method failed its own validation against lidar, so these are indications, not a validation.")
    return v


if __name__ == "__main__":
    for k, val in sorted(values().items()):
        print(k, "=", val)
