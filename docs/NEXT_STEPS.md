# Next steps

Status labels follow the report: PLANNED means not yet run. Nothing here is a result.

## 1. The first field experiment: the slope ladder

**Why this one.** The literature has no published slip-versus-slope dataset for a wheeled robot on dune sand with full soil characterisation (report section 7). The simulation study shows the traversability map is controlled by assumptions (friction angle, slip scale i0, resistance f_r, the form of the slip law) that only this experiment measures (report section 8.4).

**What.** One small four-wheel rover (5 to 25 kg, wheels at least 150 mm, fixed and fully described) on one dune stoss slope. Direct-uphill runs at about 0, 5, 10, 15, 20 and 25 degrees (plus or minus 2), randomised order within a day, fresh track every run. RTK ground truth, wheel encoders and currents, IMU, rut depth by gauge. At every station: sieve grain size, bulk density, moisture at two depths, crust, angle of repose, penetrometer, plate pressure-sinkage set.

**How many.** Start with the 12-run pilot (3 runs at each of 5, 10, 15 and 20 degrees) to measure run-to-run scatter sigma. Then set runs per bin from n = (1.96 sigma / E)^2, about 4 to 9 per bin if sigma is 0.10 to 0.15 and E = 0.10. Total about 60 runs with cross-slope, tethered descent and repeated-pass blocks.

**Analysis (pre-registered).** Calibrate with bounds on runs at or below 10 degrees (friction angle from the soil tests), write dated predictions for 15, 20 and 25 degrees before running them, then compare error, calibration slope and entrapment slope against a constant-slip and a slope-threshold baseline. A synthetic design check (SIMULATED-BY-ME, report section 9) found the fixed tolerance of 0.15 is only fair if the pilot shows sigma of about 0.03; otherwise set the tolerance from the pilot (about 3 sigma, my assumption).

**Do first, before any run.** Fetch nothing new; decide the site, permission and recovery plan, and read `docs/FIELD_VALIDATION_PLAN.md` sections 2 to 9. Run `python3 scripts/analyze_field_runs.py --synthetic` to see the output format, and use `docs/field_log_template.csv` for the log columns. The analysis code has only ever seen synthetic data.

## 2. Cheap things to do now (no vehicle needed)

1. **Add a licence** to this repository (none chosen yet).
2. **Fetch the references that could not be retrieved** (exact URLs in `research/raw/*_notes.md`, sections NOT_RETRIEVED): the Wong dry-sand parameter table, Wong and Reece 1967, Ishigami et al. 2007 and 2009, the Yu et al. 3D RFT wheel paper (ISTVS 2024), Heverly et al. 2013 (Scarecrow dune tests), Takehana et al. 2025 (high-speed grouser DEM), the full Mars 2020 slip dataset when released. Add rows through `scripts/consolidate_evidence.py` after reading each.
3. **Read the controlling Copernicus GLO-30 licence** at spacedata.copernicus.eu (it timed out here) and update `docs/DATA_AND_LICENSES.md`.
4. **Check the SIM-013 equation** (Kern et al. 2026, arXiv 2601.04547, Eq. 3) for the unit of the slope term.
5. **Ask for local help.** Regional papers in Arabic, SAE Middle East papers, and groups at Khalifa University, MBRSC, TII, Al Ain University that may hold dune-trial data; the search tool here was US-only.

## 3. Extending the simulation (SIMULATED-BY-ME, still model-dependent)

1. Replace the three assumption parameters with ranges measured in the slope ladder, and re-run the sensitivity analysis to see how much the map tightens.
2. Add a dune-height and curvature rule that flags probable slip faces at 30 m, then test it against an RTK or drone profile of a real dune (this is the data the report says is missing).
3. Compare the 30 m map with a drone-photogrammetry DEM of one dune once available.
4. Optionally run Project Chrono SCM (BSD-3) for one wheel on a calibrated sand and compare with the lab or field slope ladder. DEM is not recommended for planning (report section 4).
5. Treat route acceptability as robust only if it holds across the assumption range, not at nominal parameters.

## 4. Possible follow-on studies

- Wheel diameter and width sweep on the same sand and rover (published support is a slide deck and one thesis).
- Same-vehicle wheel, leg and track comparison on one dune slope (none found).
- Terrain-type hold-out test for a learned slip predictor: train on non-sand terrain, test on sand.
- Cross-reference with `hudasol/dhill` to schedule runs outside the hottest hours, without merging the two studies.

## 5. Proposal framing (for TII, ATRC, EDGE, Al Ain University and similar)

What is supportable from this repository: a verified evidence base (144 rows), a documented gap (no Arabian dune slip data), an open-data pipeline with its limits stated (30 m resolution does not resolve slip faces), a sensitivity analysis that identifies what to measure, and a field plan with a pre-registered analysis. What is not supportable: any claim about how well a model predicts a rover on Arabian dunes, or that any route is traversable.
