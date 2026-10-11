# Predictions register

Rule: every prediction is written and committed **before** the run it concerns. Hits and misses are recorded afterwards in the same file, in the "Outcome" column, in a later commit. Nothing is edited after the fact except the Outcome column.

Evidence class for everything in this file: **SIMULATED-BY-ME** or process predictions. Field predictions (PLANNED) live in `docs/predictions/`.

## Stage 1: verification and retrieval (committed before agents were launched, 2026-10-11)

| ID | Prediction made before the run | Outcome |
|---|---|---|
| P1-1 | Among the 107 not yet re-checked evidence rows, the material error rate will be at most 5 %, and the any discrepancy rate (material plus minor) between 15 % and 30 %. | MIXED. Material rate 6/107 = 5.6 %, so the "at most 5 %" part MISSED slightly. Any discrepancy 27/107 = 25.2 %, inside 15 to 30 %: HIT. |
| P1-2 | Across all 144 rows the material error rate will be at most 4 %. | MISSED (marginally). Material rate across all 144 rows is 6/144 = 4.2 % (Wilson 95 % CI 1.9 to 8.8 %), above the 4 % predicted. |
| P1-3 | At least 4 of the 8 items under NOT_RETRIEVED (GLO-30 licence text, Wong table, Wong and Reece 1967, Ishigami 2007 and 2009, Yu et al. 2024, Heverly 2013, Takehana 2025) will stay inaccessible in full text from this sandbox. | HIT. Five items stayed unretrieved (Wong table, Wong and Reece 1967, Ishigami 2007 and 2009, Heverly 2013, Takehana 2025) and Yu et al. 2024 was abstract only: six of eight not read in full. |
| P1-4 | The SIM-013 unit question (unit of the slope term alpha) will be resolved by reading the paper, in favour of degrees being wrong or the printed coefficients being mistyped, because the printed term exceeds 1 at 18 degrees if alpha is in degrees. | PARTLY HIT. Not resolved by the source: the paper never states the unit of alpha. By arithmetic, radians would make the slope term negligible (about 0.0003 at 18 deg) and degrees give slip above 1 at 18 deg and 0.47 m/s. So "degrees wrong" is not supported and "mistyped" cannot be shown; the equation is also even in alpha and not dimensionally consistent as printed. Treated as unresolved at source, resolved as far as reading allows. |


## Stage 2: sub grid slip face detector, three class map, Monte Carlo (committed 2026-10-12 BEFORE any of this code was run)

Pre-specified design (fixed now so the outcome cannot tune it):

- Synthetic ensemble: straight-crested asymmetric dune profiles, stoss slope 6 to 20 deg (published ranges for barchan and transverse dunes, morphology rows PM01 to PM06), active slip face 29.5 to 32.5 deg (PM18, lidar), face height fraction of dune height 0.54 to 1.0 (PM08, small dunes 7 to 10 m; extended to 0.2 to 1.0 for tall dunes as an ASSUMPTION), apron below the face at the stoss slope (ASSUMPTION), height 5 to 120 m log uniform, random phase. The share of crests with an active face is not published (not found), so baseline pi = 1 (worst case) with pi = 0.3 and 0.6 as sensitivities.
- Truth in the synthetic ensemble: "an active face (slope of 28 deg or more) lies inside the cell footprint".
- Features per cell: Horn slope, curvature along the steepest direction, slope break (largest slope difference to the 8 neighbours), local relief in a 7 by 7 window. Model: logistic regression, trained per posting (30, 60, 90 m, box mean sampling; point sampling as a sensitivity).
- Map classes per cell. Monte Carlo: 256 Latin hypercube draws of (phi, f_r, i0, i_max) over the existing ranges, seeds 20261014 (area A), 20261015 (area B), 20261016 (area C). For each draw, a cell is "passable" if at least 4 of its 8 headings are passable. BLOCKED if passable in at most 5 % of draws; TRAVERSABLE if passable in at least 95 % of draws AND the face probability is below 0.20; UNKNOWN otherwise (two causes recorded: assumption sensitive, and sub grid face risk). The 0.20 threshold is a free choice and is swept in the coverage versus certainty curve.
- Areas: A_south_Liwa and B_RubAlKhali_megadunes as in phase 1, plus C, a Rub' al Khali linear dune window (tile N20E052, Saudi Arabia; the UAE tiles I hold show star and network dunes, not linear dunes).

| ID | Prediction made before the run | Outcome |
|---|---|---|
| S2-1 | Detector skill on held out synthetic profiles at 30 m: AUC between 0.70 and 0.90 (features see tall dunes but not low ones). Skill at 90 m is lower than at 30 m. | pending |
| S2-2 | The UNKNOWN share in A_south_Liwa at 30 m (pi = 1, baseline) is between 40 % and 80 %, and it rises with coarser posting (90 m above 60 m above 30 m). | pending |
| S2-3 | The BLOCKED class stays at or below 2 % of cells at 30 m in every area (phase 1 found 0.2 to 1 % of edges blocked). | pending |
| S2-4 | Robust to the four assumed parameters: at least 90 % of cells have a unanimous passable verdict (passable in at most 5 % or at least 95 % of draws) at 30 m. | pending |
| S2-5 | The UNKNOWN share in the linear dune window C at 30 m is at least 10 percentage points lower than in A_south_Liwa (smaller relief). | pending |
| S2-6 | Coverage versus certainty: demanding at most 5 % face probability on TRAVERSABLE cells leaves coverage (share of cells not UNKNOWN) below 30 % in A_south_Liwa at 30 m. | pending |
| S2-7 | Treating UNKNOWN as impassable, fewer than half of the origin destination pairs of phase 1 stay reachable in A_south_Liwa at 30 m (phase 1: nearly all reachable). | pending |
| S2-8 | Lowering the assumed share of crests with an active face from 1.0 to 0.3 lowers the A_south_Liwa UNKNOWN share at 30 m by less than 20 percentage points (the DEM features, not the prior, carry the result). | pending |
