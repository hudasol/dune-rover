# Second rater pack (prepared 2026-10-21, not filled in)

Purpose: a second person checks the same 20 evidence rows that Huda checks in `research/spot_check_inter_rater.md`, so the agreement between two humans, and between each human and the verifier agents, can be measured. A single rater cannot show whether the verdicts are reproducible.

Who: one person who can read an engineering paper in English (for example a classmate in engineering or science). No subject knowledge of terramechanics is needed; the definitions are in the worksheet.

Steps for the second rater:
1. Read the definitions at the top of `WORKSHEET.md`.
2. For each of the 20 rows, open the source at the link, find the passage named under *where*, and compare the value, unit, slope, vehicle or terrain, and validation type with the source.
3. Write one verdict per row in `second_rater_ratings.csv`: `correct`, `minor_error`, `material_error` or `unverifiable`, with a short note (page or table where you looked).
4. Do not look at Huda's ratings, the verifier files (`research/verify_out_batch*.csv`) or `research/corrections.csv` before you finish.
5. Expected time: about 2 to 3 hours.

Afterwards, Huda runs `python3 scripts/second_rater_agreement.py`, which writes `AGREEMENT.md` (Cohen's kappa for each pair and Fleiss' kappa for the three raters).

Note: some rows were corrected after the verifier checked them; the worksheet shows each row as it is now, as for Huda's sheet.
