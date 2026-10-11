# dune-rover

Research project on predicting slip, sinkage and traversability of wheeled (and secondarily legged) robots on dry sand and dunes, with a minimal open-data traversability study for Arabian dune areas. Author: Huda Mueen. Related repository, not duplicated here: [`hudasol/dhill`](https://github.com/hudasol/dhill) (heat-and-dust operating envelope).

**Research, not engineering approval for any real vehicle.**

## Three kinds of content, kept separate

| Label | Meaning | Where |
|---|---|---|
| **PUBLISHED** | A number read in a retrieved source; 144 rows with URL, passage and retrieval date | `research/evidence.csv`, report Appendix A |
| **SIMULATED-BY-ME** | Output of the code here (slip-model traversability map on real elevation data). Model-assumption dependent, never field evidence | `src/dunerover/`, `results/` |
| **PLANNED** | Protocols not yet run | `docs/FIELD_VALIDATION_PLAN.md` |

## Read in this order

1. `docs/EXECUTIVE_BRIEF.md` (also `.pdf`): two pages.
2. `docs/REPORT.md` (also `.pdf`): the full review, taxonomy, gap analysis, simulation study, field plan, limitations, verification, appendices.
3. `docs/NEXT_STEPS.md`: what to do next, starting with the first field experiment.
4. `docs/GLOSSARY.md`: terms for newcomers.
5. `docs/PROTOCOL.md`, `docs/DATA_AND_LICENSES.md`.

## Layout

```
docs/                 report, brief, glossary, protocol, field plan, licences, next steps
docs/src/             hand-written report sections (REPORT.md is assembled from these)
research/evidence.csv the evidence table (one row per reported mobility result)
research/raw/         per-topic notes and row files, data audit, morphology and UAE facts
research/verification_log.md, factcheck_report_pass.md   independent checks
src/dunerover/        simulation code (DEM loading, slope, slip model, graph routing, sensitivity)
scripts/              fetch_data.sh, consolidate_evidence.py, verify_stats.py, build_report.py,
                      analyze_field_runs.py, calibration_identifiability.py, ...
tests/                21 tests
results/              simulation outputs and figures (all labelled SIMULATION ONLY)
data/anchor_points.csv  13 published slip points used only for descriptive comparison
```

## Reproduce the simulation study

Python 3.10 or newer. Dependencies are pinned loosely in `pyproject.toml` (numpy, scipy, matplotlib, tifffile, imagecodecs; pytest for tests).

```bash
pip install -e ".[dev]"          # or: pip install numpy scipy matplotlib tifffile imagecodecs pytest
bash scripts/fetch_data.sh       # downloads two Copernicus GLO-30 tiles (about 97 MB), checks SHA-256
PYTHONPATH=src python3 -m pytest -q tests
PYTHONPATH=src python3 -m dunerover.study --data data/raw --out results   # about 5.5 minutes
PYTHONPATH=src python3 -m dunerover.study --data data/raw --out results --only-area-figures
python3 scripts/build_report.py  # rebuild docs/REPORT.md from docs/src and the CSVs
```

Seeds are fixed (origin-destination 20261011; Latin hypercube 20261012 and 20261013). The full study was run twice during development and the area and sensitivity entries of the two summary files matched.

What the study does: slope from Copernicus GLO-30 (Horn 3 by 3), a friction-circle slip model with three assumption parameters, an 8-neighbour graph and Dijkstra routes, then one-at-a-time and Latin-hypercube sensitivity to find which assumptions change the map most. It does **not** model sinkage, wheel geometry, speed or avalanching, and it was not fitted to any data.

## Data and licences

Full list in `docs/DATA_AND_LICENSES.md`. In short: Copernicus GLO-30 (free with attribution to DLR and Airbus, EU/ESA; the controlling licence text was not read directly, so commercial terms are unverified), numpy and scipy (BSD), matplotlib (PSF-style), tifffile and imagecodecs (BSD-3), pytest (MIT, dev only). Project Chrono (BSD-3) was reviewed but is not used. The DEM tiles are not committed.

**This repository has no licence file yet.** Until you add one, all rights are reserved by default. Choose a licence before sharing publicly.

## Verification summary

Independent re-check of 30 randomly drawn evidence rows plus 7 flagged ones: 0 material errors in 37, 9 minor label or location errors (corrected). The 107 other unflagged rows were not individually re-checked. A second independent check of the report's prose (225 claim groups) found 5 wrong and 26 minor items, all corrected. Details: `research/verification_log.md`, `research/factcheck_report_pass.md`, report section 11.

## Not done

Chrono, DEM and RFT were reviewed, not run. No field data exist yet. No learning model was trained. See report section 10.
