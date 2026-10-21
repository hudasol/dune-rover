#!/usr/bin/env python3
"""One command for a field day: check the data sheets, compute slip, apply the committed analysis rule and score
every committed field prediction.

    PYTHONPATH=src python3 scripts/ingest_field_day.py FOLDER [--label 2027-01-15_site1] [--predictions 2026-10-15] [--rebuild]

FOLDER holds the three filled sheets of field_kit/ (copies of the templates, same column names):
    runs.csv      one row per run (field_kit/runs_template.csv)
    stations.csv  one row per slope station (field_kit/stations_template.csv)
    soil.csv      one row per soil test repeat (field_kit/soil_template.csv), optional

What it does, in order (nothing here changes the analysis rule; it calls src/dunerover/fieldanalysis.py as committed):
 1. validates the sheets: required columns, numbers where numbers are needed, stations referenced by runs exist,
    slopes and speeds in plausible ranges; every problem is listed and the script stops on errors;
 2. fills phi_deg (and grain size, density, moisture) of a run from the station's soil tests when the run leaves it
    empty (median of the repeats of that test at that station);
 3. computes slip per run, the per bin means with bootstrap intervals, and the committed adequacy rule
    (fieldanalysis.analyse, pilot sigma when pilot runs exist);
 4. scores the dated predictions in docs/predictions/slope_ladder_predictions_<date>.csv: for every bin, whether
    the observed mean slip lies inside the model 5 to 95 % interval and inside the planning range, and the
    difference to the published Dumont value where one exists;
 5. writes results/field_day/<label>/ (runs_with_slip.csv, per_bin.csv, prediction_scores.csv, analysis.json,
    FIELD_DAY_SUMMARY.md) and, with --rebuild, regenerates the report.

The label of every output is "field measurement, one vehicle, one site" unless the folder is a synthetic test fixture,
in which case every output says SYNTHETIC and nothing is written under results/.
"""
from __future__ import annotations
import argparse, csv, json, os, subprocess, sys
from dataclasses import asdict

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover import fieldanalysis as FA  # noqa: E402

NUM_RUN = ["slope_deg", "v_true_mps", "wheel_omega_rad_s", "r_eff_m"]
SOIL_TO_RUN = {"friction_angle_deg": "phi_deg", "angle_of_repose_deg": None, "grain_d50_mm": "grain_d50_mm",
               "bulk_density_kg_m3": "bulk_density_kg_m3", "moisture_pct_0_2cm": "moisture_pct_0_2cm"}
RANGES = {"slope_deg": (-5.0, 40.0), "v_true_mps": (0.0, 3.0), "wheel_omega_rad_s": (0.0, 50.0), "r_eff_m": (0.02, 0.6), "phi_deg": (20.0, 50.0)}


def read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def template_cols(name):
    with open(os.path.join(ROOT, "field_kit", f"{name}_template.csv"), newline="") as fh:
        return next(csv.reader(fh))


def validate(folder):
    errors, warnings = [], []
    sheets = {}
    for name, required in (("runs", True), ("stations", True), ("soil", False)):
        p = os.path.join(folder, f"{name}.csv")
        if not os.path.exists(p):
            (errors if required else warnings).append(f"{name}.csv is missing")
            sheets[name] = []
            continue
        rows = read(p)
        miss = [c for c in template_cols(name) if rows and c not in rows[0]]
        if miss:
            errors.append(f"{name}.csv lacks columns {miss}")
        if not rows:
            (errors if required else warnings).append(f"{name}.csv has no rows")
        sheets[name] = rows
    st_ids = {r["station_id"] for r in sheets["stations"]}
    seen = set()
    for i, r in enumerate(sheets["runs"], 2):
        rid = r.get("run_id", "")
        if not rid or rid in seen:
            errors.append(f"runs.csv line {i}: run_id empty or repeated ({rid!r})")
        seen.add(rid)
        if r.get("station_id") and r["station_id"] not in st_ids:
            errors.append(f"runs.csv line {i}: station {r['station_id']!r} is not in stations.csv")
        for c in NUM_RUN:
            try:
                v = float(r[c])
                lo, hi = RANGES[c]
                if not lo <= v <= hi:
                    warnings.append(f"runs.csv line {i}: {c} = {v} outside the plausible range {lo} to {hi}")
            except (ValueError, KeyError):
                errors.append(f"runs.csv line {i}: {c} is not a number ({r.get(c)!r})")
        if r.get("entrapped", "") not in ("0", "1"):
            errors.append(f"runs.csv line {i}: entrapped must be 0 or 1")
        if rid.upper().startswith("EXAMPLE"):
            errors.append(f"runs.csv line {i}: the example row of the template is still present")
    for i, r in enumerate(sheets["soil"], 2):
        try:
            float(r["value"])
        except (ValueError, KeyError):
            errors.append(f"soil.csv line {i}: value is not a number")
        if r.get("station_id") not in st_ids:
            errors.append(f"soil.csv line {i}: station {r.get('station_id')!r} is not in stations.csv")
    return sheets, errors, warnings


def fill_from_soil(sheets):
    med = {}
    for r in sheets["soil"]:
        med.setdefault((r["station_id"], r["test"]), []).append(float(r["value"]))
    filled = 0
    for r in sheets["runs"]:
        for test, col in SOIL_TO_RUN.items():
            if col and not str(r.get(col, "")).strip() and (r.get("station_id"), test) in med:
                r[col] = f"{np.median(med[(r['station_id'], test)]):.3f}"; filled += 1
    return filled


def score_predictions(per_bin, date):
    p = os.path.join(ROOT, "docs", "predictions", f"slope_ladder_predictions_{date}.csv")
    preds = {}
    for r in read(p):   # a slope with two rows (direct ascent and the cross slope reference) is scored on the direct ascent row
        x = float(r["slope_deg"])
        if x not in preds or preds[x]["role"].startswith("cross slope"):
            preds[x] = r
    out = []
    for b in per_bin:
        x = float(b["bin_deg"])
        pr = preds.get(x)
        if pr is None:
            continue
        m = float(b["mean_slip"])
        row = {"bin_deg": x, "role": pr["role"], "n_runs": b.get("n"), "observed_mean_slip": round(m, 4)}
        if not pr["prior_p05_phi_unknown"].strip():
            row.update(model_p05="", model_p95="", inside_model_5_95="no committed interval for this bin")
            out.append(row); continue
        lo, hi = float(pr["prior_p05_phi_unknown"]), float(pr["prior_p95_phi_unknown"])
        row.update(model_p05=round(lo, 4), model_p95=round(hi, 4), inside_model_5_95=lo <= m <= hi)
        if pr.get("planning_range_lo"):
            plo, phi = float(pr["planning_range_lo"]), float(pr["planning_range_hi"])
            row.update(planning_lo=round(plo, 4), planning_hi=round(phi, 4), inside_planning_range=plo <= m <= phi)
        if pr.get("published_dumont_slip_FLD_HV13_1"):
            row["observed_minus_dumont"] = round(m - float(pr["published_dumont_slip_FLD_HV13_1"]), 4)
        out.append(row)
    return out


def write_csv(path, rows):
    if rows:
        with open(path, "w", newline="") as fh:
            keys = list(dict.fromkeys(k for r in rows for k in r))
            w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--label", default=None); ap.add_argument("--predictions", default="2026-10-15")
    ap.add_argument("--out-root", default=os.path.join(ROOT, "results", "field_day")); ap.add_argument("--rebuild", action="store_true")
    a = ap.parse_args(argv)
    synthetic = os.path.exists(os.path.join(a.folder, "SYNTHETIC"))
    label = "SYNTHETIC DATA, code test only, not a measurement" if synthetic else "field measurement, one vehicle, one site"
    if synthetic and os.path.abspath(a.out_root).startswith(os.path.join(ROOT, "results")):
        raise SystemExit("a synthetic fixture may not write under results/; pass --out-root to a temporary folder")
    sheets, errors, warnings = validate(a.folder)
    for w in warnings:
        print("WARNING:", w)
    if errors:
        for e in errors:
            print("ERROR:", e)
        raise SystemExit(f"{len(errors)} errors in the sheets; nothing was analysed")
    filled = fill_from_soil(sheets)
    out = os.path.join(a.out_root, a.label or os.path.basename(os.path.abspath(a.folder)))
    os.makedirs(out, exist_ok=True)
    runs_path = os.path.join(out, "runs_merged.csv")
    write_csv(runs_path, sheets["runs"])
    d = FA.load_runs(runs_path)
    slip = FA.observed_slip(d)
    write_csv(os.path.join(out, "runs_with_slip.csv"), [{**r, "slip": round(float(s), 4)} for r, s in zip(sheets["runs"], slip)])
    res = FA.analyse(d)
    per_bin = [dict(zip(("bin_deg", "n", "mean_slip", "ci95_low", "ci95_high"), b)) for b in FA.per_bin_means(d)]
    write_csv(os.path.join(out, "per_bin.csv"), per_bin)
    scores = score_predictions(per_bin, a.predictions)
    write_csv(os.path.join(out, "prediction_scores.csv"), scores)
    json.dump({"label": label, "predictions_file": a.predictions, "values_filled_from_soil": filled, "warnings": warnings,
               "result": asdict(res)}, open(os.path.join(out, "analysis.json"), "w"), indent=1, default=str)
    inside = sum(1 for s in scores if s["inside_model_5_95"] is True)
    lines = [f"# Field day summary: {a.label or os.path.basename(os.path.abspath(a.folder))}", "", f"Label: **{label}**.", "",
             f"Runs: {len(sheets['runs'])}; stations: {len(sheets['stations'])}; soil test repeats: {len(sheets['soil'])}; values filled from soil tests: {filled}.", "",
             f"Committed rule (src/dunerover/fieldanalysis.py): slip test {'passed' if res.slip_pass else 'not passed'}; informative: {res.informative}; tolerance {res.tol:.3f}.", "",
             f"Predictions of {a.predictions}: observed bin mean inside the model 5 to 95 % interval in {inside} of {len(scores)} bins.", "",
             "| Bin, deg | Role | Runs | Observed mean slip | Model 5 % | Model 95 % | Inside |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {s['bin_deg']} | {s['role']} | {s['n_runs']} | {s['observed_mean_slip']} | {s['model_p05']} | {s['model_p95']} | {s['inside_model_5_95']} |" for s in scores]
    open(os.path.join(out, "FIELD_DAY_SUMMARY.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    if a.rebuild and not synthetic:
        subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build_report.py")], check=True, env={**os.environ, "PYTHONPATH": os.path.join(ROOT, "src")})
    return out


if __name__ == "__main__":
    main()
