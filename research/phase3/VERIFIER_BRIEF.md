# Brief for verifier agents, phase 3 (2026-10-20)

You check evidence rows written by another agent. You did not write them and you have not seen the extractor's notes or comparability warnings. Your job is to find what is wrong, not to confirm.

For every row in your input file `research/verify_batchNN.csv` (claim fields only):

1. Open the source yourself from `source_url` (or its DOI landing page, or an open access copy that is clearly the same document; record which in `source_access`: `url_pdf`, `url_html`, `oa_copy`, `local_copy` if you used a file under `research/sources/phase3/`, or `not_accessible`).
2. Find the passage, table or figure named in `passage_or_location`. If it is not there, search the document for the value.
3. Check each field against the source: vehicle or wheel, terrain, soil parameters, slope, metric meaning, value (exact as printed), unit, and validation type under these definitions: `field` natural terrain; `lab` prepared bed, tilt bed, constructed yard, single wheel rig, or an analytic model compared with such a measurement; `sim-vs-lab`, `sim-vs-field`, `simulation-only`; `none` for a property measurement, a review statement or a value with no validation.
4. Verdicts: `correct`; `minor_error` (number right, but a label, location, or descriptive detail wrong); `material_error` (wrong value, unit, metric meaning, validation type, vehicle or terrain, or slope, or the claim is not in the source); `unverifiable` (the source cannot be opened in full).

Write `research/verify_out_batchNN.csv` with the columns
`id,source_access,passage_found,location_confirmed,vehicle_ok,terrain_ok,soil_ok,slope_ok,metric_ok,value_ok,unit_ok,validation_type_ok,overall,corrected_value,what_is_wrong,notes`
(yes or no in the check columns; `corrected_value` in the form `field=value; field=value` using the column names of the input file; `notes` says where you found each item, with page numbers). Use the Python csv module. One output row per input row, same ids.

Rules: no em dash or en dash characters, no emojis, no university names of the author, no AI assistant names; do not run git; do not edit any other file; free access only; never guess a value you could not see.
