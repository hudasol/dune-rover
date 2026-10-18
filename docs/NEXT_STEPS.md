# Next steps for Huda (updated 2026-10-18)

Only what you still have to do. Commands run from the repository root in Git Bash; on Windows use `py` for `python3`.

## 1. Spot check 3

1. Open the supplied PDFs in your local `sourced evidence` folder (not in the repository).
2. For rows FLD-HV13-1, TM-IS09-3 and TM-TK5 in `research/evidence.csv`, compare the value, unit, slope, validation type and page with the PDF.
3. Write `research/spot_check_3.md`, one line per row: id, what you checked, correct or wrong, the correction.
4. Commit it with the message `Spot check 3 of three supplementary rows`.

## 2. Open questions

1. Question 5 (slope tolerance of 1 degree): walk or survey the dune you have in mind and answer whether bins at plus or minus 1 degree between 10 and 20 degrees can be found. Write the answer under question 5 in `docs/QUESTIONS_FOR_HUDA.md` and commit.
2. Question 7 (the amended rule still passes a wrong model): answer (a), (b) or (c) under question 7 in `docs/QUESTIONS_FOR_HUDA.md` and commit. Answer it before any field day.
3. Question 8 (optional runs without immobile draws, and a power study with widened truths): answer yes or no under question 8 and commit.

## 3. Read the new sections

1. `docs/REPORT.md` sections 8.4, 8.7, 8.8 and 8.9 (widened slip scale range) and the end of section 9 (amended entrapment rule).
2. `docs/REVIEW_2026-10-18.md` (second review and what was not fixed).
3. `docs/EXECUTIVE_BRIEF.md` (also `.pdf`). Note anything you disagree with in `docs/QUESTIONS_FOR_HUDA.md`.

## 4. Wong table photograph

1. Photograph the printed chapter 2 table of Bekker and Janosi parameters for dry sand in Wong, *Theory of Ground Vehicles* (4th ed. 2008 or 5th ed. 2022) or *Terramechanics and Off-Road Vehicle Engineering* (2nd ed. 2010), with the book title and page number visible.
2. Send the photograph in a message. Do not commit it.

## 5. First field pilot (PLANNED)

1. Before the day: `PYTHONPATH=src python3 scripts/analyze_field_runs.py --synthetic`. Print `docs/FIELD_DAY_CHECKLIST.md`.
2. Choose the bins in `docs/FIELD_VALIDATION_PLAN.md` section 4: the revised bins only if your answer to question 5 is yes, otherwise the original bins.
3. Pilot only, alone or with one helper: slopes up to 10 degrees, a second person and a recovery vehicle present.
4. Log every run in a copy of `docs/field_log_template.csv` named `runs.csv`, including `bin_deg` and the soil columns.
5. After the 0, 5 and 10 degree runs and before any steeper run: `PYTHONPATH=src python3 scripts/make_ladder_predictions.py --design 2026-10-15 --calibrate runs.csv` (or `--design 2026-10-12` for the original bins). Commit the new file in `docs/predictions/`.
6. After the day: `PYTHONPATH=src python3 scripts/analyze_field_runs.py runs.csv`. Commit `runs.csv` and the output. Append hits and misses to `docs/PREDICTIONS.md`.

Do not send `docs/PROPOSAL_EDGE.md` or the brief to anyone until you have read them and added a contact name; nothing has been sent.
