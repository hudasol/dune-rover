
## 16. Baselines and the conference benchmark (2026-10-27, stages 25 and 26)

> **SIMULATED BY ME (every detector, baseline, map and route) scored against PUBLISHED elevation data** (USGS 3DEP one metre lidar; Copernicus GLO-30). Registered in `docs/PREDICTIONS.md` before any baseline was coded or any metric computed. Paper: `paper/paper.pdf`; scripts: `scripts/benchmark_detection.py`, `scripts/benchmark_planning.py`; code: `src/dunerover/benchmark.py`, `src/dunerover/benchmark_cnn.py`.

### 16.1 Why

Sections 13 and 14 compared the detector and the planner only with variants of themselves, on block means of the lidar, and scored routes with a rule that flagged nearly every route. This section adds the methods a practitioner would use instead, a real 30 m product, a hazard outcome at dune scale, the shipped planner itself, and intervals.

### 16.2 Design

Six lidar windows (stages 12 and 20). Inputs: 10 m and 30 m block means of the lidar and Copernicus GLO-30 interpolated on the 30 m grid. Methods: the planner's synthetic trained detector (DET), DET recalibrated leave one site out, coarse slope, terrain ruggedness index, plane roughness, the steepest slope of a cubic interpolation, gradient boosted trees on 14 terrain features and a small dilated convolutional network, the last two trained leave one site out on lidar labels. Detection metrics with 300 m block bootstrap intervals. Planning: {{VAL:bm_pairs}} origin and destination pairs drawn from the lidar only; the planner's own naive, conservative and risk weighted policies with each hazard layer swapped in; a route is unsafe when it touches a face patch (at least 10 connected one metre posts of 28 degrees or more).

### 16.3 Results

- **Detection.** Mean AUC at 10 m: {{VAL:bm_auc_i10_det_mean}} (DET), {{VAL:bm_auc_i10_bicubic_mean}} (cubic interpolation), {{VAL:bm_auc_i10_gbm_mean}} (gradient boosting), {{VAL:bm_auc_i10_cnn_mean}} (network). At 30 m: {{VAL:bm_auc_i30_det_mean}}, {{VAL:bm_auc_i30_bicubic_mean}}, {{VAL:bm_auc_i30_gbm_mean}} and {{VAL:bm_auc_i30_cnn_mean}}, with plain slope at {{VAL:bm_auc_i30_slope_mean}}. On GLO-30: {{VAL:bm_auc_g30_det_mean}}, {{VAL:bm_auc_g30_bicubic_mean}}, {{VAL:bm_auc_g30_gbm_mean}} and {{VAL:bm_auc_g30_cnn_mean}}. The detector is not the best method at any input; at 30 m the best is the interpolation, which needs no training.
- **Planning.** Mission success (a route exists and touches no face patch) on 30 m maps: {{VAL:bm_success_i30_naive_none}} with the slip model alone, {{VAL:bm_success_i30_conservative_det}} with the conservative policy and DET, at most {{VAL:bm_success_i30_risk_weighted_bicubiccal}} with any computable layer, {{VAL:bm_success_i30_conservative_oracle}} with a perfect cell label. On 10 m maps: {{VAL:bm_success_i10_naive_none}}, {{VAL:bm_success_i10_conservative_det}}, {{VAL:bm_success_i10_risk_weighted_gbm}} (best computable layer) and {{VAL:bm_success_i10_conservative_oracle}}. A 5 m face map: {{VAL:bm_success_i5_conservative_oracle5}}.
- **Predictions.** Stage 25: 7 hit, 2 missed; stage 26: 5 hit, 3 missed (`docs/PREDICTIONS.md`).

### 16.4 Reading

At 30 m the information is not in the map: no model, physical or learned, recovers enough of the face hazard to make routes safer, and the planner's resolution gate (section 15) is the right response. At 10 m all reasonable methods see most faces and the hazard layers help, but a perfect 10 m cell label still leaves about half of the routes touching a face patch. Safe routes need a face map at about 5 m, from a drone survey, or onboard sensing. The fields are North American; the outcome counts any contact with a face patch as unsafe, which is strict; the vehicle model is an assumption range.
