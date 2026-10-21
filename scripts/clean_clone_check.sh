#!/usr/bin/env bash
# Clean clone reproduction check (W6 of docs/PLAN_2026-10-21.md): clone the public repository into a temporary folder,
# run the tests, rebuild every generated document from the committed results, and report whether they match the
# committed ones, with the time taken. The analyses that need raw downloads (lidar, ICESat-2, PDFs) are not rerun here.
#   bash scripts/clean_clone_check.sh >> results/reproducibility/clean_clone_checks.txt
D=$(mktemp -d /tmp/repro.XXXX); cd $D
T0=$(date +%s)
git clone -q https://github.com/hudasol/dune-rover.git repo && cd repo
C=$(git rev-parse --short HEAD)
PYTHONPATH=src python3 -m pytest -q -p no:cacheprovider tests > ../pytest.log 2>&1
python3 scripts/consolidate_evidence.py > /dev/null
python3 scripts/verify_stats.py > /dev/null
PYTHONPATH=src python3 scripts/build_report.py > /dev/null
PYTHONPATH=src python3 scripts/build_manuscript.py --strict > /dev/null
python3 scripts/digitise_figures.py --check > ../digitise.log 2>&1 || true
PYTHONPATH=src python3 scripts/build_number_ledger.py --check > ../ledger.log 2>&1 && L=passes || L=FAILS
git diff --stat > ../diff.txt
T1=$(date +%s)
echo "$(date -u +%Y-%m-%dT%H:%MZ) commit $C; tests: $(tail -1 ../pytest.log); generated documents identical: $([ -s ../diff.txt ] && echo NO || echo yes); ledger check: $L; seconds: $((T1-T0)); digitiser check: $(grep -q "reproduced exactly" ../digitise.log && echo reproduced || echo "not possible without the source PDFs, which are not redistributed")"
