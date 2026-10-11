#!/usr/bin/env python3
"""Turn verifier output (research/verify_out_batch4..7.csv) into rows of research/corrections.csv.

Idempotent: a (id, field) pair already present is skipped.  The verifier's `corrected_value`
column has the form `field=value; field=value`; fields are split only at known column names.
Deterministic; no network.
"""
import csv, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ["vehicle_or_wheel","terrain_description","slope_deg","method","metric","value","unit","validation_type",
          "passage_or_location","comparability_warning","notes"]
pat = re.compile(r"(?:^|;\s+)(" + "|".join(FIELDS) + r")=")
# judgement overrides: the verifier proposed a free-text value in a controlled column
OVERRIDE = {("FLD-029", "validation_type"): ("none",
            "Verifier: the 20 to 30 % at 15 deg is an unreferenced capability statement, not a measurement; no validation type applies")}
def parse(cv):
    parts = pat.split(cv)
    return [(parts[i], parts[i + 1].strip()) for i in range(1, len(parts), 2)]
path = os.path.join(ROOT, "research", "corrections.csv")
have = {(r["id"], r["field"]) for r in csv.DictReader(open(path, encoding="utf-8"))}
new = []
for b in (4, 5, 6, 7):
    for v in csv.DictReader(open(os.path.join(ROOT, "research", f"verify_out_batch{b}.csv"), encoding="utf-8")):
        if v["overall"] == "correct" or not v["corrected_value"].strip():
            continue
        for fld, val in parse(v["corrected_value"]):
            reason = "Phase 2 verifier: " + v["what_is_wrong"].strip()
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
