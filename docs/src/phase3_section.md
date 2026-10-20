## 13. Validation and extension of 2026-10-20

Everything in this section was pre registered in `docs/PREDICTIONS.md` (stages 12 to 18) before its run; hits, misses and post hoc analyses are listed there. The narrative version is `manuscript/MANUSCRIPT.md`. Labels as above.

### 13.1 Evidence base (PUBLISHED)

The evidence table now has **{{VAL:p3_rows_total}} rows from {{VAL:p3_sources_total}} distinct sources** ({{VAL:p3_vtype_line}}). {{VAL:p3_rows_new}} rows were added on 2026-10-20 under a written protocol (`docs/SEARCH_PROTOCOL.md`: five topic agents, a live DOI or URL check for every source, licences recorded, a not retrieved list per topic) in seven groups: planetary and analog traverses (PLN), single wheel terramechanics (TM3), empirical mobility models such as the cone index family and NRMM (MOB), Arabian dune sand properties (SND), dune morphology, wind and DEM error (DUN), terrain mapping and planning (MAP), and heat and dust effects (ENV). Every new row was re checked against its full text by a fresh agent: **{{VAL:p5_material}} of {{VAL:p5_n}} merged rows had a material error before correction ({{VAL:p5_material_rate}}, Wilson 95 % interval {{VAL:p5_material_ci}})**, most of them a wrong validation type; any discrepancy {{VAL:p5_any_rate}}. One row was dropped as unverifiable. A blinded random sample of 20 rows for a human rater is in `research/spot_check_inter_rater.md`. Arabian items now include grain size, sorting, mineralogy and density of UAE, Qatari, Saudi and Omani dune sands and Gulf drift potentials; no friction angle or slip face angle measured on UAE dunes was found.

### 13.2 Published curves (PUBLISHED, digitised)

{{VAL:dc_ncurves}} curves ({{VAL:dc_npoints}} points) from {{VAL:dc_nsources}} sources were digitised reproducibly (`scripts/digitise_figures.py`, calibration files in `research/phase3/digitise/`), with uncertainty, conditions and a comparability judgement per curve (`docs/DATA_CATALOG.md`). Nine published soil parameter sets are in `research/phase3/sand_parameters.csv`. The Wong table images supplied earlier remain unusable (no legible title and page) and were not used.

### 13.3 Model families (SIMULATED BY ME against PUBLISHED curves; stage 15)

{{TABLE:families}}

No family meets the bar fixed before the run. Held out errors are about 0.2 to 0.3 slip for every family, and the empirical logistic curve transfers as well as the physics based ones. The posterior of the existing exponential model over the {{VAL:post_ncurves}} curves judged comparable to dune sand is phi {{VAL:post_phi_deg}} degrees, f_r {{VAL:post_f_r}}, i0 {{VAL:post_i0}}; used as map ranges (`posterior_2026_10_20`) it gives UNKNOWN at 30 m of {{VAL:post_unk_A}} (A), {{VAL:post_unk_B}} (B) and {{VAL:post_unk_C}} (C). The Bekker Wong family with the published Ishigami 2007 simulant set does not reproduce that paper's drawbar pull curve (`results/model_validation/bw_vs_ishigami2007.csv`). Question 8: without draws that cannot move on level ground, the widened resistance range gives UNKNOWN of {{VAL:q8_unk_A}}, {{VAL:q8_unk_B}} and {{VAL:q8_unk_C}}, close to the widened i0 set, so the earlier 90 % shares came from immobile draws.

### 13.4 Independent simulation (SIMULATED BY ME; stage 14)

Project Chrono's Soil Contact Model with published wheel sizes and soil sets gives slip {{VAL:ch_w1s1_125}} at 12.5 degrees for a Scarecrow sized wheel against about 0.49 on the Dumont curve (root mean square difference {{VAL:ch_vs_dumont_rmse_grid}}), and differs from the repository's Bekker Wong family with the same inputs by {{VAL:ch_vs_bw_lo}} to {{VAL:ch_vs_bw_hi}}. Both use the Bekker and Janosi laws, so this is model form and implementation uncertainty, not independent physics. The "Toyoura" label of soil set S1 in the stage 14 files is wrong: that set is the FJS-1 lunar simulant of Ishigami et al. 2007.

### 13.5 Real terrain test (SIMULATED BY ME on PUBLISHED lidar; stages 12 and 13)

{{TABLE:lidar}}

The detector and the map work at 5 and 10 m and fail at 30 m on three real dune fields (Dumont Dunes, White Sands, Kelso Dunes; USGS 3DEP one metre lidar): at 30 m about one TRAVERSABLE cell in four contains at least 10 square metres steeper than 28 degrees, and the detector underestimates face prevalence by about 0.2. Slip face direction against ERA5 resultant drift direction: {{VAL:wind_hits}} sites within 45 degrees (`results/wind_azimuth/face_vs_wind.csv`).

### 13.6 Planning (SIMULATED BY ME; stage 17)

On 30 m maps no policy was reliably safer than naive least cost planning against lidar truth (Dumont: {{VAL:pl_Dumont_30_naive}} naive and {{VAL:pl_Dumont_30_conservative}} conservative routes met a 3 m grade above the climbing limit). With a 10 m map and a 10 m grade baseline (post hoc), conservative routes failed in {{VAL:pl10_Dumont_10_conservative}}, {{VAL:pl10_WhiteSands_10_conservative}} and {{VAL:pl10_Kelso_10_conservative}} of routed pairs at the three sites, against {{VAL:pl10_Dumont_10_naive}}, {{VAL:pl10_WhiteSands_10_naive}} and {{VAL:pl10_Kelso_10_naive}} for naive routes.

### 13.7 Sensitivity (SIMULATED BY ME; stage 16)

Total Sobol indices of the passable share in area A at 30 m: original ranges i0 {{VAL:sob_original_i0_ST}}, phi {{VAL:sob_original_phi_deg_ST}}, i_max {{VAL:sob_original_i_max_ST}}, f_r {{VAL:sob_original_f_r_ST}}; widened i0 range i0 {{VAL:sob_widened_i0_i0_ST}}, f_r {{VAL:sob_widened_i0_f_r_ST}}, i_max {{VAL:sob_widened_i0_i_max_ST}}, phi {{VAL:sob_widened_i0_phi_deg_ST}}. First order indices sum to well below one: the parameters act through interactions.

### 13.8 Field rule options (synthetic data only; stage 18; the current rule stays in force)

| Rule | Correct model accepted (sigma 0.03) | Collapse model accepted (sigma 0.03) | Dumont truth accepted (sigma 0.10) |
|---|---|---|---|
| Current (stage 10) | {{VAL:ro_current_model_0.03}} | {{VAL:ro_current_collapse_0.03}} | {{VAL:ro_current_dumont_0.1}} |
| A, stricter tolerance | {{VAL:ro_A_model_0.03}} | {{VAL:ro_A_collapse_0.03}} | {{VAL:ro_A_dumont_0.1}} |
| B, steep runs | {{VAL:ro_B_model_0.03}} | {{VAL:ro_B_collapse_0.03}} | {{VAL:ro_B_dumont_0.1}} |
| C, calibration slope | {{VAL:ro_C_model_0.03}} | {{VAL:ro_C_collapse_0.03}} | {{VAL:ro_C_dumont_0.1}} |

Every option that catches the collapse model also rejects a correct model more than half the time; more runs in the steep bins would be needed. The choice is Huda's (question 7).
