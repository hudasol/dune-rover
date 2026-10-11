# Verification log

Every one of the 144 evidence rows has now been re-checked against its source by a separate subagent that re-fetched the source and had no access to the extraction notes.
Phase 1 (2026-10-11): 30 rows drawn at random (seed 20261011) from the 137 unflagged rows, plus the 7 rows the extractors flagged. Phase 2 (2026-10-12): the other 107 rows, in four batches (batches 4 to 7).
Definitions: material error = wrong value, unit, metric meaning, validation type, vehicle/terrain or slope; minor error = number right but a label, section reference or descriptive detail wrong.

## random sample, phase 1 (n=30 of 137 unflagged) (n = 30)
- correct 24, minor 6, material 0, unverifiable 0
- material-error rate 0/30 = 0.0 % (exact 95 % upper bound 9.5 %)
- any-discrepancy rate 6/30 = 20.0 % (Wilson 95 % CI 9.5 to 37.3 %)

## flagged sample, phase 1 (n = 7)
- correct 4, minor 3, material 0, unverifiable 0
- material-error rate 0/7 = 0.0 % (exact 95 % upper bound 34.8 %)
- any-discrepancy rate 3/7 = 42.9 % (Wilson 95 % CI 15.8 to 75.0 %)

## remaining rows, phase 2 full re-check (n = 107)
- correct 80, minor 21, material 6, unverifiable 0
- material-error rate 6/107 = 5.6 % (Wilson 95 % CI 2.6 to 11.7 %)
- any-discrepancy rate 27/107 = 25.2 % (Wilson 95 % CI 18.0 to 34.2 %)

## ALL 144 ROWS (n = 144)
- correct 108, minor 30, material 6, unverifiable 0
- material-error rate 6/144 = 4.2 % (Wilson 95 % CI 1.9 to 8.8 %)
- any-discrepancy rate 36/144 = 25.0 % (Wilson 95 % CI 18.6 to 32.7 %)

## What this does and does not show
- The phase 1 random sample (0 material in 30, upper bound 9.5 %) understated the table-wide rate: the 107 rows checked in phase 2 had 6 material errors (5.6 %). The bound held, but the point estimate was optimistic.
- Six of 144 rows had a material error before correction; all six are corrected in the table. The 'ALL 144' rate is the pre-correction error rate of the extraction, not of the corrected table.
- Minor errors (labels, sections, descriptive details) were common; the corrected table still carries the risk that a verifier shared a blind spot with the extractor.
- Verifiers are language-model agents using the same search tools; they re-fetched sources but may share blind spots with the extractors, for example on figure-only values. A human spot check of a few rows remains advisable.
- Material errors found in phase 2: wrong wheel count (LRN-017), validation type lab versus field (SIM-012, LRN-006), lab versus sim-vs-lab (LRN-019), a best case labelled as worst case (TM-020), an unreferenced capability statement presented as a measurement (FLD-029). SIM-013 was set to lab for consistency with SIM-012.

## Row-level non-correct verdicts
- FLD-019 (phase 1): minor_error: Location label slightly off: the sol 1703 drive is discussed in the flight data-set comparison (Fig 25) after the checkout tests, not in the checkout section itself; the drive was in the Traction-Control-enabled set.
- SIM-022 (phase 1): minor_error: Section label wrong: Table 2 and the 12.98 mm value appear in Sec 2.3 (testing environment), just before Sec 3 Results, not in Sec 3.1.
- FLD-004 (phase 1): minor_error: Terrain detail 'about 20 m diameter' is not in the cited Li 2008 paragraph (it comes from the Maimone paper); otherwise supported.
- FLD-023 (phase 1): minor_error: Vehicle label imprecise: the 16 deg figure is a Perseverance ENav tilt limit based on worst-case drive performance of the Curiosity-class Scarecrow rover in Earth sand dunes (cited to Heverly), not a Curiosity measurement; value is a design limit, not a measured result.
- TM-018 (phase 1): minor_error: Facility labelled ESA/DLR TROLL; paper describes TROLL as a DLR facility (authors affiliated with ESA/ESTEC).
- SIM-013 (phase 1): minor_error: Equation 3 coefficients match the printed text, but the unit label 'slip ratio' describes the equation output not the coefficient; unit of alpha is not stated in the paper.
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
