# Sand test protocol: simple tests at every station and in a laboratory

**Status: DRAFT, PLANNED. No test in this document has been run. No number in it is a measurement of the field site.** Written 2026-10-21 to support section 3 of `docs/FIELD_VALIDATION_PLAN.md` and the "Sand characterisation" line of `docs/FIELD_DAY_CHECKLIST.md`.

Labels (the three labels of the repository): every number quoted from a retrieved source is **PUBLISHED**; every item marked (derived) or (design, no retrieved source), and every procedure, is **PLANNED** (a design value of this protocol, not a measurement).

Rules used in this draft:

- Every method cites a retrieved source (keys in brackets; full list in `research/phase4/protocols_references.csv`). A step that no retrieved source supports is marked **(design, no retrieved source)**; a number computed here is marked **(derived)**.
- ASTM standards are named only where the official ASTM page showing the title was retrieved. In every such case **only the free summary page (scope) was read; the full standard was not read**, so no step below is claimed to follow it.
- Expected ranges in section 7 are copied exactly from `research/evidence.csv` (SND rows), with the row id and the phase 3 verification status.
- Do not invent soil parameters: a quantity that was not measured is recorded as `unknown` (checklist).

## 1. Overview: what, where and how often

| Test | Where | Repeats (minimum) | Main source |
|---|---|---|---|
| Angle of repose, fixed funnel | field (on a board) or laboratory | 3 per site (checklist and plan); 5 recommended (section 2.2) | [kajiyama2024], [pawlowski2025] |
| Angle of repose, tilting box | laboratory or field table | 3 per site | design, no retrieved source describes it in full |
| Bulk density, core or ring | each station, 0 to 7.6 cm | 3 per station (plan; [nrcs_ssir42] collects three cores per layer) | [nrcs_testkit], [nrcs_ssir42] |
| Bulk density, known volume cup or excavation | each station, very loose surface sand | 3 per station | [nrcs_ssir42], [nrcs_testkit] |
| Moisture content, oven drying | samples from each station, 0 to 2 cm and 5 to 10 cm | 2 per depth (design) | [nrcs_ssir42], [astm_d2216] |
| Moisture content, field microwave or scale only | as above | 2 per depth (design) | [nrcs_testkit] |
| Particle size distribution, dry sieving | 1 per station, 3 per site (plan) | as stated | [nrcs_ssir42], [astm_d6913] |
| Direct shear, friction angle | laboratory only | 3 or more normal stresses per density state | [astm_d3080], [hamid2013], [deiminiat2022] |

Sample handling for all tests: sealed, labelled bags (station id, depth, time); keep moisture samples sealed and out of the sun until weighed **(design)**.

## 2. Angle of repose

### 2.1 What the sources say about the method

- There is no standard method for sand. Kajiyama et al. (2024, section 1) state that "there are no standardized methods for making a sand heap", that the three main methods are "discharge, revolving cylinder and piling", that "even with the same sample, different values of angle of repose can be obtained with these different experimental methods", and that an ASTM attempt to standardise the test "was discontinued because of its limited applicability (ASTM, withdrawn 2005)". The ASTM page of that withdrawn method was not retrieved.
- In a cone shaped heap "the apex of the sand heap is not always located at the centre ... so that observation from only one direction is insufficient"; they photographed each heap with two orthogonal cameras (Kajiyama et al. 2024, sections 1 and 2.1).
- The static angle of repose is "a measure of the angle of the pile created by the material free flow on a stationary surface"; the dynamic angle (rotating drum) gives higher values (Pawlowski et al. 2025, section 1). Only the static angle is measured here.
- Scale and method matter: pouring 16 g samples through small funnels gave 21.58 degrees for sand and 35.58 degrees for a lunar simulant, while 500 g tests of the same simulant in another study gave 37.5 plus or minus 3.4 degrees (Louca et al. 2024, section 3.2). Small funnel and small sample tests are therefore avoided here.

Consequence: a repose value is only comparable with values from the same method, apparatus and sample state. Always report the method with the number.

### 2.2 Method A: fixed funnel on a flat base (design based on the piling method class in [kajiyama2024])

Equipment: a funnel with a smooth wall, held by a clamp stand at a fixed height; a rigid flat base board larger than the heap, with sand of the same sample glued to its surface **(design)**; spirit level; ruler; two phones or cameras on tripods at 90 degrees to each other, level with the base, each with a scale in frame; sample of at least 500 g, dried (record the drying method) or at field moisture (record the moisture); a scoop.

Steps:

1. Level the base board with the spirit level. Clamp the funnel with its outlet a fixed height above the board and record that height.
2. Pour the sample slowly and steadily into the funnel so that the heap grows from its apex. Stop when the apex reaches the funnel outlet **(design)**.
3. Without touching the heap, photograph it from the two orthogonal cameras.
4. Measure the heap height h at the apex and the base diameter d along the two camera directions (four radii). Compute the angle for each direction as atan(2h / d) for a symmetric cone **(derived geometry)**, and also measure the slope line directly on each photograph with the scale. Report both.
5. Clear the board and repeat with fresh sand from the same bag.

Repeats: at least 3 per site (checklist); 5 are recommended because the reported repeatability of a purpose built apparatus was 0.26 to 0.89 degrees (sample standard deviation of five silica sands, Silica A to E, Kajiyama et al. 2024, results table), and a hand held field version is unlikely to be better **(design inference)**.

Data sheet: `site_id, station_id, sample_id, test_id, method (fixed funnel), funnel_outlet_diameter_mm, funnel_height_mm, sample_mass_g, sample_state (oven dry, air dry, field moist), moisture_pct, h_mm, d1_mm, d2_mm, d3_mm, d4_mm, angle_from_h_d_deg, angle_photo_cam1_deg, angle_photo_cam2_deg, air_temp_c, wind (calm or not), photo_ids, operator, notes`.

### 2.3 Method B: tilting box (design, no retrieved source describes it in full)

Equipment: a rigid box with one open side or a clear front, at least ten times wider than the coarsest grain **(design)**, hinged on a board; an inclinometer or phone inclinometer fixed to the box; a level.

Steps:

1. Fill the box with sand by pouring without compaction, strike the surface flat, and level the box.
2. Tilt slowly and steadily. Record the tilt at the first general slide of the surface (angle of maximum stability).
3. Stop, let the surface come to rest, and measure the angle of the remaining surface against horizontal with the inclinometer on a straight edge (angle after avalanche).
4. Refill and repeat.

Repeats: 3 per site. Data sheet: `site_id, station_id, sample_id, test_id, method (tilting box), box_length_mm, box_width_mm, fill_depth_mm, sample_state, moisture_pct, tilt_rate (slow by hand or motor), angle_first_slide_deg, angle_after_avalanche_deg, photo_ids, notes`.

Results of Method B are not comparable with Method A (section 2.1).

### 2.4 Field check on the natural slip face (design)

At each dune used, place a straight edge of about 1 m on the undisturbed slip face from the crest side, never from below (checklist, Safety 1), and read the inclinometer at 5 points along the face. This is a field slope measurement, not a laboratory repose angle, and is reported separately.

## 3. Bulk density

### 3.1 Sources

- Field ring method: a 3 inch diameter ring driven "beveled edge down, to a depth of 3 inches", with four measurements of ring height above the soil to fix the exact sample depth; the sample is trimmed flush, bagged, weighed, and a subsample dried to get water content and dry mass; "Soil bulk density (g/cm3) = oven dry weight of soil / volume of soil" [nrcs_testkit, chapter 4, steps 1 to 8 and Calculations]. 3 inches is 7.62 cm **(derived conversion)**.
- Laboratory core method 3B6a: a cylinder "pressed or driven into the soil", "Samples are collected in triplicate", dried "in an oven at 110 degrees C until weight is constant"; interferences: "compaction of the sample is a common problem" and can be seen by comparing the soil surface inside and outside the cylinder; for loose soil "If soil is too loose to remain in the liner, use core sampler without the inner liner ... Moisture cans may also be pushed directly into a prepared face"; Db = (ODW - RF - CW) / [CV - (RF / PD)], reported to 0.01 g cm-3 [nrcs_ssir42, method 3B6a, sections 3, 3.1, 8 and 9].
- Excavation method for material that a ring cannot hold: dig a bowl shaped hole about 3 inches deep, line it with plastic wrap, fill it with water from a 140 cc syringe to measure the volume, weigh and dry the removed material [nrcs_testkit, chapter 4, "Bulk Density Test for Gravelly and Rocky Soils"].
- ASTM D2937, "Standard Test Method for Density of Soil in Place by the Drive-Cylinder Method" [astm_d2937]: the scope says the method "may not be applicable for soft, organic, highly plastic, noncohesive, saturated or other soils which are easily deformed, compress during sampling, or which may not be retained in the drive cylinder sampler". The full standard was not read. Dry dune sand is noncohesive, so retention in the cylinder must be checked at every sample.
- ASTM D7263, "Standard Test Methods for Laboratory Determination of Density and Unit Weight of Soil Specimens" [astm_d7263], applies to soils "that will retain their shape during the measurement process"; full standard not read. It is listed only to show that loose sand falls outside its intended use.

### 3.2 Method at each station (design combining [nrcs_testkit] and [nrcs_ssir42])

Equipment: thin walled metal ring or cup of known volume (measure inner diameter and height with calipers, 3 times each; record volume), flat steel plate or spatula wider than the ring, flat bladed knife, sealable bags, scale with 0.1 g resolution [nrcs_testkit lists 0.1 g precision], ruler.

Steps:

1. Prepare a flat level spot on undisturbed sand at the station, away from footprints and wheel ruts.
2. Press (do not hammer) the ring vertically into the sand until its top is flush with or just below the surface; [nrcs_ssir42] notes that pressing reduces shattering, and compaction is the main error. Measure the height of the ring rim above the sand surface at four points inside and four outside, to detect compaction (inside surface lower than outside).
3. Dig beside the ring, slide the plate under it, lift, trim flush with the knife, and empty all sand into a labelled bag.
4. If sand runs out of the ring when it is lifted, record "not retained" and use the excavation method of [nrcs_testkit] at a fresh spot.
5. Weigh the bag (field scale) or seal it for weighing later; weigh an empty bag of the same type.
6. Dry and weigh (section 4) and compute dry bulk density = dry mass / ring volume.

Repeats: 3 per station (plan, and the triplicate rule of [nrcs_ssir42]). Depth: surface layer (0 to the ring height); a second layer at 5 to 10 cm if time allows, after removing the surface layer with a flat cut.

Data sheet: `site_id, station_id, sample_id, rep, depth_top_cm, depth_bottom_cm, method (ring, cup, excavation), ring_id, ring_volume_cm3, rim_height_inside_mm (4), rim_height_outside_mm (4), retained (yes or no), bag_mass_g, moist_mass_with_bag_g, dry_mass_g, drying_method, drying_temp_c, dry_bulk_density_g_cm3, moisture_pct, notes`.

Optional derived quantity: relative density Dr from the void ratio, the specific gravity and the maximum and minimum void ratios. The formula is a textbook definition **not taken from a retrieved source in this pass**; the limits in SND-022 were measured on a Saudi dune sand (section 7) and are not the limits of the field site.

## 4. Moisture content

### 4.1 Sources

- Oven drying at 110 degrees C to constant weight [nrcs_ssir42, method 3B6a, section 8.4]. The field plan specifies 105 C (`docs/FIELD_VALIDATION_PLAN.md`, section 3).
- ASTM D2216, "Standard Test Methods for Laboratory Determination of Water (Moisture) Content of Soil and Rock by Mass" [astm_d2216]: the scope gives "the standard drying temperature for this method (110 plus or minus 5 degrees C)" and warns that materials containing gypsum dehydrate slowly at that temperature; "it may be desirable to dry the materials at 60 degrees C or in a desiccator at room temperature". Full standard not read.
- [nrcs_ssir42, 9.2]: gypsum "loses most of its chemically combined water (crystal water) at 105 degrees C".
- Microwave drying for field use: "dry for two or more four-minute cycles at full power", venting one minute between cycles, and weigh after each cycle until the weight no longer changes; water content (g/g) = (moist mass - oven dry mass) / oven dry mass [nrcs_testkit, chapter 4, step 8 and Calculations].

### 4.2 Method (design combining the sources)

Equipment: sealed tins or bags, scale (0.1 g), oven at 105 to 110 C (or 60 C, see below), or a microwave and paper or ceramic cups for the field option.

Steps:

1. At each station take one sample at 0 to 2 cm and one at 5 to 10 cm (plan), two replicates each **(design)**, at least 50 g each **(design)**. Seal at once.
2. Weigh the sealed sample and an empty container of the same type as soon as possible (field scale option: weigh on site).
3. Dry to constant mass: oven at 105 or 110 C, or microwave cycles as in [nrcs_testkit]. If the sand may contain gypsum (for example near sabkha or coastal carbonate dunes), dry a duplicate at 60 C as permitted by the D2216 scope, and report both.
4. Weigh dry. Moisture (percent of dry mass) = 100 x (moist - dry) / dry. State the drying method and temperature with every value.

"Field scale only" means the moist mass is taken on site and drying is done later; it does not mean an estimate without drying. If no drying is possible, record moisture as `unknown`.

Data sheet: `site_id, station_id, sample_id, rep, depth_top_cm, depth_bottom_cm, time_sampled, container_mass_g, moist_mass_with_container_g, dry_mass_with_container_g, drying_method (oven, microwave), drying_temp_c, drying_cycles_or_hours, moisture_pct_dry_mass, surface_crust (yes or no), notes`.

## 5. Particle size distribution by dry sieving

### 5.1 Sources

- [nrcs_ssir42, method 3A1a1a]: the sand fraction "removed from the suspension by wet sieving" is "dried, ... fractionated through a sieve stack, and ... weighed"; the sieve table (section 4.35) lists openings of 1.0 mm (very coarse sand, U.S. No. 18), 0.5 mm (coarse sand, No. 35), 0.25 mm (medium sand, No. 60), 0.105 mm (fine sand, No. 140) and 0.047 mm (very fine sand, No. 300); "Shake on sieve shaker for 3 minutes" and record each fraction "to the nearest mg" (section 8.13). That method treats a 10 g sample with hydrogen peroxide and dispersant first (section 3); it is a laboratory method for soils with fines.
- ASTM D6913/D6913M, "Standard Test Methods for Particle-Size Distribution (Gradation) of Soils Using Sieve Analysis" [astm_d6913]: square opening sieves between 75 mm and 75 micrometres, and "if the maximum particle size is equal to or less than 4.75 mm (No. 4 sieve), then single-set sieving is applicable". Full standard not read.
- For fines below 75 micrometres the D6913 scope points to another method [astm_d6913, 1.4]; dune sands have few fines (SND-027 reports 3.5 percent fines).

### 5.2 Method (design combining the sources)

Equipment: nest of sieves including at least the openings 1.0, 0.5, 0.25, 0.105 (or the nearest available) and 0.075 mm, plus intermediate sieves between 0.105 and 0.5 mm because dune sand falls mostly there (SND-016, SND-021); lid and pan; balance (0.01 g); brush; drying as in section 4.

Steps:

1. Dry the sample (oven or air dry; record which), split it by coning and quartering or a riffle to about 100 g **(design; the mass requirement of the full ASTM standard was not read)**, and weigh it.
2. Stack the sieves, coarsest on top, pour in the sample, shake for a recorded time (mechanical shaker if available). Check completeness by shaking 1 minute more and confirming that no fraction changes by more than 1 percent of the total **(design)**.
3. Weigh each sieve fraction and the pan. The sum must be within 1 percent of the starting mass **(design)**; otherwise repeat.
4. Do not treat with acid: carbonate grains are part of these sands (SND-008, SND-012) and are kept.
5. Compute cumulative percent passing; read d10, d30, d50, d60, d90 by linear interpolation of cumulative percent against the logarithm of sieve opening **(derived method, no retrieved source)**; compute Cu = d60 / d10. If Folk and Ward measures are wanted for comparison with SND-005, SND-006 and SND-031, convert openings to phi, but note that those rows came from laser diffraction (SND-005, SND-006) or sieving at 10 intervals (SND-031).

Repeats: 1 per station, 3 per site (plan).

Data sheet: `site_id, station_id, sample_id, drying_method, split_method, initial_mass_g, shake_time_min, sieve_opening_mm (one column per sieve), retained_mass_g (one column per sieve), pan_mass_g, sum_mass_g, loss_pct, d10_mm, d30_mm, d50_mm, d60_mm, d90_mm, cu, notes`.

## 6. Direct shear (laboratory only, if a laboratory allows)

### 6.1 Sources

- ASTM D3080/D3080M, "Standard Test Method for Direct Shear Test of Soils Under Consolidated Drained Conditions" [astm_d3080]: "Generally, three or more tests are performed on specimens from one soil sample, each under a different normal load"; test conditions "should be selected to represent the field conditions being investigated"; "The rate of shearing must be slow enough to ensure drained conditions". Full standard not read.
- The D3080 minimum specimen width is 10 times the maximum particle size dmax; Deiminiat et al. (2022, abstract) found this "not large enough to eliminate the specimen size effect" and that the ratio needed "is about 60". In their tests the specimens were dry, sheared under three normal stresses (50, 100 and 150 kPa) at "0.015 mm/s (0.9 mm/min)" in a 60 mm x 60 mm x 45 mm box (section 3).
- On a Saudi dune sand (SND-021 to SND-023): dry specimens reconstituted at relative densities of 40, 60 and 90 percent, three normal stresses "(27.8, 55.5 and 83.3 kN/m2)", peak friction angle from the failure envelope [hamid2013, sections 3.3.4 and 5.1.2, Table 5-4]. The thesis states that the tests followed "ASTM D 5321"; that page was not retrieved.

### 6.2 Method (design combining the sources)

1. Dry the sand; record dmax from the sieve analysis. Check the box width: for dune sand with dmax of about 0.5 to 1 mm (from SND-021 and SND-016, an inference), a 60 mm box gives a width to dmax ratio of about 60 to 120 **(derived)**, which meets the ratio of about 60 of Deiminiat et al. (2022).
2. Prepare specimens at two or three target dry densities that bracket the field bulk densities measured in section 3 (for example the loosest and densest field values) by pouring from a fixed low height and tapping or tamping to the target mass in the known box volume **(design)**. Record the achieved density.
3. Shear each density state under at least three normal stresses (D3080 scope). Include the lowest normal stress the apparatus can apply, because a small rover's wheel contact pressure is far below the stresses used in [hamid2013] and [deiminiat2022]; the actual contact pressure of the rover is unknown and must be derived from its measured wheel load and contact patch before the test **(design)**.
4. Shear at a constant slow rate (Deiminiat et al. used 0.9 mm/min in the standard box), recording shear force, horizontal and vertical displacement.
5. Take the peak shear stress at each normal stress and fit a straight line; report the peak friction angle and the intercept (apparent cohesion), and say whether the line was forced through the origin. Deiminiat et al. (2022, section 2) note that fitting without forcing through the origin produces apparent cohesions.

Repeats: 3 normal stresses per density state; repeat one condition to estimate scatter **(design)**.

Data sheet: `lab_id, sample_id, station_id, box_width_mm, box_height_mm, dmax_mm, width_over_dmax, target_dry_density_g_cm3, achieved_dry_density_g_cm3, moisture_state (dry), normal_stress_kpa, shear_rate_mm_min, peak_shear_stress_kpa, displacement_at_peak_mm, residual_shear_stress_kpa, vertical_displacement_at_peak_mm, fit_through_origin (yes or no), friction_angle_peak_deg, intercept_kpa, apparatus, operator, notes`.

## 7. Expected ranges from the repository's evidence table (SND rows)

Values copied exactly from `research/evidence.csv`; `verification` is the phase 3 check result of that row. These are published values for other Arabian dune sands, **not predictions for the field site**.

### Grain size

| Row | Metric (as written) | Value (as written) | Unit | Verification |
|---|---|---|---|---|
| SND-002 | dominant particle size class of modern dune sand | predominantly coarse grained (> 125 µm) | micrometre (size class) | correct |
| SND-005 | graphic mean grain size Mz, area A (16 samples) range and average; area B range and average | A: 1.17 to 2.12, average 1.78; B: 1.61 to 2.20, average 1.98 | phi | correct |
| SND-006 | sorting (inclusive graphic standard deviation): area A range and average; area B range and average | A: 0.37 to 0.79, average 0.53; B: 0.52 to 0.73, average 0.61 | phi | correct |
| SND-016 | mean grain size range over both boreholes | 0.22 to 0.40 | mm | correct |
| SND-017 | sorting coefficient range | 0.54 (moderately well sorted) to 1.07 (poorly sorted) | phi | correct |
| SND-021 | D10; D30; D60; coefficient of uniformity Cu; specific gravity Gs | 0.146; 0.2; 0.29; 1.98; 2.68 | mm; mm; mm; dimensionless; dimensionless | correct |
| SND-027 | specific gravity Gs; fines content | 2.62; 3.5 | dimensionless; percent | correct |
| SND-031 | graphic mean size Mz range of desert dune samples; sorting range | 2.32 to 2.9; 0.4 to 0.55 | phi | minor_error (corrected) |

### Density

| Row | Metric (as written) | Value (as written) | Unit | Verification |
|---|---|---|---|---|
| SND-022 | maximum dry density; minimum dry density; maximum void ratio; minimum void ratio | 1.84; 1.63; 0.68; 0.48 | g/cm3; g/cm3; dimensionless; dimensionless | correct |
| SND-024 | average moisture content; average dry density (point near site office) | 4.64; 1.62 | percent; g/cm3 (printed as gram/cm2) | material_error (corrected) |
| SND-028 | maximum dry density; optimum water content | 1.69; 17 | g/cm3; percent | correct |

SND-023 also records, in its `soil_parameters_reported` column, the dry densities of the shear specimens: "dry density 1.7, 1.75, 1.82 ton/m3 at Dr 40, 60, 90 percent (1 percent silt)". SND-024 is compacted backfill, not a natural dune, and SND-028 is a Proctor compaction value; neither is a natural in place density.

### Moisture

| Row | Metric (as written) | Value (as written) | Unit | Verification |
|---|---|---|---|---|
| SND-019 | maximum gravimetric water content: dune limb; dune crest | 3.72; 3.31 | percent (mass of water per mass of dry sand) | correct |
| SND-029 | surface sand moisture content: first millimetre; third millimetre | 1.8; 0.6 | percent wet weight | material_error (corrected) |
| SND-024 | average moisture content (compacted backfill, see above) | 4.64 | percent | material_error (corrected) |

SND-019 is a maximum over a 10 m borehole profile and SND-029 is the top millimetres after dew; neither is a typical value at 0 to 2 cm or 5 to 10 cm on a dry day. SND-029 is on a wet weight basis while this protocol reports moisture on a dry mass basis.

### Friction angle and penetration

| Row | Metric (as written) | Value (as written) | Unit | Verification |
|---|---|---|---|---|
| SND-023 | peak friction angle at Dr 40, 60, 90 percent (natural sand, 1 percent silt) | 45; 46; 48 | deg | material_error (corrected) |
| SND-025 | DCP index as relative density rises from 40 to 90 percent | 63 to 8 | mm/blow | material_error (corrected) |
| SND-026 | friction angle correlation for natural sand (1 percent silt) | phi = 40 - 0.126(DCPI) (R2 0.99); phi = 0.14(Dr) + 27 (R2 0.96) | deg (DCPI in mm/blow, Dr in percent) | material_error (corrected) |

### Angle of repose

No SND row reports an angle of repose. The evidence table contains no measured repose angle for an Arabian dune sand, so the field values will be the first in this repository. (Row TM-TK5 gives 34 degrees as "angle of repose used to calibrate DEM parameters" in a discrete element study; it is not a dune sand measurement and is not an expected range.)

### Composition that affects the tests

| Row | Metric (as written) | Value (as written) | Unit | Verification |
|---|---|---|---|---|
| SND-008 | calcite content: area A range and average; area B range and average | A: 7.00 to 26.00, average 17.50; B: 7.00 to 18.00, average 11.69 | percent | correct |
| SND-012 | quartz Q; feldspar F; carbonate lithic grains Lc (coastal UAE dunes, n = 3) | 24; 9; 58 | percent of framework grains | correct |

Carbonate rich sands are one reason not to acid treat sieve samples (section 5.2).

## 8. Open points

1. No retrieved open source describes a tilting box test for sand in full; Method B is a design.
2. The full ASTM standards were not read (paywalled); the methods above do not claim conformity with them.
3. The method of the withdrawn ASTM angle of repose test (cited by Kajiyama et al. 2024) and any ISO repose method were not retrieved.
4. The relevant normal stress range for the rover (wheel contact pressure) is unknown until the rover's wheel load and contact patch are measured.
