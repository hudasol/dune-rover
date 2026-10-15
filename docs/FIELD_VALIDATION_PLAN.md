# Field validation plan for a low-cost rover on sand

**Status: PLANNED. Nothing in this document has been run. No result here is a measurement.**
Research plan only; it is not engineering approval for any real vehicle, site or operation.

## 1. What the experiment must answer

1. How does measured longitudinal slip change with slope for one specific small rover on one specific sand, and how large is the run-to-run scatter?
2. Can a model calibrated on gentle slopes predict slip and entrapment on steeper slopes **before** those runs are made (out-of-sample)?
3. How much do soil properties (grain size, bulk density, moisture, surface crust) and wheel state (first pass versus repeated pass) change the answer?

The review (`REPORT.md`, gap analysis) found no published slip-versus-slope dataset for a wheeled robot on Arabian dune sand, and almost no full-vehicle field data on Earth dune sand at all. Even a small honest dataset fills part of that gap.

## 2. Vehicle and instrumentation (low cost)

| Item | Minimum | Why |
|---|---|---|
| Rover | 4 wheels, 5 to 25 kg, skid-steer or Ackermann, wheels at least 150 mm in diameter, known mass and wheel load | Published lab data show that wheel diameter and width change slip by large factors (for example slip 0.741 versus 0.056 between 116 mm and 327 mm wheels at an equivalent 12 degrees, evidence LEG-017 and LEG-018), so the wheel must be fully described and kept fixed |
| Wheel encoders | One per wheel, at least 50 Hz | Wheel rim speed |
| Ground-truth position | RTK GNSS with centimetre-level accuracy (a rover and a base), or a total station | True displacement. Do not use the rover's own odometry as truth |
| IMU | 6-axis at 50 Hz or better | Pitch and roll, which give local slope under the rover |
| Motor current per wheel | Logged at 50 Hz | Proxy for wheel torque and for traction demand |
| Tow-line load cell (optional) | 100 kg class tension cell with an amplifier | Drawbar pull by a controlled pull test |
| Sinkage | Straight edge and depth gauge at marked stations in the rut, plus a photo with a scale | Cheap and direct. A downward time-of-flight sensor is an optional extra |
| Safety | Tether and recovery line, second person at all times, radio or phone contact | A rover on 25 degrees of loose sand can bury itself |

Wheel rolling radius: measure it on a hard flat surface and again on level loose sand at low speed. Slip must use the same effective radius in every run, stated in the log. Differences in how this radius is defined are one reason published slip values are hard to compare.

## 3. Site and soil characterisation (every test station)

Take these at each slope station, because published lab and field results differ by large factors between soils (Evidence table, `terrain_description` and `comparability_warning`).

| Measurement | Method | Replicates |
|---|---|---|
| Grain size (d10, d50, d90, uniformity) | Sieve a dried sample | 1 per station, 3 per site |
| Bulk density | Known-volume cup, weigh | 3 |
| Moisture | Oven dry at 105 C or a calibrated microwave method, at 0 to 2 cm and 5 to 10 cm | 2 depths |
| Surface crust | Thickness by probing, photo | per station |
| Angle of repose | Funnel pour and protractor or photo | 3 per site |
| Penetration resistance | Hand cone penetrometer, 0 to 15 cm | 5 |
| Pressure-sinkage constants | Two plate sizes pressed with at least three loads, fit Bekker's equation | 1 set per site |
| Local terrain slope | RTK line along the run or drone photogrammetry, plus an inclinometer reading | per run |
| Weather | Air temperature, wind speed and direction, time of day | per run |

Heat and dust effects on the electronics are out of scope here and are handled in the sibling repository `hudasol/dhill`. Schedule runs outside the hottest hours and note the temperature, but do not read this plan as a thermal study.

## 4. Run design

**Revised 2026-10-15 (PLANNED).** Slope bins by measured local slope: 0 (flat reference), 5, 10, 12.5, 15, 17.5 and 20 degrees, and 25 degrees only if fewer than half of the 20 degree runs end in entrapment. Tolerance plus or minus 1 degree for the 10 to 20 degree bins (so that bins 2.5 degrees apart do not overlap) and plus or minus 2 degrees for 0, 5 and 25. Log the target bin of every run in a `bin_deg` column; the analysis groups runs by it.

*Why the bins changed.* Two published sand slope results, read after the first ladder was fixed, place the change from moderate to high slip between about 10 and 17 degrees: at Dumont Dunes slip rose from below 50 % at 12.5 degrees to about 75 % at 16 and about 90 % at 20 for a 340 kg rover (FLD-HV13-1, FLD-HV13-2), and on Marsyard sand two rovers embedded at about 17 degrees (FLD-HV13-3). The model under predicts slip on both published anchors (report section 8.8), and the synthetic study found the protocol uninformative at 25 degrees (`docs/PREDICTIONS.md`, S3-5). Denser bins where the curve bends are therefore more useful than a 25 degree bin that may only show entrapment. The original bins (0, 5, 10, 15, 20, 25 within plus or minus 2) and their dated predictions (`docs/predictions/slope_ladder_predictions_2026-10-12.csv`) are kept unchanged for the record; the revised expected ranges are in `docs/predictions/slope_ladder_predictions_2026-10-15.csv` and the revision is pre registered as stage 6 in `docs/PREDICTIONS.md`. The tighter tolerance may be hard to find on a natural dune; if it cannot be met, fall back to the original bins and say so in the log.

Use natural stoss slopes and, with care, short lee-face sections. Approach each bin from the same lower position with the same entry speed (one speed, constant wheel command). Randomise the order of the bins within a day so that sun, wind and crust do not line up with slope.

| Block | Condition | Runs per cell | Cells | Runs |
|---|---|---|---|---|
| Pilot | Direct uphill, 3 runs at each of 5, 10, 15, 20 degrees | 3 | 4 | 12 |
| Main | Direct uphill, the seven bins (25 degrees only if allowed, see above) | 4 (adjust, see section 5) | 7 (8) | 28 (32) |
| Cross-slope | Traverse at 10, 15, 20 degrees | 3 | 3 | 9 |
| Descent | Direct downhill at 15 and 25 degrees (tethered) | 3 | 2 | 6 |
| Repeated pass | Same track three times at 10 degrees | 3 | 1 | 3 |
| **Total** | | | | **about 60** |

Fresh track every run in the main block (offset each run laterally by at least two wheel widths), so earlier passes do not compact the sand.

**Run protocol.** Start on level ground, drive a straight commanded line at constant wheel command, log for the whole run. A run ends after a set distance (for example 6 m on the slope), at entrapment (no forward progress for 5 s with wheels turning, or slip above 0.8 for 3 s), or at an operator safety stop. Record the reason.

## 5. How many runs

If the run-to-run standard deviation of slip in a bin is `sigma` and the target half-width of the 95 % interval for the mean is `E`, then about `n = (1.96 * sigma / E)^2` runs are needed (use the t quantile for small `n`, which needs a few more).

| sigma | E = 0.05 | E = 0.10 |
|---|---|---|
| 0.05 | 4 | 3 (minimum) |
| 0.10 | 16 | 4 |
| 0.15 | 35 | 9 |

`sigma` is not known for any vehicle on this sand. The pilot block exists to estimate it. After the pilot, set the runs per bin from the table, capped by time. A reasonable target is `E = 0.10` first, which needs about 4 to 9 runs per bin if `sigma` is between 0.10 and 0.15.

## 6. Quantities to compute from the log

All computed from RTK position and wheel encoders over a steady-state window that excludes the start-up and the stop.

- **Longitudinal slip** `i = 1 - v_true / (omega * r_eff)`, with `v_true` the ground speed along the heading from RTK.
- **Distance-based slip** `1 - (true distance) / (commanded distance by wheel odometry)`, reported alongside, since published studies use both.
- **Side-slip** on cross-slopes: angle between heading and the ground track, from RTK.
- **Sinkage:** rut depth from the gauge at three stations per run, as a share of wheel diameter.
- **Entrapment flag** and the slope and distance at which it happened.
- **Energy per metre** from motor current and voltage.
- **Drawbar pull** (optional tow test) at 0, 0.2 and 0.4 slip.

A starter analysis script and a log template are in `scripts/analyze_field_runs.py` and `docs/field_log_template.csv`. The script is tested on **synthetic** data only.

## 7. Pre-registered analysis (fix this before the main block is run)

1. **Calibrate** the minimal slip model (`src/dunerover/slipmodel.py`) using only the flat and 5 and 10 degree runs: fit the motion-resistance coefficient and the slip scale. Take the friction angle from the soil tests (and the angle of repose), not from the slip data. Fit with bounds (the assumption ranges, or ranges from your own tow and plate tests): the synthetic check found that an unbounded fit lets the two parameters trade off at gentle slopes and fails on the steep slopes in the worst 10 % of replicates (90th-percentile held-out error 0.23 to 0.33 unbounded against 0.11 to 0.14 bounded, at sigma 0.03).
2. **Predict** the slip distribution and the entrapment slope at 12.5, 15, 17.5 and 20 degrees (and 25 if it is run). Write the predictions down, with a date, before running those bins (`scripts/make_ladder_predictions.py --design 2026-10-15 --calibrate runs.csv`).
3. **Compare:** mean absolute error and root-mean-square error of predicted versus observed slip, the calibration slope of observed on predicted, and whether the observed entrapment slope falls inside the predicted range.
4. **Baselines:** compare against (a) a constant-slip assumption fitted to the flat runs, and (b) a binary slope threshold at the angle where the model first predicts slip above 0.5.
5. **Planning adequacy rule (my assumption, revise if you disagree):** the model is called adequate for a coarse planner if predicted slip is within 0.15 of observed for at least 80 % of held-out runs and the entrapment slope is within 3 degrees. These cut-offs are not published standards. **Design check (SIMULATED-BY-ME, synthetic data generated from the model itself, `scripts/calibration_identifiability.py`, `results/field_plan_identifiability.csv`):** even when the model is exactly right, calibrating on runs at or below 10 degrees and testing at 15 to 28 degrees meets this rule in only 43 to 65 % of synthetic replicates when run-to-run noise sigma is 0.06 (5 or 10 runs per bin), 73 to 78 % at sigma 0.03, and 10 to 18 % at sigma 0.10. Calibrating up to 15 degrees did not help. So the fixed 0.15 tolerance is only fair if the pilot shows sigma of about 0.03 or less. **Decision rule to fix before the main block:** set the tolerance from the pilot as about 3 times the pilot sigma (assumption), report the achieved fraction either way, and keep the bounded fit described next.
6. Report every run, including entrapments and discarded runs with the reason. No outlier removal without a written rule made beforehand.

Bootstrap confidence intervals (seeded) for per-bin means and for the error measures. Report the soil and wheel descriptions with the results. Do not generalise beyond the tested vehicle, wheels, soil and speed.

## 8. Data the rover should log for future prediction

From the gap analysis. Log all of these in every run, even if only a few are used first:

1. Per-wheel angular speed and motor current (traction demand).
2. RTK position and velocity, and IMU orientation, time-synchronised.
3. Effective rolling radius (calibration runs).
4. Local slope and aspect from the DEM **and** from the RTK profile (to measure how far a 30 m DEM is from the truth).
5. Soil state: grain size, bulk density, moisture, crust, penetration profile.
6. Wheel state: wear, grouser condition, tyre pressure if applicable.
7. Ambient: temperature, wind, time of day.
8. Pass number on each track.
9. Outcome flags: entrapment, recovery, operator intervention.

## 9. Risks and limits

- One rover, one site, one soil: results will not transfer by themselves. That is the finding, not a flaw.
- Slip on loose sand varies strongly between neighbouring patches with no visible difference (published Mars example, evidence FLD-011 and FLD-012). Expect scatter, and plan the run counts for it.
- Lee faces near the angle of repose can avalanche; do not drive people or the tether line below a rover on them.
- Access and permission to the site, vehicle recovery and local rules are the operator's responsibility and are not covered here.
- This plan is not a safety case.

## 10. Deliverables when the plan is executed

A run table, the raw logs, the soil data, the pre-registered predictions (dated), the comparison of predictions with observations, and a one-page statement of what the data do and do not support. Label every number "field measurement, one vehicle, one site".
