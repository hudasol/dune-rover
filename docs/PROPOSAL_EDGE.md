# Proposal seed for EDGE Group: field validation of slip and traversability prediction on UAE dunes

**Status: PROPOSAL, no agreement, partnership or endorsement exists.** Huda Mueen, `hudasol/dune-rover`, generated from `docs/src/proposal_edge_template.md` by `scripts/build_report.py`; numbers come from the result files. EDGE Group has not been contacted about this document, has not reviewed it and supports nothing in it. No other institution is a partner; access to Al Ain University does not exist. No cost figure appears below: costs are given only where a source was retrieved, and those are listed in `docs/ROVER_OPTIONS.md`. Heat and dust limits for people and electronics are the subject of the separate repository `hudasol/dhill` and are not repeated here.

Labels used throughout: **PUBLISHED** (a number read in a retrieved source, with a row in `research/evidence.csv`), **SIMULATED BY ME** (output of the code here; simulation only, model assumption dependent), **PLANNED** (not run).

## 1. Problem and Gulf relevance

A wheeled ground vehicle on dune sand loses traction as the slope rises, and the slope at which it stops climbing depends on the vehicle, the wheels and the sand. No published slip against slope dataset was found for a wheeled robot on Arabian dune sand with the soil characterised (`docs/REPORT.md`, section 7); the only Arabian field item in the evidence table is a qualitative report of a rover getting stuck in loose sand in Oman (FLD-042). The nearest published sand slope curve is from Dumont Dunes, California, for a 340 kg test rover: slip rose from below 50 % at 12.5 degrees to about 75 % at 16 degrees and about 90 % at 20 degrees (FLD-HV13-1, FLD-HV13-2). Run on the same slopes, the slip model here crosses 50 % slip only at 25.5 degrees against 12.6 degrees for the Dumont curve (SIMULATED BY ME, report section 8.8). Open elevation data for the region (Copernicus GLO-30, about 30 m) resolve dunes but not their slip faces (report section 8.7). A planner for UAE dunes therefore lacks both the slip law and the terrain detail it would need. Tests of 2026-10-20 (`docs/PROPOSAL_ROBOTICS.md`, report section 13) sharpen this: slip models calibrated on other studies predicted a held out study with median errors of 0.20 to 0.24 slip, and on three real dune fields a 30 m map called cells TRAVERSABLE that contained steep faces in about a quarter of cases, against 3.6 % to 2.5 % at 10 m.

## 2. What exists (all in this repository)

| Item | Label | Files |
|---|---|---|
| Evidence table of 494 published results from 174 sources, each re checked against its source | PUBLISHED | `research/evidence.csv`, `research/verification_log.md`, `docs/SEARCH_PROTOCOL.md` |
| Validation of four slip model families on 26 digitised published curves, an independent Project Chrono simulation, and a test of the map and planner against one metre lidar of three dune fields | SIMULATED BY ME against PUBLISHED data | `results/model_validation/`, `results/chrono_scm/`, `results/terrain_validation/`, `results/planner/`, report section 13 |
| Slope and slip traversability study on GLO-30 data for Liwa and the Rub' al Khali, with sensitivity analysis | SIMULATED BY ME | `src/dunerover/`, `results/`, report section 8 |
| Sub grid slip face detector and three class map (TRAVERSABLE, BLOCKED, UNKNOWN) | SIMULATED BY ME; tested against synthetic truth and, on 2026-10-20, against North American lidar (works at 10 m, fails at 30 m) | `results/subgrid/`, report section 8.7 |
| Comparison of the slip model with Dumont Dunes and Ishigami 2009 | SIMULATED BY ME against PUBLISHED values | `results/anchors/`, report section 8.8 |
| Slope ladder field plan, dated predictions, analysis script tested on synthetic data, checklist, log template | PLANNED | `docs/FIELD_VALIDATION_PLAN.md`, `docs/predictions/`, `scripts/analyze_field_runs.py`, `docs/FIELD_DAY_CHECKLIST.md`, `docs/field_log_template.csv` |
| Predictions register with every hit and miss | process record | `docs/PREDICTIONS.md` |

## 3. Validated, simulated, planned

- **Validated:** the extraction of published numbers (current table 494 rows, 38 with a material error before correction by each row's latest verdict; every material error corrected), and the slip face detector was tested against real lidar outside Arabia (it works at 10 m and fails at 30 m). No slip model in this repository has been validated against field data, and none transferred between published studies.
- **Simulated (simulation only, model assumption dependent):** the traversability maps and the UNKNOWN share; the comparison with the published anchors, which shows the slip model predicting too little slip on sand slopes above about 10 degrees (report section 8.8). That is a negative result for the model, stated as such.
- **Planned:** the slope ladder (0 to 20 degrees with denser bins between 10 and 20, revised 2026-10-15) and a survey of one dune profile to test the slip face detector. Nothing has been run; the planned pass or fail rule was amended on 2026-10-18 and still calls a wrong model adequate about half the time on synthetic data; the author must decide whether to accept that before any field day (`docs/FIELD_VALIDATION_PLAN.md`, section 7).

## 4. The specific ask, with a fallback for each

| Ask | Purpose | Fallback if not available |
|---|---|---|
| One supervised field day on a dune site that EDGE Group can access, with a named supervisor and a safety briefing | Run the pilot of the field plan (3 runs at each of 5, 10, 15 and 20 degrees) and as much of the ladder as is safe | The author runs a reduced set alone on a gentle dune with a second person and a recovery vehicle, slopes up to 10 degrees only, and reports it as incomplete |
| Loan of one small wheeled ground vehicle (5 to 25 kg, four wheels, wheel diameter at least 150 mm, known mass) for the day | The vehicle for the ladder | A low cost platform from `docs/ROVER_OPTIONS.md` (costs as retrieved there) |
| Loan of an RTK GNSS unit, or a drone flight with photogrammetry over the test slope | Measured slope per run and a dune profile for the detector test | Smartphone inclinometer with a levelled straight edge for slope bins; detector test deferred |
| Site access and permission, and a recovery vehicle with an experienced sand driver | Legal access and safe recovery | No run without written permission; no slope above 15 degrees without recovery support |

## 5. Milestones and evidence based success criteria

| Milestone | Success criterion (what would count as done) |
|---|---|
| M1. Pilot day | The 12 pilot runs of the plan (3 at each of 5, 10, 15 and 20 degrees) logged with RTK slope; run to run slip scatter (pilot sigma) computed by `scripts/analyze_field_runs.py`; tolerance fixed and committed before the main block |
| M2. Post calibration predictions | Predictions for the bins above 10 degrees written by `scripts/make_ladder_predictions.py --calibrate` and committed, with a date, before any steeper run |
| M3. Main ladder | Every run logged in `docs/field_log_template.csv` format, including entrapments and aborted runs; soil tests at every station |
| M4. Analysis | Predicted against observed slip per bin with intervals, entrapment slope against prediction, comparison with the Dumont curve; every hit and miss recorded in `docs/PREDICTIONS.md`, including a failed model |
| M5. Detector test | Face probability and three class map compared with the surveyed profile of the same dune; result reported whether or not the detector holds |

Success means a complete dataset and a reported comparison, not a model that passes.

## 6. Risks

| Risk | Mitigation |
|---|---|
| Entrapment or damage on steep sand | Tether and recovery line, second person, abort rules in `docs/FIELD_DAY_CHECKLIST.md`; no person downslope |
| Heat and dust | Early morning runs; limits for people and electronics from `hudasol/dhill` (separate study, cross referenced only) |
| Run to run scatter too large to discriminate | Pilot first; the analysis flags an uninformative experiment |
| The planned pass or fail rule discriminates weakly (amended 2026-10-18; a wrong collapse model still passes about half the time on synthetic data) | Open decision for the author before the field day (`docs/FIELD_VALIDATION_PLAN.md`, section 7); report predicted against observed as the primary result |
| One vehicle, one site, one sand | Results limited to the tested vehicle, wheels, soil and speed |
| Implied endorsement | This document and any result state that no agreement or endorsement exists unless one is signed |

## 7. What this proposal does not claim

It does not claim that any model predicts a vehicle on UAE dunes, that any route is traversable, that EDGE Group or any institution supports the work, or any cost or schedule. It is a plan to find out.
