# Release notes, version 1.0 (2026-10-21)

Author: Huda Mueen. Repository `hudasol/dune-rover`, all rights reserved (see `LICENSE` and `LICENSE-DOCS.md`). This release marks the end of the desk study. It is not field evidence and not engineering approval for any vehicle. Nothing has been sent to anyone.

## What version 1.0 contains

- **Evidence (PUBLISHED).** A verified evidence table (`research/evidence.csv`) with a measured extraction error rate, every row re checked against its full text, and the scaling law literature added on 2026-10-21.
- **Published curves (PUBLISHED).** Slip against slope curves digitised reproducibly in two rounds (`research/phase3/`, `research/phase4/`), with a repeatability check of a random third of the second round.
- **Model validation (SIMULATED BY ME against PUBLISHED curves).** Leave one study out tests of four slip model families and two families built on the granular scaling laws, on two rounds of curves and with post hoc regrouping by campaign and laboratory; none passes the bar fixed in advance (stages 15, 21 and 22 of `docs/PREDICTIONS.md`).
- **Independent simulation (SIMULATED BY ME).** Project Chrono Soil Contact Model sweeps and a calibration on the Dumont Dunes curve; the calibrated run is numerically unstable on steeper slopes, so no extrapolation test was obtained. A discrete element notebook for a free GPU is prepared, not run.
- **Terrain (SIMULATED BY ME on PUBLISHED data).** The slip face detector and three class map scored against one metre lidar of six North American dune fields; route planning policies scored on the same truth; ICESat-2 laser profiles compared with the 30 m map over three Arabian windows, with a method that failed its own validation and post hoc noise screens.
- **Closed loop (SIMULATED BY ME).** Online slip estimation and replanning against a modelled rover, in Python and as ROS 2 nodes; after two reviews, replanning shows no benefit distinguishable from a stop and retry control.
- **Field kit (PLANNED).** Data sheets, a one command analysis tested on a synthetic fixture only, a preregistration draft, drone survey and sand test protocols, and a second rater pack.
- **Documents.** `manuscript/MANUSCRIPT.md`, `docs/REPORT.md`, `docs/EXECUTIVE_BRIEF.md`, `docs/PROPOSAL_ROBOTICS.md`, `docs/PROPOSAL_EDGE.md`, `docs/COMPLETENESS.md`, all generated from result files; every number of the manuscript, brief and proposals is listed in `docs/NUMBER_LEDGER.csv`.
- **Reviews.** Fresh reviewer reports and the response to each finding: `docs/REVIEW_2026-10-15.md`, `docs/REVIEW_2026-10-18.md`, `docs/REVIEW_2026-10-20.md`, `docs/REVIEW_2026-10-21.md`.

## Known limitations at this release

- No field data of the author's own; no measured slip curve for any vehicle on Arabian dune sand.
- Arabian terrain is seen only through satellite laser profiles with a method that failed its own validation.
- The Bekker Wong family was rerun on the expanded curve set and did worse than in the first round; the calibrated Chrono model is not numerically stable above 12.5 degrees, so no extrapolation test of it exists.
- Human spot checks and a second human rater are prepared but not done.
- Source PDFs and raw downloads are not redistributed; the digitisation and the terrain analyses can be rerun only after fetching them (`docs/DATA_AND_LICENSES.md`, `scripts/fetch_lidar.sh`).

## How to check this release

Run `bash scripts/check_all.sh` from the repository root; it runs the tests, rebuilds every generated document from the committed results and checks that nothing changed, checks the number ledger, the repository hygiene and the secrets scan. `bash scripts/clean_clone_check.sh` repeats the rebuild from a fresh clone; its record is in `results/reproducibility/clean_clone_checks.txt`.
