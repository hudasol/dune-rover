# Proposal seed: field validation of slip and traversability prediction on UAE dunes

**This is a proposal outline, not an achievement.** No partnership, funding, permission or endorsement exists or is claimed. Nothing in it has been run. It builds only on what this repository contains: a verified review of the published evidence (`docs/REPORT.md`), simulation studies that depend on stated assumptions (report section 8, labelled simulation only), and a planned experiment (`docs/FIELD_VALIDATION_PLAN.md`). Heat and dust operating limits for the electronics are the subject of the sibling repository `hudasol/dhill` and are cross referenced, not repeated, here. A two page version addressed to EDGE Group, with specific asks and fallbacks, is `docs/PROPOSAL_EDGE.md` (also a proposal only; no agreement exists).

## 1. Question

Can the slip and entrapment of a small wheeled robot on the stoss slope of a dune in the UAE be predicted, before the runs, by a simple slip model calibrated on gentle slopes only, and how much of a 30 m open elevation map is trustworthy for planning once the unresolved slip faces are accounted for?

Why it matters: the review of 170 published results found no slip against slope dataset for a wheeled robot on dune sand with measured soil, and the only Arabian field evidence is one qualitative report of a rover getting stuck (FLD-042). The simulation shows the traversability map is controlled by assumptions that only a field measurement can fix.

## 2. Method (all PLANNED)

1. **Slope ladder.** One fixed small rover (5 to 25 kg, four wheels), one dune stoss slope, runs at about 0, 5, 10, 15, 20 and 25 degrees (or the 2026-10-15 revision with denser bins between 10 and 20 degrees, `docs/FIELD_VALIDATION_PLAN.md` section 4), randomised order, fresh track each run, about 60 runs including a 12 run pilot, cross slope, tethered descent and repeated passes. RTK ground truth, wheel encoders, motor currents, IMU, sinkage gauge.
2. **Soil.** Sieve grain size, bulk density, moisture, crust, angle of repose, penetrometer and plate pressure sinkage at every station. No soil parameter is assumed; unmeasured items stay unknown.
3. **Pre-registered analysis.** Dated predictions are committed before any data (`docs/predictions/`). Calibrate on 0 to 10 degrees, write the post calibration predictions, then run the steeper bins. Tolerance from the pilot scatter. Report predicted against observed with intervals; the pass or fail rule is secondary because a synthetic test shows it discriminates weakly (report section 9).
4. **Elevation map check.** Compare the 30 m Copernicus GLO-30 slope and the modelled slip face probability (report section 8.7) with an RTK or drone profile of the same dune. This is the only test the sub-grid detector can have; it has been validated against synthetic truth only.
5. **Optional extension.** A second rover design or a legged platform on the same ladder, only after the first result and with its own plan (no legged comparison has been run).

## 3. Deliverables

- An open dataset of the runs with the soil description (log template `docs/field_log_template.csv`), published under the repository licence once confirmed.
- A report stating, with intervals, how well the calibrate then predict protocol worked on the steeper bins and where the entrapment slope fell against the pre-data prediction.
- A measured slip face profile set and a statement of how far the 30 m map is from it.
- Updated assumption ranges and a re-run of the three class map with them.
- Honest negative results: if the model fails, the failure is reported with the data.

## 4. Risks

| Risk | Mitigation |
|---|---|
| Run to run scatter is larger than assumed, so the experiment cannot discriminate | The 12 run pilot measures it first; the analysis flags an uninformative experiment (3 times pilot sigma above 0.30) |
| Entrapment or damage at 20 to 25 degrees | Tether and recovery line, two people, abort rules (`docs/FIELD_DAY_CHECKLIST.md`) |
| Heat and dust | Schedule outside the hottest hours; limits of electronics are in `hudasol/dhill` and are not claimed here |
| Slip faces avalanche under or near people | Nobody downslope of the rover; tether to the side |
| One rover, one site, one soil, so poor transfer | Stated as a finding, not hidden; scope is limited to the tested vehicle, wheels, soil and speed |
| Site access and permission | Not secured; an assumption of this proposal that a partner or the site owner provides it |
| Costs unknown | Costs are given only where a source was retrieved (`docs/ROVER_OPTIONS.md`); no budget total is claimed |

## 5. What a university or research partner would provide (to be negotiated, none assumed)

- Access to a suitable dune site, permits and local knowledge of safe, legal locations.
- Vehicle transport and recovery support, and a safety and risk review under the institution's rules.
- Laboratory use for sieving, density and moisture measurement, and a soil mechanics adviser for plate pressure sinkage and shear tests.
- RTK GNSS or total station equipment and, if possible, drone photogrammetry for dune profiles.
- A named supervisor or co investigator, and student or technician time.
- Data management, ethics or safety sign off where required, and a route to publish the open dataset.

## 6. Indicative phases (durations are placeholders, not commitments)

| Phase | Content |
|---|---|
| A | Site, permission, equipment sourcing, rover fitting and bench checks of slip measurement against a tape and marker test |
| B | Pilot day (12 runs) and tolerance set from the pilot scatter |
| C | Main ladder, soil characterisation, dune profile survey |
| D | Analysis against the committed predictions, report, open data release |

## 7. What this repository cannot claim

It cannot claim that any model predicts a rover on Arabian dunes, that any route is traversable, or that any institution supports the work. The proposal is a plan to find out.
