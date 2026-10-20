# Verification log

Every one of the 423 rows of the current evidence table has been re-checked against its source by a separate subagent that re-read the source and had no access to the extraction notes.
Phase 1 (2026-10-11): 30 rows drawn at random (seed 20261011) from the 137 unflagged rows, plus the 7 rows the extractors flagged. Phase 2 (2026-10-12): the other 107 rows, in four batches (batches 4 to 7).
Phase 3 (2026-10-15): the 26 rows read from the PDFs the author supplied (Yu 2024, Takehana 2025, Ishigami 2007, Ishigami 2009, Heverly 2013), in six batches (batches 8 to 13), one verifier per source block. Verifiers saw the claim fields only, not the notes or comparability warnings.
Phase 4 (2026-10-18): FLD-HV13-5, which mixed lab and field results, was split at the author's request into FLD-HV13-5a (lab, JPL Marsyard) and FLD-HV13-5b (field, Tecopa); one fresh verifier checked both (batch 14).
Phase 5 (2026-10-20): the rows added by the evidence expansion of 2026-10-20 (ids PLN, TM3, MOB, SND, DUN, MAP, ENV), each checked by a fresh verifier agent against the full text (batches 15 and up).
Two views are reported. 'ALL 170 ROWS' is the first check of the rows as extracted (FLD-HV13-5 counts with its material error). 'CURRENT TABLE' takes each row of the current table with its latest verdict (the two split rows with their phase 4 verdicts; FLD-HV13-5 is no longer in the table).
Definitions: material error = wrong value, unit, metric meaning, validation type, vehicle/terrain or slope; minor error = number right but a label, section reference or descriptive detail wrong.

## random sample, phase 1 (n=30 of 137 unflagged) (n = 30)
- correct 24, minor 6, material 0, unverifiable 0
- material error rate 0/30 = 0.0 % (exact 95 % upper bound 9.5 %)
- any discrepancy rate 6/30 = 20.0 % (Wilson 95 % CI 9.5 to 37.3 %)

## flagged sample, phase 1 (n = 7)
- correct 4, minor 3, material 0, unverifiable 0
- material error rate 0/7 = 0.0 % (exact 95 % upper bound 34.8 %)
- any discrepancy rate 3/7 = 42.9 % (Wilson 95 % CI 15.8 to 75.0 %)

## remaining rows, phase 2 full re-check (n = 107)
- correct 80, minor 21, material 6, unverifiable 0
- material error rate 6/107 = 5.6 % (Wilson 95 % CI 2.6 to 11.7 %)
- any discrepancy rate 27/107 = 25.2 % (Wilson 95 % CI 18.0 to 34.2 %)

## ALL 144 ROWS (n = 144)
- correct 108, minor 30, material 6, unverifiable 0
- material error rate 6/144 = 4.2 % (Wilson 95 % CI 1.9 to 8.8 %)
- any discrepancy rate 36/144 = 25.0 % (Wilson 95 % CI 18.6 to 32.7 %)

## supplementary rows from supplied PDFs, phase 3 (n = 26)
- correct 11, minor 12, material 3, unverifiable 0
- material error rate 3/26 = 11.5 % (Wilson 95 % CI 4.0 to 29.0 %)
- any discrepancy rate 15/26 = 57.7 % (Wilson 95 % CI 38.9 to 74.5 %)

## ALL 170 ROWS (n = 170)
- correct 119, minor 42, material 9, unverifiable 0
- material error rate 9/170 = 5.3 % (Wilson 95 % CI 2.8 to 9.8 %)
- any discrepancy rate 51/170 = 30.0 % (Wilson 95 % CI 23.6 to 37.3 %)

## split rows, phase 4 (n = 2)
- correct 1, minor 1, material 0, unverifiable 0
- material error rate 0/2 = 0.0 % (exact 95 % upper bound 77.6 %)
- any discrepancy rate 1/2 = 50.0 % (Wilson 95 % CI 9.5 to 90.5 %)

## new rows of the 2026-10-20 evidence expansion, phase 5 (n = 252)
- correct 190, minor 36, material 26, unverifiable 0
- material error rate 26/252 = 10.3 % (Wilson 95 % CI 7.1 to 14.7 %)
- any discrepancy rate 62/252 = 24.6 % (Wilson 95 % CI 19.7 to 30.3 %)

## CURRENT TABLE, latest verdict per row (n = 423)
- correct 310, minor 79, material 34, unverifiable 0
- material error rate 34/423 = 8.0 % (Wilson 95 % CI 5.8 to 11.0 %)
- any discrepancy rate 113/423 = 26.7 % (Wilson 95 % CI 22.7 to 31.1 %)

## CURRENT SUPPLEMENTARY ROWS, latest verdict per row (n = 27)
- correct 12, minor 13, material 2, unverifiable 0
- material error rate 2/27 = 7.4 % (Wilson 95 % CI 2.1 to 23.4 %)
- any discrepancy rate 15/27 = 55.6 % (Wilson 95 % CI 37.3 to 72.4 %)

## What this does and does not show
- The phase 1 random sample (0 material in 30, upper bound 9.5 %) understated the table wide rate: the 107 rows checked in phase 2 had 6 material errors (5.6 %). The bound held, but the point estimate was optimistic.
- Six of the original 144 rows had a material error before correction; all six are corrected in the table. The 'ALL 144' and 'ALL 170' rates are pre correction error rates of the extraction, not of the corrected table.
- Phase 3: 3 of the 26 supplementary rows had a material error, all on validation type (TM-TK5 and TM-IS07-5 labelled as comparisons although no simulation was compared; FLD-HV13-5 labelled field although two of its three numbers come from the JPL Marsyard). The values themselves were right in all 26 rows. Minor errors were mostly page and section labels and one terrain wording (sand called dry where the source does not say so, TM-YU1 to TM-YU4).
- Phase 3 used supplied PDFs read through a text layer; no page images could be rendered, so values read only from figures were checked against the text, not the plot.
- Minor errors (labels, sections, descriptive details) were common; the corrected table still carries the risk that a verifier shared a blind spot with the extractor.
- Verifiers are language model agents using the same search tools; they re read sources but may share blind spots with the extractors, for example on figure-only values. A human spot check of a few rows remains advisable.
- Material errors found in phase 2: wrong wheel count (LRN-017), validation type lab versus field (SIM-012, LRN-006), lab versus sim-vs-lab (LRN-019), a best case labelled as worst case (TM-020), an unreferenced capability statement presented as a measurement (FLD-029). SIM-013 was set to lab for consistency with SIM-012.

## Row level verdicts other than correct
- FLD-019 (phase 1): minor_error: Location label slightly off: the sol 1703 drive is discussed in the flight data-set comparison (Fig 25) after the checkout tests, not in the checkout section itself; the drive was in the Traction-Control-enabled set.
- SIM-022 (phase 1): minor_error: Section label wrong: Table 2 and the 12.98 mm value appear in Sec 2.3 (testing environment), just before Sec 3 Results, not in Sec 3.1.
- FLD-004 (phase 1): minor_error: Terrain detail 'about 20 m diameter' is not in the cited Li 2008 paragraph (it comes from the Maimone paper); otherwise supported.
- FLD-023 (phase 1): minor_error: Vehicle label imprecise: the 16 deg figure is a Perseverance ENav tilt limit based on worst-case drive performance of the Curiosity-class Scarecrow rover in Earth sand dunes (cited to Heverly), not a Curiosity measurement; value is a design limit, not a measured result.
- TM-IS07-1 (phase 3): minor_error: The wheel diameter sentence is on journal page 240, not page 239; Section 3.1 only begins on page 239.
- TM-IS07-2 (phase 3): minor_error: Section 4.1 with the rover dimensions is on journal page 241, not page 243.
- TM-IS07-4 (phase 3): minor_error: Table IV is printed on journal page 246, not page 245.
- TM-IS07-5 (phase 3): material_error: The source attributes the slip ratio and slip angle ranges to observation throughout the experiments, not to the simulation, and the range itself is not a simulation versus experiment comparison, so the validation type should be lab.
- FLD-HV13-1 (phase 3): minor_error: The unit field says the slip and slope units are not stated and only presumed, whereas Figure 12 and Eq. (4) establish slip in percent and slope in degrees for the fitted curve.
- FLD-HV13-5 (phase 3): material_error: The row labels all results as field although the 22 deg bedrock limit and the 75% slip at 20 deg cohesive soil result come only from the engineered Marsyard, and the bedrock slope range starts at flat rather than 5 deg.
- FLD-HV13-6 (phase 3): minor_error: The good agreement is between Curiosity visual odometry slip data and the Earth test data in Figure 17, not between Mars data and a prediction from the onboard polynomial slip model, so the vehicle, method and metric descriptions misattribute the comparison.
- FLD-HV13-5b (phase 4): minor_error: The terrain description attributes the flat to 28 degree slope range to the Tecopa runs alone, whereas Section 6.2 gives that range for all cohesive soil tests combined and Figure 10 shows the Tecopa data starting at roughly 9 degrees.
- MAP-010 (phase 5): minor_error: Value, threshold and metric are right, but the terrain detail (Mojave roads and lakebeds, 2004 and 2005 Grand Challenge courses) is not stated for this labelled reference dataset in the source.
- MAP-014 (phase 5): minor_error: Value right; the section is titled 'Development Process and Race' (subsection 10.3 The Race), not 'Results'.
- MAP-025 (phase 5): material_error: The RMSE values 24.4 (THEMIS) and 18.6 (GTS) are pooled cross validation errors over all nine sand sites, not values for Moosilauke Valley; terrain and slope (3.5) are attributed to a single site.
- MAP-028 (phase 5): minor_error: Value right; the soil field says no grain size is reported, but the paper states the river sand grain size used for the experiment was between 0.06 mm and 2 mm.
- MAP-029 (phase 5): material_error: The figures are quoted exactly from the abstract and Results, but Table 3 shows they are ratios, not percentage changes: 135.94% is 20.20/14.86 (35.94% longer, not 135.94% longer) and 44.72% is 22.40/50.09 (55.28% shorter, not 44.72% shorter). The slope range is also reported.
- MAP-032 (phase 5): material_error: Fig. 9 is a survey traverse concept illustration; '10-20% longer' is a stated expectation ('will be'), not a measured comparison of plan against rover odometry, so it is not field validation.
- MAP-035 (phase 5): material_error: Tests ran in an indoor Mars analogue terrain facility (constructed yard inside a museum), which the brief codes as lab, not field.
- MAP-036 (phase 5): material_error: Same indoor Mars analogue facility as MAP-035 (the row itself calls it a yard); constructed yard is lab under the brief, not field.
- ENV-001 (phase 5): minor_error: The cited Figure 1c and 1d show Ouster OS-1 data only (caption: experiment environment and Ouster OS-1 LIDAR data); the row attributes the car and truck obscuration result to both OS-1 and VLP-16. The paper only states generally that attenuation behaviours were observed for both sensors.
- ENV-004 (phase 5): minor_error: Value matches the abstract (p1: approximately 7 minutes versus over 27 minutes) but the cited Sec. IV B (p4) prints more than 26 minutes of continuous locomotion, not 27; the source is internally inconsistent and the row does not flag it. Also the proposed policy run ended because the battery was depleted, so the 27 min figure is a battery limit, not a thermal limit.
- ENV-010 (phase 5): minor_error: The parenthetical (early August) is not in the source. The paper gives only 'a typical day after the 3rd month'; the experiment started 22 April 2018, so 3 months is about 22 July, and the exact date of the typical day is never printed.
- MOB-008 (phase 5): minor_error: Values right. The estimate is drawn from the single wheel P20/W tabulation on level sand for soil conditions S1 and C2 (para. 28), not from vehicle slope tests or sloped bins; vehicle slope tests used pneumatic and SLRV wheels, not the original Bendix, Boeing-GM and Grumman wheels. Soil conditions S1 to C3 overstated.
- MOB-010 (phase 5): minor_error: Value right. The comparison in para. 40 is shown in Fig. 28 for soil condition C2 only (not C1 to C3), at 115 N wheel load, 8.80 kN/m2 inflation; slopes are reported (0, 15, 25 deg tested; maximum slope climbed tan 28 deg), not absent.
- MOB-019 (phase 5): minor_error: Content right but location wrong: the executive summary is on printed p. iii (p. ii is the STO boilerplate), and the bullet list of NRMM limitations is in Section 1.1 (printed p. 20), not Section 3; Section 3.1 only lists Identified limitations as a topic of the AVT-107 report. Cone index and rating cone index are not named in the limitation statements (only in the acronym list); the text says in-situ soil measurements.
- MOB-021 (phase 5): material_error: Vehicle labelled as wheeled only; the coarse grained drawbar pull set includes tracked vehicles (M113A1, M60), and the 17.9 percent is the weighted average for all vehicles.
- MOB-026 (phase 5): material_error: The 2.5 percent offset is stated for the towed coefficient curves (plate 25, para 53), not for the pull curves. For pull (para 52, plate 24) the report says only that the curves differ by a nearly constant amount and gives no number.
- MOB-042 (phase 5): material_error: The value is a site cone index (a property measurement), so validation type should be none, not field. The slope grades of approximately 10, 15 and 20 percent are for the prepared harrowed test lanes at Yuma Test Station (paras. 43 and 44), not for the dune area whose cone index is reported (para. 45 gives no slope). Terrain merges the two sites.
- MOB-043 (phase 5): material_error: Para. 9 states 'Pilot towing tests were conducted on natural and harrowed sand' under findings of the 15th Supplement; it does not mention coastal or river sites. The 15th Supplement test programme (AD0218089, checked in this batch) was at Yuma, a desert sand area, so 'coastal and river sites' is not supported and likely wrong.
- MOB-045 (phase 5): minor_error: Para. 6 lists findings of the 13th Supplement pilot study, whose tests were 'on quartz sands found on inland areas and beaches of the United States'; the row terrain (beach, tidal flat, coastal dune and river sands) describes a different test series. Finding and value are correct.
- MOB-046 (phase 5): minor_error: The 16 to 110 cone index range in para. 27 covers tests on the beach and unstabilized dunes together, not only the dune area or dune sand; para. 27 also reports slopes from level to 75%, so 'not reported' is wrong. Cape Cod values are correct.
- MOB-047 (phase 5): minor_error: The DTIC copy does not state the slope of the drawbar pull tests (details referred to reference [3]); 0 (level) is assumed, not printed. Also the journal, volume and year (Proc. IMechE Part D, 2018) do not appear in the DTIC copy and could not be confirmed. Values correct.
- MOB-048 (phase 5): minor_error: Slope of the MMP measurements is not stated in the DTIC copy; 0 (level) is assumed. Journal citation not confirmable from the DTIC copy. Value correct.
- MOB-053 (phase 5): minor_error: The statement is in Sec. 1.3 b, p. 3 only. Sec. 2.3.1 a (p. 6) describes the cone penetrometer and Table 5 is the normal critical layer table; neither mentions natural or unprepared lanes.
- MOB-057 (phase 5): minor_error: Wheel sizes sentence falls between the p. 81 and p. 83 folios, so on p. 82, not p. 83. The source does not use the words 'soil bin' (it says 'a uniform bed of dry Calne sand'). The conference name on the cover is OCR garbled and the year 1984 rests only on the DTIC receipt stamp 'DEC2 71984', so the source title detail is not confirmed.
- MOB-058 (phase 5): minor_error: 'Excellent agreement' refers to Figs. 3 to 8, described as 'examples of good simulation of pull coefficients' after the parameters e, p1, j0 and K were determined per test to yield good simulation; it is a fitted example statement, not a general validation. p. 35 holds only the Fig. 8 caption; the sentence ends on p. 36. Figs. 10 to 36 are Yuma sand (Section IX); Figs. 37 to 47 are Buckshot clay.
- MOB-059 (phase 5): minor_error: The text before Eq. 6 does not name Yuma sand; it says the limiting pressure 'may be estimated on the basis of inflation pressure for all tire sizes', and Section VIII draws on data from both Tables 1 (Yuma sand) and 2 (Buckshot clay). Restriction to Yuma sand is not supported. Equation coefficients correct.
- MOB-062 (phase 5): material_error: The value (cone index 80 of the test course) is a property measurement, so validation type should be none; the sim-vs-field comparison is the go/no go result, not this value.
- TM-018 (phase 1): minor_error: Facility labelled ESA/DLR TROLL; paper describes TROLL as a DLR facility (authors affiliated with ESA/ESTEC).
- SIM-013 (phase 1): minor_error: Equation 3 coefficients match the printed text, but the unit label 'slip ratio' describes the equation output not the coefficient; unit of alpha is not stated in the paper.
- PLN-003 (phase 5): minor_error: Method names rear HazCam images, but the X to A track analysis (Extended Data Fig. 4b) used a NaTeCam image taken on sol 11; Methods say trace unit width is estimated using NaTeCam or rear HazCam images. Value is right.
- PLN-007 (phase 5): minor_error: Method says measured from the navigation camera panorama, but the paper gives the dimensions with reference to Fig. 3b, an image taken on sol 50; the 360 deg NaTeCam panorama (Fig. 3a) was taken on sol 6, and the paper does not state the camera or how the dune was measured. Values are right.
- PLN-018 (phase 5): minor_error: Value is right, but two context labels are misattributed: the 28% SO3 measurement is from target John Wesley Powell on sol 1861 in the western valley, not the sol 1870 site; the 4 deg south tilt is stated for sol 2072, not the sol 1870 position (the sol 1870 drive placed Spirit about 9 m northwest of Troy).
- PLN-022 (phase 5): minor_error: Values are right, but the paper describes the inoperative right front wheel as pushed during forward drives (the 500 N case), not dragged; dragging applies to backward drives (75 N).
- PLN-033 (phase 5): material_error: Value 12% per step is correct, but the VO validation run in Sec. II.C names neither the vehicle nor the terrain or site, so Rocky8 and field are not supported; the 12% is a measurement precision of the VO ground truth against a total station (an instrument property), which fits validation_type none rather than field.
- PLN-035 (phase 5): minor_error: Value right; location says paragraph after Fig. 18, but on p. 1338 the sentence sits in the paragraph that follows Fig. 17 and precedes Fig. 18.
- PLN-040 (phase 5): minor_error: Value 8.3 to 16.5 deg is right, but the soil parameter context is wrong: the external friction angle was bounded with K_y = 13 mm and 40 mm, not the 15 to 45 mm range used for the outbound path predictions.
- PLN-051 (phase 5): minor_error: Values correct but the WES conclusions are on printed pp. 27 to 28 (PDF pp. 36 to 37), not pp. 21 to 22.
- PLN-060 (phase 5): minor_error: Value correct but the M2020 Rover Capability subsection belongs to Sec. 2 Problem Description, not Sec. 3 Overview of Analysis Method.
- PLN-064 (phase 5): material_error: Values correct, but no simulation is involved: kD^0.39 is obtained by inverting an analytic small wheel model on image derived field sinkage and compared with an analytic fit to field penetrometer data, which is field under the brief (analytic model compared with a measurement takes the measurement's type), not sim-vs-field. The comparison model is named Bernstein-Goriatchkin (BG) in the paper, not Bekker.
- PLN-065 (phase 5): minor_error: Value correct. The paper does not place this ripple at the Seitah region edge; it is on the return trip from the Delta base toward Enchanted Lake. The passage is in The Next Year of Driving subsection, not the Mobility Faults paragraph.
- PLN-066 (phase 5): minor_error: Value correct; passage is in The Next Year of Driving subsection, not the Mobility Faults paragraph.
- PLN-067 (phase 5): minor_error: Value correct; passage is in The Next Year of Driving subsection, not the Mobility Faults paragraph.
- PLN-068 (phase 5): minor_error: Value correct; VOSLIP EXCESSIVE is in the Unexpected Drive Faults list (and Table 2), not the Nominal Drive Faults list.
- SND-014 (phase 5): minor_error: The values (Q 86, F 9, n = 12) are from the Table 1 row SW Rub al Khali, which holds the 12 dune samples only; the 2 sand sheet samples are a separate row (Sand sheets, Q 83, F 9). The terrain field wrongly includes sand sheets.
- SND-020 (phase 5): material_error: Validation type is field, but the row is a borehole log property (dune sand thickness and depth to water table), which the brief classes as none. Values, unit and location are right.
- SND-023 (phase 5): material_error: Validation type is lab, but a direct shear friction angle is a sand property measurement, which the brief classes as none. Minor: the 60 by 60 mm shear box is not stated in this thesis (it appears in the author's 2017 CSCE paper; the thesis cites only ASTM D 5321), and the 1 percent silt loose dry density is printed 1.7, not 1.70.
- SND-024 (phase 5): material_error: Validation type is field, but nuclear gauge moisture and dry density of a backfill are property measurements, which the brief classes as none. Minor: the site is described in the thesis as a large housing project area in Jubail, not an industrial site, and the table sits in Section 5.2.1, not Section 5.4.
- SND-025 (phase 5): material_error: Validation type is lab, but the DCP index of sand prepared at set relative densities is a penetration resistance property measurement, which the brief classes as none. Minor: the 63 to 8 mm/blow sentence is on page CON33-5, not CON33-4, and Fig. 5 is on CON33-6.
- SND-026 (phase 5): material_error: Validation type is lab, but the equations are empirical regressions fitted to the same lab property data (direct shear friction angle against DCPI and Dr), with no independent validation; under the brief this is a property correlation or a value with no validation, so none. Equations and R2 values are right.
- SND-029 (phase 5): material_error: Validation type is field, but surface moisture content is a property measurement, which the brief classes as none. Minor: the source does not say the moisture was measured gravimetrically.
- SND-030 (phase 5): material_error: Validation type is field, but a wetting front depth after an infiltration test is a property measurement, which the brief classes as none. Values, unit and location are right.
- SND-031 (phase 5): minor_error: Values are right, but Table 1 gives the desert sample positions as windward side, leeward side and inside the dune (samples 13 and 14), not crest and horns; the source also does not say the sieving was dry.
- DUN-001 (phase 5): material_error: Validation type: the values are dune spacing and swale width summarised in a symposium report (a terrain property and review statement), so none, not field. Metric label has a stray word (wales).
- DUN-006 (phase 5): minor_error: Location: Figure 2.5 and its table are on printed thesis page 35 (PDF page 56), not page 36; the 36 is the header of the next page.
- DUN-007 (phase 5): minor_error: Location: the table is on printed thesis page 35 (PDF page 56), not page 36.
- DUN-008 (phase 5): minor_error: Location: the table is on printed thesis page 35 (PDF page 56), not page 36.
- DUN-009 (phase 5): material_error: Validation type: the heights are a study area description quoted from earlier work (Embabi and Ashour [10]), a property and review statement, so none, not field.
- DUN-018 (phase 5): minor_error: Terrain label: Fig. 96 uses Bahrain (panel B) as the example of a wide unimodal regime; narrow unimodal is panel A (Walvisbaai).
- DUN-020 (phase 5): minor_error: Slope: the paper gives no slope distribution for UAV Sample Area 1; the 0 to 15 deg statement (page 13, page 17) is about where ICESat-2 based DEM errors mostly occur across the hinterland.
- DUN-023 (phase 5): material_error: Validation type: a regional morphology description is a property and review statement, so none, not field. Also, Al Ain is not named in this passage (minor).
- DUN-024 (phase 5): material_error: Validation type: regional morphology description (property and review statement), so none, not field.
- DUN-025 (phase 5): material_error: Validation type: regional morphology description (property and review statement), so none, not field.
- DUN-026 (phase 5): material_error: Validation type: field measured barchan dimensions are a terrain property measurement, so none, not field.
- DUN-027 (phase 5): material_error: Validation type: field measured dune dimensions are a terrain property measurement, so none, not field. The note printed I is an OCR artefact; the printed page reads 1 and 6.
- FLD-039 (phase 1): minor_error: Uphill vs downhill speed observation was made for SSTB-Lite only; Scarecrow was only described as tracking up a dune (motion capture) so the row attributes the observation to both vehicles.
- LRN-009 (phase 1): minor_error: Dataset split (9235/3958) is in Sec. 4.1 (end of testbed/dataset text, Fig 3), not Sec. 4.2 (which is feature selection).
- TM-021 (phase 1): minor_error: Source never calls the Toyoura sand 'dry' (word not found in the text); otherwise terrain fine. Also the '85% accuracy' is not defined in the paper and matches the average of the Table 1 adjusted R-square values (about 0.85), i.e. an in-sample goodness-of-fit, not a prediction error.
- LEG-001 (phase 2): minor_error: Fig. 2c is in the Methods and Results section (Sec. 3), not Sec. 2 (Background and Review).
- LRN-017 (phase 2): material_error: The prototype is three-wheeled (two driving wheels and a follower), not four-wheel.
- TM-014 (phase 2): minor_error: Section label V-A is wrong (Sec. V is the Conclusion; Table I is discussed in Sec. IV-B) and the 51x38 cm, 20 cm deep box belongs to the plate parameter experiments, not the foot intrusion runs.
- SIM-005 (phase 2): minor_error: The second plate is larger (0.3 m radius), not smaller, and the 100 kg annulus case is only one of several loads in a separate test.
- SIM-008 (phase 2): minor_error: Sec. 4.2 and the timing figures are on p.20 of the arXiv version, not p.17.
- LRN-018 (phase 2): minor_error: Terrain list implies seven terrains; the paper uses six in total with the unknown mixture being the sixth (Fig. 10 caption).
- LRN-022 (phase 2): minor_error: Rupture detection results are in Sec. V-B, not IV-B, and Experiment 2 used a 280 x 56 cm trackway with crust over 300 micron sand, while the 300 x 80 cm damp construction sand box was Experiment 1.
- SIM-012 (phase 2): material_error: The runs were a real rover on an artificial 20 x 20 m, 0.3 m deep sand bed in a facility, which counts as a prepared bed (lab), not natural terrain, even though the paper calls them field tests.
- LRN-019 (phase 2): material_error: Table 6 reports only physical rover measurements on a prepared M90 slope (policy trained in sim, run zero-shot on hardware); no simulated values are compared to the lab numbers, so it is not sim-vs-lab.
- TM-008 (phase 2): minor_error: Section label is wrong: the text is in Results Sec. III-D, not IV-D (IV is Discussion).
- TM-009 (phase 2): minor_error: Section label is wrong: Sec. III-D, not IV-D.
- TM-010 (phase 2): minor_error: Section label is wrong: Sec. III-E, not IV-E.
- SIM-028 (phase 2): minor_error: terrain_description holds the compute platform, not a terrain; no terrain applies.
- LRN-014 (phase 2): minor_error: The warning says the physical dataset size was not located, but Sec IV-A states it.
- LEG-015 (phase 2): minor_error: 2.5 m/s is the top of the tested range (0.5-2.5), not a measured maximum, and the subsection sits under V. Results rather than an Experiments section.
- TM-015 (phase 2): minor_error: Table 2 lists model parameters only; the 1.96 N (SD 0.9) figure appears in the Sec. 4 text.
- SIM-015 (phase 2): minor_error: Calibration was not angle of repose only: FJS-1 cohesion was also tuned and bulk density matched; the 3230 particle density figure could not be found.
- SIM-030 (phase 2): minor_error: The flat-path simulation comparison refers only to Test Setup A; Setup B (EAC-1A, high grousers) was not part of it.
- TM-020 (phase 2): material_error: 0.015 is among the lowest RMSE in the Fig. 4a grid (tied with theta=-10, omega=2pi), not the worst case; the largest slip RMSE is 0.070.
- FLD-029 (phase 2): material_error: The 20-30 percent slip at 15 deg is an unreferenced capability statement in Sec 2.2.2, not a lab measurement on GRC-1, and not in Sec 2.3.
- LEG-016 (phase 2): minor_error: The claim that sand is the least efficient terrain is in Sec. 4.4.2 (Fig. 4.16 discussion), not in the thesis abstract.
- FLD-009 (phase 2): minor_error: The 125 percent sol 206 passage is in Section 5 (Using Visual Odometry on Mars), not Section 3.
- LRN-006 (phase 2): material_error: The JPL Mars Yard is an engineered outdoor analog test site, not natural terrain, so per the stated rule it is lab rather than field.
- FLD-032 (phase 2): minor_error: The 1 rpm wheel speed is not stated in the paper text, and sinkage was read from video, not still images.
- TM-022 (phase 2): minor_error: The thesis does not state that the sand is dry.
- TM-023 (phase 2): minor_error: The thesis does not state that the sand is dry.
- TM-024 (phase 2): minor_error: Weight reduction of 20 percent belongs to the dynamic tuning step, not force tuning (cohesion change), and dry is not stated.
- TM-YU1 (phase 3): minor_error: The terrain description calls the sand dry and places the force tests in the CMU Field Robotics Center testbed, but the paper never states the moisture state and names the Field Robotics Center testbed only for the trench experiments of Sec. 4.1, not for the gantry force tests of Sec. 3.2.
- TM-YU2 (phase 3): minor_error: The terrain description calls the sand dry and places the force tests in the CMU Field Robotics Center testbed, but the paper never states the moisture state and names the Field Robotics Center testbed only for the trench experiments of Sec. 4.1, not for the gantry force tests of Sec. 3.2.
- TM-YU3 (phase 3): minor_error: The terrain description calls the sand dry and places the force tests in the CMU Field Robotics Center testbed, but the paper never states the moisture state and names the Field Robotics Center testbed only for the trench experiments of Sec. 4.1, not for the gantry force tests of Sec. 3.2.
- TM-YU4 (phase 3): minor_error: The terrain description calls the sand dry and places the force tests in the CMU Field Robotics Center testbed, but the paper never states the moisture state and names the Field Robotics Center testbed only for the trench experiments of Sec. 4.1, not for the gantry force tests of Sec. 3.2.
- TM-YU5 (phase 3): minor_error: The sinkage range of 5 cm to 25 cm is copied from Sec. 3.1, but Table 3 and Fig. 6, which supply and illustrate the cited value, give the sinkages as 5, 15 and 25 mm, a conflict the row does not flag.
- TM-TK3 (phase 3): minor_error: Table 1 (testbed specifications) is on p. 2 of the article; not p. 3 as stated.
- TM-TK4 (phase 3): minor_error: The value is correct, but Fig. 5a is printed on p. 6, not p. 5 as the location implies.
- TM-TK5 (phase 3): material_error: The 34 degree angle of repose is a lab measurement for Toyoura and Tohoku silica sand, and this source reports no simulated angle of repose value or graph to compare with it, so sim-vs-lab is not supported; the location also mislabels where the sentence sits.
