# Executive brief: predicting slip and traversability of robots on dunes

Huda Mueen, `hudasol/dune-rover`, updated 2026-10-12 (generated from `docs/src/brief_template.md` by `scripts/build_report.py`; numbers come from the result files). Research only; not engineering approval for any real vehicle. Row IDs (for example FLD-012) refer to the evidence table in `docs/REPORT.md`, Appendix A.

**Question.** How well can slip, sinkage and traversability of wheeled (and secondarily legged) robots on dry sand and dunes be predicted from terrain data and models, how well does that transfer from lab to field, and what is missing for a minimal open data planner for Arabian dunes?

## What the published evidence says (170 rows, each traced to a URL and passage)

- **Models need per soil fitting and are mostly validated on level ground.** Bekker-Wong style drawbar errors are 24 to 27 % (median) on two lunar simulant wheel datasets and sinkage errors 28 to 52 %, up to 135 % and 385 % on firm soil with a small light wheel (SIM-025 to SIM-027). Granular RFT gives wheel drawbar errors of 5.6 to 15 N in a lab bed (TM-001 to TM-004). The Janosi shear modulus differs about 75-fold between papers, so it is tuned, not transferred.
- **Speed and slope break the quasi static assumption.** Drawbar coefficient fell 63.7 % between 0.2 and 1 m/s on olivine sand (TM-019). A rover slope model had side slip errors of 14.8 % at 10 degrees and 25.9 % at 20 degrees before tuning (a thesis, TM-022, TM-023).
- **Field slip is large and patchy.** Spirit measured 15 to 20 % slip at 19 degrees and 95 % at 16 degrees about 30 m later on terrain that looked alike (FLD-011, FLD-012). Perseverance exceeded 94 % at about 20 degrees (FLD-025). These are Mars data.
- **Learning is validated in distribution.** The best held out result is AUROC 0.874 on Perseverance sols (LRN-010). No paper holds out terrain type, and none reports a learned slip error on Earth dunes.
- **Arabian evidence is nearly absent.** One qualitative report of a rover getting stuck in looser than expected sand in Oman (FLD-042). No Arabian sand parameters, no Empty Quarter grain size map, no open LiDAR of the dunes.
- **Open data resolve dunes, not slip faces.** Copernicus GLO-30 (about 28 by 31 m, free with attribution) resolves crests and interdune corridors of dunes tens to hundreds of metres high; slip faces are 1 to 4 posts wide and read too gentle. A 90 m product removes 80 to 100 % of cells steeper than 25 degrees in the three windows tested.

## What I simulated (SIMULATION ONLY, model assumption dependent, not field evidence)

A friction circle slip model with a friction angle (published range 28 to 38 degrees) and three assumed parameters, routed over real GLO-30 data from Liwa and the Rub' al Khali, with one at a time and 256-draw Latin hypercube sensitivity analysis (phase 1). Phase 2 added a sub grid slip face detector (trained on synthetic dunes, validated only against synthetic truth) and a three class map with Monte Carlo over the four assumed parameters, on three windows including a linear dune field in the Saudi Rub' al Khali.

| Result | Value |
|---|---|
| Nominal climbing limit of the model | 25.5 degrees |
| Climbing limit across the assumption ranges | 7.6 to 34.7 degrees (5 to 95 %: about 15 to 32) |
| UNKNOWN share of cells at 30 m: A south Liwa, B megadunes, C linear dunes | 8.6 %, 10.9 %, 2.5 % |
| Same if a face within one post counts (post hoc variant) | 34.4 %, 32.2 %, 22.0 % |
| UNKNOWN share at 60 and 90 m (A) | 9.1 % and 7.1 % |
| BLOCKED share at 30 m (A) | 0.00 % |
| Cells whose slope based verdict is robust to the four assumed parameters (A, B, C at 30 m) | 99.1 %, 97.0 %, 100.0 % |
| Assumptions that change the phase 1 map most | friction angle, slip law form, DEM posting, slip scale i0, resistance f_r |

The small BLOCKED share reflects the 30 m grid, not easy dunes. The UNKNOWN share depends mostly on the assumed dune shape and on what counts as "inside the cell", not on the four slip parameters.

## What is planned (PLANNED, not run)

A slope ladder field experiment with one small rover on one dune stoss slope: runs at about 0, 5, 10, 15, 20 and 25 degrees (bins revised on 2026-10-15, see `docs/FIELD_VALIDATION_PLAN.md`), RTK ground truth, full soil description, about 60 runs, calibration on gentle slopes and dated blind predictions for steep slopes. A synthetic design check shows the adequacy tolerance must be set from the pilot's scatter.

## How far to trust this

- Verification: **all 170 evidence rows were re checked against their sources** by separate agents. Material errors: 9 of 170 (5.3 %, Wilson 95 % interval 2.8 to 9.8 %); any discrepancy: 51 of 170 (30.0 %). All corrected. The first sample of 30 (0 material) had understated the rate. A second independent check of the 2026-10-11 draft of the report found 5 wrong and 26 minor items among 225 claim groups, all corrected; later sections were not part of it.
- Limits: search tool US only; paywalled standards (Bekker, Wong) and two references not read (list in `docs/NEXT_STEPS.md`); several rows are from theses, slides or a press release (flagged in the table); simulation not fitted to any data; the sub grid detector has never been compared with a real slip face profile; the synthetic test of the planned field analysis shows its pass or fail rule discriminates weakly, so the ladder results should be read as predicted against observed, not as pass or fail.
- Pre registration: predictions were committed before each run; most quantitative predictions about the simulation missed (`docs/PREDICTIONS.md`).

## First experiment to run

The slope ladder (`docs/FIELD_VALIDATION_PLAN.md`): start with the 12-run pilot to measure run to run scatter (it sets the tolerance), then the main block; dated pre data predictions are in `docs/predictions/`. It fills the largest gap: no published slip versus slope data for a wheeled robot on dune sand with measured soil.
