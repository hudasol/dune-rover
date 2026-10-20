#!/usr/bin/env python3
"""Draw a blinded random sample of 20 evidence rows for a human rater (Huda) and write the rating sheet.

    python3 scripts/make_inter_rater_sample.py

Seed 20261025, drawn from research/evidence.csv as merged on 2026-10-20 (rows of every phase).  The sheet shows the
claim fields only, not the verifier's verdict, so the human rating is independent.  After rating, run
scripts/inter_rater_agreement.py.  Outputs: research/spot_check_inter_rater.md, research/spot_check_inter_rater_ratings.csv.
"""
import csv, os, random
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED, N = 20261025, 20
rows = list(csv.DictReader(open(os.path.join(ROOT, "research", "evidence.csv"), encoding="utf-8")))
pick = sorted(random.Random(SEED).sample(rows, N), key=lambda r: r["id"])
md = ["# Inter rater spot check (blinded), drawn 2026-10-20", "",
      f"Twenty rows drawn at random (seed {SEED}) from the {len(rows)} rows of `research/evidence.csv`. The verifier's verdict is hidden.",
      "For each row: open the source at the link, find the passage named under *where*, and check the value, unit, slope, vehicle or terrain, and validation type.",
      "Write one verdict per row in `research/spot_check_inter_rater_ratings.csv` (correct, minor_error, material_error or unverifiable) with a short note, then run `python3 scripts/inter_rater_agreement.py`.",
      "Definitions: material error = wrong value, unit, metric meaning, validation type, vehicle or terrain, or slope; minor error = number right but a label, location or descriptive detail wrong.", ""]
for i, r in enumerate(pick, 1):
    md += [f"## {i}. {r['id']}", f"- source: {r['source_title']} ({r['source_url']})", f"- where: {r['passage_or_location']}",
           f"- vehicle or wheel: {r['vehicle_or_wheel']}", f"- terrain: {r['terrain_description']}", f"- slope: {r['slope_deg']}",
           f"- metric: {r['metric']}", f"- value and unit: {r['value']} {r['unit']}", f"- validation type: {r['validation_type']}", ""]
open(os.path.join(ROOT, "research", "spot_check_inter_rater.md"), "w", encoding="utf-8").write("\n".join(md))
with open(os.path.join(ROOT, "research", "spot_check_inter_rater_ratings.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["id", "huda_verdict", "huda_note"]); [w.writerow([r["id"], "", ""]) for r in pick]
print("wrote", N, "rows")
