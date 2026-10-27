# Dune Rover Planner: user guide

The Dune Rover Planner is the research of this repository packaged as a tool. It reads an elevation model of dune terrain and a description of the vehicle, and returns where the vehicle can drive, where the map cannot tell, and a route with its risks. **SIMULATED BY ME:** every output is model and assumption dependent, not field evidence and not a safety case. All rights reserved; ask the author before any use.

Interactive demonstration: `demo/web/dune_rover_planner.html` (open it in a browser; it holds four lidar dune fields at 10 m and 30 m).

## 1. Install

```
pip install .                 # from the repository root; adds the dunerover command
pip install ".[projected]"    # also pyproj, needed for projected inputs (UTM lidar, drone surveys) and GeoJSON in WGS84
```

Without installing: `PYTHONPATH=src python3 -m dunerover.cli ...` from the repository root. Free tools only: Python, NumPy, SciPy, Matplotlib, tifffile and, optionally, pyproj.

## 2. Five commands

```
dunerover demo --out demo_out
dunerover assess DEM.tif --posting 10 --out out_assess
dunerover plan DEM.tif --posting 10 --start 53.71,23.12 --goal 53.74,23.10 --out out_plan
dunerover vehicle calibrate runs.csv --name my-rover --out my-rover.json
dunerover plan DEM.tif --vehicle my-rover.json --start-rc 40,5 --goal-rc 40,180 --policy conservative --out out_rover
```

- `demo` runs on the Kelso Dunes lidar when it has been fetched (`scripts/fetch_lidar.sh`), else on a synthetic dune field, as a 10 m and a 30 m map.
- `assess` writes the class map without a route.
- `plan` adds routes between two points, given as longitude and latitude (`--start`, `--goal`) or as row and column of the analysis grid (`--start-rc`, `--goal-rc`). `--policy all` (the default) plans with the three policies.
- `vehicle calibrate` builds a vehicle profile from the vehicle's own slope runs (section 5).
- Options for `assess` and `plan`: `--window xmin,xmax,ymin,ymax` crops in map units; `--coarsen K` block averages the input first (to see what a coarser map would hold); `--posting` sets the analysis posting in metres (an integer multiple of the input); `--draws` and `--seed` set the parameter sampling.

## 3. Inputs

- **Elevation model:** a single band GeoTIFF with model pixel scale and tiepoint tags, either geographic (EPSG:4326, such as Copernicus GLO-30) or projected in metres (such as USGS 3DEP lidar in UTM or a drone survey export). No GDAL is needed. A file without GeoKeys is read as a local frame in metres (give start and goal as row and column); a projected file in units other than metres is refused.
- **Vehicle profile:** `assumed` (the default: the assumption ranges of the study), `published-posterior` (the posterior of the slip model fitted to published curves of other vehicles; wider, and not a description of any rover in Arabia), or a JSON file from `dunerover vehicle calibrate`.

## 4. Outputs (in the `--out` folder)

| File | Content |
|---|---|
| `report.html` | Self contained report: resolution gate, map, routes, warnings, class shares, vehicle profile and what the evidence says about this kind of map |
| `map.png` | Three class map over a hillshade with the routes, beside the slip face probability |
| `classes.tif` | Class map as a GeoTIFF in the reference system of the input: 0 TRAVERSABLE, 1 BLOCKED, 2 UNKNOWN (assumption sensitive), 3 UNKNOWN (slip face risk), 4 UNKNOWN (both) |
| `routes.geojson` | One feature per policy, in WGS84 longitude and latitude when the input has a reference system, with length, UNKNOWN cells, face risk cells, steepest grade and warnings |
| `summary.json` | Everything above as numbers, with the seed and the vehicle profile |
| `face_probability.tif`, `q_pass.tif` | The slip face probability and the share of vehicle parameter draws for which each cell is passable, as float32 GeoTIFF layers on the same grid as `classes.tif` |
| `nav2_map.pgm`, `nav2_map.yaml` | Occupancy map for the ROS 2 Nav2 map server (trinary mode): TRAVERSABLE free, BLOCKED and NO DATA occupied, every UNKNOWN class unknown, so the robot's own costmap decides how to treat ground the map could not verify; origin in the input's map units (a local metre frame for geographic inputs, with the corner's longitude and latitude in a comment) |
| `routes.kml` | The routes for Google Earth or a ground station, when the input has a reference system |
| `mission_<policy>.plan` | QGroundControl mission (waypoints for a ground rover, at most 100 per route) for ArduPilot or PX4 rovers, when the input has a reference system; every file is labelled SIMULATED BY ME and every route must be checked on the ground |

## 5. How it decides

- **Passable cell.** For each of `--draws` parameter sets drawn inside the vehicle profile's ranges (sets that cannot move on level ground are dropped), a cell is passable when at least four of its eight headings have slip below the planning limit under the friction circle slip model (`src/dunerover/slipmodel.py`).
- **Classes.** TRAVERSABLE: passable in at least 95 % of the draws and slip face probability below 0.2. BLOCKED: passable in at most 5 % of the draws. UNKNOWN: everything else, split by cause.
- **Slip faces.** At 2 m or finer input, faces are read from the input: a cell holds a face when at least 10 square metres of it are 28 degrees or steeper (the truth rule of the lidar tests); for cells smaller than 10 square metres the rule is applied over a moving footprint of 10 square metres. Coarser, a detector trained on synthetic dunes estimates the probability of a face hidden inside the cell.
- **Resolution gate.** RESOLVED (input at 2 m or finer), DETECTOR (analysis at 10 m or finer) or COARSE (coarser than 10 m: TRAVERSABLE is not verified). The message quotes the miss rates measured on lidar dune fields from `src/dunerover/data/evidence_card.json`, which `scripts/build_evidence_card.py` builds from the result files.
- **Policies.** naive (the slip model only), conservative (TRAVERSABLE cells only), risk weighted (avoids BLOCKED cells, cost raised by the face probability). The two cautious policies also never descend a grade of 28 degrees or more between cells, and every policy avoids NO DATA cells (more than half of the cell's posts void; voids are filled with the nearest valid elevation for the slope computation). A route that descends 25 degrees or more gets a warning.
- **Vehicle calibration.** `dunerover vehicle calibrate` reads runs in the format of `docs/field_log_template.csv` (or the output of `scripts/ingest_field_day.py`), fits the motion resistance f_r and slip scale i0 to the runs at 10 degrees or less without entrapment, with the friction angle from the soil tests, and keeps the bootstrap pairs of (f_r, i0), which the planner draws jointly because the two trade off on gentle slopes. When there are at least three runs above 10 degrees, the profile reports the error of the calibrated model on them. The planning slip limit i_max stays the study's assumption range. The calibration bounds are the assumption ranges of the study; a value at a bound means the bound decided it.

## 6. What it cannot do

- It does not know any real vehicle until it is given that vehicle's runs, and even then only on the sand they were made on.
- No slip model in this repository transferred between published studies (report section 14.2), so routes near the climbing limit are guesses.
- At 30 m it misses most slip faces; at 10 m it still misses some (report sections 13 and 14.4). Onboard sensing remains necessary for metre scale features.
- A cautious policy is not a safe policy: in the registered test on three lidar dune fields (stage 17), no policy was reliably safer than naive on 30 m maps, and the gains at 10 m came from a post hoc comparison (report section 13).
- No hazard layer helps much on a 30 m map: in the stage 25 and 26 benchmark (report section 16, `paper/paper.pdf`) mission success on six lidar dune fields stayed between 6 % and 11 % at 30 m with every hazard layer a rover could compute, including this planner's detector; on 10 m maps the detector raised it from 15 % to 24 to 27 %, gradient boosting trained on lidar to 34 %. With a face map made from fine data (lidar or a drone survey), a hard gate found face free routes for most pairs even on a 30 m grid (post hoc), so give the planner a fine input whenever one exists: at 2 m or finer it reads the faces directly. At 30 m a cubic interpolation of the map ranks hidden faces better than the planner's detector.
- It plans on a static map; online slip feedback showed no benefit over stopping and retrying in simulation (report section 14.6).
- It has not been run on Arabian terrain with a validated survey; that is the first work package of the robotics proposal.

## 7. For developers

Python API: `dunerover.planner` (`read_raster`, `crop_map`, `coarsen_raster`, `assess`, `plan`, `compare_policies`, `VehicleProfile`, `builtin_profile`, `profile_from_runs`), `dunerover.report.write_outputs` and `dunerover.exports` (`write_nav2_map`, `write_kml`, `write_qgc_plan`). The benchmark baselines of stages 25 and 26 are in `dunerover.benchmark` and `dunerover.benchmark_cnn`. Tests: `tests/test_planner.py` (synthetic inputs only). The gate (`scripts/check_all.sh`) and CI check that the evidence card matches the result files.
