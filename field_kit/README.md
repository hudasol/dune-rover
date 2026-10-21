# Field kit: data sheets and the one command ingest (PLANNED)

These are blank data sheets for the slope ladder field day of `docs/FIELD_VALIDATION_PLAN.md`. Nothing here is a measurement.

| Sheet | One row per | Notes |
|---|---|---|
| `runs_template.csv` | run | Same columns as `docs/field_log_template.csv`, plus `station_id`. Slip is computed, never typed. `entrapped` is 0 or 1. Leave `phi_deg`, grain size, density or moisture empty when they come from the soil sheet. |
| `stations_template.csv` | slope station | Slope from RTK GNSS or the drone surface, with the source named in `slope_source`. |
| `soil_template.csv` | soil test repeat | `test` is one of `friction_angle_deg`, `angle_of_repose_deg`, `grain_d50_mm`, `bulk_density_kg_m3`, `moisture_pct_0_2cm`; methods in `docs/SAND_LAB_PROTOCOL.md`. |

On the evening of the field day, copy the three filled sheets into one folder (named `runs.csv`, `stations.csv`, `soil.csv`) and run:

    PYTHONPATH=src python3 scripts/ingest_field_day.py path/to/folder --label 2027-01-15_site1 --rebuild

The script checks the sheets and stops on any error, fills soil values from the station tests, computes slip, applies the committed adequacy rule (`src/dunerover/fieldanalysis.py`, unchanged), scores the dated predictions in `docs/predictions/`, and writes `results/field_day/<label>/` with a one page summary. It was tested only on the SYNTHETIC fixture in `tests/fixtures/field_day_synthetic/`, which can never write under `results/`.
