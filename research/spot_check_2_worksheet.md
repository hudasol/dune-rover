# Spot check 2: five more rows for the author

Rows drawn at random (seed 20261015), one per area, excluding the five rows already checked. For each row: open the source link, go to the passage named, and fill the last line. Mark correct, wrong or unclear and write what you saw. Do not trust the table; read the paper.

Checklist per row: value, unit, slope, terrain, vehicle or wheel, validation type (lab means a prepared bed, field means natural terrain, simulation only means a model).

## 1. TM-007 (terramechanics)

- Vehicle or wheel: Pairs of cylindrical and four-arm lug wheels of different sizes, masses and speeds (dimensions in paper Table I, not extracted)
- Terrain: Quikrete medium sand bed, dry; sandpaper-covered cylindrical wheels
- Slope: 0 (level)
- Metric: Deviation of best-fit slope of scaled big-vs-small wheel data from the predicted value of 1
- Value: 3 % (max, over six datasets)
- Validation type: lab
- Source: General scaling relations for locomotion in granular media (Slonaker et al., arXiv 2016/PRE 2017)
- Link: https://arxiv.org/abs/1604.02490
- Passage: Experiments section, text after Fig. 4 (lug-wheel pair results) and abstract
- Result (correct, wrong or unclear) and what you saw: 

## 2. SIM-008 (simulation)

- Vehicle or wheel: Yutu-type six-wheel grouser rover, ~120 kg, wheelbase 1.136 m
- Terrain: DEM bin 14 x 2.5 x 0.375 m with ~15 million particles; v=1 m/s, slip 0 to 0.8, 10 s per run
- Slope: 0
- Metric: Wall-clock for 10 s full-rover run: DEM vs SCM
- Value: DEM 10000 s (about 3 h); SCM 20 s (RTF about 1000 vs 2, derived by me) s wall per 10 s sim
- Validation type: simulation-only
- Source: Using high-fidelity discrete element simulation to calibrate an expeditious terramechanics model in a multibody dynamics framework (Zhang et al. 2024)
- Link: https://arxiv.org/abs/2407.18903
- Passage: Sec 4.2, p.20; Conclusions
- Result (correct, wrong or unclear) and what you saw: 

## 3. LRN-015 (learning)

- Vehicle or wheel: Boston Dynamics Spot quadruped (joint position, velocity, effort)
- Terrain: Lava-tube floors (steep, sandy sloping floors in Mammoth Cave), limestone cave, dusty LA subway terminal; six runs of ~30 min
- Slope: described as steep/sloping; not reported numerically
- Metric: slip prediction precision / recall / F-score (current time); with 720 ms look-ahead
- Value: 95% / 80% / 0.84; 95% / 77% / 0.82 at 720 ms ahead %, F-score
- Validation type: field
- Source: PrePARE: Predictive Proprioception for Agile Failure Event Detection in Robotic Exploration of Extreme Terrains
- Link: https://arxiv.org/abs/2208.00322
- Passage: Sec. IV Time-delay embedding and Future prediction (text before Fig. 5-6); abstract
- Result (correct, wrong or unclear) and what you saw: 

## 4. FLD-032 (field)

- Vehicle or wheel: Four-wheel rover, 2 driven front wheels, 23 kg, wheel 296 mm dia x 90 mm, 12 fixed grousers of 20 mm
- Terrain: Indoor sandbox, 0.725 m3 dry Toyoura sand 250 mm deep, incline 0-30 deg, Earth
- Slope: 10
- Metric: maximum sinkage angle, 20 mm grouser
- Value: 127 deg
- Validation type: lab
- Source: The Effect of Assistive Anchor-Like Grousers on Wheeled Rover Performance over Unconsolidated Sandy Dune Inclines (Sensors 2016, 16(9):1507)
- Link: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5038780/
- Passage: Section 4.1 (Figure 12b)
- Result (correct, wrong or unclear) and what you saw: 

## 5. LEG-001 (legged)

- Vehicle or wheel: SandBot RHex-class hexapod (total mass 2.3 kg; c-legs R=3.55 cm, hip height 2.5 cm), hard-ground clock (HGK)
- Terrain: Lab fluidized-bed trackway of ~1 mm poppy seeds, volume fraction 0.605 (model granular medium, not natural sand)
- Slope: 0 (level)
- Metric: mean forward speed
- Value: 2 cm/s
- Validation type: lab
- Source: The effect of limb kinematics on the speed of a legged robot on granular media
- Link: https://arxiv.org/abs/1303.7276
- Passage: Sec. 3 (Methods and Results), Fig. 2c caption (HGK speed ~2 cm/s)
- Result (correct, wrong or unclear) and what you saw: 
