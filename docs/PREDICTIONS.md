# Predictions register

Rule: every prediction is written and committed **before** the run it concerns. Hits and misses are recorded afterwards in the same file, in the "Outcome" column, in a later commit. Nothing is edited after the fact except the Outcome column.

Evidence class for everything in this file: **SIMULATED-BY-ME** or process predictions. Field predictions (PLANNED) live in `docs/predictions/`.

## Stage 1: verification and retrieval (committed before agents were launched, 2026-10-11)

| ID | Prediction made before the run | Outcome |
|---|---|---|
| P1-1 | Among the 107 not yet re-checked evidence rows, the material error rate will be at most 5 %, and the any discrepancy rate (material plus minor) between 15 % and 30 %. | pending |
| P1-2 | Across all 144 rows the material error rate will be at most 4 %. | pending |
| P1-3 | At least 4 of the 8 items under NOT_RETRIEVED (GLO-30 licence text, Wong table, Wong and Reece 1967, Ishigami 2007 and 2009, Yu et al. 2024, Heverly 2013, Takehana 2025) will stay inaccessible in full text from this sandbox. | pending |
| P1-4 | The SIM-013 unit question (unit of the slope term alpha) will be resolved by reading the paper, in favour of degrees being wrong or the printed coefficients being mistyped, because the printed term exceeds 1 at 18 degrees if alpha is in degrees. | pending |
