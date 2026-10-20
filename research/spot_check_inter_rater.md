# Inter rater spot check (blinded), drawn 2026-10-20

Twenty rows drawn at random (seed 20261025) from the 494 rows of `research/evidence.csv`. The verifier's verdict is hidden.
For each row: open the source at the link, find the passage named under *where*, and check the value, unit, slope, vehicle or terrain, and validation type.
Write one verdict per row in `research/spot_check_inter_rater_ratings.csv` (correct, minor_error, material_error or unverifiable) with a short note, then run `python3 scripts/inter_rater_agreement.py`.
Definitions: material error = wrong value, unit, metric meaning, validation type, vehicle or terrain, or slope; minor error = number right but a label, location or descriptive detail wrong.

## 1. DUN-010
- source: Migration of barchan dunes in Qatar: controls of the Shamal, teleconnections, sea level changes and human impact (Engel, Boesl, Brueckner; Geosciences 8(7), 240, 2018) (https://mdpi-res.com/d_attachment/geosciences/geosciences-08-00240/article_deploy/geosciences-08-00240.pdf)
- where: Section 4.1 Barchan migration, page 9, Fig. 8; methods Section 3 pages 6 to 7, Table 1
- vehicle or wheel: not applicable (terrain property)
- terrain: 16 barchans (B1 to B16), south east Qatar, time window 1965 to 1995
- slope: not reported
- metric: migration rate range across the 16 dunes, 1965 to 1995
- value and unit: 0.4 (B1) to 2.1 (B12) m/month
- validation type: none

## 2. DUN-017
- source: A study of global sand seas (McKee, ed.; USGS Professional Paper 1052, 1979): chapter F, Dune forms and wind regime (Fryberger with Dean) and chapter J, Regional studies of sand seas using Landsat imagery (https://pubs.usgs.gov/pp/1052/report.pdf)
- where: Chapter F, Table 16 and text, report page 150
- vehicle or wheel: not applicable (terrain property)
- terrain: Northern Arabian sand seas: Saudi Arabia and Kuwait (An Nafud, north), 10 stations
- slope: not applicable
- metric: average annual drift potential (10 stations); energy class thresholds used
- value and unit: 489; low < 200, intermediate 200 to 399, high at least 400 vector units
- validation type: none

## 3. ENV-006
- source: Airborne Particle Classification in LiDAR Point Clouds Using Deep Learning (Stanislas, Nubert, Dugas, Nitsch, Sunderhauf, Siegwart, Cadena, Peynot; Field and Service Robotics 2019, EasyChair preprint 1443) (https://easychair.org/publications/preprint/TCpW)
- where: Table 5 and Sec. 5.5.2 Obstacle Detection Task
- vehicle or wheel: Clearpath Husky with Velodyne HDL-32E lidar
- terrain: Outdoor scenes with dust and fog; 2D occupancy grid 30 m by 30 m at 0.4 m resolution, obstacle if height difference above 0.3 m
- slope: not applicable
- metric: false obstacle cells prevented; true obstacle cells removed
- value and unit: 96% prevented, 0.4% removed (point); 89% prevented, 0.1% removed (voxel) % of cells
- validation type: field

## 4. FLD-018
- source: Curiosity Rover Mobility Issues: Crossing Martian Megaripple Fields (Arvidson, Maimone, Gildner, Hines; LPSC 2016 poster abstract 1137) (https://www-robotics.jpl.nasa.gov/media/documents/lpsc_2016_arvidson_ripple_crossing.pdf)
- where: Left column bullets, sol 1181-1185 crossing experiments
- vehicle or wheel: MSL Curiosity (6 wheels; ~0.5 m wheel diameter per Li and Lewis 2022 Fig. 1 scale bars)
- terrain: Megaripple field, Gale Crater, Mars (sol 1181 controlled crossing)
- slope: slightly uphill (value not reported)
- metric: rover 3D slip over ~8 m of shallow megaripple sand
- value and unit: exceeded 70 in places %
- validation type: field

## 5. FLD-026
- source: Driving Strategies Used During Perseverance Rapid Traverse Campaign (Rankin et al., 2023) (https://robotics.jpl.nasa.gov/media/documents/2023-rapid-traverse.pdf)
- where: Section 6/7 text around 'sand ripples near the preferred path'
- vehicle or wheel: Perseverance (Mars 2020)
- terrain: Small sand ripples near preferred path, Jezero crater floor, Mars (Rapid Traverse)
- slope: not reported
- metric: wheel slip over small ripples
- value and unit: not quantified; described as insignificant n/a
- validation type: field

## 6. FLD-041
- source: Self-driving rovers tested in Mars-like Morocco (ESA, 2018-12-19) (https://esa.int/Our_Activities/Space_Engineering_Technology/Self-driving_rovers_tested_in_Mars-like_Morocco)
- where: Quote paragraph by G. Visentin
- vehicle or wheel: ESA/DFKI rover field campaign (Mana, Minnie, SherpaTT)
- terrain: Sahara dunes near Erfoud, Morocco (Dec 2018 field test)
- slope: not reported
- metric: vision-feature tracking on smooth dunes
- value and unit: difficult; algorithms behaved unexpectedly (qualitative) n/a
- validation type: field

## 7. FLD-HV13-6
- source: Traverse Performance Characterization for the Mars Science Laboratory Rover (Heverly et al. 2013, J. Field Robotics 30(6), 835-846) (https://doi.org/10.1002/rob.21481)
- where: Abstract p. 835; Section 9 p. 844 to 845 and Figure 17; Section 10 p. 845
- vehicle or wheel: Curiosity (MSL flight rover on Mars, 899 kg)
- terrain: Hummocky well consolidated soil at Gale Crater, Mars, first 250 sols, 723 m driven as of 1 May 2013
- slope: not stated
- metric: Agreement of Curiosity slip vs slope data on Mars with Earth based DTM and Scarecrow cohesive soil test data
- value and unit: good agreement (qualitative; no numeric error reported) qualitative
- validation type: field

## 8. LEG-004
- source: Sensitive dependence of the motion of a legged robot on granular media (https://arxiv.org/abs/0905.4950)
- where: Results, text around Fig. 1d,e (vx ~2 cm/s at phi=0.600)
- vehicle or wheel: SandBot hexapod (2.3 kg), same gait, leg frequency 16 rad/s, loosely packed bed
- terrain: Lab fluidized-bed trackway of ~1 mm poppy seeds, volume fraction 0.600
- slope: 0 (level)
- metric: mean forward speed
- value and unit: 2 cm/s
- validation type: lab

## 9. MAP-010
- source: Stanley: The Robot that Won the DARPA Grand Challenge (Thrun et al., Journal of Field Robotics 23(9), 2006) (https://pages.cs.wisc.edu/~dyer/cs540/handouts/thrun.stanley05.pdf)
- where: Sec. 5 Laser Terrain Mapping, paragraph after Figure 9
- vehicle or wheel: Stanley, modified Volkswagen Touareg with five roof lidars
- terrain: reference dataset of labelled terrain (location and course not specified in the passage)
- slope: not reported
- metric: fraction of known drivable area classified as obstacle
- value and unit: 12.6 %
- validation type: field

## 10. MAP-022
- source: The Effect of DEM Resolution on Slope Estimation and Sediment Predictions (Sadeghi, Beeson, Lang, Tomer; conference poster, SWAT conference) (https://swat.tamu.edu/media/40684/sadeghi.pdf)
- where: Poster Table 1 (Values assigned by the GIS interface); abstract text '100% increase in slope from the 90m to 3m DEMs'
- vehicle or wheel: not applicable (terrain map derivation)
- terrain: South Fork of the Iowa River agricultural watershed; DEMs at 3 m (lidar), 10, 30 and 90 m
- slope: average 0.0115 to 0.0301 m/m (gentle)
- metric: average slope at 3 m versus 90 m DEM
- value and unit: 0.0301 (3m) versus 0.0115 (90m) m/m
- validation type: none

## 11. MAP-033
- source: Aeolian dune modelling from airborne LiDAR, terrestrial LiDAR and Structure from Motion-Multi View Stereo (Grohmann, Garcia, Affonso, Albuquerque; arXiv 1910.06186 v3, 2020; published in Computers and Geosciences 143:104569) (https://arxiv.org/abs/1910.06186)
- where: Sec. 3.1 TLS and SfM-MVS, paragraph beginning 'The vertical accuracy of the SfM-MVS DEM'; Sec. 4 Discussions and Conclusions
- vehicle or wheel: Small drone (remotely piloted aircraft) photogrammetry versus terrestrial laser scanner, as a source of rover maps
- terrain: Coastal dunefield, southern Brazil, February 2019; 810 photos from 100 m, DEM gridded at 10 cm
- slope: not reported
- metric: vertical accuracy of drone DEM against terrestrial lidar DEM (RMSE and MAE)
- value and unit: RMSE of 0.08 m and MAE of 0.06 m m
- validation type: field

## 12. MOB-034
- source: Performance of Soils Under Tire Loads, Report 2: Analysis of Tests in Yuma Sand Through August 1962, Technical Report 3-666 (Powell, Green; Waterways Experiment Station, August 1965) (https://apps.dtic.mil/sti/pdfs/AD0621045.pdf)
- where: Para. 5
- vehicle or wheel: not applicable (soil characterisation)
- terrain: Yuma desert sand
- slope: not applicable
- metric: direct shear friction angle range, air-dry Yuma sand
- value and unit: 35.1 to 38.2 deg
- validation type: none

## 13. MOB-041
- source: A Technique for Estimating the Slope-Climbing Ability of Wheeled Vehicles in Sand, Miscellaneous Paper 4-535 (Waterways Experiment Station, October 1962; S. J. Knight and a co-author whose name is illegible in the scan) (https://apps.dtic.mil/sti/pdfs/AD0744214.pdf)
- where: Paras. 13 and 20
- vehicle or wheel: 2-1/2 ton truck with 11.00-20 tires
- terrain: Desert dune and beach sands
- slope: not reported
- metric: residual spread in slope at the same dimensionless vehicle parameter
- value and unit: as great as a 3 percent slope
- validation type: field

## 14. MOB-057
- source: The Rolling Resistance and Sinkage of Towed Dual Wheel Combinations in Sand (Hetherington, Littleton; ISTVS International Conference on the Performance of Off-Road Vehicles and Machines, 1984 per DTIC stamp; DTIC component part AD-P004 261) (https://apps.dtic.mil/sti/pdfs/ADP004261.pdf)
- where: p. 85, Discussion; p. 82 wheel sizes (page placed by folio order); p. 83 theory
- vehicle or wheel: Towed rigid model wheels, 0.047 m wide (0.25 m and 0.3 m diameter) and 0.072 m wide (0.3 m diameter), single and dual
- terrain: Dry Calne sand, laboratory soil bin
- slope: 0 (level)
- metric: predicted versus observed benefit of dual wheels in rolling resistance
- value and unit: predicted benefit considerably more than that actually observed qualitative
- validation type: lab

## 15. PLN-010
- source: Mars Curiosity Rover Mobility Trends During the First Seven Years (Rankin, Maimone, Biesiadecki, Patel, Levine, Toupet; J. Field Robotics 2021, accepted manuscript) (https://www-robotics.jpl.nasa.gov/media/documents/ROB-20-0040_R3.pdf)
- where: Sec. 3.1, Table 7
- vehicle or wheel: MSL Curiosity (6 aluminium wheels, 50 cm diameter, 40 cm width, rocker bogie)
- terrain: Gale crater, Mars; all terrain driven sols 1 to about 2488
- slope: not reported
- metric: average of maximum rover slip per sol
- value and unit: 16.69 %
- validation type: field

## 16. SND-009
- source: Physicochemical characterization and origin of aeolian sand dunes in southeastern Qatar: a comparative study with Mediterranean sand dunes (Al-Awah and Matter; Advances in Geosciences 63, 1 to 13, 2023) (https://adgeo.copernicus.org/articles/63/1/2023/adgeo-63-1-2023.pdf)
- where: Section 3.1.2 Chemical composition by XRF, page 6
- vehicle or wheel: not applicable (terrain property)
- terrain: Southern Qatar dunes, areas A and B
- slope: not reported
- metric: SiO2 range (area A; area B) and CaO average (A; B)
- value and unit: SiO2 58.1 to 74.5 (A), 63.7 to 74.9 (B); CaO average 18.3 (A), 13.2 (B) percent
- validation type: none

## 17. TM-TK2
- source: Grouser wheel high-speed traction performance: DEM simulation and experimental result (Takehana et al., J. Terramechanics 120, 101084, 2025) (https://doi.org/10.1016/j.jterra.2025.101084)
- where: Section 7.3, p. 7 (0.03) and Section 7.4, p. 8 (0.1 and 0.2), text on Figs. 7b and 8b
- vehicle or wheel: Slick (non-grouser) wheel, 180 mm diameter, PLA, 50 N vertical load
- terrain: Tohoku Silica Sand No. 5, prepared bed, tilled and levelled, sand height 0.3 m in 6.85 m x 0.5 m x 0.4 m sandpit
- slope: not reported
- metric: traction efficiency (Fx*vx / T*omega) versus translational speed
- value and unit: approximately 0.03 at 1.0 m/s (slip above 0.25); approximately 0.1 at 0.5 m/s; approximately 0.2 at 0.2 m/s dimensionless
- validation type: lab

## 18. TM3-029
- source: Design of a special rigid wheel for traversing loose soil (Elsheikh; Scientific Reports 2023, 13:171) (https://doi.org/10.1038/s41598-022-27312-6)
- where: Results, Table 2 (columns Push force Fp and Net traction force NT)
- vehicle or wheel: Serpentine edge rigid PLA wheel, 100 mm diameter, 5 mm thickness, 44 mm breadth, 80 g, static load 8 N, 20 rpm, on a single wheel tester
- terrain: Beach sand from Port Said (Egypt) in bin 1 m x 0.25 m x 0.12 m with transparent side, filled uniformly with loose soil
- slope: 0 (level)
- metric: net traction force at sinkage heights 10, 20, 40 percent of wheel diameter
- value and unit: 3 (10%); 7 (20%); 9 (40%) N
- validation type: lab

## 19. TM3-056
- source: Aircraft Tire Behavior During High-Speed Operations in Soil (Leland, Smith; NASA TN D-6813, August 1972) (https://ntrs.nasa.gov/citations/19720020356)
- where: Results, 'Comparison of clay and sand data' paragraphs and Figure 20 (report p. 14; PDF p. 16); sand bed preparation p. 9 (PDF p. 11)
- vehicle or wheel: 29 x 11.0-10 8 ply type III aircraft tyre, 74 cm diameter, 28 cm wide, towed on SAXLE carriage; rated load 22 kN; inflation 48, 31 and 21 N/cm2 (70, 45, 30 lb/in2)
- terrain: Langley landing loads track sand test bed: locally obtained poorly graded medium river sand, graded and compacted; two test lanes
- slope: 0 (level)
- metric: free rolling axle drag coefficient versus speed in sand at three inflation pressures
- value and unit: drag versus speed similar in shape to clay but smaller in magnitude qualitative
- validation type: lab

## 20. TM3-071
- source: Performance of Wheel-Typed Vehicle with Crawlers in Between Front and Rear Wheels on Soft Ground (Eto, Satomi, Takahashi; Journal of Robotics and Mechatronics 2014, 26(2):261) (https://doi.org/10.20965/jrm.2014.p0261)
- where: Development report, text with Figures 2 and 3 (single page)
- vehicle or wheel: Model wheeled vehicle with independently driven front and back wheels, optionally with an active intermediate crawler between them; speed fixed at 20 mm/s over 1000 mm (vehicle size not stated)
- terrain: Dry silica sand test lane, same preparation for both configurations
- slope: 0 (level)
- metric: slip ratio of the wheeled vehicle without and with the intermediate crawler on dry sand
- value and unit: 1 (wheels only, did not move); 0.065 (with crawler) ratio
- validation type: lab
