# Drone survey protocol: photogrammetric DEM and orthomosaic of one dune

**Status: DRAFT, PLANNED. Nothing in this document has been flown or processed. No number in it is a measurement of the field site.** Written 2026-10-21 for the slope ladder field day (`docs/FIELD_VALIDATION_PLAN.md`, `docs/FIELD_DAY_CHECKLIST.md`). It is a research plan, not an operational approval, a safety case or legal advice.

Labels (the three labels of the repository): every number quoted from a retrieved source is **PUBLISHED**; every item marked (derived) or (design, no retrieved source), and every procedure, is **PLANNED** (a design value of this protocol, not a measurement).

Every recommendation is tied to a retrieved source (keys in brackets, full list in `research/phase4/protocols_references.csv`). Where a step is a design choice of this protocol and no retrieved source supports it, it is marked **(design, no retrieved source)**. Where a number is computed here rather than copied from a source, it is marked **(derived)**.

## 1. Purpose and products

The survey covers one dune of about 200 m by 200 m and must deliver:

1. A digital elevation model (DEM) at 0.10 m posting (0.05 m if the ground sampling distance allows), with an independent accuracy report.
2. An orthomosaic at the native ground sampling distance (GSD) or close to it.
3. Block mean DEMs at 1, 5, 10 and 30 m, made from the 0.10 m DEM in the same way as the repository's map tests (`scripts/terrain_validation_lidar.py`), so that the slip face detector and three class map can be scored on Arabian dune sand as they were on the USGS lidar sites.

The DEM serves three uses in the field plan: choosing the slope bins before the runs (checklist: "Slope bins chosen by RTK walk or drone map"), giving the local slope and aspect of every run lane (plan section 8, item 4), and measuring how far a coarse DEM is from the truth at the run scale.

**Run scale requirement (derived).** A run is 6 m long on the slope. A relative height error of e metres between the two ends of a 6 m lane gives a slope error of atan(e / 6). To keep that error below 1 degree, the bin tolerance of the revised ladder for 10 to 20 degrees, the relative vertical error between points 6 m apart must be below 6 x tan(1 degree) = 0.105 m; for 0.5 degree it must be below 0.052 m. This is the accuracy target that the check point report in section 7 is judged against.

## 2. Flight height and ground sampling distance

**GSD.** For a nadir frame camera the ground footprint of one pixel is GSD = (sensor width x flight height above ground) / (focal length x image width in pixels) **(derived from pinhole camera geometry; not taken from a retrieved source)**. Compute it with the real camera values and check it against the flight planning app. Published sand surveys give reference pairs: an eBee flying wing at 149 m gave 4.6 cm pixels and at 65 m gave 2.0 cm (Long et al. 2016, Table 1); a multirotor at 40 m above take off with oblique images gave an expected GSD of 1.75 to 2.91 cm (Nesbit and Hugenholtz 2019, section 2).

**Target GSD.** The OpenDroneMap (ODM) DEM and orthophoto resolutions are "capped by a ground sampling distance (GSD) estimate" [odm_arguments, `--dem-resolution`, `--orthophoto-resolution`], and the ODM stockpile example uses a DEM at 2.0 cm with an orthophoto at 1.0 cm, that is a DEM about twice the orthophoto pixel [odm_tutorials, stockpile section, "Processing parameters"]. For a 0.10 m DEM a GSD of 5 cm or finer is therefore the minimum, and a GSD of about 2.5 cm leaves margin for the 0.05 m option **(design, from the two ODM statements above)**.

**Relief.** GSD grows with distance from the camera. In a survey flown at one fixed altitude over a site with almost 1000 m of relief, GSD ranged from 3 cm to 11 cm with an average of 6.86 cm (Sanz-Ablanedo et al. 2018, section 2), and GCPs at low altitude, with larger GSD, were less accurate (section 4). For a dune, compute the GSD at the lowest ground (interdune or dune toe), not at the take off point. The ODM stockpile guidance recommends a flight height of 3 to 4 times the tallest stockpile height and higher overlap as height increases [odm_tutorials, "Flight height"]; it is written for stockpiles, so treat it as a lower bound on clearance above the crest, not as a rule for dunes. Gafurov (2021, section 2.2) flew a dune complex with 197 m of relief at a limit of 150 m above the take off point, moved the take off point between blocks and recommends flying "by small squares" so that each block has the same illumination.

**Legal ceiling.** For recreational users the General Civil Aviation Authority (GCAA) page states that drones shall fly "within line-of-sight and not more than 400 feet above ground level" [gcaa_uas, section 5a]. 400 feet is 121.9 m **(derived conversion)**. Any flight plan must respect the ceiling that the permission actually granted states (section 11).

## 3. Overlap

| Source | Recommendation or setting |
|---|---|
| ODM flying tips [odm_flying] | 2D and 2.5D products: "70-80% overlap slightly off-nadir (5-10 degree off nadir)"; closer to 80 to 83 % for complex scenes. Full 3D: 60 % nadir plus 70 to 80 % at a 45 degree gimbal cross grid |
| ODM stockpile tutorial [odm_tutorials] | overlap 75 to 80 %, sidelap 65 to 70 %, increased slightly with flight height |
| ODM camera calibration section [odm_tutorials] | crossgrid flights: 42 % overlap and sidelap are equivalent to 70 % for 2D and 2.5D results, and 68 % to 83 % for 3D results (from James and Robson 2014, CC BY 4.0, as summarised by ODM) |
| Nesbit and Hugenholtz 2019 | tested 90/90, 90/70 and 70/70; recommendation 2: "Higher overlap is preferred for combination datasets" |
| Long et al. 2016 (sand bank) | 60 / 75 % latitudinal / longitudinal overlap at 149 m and 65 m |
| Gafurov 2021 (dune complex) | 70 % longitudinal and transverse overlap |

**Setting for this survey (design, from the table):** front overlap 80 %, side overlap 75 % for the nadir block, because bare sand has little texture (section 8) and the ODM guidance raises overlap for difficult scenes. If battery time is short, keep the front overlap and reduce the side overlap to 70 %, not below.

## 4. Flight pattern

1. **Nadir grid** over the whole dune plus a margin of at least 20 m on every side, so that GCPs placed 10 to 30 m inside the perimeter are seen in at least 5 images [odm_gcp].
2. **Crosshatch.** ODM summarises James and Robson (2014): to mitigate the bowling (doming) effect, "fly two patterns separated by 20 degrees, and rather than having a nadir (straight down pointing) camera, use one that tilts forward by 5 degrees" [odm_tutorials, "Calibrating the Camera"]. Fly the second grid rotated by 20 degrees with the camera tilted 5 degrees forward. ODM's own 2.5D advice of 5 to 10 degrees off nadir is consistent with this [odm_flying].
3. **Oblique block for the slip face.** Single angle image sets "are prone to higher levels of deformation along steep slopes", and nadir blocks are "susceptible to systematic 'dome' deformation, even with the use of survey-grade control points within high-relief scenes"; supplementing nadir blocks with oblique images "consistently mitigates these systematic error patterns" (Nesbit and Hugenholtz 2019, section 5). Their recommendations: combination datasets (nadir plus off nadir) are preferred; higher overlap is preferred; tilt angles of 15 to 35 degrees generally increase precision but may affect accuracy (recommendations 1 to 3). Fly one extra line or arc parallel to the slip face, camera tilted 20 to 30 degrees toward the face, from a position that does not require anyone to stand below the face.
4. Keep camera focus, zoom and aperture fixed for all blocks (Nesbit and Hugenholtz 2019, section 1, list item 5).
5. If the area needs more than one battery, split it into blocks that each finish within one battery and overlap their neighbours, as in Gafurov (2021), who used 70 % overlap between the outermost images of adjacent squares.

## 5. Camera settings and what to record

James et al. (2019) list what a repeatable survey must state; this protocol adopts the list as the minimum record:

- Sensor make and model, sensor size, image size, effective focal length, lens type (zoom or prime) (point 2).
- Shutter type, rolling or global, because of "the implications for processing with a forward motion correction" (point 2). If the shutter is rolling, enable `--rolling-shutter` in ODM [odm_arguments].
- Nominal flight height, image overlap and GSD, and the rationale (point 3).
- Number of images captured and rejected, field conditions, weather and illumination, and any deviation from the plan (point 5).

Exposure on bright sand: check a test image for clipped highlights before the main flight and record the exposure mode used **(design, no retrieved source)**. Do not change zoom or focus between blocks [Nesbit and Hugenholtz 2019].

## 6. Ground control points (GCPs)

### 6.1 Number and layout

| Source | Finding |
|---|---|
| ODM [odm_gcp] | "A minimum of 5 GCP works for most of the jobs, and for larger projects 8 - 10 are sufficient"; corners and centre; cover high and low elevations; spacing larger than the image footprint; 10 to 30 m inside the perimeter so that each is found in at least 5 images; the GCP file needs at least 5 points seen in 3 images each |
| Sanz-Ablanedo et al. 2018, section 3.3 | planimetric RMSE similar to the GSD with about 2.5 to 3 GCPs per 100 photos; vertical accuracy improves toward 1.5 x GSD with 4 GCPs per 100 photos; below 1 GCP per 100 photos accuracy degrades rapidly |
| Sanz-Ablanedo et al. 2018, section 4 | best results with GCPs evenly distributed over the whole area, "ideally ... in a triangular node grid"; concentrating them at the periphery or the centre is a poor strategy |
| Long et al. 2016, section 4 (32 ha sand bank) | with 4 GCPs on the corners the RMSD of the check profile was 94.359 cm; it stabilised at about 9 cm from 14 GCPs; GCPs in the corners and the centre are needed |
| Gafurov 2021, section 2.2 (dune complex) | 18 points: 11 for georeferencing and 7 for validation; points placed on the lowest accessible area, the highest point of the barchan ridge and points with steep height differences; extra points on low texture areas |

**Layout for a 200 m by 200 m dune (design, from the table).** At least 9 GCPs on a staggered triangular grid with about 70 m spacing, including the dune toe on all sides, the stoss slope at mid height, the crest line (on the stoss side of the brink, never on the slip face) and the interdune. Then raise the count to 4 per 100 nadir photos if the photo count makes that larger (Sanz-Ablanedo et al. 2018), as far as time allows; record the final ratio of GCPs per 100 photos.

### 6.2 Marking targets on sand

- Natural features are absent on bare sand: Long et al. (2016, section 3.3.2) state that GCPs "should be placed on the sand because, in this natural environment, no time-invariant objects or features are present", used white sheets of paper, and these were "partially buried because of the wind".
- Gafurov (2021) used 70 x 70 cm black and white panels and reports that panels of this size are clearly visible from 150 m.
- ODM: targets can be made from materials "ranging from bucket lids to floor tiles", and "Sharp corners are good picks for GCPs" [odm_gcp].

**Target specification (design, from the sources above):** rigid black and white checkerboard targets with a sharp centre. Scale the side to the flight height in proportion to Gafurov's 70 cm at 150 m (for example about 30 cm at 60 m, **derived** by proportion). Fix each target with stakes or sand filled weights at its corners, photograph it in place, survey its centre after placement, and check at the end of the flights that it has not moved or been buried. A target that moved is used as neither control nor check point.

### 6.3 Surveying the targets

**Option A, RTK or PPK GNSS (preferred).** The field kit already includes an RTK base and rover (checklist, "Position truth"). ODM: "equipment accuracy should be greater than the GSD. Survey grade GNSS and total stations are intended to provide the required millimetric accuracy" [odm_tutorials, stockpile "GCPs"]. Long et al. (2016) set a base within 3 km of the farthest part of the site and post processed the rover data (PPK) to "guarantee an absolute precision from 8 cm". Gafurov (2021) used a receiver whose internal antenna gave about 0.1 m and reached 0.15 to 0.16 m georeferencing RMS. Record for each point: fix type, number of epochs, the receiver's reported precision, antenna height. Keep the same vertical datum for GCPs and check points; ODM's `--gps-z-offset` note mentions the ellipsoidal to orthometric case [odm_arguments]. A constant vertical offset does not change slope.

**Option B, no RTK: measured tape and level network, relative accuracy only (design, no retrieved source).** Survey the targets in a local frame: horizontal distances between neighbouring targets by tape along a closed network, heights by levelling from one benchmark, orientation of one baseline by compass. Assign the benchmark approximate coordinates from a handheld GNSS fix and express all other targets as offsets in the site's UTM zone, so that ODM accepts the file. The absolute position is then uncertain by several metres, but slopes depend only on relative geometry and on the vertical direction, which levelling fixes. Report the network misclosures. The achievable accuracy of this option was not found in any retrieved source and must be measured from its own check points.

**Option C, no ground control (not acceptable for slope work).** Direct georeferencing from the drone's own GNSS "can achieve only decimeter to meter accuracies", with published examples of 1.247 m and of 1.55 m horizontal and 3.16 m vertical (Sanz-Ablanedo et al. 2018, section 1). The ODM default `--gps-accuracy` is 3 m [odm_arguments]. An uncontrolled model can also be domed, which tilts slopes; use Option C only for a preview map.

### 6.4 GCP file for ODM

The first line is the projection (a PROJ string, an EPSG code, or "WGS84 UTM <zone>[N|S]"), then one line per image observation: `geo_x geo_y geo_z im_x im_y image_name [gcp_name]`; the file must be called `gcp_list.txt` or passed with `--gcp`; avoid "NaN" elevations [odm_gcp]. WebODM includes the POSM GCPi interface for tagging targets in images [odm_gcp]. Check points are **not** written into this file (section 7).

## 7. Independent check points and the accuracy report

James et al. (2019) set the reporting standard adopted here:

- Control and check data must be separate, and check points "clearly identified" (points 4 and 9). Quality "must not be evaluated by simply stating the error observed at control measurements" (point 9).
- Report bias (mean error) and precision (standard deviation of error); avoid relying only on RMSE, which conflates them (point 7). Examine the spatial pattern of errors (points 7 and 9).
- Report image residuals at tie points and control points in pixels (point 8), and non dimensionalise errors, for example by the GSD (point 9).
- Without check data, use a split test, for example two flights of different design (point 10).

Sanz-Ablanedo et al. (2018, section 4) show why: with 3 to 5 control points the RMSE at control points was sometimes a few millimetres while check points showed errors above 1 m and up to 8 m.

**Check data for this survey (design):**

1. At least 8 targeted check points, never used as control, spread over toe, stoss slope, crest and interdune.
2. The RTK profiles along every rover run lane (the field plan already measures them, section 8 item 4). Compare DEM heights and DEM slopes along each lane with the RTK profile. Long et al. (2016) used the same idea with a 528 point GNSS profile over 677 m.

**Accuracy report table (one row per check point or profile point):** `point_id, type (target or profile), easting, northing, z_survey, z_dem, dz = z_dem - z_survey, dz_over_gsd, terrain (toe, stoss, crest, interdune), slope_deg_dem_1m, notes`. Summary: n, mean dz, standard deviation of dz, RMSE, maximum absolute dz, the same for horizontal errors at targets, image residuals in pixels, and, for each run lane, the DEM slope minus the RTK slope over the 6 m lane, judged against the 0.105 m and 0.052 m relative targets of section 1 (derived).

## 8. Problems specific to sand

| Problem | Effect | Mitigation |
|---|---|---|
| Low texture of bare sand | few matched features; gaps and poor alignment | high overlap (section 3); raise `--min-num-features` above its default of 10000, since "More features can be useful for finding more matches between images, potentially allowing the reconstruction of areas with little overlap or insufficient features" [odm_arguments]; `--feature-quality high` or `ultra` [odm_arguments]; extra targets on the most uniform areas, as Gafurov (2021) did on low contrast areas |
| Wind moving sand | ripples migrate and targets get buried during the survey (Long et al. 2016) | fly the whole dune in one short window, record wind speed and direction as Long et al. (2016, Table 1) did, check targets after the flights, keep only targets that did not move |
| Sun angle and slip face shadows | a low sun puts the lee face in shadow and changes illumination between blocks | Gafurov (2021) recommends shooting by small squares so each has the same illumination; choose the time of day so the slip face is lit, and record sun conditions **(the choice of hour is design, no retrieved source)** |
| Steep slip face near the angle of repose | nadir blocks deform on steep slopes; avalanching under foot | oblique block of section 4; never place targets or people on or below the face (checklist, Safety 1) |
| Heat | battery and electronics limits | out of scope here, handled in the sibling repository `hudasol/dhill`; the GCAA page states flights "only during day time and in good weather conditions" for recreational users [gcaa_uas] |
| DEM gap filling | ODM fills gaps by inverse distance weighting over progressively larger radii (`--dem-gapfill-steps`, default 3) [odm_arguments] | export `--dem-euclidean-map`, which "can be useful to isolate the areas that have been filled" [odm_arguments], and report the filled share; exclude filled cells from slope truth |

## 9. Processing in OpenDroneMap or WebODM

Record the ODM or WebODM version and every non default option (James et al. 2019, point 6). Suggested starting options, with the reason for each:

| Option | Value | Reason |
|---|---|---|
| `--dsm` | on | builds the surface model; on bare sand the surface is the ground |
| `--dtm` | off unless vegetation is present | the DTM uses the Simple Morphological Filter with `--smrf-slope` default 0.15 rise over run [odm_arguments], which is about 8.5 degrees **(derived)**; a filter tuned for gentle ground may treat a 30 degree slip face as non ground. If vegetation forces a DTM, raise `--smrf-slope` and compare DTM and DSM at the check points |
| `--dem-resolution` | 10 (cm), or 5 | target posting; capped by the GSD estimate [odm_arguments] |
| `--orthophoto-resolution` | the GSD in cm | capped by the GSD estimate [odm_arguments] |
| `--pc-quality` | high | default medium; "Each step up in quality increases processing time roughly by a factor of 4x" [odm_arguments] |
| `--feature-quality`, `--min-num-features` | high or ultra; 20000 if alignment is poor **(design)** | low texture (section 8) |
| `--gcp` | `gcp_list.txt` | section 6.4 |
| `--rolling-shutter` | on for a rolling shutter camera | [odm_arguments]; James et al. (2019) point 2 |
| `--use-fixed-camera-params` | only if doming is seen at check points | "can be sometimes useful for improving results that exhibit doming/bowling" [odm_arguments] |
| `--gps-accuracy` | leave automatic for RTK drones | "Lowering this option can sometimes help control bowling-effects over large areas" [odm_arguments] |
| `--dem-euclidean-map` | on | section 8 |
| `--pc-las`, `--cog`, `--build-overviews` | on | point cloud and cloud optimised GeoTIFFs for archiving and viewing [odm_arguments] |
| `--ignore-gsd` | off | the documentation says "Never set --ignore-gsd to true unless you are positive you need it, and even then: do not use it" [odm_arguments] |

Example command (Docker, as in the ODM DEM tutorial [odm_tutorials]); the values are the starting point above, not tested on this site:

```
docker run -ti --rm -v /path/to/project:/datasets/code <my_odm_image> --project-path /datasets \
  --dsm --dem-resolution 10 --orthophoto-resolution 2.5 --pc-quality high --feature-quality high \
  --gcp /datasets/code/gcp_list.txt --dem-euclidean-map --pc-las --cog --build-overviews
```

Outputs are written to `odm_dem/dsm.tif`, `odm_orthophoto/odm_orthophoto.tif` and `odm_georeferencing/odm_georeferenced_model.laz` [odm_outputs]. ODM also writes a PDF processing report unless `--skip-report` is set [odm_arguments]; keep it with the raw data.

## 10. Outputs and the block means used by the map tests

1. `dsm.tif` at 0.10 m in the UTM zone of the site, with the euclidean map and the check point report.
2. Resample to a grid whose origin is a whole multiple of 30 m in easting and northing, so that the 1, 5, 10 and 30 m blocks nest exactly **(design)**.
3. Make the 1 m DEM as the block mean of 10 x 10 cells of the 0.10 m DEM, then the 5, 10 and 30 m DEMs as block means of the 1 m DEM, using the same rule as the `block()` function in `scripts/terrain_validation_lidar.py` (crop to whole blocks, mean of each block). That script computes the 1 m slope with the Horn gradient and counts a slip face where at least `MIN_POSTS = 10` one metre posts in a cell reach `FACE_TRUTH_DEG = 28.0` degrees (`src/dunerover/subgrid.py`). The script reads USGS tiles from `data/raw/lidar/` and asserts a 1 m posting, so a small adapter that reads the drone 1 m DEM is needed; that is a code change outside this draft.
4. Cells containing gap filled 0.10 m cells (from the euclidean map) are flagged and reported separately.
5. **Size limit (derived):** a 200 m square holds 6 x 6 whole cells at 30 m (180 m), 20 x 20 at 10 m and 40 x 40 at 5 m. Statistics at 30 m rest on 36 cells from one dune and must be reported as such.

Label every product "drone photogrammetry, one dune, one date", with its check point accuracy.

## 11. Permission and safety

**Retrieved official source.** The GCAA page "UAS Registration" [gcaa_uas], read on 2026-10-21 (the page shows no date of last update), states among other points:

- Recreational users: the user and drone "shall be registered with the GCAA before flying"; drones of 5 kg or less fly only "in the approved flying zone indicated in my drone hub mobile application (i.e the green zone)"; "Camera usage is only allowed in the flying zones"; "within line-of-sight and not more than 400 feet above ground level"; "only during day time and in good weather conditions"; not "for commercial purposes"; not "within 5 km of UAE airports outer fence, Heliports, Helicopter landing Sites, and airfields or in controlled zones"; incidents are reported to the GCAA.
- Organisations and operators "for professional use or special operations": the examples of special operations include "Survey"; step 1 is an Unmanned Aircraft Operator Authorisation (UOA), with a security clearance and a subscription to the GCAA E-Publications Service with a stated fee of AED 1,200, and a stated time of 3 weeks; step 2 is an operation permission "for each drone flying activity in red zone"; and "regardless of the flying zone (red or green), organization/operator must apply for Security Clearance Approval if their drone flying activity will involve the use of any capturing devices", with a stated time of 14 working days.
- Flying zones are shown in the "My Drone Hub" app and on the GCAA fly zone map.

A photogrammetric survey for research uses a camera and is listed by the page under survey type operations, so the operator should expect the organisation route and its lead times. Obtain the required permissions from the competent authority, and from the landowner or site manager, before the field day; an emirate level authority may have additional rules that were not retrieved here. Flying through a partner organisation that already holds an operator authorisation may avoid a new fee; this was not verified.

**Safety on site (from the field checklist):** two people at all times, water and shade, no person or tether below a lee face or a slope near the angle of repose, visual line of sight kept by the pilot, and an abort if wind blows sand into equipment. Placing and collecting targets is the main time on foot: plan the walking route along the stoss slope and toe, not across the slip face.

## 12. Field log sheets

**Flight log:** `flight_id, date, block (nadir, crosshatch, oblique), start_time, end_time, takeoff_point, height_above_takeoff_m, planned_gsd_cm_at_lowest_ground, front_overlap_pct, side_overlap_pct, camera_tilt_deg, grid_heading_deg, images_captured, images_rejected, wind_speed, wind_direction, air_temperature, sun_and_cloud, battery_id, notes`.

**Target log:** `target_id, role (control or check), size_cm, placed_time, easting, northing, z, vertical_datum, fix_type, epochs, reported_precision_h, reported_precision_v, antenna_height, photo_id, checked_at_end (moved, buried, intact), notes`.

**Processing log:** `software_and_version, options (full command line), camera_model_type, images_used, gcps_used, check_points_used, image_residual_px_control, image_residual_px_tie, output_files, filled_share_pct`.

## 13. Open points

1. The tape and level fallback (Option B) has no retrieved accuracy figure; its accuracy must come from its own check points.
2. The best hour for slip face illumination on a given dune orientation is not taken from any retrieved source.
3. A reader for the drone 1 m DEM in the map test script is a code change that is not part of this draft.
4. The James and Robson (2014) paper itself was not opened; its crosshatch advice is used here only as summarised in the ODM documentation (CC BY 4.0 figure credit stated there).
