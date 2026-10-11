# Review protocol (written before searching)

Project: dune-rover. Author: Huda Mueen. Protocol date: 2026-10-11.
Status: research, not engineering approval for any real vehicle.

## 1. Research question

How well can wheeled (and, secondarily, legged) robots' slip, sinkage and traversability on dry sand and dunes be predicted from terrain data and models; how well do those predictions transfer from lab to field; and what would a minimal open-data traversability planner for Arabian desert dunes need that the literature does not yet provide?

Out of scope: thermal and dust effects on robots (see sibling repo hudasol/dhill). This project cross-references it only.

## 2. Evidence classes (kept visibly separate everywhere)

| Label | Meaning |
|---|---|
| PUBLISHED | A number reported in a source that was retrieved and read |
| SIMULATED-BY-ME | Output of code in this repo, model-assumption dependent |
| PLANNED | A protocol or experiment not yet run |

Published results carry a validation type: `lab` (single-wheel bench, soil bin, lab test rig), `field` (real vehicle on real terrain), `simulation-only` (published simulation with no physical comparison), or `sim-vs-lab` / `sim-vs-field` where a comparison is reported.

## 3. Search strategy

Sources, in order: arXiv (API), NASA NTRS, publisher pages and open-access repositories reachable from the sandbox (MDPI, Frontiers, PMC, university repositories), Semantic Scholar / OpenAlex / Crossref metadata where reachable, project and dataset pages (Project Chrono, Copernicus, USGS, OpenTopography, JAXA, NASA). Paywalled-only sources are recorded as "not retrieved" and are not cited for numbers.

Query families (each logged with date and hit count in `research/search_log.csv`):

1. terramechanics: Bekker, Wong, Reece, wheel-soil interaction, slip-sinkage, drawbar pull, dry sand
2. granular: resistive force theory, RFT wheel, granular scaling, locomotion on sand
3. simulation: DEM, Project Chrono SCM / DEM, multibody, high-fidelity versus empirical comparisons
4. learning: slip prediction, traversability estimation, self-supervised, proprioceptive, terrain classification, slip from vision
5. field and analog: Mars rover slip (Spirit, Opportunity, Curiosity, Perseverance), Meridiani, Purgatory Ripple, Dingo Gap, Hidden Valley, Moses Lake and Kelso dunes, desert field trials, Gulf / Arabian / Rub' al Khali / Empty Quarter robotics
6. legged and tracked: legged robots on sand/granular terrain, quadruped sand locomotion, tracked vehicle sinkage
7. open data: Copernicus GLO-30, SRTM, ASTER GDEM, ALOS AW3D30, NASADEM, FABDEM, ArcticDEM-style products, Sentinel-2, Landsat, UAE national datasets, TanDEM-X
8. UAE context: Rashid rover, MBRSC, Emirates Mars Mission, Emirates Lunar Mission, national space strategy
9. dune morphology: slip face angle of repose, dune height and wavelength, barchan and linear dune geometry in the Rub' al Khali

## 4. Inclusion criteria

A mobility result becomes an evidence row only if all hold:

- the source was retrieved and the number found in the retrieved text (table, figure caption, abstract, or body);
- the terrain is dry granular/sand-like (dry sand, lunar/Martian simulant, dune, ripple) or the row is explicitly flagged as a comparison on other terrain;
- it reports at least one of: slip ratio, sinkage, drawbar pull / traction, motion resistance, traversability prediction error, success rate on a slope;
- vehicle or wheel/leg geometry and the soil description are reported or marked "not reported".

Excluded: results only seen in a snippet or secondary summary; unverifiable claims; paywalled content not retrieved.

## 5. Comparability rules

Rows are never averaged or ranked across setups without a warning. A `comparability_warning` is raised, and written in the row, when any of these differ from the nearest comparison: wheel diameter/width/grouser, vertical load, soil type or relative density, slope definition (terrain slope vs. pitch), slip definition (longitudinal wheel slip vs. visual-odometry slip vs. skid), error metric (RMSE, MAE, relative error, classification accuracy), travel speed, scale (single wheel vs. full vehicle), and validation type.

## 6. Extraction fields (evidence table)

`id, vehicle_or_wheel, terrain_description, soil_parameters_reported, slope_deg, method, method_family, metric, value, unit, validation_type, source_title, source_url, passage_or_location, retrieval_date, comparability_warning, notes`

Each value needs a passage location (table/figure/section/page) so it can be re-checked.

## 7. Parameters and licences

- No soil parameter is invented. Each is cited from a retrieved source with its location, or labelled ASSUMPTION and given a sensitivity range.
- Every dataset or code library used is recorded with its licence in `docs/DATA_AND_LICENSES.md`, checked against the provider's own page.

## 8. Quotation and copyright

Paraphrase. At most one short attributed quote (under 15 words) per source. No reproduced passages or figures.

## 9. Verification plan

After drafting, a separate agent with no access to the drafting context re-opens the sources for a random sample (fixed seed) of at least 25 evidence rows and checks vehicle, terrain, metric, value, unit and validation type. Error rate = rows with at least one wrong field divided by rows checked, reported with the field-level breakdown. Errors are corrected in the CSV and the report, and the correction log is kept in `research/verification_log.md`.

## 10. Simulation protocol (item 4(a))

Real open elevation model of a real dune area; stated slip-versus-slope model with cited or labelled-assumption parameters; fixed seeds; every output labelled "simulation only, model-assumption dependent"; one-at-a-time and global sensitivity analysis on the assumptions; unit tests for slope computation, model monotonicity and reproducibility.

## 11. Stopping rule

Stop and report if a needed source or dataset cannot be retrieved from the sandbox, stating exactly what to fetch and where to put it.
