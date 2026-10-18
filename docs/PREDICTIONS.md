# Predictions register

Rule: every prediction is written and committed **before** the run it concerns. Hits and misses are recorded afterwards in the same file, in the "Outcome" column, in a later commit. Nothing is edited after the fact except the Outcome column.

Evidence class for everything in this file: **SIMULATED-BY-ME** or process predictions. Field predictions (PLANNED) live in `docs/predictions/`.

## Stage 1: verification and retrieval (committed before agents were launched, 2026-10-11)

| ID | Prediction made before the run | Outcome |
|---|---|---|
| P1-1 | Among the 107 not yet re-checked evidence rows, the material error rate will be at most 5 %, and the any discrepancy rate (material plus minor) between 15 % and 30 %. | MIXED. Material rate 6/107 = 5.6 %, so the "at most 5 %" part MISSED slightly. Any discrepancy 27/107 = 25.2 %, inside 15 to 30 %: HIT. |
| P1-2 | Across all 144 rows the material error rate will be at most 4 %. | MISSED (marginally). Material rate across all 144 rows is 6/144 = 4.2 % (Wilson 95 % CI 1.9 to 8.8 %), above the 4 % predicted. |
| P1-3 | At least 4 of the 8 items under NOT_RETRIEVED (GLO-30 licence text, Wong table, Wong and Reece 1967, Ishigami 2007 and 2009, Yu et al. 2024, Heverly 2013, Takehana 2025) will stay inaccessible in full text from this sandbox. | HIT. Five items stayed unretrieved (Wong table, Wong and Reece 1967, Ishigami 2007 and 2009, Heverly 2013, Takehana 2025) and Yu et al. 2024 was abstract only: six of eight not read in full. |
| P1-4 | The SIM-013 unit question (unit of the slope term alpha) will be resolved by reading the paper, in favour of degrees being wrong or the printed coefficients being mistyped, because the printed term exceeds 1 at 18 degrees if alpha is in degrees. | PARTLY HIT. Not resolved by the source: the paper never states the unit of alpha. By arithmetic, radians would make the slope term negligible (about 0.0003 at 18 deg) and degrees give slip above 1 at 18 deg and 0.47 m/s. So "degrees wrong" is not supported and "mistyped" cannot be shown; the equation is also even in alpha and not dimensionally consistent as printed. Treated as unresolved at source, resolved as far as reading allows. |


## Stage 2: sub grid slip face detector, three class map, Monte Carlo (committed 2026-10-12 BEFORE any of this code was run)

Pre-specified design (fixed now so the outcome cannot tune it):

- Synthetic ensemble: straight-crested asymmetric dune profiles, stoss slope 6 to 20 deg (published ranges for barchan and transverse dunes, morphology rows PM01 to PM06), active slip face 29.5 to 32.5 deg (PM18, lidar), face height fraction of dune height 0.54 to 1.0 (PM08, small dunes 7 to 10 m; extended to 0.2 to 1.0 for tall dunes as an ASSUMPTION), apron below the face at the stoss slope (ASSUMPTION), height 5 to 120 m log uniform, random phase. The share of crests with an active face is not published (not found), so baseline pi = 1 (worst case) with pi = 0.3 and 0.6 as sensitivities.
- Truth in the synthetic ensemble: "an active face (slope of 28 deg or more) lies inside the cell footprint".
- Features per cell: Horn slope, curvature along the steepest direction, slope break (largest slope difference to the 8 neighbours), local relief in a 7 by 7 window. Model: logistic regression, trained per posting (30, 60, 90 m, box mean sampling; point sampling as a sensitivity).
- Map classes per cell. Monte Carlo: 256 Latin hypercube draws of (phi, f_r, i0, i_max) over the existing ranges, seeds 20261014 (area A), 20261015 (area B), 20261016 (area C). For each draw, a cell is "passable" if at least 4 of its 8 headings are passable. BLOCKED if passable in at most 5 % of draws; TRAVERSABLE if passable in at least 95 % of draws AND the face probability is below 0.20; UNKNOWN otherwise (two causes recorded: assumption sensitive, and sub grid face risk). The 0.20 threshold is a free choice and is swept in the coverage versus certainty curve.
- Areas: A_south_Liwa and B_RubAlKhali_megadunes as in phase 1, plus C, a Rub' al Khali linear dune window (tile N20E052, Saudi Arabia; the UAE tiles I hold show star and network dunes, not linear dunes).

| ID | Prediction made before the run | Outcome |
|---|---|---|
| S2-1 | Detector skill on held out synthetic profiles at 30 m: AUC between 0.70 and 0.90 (features see tall dunes but not low ones). Skill at 90 m is lower than at 30 m. | MIXED. AUC at 30 m is 0.92, above the predicted 0.70 to 0.90 band (MISS on the band). Skill at 90 m (0.857) is lower than at 30 m (HIT on direction); 60 m is 0.84. |
| S2-2 | The UNKNOWN share in A_south_Liwa at 30 m (pi = 1, baseline) is between 40 % and 80 %, and it rises with coarser posting (90 m above 60 m above 30 m). | MISSED. The UNKNOWN share in A_south_Liwa at 30 m is 8.6 %, not 40 to 80 %. It does not rise monotonically with posting: 8.6 % (30 m), 9.1 % (60 m), 7.1 % (90 m). A smoke test on three 0.03 degree windows (8 to 15 %) had been run before the full run, so this miss was foreseeable. |
| S2-3 | The BLOCKED class stays at or below 2 % of cells at 30 m in every area (phase 1 found 0.2 to 1 % of edges blocked). | HIT. BLOCKED is 0.00 to 0.01 % of cells at 30 m in all three areas. |
| S2-4 | Robust to the four assumed parameters: at least 90 % of cells have a unanimous passable verdict (passable in at most 5 % or at least 95 % of draws) at 30 m. | HIT. Unanimous passable verdict across the 256 draws for 99.2 % of cells (A), 97.0 % (B) and 100 % (C) at 30 m. |
| S2-5 | The UNKNOWN share in the linear dune window C at 30 m is at least 10 percentage points lower than in A_south_Liwa (smaller relief). | MISSED, direction right. C has 2.5 % UNKNOWN at 30 m against 8.6 % in A_south_Liwa: 6.1 points lower, less than 10. |
| S2-6 | Coverage versus certainty: demanding at most 5 % face probability on TRAVERSABLE cells leaves coverage (share of cells not UNKNOWN) below 30 % in A_south_Liwa at 30 m. | MISSED. At face probability below 0.05 the coverage is 67 % (A, 30 m), not below 30 %. Coverage falls to 42 % only at a threshold of 0.02. |
| S2-7 | Treating UNKNOWN as impassable, fewer than half of the origin destination pairs of phase 1 stay reachable in A_south_Liwa at 30 m (phase 1: nearly all reachable). | MISSED. 10 of 10 origin destination pairs stay reachable at 30 m in every area. At 60 and 90 m the reachable share falls to 70 and 80 % (A), 20 and 40 % (B), 80 and 60 % (C), largely because endpoints themselves become UNKNOWN. |
| S2-8 | Lowering the assumed share of crests with an active face from 1.0 to 0.3 lowers the A_south_Liwa UNKNOWN share at 30 m by less than 20 percentage points (the DEM features, not the prior, carry the result). | HIT. Lowering pi from 1.0 to 0.3 lowers the A_south_Liwa UNKNOWN share from 8.6 % to 2.9 % (5.7 points, less than 20). |


## Stage 3: field kit, analysis rule and synthetic power study (committed 2026-10-12 BEFORE the study was run)

Design fixed now. Script: `scripts/field_analysis_power.py` (to be written after this commit). Everything here concerns SYNTHETIC data and the analysis code, not the world.

- Truth generators: `model` (the exponential slip law, f_r 0.14, i0 0.22, phi 33), `janosi_mean` (same parameters, contact-patch-averaged shear law form, a modest structural difference), `collapse` (exponential law below 20 deg, slip jumps to 0.85 from 22 deg upward, a stand-in for avalanche or bearing failure; the model is WRONG here by construction).
- Noise sigma 0.03, 0.06, 0.10. Bins 0, 5, 10, 15, 20, 25, 28 deg, 6 runs per bin; the first 3 runs in each of the 5, 10, 15 and 20 deg bins are the pilot block. 300 replicates per cell, seeds 30000 and up.
- Tolerance rule: tol = max(3 x pilot sigma, 0.05), pilot sigma = pooled within bin standard deviation of the pilot runs. Adequate if at least 80 % of held out runs (above 10 deg) lie within tol and the entrapment slope is within 3 deg (as in the field plan).
- Slope ladder pre-data prediction file: prior predictive slip at 0, 5, 10, 15, 20, 25 deg from the assumption ranges (phi 28 to 38 or phi measured 33 plus or minus 2, f_r 0.05 to 0.25, i0 0.05 to 0.40), 4000 draws, seed 20261017, and the error band of the calibrate then predict protocol (calibrate on 0, 5, 10 deg, noise sigma 0.06).

| ID | Prediction made before the run | Outcome |
|---|---|---|
| S3-1 | truth = model, sigma = 0.03: the adequacy pass rate is at least 75 %. | MISSED. Adequacy pass rate for the exactly right model at sigma = 0.03 is 46 % (300 replicates), not 75 %. Note: a first version of the entrapment estimator returned the bin centre (28 degrees became 30) and failed correct models; it was fixed before this run, and the 46 % is with the fixed estimator. |
| S3-2 | The rule gets more lenient as noise grows: for truth = model the pass rate at sigma = 0.10 is at least as high as at sigma = 0.03. | MISSED. For truth = model the pass rate falls with noise: 46 % (0.03), 39 % (0.06), 34 % (0.10). The leniency prediction holds only for truth = janosi_mean (24 %, 56 %, 78 %). |
| S3-3 | truth = collapse: the failure (detection) rate is at least 90 % at sigma = 0.03 and at most 60 % at sigma = 0.10. | MISSED on both parts. Failure rate for truth = collapse is 69 % at sigma = 0.03 (predicted at least 90 %) and 62 % at 0.10 (predicted at most 60 %). The rule fails a correct model (54 % failure) almost as often as this wrong one (69 %): it discriminates weakly. |
| S3-4 | truth = janosi_mean: the detection rate is between 20 % and 80 % at sigma = 0.03 and at most 30 % at sigma = 0.10 (a structural error of this size is mostly hidden by noise). | HIT on both parts. truth = janosi_mean is detected in 76 % of replicates at sigma = 0.03 (inside 20 to 80 %) and 22 % at 0.10 (at most 30 %). |
| S3-5 | Prior predictive 90 % band of slip at 25 deg is at least 0.5 wide, and the calibrate then predict error band at 25 deg (sigma = 0.06) is at least twice narrower than the prior band. | MIXED. The prior 90 % band at 25 deg is 0.84 wide (0.16 to 1.00): HIT. The calibrate then predict error band at 25 deg (sigma 0.06, phi known) is 0.90 wide (-0.41 to +0.49), not narrower than the prior band: MISS. The protocol is informative at 15 deg (band 0.12) and weakly at 20 deg (0.49), and not at 25 deg. |
| S3-6 | The prior predictive entrapment slope (slip 0.8) has median between 24 and 34 deg and a 90 % range wider than 10 deg. | HIT. Prior predictive entrapment slope median 25.3 deg, 90 % range 17.8 to 32.2 deg (14.4 deg wide). |


## Stage 4: verification of the 26 supplementary rows (written 2026-10-15)

Timing, stated plainly: six verifier agents were launched at about 19:35 (AST) on 2026-10-15 on batches 8 to 13 (`research/verify_batch8.csv` to `research/verify_batch13.csv`); these predictions were written and committed a few minutes later, before any verifier output file existed or was read. Each verifier re read the supplied source PDF with no access to the extraction notes or comparability warnings.

| ID | Prediction made before the outcome was seen | Outcome |
|---|---|---|
| P4-1 | Among the 26 supplementary rows (`research/phase2/supplied_pdf_rows_2026-10-13.csv`), at most 2 rows (7.7 %) will be judged a material error. | MISSED. 3 of 26 (11.5 %, Wilson 95 % CI 4.0 to 29.0 %) were material errors (TM-TK5, TM-IS07-5, FLD-HV13-5), all on validation type; no value was wrong. |
| P4-2 | Among the 26 rows, the any discrepancy rate (minor plus material) will be between 20 % and 50 % (rows read from supplied PDFs carry many page and section labels, which were the commonest minor errors before). | MISSED. 15 of 26 (57.7 %), above the band. Direction of the reasoning held: most minor errors were page labels, plus the word dry used where the source does not say so (TM-YU1 to TM-YU4). |
| P4-3 | Across all 170 rows the material error rate will stay at or below 5.0 %. | MISSED (marginally). 9 of 170 (5.3 %, Wilson 95 % CI 2.8 to 9.8 %). |
| P4-4 | At least one of the six Heverly 2013 rows (FLD-HV13-1 to 6) will receive a non correct verdict, most likely on validation type or location, because several rows mix the Marsyard (a prepared yard, counted as lab) with natural sites. | HIT. Three of six were non correct: FLD-HV13-5 material (Marsyard and Tecopa mixed under `field`, now `lab and field`), FLD-HV13-1 minor (the paper does give slip in percent and slope in degrees, on the Figure 12 axes), FLD-HV13-6 minor (the agreement is between Mars data and Earth test data, not a test of the onboard polynomial). |


## Stage 5: published anchors, Dumont Dunes and Ishigami 2009 (written 2026-10-15, BEFORE the comparison script was written or run)

**Both comparisons are of unlike vehicles and soils.** The model is a lumped slope to slip law (`src/dunerover/slipmodel.py`) with assumed parameter ranges; it is not changed here. Script to be written after this commit: `scripts/anchor_comparisons.py`, outputs in `results/anchors/`. Evidence class of every output: SIMULATED BY ME, simulation only, model assumption dependent. The published inputs are PUBLISHED rows FLD-HV13-1, FLD-HV13-2 and TM-IS09-1 to TM-IS09-5 (all verified 2026-10-15).

How these predictions were formed: from results already in the repository (`results/anchor_check.csv`: nominal model slip 0.20 at 16 deg and 0.27 at 20 deg; stage 3 prior predictive entrapment slope) and rough hand arithmetic on the model equation. No comparison code existed when they were committed.

Design fixed now:

- **(a) Dumont Dunes.** Published curve: slip % = 26.197 - 8.849 s + 1.281 s^2 - 0.034 s^3 (s = slope in deg; ascending powers, the only ordering that reproduces the text), compared only on 4 to 21 deg, grid 0.1 deg, converted to a fraction. Model: direct ascent (no cross slope), nominal parameters, and an envelope of 4000 Latin hypercube draws of phi 28 to 38 deg, f_r 0.05 to 0.25, i0 0.05 to 0.40 (the existing ranges), seed 20261020, slip capped at 1 (entrapment). Two envelopes: min to max over draws, and the 5 to 95 % band. Reported: fraction of the Dumont grid inside each envelope; slope where the Dumont curve, the nominal model and the model median cross 50 % slip; slopes where the Dumont curve leaves each envelope; share of draws within plus or minus 0.10 of Dumont at every grid point. Differences stated with the result: Scarecrow is a 340 kg six wheel rover with 50 cm grousered wheels, slope is rover tilt, slip is 1 minus traverse over commanded distance, Dumont soil parameters are not reported, the fit is to eight runs.
- **(a, post hoc) Recalibration test.** Least squares fit of phi, f_r, i0 (bounded to the same ranges) to the Dumont grid. Labelled POST HOC; the untuned result is reported first. It asks only whether the model form can reproduce the published shape, not whether the model is right.
- **(b) Ishigami 2009, Table I.** Side slope traversal at 5 and 10 deg (model: along slope 0, cross slope = slope angle, friction circle as in the model). phi = 38.0 deg from Table I (c = 0 matches the model). Table I gives no f_r and no contact length, so: (b1) phi 38, f_r and i0 over their assumed ranges, 4000 draws, seed 20261021; (b2) phi 38, i0 from Table I kx = 0.07 m divided by the largest possible contact arc for r = 0.055 m (a quarter circumference, 0.0864 m), that is i0 = 0.81 as a lower bound on i0 under the model's own definition i0 = K/L, f_r over its assumed range. Compared with: the measured slip ratio of about 0.5 in case B (10 deg, feed forward control, TM-IS09-3); Ishigami's own model value that slip must exceed 0.6 for positive thrust at 5 deg (TM-IS09-2, a model to model comparison); the feedback control runs (slip below 0.4, TM-IS09-5) are a controlled slip and are reported but not scored.

| ID | Prediction made before the run (tolerance in the statement) | Outcome |
|---|---|---|
| A5-1 | The Dumont curve crosses 50 % slip at 12.6 deg (plus or minus 0.3). The nominal model crosses 50 % between 23 and 28 deg, so the nominal model is at least 10 deg too permissive against Dumont. | HIT. Dumont crosses 50 % at 12.59 deg; the nominal model at 25.46 deg, 12.9 deg later (`results/anchors/summary.json`). |
| A5-2 | At least 90 % of the Dumont grid (4 to 21 deg) lies inside the min to max envelope of the 4000 draws (the envelope is very wide). | HIT. 100 % of the Dumont grid lies inside the min to max envelope; the envelope is so wide that this says little. |
| A5-3 | Between 30 % and 70 % of the Dumont grid lies inside the 5 to 95 % band; the Dumont curve leaves the band upwards (more slip than the model) at a slope between 11 and 16 deg and stays above it to 21 deg. | MIXED. 57.3 % of the grid lies inside the 5 to 95 % band (HIT on the 30 to 70 % part). The Dumont curve leaves the band upwards at 10.7 deg, earlier than the predicted 11 to 16 deg (MISS), and it re enters the band at 18.0 deg because the upper band reaches 1.0 near 19 deg, so it does not stay above to 21 deg (MISS). |
| A5-4 | The model median (over draws) crosses 50 % slip between 20 and 28 deg. | HIT. The model median crosses 50 % at 22.90 deg. |
| A5-5 | Fewer than 2 % of the 4000 draws stay within plus or minus 0.10 of the Dumont curve at every grid point. | HIT. No draw (0 of 4000) stays within 0.10 of the Dumont curve at every grid point. |
| A5-6 | POST HOC fit: the best bounded fit has RMSE between 0.03 and 0.10 against the Dumont grid, and at least one of the three parameters sits at a bound of its range. | HIT. POST HOC fit RMSE 0.085 with phi at its lower bound (28 deg) and i0 at its upper bound (0.40), f_r 0.139; the fitted curve crosses 50 % at 13.5 deg. Even pushed to the edge of its ranges the model form misses the S shape by up to 0.13. |
| A5-7 | A change of 0.0005 in c3 (its rounding) moves the Dumont slip at 21 deg by between 4 and 5 percentage points. | HIT. 4.63 percentage points at 21 deg (simple arithmetic, so a weak test). |
| I5-1 | (b1) At 10 deg cross slope the model envelope (min to max) with phi 38 and assumed f_r, i0 does not reach the measured slip ratio of about 0.5: its maximum is below 0.35. | HIT. With phi 38 and assumed f_r, i0 the model reaches at most 0.197 at 10 deg; the measured slip ratio of about 0.5 is far outside. |
| I5-2 | (b1) At 5 deg cross slope the envelope maximum is below 0.25, so Ishigami's model value (slip above 0.6 needed for positive thrust) is outside it. | HIT. Maximum 0.164 at 5 deg; Ishigami's model value of more than 0.6 is outside. |
| I5-3 | (b2) With i0 = 0.81, the model slip at 10 deg cross slope spans from about 0.2 to about 0.4 over the f_r range (each end plus or minus 0.07); the measured 0.5 is above it or at its upper edge. | HIT. With i0 = 0.81 the model spans 0.217 to 0.403 at 10 deg; the measured 0.5 is above the whole range. |

Note on stage 5: nine of ten predictions hit and one was mixed, but several were informed by hand arithmetic on the model equation before the commit (stated above the table), so the hits show that the script does what the equation says rather than foresight about the world. The informative results are the comparisons themselves, reported in `results/anchors/` and report section 8.8.


## Stage 6: revised slope ladder bins and expected slip ranges (written 2026-10-15, BEFORE any code for it was written or run)

Why the ladder is revised (PUBLISHED inputs, verified rows): at Dumont Dunes slip rises from below 50 % at 12.5 deg to about 75 % at 16 deg and about 90 % at 20 deg (FLD-HV13-1, FLD-HV13-2); on Marsyard sand both test rovers embedded at about 17 deg (FLD-HV13-3); Ishigami 2009 measured a slip ratio of about 0.5 on a 10 deg side slope with a 13.5 kg rover (TM-IS09-3). Stage 5 showed the model's expected slip is too low on sand slopes, and stage 3 showed the protocol is uninformative at 25 deg (S3-5). The 2026-10-12 ladder has only the 10, 15 and 20 deg bins in the range where the published curves bend.

Design fixed now (the 2026-10-12 prediction files are not edited; a new dated file is written):

- **Bins (PLANNED):** direct uphill at 0, 5, 10, 12.5, 15, 17.5 and 20 deg; 25 deg only if fewer than half of the 20 deg runs end in entrapment. Slope tolerance plus or minus 1 deg for the 10 to 20 deg bins (needed so that bins 2.5 deg apart do not overlap), plus or minus 2 deg for 0, 5 and 25 deg. Pilot unchanged (3 runs at each of 5, 10, 15, 20 deg). Cross slope block unchanged (10, 15, 20 deg).
- **Analysis code:** a run may carry its target bin (`bin_deg`); when present the analysis groups runs by it instead of rounding the measured slope to 5 deg. Defaults are unchanged, so the stage 3 study reproduces exactly.
- **Expected slip ranges (new file `docs/predictions/slope_ladder_predictions_2026-10-15.csv`):** for each bin, (1) the unchanged model prior predictive, same code, ranges and seeds as 2026-10-12 (SIMULATED BY ME); (2) the Dumont cubic value where the slope lies inside 4 to 21 deg (PUBLISHED, a different and heavier vehicle); (3) a planning range from the model 5th percentile to the larger of the model 95th percentile and the Dumont value (PLANNED; it widens the upper end only where a published sand curve says more slip is possible). Cross slope 10 deg: the measured Ishigami value is listed as a reference.
- **Synthetic power study re run** with the new bins (`scripts/field_analysis_power.py --design 2026-10-15`, output `results/field_kit/power_study_2026-10-15.csv`; the 2026-10-12 output is kept): truths model, janosi_mean and collapse as before, plus a new truth `dumont` (the Dumont cubic between 4 and 21 deg, 0.10 below 4 deg and slip 1 above 21 deg, as the source text describes; a PUBLISHED shape used as a synthetic truth, not a prediction for any rover). Noise 0.03, 0.06, 0.10; 300 replicates; seeds 30000 and up; 6 runs per bin; jitter plus or minus 1.0 deg in the 10 to 20 deg bins and 1.5 deg elsewhere; the 25 deg bin always included in the synthetic runs.

| ID | Prediction made before the run (tolerance in the statement) | Outcome |
|---|---|---|
| L6-1 | The model prior predictive at 0, 5, 10, 15, 20 and 25 deg in the new file equals the 2026-10-12 values to within 1e-12 (same seeds and draws). | HIT. Every prior predictive value at 0, 5, 10, 15, 20 and 25 deg equals the 2026-10-12 file to within 1e-12. The protocol error band columns differ by up to 1.2e-8, which I attribute to different numpy and scipy versions in the least squares step (not checked further). |
| L6-2 | The Dumont value lies above the model prior 95th percentile (friction angle unknown) at 12.5, 15 and 17.5 deg, and inside the 5 to 95 % band at 5 and 10 deg. | HIT. Dumont lies above the model 95th percentile at 12.5 (0.49 against 0.42), 15 (0.67 against 0.53) and 17.5 deg (0.81 against 0.76), and inside the band at 5 and 10 deg. |
| L6-3 | New design, truth = model, sigma 0.03: adequacy pass rate within 15 points of the stage 3 value (46 %). | MISSED, badly. Under the revised bins a correct model passes the adequacy rule in 1.3 % of replicates at sigma 0.03 (stage 3: 46 %). A post hoc diagnostic (60 replicates, not pre registered) shows why: the synthetic truth entraps at 26.3 deg, above the top bin, so the observed entrapment slope is undefined in 97 % of replicates and the rule, which needs it, fails; the share of held out runs within tolerance actually rose (median 0.91 against 0.81). The revised ladder and the stage 3 adequacy rule are incompatible as written. |
| L6-4 | New design, truth = collapse, sigma 0.03: failure (detection) rate between 30 % and 69 % (lower than stage 3 because the 28 deg bin is gone). | HIT. Collapse is failed in 47.3 % of replicates at sigma 0.03. |
| L6-5 | New design, truth = dumont: failure (detection) rate at least 90 % at sigma 0.03 and at least 80 % at sigma 0.10 (the model form cannot follow the S shaped curve, stage 5). | HIT, but uninformative. Dumont is failed in 100 % of replicates at sigma 0.03 and 94.7 % at 0.10; a correct model is failed almost as often (98.7 % at 0.03), so this detection says nothing about the rule's power. |
| L6-6 | The existing synthetic wrong model test (`test_blatantly_wrong_model_is_always_failed`) still passes, and the same test on the new design also fails the blatantly wrong model in 10 of 10 replicates. | HIT. The existing wrong model test passes and the new design test fails the blatantly wrong model in 10 of 10 replicates. |

Note on stage 6: the stage 3 design reproduces exactly from the changed code (all rates in `results/field_kit/power_study.csv` identical; medians differ only around 1e-10). The miss on L6-3 is the main finding: denser bins in the transition improve the slip comparison but remove the evidence the entrapment criterion needs. Whether to amend the criterion or keep a steep bin is the author's decision (`docs/QUESTIONS_FOR_HUDA.md`); nothing was changed to make the rule pass.

## Corrections notes (appended 2026-10-15 after the adversarial review; no prediction or earlier outcome text was edited)

- Formatting: the outcome cells of A5-1 to A5-7, I5-1 to I5-3 and L6-1 to L6-6 were first written with a doubled cell separator, so GitHub did not show them; the separator was corrected in a formatting only commit. Prediction text was not changed.
- S2-4 outcome says 99.2 % for area A; `results/subgrid/robustness_to_assumed_parameters.csv` gives 0.99148, which rounds to 99.1 % (the report uses 99.1 %).
- S3-5 outcome gives the lower end of the 25 deg protocol band as -0.41; the file value is -0.4047, which the report rounds to -0.40.
- S2-4 and the report call a cell "unanimous" when it is passable in at most 5 % or at least 95 % of the 256 draws, as defined in the stage 2 design; it does not mean all 256 draws agree.
- Stage 4 was in effect concurrent with the verifier runs: the predictions were committed about one minute after the verifiers were launched and before any output existed, as stated above the stage 4 table.
- The post hoc diagnostic quoted in the L6-3 outcome (60 replicates, 97 %, medians 0.91 and 0.81, truth entrapment at 26.3 deg) is now reproducible: `scripts/diagnose_ladder_entrapment.py`, output `results/field_kit/diagnostic_entrapment_2026-10-15.csv` (26.25 deg; 0.967; 0.906 and 0.815).


## Stage 7: Dumont Dunes as a prior for the slip scale i0 (stretch study, written 2026-10-15 BEFORE the script was written or the elevation tiles were downloaded)

**SIMULATED BY ME, simulation only, model assumption dependent. A sensitivity study, not a change to the model or to any earlier result.** It uses a published curve for a different, heavier vehicle on a different dune (FLD-HV13-1) as if it described the slip scale of the rover the map is for; that assumption is not supported and is the point being tested.

Design fixed now. Script to be written after this commit: `scripts/study_dumont_prior.py`; outputs `results/dumont_prior/`.

- Areas A_south_Liwa, B_RubAlKhali_megadunes, C_RubAlKhali_linear at 30 m only, same crops, the same 256 Latin hypercube draws and seeds as phase 2 (20261014, 20261015, 20261016), the same detector, face threshold 0.20 and class rules.
- Baseline: the phase 2 draws unchanged (a reproduction check against `results/subgrid/class_shares.csv`).
- Dumont prior, unclipped: in each draw keep phi, f_r and i_max and replace i0 by the value in 0.05 to 3.0 that minimises the squared difference between the model (direct ascent, slip capped at 1) and the Dumont cubic on 4 to 21 deg (0.1 deg grid).
- Dumont prior, clipped: the same i0 clipped to the existing range 0.05 to 0.40.
- Reported per area: TRAVERSABLE, BLOCKED and UNKNOWN shares (and the two UNKNOWN causes), and the distribution of the fitted i0.

| ID | Prediction made before the run (tolerance in the statement) | Outcome |
|---|---|---|
| D7-1 | The baseline reproduces the committed 30 m class shares of all three areas to within 0.1 percentage point. |  HIT. The baseline equals the committed 30 m shares exactly in all three areas (difference 0.0). |
| D7-2 | The median Dumont fitted i0 over the 256 draws of area A lies between 0.4 and 2.0, outside the assumed range of 0.05 to 0.40. |  HIT. Median fitted i0 0.581 in area A (5 to 95 %: 0.286 to 0.944); 81 % of draws lie above 0.40. |
| D7-3 | Unclipped Dumont prior: BLOCKED in area A at 30 m rises above 1 % (baseline under 0.1 %). |  MISSED. BLOCKED in area A rises only to 0.32 % (B: 1.68 %, C: 0.00 %). |
| D7-4 | Unclipped Dumont prior: UNKNOWN in area A at 30 m lies between 15 % and 60 % (baseline 8.6 %). |  MISSED. UNKNOWN in area A is 8.95 %, barely above the baseline 8.60 % (B 10.89 to 12.24 %, C 2.54 to 2.56 %). The 30 m slopes are mostly gentler than the slopes where the Dumont prior changes the verdict, so the map hardly moves; the UNKNOWN share stays driven by the sub grid face risk. |
| D7-5 | Clipped Dumont prior: UNKNOWN in area A lies between the baseline and the unclipped value. |  HIT, trivially. Clipped: 8.61 %, between 8.60 % and 8.95 %. |
| D7-6 | Under the unclipped prior, area C has the lowest UNKNOWN share of the three areas, as in the baseline. |  HIT. C has the lowest UNKNOWN share (2.56 %) under the unclipped prior. |


## Stage 8: split of FLD-HV13-5 (written 2026-10-18, BEFORE the split rows exist or are verified)

Design: following Huda's answer of 2026-10-18, FLD-HV13-5 is replaced by FLD-HV13-5a (lab: JPL Marsyard bedrock and constructed cohesive soil slopes) and FLD-HV13-5b (field: Tecopa desiccated lake bed), through a `split_into` entry in `research/corrections.csv` handled by `scripts/consolidate_evidence.py`. One fresh verifier agent re reads the Heverly PDF and judges both rows (batch 14). Error rates are then reported two ways: the first check of the extraction (170 rows as first extracted, unchanged by construction) and the current table (171 rows, each row with its latest verdict; the two split rows count with their batch 14 verdicts and FLD-HV13-5 drops out).

| ID | Prediction made before the run | Outcome |
|---|---|---|
| P8-1 | Neither split row is judged a material error. |  HIT. FLD-HV13-5a correct, FLD-HV13-5b minor; no material error (`research/verify_out_batch14.csv`). |
| P8-2 | At least one split row receives a minor verdict (page or wording), because the two Tecopa slip figures (Sec 6.2 and Sec 10) are not tied to the same site in the text. |  HIT, for a different reason than predicted. The minor error on FLD-HV13-5b is the slope range (flat to 28 deg covers all cohesive soil tests, not Tecopa alone), not the two Tecopa slip figures. |
| P8-3 | Current table: material errors 8 of 171 (4.7 %) and, for the current supplementary rows, 2 of 27 (7.4 %), if P8-1 holds. |  HIT. Current table 8 of 171 (4.7 %); current supplementary rows 2 of 27 (7.4 %). This follows arithmetically from P8-1, so it is not independent evidence. |


## Stage 9: widened slip scale range (written 2026-10-18, BEFORE any code for it was written or run)

Following Huda's answer to question 1 (2026-10-18). **SIMULATED BY ME, simulation only, model assumption dependent.** The original ranges stay the default and every earlier result stays as it is; the new runs are written beside them.

Design fixed now:

- **Range sets.** `original`: as before (i0 0.05 to 0.40, nominal 0.20; f_r 0.05 to 0.25, nominal 0.12). `widened_i0`: i0 0.05 to 1.20 with nominal 0.81, the lower bound implied by Ishigami et al. 2009 Table I under the model definition i0 = K / contact length (TM-IS09-2; the upper end 1.20 is an ASSUMPTION chosen to contain that value and the Dumont fitted i0 of stage 7, 5 to 95 % 0.29 to 0.94); everything else unchanged. `widened_i0_fr`: as `widened_i0` and f_r 0.05 to 0.35 (ASSUMPTION, a test of the f_r range; nominal 0.12 unchanged).
- **Runs.** Phase 1 (`python -m dunerover.study --range-set ...`, outputs `results/widened_i0/`, `results/widened_i0_fr/`), phase 2 (`python -m dunerover.study_subgrid --range-set ...`, outputs `results/subgrid_widened_i0/`, `results/subgrid_widened_i0_fr/`), and the anchors (`scripts/anchor_comparisons.py --range-set ...`, outputs `results/anchors_widened_i0/`, `results/anchors_widened_i0_fr/`), all with the same seeds as the original runs.
- These predictions were informed by hand arithmetic on the model equation (nominal crossing, Ishigami envelope ends) and by the stage 7 result; such hits are not independent evidence.

| ID | Prediction made before the run (tolerance in the statement) | Outcome |
|---|---|---|
| W9-1 | `widened_i0`: the nominal model crosses 50 % slip between 8 and 13 deg, so it now crosses before or near the Dumont curve (12.6 deg) instead of 12.9 deg after it. |  HIT. Nominal crossing 10.15 deg (Dumont 12.59): the nominal model now predicts too much slip below about 12 deg, the opposite error to before (`results/anchors_widened_i0/summary.json`). |
| W9-2 | `widened_i0`: the median of the draws crosses 50 % slip between 12 and 18 deg. |  HIT. Median of draws 12.26 deg. |
| W9-3 | `widened_i0`: at least 80 % of the Dumont grid lies inside the 5 to 95 % band (original: 57.3 %). |  HIT. 100 % of the Dumont grid lies inside the 5 to 95 % band (original 57.3 %); the band is now so wide that this says little. |
| W9-4 | `widened_i0`, Ishigami b1 (phi 38): the envelope maximum at 10 deg side slope lies between 0.50 and 0.70, so the measured slip ratio of about 0.5 is inside it (original: maximum 0.20); at 5 deg the maximum stays below 0.6, so Ishigami's model value is still outside. |  HIT. b1 maximum 0.59 at 10 deg (measured 0.5 now inside) and 0.49 at 5 deg (Ishigami's 0.6 still outside). |
| W9-5 | Phase 2, 30 m, `widened_i0`: UNKNOWN is between 8.6 and 12 % in A, between 10.9 and 15 % in B and between 2.5 and 4 % in C; BLOCKED stays below 1 % in A. |  MISSED, badly. UNKNOWN at 30 m is 33.9 % in A, 39.2 % in B and 11.2 % in C (original 8.6, 10.9, 2.5 %); BLOCKED stays at or below 0.02 %. Stage 7 had suggested a small change, but there i0 was fitted to each draw's phi and f_r, so the draws agreed with each other; here i0 is drawn independently over a range six times wider, so many more cells change verdict between draws. |
| W9-6 | Phase 1, `widened_i0`: the median climbing limit across the Latin hypercube draws falls by at least 3 deg from 23.4 deg. |  HIT. Median climbing limit across draws 13.5 deg, down 9.9 deg from 23.4 deg; the 5th percentile is 2.4 deg. |
| W9-7 | `widened_i0_fr` adds at most 3 percentage points of UNKNOWN to `widened_i0` in each area at 30 m. |  MISSED, badly. Widening f_r to 0.35 as well raises UNKNOWN at 30 m to 92.6 % (A), 90.1 % (B) and 97.4 % (C); with f_r near 0.35 and large i0 some draws cannot climb any slope, so almost every cell becomes assumption sensitive. |
| W9-8 | Even with the widened range the post hoc fit to the Dumont curve keeps an RMSE above 0.05: the model form, not only the range, misses the S shape. |  HIT. Post hoc fit RMSE 0.071 (original 0.085), with phi and f_r at their bounds and i0 0.66 inside the range; the S shape is still missed. |


## Stage 10: amended entrapment rule for the 2026-10-15 ladder (written 2026-10-18, BEFORE the amended rule was coded or run)

**This amendment was made after seeing the stage 6 result** (a correct model called adequate in 1.3 % of synthetic replicates under the 2026-10-15 bins, `docs/PREDICTIONS.md` L6-3), at Huda's decision (question 4, option a). It is therefore not a blind rule; it is fixed here before its own power run, and it will not be tuned after that run. The 2026-10-12 and 2026-10-15 prediction files and the stage 3 and stage 6 results are not changed.

Amended rule (applies to the 2026-10-15 design):
- Slip test, unchanged: at least 80 % of held out runs within the tolerance (the larger of 3 times the pilot sigma and 0.05); uninformative flag unchanged.
- Entrapment test, three outcomes: **pass** (observed entrapment slope defined and within 3 deg of the predicted one), **fail** (defined and more than 3 deg away), **not reached** (no slope bin with at least half of its runs entrapped). Not reached is reported as such, never as a failure, and never as a pass.
- Verdict: **adequate** only if the slip test and the entrapment test both pass; **not adequate** if either test fails; **slip within tolerance, entrapment not reached** if the slip test passes and entrapment is not reached. The boolean `adequate` keeps its old meaning, so the stage 6 numbers do not change.
- Power study: `scripts/field_analysis_power.py --design 2026-10-15 --rule 2026-10-18`, same truths (model, janosi_mean, collapse, dumont), noise 0.03, 0.06, 0.10, 300 replicates, seeds 30000 and up; output `results/field_kit/power_study_2026-10-15_rule_2026-10-18.csv`. Reported per cell: the adequate rate, the not adequate rate, the not reached verdict rate, and the share of replicates where entrapment is not reached.

| ID | Prediction made before the run (tolerance in the statement) | Outcome |
|---|---|---|
| R10-1 | truth = model, sigma 0.03: entrapment is not reached in at least 90 % of replicates; the adequate rate stays below 5 % (as in stage 6, by construction); the "slip within tolerance, entrapment not reached" verdict lies between 60 % and 95 %. |  HIT. Not reached 97.7 %; adequate 1.3 %; slip within tolerance, entrapment not reached 74.3 %. The other 24.3 % of correct model replicates are not adequate because the slip test fails. |
| R10-2 | truth = model, sigma 0.10: the "slip within tolerance, entrapment not reached" verdict lies between 40 % and 90 %. |  HIT. 79.7 % at sigma 0.10 (38.7 % of those replicates are flagged uninformative). |
| R10-3 | truth = dumont: the not adequate rate is at least 90 % at sigma 0.03 (the slip test fails, so not reached cannot rescue it). |  HIT. Not adequate in 100 % of replicates at sigma 0.03. |
| R10-4 | truth = collapse, sigma 0.03: entrapment is reached in at least 80 % of replicates (slip 0.85 from 22 deg), and the adequate (false pass) rate lies between 10 % and 60 %. |  HIT, and it is a poor result for the rule: entrapment is reached in 100 % of collapse replicates, and the wrong collapse model is called adequate in 52.7 % at sigma 0.03 (48.0 % at 0.06, 45.3 % at 0.10), because it entraps at the 25 deg bin close to where the calibrated model predicts. |
| R10-5 | The amended rule separates a correct model from the dumont truth: the share of "adequate" plus "slip within tolerance, entrapment not reached" is at least 50 points higher for truth = model than for truth = dumont at sigma 0.03. |  HIT. Adequate plus not reached: 75.6 % for the correct model against 0 % for the dumont truth at sigma 0.03. |

Note on stage 10: the amended rule now separates a correct model from the Dumont shaped truth, but it still calls the wrong collapse model adequate about half the time, and a mildly wrong janosi_mean model 65 % of the time at sigma 0.10. The rule was not tuned after this run; the decision is put to Huda (`docs/QUESTIONS_FOR_HUDA.md`, 2026-10-18 heading).

Note on stage 9: the widened range moves the anchors in the predicted direction and overshoots at the nominal value, while the 30 m map becomes far less certain than predicted. The anchor hits were informed by hand arithmetic on the model equation; the map misses were not foreseen. The main lesson is that the map's UNKNOWN share is controlled by how wide the assumed ranges are, which only a field measurement can narrow.


## Stage 11: share of draws that cannot move on level ground (written 2026-10-18, BEFORE the diagnostic script was written)

A diagnostic, not a test of the model. The second review (2026-10-18) found that some draws of the widened range sets leave the vehicle unable to move on level sand (slip on level ground above i_max), which the original f_r basis was meant to exclude. Those figures were computed by the reviewer, so the predictions below are a reproduction check, not foresight. Script to be written after this commit: `scripts/diagnose_level_ground.py`; output `results/range_set_diagnostics/immobile_on_level.csv`. Draws: `threeclass.lhs_draws(256, seed)` with the phase 2 seeds of areas A, B and C, under each range set.

| ID | Prediction made before the run | Outcome |
|---|---|---|
| G11-1 | original: 0 % of draws immobile on level ground in every area. |  HIT. 0.0 % in all three areas (`results/range_set_diagnostics/immobile_on_level.csv`). |
| G11-2 | widened_i0: between 1 % and 3 % per area (reviewer: 1.2, 2.0, 2.3 %). |  HIT. 1.2 %, 2.0 %, 2.3 %, as the reviewer found. |
| G11-3 | widened_i0_fr: between 8 % and 13 % per area (reviewer: 12.1, 9.0, 11.3 %), more than the 5 % of draws a cell may fail and still be TRAVERSABLE, which explains most of the 90 % UNKNOWN shares. |  HIT. 12.1 %, 9.0 %, 11.3 %, as the reviewer found. Correction to the heading: the script was written in the same step as this table and committed after it; it was not run before the table was committed. |

Notes appended 2026-10-18 after the second review (no prediction text edited):
- Stage 9 note placement: the "Note on stage 9" paragraph above sits under the stage 10 heading by mistake; it refers to stage 9.
- Stage 9 outcome corrections: W9-5 says the i0 range is "six times wider"; it is 3.3 times wider (0.35 to 1.15). W9-6 gives the 5th percentile as 2.4 deg; the file value is 2.35 (the report shows 2.3).
- Stage 9 context: in the widened_i0_fr set 9 to 12 % of draws cannot move on level ground (stage 11), more than the 5 % a TRAVERSABLE cell may tolerate, so the 90 % UNKNOWN shares largely reflect parameter combinations the original f_r basis excluded, not terrain.
- Stage 10 corrections: R10-2's 38.7 % is the share of all 300 replicates flagged uninformative, not of the not reached replicates. R10-5's sum is 75.7 % (1.3 % plus 74.3 %), not 75.6 %.
- Stage 10 informativeness: because `adequate` keeps its old meaning, the adequate rates in R10-1 and R10-4 and the R10-3 result were already determined by the stage 6 file, and the not reached share in R10-1 by the stage 6 diagnostic (96.7 % on 60 replicates). Only the third clause of R10-1, R10-2 and R10-5 carried new information. When the predicted entrapment slope is undefined but entrapment is observed, the implementation counts the entrapment test as failed; stage 10 did not state this case.
