#!/usr/bin/env python3
"""Turn verifier output (research/verify_out_batch4..14.csv) into rows of research/corrections.csv.

Batch 14 (2026-10-18): check of the two rows split from FLD-HV13-5.
Batches 4 to 7: phase 2 re-check of the original rows. Batches 8 to 13: re-check of the 26 rows read from
the supplied PDFs (research/phase2/supplied_pdf_rows_2026-10-13.csv), 2026-10-15.

Idempotent: a (id, field) pair already present is skipped.  The verifier's `corrected_value`
column has the form `field=value; field=value`; fields are split only at known column names.
Deterministic; no network.
"""
import csv, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ["vehicle_or_wheel","terrain_description","soil_parameters_reported","slope_deg","method","metric","value","unit","validation_type",
          "passage_or_location","comparability_warning","notes"]
pat = re.compile(r"(?:^|;\s+)(" + "|".join(FIELDS) + r")=")
# judgement overrides: the verifier proposed a free-text value in a controlled column
OVERRIDE = {("FLD-029", "validation_type"): ("none",
            "Verifier: the 20 to 30 % at 15 deg is an unreferenced capability statement, not a measurement; no validation type applies"),
            ("FLD-HV13-5", "validation_type"): ("lab and field",
            "Supplied PDF verifier: the 22 deg bedrock limit and 75 % slip at 20 deg come from the JPL Marsyard (an engineered yard, counted as lab); only the 28 deg cohesive soil result is from Tecopa (field). Free text shortened to a controlled value")}
def parse(cv):
    parts = pat.split(cv)
    return [(parts[i], parts[i + 1].strip()) for i in range(1, len(parts), 2)]
path = os.path.join(ROOT, "research", "corrections.csv")
# a pair already corrected by a verifier is skipped; definitions of split rows do not count as corrections
have = {(r["id"], r["field"]) for r in csv.DictReader(open(path, encoding="utf-8")) if not r["reason"].startswith("Definition of the split row")}
new = []
for b in (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14):
    for v in csv.DictReader(open(os.path.join(ROOT, "research", f"verify_out_batch{b}.csv"), encoding="utf-8")):
        if v["overall"] == "correct" or not v["corrected_value"].strip():
            continue
        for fld, val in parse(v["corrected_value"]):
            reason = ("Phase 2 verifier: " if b <= 7 else "Supplied PDF verifier (2026-10-15): " if b <= 13 else "Split row verifier (2026-10-18): ") + v["what_is_wrong"].strip()
            if (v["id"], fld) in OVERRIDE:
                val, reason = OVERRIDE[(v["id"], fld)]
            if (v["id"], fld) not in have:
                new.append({"id": v["id"], "field": fld, "new_value": val, "reason": reason}); have.add((v["id"], fld))
        if v["id"] == "FLD-029" and ("FLD-029", "comparability_warning") not in have:
            new.append({"id": "FLD-029", "field": "comparability_warning", "new_value": "Unreferenced author capability statement in Sec 2.2.2; not a measurement, not tied to GRC-1; do not use as a comparator",
                        "reason": "Phase 2 verifier"}); have.add(("FLD-029", "comparability_warning"))
with open(path, "a", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["id", "field", "new_value", "reason"]); [w.writerow(r) for r in new]
print("appended", len(new), "corrections")
