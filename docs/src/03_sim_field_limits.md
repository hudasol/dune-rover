
---

## 8. Simulation study (SIMULATED BY ME): slope and slip traversability from an open elevation model

> **SIMULATION ONLY, model assumption dependent. Nothing in this section is field evidence.** The model is a deliberately minimal planning screen, not a vehicle model. It omits sinkage, wheel geometry, vehicle mass, speed, avalanching and cohesion. The published evidence in section 3 shows that the slip it tries to represent varies from near 0 to near 1 at similar slopes, so the outputs below describe the **model**, not any real rover on any real dune.

### 8.1 What was run

- **Data.** Copernicus DEM GLO-30 tiles N23E053 and N22E054 (licence in section 5; tile hashes in `results/summary.json`). Three windows: **A-south Liwa** (23.02 to 23.17 N, 53.55 to 53.95 E, about 17 by 41 km, relief 139 m), **A north Liwa** (23.25 to 23.45 N, same longitudes; smaller crescentic dunes, relief 85 m) and **B Rub' al Khali megadunes** (22.20 to 22.50 N, 54.20 to 54.60 E, relief 211 m). The windows were chosen by me for visible dune texture, not at random.
- **Slope.** Horn 3 by 3 gradient with per latitude metric spacing (`src/dunerover/terrain.py`). A central difference check on the same A-south window gave 1.70 % of cells above 20 degrees in the earlier data audit against 1.45 % here (Horn): slope tails depend on the kernel by roughly 15 % relative.
- **Slip model** (`src/dunerover/slipmodel.py`). For an edge between neighbouring cells with along heading slope angle theta_a and cross slope theta_c:
  demand D = sqrt((tan theta_a + f_r)^2 + tan^2 theta_c) (friction circle), capacity mu_max = tan(phi), slip i = -i0 ln(1 - D / mu_max), entrapment if D >= mu_max. An edge is passable if i <= i_max; travel cost = distance / (1 - i). The exponential comes from the Janosi-Hanamoto shear law applied at the contact patch level.
- **Planner.** 8-neighbour directed graph, Dijkstra least cost routes (`scipy.sparse.csgraph`), ten deterministic origin destination pairs per window picked on gentle low ground (seed 20261011). Slope in each direction is taken from the elevation difference along the edge, cross slope from the Horn gradient at the edge midpoint.
- **Seeds and reproducibility.** Origin destination 20261011; Latin hypercube 20261012 (A core) and 20261013 (B core); 256 draws each, on core windows of 0.07 by 0.16 degrees (A core 23.06 to 23.13 N, 53.62 to 53.78 E; B core 22.28 to 22.35 N, 54.30 to 54.46 E); the full study was run twice and the area and sensitivity entries of the two `results/summary.json` files were identical (a one off comparison that is not stored in the repository; re run to confirm). Runtime about 330 s.

**Table 8.1: parameters of the slip model.** Only the friction angle has a published basis; the other three are assumptions with ranges. DEM noise is an additional assumption used in the sensitivity analysis only (spatially correlated, correlation length 3 posts, standard deviation 0 to 2 m).

{{TABLE:params}}

### 8.2 Elevation statistics (computed from the data, not from the slip model)

{{TABLE:slopestats}}

Coarsening to 60 and 90 m (block mean) removes most steep cells: the share of A-south cells above 25 degrees falls from 0.57 % at about 30 m to 0.093 % at about 60 m and 0.0046 % at about 90 m. This is the resolution effect discussed in section 5, reproduced on real tiles.

### 8.3 Nominal results

Under nominal parameters the model's critical direct ascent slope (slip equal to i_max) is **25.5 degrees**; the slip curve reaches entrapment at about 28 degrees. Model slip at 0, 5, 10, 15, 20 and 25 degrees of direct ascent is about 0.04, 0.08, 0.12, 0.18, 0.27 and 0.47.

{{TABLE:nominal}}

![Figure 8.1: A-south Liwa. SIMULATION ONLY.](../results/figures/fig_area_A_south_Liwa.png)

*Figure 8.1. (a) hillshade of GLO-30, (b) slope with the nominal critical angle contoured, (c) cells where at least one of eight headings is blocked, (d) three least cost routes. SIMULATION ONLY, model assumption dependent, not field evidence. The Rub' al Khali window is `results/figures/fig_area_B_RubAlKhali_megadunes.png`.*

**How to read these numbers.**

- The blocked share is tiny (0.2 to 1 % of edges). That follows from two things, not from the dunes being easy: at 30 m posting only a small share of cells exceed the nominal critical angle (section 8.2), and slip face slopes are biased low by the grid (section 5). A real rover facing the steepest faces would be blocked far more often than this map shows.
- The median route cost ratio (about 1.115 in all three windows) is **almost entirely a grid and baseline effect**: an 8-neighbour path is about 6 % longer than the straight line (column "Median length ratio" above) and nominal flat sand slip of about 0.04 adds a factor near 1.04. It should not be read as a dune effect. The routes avoid steep cells at small cost because the origin and destination are on gentle ground.
- Reachability is about 0.9999 in every window: the interdune corridors connect everything at nominal parameters.

### 8.4 Sensitivity analysis: which assumptions change the map most

Two analyses were run. **One at a time (OAT):** each parameter to its low and high value, plus structural alternatives (slip law form, cross slope rule, DEM posting, DEM noise). **Global:** 256 Latin hypercube draws of the five continuous assumptions on a core window of A and of B, with Spearman rank correlations against each output (ranks are used because the outputs are monotonic but non linear; the rank regression R squared values in `results/summary.json` are 0.86 to 0.96 for blocked share, reachability and climbing limit, so the ranking explains most of the variance).

**Table 8.2: one at a time sensitivity, area A-south (SIMULATED BY ME).**

{{TABLE:oat}}

![Figure 8.2: one-at-a-time sensitivity. SIMULATION ONLY.](../results/figures/fig_sensitivity_oat.png)

*Figure 8.2. Change from nominal in blocked share (left) and median route cost ratio (right), area A-south. SIMULATION ONLY.*

**Table 8.3: global sensitivity, Spearman rank correlation of each assumption with each output (Latin hypercube, n = 256, SIMULATED BY ME).**

{{TABLE:lhs_rank}}

**Table 8.4: spread of outputs across the assumption ranges (5th, 50th and 95th percentile, and extremes; SIMULATED BY ME).**

{{TABLE:lhs_pct}}

![Figure 8.3: global sensitivity. SIMULATION ONLY.](../results/figures/fig_sensitivity_rank.png)

*Figure 8.3. Spearman rank correlations (Latin hypercube). SIMULATION ONLY.*

**Reading of the sensitivity results.**

1. **Structural modelling choices move the map as much as the parameter ranges.** Replacing the point wise exponential with the contact patch averaged Janosi form raises the blocked share in A-south from 0.0025 to 0.0199 (8-fold, the largest single upward change in Table 8.2) and lowers the model's critical slope to 16.2 degrees (independent of the DEM). The additive cross slope rule (instead of the friction circle) raises the blocked share about 4-fold. Neither choice has published validation for dune sand. For comparison, moving the friction angle from 28 to 38 degrees changes the blocked share about 50-fold (0.0084 to 0.0002), so the friction angle gives the largest swing of any single parameter.
2. **DEM posting matters as much as the parameters.** Block averaging to 60 m and 90 m cuts the blocked share to 0.25 and 0.05 times nominal in A-south and to about 0.5 and 0.24 times in B (Table 8.2), because slip faces disappear (section 5). A map built from a coarser product would look easier than the 30 m map, and the 30 m map is itself likely too easy.
3. **Among the continuous parameters, the slip scale i0, the friction angle and the resistance coefficient dominate.** In both cores, the friction angle has the strongest rank correlation with blocked share (about -0.67 to -0.69), then i0 (+0.56 to +0.59), then f_r (+0.36 to +0.46). For the route cost ratio, i0 and f_r come first. The model's climbing limit spans 7.6 to 34.7 degrees across the draws under the original ranges (i0 0.05 to 0.40, f_r 0.05 to 0.25) (5 to 95 %: 14.7 to 31.4 in A, 15.3 to 31.6 in B). Two of these three (i0, f_r) are assumptions with no transferable published value, and the third (phi) differs by 10 degrees between published lab sands, so this is where measurements pay off most.
4. **The slip limit i_max and spatially correlated DEM noise matter least** in this setup (rank correlation magnitudes at most 0.27 and 0.11). The noise result is conditional on the assumed noise model; real DEM error over dunes (X-band penetration, slip face bias) is not modelled.
5. **Blocked share varies by about two orders of magnitude** between the 5th and 95th percentiles of the assumption space (A core 0.02 to 2.4 %; B core 0.03 to 5.5 %), with extremes of 0 to 5 % (A) and 0.01 to 19.5 % (B), while the OAT ranking is similar in the two areas. The conclusion that matters for a planner is that **the map is controlled by assumptions that field data have not yet measured**.

**Widened slip scale range (2026-10-18; SIMULATED BY ME, simulation only, model assumption dependent).** At the author's decision the phase 1 study was run again with the i0 range widened to 0.05 to 1.20 and a nominal value of 0.81, the lower bound implied by Ishigami et al. 2009 Table I under the model definition (TM-IS09-2), and once more with f_r also widened to 0.35 as a test. Same seeds; the original results above are unchanged and stay the reference (`results/widened_i0/`, `results/widened_i0_fr/`; pre registered as stage 9 in `docs/PREDICTIONS.md`).

{{TABLE:rs_phase1}}

With the widened range the nominal climbing limit falls from 25.5 to about 10 degrees and the median across draws from {{VAL:rs_o_crit_med}} to {{VAL:rs_w_crit_med}} degrees, and the nominal map blocks many more travel directions. With the widened range the assumed i0 range appears to dominate the map; only a measured slip against slope curve for the vehicle can narrow it. In the widened_i0_fr set 9 to 12 % of draws cannot move on level ground (stage 11), a case the original f_r basis excluded.

### 8.5 Comparison with published slip (descriptive only, nothing fitted)

Thirteen published slip versus slope points were transcribed by hand (`data/anchor_points.csv`: nine from FLD-010, FLD-011, FLD-012, FLD-025 and FLD-027 to FLD-031, and four from LEG-017 to LEG-020). They differ in slip definition, gravity, wheel and soil (see the warning column) and **should not be used as a test of the model**. The comparison shows only whether the assumption envelope overlaps them.

{{TABLE:anchor}}

![Figure 8.4: model envelope against published slip. Model SIMULATED BY ME, points PUBLISHED.](../results/figures/fig_slip_vs_slope_envelope.png)

*Figure 8.4. Blue line and band: model at nominal parameters and its 5 to 95 % range over the assumption space (SIMULATED BY ME). Orange circles: published field results (Mars rovers). Green squares: published lab beds. Bars show reported ranges or bounds. Published points at similar slopes span nearly 0 to 1 and no single curve fits them.*

The assumption envelope overlaps 11 of the 13 published points, which says mostly that it is wide, not that the model is valid. The nominal curve is more than 0.5 slip away from six of them (FLD-012, FLD-025, FLD-027, FLD-028, FLD-030, LEG-017), and the envelope misses two (FLD-030, a smooth wheeled lab rover at 0.9 slip at 4 degrees, and LEG-017, a 116 mm wheel at 0.741 at 12 degrees). These are cases a slope only model with lumped constants cannot represent.

### 8.6 Limitations specific to this study

- Quasi static, point mass, no sinkage, speed or avalanching; no wheel geometry or vehicle mass; i0 and f_r absorb everything.
- Slope is taken from a 30 m radar surface model whose slip face slopes are biased low (section 5); the blocked shares of phase 1 are lower bounds in that sense. Section 8.7 adds a modelled sub grid face probability and an UNKNOWN class to address this, with its own assumptions.
- The windows are not random samples of any dune field. Origins and destinations sit on gentle low ground, so route statistics say nothing about crossing slip faces.
- Descent is treated with the same symmetric friction circle demand (|tan theta_a + f_r|); descending stability and avalanching are not modelled.
- Parameters were not fitted to any data. No claim is made that the nominal values represent Arabian sand or any vehicle.
- Code is tested (`tests/test_core.py`: 15 tests covering exact planar slope, aspect, slip monotonicity and entrapment, cross slope behaviour, graph blocking, flat ground cost ratio, determinism of origin destination pairs and sampling, coarsening, noise reproducibility and metres per degree), but passing tests show the code does what it says, not that the model is right.

{{INCLUDE:subgrid}}

{{INCLUDE:anchors}}

---

## 9. Field validation plan (PLANNED; nothing here has been run)

Full plan: `docs/FIELD_VALIDATION_PLAN.md`. Summary:

1. **Vehicle.** One small four wheel rover (5 to 25 kg, wheels at least 150 mm, mass and wheel load known and kept fixed). Wheel diameter and width alter slip by large factors in the published lab data (LEG-017 to LEG-020), so the wheel must be fully described.
2. **Measurements.** Per wheel encoders and motor current at 50 Hz or better, RTK GNSS ground truth (not rover odometry), a 6-axis IMU, rut depth by gauge at three stations per run, and tow tension if a load cell is available. Slip is computed against ground truth speed with a calibrated effective radius, and distance based slip is reported alongside because published studies use both.
3. **Soil, at every station.** Sieve grain size, bulk density, moisture at two depths, crust thickness, angle of repose, hand penetrometer profile and a plate pressure sinkage set, with local slope from the RTK profile.
4. **Run design (about 60 runs).** Slope bins at 0, 5, 10, 15, 20 and 25 degrees (plus or minus 2) in the original plan, revised on 2026-10-15 (below), randomised order within a day, fresh track each run; a 12-run pilot to measure run to run scatter, then about 30 main runs; 9 cross slope, 6 tethered descent and 3 repeated pass runs. Run counts follow n = (1.96 sigma / E)^2: for sigma = 0.10 to 0.15 and E = 0.10 that is 4 to 9 runs per bin.
5. **Pre registered analysis.** Calibrate the section 8 model on 0 to 10 degree runs only, **record dated predictions** for 15, 20 and 25 degrees (original bins; 12.5 to 20 degrees in the revision below) before running them, then compare mean and root mean square error, the calibration slope and the entrapment slope, against a constant slip baseline and a slope threshold baseline. **Pre data predictions are committed** (`docs/predictions/{{LADDER_FILE}}`, SIMULATED BY ME, from the assumption ranges only) and a script writes the post calibration predictions from the gentle slope runs before the steep runs. **Tolerance rule (assumption, fixed before the main block):** tolerance = the larger of 3 times the pilot sigma and 0.05, with pilot sigma the pooled within bin standard deviation of the 12 pilot runs; the model is called adequate if at least 80 % of held out runs fall within the tolerance and the entrapment slope is within 3 degrees; if 3 times the pilot sigma exceeds 0.30 the experiment is flagged uninformative. **Synthetic test with known truth (SIMULATED BY ME, `scripts/field_analysis_power.py`)** shows this rule discriminates weakly:

{{TABLE:power}}

The rule passes an exactly right model in under half of the replicates and fails a model that is wrong by construction (`collapse`: slip jumps to 0.85 from 22 degrees) in less than 70 %; at high noise it is lenient and flagged. **So an adequacy pass or fail from one ladder must not be over read. Report the per bin predicted against observed slip with intervals and the entrapment slope as the primary result, and treat the pass or fail as secondary.** Table 9.1 shows what the protocol can and cannot predict before any data:

**Table 9.1: pre data slope ladder predictions** (prior predictive from the assumption ranges, and the error band of the calibrate then predict protocol on synthetic truths).

{{TABLE:ladder}}

Calibrating on 0 to 10 degrees constrains the 15 degree prediction well, the 20 degree prediction weakly, and the 25 degree prediction hardly at all: the slip diverges near entrapment and gentle runs do not fix where that happens. The 25 degree bin is therefore mainly a test of the entrapment slope, not of the slip value. The same check found that calibration needs bounds on f_r and i0, because the two trade off at gentle slopes.

   **Revision of 2026-10-15 (PLANNED; pre registered as stage 6 in `docs/PREDICTIONS.md`).** The Dumont Dunes curve (section 8.8) and the Marsyard sand result (FLD-HV13-3) put the change from moderate to high slip between about 10 and 17 degrees, so the bins became 0, 5, 10, 12.5, 15, 17.5 and 20 degrees (plus or minus 1 degree from 10 to 20), with 25 degrees only if fewer than half of the 20 degree runs entrap. The original file is kept; the revised expected ranges add the Dumont value and widen the upper end of the planning range where it lies above the model band (`docs/predictions/slope_ladder_predictions_2026-10-15.csv`):

{{TABLE:ladder_rev}}

   **The revision has a cost that the synthetic re run exposed** (`results/field_kit/power_study_2026-10-15.csv`, SIMULATED BY ME, synthetic data only):

{{TABLE:power_rev}}

   Without a bin beyond the synthetic truth's entrapment slope (26.3 degrees), the observed entrapment slope is usually undefined and the adequacy rule fails even a correct model. The rule and the revised bins are incompatible as written; the choice between amending the rule, keeping a tethered 25 degree bin, or returning to the original bins is left to the author (`docs/QUESTIONS_FOR_HUDA.md`). The Dumont shaped truth is failed in nearly every replicate, but so is a correct model, so that detection is uninformative.
   **Amended entrapment rule (2026-10-18; PLANNED rule, tested on SIMULATED BY ME synthetic data only).** At the author's decision, and after seeing the 1.3 % result above, the rule was amended and pre registered again (stage 10 in `docs/PREDICTIONS.md`): an entrapment slope that is not reached is reported as "not reached", never as a failure and never as a pass. A run set is adequate only if the slip test and the entrapment test both pass; "slip within tolerance, entrapment not reached" is its own verdict. Re run on the revised bins (`results/field_kit/power_study_2026-10-15_rule_2026-10-18.csv`):

{{TABLE:power_rule}}

   For a correct model at sigma 0.03, entrapment is not reached in {{VAL:pr_model_nrshare}} of replicates; {{VAL:pr_model_nr}} end as "slip within tolerance, entrapment not reached", {{VAL:pr_model_adeq}} as adequate and {{VAL:pr_model_not}} as not adequate. The Dumont shaped truth is called adequate in {{VAL:pr_dumont_adeq}}. **The wrong collapse model is still called adequate in {{VAL:pr_collapse_adeq}} of replicates at sigma 0.03, and the mildly wrong janosi_mean model in {{VAL:pr_janosi10_adeq}} at sigma 0.10.** The rule was not tuned after this run; the next decision is the author's (`docs/QUESTIONS_FOR_HUDA.md`, question 7). Both bin designs stay documented; whether the 1 degree tolerance of the revised bins can be achieved on a real dune is unconfirmed. The calibration bounds in the field analysis and the synthetic truths of this power study still use the original ranges (i0 up to 0.40, f_r up to 0.25); a real rover whose slip scale lies near the widened range would push the calibration to its bound, and the power result does not cover such truths.
6. **Safety and scope.** Tether and recovery line, a second person at all times; slip faces near repose can avalanche. Not a safety case. Heat and dust are handled in `hudasol/dhill`.
7. **What to log for future prediction.** Wheel speeds and currents, RTK and IMU synchronised, effective radius, DEM and RTK slope and aspect, the soil state list, wheel state, ambient conditions, pass number and outcome flags.

The helper script `scripts/analyze_field_runs.py` and the log template `docs/field_log_template.csv` implement the analysis and logging; the script is tested on synthetic data only (including a wrong model case) and has never seen a field measurement. A one page checklist for the field day is `docs/FIELD_DAY_CHECKLIST.md`; low cost rover and measurement kit options, with costs only where a source was retrieved, are in `docs/ROVER_OPTIONS.md`; a proposal outline for a funded validation is `docs/PROPOSAL_SEED.md` (a proposal, not an achievement).

---

## 10. Limitations

**What this work cannot say without field data.**

- It cannot say how well any model predicts slip, sinkage or entrapment of any rover on Arabian dune sand. No published number does either, and the simulation here is not evidence.
- It cannot say that any route is traversable. The model map is lower bound optimistic (30 m grid) and its assumptions are unmeasured.
- It cannot say which model family (RFT, Bekker-Wong, SCM, DEM, learned) is best for dunes; no head to head test exists.
- It cannot give soil parameters for Gulf sand. The only grain sizes of natural dune sand retrieved are from Kuwait and Brazil.

**Limits of the review.**

- Retrieval was constrained to sources reachable from the sandbox and found by a US only search tool. Paywalled journals and standard textbooks were not read, except five papers the author supplied as PDFs on 2026-10-13; the per topic notes list the exact URLs to fetch (`research/raw/*_notes.md`, sections NOT_RETRIEVED).
- Several values are secondary: tilt bed slip numbers for a Mars rover engineering model from a JPL press release (FLD-006, excluded from the comparison), a thesis (TM-022 to TM-024), conference slides (LEG-017 to LEG-020), and RoverDevKit's own re evaluation of other authors' data (SIM-025 to SIM-027).
- Slip is defined differently across papers; several rows in the same figure measure different things. The warning column says how.
- Many simulation validations are plot only. Rows with "qualitative" values carry no error.
- The rows' extraction and the first verification were done by language model agents using the same search tools; shared blind spots (especially on figure only values) are possible.
- UAE items are as of 2026-10-11 and some, such as the Rashid 2 launch date, conflict between sources.

**Not done.** DEM and RFT were reviewed but not run; Chrono was run from 2026-10-20 (section 13.4). No dataset with slip labels from dunes was available, so no learning model was trained. The GLO-30 licence (COP-DEM-GLO-30-F) was read in full in phase 2 (`docs/DATA_AND_LICENSES.md`). Ishigami et al. 2007 and 2009, Heverly et al. 2013, Yu et al. 2024 and Takehana et al. 2025 were supplied by the author as PDFs on 2026-10-13, read in full and added as {{VAL:ver_sup_n}} rows (verified 2026-10-15). Still not retrieved: Wong and Reece 1967 and the Wong textbook parameter table; neither is cited for any number. Until 2026-10-20 the sub grid detector (section 8.7) had not been compared with any real lidar or drone profile; it has since been tested against one metre lidar of three North American dune fields (section 13.5), never against an Arabian slip face; the share of dune crests with an active face and the face height fraction of tall dunes are not published and are assumptions.

**Licence.** All rights reserved: the work is public for reading and review, and any use, modification, distribution or sale needs the author's prior permission (`LICENSE`, `LICENSE-DOCS.md`). Source PDFs and raw downloads are excluded by a CI check.

---

## 11. Verification

**Evidence table, the {{VAL:ver_p4_n}} rows before 2026-10-20** (the {{VAL:p3_rows_new}} rows of phase 5 are described in section 13.1). Separate agents with no access to the extraction notes re read sources. Phase 1 checked **30 rows drawn at random** (seed 20261011) from the 137 rows the extractors had not flagged, plus all 7 flagged rows; phase 2 checked the **remaining 107 rows** in four batches; phase 3 (2026-10-15) checked the **{{VAL:ver_sup_n}} rows read from the PDFs the author supplied**, one verifier per source, each seeing the claim fields only; phase 4 (2026-10-18) checked the **two rows split from FLD-HV13-5**. The table gives two views: the first check of the 170 rows as extracted (rows labelled ALL 144 and ALL 170), and the current table of 171 rows with each row's latest verdict (rows labelled CURRENT). Material error means a wrong value, unit, metric meaning, validation type, vehicle, terrain or slope; minor error means a correct number with a wrong label, section reference or descriptive detail.

{{TABLE:verif}}

All errors were corrected through `research/corrections.csv` (old values in `research/dedup_log.md`). The six material errors found in phase 2: LRN-017 (a three wheeled prototype labelled four wheel), SIM-012 and LRN-006 (validation type: a prepared sand bed and the engineered JPL Mars Yard are `lab`, not `field`), LRN-019 (physical rover results only, `lab`, not `sim-vs-lab`), TM-020 (0.015 was a best case grid entry, the worst case is 0.070) and FLD-029 (an unreferenced capability statement presented as a lab measurement; now validation type `none`). SIM-013 was set to `lab` for consistency with SIM-012 and carries the unit warning. The phase 1 sample had suggested zero material errors; the 107 rows showed that estimate was optimistic, which is why all rows were checked. Verifiers are language model agents using the same search tools, so shared blind spots (for example on figure only values) remain possible; a human spot check of a few rows is advisable. Phase 3 found {{VAL:ver_sup_material}} material errors in {{VAL:ver_sup_n}} rows ({{VAL:ver_sup_material_rate}}), all on validation type and none on a value: TM-TK5 and TM-IS07-5 were labelled as model comparisons although the source compares no simulation with them (now `lab`), and FLD-HV13-5 was labelled `field` although its bedrock limit and its 75 % slip at 20 degrees come from the JPL Marsyard (set to `lab and field`, then split on 2026-10-18 at the author's request into FLD-HV13-5a, `lab`, and FLD-HV13-5b, `field`, both checked again in phase 4). Any discrepancy was {{VAL:ver_sup_any}} of {{VAL:ver_sup_n}} ({{VAL:ver_sup_any_rate}}), mostly page labels. The phase 3 verifiers read the PDFs through their text layer and could not render page images, so figure only values were checked against the text. Duplicate rows between agents were removed (`research/dedup_log.md`); seven Kern et al. candidate rows read in phase 2 duplicate SIM-012 to SIM-014 and were not added.

**Predictions register.** Predictions were written and committed before each run (`docs/PREDICTIONS.md`). Hits and misses so far:

{{TABLE:pred_tally}}

**Report claims, second pass.** {{SECOND_PASS}}

---

## 12. Open questions

1. **Sand variability.** How do grain size and shape distribution, packing, moisture and subsurface cementation (Liwa has sabkha interdunes with a shallow water table) change slip and sinkage, at one vehicle and slope? No quantitative Gulf data were found.
2. **Sim to field gaps.** Does a model calibrated on a flat or gentle slope predict slip at 15 to 25 degrees on the same dune sand? Is slope induced shear collapse near repose important enough that a model must include avalanching?
3. **Resolution.** How far does a 30 m radar DEM understate the slope a rover feels at a slip face, measured against RTK profiles? Can aspect, curvature and dune height infer slip faces better than slope?
4. **Slip measurement.** Can a low cost rover (RTK or total station, wheel encoders, IMU) give a slip estimate that agrees across the definitions used in the literature?
5. **Learning.** Does a model trained on non sand terrain transfer to sand? Does a physical prior hybrid generalise to Arabian dunes with a handful of onboard runs?
6. **Legged and tracked.** What are the same vehicle differences on the same dune slope?
7. **Dynamics.** Crosswind, lateral slip on crests, speed and repeated passes.

---

{{INCLUDE:phase3}}

{{INCLUDE:phase4}}

## Sources and appendices

Appendix A lists every evidence row. Appendix B lists the UAE facts used. Appendix C lists the sources, one line each, with the rows that cite them. All are generated from `research/evidence.csv` and `research/raw/uae_facts.csv` by `scripts/build_report.py`.

