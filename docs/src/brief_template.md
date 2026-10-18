# Executive brief: predicting slip and traversability of wheeled robots on Arabian dunes

Huda Mueen, `hudasol/dune-rover`, 2026-10-18. Generated from `docs/src/brief_template.md` by `scripts/build_report.py`; every number comes from a result file or an evidence row (IDs such as FLD-012 refer to `research/evidence.csv`). **This is a proposal and a research summary. No agreement, partnership or endorsement exists with any institution, and none is implied.** Heat and dust limits for people and electronics are the subject of the separate repository `hudasol/dhill` and are not repeated here. No cost is given.

Labels: **PUBLISHED** (read in a retrieved source), **SIMULATED BY ME** (output of this repository's code; simulation only, model assumption dependent, never field evidence), **PLANNED** (not run).

## 1. Question and Gulf relevance

How much does a small wheeled robot slip on a dune slope, can that be predicted before the run, and how much of an open 30 m elevation map of UAE dunes can be trusted for planning? No published slip against slope dataset was found for a wheeled robot on Arabian dune sand with the soil characterised; the only Arabian field item is a qualitative report of a rover getting stuck in loose sand in Oman (FLD-042). Open elevation data (Copernicus GLO-30, about 30 m) resolve the dunes but not their slip faces.

## 2. What is published (PUBLISHED; {{VAL:ver_all_n}} rows, each traced to a source passage)

- **Earth dune slope curve.** At Dumont Dunes, California, a 340 kg test rover went from below 50 % slip at 12.5 degrees to about 75 % at 16 and about 90 % at 20 degrees; no soil parameters are reported (FLD-HV13-1, FLD-HV13-2).
- **Small rover on a sand bed.** A 13.5 kg rover traversing a 10 degree side slope of Toyoura sand showed a slip ratio of about 0.5 (TM-IS09-3).
- **Mars field slip is large and patchy.** Spirit measured 15 to 20 % slip at 19 degrees and 95 % at 16 degrees about 30 m away on similar looking terrain (FLD-011, FLD-012).
- **Models need fitting per soil.** Bekker type drawbar errors of 24 to 27 % (median) on two lunar simulant datasets (SIM-025 to SIM-027); the Janosi shear modulus spans about two orders of magnitude between sources, so it is tuned, not transferred.

## 3. What is simulated by me (SIMULATED BY ME; simulation only, model assumption dependent)

A lumped slope to slip model with a friction angle from published laboratory ranges and three assumed parameters, run over GLO-30 data for Liwa and the Rub' al Khali, with Monte Carlo over the assumptions, a sub grid slip face detector validated against synthetic truth only, and a three class map (TRAVERSABLE, BLOCKED, UNKNOWN). The nominal climbing limit is {{VAL:crit_nom}} degrees; across the original assumption ranges it spans {{VAL:crit_p05}} to {{VAL:crit_p95}} degrees (5th to 95th percentile).

**UNKNOWN share of cells by elevation model posting** (original ranges; last column with the slip scale range widened on 2026-10-18):

| Area | 30 m | 60 m | 90 m | 30 m, widened i0 range |
|---|---|---|---|---|
| A, south Liwa | {{VAL:unk_A_30}} | {{VAL:unk_A_60}} | {{VAL:unk_A_90}} | {{VAL:rs_w_unk_A}} |
| B, Rub' al Khali megadunes | {{VAL:unk_B_30}} | {{VAL:unk_B_60}} | {{VAL:unk_B_90}} | {{VAL:rs_w_unk_B}} |
| C, Rub' al Khali linear dunes (Saudi Arabia) | {{VAL:unk_C_30}} | {{VAL:unk_C_60}} | {{VAL:unk_C_90}} | {{VAL:rs_w_unk_C}} |

BLOCKED stays under 0.1 % at 30 m in every area, because the grid hardly shows slopes the model calls impassable. When the resistance range is widened as well, UNKNOWN at 30 m reaches {{VAL:rs_wf_unk_A}} in A, largely because 9 to 12 % of those draws cannot move on level ground at all. Under the original ranges the map is robust to the slip parameters; under the widened ones it is not.

## 4. Negative results

- **The model predicts too little slip on both published anchors** (comparisons of unlike vehicles and soils). With the original ranges the nominal model crosses 50 % slip at {{VAL:an_nom_cross}} degrees against {{VAL:an_d_cross}} degrees for the Dumont curve, and it gives {{VAL:an_b1_10deg}} slip where about 0.5 was measured on Ishigami's 10 degree side slope.
- **Widening the slip scale range does not fix it.** The nominal model then crosses 50 % at {{VAL:rs_w_nomcross}} degrees, too early, and the envelope contains both anchors only because it is very wide; a post hoc fit still misses the shape of the Dumont curve (RMSE {{VAL:rs_w_rmse}}).
- **The planned pass or fail rule discriminates weakly.** On synthetic data with the revised slope bins and the amended entrapment rule, a wrong model with collapse above 20 degrees is called adequate in {{VAL:pr_collapse_adeq}} of replicates.
- Most quantitative predictions about the simulation missed ({{VAL:pred_stage_line}}; `docs/PREDICTIONS.md`).

## 5. Error rate of the evidence table

Every row was re checked against its source by a separate agent with no access to the extraction notes. First check of the {{VAL:ver_ext_n}} rows as extracted: {{VAL:ver_ext_material}} material errors ({{VAL:ver_ext_material_rate}}) and {{VAL:ver_ext_any}} with any discrepancy ({{VAL:ver_ext_any_rate}}). Current table of {{VAL:ver_all_n}} rows, latest verdict per row: {{VAL:ver_all_material}} material ({{VAL:ver_all_material_rate}}). All are corrected. The checkers are language model agents; a human spot check by the author is planned.

## 6. The first field experiment (PLANNED)

A slope ladder with one small four wheel rover (5 to 25 kg) on one dune stoss slope: direct uphill runs in bins at 0, 5, 10, 12.5, 15, 17.5 and 20 degrees (25 degrees only if allowed; whether the 1 degree tolerance of these bins can be met on a real dune is unconfirmed, and the original bins at 5 degree spacing remain documented), a 12 run pilot to measure run to run scatter, RTK ground truth, full soil description at every station, calibration on runs up to 10 degrees and dated predictions committed before the steeper runs. Plan: `docs/FIELD_VALIDATION_PLAN.md`; predictions: `docs/predictions/`.

## 7. The ask

A supervised field day on a dune site with a named supervisor and recovery support; the loan of one small wheeled rover; the loan of an RTK GNSS unit or a drone survey of the test slope; and written site access. Each has a fallback in `docs/PROPOSAL_EDGE.md`. Success means a complete, openly reported dataset and a comparison with the committed predictions, including a failed model.
