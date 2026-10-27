# Reproduce every result

Moved from the README on 2026-10-27; the commands are unchanged. Stage numbers refer to `docs/PREDICTIONS.md`.


Python 3.10 or newer. Dependencies: numpy, scipy, matplotlib, tifffile, imagecodecs; pytest for tests.

```bash
pip install -e ".[dev]"          # or: pip install numpy scipy matplotlib tifffile imagecodecs pytest
bash scripts/fetch_data.sh       # downloads three Copernicus GLO-30 tiles (about 143 MB), checks SHA-256
PYTHONPATH=src python3 -m pytest -q tests
PYTHONPATH=src python3 -m dunerover.study --data data/raw --out results                    # phase 1, about 5.5 minutes
PYTHONPATH=src python3 -m dunerover.study_subgrid --data data/raw --out results/subgrid    # phase 2, about 5 minutes
PYTHONPATH=src python3 scripts/field_analysis_power.py                                      # synthetic power study, original bins, about 1 minute
PYTHONPATH=src python3 scripts/field_analysis_power.py --design 2026-10-15                   # same for the revised bins, a few minutes
PYTHONPATH=src python3 scripts/make_ladder_predictions.py --design 2026-10-15 --date 2026-10-15   # revised expected ranges
PYTHONPATH=src python3 scripts/anchor_comparisons.py                                       # Dumont Dunes and Ishigami 2009 anchors, about 10 s
PYTHONPATH=src python3 scripts/study_dumont_prior.py                                       # stage 7: Dumont fitted i0 in the 30 m map, about 12 minutes
PYTHONPATH=src python3 -m dunerover.study --data data/raw --out results/widened_i0 --range-set widened_i0                 # stage 9, also widened_i0_fr
PYTHONPATH=src python3 -m dunerover.study_subgrid --data data/raw --out results/subgrid_widened_i0 --range-set widened_i0  # stage 9, also widened_i0_fr
PYTHONPATH=src python3 scripts/anchor_comparisons.py --range-set widened_i0                # stage 9, writes results/anchors_widened_i0, also widened_i0_fr
PYTHONPATH=src python3 scripts/field_analysis_power.py --design 2026-10-15 --rule 2026-10-18   # stage 10, amended entrapment rule
PYTHONPATH=src python3 scripts/diagnose_level_ground.py                                  # stage 11, draws that cannot move on level ground
bash scripts/fetch_lidar.sh                                                              # 2026-10-20: USGS 3DEP lidar tiles with SHA-256 check
PYTHONPATH=src python3 scripts/terrain_validation_lidar.py                               # stage 12, detector and map against lidar (also --truth-max-deg 36, post hoc)
PYTHONPATH=src python3 scripts/wind_face_direction.py                                    # stage 13, ERA5 wind from the Open-Meteo archive (slow: rate limited)
/opt/mm/chrono/bin/python scripts/chrono_wheel_slope.py                                  # stage 14, needs pychrono 9.0.1 (conda, see the script header)
PYTHONPATH=src python3 scripts/compare_chrono.py                                         # stage 14 comparison
PYTHONPATH=src python3 scripts/digitise_figures.py --check                               # W2: rebuild curves.csv from the calibration files (needs the source PDFs locally)
PYTHONPATH=src python3 scripts/model_validation.py --families exp_existing,mohr_coulomb_ratio,logistic_empirical   # stage 15, also --families bekker_wong (slow)
PYTHONPATH=src python3 -m dunerover.study_subgrid --range-set posterior_2026_10_20 --out results/subgrid_posterior_2026_10_20   # stage 15 map
PYTHONPATH=src python3 -m dunerover.study_subgrid --range-set widened_i0_fr --reject-immobile --out results/subgrid_widened_i0_fr_mobile   # stage 16, question 8
PYTHONPATH=src python3 scripts/sobol_map.py                                              # stage 16, Sobol indices
PYTHONPATH=src python3 scripts/planner_lidar.py && python3 scripts/planner_matched_pairs.py   # stage 17
PYTHONPATH=src python3 scripts/field_rule_options.py                                     # stage 18
PYTHONPATH=src python3 scripts/terrain_validation_lidar.py --sites-file config/lidar_sites_phase4.json --out results/terrain_validation_phase4   # stage 20
PYTHONPATH=src python3 scripts/planner_lidar.py --sites-file config/lidar_sites_phase4.json --out results/planner_phase4                     # stage 20
python3 scripts/icesat2_profiles.py fetch && PYTHONPATH=src python3 scripts/icesat2_profiles.py analyse --lengths 10   # stage 19 (docs/ICESAT2_GUIDE.md)
PYTHONPATH=src python3 scripts/model_validation.py --families exp_existing,mohr_coulomb_ratio,logistic_empirical --extra-curves research/phase4/curves_new.csv --out results/model_validation_phase4   # stage 21
PYTHONPATH=src python3 scripts/model_validation.py --families mobility_pull,mobility_logistic --extra-curves research/phase4/curves_new.csv --out results/model_validation_phase4         # stage 22
PYTHONPATH=src python3 demo/closed_loop.py && PYTHONPATH=src python3 demo/closed_loop_posthoc.py   # stage 23 and its post hoc variant
/opt/mm/chrono/bin/python scripts/chrono_scm_calibration.py                              # stage 24
PYTHONPATH=src python3 scripts/ingest_field_day.py FOLDER --label LABEL --rebuild         # after a field day (field_kit/README.md)
PYTHONPATH=src python3 scripts/build_manuscript.py --pdf && python3 scripts/check_manuscript_numbers.py   # manuscript and its number check
PYTHONPATH=src python3 scripts/build_number_ledger.py --check                              # every number traced (docs/NUMBER_LEDGER.csv)
bash scripts/clean_clone_check.sh                                                          # clean clone rebuild of every generated document
python3 scripts/consolidate_evidence.py && python3 scripts/verify_stats.py                  # evidence table and verification log from files
python3 scripts/build_report.py  # rebuilds docs/REPORT.md, the brief and this README from docs/src, the CSVs and results
python3 scripts/check_repo_hygiene.py --history && python3 scripts/scan_secrets.py --history
PYTHONPATH=src python3 scripts/benchmark_detection.py && PYTHONPATH=src python3 scripts/benchmark_planning.py   # stages 25 and 26 (bash scripts/fetch_data.sh first for the GLO-30 tiles over the lidar fields; about 1.5 hours on 2 cores)
PYTHONPATH=src python3 scripts/build_paper_figures.py && PYTHONPATH=src python3 scripts/build_paper.py   # the conference paper (paper/paper.pdf; needs LaTeX with the IEEEtran class)
```

Seeds are fixed and listed in `results/summary.json` and `results/subgrid/summary.json`. Phase 2 was run twice and the CSVs matched.

