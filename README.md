# dune-rover

Research project on predicting slip, sinkage and traversability of wheeled (and secondarily legged) robots on dry sand and dunes, with a minimal open data traversability study for Arabian dune areas. Author: Huda Mueen. Related repository, not duplicated here: [`hudasol/dhill`](https://github.com/hudasol/dhill) (heat and dust operating envelope).

**Research, not engineering approval for any real vehicle.** Generated from `docs/src/readme_template.md` by `scripts/build_report.py`; numbers come from the result files.

## What is published, what is simulated, what is planned

| Label | Meaning | Where |
|---|---|---|
| **PUBLISHED** | A number read in a retrieved source: 170 rows with URL, passage, retrieval date and an independent re check | `research/evidence.csv`, report Appendix A |
| **SIMULATED BY ME** | Output of the code here: a slip model on real Copernicus GLO-30 elevation data, a sub grid slip face detector trained on synthetic dunes, a three class map (TRAVERSABLE, BLOCKED, UNKNOWN) and synthetic tests of the field analysis. Model assumption dependent, never field evidence | `src/dunerover/`, `results/` |
| **PLANNED** | A slope ladder field experiment, its pre data predictions, checklist, rover options and two proposal outlines (no agreement exists with anyone). Nothing here has been run | `docs/FIELD_VALIDATION_PLAN.md`, `docs/predictions/`, `docs/FIELD_DAY_CHECKLIST.md`, `docs/ROVER_OPTIONS.md`, `docs/PROPOSAL_SEED.md`, `docs/PROPOSAL_EDGE.md` |

## Headline numbers (from files)

- Verification: all 170 evidence rows re checked against their sources; material errors 9 of 170 (5.3 %), any discrepancy 51 of 170 (30.0 %); for the 26 rows read from supplied PDFs alone, material 3 of 26 (11.5 %, all on validation type), any discrepancy 15 of 26 (57.7 %); all corrected (`research/verification_log.md`).
- Simulation, 30 m: UNKNOWN share 8.6 % (A south Liwa), 10.9 % (B megadunes), 2.5 % (C linear dunes, Saudi Arabia); BLOCKED under 0.1 %; 99.1 % of cells in A have the same slope based verdict under all 256 draws of the four assumed parameters. If a face within one post of the cell counts (post hoc variant), UNKNOWN is 34.4 %, 32.2 %, 22.0 %. **Simulation only, model assumption dependent; the detector is validated against synthetic truth only.**
- Published anchors (comparison of unlike vehicles and soils, report section 8.8): the Dumont Dunes slip curve (PUBLISHED, FLD-HV13-1) crosses 50 % slip at 12.6 degrees, the nominal model at 25.5 degrees; with Ishigami 2009 Table I values the model gives 0.22 to 0.40 slip on a 10 degree side slope where a slip ratio of about 0.5 was measured (TM-IS09-3). **The model predicts too little slip on sand slopes. Simulation only, model assumption dependent.**
- Pre registered predictions and their hits and misses: `docs/PREDICTIONS.md`.

## Read in this order

1. `docs/EXECUTIVE_BRIEF.md` (also `.pdf`): two pages.
2. `docs/REPORT.md` (also `.pdf`): the full review, taxonomy, gap analysis, simulation studies (sections 8 and 8.7), field plan, limitations, verification, appendices.
3. `docs/NEXT_STEPS.md`: what to do next, starting with the first field experiment, and what to fetch.
4. `docs/PREDICTIONS.md`, `docs/predictions/`: dated predictions written before runs.
5. `docs/GLOSSARY.md`, `docs/PROTOCOL.md`, `docs/DATA_AND_LICENSES.md`.

## Layout

```
docs/                 report, brief, glossary, protocol, field plan, checklist, rover options, proposal seed, licences
docs/src/             hand written report sections and templates (REPORT.md, the brief and this README are built from them)
docs/predictions/     dated pre-data slope ladder predictions (PLANNED field experiment)
research/evidence.csv the evidence table (one row per reported mobility result)
research/raw/         per-topic notes and row files, data audit, morphology and UAE facts
research/phase2/      phase 2 retrieval reports and CSVs (morphology, rover options); downloaded sources are not committed
src/dunerover/        simulation code (DEM, slope, slip model, graph routing, sensitivity, sub-grid detector, three class map, field analysis)
scripts/              fetch_data.sh, consolidate_evidence.py, ingest_verification.py, verify_stats.py, build_report.py,
                      analyze_field_runs.py, field_analysis_power.py, make_ladder_predictions.py, check_repo_hygiene.py, scan_secrets.py ...
tests/                52 tests
results/              simulation outputs and figures (all labelled SIMULATION ONLY); results/subgrid, results/field_kit
data/anchor_points.csv  13 published slip points used only for descriptive comparison
```

## Reproduce

Python 3.10 or newer. Dependencies: numpy, scipy, matplotlib, tifffile, imagecodecs; pytest for tests.

```bash
pip install -e ".[dev]"          # or: pip install numpy scipy matplotlib tifffile imagecodecs pytest
bash scripts/fetch_data.sh       # downloads three Copernicus GLO-30 tiles (about 146 MB), checks SHA-256
PYTHONPATH=src python3 -m pytest -q tests
PYTHONPATH=src python3 -m dunerover.study --data data/raw --out results                    # phase 1, about 5.5 minutes
PYTHONPATH=src python3 -m dunerover.study_subgrid --data data/raw --out results/subgrid    # phase 2, about 5 minutes
PYTHONPATH=src python3 scripts/field_analysis_power.py                                      # synthetic power study, about 1 minute
python3 scripts/consolidate_evidence.py && python3 scripts/verify_stats.py                  # evidence table and verification log from files
python3 scripts/build_report.py  # rebuilds docs/REPORT.md, the brief and this README from docs/src, the CSVs and results
python3 scripts/check_repo_hygiene.py --history && python3 scripts/scan_secrets.py --history
```

Seeds are fixed and listed in `results/summary.json` and `results/subgrid/summary.json`. Phase 2 was run twice and the CSVs matched.

## Data and licences

Full list in `docs/DATA_AND_LICENSES.md`. Copernicus GLO-30 (the controlling Free and Open licence was read in full; attribution and no liability notices required; no commercial restriction in the text), numpy, scipy, matplotlib, tifffile, imagecodecs, pytest (permissive). The DEM tiles are not committed. Source PDFs and raw downloads are never committed: a CI job fails if they are.

**Licence:** all rights reserved. The repository is public for reading and review; please contact the author before any use, modification, distribution or sale (`LICENSE`, `LICENSE-DOCS.md`).

## Not done

Chrono, DEM and RFT were reviewed, not run. No field data exist. No learning model was trained. The sub grid detector has not been compared with any real slip face profile. See report section 10.
