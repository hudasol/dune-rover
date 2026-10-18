"""Merge per-area evidence rows into research/evidence.csv.

Fixes one malformed row (LEG-015, unquoted comma), removes cross-agent duplicates
(logged in research/dedup_log.md), and flags rows the extracting agents marked as
weakly supported. Deterministic; no randomness.
"""
import csv, glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "research", "raw")
HEADER = ["id","vehicle_or_wheel","terrain_description","soil_parameters_reported","slope_deg","method",
          "method_family","metric","value","unit","validation_type","source_title","source_url",
          "passage_or_location","retrieval_date","comparability_warning","notes"]
DROP = {  # id -> reason
 "TM-025":"duplicate of SIM-026 (Ding wheel data, arXiv 2606.21755); validation type there is sim-vs-lab",
 "TM-026":"duplicate of SIM-026 (sinkage part)",
 "TM-027":"duplicate of SIM-025 (Rashid wheel, arXiv 2606.21755)",
 "TM-028":"duplicate of SIM-027 (Wang and Han wheel, arXiv 2606.21755)",
 "LRN-023":"duplicate of LEG-007 (same source and values, arXiv 2603.06928)",
 "TM-030":"duplicate of SIM-010 (same 7.4 % value, arXiv 2507.05643)",
}
FLAG_PAT = re.compile(r"unverified|garbled|abstract[- ]only|press release|re-?check|ambiguous|not retrieved in full|secondary", re.I)

def read_rows(path):
    rd = csv.reader(open(path, encoding="utf-8")); h = next(rd); out = []
    for row in rd:
        if row and row[0] == "LEG-015" and len(row) == 18:   # unquoted comma in passage field
            row = row[:13] + [row[13] + "," + row[14]] + row[15:]
        if len(row) != 17:
            raise SystemExit(f"malformed row {row[0] if row else '?'} in {path}: {len(row)} fields")
        out.append(dict(zip(HEADER, row)))
    return out

rows = []
for f in sorted(glob.glob(os.path.join(RAW, "*_rows.csv"))):
    if os.path.basename(f).startswith("morphology"): continue
    area = os.path.basename(f).replace("_rows.csv", "")
    for r in read_rows(f):
        r["area"] = area; rows.append(r)
# rows read from PDFs the author supplied (2026-10-13), verified 2026-10-15 (batches 8 to 13)
for f in sorted(glob.glob(os.path.join(ROOT, "research", "phase2", "supplied_pdf_rows_*.csv"))):
    for r in read_rows(f):
        r["area"] = {"TM": "terramechanics", "FLD": "field", "SIM": "simulation", "LRN": "learning", "LEG": "legged"}[r["id"].split("-")[0]]
        rows.append(r)
kept = [r for r in rows if r["id"] not in DROP]
for r in kept:
    r["evidence_label"] = "PUBLISHED"
    text = " ".join([r["comparability_warning"], r["notes"], r["passage_or_location"]])
    r["recheck_flag"] = "yes" if FLAG_PAT.search(text) else ""
prefix_order = {"terramechanics":0,"simulation":1,"learning":2,"field":3,"legged":4}
# ---- verification overlay: corrections and verdicts (research/corrections.csv, research/verify_out_batch*.csv)
corr_path = os.path.join(ROOT, "research", "corrections.csv")
by_id = {r["id"]: r for r in kept}
applied, splits, split_new = [], [], set()
if os.path.exists(corr_path):
    for c in csv.DictReader(open(corr_path, encoding="utf-8")):
        if c["field"] == "split_into":   # replace one row by several (ids separated by ';'), each starting as a copy
            src = by_id.pop(c["id"]); kept.remove(src)
            for nid in c["new_value"].split(";"):
                r = dict(src); r["id"] = nid; kept.append(r); by_id[nid] = r; split_new.add(nid)
            splits.append((c["id"], c["new_value"], c["reason"]))
            continue
        r = by_id[c["id"]]
        if c["id"] not in split_new:      # fields of a split row define it; they are not verifier corrections
            applied.append((c["id"], c["field"], r[c["field"]]))
        r[c["field"]] = c["new_value"]
random_ids = set(r["id"] for r in csv.DictReader(open(os.path.join(ROOT, "research", "verify_sample_random30.csv"), encoding="utf-8"))) if os.path.exists(os.path.join(ROOT, "research", "verify_sample_random30.csv")) else set()
for r in kept:
    r["verification"] = "not individually verified"
for f in sorted(glob.glob(os.path.join(ROOT, "research", "verify_out_batch*.csv"))):
    for v in csv.DictReader(open(f, encoding="utf-8")):
        if v["id"] in by_id:
            n = int(re.search(r"batch(\d+)", f).group(1))
            if n >= 14:
                grp, date = "split row check", "2026-10-18"
            elif n >= 8:
                grp, date = "supplied PDF re-check", "2026-10-15"
            elif n >= 4:
                grp, date = "full re-check, phase 2", "2026-10-12"
            else:
                grp, date = ("random sample" if v["id"] in random_ids else "flagged sample"), "2026-10-11"
            by_id[v["id"]]["verification"] = f"verified {date} ({grp}): {v['overall']}" + (" (corrected)" if any(a[0] == v["id"] for a in applied) else "")
            by_id[v["id"]]["recheck_flag"] = ""
kept.sort(key=lambda r: (prefix_order[r["area"]], r["id"]))
cols = HEADER + ["area","evidence_label","recheck_flag","verification"]
with open(os.path.join(ROOT, "research", "evidence.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(kept)
with open(os.path.join(ROOT, "research", "dedup_log.md"), "w", encoding="utf-8") as fh:
    fh.write("# Dedup log\n\n")
    for k, v in DROP.items(): fh.write(f"- {k}: dropped, {v}\n")
    fh.write("\nLEG-015 repaired: unquoted comma had split the passage field.\n")
    for old, new, why in splits: fh.write(f"\n{old} split into {new.replace(';', ' and ')}: {why}\n")
    fh.write("\n## Corrections applied from independent verification (old values)\n")
    for i, f, old in applied: fh.write(f"- {i}.{f}: was: {old}\n")
import collections
print("kept", len(kept), "dropped", len(rows) - len(kept))
print(collections.Counter(r["validation_type"] for r in kept))
print("recheck-flagged:", [r["id"] for r in kept if r["recheck_flag"]])
print("distinct sources:", len({r["source_url"] for r in kept}))
