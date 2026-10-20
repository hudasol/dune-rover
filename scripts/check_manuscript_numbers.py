#!/usr/bin/env python3
"""Check that every number typed by hand in manuscript/src/manuscript.md has a written justification in
manuscript/src/hand_numbers.csv; every other number comes from a result file through a {{VAL:...}} placeholder,
and the generated manuscript must have no unresolved placeholder.  Exit 1 on any failure.

    python3 scripts/check_manuscript_numbers.py
"""
import csv, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = open(os.path.join(ROOT, "manuscript", "src", "manuscript.md"), encoding="utf-8").read()
t = re.sub(r"\{\{[^}]*\}\}", "", t); t = re.sub(r"`[^`]*`", "", t)
t = re.sub(r"\b(?:FLD|TM|SIM|LRN|LEG|PLN|TM3|MOB|SND|DUN|MAP|ENV)-[A-Za-z0-9-]+", "", t)
tokens = set(re.findall(r"(?<![A-Za-z_])\d+(?:\.\d+)?", t))
ok = {r["token"]: r["justification"] for r in csv.DictReader(open(os.path.join(ROOT, "manuscript", "src", "hand_numbers.csv"), encoding="utf-8"))}
missing = sorted(tokens - set(ok), key=float)
gen = os.path.join(ROOT, "manuscript", "MANUSCRIPT.md")
left = re.findall(r"\{\{[^}]*\}\}", open(gen, encoding="utf-8").read()) if os.path.exists(gen) else ["MANUSCRIPT.md missing"]
print(f"hand typed numbers: {len(tokens)}, justified: {len(tokens) - len(missing)}")
if missing:
    print("UNJUSTIFIED:", missing)
if left:
    print("UNRESOLVED in MANUSCRIPT.md:", sorted(set(left)))
sys.exit(1 if missing or left else 0)
