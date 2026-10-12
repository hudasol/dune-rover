# Proposal: a supervised field day for the dune slope ladder (draft for Al Ain University)

**Status: PROPOSAL. No agreement, partnership or endorsement exists.** The author has not yet obtained access to Al Ain University (AAU). Until access exists, the project proceeds alone (see `docs/NEXT_STEPS.md`, section 2, route A). This document is what the author would send, or present, once access exists (route B).

## Purpose
Run the pre registered slope ladder (`docs/FIELD_VALIDATION_PLAN.md`) on one dune stoss slope, to measure slip against slope for a small wheeled rover and to test the sub grid slip face detector against a surveyed profile. Nothing in the repository has yet been compared with real dune data.

## What the author brings (already done)
- Pre registered, dated predictions (`docs/predictions/`) and a tested analysis script (`scripts/analyze_field_runs.py`, with a wrong model test).
- A one page field day checklist (`docs/FIELD_DAY_CHECKLIST.md`), a log template (`docs/field_log_template.csv`) and rover options (`docs/ROVER_OPTIONS.md`, costs only where retrieved).
- A simulation study, labelled simulation only and dependent on model assumptions (`docs/REPORT.md`).

## What the author would ask AAU for (each item is a request, not an assumption)
| Request | Why | Fallback if unavailable |
|---|---|---|
| A named academic supervisor or research contact | Oversight, safety sign off, authority to request access | Route A, alone |
| Loan of a small wheeled rover, or lab space to build one from the options list | The vehicle for the ladder | Cheapest option in `docs/ROVER_OPTIONS.md` |
| A survey grade GNSS (RTK) unit or a drone with photogrammetry | Slope bins and the detector test profile | Smartphone inclinometer with a levelled straight edge for slope bins; detector test deferred |
| A second vehicle with a tow strap and a driver experienced on sand | Recovery | Do not run on slopes above 15 degrees |
| A letter or email giving permission for the site | Land access | No run without it |
| Two student volunteers | Spotter, logger | One volunteer plus the author |

## Plan
1. Pilot (12 runs, slopes up to 10 degrees) to set the tolerance from the scatter.
2. Full ladder (0, 5, 10, 15, 20, 25 degrees), randomised order, with the post calibration prediction file committed before the 15 to 25 degree runs.
3. Analyse with the committed script; report every hit and miss, including a negative result.
4. Share the data and the write up with AAU.

## Safety and conditions
Start early morning to avoid the hottest hours (coordinate with `hudasol/dhill`, kept as a separate study). Water and shade for people, a spotter on every run, abort rules in the checklist, no person on a slope above 20 degrees during a run.

## Open items (the author's to fill in)
- Contact at AAU: not yet identified.
- Site: not yet chosen.
- Dates: not yet set.
- Budget: none assumed; free options first.
