# Next steps for Huda (updated 2026-10-28)

Only what you still have to do, in order. Commands run from the repository root in Git Bash; on Windows use `py` for `python3`.

## 0. Tag the two versions (two commands each)

The sessions could not push tags. On your computer, in the repository folder, run `git pull`, then:

1. Version 1.0 (the desk study, commit 7dfcc09): `git tag -a v1.0 7dfcc09 -m "Version 1.0 of the dune-rover desk study (2026-10-21). See docs/RELEASE_NOTES_v1.md."` and `git push origin v1.0`.
2. Version 1.1 (the Dune Rover Planner): check that the latest commit (`git log -1`) has a green CI check on GitHub, then `git tag -a v1.1 -m "Version 1.1: the Dune Rover Planner (2026-10-23). See docs/RELEASE_NOTES_v1.md."` and `git push origin v1.1`.

3. Version 1.2 (the benchmark and the conference paper, 2026-10-28): check that the latest commit has a green CI check, then `git tag -a v1.2 -m "Version 1.2: baselines, benchmark and conference paper (2026-10-28). See docs/RELEASE_NOTES_v1.md."` and `git push origin v1.2`.

## 0.25 The conference paper (`paper/paper.pdf`)

1. Read the paper in full and mark anything you disagree with; the text is in `paper/src/`, the numbers come from the result files, and `PYTHONPATH=src python3 scripts/build_paper.py` rebuilds it (needs LaTeX with the IEEEtran class; on Windows, MiKTeX installs it automatically).
2. Choose the venue (`docs/VENUES.md`): IROS 2027 first (deadline 1 March 2027, to confirm on the IROS 2027 site once it is up), ICAR 2027 second (21 March 2027). Do not submit the same paper to two venues at once.
3. Decide the affiliation line (now "Independent Researcher, United Arab Emirates"), and read the venue's rules on authorship, double blind review (IROS reviews are not double blind in recent years, but check the 2027 call), and any disclosure the venue requires; add what it asks for before submitting.
4. Ask one person with robotics or remote sensing experience to read it before submission (question 17).
5. Submission is yours to make; nothing has been sent anywhere.

## 0.5 Try the planner (ten minutes)

`pip install ".[projected]"`, then `dunerover demo --out demo_out` and open `demo_out/30m/report.html` and `demo_out/10m/report.html`; open `demo/web/dune_rover_planner.html` in a browser. To run it on your own area, download a Copernicus GLO-30 tile (free) and follow `docs/PLANNER.md`. After the field day, `dunerover vehicle calibrate` turns the run sheet into your rover's profile.

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

## 7. Technical items left open by the 2026-10-21 session (any helper can do these)

1. Key hand typed numbers by sentence, not only by token, and make the ledger recompute each value from a named file and column (final review items 8 and 9).
2. A Soil Contact Model run that stays numerically stable at 15 to 20 degrees (smaller time step, longer settling) before any statement about its extrapolation.

Nothing has been sent to anyone. Do not send a proposal or the brief until you have read it and added a contact name.
