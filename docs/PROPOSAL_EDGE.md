# Proposal seed for EDGE Group: field validation of slip and traversability prediction on UAE dunes

**Status: PROPOSAL, no agreement, partnership or endorsement exists.** Huda Mueen, `hudasol/dune-rover`, generated from `docs/src/proposal_edge_template.md` by `scripts/build_report.py`; numbers come from the result files. EDGE Group has not been contacted about this document, has not reviewed it and supports nothing in it. No other institution is a partner; access to Al Ain University does not exist. No cost figure appears below: costs are given only where a source was retrieved, and those are listed in `docs/ROVER_OPTIONS.md`. Heat and dust limits for people and electronics are the subject of the separate repository `hudasol/dhill` and are not repeated here.

Labels used throughout: **PUBLISHED** (a number read in a retrieved source, with a row in `research/evidence.csv`), **SIMULATED BY ME** (output of the code here; simulation only, model assumption dependent), **PLANNED** (not run).

## 1. Problem and Gulf relevance

A wheeled ground vehicle on dune sand loses traction as the slope rises, and the slope at which it stops climbing depends on the vehicle, the wheels and the sand. No published slip against slope dataset was found for a wheeled robot on Arabian dune sand with the soil characterised (`docs/REPORT.md`, section 7); the only Arabian field item in the evidence table is a qualitative report of a rover getting stuck in loose sand in Oman (FLD-042). The nearest published sand slope curve is from Dumont Dunes, California, for a 340 kg test rover: slip rose from below 50 % at 12.5 degrees to about 75 % at 16 degrees and about 90 % at 20 degrees (FLD-HV13-1, FLD-HV13-2). Run on the same slopes, the slip model here crosses 50 % slip only at 25.5 degrees against 12.6 degrees for the Dumont curve (SIMULATED BY ME, report section 8.8). Open elevation data for the region (Copernicus GLO-30, about 30 m) resolve dunes but not their slip faces (report section 8.7). A planner for UAE dunes therefore lacks both the slip law and the terrain detail it would need. Tests of 2026-10-20 and 2026-10-21 (SIMULATED BY ME against PUBLISHED data; `docs/PROPOSAL_ROBOTICS.md`, report sections 13 and 14) sharpen this: on 49 published curves, slip models calibrated on other studies predicted a held out study with median errors of 0.20 to 0.22 slip; and on 6 real dune fields a 30 m map labelled TRAVERSABLE 36 % to 80 % of the cells that contain a steep face, against 7 % to 33 % at 10 m. Satellite laser profiles were also compared with the 30 m map over Arabian dunes. Over Liwa (A), the Rub' al Khali megadunes (B) and the linear dunes (C), 71 %, 47 % and 67 % of the ICESat-2 segments steeper than 28 degrees fell in cells the 30 m map calls TRAVERSABLE, against 93 %, 92 % and 98 % of all segments; keeping only steep crossings confirmed by a neighbouring segment and no steeper than 35 degrees (post hoc), 52 %, 29 % and 49 %. The ICESat-2 method failed its own validation against lidar, so these are indications, not a validation.

## 2. What exists (all in this repository)

| Item | Label | Files |
|---|---|---|
| Evidence table of 510 published results from 176 sources, each re checked against its source | PUBLISHED | `research/evidence.csv`, `research/verification_log.md`, `docs/SEARCH_PROTOCOL.md` |
| Validation of slip model families on digitised published curves (none passed, including two built on the granular scaling laws), an independent Project Chrono simulation calibrated on a field curve, and a test of the map and planner against one metre lidar of 6 dune fields | SIMULATED BY ME against PUBLISHED data | `results/model_validation*/`, `results/chrono_scm*/`, `results/terrain_validation*/`, `results/planner*/`, report sections 13 and 14 |
| ICESat-2 laser profiles over Liwa and the Rub' al Khali, scored against the 30 m map | PUBLISHED data, SIMULATED BY ME scoring | `results/icesat2/`, report section 14.5 |
| Closed loop demonstration: online slip estimation and replanning, also as ROS 2 nodes | SIMULATED BY ME | `demo/`, `results/closed_loop/` |
| Field kit: data sheets, one command ingest, preregistration draft, drone and sand protocols | PLANNED | `field_kit/`, `scripts/ingest_field_day.py`, `docs/OSF_PREREGISTRATION_DRAFT.md`, `docs/DRONE_SURVEY_PROTOCOL.md`, `docs/SAND_LAB_PROTOCOL.md` |
| Slope and slip traversability study on GLO-30 data for Liwa and the Rub' al Khali, with sensitivity analysis | SIMULATED BY ME | `src/dunerover/`, `results/`, report section 8 |
| Sub grid slip face detector and three class map (TRAVERSABLE, BLOCKED, UNKNOWN) | SIMULATED BY ME; tested against synthetic truth and, on 2026-10-20, against North American lidar (works at 10 m, fails at 30 m) | `results/subgrid/`, report section 8.7 |
| Comparison of the slip model with Dumont Dunes and Ishigami 2009 | SIMULATED BY ME against PUBLISHED values | `results/anchors/`, report section 8.8 |
| Slope ladder field plan, dated predictions, analysis script tested on synthetic data, checklist, log template | PLANNED | `docs/FIELD_VALIDATION_PLAN.md`, `docs/predictions/`, `scripts/analyze_field_runs.py`, `docs/FIELD_DAY_CHECKLIST.md`, `docs/field_log_template.csv` |
| Predictions register with every hit and miss | process record | `docs/PREDICTIONS.md` |

## 3. Validated, simulated, planned

- **Checked or tested (not validated against field data):** the extraction of published numbers (current table 510 rows, 38 with a material error before correction by each row's latest verdict; every material error corrected), and the slip face detector was tested against real lidar outside Arabia (it works much better at 10 m than at 30 m). No slip model in this repository has been validated against field data, and none transferred between published studies.
- **A working tool (simulation only, model assumption dependent):** the Dune Rover Planner (`docs/PLANNER.md`) reads a dune elevation model and a vehicle profile and returns a three class map, routes with their risks and an HTML report; a resolution gate refuses to call ground coarser than 10 m verified traversable, and the rover's own slope runs calibrate its profile. The field day is what turns it into a tool for a real rover on Gulf sand.
- **Simulated (simulation only, model assumption dependent):** the traversability maps and the UNKNOWN share; the comparison with the published anchors, which shows the slip model predicting too little slip on sand slopes above about 10 degrees (report section 8.8). That is a negative result for the model, stated as such.
- **Planned:** the slope ladder (0 to 20 degrees with denser bins between 10 and 20, revised 2026-10-15) and a drone survey of the test dune at about 10 cm with ground control and check points (`docs/DRONE_SURVEY_PROTOCOL.md`) to test the slip face detector and the map on Arabian terrain. Nothing has been run; the planned pass or fail rule was amended on 2026-10-18 and still calls a wrong model adequate about half the time on synthetic data; the author must decide whether to accept that before any field day (`docs/FIELD_VALIDATION_PLAN.md`, section 7).

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

## 6. Readiness

Using the common nine step technology readiness scale only as a shorthand (no body has assessed it): the slip model for a vehicle on Arabian sand is at concept level (2); the slip face detector and three class map are a proof of concept against lidar of dune fields outside Arabia (3); online slip estimation and replanning are software in simulation against a modelled rover, including ROS 2 nodes, with no benefit of replanning shown against a retry control (2 to 3); the field protocol and ingest are tested on synthetic data only (3); the Dune Rover Planner, which packages the map, the routes and the vehicle calibration as one tool, is tested on synthetic inputs and demonstrated on lidar outside Arabia (3). Details in `docs/PROPOSAL_ROBOTICS.md`, section 4.

## 7. Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Entrapment or damage on steep sand | High | Medium | Tether and recovery line, second person, abort rules in `docs/FIELD_DAY_CHECKLIST.md`; no person downslope | Field lead |
| Heat and dust | Medium | High | Early morning runs; limits for people and electronics from `hudasol/dhill` (separate study, cross referenced only) | Supervisor |
| Drone flight without the right permission | Medium | High | Fly only through an operator who holds the authorisation | Partner |
| Run to run scatter too large to discriminate | Medium | Medium | Pilot first; the analysis flags an uninformative experiment | Author |
| The planned pass or fail rule discriminates weakly (amended 2026-10-18; a wrong collapse model still passes about half the time on synthetic data) | High | Medium | Open decision for the author before the field day (`docs/FIELD_VALIDATION_PLAN.md`, section 7); report predicted against observed as the primary result | Author |
| One vehicle, one site, one sand | Certain | Medium | Results limited to the tested vehicle, wheels, soil and speed | Author |
| Implied endorsement | Low | High | This document and any result state that no agreement or endorsement exists unless one is signed | Author |

## 8. What this proposal does not claim

It does not claim that any model predicts a vehicle on UAE dunes, that any route is traversable, that EDGE Group or any institution supports the work, or any cost or schedule. It is a plan to find out.
