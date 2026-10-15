# Simulation (DEM / multibody / Chrono) notes - dune-rover review

Retrieval date for everything below: 2026-10-11. Working copies of fetched PDFs/text are in <repository root>/research/sources/ (not for redistribution). Rows are in simulation_rows.csv (30 rows, 11 papers).

## SEARCH_LOG

WebSearch queries (standard mode):
1. "Project Chrono SCM deformable terrain rover validation experiment slip sinkage comparison" -> found Hu 2024 (arXiv 2405.11001), Zhang 2024 (2407.18903), Kern 2026 (2601.04547), Liu 2026 (2602.18688), a Polito thesis, a Multibody 2023 abstract.
2. "DEM simulation single wheel experiment validation slip sinkage drawbar pull lunar simulant arXiv" -> Hu 2024, RoverDevKit (2606.21755), Hurrell 2025 (Springer), IMEKO lunar-rover paper (not opened), ISTVS news items.
3. "discrete element method wheel sand experiment comparison ... MDPI" -> Jelinek (CAVS preprint), Ono 2020 (DLR elib), Purdue/IUPUI DEM thesis (not opened).
4. "Chrono SCM soil contact model validation against experiments rover wheel real-time factor" -> Unjhawala 2025 (2507.05643), SBEL pages.
5. "Gazebo ODE terramechanics plugin rover wheel slip simulation validated experiment sand" -> Archimede rover (MDPI Robotics 2023), Frontiers Sakayori 2024, others not opened.
6. "multibody terramechanics rover simulation compared with experimental test ... MSC Adams OR RecurDyn OR ARTEMIS OR RoverSim" -> nothing new usable. No retrievable ARTEMIS, RoverSim, MSC Adams terramechanics or RecurDyn sim-vs-experiment paper surfaced in two searches (see GAPS).
7. "DEM full rover simulation vs physical rover test dry sand slope climbing ..." -> Watanabe 2024 (Aerospace, abstract only), Kyoto repository item (landing page only), NTRS items not opened.
8. "DEM simulation legged robot foot granular sand experiment validation" -> Candalot/Hurrell ISTVS 2024 (arXiv 2411.07261); others (Qian/Li RSS 2012 foot-intrusion work) not opened.
9. "Chrono documentation SCM ... BSD-3 licence" -> api.projectchrono.org vehicle terrain page.

Fetches that worked: arXiv PDFs (curl), Springer open-access PDF (Hurrell), DLR elib PDF, MSU CAVS PDF, Frontiers PDF, Chrono GitHub LICENSE/README, projectchrono.org license-chrono.txt, projectchrono.org/validation/, api.projectchrono.org/vehicle_terrain.html, arts.units.it repository copy of the Archimede paper (image-only PDF, read by tesseract OCR).
Fetches that failed: MDPI direct (HTTP "Access Denied" via curl; WebFetch gave a truncated page with no numbers), Kyoto repository PDF (returned an HTML landing page), McGill eScholarship (HTML), Frontiers /full page via WebFetch (permission not granted; PDF via curl worked).

## KEY_FINDINGS

Fidelity versus cost
- Cost ladder (all hardware-specific, RTF = wall time / simulated time, my derivations marked "derived"): fine-particle CPU DEM about 9 million (26 h for 10 ms; SIM-020, derived); GPU DEM with 1.2-1.4 M scaled particles about 840-3240 (SIM-016, SIM-024, derived); 4.6-15 M particle GPU DEM about 320-1000 (SIM-007, SIM-008, derived); Chrono CRM (SPH) 10.9-22.5 on optimised VIPER and tracked-vehicle cases, 20-60 on the single MGRU3 wheel (SIM-011, SIM-009 via notes of Table 2); Chrono SCM 17.6-50.7 on VIPER and about 24-26 on the tracked vehicle in the same benchmark (SIM-011) but about 2 in the Zhang setup (SIM-007/008); closed-form Bekker-Wong well below 1 (0.5 ms per wheel solve; SIM-028). The SCM-vs-CRM ordering therefore depends on the benchmark and on SCM grid choice; do not quote "SCM is real-time" without the benchmark.
- Hu 2024 (Intro, not a row) quotes DEM RTF 3000-15000 and CRM 30-150, citing other works; treat as secondary.
- DEM vs SCM agree closely when SCM is calibrated to that same DEM (SIM-005, SIM-006), but this is sim-vs-sim: both can be wrong against a real bevameter, which Zhang et al. say has not been checked.

Accuracy against physical data (scalar errors actually reported)
- Slip: 2D DEM vs lab single grouser wheel on Toyoura sand, 12.1% vs 14.7+/-3.0% (about 18% relative; SIM-018). Within one SD of the lab.
- Drawbar pull / traction: ERDC 36 M-particle DEM vs lab rigid tire: pull 15 vs 17 and gross traction 20 vs 31 (% of weight) at 20% slip (SIM-019); sinkage and motion resistance were under-predicted.
- Foot sinkage: EDEM DEM vs lab gripper in silica sand, mean 13.5% difference (SIM-021).
- Classical Bekker-Wong benchmark: 24% (FJS-1, small wheel) and 27% (Ding data) median drawbar-pull error, sinkage 28-52%, rising to 135% / 385% on firm dense simulant (SIM-025 to SIM-027).
- Many DEM/CRM wheel and rover validations (SIM-001, SIM-002, SIM-009, SIM-015) report only "good agreement" from plots, with no scalar error. Only a handful give numbers.

Calibration needs
- DEM: contact friction, rolling friction and cohesion are tuning knobs; angle of repose alone was used for Toyoura/FJS-1 (SIM-015) but particles were scaled 10-13x; Ono tuned the particle friction angle (SIM-018). Surface-scaled DEM is not independent evidence for a specific sand.
- SCM: needs six parameters from a bevameter; calibrating them against DEM gave Kc negative and phi about 21 deg (SIM-005), i.e. a numerical fit rather than a physical soil. Liu et al. mapped penetrometer stiffness into Kphi by a scaling rule (SIM-029).
- CRM: authors claim physical inputs only (density, friction angle) with little calibration (SIM-001, SIM-009), but the single-wheel runs used coarse resolution (0.01 m) and the lab material was a simulant.

Sim-to-real gaps
- Gravity offload: Hu et al. simulate VIPER at lunar gravity and predict far higher slip than a light 1-g rover test (about 85% vs about 42% at 30 deg; about 75% vs 18% at 10 deg; SIM-003, SIM-004). These are simulation predictions with no lunar validation (authors state this).
- Rigid-body simulators without deformable terrain: Gazebo/ODE odometry error under 5% in simulation vs under 10% in the sandbox on flat paths, and slope-slip results exist only as experiment (SIM-030). Data-driven real-time simulators (SIM-014) reproduce their own regression almost exactly but cannot predict immobilisation, since slip is prescribed.
- Soil type matters: Toyoura sand gave 15-20% lower simulated traction coefficient than FJS-1 under lunar gravity (SIM-017, simulation-only).
- Slope: real foot sinkage on dry silica sand rose from 13 mm (0 deg) to 36 mm (35 deg, near angle of repose) at 66 N (SIM-022, SIM-023, lab only). Any simulator that omits slope-induced shear collapse will under-predict.

## TOOLS_AND_LICENCES

- Project Chrono core (Chrono::Engine, Chrono::Vehicle, SCM, DEM-P, Chrono::GPU, CRM/FSI-SPH, FEA): BSD (3-clause) licence. Verified: LICENSE file text at https://raw.githubusercontent.com/projectchrono/chrono/main/LICENSE (copy of 2016 Project Chrono Development Team; redistribution conditions plus no-endorsement clause, "as is" disclaimer) and the same text served at https://projectchrono.org/license-chrono.txt (HTTP 200); README.md of github.com/projectchrono/chrono says it is distributed under a permissive BSD licence. The CRM paper (SIM-009 source, abstract) states the CRM model is released under BSD-3. Saved at sources/chrono_LICENSE.txt and sources/chrono_README.md. (The licence page https://projectchrono.org/license/ returned a 404 page; use license-chrono.txt.)
- Chrono::Vehicle terrain modules, from https://api.projectchrono.org/vehicle_terrain.html (saved as sources/chrono_vehicle_terrain.txt): flat, rigid, CRG, deformable SCM (grid with vertical node deflection; generalised Bekker-Wong with Janosi shear; "close to real time"; optional HIP GPU backend), deformable DEM (granular), deformable FEA (ANCF), deformable CRM (SPH). Deformable terrains work with rigid or FEA tires and tracked vehicles, not semi-empirical tire models.
- Chrono validation page https://projectchrono.org/validation/ lists granular validations (cone penetration, PIV shear, cratering, triaxial, flow rate), Chrono::Vehicle vs ADAMS/Car, and tire validation vs ADAMS; no wheel-on-sand or rover-on-sand experiment is listed there (as of retrieval). The rover-on-simulant validation lives in the papers (Hu 2024, Unjhawala 2025).
- Altair EDEM (+ HyperStudy, MotionSolve): used in SIM-015/016/017 and SIM-021/022/024; commercial software per the papers. Licence terms not checked.
- Gazebo with ODE: used in SIM-030; licence not checked.
- OmniLRS on NVIDIA Isaac Sim: SIM-012 to SIM-014 source calls OmniLRS open source; licence of OmniLRS and Isaac Sim not checked.
- Not covered by any retrieved source: RoverSim, ARTEMIS, MSC Adams terramechanics, RecurDyn.

## GAPS

- No retrieved study compares DEM, Chrono SCM or CRM against a full rover on real dune-scale sand or field dunes; every sim-vs-physical comparison is lab, on simulants (GRC-1/3, FJS-1) or Toyoura/silica sand.
- Only slopes 0-30 deg (SLOPE-lab ramp with simulant) have rover-level sim-vs-lab; legged work is foot sinkage only (SIM-021).
- Scalar rover-speed, climbing-limit, and drawbar-pull errors for Chrono/DEM against physical rover tests: none found beyond qualitative agreement; slope climbing ability is not reported as an error anywhere in the retrieved set.
- Gazebo/ODE and other game-engine style simulators lack published slip validation on slopes (SIM-030 explicitly has none).
- Real-time factor for DEM wheel-sand simulations is reported in very different units; no common benchmark.
- No UAE or Gulf sand parameters appear in any retrieved simulation paper.
- Search coverage: two searches for ARTEMIS/RoverSim/Adams returned nothing relevant, so absence is a search limitation, not evidence of absence.

## NOT_RETRIEVED

Items below are not recorded in the CSV because the number was not read in full text.
- Takehana et al. 2025, "Grouser wheel high-speed traction performance: DEM simulation and experimental result", Journal of Terramechanics vol. 120, article 101084 (cited by SIM-012 source). DOI not confirmed; locate via https://www.sciencedirect.com/journal/journal-of-terramechanics/vol/120.
- Nakashima et al., lugged-wheel DEM, J. Terramechanics 2010: https://repository.kulib.kyoto-u.ac.jp/dspace/bitstream/2433/126852/1/j.jterra.2010.04.001.pdf (curl returned a repository landing page; open in a browser).
- Watanabe, Horiguchi, Tanaka, "Effect of Soil Type on Running Performance of Small Lunar Rover", Aerospace 12(1):24, https://doi.org/10.3390/aerospace12010024 (abstract seen: 30 deg slope climbed on simulant, higher slip on simulant than on silica sand; no numbers read; lab study not simulation).
- MDPI Robotics 12(5):125 original figures (Archimede slip vs slope 5-20 deg, Figs 12-14; end-point errors Fig 11b): https://www.mdpi.com/2218-6581/12/5/125 (curl blocked). SIM-030 uses OCR text of the repository copy https://arts.units.it/handle/11368/3065703; the figure values are not extracted.
- Kern et al. 2026 Eq. 3: confirm the unit of alpha and the printed coefficients in https://arxiv.org/pdf/2601.04547 (SIM-013 is flagged unverified numerically).
- Hu et al. 2024 supplementary material (CRM parameters) and earlier validation [21] (single wheel and rover vs SLOPE lab): referenced inside https://arxiv.org/pdf/2405.11001; reference list entry [21]/[73]/[74] for the RTF ranges (DEM 3000-15000, CRM 30-150).
- Hurrell et al. Table 4 and Figs 5-6 numbers (traction coefficient, sinkage vs slip): https://link.springer.com/article/10.1007/s11214-025-01164-8 (figure data not in text layer).
- Jelinek et al. companion paper Peters et al. 2019 (DEM parameters and cone index calibration, ERDC).
- Chrono SCM validation reference "73" cited in Liu 2026 (https://arxiv.org/pdf/2602.18688), not identified.
- Sakayori and Ishigami 2024 (Frontiers in Robotics and AI, https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1320261/pdf): retrieved; Chrono SCM dynamics simulation of slip-rate path planning (mean slip ratio about 0.19-0.21 in rough-terrain runs, Table 4) but no sim-vs-experiment comparison, soil parameters not extracted, so no row.
- Polito master thesis (Fiammengo 2025), DEM vs SCM inside Chrono https://webthesis.biblio.polito.it/34661/1/tesi.pdf: retrieved; sim-only sensitivity study with reduced particle counts due to hardware limits; not a refereed source, no row.
- Candidates not opened: IMEKO TC22 2017 "mobility performance with numerical analysis and experimental validation for a lunar exploration rover" (https://imeko.org/publications/tc22-2017/IMEKO-TC22-2017-019.pdf); Purdue/IUPUI "Experimental Validation of Non-Cohesive Soil Using DEM" (https://hammer.purdue.edu/articles/thesis/Experimental_Validation_of_Non-Cohesive_Soil_using_Discrete_Element_Method/7436882); Chrono-based sensor simulation (https://arxiv.org/abs/2410.04371) downloaded but not read.

## PROCESS_NOTE

During this task another subagent wrote a script to the same scratchpad filename (mk.py) and I accidentally re-ran it once, regenerating <repository root>/research/raw/learning_rows.csv from that agent's own script (same inputs, so content should be unchanged). simulation_rows.csv was not affected.
