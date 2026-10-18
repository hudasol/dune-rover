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
