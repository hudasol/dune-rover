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
| D7-1 | The baseline reproduces the committed 30 m class shares of all three areas to within 0.1 percentage point. | |
| D7-2 | The median Dumont fitted i0 over the 256 draws of area A lies between 0.4 and 2.0, outside the assumed range of 0.05 to 0.40. | |
| D7-3 | Unclipped Dumont prior: BLOCKED in area A at 30 m rises above 1 % (baseline under 0.1 %). | |
| D7-4 | Unclipped Dumont prior: UNKNOWN in area A at 30 m lies between 15 % and 60 % (baseline 8.6 %). | |
| D7-5 | Clipped Dumont prior: UNKNOWN in area A lies between the baseline and the unclipped value. | |
| D7-6 | Under the unclipped prior, area C has the lowest UNKNOWN share of the three areas, as in the baseline. | |
