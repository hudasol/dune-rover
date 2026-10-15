# Independent fact-check of docs/REPORT.md prose (before Appendix A)

Checker did not write the report. No file in the build workspace other than this one was edited. All checks are against the repository files named in the task; no web or memory was used. Simulation numbers were recomputed from results/*.csv and results/summary.json with python3; the verification statistics (exact bounds, Wilson intervals, row counts) were recomputed from research/evidence.csv.

## Summary

Claims checked: 225 (claim IDs C001 to C241; the gaps in numbering are claims merged into a neighbouring ID).

| Verdict | Count | Share |
|---|---|---|
| CORRECT | 188 | 83.6 % |
| MINOR | 26 | 11.6 % |
| WRONG | 5 | 2.2 % |
| UNVERIFIABLE | 6 | 2.7 % |

Overall WRONG rate: 5/225 = 2.2 %. WRONG plus MINOR: 31/225 = 13.8 %. (Claims were counted at the granularity of one number-bearing sentence fragment or one table block; a table block that matched entirely, for example the 40 cells of Table 8.4, counts once, so the rate is a rate over claim groups, not over individual numbers. Every individual number in Tables 8.2 to 8.5 was nevertheless compared.)

### Answers to the specific concerns

- (a) Row-ID mix-ups: found in three places (SIM-004 cited for the 30 degree gravity pair, SIM-015 cited as a Chrono/NASA comparison, SIM-011 cited for DEM cost) and one unit error that uses TM-001 to TM-004 (values in N and mm) as percentages. All other row IDs cited in sections 0, 3, 4, 7, 8 say what the sentence says (value, unit, slope, vehicle, validation type checked row by row). The Perseverance rows are correctly LRN-010/011 (the older LRN-011/012 numbering in learning_notes.md was not carried over).
- (b) Simulation or lab shown as field: no simulation result is presented as field evidence. Two lab or sim-vs-lab rows are blurred: FLD-006 (an Earth lab tilt bed) is called "Mars slip numbers" in section 10 (WRONG, C232), and LRN-019 (sim-vs-lab) is labelled "lab" in 3.4 (MINOR, C082). Section 7.1 item 1 and 7.1 "Mars field data (FLD-001 to FLD-025)" include Earth lab rows FLD-006 to FLD-008 (MINOR).
- (c) x-fold and percentage claims in section 8: all reproduce from the CSV files. Janosi form 8.02-fold, additive cross rule 3.92-fold, friction angle 28 to 38 about 50-fold (50.0 with unrounded values, 42 with the rounded values printed in Table 8.2), 0.25/0.05 and 0.5/0.24 for coarser posting, Spearman values (-0.67 and so on), R-squared 0.86 to 0.96, climbing limit 7.6 to 34.7, all correct. The only soft spot is "about two orders of magnitude" for blocked share (C216).
- (d) Executive summary versus body: consistent except "two orders of magnitude" for K (75-fold in the body), "90 m products remove almost all slopes above 25 degrees" (81 % in window B), "Six passes collected 144 rows" (five passes) and "All were corrected" (SIM-013 is still open).
- (e) Taxonomy table: 13 cells checked; one WRONG (RFT strengths, units), two MINOR (K about 100-fold; Chrono cheaper than DEM cited to SIM-011), the rest correct.
- (f) Sections 5 and 6: one WRONG in each (skadi coverage; TII vehicle "shown in 2026"), several MINOR labels. Section 6 UAE01 to UAE27 attributions are otherwise right.
- Not carried over by the report but worth knowing: UAE06's own note says the Rashid rig data were used for both tuning and validation (not independent); section 6 does not claim otherwise.

## Claims that are not CORRECT

| ID | Section | Exact fragment | Verdict | What the source says (file, row or line) | Suggested corrected wording |
|---|---|---|---|---|---|
| C034 | 3.1 | "the fitted kphi roughly doubles (about 430 to 800-880) ... and kc turns negative" | WRONG | evidence.csv TM-029, soil_parameters_reported, Table 2: kc 2.54 (circular), 2.99 (aspect 6), 6.30 (aspect 3), 10.41 (aspect 2), 9.04 (aspect 1.4), all positive and rising as aspect ratio falls. No negative kc in this row. (The same error is in terramechanics_notes.md KEY_FINDINGS 2; the negative kc values in the table are TM-001/TM-002 for Quikrete sand, a different source.) | "... and kc rises about four-fold (from about 2.5-3 to 9-10)" |
| C111 | 4 (RFT row, Strengths) | "sinkage and drawbar within roughly 5 to 15 % in controlled beds (TM-001 to TM-004, TM-008 to TM-013)" | WRONG | TM-001 5.55 N, TM-002 7.11 N, TM-003 15.11 N (drawbar mean absolute error, unit N), TM-004 18.41 mm (sinkage, unit mm): none is a percentage. Percentage rows: TM-008 6.84 %, TM-009 2.6 %, TM-011 within 15 %, TM-012 within 15 % (L-legs) and within 30 % (reversed L-legs), TM-013 1.2-6.5 %. TM-008 to TM-012 are legged robots or plates, mostly poppy seeds or glass beads, not wheels on sand. | "wheel drawbar mean absolute error 5.6-15 N and sinkage 18 mm at 190 N (TM-001 to TM-004); relative errors of about 2.6-15 % (up to 30 % for reversed legs) for legged or plate tests (TM-008 to TM-013)" |
| C150 | 5 (data table, skadi row) | Coverage cell "60 N to 56 S" for "SRTM-derived 'skadi' tiles" | WRONG | data_audit.csv: skadi row coverage = "Global (skadi); registry: bare-earth terrain heights". "60N-56S" is the coverage of the NASADEM row; ASTER GDEM is 83N-83S. The report seems to have shifted the NASADEM coverage onto skadi and written "Large parts of the globe" for NASADEM/ASTER. | skadi: "Global (mixed SRTM/other sources)"; NASADEM: "60 N to 56 S"; ASTER GDEM v3: "83 N to 83 S" |
| C167 | 6 (Desert ground vehicles) | "TII, SteerAI's xRift (debuted 20 January 2026) and a Space42 vehicle ... were shown in 2026" | WRONG | uae_facts.csv UAE22 (TII UGV): "page date shown 05-01-23; metadata modified 2025-05-19", status partially-verified, date ambiguous. uae_notes.md SUMMARY: UGVs "were shown in 2023-2026". Only xRift (UAE23) and Space42 (UAE25) are UMEX January 2026. | "A TII desert UGV (page dated 2023 or 2025; date ambiguous) and, at UMEX in January 2026, SteerAI's xRift (debuted 20 January 2026) and a Space42 vehicle (25 degree slope capability stated) were shown; ..." |
| C232 | 10 (Limits of the review) | "Mars slip numbers from a press release (FLD-006, excluded from the comparison)" | WRONG | FLD-006 validation_type = lab; terrain = variable-tilt platform with 6 inches of dry loose sand, "Earth gravity lab tilt bed" with SSTB-lite, an engineering model of MER (comparability_warning). It is an Earth lab tilt bed number quoted in a JPL press release about Mars, not a Mars slip measurement. Presenting it as "Mars slip numbers" blurs lab and field. | "tilt-bed slip numbers for a MER engineering model from a JPL press release (FLD-006, excluded from the comparison)" |
| C001 | 0 (Method) | "Six parallel research passes (terramechanics, simulation, learning, field and analog, legged and wheel design, open data and UAE context) collected 144 evidence rows" | MINOR | Evidence rows come from five passes (raw row files: terramechanics 30, simulation 30, learning 24, field 42, legged 24 = 150, minus 6 duplicates in dedup_log.md = 144). The open-data/UAE pass produced data_audit.csv, morphology_rows.csv and uae_facts.csv, not evidence rows. | "Five row-extraction passes ... collected 144 evidence rows; a sixth pass audited open data and UAE facts" |
| C008 | 0 (finding 1) | "The Janosi shear modulus K ... differs by about two orders of magnitude between papers" | MINOR | terramechanics_notes.md: K 0.0006 m (Agarwal MS/MMS) to 0.045 m (poppy seeds, TM-005, K tuned ad hoc): ratio 75, i.e. 1.9 orders; the high end is poppy seeds, not sand. Same rounding appears in section 4 ("about 100-fold"). | "differs by about 75-fold (0.0006 to 0.045 m, the top of the range from poppy seeds)" |
| C017 | 0 (finding 6) | "90 m products remove almost all slopes above 25 degrees" | MINOR | slope_stats.csv pct_gt_25 at 30 m vs 90 m: A_south 0.570 -> 0.0046 (99 % removed); A_north 0.304 -> 0 (100 %); B_RubAlKhali 2.33 -> 0.437 (81 % removed, 19 % remain). data_notes.md for AOI B: >25 deg 2.54 % -> 0.67 % by the earlier central-difference audit. | "90 m products remove 80 to 100 % of cells steeper than 25 degrees in the three windows" |
| C029 | 0 (Verification) | "Flagged rows: 0 of 7 material, 3 of 7 minor. All were corrected." | MINOR | verification_log.md / corrections.csv: FLD-004, FLD-023 corrected; SIM-013 only received a note: "the dimensional concern stays open. Treat as unverified numerically." evidence.csv still has recheck_flag = yes for SIM-013. | "... 3 of 7 minor. Two were corrected; SIM-013's unit question remains open." |
| C037 | 1 (Method) | "A second pass on the report's numeric claims is described in section 11." | MINOR | Section 11 says "Report claims, second pass. Pending at the time of building this file." Nothing is described. | "A second pass on the report's numeric claims is planned (section 11 records its status)." |
| C046 | 3.2 | "The response surfaces for the fines were scaled from poppy-seed data rather than measured directly." (also section 4 RFT row: "scaled response surfaces for fines") | MINOR | TM-001 comparability_warning: "RFT response surface for MS/MMS was NOT measured directly but scaled from poppy-seed data". MS is the medium sand, not only the fines, so the 5.55 and 7.11 N medium-sand results are also affected. | "The response surfaces for both Quikrete medium sand and the fines were scaled from poppy-seed data" |
| C055 | 3.2 | "Legged RFT follow-ups agree with controlled-box experiments within roughly 7 to 15 % (TM-008, TM-009, TM-011, TM-012)" | MINOR | TM-008 6.84 %, TM-009 2.6 % (sinkage overestimate), TM-011 within 15 %, TM-012 within 15 % (L-legs) and within 30 % (reversed L-legs up to 3 Hz). TM-011 and TM-012 are on poppy seeds, not sand. The 7-15 % range is copied from terramechanics_notes.md, which also included TM-013 (1.2-6.5 %). | "within roughly 3 to 15 % (up to 30 % for reversed legs); two of the four tests used poppy seeds, not sand" |
| C064 | 3.3 | "Chrono CRM and SCM wheel and rover comparisons against NASA tilted-bed data ... (SIM-001, SIM-002, SIM-009, SIM-015)" | MINOR | SIM-001 is CRM against the NASA Glenn TREC single-wheel rig on a flat bed (not tilted); SIM-015 is an EDEM DEM model of the Rashid-1 wheel against a single-wheel testbed (not Chrono, not NASA, not tilted); no row compares SCM with NASA data (SIM-005 to SIM-008 are SCM vs DEM). | "CRM and DEM wheel and rover comparisons against lab data (NASA flat and tilted beds, SIM-001, SIM-002, SIM-009; Rashid-1 wheel rig, SIM-015)" |
| C069 | 3.3 | "and below 1 for a closed-form Bekker-Wong solve (SIM-028)" (wall-clock to simulated time) | MINOR | SIM-028 value: "0.50 ms per wheel solve (median); 10.3 ms per mission evaluation" - a compute time, with no simulated-time denominator; the row note calls it "RTF far below 1" (inference). Not comparable to the real-time factors listed with it. | "and about 0.5 ms per closed-form wheel solve (SIM-028; no simulated-time ratio reported)" |
| C071 | 3.3 (Gravity) | "predicted far higher slip than a light 1 g rover test (about 85 % versus about 42 % at 30 degrees; SIM-003, SIM-004)" | MINOR | SIM-003 = 85 % at 30 deg. SIM-004 = 75 % at 10 deg (its pair is 18 %), not 30 deg. The 42 % figure appears only in SIM-003's comparability warning, which says the passage does not state whether it is measured or simulated, so "test" is not supported. | "about 85 % versus about 42 % at 30 degrees (SIM-003; the source of the 42 % is not stated) and about 75 % versus 18 % at 10 degrees (SIM-004)" |
| C082 | 3.4 (Transfer) | "... (LRN-019, lab, trial count not stated)" | MINOR | LRN-019 validation_type = sim-vs-lab (policy trained in simulation, tested on a physical rover on M90 simulant). Calling it "lab" hides the simulation-trained part; the other numbers (81.9 -> 43.0 %, 100 -> 30 %) are right. | "(LRN-019, sim-vs-lab, trial count not stated)" |
| C100 | 3.5 (Lab-to-field) | "Engineering slip tables built from a dry-sand tilt bed worked on pure sand but failed on mixed or hidden weak deposits (Maimone et al., Lamarre and Kelly ...)" | MINOR | field_notes.md GAPS: tables "worked on pure Eagle-crater sand but failed on mixed or nonhomogeneous terrain and on hidden weak deposits (Maimone 2007)"; Lamarre and Kelly 2018 are cited only for "vision-based slip prediction fails on sand". Attribution to both is loose. | "(Maimone et al.); separately, Lamarre and Kelly report that vision-based slip prediction fails on sand" |
| C122 | 3.6 (Legs) | "A 22 kg quadruped (SpaceBok) slipped near the soil friction angle and sank up to 120 mm with point feet (LEG-010, LEG-013)" | MINOR | LEG-010 = 120 mm max foot sinkage (point feet) - correct. LEG-013 = maximum slope traversed 25 deg (testbed limit), no slip value. legged_notes.md: it was the planar feet that "slipped near the soil friction angle" (LEG-010/012/013 together); point feet sank but resisted slip. The sentence merges the two foot types. | "Planar feet slipped near the soil friction angle, while point feet sank up to 120 mm (LEG-010, LEG-012, LEG-013; testbed limit 25 degrees)" |
| C128 | 4 (Slope-threshold row) | "K varies about 100-fold, section 3.1" | MINOR | Section 3.1 gives 0.0006 to 0.045 m = 75-fold, and the top is poppy seeds. See C008. | "K varies about 75-fold" |
| C143 | 4 (Chrono row) | "Orders of magnitude cheaper than DEM (SIM-011)" | MINOR | SIM-011 compares CRM with SCM only (RTF 10.9-50.7); it contains no DEM figure. DEM-vs-SCM cost is in SIM-007/SIM-008 (derived ratios about 160x and 500x) and RTFs for DEM in SIM-016/020/024. | "Two to several orders of magnitude cheaper than DEM (SIM-007, SIM-008, SIM-011)" |
| C146 | 5 (GLO-30 row, Resolution) | "about 28.3 m E-W by 30.9 m N-S at 23.5 N (my arithmetic from tile geometry)" | MINOR | E-W 28.3 m agrees (data_notes.md). N-S 30.9 m is the spherical-Earth value (30.89 m in data_notes.md); the code actually used for all results gives dy = 30.76 m (summary.json areas.*.dy_m) and dx = 28.40-28.61 m. Section 8 results therefore use 30.8 m, not 30.9 m. | "about 28.3 m E-W by 30.8-30.9 m N-S (30.76 m on the ellipsoid used by the code)" |
| C148 | 5 (GLO-90 row) | "Block-mean of GLO-30 gives the same slopes as the official product in my check" | MINOR | data_notes.md AOI A: official GLO-90 max 27.7, >20 deg 0.30 %, >25 deg 0.029 %; own 3x3 block mean max 27.7, 0.30 %, 0.037 %. Same in two statistics, but the >25 deg tail differs by about 28 % relative. | "Block-mean of GLO-30 reproduces the official product's slope statistics closely (max 27.7 degrees, 0.30 % above 20 degrees; 0.037 % against 0.029 % above 25 degrees)" |
| C151 | 5 (NASADEM, ASTER row) | Coverage "Large parts of the globe"; licence "Free with Earthdata login" | MINOR | data_audit.csv: NASADEM 60N-56S, 'openly shared, without restriction'; ASTER 83N-83S, 'as is', openly shared. Earthdata Login is an access requirement (access_tested = NO), not part of the licence. Row combines two products with different extents. | "NASADEM 60 N to 56 S; ASTER 83 N to 83 S; openly shared, download needs an Earthdata login" |
| C158 | 5 (Can slip faces ... be resolved?) | "published wavelengths 0.6 to 3.3 km (USGS Professional Paper 1052 Landsat morphometry; morphology_rows.csv)" | MINOR | morphology_rows.csv M18-M23 (PP1052 mean wavelengths): 1.41, 2.18, 3.17, 0.63, 2.56, 2.06 km, i.e. 0.63 to 3.17 km. 3.3 km appears only in M12 (Lancaster via Guth, spacing 1500-3300 m), a different source. (The conclusion '20 to 110 posts' follows from the stated range; with 3.17 km it is 21 to 106.) | "published mean wavelengths 0.63 to 3.17 km (PP1052)" |
| C175 | 7.1 item 1 | "Every quantitative sand-slope result is lab or Mars; none is Arabian dune sand." | MINOR | SIM-013 (Kern et al. 2026, EX1 rover on a prepared 20 x 20 m Earth sand field, slopes 0 to 18 deg, validation_type = field) is a quantitative Earth sand-slope regression that is neither a lab bed nor Mars (though its alpha unit is unresolved, recheck_flag yes). LEG-016 and LRN-024 are Earth sand/field rows without slope values. | "Every quantitative sand-slope result is lab, a prepared sand field (SIM-013) or Mars; none is Arabian dune sand." |
| C176 | 7.1 item 1 | "Lab slope beds use simulants or Toyoura sand, small wheels and slow speeds (FLD-027 to FLD-035, LEG-017 to LEG-020, TM-022 to TM-024)" | MINOR | FLD-027/FLD-028 are the Scarab rover: 400 kg, 71 cm x 18 cm wheels on GRC-1 simulant (not small). FLD-036/037/038 are also lab rows. | "... mostly small wheels (exception: the 400 kg Scarab, FLD-027, FLD-028) and slow speeds ..." |
| C177 | 7.1 item 1 | "Mars field data ... on megaripples, crusts and sulfates (FLD-001 to FLD-025)" | MINOR | FLD-006, FLD-007, FLD-008 (SSTB-lite tilt platform, Earth gravity) have validation_type = lab and lie inside FLD-001 to FLD-025; FLD-021 and FLD-023 are operating or design limits; FLD-019 to FLD-022 are slip statistics of traction control and thresholds. | "(FLD-001 to FLD-025, apart from the Earth tilt-bed rows FLD-006 to FLD-008)" |
| C179 | 7.1 item 2 | "The mechanism, a hidden crust or moisture change under a visually identical surface, appears in the Spirit 15 to 20 % versus 95 % pair (FLD-011, FLD-012)" | MINOR | FLD-011/FLD-012 state only that PanCam imagery showed no visible difference and that slip is not predictable from slope or imagery alone; no mechanism (crust, moisture) is given in the rows or in field_notes.md for this pair. The mechanism is the report's interpretation (FLD-040 mentions a crust only for Spirit's Troy deposit). | "The same pattern appears in the Spirit pair ... (cause not stated in the source)" |
| C216 | 8.4 item 5 | "Blocked share varies by about two orders of magnitude across the assumption space (A core: 0 to 5 %; B core: about 0.01 to 19.5 %)" | MINOR | sensitivity_lhs_B_core.csv: min 0.0001, max 0.195 = 1950-fold (3.3 orders); A core min 0.0000 (zero), so no ratio. The 5th-95th percentiles give about 120-fold (A: 0.0002 -> 0.0240) and 180-fold (B: 0.0003 -> 0.0550), i.e. about 2.1-2.3 orders. The sentence quotes min-max but the order of magnitude matches 5-95 %. | "varies by about two orders of magnitude between the 5th and 95th percentiles (A core 0.02 to 2.4 %; B core 0.03 to 5.5 %); the extremes span 0 to 5 % (A) and 0.01 to 19.5 % (B)" |
| C219 | 8.5 intro | "nine from the evidence rows FLD-010 to FLD-031 apart from FLD-006" | MINOR | anchor_check.csv uses FLD-010, 011, 012, 025, 027, 028, 029, 030, 031 (nine). FLD-006 is outside the FLD-010 to FLD-031 range, so 'apart from FLD-006' is redundant; FLD-013 to FLD-024 (except 025) and FLD-032 to FLD-038 were also not used. | "nine from FLD-010, -011, -012, -025 and -027 to -031" |
| C241 | 10 (Limits) | "It cannot give soil parameters for Gulf sand. The only grain sizes retrieved are from Kuwait and Brazil." | MINOR | Grain sizes of lab sands are retrieved in many rows (e.g. TM-001 Quikrete 0.3-0.8 mm, TM-018 olivine 90-700 um, SIM-018 Toyoura 106-300 um). Only the dune-sand grain sizes (M07, M30) are Kuwait and Brazil, as section 7.2 item 3 says. | "The only grain sizes of natural dune sand retrieved are from Kuwait and Brazil" |
| C038 | 1 | "One deviation is documented: the verification pass was run on the draft evidence table, before this report's prose was written" | UNVERIFIABLE | No log orders the two events; file mtimes (PROTOCOL.md 06:53, evidence.csv 07:33) show only that the protocol precedes the table. verification_log.md has no date or ordering. | Keep only if a log or source is added; otherwise soften. |
| C039 | 1 | "Written before searching (docs/PROTOCOL.md)" | UNVERIFIABLE | PROTOCOL.md says '(written before searching)' in its own title; no independent timestamp (only file mtime 06:53 same day). | Keep only if a log or source is added; otherwise soften. |
| C040 | 1 (Limits of the search) | "Wong 2008" (as the textbook not retrieved) | UNVERIFIABLE | terramechanics_notes.md names Wong 'Theory of Ground Vehicles' without an edition year; the year 2008 is not in the notes. | Keep only if a log or source is added; otherwise soften. |
| C155 | 5 (ALOS row) | Coverage "Global except Japan, Antarctica" | UNVERIFIABLE | data_audit.csv: "Global land within ~82 deg lat (tiles; v4.1 19,051 tiles)". No exclusion of Japan appears in any file read. | Keep only if a log or source is added; otherwise soften. |
| C157 | 5 (Maxar row) | Resolution "sub-metre class" | UNVERIFIABLE | data_audit.csv: "sub-metre class (resolution figure not stated on registry page I read)"; data_notes.md also says sub-metre without a retrieved source. | Keep only if a log or source is added; otherwise soften. |
| C195 | 8.1 (Seeds and reproducibility) | "the full study was run twice and the summary numbers were identical (checked by comparing results/summary.json)" | UNVERIFIABLE | Only one summary.json and one run_log.txt exist (single 329.3 s run). No record of a second run or a comparison was found in the repository files read. | Keep only if a log or source is added; otherwise soften. |

## Claims judged CORRECT

Format: ID (section) label. Row IDs in a label were checked for value, unit, slope, vehicle and validation type.

- C002 (0) Method: protocol first; 30 random + 7 flagged rows re-checked
- C003 (0) Method: Copernicus GLO-30, Liwa and Rub al Khali windows, OAT and LHS sensitivity
- C004 (0 f1) Bekker-Wong drawbar errors 24-27 % median on two lunar-simulant datasets (SIM-025, SIM-026)
- C005 (0 f1) sinkage errors 28-52 %
- C006 (0 f1) 135 % and 385 % on a firm soil with small light wheel (SIM-027)
- C007 (0 f1) RFT drawbar MAE about 5 to 7 N on medium sand and 15 N on fine simulant (TM-001 to TM-003)
- C009 (0 f2) drawbar coefficient fell 8 % (0.01-0.2 m/s) and 63.7 % (0.2-1 m/s), TM-018/019
- C010 (0 f2) untuned side-slip 14.8 % at 10 deg and 25.9 % at 20 deg, TM-022/023, thesis
- C011 (0 f2) 0.49 % at 20 deg after tuning on same case, TM-024, in-sample
- C012 (0 f3) Spirit 15-20 % at 19 deg, 95 % at 16 deg about 30 m later, similar-looking terrain (FLD-011/012)
- C013 (0 f3) Opportunity VO slip 98.9-99.5 % at Purgatory (FLD-002)
- C014 (0 f3) Perseverance >94 % at about 20 deg (FLD-025)
- C015 (0 f3) VO degrades on bland sand (FLD-041, qualitative)
- C016 (0 f4) AUROC 0.874 on held-out sols, LRN-010; no terrain-type hold-out; no learned error on Earth dunes
- C018 (0 f5) AMADEE-18 Husky rover in Dhofar, looser sand than expected, got stuck (FLD-042)
- C019 (0 f5) No Bekker/RFT parameters, grain-size map or open LiDAR/drone DEM found; UAE wheel work is single-wheel lunar simulant
- C020 (0 f6) GLO-30 about 28 by 31 m, free licence with attribution, resolves crests and interdune corridors
- C021 (0 f6) slip faces of large Rub al Khali dunes 1 to 4 posts wide, slope biased low
- C022 (0 sim) blocks only 0.2 to 1 % of travel directions (0.20, 0.25, 0.97 %)
- C023 (0 sim) nominal climbing limit 25.5 deg
- C024 (0 sim) climbing limit 7.6 to 34.7 deg; 5-95 % about 15 to 32 deg (pooled 14.9-31.6)
- C025 (0 sim) ranking of influential assumptions (phi, slip-law form, DEM posting, i0, f_r; noise and i_max least)
- C026 (0 ver) random 30: 0 material, upper bound 9.5 %, 6 minor, 20 %, Wilson 9.5-37.3 % (recomputed)
- C027 (0 ver) flagged 0/7 material, 3/7 minor
- C028 (0 ver) 107 other unflagged rows not re-checked
- C030 (0) Slope ladder 0, 5, 10, 15, 20, 25 deg, RTK, calibrate gentle, predict steep blind (plan section 7)
- C031 (0) No published slip-vs-slope dataset for wheeled robot on dune sand (consistent with field_notes GAPS)
- C032 (1) 144 rows: 63 lab, 41 field, 20 simulation-only, 19 sim-vs-lab, 1 sim-vs-field (recounted)
- C033 (1) US-only search tool; Bekker 1969 and Wong and Reece 1967 not retrieved; JoT and Science paywalled
- C041 (2) friction angle about 28 to 38 deg in lab papers; slip-face angle of repose 32-35 deg (M05)
- C042 (2) dry sand has almost no cohesion (rows give c = 0 to 2 kPa)
- C043 (3.1) kphi about 430 to 800-880 as plate aspect ratio drops from 6 to 2-1.4 (TM-029)
- C044 (3.1) sinkage goodness of fit 65 to 95 % (TM-029)
- C045 (3.1) K from 0.0006 m to 0.045 m
- C047 (3.1) Wong dry-sand table not retrieved; secondary table has apparent transcription error (kc = clay entry)
- C048 (3.1) RoverDevKit median errors 24 % (FJS-1) and 27 % (Ding), sinkage 28 and 52 %
- C049 (3.1) 135 % drawbar and 385 % sinkage, small light wheel on dense simulant
- C050 (3.1) 'authors' evaluations of other authors' data, sim-vs-lab, not field'
- C051 (3.1) thesis, 7 kg rover, Toyoura sand, 14.76 % at 10 deg, 25.91 % at 20 deg, 0.49 % at 20 deg after tuning
- C052 (3.1) side-slip distance ratio not slip ratio; sandbox 0.08 m deep; parameters borrowed from another lab
- C053 (3.1) drawbar coefficient 8 % and 63.7 % at 20 % slip on olivine sand (TM-018/019)
- C054 (3.1) TM-021 '85 %' is an in-sample goodness of fit
- C056 (3.2) RFT MAE 5.55 to 7.11 N across loads on Quikrete medium sand (TM-001/002)
- C057 (3.2) MMS 15.11 N and 18.41 mm at 190 N (TM-003/004)
- C058 (3.2) error grows with load; RFT under-predicts at low positive slip and over-predicts at |slip| > 0.4
- C059 (3.2) poppy seeds: RFT sinkage 2.73 mm vs 26.07 mm; drawbar 5.05 N vs 3.41 N (TM-005/006)
- C060 (3.2) plate in Bekker fit far smaller than wheel patch
- C061 (3.2) scaling laws within about 3 % on level Quikrete sand (TM-007)
- C062 (3.2) slopes and lunar gravity checked only in DEM, slip RMSE 0.015 (TM-020, simulation-only)
- C063 (3.2) no physical sloped or low-gravity scaling validation found
- C065 (3.2) 10.5 and 11.5 % mean speed and height error against beach (TM-010, sim-vs-field, legged)
- C066 (3.2) humanoid RFT-trained, real dry sand, up to 2.5 m/s commanded (LEG-015)
- C067 (3.3) 2D DEM grouser wheel on Toyoura 12.1 % vs 14.7 +/- 3.0 % (SIM-018)
- C068 (3.3) 36 M-particle DEM: pull 15 vs 17 % weight, gross traction 20 vs 31 % at 20 % slip, sinkage and resistance under-predicted (SIM-019)
- C070 (3.3) soft foot silica sand mean pressure-sinkage difference 13.5 % (SIM-021)
- C072 (3.3) slope-climbing limit error not reported anywhere in retrieved set
- C073 (3.3) SCM fitted to DEM: negative Kc, phi about 21 deg (SIM-005)
- C074 (3.3) DEM scaled particles (SIM-015) and tuned friction (SIM-018)
- C075 (3.3) about 9 million (SIM-020, derived; 26 h per 10 ms = 9.4e6)
- C076 (3.3) hundreds or thousands for GPU DEM (SIM-016 about 840; SIM-024 about 3240)
- C077 (3.3) Chrono CRM 11-23 (10.9, 22.5) and SCM 18-51 (17.6-50.7) on SIM-011 benchmark
- C078 (3.3) SCM-vs-CRM ordering depends on benchmark (simulation_notes: SCM about 2 in Zhang setup)
- C079 (3.3) Chrono BSD-3 verified from LICENSE; not used by repository code (grep of src and scripts; DATA_AND_LICENSES.md)
- C080 (3.3) no source compares Chrono/DEM/multibody with full rover on real dune sand
- C081 (3.4) 1000-2000 stereo frames per terrain (LRN-003 terrain description)
- C083 (3.4) Perseverance 43,000 images, 500 sols, 45 km (LRN-010)
- C084 (3.4) 13,000 samples (9235 train, 3958 test), one single-wheel testbed (LRN-009)
- C085 (3.4) AUROC 0.874, F1 0.758, sand dune patch about 0.3 slip (LRN-010/011)
- C086 (3.4) held out by sol not terrain; Mars; no-alignment AUROC 0.723 (LRN-011)
- C087 (3.4) gravel test 27.5 % vs 7.16 % train (LRN-003)
- C088 (3.4) 11.2 -> 21.8 % when soil/gravel misclassified as sand (LRN-004)
- C089 (3.4) moderate-slip class about 75 % vs about 85 %; random hold-out one testbed (LRN-009)
- C090 (3.4) LRN-019 values 81.9 -> 43.0 % dry, 100 -> 30 % wet, 20 deg (numbers only; label see C082)
- C091 (3.4) TAIL: sandy sites, SLAM benchmark, GPLv3, no slip labels; Perseverance set release pending, no licence seen
- C092 (3.5) Spirit 15-20 % at 19 deg and 95 % at 16 deg (FLD-011/012)
- C093 (3.5) Spirit up to 50 % at 10-13 deg (FLD-010)
- C094 (3.5) Spirit over 100 % in places (FLD-009 125 %, FLD-013)
- C095 (3.5) Opportunity about 50 m wheel travel for 2 m track (FLD-001)
- C096 (3.5) Opportunity slip 98.9 to 99.5 % (FLD-002)
- C097 (3.5) ripple 30 cm high, trapped several weeks (FLD-040)
- C098 (3.5) Curiosity 3D slip above 70 % on shallow megaripples (FLD-018)
- C099 (3.5) Perseverance above 94 % at about 20 deg (FLD-025); limits above 50 % on 15-20 deg hill (FLD-024)
- C101 (3.5) Spirit sand-sized 4.0 % (0-5 deg) -> 9.9 % (5-10 deg) (FLD-015/016); fine-grain approaches 100 % at 10-15 deg (FLD-014); warning on FLD-015
- C102 (3.5) FLD-006 (90 % at 20 deg) and FLD-007 (25 deg limit) from a press release; FLD-006 excluded from anchors
- C103 (3.5) El-Dorado-II 35 kg, slip close to 0.9 at 4 deg, about 0.2 with grousers (FLD-030/031)
- C104 (3.5) 23 kg rover, 296 mm wheels, less than 10 mm per revolution at 30 deg (FLD-035)
- C105 (3.5) Scarab 400 kg: >90 % at 20 deg, no uphill progress at 25 deg (FLD-027/028)
- C106 (3.5) AMADEE-18 Husky in Dhofar, looser and softer sand than expected (FLD-042); no numbers for Rub al Khali etc.
- C107 (3.5) UAE-authored rig results slip 0-0.75, sinkage about 1-2 cm, lunar simulant
- C108 (3.6) SandBot about 2 cm/s hard-ground vs 8 cm/s soft-ground gait (LEG-001/002)
- C109 (3.6) about 20 cm/s vs 2 cm/s for a 5 % change in packing (LEG-003/004; 0.633 vs 0.600)
- C110 (3.6) 350 g hexapod lost about two thirds of speed 0 to 20-24 deg (15.7 -> 4.98 / 5.6 cm/s); LEG-007-009 = FLD-037/038
- C112 (3.6) all lab beds, none dune sand (for the quoted rows)
- C113 (3.6) slip 0.741 (D 116 mm) vs 0.056 (D 327 mm) at 12 deg; 0.471 vs 0.247 at 14 deg (LEG-017 to LEG-020); slope emulated by horizontal pull; slides
- C114 (3.6) grouser benefit saturates (LEG-021, 24 grousers)
- C115 (3.6) flexible metallic wheel more than twice drawbar pull at 1 m/s on olivine sand (LEG-022)
- C116 (3.6) tracks: no row entered; no same-vehicle wheel/leg/track comparison
- C117 (4) Bekker row: 24 to 52 % median error, worse on firm soil (SIM-025 to SIM-027), TM-029 geometry dependence, TM-018/019 quasi-static, fast (SIM-028)
- C118 (4) Scaling row: within about 3 % (TM-007); TM-020 DEM only
- C119 (4) DEM row: about 13 to 18 % (SIM-018 relative 17.7 %, SIM-021 13.5 %); gross traction 20 vs 31 % (SIM-019)
- C120 (4) DEM cost: SIM-016, SIM-024 hundreds-thousands; SIM-020 about 9 million; all derived
- C121 (4) Chrono row: validation mostly plots (SIM-001/002/009); unphysical SCM (SIM-005); BSD-3
- C123 (4) Learning-from-images row: AUROC 0.874 (LRN-010); LRN-004; LRN-003
- C124 (4) Proprioception row: LRN-009, LRN-015, LRN-024; moderate slip weakest; random hold-outs
- C125 (4) Hybrid row: NeSAM grass-to-sand completion 3/5 vs 1/5 (LRN-014, 5 trials)
- C126 (4) Empirical tables row: FLD-020, FLD-021, FLD-024
- C127 (4) 'No retrieved study compares these families on the same vehicle and same dune sand'
- C144 (5) GLO-30 licence cell: free with attribution (c) DLR/Airbus, EU/ESA; controlling text not read; commercial unverified; AWS COG tiles used
- C145 (5) GLO-30 accuracy: absolute <4 m LE90; relative <2 m (slope <=20 %), <4 m above
- C147 (5) GLO-90 3 arcsec about 90 m, audit only
- C149 (5) skadi: Joerd attribution; max slope 66.5 deg; mean +1.47 m, std 4.31 m vs GLO-30
- C152 (5) ALOS 'Good' <5 m is a quality flag, not validated accuracy
- C153 (5) FABDEM CC BY-NC-SA 4.0; corrects buildings and forests
- C154 (5) TanDEM-X 90 m: scientific use, registration
- C156 (5) ICESat-2 ATL08 100 m segments, GEDI 25 m footprints, GEDI 54N-54S, Earthdata login, none downloaded
- C159 (5) Sentinel-2 10/20/60 m, free; catalogue search only
- C160 (5) Landsat 8/9 30 m, no restrictions stated, not downloaded
- C161 (5) Maxar CC BY-NC 4.0, event-based, no Gulf event (55 collections)
- C162 (5) Planet NICFI terms not verified; Pleiades Neo commercial
- C163 (5) Abu Dhabi SDI: vector, licence field empty, no elevation layer
- C164 (5) Not found: open LiDAR/drone DEM of Liwa/Rub al Khali, grain-size/colour map, open sub-metre stereo
- C165 (5) Liwa dunes 50-80 m (Lorenz, M14); northern Rub al Khali 50-100 m (Lancaster, M17)
- C166 (5) 20 to 110 posts per wavelength at 30 m (arithmetic from 0.6-3.3 km)
- C168 (5) 10-25 m dunes, 200-300 m spacing: 7-10 posts at 30 m, 2-3 at 90 m
- C169 (5) 32 deg face run about 1.6 H; 50 m face spans 80 m = 2.7 posts
- C170 (5) consecutive posts >25 deg: median 2, p90 4, 45 % single post
- C171 (5) synthetic face test: full steepness at H >= 30 m (forward) / 50 m (central); 10 m reads 9-18, 20 m reads 18-26; 90 m, 50 m face 16-23 deg
- C172 (5) verdict and caveats (2010-2015 epoch; >20 m/yr Kuwait small dunes; no lidar truth)
- C173 (6) Rashid 1: about 10 kg, four wheels, 20 deg slopes, 10 cm rocks; Hakuto-R M1 failed 2023-04-26 JST; software altitude handling (UAE01, 02, 10, 11)
- C174 (6) Rashid 2 built, shipped to US, Blue Ghost Mission 2 far side; launch dates conflict (UAE14, 15, 17)
- C178 (6) Khalifa/MBRSC rig results slip 0-0.75, sinkage about 1-2 cm (0.010-0.0192 m), drawbar 5.2-24.1 N (UAE04/06)
- C180 (6) wheel and grouser studies UAE07/UAE08
- C181 (6) xRift debuted 20 Jan 2026; Space42 25 deg slope capability stated; no slip/sinkage data (UAE23-25)
- C182 (6) Hope orbiter (UAE19/20); Mars Science City article silent on rover testing (UAE21); ERC indoor (UAE26)
- C183 (6) 1963 archive item could not be read; Rashid 2 wheel design not found
- C184 (7.1) Rover slope error fell 25.9 -> 0.49 % only after tuning on same case (TM-023/024); DEM/SCM fits are calibrations (SIM-005/015/018)
- C185 (7.1) quasi-static outside envelope when fast (TM-018/019/021)
- C186 (7.1) hold-outs random/temporal/by sol (LRN-003/007/009/015); only held-out soil result is simulation (LRN-016)
- C187 (7.1) VO unreliable on featureless sand (FLD-041)
- C188 (7.2) shear collapse shown for foot on silica sand, 13 -> 36 mm at 35 deg (SIM-022/023)
- C189 (7.2) nearest grain sizes: Kuwaiti barchans 0.23 mm, Brazilian dune d50 about 0.2 mm
- C190 (7.2/7.3) 'none found' gap statements (slip-vs-slope dataset, open metre-scale DEM, slip-face detector unvalidated)
- C191 (8.1) tiles N23E053 and N22E054 (summary.json inputs)
- C192 (8.1) window extents, 17 x 41 km, reliefs 139 / 85 / 211 m
- C193 (8.1) central-difference 1.70 % vs Horn 1.45 % above 20 deg, about 15 % relative (14.7 %)
- C194 (8.1) model equations match slipmodel.py; Dijkstra via scipy.sparse.csgraph; 8-neighbour; ten OD pairs; seed 20261011
- C196 (8.1) LHS seeds 20261012/13; 256 draws; core windows 0.07 x 0.16 deg and coordinates
- C197 (8.1) runtime about 330 s (329.3)
- C198 (8.1) Table 8.1 parameters, ranges, status; phi basis list matches TM-015, TM-001, TM-003, TM-018, TM-022, TM-029
- C199 (8.2) Table 8.2 elevation statistics: all 9 rows x 7 columns match slope_stats.csv
- C200 (8.2) 0.57 % -> 0.093 % -> 0.0046 % above 25 deg in A-south
- C201 (8.3) critical slope 25.5 (25.46); entrapment about 28 (27.9); slip at 0-25 deg = 0.041, 0.077, 0.122, 0.182, 0.274, 0.466 (recomputed)
- C202 (8.3) route table: grid sizes, blocked 0.25/0.20/0.97 %, reach, cost ratio, length ratio, steepest uphill 20.4/18.1/23.1, 10 OD (routes_nominal.csv)
- C203 (8.3) 0.2-1 % blocked; cost ratio about 1.115; 8-neighbour about 6 % longer; flat-sand slip 0.04 -> factor 1.04
- C204 (8.3) reachability about 0.9999 (A: 0.999996, 0.999999; B: 0.99990)
- C205 (8.4) rank-regression R2 0.86 to 0.96 (0.856-0.969)
- C206 (8.4) Table 8.2 OAT: all blocked-share, ratio, cost-ratio, critical-uphill cells for A-south and B match sensitivity_oat.csv (recomputed x nominal)
- C207 (8.4) Table 8.3 Spearman: all 30 cells match summary.json to 2 decimals
- C208 (8.4) Table 8.4 percentiles: all 40 cells match the LHS csvs
- C209 (8.4) janosi_mean 8-fold (8.02x), critical slope 16.2; additive cross rule about 4-fold (3.92x)
- C210 (8.4) friction angle 28 -> 38 changes blocked share about 50-fold (50.0x from unrounded 0.008386 / 0.000168; printed 0.0084/0.0002 gives 42x); largest swing of any single parameter
- C211 (8.4) 60/90 m posting: 0.25x and 0.05x (A), 0.5x and 0.24x (B)
- C212 (8.4) item 3: phi -0.67 to -0.69, i0 +0.56 to +0.59, f_r +0.36 to +0.46; climbing limit 14.7-31.4 (A), 15.3-31.6 (B); phi differs by 10 deg
- C213 (8.4) item 4: i_max and noise correlations at most 0.27 and 0.11 in magnitude
- C214 (8.4) climbing limit and OAT ranking stable across A and B
- C215 (8.4) max and min figures 'A core 0 to 5 %' and 'B core 0.01 to 19.5 %' (numbers only; see C216)
- C217 (8.5) Table 8.5: slope, published slip, model nominal, envelope min-max, overlap flag for 13 rows match anchor_check.csv
- C218 (8.5) 13 points = 9 FLD + 4 LEG; envelope overlaps 11 of 13; nominal more than 0.5 away from six (FLD-012, 025, 027, 028, 030, LEG-017; gaps .75, .67, .63, .53, .78, .60); envelope misses FLD-030 and LEG-017
- C220 (8.5) FLD-030 'smooth-wheeled lab rover at 0.9 slip at 4 degrees'; LEG-017 '116 mm wheel at 0.741 at 12 degrees'
- C221 (8.6) tests/test_core.py has 14 tests
- C222 (8) SIMULATION ONLY banner; the section never labels a simulated number as field (checked all of section 8)
- C223 (9) vehicle 5-25 kg, wheels at least 150 mm; wheel diameter/width evidence LEG-017 to 020
- C224 (9) encoders and current 50 Hz, RTK, IMU, rut gauge three stations, tow load cell optional
- C225 (9) about 60 runs = 12 pilot + about 30 main + 9 cross-slope + 6 descent + 3 repeated pass
- C226 (9) n = (1.96 sigma / E)^2: sigma 0.10-0.15, E = 0.10 -> 3.8 to 8.6, i.e. 4 to 9 runs
- C227 (9) calibrate on 0-10 deg, record dated predictions for 15, 20, 25; baselines; adequacy rule 0.15 / 80 % / 3 deg is an assumption
- C228 (9) identifiability: 43-65 % at sigma 0.06 and 10-18 % at sigma 0.10 (calibrate to 10 deg; rows 0.43, 0.65; 0.18, 0.10); if calibration to 15 deg is included the ranges are 32-65 % and 7-18 %
- C229 (9) calibration needs bounds on f_r and i0 (plan section 7.1; CSV holds no bounded/unbounded column, so rests on the plan text)
- C230 (9) analysis script and log template exist; script tested on synthetic data only
- C231 (10) model map optimistic (30 m grid); cannot say which family is best; no head-to-head test
- C233 (10) thesis (TM-022 to TM-024), conference slides (LEG-017 to LEG-020), RoverDevKit re-evaluation (SIM-025 to SIM-027) are secondary
- C234 (10) Chrono, DEM, RFT reviewed but not run; GLO-30 terms from secondary pages; no LICENSE file in repository root
- C235 (10) verification by language-model agents using the same tools; UAE dates may conflict
- C236 (11) three agents, 30 random (seed 20261011) from 137 unflagged plus 7 flagged
- C237 (11) table counts 24/6/0 and 4/3/0; exact upper bounds 9.5 % and 34.8 %; Wilson 9.5-37.3 and 15.8-75.0 % (recomputed 9.51-37.31, 15.82-74.95)
- C238 (11) corrections in corrections.csv, old values in dedup_log.md; examples SIM-022 (section label), FLD-023 (vehicle), TM-021 (in-sample)
- C239 (11) 107 unflagged rows not re-checked; 0/30 compatible with true rate up to about 10 %
- C240 (11) duplicates removed (6 rows in dedup_log.md)

## Method notes and limits

- Evidence rows were read from research/evidence.csv (144 rows); per-topic notes were used only for claims not tied to a row, and are flagged where they use older row IDs.
- Recomputed: model slip at 0 to 25 degrees, critical angle 25.46, entrapment 27.9, route medians (cost and length ratios, steepest uphill), percentiles of all LHS outputs, OAT x-nominal ratios, 13 anchor overlaps, n = (1.96 sigma/E)^2, exact binomial bounds, Wilson intervals, sample counts (24+6 random, 4+3 flagged).
- Not checkable from the files: the claim that the study was run twice with identical output (C195), whether the protocol was literally written before searching (C038, C039), and the ALOS, Maxar and Wong-2008 details (C155, C157, C040).
- I did not check sections 12 and the appendices, as instructed. The Appendix A table is generated from evidence.csv; a spot check of rows quoted in the prose against the CSV found no discrepancy beyond those listed.

