# Executive brief: predicting slip and traversability of robots on dunes

Huda Mueen, `hudasol/dune-rover`, 2026-10-11. Research only; not engineering approval for any real vehicle. Row IDs (for example FLD-012) refer to the evidence table in `docs/REPORT.md`, Appendix A.

**Question.** How well can slip, sinkage and traversability of wheeled (and secondarily legged) robots on dry sand and dunes be predicted from terrain data and models, how well does that transfer from lab to field, and what is missing for a minimal open-data planner for Arabian dunes?

## What the published evidence says (144 rows, each traced to a URL and passage)

- **Models need per-soil fitting and are mostly validated on level ground.** Bekker-Wong style drawbar errors are 24 to 27 % (median) on two lunar-simulant wheel datasets and sinkage errors 28 to 52 %, up to 135 % and 385 % on firm soil with a small light wheel (SIM-025 to SIM-027). Granular RFT gives wheel drawbar errors of 5.6 to 15 N in a lab bed (TM-001 to TM-004). The Janosi shear modulus differs about 75-fold between papers, so it is tuned, not transferred.
- **Speed and slope break the quasi-static assumption.** Drawbar coefficient fell 63.7 % between 0.2 and 1 m/s on olivine sand (TM-019). A rover slope model had side-slip errors of 14.8 % at 10 degrees and 25.9 % at 20 degrees before tuning (a thesis, TM-022, TM-023).
- **Field slip is large and patchy.** Spirit measured 15 to 20 % slip at 19 degrees and 95 % at 16 degrees about 30 m later on terrain that looked alike (FLD-011, FLD-012). Perseverance exceeded 94 % at about 20 degrees (FLD-025). These are Mars data.
- **Learning is validated in-distribution.** The best held-out result is AUROC 0.874 on Perseverance sols (LRN-010). No paper holds out terrain type, and none reports a learned slip error on Earth dunes.
- **Arabian evidence is nearly absent.** One qualitative report of a rover getting stuck in looser-than-expected sand in Oman (FLD-042). No Arabian sand parameters, no Empty Quarter grain-size map, no open LiDAR of the dunes.
- **Open data resolve dunes, not slip faces.** Copernicus GLO-30 (about 28 by 31 m, free with attribution) resolves crests and interdune corridors of dunes tens to hundreds of metres high; slip faces are 1 to 4 posts wide and read too gentle. A 90 m product removes 80 to 100 % of cells steeper than 25 degrees in the three windows tested.

## What I simulated (SIMULATION ONLY, model-assumption dependent, not field evidence)

A friction-circle slip model with a friction angle (published range 28 to 38 degrees) and three assumed parameters, routed over real GLO-30 data from Liwa and the Rub' al Khali, with one-at-a-time and 256-draw Latin-hypercube sensitivity analysis.

| Result | Value |
|---|---|
| Nominal climbing limit of the model | 25.5 degrees |
| Edges blocked at nominal parameters (three windows) | 0.2 to 1 % |
| Climbing limit across the assumption ranges | 7.6 to 34.7 degrees (5 to 95 %: about 15 to 32) |
| Assumptions that change the map most | friction angle, slip-law form, DEM posting, slip scale i0, resistance f_r |
| Assumptions that change it least | planning slip limit, spatially correlated DEM noise |

The small blocked share reflects the 30 m grid and nominal assumptions, not easy dunes. The map is controlled by parameters that field data have not yet measured.

## What is planned (PLANNED, not run)

A slope-ladder field experiment with one small rover on one dune stoss slope: runs at about 0, 5, 10, 15, 20 and 25 degrees, RTK ground truth, full soil description, about 60 runs, calibration on gentle slopes and dated blind predictions for steep slopes. A synthetic design check shows the adequacy tolerance must be set from the pilot's scatter.

## How far to trust this

- Verification: 30 randomly drawn rows plus 7 flagged ones were re-checked against the sources by separate agents: **0 material errors** (exact 95 % upper bound 9.5 % on the random sample), 9 minor label errors, corrected. 107 rows were not individually re-checked. A second independent check of the report's prose found 5 wrong and 26 minor items among 225 claim groups, all corrected.
- Limits: search tool US-only; paywalled standards (Bekker, Wong) not read; several rows are from theses, slides or a press release (flagged in the table); simulation not fitted to any data; the GLO-30 licence text was not read directly; no repository licence chosen yet.

## First experiment to run

The slope ladder (`docs/FIELD_VALIDATION_PLAN.md`): start with the 12-run pilot to measure run-to-run scatter, then the main block. It fills the largest gap: no published slip-versus-slope data for a wheeled robot on dune sand with measured soil.
