# Next steps for Huda (updated 2026-10-21)

Only what you still have to do, in order. Commands run from the repository root in Git Bash; on Windows use `py` for `python3`.

## 1. Human checks (needed before any preprint)

1. Spot check 3: for rows FLD-HV13-1, TM-IS09-3 and TM-TK5 in `research/evidence.csv`, compare value, unit, slope, validation type and page with the supplied PDFs in your local `sourced evidence` folder. Write `research/spot_check_3.md`, one line per row (id, what you checked, correct or wrong, the correction). Commit with the message `Spot check 3 of three supplementary rows`.
2. Inter rater check: open `research/spot_check_inter_rater.md`, check the 20 rows against their sources, write one verdict per row in `research/spot_check_inter_rater_ratings.csv`, run `python3 scripts/inter_rater_agreement.py`, and commit both files and `research/inter_rater_agreement.md`.
3. Second rater: give `research/second_rater_pack/` to one classmate (instructions in its README; about 2 to 3 hours). When both sheets are filled, run `python3 scripts/second_rater_agreement.py` and commit the result.

## 2. Decisions (in `docs/QUESTIONS_FOR_HUDA.md`)

1. Question 7 (field pass or fail rule): answer before any field day.
2. Question 13 (which friction angle the field model uses): confirm or change before any field day.
3. Question 15 (calibration bound of the slip scale): keep or widen, before any field day.
4. Question 11 (drone permission route) and question 10 (a 10 m or finer survey of the test dune).
5. Question 5 (slope tolerance of 1 degree): answer after looking at the dune.
6. Question 12 (preprint affiliation and licence): only when you decide to post.

## 3. Read

1. `manuscript/MANUSCRIPT.md` (also `.pdf`).
2. `docs/REPORT.md` sections 13 and 14, `docs/COMPLETENESS.md`, `docs/REVIEW_2026-10-21.md`.
3. `docs/PROPOSAL_ROBOTICS.md`, `docs/PROPOSAL_EDGE.md` and `docs/EXECUTIVE_BRIEF.md` (also `.pdf`). Note anything you disagree with in `docs/QUESTIONS_FOR_HUDA.md`.

## 4. Things only you can run or supply

1. Optional: run `notebooks/chrono_dem_gpu.ipynb` on a free Kaggle or Colab GPU, then `python3 scripts/ingest_chrono_dem.py` (question 14).
2. Photograph the chapter 2 table of Bekker and Janosi parameters for dry sand in Wong, *Theory of Ground Vehicles*, with the book title and page visible, and send it in a message. Do not commit it.
3. Optional: download Zhang, Townsend and Kamrin 2020 (Physical Review Fluids, open repository copy named in `research/phase4/scaling_laws_notes.md`) in a browser into your local `sourced evidence` folder; it holds the slope term of the scaling law that could not be retrieved here.

## 5. External review and preprint

1. If you choose, send `docs/EXTERNAL_REVIEW_PACK.md` with the manuscript to one terramechanics or field robotics researcher. Nothing has been sent.
2. Work through the checklist in that file before posting a preprint.

## 6. First field day (PLANNED)

1. Submit the preregistration yourself from `docs/OSF_PREREGISTRATION_DRAFT.md` (fill the bracketed fields first).
2. Print `docs/FIELD_DAY_CHECKLIST.md`, `docs/SAND_LAB_PROTOCOL.md` and, if a drone flight is allowed, `docs/DRONE_SURVEY_PROTOCOL.md`.
3. Copy the three sheets in `field_kit/` and fill them on the day (pilot only first, with a second person and a recovery vehicle, slopes up to 10 degrees).
4. After the 0, 5 and 10 degree runs and before any steeper run: `PYTHONPATH=src python3 scripts/make_ladder_predictions.py --design 2026-10-15 --calibrate runs.csv` (or `--design 2026-10-12`). Commit the new file in `docs/predictions/`.
5. After the day: `PYTHONPATH=src python3 scripts/ingest_field_day.py your_folder --label 2027-01-15_site1 --rebuild`. Commit the folder and `results/field_day/`. Append every hit and miss to `docs/PREDICTIONS.md`.

Nothing has been sent to anyone. Do not send a proposal or the brief until you have read it and added a contact name.
