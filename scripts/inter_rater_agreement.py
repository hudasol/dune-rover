#!/usr/bin/env python3
"""Agreement between Huda's blinded verdicts and the verifier agents' verdicts on the inter rater sample.

    python3 scripts/inter_rater_agreement.py

Reads research/spot_check_inter_rater_ratings.csv (Huda) and the latest verifier verdict per row
(research/verify_out_batch*.csv).  The sheet shows each row as it is now; rows corrected after verification
(research/corrections.csv) are reported separately, because the verifier judged them before the correction.  Reports raw agreement and Cohen's kappa on three classes (correct, minor_error,
material_error; unverifiable rows are excluded and counted) and on two classes (material or not).  Writes
research/inter_rater_agreement.md.
"""
import csv, glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def kappa(a, b, labels):
    n = len(a)
    if n == 0:
        return float("nan"), float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


def main():
    h = {r["id"]: r["huda_verdict"].strip() for r in csv.DictReader(open(os.path.join(ROOT, "research", "spot_check_inter_rater_ratings.csv"), encoding="utf-8"))}
    latest = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "research", "verify_out_batch*.csv")), key=lambda p: int(re.search(r"batch(\d+)", p).group(1))):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            latest[r["id"]] = r["overall"].strip()
    # the sheet shows the CURRENT (corrected) row; the verifier judged the row BEFORE correction.  Rows corrected after
    # verification are therefore compared separately: for them the expected human verdict is 'correct'.
    corrected = {c["id"] for c in csv.DictReader(open(os.path.join(ROOT, "research", "corrections.csv"), encoding="utf-8"))
                 if not c["reason"].startswith("Definition of the split row")}
    corr_rows = [(i, h[i]) for i in h if h[i] and i in corrected]
    pairs = [(h[i], latest.get(i, "")) for i in h if h[i] and latest.get(i) and i not in corrected]
    if not pairs:
        print("no ratings yet: fill research/spot_check_inter_rater_ratings.csv first"); return
    keep = [(a, b) for a, b in pairs if "unverifiable" not in (a, b)]
    a3, b3 = [x for x, _ in keep], [y for _, y in keep]
    po3, k3 = kappa(a3, b3, ["correct", "minor_error", "material_error"])
    a2 = ["material" if x == "material_error" else "not" for x in a3]; b2 = ["material" if y == "material_error" else "not" for y in b3]
    po2, k2 = kappa(a2, b2, ["material", "not"])
    lines = ["# Inter rater agreement (generated)", "", f"Rated rows not corrected after verification: {len(pairs)}; excluded as unverifiable by either rater: {len(pairs) - len(keep)}.",
             f"Rows corrected after verification (expected human verdict: correct): {len(corr_rows)}, of which the human rated correct: {sum(v == 'correct' for _, v in corr_rows)}.",
             f"- Three classes: raw agreement {po3:.2f}, Cohen's kappa {k3:.2f} (n = {len(keep)}).",
             f"- Material or not: raw agreement {po2:.2f}, Cohen's kappa {k2:.2f}.", "", "| id | Huda | verifier |", "|---|---|---|"]
    lines += [f"| {i} | {h[i]} | {latest.get(i, '')} |" for i in h if h[i]]
    open(os.path.join(ROOT, "research", "inter_rater_agreement.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines[:5]))


if __name__ == "__main__":
    main()
