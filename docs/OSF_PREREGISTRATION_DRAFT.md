# OSF preregistration draft: slip of a small wheeled rover on a UAE dune slope

**Status: PLANNED. Draft prepared 2026-10-21 for Huda to paste into a preregistration on the Open Science Framework (osf.io) herself. Nothing has been submitted.** The sections follow the usual headings of the OSF preregistration form; check the current form when pasting, and paste each section into the matching field. Everything below repeats decisions already committed in this repository; nothing here changes them. Where a decision is still open (questions 5 and 7 in `docs/QUESTIONS_FOR_HUDA.md`), the draft says so and keeps both options, as the repository does.

Labels: everything in this draft is **PLANNED**; numbers quoted from the repository's results carry their own labels in the files cited.

Before submitting: fill the bracketed fields, attach `docs/predictions/slope_ladder_predictions_2026-10-12.csv` and `docs/predictions/slope_ladder_predictions_2026-10-15.csv` (the dated predictions), and cite the repository commit that holds them.

## 1. Study information

**Title.** Out of sample prediction of longitudinal slip of a small four wheel rover on the stoss slope of a UAE sand dune.

**Authors.** Huda Mueen. [Add any collaborator who joins the field day.]

**Description.** No published dataset of slip against slope exists for a wheeled robot on Arabian dune sand. This study measures longitudinal slip of one small rover at a ladder of slopes on one natural dune and tests whether a slip model calibrated on gentle slopes predicts slip and entrapment on steeper slopes before those runs are made.

**Research questions.**
1. How does measured longitudinal slip change with slope for this rover on this sand, and how large is the run to run scatter?
2. Does a slip model calibrated only on runs at 10 degrees or less predict slip and entrapment at steeper slopes within a tolerance fixed in advance?
3. How much do soil state (grain size, bulk density, moisture, crust) and repeated passes change slip?

**Hypotheses (directional where stated).**
- H1: slip is positively associated with slope between 0 and 20 degrees (tested as a positive rank correlation, not as strict monotonicity).
- H2: the calibrated model meets the adequacy rule of section 5 (this is the test; it may fail, and a failure is a result).
- H3: slip on the third pass over the same track at 10 degrees differs from first pass slip (no direction predicted).
- The dated numerical predictions per slope bin are in the attached prediction files; they were written before any field run.

## 2. Design plan

**Study type.** Field experiment with one vehicle on one natural dune site; observational with respect to soil.

**Blinding.** No blinding is possible for the operator. The analysis is fixed in code before the main block (`src/dunerover/fieldanalysis.py`, `scripts/ingest_field_day.py`), and the predictions for the steep bins are committed before those bins are driven.

**Design.** Slope bins by measured local slope. Two bin designs are registered because the choice is still open (question 5):
- Design of 2026-10-12: 0, 5, 10, 15, 20 and 25 degrees, tolerance plus or minus 2 degrees.
- Design of 2026-10-15: 0, 5, 10, 12.5, 15, 17.5 and 20 degrees (plus or minus 1 degree from 10 to 20 degrees, plus or minus 2 otherwise), and 25 degrees only if fewer than half of the 20 degree runs end in entrapment.
[State here which design is used on the day, before the main block, and delete the other.]

Blocks: pilot (3 runs at each of 5, 10, 15 and 20 degrees), main direct uphill block (4 runs per bin, adjusted after the pilot as in section 3), cross slope traverse at 10, 15 and 20 degrees (3 each), tethered descent at 15 degrees (and 25 where used, 3 each), repeated pass at 10 degrees (one track driven three times, 3 sets). About 60 runs in total.

**Randomisation.** The order of the bins within a day is randomised (seeded list printed before the day) so that sun, wind and crust do not line up with slope. Each main block run uses a fresh track offset by at least two wheel widths.

## 3. Sampling plan

**Existing data.** No field data exist at the time of registration. [Confirm on the day of submission: "Registration prior to creation of data".]

**Data collection procedures.** Rover: four wheels, 5 to 25 kg, wheels of at least 150 mm diameter, mass, wheel size and grousers recorded. Ground truth position by RTK GNSS (or a total station); wheel speed by encoders; pitch and roll by an IMU at 50 Hz or more. Effective rolling radius measured on hard ground and on level sand at low speed, one value used for every run. Each run starts on level ground, drives a straight line at constant wheel command, and ends at 6 m on the slope, at entrapment (no forward progress for 5 s with wheels turning, or slip above 0.8 for 3 s), or at a safety stop; the reason is recorded. Soil at every station: grain size, bulk density, moisture at two depths, crust, angle of repose, penetration resistance, by the methods of `docs/SAND_LAB_PROTOCOL.md`. Local slope from the RTK line or the drone surface (`docs/DRONE_SURVEY_PROTOCOL.md`) and an inclinometer. Data sheets: `field_kit/`.

**Sample size.** About 60 runs (section 2). Runs per bin in the main block follow n = (1.96 sigma / E)^2 with E = 0.10, where sigma is the run to run standard deviation of slip estimated from the pilot block, capped by the time available.

**Stopping rule.** The 25 degree bin is driven only under the condition above. Any bin is stopped for safety at the operator's judgement; stopped runs are reported with their reason. Data collection ends when the planned runs are done or the day's time limit is reached; the shortfall is reported.

## 4. Variables

**Manipulated.** Slope bin (by choice of station), heading (uphill, cross slope, downhill), pass number (repeated pass block).

**Measured.** Ground speed and distance (RTK), wheel angular speed (encoders), pitch and roll (IMU), motor current, sinkage at three stations per run, entrapment flag and position, soil properties per station, air temperature and wind.

**Indices.** Longitudinal slip i = 1 minus v_true / (omega r_eff), with entrapped runs set to 1; distance based slip reported beside it; side slip on cross slopes; sinkage as a share of wheel diameter; energy per metre.

## 5. Analysis plan

**Runs that enter the rule.** Only the direct uphill, first pass runs of the pilot and main blocks (heading within 15 degrees of uphill, pass number 1 or left empty, which the analysis reads as a first pass) enter the calibration and the held out test. Cross slope, descent and repeated pass runs are analysed separately and never enter the rule (`scripts/ingest_field_day.py`). This is a selection of runs, as the field plan defines the sets, not a change of the rule.

**Friction angle used by the model.** In this order: a friction angle written on the run sheet; otherwise the median of the station's direct shear friction angles, measured on sand prepared at the field bulk density and at the lowest normal stress the laboratory can apply; otherwise the median of the station's angle of repose tests, used as a proxy and flagged as such. If any run lacks all three, the analysis stops and reports which runs lack a friction angle, so that nothing is analysed with a missing value. [Confirm or change this order before submitting.]

**Model and calibration.** The minimal slip model of `src/dunerover/slipmodel.py`, calibrated on the 0, 5 and 10 degree runs only, with the motion resistance coefficient and the slip scale fitted within bounds (i0 up to 0.40, f_r up to 0.25) and the friction angle as above, not from the slip data. A fit that ends at a bound is reported as such. Note for reviewers: the calibration on published curves in the repository (stage 15) put the slip scale near 0.63, above the 0.40 bound, so a fit at the bound is likely; the bound is kept unchanged unless the author changes it before the field day.

**Predictions.** Before the steep bins are driven, the calibrated model's predictions for 12.5, 15, 17.5 and 20 degrees (and 25 if used) are written, dated and committed (`scripts/make_ladder_predictions.py`).

**Inference criteria (the committed rule, unchanged).** Tolerance = the larger of 3 times the pilot sigma and 0.05 (0.15 if there is no pilot). The slip test passes if at least 80 % of held out runs are within the tolerance of the prediction. The entrapment test has three outcomes: pass (observed entrapment slope within 3 degrees of the predicted), fail, or not reached. The verdict is adequate (both pass), not adequate (either fails), or slip within tolerance with entrapment not reached. If 3 times the pilot sigma exceeds 0.30 the experiment is reported as uninformative. Note for reviewers: a synthetic study in the repository found that this rule calls a wrong model (one that collapses above 20 degrees) adequate in a large share of replicates; alternative rules exist as options (`results/field_kit/rule_options_2026-10-20.csv`) and the author has not changed the rule (question 7). [If the author changes the rule before the field day, replace this paragraph with the new rule and say when it was changed.]

**Tests of H1 and H3.** H1 is supported if the Spearman rank correlation between slope and slip over the direct uphill first pass runs is positive with a seeded bootstrap 95 % interval that excludes zero. H3 is supported if the seeded bootstrap 95 % interval of the difference between third pass and first pass mean slip at 10 degrees excludes zero.

**Secondary analyses.** Mean absolute error, root mean square error and the calibration slope of observed on predicted slip; comparison with a constant slip baseline and a slope threshold baseline; per bin means with seeded bootstrap 95 % intervals; scoring of every dated prediction (inside or outside the model 5 to 95 % interval and the planning range).

**Data exclusion.** No run is excluded without a written reason recorded on the day (for example equipment failure or loss of RTK fix). Every run, including entrapments and discarded runs, is reported.

**Missing data.** A run without RTK fix over the steady window is reported with slip "not computed" and is not imputed.

**Exploratory analyses (labelled as such).** Effect of soil properties and pass number; comparison of the RTK slope with the 30 m and drone derived map slopes; any analysis not listed above.

## 6. Other

All code, predictions and data sheets are in the repository `hudasol/dune-rover` [cite the commit]. Results are labelled "field measurement, one vehicle, one site" and are not generalised beyond the tested vehicle, wheels, soil and speed. Permissions for the site and any drone flight are obtained from the competent authorities before the field day.
