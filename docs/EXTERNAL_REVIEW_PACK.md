# External review pack (prepared 2026-10-21; nothing has been sent)

This page is for Huda to send, if she chooses, to one outside reviewer in terramechanics or field robotics before the manuscript is posted as a preprint. No one has been contacted. It contains a one page brief, the questions to ask, and a preprint readiness checklist.

## 1. One page brief for the reviewer

**Title.** Wheeled rover slip and traversability on dune sand: a pre registered desk study, with a field plan for Gulf dunes.

**Author.** Huda Mueen (sole author). Repository: `hudasol/dune-rover` (public to read, all rights reserved).

**What the study asks.** How much does a small wheeled robot slip on a dune slope, can that slip be predicted for a vehicle and sand it was not calibrated on, and how fine must a terrain map be to plan safely on Arabian dunes?

**What was done (desk only, no field data yet).**
- An evidence table of published results on wheeled, tracked and legged mobility on sand, each row re checked against the full text by a separate reader, with the measured extraction error rate reported.
- Published slip against slope curves digitised with calibration files; a random third redigitised independently.
- Several slip model families, calibrated on some studies and tested on a held out study, against a bar fixed in advance.
- An independent simulator (Project Chrono, Soil Contact Model), including a calibration on one published field curve and a prediction of the steeper slopes.
- A slip face detector and a three class traversability map scored against one metre lidar of North American dune fields, and against ICESat-2 laser profiles over the Liwa and Rub' al Khali dunes.
- Route planning policies scored against lidar truth, and a closed loop demonstration with online slip estimation and replanning (also run as ROS 2 nodes).
- Every test was registered before it was run (`docs/PREDICTIONS.md`); hits and misses are both recorded.

**Main findings so far.** See the abstract of `manuscript/MANUSCRIPT.md` and `docs/EXECUTIVE_BRIEF.md`. Every number there is traced in `docs/NUMBER_LEDGER.csv` to the script and input file that produced it.

**What is planned.** A slope ladder field experiment with one small rover on one UAE dune, with soil tests and a drone survey (`docs/FIELD_VALIDATION_PLAN.md`, `docs/OSF_PREREGISTRATION_DRAFT.md`).

**Time asked of the reviewer.** About two hours for the manuscript (14 pages) and, optionally, one hour for the field plan.

## 2. Questions to ask the reviewer

1. Is the leave one study out test of the slip model families a fair test of transfer between vehicles and sands? Would you change the bar (median held out error 0.15, coverage 0.80)?
2. Are the published curves comparable enough to pool (whole vehicles and single wheels, lunar simulants and quartz sand, real and emulated slopes)? Which would you exclude?
3. Is the Soil Contact Model calibration on the Dumont Dunes curve set up in a way you would trust, and is the conclusion drawn from it fair?
4. Is the lidar truth (cells with at least ten one metre posts at 28 degrees or more) a reasonable definition of a slip face cell? Would you score the map differently?
5. Is the ICESat-2 method (along track slope of short segments, apparent slope corrected with the wind derived face direction) sound, and is its validation against lidar sufficient?
6. For the field experiment: are the slope bins, run counts, soil tests and the pass or fail rule appropriate? What would make you trust the result?
7. Is any claim in the manuscript stronger than its evidence?
8. Which journal or conference would suit this work, and what is missing for it to be accepted there?

## 3. Preprint readiness checklist (TechRxiv or a similar free server)

| Item | Status on 2026-10-21 | Who |
|---|---|---|
| Manuscript generated from the result files, every number traced (`docs/NUMBER_LEDGER.csv`) | Done | |
| Every test registered before it was run; misses reported | Done | |
| Human spot check of the evidence table (spot check 3 and the 20 row blinded check) | Not done | Huda |
| Second human rater on the same 20 rows (`research/second_rater_pack/`) | Not done | Huda and a second rater |
| One outside review (this pack) | Not done | Huda |
| Author affiliation line decided (the manuscript must not name an institution without its agreement) | Open | Huda |
| Licence for the preprint chosen on the server (the repository stays all rights reserved; a preprint server requires a licence for the PDF) | Open | Huda |
| Figures readable in black and white print | Check | Huda |
| Statement that no field data exist yet and that all Arabian results are desk results | Done (abstract and limitations) | |
| No use of any organisation's name that implies endorsement | Done | |
| Field results, if a field day happens before submission, added through `scripts/ingest_field_day.py` | Planned | Huda |
