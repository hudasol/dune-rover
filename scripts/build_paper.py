#!/usr/bin/env python3
"""Build the conference paper from its template and the stage 25 and 26 result files.

    PYTHONPATH=src python3 scripts/build_paper.py            # paper/paper.tex and paper/paper.pdf
    PYTHONPATH=src python3 scripts/build_paper.py --check    # fail if paper/paper.tex is stale or a value is missing

Every number in the paper comes from a result file through a {{VAL:key}} placeholder; tables are built here. The text
around the numbers is in paper/src/paper_template.tex and paper/src/text_*.tex. SIMULATED BY ME on PUBLISHED data.
"""
from __future__ import annotations
import csv, json, os, re, shutil, subprocess, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(ROOT, "paper")
DET = os.path.join(ROOT, "results", "benchmark", "detection")
PLN = os.path.join(ROOT, "results", "benchmark", "planning")
SITE_LABEL = {"Dumont": "Dumont Dunes, CA", "WhiteSands": "White Sands, NM", "Kelso": "Kelso Dunes, CA",
              "GreatSandDunes": "Great Sand Dunes, CO", "Algodones": "Algodones Dunes, CA", "LittleSahara": "Little Sahara, UT"}
SITES = list(SITE_LABEL)
INPUTS = ("I10", "I30", "G30")
METHODS = ("DET", "SLOPE", "TRI", "ROUGH", "BICUBIC", "GBM", "CNN")
NAMES = {"DET": "DET (ours)", "SLOPE": "SLOPE", "TRI": "TRI", "ROUGH": "ROUGH", "BICUBIC": "BICUBIC", "GBM": "GBM$^{*}$", "CNN": "CNN$^{*}$"}


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def f2(x):
    return f"{float(x):.2f}"


def pct(x, nd=0):
    return f"{100 * float(x):.{nd}f}\\,\\%"


def values() -> dict:
    V = {}
    met = read(os.path.join(DET, "metrics.csv"))
    diffs = read(os.path.join(DET, "paired_differences.csv"))
    summ = json.load(open(os.path.join(DET, "summary.json")))
    get = lambda s, i, m: next((r for r in met if r["site"] == s and r["input"] == i and r["method"] == m), None)
    for i in INPUTS:
        for m in METHODS + ("DET-cal", "SLOPE-cal", "TRI-cal", "ROUGH-cal", "BICUBIC-cal"):
            rr = [get(s, i, m) for s in SITES]
            rr = [r for r in rr if r]
            if not rr:
                continue
            for key in ("auc", "ap", "recall_at_fpr10", "brier", "miss_at_0.20", "flagged_at_0.20", "auc_28_36"):
                v = [float(r[key]) for r in rr if r.get(key, "") not in ("", None)]
                if v:
                    k = key.replace(".", "").replace("_at_", "_")
                    V[f"{k}_{i}_{m}_mean"] = f2(np.mean(v)) if "auc" in key or key in ("ap", "brier") else pct(np.mean(v))
                    V[f"{k}_{i}_{m}_min"] = f2(min(v)) if "auc" in key or key in ("ap", "brier") else pct(min(v))
                    V[f"{k}_{i}_{m}_max"] = f2(max(v)) if "auc" in key or key in ("ap", "brier") else pct(max(v))
            for s in SITES:
                r = get(s, i, m)
                if r and r.get("auc", ""):
                    V[f"auc_{i}_{m}_{s}"] = f2(r["auc"])
        for m in METHODS:
            for ref in ("DET", "SLOPE"):
                dd = [d for d in diffs if d["input"] == i and d["method"] == m and d["reference"] == ref]
                if dd:
                    V[f"nbetter_{i}_{m}_vs_{ref}"] = str(sum(d["significant"] == "True" and float(d["auc_difference"]) > 0 for d in dd))
                    V[f"nworse_{i}_{m}_vs_{ref}"] = str(sum(d["significant"] == "True" and float(d["auc_difference"]) < 0 for d in dd))
                    V[f"dauc_{i}_{m}_vs_{ref}"] = f"{np.mean([float(d['auc_difference']) for d in dd]):+.2f}"
    for s in SITES:
        for i in ("I10", "I30"):
            V[f"prev_{i}_{s}"] = pct(get(s, i, "DET")["prevalence"])
    V["n_sites"] = str(len(SITES))
    pl = [r for r in read(os.path.join(PLN, "summary.csv"))]
    for r in pl:
        key = f"{r['profile']}_{r['input']}_{r['policy']}_{r['hazard']}".replace("-", "").replace("published-posterior", "posterior")
        for k in ("routed", "mission_success", "unsafe_of_routed", "uphill_of_routed"):
            if r.get(k, "") != "":
                V[f"pl_{key}_{k}"] = pct(r[k]); V[f"pl_{key}_{k}_lo"] = pct(r[k + "_lo"]); V[f"pl_{key}_{k}_hi"] = pct(r[k + "_hi"])
        if r.get("length_ratio", "") != "":
            V[f"pl_{key}_length_ratio"] = f2(r["length_ratio"])
        if r.get("patch_entries_per_km", "") != "":
            V[f"pl_{key}_entries_km"] = f"{float(r['patch_entries_per_km']):.1f}"
    V["pairs_total"] = str(int(sum(1 for _ in read(os.path.join(PLN, "endpoints.csv")))))
    tests = read(os.path.join(PLN, "tests.csv"))
    for t in tests:
        key = f"{t['profile']}_{t['input']}_{t['policy']}_{t['hazard']}_vs_{t['reference'].replace(' ', '_')}".replace("-", "")
        V[f"t_{key}_p"] = t["p_holm"]; V[f"t_{key}_diff"] = f"{100 * float(t['difference']):+.0f}"
    V["crit_assumed"] = f"{json.load(open(os.path.join(PLN, 'summary.json')))['critical_uphill_deg']['assumed']:.1f}"
    V["crit_posterior"] = f"{json.load(open(os.path.join(PLN, 'summary.json')))['critical_uphill_deg']['published-posterior']:.1f}"
    return V, met, pl, summ


def table_sites(met, summ):
    lines = [r"\begin{table}[t]", r"\caption{Lidar windows and the share of cells that hold a face (cell label).}", r"\label{tab:sites}",
             r"\centering\small", r"\begin{tabular}{lrrrr}", r"\toprule", r"Site & Area & Relief & \multicolumn{2}{c}{Face cells} \\",
             r" & km$^2$ & m & 10\,m & 30\,m \\", r"\midrule"]
    for s in SITES:
        st = summ["sites"][s]
        w = st["window_utm"]
        area = (w[1] - w[0]) * (w[3] - w[2]) / 1e6
        rel = st.get("relief_m")
        p10 = next(r for r in met if r["site"] == s and r["input"] == "I10" and r["method"] == "DET")["prevalence"]
        p30 = next(r for r in met if r["site"] == s and r["input"] == "I30" and r["method"] == "DET")["prevalence"]
        lines.append(f"{SITE_LABEL[s]} & {area:.1f} & {rel:.0f} & {100 * float(p10):.0f}\\,\\% & {100 * float(p30):.0f}\\,\\% \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def table_detection(met):
    def cell(i, m, key):
        v = [float(r[key]) for r in met if r["input"] == i and r["method"] == m and r.get(key, "") != ""]
        return f"{np.mean(v):.2f}" if v else "--"
    best = {i: max(METHODS, key=lambda m: float(cell(i, m, "auc")) if cell(i, m, "auc") != "--" else -1) for i in INPUTS}
    lines = [r"\begin{table}[t]", r"\caption{Detection: mean over six sites of the AUC and average precision (AP); $^{*}$trained on lidar labels of the other five sites. Best AUC per input in bold.}",
             r"\label{tab:detection}", r"\centering\small", r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{lcccccc}", r"\toprule",
             r" & \multicolumn{2}{c}{I10} & \multicolumn{2}{c}{I30} & \multicolumn{2}{c}{G30} \\",
             r"Method & AUC & AP & AUC & AP & AUC & AP \\", r"\midrule"]
    for m in METHODS:
        if not any(r["method"] == m for r in met):
            continue
        cells = []
        for i in INPUTS:
            a = cell(i, m, "auc")
            cells += [f"\\textbf{{{a}}}" if best[i] == m else a, cell(i, m, "ap")]
        lines.append(f"{NAMES[m]} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


PLAN_ROWS = [("shortest", "none", "Shortest path"), ("naive", "none", "Slip model only"),
             ("conservative", "SLOPE-cal", "Gate: SLOPE"), ("conservative", "DET", "Gate: DET (ours)"), ("conservative", "DET-cal", "Gate: DET-cal"),
             ("conservative", "GBM", "Gate: GBM$^{*}$"), ("conservative", "CNN", "Gate: CNN$^{*}$"), ("risk_weighted", "DET", "Weight: DET (ours)"),
             ("risk_weighted", "GBM", "Weight: GBM$^{*}$"), ("conservative", "ORACLE", "Gate: ORACLE")]


def table_planning(pl):
    def g(i, pol, hz, k):
        r = next((r for r in pl if r["profile"] == "assumed" and r["input"] == i and r["policy"] == pol and r["hazard"] == hz), None)
        return f"{100 * float(r[k]):.0f}" if r and r.get(k, "") != "" else "--"
    lines = [r"\begin{table}[t]", r"\caption{Planning, pooled over six sites (600 pairs): unsafe share of routed pairs (U) and mission success (S), in \%. Gate: conservative policy; Weight: risk weighted policy.}",
             r"\label{tab:planning}", r"\centering\small", r"\setlength{\tabcolsep}{3.5pt}", r"\begin{tabular}{lcccccc}", r"\toprule",
             r" & \multicolumn{2}{c}{I10} & \multicolumn{2}{c}{I30} & \multicolumn{2}{c}{G30} \\", r"Planner & U & S & U & S & U & S \\", r"\midrule"]
    for pol, hz, lab in PLAN_ROWS:
        cells = []
        for i in INPUTS:
            cells += [g(i, pol, hz, "unsafe_of_routed"), g(i, pol, hz, "mission_success")]
        lines.append(f"{lab} & " + " & ".join(cells) + r" \\")
    o5 = next((r for r in pl if r["profile"] == "assumed" and r["hazard"] == "ORACLE-5"), None)
    if o5:
        lines.append(r"\midrule")
        lines.append(f"ORACLE-5 (5\\,m) & \\multicolumn{{6}}{{c}}{{U {100 * float(o5['unsafe_of_routed']):.0f}, S {100 * float(o5['mission_success']):.0f}}} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def render(V, met, pl, summ) -> str:
    t = open(os.path.join(PAPER, "src", "paper_template.tex"), encoding="utf-8").read()
    for name in sorted(os.listdir(os.path.join(PAPER, "src"))):
        if name.startswith("text_") and name.endswith(".tex"):
            body = open(os.path.join(PAPER, "src", name), encoding="utf-8").read().strip()
            t = t.replace("{{VAL:" + name[5:-4] + "}}", body)
    t = t.replace("{{TABLE:sites}}", table_sites(met, summ)).replace("{{TABLE:detection}}", table_detection(met)).replace("{{TABLE:planning}}", table_planning(pl))
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


def main():
    check = "--check" in sys.argv
    V, met, pl, summ = values()
    # relief per site from the stage 12 and 20 summaries (the same windows)
    for f in ("results/terrain_validation/summary.json", "results/terrain_validation_phase4/summary.json"):
        for s, v in json.load(open(os.path.join(ROOT, f)))["sites"].items():
            summ["sites"][s]["relief_m"] = v["relief_m"]
    tex = render(V, met, pl, summ)
    out = os.path.join(PAPER, "paper.tex")
    if check:
        old = open(out, encoding="utf-8").read() if os.path.exists(out) else ""
        if old != tex:
            raise SystemExit("paper/paper.tex is stale: run scripts/build_paper.py")
        print("paper: ok"); return
    open(out, "w", encoding="utf-8").write(tex)
    json.dump(V, open(os.path.join(PAPER, "values.json"), "w"), indent=0, sort_keys=True)
    if shutil.which("latexmk") and "--no-pdf" not in sys.argv:
        r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "paper.tex"], cwd=PAPER, capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-3000:]); raise SystemExit("LaTeX failed")
        subprocess.run(["latexmk", "-c"], cwd=PAPER, capture_output=True)
        log = open(os.path.join(PAPER, "paper.log"), encoding="latin-1").read() if os.path.exists(os.path.join(PAPER, "paper.log")) else ""
        print("pages:", re.findall(r"Output written on paper.pdf \((\d+) pages", r.stdout + log))
    print("wrote", out)


if __name__ == "__main__":
    main()
