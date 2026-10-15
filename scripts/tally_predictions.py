#!/usr/bin/env python3
"""Count hits and misses in docs/PREDICTIONS.md (first word of the Outcome column).  Prints a markdown table."""
import os, re, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def tally(path=None):
    path = path or os.path.join(ROOT, "docs", "PREDICTIONS.md")
    stages = collections.OrderedDict(); cur = None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"## (Stage \d+)", line)
        if m: cur = m.group(1); stages[cur] = collections.Counter(); continue
        m = re.match(r"\| ([A-Z]+\d-\d+) \|", line)
        if cur and m:
            cells = [c.strip() for c in line.rstrip().strip("|").split("|")]
            mw = re.match(r"([A-Z]+)", cells[-1])
            w = mw.group(1) if mw else ""
            stages[cur]["HIT" if w == "HIT" else "MISSED" if w.startswith("MISSED") else "MIXED" if w in ("MIXED", "PARTLY") else "PENDING"] += 1
    return stages
if __name__ == "__main__":
    t = tally()
    print("| Stage | HIT | MIXED (part hit) | MISSED | pending |\n|---|---|---|---|---|")
    for k, c in t.items(): print(f"| {k} | {c['HIT']} | {c['MIXED']} | {c['MISSED']} | {c['PENDING']} |")
