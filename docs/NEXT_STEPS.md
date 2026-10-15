# Next steps

Status labels follow the report: PLANNED means not yet run. Nothing here is a result.

## 1. The first field experiment: the slope ladder

**Why this one.** The literature has no published slip-versus-slope dataset for a wheeled robot on dune sand with full soil characterisation (report section 7). The simulation study shows the traversability map is controlled by assumptions (friction angle, slip scale i0, resistance f_r, the form of the slip law) that only this experiment measures (report section 8.4).

**What.** One small four-wheel rover (5 to 25 kg, wheels at least 150 mm, fixed and fully described) on one dune stoss slope. Direct-uphill runs at about 0, 5, 10, 15, 20 and 25 degrees (plus or minus 2), randomised order within a day, fresh track every run. RTK ground truth, wheel encoders and currents, IMU, rut depth by gauge. At every station: sieve grain size, bulk density, moisture at two depths, crust, angle of repose, penetrometer, plate pressure-sinkage set.

**How many.** Start with the 12-run pilot (3 runs at each of 5, 10, 15 and 20 degrees) to measure run-to-run scatter sigma. Then set runs per bin from n = (1.96 sigma / E)^2, about 4 to 9 per bin if sigma is 0.10 to 0.15 and E = 0.10. Total about 60 runs with cross-slope, tethered descent and repeated-pass blocks.

**Analysis (pre-registered).** Calibrate with bounds on runs at or below 10 degrees (friction angle from the soil tests), write dated predictions for 15, 20 and 25 degrees before running them (`scripts/make_ladder_predictions.py --calibrate runs.csv`; pre-data predictions are already in `docs/predictions/`), then compare error, calibration slope and entrapment slope against a constant-slip and a slope-threshold baseline. The tolerance is set from the pilot (3 times pilot sigma, floor 0.05, my assumption). A synthetic test with known truth (SIMULATED-BY-ME, report section 9) shows the adequacy rule discriminates weakly, so report predicted against observed with intervals first and treat pass or fail as secondary.

**Do first, before any run.** Decide the site, permission and recovery plan; read `docs/FIELD_VALIDATION_PLAN.md` sections 2 to 9 and print `docs/FIELD_DAY_CHECKLIST.md`. Run `python3 scripts/analyze_field_runs.py --synthetic` to see the output format, and use `docs/field_log_template.csv` for the log columns. The analysis code has only ever seen synthetic data. Rover and kit options with retrieved costs are in `docs/ROVER_OPTIONS.md`.

## 2. What you need to do (cheap, no vehicle needed)

1. **Licence (decided).** All rights reserved; permission is requested by contacting the author (`LICENSE`, `LICENSE-DOCS.md`). Nothing further to do.
2. **Upload the references that could not be retrieved.** Each is paywalled or blocked from the workspace, and none is cited for any number. Please send the PDF, or the pages named in the State column, in a message. Do not commit the PDFs to the repository (the CI check rejects them).

| Title | DOI or URL | State |
|---|---|---|
| Wong, J. Y., *Theory of Ground Vehicles*, 4th ed. 2008 (ISBN 978 0 470 17038 0) or 5th ed. 2022 | https://www.wiley.com/en-us/Theory+of+Ground+Vehicles%2C+4th+Edition-p-9780470170380 | a screenshot of a table was supplied on 2026-10-12 (dry sand: n 1.1, kc 0.99, kphi 1528.43, c 1.0, phi 28 degrees, K 0.011) but it carries no citation, is not a page of the book, and I could not confirm it against the book (the K column in particular), so it is **not used and not cited**. A second file supplied later (a print to PDF of a local HTML page titled "Theory of Ground Vehicles, Chapter 2, Page 89", values for loose, standard and dense dry sand) is also **not used and not cited**: it is a printout of a locally saved web page, not a scan or photograph of the printed book, and its dry sand values (kc 0, kphi 850 to 1600, K 1.6 to 2.5 cm) disagree with the earlier screenshot (kc 0.99, kphi 1528.43, K 0.011), so neither can be taken as the book's table; a third file supplied 2026-10-13 (a typeset image titled "Table 1. Bekker and Janosi-Hanamoto parameters for dry sand", with Example A, B and C columns, n 0.90 to 1.10, kphi 1000 to 2000, phi 25 to 35 degrees) shows no book title, edition or page and is not a photograph of a printed page, so it is **not used and not cited** either; please upload the book page itself (photo of the printed table with the title and page visible), the chapter 2 table of Bekker and Janosi parameters (n, kc, kphi, c, phi, K) for dry sand. Alternative: Wong, *Terramechanics and Off-Road Vehicle Engineering*, 2nd ed. 2010 |
| Wong, J. Y. and Reece, A. R. (1967), Prediction of rigid wheel performance based on the analysis of soil-wheel stresses, part I, *Journal of Terramechanics* 4(1), 81 to 98 | https://doi.org/10.1016/0022-4898(67)90105-X | not available to the author (2026-10-13); cited for no number. Optional: a library interlibrary request |
| Ishigami, G., Miwa, A., Nagatani, K., Yoshida, K. (2007), *Journal of Field Robotics* 24(3), 233 to 250 | https://doi.org/10.1002/rob.20187 | full text supplied 2026-10-13 and read; 5 rows in `research/phase2/supplied_pdf_rows_2026-10-13.csv` |
| Ishigami, G., Nagatani, K., Yoshida, K. (2009), *Journal of Field Robotics* 26(3), 264 to 286 | https://doi.org/10.1002/rob.20277 | full text supplied 2026-10-13 and read; 5 rows in `research/phase2/supplied_pdf_rows_2026-10-13.csv` |
| Yu, Q., Pavlov, C., Kim, W., Johnson, A. M. (2024), Modeling wheeled locomotion in granular media using 3D RFT and sand deformation, *Journal of Terramechanics* 115, 100987 | https://doi.org/10.1016/j.jterra.2024.100987 | full text supplied 2026-10-13 and read; 5 rows in `research/phase2/supplied_pdf_rows_2026-10-13.csv` (not yet in the 144 row table). An earlier note in this repository pointed at an ISTVS URL that is a different paper; this is the correct reference |
| Heverly, M. et al. (2013), Traverse performance characterization for the Mars Science Laboratory rover, *Journal of Field Robotics* 30(6) | https://doi.org/10.1002/rob.21481 | full text supplied 2026-10-13 and read; 6 rows in `research/phase2/supplied_pdf_rows_2026-10-13.csv`, including a Dumont Dunes slip against slope fit (Sec 6.3) |
| Takehana, K. et al. (2025), Grouser wheel high speed traction performance: DEM simulation and experimental result, *Journal of Terramechanics* 120, 101084 | https://doi.org/10.1016/j.jterra.2025.101084 | full text supplied 2026-10-13 and read; 5 rows in `research/phase2/supplied_pdf_rows_2026-10-13.csv` (not yet in the 144 row table). No numeric DEM versus experiment error metric is given in the text, only qualitative disagreement |
3. **Release tagged:** v0.2.0 (done by the author on 2026-10-12; the About text and topics are already set).
4. **Local help (two routes).** Route A, now: proceed alone with free options (`docs/ROVER_OPTIONS.md`, smartphone inclinometer, pilot runs only up to 10 degrees on a gentle dune with a second person and a recovery vehicle). Route B, later: present `docs/AAU_FIELD_DAY_PROPOSAL.md` to Al Ain University once access exists; it is a proposal only and no partnership exists. Regional papers in Arabic and SAE Middle East papers may hold dune trial data; the search tool here was US only.
5. **Spot check (done 2026-10-12):** five rows chosen by the author were compared with the supplied source PDFs; 4 of 5 correct, 1 label corrected (`research/spot_check_2026-10-12.md`). A human check of more rows is still welcome, because the checker was a language model agent, not a person.

6. **Brief (reminder):** when the build is finished, build the brief; the author asked to be reminded.
7. **Comparison baseline:** Heverly et al. (2013, Sec 6.3) report slip against slope at Dumont Dunes (cubic fit valid for about 4 to 21 degrees, about 75 percent slip at 16 degrees, no soil parameters given). Compare the slope ladder with it, as a different vehicle and a different dune.

Done in phase 2 (no longer open): the GLO-30 licence was read in full; the SIM-013 unit is not stated in its source (resolution recorded in the evidence table); all 144 rows were re-checked; the sub-grid detector, three class map and second morphology were added; the licence was decided (all rights reserved).

## 3. Extending the simulation (SIMULATED-BY-ME, still model-dependent)

1. **Test the sub-grid detector against a real profile.** Compare the face probability and the three class map with an RTK or drone profile of one real dune (the slope ladder site). This is the only way the detector can be validated; today it is validated against synthetic truth only.
2. Replace the three assumption parameters with ranges measured in the slope ladder, and re-run the Monte Carlo to see how much the map tightens.
3. Compare the 30 m map with a drone photogrammetry DEM of one dune once available.
4. Optionally run Project Chrono SCM (BSD-3) for one wheel on a calibrated sand and compare with the lab or field slope ladder. DEM is not recommended for planning (report section 4).
5. Treat route acceptability as robust only if it holds across the assumption range and the face probability is below the threshold, not at nominal parameters.
6. A legged versus wheeled comparison on the same slope ladder was **not run**: it would need invented leg and foot parameters, and no source retrieved gives them for sand at a usable level. It stays an open question (report section 12).

## 4. Possible follow-on studies

- Wheel diameter and width sweep on the same sand and rover (published support is a slide deck and one thesis).
- Same-vehicle wheel, leg and track comparison on one dune slope (none found).
- Terrain-type hold-out test for a learned slip predictor: train on non-sand terrain, test on sand.
- Cross-reference with `hudasol/dhill` to schedule runs outside the hottest hours, without merging the two studies.

## 5. Proposal framing (for any interested university or research partner)

What is supportable from this repository: a verified evidence base (all 144 rows re-checked), a documented gap (no Arabian dune slip data), an open-data pipeline with its limits stated (30 m resolution does not resolve slip faces; a modelled UNKNOWN class makes that visible), a sensitivity analysis that identifies what to measure, and a field plan with pre-data predictions and a pre-registered analysis. An outline is in `docs/PROPOSAL_SEED.md`; no partnership or endorsement exists. What is not supportable: any claim about how well a model predicts a rover on Arabian dunes, or that any route is traversable.
