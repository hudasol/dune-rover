# dune-rover

- **Problem.** Small wheeled robots that cross sand dunes plan on global 30 m elevation maps, but the main hazard, the slip face at the angle of repose, is often only metres to tens of metres long.
- **Finding.** On six North American dune fields with one metre lidar as truth, no hazard model of a 30 m map (a synthetic trained detector, slope, roughness, interpolation, or models trained on lidar) plans many face free routes: mission success {{VAL:bm_success_i30_naive_none}} with the slip model alone, at most {{VAL:bm_success_i30_risk_weighted_bicubiccal}} with any of them. The better layers roughly halve the length of route on faces ({{VAL:bm_ph_mkm_i30_naive_none}} to {{VAL:bm_ph_mkm_i30_risk_weighted_bicubiccal}} m per km), but almost no route is face free. At 10 m the best layer reaches {{VAL:bm_success_i10_risk_weighted_gbm}}. A face map made from fine data makes even a 30 m planning grid safe ({{VAL:bm_ph_success_i30_conservative_oracleany}} of pairs routed, none touching a face; post hoc): the limit is the face information that global elevation models do not hold (stages 25 and 26, `docs/PREDICTIONS.md`).
- **Product.** The Dune Rover Planner: slip face risk, a three class map and routes from any elevation model, a resolution gate that refuses to verify ground on maps coarser than 10 m, and exports for ROS 2 Nav2, QGroundControl and Google Earth (`docs/PLANNER.md`).
- **Ask.** A partner for a drone survey of an Arabian dune field and a slope ladder with a small rover (`docs/PARTNER_INDEX.md`).
- **Status.** Desk study, benchmark and conference paper draft (`paper/paper.pdf`, aimed at IROS 2027, `docs/VENUES.md`) complete; no field data yet. Author: Huda Mueen. **SIMULATED BY ME on PUBLISHED data; research, not engineering approval for any real vehicle.**

![Kelso Dunes: face patches in the lidar, the detector and gradient boosting on a 30 m map, and conservative routes on 30 m and 10 m maps](paper/figures/fig_map.png)

Generated from `docs/src/readme_template.md` by `scripts/build_report.py`; numbers come from the result files. Related repository, not duplicated here: [`hudasol/dhill`](https://github.com/hudasol/dhill) (heat and dust operating envelope).

## What is published, what is simulated, what is planned

| Label | Meaning | Where |
|---|---|---|
| **PUBLISHED** | A number read in a retrieved source: {{VAL:p3_rows_total}} rows from {{VAL:p3_sources_total}} sources with URL, passage, retrieval date and an independent re check; {{VAL:dc_ncurves}} digitised published curves | `research/evidence.csv`, `research/phase3/curves.csv`, report Appendix A |
| **SIMULATED BY ME** | Output of the code here: a slip model on real Copernicus GLO-30 elevation data, four slip model families and two built on the granular scaling laws tested on published curves (none passed the pre registered bar), a Project Chrono single wheel simulation, a sub grid slip face detector and three class map tested against one metre lidar of real dunes, route planning policies, and synthetic tests of the field analysis. Model assumption dependent, never field evidence | `src/dunerover/`, `results/`, `manuscript/` |
| **PLANNED** | A slope ladder field experiment, its pre data predictions, checklist, rover options and proposals (seed, EDGE, AAU field day, robotics project; no agreement exists with anyone). Nothing here has been run | `docs/FIELD_VALIDATION_PLAN.md`, `docs/predictions/`, `docs/FIELD_DAY_CHECKLIST.md`, `docs/ROVER_OPTIONS.md`, `docs/PROPOSAL_SEED.md`, `docs/PROPOSAL_EDGE.md` |

## Dune Rover Planner (the product)

The study is packaged as a planning tool: give it a dune elevation model (Copernicus GLO-30, lidar or a drone survey) and a vehicle profile, and it returns a slip face risk map, a three class map (TRAVERSABLE, BLOCKED, UNKNOWN), routes under three policies and a self contained HTML report. A resolution gate built from the lidar tests refuses to call ground coarser than 10 m verified traversable (a 30 m map called {{VAL:lid6_miss_min_30}} to {{VAL:lid6_miss_max_30}} of the face cells TRAVERSABLE on {{VAL:lid6_nsites}} lidar dune fields), and `dunerover vehicle calibrate` turns the rover's own slope runs into a measured profile. **SIMULATED BY ME**, not a safety case.

```
pip install ".[projected]"
dunerover demo --out demo_out
dunerover plan DEM.tif --posting 10 --start LON,LAT --goal LON,LAT --vehicle assumed --out out
```

User guide: `docs/PLANNER.md`. Interactive demonstration on four lidar dune fields: `demo/web/dune_rover_planner.html`. Report section 15.

## Earlier headline numbers (dated, from files)

- **2026-10-21 (report section 14; every number traced in `docs/NUMBER_LEDGER.csv`):** on {{VAL:mv4_exp_existing_n}} published curves from {{VAL:mv4_nsources}} studies no slip model family passes (median held out error {{VAL:mv4_heldout_min}} to {{VAL:mv4_heldout_max}}), and families built on the granular scaling laws do worse ({{VAL:mob_heldout_min}} to {{VAL:mob_heldout_max}}); Chrono calibrated on the Dumont curve up to 12.5 degrees gave no usable prediction of steeper slopes (numerically unstable there); on {{VAL:lid6_nsites}} lidar dune fields a 30 m map labels TRAVERSABLE {{VAL:lid6_miss_min_30}} to {{VAL:lid6_miss_max_30}} of face cells; over Liwa and the Rub' al Khali, {{VAL:is2_ps_trav_kept_B}} to {{VAL:is2_ps_trav_kept_A}} of screened steep ICESat-2 crossings fall in TRAVERSABLE cells, against more than 90 % of all segments (post hoc; method not validated, many steep segments are noise); in simulation, replanning on an online slip estimate shows no benefit distinguishable from a stop and retry control (post hoc). Field kit, preregistration draft, drone and sand protocols, and a ROS 2 demonstration are in the repository. Completeness: see `docs/COMPLETENESS.md`.
- **2026-10-20 (SIMULATED BY ME against PUBLISHED data; report section 13, `manuscript/MANUSCRIPT.md`):** slip model families calibrated on other studies predict a held out study with median errors of {{VAL:mv_heldout_min}} to {{VAL:mv_heldout_max}} slip ({{VAL:mv_verdict_line}}; bar 0.15). Against one metre lidar of three dune fields, {{VAL:tv_fs_min_30}} to {{VAL:tv_fs_max_30}} of the cells the 30 m map calls TRAVERSABLE contain steep faces ({{VAL:tv_fs_min_10}} to {{VAL:tv_fs_max_10}} at 10 m). Completeness: `docs/COMPLETENESS.md`.

- Verification: all {{VAL:ver_all_n}} evidence rows re checked against their sources. First check of the {{VAL:ver_ext_n}} rows as extracted: material errors {{VAL:ver_ext_material}} of {{VAL:ver_ext_n}} ({{VAL:ver_ext_material_rate}}), any discrepancy {{VAL:ver_ext_any}} of {{VAL:ver_ext_n}} ({{VAL:ver_ext_any_rate}}); of these, the {{VAL:ver_sup_n}} rows read from supplied PDFs had {{VAL:ver_sup_material}} material ({{VAL:ver_sup_material_rate}}, all on validation type). Current table, latest verdict per row (FLD-HV13-5 split into a lab and a field row): material {{VAL:ver_all_material}} of {{VAL:ver_all_n}} ({{VAL:ver_all_material_rate}}); current supplementary rows {{VAL:ver_cs_material}} of {{VAL:ver_cs_n}} ({{VAL:ver_cs_material_rate}}). Every material error corrected (`research/verification_log.md`).
- Simulation, 30 m: UNKNOWN share {{VAL:unk_A_30}} (A south Liwa), {{VAL:unk_B_30}} (B megadunes), {{VAL:unk_C_30}} (C linear dunes, Saudi Arabia); BLOCKED under 0.1 %; {{VAL:uni_A_30}} of cells in A have the same slope based verdict in at least 95 % of the 256 draws of the four assumed parameters (under the original ranges; not under the widened ranges below). If a face within one post of the cell counts (post hoc variant), UNKNOWN is {{VAL:unk3_A_30}}, {{VAL:unk3_B_30}}, {{VAL:unk3_C_30}}. **Simulation only, model assumption dependent; the detector was validated against synthetic truth in phase 2 and tested against North American lidar on 2026-10-20 (it fails at 30 m).**
- Published anchors (comparison of unlike vehicles and soils, report section 8.8): the Dumont Dunes slip curve (PUBLISHED, FLD-HV13-1) crosses 50 % slip at {{VAL:an_d_cross}} degrees, the nominal model at {{VAL:an_nom_cross}} degrees; with Ishigami 2009 Table I values the model gives {{VAL:an_b2_10deg}} slip on a 10 degree side slope where a slip ratio of about 0.5 was measured (TM-IS09-3). **The model predicts too little slip on sand slopes. Simulation only, model assumption dependent.**
- Widened slip scale range (2026-10-18, simulation only, model assumption dependent): with i0 0.05 to 1.20 (nominal 0.81) the nominal model crosses 50 % slip at {{VAL:rs_w_nomcross}} degrees and UNKNOWN at 30 m is {{VAL:rs_w_unk_A}} (A), {{VAL:rs_w_unk_B}} (B), {{VAL:rs_w_unk_C}} (C); with f_r also widened, {{VAL:rs_wf_unk_A}}, {{VAL:rs_wf_unk_B}}, {{VAL:rs_wf_unk_C}}. The original ranges remain the reference.
- Pre registered predictions and their hits and misses: `docs/PREDICTIONS.md`.

## Read in this order

1. `paper/paper.pdf`: the conference paper (five pages): the lidar benchmark with baselines, stages 25 and 26.
2. `docs/PLANNER.md`: the Dune Rover Planner, how to install and run it, its exports, and what it cannot do. Interactive demonstration: `demo/web/dune_rover_planner.html`.
3. `docs/PARTNER_INDEX.md` and `docs/EXECUTIVE_BRIEF.md` (also `.pdf`): one and two pages for a partner.
4. `docs/PREDICTIONS.md`: every prediction, written before its run, with its hit or miss.
5. `manuscript/MANUSCRIPT.md` (also `.pdf`) and `docs/REPORT.md` (also `.pdf`): the full desk study with every negative result.
6. `docs/NEXT_STEPS.md`: what the author does next.
7. `docs/PROPOSAL_ROBOTICS.md` and `docs/PROPOSAL_EDGE.md`: proposals; nothing has been sent and no agreement exists.
8. `docs/GLOSSARY.md`, `docs/PROTOCOL.md`, `docs/SEARCH_PROTOCOL.md`, `docs/DATA_CATALOG.md`, `docs/DATA_AND_LICENSES.md`, `docs/REPRODUCE.md`; working records of the sessions are in `docs/process/`.

## Layout

```
docs/                 report, brief, glossary, protocol, field plan, checklist, rover options, proposal seed, EDGE proposal,
                      licences, predictions register, open questions for the author, review and overnight log
docs/src/             hand written report sections and templates (REPORT.md, the brief and this README are built from them)
docs/predictions/     dated pre-data slope ladder predictions (PLANNED field experiment)
research/evidence.csv the evidence table (one row per reported mobility result)
research/raw/         per-topic notes and row files, data audit, morphology and UAE facts
research/phase2/      phase 2 retrieval reports and CSVs (morphology, rover options, rows read from supplied PDFs); no PDFs committed
research/phase3/      2026-10-20 evidence rows by topic, references with licences, search logs, digitised curves and calibrations, agent briefs
research/phase4/      2026-10-21 curves, their redigitisation check, scaling law notes and rows, protocol sources
field_kit/            data sheets for a field day; demo/ closed loop demonstration and its ROS 2 package; notebooks/ GPU notebook; config/ lidar sites
manuscript/           the paper (source in manuscript/src, generated MANUSCRIPT.md and .pdf)
src/dunerover/        simulation code (DEM, slope, slip model, graph routing, sensitivity, sub grid detector, three class map, field analysis)
                      and the Dune Rover Planner (planner.py, report.py, cli.py; evidence card in data/)
demo/web/             interactive planner demonstration (generated by scripts/build_web_demo.py)
scripts/              fetch_data.sh, consolidate_evidence.py, ingest_verification.py, verify_stats.py, build_report.py,
                      analyze_field_runs.py, field_analysis_power.py, make_ladder_predictions.py, anchor_comparisons.py, check_repo_hygiene.py, scan_secrets.py ...
tests/                {{VAL:ntests}} test functions (more cases when parametrised)
results/              simulation outputs and figures (all labelled SIMULATION ONLY); results/subgrid, results/field_kit (synthetic data),
                      results/anchors (model against the Dumont Dunes and Ishigami 2009 values), results/dumont_prior (stage 7),
                      results/*widened_i0* (stage 9, widened ranges), results/range_set_diagnostics (stage 11)
data/anchor_points.csv  13 published slip points used only for descriptive comparison
```

## Reproduce

Python 3.10 or newer.

```bash
pip install ".[projected]"                     # the planner and its command line
dunerover demo --out demo_out                  # runs on the Kelso lidar if fetched, otherwise on a synthetic dune field
pip install ".[dev,benchmark]" && PYTHONPATH=src python3 -m pytest -q tests
bash scripts/fetch_lidar.sh && bash scripts/fetch_data.sh   # lidar and Copernicus tiles with SHA-256 checks
PYTHONPATH=src python3 scripts/benchmark_detection.py && PYTHONPATH=src python3 scripts/benchmark_planning.py   # the paper's results
```

Every other result, stage by stage: `docs/REPRODUCE.md`.

## Data and licences

Full list in `docs/DATA_AND_LICENSES.md`. Copernicus GLO-30 (the controlling Free and Open licence was read in full; attribution and no liability notices required; no commercial restriction in the text), numpy, scipy, matplotlib, tifffile, imagecodecs, pytest (permissive). The DEM tiles are not committed. Source PDFs and raw downloads are never committed: a CI job fails if they are.

**Licence:** all rights reserved. The repository is public for reading and review; please contact the author before any use, modification, distribution or sale (`LICENSE`, `LICENSE-DOCS.md`).

## Not done

DEM and RFT were reviewed, not run; Project Chrono was run for a single wheel on 2026-10-20 (report section 13.4). No field data exist. Two learned baselines (gradient boosted trees and a small convolutional network) were trained leave one site out on lidar labels for the benchmark (stage 25). The sub grid detector was tested against one metre lidar of six North American dune fields (it works at 10 m and fails at 30 m, where a cubic interpolation and models trained on lidar rank faces better; stages 12, 20 and 25), never against an Arabian slip face. See report sections 10 and 13.
