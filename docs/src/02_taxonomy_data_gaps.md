
---

## 4. Taxonomy of prediction approaches and when each is appropriate

The table is a judgement made from the evidence above, not a ranking from head to head tests. No retrieved study compares these families on the same vehicle and the same dune sand.

| Family | Needs | Strengths (published) | Weaknesses (published) | Appropriate when | Not appropriate when |
|---|---|---|---|---|---|
| **Slope threshold or friction circle rules** (the model in section 8) | Slope, a friction angle, a few tuned constants | Costs almost nothing, runs on any elevation model, transparent | Constants for slip and resistance are not transferable (K varies about 75-fold, section 3.1); no sinkage; blind to sand state | Coarse screening of large areas, ranking assumptions, planning where entrapment is the worst case | Predicting actual slip or drawbar for a specific vehicle without calibration |
| **Classical Bekker-Wong, Wong-Reece** | Bevameter or plate tests, shear tests, wheel geometry and load | Interpretable, closed form, fast (SIM-028) | 24 to 52 % median error on benchmark wheels, worse on firm soil (SIM-025 to SIM-027); parameters depend on plate geometry (TM-029); quasi static (TM-018, TM-019) | Single wheel design trade studies on a characterised soil, with tuning on that soil | Transient or fast driving; sloped dune faces; soils not measured |
| **Granular RFT** | Depth and orientation force law from a plate or intruder test | Few parameters; wheel drawbar mean absolute error 5.6 to 15 N and sinkage error 18 mm at 190 N on sand and fines (TM-001 to TM-004); relative errors of about 2.6 to 15 %, up to 30 % for reversed legs, in legged and plate tests (TM-008 to TM-013) | Error grows with load; response surfaces scaled from poppy seeds; no sloped wheel field validation found | Slow quasi static locomotion on dry grains in a controlled bed, legged robots, fast what if studies | Wet, crusted or cohesive sand; high speed; steep slopes close to repose |
| **Scaling laws** | Matched wheel pairs | Collapse level ground data within about 3 % (TM-007) | Slopes and low gravity unvalidated physically (TM-020 is DEM only) | Transferring a lab result between wheel sizes on level sand | Slope or gravity changes |
| **DEM** | Particle contact calibration (friction, rolling resistance, cohesion), often scaled particles | Captures flow, avalanching and high slip behaviour; about 13 to 18 % where a scalar error exists (SIM-018, SIM-021), with larger gaps for gross traction (20 against 31 % of weight, SIM-019) | Wall clock hundreds to thousands of times simulated time with scaled particles on GPU (SIM-016, SIM-024) and about 9 million for fine particles on CPU (SIM-020), all derived; calibration is a tuning step, not independent evidence | Mechanism studies, generating training data, checking simpler models | Planning, anything needing many runs |
| **Chrono SCM / CRM, multibody** | Bekker-Wong constants (SCM) or density and friction angle (CRM) | Two to several orders of magnitude cheaper than DEM (SIM-007, SIM-008, SIM-011); BSD-3 | Validation mostly plots, no scalar errors (SIM-001, SIM-002, SIM-009); fitted SCM constants can be unphysical (SIM-005) | Rover scale simulation, controller testing, generating labelled data | Claiming predictions for unmeasured soils |
| **Learning from images or terrain class** | Slip labels per terrain from visual odometry or encoders | Held out AUROC 0.874 on Perseverance (LRN-010) | Needs labelled runs on each terrain; class confusion inflates error (LRN-004); fails outside training roll/pitch (LRN-003) | Onboard hazard ranking where the vehicle has driven similar sand | A new terrain type, or a regional sand never driven on |
| **Learning from proprioception** | Wheel speeds, currents, IMU | Detects slip as it happens (LRN-009, LRN-015, LRN-024) | Moderate slip is weakest (LRN-009); mostly binary events; random hold outs | Online slip detection and adaptation | Predicting slip in advance of driving |
| **Hybrid or physics informed learning** | Physical model plus onboard adaptation | Online soil adaptation lifted physical grass to sand completion in a small trial (NeSAM, notes; the physical dataset size was not located) | Few physical tests, small trial counts | Promising for adapting a planner to unseen sand | As proven evidence of generalisation |
| **Empirical field tables** (Mars slip tables) | Prior drives and operational constraints | Used in practice on Mars (FLD-020, FLD-021, FLD-024) | Failed on mixed terrain and hidden weak deposits (field notes) | Conservative operations with a human in the loop | Autonomy on unseen terrain |

**Selection rule used in this project.** Use a cheap slope and slip rule to map where the answer is sensitive to assumptions (section 8), use a calibrated single wheel model or RFT to choose wheel geometry on a characterised sand, and use proprioceptive or image based learning on board only after the vehicle has logged enough runs on that sand. Use DEM only to understand mechanisms.

---

## 5. Open data for an Arabian dune planner

All retrievals 2026-10-11. Licences are as read from provider pages; legal reading is the user's responsibility. Full table: `research/raw/data_audit.csv`; licences: `docs/DATA_AND_LICENSES.md`.

| Dataset | Resolution | Coverage | Licence (as read) | Access tested | Notes |
|---|---|---|---|---|---|
| Copernicus DEM GLO-30 (DSM, TanDEM-X, 2010 to 2015) | 1 arcsec; about 28.3 m E-W by 30.8 to 30.9 m N-S at 23.5 N (my arithmetic from tile geometry; the code uses 30.76 m) | Global land | Free with attribution (c) DLR and Airbus, EU/ESA; controlling licence (COP-DEM-GLO-30-F) read in full in phase 2: no commercial restriction, attribution and no liability notices required (`docs/DATA_AND_LICENSES.md`) | Yes, AWS COG tiles; used here | Published accuracy: absolute <4 m (LE90), relative <2 m on slopes <=20 % and <4 m above |
| Copernicus GLO-90 | 3 arcsec (about 90 m) | Global land | As GLO-30 | Yes (audit only) | Block mean of GLO-30 reproduces the official product's slope statistics closely in my check (max 27.7 degrees and 0.30 % above 20 degrees in both; 0.037 % against 0.029 % above 25 degrees) |
| SRTM derived "skadi" tiles | 1 arcsec | Global (mixed SRTM and other sources per the tiles page) | Joerd project attribution, SRTM courtesy USGS | Yes (audit only) | Spiky: maximum slope 66.5 degrees in the test window; mean +1.47 m and std 4.31 m against GLO-30 |
| NASADEM, ASTER GDEM v3 | 1 arcsec | NASADEM 60 N to 56 S; ASTER 83 N to 83 S | Openly shared; download needs an Earthdata login | No | Vertical accuracy numbers not retrieved |
| ALOS AW3D30 v4.1 | 1 arcsec | Global land within about 82 degrees latitude | Free after registration, JAXA terms not read | No | A quality flag "Good" at <5 m is not a validated accuracy |
| FABDEM v1-2 | 1 arcsec | Global | CC BY-NC-SA 4.0 (non commercial) | No | Corrects buildings and forests, which does little in open sand |
| TanDEM-X 90 m (DLR) | 3 arcsec | Global | Scientific use, registration | No | |
| ICESat-2 ATL08, GEDI L2A | 100 m segments; 25 m footprints | Tracks only; GEDI 54 N to 54 S | Free, Earthdata login | No | Possible ground truth profiles; none downloaded |
| Sentinel-2 L2A | 10, 20, 60 m | Global, frequent | Free, full and open | Catalogue search only | Imagery for dune context, not slope |
| Landsat 8/9 | 30 m | Global | No restrictions stated | Not downloaded | |
| Maxar Open Data | sub metre class (figure not stated on the page read) | Event based; no Gulf event found | CC BY-NC 4.0 | Catalogue only | |
| Planet NICFI, Pleiades Neo | n/a | n/a | Planet terms not verified; Pleiades Neo commercial | No | Not usable as open data |
| Abu Dhabi SDI open data (habitat and geology polygons) | vector | Abu Dhabi emirate | Licence field empty in service metadata | Metadata only | No elevation layer found |

**Not found.** Open airborne LiDAR or drone elevation models of Liwa or the Rub' al Khali dunes; any gridded sand colour or grain size map of the Empty Quarter; any open sub metre stereo for the region.

**Can slip faces and crests be resolved?** Evidence for the answer, all of it my arithmetic or computation unless marked published:

- Published dune sizes: Liwa dunes 50 to 80 m high (Lorenz et al., abstract); northern Rub' al Khali complex linear dunes 50 to 100 m (Lancaster et al., abstract); published mean wavelengths 0.63 to 3.17 km (USGS Professional Paper 1052 Landsat morphometry; `morphology_rows.csv`). At 30 m posting that is 20 to 110 posts per wavelength: well resolved. Small simple linear dunes of 10 to 25 m height and 200 to 300 m spacing (a secondary summary, to be re verified) are 7 to 10 posts at 30 m and 2 to 3 at 90 m.
- A slip face at 32 degrees has a horizontal run of about 1.6 times its height, so a 50 m dune face spans about 80 m, 2.7 posts at 30 m. In the Rub' al Khali window, runs of consecutive posts steeper than 25 degrees had a median length of 2 posts (90th percentile 4; 45 % a single post).
- A synthetic test of an ideal 32 degree face sampled at 30 m with random phase (SIMULATED BY ME, optimistic because it samples points rather than averaging over cells) recovers full steepness only if the face is 30 m or higher by forward difference (50 m or higher by central difference). A 10 m face reads as 9 to 18 degrees and a 20 m face as 18 to 26 degrees. At 90 m, even 50 m faces read 16 to 23 degrees.
- **Verdict.** Dune crests, ridges and interdune corridors of the large Liwa and Rub' al Khali dunes: resolved at 30 m. Slip faces of dunes above about 40 to 50 m: marginal, located as thin bands of high slope but biased low. Slip faces of dunes below about 20 m, brink sharpness, ripples (centimetre wavelength) and small barchans of 1 to 7 m: not resolved, and the barchans are at or below the published vertical error. A planner reading 30 m slope alone will under flag lee faces.
- **Caveats.** GLO-30 is a radar surface model; the size of X-band bias over dry sand was not retrieved. The epoch (2010 to 2015) is stale for fast small dunes (over 20 m/yr in Kuwait). No lidar truth was available, so slip face bias is estimated by synthetic and cross product comparison only.

---

## 6. UAE context (factual background; every item checked against retrieved sources, see `research/raw/uae_facts.csv`)

- **Rashid 1** (MBRSC, about 10 kg, four wheels, designed for slopes up to 20 degrees and rocks 10 cm high) never operated: the ispace Hakuto-R Mission 1 lander failed to land on 2023-04-26 (JST), which ispace attributed to altitude sensor handling in software (UAE01, UAE02, UAE10, UAE11).
- **Rashid 2** is built and was shipped to the US for Firefly's Blue Ghost Mission 2 (lunar far side). Launch dates conflict between sources (2026 in late-2025 coverage, not earlier than 2027 in an October 2026 report), so no flight data exist and the date is unresolved (UAE14, UAE15, UAE17).
- **Wheel work.** Khalifa University and MBRSC published single wheel rig results for the Rashid wheel on a lunar regolith sample (slip 0 to 0.75, sinkage about 1 to 2 cm, drawbar 5.2 to 24.1 N, UAE04, UAE06) and wheel and grouser studies (UAE07, UAE08). These concern lunar simulant, not Arabian sand.
- **Desert ground vehicles.** A TII desert unmanned ground vehicle (page date ambiguous, 2023 or 2025) and, at UMEX in January 2026, SteerAI's xRift (debuted 20 January 2026) and a Space42 vehicle (25 degree slope capability stated) were shown; the retrieved pages give no slip, sinkage or dune traversability data (UAE22 to UAE25).
- **Programmes that are not mobility evidence.** Hope is an orbiter (UAE19, UAE20); Mars Science City was announced as a simulated settlement with 3D-printed desert sand domes and its article does not mention rover testing (UAE21); the Emirates Robotics Competition task is indoor (UAE26).
- **Not verified or not found:** Rashid 2 wheel design, current Rashid 2 launch date, any rover testing on UAE dunes by UAE universities, current Mars Science City status. The 1963 archive item on wheeled vehicle sand trials could not be read.
- Thermal and dust effects on these vehicles are out of scope; see `hudasol/dhill`.

---

## 7. Gap analysis

### 7.1 Where lab to field transfer fails or is untested

1. **Every quantitative sand slope result is lab, a prepared Earth sand bed (SIM-012, SIM-013; the unit of the slope term is not stated in its source) or Mars, except one Earth dune curve from Dumont Dunes, California, for a 340 kg rover with no soil parameters reported (FLD-HV13-1, FLD-HV13-2); none is Arabian dune sand.** Lab slope beds use simulants or Toyoura sand, mostly small wheels (exception: the 400 kg Scarab, FLD-027, FLD-028) and slow speeds (FLD-027 to FLD-035, LEG-017 to LEG-020, TM-022 to TM-024). Mars field data are low gravity and on megaripples, crusts and sulfates (FLD-001 to FLD-025, apart from the Earth tilt bed rows FLD-006 to FLD-008).
2. **Engineering tables transferred from a lab bed work on uniform sand and fail on mixed or hidden weak ground** (field notes, Maimone et al.). The Spirit pair (15 to 20 % versus 95 % slip on terrain with no visible difference, FLD-011, FLD-012) shows the pattern; the source does not state the cause.
3. **Model validation uses in sample or borrowed parameters.** The rover scale slope error fell from 25.9 to 0.49 % only after tuning on the same case (TM-023, TM-024); DEM and SCM fits are calibrations (SIM-005, SIM-015, SIM-018).
4. **The quasi static models are outside their validated envelope when driving is fast or transient** (TM-018, TM-019, TM-021).
5. **Learning evidence is in distribution.** Hold outs are random, temporal or by sol, never by terrain type (LRN-003, LRN-007, LRN-009, LRN-015). The one held out soil result is a simulation (LRN-016).
6. **The field slip sensor is unreliable on exactly the terrain of interest.** Visual odometry degrades on featureless sand (FLD-041), and different papers define slip differently (wheel odometry, visual odometry, velocity based, distance based), so numbers are not interchangeable.

### 7.2 What is missing for dune terrain specifically

1. A **slip versus slope dataset with a wheeled vehicle on dune sand with complete soil and wheel description** and independent ground truth position. None found.
2. **Behaviour on and near the slip face**: avalanching and shear collapse near the angle of repose. Slope induced shear collapse is shown only for a foot on silica sand (sinkage 13 mm at 0 degrees to 36 mm at 35 degrees, SIM-022, SIM-023) and in a few legged tests. Simulators that omit it will under predict.
3. **Arabian sand properties**: grain size, rounding, packing, moisture and cementation below the surface, and Bekker or RFT constants. Nearest values are Kuwaiti barchans (mean grain 0.23 mm) and a Brazilian dune (d50 about 0.2 mm), not Gulf dunes (`morphology_rows.csv`).
4. **Dune scale terrain data at the resolution that matters** (open, metre scale elevation). None open for the region; GLO-30 under resolves slip faces (section 5).
5. **A common slip definition and a shared benchmark** so that rows can be compared.
6. **Dynamic effects**: crosswind and lateral slip on crests, slope at speed, repeated passes on the same track (not covered by any retrieved row).
7. **Tracked and legged vehicles on real dunes**, and any same vehicle comparison of the three.

### 7.3 What a minimal open data planner needs that the literature does not provide

- A slip law whose constants come from **measurements on the target sand and the target vehicle**, with stated uncertainty. This project supplies the structure and an analysis plan (sections 8 and 9) but not the constants.
- A **slip face and crest detector** that does not rely on a 30 m slope value: aspect, curvature, dune height and optical imagery are the open candidates, but none has been validated here.
- A **way to carry the assumption uncertainty into the plan**, for example by treating a route as acceptable only if it is acceptable across the plausible parameter range, which is what the sensitivity analysis in section 8 suggests is necessary.
- An **onboard log** (section 9.5) that lets the vehicle correct the model as it drives.

