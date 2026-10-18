"""Error-rate statistics from the independent verification outputs."""
import csv, glob, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rand = {r["id"] for r in csv.DictReader(open(os.path.join(ROOT, "research", "verify_sample_random30.csv"), encoding="utf-8"))}
import re
rows = []
for f in sorted(glob.glob(os.path.join(ROOT, "research", "verify_out_batch*.csv"))):
    nb = int(re.search(r"batch(\d+)", f).group(1))
    for r in csv.DictReader(open(f, encoding="utf-8")):
        r["phase"] = 4 if nb >= 14 else (3 if nb >= 8 else (2 if nb >= 4 else 1)); rows.append(r)
current = {r["id"] for r in csv.DictReader(open(os.path.join(ROOT, "research", "evidence.csv"), encoding="utf-8"))}
supplied = {r["id"] for r in csv.DictReader(open(os.path.join(ROOT, "research", "phase2", "supplied_pdf_rows_2026-10-13.csv"), encoding="utf-8"))}
latest = {}
for r in rows:          # files are read in batch order, so the last verdict per id wins
    latest[r["id"]] = r
cur_rows = [latest[i] for i in sorted(current) if i in latest]
cur_sup = [r for r in cur_rows if r["id"] in supplied or r["id"].startswith("FLD-HV13-5")]
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d
def upper_zero(n, a=0.05):  # exact one-sided upper bound when 0 events
    return 1 - a ** (1 / n)
out = []
grp = (("random sample, phase 1 (n=30 of 137 unflagged)", lambda r: r["phase"] == 1 and r["id"] in rand),
       ("flagged sample, phase 1", lambda r: r["phase"] == 1 and r["id"] not in rand),
       ("remaining rows, phase 2 full re-check", lambda r: r["phase"] == 2),
       ("ALL 144 ROWS", lambda r: r["phase"] in (1, 2)),
       ("supplementary rows from supplied PDFs, phase 3", lambda r: r["phase"] == 3),
       ("ALL 170 ROWS", lambda r: r["phase"] in (1, 2, 3)),
       ("split rows, phase 4", lambda r: r["phase"] == 4))
for name, fn in grp:
    sub = [r for r in rows if fn(r)]; n = len(sub)
    cnt = {k: sum(r["overall"] == k for r in sub) for k in ("correct", "minor_error", "material_error", "unverifiable")}
    out.append((name, n, cnt))
for name, sub in (("CURRENT TABLE, latest verdict per row", cur_rows), ("CURRENT SUPPLEMENTARY ROWS, latest verdict per row", cur_sup)):
    out.append((name, len(sub), {k: sum(r["overall"] == k for r in sub) for k in ("correct", "minor_error", "material_error", "unverifiable")}))
assert out[3][1] == 144 and out[4][1] == 26 and out[5][1] == 170
assert out[7][1] == len(current) and all(i in latest for i in current), "every current row needs a verdict"
lines = ["# Verification log", "", f"Every one of the {len(current)} rows of the current evidence table has been re-checked against its source by a separate subagent that re-read the source and had no access to the extraction notes.",
         "Phase 1 (2026-10-11): 30 rows drawn at random (seed 20261011) from the 137 unflagged rows, plus the 7 rows the extractors flagged. Phase 2 (2026-10-12): the other 107 rows, in four batches (batches 4 to 7).",
         "Phase 3 (2026-10-15): the 26 rows read from the PDFs the author supplied (Yu 2024, Takehana 2025, Ishigami 2007, Ishigami 2009, Heverly 2013), in six batches (batches 8 to 13), one verifier per source block. Verifiers saw the claim fields only, not the notes or comparability warnings.",
         "Phase 4 (2026-10-18): FLD-HV13-5, which mixed lab and field results, was split at the author's request into FLD-HV13-5a (lab, JPL Marsyard) and FLD-HV13-5b (field, Tecopa); one fresh verifier checked both (batch 14).",
         "Two views are reported. 'ALL 170 ROWS' is the first check of the rows as extracted (FLD-HV13-5 counts with its material error). 'CURRENT TABLE' takes each row of the current table with its latest verdict (the two split rows with their phase 4 verdicts; FLD-HV13-5 is no longer in the table).",
         "Definitions: material error = wrong value, unit, metric meaning, validation type, vehicle/terrain or slope; minor error = number right but a label, section reference or descriptive detail wrong.", ""]
for name, n, c in out:
    lines.append(f"## {name} (n = {n})")
    lines.append(f"- correct {c['correct']}, minor {c['minor_error']}, material {c['material_error']}, unverifiable {c['unverifiable']}")
    k = c["material_error"]
    lines.append(f"- material error rate {k}/{n} = {100*k/n:.1f} %" + (f" (exact 95 % upper bound {100*upper_zero(n):.1f} %)" if k == 0 else f" (Wilson 95 % CI {100*wilson(k,n)[0]:.1f} to {100*wilson(k,n)[1]:.1f} %)"))
    k2 = c["minor_error"] + c["material_error"]
    lo, hi = wilson(k2, n)
    lines.append(f"- any discrepancy rate {k2}/{n} = {100*k2/n:.1f} % (Wilson 95 % CI {100*lo:.1f} to {100*hi:.1f} %)")
    lines.append("")
lines += ["## What this does and does not show",
          "- The phase 1 random sample (0 material in 30, upper bound 9.5 %) understated the table wide rate: the 107 rows checked in phase 2 had 6 material errors (5.6 %). The bound held, but the point estimate was optimistic.",
          "- Six of the original 144 rows had a material error before correction; all six are corrected in the table. The 'ALL 144' and 'ALL 170' rates are pre correction error rates of the extraction, not of the corrected table.",
          "- Phase 3: 3 of the 26 supplementary rows had a material error, all on validation type (TM-TK5 and TM-IS07-5 labelled as comparisons although no simulation was compared; FLD-HV13-5 labelled field although two of its three numbers come from the JPL Marsyard). The values themselves were right in all 26 rows. Minor errors were mostly page and section labels and one terrain wording (sand called dry where the source does not say so, TM-YU1 to TM-YU4).",
          "- Phase 3 used supplied PDFs read through a text layer; no page images could be rendered, so values read only from figures were checked against the text, not the plot.",
          "- Minor errors (labels, sections, descriptive details) were common; the corrected table still carries the risk that a verifier shared a blind spot with the extractor.",
          "- Verifiers are language model agents using the same search tools; they re read sources but may share blind spots with the extractors, for example on figure-only values. A human spot check of a few rows remains advisable.",
          "- Material errors found in phase 2: wrong wheel count (LRN-017), validation type lab versus field (SIM-012, LRN-006), lab versus sim-vs-lab (LRN-019), a best case labelled as worst case (TM-020), an unreferenced capability statement presented as a measurement (FLD-029). SIM-013 was set to lab for consistency with SIM-012.", "",
          "## Row level verdicts other than correct"]
for r in rows:
    if r["overall"] != "correct":
        lines.append(f"- {r['id']} (phase {r['phase']}): {r['overall']}: {r['what_is_wrong']}")
open(os.path.join(ROOT, "research", "verification_log.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
import json
stats = {}
for name, n, c in out:
    k, k2 = c["material_error"], c["minor_error"] + c["material_error"]
    stats[name] = {"n": n, **c, "material_rate": k / n, "material_wilson95": wilson(k, n) if k else None, "material_upper95_exact": upper_zero(n) if k == 0 else None,
                   "any_rate": k2 / n, "any_wilson95": wilson(k2, n)}
json.dump(stats, open(os.path.join(ROOT, "research", "verification_stats.json"), "w"), indent=1)
print("\n".join(lines[:24]))
