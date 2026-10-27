# Partner index: what exists, what is measured, what is assumed

One page for a supervisor, a funder or a robotics team deciding whether to work on this. Author: Huda Mueen. The repository is all rights reserved; contact the author before using any of it.

## What exists

| Item | Where | Status |
|---|---|---|
| Dune Rover Planner: slip face risk map, three class map, routes under three policies, HTML report; exports for Nav2, QGroundControl and Google Earth; a ROS 2 node | `src/dunerover/`, `docs/PLANNER.md`, `demo/ros2/` | Software, tested in CI on Python 3.10 to 3.13 and Windows; SIMULATED BY ME |
| Conference paper: lidar benchmark of coarse map slip face detection and route planning, with six baselines | `paper/paper.pdf`, `paper/src/` | Draft for IROS 2027 (`docs/VENUES.md`) |
| Desk study: evidence table, slip model families against published curves, lidar tests, closed loop simulation | `docs/REPORT.md`, `manuscript/MANUSCRIPT.md`, `docs/EXECUTIVE_BRIEF.md` | Complete as a desk study |
| Field kit: slope ladder protocol, data sheets, ingest script, preregistration draft, drone and sand laboratory protocols | `docs/FIELD_VALIDATION_PLAN.md`, `field_kit/`, `docs/OSF_PREREGISTRATION_DRAFT.md` | PLANNED; never run |
| Proposals | `docs/PROPOSAL_ROBOTICS.md`, `docs/PROPOSAL_EDGE.md` | PLANNED; nothing sent, no agreement exists |

## What is measured (PUBLISHED data, scored by the code here)

- One metre USGS 3DEP lidar of six North American dune fields is the ground truth for every map and route test (stages 12, 20, 25 and 26 of `docs/PREDICTIONS.md`).
- Published slip curves of other vehicles (49 curves from 10 studies) are the test set for the slip models.

## What is assumed

- Every vehicle parameter of the planner (friction angle, motion resistance, slip scale, planning slip limit) is an assumption range for a small wheeled robot until a vehicle's own slope runs calibrate it (`dunerover vehicle calibrate`).
- No Arabian dune field has been tested against a fine survey; the Arabian maps in the report are 30 m and fall under the resolution gate.

## What a partner would provide

A named supervisor and a safety review; written access to one dune site; one small wheeled rover (5 to 25 kg) or support to build one; RTK GNSS or a total station; a drone survey by an authorised operator; sand laboratory access; one outside reviewer (`docs/PROPOSAL_ROBOTICS.md`, section 7).

## Where to look first

1. `paper/paper.pdf` (six pages) and `docs/EXECUTIVE_BRIEF.md` (two pages).
2. `docs/PLANNER.md`, then `dunerover demo` after `pip install ".[projected]"`.
3. `docs/PREDICTIONS.md` for every prediction and its hit or miss, and the `docs/REVIEW_*.md` files for the independent reviews and the response to each finding.
