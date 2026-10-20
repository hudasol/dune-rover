#!/usr/bin/env bash
# Local gate run before every push: tests, hygiene, secrets, writing rules, stale generated files.
set -e
cd "$(dirname "$0")/.."
PYTHONPATH=src python3 -m pytest -q tests
python3 scripts/check_repo_hygiene.py
python3 scripts/scan_secrets.py
python3 scripts/consolidate_evidence.py > /dev/null
python3 scripts/verify_stats.py > /dev/null
PYTHONPATH=src python3 scripts/build_report.py > /dev/null
git diff --ignore-cr-at-eol --exit-code -- README.md docs/REPORT.md docs/EXECUTIVE_BRIEF.md docs/PROPOSAL_EDGE.md research/ || { echo "generated files are stale: commit the regenerated files"; exit 1; }
python3 - <<'PY'
import subprocess, sys
bad = []
for f in subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], capture_output=True, text=True).stdout.split():
    if not f.endswith((".md", ".py", ".csv", ".txt", ".json", ".yml")) or f == "scripts/scan_secrets.py":
        continue
    t = open(f, encoding="utf-8", errors="ignore").read()
    for w in (chr(0x2014), chr(0x2013), "Stir" + "ling", "Clau" + "de"):
        if w in t:
            bad.append((f, repr(w)))
print("\n".join(f"{f}: {w}" for f, w in bad) or "writing check: ok")
sys.exit(1 if bad else 0)
PY
echo "local gate: ok"
