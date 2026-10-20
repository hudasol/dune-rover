# Robotics project proposal: measured slip and fine terrain for wheeled robots on Gulf dunes

**Status: PROPOSAL. No agreement, partnership, funding or endorsement exists with any institution, and none is implied.** Author: Huda Mueen, `hudasol/dune-rover`. Generated from `docs/src/proposal_robotics_template.md` by `scripts/build_report.py`; every number comes from a result file or `research/evidence.csv`. Nothing has been sent to anyone. Costs are given only where a source was retrieved; otherwise "not estimated". Heat and dust limits for people and electronics are covered in the separate repository `hudasol/dhill`.

Labels: **PUBLISHED** (read in a retrieved source), **SIMULATED BY ME** (output of this repository's code), **PLANNED** (not run).

## 1. Problem

A small wheeled robot on a dune slope can lose most of its forward progress to slip, and the slope at which it stops depends on the vehicle, its wheels and the sand. Route planning on Gulf dune fields needs (i) a slip law that holds for the vehicle on that sand and (ii) a terrain model fine enough to see slip faces. Neither exists in open form for Arabian dunes: no published slip against slope dataset was found for any wheeled robot on Arabian dune sand, and open elevation data are about 30 m.

## 2. Evidence (what the desk study established)

- **Published evidence base:** 494 verified rows from 174 sources, with a measured extraction error rate (9.3 % material errors in the 323 rows added on 2026-10-20, all corrected) (`research/evidence.csv`, `docs/SEARCH_PROTOCOL.md`).
- **Slip models do not transfer between vehicles and soils** (SIMULATED BY ME against PUBLISHED curves): calibrated on other studies, four model families predicted a held out study with median root mean square slip errors of 0.24 to 0.24; none met the pre registered bar of 0.15, and an empirical curve did as well as the physics.
- **Open 30 m terrain data are not enough** (SIMULATED BY ME on PUBLISHED lidar): on three real dune fields, a three class map at 30 m called cells TRAVERSABLE that contained steep slip faces in 25.6 %, 28.6 % and 28.0 % of cases; at 10 m the same method fell to 3.6 %, 2.5 % and 1.8 %.
- **Planning on 30 m maps was not safer than naive planning** against lidar truth; with 10 m maps a conservative policy avoided most steep ground (post hoc analysis, `docs/PREDICTIONS.md` stage 17).
- **A simulator does not replace measurement:** Project Chrono with published soils predicted slip of 0.21 at 12.5 degrees where the Dumont Dunes field curve shows about 0.49.

## 3. What is validated and what is not

| Item | Status |
|---|---|
| Extraction of published numbers | Checked against full text by independent agents; human spot check prepared, not done |
| Slip model for any vehicle on Arabian sand | **Not validated.** No field data exist |
| Slip face detector | Validated against real lidar at 5 to 30 m in North America; works at 10 m, fails at 30 m; **not tested on Arabian dunes** |
| Planner | Tested against lidar truth in North America; **not tested in Arabia** |
| Field protocol and analysis rule | Written, pre registered, tested on synthetic data; the pass or fail rule cannot yet separate a correct model from a collapse model (an open decision) |

## 4. Objectives

1. Measure the slip against slope curve of one small wheeled robot on one Gulf dune with the sand characterised (grain size, density, moisture, friction angle).
2. Survey the test dune at 10 m or finer (drone photogrammetry or lidar) and test the slip face detector and the three class map on Arabian terrain.
3. Test whether a model calibrated on gentle slopes predicts the steep slopes, against predictions committed before the steep runs.
4. Deliver an open, documented dataset and a planner whose map resolution and slip law are justified by measurement.

## 5. Work packages and milestones

| Work package | Content | Milestone and pre registered success criterion |
|---|---|---|
| WP1 Preparation | Site access in writing; safety plan; rover choice (`docs/ROVER_OPTIONS.md`); decision on the field rule (question 7) | M1: signed site access and a committed decision on the rule before any run |
| WP2 Supervised sand pilot | 12 pilot runs at 5, 10, 15 and 20 degrees; soil tests at every station; RTK or drone slope | M2: pilot sigma computed and the tolerance committed before the main block (`docs/FIELD_VALIDATION_PLAN.md`) |
| WP3 Main slope ladder | Runs in the 2026-10-15 bins with predictions for slopes above 10 degrees committed after calibration | M3: every run logged in `docs/field_log_template.csv` format, including entrapments; predicted against observed per bin reported whatever the result |
| WP4 Fine terrain survey | Drone or lidar survey of the test dune at 10 m or finer; detector and map scored as in stage 12 | M4: AUC and false safe rate reported for the Arabian dune against its own survey |
| WP5 Small rover trial | Route following on the surveyed dune with the conservative policy, a safety driver and recovery | M5: route success and entrapment counts against the planner's predictions, with every failure reported |
| WP6 Open dataset and paper | Data, code and a manuscript update | M6: dataset released under terms set by the author and the partner; manuscript revised with field results |

Success means complete data and an honest comparison, not a model that passes.

## 6. What a partner would provide (requests, not commitments)

| Need | From a university (for example Al Ain University) | From an industry partner (for example EDGE Group) |
|---|---|---|
| Supervision and safety | Named supervisor, safety review | Safety officer for vehicle trials |
| Site | Access to a dune site with permission | Access to a test range with dunes |
| Equipment | Soil lab tests (sieve, density, direct shear) | Loan of a small wheeled platform, RTK GNSS, drone survey |
| Recovery | | Recovery vehicle and experienced sand driver |

Costs: not estimated (no retrieved source covers these items).

## 7. Risks

| Risk | Mitigation |
|---|---|
| Entrapment or rollover on steep sand | Tether, second person, abort rules (`docs/FIELD_DAY_CHECKLIST.md`), no person downslope |
| Heat and dust | Early morning work; limits from `hudasol/dhill` |
| Rule cannot discriminate | Decide before the field day; report predicted against observed as the primary result |
| Single vehicle, single site | Results stated for that vehicle, wheels, sand and speed only |
| Implied endorsement | Every document states that no agreement exists unless one is signed |

## 8. What this proposal does not claim

It does not claim a validated slip model, a traversable route, a cost or schedule, or any institutional support.
