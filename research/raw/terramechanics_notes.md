# Terramechanics and granular-media models: notes (retrieval date 2026-10-11)

Companion file: terramechanics_rows.csv (30 rows, 15 distinct sources, ids TM-001..TM-030).
Working copies of every source read are in /home/claude/dune-rover/research/sources/ (my files: arxiv_1901.10667, arxiv_1604.02490, arxiv_2005.10976, arxiv_1911.00075, arxiv_1911.00079, arxiv_2606.19504, arxiv_2603.07796, arxiv_2403.03460, arxiv_2507.05643, arxiv_2306.02167, arxiv_2510.21006, arxiv_2412.05801, arxiv_2606.21755, treers_3drft, irani_dynamic, irani_pressure, terramech2019, ntrs_mueller_ps, saga_zr6175, sbmac_4643, arxiv_2603.28965, frontiers_slip_rate, easychair_kJRL, imeko_tc22_2017_019, carletti_polimi; other files in that folder belong to other agents and were not used).

Convention for validation_type: an analytic model (Bekker-Wong, RFT, regression) compared with a lab measurement is "lab"; a numerical simulation (DEM, SPH, MuJoCo, multibody rover sim) compared with a lab measurement is "sim-vs-lab"; simulation checked only against simulation is "simulation-only". No row is field evidence except TM-012 (sim-vs-field, beach, legged robot). Nothing here is wheeled-rover field data on dunes.

## SEARCH_LOG
| # | Query / action | Date | Hits looked at |
|---|---|---|---|
| 1 | arXiv API: "resistive force theory" AND wheel | 2026-10-11 | 1901.10667, 1604.02490, 2005.10976, 1911.00075 (all read) |
| 2 | arXiv API: "resistive force" granular locomotion | 2026-10-11 | 1911.00079, 2606.19504, 2603.07796, 2403.03460, 2412.05801 (read; 2603.07796, 2412.05801 gave no wheel/sand numbers used) |
| 3 | arXiv API: terramechanics + sand; Bekker + wheel; slip sinkage wheel sand; lunar simulant wheel drawbar | 2026-10-11 | 2507.05643 (read), 2306.02167 (read), 2510.21006 (read, parameters only), 2606.06790, 2509.22065, 2512.05008, 2603.28965 (Koopman; simulation of sandy loam/clay only, not used) |
| 4 | WebSearch: Bekker parameters dry sand (Wong table) | 2026-10-11 | sbmac proceedings (secondary table, read), saga-u Tottori sand paper (read); DTIC ADP004261 and AD1082843 refused (403) |
| 5 | WebSearch: single wheel testbed dry sand drawbar Bekker-Wong error | 2026-10-11 | RoverDevKit 2606.21755 (read), Irani Carleton PDFs x2 (read), Springer 10846-012-9777-3 (paywalled; used Carleton copy), ISTVS Senatore-Iagnemma page (abstract only) |
| 6 | WebSearch: Treers 3D RFT wheels | 2026-10-11 | Treers_3DRFT (read), Terramechanics-2019 journal version of Agarwal (read) |
| 7 | WebSearch: Bekker params lunar simulants GRC-1/JSC-1A/Toyoura | 2026-10-11 | NASA NTRS Mueller LPSC abstract (read, no numbers), Saga Tottori paper (read) |
| 8 | WebSearch: rover wheel dry sand slope slip DEM validation | 2026-10-11 | Omura & Ishigami EasyChair (read), IMEKO 2017 Kim (read; qualitative only), JBNU pages (not read) |
| 9 | WebSearch: Mars rover slip sand dunes wheel-soil validation | 2026-10-11 | Sakayori & Ishigami Frontiers 2024 (read); Arvidson kiss poster, EPSC2006 abstract (not read; left to other agent) |
| 10 | WebSearch: MDPI wheel-soil dry sand error | 2026-10-11 | Carletti MSc thesis (read); Politecnico/Torino theses (second not read) |
| 11 | WebSearch: Yu/Johnson 3D RFT wheeled locomotion | 2026-10-11 | istvs.org page returned 404 to fetch; abstract not retrieved |
Later arXiv API calls timed out (rate limit); I switched to WebSearch.

## KEY_FINDINGS
1. Classical Bekker/Wong-Reece terramechanics gives usable mean drawbar pull on sand only after per-soil fitting; sinkage is its weak output. Median per-point drawbar error 24-27% and sinkage error 28-52% on two lunar-simulant wheel datasets (TM-025 to TM-027, RoverDevKit's own evaluation of Ding and Hurrell data); it fails on firm soil with a small light wheel (135% drawbar, 385% sinkage, TM-028). In Agarwal et al., Bekker-type sinkage MAE was 26.07 mm vs RFT 2.73 mm on poppy seeds, but TM drawbar (3.41 N) beat RFT (5.05 N) there (TM-005, TM-006; poppy seeds not sand; TM plate far smaller than wheel patch).
2. Bekker parameters depend on plate geometry. Fitted kphi on dry Tottori sand roughly doubles (about 430 to 800-880) when plate aspect ratio drops from 6 to 2-1.4 and kc turns negative; sinkage prediction goodness of fit ranged 95% to 65% (TM-029 and the Table 2 values in the parameter table). Direct-shear K of order tenths of mm gave unrealistic drawbar and torque in Agarwal Sec. 10, so K is usually tuned.
3. Granular RFT predicts rigid-wheel drawbar and sinkage on real sands from a small parameter set, with residual error. Quikrete medium sand: drawbar MAE 5.55-7.11 N across 80-190 N loads (TM-001, TM-002). Mars Mojave Simulant (fines): 15.11 N drawbar and 18.41 mm sinkage at 190 N (TM-003, TM-004). Error grows with load; RFT underestimates drawbar at low positive slip and overestimates it at |slip| > 0.4. The MS/MMS response surfaces were scaled from poppy-seed data, not measured directly.
4. RFT and quasi-static Bekker models assume rate independence, but measured wheels are not rate independent: drawbar coefficient fell 8% between 0.01 and 0.2 m/s and 63.7% between 0.2 and 1 m/s on olivine sand at 20% slip (TM-018, TM-019). Agarwal et al. 2021 (arXiv 2005.10976, read; no numeric row) shows linear RFT wheel speed-vs-omega fails at high rotation while a continuum MPM model reproduces the plateau. Sakayori and Ishigami show that traction-slip depends on slip rate (TM-021). Transient or fast dune driving is outside the validated envelope of classical models.
5. Rover-scale slope tests on sand with a Bekker-Wong-Ishigami model needed tuning: untuned side-slip error 14.76% at 10 deg and 25.91% at 20 deg on Toyoura sand (TM-022, TM-023), falling to 0.49% at 20 deg only after tuning on that same case (TM-024, in-sample).
6. RFT legged-locomotion follow-ups report forces/speed/sinkage within roughly 7-15% in controlled boxes (TM-008, TM-009, TM-011, TM-012, TM-013), and one sim-vs-beach comparison with 10.5% and 11.5% mean speed/height error (TM-010). These are legged or plate tests, not wheels, and sinkage depends strongly on the RFT coefficient zeta.
7. Granular scaling laws: Slonaker big-vs-small wheel pairs on Quikrete sand satisfy predicted invariance within about 3% on level ground (TM-007, re-check against Fig. 4 because the text extraction is garbled). The extension to slopes and 1/6 g has been checked only in DEM (Omura and Ishigami, slip RMSE 0.015, TM-020, simulation-only). No physical low-gravity or sloped scaling validation was found.
8. DEM/SPH continuum can capture soil flow and high-slip behaviour that SCM-type Bekker models struggle with (Chrono::CRM paper's own statement), but needs rheology/contact calibration: cone-drop penetration error 7.4% on Ottawa sand and 3.5% on glass beads (TM-030). Its wheel slip-vs-slope agreement is shown only as a plot.
9. What none of these show: a field-validated slip or sinkage error for a wheeled vehicle on dune sand, heterogeneity effects (Kim et al. note the homogeneity assumption), or cohesionless slope-face avalanching.

## SOIL_PARAMETER_TABLE
All values below are PUBLISHED values copied from the cited location. None are my estimates. Units as printed; where the print is unusual I say so.

| Soil | Parameters (published) | Source and location | Note |
|---|---|---|---|
| Quikrete 1962 Medium Sand (silica, 0.3-0.8 mm) | kc -2.05e4 kN/m^(n+1); kphi 3.13e6 kN/m^(n+2); n 1.0; c 1500 Pa; phi 34 deg; K 0.0006 m; RFT const 2.02 N/cm3; rho_grain 2600 kg/m3; packing 0.6 | Agarwal et al. arXiv 1901.10667, Table 1 | From plate penetration and direct shear tests; negative kc and large kphi as printed, check units in PDF |
| Mars Mojave Simulant (basalt fines) | kc 846; kphi 6708; n 1.4; c 600 Pa; phi 35 deg; K 0.0006 m; RFT 3.05 N/cm3; rho_grain 2875 kg/m3 | same, Table 1 | Same caveats |
| Dry Tottori sand (loose, 1.5 g/cm3) | circular plates kc 2.54, kphi 428.97, n 0.76; aspect 6: 2.99, 427.02, 0.80; aspect 3: 6.30, 433.56, 0.82; aspect 2: 10.41, 880.86, 0.81; aspect 1.4: 9.04, 799.58, 0.79; cohesion 2 kPa; phi 38 deg | Nguyen Van et al. 2007 (saga_zr6175), Tables 1 and 2 | Units in text: kc kPa/m^(n-1), kphi kPa/m^n; geometry dependence |
| Dry sand (Irani testbed) | c 0; phi 28 deg; n 1 (taken from Wong); kphi' 20 (dimensionless, tuned); kc' 0; K 0.036 m; gamma 13734 N/m3; eta 1.35 | Irani et al. IJVAS preprint, Table 1 | Tuned, not independently measured (kphi' hand-tuned) |
| Dry sand (Irani smooth-wheel work) | c 0; phi 28 deg; kphi 900 (units not printed); kc 0; ka 110; gamma 13734 | Irani et al. JIRS 2012, Table 2 | Fitted |
| Toyoura sand (Ishigami values as quoted by Carletti) | c 0; phi 38 deg; chi_c 26 deg; kc0 0; kphi0 120.54; n 1.703; a0 0.4; a1 0.15; rho 1490 kg/m3 | Carletti MSc thesis, Table 1 (Sec. 2.13) | Secondary (borrowed from Ishigami [6], not re-measured). Units of kphi0 not printed |
| Generic "sand" (Wong via secondary) | kc 12.7e3; kphi 1528.43e3; n 1.1 | Rodrigues and Lopes, SBMAC 2025 (sbmac_4643), Table 1, citing ref [7] | SECONDARY and suspect: kc equals the clay entry (12.7e3), probably a transcription error. Do not use without the original Wong table (not retrieved) |
| "Loose dune sand" nominal | kc 2.0e3 N m^-(n+1); kphi 5.0e5 N m^-(n+2); n 1.2; +/-20% uncertainty band | Naik et al. arXiv 2510.21006, Table 1 | ASSIGNED nominal values for a planning study; provenance not given; no measurement |
| FJS-1 lunar simulant | min bulk density 1.549-1.560 g/cm3; peak cohesion 2.5 kPa, peak phi 44.1 deg (Dr 70%); residual cohesion 0.2-1.9 kPa; residual phi 34.1-37.2 deg | Omura and Ishigami, Table 1 (citing Ozaki 2023) | Not dry sand; DEM calibration targets |
| RMCS14 olivine sand | grain 90-700 um; internal friction about 35 deg | Rodriguez-Martinez et al. arXiv 2306.02167, Table 2 | No Bekker values reported |
| GRC-1 lunar simulant | bulk density 1760 kg/m3 (60% relative density), phi 38.4 deg | Unjhawala et al. arXiv 2507.05643, Sec. 3.3 | Used in CRM sim; no Bekker values |

Janosi-Hanamoto shear: published shear deformation moduli seen: K 0.0006 m (Agarwal, MS/MMS), 0.036 m (Irani), 0.018 m default (RoverDevKit Sec. 3.2, citing a cited ref), 0.04-0.045 m (poppy seeds). The spread over two orders of magnitude supports the finding that K is a tuning parameter rather than a transferable soil constant.

## GAPS
- No retrieved paper gives a numeric model-vs-experiment error for slip on a SLOPE with a single wheel on dry quartz sand using Wong-Reece and RFT side by side; Carletti is the only slope result (small rover, thesis, tuned).
- No open-access numeric validation of wheel RFT on dune-scale slopes, or of RFT/Bekker with cohesion-free sand near the angle of repose (avalanching).
- No retrieved field evidence for classical models (all rows lab or sim). The one field-type row is legged RFT on beaches.
- Bekker kc/kphi for clean quartz dune sand at Gulf conditions: not found. The Wong textbook table was not retrievable.
- Rate dependence: the only quantitative speed data is the olivine/ESA set (TM-017, TM-018); no sand model validated above 0.2 m/s.
- Slip-sinkage coupling and the transient hysteresis (Sakayori) lack model-based closure; RoverDevKit shows a rigid-wheel kernel under-predicts slip-dependent sinkage by about 52% median.
- Low-gravity physical validation of scaling laws is absent from what I read (Omura is DEM only).

## NOT_RETRIEVED
Items I could not read, or read only as abstract/snippet; no numbers were recorded from them.
- Li, Zhang, Goldman, "A terradynamics of legged locomotion on granular media", Science 339:1408 (2013). Fetch: https://www.science.org/doi/10.1126/science.1229163 (paywalled; I did not obtain a full text).
- Wong and Reece 1967, J. Terramechanics 4(1):81-98; Bekker 1969 "Introduction to Terrain-Vehicle Systems"; Janosi and Hanamoto 1961 (books/paywalled; not retrieved). Wong "Theory of Ground Vehicles" Table of dry sand Bekker values: not retrieved (only the suspect secondary table in sbmac_4643).
- Senatore and Iagnemma, "Analysis of stress distributions under lightweight wheeled vehicles", J. Terramechanics 2014. Only a news page seen: https://www.istvs.org/publication-news/2014/1/15/analysis-of-stress-distributions-under-lightweight-wheeled-vehicles
- Yu, Pavlov, Kim, Johnson, "Modeling wheeled locomotion in granular media using 3D RFT and sand deformation" (ISTVS 2024). Fetch: https://istvs.org/publication-news/modeling-wheeled-locomotion-in-granular-media-using-3d-rft-and-sand-deformation (returned 404 to my fetch) or https://2024.istvs.org/submissions/papers/2919
- Ding et al. (lunar simulant smooth and grousered wheel, r=157 mm, 80 N); Hurrell et al. (Rashid-1, FJS-1); Wang and Han (KLS-1). The numbers recorded from them are RoverDevKit's own computed errors (arXiv 2606.21755 Sec. 5.1), not retrieved from the originals; refs [21]-[23] in that paper.
- Ishigami et al. 2007, J. Field Robotics 24(3):233-250 (steering/slope wheel-soil model on loose soil); Ishigami, Nagatani, Yoshida 2009 slope traversal. Paywalled; Toyoura parameters only seen via Carletti.
- Kim et al. IMEKO TC22 2017 (lunar simulant wheel testbed): read, but drawbar/sinkage vs model are shown only in figures; no numeric error. Full thesis (K.-J. Kim 2017, Chonbuk) not retrieved.
- Chrono::CRM MGRU3 wheel slip vs slope (0-30 deg, GRC-1, NASA SLOPE lab data): plot only in arXiv 2507.05643 Fig. 5a, qualitative "good agreement"; numbers must be read off the figure or fetched from the SLOPE lab reference there [29].
- Agarwal et al. 2021 Science Advances (arXiv 2005.10976): read; contains qualitative statements and poppy-seed plots, no usable numeric error recorded.
- Treers wheel-specific RFT work and Kerimoglu et al. cohesive-RFT (arXiv 2412.05801): read abstract/intro level only for the cohesive paper; no sand-wheel numbers extracted.
- Retrieval problems: apps.dtic.mil ADP004261 and AD1082843 returned HTTP 403; kiss.caltech.edu predicting.pdf returned 404; arXiv API timed out repeatedly after the first few queries.
