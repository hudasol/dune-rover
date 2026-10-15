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
