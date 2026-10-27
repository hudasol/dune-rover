# dune-rover

Research project on predicting slip, sinkage and traversability of wheeled (and secondarily legged) robots on dry sand and dunes, with a minimal open data traversability study for Arabian dune areas. Author: Huda Mueen. Related repository, not duplicated here: [`hudasol/dhill`](https://github.com/hudasol/dhill) (heat and dust operating envelope).

**Research, not engineering approval for any real vehicle.** Generated from `docs/src/readme_template.md` by `scripts/build_report.py`; numbers come from the result files.

## What is published, what is simulated, what is planned

| Label | Meaning | Where |
|---|---|---|
| **PUBLISHED** | A number read in a retrieved source: 510 rows from 176 sources with URL, passage, retrieval date and an independent re check; 26 digitised published curves | `research/evidence.csv`, `research/phase3/curves.csv`, report Appendix A |
| **SIMULATED BY ME** | Output of the code here: a slip model on real Copernicus GLO-30 elevation data, four slip model families and two built on the granular scaling laws tested on published curves (none passed the pre registered bar), a Project Chrono single wheel simulation, a sub grid slip face detector and three class map tested against one metre lidar of real dunes, route planning policies, and synthetic tests of the field analysis. Model assumption dependent, never field evidence | `src/dunerover/`, `results/`, `manuscript/` |
| **PLANNED** | A slope ladder field experiment, its pre data predictions, checklist, rover options and proposals (seed, EDGE, AAU field day, robotics project; no agreement exists with anyone). Nothing here has been run | `docs/FIELD_VALIDATION_PLAN.md`, `docs/predictions/`, `docs/FIELD_DAY_CHECKLIST.md`, `docs/ROVER_OPTIONS.md`, `docs/PROPOSAL_SEED.md`, `docs/PROPOSAL_EDGE.md` |

## Dune Rover Planner (the product)

The study is packaged as a planning tool: give it a dune elevation model (Copernicus GLO-30, lidar or a drone survey) and a vehicle profile, and it returns a slip face risk map, a three class map (TRAVERSABLE, BLOCKED, UNKNOWN), routes under three policies and a self contained HTML report. A resolution gate built from the lidar tests refuses to call ground coarser than 10 m verified traversable (a 30 m map called 36 % to 80 % of the face cells TRAVERSABLE on 6 lidar dune fields), and `dunerover vehicle calibrate` turns the rover's own slope runs into a measured profile. **SIMULATED BY ME**, not a safety case.

```
pip install ".[projected]"
dunerover demo --out demo_out
dunerover plan DEM.tif --posting 10 --start LON,LAT --goal LON,LAT --vehicle assumed --out out
```

User guide: `docs/PLANNER.md`. Interactive demonstration on four lidar dune fields: `demo/web/dune_rover_planner.html`. Report section 15.

## Headline numbers (from files)

- **2026-10-21 (report section 14; every number traced in `docs/NUMBER_LEDGER.csv`):** on 49 published curves from 10 studies no slip model family passes (median held out error 0.20 to 0.22), and families built on the granular scaling laws do worse (0.31 to 0.34); Chrono calibrated on the Dumont curve up to 12.5 degrees gave no usable prediction of steeper slopes (numerically unstable there); on 6 lidar dune fields a 30 m map labels TRAVERSABLE 36 % to 80 % of face cells; over Liwa and the Rub' al Khali, 29 % to 52 % of screened steep ICESat-2 crossings fall in TRAVERSABLE cells, against more than 90 % of all segments (post hoc; method not validated, many steep segments are noise); in simulation, replanning on an online slip estimate shows no benefit distinguishable from a stop and retry control (post hoc). Field kit, preregistration draft, drone and sand protocols, and a ROS 2 demonstration are in the repository. Completeness: see `docs/COMPLETENESS.md`.
- **2026-10-20 (SIMULATED BY ME against PUBLISHED data; report section 13, `manuscript/MANUSCRIPT.md`):** slip model families calibrated on other studies predict a held out study with median errors of 0.20 to 0.24 slip (exponential fails (held out median 0.24); Mohr Coulomb ratio fails (held out median 0.23); logistic fails (held out median 0.24); Bekker Wong fails (held out median 0.20); bar 0.15). Against one metre lidar of three dune fields, 25.6 % to 28.6 % of the cells the 30 m map calls TRAVERSABLE contain steep faces (1.8 % to 3.6 % at 10 m). Completeness: `docs/COMPLETENESS.md`.

- Verification: all 510 evidence rows re checked against their sources. First check of the 170 rows as extracted: material errors 9 of 170 (5.3 %), any discrepancy 51 of 170 (30.0 %); of these, the 26 rows read from supplied PDFs had 3 material (11.5 %, all on validation type). Current table, latest verdict per row (FLD-HV13-5 split into a lab and a field row): material 38 of 510 (7.5 %); current supplementary rows 2 of 27 (7.4 %). Every material error corrected (`research/verification_log.md`).
- Simulation, 30 m: UNKNOWN share 8.6 % (A south Liwa), 10.9 % (B megadunes), 2.5 % (C linear dunes, Saudi Arabia); BLOCKED under 0.1 %; 99.1 % of cells in A have the same slope based verdict in at least 95 % of the 256 draws of the four assumed parameters (under the original ranges; not under the widened ranges below). If a face within one post of the cell counts (post hoc variant), UNKNOWN is 34.4 %, 32.2 %, 22.0 %. **Simulation only, model assumption dependent; the detector was validated against synthetic truth in phase 2 and tested against North American lidar on 2026-10-20 (it fails at 30 m).**
- Published anchors (comparison of unlike vehicles and soils, report section 8.8): the Dumont Dunes slip curve (PUBLISHED, FLD-HV13-1) crosses 50 % slip at 12.6 degrees, the nominal model at 25.5 degrees; with Ishigami 2009 Table I values the model gives 0.22 to 0.40 slip on a 10 degree side slope where a slip ratio of about 0.5 was measured (TM-IS09-3). **The model predicts too little slip on sand slopes. Simulation only, model assumption dependent.**
- Widened slip scale range (2026-10-18, simulation only, model assumption dependent): with i0 0.05 to 1.20 (nominal 0.81) the nominal model crosses 50 % slip at 10.2 degrees and UNKNOWN at 30 m is 33.9 % (A), 39.2 % (B), 11.2 % (C); with f_r also widened, 92.6 %, 90.1 %, 97.4 %. The original ranges remain the reference.
- Pre registered predictions and their hits and misses: `docs/PREDICTIONS.md`.

## Read in this order

1. `docs/EXECUTIVE_BRIEF.md` (also `.pdf`): two pages.
2. `manuscript/MANUSCRIPT.md` (also `.pdf`): the paper, with every negative result.
3. `docs/REPORT.md` (also `.pdf`): the full review, taxonomy, gap analysis, simulation studies (sections 8, 8.7 and the published anchors in 8.8), field plan (section 9, with the 2026-10-15 revision), limitations, verification, appendices.
4. `docs/NEXT_STEPS.md`: what the author does next: decisions, checks, then the first field experiment, and what to fetch.
5. `docs/PREDICTIONS.md`, `docs/predictions/`: dated predictions written before runs.
6. `docs/GLOSSARY.md`, `docs/PROTOCOL.md`, `docs/SEARCH_PROTOCOL.md`, `docs/DATA_CATALOG.md`, `docs/DATA_AND_LICENSES.md`.
7. `docs/PROPOSAL_ROBOTICS.md` and `docs/PROPOSAL_EDGE.md`: proposals; nothing has been sent and no agreement exists.
8. `docs/PLANNER.md`: the Dune Rover Planner, how to install and run it, and what it cannot do.

## Layout

```
docs/                 report, brief, glossary, protocol, field plan, checklist, rover options, proposal seed, EDGE proposal,
                      licences, predictions register, open questions for the author, review and overnight log
docs/src/             hand written report sections and templates (REPORT.md, the brief and this README are built from them)
docs/predictions/     dated pre-data slope ladder predictions (PLANNED field experiment)
research/evidence.csv the evidence table (one row per reported mobility result)
research/raw/         per-topic notes and row files, data audit, morphology and UAE facts
research/phase2/      phase 2 retrieval reports and CSVs (morphology, rover options, rows read from supplied PDFs); no PDFs committed
research/phase3/      2026-10-20 evidence rows by topic, references with licences, search logs, digitised curves and calibrations, agent briefs
research/phase4/      2026-10-21 curves, their redigitisation check, scaling law notes and rows, protocol sources
field_kit/            data sheets for a field day; demo/ closed loop demonstration and its ROS 2 package; notebooks/ GPU notebook; config/ lidar sites
manuscript/           the paper (source in manuscript/src, generated MANUSCRIPT.md and .pdf)
src/dunerover/        simulation code (DEM, slope, slip model, graph routing, sensitivity, sub grid detector, three class map, field analysis)
                      and the Dune Rover Planner (planner.py, report.py, cli.py; evidence card in data/)
demo/web/             interactive planner demonstration (generated by scripts/build_web_demo.py)
scripts/              fetch_data.sh, consolidate_evidence.py, ingest_verification.py, verify_stats.py, build_report.py,
                      analyze_field_runs.py, field_analysis_power.py, make_ladder_predictions.py, anchor_comparisons.py, check_repo_hygiene.py, scan_secrets.py ...
tests/                113 test functions (more cases when parametrised)
results/              simulation outputs and figures (all labelled SIMULATION ONLY); results/subgrid, results/field_kit (synthetic data),
                      results/anchors (model against the Dumont Dunes and Ishigami 2009 values), results/dumont_prior (stage 7),
                      results/*widened_i0* (stage 9, widened ranges), results/range_set_diagnostics (stage 11)
data/anchor_points.csv  13 published slip points used only for descriptive comparison
```

## Reproduce

Python 3.10 or newer. Dependencies: numpy, scipy, matplotlib, tifffile, imagecodecs; pytest for tests.

```bash
pip install -e ".[dev]"          # or: pip install numpy scipy matplotlib tifffile imagecodecs pytest
bash scripts/fetch_data.sh       # downloads three Copernicus GLO-30 tiles (about 143 MB), checks SHA-256
PYTHONPATH=src python3 -m pytest -q tests
PYTHONPATH=src python3 -m dunerover.study --data data/raw --out results                    # phase 1, about 5.5 minutes
PYTHONPATH=src python3 -m dunerover.study_subgrid --data data/raw --out results/subgrid    # phase 2, about 5 minutes
PYTHONPATH=src python3 scripts/field_analysis_power.py                                      # synthetic power study, original bins, about 1 minute
PYTHONPATH=src python3 scripts/field_analysis_power.py --design 2026-10-15                   # same for the revised bins, a few minutes
PYTHONPATH=src python3 scripts/make_ladder_predictions.py --design 2026-10-15 --date 2026-10-15   # revised expected ranges
PYTHONPATH=src python3 scripts/anchor_comparisons.py                                       # Dumont Dunes and Ishigami 2009 anchors, about 10 s
PYTHONPATH=src python3 scripts/study_dumont_prior.py                                       # stage 7: Dumont fitted i0 in the 30 m map, about 12 minutes
PYTHONPATH=src python3 -m dunerover.study --data data/raw --out results/widened_i0 --range-set widened_i0                 # stage 9, also widened_i0_fr
PYTHONPATH=src python3 -m dunerover.study_subgrid --data data/raw --out results/subgrid_widened_i0 --range-set widened_i0  # stage 9, also widened_i0_fr
PYTHONPATH=src python3 scripts/anchor_comparisons.py --range-set widened_i0                # stage 9, writes results/anchors_widened_i0, also widened_i0_fr
PYTHONPATH=src python3 scripts/field_analysis_power.py --design 2026-10-15 --rule 2026-10-18   # stage 10, amended entrapment rule
PYTHONPATH=src python3 scripts/diagnose_level_ground.py                                  # stage 11, draws that cannot move on level ground
bash scripts/fetch_lidar.sh                                                              # 2026-10-20: USGS 3DEP lidar tiles with SHA-256 check
PYTHONPATH=src python3 scripts/terrain_validation_lidar.py                               # stage 12, detector and map against lidar (also --truth-max-deg 36, post hoc)
PYTHONPATH=src python3 scripts/wind_face_direction.py                                    # stage 13, ERA5 wind from the Open-Meteo archive (slow: rate limited)
/opt/mm/chrono/bin/python scripts/chrono_wheel_slope.py                                  # stage 14, needs pychrono 9.0.1 (conda, see the script header)
PYTHONPATH=src python3 scripts/compare_chrono.py                                         # stage 14 comparison
PYTHONPATH=src python3 scripts/digitise_figures.py --check                               # W2: rebuild curves.csv from the calibration files (needs the source PDFs locally)
PYTHONPATH=src python3 scripts/model_validation.py --families exp_existing,mohr_coulomb_ratio,logistic_empirical   # stage 15, also --families bekker_wong (slow)
PYTHONPATH=src python3 -m dunerover.study_subgrid --range-set posterior_2026_10_20 --out results/subgrid_posterior_2026_10_20   # stage 15 map
PYTHONPATH=src python3 -m dunerover.study_subgrid --range-set widened_i0_fr --reject-immobile --out results/subgrid_widened_i0_fr_mobile   # stage 16, question 8
PYTHONPATH=src python3 scripts/sobol_map.py                                              # stage 16, Sobol indices
PYTHONPATH=src python3 scripts/planner_lidar.py && python3 scripts/planner_matched_pairs.py   # stage 17
PYTHONPATH=src python3 scripts/field_rule_options.py                                     # stage 18
PYTHONPATH=src python3 scripts/terrain_validation_lidar.py --sites-file config/lidar_sites_phase4.json --out results/terrain_validation_phase4   # stage 20
PYTHONPATH=src python3 scripts/planner_lidar.py --sites-file config/lidar_sites_phase4.json --out results/planner_phase4                     # stage 20
python3 scripts/icesat2_profiles.py fetch && PYTHONPATH=src python3 scripts/icesat2_profiles.py analyse --lengths 10   # stage 19 (docs/ICESAT2_GUIDE.md)
PYTHONPATH=src python3 scripts/model_validation.py --families exp_existing,mohr_coulomb_ratio,logistic_empirical --extra-curves research/phase4/curves_new.csv --out results/model_validation_phase4   # stage 21
PYTHONPATH=src python3 scripts/model_validation.py --families mobility_pull,mobility_logistic --extra-curves research/phase4/curves_new.csv --out results/model_validation_phase4         # stage 22
PYTHONPATH=src python3 demo/closed_loop.py && PYTHONPATH=src python3 demo/closed_loop_posthoc.py   # stage 23 and its post hoc variant
/opt/mm/chrono/bin/python scripts/chrono_scm_calibration.py                              # stage 24
PYTHONPATH=src python3 scripts/ingest_field_day.py FOLDER --label LABEL --rebuild         # after a field day (field_kit/README.md)
PYTHONPATH=src python3 scripts/build_manuscript.py --pdf && python3 scripts/check_manuscript_numbers.py   # manuscript and its number check
PYTHONPATH=src python3 scripts/build_number_ledger.py --check                              # every number traced (docs/NUMBER_LEDGER.csv)
bash scripts/clean_clone_check.sh                                                          # clean clone rebuild of every generated document
python3 scripts/consolidate_evidence.py && python3 scripts/verify_stats.py                  # evidence table and verification log from files
python3 scripts/build_report.py  # rebuilds docs/REPORT.md, the brief and this README from docs/src, the CSVs and results
python3 scripts/check_repo_hygiene.py --history && python3 scripts/scan_secrets.py --history
```

Seeds are fixed and listed in `results/summary.json` and `results/subgrid/summary.json`. Phase 2 was run twice and the CSVs matched.

## Data and licences

Full list in `docs/DATA_AND_LICENSES.md`. Copernicus GLO-30 (the controlling Free and Open licence was read in full; attribution and no liability notices required; no commercial restriction in the text), numpy, scipy, matplotlib, tifffile, imagecodecs, pytest (permissive). The DEM tiles are not committed. Source PDFs and raw downloads are never committed: a CI job fails if they are.

**Licence:** all rights reserved. The repository is public for reading and review; please contact the author before any use, modification, distribution or sale (`LICENSE`, `LICENSE-DOCS.md`).

## Not done

DEM and RFT were reviewed, not run; Project Chrono was run for a single wheel on 2026-10-20 (report section 13.4). No field data exist. No learning model was trained. The sub grid detector was tested against one metre lidar of three North American dune fields on 2026-10-20 (it works at 10 m and fails at 30 m; report section 13.5), never against an Arabian slip face. See report sections 10 and 13.
