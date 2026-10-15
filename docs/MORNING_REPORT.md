# Morning report, 2026-10-15 (work from 19:33 to about 21:15 AST)

All tasks T1 to T6 and the stretch task T7 are done. About 70 commits (68 before this report), each pushed to main; every push passed the tests, the hygiene check and the secrets scan, and the GitHub CI run passed. Nothing claims a partnership. Labels: PUBLISHED, SIMULATED BY ME, PLANNED.

## What changed (commits grouped by task)

- **T1, verification and merge of the 26 rows.** Predictions first (be6f86f); six independent verifier agents, one per source block, saw the claim fields only (5fba6ce); corrections ingested (d79b675); rows merged, 170 in total (95439e4); error rates for 170 and for the 26 (7731fd9); report and README regenerated (b379857); outcomes (d56552b).
- **T2, published anchors.** Predictions first (893b536); tally fix (a8c03e5); script and tests (af6260d); results in `results/anchors/` with two figures (7916c19); outcomes (a2148c3); report section 8.8 (f7d0384).
- **T3, field plan.** Predictions first (4a52267); analysis code, power option, new dated expected ranges file `docs/predictions/slope_ladder_predictions_2026-10-15.csv` (9afa5d3, c4a4f53, a49e43c, b408e0b); plan, checklist and log template (8f03bd1); power re run (90a37b3); outcomes (38d102e); conflict flagged (8593aad); report section 9 (05ca1cd). The 2026-10-12 prediction files were not edited.
- **T4, adversarial review.** A fresh reviewer reported 38 findings; with my own scans, all are listed in `docs/REVIEW_2026-10-15.md` with a fix commit or a reason. Main fixes: build paths in six scripts (161d729), tool names in notes (6d7a624), stale statements (d92d7cc), hyphens (dc856af, b4e120a), hidden outcome cells in PREDICTIONS (abfc934), report and plan corrections (39177b6, cd73368, 65ca428, 28a3b8e), traceable diagnostic (c2f1b6a), labels (0b63779), tests (a582677), CI checks for stale generated files and writing rules (90ab163, 9d6d0af).
- **T5, EDGE proposal.** `docs/PROPOSAL_EDGE.md`, generated from `docs/src/proposal_edge_template.md` (af40b43), linked (3ca400c), corrected after review (65ca428).
- **T6, housekeeping.** NEXT_STEPS rewritten (fe09189); licences recorded (6729114, 458ed35); PDFs rebuilt (628f790, rebuilt again at the end); tests 55 pass; only `docs/REPORT.pdf` and `docs/EXECUTIVE_BRIEF.pdf` are tracked PDFs; no raw data tracked.
- **T7, stretch.** Predictions first (3e9ed7d); script (226f571); results in `results/dumont_prior/` (60a4bea); outcomes (febf8fa); report section 8.9 (c323cae, f90b64d). The elevation tiles were downloaded with the checksummed script and are not committed.

## Verification

- All 170 rows: material errors 9 of 170 (5.3 %, Wilson 95 % CI 2.8 to 9.8 %); any discrepancy 51 of 170 (30.0 %).
- The 26 supplementary rows: material 3 of 26 (11.5 %, CI 4.0 to 29.0 %), all on validation type (TM-TK5, TM-IS07-5, FLD-HV13-5); any discrepancy 15 of 26 (57.7 %), mostly page labels. No value was wrong. All corrected; every row carries a verification note.
- Verifiers are language model agents reading the PDFs through a text layer; no page images could be rendered, so figure only values were checked against the text.

## Prediction hits and misses

- Stage 4 (verification): 1 hit, 3 missed. More errors than predicted.
- Stage 5 (anchors): 9 hit, 1 mixed. Weak evidence of foresight: hand arithmetic on the model equation informed several predictions.
- Stage 6 (revised ladder): 5 hit, 1 bad miss. A correct model passes the adequacy rule in 1.3 % of synthetic replicates (stage 3: 46 %).
- Stage 7 (Dumont prior): 4 hit, 2 missed. The map was predicted to react strongly; it barely moved.

## What the Dumont and Ishigami comparisons showed (including negative results)

Both are comparisons of unlike vehicles and soils, simulation only, model assumption dependent.
- Dumont Dunes: the published curve crosses 50 % slip at 12.6 degrees; the nominal model crosses it at 25.5 degrees. The Dumont curve lies above the model's 95th percentile from 10.7 to 17.9 degrees. The min to max envelope contains it only because the ranges are wide. No draw stays within 0.10 of it. A post hoc refit ends at the edges of the ranges (phi 28, i0 0.40) and still misses the S shape (RMSE 0.085).
- Ishigami 2009: with the Table I friction angle the model gives 0.01 to 0.20 slip on a 10 degree side slope, and 0.22 to 0.40 with the Table I shear modulus. The measured slip ratio was about 0.5. Neither variant reaches it.
- Verdict: the model predicts too little slip on sand slopes above about 10 degrees. This is a negative result for the model.
- Stage 7: using the Dumont fitted i0 (median 0.58) in the 30 m map moves UNKNOWN in area A only from 8.60 % to 8.95 %. The map is dominated by what the grid cannot see, not by the slip law.

## What is still unknown

- Any slip value for any vehicle on Arabian dune sand. No field data exist.
- Whether the slip face detector works on a real dune. It is validated against synthetic truth only.
- The soil parameters of the Dumont sand, and whether a small rover follows a Dumont shaped curve.
- How to reconcile the revised bins with the adequacy rule (question 4).
- Wong's dry sand table and Wong and Reece 1967 (not retrieved).
- The licence of pdftotext and of the Playwright Chromium build (not read; tools only, nothing distributed).

## Questions for Huda (copied from docs/QUESTIONS_FOR_HUDA.md)

1. **Slip scale range (simulation parameter, your decision).** Ishigami 2009 Table I gives a shear deformation modulus kx = 0.07 m for Toyoura sand with a 5.5 cm wheel. Under the model's definition (i0 = K / contact length) that implies i0 of at least 0.81, while the assumed range in `src/dunerover/slipmodel.py` is 0.05 to 0.40. Both anchors (report section 8.8) show the model predicting too little slip on sand slopes. Do you want the i0 range (and possibly the f_r range) widened and the phase 1 and phase 2 studies re run with a new dated prediction set? Note that the stage 7 study (report section 8.9) found the 30 m map barely changes with a larger i0, so the main effect of a wider range would be on the slope ladder predictions, not on the map. Answer yes or no; nothing was changed overnight.
2. **FLD-HV13-5 validation type.** The verifier found the row mixes JPL Marsyard results (lab) and the Tecopa result (field). I set the value to `lab and field`. Would you rather split it into two rows (one lab, one field)? Answer: keep, or split.
3. **Second human spot check.** Please check at least three of the 26 supplementary rows yourself against the PDFs (suggested: FLD-HV13-1, TM-IS09-3, TM-TK5), using `research/spot_check_2_worksheet.md` as the format, and record the result in a new file `research/spot_check_3.md`.
4. **Revised ladder against the adequacy rule (your decision before any field day).** With the 2026-10-15 bins (0 to 20 deg, 25 conditional) a correct model is called adequate in only 1.3 % of synthetic replicates, because entrapment is usually not reached and the rule requires an observed entrapment slope (`docs/PREDICTIONS.md`, L6-3; `results/field_kit/power_study_2026-10-15.csv`). Choose one: (a) keep the revised bins and amend the rule so the entrapment part is reported as "not reached" rather than failed, with a new dated pre registration and a re run of the power study; (b) keep the revised bins and run the 25 deg bin always, tethered; (c) go back to the original bins. Overnight nothing was changed to make the rule pass.
5. **Slope tolerance of 1 degree.** The revised bins need plus or minus 1 degree between 10 and 20 degrees. Is that achievable on the dune you have in mind with an RTK walk or a drone map? If not, the plan says to fall back to the original bins.
6. **Licence in the public history.** Commit ed7eedb (2026-10-12) added an MIT `LICENSE`, replaced by the all rights reserved notice in commit cb3370c the same day, so that snapshot of the history carries an MIT licence (its commit message calls it proposed). Whether it was public at the time depends on when it was pushed, which cannot be seen from the repository. History was not rewritten (it must not be without your decision). Answer: leave as is, or decide yourself whether to take advice on it.

## Exactly what Huda must do next

1. Answer questions 1 to 6 in `docs/QUESTIONS_FOR_HUDA.md` and commit. Answer question 4 before any field day.
2. Do spot check 3 (question 3) and commit `research/spot_check_3.md`.
3. Read report sections 8.8, 8.9 and 9 and the two figures in `results/anchors/figures/`.
4. Read `docs/PROPOSAL_EDGE.md`; add a contact name before sending it to anyone. Nothing was sent.
5. Follow `docs/NEXT_STEPS.md` sections 4 and 5 for the field steps and the two missing references.

## Remind Huda: build the executive brief

Build the executive brief: ask for it when you are ready. `docs/EXECUTIVE_BRIEF.md` still has the 2026-10-12 text, with numbers regenerated from files.
