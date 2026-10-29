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


def f2(x):
    return f"{rnd(x, 2):.2f}"


def pc(x, nd=0):
    return f"{rnd(100 * float(x), nd):.{nd}f}\\,\\%"


def pts(x):
    v = rnd(100 * float(x), 0)
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
            V[k + "_dabs"] = f"{rnd(100 * abs(float(r['difference']))):.0f}"
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
            V[key("pc", r["input"], r["map"])] = pc(r["mission_success"])
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
    # prediction log tallies (stages 25 to 28)
    reg = open(os.path.join(ROOT, "docs", "PREDICTIONS.md"), encoding="utf-8").read()
    outs = re.findall(r"^\| (?:B25|P26|D27|P28)-\d+ \|[^\n]*\| (HIT|MISSED)\b", reg, flags=re.M)
    V["log_n"] = str(len(outs)); V["log_hit"] = str(outs.count("HIT")); V["log_missed"] = str(outs.count("MISSED"))
    for k in ("log_n", "log_hit", "log_missed"):
        V[k + "_word"] = WORDS.get(int(V[k]), V[k])
    return V


# ---------------------------------------------------------------------------------------------------------------------
# tables
# ---------------------------------------------------------------------------------------------------------------------
def table_sites():
    meta = {r["site"]: r for r in read(os.path.join(BEN, "site_metadata.csv"))}
    A = read(os.path.join(S27, "A_metrics.csv"))
    pm = json.load(open(os.path.join(S27, "prepare_meta.json")))
    prev = lambda s, i: float(next(r for r in A if r["site"] == s and r["input"] == i)["prevalence"])
    L = [r"\begin{table}[t]", r"\caption{Lidar windows (USGS 3DEP one metre DEM; flown: acquisition period of the lidar project), the number of face patches and the share of cells holding a face patch post at 10 and 30\,m.}",
         r"\label{tab:sites}", r"\centering\scriptsize", r"\setlength{\tabcolsep}{2.6pt}", r"\begin{tabular}{@{}lrrrrrrr@{}}", r"\toprule",
         r"Site & Lat., lon. & km$^2$ & Relief & Flown & Patches & 10\,m & 30\,m \\", r"\midrule"]
    for s in SITES:
        m = meta[s]
        y0, y1 = m["acquisition_start"][:4], m["acquisition_end"][:4]
        L.append(f"{SITE_LABEL[s]} & {float(m['centre_lat']):.2f}, {float(m['centre_lon']):.2f} & {float(m['area_km2']):.1f} & {float(m['relief_m']):.0f}\\,m & "
                 f"{y0 if y0 == y1 else y0 + ' to ' + y1[2:]} & {pm[s]['patches']} & {rnd(100 * prev(s, 'I10')):.0f}\\,\\% & {rnd(100 * prev(s, 'I30')):.0f}\\,\\% \\\\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


DET_ROWS = [("SLOPE", "Slope"), ("TRI", "Ruggedness"), ("ROUGH", "Roughness"), ("ASPECT", "Aspect rule"), ("BICUBIC", "Interpolation"),
            ("SR", "Super resolution$^{*}$"), ("DET", "Detector"), ("GBM", "Boosting$^{*}$"), ("GBM+", "Boosting+$^{*}$"), ("GBM-tuned", "Boosting, tuned$^{*}$"),
            ("CNN", "Network$^{*}$"), ("CNN-long", "Network, 6000 steps$^{*}$"), ("IMG-S2", "Sentinel-2 only$^{*}$"), ("DEM+S2", "Boosting + Sentinel-2$^{*}$"),
            ("IMG-NAIP", "NAIP only$^{*}$"), ("DEM+NAIP", "Boosting + NAIP$^{*}$")]
DET_COLS = [("I10", "I10"), ("I30", "I30"), ("I10to30", r"I10$\rightarrow$30"), ("R10", "R10"), ("N30", "N30"), ("G30n", "G30")]


def table_detection():
    D = det_rows()
    mean = {}
    for r in D:
        mean.setdefault((r["input"], r["method"]), []).append(float(r["auc"]))
    best = {c: f2(max(np.mean(v) for (i, m), v in mean.items() if i == c)) for c, _ in DET_COLS if any(i == c for i, _ in mean)}
    g30i = {r["method"]: f2(r["auc"]) for f in ("A_macro.csv", "F_macro.csv") for r in read(os.path.join(S27, f)) if r["input"] == "G30" and r["label"] == "L-ANY" and r["method"] in ("CNN", "SR")}
    L = [r"\begin{table}[t]", r"\caption{Detection of the face map label of Eq.~(\ref{eq:label}): mean AUC over the six sites. I: lidar block means; I10$\rightarrow$30: the largest of the nine 10\,m scores in each 30\,m cell; R10: USGS 1/3 arc second DEM, resampled by USGS from the same lidar at all six sites; N30: NASADEM; G30: GLO-30; R10, N30 and G30 on their own grids, where the network and super resolution were not run (on GLO-30 interpolated to the 30\,m lidar grid they reach " + g30i["CNN"] + " and " + g30i["SR"] + r"). $^{*}$Trained on the lidar of the other five sites. Best per column in bold (ties at two decimals all bold); $\cdot$ not run.}",
         r"\label{tab:detection}", r"\centering\scriptsize", r"\setlength{\tabcolsep}{2.8pt}", r"\begin{tabular}{@{}l" + "c" * len(DET_COLS) + r"@{}}", r"\toprule",
         "Layer & " + " & ".join(h for _, h in DET_COLS) + r" \\", r"\midrule"]
    for m, lab in DET_ROWS:
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


PLAN_LAYERS = [("none", "Slip model only"), ("SLOPE-cal", "Slope"), ("BICUBIC-cal", "Interpolation"), ("DET", "Detector"), ("DET-cal", "Detector, recalibrated"),
               ("GBM", "Boosting$^{*}$"), ("CNN", "Network$^{*}$"), ("DEM+S2", "Boosting + Sentinel-2$^{*}$"), ("FACEMAP", "Face map (oracle)")]
PLAN_COLS = [("E1", "I10"), ("E2", "I10"), ("E1", "I30"), ("E2", "I30"), ("E1", "G30")]
DEGRADED = [("FACEMAP", "Face map, $w=5$"), ("shift5", "Face map 5\\,m off"), ("shift10", "Face map 10\\,m off"), ("shift30", "Face map 30\\,m off"),
            ("survey2", "Face map from 2\\,m survey"), ("survey5", "Face map from 5\\,m survey")]


def table_planning():
    H = read(os.path.join(S28, "A_held_out.csv"))
    N = read(os.path.join(S28, "A_naive.csv"))
    C = read(os.path.join(S28, "C_degraded.csv")) if os.path.exists(os.path.join(S28, "C_degraded.csv")) else []

    def ho(e, i, lay):
        if lay == "none":
            r = next((r for r in N if r["profile"] == "published-posterior" and r["endpoints"] == e and r["input"] == i), None)
            return f"{rnd(100 * float(r['mission_success'])):.0f}" if r else NA
        r = next((r for r in H if r["profile"] == "published-posterior" and r["endpoints"] == e and r["input"] == i and r["layer"] == lay
                  and r["policies"] == "conservative+risk_weighted"), None)
        if r is None:
            return NA
        s = f"{rnd(100 * float(r['mission_success'])):.0f}"
        return s + ("$^{\\dagger}$" if float(r["diff_lo"]) > 0 else "")
    L = [r"\begin{table}[t]", r"\caption{Mission success (\%) at the operating point chosen on the other five sites (gate threshold or weight), 100 pairs per site, posterior vehicle. E1: endpoints chosen with the truth; E2: chosen from the coarse map only. $^{\dagger}$Two stage bootstrap interval of the gain over the slip model entirely above zero (not corrected for the number of cells). Lower part, a second protocol: face maps degraded as registered, weight policy at a fixed $w=5$. $\cdot$ not run. $^{*}$Trained leave one site out.}",
         r"\label{tab:planning}", r"\centering\scriptsize", r"\setlength{\tabcolsep}{3pt}", r"\begin{tabular}{@{}lccccc@{}}", r"\toprule",
         r" & \multicolumn{2}{c}{I10} & \multicolumn{2}{c}{I30} & G30 \\", r"Layer & E1 & E2 & E1 & E2 & E1 \\", r"\midrule"]
    for lay, lab in PLAN_LAYERS:
        L.append(f"{lab} & " + " & ".join(ho(e, i, lay) for e, i in PLAN_COLS) + r" \\")
    if C:
        L.append(r"\midrule")
        for mp, lab in DEGRADED:
            cells = []
            for e, i in PLAN_COLS:
                r = next((r for r in C if r["endpoints"] == e and r["input"] == i and r["map"] == mp and r["policy"] == "risk_weighted"), None)
                cells.append(f"{rnd(100 * float(r['mission_success'])):.0f}" if r else NA)
            L.append(f"{lab} & " + " & ".join(cells) + r" \\")
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
        return f"{rnd(100 * float(r[k])):.0f}" if k in ("success", "stuck") else f"{rnd(float(r[k])):.0f}"
    L = [r"\begin{table}[H]", r"\caption{Registered closed loop with an idealised sensor (radius $R$), 20 pairs per site, posterior vehicle, sensing every face within the radius: success (\%; goal reached, no face contact) and replans per pair (Rp), E1 endpoints unless marked E2. Main runs $R=20$\,m; I30 also with $R=10$ and 30\,m.}",
         r"\label{tab:closedloop_ideal}", r"\centering\scriptsize", r"\setlength{\tabcolsep}{2.4pt}", r"\begin{tabular}{@{}lccccccc@{}}", r"\toprule",
         r" & \multicolumn{2}{c}{I10, $R$ 20} & \multicolumn{2}{c}{I30, $R$ 20} & \multicolumn{3}{c}{I30, S} \\",
         r"Prior layer & S & Rp & S & Rp & E2 & $R$ 10 & $R$ 30 \\", r"\midrule"]
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
        c = f"{rnd(100 * float(r['success'])):.0f}"
        return c + ("$^{\\dagger}$" if r["diff_lo"] not in ("", None) and float(r["diff_lo"]) > 0 else "")

    def ideal(lay):
        r = next((r for r in E if r["profile"] == "published-posterior" and r["endpoints"] == "E1" and r["input"] == "I30" and r["layer"] == lay and float(r["radius_m"]) == 20.0), None)
        return f"{rnd(100 * float(r['success'])):.0f}" if r else NA
    L = [r"\begin{table}[t]", r"\caption{Closed loop with onboard sensing within 20\,m, 20 pairs per site, posterior vehicle, weight $w=5$: success (\%; goal reached without touching a face). Line of sight: a 5\,m cell is sensed only when visible from an eye 1\,m above the ground; $p_d=0.8$: each face cell is detectable with probability 0.8. Last column: the registered idealised sensor that sees every face within the radius. $^{\dagger}$Two stage bootstrap interval of the gain over the slip model prior entirely above zero. $\cdot$ not run. $^{*}$Trained leave one site out. Line of sight runs are post hoc.}",
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
    rows = re.findall(r"^\| ((?:B25|P26|D27|P28|X29|Y30)-\d+) \| ([^|\n]*) \| ([^\n]*)\|\s*$", reg, flags=re.M)
    L = [r"\begin{longtable}{@{}p{0.08\linewidth}p{0.42\linewidth}p{0.46\linewidth}@{}}",
         r"\caption{Prediction log of stages 25 to 30: every prediction as committed before its run (verbatim) and the outcome as recorded afterwards. Stages 29 (X29) and 30 (Y30) are post hoc and not counted in the tally.}\label{tab:log}\\",
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
            ("E1, E2", "endpoints chosen with the truth (all posts gentle) and from the coarse map only")]


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
    L = [r"\begin{table}[H]", r"\caption{Spread of the AUC across the six sites (lowest to highest) for each layer and input of Table III of the paper.}",
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
    L = [r"\begin{table}[H]", r"\caption{AUC per site on I30 (face map label), three decimals, with 95\,\% block bootstrap intervals where computed.}", r"\label{tab:persite}",
         r"\centering\scriptsize", r"\setlength{\tabcolsep}{2.5pt}", r"\begin{tabular}{@{}l" + "c" * len(ms) + r"@{}}", r"\toprule",
         "Site & " + " & ".join(h for _, h in ms) + r" \\", r"\midrule"]
    for s in SITES:
        cells = []
        for m, _ in ms:
            r = next((r for r in D + E if r["site"] == s and r["method"] == m), None)
            if r is None:
                cells.append(NA); continue
            c = f"{rnd(r['auc'], 3):.3f}"
            if r.get("auc_lo", ""):
                c += f" [{f2(r['auc_lo'])}, {f2(r['auc_hi'])}]"
            cells.append(c)
        L.append(f"{SITE_LABEL[s].split(',')[0]} & " + " & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(L)


# ---------------------------------------------------------------------------------------------------------------------
# render and build
# ---------------------------------------------------------------------------------------------------------------------
TABLES = {"sites": table_sites, "methods": lambda: open(os.path.join(SRC, "table_methods.tex"), encoding="utf-8").read().strip(),
          "detection": table_detection, "planning": table_planning, "closedloop": table_closed_loop, "closedloop_los": table_closed_loop_los, "log": table_log, "persite": table_persite,
          "glossary": table_glossary, "spread": table_spread}


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
