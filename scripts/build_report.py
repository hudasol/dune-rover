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
                     "Steepest uphill on any route, deg", "Origin-destination pairs"], rows)


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
    return md_table(["#", "Title", "URL (retrieved 2026-10-11)", "Evidence rows"], rows), len(by)


def main():
    ev = rd("research/evidence.csv")
    uae = rd("research/raw/uae_facts.csv")
    body = ""
    for fn in sorted(os.listdir(os.path.join(ROOT, "docs/src"))):
        if re.match(r"\d\d_.*\.md$", fn):
            body += open(os.path.join(ROOT, "docs/src", fn), encoding="utf-8").read() + "\n"
    sp = os.path.join(ROOT, "docs/src/second_pass.txt")
    second = open(sp, encoding="utf-8").read().strip() if os.path.exists(sp) else "Pending at the time of building this file."
    tabs = {"params": t_params(), "slopestats": t_slopestats(), "nominal": t_nominal(), "oat": t_oat(), "lhs_rank": t_lhs_rank(),
            "lhs_pct": t_lhs_pct(), "anchor": t_anchor()}
    for k, v in tabs.items():
        body = body.replace("{{TABLE:%s}}" % k, v)
    body = body.replace("{{SECOND_PASS}}", second)
    c_tab, n_src = appendix_c(ev)
    app = ["\n---\n\n## Appendix A. Evidence table (all PUBLISHED; condensed, full fields in `research/evidence.csv`)\n",
           f"{len(ev)} rows. Validation types: " + ", ".join(f"{k} {v}" for k, v in sorted(
               {t: sum(1 for r in ev if r['validation_type'] == t) for t in {r['validation_type'] for r in ev}}.items())) +
           ". Values are as printed in the source; read the comparability warning before comparing any two rows. Verification status of each row is in the CSV (column `verification`).\n",
           appendix_a(ev),
           "\n\n## Appendix B. UAE facts (from `research/raw/uae_facts.csv`)\n", appendix_b(uae),
           f"\n\n## Appendix C. Sources ({n_src} distinct URLs; each was retrieved on 2026-10-11)\n", c_tab, "\n"]
    out = body + "\n".join(app)
    path = os.path.join(ROOT, "docs/REPORT.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(out)
    print("wrote", path, len(out), "chars;", len(out.split()), "words")


if __name__ == "__main__":
    main()
