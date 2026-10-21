# Morning report, 2026-10-15 (work from 19:33 to about 21:15 AST)

All tasks T1 to T6 and the stretch task T7 are done. About 70 commits (68 before this report), each pushed to main; every push passed the tests, the hygiene check and the secrets scan locally. **One lapse:** from c747820 to the morning report commit, the GitHub CI writing check (added during T4) failed because `docs/REVIEW_2026-10-15.md` named the excluded institution while describing the scans; I had run the local scans but not that new check before pushing. Fixed in b5c9d74; the name remains in the history of those commits, which was not rewritten. Nothing claims a partnership. Labels: PUBLISHED, SIMULATED BY ME, PLANNED.

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


---

# Morning report, 2026-10-18 (work from 11:34 to about 13:35 AST)

All six tasks F1 to F6 are done, applying Huda's answers of 2026-10-18. Every push went through the local gate (tests, hygiene, secrets, writing check and, from 11:40, a generated files check) and waited for CI. Labels: PUBLISHED, SIMULATED BY ME, PLANNED. Nothing claims a partnership, and nothing was sent to anyone.

**CI was red once:** about 3 minutes (11:38 to 11:40), after a predictions commit that did not regenerate the report, which embeds the prediction tally. Fixed by 2b552bf; the local gate now runs the generated files check before every push. Two other process slips, both fixed with new commits and not rewritten: commit eaf1a5e says it adds a test but did not (the test came in def9efc), and a parallel re run of four studies ran out of memory, so three were re run with fewer jobs at a time.

## What changed

- **F1, split of FLD-HV13-5.** Stage 8 pre registered (acd2c7a); split mechanism in `scripts/consolidate_evidence.py` (598afe1); FLD-HV13-5a (lab, Marsyard) and FLD-HV13-5b (field, Tecopa) written through `research/corrections.csv`, verified by a fresh agent (batch 14) and merged (bc43125); wording (ab9b3d2); outcomes (9598405).
- **F2, widened slip scale range.** Stage 9 pre registered (8a42986); named range sets with the original as default (`src/dunerover/slipmodel.py`, c3b022f); phase 1, phase 2 and anchors re run beside the originals (`results/widened_i0*`, `results/subgrid_widened_i0*`, `results/anchors_widened_i0*`); outcomes (aa7d649); report sections 0, 8.4, 8.7, 8.8, 8.9 from files (8a18a88, bd2b7d3).
- **F3, amended entrapment rule.** Stage 10 pre registered, stating it was made after the 1.3 % result (8d0bdcc); rule coded beside the old flag (1c7c7ab, 4fbd47e); power study re run (cd1637e, `results/field_kit/power_study_2026-10-15_rule_2026-10-18.csv`); outcomes (6a910d4) and question 7 (723f6cc).
- **F4, licence sentence and second review.** Sentence on the proposed MIT licence (720c433). A fresh reviewer reported 23 findings on the 2026-10-18 work; all are listed with fix commits or reasons in `docs/REVIEW_2026-10-18.md` (87dd778) (tally bug, undisclosed immobile draws as stage 11, unqualified insensitivity claims, b2 label, run labels, plan and proposals, README, and others). The five earlier open findings were rechecked: two are now resolved, three stay open with reasons.
- **F5.** `docs/NEXT_STEPS.md` rewritten with only what Huda must still do (f7fbdee).
- **F6.** `docs/EXECUTIVE_BRIEF.md` rebuilt from a new template (67c7916), Markdown and PDF, generated from files.

## Verification (new error rates)

- First check of the 170 rows as extracted: material errors 9 of 170 (5.3 %), unchanged.
- Current table, 171 rows, latest verdict per row: material 8 of 171 (4.7 %, Wilson 95 % CI 2.4 to 9.0 %); any discrepancy 51 of 171 (29.8 %).
- Current supplementary rows, 27: material 2 of 27 (7.4 %); any discrepancy 15 of 27 (55.6 %).
- The two split rows: FLD-HV13-5a correct; FLD-HV13-5b minor (slope range given for Tecopa alone), corrected.

## Prediction hits and misses

- Stage 8 (split): 3 hit; one for a different reason than predicted; P8-3 followed arithmetically from P8-1.
- Stage 9 (widened range): 6 hit on the anchors (informed by hand arithmetic, so weak), 2 badly missed on the map.
- Stage 10 (amended rule): 5 hit, but the adequate rates were already fixed by stage 6 files; only three clauses carried new information.
- Stage 11 (immobile draws): 3 hit, a reproduction of the reviewer's figures, not foresight.

## What the widened range did to the anchors and the map

All simulation only, model assumption dependent; anchors are comparisons of unlike vehicles and soils.
- Dumont: with nominal i0 0.81 the model crosses 50 % slip at 10.2 deg against 12.6 deg for the published curve; the nominal error changed sign rather than disappearing. The 5 to 95 % band now contains the whole curve, because it is very wide. A post hoc fit improves only from RMSE 0.085 to 0.071; the S shape is still missed.
- Ishigami 2009: the b1 envelope at 10 deg now reaches 0.59, so the measured 0.5 is inside; at 5 deg it reaches 0.49, so his model value of 0.6 is still outside.
- Map at 30 m, UNKNOWN: A 8.6 to 33.9 %, B 10.9 to 39.2 %, C 2.5 to 11.2 % with widened i0; with f_r also widened, 92.6, 90.1 and 97.4 %. In that second set 9 to 12 % of draws cannot move on level ground, which explains most of it. BLOCKED stays at or below 0.02 %.
- Reading: the original claim that the map is insensitive to the slip parameters holds only under the original ranges; once the ranges are wide, the map is mostly uncertain. Only a measured slip curve for the vehicle can narrow it.

## Field rule result

With the revised bins and the amended rule (synthetic data only): a correct model at sigma 0.03 is "slip within tolerance, entrapment not reached" in 74.3 %, adequate in 1.3 % and not adequate in 24.3 % of replicates; entrapment is not reached in 97.7 %. The Dumont shaped truth is never called adequate. **The wrong collapse model is still called adequate in 52.7 %, and the mildly wrong janosi_mean model in 65.3 % at sigma 0.10.** The rule was not tuned further; the decision is question 7.

## Still unknown

- Any slip value for any vehicle on Arabian dune sand; no field data exist.
- Whether the 1 degree slope tolerance of the revised bins can be met on a real dune (question 5, unanswered).
- The slip scale and resistance of the actual rover; the widened ranges are assumptions.
- Whether the slip face detector works on a real dune (validated against synthetic truth only).
- The Wong dry sand table and Wong and Reece 1967.

## Questions for Huda

Copied from `docs/QUESTIONS_FOR_HUDA.md`. Questions 1 to 4 and 6 were answered on 2026-10-18 and applied; question 3 is yours to do (spot check 3).

5. **Slope tolerance of 1 degree.** The revised bins need plus or minus 1 degree between 10 and 20 degrees. Is that achievable on the dune you have in mind with an RTK walk or a drone map? If not, the plan says to fall back to the original bins.

   Status: UNANSWERED on 2026-10-18; both bin designs stay documented and achievability is not claimed anywhere.

7. **Amended rule still passes a wrong model (your decision before any field day).** With the amended entrapment rule and the 2026-10-15 bins, a correct model is "slip within tolerance, entrapment not reached" in 74 % of synthetic replicates and the Dumont shaped truth is never passed, but the wrong collapse model is called adequate in 53 % at sigma 0.03, and the mildly wrong janosi_mean model in 65 % at sigma 0.10 (`results/field_kit/power_study_2026-10-15_rule_2026-10-18.csv`, `docs/PREDICTIONS.md` stage 10). The rule was not tuned after the run. Choose one: (a) accept it and treat pass or fail as secondary to predicted against observed slip, as the plan already says; (b) ask for a further pre registered change (for example a stricter slip tolerance or a test on the 20 to 25 deg runs alone), with its own power run; (c) something else.

8. **Widened range without immobile draws (optional).** In the widened_i0_fr set 9 to 12 % of draws cannot move on level ground (stage 11), which the original resistance basis excluded and which drives most of its 90 % UNKNOWN share. Do you want a new pre registered run that rejects such draws (and, separately, a power study whose synthetic truths and calibration bounds use the widened i0 range)? Answer yes or no for each.

## Exactly what Huda must do next

1. Spot check 3: rows FLD-HV13-1, TM-IS09-3, TM-TK5 against the PDFs; write and commit `research/spot_check_3.md`.
2. Answer questions 5, 7 and 8 in `docs/QUESTIONS_FOR_HUDA.md` and commit; question 7 before any field day.
3. Read report sections 8.4, 8.7, 8.8, 8.9 and the end of section 9, `docs/REVIEW_2026-10-18.md` and `docs/EXECUTIVE_BRIEF.md`.
4. Photograph the Wong chapter 2 dry sand table with title and page visible and send it in a message.
5. First field pilot as in `docs/NEXT_STEPS.md` section 5.


# Morning report, 2026-10-20 (work from 12:17 to about 14:10 AST)

All workstreams W0 to W9 are done except the discrete element check (blocked by run time) and the field data (not possible without Huda). Every main test was pre registered before its run (stages 12 to 18 in `docs/PREDICTIONS.md`); post hoc analyses are labelled. Labels: PUBLISHED, SIMULATED BY ME, PLANNED. Nothing was sent to anyone, and no agreement exists with anyone.

**CI:** red twice, each for about a minute: 144796e (a predictions commit without the regenerated report, fixed by 658e4d7) and 382dc39 (tests still pinned the old row count of 171, fixed by 4cc3810). The local gate now checks the committed tree in a clean worktree, including the manuscript. CI passes on the latest commit.

## What changed

- **Evidence base (W1):** five topic agents extracted 324 rows from 103 newly used sources under a written brief; 13 fresh verifier agents re checked every row against its full text; 323 merged, 1 dropped as unverifiable. The table now has **494 rows from 174 sources**. Search protocol and flow: `docs/SEARCH_PROTOCOL.md` (229 logged searches). Blinded 20 row sheet for your own check: `research/spot_check_inter_rater.md`.
- **Curves (W2):** 26 published curves (235 points) from 7 sources digitised reproducibly with uncertainty, 9 published soil parameter sets (`docs/DATA_CATALOG.md`).
- **Model families (W3):** four families behind one interface (`src/dunerover/models/`), calibrated with MCMC or a bootstrap and validated leave one study out; posterior range set; question 8; Sobol indices.
- **Independent simulation (W4):** Project Chrono single wheel sweep with published wheels and soils. Discrete element check not run (1860 spheres at more than 60 ms per step on two cores).
- **Real terrain (W5):** USGS one metre lidar of Dumont, White Sands and Kelso degraded to 5, 10 and 30 m; slip face direction against ERA5 wind at six sites.
- **Planning and field rule (W6):** three planner policies against lidar truth; three alternative field rules evaluated as options; wheeled, tracked and legged rows compared (published only).
- **Writing (W7, W8):** `manuscript/MANUSCRIPT.md` and `.pdf` (14 pages, every number from files, hand typed numbers justified and checked in CI), report section 13, `docs/PROPOSAL_ROBOTICS.md`, the brief (2 pages) and EDGE proposal rewritten, `docs/COMPLETENESS.md`.
- **Reviews (W9):** two adversarial reviews by fresh agents, 24 findings, all fixed or reasoned in `docs/REVIEW_2026-10-20.md`.

## Verification of the new rows

Material errors before correction: 30 of 323 (9.3 %, Wilson 95 % interval 6.6 to 12.9 %), mostly a wrong validation type, not a wrong value; any discrepancy 25.4 %. Whole current table, latest verdict per row: 38 of 494 (7.7 %). Every material error is corrected.

## Prediction hits and misses (stages 12 to 18)

22 hit, 19 missed. Stage 12 lidar 3 and 3; stage 13 wind 4 and 3; stage 14 Chrono 5 and 2; stage 15 models 4 and 3; stage 16 sensitivity 2 and 2; stage 17 planner 1 and 4; stage 18 rule options 3 and 2. Some hits were informed by quick checks, disclosed in each stage.

## Which model families survived

None. Median held out slip error (bar 0.15) and 90 % coverage: exponential 0.24 and 0.89, Mohr Coulomb 0.23 and 0.85, logistic 0.24 and 0.86, Bekker Wong 0.20 and 0.71 (on the 8 curves with wheel size and load). The empirical curve transfers as well as the lumped physics; Bekker Wong comes closest but its intervals are too narrow, and with the published Ishigami 2007 simulant set it does not reproduce that paper's own drawbar curve.

## What the posterior ranges did to the map

Posterior from 12 published curves: phi 36.9 (30.6 to 43.7) deg, f_r 0.13 (0.03 to 0.32), i0 0.63 (0.33 to 1.21). UNKNOWN at 30 m: 62.8 % (A), 44.3 % (B), 46.0 % (C), against 8.6, 10.9 and 2.5 % under the original assumed ranges; 25.1, 30.9 and 4.2 % if the about 5 % of draws that cannot move on level ground are rejected (post hoc). The Arabian UNKNOWN share is itself uncertain.

## What the real terrain test showed

The detector and map work much better at 10 m than at 30 m. At 30 m, 25.6 to 28.6 % of TRAVERSABLE cells contain a steep face and 36 to 73 % of face cells are called TRAVERSABLE; at 10 m 1.8 to 3.6 % and 7 to 20 %. Excluding slopes steeper than sand can stand leaves this unchanged. Slip faces follow the ERA5 drift direction within 45 deg at 4 of 6 sites, including Liwa (2 deg).

## Simulation cross check

Chrono with published soils: slip 0.21 at 12.5 deg for a Scarecrow sized wheel against about 0.49 on the Dumont curve (difference 0.35 root mean square); it differs from the Bekker Wong family with the same inputs by 0.44 to 0.75. Model form and implementation are a large source of uncertainty.

## Planner result

On 30 m maps no policy was safer than naive planning against lidar truth. At 10 m, on matched pairs (post hoc), the conservative policy failed less often than naive at White Sands and Kelso and refused most Dumont pairs.

## Completeness

5.5 out of 10 (`docs/COMPLETENESS.md`): complete as a desk study, not as an empirical study. Remaining gaps: field slip data for the project's vehicle, a 10 m or finer survey of an Arabian dune, the decision on the field rule, your spot checks, the Wong table and Wong and Reece 1967, a discrete element check, and an external human review.

## Questions for Huda

Question 7 (field rule, now with three evaluated options), question 5 (1 degree bins), question 9 (20 row human check) and question 10 (a 10 m survey of an Arabian dune) in `docs/QUESTIONS_FOR_HUDA.md`.

## Exactly what Huda must do next

Follow `docs/NEXT_STEPS.md`: the two spot checks, questions 7, 5 and 10, read the manuscript and the proposals, send the Wong table photograph, then the field pilot.

# Morning report, 2026-10-21 (work from 03:37 to about 08:45 Gulf Standard Time)

All workstreams W0 to W10 of `docs/PLAN_2026-10-21.md` were carried out; what is still missing (field data, a fine Arabian survey, the human checks, the discrete element run) is in the completeness section below. Every main test was registered in `docs/PREDICTIONS.md` (stages 19 to 24) and pushed before it ran; analyses decided after a result are labelled post hoc. Labels: PUBLISHED, SIMULATED BY ME, PLANNED. Nothing was sent to anyone, no account was opened, and no agreement exists with anyone. About 80 commits, each pushed to main after the local gate.

**CI:** red once, on 5c55160, for about two minutes: the number ledger ordered two tied typed numbers (0.2 and 0.20) by the Python hash seed, so CI saw it as stale; fixed in 289e5b6. CI passes on the latest commit. **Other things that went wrong:** the machine restarted once early on (out of memory with four helper agents and a test request running together); the stage 21 Bekker Wong run was stopped by mistake after 2 of its 6 folds and restarted (it then completed at 08:16); the first reading of the ICESat-2 and closed loop results was too strong and was corrected after the final review; the 20 m ICESat-2 fetch needed a restart and the analysis a memory fix.

## What changed

- **Evidence (W3):** 16 scaling law rows (SCL) from the granular scaling literature, verified (no material error, 3 location labels corrected); the table has 510 rows from 176 sources.
- **Curves (W3):** 36 further slip against slope curves from 7 new sources with calibration files; a second reading of a random third measures repeatability (largest single point difference 0.30 slip, on overlapping markers).
- **Model families (W4, stages 21 and 22):** the stage 15 validation repeated on 49 held out curves from 10 studies, plus two families built on the scaling laws; post hoc regrouping by test campaign and by laboratory.
- **ICESat-2 (W1, stage 19):** method checked against lidar at White Sands and Kelso, then applied to Liwa and two Rub' al Khali windows, with 20 m segments as the registered sensitivity and post hoc base rate and noise screens.
- **More lidar fields (W2, stage 20):** Great Sand Dunes, Algodones and Little Sahara added (six fields in all), detector, map and planner unchanged.
- **Simulation (W5, stage 24):** Chrono's Soil Contact Model calibrated on the Dumont curve up to 12.5 degrees; CPU timing of the discrete element model; a GPU notebook for a free GPU, not run.
- **Closed loop (W7, stage 23):** online slip estimation and replanning against a modelled rover, in Python and as ROS 2 nodes (RoboStack Jazzy), with a post hoc fixed field version and a five field repeat against a retry control.
- **Field kit (W8):** data sheets, `scripts/ingest_field_day.py` (tested on a synthetic fixture only), preregistration draft, drone survey and sand test protocols, second rater pack.
- **Traceability and release (W6):** `docs/NUMBER_LEDGER.csv` (every number of the manuscript, brief and proposals with its producer and the SHA-256 of its inputs, checked in CI), `docs/PROVENANCE.md` with a figure, `CITATION.cff`, a clean clone rebuild check, `docs/RELEASE_NOTES_v1.md`; the annotated tag v1.0 could not be pushed from the session (the connection allows branch pushes only, and the GitHub API refused tag creation), so it is the first item of `docs/NEXT_STEPS.md`.
- **Writing (W9, W10):** manuscript, report section 14, brief, both proposals (readiness levels, work packages with weeks, risk register), completeness table and `docs/EXTERNAL_REVIEW_PACK.md`; a midpoint review (22 findings) and a final review (25 findings), all answered in `docs/REVIEW_2026-10-21.md`.

## Prediction hits and misses (stages 19 to 24)

22 hit, 10 missed, none pending. Stage 19 ICESat-2 6 and 2; stage 20 more lidar fields 5 and 2; stage 21 replication 2 and 3 (all three misses from the Bekker Wong family, which did much worse on the expanded set); stage 22 scaling law families 3 and 1; stage 23 closed loop 4 and 1 (C23-2 measured a restart effect); stage 24 Chrono calibration 2 and 1 (S24-2 a hit on a numerically unstable run). Some outcomes were informed by quick checks disclosed in each stage.

## The three findings that matter most

1. **No slip model transfers between studies, even with twice the curves.** On 49 held out curves from 10 studies, three families reached median held out errors of 0.20 to 0.22 slip (bar 0.15); grouping shared campaigns or one laboratory did not change this; the Bekker Wong family, the only one using wheel size and load, fell to 0.41 on its 33 curves, and the scaling law families did worse than a plain curve (0.31 to 0.34). A slip curve measured for the actual vehicle on the actual sand remains the first need.
2. **A 30 m map misses steep faces on all six lidar fields** (36 to 80 % of face cells called TRAVERSABLE at 30 m, 7 to 33 % at 10 m); on three new fields a conservative planner was only somewhat safer than naive at 30 m. Over Arabian dunes, ICESat-2 is consistent with this but cannot confirm it: the 10 m method failed its lidar bar, about half of the steep segments are isolated (likely noise), and after a screen 29 to 52 % of the steep crossings fall in TRAVERSABLE cells against more than 90 % of all segments.
3. **Two promising results did not survive checking.** Replanning on an online slip estimate showed no effect distinguishable from a stop and retry control over five slip fields, and the Chrono model calibrated on Dumont became numerically unstable above 12.5 degrees, so it gave no usable steep slope prediction.

## Completeness

5.9 out of 10 (`docs/COMPLETENESS.md`; 5.5 on 2026-10-20). Complete as a desk study; not complete as an empirical study, because no field slip data for the project's vehicle and no fine survey of an Arabian dune exist.

## Questions for Huda

Questions 5, 7 and 10 are still open (the defaults were kept); new questions 11 to 16 in `docs/QUESTIONS_FOR_HUDA.md` (drone permission route, preprint affiliation and licence, the friction angle used by the field model, the GPU notebook, the slip scale bound, and whether to keep the closed loop work package).

## Exactly what Huda must do next

Follow `docs/NEXT_STEPS.md`: (0) push the v1.0 tag (one command, section 0); (1) spot check 3 and the 20 row inter rater check; (2) answer questions 7, 13 and 15 before any field day; (3) read the manuscript, the robotics proposal and the brief; (4) start the drone permission route (question 11) or choose a site where a survey is allowed; (5) give the second rater pack to one classmate.
