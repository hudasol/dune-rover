# Next steps for Huda (updated 2026-10-15)

Status labels: PUBLISHED, SIMULATED BY ME, PLANNED. Nothing below is a result. Commands run from the repository root in Git Bash (on Windows use `py` for `python3`).

## 1. Decisions (no vehicle needed)

1. Open `docs/QUESTIONS_FOR_HUDA.md` and write your answer under each of items 1 to 5. Commit with the message `Answer questions for Huda, 2026-10-xx`.
2. Item 4 (slope ladder against the adequacy rule) must be answered before any field day. If you choose option (a) or (b), ask for a new dated pre registration and a re run of `scripts/field_analysis_power.py --design 2026-10-15` before changing anything.
3. Item 1 (the i0 range): if yes, ask for a new dated prediction set first; do not edit `src/dunerover/slipmodel.py` by hand.

## 2. Checks you can do in an evening

1. **Spot check 3.** Open the supplied PDFs in `sourced evidence`. For rows FLD-HV13-1, TM-IS09-3 and TM-TK5 in `research/evidence.csv`, compare the value, unit, slope, validation type and page with the PDF. Write `research/spot_check_3.md` with one line per row: id, what you checked, correct or wrong, and the correction. Commit it.
2. **Read report section 8.8** (`docs/REPORT.md`) and the two figures in `results/anchors/figures/`. Note anything you disagree with in `docs/QUESTIONS_FOR_HUDA.md`.
3. **Read `docs/PROPOSAL_EDGE.md`.** Do not send it to anyone until you have read section 7 and filled in a contact name. Sending is your decision; nothing was sent.

## 3. Executive brief (reminder)

Build the executive brief: ask for it when you are ready. `docs/EXECUTIVE_BRIEF.md` is still the 2026-10-12 text with numbers refreshed from files.

## 4. First field experiment (PLANNED)

Route A, alone, now: pilot only, slopes up to 10 degrees, a second person and a recovery vehicle. Route B, later: `docs/AAU_FIELD_DAY_PROPOSAL.md` once Al Ain University access exists, or `docs/PROPOSAL_EDGE.md` if EDGE Group agrees to anything. No partnership exists with either.

1. Before the day: `PYTHONPATH=src python3 scripts/analyze_field_runs.py --synthetic` (shows the output format). Print `docs/FIELD_DAY_CHECKLIST.md`.
2. Choose the bins from `docs/FIELD_VALIDATION_PLAN.md` section 4 according to your answer to question 4.
3. Log every run in a copy of `docs/field_log_template.csv` named `runs.csv`, including `bin_deg` and the soil columns.
4. After the 0, 5 and 10 degree runs and before any steeper run: `PYTHONPATH=src python3 scripts/make_ladder_predictions.py --design 2026-10-15 --calibrate runs.csv` (use `--design 2026-10-12` if you keep the original bins). Commit the new file in `docs/predictions/` before continuing.
5. After the day: `PYTHONPATH=src python3 scripts/analyze_field_runs.py runs.csv`. Commit `runs.csv` and the output. Record hits and misses in `docs/PREDICTIONS.md` (append only).
6. Compare the per bin slip with the Dumont Dunes curve in `results/anchors/dumont_curve_comparison.csv` as a different, heavier vehicle on a different dune.

## 5. References still missing

| Reference | What to send |
|---|---|
| Wong, J. Y., *Theory of Ground Vehicles*, 4th ed. 2008 or 5th ed. 2022 (or *Terramechanics and Off-Road Vehicle Engineering*, 2nd ed. 2010) | A photograph of the printed chapter 2 table of Bekker and Janosi parameters for dry sand, with the book title and page visible. The three images supplied so far are not used. |
| Wong, J. Y. and Reece, A. R. (1967), Journal of Terramechanics 4(1), 81 to 98, https://doi.org/10.1016/0022-4898(67)90105-X | Optional: an interlibrary copy. |

Send them in a message; do not commit PDFs (the CI check rejects them).

## 6. Done (no action)

Licence decided (all rights reserved). Release v0.2.0 tagged on 2026-10-12. Spot check of five rows done on 2026-10-12. All 170 evidence rows re checked (`research/verification_log.md`). The five supplied papers (Ishigami 2007 and 2009, Heverly 2013, Yu 2024, Takehana 2025) are read, verified and merged. Anchor comparisons and the revised ladder are in report sections 8.8 and 9. A legged versus wheeled comparison was not run because it would need invented parameters.
