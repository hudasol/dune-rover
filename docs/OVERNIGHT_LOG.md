# Overnight log

One line per commit batch: time (AST, 2026-10-15 unless stated), task, state.

- 19:33 start: pulled main (789b13e), read the context documents.
- 19:36 T1: six verifier agents launched on batches 8 to 13; stage 4 predictions committed before any output was read.
- 19:50 T1 done: 26 rows verified (11 correct, 12 minor, 3 material), merged to 170 rows, error rates regenerated, tests 43 passed, scans clean; P4 outcomes recorded (1 hit, 3 missed).
- 20:00 T2 done: stage 5 predictions committed first, comparisons run, outcomes 9 hit and 1 mixed, report section 8.8 added; tests 47 passed, scans clean.
- 20:15 T3 done: revised bins and expected ranges in a new dated file, power study re run; correct model now passes only 1.3 % (entrapment not reached), logged as question 4; tests 52 passed, scans clean.
- 20:21 T4 in progress (reviewer running; fixed build paths in six scripts and tool mentions in two notes); T5 done early: docs/PROPOSAL_EDGE.md generated from a template and linked; tests 52 passed, scans clean.
- 20:43 T4 done: 38 reviewer findings plus own scans in docs/REVIEW_2026-10-15.md, all fixed except 5 with reasons; CI now checks generated files and writing rules. T6: PDFs rebuilt, 55 tests pass, hygiene and secrets scans clean over full history, only allow listed PDFs tracked, no raw data.
- 21:08 T7 done (stretch): stage 7 pre registered, tiles fetched by the checksummed script (not committed), study run; map barely moves (4 hit, 2 missed); report section 8.9.
- 21:13 Morning report written; PDFs rebuilt; 55 tests pass; hygiene and secrets scans clean over full history.
- 21:15 CI writing check failure (institution name in the review document) fixed in b5c9d74; CI green; work stopped, all tasks done.
- 2026-10-18 11:49 F1 done: FLD-HV13-5 split into 5a (lab, correct) and 5b (field, minor, corrected); 171 rows; first check 9 of 170 material, current 8 of 171, supplementary 2 of 27. CI was red about 3 minutes (11:38 to 11:40) after a predictions commit without the report regenerated.
- 2026-10-18 12:17 F2 done: widened i0 (and i0 plus f_r) range sets added, phase 1, phase 2 and anchors re run beside the originals; stage 9: 6 hit, 2 badly missed (UNKNOWN A 30 m 33.9 % and 92.6 %); report sections 8.4, 8.7, 8.8, 8.9 updated from files.
- 2026-10-18 12:17 F3 done: amended entrapment rule pre registered (stated as made after the 1.3 % result) and re run; stage 10: 5 hit; correct model 74 % slip ok with entrapment not reached, wrong collapse model still adequate 53 %; question 7 to Huda.
- 2026-10-18 13:34 F4 done: licence sentence added; second review (23 findings) fixed or reasoned in docs/REVIEW_2026-10-18.md; stage 11 diagnostic added; the widened outputs re run with labelled footers (a first parallel attempt ran out of memory; three re run with fewer jobs).
- 2026-10-18 13:34 F5 done: NEXT_STEPS rewritten.
- 2026-10-18 13:34 F6 done: executive brief rebuilt from files, 2 page PDF; report PDF 72 pages. CI red once today, about 3 minutes (11:38 to 11:40).

## 2026-10-20 session (W0 to W9; times AST)

- 2026-10-20 12:17 W0 done: plan with success criteria committed first (6d5619d); local gate script; task list opened.
- 2026-10-20 12:43 W5 stage 12 done: detector and map against one metre lidar of Dumont, White Sands and Kelso (144796e to ee865d9): works at 5 and 10 m, fails at 30 m; Kelso window corrected before any metric (084f92a). CI red once, under a minute (144796e, report not regenerated; fixed by 658e4d7).
- 2026-10-20 12:50 W4 stage 14 done: Project Chrono single wheel sweep with published wheels and soils (e0befa1 to a6668e8); far less slip than Dumont; disagrees with the Bekker Wong family; FJS-1 mislabel corrected later.
- 2026-10-20 12:52 W6 stage 17 done: three planner policies against lidar truth (1704723 to a63419e); stage 18 rule options done (61e9cb4, fe18ea0).
- 2026-10-20 12:55 W3 stage 16 done: question 8 re run without immobile draws and Sobol indices (6cb4c9b, fe18ea0, 51e874e).
- 2026-10-20 13:00 W1 done: 323 rows extracted by five topic agents, all verified by 13 fresh verifier agents (batches 15 to 27), 322 merged, 1 dropped (382dc39 to a341cd8); table 494 rows. CI red once, about a minute (382dc39: tests pinned the old row count; fixed by 4cc3810).
- 2026-10-20 13:02 W2 done: 26 curves from 7 sources digitised reproducibly, 9 soil parameter sets, data catalogue (3b58074).
- 2026-10-20 13:05 W3 stage 15 three families done (b90eb64); posterior range set and map re run (b0a7c21); Bekker Wong family still running.
- 2026-10-20 13:16 W9 midpoint review done: 12 findings, fixed or reasoned in docs/REVIEW_2026-10-20.md (21d8e6f, 0920219, 17dde09, 20cbe58).
- 2026-10-20 13:16 W7 and W8 drafts committed: manuscript template and builder, report section 13, robotics proposal, brief and EDGE proposal rewritten, completeness table.
- 2026-10-20 13:25 W3 stage 15 done: the Bekker Wong family also fails the bar (held out 0.20, coverage 0.71) (cd11473); post hoc posterior without immobile draws (94e720c) and on Earth sand curves only (0920219).
- 2026-10-20 13:30 W4 discrete element check blocked: a Chrono DEM bed of 1860 spheres ran at more than 60 ms per step on this two core machine (a 3 s run would need over 30 minutes per slope); stopped within its budget, not run. Logged as a remaining gap in docs/COMPLETENESS.md.
- 2026-10-20 13:40 W9 final review done: 12 findings, fixed in a1d3fc0 and recorded in docs/REVIEW_2026-10-20.md (86d0e19).
- 2026-10-20 14:05 W5 stage 13 done: ERA5 wind for six sites (download slowed by rate limits); 4 of 6 sites within 45 deg (b73b595).
- 2026-10-20 14:08 W7, W8 and W9 closed: manuscript committed with a CI check (b8ecce1), report and brief PDFs rebuilt (dcf7b6b), morning report section written. CI green on the latest commit.

## 2026-10-21 session (W0 to W10; times Gulf Standard Time)

- 03:43 W0 plan committed (5347886); gate clean at the start. No Earthdata token set; SlideRule Earth, NASA CMR and the National Map API reachable; the NSIDC download server not.
- 03:45 Four helper agents launched (two curve agents, scaling law literature, field protocols) under a written brief (7e0863a).
- 03:5x The SlideRule client could not connect until it was told to use the machine's proxy settings (trust_env); then the machine restarted (out of memory while a test request, four agents and other work ran together). Agents were resumed from their saved transcripts; nothing committed was lost, but the lidar tiles of White Sands and Kelso had to be fetched again (checksums matched).
- 03:55 Stage 19 registered before any ICESat-2 data was saved (41f045d); the first push was held back by the gate because the report was stale, then pushed with its regeneration (12fc06b).
- 04:05 to 04:21 Curves (61a0e67), field kit (a01f9fe, c31d076, b1bc6b7, a52ec0e), stages 20 to 24 registered (2b73c13, b576727, 9b987a1, 90b40af, bb2607c), SCL rows merged after verification (e81444f).
- 04:33 to 04:51 Results of stages 23, 20, 22 and 24 (4205149, 9113adf, 910e3c2, 2c1d9f1). ROS 2 Jazzy installed through RoboStack and the smoke test run.
- 04:5x Midpoint review: 22 findings, 6 major (the closed loop gain was a restart effect; field ingest let every run into the rule; friction angle undefined; leave one study out folds shared a campaign; the stage 19 bar mixes effects). Fixes in edba2f9, 99fe166, e46bcc1, 890eb47 and af9db10 (the stage 19 clarification was written before any Arabian segment was scored).
- 05:14 Stage 19 results (f131cb8): the ICESat-2 method failed its lidar bar; Arabian numbers reported as indications.
- 05:15 Report section 14, brief, proposals, completeness (5.9 of 10), manuscript and number ledger (1669230 to 5c55160).
- 05:17 **CI red once** on 5c55160: the number ledger listed two tied typed numbers (0.2 and 0.20) in an order that depended on the Python hash seed, so CI saw it as stale. Fixed in 289e5b6 about two minutes later.
- The Bekker Wong rerun of stage 21 is slow (its calibration uses a slip grid solver over many more curves than on 2026-10-20); it was left running in the background.
- 05:26 Final review by a fresh reviewer received: 25 findings, 7 major (stage 21 outcomes left pending; "four families" where three were run; the stage 20 planner result missing from the manuscript; the ICESat-2 reading too strong; the closed loop compared with open loop instead of the retry control; three midpoint responses claimed text that did not exist; stage 24 possibly a numerical artefact).
- 05:26 to 05:47 Post hoc checks run for the majors: ICESat-2 base rate, noise screen and Kelso slope gap; SCM grid and speed checks at 15 to 20 degrees (the run is unstable there); the closed loop over five slip fields (no effect of replanning distinguishable from retry). The Bekker Wong rerun was stopped after 2 folds in the belief that 10 remained; it has 6 (only six studies give wheel size, width and load), so it was restarted unchanged at 05:49.
- 05:47 Corrections and responses committed (2acf60a, bd23370, db79aea, 50ba772); gate clean.
