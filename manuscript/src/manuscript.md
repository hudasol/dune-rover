# How far can open data and textbook models predict wheeled rover slip on dune sand? An evidence synthesis, pre registered model validation and lidar test, with an Arabian focus

**Huda Mueen** (independent researcher; repository `hudasol/dune-rover`)

Manuscript generated from the repository files by `scripts/build_manuscript.py` on {{VAL:build_date}}. Every number in the text is filled in from a result file or the evidence table; `scripts/check_manuscript_numbers.py` lists every number typed by hand and its justification. Labels: **PUBLISHED** (read in a retrieved source, with an evidence row id in brackets), **SIMULATED BY ME** (output of the repository's code, simulation only and model assumption dependent), **PLANNED** (not run). No field data of the author's own exist yet. No agreement, partnership or endorsement with any institution exists.

## Abstract

Small wheeled robots are being proposed for work on Gulf dune fields, yet no published slip against slope dataset exists for a wheeled robot on Arabian dune sand. This study asks how far open elevation data and textbook terramechanics can go without such data, and states every failure. A verified evidence table of {{VAL:p3_rows_total}} published results from {{VAL:p3_sources_total}} sources was built; {{VAL:p3_rows_new}} rows were added in this round and each was re checked against its full text by an independent agent ({{VAL:p5_material_rate}} material errors before correction, Wilson 95 % interval {{VAL:p5_material_ci}}). Four slip model families (SIMULATED BY ME) were calibrated and tested on {{VAL:mv_ncurves}} digitised published slip against slope curves from {{VAL:mv_nsources}} studies by leave one study out. No family met the pre registered bar (median held out error at most 0.15): median held out root mean square slip errors were {{VAL:mv_exp_existing_heldout}} for the repository's exponential model, {{VAL:mv_mohr_coulomb_ratio_heldout}} for a Mohr Coulomb ratio, {{VAL:mv_logistic_empirical_heldout}} for a two parameter empirical curve, and {{VAL:mv_bekker_wong_heldout}} for a Bekker Wong rigid wheel model on the curves with known wheel size and load, whose predictive intervals however covered only {{VAL:mv_bekker_wong_cover}} of held out points. An independent single wheel simulation in Project Chrono (SIMULATED BY ME) with published soil sets predicted far less slip than the Dumont Dunes field curve ({{VAL:ch_w1s1_125}} against about 0.49 at 12.5 degrees), and disagreed with a direct implementation of the same Bekker and Janosi laws. Scored against one metre lidar of three North American dune fields, a slip face detector trained on synthetic dunes (SIMULATED BY ME) reached an AUC of about {{VAL:tv_auc_max_5}} at 5 m but only {{VAL:tv_auc_min_30}} to {{VAL:tv_auc_max_30}} at 30 m, where {{VAL:tv_fs_min_30}} to {{VAL:tv_fs_max_30}} of the cells a three class map called TRAVERSABLE contained steep faces and {{VAL:tv_miss_min_30}} to {{VAL:tv_miss_max_30}} of the cells containing a face were called TRAVERSABLE. Route planning on 30 m maps was no safer than naive planning (SIMULATED BY ME). The study concludes that a 10 m or finer surface and a measured slip curve for the actual vehicle are prerequisites for planning on dunes, and sets out a pre registered field experiment and a robotics project to obtain them.

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

{{TABLE:locomotion}}

**Arabian sand and dunes.** Grain size, sorting and mineralogy of UAE, Qatari, Saudi and Omani dune sands are published (SND rows); a direct shear friction angle of 45 to 48 degrees was found for Dhahran dune sand in one thesis (SND-023), and no friction angle or slip face angle measured on UAE dunes was found. Drift potentials from Gulf stations exist (DUN rows).

## 3. Data and methods

### 3.1 Evidence table and verification

Rows were extracted by topic agents under a written brief (full text only, a live DOI or URL check, licence recorded, a comparability warning per row) and then re checked by fresh agents that saw only the claim fields and re opened the full text (`docs/SEARCH_PROTOCOL.md`). Corrections enter through a corrections file; unverifiable rows are dropped; the error rate is reported with Wilson intervals. A blinded random sample of 20 rows is prepared for a human rater with an agreement script (Cohen's kappa).

### 3.2 Published curves

Slip against slope curves were digitised reproducibly from figures (calibration files and marker coordinates committed, uncertainty from axis scale and marker spread) or copied from tables, {{VAL:dc_ncurves}} curves with {{VAL:dc_npoints}} points from {{VAL:dc_nsources}} sources in total (`docs/DATA_CATALOG.md`). Each carries the vehicle, wheel size, load, soil, preparation, test type and a judgement of comparability to loose dry dune sand. Unlike conditions are never pooled into one curve.

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

The table now holds {{VAL:p3_rows_total}} rows from {{VAL:p3_sources_total}} sources ({{VAL:p3_vtype_line}}). Of the {{VAL:p5_n}} rows added and merged in this round, {{VAL:p5_material}} had a material error before correction ({{VAL:p5_material_rate}}, Wilson 95 % interval {{VAL:p5_material_ci}}) and {{VAL:p5_any_rate}} had any discrepancy; most material errors were a wrong validation type, not a wrong value. Across the whole current table, by each row's latest verdict, {{VAL:cur_material}} of {{VAL:cur_n}} rows carried a material error before correction ({{VAL:cur_material_rate}}); every material error is corrected.

### 4.2 No slip model family transfers between studies (SIMULATED BY ME against PUBLISHED curves)

{{TABLE:families}}

Fitted to one curve at a time, every family can match its shape (median error {{VAL:mv_logistic_empirical_fit}} for the logistic, {{VAL:mv_exp_existing_fit}} for the exponential model). Asked to predict a study it was not calibrated on, none can: held out errors are around 0.2 to 0.3 slip, the predictive intervals are wide enough to cover most points only because the fitted model error is about {{VAL:post_s_med}}, and the empirical logistic curve does as well as the two lumped physics models. The Bekker Wong family, the only one that uses wheel size and load, came closest ({{VAL:mv_bekker_wong_heldout}} on its 8 curves, against 0.23 for the logistic on the same curves): calibrated on the Inotsume curves (the El Dorado wheels and the Scarab rover) it predicted the Heverly curves with held out errors of 0.08 to 0.15, but calibrated on Heverly it predicted the Inotsume curves with errors of 0.20 to 0.56, and its intervals were too narrow. With its nominal parameters the repository's model misses the Dumont curve by {{VAL:mv_exp_existing_dumont_nominal}} (root mean square). The Bekker Wong family with the published simulant set of Ishigami et al. 2007 does not even reproduce that paper's own drawbar pull curve (negative pull up to 0.6 slip against 1 to 25 N measured; `results/model_validation/bw_vs_ishigami2007.csv`), because the published parameters belong to an implementation with details not reproduced here.

The posterior of the exponential family over the {{VAL:post_ncurves}} curves judged comparable to dune sand gives phi {{VAL:post_phi_deg}} degrees, f_r {{VAL:post_f_r}} and i0 {{VAL:post_i0}} (median, 5 to 95 %). Used as the map's parameter ranges, it raises UNKNOWN at 30 m to {{VAL:post_unk_A}} in Liwa (A), {{VAL:post_unk_B}} in the Rub' al Khali megadunes (B) and {{VAL:post_unk_C}} in linear dunes (C), against {{VAL:orig_unk_A}}, {{VAL:orig_unk_B}} and {{VAL:orig_unk_C}} under the original assumed ranges. About 5 % of the posterior draws cannot move on level ground; rejecting them (a post hoc choice) gives {{VAL:postm_unk_A}}, {{VAL:postm_unk_B}} and {{VAL:postm_unk_C}}, so the Arabian UNKNOWN share itself depends strongly on that choice (by a factor of 1.4 in B and of more than ten in C).

{{FIG:fits}}

### 4.3 An independent simulator does not rescue the models (SIMULATED BY ME)

With published soil sets and smooth wheels, Chrono's Soil Contact Model gives slip {{VAL:ch_w1s1_125}} at 12.5 degrees and {{VAL:ch_w1s1_30}} at 30 degrees for the Scarecrow sized wheel on the simulant set, against about 0.49 and embedding above 21 degrees on the Dumont field curve (root mean square difference {{VAL:ch_vs_dumont_rmse_grid}}). Grid halving and a fourfold lower speed changed slip by at most 0.02. The repository's Bekker Wong family, given the same wheels and soil sets, differs from Chrono by {{VAL:ch_vs_bw_lo}} to {{VAL:ch_vs_bw_hi}} (root mean square). Both rest on the same Bekker and Janosi laws, so the gap is a measure of implementation and model form uncertainty, not of physics.

{{FIG:chrono}}

### 4.4 The slip face detector works much better at 10 m than at 30 m (SIMULATED BY ME on PUBLISHED lidar)

{{TABLE:lidar}}

At 5 and 10 m the detector, trained only on synthetic dunes, ranks real lidar faces well and the map's TRAVERSABLE class is nearly free of steep faces. At 30 m it underestimates how many cells contain a face: about one TRAVERSABLE cell in four contains at least 10 square metres steeper than 28 degrees, and {{VAL:tv_miss_min_30}} to {{VAL:tv_miss_max_30}} of the cells that contain such a face are called TRAVERSABLE. At 10 m that share is still {{VAL:tv_miss_min_10}} to {{VAL:tv_miss_max_10}}, so even a 10 m map leaves some faces unflagged. The steepest one metre slope inside a 30 m face cell exceeds the cell's own slope by a median of {{VAL:tv_gap_WhiteSands}} degrees at White Sands, {{VAL:tv_gap_Dumont}} at Dumont and {{VAL:tv_gap_Kelso}} at Kelso. At Dumont the median steepest slope in face cells is {{VAL:tv_max1m_Dumont}} degrees, steeper than loose sand stands, so the truth there includes rock or lidar artefacts; at White Sands it is {{VAL:tv_max1m_WhiteSands}} degrees, matching published slip face angles.

{{FIG:lidar}}

### 4.5 Planning on a 30 m map is not safer than naive planning (SIMULATED BY ME)

Under the registered event rule (any 3 m uphill grade above the nominal climbing limit of 25.5 degrees), {{VAL:pl_Dumont_30_naive}} of naive and {{VAL:pl_Dumont_30_conservative}} of conservative routes at Dumont met such a grade at 30 m; the conservative policy cut face contacts per kilometre from {{VAL:pl_fpk_Dumont_30_naive}} to {{VAL:pl_fpk_Dumont_30_conservative}} but doubled route length, and at White Sands and Kelso it did no better than naive. At 10 m, compared on matched pairs (only the pairs the conservative policy could route; a post hoc comparison), the conservative policy failed less often than naive at White Sands ({{VAL:pm3_WhiteSands_10_conservative}} against {{VAL:pm3_WhiteSands_10_naive}}) and Kelso ({{VAL:pm3_Kelso_10_conservative}} against {{VAL:pm3_Kelso_10_naive}}), and with a 10 m grade baseline ({{VAL:pm10_WhiteSands_10_conservative}} against {{VAL:pm10_WhiteSands_10_naive}}; {{VAL:pm10_Kelso_10_conservative}} against {{VAL:pm10_Kelso_10_naive}}); at Dumont it could route only {{VAL:pm_n_Dumont_10}} of 40 pairs and was not safer on them. Most failures at every resolution come from metre scale steep features that no map at these postings resolves.

{{FIG:routes}}

### 4.6 Slip faces and wind (faces SIMULATED BY ME from PUBLISHED elevation; wind PUBLISHED reanalysis)

Slip face dip directions matched the resultant drift direction within 45 degrees at {{VAL:wind_hits}} sites (White Sands {{VAL:wind_diff_WhiteSands}} degrees, Dumont {{VAL:wind_diff_Dumont}}, Kelso {{VAL:wind_diff_Kelso}}, Liwa {{VAL:wind_diff_A_south_Liwa}}, Rub' al Khali megadunes {{VAL:wind_diff_B_RubAlKhali_megadunes}}, linear dunes {{VAL:wind_diff_C_RubAlKhali_linear}}). With six sites this is a check of the method, not a test.

{{FIG:wind}}

### 4.7 Sensitivity of the map (SIMULATED BY ME)

Under the original ranges the passable share hardly varies; its total Sobol indices are {{VAL:sob_original_i0_ST}} for i0 and {{VAL:sob_original_phi_deg_ST}} for phi. Under the widened slip scale range i0 has the largest total index ({{VAL:sob_widened_i0_i0_ST}}, with f_r at {{VAL:sob_widened_i0_f_r_ST}} and overlapping intervals), and first order indices sum to well below one: the parameters act through interactions. Rejecting parameter draws that cannot move on level ground removes the extreme UNKNOWN shares seen earlier ({{VAL:wfr_unk_A}} in A falls to {{VAL:q8_unk_A}}).

### 4.8 The planned field rule cannot separate a correct model from a collapse model (SIMULATED BY ME, synthetic data)

On synthetic data with the revised slope bins, the current rule accepts a correct model in {{VAL:ro_current_model_0.03}} of replicates and a model that collapses above 20 degrees in {{VAL:ro_current_collapse_0.03}}. Of three alternative rules, the two that reject the collapse model at least 80 % of the time (B and C) also reject the correct model more than half the time (accepting it in {{VAL:ro_B_model_0.03}} and {{VAL:ro_C_model_0.03}}); the third (A) rejects the collapse model in only {{VAL:ro_A_collapse_rej_0.03}} of replicates. More runs in the steep bins are needed; the choice is left to the experimenter before any field day.

## 5. Discussion

The results agree on one point from three directions: the uncertainty that matters for planning on dunes is not in the parameters of a chosen slip law but in which law, which implementation and which terrain resolution. Calibrating a slip model on other vehicles' curves gives held out errors of about a quarter of the slip scale whatever the family; two implementations of the same textbook laws disagree by more than the field scatter; and a 30 m map labels {{VAL:tv_miss_min_30}} to {{VAL:tv_miss_max_30}} of the cells that contain a steep face as TRAVERSABLE. A small robot on a Gulf dune therefore needs, at minimum, (i) a slip curve measured for that vehicle on that sand, which the slope ladder provides, and (ii) a 10 m or finer surface of the operating area, from a drone survey or lidar, before a map based planner is trusted; onboard sensing remains necessary for metre scale features no map resolves.

These conclusions transfer to Arabian dunes only as indications. The lidar sites are North American, the field curves come from other vehicles and soils (and some from Mars), and Arabian dune sand has published grain size and mineralogy but, in the sources found, no UAE friction angle or measured slip face angle.

## 6. Threats to validity

- **Agent extraction and verification.** Both were done by language model agents; verifiers re opened the sources but may share blind spots with extractors, for example on values read from figures. A human spot check is prepared but not yet done.
- **Digitisation.** Figure points carry reading error and, for scatter plots, pooled run spread; two markers were lost in one figure and merged in another (`research/phase3/curves_notes.md`).
- **Selection of curves.** Only {{VAL:mv_nsources}} studies supplied slip against slope curves; leave one study out with so few groups gives a coarse estimate.
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

{{REFERENCES}}
