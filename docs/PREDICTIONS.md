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
