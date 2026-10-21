# Robotics project proposal: measured slip and fine terrain for wheeled robots on Gulf dunes

**Status: PROPOSAL. No agreement, partnership, funding or endorsement exists with any institution, and none is implied.** Author: Huda Mueen, `hudasol/dune-rover`. Generated from `docs/src/proposal_robotics_template.md` by `scripts/build_report.py`; every number comes from a result file or `research/evidence.csv` and is traced in `docs/NUMBER_LEDGER.csv`. Nothing has been sent to anyone. No price or cost is given: the resources below are what a partner would be asked to provide. Heat and dust limits for people and electronics are covered in the separate repository `hudasol/dhill`.

Labels: **PUBLISHED** (read in a retrieved source), **SIMULATED BY ME** (output of this repository's code), **PLANNED** (not run).

## 1. Problem

A small wheeled robot on a dune slope can lose most of its forward progress to slip, and the slope at which it stops depends on the vehicle, its wheels and the sand. Route planning on Gulf dune fields needs (i) a slip law that holds for the vehicle on that sand and (ii) a terrain model fine enough to see slip faces. Neither exists in open form for Arabian dunes: no published slip against slope dataset was found for any wheeled robot on Arabian dune sand, and open elevation data are about 30 m.

## 2. What the desk study established

- **Evidence base (PUBLISHED):** {{VAL:p3_rows_total}} verified rows from {{VAL:p3_sources_total}} sources, each re checked against the full text, with a measured extraction error rate ({{VAL:cur_material_rate}} of the current rows had a material error before correction; every one corrected).
- **Slip models do not transfer (SIMULATED BY ME against PUBLISHED curves):** on {{VAL:mv4_exp_existing_n}} held out published curves, the best of three model families (exponential, Mohr Coulomb, logistic) predicted a study it was not calibrated on with a median slip error of {{VAL:mv4_heldout_min}} (bar fixed in advance: 0.15); a fourth, Bekker Wong, failed on the {{VAL:mv_bw_ncurves}} first round curves it applies to ({{VAL:mv_bekker_wong_heldout}}). Two families built on the granular scaling laws did worse ({{VAL:mob_heldout_min}} to {{VAL:mob_heldout_max}}).
- **A simulator calibrated on a field curve gave no usable steep slope prediction (SIMULATED BY ME):** calibrated on the Dumont Dunes curve up to 12.5 degrees, Project Chrono's Soil Contact Model became numerically unstable at 15 to 20 degrees (post hoc grid and speed checks), so the steep slopes still need measurement.
- **30 m terrain data are not enough (SIMULATED BY ME on PUBLISHED lidar):** on {{VAL:lid6_nsites}} dune fields, a 30 m map labelled TRAVERSABLE {{VAL:lid6_miss_min_30}} to {{VAL:lid6_miss_max_30}} of the cells that contain a steep face; at 10 m, {{VAL:lid6_miss_min_10}} to {{VAL:lid6_miss_max_10}}.
- **Arabian dunes from space (PUBLISHED ICESat-2 data, SIMULATED BY ME scoring):** {{VAL:is2_summary_line}}
- **A closed loop in simulation (SIMULATED BY ME, the true rover is itself a model):** online slip estimation from odometry and position fixes had a median error of about {{VAL:cl_est_WhiteSands}}, which follows from the assumed position noise. {{VAL:clm_sentence}} The loop runs as ROS 2 nodes (one smoke test, on a pair that also arrives without replanning).

## 3. Technology readiness, stated honestly

The levels below use the common nine step technology readiness scale only as a shorthand; no assessment by any body has been made.

| Component | Readiness | Evidence |
|---|---|---|
| Slip model for a vehicle on Arabian sand | Concept only (level 2): no model transferred between published studies, and no Arabian measurement exists | Stages 15, 21, 22 |
| Slip face detector and three class map | Proof of concept against lidar of dune fields outside Arabia (level 3): works at 10 m or finer, fails at 30 m | Stages 12, 20 |
| Map on Arabian dunes | Compared only with satellite laser profiles, with a method that did not pass its own validation bar and a noisy steep segment set | Stage 19 |
| Online slip estimation and replanning | Software in simulation against a modelled rover, including ROS 2 nodes (level 2 to 3); no benefit of replanning shown against a retry control | Stage 23 |
| Field protocol, data sheets, analysis and ingest | Written and tested on synthetic data (level 3); pass or fail rule still an open decision | `docs/FIELD_VALIDATION_PLAN.md`, `scripts/ingest_field_day.py` |

## 4. Objectives

1. Measure the slip against slope curve of one small wheeled robot on one Gulf dune with the sand characterised (grain size, density, moisture, angle of repose, friction angle).
2. Survey the test dune at 10 cm (drone photogrammetry), and score the slip face detector and the three class map on Arabian terrain at 1, 5, 10 and 30 m.
3. Test whether a model calibrated on gentle slopes predicts the steep slopes, against predictions committed before the steep runs.
4. Measure online slip estimation on the real rover on the surveyed dune, with a safety driver, and test whether replanning on it lowers entrapment against a control that stops and retries.
5. Deliver a documented dataset and a manuscript revised with the field results.

## 5. Work packages

Durations are planning estimates (PLANNED), in weeks from the start of the project.

| Work package | Content | Weeks | Depends on | Deliverable |
|---|---|---|---|---|
| WP1 Preparation | Site access in writing, permissions for any drone flight, safety plan, rover choice (`docs/ROVER_OPTIONS.md`), decision on the field rule (question 7), preregistration submitted (`docs/OSF_PREREGISTRATION_DRAFT.md`) | 1 to 4 | none | Signed access, committed rule, preregistration |
| WP2 Rover and instruments | Wheel encoders, RTK or fixed position logging, IMU, effective radius calibration, closed loop software from `demo/ros2/` on the rover computer | 3 to 6 | WP1 | Bench tested rover with logged test runs |
| WP3 Sand tests | Grain size, density, moisture, angle of repose at every station; direct shear if a laboratory allows (`docs/SAND_LAB_PROTOCOL.md`) | 5 to 8 | WP1 | Soil sheet for every station |
| WP4 Pilot and slope ladder | 12 pilot runs, pilot scatter, then the main ladder with predictions committed before the steep bins (`field_kit/`) | 6 to 9 | WP2, WP3 | Run sheets and scored predictions (`scripts/ingest_field_day.py`) |
| WP5 Drone survey | Survey of the test dune at about 10 cm with ground control and check points (`docs/DRONE_SURVEY_PROTOCOL.md`); detector and map scored as in stage 20 | 6 to 9 | WP1 | Elevation model, accuracy report, map scores |
| WP6 Closed loop trial | Route following on the surveyed dune with online slip estimation; replanning tested against a stop and retry control (in simulation it showed no benefit over that control); safety driver and recovery | 10 to 12 | WP4, WP5 | Estimator error on the real rover; route outcomes with and without replanning |
| WP7 Analysis and paper | Every hit and miss recorded; manuscript revised; external review | 12 to 16 | WP4 to WP6 | Revised manuscript and dataset |

## 6. Resources the partner is asked to provide (no prices; nothing is requested from the author's own funds)

| Need | Purpose |
|---|---|
| A named supervisor and a safety review | Oversight of every field activity |
| Access to one dune site with permission in writing | All field work |
| One small wheeled ground vehicle (5 to 25 kg, four wheels, wheels at least 150 mm in diameter, known mass) or support to build one | The slope ladder and the closed loop trial |
| RTK GNSS (rover and base) or a total station | Measured slope and true displacement |
| A drone flight by an authorised operator, with ground control targets | The 10 cm survey of the test dune |
| Laboratory access for sieving, density and, if possible, direct shear | Sand properties |
| A recovery vehicle and an experienced sand driver | Safe recovery of the rover |
| One outside reviewer in terramechanics or field robotics | Review of the manuscript before submission |

## 7. Success and failure criteria

| Criterion | Tied to | Counts as success | Counts as failure |
|---|---|---|---|
| Field data complete | WP4 | Every planned run logged, including entrapments and aborted runs, with soil tests at every station | Missing runs without a written reason |
| Predictions scored | `docs/predictions/` and the committed rule | Every dated prediction scored as hit or miss, whatever the result | Any prediction changed after a run |
| Arabian map test | Stages 12, 19, 20 | Detector AUC and the 30 m miss rate reported for the surveyed dune | No survey, or a survey without check points |
| Closed loop on the rover | Stage 23 | Entrapment share with and without replanning reported on the same routes | Results reported only for routes that succeeded |

Success means complete data and an honest comparison, not a model that passes.

## 8. Risk and safety register

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Rover entrapment or rollover on a steep face | High | Medium | Tether and recovery line, abort rules (`docs/FIELD_DAY_CHECKLIST.md`), no person downslope, steepest bins last | Field lead |
| Heat illness of the team | Medium | High | Work in the early morning, water and shade, limits from `hudasol/dhill` | Supervisor |
| Drone flight without the right permission | Medium | High | Fly only through an operator who holds the authorisation; no flight otherwise | Partner |
| Run to run scatter too large to discriminate | Medium | Medium | Pilot first; the analysis flags an uninformative experiment | Author |
| The pass or fail rule cannot separate a correct from a collapse model | High | Medium | Decide question 7 before the field day; report predicted against observed as the main result | Author |
| Sand properties change during the day (crust, moisture) | Medium | Medium | Soil tests at every station and time of test recorded | Field lead |
| Single vehicle, single site | Certain | Medium | Results stated for that vehicle, wheels, sand and speed only | Author |
| Implied endorsement | Low | High | Every document states that no agreement exists unless one is signed | Author |

## 9. What this proposal does not claim

It does not claim a validated slip model, a traversable route, a cost or schedule beyond the planning estimates above, or any institutional support.
