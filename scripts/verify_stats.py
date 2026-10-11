"""Error-rate statistics from the independent verification outputs."""
import csv, glob, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rand = {r["id"] for r in csv.DictReader(open(os.path.join(ROOT, "research", "verify_sample_random30.csv"), encoding="utf-8"))}
rows = []
for f in sorted(glob.glob(os.path.join(ROOT, "research", "verify_out_batch*.csv"))):
    rows += list(csv.DictReader(open(f, encoding="utf-8")))
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d
def upper_zero(n, a=0.05):  # exact one-sided upper bound when 0 events
    return 1 - a ** (1 / n)
out = []
for name, ids in (("random sample", rand), ("flagged sample", {r["id"] for r in rows} - rand)):
    sub = [r for r in rows if r["id"] in ids]; n = len(sub)
    cnt = {k: sum(r["overall"] == k for r in sub) for k in ("correct", "minor_error", "material_error", "unverifiable")}
    out.append((name, n, cnt))
lines = ["# Verification log", "", "Independent re-check by three separate subagents that re-fetched sources and had no access to the extraction notes.",
         "Sample: 30 rows drawn at random (seed 20261011) from the 137 rows not flagged by the extractors, plus all 7 rows the extractors flagged as weakly supported.",
         "Definitions: material error = wrong value, unit, metric meaning, validation type, vehicle/terrain or slope; minor error = number right but a label, section reference or descriptive detail wrong.", ""]
for name, n, c in out:
    lines.append(f"## {name} (n = {n})")
    lines.append(f"- correct {c['correct']}, minor {c['minor_error']}, material {c['material_error']}, unverifiable {c['unverifiable']}")
    k = c["material_error"]
    lines.append(f"- material-error rate {k}/{n} = {100*k/n:.1f} %" + (f" (exact 95 % upper bound {100*upper_zero(n):.1f} %)" if k == 0 else f" (Wilson 95 % CI {100*wilson(k,n)[0]:.1f}-{100*wilson(k,n)[1]:.1f} %)"))
    k2 = c["minor_error"] + c["material_error"]
    lo, hi = wilson(k2, n)
    lines.append(f"- any-discrepancy rate {k2}/{n} = {100*k2/n:.1f} % (Wilson 95 % CI {100*lo:.1f}-{100*hi:.1f} %)")
    lines.append("")
lines += ["## What this does and does not show", "- The 30-row sample is 21 % of the 144-row table; the other 107 unflagged rows were not individually re-checked.",
          "- Zero material errors in 30 rows is compatible with a true material-error rate up to about 10 % (exact one-sided 95 % bound 9.5 %); it does not show the table is error-free.",
          "- Minor errors (labels, sections) were common (see the any-discrepancy rate), so expect similar label slips in unchecked rows.",
          "- Verifiers are language-model agents using the same search tools; they re-fetched the sources but may share blind spots with the extractors, for example on figure-only values.", "",
          "## Row-level non-correct verdicts"]
for r in rows:
    if r["overall"] != "correct":
        lines.append(f"- {r['id']} ({'random' if r['id'] in rand else 'flagged'}): {r['overall']}: {r['what_is_wrong']}")
open(os.path.join(ROOT, "research", "verification_log.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines[:18]))
