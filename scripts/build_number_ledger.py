#!/usr/bin/env python3
"""Number ledger: trace every number in the manuscript, the executive brief and the two proposals to its source.

    PYTHONPATH=src python3 scripts/build_number_ledger.py          # writes docs/NUMBER_LEDGER.csv
    PYTHONPATH=src python3 scripts/build_number_ledger.py --check  # gate: fails on any untraced number or a stale ledger

Every number in those four documents reaches them in one of four ways, and each way has its own ledger row:
  value    a {{VAL:key}} placeholder filled from a result file; the row gives the key, the rendered value, the script
           that produced the result file, the input files and their SHA-256 (PRODUCERS below);
  table    a {{TABLE:name}} placeholder generated from result files (one row per table);
  evidence a cited evidence row id (FLD-..., TM3-... and so on): the row gives the source, its location and the value
           as recorded in research/evidence.csv;
  hand     a number typed by hand in the template (a design constant, a published value quoted with its row, a date or
           a cross reference): the row gives the written justification from the document's hand numbers file.
The check fails if a placeholder key has no producer, if a hand typed number has no justification, or if the
committed ledger differs from a fresh build.
"""
from __future__ import annotations
import csv, glob, hashlib, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "docs", "NUMBER_LEDGER.csv")

DOCS = [  # generated document, template, hand numbers file
    ("manuscript/MANUSCRIPT.md", "manuscript/src/manuscript.md", "manuscript/src/hand_numbers.csv"),
    ("docs/EXECUTIVE_BRIEF.md", "docs/src/brief_template.md", "docs/src/hand_numbers_brief.csv"),
    ("docs/PROPOSAL_ROBOTICS.md", "docs/src/proposal_robotics_template.md", "docs/src/hand_numbers_proposal_robotics.csv"),
    ("docs/PROPOSAL_EDGE.md", "docs/src/proposal_edge_template.md", "docs/src/hand_numbers_proposal_edge.csv"),
]

# key pattern (regular expression, matched from the start of the key) -> (producing script, input files as globs)
PRODUCERS = [
    (r"bm_auc_|bm_miss_|bm_n_sites", "scripts/benchmark_detection.py", ["results/benchmark/detection/metrics.csv", "results/benchmark/detection/summary.json"]),
    (r"bm_", "scripts/benchmark_planning.py", ["results/benchmark/planning/summary.csv", "results/benchmark/planning/endpoints.csv"]),
    (r"cur_material_ci", "scripts/verify_stats.py", ["research/verification_stats.json"]),
    (r"p3_|ver_p4_n", "scripts/consolidate_evidence.py", ["research/evidence.csv"]),
    (r"p5_|cur_", "scripts/verify_stats.py", ["research/verification_stats.json"]),
    (r"ver_", "scripts/verify_stats.py", ["research/verification_stats.json"]),
    (r"tv_", "scripts/terrain_validation_lidar.py", ["results/terrain_validation/metrics.csv", "results/terrain_validation/slope_gap.csv"]),
    (r"wind_", "scripts/wind_face_direction.py", ["results/wind_azimuth/face_vs_wind.csv"]),
    (r"ch_", "scripts/chrono_wheel_slope.py; scripts/compare_chrono.py", ["results/chrono_scm/sweep.csv", "results/chrono_scm/comparison.csv"]),
    (r"mv_ncurves|mv_nsources", "scripts/model_validation.py (load_curves)", ["research/phase3/curves.csv"]),
    (r"mv_|score_model", "scripts/model_validation.py", ["results/model_validation/part_*/summary.json", "results/model_validation/part_*/nominal.csv"]),
    (r"post_unk_", "src/dunerover/study_subgrid.py --range-set posterior_2026_10_20", ["results/subgrid_posterior_2026_10_20/class_shares.csv"]),
    (r"postm_unk_", "src/dunerover/study_subgrid.py --range-set posterior_2026_10_20 --reject-immobile (post hoc)", ["results/subgrid_posterior_2026_10_20_mobile_posthoc/class_shares.csv"]),
    (r"post_s_med|post_", "scripts/model_validation.py", ["results/model_validation/part_exp_existing_mohr_coulomb_ratio_logistic_empirical/posterior_exp.json"]),
    (r"q8_unk_", "src/dunerover/study_subgrid.py --range-set widened_i0_fr --reject-immobile", ["results/subgrid_widened_i0_fr_mobile/class_shares.csv"]),
    (r"orig_unk_", "src/dunerover/study_subgrid.py", ["results/subgrid/class_shares.csv"]),
    (r"wi0_unk_", "src/dunerover/study_subgrid.py --range-set widened_i0", ["results/subgrid_widened_i0/class_shares.csv"]),
    (r"wfr_unk_", "src/dunerover/study_subgrid.py --range-set widened_i0_fr", ["results/subgrid_widened_i0_fr/class_shares.csv"]),
    (r"unk_|unk3_|unkpi03_|trav_|blk_|uni_|sens_", "src/dunerover/study_subgrid.py", ["results/subgrid/class_shares.csv", "results/subgrid/robustness_to_assumed_parameters.csv", "results/subgrid/subgrid_prior_sensitivity.csv"]),
    (r"sob_", "scripts/sobol_map.py", ["results/sobol_map/sobol_indices.csv"]),
    (r"pl10_", "scripts/planner_lidar.py --baseline 10 (post hoc)", ["results/planner/posthoc_baseline_10m/policy_summary.csv"]),
    (r"pl_", "scripts/planner_lidar.py", ["results/planner/policy_summary.csv"]),
    (r"pm", "scripts/planner_matched_pairs.py (post hoc)", ["results/planner/matched_pairs.csv"]),
    (r"ro_", "scripts/field_rule_options.py", ["results/field_kit/rule_options_2026-10-20.csv"]),
    (r"dc_", "scripts/digitise_figures.py", ["research/phase3/curves.csv"]),
    (r"an_", "scripts/anchor_comparisons.py", ["results/anchor_check.csv", "results/anchors/summary.json", "results/anchors/ishigami2009_comparison.csv"]),
    (r"rs_", "src/dunerover/study.py, src/dunerover/study_subgrid.py and scripts/anchor_comparisons.py per range set",
     ["results/widened_i0/summary.json", "results/widened_i0_fr/summary.json", "results/subgrid_widened_i0/class_shares.csv",
      "results/subgrid_widened_i0_fr/class_shares.csv", "results/anchors_widened_i0/summary.json", "results/anchors_widened_i0_fr/summary.json"]),
    (r"crit_", "src/dunerover/study.py", ["results/summary.json"]),
    (r"ntests", "scripts/build_report.py (counts test functions)", ["tests/test_*.py"]),
    (r"npred|pred_stage_line", "scripts/tally_predictions.py", ["docs/PREDICTIONS.md"]),
    (r"score_overall", "scripts/build_report.py (mean of the completeness table scores)", ["docs/src/completeness_template.md"]),
    (r"build_date", "scripts/build_manuscript.py (DATE constant)", ["scripts/build_manuscript.py"]),
    (r"is2_ps_|is2_kg_", "scripts/icesat2_posthoc_screen.py (post hoc)", ["results/icesat2/posthoc_screen.csv", "results/icesat2/posthoc_kelso_gap.csv"]),
    (r"is2_", "scripts/icesat2_profiles.py", ["results/icesat2/validation_metrics.csv", "results/icesat2/arabia_metrics.csv"]),
    (r"scl_|p6_|cur_material_ci", "scripts/consolidate_evidence.py; scripts/verify_stats.py", ["research/evidence.csv", "research/verification_stats.json"]),
    (r"p4_", "scripts/digitise_figures.py --phase 4", ["research/phase4/curves_new.csv"]),
    (r"redig_", "scripts/select_redigitise.py compare", ["research/phase4/redigitise_agreement.csv"]),
    (r"mvl_", "scripts/model_validation.py --group-sources, laboratory level (post hoc)", ["results/model_validation_phase4_posthoc_lab_grouped/*/summary.json"]),
    (r"mvg_", "scripts/model_validation.py --group-sources (post hoc)", ["results/model_validation_phase4_posthoc_grouped/*/summary.json"]),
    (r"mv4_|mob_|post4_", "scripts/model_validation.py on the expanded curve set (stages 21 and 22)", ["research/phase4/curves_new.csv", "results/model_validation_phase4/*/summary.json", "results/model_validation_phase4/*/loso.csv"]),
    (r"lid4_|lid6_", "scripts/terrain_validation_lidar.py (stages 12 and 20)", ["results/terrain_validation/metrics.csv", "results/terrain_validation_phase4/metrics.csv"]),
    (r"pl4_", "scripts/planner_lidar.py (stage 20)", ["results/planner_phase4/policy_summary.csv"]),
    (r"clph_", "demo/closed_loop_posthoc.py (post hoc)", ["results/closed_loop/posthoc_fixed_field/summary.csv", "results/closed_loop/posthoc_fixed_field/estimator.csv"]),
    (r"cl_|ros_", "demo/closed_loop.py; demo/ros2 (stage 23)", ["results/closed_loop/summary.csv", "results/closed_loop/estimator.csv", "results/closed_loop/ros2_smoke_test.json"]),
    (r"scm_chk_", "scripts/chrono_scm_calibration.py --checks (post hoc)", ["results/chrono_scm_calibration/posthoc_checks.csv", "results/chrono_scm_calibration/posthoc_checks_calibration_slopes.csv"]),
    (r"pd_", "scripts/build_web_demo.py (planner demonstration, not a registered test)", ["results/planner_demo/metrics.json"]),
    (r"clm_", "demo/closed_loop_multiseed.py (post hoc)", ["results/closed_loop/posthoc_multiseed/summary.csv"]),
    (r"mvc_", "scripts/model_validation.py (load_curves, run logs)", ["research/phase3/curves.csv", "research/phase4/curves_new.csv", "results/model_validation/part_exp_existing_mohr_coulomb_ratio_logistic_empirical/run_log.txt", "results/model_validation_phase4/part_exp_existing_mohr_coulomb_ratio_logistic_empirical/run_log.txt"]),
    (r"scm_", "scripts/chrono_scm_calibration.py", ["results/chrono_scm_calibration/summary.json", "results/chrono_scm_calibration/prediction.csv"]),
]
TABLES = {"families": ("scripts/build_manuscript.py (t_families)", ["results/model_validation/part_*/summary.json"]),
          "lidar": ("scripts/build_manuscript.py (t_lidar)", ["results/terrain_validation/metrics.csv"]),
          "locomotion": ("scripts/build_manuscript.py (t_locomotion)", ["research/evidence.csv"])}
ROW_ID = re.compile(r"\b(?:FLD|TM|SIM|LRN|LEG|PLN|TM3|MOB|SND|DUN|MAP|ENV|SCL)-[A-Za-z0-9]+(?:-[0-9a-z]+)?\b")
_SHA = {}


def sha(rel):
    if rel not in _SHA:
        h = hashlib.sha256()
        with open(os.path.join(ROOT, rel), "rb") as f:
            h.update(f.read())
        _SHA[rel] = h.hexdigest()
    return _SHA[rel]


def expand(globs):
    files = []
    for g in globs:
        files += sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, g)))
    return files


def producer(key):
    for pat, script, files in PRODUCERS:
        if re.match(pat, key):
            return script, expand(files)
    return None, []


def hand_tokens(template_text):
    """Numbers typed by hand: the rule of scripts/check_manuscript_numbers.py, plus two exclusions that are not
    quantities: ISO dates (2026-10-21) and the numbers of markdown headings (## 3. or ### 13.1)."""
    t = re.sub(r"\{\{[^}]*\}\}", "", template_text); t = re.sub(r"`[^`]*`", "", t)
    t = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "", t)
    t = re.sub(r"(?m)^#+\s*[\d.]+\s", "# ", t)
    t = ROW_ID.sub("", t)
    t = re.sub(r"\(https?://[^)]*\)|https?://\S+", "", t)
    return sorted(set(re.findall(r"(?<![A-Za-z_])\d+(?:\.\d+)?", t)), key=lambda s: (float(s), s))   # ties such as 0.2 and 0.20 ordered by text, so the ledger is deterministic


def build():
    import build_report as BR, phase3_values as P3, build_manuscript as BM
    ev = BR.rd("research/evidence.csv")
    v = BR.values(ev); v.update(P3.values()); v = BM.extra_values(v)
    evd = {r["id"]: r for r in ev}
    rows, problems = [], []
    for doc, tmpl, hand in DOCS:
        t = open(os.path.join(ROOT, tmpl), encoding="utf-8").read()
        for key in sorted(set(re.findall(r"\{\{VAL:([^}]*)\}\}", t))):
            script, files = producer(key)
            if script is None:
                problems.append(f"{doc}: placeholder {key} has no producer in PRODUCERS")
                continue
            if key not in v and key != "score_overall":
                problems.append(f"{doc}: placeholder {key} has no value (result not produced)")
            rows.append({"document": doc, "kind": "value", "item": key, "value": str(v.get(key, "computed at build")), "producer": script,
                         "inputs": "; ".join(files), "input_sha256": "; ".join(sha(f) for f in files), "evidence_rows": "", "justification": ""})
        for name in sorted(set(re.findall(r"\{\{TABLE:([^}]*)\}\}", t))):
            script, files = TABLES[name]; files = expand(files)
            rows.append({"document": doc, "kind": "table", "item": name, "value": "every number in the table", "producer": script,
                         "inputs": "; ".join(files), "input_sha256": "; ".join(sha(f) for f in files), "evidence_rows": "", "justification": ""})
        for rid in sorted(set(ROW_ID.findall(re.sub(r"\{\{[^}]*\}\}", "", t)))):
            r = evd.get(rid)
            if r is None:
                problems.append(f"{doc}: evidence row {rid} is not in research/evidence.csv")
                continue
            rows.append({"document": doc, "kind": "evidence", "item": rid, "value": f"{r['value']} {r['unit']}".strip(), "producer": "research/evidence.csv (verified row)",
                         "inputs": r["source_url"], "input_sha256": "", "evidence_rows": rid, "justification": r["passage_or_location"]})
        just = {}
        hp = os.path.join(ROOT, hand)
        if os.path.exists(hp):
            just = {r["token"]: r["justification"] for r in csv.DictReader(open(hp, encoding="utf-8"))}
        for tok in hand_tokens(t):
            if tok not in just:
                problems.append(f"{doc}: hand typed number {tok} has no justification in {hand}")
                continue
            rows.append({"document": doc, "kind": "hand", "item": tok, "value": tok, "producer": "typed in the template", "inputs": tmpl,
                         "input_sha256": "", "evidence_rows": ", ".join(ROW_ID.findall(just[tok])), "justification": just[tok]})
    return rows, problems


def render(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["document", "kind", "item", "value", "producer", "inputs", "input_sha256", "evidence_rows", "justification"], lineterminator="\n")
    w.writeheader(); w.writerows(rows)
    return buf.getvalue()


def main():
    rows, problems = build()
    text = render(rows)
    if "--check" in sys.argv:
        old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        stale = old != text
        print(f"number ledger: {len(rows)} rows; {len(problems)} untraced items; {'STALE' if stale else 'up to date'}")
        for p in problems:
            print("  " + p)
        sys.exit(1 if problems or stale else 0)
    open(OUT, "w", encoding="utf-8").write(text)
    print(f"wrote {len(rows)} rows to docs/NUMBER_LEDGER.csv; {len(problems)} untraced items")
    for p in problems:
        print("  " + p)


if __name__ == "__main__":
    main()
