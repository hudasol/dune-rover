# Verification log

Independent re-check by three separate subagents that re-fetched sources and had no access to the extraction notes.
Sample: 30 rows drawn at random (seed 20261011) from the 137 rows not flagged by the extractors, plus all 7 rows the extractors flagged as weakly supported.
Definitions: material error = wrong value, unit, metric meaning, validation type, vehicle/terrain or slope; minor error = number right but a label, section reference or descriptive detail wrong.

## random sample (n = 30)
- correct 24, minor 6, material 0, unverifiable 0
- material-error rate 0/30 = 0.0 % (exact 95 % upper bound 9.5 %)
- any-discrepancy rate 6/30 = 20.0 % (Wilson 95 % CI 9.5-37.3 %)

## flagged sample (n = 7)
- correct 4, minor 3, material 0, unverifiable 0
- material-error rate 0/7 = 0.0 % (exact 95 % upper bound 34.8 %)
- any-discrepancy rate 3/7 = 42.9 % (Wilson 95 % CI 15.8-75.0 %)

## What this does and does not show
- The 30-row sample is 21 % of the 144-row table; the other 107 unflagged rows were not individually re-checked.
- Zero material errors in 30 rows is compatible with a true material-error rate up to about 10 % (exact one-sided 95 % bound 9.5 %); it does not show the table is error-free.
- Minor errors (labels, sections) were common (see the any-discrepancy rate), so expect similar label slips in unchecked rows.
- Verifiers are language-model agents using the same search tools; they re-fetched the sources but may share blind spots with the extractors, for example on figure-only values.

## Row-level non-correct verdicts
- FLD-019 (random): minor_error: Location label slightly off: the sol 1703 drive is discussed in the flight data-set comparison (Fig 25) after the checkout tests, not in the checkout section itself; the drive was in the Traction-Control-enabled set.
- SIM-022 (random): minor_error: Section label wrong: Table 2 and the 12.98 mm value appear in Sec 2.3 (testing environment), just before Sec 3 Results, not in Sec 3.1.
- FLD-004 (flagged): minor_error: Terrain detail 'about 20 m diameter' is not in the cited Li 2008 paragraph (it comes from the Maimone paper); otherwise supported.
- FLD-023 (flagged): minor_error: Vehicle label imprecise: the 16 deg figure is a Perseverance ENav tilt limit based on worst-case drive performance of the Curiosity-class Scarecrow rover in Earth sand dunes (cited to Heverly), not a Curiosity measurement; value is a design limit, not a measured result.
- TM-018 (random): minor_error: Facility labelled ESA/DLR TROLL; paper describes TROLL as a DLR facility (authors affiliated with ESA/ESTEC).
- SIM-013 (flagged): minor_error: Equation 3 coefficients match the printed text, but the unit label 'slip ratio' describes the equation output not the coefficient; unit of alpha is not stated in the paper.
- FLD-039 (random): minor_error: Uphill vs downhill speed observation was made for SSTB-Lite only; Scarecrow was only described as tracking up a dune (motion capture) so the row attributes the observation to both vehicles.
- LRN-009 (random): minor_error: Dataset split (9235/3958) is in Sec. 4.1 (end of testbed/dataset text, Fig 3), not Sec. 4.2 (which is feature selection).
- TM-021 (random): minor_error: Source never calls the Toyoura sand 'dry' (word not found in the text); otherwise terrain fine. Also the '85% accuracy' is not defined in the paper and matches the average of the Table 1 adjusted R-square values (about 0.85), i.e. an in-sample goodness-of-fit, not a prediction error.
