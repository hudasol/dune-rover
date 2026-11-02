#!/usr/bin/env python3
"""Build the conference paper and its supplement from their templates and the result files of stages 25 to 29.

    PYTHONPATH=src python3 scripts/build_paper.py            # paper/paper.tex, paper/paper.pdf, paper/supplement.tex, .pdf
    PYTHONPATH=src python3 scripts/build_paper.py --check    # fail if a generated .tex is stale or a value is missing

Every number in the paper comes from a result file through a {{VAL:key}} placeholder; tables are built here. The text
around the numbers is in paper/src/*.tex. SIMULATED BY ME on PUBLISHED data.
"""
from __future__ import annotations
import csv, json, os, re, shutil, subprocess, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(ROOT, "paper")
SRC = os.path.join(PAPER, "src")
BEN = os.path.join(ROOT, "results", "benchmark")
S27, S28, S29, S30 = os.path.join(BEN, "stage27"), os.path.join(BEN, "stage28"), os.path.join(BEN, "stage29"), os.path.join(BEN, "stage30")
S31 = os.path.join(BEN, "stage31")
SITE_LABEL = {"Dumont": "Dumont Dunes, CA", "WhiteSands": "White Sands, NM", "Kelso": "Kelso Dunes, CA",
              "GreatSandDunes": "Great Sand Dunes, CO", "Algodones": "Algodones Dunes, CA", "LittleSahara": "Little Sahara, UT"}
SITES = list(SITE_LABEL)
NA = r"$\cdot$"
WORDS = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
         11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
         19: "nineteen", 20: "twenty"}


def read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def key(*parts):
    return "_".join(str(p) for p in parts).replace("-", "").replace("+", "plus").replace(".", "p").replace(" ", "")


def rnd(x, nd=0):
    """Round half away from zero (Python's round and format round half to even)."""
    from decimal import Decimal, ROUND_HALF_UP
    q = Decimal(1).scaleb(-nd)
    return float(Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP))


def rnd100(x, nd=0):
    """100 times x, rounded half away from zero on the decimal value of x (so 0.285 gives 28.5 and then 29)."""
    from decimal import Decimal, ROUND_HALF_UP
    q = Decimal(1).scaleb(-nd)
    return float((Decimal(repr(float(x))) * 100).quantize(q, rounding=ROUND_HALF_UP))


def f2(x):
    return f"{rnd(x, 2):.2f}"


def pc(x, nd=0):
    return f"{rnd100(float(x), nd):.{nd}f}\\,\\%"


def pts(x):
    v = rnd100(float(x), 0)
    return (f"+{v:.0f}" if v > 0 else f"$-${-v:.0f}") if v != 0 else "0"


# ---------------------------------------------------------------------------------------------------------------------
# values
# ---------------------------------------------------------------------------------------------------------------------
def det_rows():
    rows = []
    for f in ("A_metrics.csv", "D_metrics.csv", "E_metrics.csv", "F_metrics.csv", "G_metrics.csv", "H_metrics.csv"):
        p = os.path.join(S27, f)
        if os.path.exists(p):
            for r in read(p):
                if f == "F_metrics.csv" and r["method"] == "BICUBIC":
                    continue          # the same numbers as part A
                if f == "E_metrics.csv" and r["method"] == "GBM":
                    continue
                if f == "G_metrics.csv" and r["method"] == "GBM":
                    continue
                if f == "H_metrics.csv" and r["method"] == "SLOPE":
                    continue
                rows.append(r)
    p = os.path.join(S30, "e_imagery_cnn_detection_by_site.csv")       # stage 30, post hoc
    if os.path.exists(p):
        rows += read(p)
    for f in ("e_products_detection_by_site.csv", "f_unet_detection_by_site.csv"):   # stage 31, post hoc
        p = os.path.join(S31, f)
        if os.path.exists(p):
            rows += read(p)
    return rows


def values():
    V = {}
    D = det_rows()
    groups = {}
    for r in D:
        groups.setdefault((r["input"], r["method"]), []).append(r)
    for (i, m), rr in groups.items():
        a = [float(r["auc"]) for r in rr]
        V[key("auc", i, m)] = f2(np.mean(a)); V[key("aucmin", i, m)] = f2(min(a)); V[key("aucmax", i, m)] = f2(max(a))
        ap = [float(r["ap"]) for r in rr if r.get("ap", "") not in ("", "nan")]
        if ap:
            V[key("ap", i, m)] = f2(np.mean(ap))
        prev = [float(r["prevalence"]) for r in rr]
        V[key("prev", i)] = pc(np.mean(prev))
        for r in rr:
            V[key("auc", i, m, r["site"])] = f2(r["auc"])
    # paired differences (part A): sites where the method is significantly above or below the reference
    for r0 in {(r["input"], r["method"], r["reference"]) for r in read(os.path.join(S27, "A_paired_differences.csv"))}:
        rr = [r for r in read(os.path.join(S27, "A_paired_differences.csv")) if (r["input"], r["method"], r["reference"]) == r0]
        V[key("nup", *r0)] = str(sum(r["significant"] == "True" and float(r["auc_difference"]) > 0 for r in rr))
        V[key("ndown", *r0)] = str(sum(r["significant"] == "True" and float(r["auc_difference"]) < 0 for r in rr))
        V[key("nupb", *r0)] = str(sum(r["significant_bonferroni6"] == "True" and float(r["auc_difference"]) > 0 for r in rr))
    # gains
    g = lambda i, m: float(V[key("auc", i, m)])
    V["gain_s2_I30"] = f"{g('I30', 'DEM+S2') - g('I30', 'GBM'):+.2f}"
    V["auc_G30_best"] = f2(max(np.mean([float(r["auc"]) for r in rr]) for (i, m), rr in groups.items() if i == "G30"))
    V["gain_naip_I30"] = f"{g('I30', 'DEM+NAIP') - g('I30', 'GBM'):+.2f}"
    V["gain_10to30_bic"] = f"{g('I10to30', 'BICUBIC') - g('I30', 'BICUBIC'):+.2f}"
    # resolution sweep and scaling
    if os.path.exists(os.path.join(S27, "C_macro.csv")):
        for r in read(os.path.join(S27, "C_macro.csv")):
            V[key("sw", int(float(r["posting_m"])), r["method"])] = f2(r["auc"])
        bs = read(os.path.join(S27, "C_scaling_by_site.csv"))
        for d in {int(float(r["posting_m"])) for r in bs}:
            for m in ("GBM", "BICUBIC"):
                tot = 0
                for b in ("0 to 0.5", "0.5 to 1", "1 to 2", "2 to 4", "4 to 8", "8 to inf"):
                    rr = [r for r in bs if int(float(r["posting_m"])) == d and r["method"] == m and r["ratio_bin"] == b]
                    n = sum(int(r["patches"]) for r in rr); tot += n
                    if n:
                        V[f"rec{d}_{m}_{b.split()[0].replace('.', 'p')}"] = pc(sum(int(r["detected"]) for r in rr) / n)
            rr = [r for r in bs if int(float(r["posting_m"])) == d and r["method"] == "GBM"]
            short = sum(int(r["patches"]) for r in rr if r["ratio_bin"] in ("0 to 0.5", "0.5 to 1"))
            V[f"short{d}_share"] = pc(short / max(1, sum(int(r["patches"]) for r in rr)))
        sc = read(os.path.join(S27, "C_scaling.csv"))
        for m in ("GBM", "BICUBIC", "SLOPE", "DET"):
            for b in ("0 to 0.5", "0.5 to 1", "1 to 2", "2 to 4", "4 to 8", "8 to inf"):
                rr = [r for r in sc if r["method"] == m and r["ratio_bin"] == b and r["recall"] != ""]
                n = sum(int(r["patches"]) for r in rr)
                if n:
                    V[key("rec", m, b.split()[0])] = pc(sum(float(r["recall"]) * int(r["patches"]) for r in rr) / n)
    # label sensitivity
    if os.path.exists(os.path.join(S27, "B_macro.csv")):
        for r in read(os.path.join(S27, "B_macro.csv")):
            V[key("lab", r["label"], r["method"])] = f2(r["auc"])
    # statistics
    if os.path.exists(os.path.join(S27, "I_summary.json")):
        I = json.load(open(os.path.join(S27, "I_summary.json")))
        rng = [v for v in I["correlogram_range_m"].values() if v]
        V["corr_range_min"], V["corr_range_max"] = f"{min(rng):.0f}", f"{max(rng):.0f}"
        V["corr_block_m"] = f"{I['block_m_used_for_sensitivity']:.0f}"
        for r in read(os.path.join(S27, "I_site_tests.csv")):
            m = r["comparison"].split(" minus")[0]
            V[key("sf_p", m)] = f"{float(r['p_sign_flip']):.3f}".rstrip("0").rstrip("."); V[key("sf_holm", m)] = f"{float(r['p_holm']):.2f}"
            V[key("sf_pos", m)] = r["positive_sites"]
    # stage 28
    if os.path.exists(os.path.join(S28, "A_held_out.csv")):
        for r in read(os.path.join(S28, "A_held_out.csv")):
            if r["policies"] != "conservative+risk_weighted":
                continue
            pf = "post" if r["profile"] == "published-posterior" else "assu"
            k = key("ho", pf, r["endpoints"], r["input"], r["layer"])
            V[k] = pc(r["mission_success"]); V[k + "_d"] = pts(r["difference"]); V[k + "_lo"] = pts(r["diff_lo"]); V[k + "_hi"] = pts(r["diff_hi"])
            V[k + "_dabs"] = f"{rnd100(abs(float(r['difference']))):.0f}"
            V[k + "_pos"] = r["positive_sites"]; V[k + "_p"] = f"{float(r['p_sign_flip']):.3f}".rstrip("0").rstrip(".")
            V[k + "_routed"] = pc(r["routed"])
            if r.get("m_on_face_per_km", "") != "":
                V[k + "_mkm"] = f"{float(r['m_on_face_per_km']):.0f}"
        for r in read(os.path.join(S28, "A_naive.csv")):
            pf = "post" if r["profile"] == "published-posterior" else "assu"
            k = key("nv", pf, r["endpoints"], r["input"])
            V[k] = pc(r["mission_success"]); V[k + "_unsafe"] = pc(r["unsafe_of_routed"]); V[k + "_unsafefp"] = pc(r["unsafe_fp_of_routed"])
            V[k + "_unsafe1"] = pc(r["unsafe_of_routed"], 1); V[k + "_unsafefp1"] = pc(r["unsafe_fp_of_routed"], 1)
            V[k + "_mkm"] = f"{float(r['m_on_face_per_km']):.0f}"
            V[k + "_desc"] = pc(r["unsafe_descent_only"]) if r.get("unsafe_descent_only", "") != "" else NA
        ref = read(os.path.join(S28, "B_refusals.csv"))
        for r in ref:
            if r["profile"] == "published-posterior" and r["endpoints"] == "E1" and r["policy"] == "conservative" and r["param"] == "0.2":
                k = key("ref", r["input"], r["layer"])
                n = int(r["unrouted"])
                V[k] = pc((int(r["start_refused"]) + int(r["goal_refused"]) + int(r["both_refused"])) / n) if n else NA
        dr = read(os.path.join(S28, "D_descent_rule.csv"))
        for pf in ("published-posterior", "assumed"):
            for i in ("I10", "I30"):
                v = [float(r["share_removed"]) for r in dr if r["profile"] == pf and r["input"] == i]
                V[key("descent", pf[:4], i, "max")] = pc(max(v), 2)
        sweep = read(os.path.join(S28, "A_sweep.csv"))
        cons = [float(r["routed"]) for r in sweep if r["profile"] == "published-posterior" and r["endpoints"] == "E1" and r["input"] == "I30" and r["policy"] == "conservative"]
        V["cons_routed_I30_max"] = pc(max(cons))
        cons10 = [float(r["routed"]) for r in sweep if r["profile"] == "published-posterior" and r["endpoints"] == "E1" and r["input"] == "I10" and r["policy"] == "conservative"]
        V["cons_routed_I10_max"] = pc(max(cons10))
    if os.path.exists(os.path.join(S28, "C_degraded.csv")):
        for r in read(os.path.join(S28, "C_degraded.csv")):
            k = key("dg", r["endpoints"], r["input"], r["map"], r["policy"][:4])
            V[k] = pc(r["mission_success"]); V[k + "_routed"] = pc(r["routed"]); V[k + "_lr"] = f2(r["length_ratio"])
    if os.path.exists(os.path.join(S28, "E_closed_loop.csv")):
        for r in read(os.path.join(S28, "E_closed_loop.csv")):
            pf = "post" if r["profile"] == "published-posterior" else "assu"
            k = key("cl", pf, r["endpoints"], r["input"], r["layer"], int(float(r["radius_m"])))
            V[k] = pc(r["success"]); V[k + "_stuck"] = pc(r["stuck"]); V[k + "_unsafe"] = pc(r["unsafe"]); V[k + "_lr"] = f2(r["length_ratio_reached"]) if r["length_ratio_reached"] else NA
            V[k + "_replans"] = f"{float(r['replans']):.0f}"
            if r.get("diff_vs_slip_only", "") not in ("", None):
                V[k + "_d"] = pts(r["diff_vs_slip_only"]); V[k + "_lo"] = pts(r["diff_lo"]); V[k + "_hi"] = pts(r["diff_hi"])
    # vehicle limits and run sizes
    pl = json.load(open(os.path.join(BEN, "planning", "summary.json")))
    V["crit_assumed"] = f"{pl['critical_uphill_deg']['assumed']:.1f}"
    V["crit_posterior"] = f"{pl['critical_uphill_deg']['published-posterior']:.1f}"
    for r in read(os.path.join(BEN, "runtime.csv")):
        V[f"rt_{r['input']}_assess"] = f"{float(r['assess_s']):.1f}"; V[f"rt_{r['input']}_routes"] = f"{float(r['routes_100_s']):.1f}"
        V["rt_area"] = f"{float(r['area_km2']):.0f}"
    for r in read(os.path.join(BEN, "posthoc", "glo30_shift.csv")):
        V[f"shift_{r['site']}"] = f"{float(r['best_shift_m']):.0f}"
    meta = read(os.path.join(BEN, "site_metadata.csv"))
    for r in meta:
        V[f"s2date_{r['site']}"] = r["sentinel2_date"]
    V["naip_min"], V["naip_max"] = min(r["naip_year"] for r in meta), max(r["naip_year"] for r in meta)
    V["area_total"] = f"{sum(float(r['area_km2']) for r in meta):.0f}"
    p = os.path.join(BEN, "r10_source.csv")
    if os.path.exists(p):
        src = read(p)
        same = {r["site"] for r in src if r["same_as_truth_lidar"] == "True" and float(r["window_share"]) > 0.99}
        V["r10_same_sites"] = "all six" if len(same) == 6 else WORDS[len(same)] + " of the six"
    # stage 29, post hoc checks
    p = os.path.join(S29, "a_patch_size.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("ps", r["endpoints"], r["input"], r["layer"], r["min_patch_posts"]) + ("_nd" if r["without_dumont"] == "True" else "")
            V[k] = pc(r["mission_success"])
        A = {(r["endpoints"], r["input"], r["layer"], r["min_patch_posts"], r["without_dumont"]): float(r["mission_success"]) for r in read(p)}
        for inp in ("I10", "I30"):
            V[f"ps_gain_{inp}_300"] = f"{rnd(round(100 * (A[('E1', inp, 'BICUBIC-cal', '300', 'False')] - A[('E1', inp, 'none', '300', 'False')]), 6), 0):.0f}"
    p = os.path.join(S29, "b_planning.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("pb", r["input"], r["layer"])
            V[k] = pc(r["mission_success"])
            if r["difference"] not in ("", None):
                V[k + "_d"] = pts(r["difference"]); V[k + "_lo"] = pts(r["diff_lo"]); V[k + "_hi"] = pts(r["diff_hi"])
    p = os.path.join(S29, "c_degraded_held_out.csv")
    if os.path.exists(p):
        for r in read(p):
            V[key("pc", r["input"], r["map"])] = pc(r["mission_success"]); V[key("pc1", r["input"], r["map"])] = pc(r["mission_success"], 1)
    p = os.path.join(S29, "d_closed_loop_line_of_sight.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("los", r["layer"])
            V[k] = pc(r["success"]); V[k + "_unsafe"] = pc(r["unsafe"]); V[k + "_start"] = pc(r["stuck_at_start"])
            V[k + "_after"] = pc(r["stuck_after_replans"]); V[k + "_gaveup"] = pc(r["gave_up"]); V[k + "_replans"] = f"{float(r['replans']):.0f}"
            if r.get("diff_vs_slip_only", "") not in ("", None):
                V[k + "_d"] = pts(r["diff_vs_slip_only"]); V[k + "_lo"] = pts(r["diff_lo"]); V[k + "_hi"] = pts(r["diff_hi"])
                V[k + "_sitespos"] = WORDS[int(r["sites_positive"])]
    p = os.path.join(S29, "g_closed_loop_failures_radius.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("fb", r["endpoints"], r["input"], r["layer"])
            for c in ("pairs", "reached", "stuck_at_start", "stuck_after_replans", "gave_up", "unsafe"):
                V[k + "_" + c.replace("_", "")] = r[c]
    p = os.path.join(S29, "e_survey_coverage.csv")
    if os.path.exists(p):
        E = read(p)
        for m in ("2", "5"):
            v = [float(r["face_posts_covered"]) for r in E if r["survey_m"] == m]
            V[f"cov{m}_min"], V[f"cov{m}_max"] = pc(min(v)), pc(max(v))
            V[f"cov{m}_below60"] = WORDS[sum(x < 0.6 for x in v)]
    p = os.path.join(S29, "f_glo30_migration.csv")
    if os.path.exists(p):
        for r in read(p):
            a = "det" if r["analysis"].startswith("detection") else ("plI30" if "I30" in r["analysis"] else "plG30")
            fmt = f2 if a == "det" else pc
            V[key("mig", a, r["layer"], "still")] = fmt(r["sites_without_shift"]); V[key("mig", a, r["layer"], "other")] = fmt(r["other_sites"])
    # stage 30, post hoc checks after the third review
    p = os.path.join(S30, "a_closed_loop_line_of_sight.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("lo", r["input"], r["endpoints"], r["layer"], "p" + r["p_detect"].replace(".", ""))
            V[k] = pc(r["success"]); V[k + "_unsafe"] = pc(r["unsafe"]); V[k + "_replans"] = f"{float(r['replans']):.0f}"
            V[k + "_start"] = pc(r["stuck_at_start"]); V[k + "_after"] = pc(r["stuck_after_replans"]); V[k + "_gaveup"] = pc(r["gave_up"])
            if r["diff_vs_slip_only"] not in ("", None):
                V[k + "_d"] = pts(r["diff_vs_slip_only"]); V[k + "_lo"] = pts(r["diff_lo"]); V[k + "_hi"] = pts(r["diff_hi"])
                V[k + "_sitespos"] = WORDS[int(r["sites_positive"])]
    p = os.path.join(S30, "b_vehicle_exposure_labels.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("vb", r["endpoints"], r["input"], r["layer"])
            for c in ("mission_success", "vehicle_success", "success_H", "success_M", "success_L60"):
                V[k + "_" + c.replace("_", "")] = pc(r[c])
            V[k + "_feas"] = pc(r["feasible_share_of_successes"]); V[k + "_infeas"] = pc(1 - float(r["feasible_share_of_successes"]))
            V[k + "_facekm"] = f"{rnd(float(r['face_m_per_km']), 1):.1f}"; V[k + "_entkm"] = f"{rnd(float(r['entries_per_km']), 1):.1f}"
        B_ = {(r["endpoints"], r["input"], r["layer"]): r for r in read(p)}
        comp = [float(B_[("E1", "I30", l)]["vehicle_success"]) for l in ("DET", "BICUBIC-cal", "GBM", "DEM+S2") if ("E1", "I30", l) in B_]
        V["vb_E1_I30_maxcomp"] = pc(max(comp))
        for e in ("E1", "E2"):
            for inp in ("I10", "I30"):
                for c in ("success_L60", "vehicle_success"):
                    for lay in ("BICUBIC-cal", "FACEMAP", "GBM", "DEM+S2", "DET"):
                        if (e, inp, lay) in B_:
                            V[key("vbd", e, inp, lay, c.replace("_", ""))] = pts(round(float(B_[(e, inp, lay)][c]) - float(B_[(e, inp, "none")][c]), 6))
    p = os.path.join(S30, "b_label_stats.csv")
    if os.path.exists(p):
        for r in read(p):
            V[key("lab30", r["label"], "shortcount")] = pc(r["short_share_count"]); V[key("lab30", r["label"], "shortarea")] = pc(r["short_share_area"])
            V[key("lab30", r["label"], "n")] = f"{int(r['patches']):,}".replace(",", "\\,")
    p = os.path.join(S30, "b_detection_robust_labels.csv")
    if os.path.exists(p):
        for r in read(p):
            V[key("rl", r["label"], r["method"])] = f2(r["auc"])
    p = os.path.join(S30, "c_glo30_shift_detection.csv")
    if os.path.exists(p):
        for r in read(p):
            V[key("gs", r["input"], r["method"])] = f2(r["auc"])
    p = os.path.join(S30, "c_glo30_shift_planning.csv")
    if os.path.exists(p):
        for r in read(p):
            V[key("gsp", r["input"], r["layer"])] = pc(r["mission_success"])
    p = os.path.join(S30, "d_extended_weight_grid.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("xw", r["endpoints"], r["input"], r["layer"])
            V[k] = pc(r["weight_only_up_to_1000"]); V[k + "_100"] = pc(r["weight_only_up_to_100"]); V[k + "_1"] = pc(r["weight_only_up_to_1000"], 1)
            if r["registered_both_policies"] != "":
                V[k + "_up"] = pts(round(float(r["weight_only_up_to_1000"]) - float(r["registered_both_policies"]), 6))
        X = [r for r in read(p) if r["registered_both_policies"] != "" and r["layer"] != "FACEMAP"]
        for inp in ("I10", "I30", "G30"):
            V[f"xw_{inp}_maxup"] = pts(max(float(r["weight_only_up_to_1000"]) - float(r["registered_both_policies"]) for r in X if r["input"] == inp))
    p = os.path.join(S30, "e_imagery_cnn_detection.csv")
    if os.path.exists(p):
        for r in read(p):
            V[key("im", r["method"])] = f2(r["auc"])
    p = os.path.join(S30, "e_imagery_cnn_planning.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("imp", r["endpoints"], r["layer"])
            V[k] = pc(r["mission_success"]); V[k + "_d"] = pts(r["difference"]); V[k + "_lo"] = pts(r["diff_lo"]); V[k + "_hi"] = pts(r["diff_hi"])
    values31(V)
    # prediction log tallies (stages 25 to 28)
    reg = open(os.path.join(ROOT, "docs", "PREDICTIONS.md"), encoding="utf-8").read()
    outs = re.findall(r"^\| (?:B25|P26|D27|P28)-\d+ \|[^\n]*\| (HIT|MISSED)\b", reg, flags=re.M)
    V["log_n"] = str(len(outs)); V["log_hit"] = str(outs.count("HIT")); V["log_missed"] = str(outs.count("MISSED"))
    for k in ("log_n", "log_hit", "log_missed"):
        V[k + "_word"] = WORDS.get(int(V[k]), V[k])
    return V


def ci_pts(lo, hi):
    return f"{pts(lo)} to {pts(hi)}"


def values31(V):
    """Stage 31, post hoc checks after the fourth review."""
    p = os.path.join(S31, "c_vehicle_all_cells.csv")
    if os.path.exists(p):
        C = read(p)
        for r in C:
            k = key("vc", r["endpoints"], r["input"], r["layer"])
            V[k + "_m"] = pc(r["mission_success"]); V[k + "_v"] = pc(r["vehicle_success"]); V[k + "_feas"] = pc(r["feasible_share_of_successes"])
            for m in ("P300", "L60", "H", "M"):
                V[k + "_" + m] = pc(r[f"success_{m}"])
                b = next((x for x in C if x["endpoints"] == r["endpoints"] and x["input"] == r["input"] and x["layer"] == "none"), None)
                if b is not None and r["layer"] != "none":
                    V[k + "_" + m + "d"] = pts(round(float(r[f"success_{m}"]) - float(b[f"success_{m}"]), 6))
            for e in ("mission", "vehicle"):
                if r[f"{e}_site_lo"] != "":
                    V[k + f"_{e[0]}d"] = pts(r[f"{e}_diff"]); V[k + f"_{e[0]}ci"] = ci_pts(r[f"{e}_site_lo"], r[f"{e}_site_hi"])
                    V[k + f"_{e[0]}pos"] = WORDS[int(r[f"{e}_sites_positive"])]
        comp = ("SLOPE-cal", "BICUBIC-cal", "DET", "GBM", "CNN", "DEM+S2")
        for e in ("E1", "E2"):
            for inp in ("I10", "I30", "G30"):
                rr = [r for r in C if r["endpoints"] == e and r["input"] == inp and r["layer"] in comp]
                if rr:
                    V[key("vc", e, inp, "maxcomp", "vd")] = pts(max(float(r["vehicle_diff"]) for r in rr))
                    V[key("vc", e, inp, "maxcomp", "md")] = pts(max(float(r["mission_diff"]) for r in rr))
                    V[key("vc", e, inp, "maxcomp", "v")] = pc(max(float(r["vehicle_success"]) for r in rr))
                    V[key("vc", e, inp, "maxcomp", "md1")] = f"{rnd100(max(float(r['mission_diff']) for r in rr), 1):.1f}"
                    V[key("vc", e, inp, "maxcomp", "vd1")] = f"{rnd100(max(float(r['vehicle_diff']) for r in rr), 1):.1f}"
                    V[key("vc", e, inp, "maxcomp", "mdlay")] = max(rr, key=lambda r: float(r["mission_diff"]))["layer"]
        ci_ex = [r for r in C if r["layer"] in comp and r["mission_site_lo"] != "" and float(r["mission_site_lo"]) > 0]
        V["vc_I30_E1_mci_exclude"] = WORDS[sum(r["input"] == "I30" and r["endpoints"] == "E1" for r in ci_ex)]
    p = os.path.join(S31, "c_by_pair_distance.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("tt", r["endpoints"], r["input"], r["layer"], r["tertile"])
            V[k] = pc(r["mission_success"]); V[k + "_v"] = pc(r["vehicle_success"])
            V[key("tt", r["endpoints"], "edge", r["tertile"])] = f"{float(r['from_m']) / 1000:.1f}"
    p = os.path.join(S31, "c_route_overlap.csv")
    if os.path.exists(p):
        O = read(p)
        V["ov_min"], V["ov_max"] = pc(min(float(r["share_of_cells_shared"]) for r in O)), pc(max(float(r["share_of_cells_shared"]) for r in O))
        V["jac_max"] = f2(max(float(r["mean_pairwise_jaccard"]) for r in O))
    p = os.path.join(S31, "e_products_detection.csv")
    if os.path.exists(p):
        for r in read(p):
            V[key("pr", r["input"], r["method"])] = f2(r["auc"]); V[key("pr3", r["input"], r["method"])] = f"{rnd(float(r['auc']), 3):.3f}"
    p = os.path.join(S30, "c_glo30_shift_detection.csv")
    if os.path.exists(p):
        for r in read(p):
            V[key("gs3", r["input"], r["method"])] = f"{rnd(float(r['auc']), 3):.3f}"
    p = os.path.join(S31, "e_products_planning.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("prp", r["input"], r["layer"])
            V[k] = pc(r["mission_success"]); V[k + "_v"] = pc(r["vehicle_success"])
    p = os.path.join(S31, "c_vehicle_all_cells.csv")
    if os.path.exists(p):           # largest 30 m gain of a computable layer, registered grid or weights up to 1000
        comp = ("SLOPE-cal", "BICUBIC-cal", "DET", "GBM", "CNN", "DEM+S2")
        g = [float(r["mission_diff"]) for r in read(p) if r["endpoints"] == "E1" and r["input"] == "I30" and r["layer"] in comp]
        base = next(float(r["mission_success"]) for r in read(p) if r["endpoints"] == "E1" and r["input"] == "I30" and r["layer"] == "none")
        g += [float(r["weight_only_up_to_1000"]) - base for r in read(os.path.join(S30, "d_extended_weight_grid.csv"))
              if r["endpoints"] == "E1" and r["input"] == "I30" and r["layer"] in comp]
        V["i30_maxgain_any1"] = f"{rnd100(max(g), 1):.1f}"
    if "vc_E1_G30_maxcomp_md1" in V and os.path.exists(os.path.join(S31, "e_products_planning.csv")):
        P = {(r["input"], r["layer"]): float(r["mission_success"]) for r in read(os.path.join(S31, "e_products_planning.csv"))}
        g30 = {(r["input"], r["layer"]): float(r["mission_success"]) for r in read(os.path.join(S30, "c_glo30_shift_planning.csv"))}
        cands = [float(V["vc_E1_G30_maxcomp_md1"]) / 100, P[("A30", "BICUBIC-cal")] - P[("A30", "none")], P[("F30", "BICUBIC-cal")] - P[("F30", "none")],
                 g30[("G30", "BICUBIC-cal")] - g30[("G30", "none")]]
        V["real30_max_md1"] = f"{rnd100(max(cands), 1):.1f}"
        for pn in ("A30", "F30"):
            V[key("prp", pn, "d1")] = f"{rnd100((P[(pn, 'BICUBIC-cal')] - P[(pn, 'none')]), 1):.1f}"
    p = os.path.join(S31, "f_unet_detection.csv")
    if os.path.exists(p):
        for r in read(p):
            V["un_auc"] = f2(r["auc"])
    p = os.path.join(S31, "f_unet_planning.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("unp", r["endpoints"])
            V[k] = pc(r["mission_success"]); V[k + "_v"] = pc(r["vehicle_success"]); V[k + "_base"] = pc(r["slip_only"])
            V[k + "_d"] = pts(r["diff"]); V[k + "_ci"] = ci_pts(r["site_lo"], r["site_hi"])
    p = os.path.join(S31, "a_sensor_variants.csv")
    if os.path.exists(p):
        for r in read(p):
            if r["success"] == "":
                continue
            k = key("sv", r["variant"].split()[0] if r["variant"].startswith(("registered", "stage")) else r["variant"], r["layer"])
            if r["variant"].startswith("stage 30"):
                k = key("sv", "pair08", r["layer"])
            V[k] = pc(r["success"])
            if r["site_lo"] != "" and r["layer"] != "none":
                V[k + "_d"] = pts(r["diff"]); V[k + "_ci"] = ci_pts(r["site_lo"], r["site_hi"]); V[k + "_pos"] = WORDS[int(r["sites_positive"])]
            for c in ("unsafe", "gave_up", "stuck"):
                if r.get(c, "") not in ("", None):
                    V[k + "_" + c.replace("_", "")] = pc(r[c])
    p = os.path.join(S31, "b_closed_loop_held_out_weight.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("hw", r["input"], r["layer"])
            V[k] = pc(r["success"]); V[k + "_d"] = pts(r["diff"]); V[k + "_ci"] = ci_pts(r["site_lo"], r["site_hi"])
            V[k + "_chosen"] = ", ".join(sorted({c.split(":")[1] for c in r["chosen"].split()}, key=float))
            for w in (1, 5, 20, 100):
                if r.get(f"success_w{w}", "") != "":
                    V[k + f"_w{w}"] = pc(r[f"success_w{w}"])
    p = os.path.join(S31, "d_site_level_line_of_sight.csv")
    if os.path.exists(p):
        for r in read(p):
            k = key("sl", r["input"], r["endpoints"], r["layer"], "p" + r["p_detect"].replace(".", ""))
            if r["site_lo"] != "":
                V[k + "_ci"] = ci_pts(r["site_lo"], r["site_hi"]); V[k + "_d"] = pts(r["diff"])
                V[k + "_excl"] = "yes" if float(r["site_lo"]) > 0 else "no"
    p = os.path.join(S31, "d_detection_intervals_sr_dems2.csv")
    if os.path.exists(p):
        R = read(p)
        for m in ("SR", "DEM+S2"):
            rr = [r for r in R if r["method"] == m]
            V[key("di", m, "above")] = WORDS[sum(float(r["diff_lo"]) > 0 for r in rr)]
            V[key("di", m, "pos")] = WORDS[sum(float(r["diff_vs_bicubic"]) > 0 for r in rr)]
    p = os.path.join(S31, "g_grid_edges.csv")
    if os.path.exists(p):
        G = read(p)
        reg = [r for r in G if r["source"].startswith("stage 28") and r["layer"] not in ("none",)]
        V["edge_reg_share"] = pc(sum(int(r["sites_at_edge"]) for r in reg) / (6 * len(reg)))
        xw = [r for r in G if r["source"].startswith("stage 30")]
        V["edge_xw_share"] = pc(sum(int(r["sites_at_edge"]) for r in xw) / (6 * len(xw)))
    return V


# ---------------------------------------------------------------------------------------------------------------------
# tables
# ---------------------------------------------------------------------------------------------------------------------
def table_sites():
    meta = {r["site"]: r for r in read(os.path.join(BEN, "site_metadata.csv"))}
    A = read(os.path.join(S27, "A_metrics.csv"))
    pm = json.load(open(os.path.join(S27, "prepare_meta.json")))
    prev = lambda s, i: float(next(r for r in A if r["site"] == s and r["input"] == i)["prevalence"])
    L = [r"\begin{table}[t]", r"\caption{Lidar windows (USGS 3DEP one metre DEM; flown: acquisition period), face patches and the share of cells holding a face patch post at 10 and 30\,m.}",
         r"\label{tab:sites}", r"\centering\scriptsize", r"\setlength{\tabcolsep}{2.6pt}", r"\begin{tabular}{@{}lrrrrrrr@{}}", r"\toprule",
         r"Site & Lat., lon. & km$^2$ & Relief & Flown & Patches & 10\,m & 30\,m \\", r"\midrule"]
    for s in SITES:
        m = meta[s]
        y0, y1 = m["acquisition_start"][:4], m["acquisition_end"][:4]
        L.append(f"{SITE_LABEL[s]} & {float(m['centre_lat']):.2f}, {float(m['centre_lon']):.2f} & {float(m['area_km2']):.1f} & {float(m['relief_m']):.0f}\\,m & "
                 f"{y0 if y0 == y1 else y0 + ' to ' + y1[2:]} & {pm[s]['patches']} & {rnd100(prev(s, 'I10')):.0f}\\,\\% & {rnd100(prev(s, 'I30')):.0f}\\,\\% \\\\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


DET_ROWS = [("SLOPE", "Slope"), ("TRI", "Ruggedness"), ("ROUGH", "Roughness"), ("ASPECT", "Aspect rule"), ("BICUBIC", "Interpolation"),
            ("SR", "Super resolution$^{*}$"), ("DET", "Detector"), ("GBM", "Boosting$^{*}$"), ("GBM+", "Boosting+$^{*}$"),
            ("CNN", "Network$^{*}$"), ("CNN-long", "Network, 6000 steps$^{*}$"), ("IMG-S2", "Sentinel-2 only$^{*}$"), ("DEM+S2", "Boosting + Sentinel-2$^{*}$"),
            ("IMG-NAIP", "NAIP only$^{*}$"), ("DEM+NAIP", "Boosting + NAIP$^{*}$"),
            ("IMG-CNN-S2", "Sentinel-2 network$^{*\\ddagger}$"), ("IMG-CNN-NAIP", "NAIP network$^{*\\ddagger}$"), ("UNET", "U-Net$^{*\\ddagger}$")]
DET_COLS = [("I10", "I10"), ("I30", "I30"), ("I10to30", r"I10$\rightarrow$30"), ("R10", "R10"), ("N30", "N30"), ("G30n", "G30"), ("A30", "A30$^{\\ddagger}$"), ("F30", "F30$^{\\ddagger}$")]


def table_detection():
    D = det_rows()
    mean = {}
    for r in D:
        mean.setdefault((r["input"], r["method"]), []).append(float(r["auc"]))
    best = {c: f2(max(np.mean(v) for (i, m), v in mean.items() if i == c)) for c, _ in DET_COLS if any(i == c for i, _ in mean)}
    g30i = {r["method"]: f2(r["auc"]) for f in ("A_macro.csv", "F_macro.csv") for r in read(os.path.join(S27, f)) if r["input"] == "G30" and r["label"] == "L-ANY" and r["method"] in ("CNN", "SR")}
    L = [r"\begin{table}[t]", r"\caption{Detection of the face map label of Eq.~(\ref{eq:label}): mean AUC over the six sites. I: lidar block means; I10$\rightarrow$30: the largest of the nine 10\,m scores in each 30\,m cell; R10: USGS 1/3 arc second DEM, made by USGS from the same lidar at all six sites; N30: NASADEM; G30: GLO-30; R10, N30 and G30 on their own grids, where the networks and super resolution were not run (on GLO-30 interpolated to the 30\,m lidar grid they reach " + g30i["CNN"] + " and " + g30i["SR"] + r"); A30: AW3D30 and F30: FABDEM, interpolated to the 30\,m lidar grid. Ruggedness and roughness (I30 " + f2(np.mean(mean[("I30", "TRI")])) + " and " + f2(np.mean(mean[("I30", "ROUGH")])) + r"): supplement Table~S5. $^{*}$Trained on the lidar of the other five sites. $^{\ddagger}$Post hoc. Best per column in bold (ties at two decimals all bold); $\cdot$ not run.}",
         r"\label{tab:detection}", r"\centering\scriptsize", r"\setlength{\tabcolsep}{2.8pt}", r"\begin{tabular}{@{}l" + "c" * len(DET_COLS) + r"@{}}", r"\toprule",
         "Layer & " + " & ".join(h for _, h in DET_COLS) + r" \\", r"\midrule"]
    for m, lab in DET_ROWS:
        if m in ("TRI", "ROUGH"):
            continue                      # in the supplement (Table S5)
        cells = []
        for c, _ in DET_COLS:
            v = mean.get((c, m))
            if v is None:
                cells.append(NA)
            else:
                s = f2(np.mean(v))
                cells.append(f"\\textbf{{{s}}}" if best.get(c) == s else s)
        if all(x == NA for x in cells):
            continue
        L.append(f"{lab} & " + " & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


PLAN_LAYERS = [("none", "Slip model only"), ("SLOPE-cal", "Slope"), ("BICUBIC-cal", "Interpolation"), ("DET", "Detector"),
               ("GBM", "Boosting$^{*}$"), ("CNN", "Network$^{*}$"), ("DEM+S2", "Boosting + Sentinel-2$^{*}$"), ("FACEMAP", "Face map (oracle)")]
PLAN_COLS = [("E1", "I10"), ("E2", "I10"), ("E1", "I30"), ("E2", "I30"), ("E1", "G30")]
DEGRADED = [("FACEMAP", "Face map, $w=5$"), ("shift5", "Face map 5\\,m off"), ("shift10", "Face map 10\\,m off"), ("shift30", "Face map 30\\,m off"),
            ("survey2", "Face map from 2\\,m survey"), ("survey5", "Face map from 5\\,m survey")]


def table_planning(degraded=False):
    if degraded:
        return table_degraded()
    p = os.path.join(S31, "c_vehicle_all_cells.csv")
    C = {(r["endpoints"], r["input"], r["layer"]): r for r in read(p)} if os.path.exists(p) else {}

    def cell(e, i, lay):
        r = C.get((e, i, lay))
        if r is None:
            return NA
        return f"{rnd100(float(r['mission_success'])):.0f}/{rnd100(float(r['vehicle_success'])):.0f}"
    L = [r"\begin{table}[t]", r"\caption{Mission success / vehicle success (\%; vehicle success post hoc) at the operating point chosen on the other five sites, 100 pairs per site, posterior vehicle. E1: endpoints chosen with the truth; E2: from the coarse map only. Site level intervals: supplement S6. $^{*}$Trained leave one site out.}",
         r"\label{tab:planning}", r"\centering\scriptsize", r"\setlength{\tabcolsep}{2.6pt}", r"\begin{tabular}{@{}lccccc@{}}", r"\toprule",
         r" & \multicolumn{2}{c}{I10} & \multicolumn{2}{c}{I30} & G30 \\", r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(l){6-6}", r"Layer & E1 & E2 & E1 & E2 & E1 \\", r"\midrule"]
    for lay, lab in PLAN_LAYERS:
        L.append(f"{lab} & " + " & ".join(cell(e, i, lay) for e, i in PLAN_COLS) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


def table_degraded():
    C = read(os.path.join(S28, "C_degraded.csv")) if os.path.exists(os.path.join(S28, "C_degraded.csv")) else []
    L = [r"\begin{table}[H]", r"\caption{Registered degraded face maps (stage 28), weight policy at a fixed $w=5$: mission success (\%), 100 pairs per site, posterior vehicle. The first row is the exact face map at the same weight; Table~III of the paper gives the face map at the weight chosen on the other five sites.}",
         r"\label{tab:planning_s}", r"\centering\small", r"\begin{tabular}{@{}lcccc@{}}", r"\toprule",
         r" & \multicolumn{2}{c}{I10} & \multicolumn{2}{c}{I30} \\", r"Face map & E1 & E2 & E1 & E2 \\", r"\midrule"]
    for mp, lab in DEGRADED:
        cells = []
        for e, i in PLAN_COLS[:4]:
            r = next((r for r in C if r["endpoints"] == e and r["input"] == i and r["map"] == mp and r["policy"] == "risk_weighted"), None)
            cells.append(f"{rnd100(float(r['mission_success'])):.0f}" if r else NA)
        L.append(f"{lab} & " + " & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


def _cidisp(r, e):
    if r is None or r.get(f"{e}_site_lo", "") == "":
        return NA
    return f"{pts(r[f'{e}_diff'])} ({pts(r[f'{e}_site_lo'])}, {pts(r[f'{e}_site_hi'])})"


def table_site_level():
    p = os.path.join(S31, "c_vehicle_all_cells.csv")
    if not os.path.exists(p):
        return "% site level table not run yet"
    C = {(r["endpoints"], r["input"], r["layer"]): r for r in read(p)}
    cols = [("E1", "I10", "mission"), ("E1", "I10", "vehicle"), ("E1", "I30", "mission"), ("E1", "I30", "vehicle"), ("E2", "I30", "mission"), ("E1", "G30", "mission")]
    L = [r"\begin{table}[H]", r"\caption{Site level inference for Table~III of the paper: gain over the slip model alone in points, mean of the six per site differences, with a 95\,\% $t$ interval (five degrees of freedom; it can extend beyond the possible range). M: mission success; V: vehicle success.}",
         r"\label{tab:sitelevel}", r"\centering\scriptsize", r"\setlength{\tabcolsep}{3pt}", r"\begin{tabular}{@{}l" + "c" * len(cols) + r"@{}}", r"\toprule",
         "Layer & " + " & ".join(f"{i} {e} {m[0].upper()}" for e, i, m in cols) + r" \\", r"\midrule"]
    for lay, lab in PLAN_LAYERS:
        if lay == "none":
            continue
        L.append(f"{lab} & " + " & ".join(_cidisp(C.get((e, i, lay)), m) for e, i, m in cols) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


def table_labels():
    p = os.path.join(S31, "c_vehicle_all_cells.csv")
    if not os.path.exists(p):
        return "% label table not run yet"
    C = {(r["endpoints"], r["input"], r["layer"]): r for r in read(p)}
    labs = [("mission_success", "Registered"), ("success_P300", "P300"), ("success_L60", "L60"), ("success_H", "H"), ("success_M", "M")]
    L = [r"\begin{table}[H]", r"\caption{Mission success (\%) of the routes of Table~III of the paper (E1 endpoints) scored against other face rules: patches of at least 300 posts (P300), patches at least 60\,m long (L60), hysteresis patches (H) and patches merged across gaps of one post (M). The operating points stay those chosen for the registered rule.}",
         r"\label{tab:labels}", r"\centering\scriptsize", r"\setlength{\tabcolsep}{3pt}", r"\begin{tabular}{@{}l" + "c" * (2 * len(labs)) + r"@{}}", r"\toprule",
         r" & \multicolumn{" + str(len(labs)) + r"}{c}{I10} & \multicolumn{" + str(len(labs)) + r"}{c}{I30} \\",
         "Layer & " + " & ".join(h for _ in range(2) for _, h in labs) + r" \\", r"\midrule"]
    for lay, lab in PLAN_LAYERS:
        cells = []
        for i in ("I10", "I30"):
            r = C.get(("E1", i, lay))
            cells += [f"{rnd100(float(r[c])):.0f}" if r else NA for c, _ in labs]
        L.append(f"{lab} & " + " & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


def table_tertiles():
    p = os.path.join(S31, "c_by_pair_distance.csv")
    if not os.path.exists(p):
        return "% distance table not run yet"
    T = read(p)
    get = lambda e, i, lay, t: next((r for r in T if r["endpoints"] == e and r["input"] == i and r["layer"] == lay and r["tertile"] == str(t)), None)
    e1 = [r for r in T if r["endpoints"] == "E1" and r["input"] == "I30" and r["layer"] == "none"]
    edges = sorted({float(r["from_m"]) for r in e1})[1:]
    L = [r"\begin{table}[H]", r"\caption{Mission success / vehicle success (\%) by tertile of the straight distance of the pair (E1 endpoints, 200 pairs per tertile; edges " + f"{edges[0] / 1000:.1f} and {edges[1] / 1000:.1f}" + r"\,km).}",
         r"\label{tab:tertiles}", r"\centering\scriptsize", r"\begin{tabular}{@{}lcccccc@{}}", r"\toprule",
         r" & \multicolumn{3}{c}{I10} & \multicolumn{3}{c}{I30} \\", r"Layer & short & middle & long & short & middle & long \\", r"\midrule"]
    for lay, lab in (("none", "Slip model only"), ("BICUBIC-cal", "Interpolation"), ("FACEMAP", "Face map (oracle)")):
        cells = []
        for i in ("I10", "I30"):
            for t in (1, 2, 3):
                r = get("E1", i, lay, t)
                cells.append(f"{rnd100(float(r['mission_success'])):.0f}/{rnd100(float(r['vehicle_success'])):.0f}" if r else NA)
        L.append(f"{lab} & " + " & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


def table_cl_variants():
    p = os.path.join(S31, "a_sensor_variants.csv")
    if not os.path.exists(p):
        return "% sensor variants not run yet"
    A = read(p)
    H = read(os.path.join(S31, "b_closed_loop_held_out_weight.csv")) if os.path.exists(os.path.join(S31, "b_closed_loop_held_out_weight.csv")) else []
    cols = [("registered eye 1 m", "Eye 1\\,m"), ("eye0.5", "Eye 0.5\\,m"), ("eye1.5", "Eye 1.5\\,m"), ("noise0.05", "Noise 0.05\\,m"), ("noise0.15", "Noise 0.15\\,m"),
            ("stage 30 p 0.8 once per pair", "$p_d$ 0.8, pair"), ("obs0.8", "$p_d$ 0.8, view")]

    def g(v, lay):
        r = next((r for r in A if r["variant"] == v and r["layer"] == lay), None)
        return f"{rnd100(float(r['success'])):.0f}" if r and r["success"] != "" else NA

    def hw(i, lay):
        r = next((r for r in H if r["input"] == i and r["layer"] == lay), None)
        return f"{rnd100(float(r['success'])):.0f}" if r else NA
    L = [r"\begin{table}[H]", r"\caption{Line of sight closed loop on I30 (E1 endpoints, 20 pairs per site, $R=20$\,m) under sensor variants (post hoc): success (\%). Eye: height of the sensor above the ground. Noise: standard deviation of the noise added to every lidar post before the rover's face patches are computed. $p_d$ 0.8: each face cell is detected with probability 0.8, drawn once per pair (pair) or at every view (view). All at $w=5$; last columns: weight chosen on the other five sites from $\{1,5,20,100\}$, on I30 and on I10.}",
         r"\label{tab:clvariants}", r"\centering\scriptsize", r"\setlength{\tabcolsep}{2.6pt}", r"\begin{tabular}{@{}l" + "c" * (len(cols) + 2) + r"@{}}", r"\toprule",
         "Prior layer & " + " & ".join(h for _, h in cols) + r" & Held out $w$ & I10, held out $w$ \\", r"\midrule"]
    for lay, lab in (("none", "Slip model only"), ("BICUBIC-cal", "Interpolation"), ("GBM", "Boosting$^{*}$"), ("FACEMAP", "Face map (oracle)")):
        hcell = NA if lay == "none" else hw("I30", lay)
        h10 = NA if lay in ("none", "GBM") else hw("I10", lay)
        L.append(f"{lab} & " + " & ".join(g(v, lay) for v, _ in cols) + f" & {hcell} & {h10} \\\\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


def table_los_site_level():
    p = os.path.join(S31, "d_site_level_line_of_sight.csv")
    if not os.path.exists(p):
        return "% not run yet"
    R = read(p)
    cols = [("I30", "E1", "1.0", "I30, E1"), ("I30", "E2", "1.0", "I30, E2"), ("I30", "E1", "0.8", "I30, E1, $p_d$ 0.8"), ("I10", "E1", "1.0", "I10, E1")]

    def g(i, e, pd, lay):
        r = next((r for r in R if r["input"] == i and r["endpoints"] == e and r["p_detect"] == pd and r["layer"] == lay), None)
        return f"{pts(r['diff'])} ({pts(r['site_lo'])}, {pts(r['site_hi'])})" if r and r["site_lo"] != "" else NA
    L = [r"\begin{table}[H]", r"\caption{Line of sight closed loop of Table~IV of the paper: gain over the slip model prior in points, mean of the six per site differences with a 95\,\% $t$ interval (five degrees of freedom).}",
         r"\label{tab:lossite}", r"\centering\scriptsize", r"\begin{tabular}{@{}lcccc@{}}", r"\toprule", "Prior layer & " + " & ".join(c[3] for c in cols) + r" \\", r"\midrule"]
    for lay, lab in LOS_LAYERS:
        if lay == "none":
            continue
        L.append(f"{lab} & " + " & ".join(g(i, e, pd, lay) for i, e, pd, _ in cols) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


def table_products():
    p = os.path.join(S31, "e_products_detection.csv")
    if not os.path.exists(p):
        return "% products not run yet"
    D = {(r["input"], r["method"]): r for r in read(p)}
    D.update({(r["input"], r["method"]): r for r in read(os.path.join(S30, "c_glo30_shift_detection.csv"))})
    P = {(r["input"], r["layer"]): r for r in read(os.path.join(S31, "e_products_planning.csv"))} if os.path.exists(os.path.join(S31, "e_products_planning.csv")) else {}
    G = {(r["input"], r["layer"]): r for r in read(os.path.join(S30, "c_glo30_shift_planning.csv"))}
    L = [r"\begin{table}[H]", r"\caption{Real 30\,m products interpolated to the 30\,m lidar grid (post hoc for A30 and F30): mean AUC against the face map label, and mission success / vehicle success (\%) on E1 with the weight chosen on the other five sites from $\{1,\dots,1000\}$. G30: GLO-30 (vehicle success not scored on this grid); A30: AW3D30 (optical stereo surface model); F30: FABDEM (GLO-30 with forest and buildings removed). Boosting is trained on the other five sites.}",
         r"\label{tab:products}", r"\centering\scriptsize", r"\begin{tabular}{@{}lcccccc@{}}", r"\toprule",
         r" & \multicolumn{4}{c}{AUC} & \multicolumn{2}{c}{Success} \\", r"\cmidrule(lr){2-5}\cmidrule(l){6-7}",
         r"Product & Slope & Interp. & Detector & Boosting & Slip only & Interp. \\", r"\midrule"]
    g25 = [float(r["auc"]) for r in read(os.path.join(S27, "A_metrics.csv")) if r["input"] == "G30" and r["method"] == "GBM"]
    if g25:
        D[("G30", "GBM")] = {"auc": float(np.mean(g25))}
    for inp, lab in (("G30", "G30"), ("A30", "A30"), ("F30", "F30")):
        aucs = [f2(D[(inp, m)]["auc"]) if (inp, m) in D else NA for m in ("SLOPE", "BICUBIC", "DET", "GBM")]
        if inp == "G30":
            pl = [f"{rnd100(float(G[(inp, l)]['mission_success'])):.0f}/$\\cdot$" if (inp, l) in G else NA for l in ("none", "BICUBIC-cal")]
        else:
            pl = [f"{rnd100(float(P[(inp, l)]['mission_success'])):.0f}/{rnd100(float(P[(inp, l)]['vehicle_success'])):.0f}" if (inp, l) in P else NA for l in ("none", "BICUBIC-cal")]
        L.append(f"{lab} & " + " & ".join(aucs + pl) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


def table_sensitivity():
    H = read(os.path.join(S28, "A_held_out.csv")); N = read(os.path.join(S28, "A_naive.csv"))
    cols = [("E1", "I10"), ("E1", "I30"), ("E1", "G30")]

    def g(prof, e, i, lay):
        if lay == "none":
            r = next((r for r in N if r["profile"] == prof and r["endpoints"] == e and r["input"] == i), None)
        else:
            r = next((r for r in H if r["profile"] == prof and r["endpoints"] == e and r["input"] == i and r["layer"] == lay and r["policies"] == "conservative+risk_weighted"), None)
        return f"{rnd100(float(r['mission_success'])):.0f}" if r else NA
    L = [r"\begin{table}[H]", r"\caption{Mission success (\%) with the posterior vehicle (P) and the sensitivity vehicle with narrower assumed ranges (A), E1 endpoints, operating point chosen on the other five sites.}",
         r"\label{tab:sensitivity}", r"\centering\scriptsize", r"\begin{tabular}{@{}lcccccc@{}}", r"\toprule",
         r" & \multicolumn{2}{c}{I10} & \multicolumn{2}{c}{I30} & \multicolumn{2}{c}{G30} \\", r"Layer & P & A & P & A & P & A \\", r"\midrule"]
    for lay, lab in PLAN_LAYERS:
        if lay == "DEM+S2":
            continue
        L.append(f"{lab} & " + " & ".join(g(pf, e, i, lay) for e, i in cols for pf in ("published-posterior", "assumed")) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


def table_dates():
    meta = {r["site"]: r for r in read(os.path.join(BEN, "site_metadata.csv"))}
    L = [r"\begin{table}[H]", r"\caption{Lidar projects and acquisition dates, and the dates of the other inputs. NASADEM is from February 2000 and GLO-30 from radar acquisitions of 2011 to 2015 at every site (the copyright years of the licence statement, 2010 to 2014, are not acquisition dates).}",
         r"\label{tab:dates}", r"\centering\scriptsize", r"\begin{tabular}{@{}llccc@{}}", r"\toprule",
         r"Site & Lidar project & Lidar flown & Sentinel-2 & NAIP \\", r"\midrule"]
    for s in SITES:
        m = meta[s]
        a, b = m["acquisition_start"], m["acquisition_end"]
        fl = a if a == b else f"{a} to {b}"
        L.append(f"{SITE_LABEL[s].split(',')[0]} & {_esc(m['lidar_project'])} & {fl} & {m['sentinel2_date']} & {m['naip_year']} \\\\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


CL_LAYERS = [("none", "Slip model only"), ("DET", "Detector"), ("BICUBIC-cal", "Interpolation"), ("GBM", "Boosting$^{*}$"), ("FACEMAP", "Face map")]


def table_closed_loop():
    p = os.path.join(S28, "E_closed_loop.csv")
    if not os.path.exists(p):
        return "% closed loop not run yet"
    E = read(p)

    def g(e, i, lay, R, k):
        r = next((r for r in E if r["profile"] == "published-posterior" and r["endpoints"] == e and r["input"] == i and r["layer"] == lay and float(r["radius_m"]) == R), None)
        if r is None or r.get(k, "") == "":
            return NA
        return f"{rnd100(float(r[k])):.0f}" if k in ("success", "stuck") else f"{rnd(float(r[k])):.0f}"
    L = [r"\begin{table}[H]", r"\caption{Registered closed loop with an idealised sensor (radius $R$), 20 pairs per site, posterior vehicle, sensing every face within the radius: success S (\%; goal reached, no face contact) and replans per pair Rp. Main runs $R=20$\,m; I30 also with E2 endpoints and with $R=10$ and 30\,m.}",
         r"\label{tab:closedloop_ideal}", r"\centering\scriptsize", r"\setlength{\tabcolsep}{2.4pt}", r"\begin{tabular}{@{}lccccccc@{}}", r"\toprule",
         r" & \multicolumn{2}{c}{I10, E1, $R$ 20} & \multicolumn{2}{c}{I30, E1, $R$ 20} & I30, E2 & \multicolumn{2}{c}{I30, E1} \\",
         r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-6}\cmidrule(l){7-8}",
         r"Prior layer & S & Rp & S & Rp & S, $R$ 20 & S, $R$ 10 & S, $R$ 30 \\", r"\midrule"]
    for lay, lab in CL_LAYERS:
        L.append(f"{lab} & {g('E1', 'I10', lay, 20.0, 'success')} & {g('E1', 'I10', lay, 20.0, 'replans')} & "
                 f"{g('E1', 'I30', lay, 20.0, 'success')} & {g('E1', 'I30', lay, 20.0, 'replans')} & "
                 f"{g('E2', 'I30', lay, 20.0, 'success')} & {g('E1', 'I30', lay, 10.0, 'success')} & {g('E1', 'I30', lay, 30.0, 'success')} \\\\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


LOS_LAYERS = [("none", "Slip model only"), ("DET", "Detector"), ("BICUBIC-cal", "Interpolation"), ("GBM", "Boosting$^{*}$"),
              ("DEM+S2", "Boosting + Sentinel-2$^{*}$"), ("SR-cal", "Super resolution$^{*}$"), ("CNN-long", "Network, 6000 steps$^{*}$"),
              ("FACEMAP", "Face map (oracle)")]


def table_closed_loop_los():
    p = os.path.join(S30, "a_closed_loop_line_of_sight.csv")
    if not os.path.exists(p):
        return "% line of sight closed loop not run yet"
    A = read(p)
    E = read(os.path.join(S28, "E_closed_loop.csv"))

    def g(inp, e, lay, pd):
        r = next((r for r in A if r["input"] == inp and r["endpoints"] == e and r["layer"] == lay and float(r["p_detect"]) == pd), None)
        if r is None:
            return NA
        return f"{rnd100(float(r['success'])):.0f}"

    def ideal(lay):
        r = next((r for r in E if r["profile"] == "published-posterior" and r["endpoints"] == "E1" and r["input"] == "I30" and r["layer"] == lay and float(r["radius_m"]) == 20.0), None)
        return f"{rnd100(float(r['success'])):.0f}" if r else NA
    L = [r"\begin{table}[t]", r"\caption{Exploratory closed loop, sensing within 20\,m (post hoc except the last column), 20 pairs per site, $w=5$: success (\%; goal reached, no face touched). Line of sight: eye 1\,m above the ground; $p_d=0.8$: each face cell detectable with probability 0.8. Ideal: the registered sensor that sees every face. Intervals and sensor variants: supplement S6. $^{*}$Trained leave one site out.}",
         r"\label{tab:closedloop}", r"\centering\scriptsize", r"\setlength{\tabcolsep}{2.6pt}", r"\begin{tabular}{@{}lccccc@{}}", r"\toprule",
         r" & \multicolumn{4}{c}{Line of sight} & Ideal \\", r"\cmidrule(lr){2-5}\cmidrule(l){6-6}",
         r" & \multicolumn{3}{c}{I30} & I10 & I30 \\", r"\cmidrule(lr){2-4}\cmidrule(lr){5-5}\cmidrule(l){6-6}",
         r"Prior layer & E1 & E2 & E1, $p_d$ 0.8 & E1 & E1 \\", r"\midrule"]
    for lay, lab in LOS_LAYERS:
        L.append(f"{lab} & {g('I30', 'E1', lay, 1.0)} & {g('I30', 'E2', lay, 1.0)} & {g('I30', 'E1', lay, 0.8)} & {g('I10', 'E1', lay, 1.0)} & {ideal(lay)} \\\\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


# ---------------------------------------------------------------------------------------------------------------------
# supplement tables
# ---------------------------------------------------------------------------------------------------------------------
def tex_escape(s):
    parts = re.split(r"(`[^`]*`)", s)
    return "".join(r"\url{" + p[1:-1] + "}" if p.startswith("`") else _esc(p) for p in parts)


def _esc(s):
    s = s.replace("\\", "/").replace("%", "\\%").replace("&", "\\&").replace("#", "\\#").replace("_", "\\_")
    s = s.replace("**", "").replace(">=", "$\\geq$").replace("<=", "$\\leq$").replace("x 300", "$\\times$ 300")
    s = s.replace("≥", "$\\geq$").replace("≤", "$\\leq$").replace("×", "$\\times$").replace("→", "$\\rightarrow$")
    return s


def table_log():
    reg = open(os.path.join(ROOT, "docs", "PREDICTIONS.md"), encoding="utf-8").read()
    rows = re.findall(r"^\| ((?:B25|P26|D27|P28|X29|Y30|Z31)-\d+) \| ([^|\n]*) \| ([^\n]*)\|\s*$", reg, flags=re.M)
    L = [r"\begin{longtable}{@{}p{0.08\linewidth}p{0.42\linewidth}p{0.46\linewidth}@{}}",
         r"\caption{Prediction log of stages 25 to 31: every prediction as committed before its run (verbatim) and the outcome as recorded afterwards. Stages 29 (X29), 30 (Y30) and 31 (Z31) are post hoc and not counted in the tally.}\label{tab:log}\\",
         r"\toprule", r"ID & Prediction (before the run) & Outcome \\", r"\midrule", r"\endhead"]
    for i, p, o in rows:
        L.append(f"{i} & {tex_escape(p.strip())} & {tex_escape(o.strip())} \\\\")
    L += [r"\bottomrule", r"\end{longtable}"]
    return "\n".join(L)


GLOSSARY = [("Slip face", "the lee face of a dune near the angle of repose; in this paper approximated by face patches"),
            ("Steep post", "a one metre lidar post with Horn slope of 28 degrees or more"),
            ("Face patch", "an 8 connected group of at least 10 steep posts (10 square metres)"),
            ("Face map label", "a cell is positive when it holds a face patch post (Eq. 1); L-ANY in the result files"),
            ("Cell label", "at least 10 steep posts in the cell, the label of the first version (L-CELL)"),
            ("I10, I30, I5", "block means of the lidar at 10, 30 and 5 m"),
            ("R10, N30", "USGS 1/3 arc second DEM and NASADEM on their own grids"),
            ("G30", "Copernicus GLO-30; on its own grid in the detection table (G30n in the files), interpolated to the 30 m lidar grid for planning"),
            ("Interpolation", "steepest slope after cubic spline interpolation to 1 m (BICUBIC; BICUBIC-cal when calibrated)"),
            ("Detector", "the synthetic subgrid detector of the planner (DET; DET-cal when recalibrated on the other sites)"),
            ("Boosting, network", "gradient boosted trees (GBM) and the dilated convolutional network (CNN)"),
            ("Slip model only", "the planner without a hazard layer (naive in the files)"),
            ("Gate, weight", "the conservative and risk weighted policies"),
            ("Face map (oracle)", "the face map label used as a hazard layer (FACEMAP, ORACLE-ANY); an oracle, not a bound"),
            ("Posterior vehicle", "the slip model with parameters drawn from a posterior fitted to published slip curves of other wheeled vehicles"),
            ("E1, E2", "endpoints chosen with the truth (centres of 30 m cells whose one metre posts are all valid and below 20 degrees, 25 degrees at a site with fewer than 200 such cells) and from the coarse map only (coarse slope below 15 degrees)"),
            ("Mission success", "a route exists and no sample of it lies on a face patch"),
            ("Vehicle success", "mission success and every 5 m step of the route climbable by the nominal posterior vehicle on the 5 m lidar block mean, with no descent of 28 degrees or more"),
            ("Slope, ruggedness, roughness, aspect rule", "SLOPE, TRI, ROUGH and ASPECT in the files; -cal: calibrated on the other five sites"),
            ("BICUBIC", "the file name of interpolation; the method is a cubic spline"),
            ("Super resolution", "SR (SR-cal when calibrated)"),
            ("Network, 6000 steps", "CNN-long; U-Net: UNET"),
            ("Boosting variants", "GBM+ (five more features), GBM-tuned (nested tuning), GBM-noDET (without the detector features)"),
            ("Imagery layers", "IMG-S2 and IMG-NAIP (imagery features only), DEM+S2 and DEM+NAIP (terrain plus imagery features), IMG-CNN-S2 and IMG-CNN-NAIP (pixel level networks on the imagery)"),
            ("A30, F30", "AW3D30 and FABDEM interpolated to the 30 m lidar grid"),
            ("SHORTEST, ORACLE-5", "stage 26 references: the shortest grid path without terrain, and the gate on the 5 m surface with every face cell marked"),
            ("P300, L60, H, M", "other face rules: patches of at least 300 posts, patches at least 60 m long, hysteresis patches and patches merged across one post gaps"),
            ("Exponential family", "the slip law of Eq. (2) (not the statistical exponential family)"),
            ("Stage, part", "one round of the prediction log (stages 25 to 31) and a lettered part of its design"),
            ("Crop margin", "the local grid of a closed loop run covers the bounding box of the pair plus this margin"),
            ("Blind review", "a critical review of the paper by a reader who had not seen the work being produced, used to decide the post hoc checks")]


def table_glossary():
    L = [r"\begin{table}[H]", r"\caption{Names used in the paper and in the result files.}", r"\label{tab:glossary}", r"\centering\small",
         r"\begin{tabular}{@{}lp{0.68\linewidth}@{}}", r"\toprule", r"Name & Meaning \\", r"\midrule"]
    L += [f"{a} & {b} \\\\" for a, b in GLOSSARY]
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


def table_spread():
    D = det_rows()
    vals = {}
    for r in D:
        vals.setdefault((r["input"], r["method"]), []).append(float(r["auc"]))
    cols = [c for c in DET_COLS if any(i == c[0] for i, _ in vals)]
    L = [r"\begin{table}[H]", r"\caption{Spread of the AUC across the six sites (lowest to highest) for each layer and input of Table~II of the paper.}",
         r"\label{tab:spread}", r"\centering\scriptsize", r"\begin{tabular}{@{}l" + "c" * len(cols) + r"@{}}", r"\toprule",
         "Layer & " + " & ".join(h for _, h in cols) + r" \\", r"\midrule"]
    for m, lab in DET_ROWS:
        cells = [f"{f2(min(vals[(c, m)]))} to {f2(max(vals[(c, m)]))}" if (c, m) in vals else NA for c, _ in cols]
        if all(x == NA for x in cells):
            continue
        L.append(f"{lab} & " + " & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


def table_persite():
    D = [r for r in read(os.path.join(S27, "A_metrics.csv")) if r["input"] == "I30"]
    E = [r for r in read(os.path.join(S27, "E_metrics.csv")) if r["input"] == "I30"]
    E += [r for r in read(os.path.join(S27, "F_metrics.csv")) if r["input"] == "I30" and r["method"] == "SR"]
    ms = [("SLOPE", "Slope"), ("BICUBIC", "Interp."), ("SR", "Super res."), ("DET", "Detector"), ("GBM", "Boosting"), ("CNN", "Network"), ("DEM+S2", "Boost.+S2")]
    dp = os.path.join(S31, "d_detection_intervals_sr_dems2.csv")
    DI = {(r["site"], r["method"]): r for r in read(dp)} if os.path.exists(dp) else {}
    L = [r"\begin{table}[H]", r"\caption{AUC per site on I30 (face map label), three decimals, with 95\,\% block bootstrap intervals (300\,m blocks). Paired intervals of super resolution and of boosting with Sentinel-2 against interpolation (post hoc) lie above zero at " + WORDS[sum(float(r["diff_lo"]) > 0 for r in DI.values() if r["method"] == "SR")] + " and " + WORDS[sum(float(r["diff_lo"]) > 0 for r in DI.values() if r["method"] == "DEM+S2")] + r" of the six sites.}", r"\label{tab:persite}",
         r"\centering\scriptsize", r"\setlength{\tabcolsep}{2.5pt}", r"\begin{tabular}{@{}l" + "c" * len(ms) + r"@{}}", r"\toprule",
         "Site & " + " & ".join(h for _, h in ms) + r" \\", r"\midrule"]
    for s in SITES:
        cells = []
        for m, _ in ms:
            r = next((r for r in D + E if r["site"] == s and r["method"] == m), None)
            if r is None:
                cells.append(NA); continue
            c = f"{rnd(r['auc'], 3):.3f}"
            di = DI.get((s, m))
            if r.get("auc_lo", ""):
                c += f" [{f2(r['auc_lo'])}, {f2(r['auc_hi'])}]"
            elif di:
                c += f" [{f2(di['lo'])}, {f2(di['hi'])}]"
            cells.append(c)
        L.append(f"{SITE_LABEL[s].split(',')[0]} & " + " & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


# ---------------------------------------------------------------------------------------------------------------------
# render and build
# ---------------------------------------------------------------------------------------------------------------------
TABLES = {"sites": table_sites, "methods": lambda: open(os.path.join(SRC, "table_methods.tex"), encoding="utf-8").read().strip(),
          "detection": table_detection, "planning": table_planning, "planning_degraded": table_degraded, "closedloop": table_closed_loop, "closedloop_los": table_closed_loop_los, "log": table_log, "persite": table_persite,
          "glossary": table_glossary, "sitelevel": table_site_level, "labels": table_labels, "tertiles": table_tertiles,
          "clvariants": table_cl_variants, "lossite": table_los_site_level, "products": table_products, "sensitivity": table_sensitivity, "dates": table_dates, "methods_supp": lambda: re.sub(r"~?\\cite\{[^}]*\}", "", open(os.path.join(SRC, "table_methods.tex"), encoding="utf-8").read().strip()).replace("\\begin{table}[t]", "\\begin{table}[H]").replace("tab:methods", "tab:methods_s"), "spread": table_spread}


def render(template, V) -> str:
    t = open(os.path.join(SRC, template), encoding="utf-8").read()
    for name in sorted(os.listdir(SRC)):
        if name.startswith("text_") and name.endswith(".tex"):
            body = open(os.path.join(SRC, name), encoding="utf-8").read().strip()
            t = t.replace("{{VAL:" + name[5:-4] + "}}", body)
    for name, fn in TABLES.items():
        if "{{TABLE:" + name + "}}" in t:
            t = t.replace("{{TABLE:" + name + "}}", fn())
    missing = []

    def sub(mo):
        k = mo.group(1)
        if k not in V:
            missing.append(k); return "??"
        return V[k]
    t = re.sub(r"\{\{VAL:([A-Za-z0-9_\-]+)\}\}", sub, t)
    if missing:
        raise SystemExit("missing values: " + ", ".join(sorted(set(missing))))
    return t


def latex(name):
    r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"], cwd=PAPER, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-3000:]); raise SystemExit(f"LaTeX failed on {name}")
    subprocess.run(["latexmk", "-c", f"{name}.tex"], cwd=PAPER, capture_output=True)
    log = r.stdout
    print(name, "pages:", re.findall(rf"Output written on {name}.pdf \((\d+) pages", log))


def main():
    check = "--check" in sys.argv
    V = values()
    docs = {"paper.tex": render("paper_template.tex", V), "supplement.tex": render("supplement_template.tex", V)}
    if check:
        for name, tex in docs.items():
            old = open(os.path.join(PAPER, name), encoding="utf-8").read() if os.path.exists(os.path.join(PAPER, name)) else ""
            if old != tex:
                raise SystemExit(f"paper/{name} is stale: run scripts/build_paper.py")
        print("paper: ok"); return
    for name, tex in docs.items():
        open(os.path.join(PAPER, name), "w", encoding="utf-8").write(tex)
    json.dump(V, open(os.path.join(PAPER, "values.json"), "w"), indent=0, sort_keys=True)
    if shutil.which("latexmk") and "--no-pdf" not in sys.argv:
        for name in docs:
            latex(name[:-4])
    print("wrote", ", ".join(docs))


if __name__ == "__main__":
    main()
