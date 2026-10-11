# Learning-based slip prediction and traversability: notes (retrieval date 2026-10-11)

Row file: /home/claude/dune-rover/research/raw/learning_rows.csv (24 rows, LRN-001 to LRN-024, 18 distinct sources).
Working copies of every PDF/text read are in /home/claude/dune-rover/research/sources/ (short ids noted per source below).

## SEARCH_LOG

Tools: WebSearch (standard mode), WebFetch, Bash curl to arxiv.org, robotics.jpl.nasa.gov, roboticsproceedings.org, openaccess.thecvf.com, frontiersin.org, hal.univ-grenoble-alpes.fr, then `pdftotext -layout`. The arXiv search API (export.arxiv.org) was slow and returned only a partial list before timing out, so discovery was mostly WebSearch.

Queries run (all WebSearch unless noted):
1. arXiv slip prediction legged robot sand proprioceptive learning
2. self-supervised slip prediction from images planetary rover terrain Angelova
3. learning-based wheel slip estimation deformable terrain sand neural network rover field test RMSE
4. terrain-aware slip prediction legged robot granular media learning 2024 arXiv
5. SPOC Mars terrain classification deep learning rover Rothrock slip accuracy
6. physics-informed neural network terramechanics wheel soil interaction sinkage slip prediction
7. desert sand dune off-road dataset traversability slip robot dataset
8. quadruped robot terrain classification slip sand proprioception deep learning deformable terrain accuracy 2023
9. Gonzalez Iagnemma slippage estimation compensation planetary exploration rovers (review)
10. Ishigami OR Skonieczny slip estimation machine learning lunar rover wheel sinkage learning terrain parameters
11. vibration-based terrain classification rover wheel sand accuracy Iagnemma Brooks Dubowsky
12. learned slip model wheeled robot sand dune 2025 arXiv self-supervised traversability slip off-road
13. TAIL dataset (deformable granular) arXiv
14. AI4Mars dataset download data.nasa.gov license
15. MADMAX dataset Morocco desert Mars analogue DLR licence download
16. legged robot deformable terrain sand foot sinkage slip learned estimation quadruped RL 2024 2025
17. wheeled rover sand dune slip prediction transformer OR LSTM proprioceptive IMU field desert
18. terrain-aware traversability learned from slip Gaussian process sand Mars analog rover self-supervised slip cost map
19. Gonzalez Fiacchini Iagnemma slippage prediction ML regression pdf
20. Rothrock SPOC AIAA 2016 ntrs
21. Brooks Iagnemma vibration-based terrain classification T-RO 2005
Also arXiv API title queries (TartanDrive, RELLIS-3D) and WebFetch of dataset pages (RELLIS-3D GitHub, TartanDrive GitHub, TAIL site, data.gov AI4Mars, DLR Morocco page, Zooniverse AI4Mars).

Papers read in full or in the relevant sections (source id = file stem in sources/):
slipnet (2409.02273); angelova06 / rss06_angelova (Angelova et al., RSS 2006); angelova_jfr (Helmick/Angelova/Matthies, TANav); deepterramech (1806.07379); gonzalez2018_ras (HAL hal-01904487); learn_drive_mars_2609.24952; ai4mars; nesam (2608.21330); a2208_00322 (PrePARE); metalearn_2009.10191; semantic_clues_2011.01872; reservoir_2504.13348; a2606_06790 (ERNEST); frobt2025_1638667; frobt2024_1320261; a2509_22065; a2603_06928; slipdetect_2207.13629; wayfast_2203.12071; tartandrive; tartandrive2; rellis3d; tail_2403.16875; stone; tomd_2506.21630 (this is TOMD, not TAIL; renamed); mars_trav_2509.11082; hybrid_2410.17738; bevameter_2202.08495; valada_1804.00736.

## KEY_FINDINGS

Data needs and training sizes
- Visual slip prediction in the Angelova line needs per-terrain training sequences of ~1000-2000 stereo frames each plus a labelled texture dictionary (LRN-004, LRN-005; source angelova06). Slip labels come from visual odometry or encoders, so a labelled run is required for every terrain class.
- Perseverance study: ~500 sols, 45 km, ~43,000 images with self-labelled slip (wheel odometry vs visual odometry) and tilt/suspension signals; 5M-parameter transformer on frozen DINOv2 (LRN-011).
- Proprioceptive slip classification from a single-wheel testbed used roughly 13-15k samples (9235+3958 in Gonzalez 2018; 15,000 in DeepTerramechanics) (LRN-008, LRN-010).
- Legged slip-event detection used six ~30 min Spot runs with human-confirmed labels (LRN-016).
- Neuro-symbolic kinodynamics (NeSAM) used ~125,000 simulated transitions (LRN-014).
- SlipNet used 10,080 labelled simulated samples (8064/2016) (LRN-002 notes).

Generalisation evidence (what was and was not held out)
- Strongest held-out evidence: Perseverance 35 held-out sols, AUROC 0.874, F1 0.758, including a sand dune patch at 0.3 slip (LRN-011, LRN-012). Held out by sol (with stated geographic diversity), not by terrain type. Mars, not Earth dune sand.
- Angelova: temporal split inside one-terrain sequences. Gravel test RMS rose to 27.5% versus 7.16% train because test roll/pitch combinations were absent from training (LRN-004). This is the clearest documented extrapolation failure in slope space.
- Meta-learning (ALPaCA): cohesion band 0.7-1.3 kPa and friction angle 20-45 deg held out in training, velocity error under 5% on loose sand, but simulation only (LRN-017).
- NeSAM: online EKF soil adaptation lifted simulated out-of-distribution soil completion from 0/5 to 4/5 and physical grass-to-sand completion from 1/5 to 3/5 (LRN-015, with simulation numbers in its notes). Only five trials per configuration.
- ERNEST (JPL): policy trained in simulation transferred zero-shot to a real rover on M90 simulant at 20 deg; travel reduction (slip-like) fell from 81.9% (passive) to 43.0% (learned) on dry sand and from 100% (entrapment) to 30.0% on wet sand (LRN-020). Trial count not stated.
- Gonzalez 2018, DeepTerramechanics, Reservoir: all random in-distribution hold-out on one testbed or one dataset; none tested unseen soil (LRN-008, LRN-009, LRN-010, LRN-019).

Failure modes
- Terrain-class confusion dominates image-based slip error: soil/gravel misread as sand inflated error from 11.2% to 21.8% (LRN-005).
- Visual appearance does not fix mechanics: SlipNet authors state unseen terrains that look alike but differ mechanically are hard to predict (LRN-002). Slip is not predictable from vision alone; removing the proprioceptive alignment dropped AUROC 0.874 to 0.723 (LRN-012).
- Skewed slip distributions: regression losses are dominated by abundant low-slip samples, which hurts ranking of the rare high-slip cells (Perseverance paper, Sec. V-B).
- Moderate-slip class is the weakest (about 75% vs 85% for low/high) in proprioceptive classification (LRN-010). Medium and high slip bins blur into low slip in IMU-INS slip detection (LRN-025).
- Legged proprioception: gait choice changes sensing reliability. Trot gave 12.5% specificity for crust rupture versus 96% for slow crawl (LRN-023). Slip-event models are binary and pooled across sites (LRN-016).
- Sand versus large stones confused in wheel-vibration classification (LRN-019).
- Learned models claim sand capability without quantifying it: WayFAST abstract lists sandy dry beaches but the body gives no sand metric (not recorded as a row).

Slope dependence
- Legged evidence on a tilted granular bed shows speed falling from 15.7 to 4.98 cm/s from 0 to 20 deg and shear resistance at 20 deg about 40% of level (LRN-024). This is a physics model on glass beads, not a learned one; it shows what a slope-aware learned model must capture.
- Slope-dependent learned slip RMSE on sand specifically was not found. Angelova slope regressions were on soil and gravel with numeric slope ranges not reported.

## DATASETS

Licences were verified only where stated below. "Not verified" means no licence text was seen.

| Dataset | Terrain types | Size | Licence and where verified |
|---|---|---|---|
| RELLIS-3D | Texas A&M campus: grass, mud, puddle, rubble, asphalt, etc.; no sand or dune class listed | 13,556 LiDAR scans, 6,235 images, 20 classes | CC BY-NC-SA 3.0 as stated on the GitHub README (https://github.com/unmannedlab/RELLIS-3D, fetched 2026-10-11). Non-commercial. |
| TartanDrive 1.0 | Pittsburgh PA off-road: mud, rocks, foliage, dirt; no sand | 630 trajectories, ~5 h, ATV with IMU, shocks, wheel RPM, images, maps | GitHub repo shows an MIT licence (https://github.com/castacks/tartan_drive) but this may cover code only; dataset terms not verified. Files ~100 GB each. |
| TartanDrive 2.0 | Pennsylvania, 255 acres, narrow paths, foliage, rocky, dirt | 7 h, speeds to 15 m/s, adds LiDAR | Hosted at https://theairlab.org/TartanDrive2 (per paper). Licence not verified (WebFetch to the lab site was not permitted). |
| AI4Mars | Mars: soil, bedrock, sand, big rock | ~35K images, ~326K crowd labels, ~1.5K expert labels (data.gov record); distribution entry lists ~50K images, ~425K labels | data.gov catalog record has no licence field, only accessLevel public (https://catalog.data.gov/dataset/ai4mars-a-dataset-for-terrain-aware-autonomous-driving-on-mars, fetched 2026-10-11). Treat as public NASA data, licence unstated. |
| TAIL | Two sandy sites (fine and coarse sand), wheeled Scout and quadruped Unitree, flowing sand | 14 sequences, 74-194 s each, distance 15-148 m | Site states GPLv3 and commercial use by contact (https://tailrobot.github.io/, fetched 2026-10-11). Distribution on request/download page. SLAM benchmark with RTK ground truth, no explicit slip labels. |
| STONE | Farmland, mountain, lakes, construction; includes sandy, rocky, gravelly, puddled, muddy roads | 43 sequences, ~51k frames (31/7/5 split) | Not verified. Traversability labels derived from robot trajectories, no slip. |
| Mars 2020 Perseverance driving set | Mars: rocky hills, bedrock, sand ripples, gravel, sand dunes | ~500 sols, 45 km, ~43,000 images with slip and tilt per sample | Paper says "will be available"; no licence seen (arXiv 2609.24952). Only dataset found with onboard slip labels over dune-like sand, but Martian. |
| DLR Morocco navigation tests (2018) | Mars-analog desert, 8 sites | 36 experiments, 9.2 km, RTK ground truth, no slip | Page states no data licence (https://www.dlr.de/en/rm/research/publications-and-downloads/datasets/marokko-navigations-tests). Access via datasets.arches-projekt.de/morocco2018/. Not verified further. |
| MIT single-wheel data (Gonzalez et al.) | MIT regolith simulant with ripples | ~13-15k samples | Not stated as public in the papers read. |
| WVU Pathfinder slip data | Mars-analog field, PA | runs of 140-650 m | DOI 10.21227/vz7z-jc84 cited in paper; licence not verified. |
| TOMD (2506.21630) | Forest trails, no sand | 31.4k frame pairs | Not verified; irrelevant to sand. |

No public dataset was found that has Earth dune or desert sand with measured wheel or foot slip labels.

## GAPS

- Dune-specific learned slip prediction: no paper found that trains or tests a learned slip or sinkage predictor on open Earth dunes. Closest are Perseverance dune/ripple samples (Mars, labels from VO vs WO) and a scaled-vehicle grass-to-sand patch (NeSAM).
- Unseen-terrain generalisation: almost all held-out tests are random splits, temporal splits or sol splits. Terrain-type holdout (train on non-sand, test on sand) was not found. Only the simulation meta-learning paper holds out soil parameters, and only inside an analytic model.
- Slope dependence of learned error on sand: no table of learned slip error versus slope angle on sand. Angelova numeric slope range not reported.
- Legged slip on sand: no learned legged slip-magnitude estimator on sand found; the legged evidence is binary slip events (PrePARE, mixed sites) and non-learned penetration sensing (Fulcher et al.). RL locomotion papers on sand (e.g. RaiBo, appeared in search results only) were not retrieved.
- Slip label definitions differ: wheel-odometry vs VO (Perseverance), encoder vs carriage (testbed), DGPS (Kilic), 3-bin classes (Gonzalez, DeepTerramechanics). No common metric across rows.
- Physics-informed learning on real sand: NeSAM is the only recent hybrid with a physical test and its physical dataset size was not located. Nishishita and Ishigami is a fit to simulation, not real data.
- Sinkage targets: no learned sinkage-prediction numbers on sand retrieved (only the 5% vision measurement error in the articulated bevameter paper, which was not recorded as a row because it is not learning).

## NOT_RETRIEVED

Not read, therefore no numbers recorded:
- Brooks and Iagnemma, vibration-based terrain classification (T-RO 2005): https://dspace.mit.edu/handle/1721.1/30303 (bitstream returned 404).
- Gonzalez and Iagnemma, slippage estimation review (J. Field Robotics 2018): found only via citations; no open text fetched. Related abstract page: https://www.istvs.org/publication-news/characterization-of-machine-learning-algorithms-for-slippage-estimation-in-planetary-exploration-rovers
- Rothrock et al., SPOC (AIAA 2016): https://ntrs.nasa.gov/citations/20160008261 (PDF download returned 404; only the JPL MAARS poster https://www.jpl.nasa.gov/site/research/media/posters/2020/R18014p.pdf was read, with no accuracy number).
- Angelova et al., ICRA 2006 and JFR 2007 slip papers (cited by RSS 2006 for the other datasets); DTIC copy https://apps.dtic.mil/sti/pdfs/ADA593494.pdf returned 403.
- Deep MLP terrain classification for planetary rovers (Sensors 2019): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6679340/ (reCAPTCHA interstitial).
- TartanDrive project page licence: https://theairlab.org/tartandrive/ (WebFetch permission not granted).
- Skonieczny et al. 2019 slope-slip work, Iagnemma and Ward 2009 classification-based slip detection: citations only.
- RaiBo sand-beach RL locomotion and other RL-on-sand results surfaced in search: https://techxplore.com/news/2023-01-raibo-versatile-robo-dog-sandy-beach.amp (news page only, not read).
- NeSAM physical dataset size and Table III baseline TAL rows beyond those quoted: not located in text read.
- Gonzalez 2018 Fig. 6 MAE values (figure only), SlipNet soil parameter values, Nishishita SCM soil parameters: not found in text.
- ERNEST trial counts: not stated in text read.
- Papers read but yielding no recordable sand/slip number: 2509.11082 (Mars costmap from IMU roughness labels, simulation heavy), 2410.17738 (synthetic Mars segmentation in Unity), 2202.08495 (bevameter, not learning), 1804.00736 (acoustic terrain classification, no sand class), WayFAST (no sand metric), TartanDrive papers (no sand).
