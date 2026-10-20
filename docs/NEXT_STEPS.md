# Next steps for Huda (updated 2026-10-20)

Only what you still have to do. Commands run from the repository root in Git Bash; on Windows use `py` for `python3`.

## 1. Human spot checks

1. Spot check 3: for rows FLD-HV13-1, TM-IS09-3 and TM-TK5 in `research/evidence.csv`, compare value, unit, slope, validation type and page with the supplied PDFs in your local `sourced evidence` folder. Write `research/spot_check_3.md`, one line per row (id, what you checked, correct or wrong, the correction). Commit with the message `Spot check 3 of three supplementary rows`.
2. Inter rater check: open `research/spot_check_inter_rater.md`, check the 20 rows against their sources, and write one verdict per row (correct, minor_error, material_error or unverifiable) with a short note in `research/spot_check_inter_rater_ratings.csv`. Then run `python3 scripts/inter_rater_agreement.py` and commit both files and `research/inter_rater_agreement.md`.

## 2. Open questions (in `docs/QUESTIONS_FOR_HUDA.md`)

1. Question 7 (field rule, now with three evaluated options): answer (a), (b) or (c). Answer it before any field day.
2. Question 5 (slope tolerance of 1 degree): answer after looking at the dune.
3. Question 10 (a 10 m or finer survey of an Arabian dune): answer yes, no or not yet.

## 3. Read

1. `manuscript/MANUSCRIPT.md` (also `.pdf`), the full paper with every negative result.
2. `docs/REPORT.md` section 13, `docs/COMPLETENESS.md` and `docs/REVIEW_2026-10-20.md`.
3. `docs/PROPOSAL_ROBOTICS.md`, `docs/PROPOSAL_EDGE.md` and `docs/EXECUTIVE_BRIEF.md` (also `.pdf`). Note anything you disagree with in `docs/QUESTIONS_FOR_HUDA.md`.

## 4. Sources only you can supply

1. Photograph the chapter 2 table of Bekker and Janosi parameters for dry sand in Wong, *Theory of Ground Vehicles*, with the book title and page number visible, and send it in a message. Do not commit it.
2. Optional, if you have library access: Wong and Reece 1967, Sullivan et al. 2011 (JGR, rover wheel trenches) and Arvidson et al. 2017 (J. Field Robotics, Curiosity megaripples). Put the PDFs in your local `sourced evidence` folder, not in the repository.

## 5. First field pilot (PLANNED)

1. Before the day: `PYTHONPATH=src python3 scripts/analyze_field_runs.py --synthetic`. Print `docs/FIELD_DAY_CHECKLIST.md`.
2. Choose the bins in `docs/FIELD_VALIDATION_PLAN.md` section 4: the revised bins only if your answer to question 5 is yes, otherwise the original bins.
3. Pilot only, with a second person and a recovery vehicle present, slopes up to 10 degrees.
4. Log every run in a copy of `docs/field_log_template.csv` named `runs.csv`, including `bin_deg` and the soil columns.
5. After the 0, 5 and 10 degree runs and before any steeper run: `PYTHONPATH=src python3 scripts/make_ladder_predictions.py --design 2026-10-15 --calibrate runs.csv` (or `--design 2026-10-12`). Commit the new file in `docs/predictions/`.
6. After the day: `PYTHONPATH=src python3 scripts/analyze_field_runs.py runs.csv`. Commit `runs.csv` and the output. Append hits and misses to `docs/PREDICTIONS.md`.

Nothing has been sent to anyone. Do not send a proposal or the brief until you have read it and added a contact name.
