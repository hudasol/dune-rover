#!/usr/bin/env python3
"""POST HOC (added after the midpoint review of 2026-10-20): compare planning policies on matched pairs, that is only
the origin and destination pairs the conservative policy could route, so a policy is not credited for refusing hard
pairs.  Reads results/planner/routes.csv (3 m baseline, registered) and results/planner/posthoc_baseline_10m/routes.csv.
Output: results/planner/matched_pairs.csv.  SIMULATED BY ME.
"""
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = []
for base, path in (("3 m (registered)", "results/planner/routes.csv"), ("10 m (post hoc)", "results/planner/posthoc_baseline_10m/routes.csv")):
    rows = list(csv.DictReader(open(os.path.join(ROOT, path))))
    for site in ("Dumont", "WhiteSands", "Kelso"):
        for k in ("30", "10"):
            R = {(r["policy"], r["pair"]): r for r in rows if r["site"] == site and r["posting_m"] == k}
            pairs = [p for (pol, p), r in R.items() if pol == "conservative" and r["routed"] == "True"]
            rec = {"grade_baseline": base, "site": site, "posting_m": k, "pairs_total": len({p for _, p in R}), "pairs_routed_by_conservative": len(pairs)}
            for pol in ("naive", "conservative", "risk_weighted"):
                v = [R[(pol, p)]["fails_on_truth"] == "True" for p in pairs if R[(pol, p)]["routed"] == "True"]
                rec[f"{pol}_fail_share"] = round(sum(v) / len(v), 4) if v else ""
            out.append(rec)
with open(os.path.join(ROOT, "results", "planner", "matched_pairs.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for r in out:
    print(r)
