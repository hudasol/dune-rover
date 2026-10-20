# Brief for evidence extraction agents, phase 3 (2026-10-20)

This file is the common instruction set for every agent that adds evidence rows in phase 3. It is kept in the repository so the protocol can be audited.

## What a row is

One row is one quantitative or clearly stated finding from one source that bears on wheeled (or, for comparison, tracked or legged) mobility on loose dry sand, on dune terrain, or on the terrain and sand properties that drive it. Use the 17 column schema of `research/raw/field_rows.csv` exactly:

`id,vehicle_or_wheel,terrain_description,soil_parameters_reported,slope_deg,method,method_family,metric,value,unit,validation_type,source_title,source_url,passage_or_location,retrieval_date,comparability_warning,notes`

- `validation_type`: `field` (natural terrain), `lab` (prepared bed, tilt bed, constructed yard, single wheel rig; an analytic model compared with such a measurement is also `lab`), `sim-vs-lab`, `sim-vs-field`, `simulation-only`, `none` (property measurement, review statement, or a value with no validation).
- `slope_deg`: number, range, `0 (level)`, or `not reported`.
- `value` and `unit`: copy the number exactly as printed; never compute a new number into `value`. If you derive something, write it in `notes` and say it is derived.
- `passage_or_location`: section, page, table or figure so a verifier can find it in under a minute.
- `retrieval_date`: 2026-10-20.
- `comparability_warning`: always fill: gravity, soil, wheel size, preparation, definitions of slip, anything that limits transfer to a small wheeled rover on Arabian dune sand.

## Hard rules

1. Full text only. Download or open the full text (open access PDF, arXiv, NASA NTRS, publisher open access page, institutional repository, thesis repository). If only an abstract is reachable, the source goes into the "not retrieved" list and produces no row. Never write a row from memory, from a search snippet or from a secondary citation of another paper.
2. Never invent or round values. Unknown is a valid value (`not reported`).
3. Check every source by a live lookup of its DOI (https://api.crossref.org/works/DOI or https://api.openalex.org/works/doi:DOI) or, without DOI, by opening its stable URL. Record it in your references file.
4. Free access only. No paid services, no logins.
5. Save downloaded files only under `research/sources/phase3/` (git ignores that folder). Never put a PDF anywhere else in the repository.
6. Text rules for everything you write: no em dash or en dash characters (use commas, colons or the word "to"), no emojis. Do not write the name of any university that the author studied at; it is excluded. Do not write the name of any AI assistant or model anywhere.
7. Do not run git. Do not edit any file except the files assigned to you below.
8. Do not duplicate a source that is already in `research/evidence.csv` (check `source_url` and title) unless you add a different finding from it, and then say so in `notes`.

## Your output files (replace TOPIC with your assigned topic)

- `research/phase3/TOPIC_rows.csv`: the rows, 17 columns, header included, quoted CSV (use Python csv module to write it).
- `research/phase3/TOPIC_references.csv` with columns `ref_key,citation,doi,url,resolved_by,resolved_on,licence,access,parts_read,local_file,rows`. `resolved_by` is the lookup used (crossref, openalex, url opened); `licence` as stated on the source (for example CC BY 4.0, arXiv non exclusive, NASA public domain, publisher all rights reserved with open access copy); `parts_read` names the sections read; `rows` lists the row ids it supports.
- `research/phase3/TOPIC_search_log.md`: a table with one line per search (database or tool, exact query string, date, number of hits returned, number screened, number retrieved in full, number used), then the inclusion and exclusion reasons, then a "not retrieved" list (citation, why, what would be needed).

## Inclusion

Include: quantitative results on slip, sinkage, drawbar pull, traction, gradeability, entrapment, motion resistance, terramechanics parameters, sand properties (grain size, density, friction angle, moisture, cohesion), dune slope and slip face geometry, wind regime and dune orientation, terrain classification accuracy from elevation or images, heat and dust effects on vehicles or robots. Prefer dry sand and dune terrain; include lunar and Martian evidence with a gravity warning.

Exclude: results with no number and no clear qualitative finding; marketing; news; anything you could not read in full.
