# How far can open data and textbook models predict wheeled rover slip on dune sand? An evidence synthesis, pre registered model validation and lidar test, with an Arabian focus

**Huda Mueen** (independent researcher; repository `hudasol/dune-rover`)

Manuscript generated from the repository files by `scripts/build_manuscript.py` on 2026-10-20. Every number in the text is filled in from a result file or the evidence table; `scripts/check_manuscript_numbers.py` lists every number typed by hand and its justification. Labels: **PUBLISHED** (read in a retrieved source, with an evidence row id in brackets), **SIMULATED BY ME** (output of the repository's code, simulation only and model assumption dependent), **PLANNED** (not run). No field data of the author's own exist yet. No agreement, partnership or endorsement with any institution exists.

## Abstract

Small wheeled robots are being proposed for work on Gulf dune fields, yet no published slip against slope dataset exists for a wheeled robot on Arabian dune sand. This study asks how far open elevation data and textbook terramechanics can go without such data, and states every failure. A verified evidence table of 494 published results from 174 sources was built; 323 rows were added in this round and each was re checked against its full text by an independent agent (9.3 % material errors before correction, Wilson 95 % interval 6.6 to 12.9 %). Four slip model families (SIMULATED BY ME) were calibrated and tested on 17 digitised published slip against slope curves from 4 studies by leave one study out. No family met the pre registered bar (median held out error at most 0.15): median held out root mean square slip errors were 0.24 for the repository's exponential model, 0.23 for a Mohr Coulomb ratio, 0.24 for a two parameter empirical curve, and 0.20 for a Bekker Wong rigid wheel model on the curves with known wheel size and load, whose predictive intervals however covered only 0.71 of held out points. An independent single wheel simulation in Project Chrono (SIMULATED BY ME) with published soil sets predicted far less slip than the Dumont Dunes field curve (0.21 against about 0.49 at 12.5 degrees), and disagreed with a direct implementation of the same Bekker and Janosi laws. Scored against one metre lidar of three North American dune fields, a slip face detector trained on synthetic dunes (SIMULATED BY ME) reached an AUC of about 0.98 at 5 m but only 0.66 to 0.86 at 30 m, where 25.6 % to 28.6 % of the cells a three class map called TRAVERSABLE contained steep faces and 36 % to 73 % of the cells containing a face were called TRAVERSABLE. Route planning on 30 m maps was no safer than naive planning (SIMULATED BY ME). The study concludes that a 10 m or finer surface and a measured slip curve for the actual vehicle are prerequisites for planning on dunes, and sets out a pre registered field experiment and a robotics project to obtain them.

## 1. Introduction

A wheeled ground vehicle climbing a dune slope loses traction as the slope rises. How much it slips, and at which slope it stops, depends on the vehicle, its wheels and the sand, and it decides whether a route is feasible. Dune fields cover large parts of the United Arab Emirates and the wider Arabian Peninsula (Liwa, the Rub' al Khali, the Wahiba Sands), and robots for survey, logistics and inspection there would need to plan routes over them. Two things are needed: a slip law that holds for the vehicle on that sand, and a terrain model fine enough to see the slopes that matter.

Neither exists in open form. The only published slip against slope curve on a natural Earth dune found in this study is for a 340 kg Mars rover test vehicle at Dumont Dunes, California, without soil parameters (FLD-HV13-1, FLD-HV13-2). The only Arabian wheeled robot field evidence is qualitative (FLD-042). Open elevation data for the region (Copernicus GLO 30, about 30 m posts) resolve dunes but not their slip faces.

This paper reports what can and cannot be said with open data and published models, with every prediction registered before its run and every miss reported. Its contributions are: (i) a verified, openly structured evidence table with an explicit error rate; (ii) a leave one study out validation of four slip model families on digitised published curves; (iii) an independent simulator cross check; (iv) the first test, to the author's knowledge, of a sub grid slip face detector and three class traversability map against real lidar dunes degraded to coarse resolution; (v) a test of route planning policies against lidar truth; and (vi) a pre registered field experiment and analysis rule with a synthetic power study. It does not contribute field slip data, a validated slip model or an Arabian terrain validation; those are the gaps it measures.

## 2. Related work (from the evidence table)

**Terramechanics.** Bekker pressure sinkage and Janosi shear laws, assembled into rigid wheel models in the Wong and Reece tradition, describe drawbar pull and sinkage on level sand once fitted per soil; reported median drawbar errors are around a quarter of the measured value on two lunar simulant datasets but reach 135 % on a firm soil with a small light wheel (SIM-025 to SIM-027), and the Janosi shear modulus differs by about 75 times across the materials of one paper (TM-001 to TM-006, the largest value for poppy seeds) and is 0.07 m in the Toyoura sand model inputs of another (TM-IS09-2). Granular resistive force theory gives drawbar errors of a few newtons on medium sand (TM-001 to TM-004).

**Empirical vehicle mobility models.** The cone index based family (Waterways Experiment Station sand numerics and the NATO Reference Mobility Model) was built from military vehicle trials; its reported accuracy against field data is modest, for example a 30.1 % overall error in predicted traverse speed across several vehicles on mixed terrain (MOB-020), a 17.9 % drawbar pull error in coarse grained soils (MOB-021), and deviations of 73 and 109 % in the predicted maximum sand slope of two tracked vehicles (MOB-023).

**Field and planetary evidence.** Field slip on sand is large and patchy: Spirit measured 15 to 20 % slip at 19 degrees and 95 % at 16 degrees on look alike terrain 30 m apart (FLD-011, FLD-012); Perseverance exceeded 94 % at about 20 degrees (FLD-025); Curiosity's mission statistics and its Hidden Valley experience, Zhurong, Yutu 2 and Apollo rover data are in the PLN rows. Slip prediction from terrain properties on nine Curiosity sand sites had leave one site out errors of 20.4 to 30.3 percentage points, the larger for a slope only model (PLN-055, MAP-023).

**Terrain mapping.** Coarser elevation models lower the measured slope of steep terrain; satellite DEM errors grow on dune slopes (DUN rows). Risk aware planners improve success rates in simulation, but evidence on real dunes is thin (MAP rows).

**Other locomotion.** Published comparisons on sand favour tracks and wheel and crawler hybrids over plain wheels in some conditions (MOB-043, TM3-071), and small legged robots climb sand slopes slowly (LEG-007 to LEG-009); the rows differ in size, sand and metric and cannot be ranked (table below).

Wheeled, tracked and legged locomotion on sand (PUBLISHED rows only; vehicles, soils and metrics differ, so the rows are not comparable with each other).

| Row | Vehicle | Slope, deg | Metric | Value | Validation |
|---|---|---|---|---|---|
| MOB-043 | Military wheeled vehicles (and tracked for comparison) | 0 (level) | maximum drawbar pull on level sand as fraction of gross vehicle test weight (wh… | 20 and 40; 50 and 60 percent (ranges between) | field |
| TM3-067 | Four track platform rover with robotic arm, 120 kg, L153 x W154 x H11… | 0 (level) and 18 | steady state track slip on level ground and on an 18 deg sand slope | approximately 0.05 (level); approximately 0.3 (18 deg slope… | lab |
| TM3-071 | Model wheeled vehicle with independently driven front and back wheels… | 0 (level) | slip ratio of the wheeled vehicle without and with the intermediate crawler on… | 1 (wheels only, did not move); 0.065 (with crawler) ratio | lab |
| FLD-HV13-1 | Scarecrow (Mars weight MSL test rover, 340 kg, 50 cm diameter rigid g… | 4 to 21 (fit validity r… | Cubic fit coefficients c0; c1; c2; c3 (slip vs slope) | 26.197; -8.849; 1.281; -0.034 dimensionless polynomial coef… | field |
| FLD-025 | Perseverance (Mars 2020) | about 20 | slip | in excess of 94 % | field |
| LEG-007 | Hexapod with C-shaped legs (350 g, 22 cm x 10 cm; leg radius 4 cm, wi… | 0 | step-averaged speed parallel to surface | 15.7 cm/s | lab |
| LEG-008 | Same 350 g hexapod | 10 | step-averaged speed parallel to surface | 11.0 cm/s | lab |
| LEG-009 | Same 350 g hexapod | 24 | step-averaged speed parallel to surface | 5.6 cm/s | lab |
| LEG-013 | SpaceBok quadruped (22 kg), planar and point feet, static and trot | 25 | maximum slope traversed (testbed limit) | 25 deg | lab |

**Arabian sand and dunes.** Grain size, sorting and mineralogy of UAE, Qatari, Saudi and Omani dune sands are published (SND rows); a direct shear friction angle of 45 to 48 degrees was found for Dhahran dune sand in one thesis (SND-023), and no friction angle or slip face angle measured on UAE dunes was found. Drift potentials from Gulf stations exist (DUN rows).

## 3. Data and methods

### 3.1 Evidence table and verification

Rows were extracted by topic agents under a written brief (full text only, a live DOI or URL check, licence recorded, a comparability warning per row) and then re checked by fresh agents that saw only the claim fields and re opened the full text (`docs/SEARCH_PROTOCOL.md`). Corrections enter through a corrections file; unverifiable rows are dropped; the error rate is reported with Wilson intervals. A blinded random sample of 20 rows is prepared for a human rater with an agreement script (Cohen's kappa).

### 3.2 Published curves

Slip against slope curves were digitised reproducibly from figures (calibration files and marker coordinates committed, uncertainty from axis scale and marker spread) or copied from tables, 26 curves with 235 points from 7 sources in total (`docs/DATA_CATALOG.md`). Each carries the vehicle, wheel size, load, soil, preparation, test type and a judgement of comparability to loose dry dune sand. Unlike conditions are never pooled into one curve.

### 3.3 Model families and validation protocol

Four families share one interface: (a) the repository's quasi static model, slip = minus i0 ln(1 minus demand over capacity), with the friction circle demand; (b) a rigid wheel Bekker, Wong and Reece stress model in the form of Ishigami et al. 2007, which needs wheel radius, width and load; (c) a Mohr Coulomb demand ratio; (d) a two parameter logistic curve with no physics. Calibration uses a Gaussian likelihood with per point variance equal to the digitisation variance plus a fitted model variance, uniform priors, affine invariant MCMC for (a), (c) and (d) and maximum a posteriori with a bootstrap for (b). Validation is leave one study out: a family is calibrated on all other studies and predicts the held out study. The bar, fixed before the run, is a median held out root mean square error of at most 0.15 and at least 80 % of held out points inside the 90 % predictive interval.

### 3.4 Independent simulation

A single rigid smooth wheel with published dimensions (a Scarecrow like wheel, radius 0.25 m, width 0.40 m, 556 N; and the Ishigami test bed wheel, radius 0.055 m, width 0.064 m, 29.8 N) was driven at constant angular speed on Project Chrono's Soil Contact Model with gravity tilted to emulate the slope, for two published soil parameter sets (a lunar simulant set of Ishigami et al. 2007 and a discrete element calibrated set of Zhang et al. 2024), slopes 0 to 30 degrees. Grid and speed checks were run.

### 3.5 Traversability map

On Copernicus GLO 30, each cell's eight headings are passable or not under the slip model for each of 256 Latin hypercube parameter draws; the share of draws in which at least four headings pass gives TRAVERSABLE, BLOCKED or UNKNOWN, and a logistic sub grid detector trained on synthetic dunes gives the probability that an unresolved slip face of 28 degrees or more lies inside the cell. Global sensitivity of the passable share to the four parameters is estimated with Sobol indices.

### 3.6 Lidar terrain validation, wind and planning

USGS 3DEP one metre bare earth DEMs of Dumont Dunes (the field site of the Dumont curve), White Sands and Kelso Dunes were block averaged to 5, 10 and 30 m. Truth for a coarse cell is at least 10 square metres of one metre slope at 28 degrees or more. Slip face dip directions were compared with the resultant sand drift direction from ERA5 hourly wind (2015 to 2024). Three planning policies (naive, conservative over TRAVERSABLE cells only, risk weighted by face probability) were run between 40 origin and destination pairs per site and scored by resampling each route on the lidar surface.

### 3.7 Field experiment and analysis rule (PLANNED)

A slope ladder with one small four wheel rover on one dune stoss slope, calibration on runs up to 10 degrees, predictions committed before steeper runs, and a pass or fail rule whose power was studied on synthetic data.

## 4. Results

### 4.1 Evidence base

The table now holds 494 rows from 174 sources (162 lab, 133 field, 112 none, 33 sim-vs-lab, 31 simulation-only, 23 sim-vs-field). Of the 323 rows added and merged in this round, 30 had a material error before correction (9.3 %, Wilson 95 % interval 6.6 to 12.9 %) and 25.4 % had any discrepancy; most material errors were a wrong validation type, not a wrong value. Across the whole current table, by each row's latest verdict, 38 of 494 rows carried a material error before correction (7.7 %); every material error is corrected.

### 4.2 No slip model family transfers between studies (SIMULATED BY ME against PUBLISHED curves)

Table 1. Model families on the published slip against slope curves (SIMULATED BY ME against PUBLISHED curves). Bar fixed before the run: median held out error at most 0.15 and coverage at least 0.80.

| Family | Held out curves | Median error, nominal | Median error, own fit | Median error, held out | 90 % interval coverage | Bar |
|---|---|---|---|---|---|---|
| Exponential (existing model) | 17 | 0.31 | 0.06 | 0.24 | 0.89 | fails |
| Bekker Wong rigid wheel | 8 | 0.26 | 0.08 | 0.20 | 0.71 | fails |
| Mohr Coulomb ratio | 17 | 0.24 | 0.10 | 0.23 | 0.85 | fails |
| Logistic, empirical | 17 | 0.19 | 0.03 | 0.24 | 0.86 | fails |

Fitted to one curve at a time, every family can match its shape (median error 0.03 for the logistic, 0.06 for the exponential model). Asked to predict a study it was not calibrated on, none can: held out errors are around 0.2 to 0.3 slip, the predictive intervals are wide enough to cover most points only because the fitted model error is about 0.26, and the empirical logistic curve does as well as the two lumped physics models. The Bekker Wong family, the only one that uses wheel size and load, came closest (0.20 on its 8 curves, against 0.23 for the logistic on the same curves): calibrated on the Inotsume curves (the El Dorado wheels and the Scarab rover) it predicted the Heverly curves with held out errors of 0.08 to 0.15, but calibrated on Heverly it predicted the Inotsume curves with errors of 0.20 to 0.56, and its intervals were too narrow. With its nominal parameters the repository's model misses the Dumont curve by 0.42 (root mean square). The Bekker Wong family with the published simulant set of Ishigami et al. 2007 does not even reproduce that paper's own drawbar pull curve (negative pull up to 0.6 slip against 1 to 25 N measured; `results/model_validation/bw_vs_ishigami2007.csv`), because the published parameters belong to an implementation with details not reproduced here.

The posterior of the exponential family over the 12 curves judged comparable to dune sand gives phi 36.93 (30.57 to 43.74) degrees, f_r 0.13 (0.03 to 0.32) and i0 0.63 (0.33 to 1.21) (median, 5 to 95 %). Used as the map's parameter ranges, it raises UNKNOWN at 30 m to 62.8 % in Liwa (A), 44.3 % in the Rub' al Khali megadunes (B) and 46.0 % in linear dunes (C), against 8.6 %, 10.9 % and 2.5 % under the original assumed ranges. About 5 % of the posterior draws cannot move on level ground; rejecting them (a post hoc choice) gives 25.1 %, 30.9 % and 4.2 %, so the Arabian UNKNOWN share itself depends strongly on that choice (by a factor of 1.4 in B and of more than ten in C).

![Per curve best fits of three families to the published curves (points with digitisation uncertainty). A good fit shows shape capacity, not predictive skill. SIMULATED BY ME against PUBLISHED curves.](../results/model_validation/part_exp_existing_mohr_coulomb_ratio_logistic_empirical/figures/fig_family_fits.png)

### 4.3 An independent simulator does not rescue the models (SIMULATED BY ME)

With published soil sets and smooth wheels, Chrono's Soil Contact Model gives slip 0.21 at 12.5 degrees and 0.48 at 30 degrees for the Scarecrow sized wheel on the simulant set, against about 0.49 and embedding above 21 degrees on the Dumont field curve (root mean square difference 0.35). Grid halving and a fourfold lower speed changed slip by at most 0.02. The repository's Bekker Wong family, given the same wheels and soil sets, differs from Chrono by 0.44 to 0.75 (root mean square). Both rest on the same Bekker and Janosi laws, so the gap is a measure of implementation and model form uncertainty, not of physics.

![Single wheel slip against slope in Project Chrono (points), the Bekker Wong family with the same wheel and soil (dashed), the existing model (dotted) and the Dumont Dunes curve (PUBLISHED, green).](../results/chrono_scm/figures/fig_chrono_vs_published.png)

### 4.4 The slip face detector works much better at 10 m than at 30 m (SIMULATED BY ME on PUBLISHED lidar)

Table 2. Slip face detector and three class map against one metre lidar truth (SIMULATED BY ME on PUBLISHED USGS 3DEP data; North American dune fields).

| Site | Posting, m | AUC | True face rate | Mean predicted probability | TRAVERSABLE share | Faces in TRAVERSABLE | Faces in UNKNOWN |
|---|---|---|---|---|---|---|---|
| Dumont | 5 | 0.98 | 23.0 % | 35.5 % | 59.3 % | 0.2 % | 51.4 % |
| Dumont | 10 | 0.97 | 32.0 % | 29.9 % | 62.0 % | 3.6 % | 77.1 % |
| Dumont | 30 | 0.86 | 48.0 % | 23.1 % | 67.8 % | 25.6 % | 95.1 % |
| WhiteSands | 5 | 0.98 | 5.0 % | 10.2 % | 87.3 % | 0.1 % | 38.4 % |
| WhiteSands | 10 | 0.97 | 10.8 % | 9.9 % | 86.0 % | 2.5 % | 61.6 % |
| WhiteSands | 30 | 0.66 | 35.7 % | 14.6 % | 75.9 % | 28.6 % | 58.0 % |
| Kelso | 5 | 0.98 | 5.5 % | 15.7 % | 79.1 % | 0.1 % | 26.4 % |
| Kelso | 10 | 0.95 | 10.7 % | 13.0 % | 80.8 % | 1.8 % | 48.4 % |
| Kelso | 30 | 0.70 | 34.0 % | 8.6 % | 88.4 % | 28.0 % | 79.5 % |

At 5 and 10 m the detector, trained only on synthetic dunes, ranks real lidar faces well and the map's TRAVERSABLE class is nearly free of steep faces. At 30 m it underestimates how many cells contain a face: about one TRAVERSABLE cell in four contains at least 10 square metres steeper than 28 degrees, and 36 % to 73 % of the cells that contain such a face are called TRAVERSABLE. At 10 m that share is still 7 % to 20 %, so even a 10 m map leaves some faces unflagged. The steepest one metre slope inside a 30 m face cell exceeds the cell's own slope by a median of 29.0 degrees at White Sands, 27.6 at Dumont and 21.8 at Kelso. At Dumont the median steepest slope in face cells is 45.0 degrees, steeper than loose sand stands, so the truth there includes rock or lidar artefacts; at White Sands it is 32.6 degrees, matching published slip face angles.

![Three class maps at 30 m over three real dune fields; black outlines mark cells that contain a face of 28 degrees or more in the one metre lidar. SIMULATED BY ME on PUBLISHED USGS 3DEP data.](../results/terrain_validation/figures/fig_lidar_class_maps_30m.png)

### 4.5 Planning on a 30 m map is not safer than naive planning (SIMULATED BY ME)

Under the registered event rule (any 3 m uphill grade above the nominal climbing limit of 25.5 degrees), 70.0 % of naive and 72.5 % of conservative routes at Dumont met such a grade at 30 m; the conservative policy cut face contacts per kilometre from 125 to 38 but doubled route length, and at White Sands and Kelso it did no better than naive. At 10 m, compared on matched pairs (only the pairs the conservative policy could route; a post hoc comparison), the conservative policy failed less often than naive at White Sands (61.1 % against 66.7 %) and Kelso (36.1 % against 63.9 %), and with a 10 m grade baseline (13.9 % against 25.0 %; 2.8 % against 11.1 %); at Dumont it could route only 15 of 40 pairs and was not safer on them. Most failures at every resolution come from metre scale steep features that no map at these postings resolves.

![First six routes per policy over the 30 m three class map. SIMULATED BY ME.](../results/planner/figures/fig_routes_30m.png)

### 4.6 Slip faces and wind (faces SIMULATED BY ME from PUBLISHED elevation; wind PUBLISHED reanalysis)

Slip face dip directions matched the resultant drift direction within 45 degrees at 4 of 6 sites (White Sands 36 degrees, Dumont 138, Kelso 55, Liwa 2, Rub' al Khali megadunes 7, linear dunes 38). With six sites this is a check of the method, not a test.

![Slip face dip directions (pink) against the resultant sand drift direction from ERA5 (plum) and the mean face dip (wine).](../results/wind_azimuth/figures/fig_face_vs_wind.png)

### 4.7 Sensitivity of the map (SIMULATED BY ME)

Under the original ranges the passable share hardly varies; its total Sobol indices are 0.55 for i0 and 0.45 for phi. Under the widened slip scale range i0 has the largest total index (0.67, with f_r at 0.48 and overlapping intervals), and first order indices sum to well below one: the parameters act through interactions. Rejecting parameter draws that cannot move on level ground removes the extreme UNKNOWN shares seen earlier (92.6 % in A falls to 33.3 %).

### 4.8 The planned field rule cannot separate a correct model from a collapse model (SIMULATED BY ME, synthetic data)

On synthetic data with the revised slope bins, the current rule accepts a correct model in 76 % of replicates and a model that collapses above 20 degrees in 53 %. Of three alternative rules, the two that reject the collapse model at least 80 % of the time (B and C) also reject the correct model more than half the time (accepting it in 39 % and 44 %); the third (A) rejects the collapse model in only 70 % of replicates. More runs in the steep bins are needed; the choice is left to the experimenter before any field day.

## 5. Discussion

The results agree on one point from three directions: the uncertainty that matters for planning on dunes is not in the parameters of a chosen slip law but in which law, which implementation and which terrain resolution. Calibrating a slip model on other vehicles' curves gives held out errors of about a quarter of the slip scale whatever the family; two implementations of the same textbook laws disagree by more than the field scatter; and a 30 m map labels 36 % to 73 % of the cells that contain a steep face as TRAVERSABLE. A small robot on a Gulf dune therefore needs, at minimum, (i) a slip curve measured for that vehicle on that sand, which the slope ladder provides, and (ii) a 10 m or finer surface of the operating area, from a drone survey or lidar, before a map based planner is trusted; onboard sensing remains necessary for metre scale features no map resolves.

These conclusions transfer to Arabian dunes only as indications. The lidar sites are North American, the field curves come from other vehicles and soils (and some from Mars), and Arabian dune sand has published grain size and mineralogy but, in the sources found, no UAE friction angle or measured slip face angle.

## 6. Threats to validity

- **Agent extraction and verification.** Both were done by language model agents; verifiers re opened the sources but may share blind spots with extractors, for example on values read from figures. A human spot check is prepared but not yet done.
- **Digitisation.** Figure points carry reading error and, for scatter plots, pooled run spread; two markers were lost in one figure and merged in another (`research/phase3/curves_notes.md`).
- **Selection of curves.** Only 4 studies supplied slip against slope curves; leave one study out with so few groups gives a coarse estimate.
- **Truth definitions.** The lidar truth counts any surface steeper than 28 degrees, including rock and artefacts; the planner's event rule depends on its baseline, which was varied post hoc.
- **Reanalysis wind.** ERA5 grid cells are tens of kilometres wide; local winds that shape dunes may differ.
- **Simulator settings.** Chrono's elastic stiffness and damping are example defaults, and the wheels are smooth.
- **Pre registration.** Some predictions were informed by quick checks, disclosed in each stage; post hoc analyses are labelled.

## 7. Limitations

No field data of the author's own; no Arabian terrain validation; one terrain model resolution test on three foreign sites; the Bekker Wong family is calibrated with a coarse optimiser; the cone index family was not implemented because the needed vehicle cone index relations for sand were not retrieved in usable form; legged and tracked vehicles appear only through published rows.

## 8. Reproducibility

All code, digitisation calibrations, result tables and figures are in the repository; raw downloads (PDFs, lidar tiles, wind series) are not redistributed but are listed with their identifiers, licences and checksums (`docs/DATA_AND_LICENSES.md`). Seeds are fixed and recorded in each result. The continuous integration checks rebuild the generated files and fail if they differ from the committed ones. The repository is public for reading; reuse requires the author's permission.

## 9. What this work is and is not

It is a verified map of the evidence, an honest validation of the available models with their failures, a resolution test of open terrain data against lidar, and a ready field protocol. It is not a validated slip model, not a traversability product, not field evidence from Arabia and not an endorsement by any institution.

## References

1. AMADEE-18 Mission Report V1.2 public version (Austrian Space Forum, Oman Dhofar Mars analog, Feb 2018) https://oewf.org/en/download/14445/ (rows FLD-042)
2. Assessment of density and shear strength of Eastern Saudi sands using dynamic cone penetration test (DCPT) (A. M. Hamid, MSc thesis, November 2013) https://eprints.kfupm.edu.sa/id/eprint/139150/1/ASSESSMENT_OF_DENSITY_AND_SHEAR_STRENGTH_OF_EASTERN_SAUDI_SANDS_USING_DYNAMIC_CONE_PENETRATION_TESTING_%28DCPT%29.pdf (rows SND-023)
3. Development and Evaluation of Mobility and Excavation Rover Toward Lunar Base Construction (Sutoh; Journal of Robotics and Mechatronics 2024, 36(2):334 to 342) https://doi.org/10.20965/jrm.2024.p0334 (rows TM3-067)
4. Failure Mechanisms and Risk Estimation for Legged Robot Locomotion on Granular Slopes https://arxiv.org/abs/2603.06928 (rows LEG-007, LEG-008, LEG-009)
5. Improving Slip Prediction on Mars Using Thermal Inertia Measurements (Cunningham, Nesnas, Whittaker; Robotics: Science and Systems XIII, 2017) https://roboticsproceedings.org/rss13/p38.pdf (rows PLN-055)
6. Improving Slip Prediction on Mars Using Thermal Inertia Measurements (Cunningham, Whittaker, Nesnas; Robotics: Science and Systems XIII, 2017) https://roboticsproceedings.org/rss13/p38.pdf (rows MAP-023)
7. Mars Exploration Rover Surface Operations: Driving Spirit at Gusev Crater (Leger et al., 2005) https://www-robotics.jpl.nasa.gov/media/documents/leger_driving05.pdf (rows FLD-011, FLD-012)
8. Modeling of the interaction of rigid wheels with dry granular media (Agarwal et al., J. Terramechanics 2019 / arXiv 2019) https://arxiv.org/abs/1901.10667 (rows TM-001, TM-004, TM-006)
9. Performance of Wheel-Typed Vehicle with Crawlers in Between Front and Rear Wheels on Soft Ground (Eto, Satomi, Takahashi; Journal of Robotics and Mechatronics 2014, 26(2):261) https://doi.org/10.20965/jrm.2014.p0261 (rows TM3-071)
10. RoverDevKit: An open, physics-grounded tradespace toolkit for conceptual design of lunar micro-rovers (Reifschneider 2026) https://arxiv.org/abs/2606.21755 (rows SIM-025, SIM-027)
11. Roving on the Edge: Robotic Operations Power Perseverance's Ascent of Jezero Crater Rim (Maimone et al., AAS 08-138) https://robotics.jpl.nasa.gov/media/documents/2026_RO_AAS_final.pdf (rows FLD-025)
12. Slope traversal controls for planetary exploration rover on sandy terrain (Ishigami, Nagatani, Yoshida, J. Field Robotics 26(3) 264-286, 2009) https://doi.org/10.1002/rob.20277 (rows TM-IS09-2)
13. Trafficability of Soils: Tests on Coarse-Grained Soils with Self-Propelled and Towed Vehicles, 1958-1961, Technical Memorandum 3-240, Seventeenth Supplement (Rush; Waterways Experiment Station, May 1963) https://apps.dtic.mil/sti/pdfs/AD0409691.pdf (rows MOB-043)
14. Traverse Performance Characterization for the Mars Science Laboratory Rover (Heverly et al. 2013, J. Field Robotics 30(6), 835-846) https://doi.org/10.1002/rob.21481 (rows FLD-HV13-1, FLD-HV13-2)
15. Traversing Steep and Granular Martian Analog Slopes With a Dynamic Quadrupedal Robot https://arxiv.org/abs/2106.01974 (rows LEG-013)
16. Validation of the AMC-71 Mobility Model, Technical Report M-76-5 (Schreiner, Willoughby; Waterways Experiment Station, March 1976) https://apps.dtic.mil/sti/pdfs/ADA023609.pdf (rows MOB-020, MOB-021, MOB-023)
17. U.S. Geological Survey, 3D Elevation Program one metre DEM tiles USGS_1M_11_x56y395_CA_FEMAR9Southeast_D24, USGS_1M_13_x37y364_NM_WhiteSandsNM_2020_D20, USGS_1M_11_x61y387_CA_FEMAR9Southeast_D24 (public domain), https://www.usgs.gov/3d-elevation-program, retrieved 2026-10-20.
18. European Space Agency and Airbus, Copernicus DEM GLO-30, https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model, retrieved 2026-10-11 and 2026-10-15 (licence in docs/DATA_AND_LICENSES.md).
19. ECMWF, ERA5 hourly reanalysis (Copernicus Climate Change Service), accessed through the Open-Meteo archive API, https://open-meteo.com (data CC BY 4.0), retrieved 2026-10-20.
20. Project Chrono, pychrono 9.0.1, https://projectchrono.org (BSD 3-Clause).
21. emcee 3.1.6, affine invariant MCMC ensemble sampler (MIT licence).

Groups of rows cited by prefix (PLN, TM3, MOB, SND, DUN, MAP, ENV rows) are listed with their sources in `research/evidence.csv` and in Appendix C of `docs/REPORT.md`.
