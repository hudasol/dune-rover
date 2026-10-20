# Brief for curve agents, phase 4 (2026-10-21)

This brief is the common instruction set for every agent that adds published slip curves in phase 4. It is kept in the repository so the protocol can be audited. The phase 3 rules in `research/phase3/AGENT_BRIEF.md` (full text only, live DOI check, free access, text rules) apply unchanged; read that file first.

## What a curve is

A curve is a set of published points of wheel or vehicle **slip (or slip ratio, or travel reduction) against slope** on sand or sand like granular soil, from one figure or one table of one source. Slope may be a real tilt (tilt bed, constructed slope, natural dune or hill) or a slope emulated by a drawbar pull equal to the downslope weight component, if the source says so. Curves of slip against drawbar pull without a stated slope equivalence are recorded in the search log as "candidate, pull only" and not digitised.

Priority: (1) natural dune or field data on Earth sand; (2) whole vehicle tilt bed or constructed slope tests in dry sand; (3) single wheel test beds with the wheel diameter, width, load and grouser height stated; (4) Mars and Moon field data, with a gravity warning. Prefer sources that report wheel diameter, wheel width, load per wheel, grouser height, grain size, bulk density and friction angle, because the new model families need them.

## Sources already used (do not repeat)

heverly2013 (Journal of Field Robotics, MSL), hurrell2025, inotsume2016 (thesis), ishigami2007, li2008 (Spirit, Husband Hill), takehana2025, yoshida2010. Also check `research/evidence.csv` (`source_url`) before you claim a source.

## Avoiding duplicate work

Before you start on a source, append one line `source_key, agent name, citation` to `research/phase4/claimed_sources.txt` and check that no other agent claimed it. If it is claimed, choose another source.

## Files you write

- PDFs: only under `research/sources/phase4/` (git ignores it).
- One specification file per curve: `research/phase4/digitise/<curve_id>.json` for a curve read from a figure, `research/phase4/tabulated/<curve_id>.json` for a curve copied from a table or text. Copy the structure of the existing files in `research/phase3/digitise/` and `research/phase3/tabulated/` exactly (keys `pdf`, `pdf_note`, `page`, `dpi`, `x_axis`, `y_axis`, `marker`, `meta`; for tables `meta`, `method`, `points`). `meta.curve_id` must equal the file name. Fill every `meta` key; write `not reported` where the source does not give a value; put any value you derive (for example load per wheel from vehicle mass) in `comparability_note` and say it is derived.
- `x_name` must contain the word `slope` (for example `slope`, `slope angle`, `emulated slope`), `y_name` must contain `slip` or `slippage`, and units must be `deg` and either `percent` or `ratio` (0 to 1). Lateral slip curves are recorded with `y_name` containing `lateral`.
- Build and check your curves with `python3 scripts/digitise_figures.py --phase 4 --debug`; it writes `research/phase4/curves_new.csv` and overlay images under `research/sources/phase4/figures/`. Open the overlay images and confirm every point sits on its marker. Use tick marks for calibration, never the frame, unless the frame lines carry labelled values.
- Your log: `research/phase4/curves_<agent>_search_log.md` (searches table as in phase 3, inclusions, exclusions with reasons, the "not retrieved" list) and `research/phase4/curves_<agent>_references.csv` with the phase 3 references columns.

## Hard rules (repeated)

1. Full text only; a curve from a source you did not open in full is never written.
2. Never invent a point. If a marker is ambiguous, leave it out and say so in `comparability_note`.
3. Never edit files outside your own outputs and `claimed_sources.txt`. Do not run git. Do not touch `research/phase3/`.
4. No em dash or en dash characters, no emojis, no university names of any author's own studies, no AI assistant names, in anything you write.
