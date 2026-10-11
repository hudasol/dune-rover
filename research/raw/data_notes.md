# Data audit and dune morphology / resolvability notes (dune-rover)

Prepared 2026-10-11. Labels used throughout:
- PUBLISHED = number or statement read in a retrieved source (URL given in morphology_rows.csv or data_audit.csv).
- COMPUTED-BY-ME / SIMULATED = my own computation on the downloaded tiles or a synthetic profile; not published.
- MY ARITHMETIC / MY INFERENCE = reasoning from published numbers; not a retrieved statement.

Companion files: research/raw/data_audit.csv (21 rows), research/raw/morphology_rows.csv (32 rows), data/raw/MANIFEST.md (tiles + sha256), scripts in /home/claude/dune-rover/scripts/, derived outputs in /home/claude/dune-rover/data/derived/ (slope_stats.json, resolvability.json, A_north_stats.json, hillshade/slope PNGs).

## SEARCH_LOG

Sandbox tests (curl, 2026-10-11):
- HEAD https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N23_00_E053_00_DEM/Copernicus_DSM_COG_10_N23_00_E053_00_DEM.tif -> 200, Content-Length 48,561,117, Last-Modified 2022-05-09. Full download OK.
- Same pattern N22_00_E053 (49,450,340 B) and N22_00_E054 (48,277,338 B) downloaded OK. HEAD 200 also for N19E046, N20E052, N21E054, N22E055, N24E054.
- GLO-90: https://copernicus-dem-90m.s3.amazonaws.com/Copernicus_DSM_COG_30_N23_00_E053_00_DEM/Copernicus_DSM_COG_30_N23_00_E053_00_DEM.tif -> 200, 5,646,288 B, downloaded.
- skadi: https://s3.amazonaws.com/elevation-tiles-prod/skadi/N23/N23E053.hgt.gz -> 200, 8,310,302 B, downloaded; gunzip size 25,934,402 B = 3601 x 3601 x 2 bytes.
- First attempt at the file name with a typo (Copernicus_DSM_COG_10_N22_00_E053_DEM) returned a 370-byte 404 XML; those two stub files were deleted. The correct name has "_00_" twice (northing and easting).
- tileList.txt (26,450 lines) fetched; 30 entries inside 20-25N, 50-56E by my grep.
- Python in the sandbox had numpy/scipy/matplotlib/tifffile but no GDAL/rasterio; installing imagecodecs (pip) was needed to decode the COG (float predictor).
- Earth Search STAC POST (sentinel-2-l2a, bbox 53.7-53.9E, 23.0-23.2N) -> scene S2C_39QYF_20261007; HEAD on its B04.tif -> 200, 224,747,452 B (not downloaded).
- maxar-opendata catalog.json -> 55 event children, none with Gulf/UAE/Saudi/Oman names (name grep).
- ISRIC WebDAV https://files.isric.org/soilgrids/latest/data/sand/sand_0-5cm_mean.vrt HEAD 200 (5,928,942 B).
- ADSDI OpenData ArcGIS MapServer JSON: 216 layer names listed; no DEM/elevation/contour/LiDAR layer by name grep.

Web retrievals (curl + text extraction, pdftotext; WebFetch only after the first attempts were refused for lack of permission, later accepted):
- Copernicus: Product Handbook issue 5.0 (pdftotext), AWS registry + readme.html, CDSE COP-DEM page, GEE catalogue page (terms text), CDSE licence PDF (covers EEA-10/GLO-30-R restricted licences, not the free GLO-30 licence; only skimmed).
- NASA/LP DAAC catalogue pages: NASADEM, ASTER GDEM v3 (plus V3 User Guide PDF), GEDI L2A v002; NSIDC ATL08 v7; NASA Landsat 9 page.
- JAXA AW3D30 page + v4.1 product description PDF; Takaku et al. 2016 (ISPRS Annals) PDF.
- FABDEM: Hawker et al. 2022 (IOP page), Bristol directory listing, readme.txt, license.txt (CC BY-NC-SA 4.0 text).
- DLR TanDEM-X 90m guide page (licence text in page).
- AWS registry pages: Sentinel-2 COGs, USGS Landsat, Maxar Open Data, Terrain Tiles; Tilezen joerd docs (attribution, formats, data-sources).
- SoilGrids: ISRIC GeoNetwork record (licence CC BY 4.0). UAE: u.ae geospatial page, atlas.co Bayanat page, ADSDI ArcGIS REST.
- Morphology: Pelletier et al. 2015 (PDF), Kroy et al. 2002 (arXiv), Claudin & Andreotti 2006 (arXiv), Csahok et al. 2000 (arXiv), Guth 2009, Bishop 2011, Lorenz et al. EGU2016, Lancaster et al. GSA 2004 abstract, Almasrahy & Mountney AAPG abstract (no numbers), Al-Awadhi et al. Kuwait barchans, USGS Professional Paper 1052 (105 MB PDF; Tables 36-40 read, two tables from page images), Almutlaq & Mulligan 2023 (WebFetch summary only).
- Searches run (WebSearch): Copernicus handbook accuracy; Rub al Khali / Liwa dune morphometry (3 variants); angle of repose slip face; ripple wavelength (2 variants); Almasrahy Mountney; Breed/McKee global dune types; Liwa migration; SoilGrids; UAE open data/Bayanat/DEM; ICESat-2 footprint; SRTM accuracy; radar penetration over sand; Empty Quarter grain size.

Failures (see NOT_RETRIEVED for URLs): spacedata.copernicus.eu timeouts; MDPI/TTU/ifremer/Southampton/landinfo/usgs.gov HTTP 403 from curl; journal.ut.ac.ir and KAU PDF tunnel closed; Bristol landing page timeout; figshare 202 empty; JAXA terms page is a JS shell.

## DATA_SUMMARY

Full per-product details are in data_audit.csv. Short version for the planner:

| Product | Posting | Open? | Tested here | Role for a dune planner |
|---|---|---|---|---|
| Copernicus GLO-30 (AWS, COG) | 1 arcsec (~28.3 m E-W, 30.9 m N-S at 23.5N, my arithmetic) | Free licence + attribution notice (provider texts read via GEE/CDSE/AWS; controlling licence document not read directly) | YES, 3 tiles downloaded | Primary DEM. DSM, TanDEM-X X-band, epoch Dec 2010 - Jan 2015. Published spec: absolute <4 m LE90; relative <2 m (slope <=20%), <4 m (slope >20%) |
| Copernicus GLO-90 | 3 arcsec | same | YES, 1 tile | Useful only as a degradation baseline |
| SRTM-derived "skadi" | 1 arcsec, int16 | joerd attribution; SRTM courtesy USGS | YES | Epoch 2000 cross-check; integer metres; noisier tail (max slope 66 deg in AOI A, COMPUTED-BY-ME) |
| NASADEM, ASTER GDEM v3, GEDI, ICESat-2 | 30 m / 25 m / 11-17 m | Free but Earthdata Login | NO | NASADEM/ASTER redundant with COP30; GEDI/ICESat-2 only for ground-truth profiles |
| AW3D30 v4.1 | 1 arcsec | Free after registration | NO | Optical stereo 2006-2011; possible second opinion on crest geometry |
| FABDEM v1-2 | 1 arcsec | CC BY-NC-SA 4.0 (non-commercial) | listing only; zips 1.6-1.8 GB | Corrects forests/buildings only; no expected benefit on bare dunes (MY INFERENCE) |
| TanDEM-X 90 m (DLR) | 3 arcsec | scientific use only, registration | NO | Redundant with GLO-90, more restrictive licence |
| Sentinel-2 L2A (AWS COG, STAC) | 10 m | free, full, open | YES (STAC + HEAD) | Optical context, sand/interdune/sabkha mapping; no elevation |
| Landsat 8/9 | 30 m / 15 m pan | no restrictions | NO | Context only |
| Maxar Open Data | sub-metre | CC BY-NC 4.0, event-based | catalog read | No Gulf events found: not usable |
| Pleiades Neo | 30 cm | COMMERCIAL, NOT open | n/a | Would resolve slip faces (stereo DEM) but paid |
| Airborne LiDAR / drone DEM | n/a | NONE FOUND open for Rub al Khali/Liwa | n/a | Gap |
| ADSDI OpenData (EAD habitat/geology) | vector | licence field empty | YES | Dune/sandsheet habitat polygons, low-dune (<20 m) description; no elevation |
| SoilGrids sand fraction | 250 m | CC BY 4.0 | HEAD only | Texture class fraction, not grain size or colour; little information inside the dune sea (MY INFERENCE) |
| Sand-colour / grain-size map of Empty Quarter | | | | NOT FOUND |

Key access fact: the two sandbox-reachable hosts work for real Rub al Khali tiles; no authentication needed. COP30 tile naming uses the lower-left corner in whole degrees, e.g. N23_00_E053_00. The tile is pixel-is-point: top-left post at the nominal northern edge (24.0N for N23), 3600 x 3600 posts, bottom row removed.

Temporal note: COP30 epoch 2010-2015, SRTM Feb 2000, ALOS 2006-2011, ASTER 2000-2013. Published migration for 50-80 m Liwa dunes is ~0.1 m/yr (PUBLISHED, Lorenz et al.), so ~1-2 m between SRTM and TanDEM-X (MY ARITHMETIC). Small barchans in Kuwait move >20 m/yr (PUBLISHED, Al-Awadhi et al.).

## DUNE_MORPHOLOGY

All rows with sources and locations are in morphology_rows.csv (ids M01-M32). Summary, every number PUBLISHED unless marked:

Slip face and sand
- Angle of repose of aeolian sand about 32-35 deg (Kroy et al. 2002, intro; M05). Field TLS on barchans: critical angle 32.2-32.35 deg on a 30 m slip face and 32.2-33 deg on a 17 m one; relaxation angle 0.05-0.15 deg (large) and ~0.2-0.8 deg (small) (Pelletier et al. 2015, Sec 4.3; M01-M03). Lab 1.2 m face: 34 deg critical, 32 deg repose (Sutton et al., as cited by Pelletier, secondhand; M04). Brazil coastal dunes, not Arabia.
- Slip face top ends in a "sharp brink" (Kroy et al., qualitative). No numeric crest radius of curvature found.
- Grain size: d50 ~0.2 mm on the large Brazilian dune (M07); 0.23 mm mean on Kuwaiti barchans (M30). No Liwa/Rub al Khali grain size retrieved.

Dune sizes (Arabian Peninsula)
- Liwa large dunes 50-80 m high, ~0.1 m/yr migration (Lorenz et al., abstract; M14-M15). Interdune sabkhas with near-surface water table at Liwa (M16).
- Northern Rub al Khali complex linear dunes 50-100 m high (Lancaster et al. GSA 2004 abstract; M17).
- Linear dune statistics after Lancaster 1995 via Guth 2009: simple spacing 430-2346 m, height 4-21 m; compound spacing 990-2080 m, height 24-48 m; complex spacing 1500-3300 m, height 40-200 m (M10-M12); tallest complex dunes in SW Saudi Arabia ~100 m (M13).
- Almutlaq & Mulligan 2023 (read only via an automated page summary; re-verify): simple linear 10-25 m high, 200-300 m spacing; compound linear 45-80 m (to 150 m), spacing 1.5-2 km; megabarchans 3-4 km wide and 100-260 m high; star dunes >200 m high, spacing 1-3 km (M24-M27).
- USGS PP1052 Landsat morphometry (km): simple linear NE Rub al Khali width 0.38, wavelength 1.41; compound linear SW width 1.21, wavelength 2.18; complex linear W width 1.48, wavelength 3.17; Al Jiwa (Liwa) simple crescentic length 0.59, width 0.80, wavelength 0.63; compound crescentic eastern Rub al Khali ('Uruq al Mu'taridah) length 2.09, width 2.76, wavelength 2.56; star dunes SE Rub al Khali diameter 0.84, wavelength 2.06 (M18-M23). No heights in these tables.
- Small barchans, northern Kuwait: height 1-7 m, migration >20 m/yr (M28-M29).

Ripples
- Wind-ripple wavelength "a few cm" (Csahok et al.; M09). Megaripples/ridges can reach metres (same source). Ripple height not retrieved. The wavelength of the instability that forms small dunes on barchan flanks ~20 m (Morocco; Claudin & Andreotti; M08).

Crests: no published numeric crest sharpness found (see GAPS).

## RESOLVABILITY

Posting facts used: COP30 cell at 23.0-24.0N is 28.2-28.4 m E-W by 30.89 m N-S (COMPUTED-BY-ME from the tile geometry); GLO-90 is 3x coarser.

### Scale arguments (MY ARITHMETIC unless stated)
1. Slip-face footprint. A face at repose angle theta has horizontal run H / tan(theta). For theta = 32 deg, run = 1.60 H (published 32-35 deg; 32 used). A Nyquist-type minimum of 2 posts across the run needs 60 m at 30 m posting, i.e. H >= 37.5 m; 3 posts needs H >= 56 m. At 90 m posting the same criteria need H >= 112 m and 169 m.
2. Dune wavelength. Published Arabian linear/star/crescentic wavelengths 0.6-3.3 km are 20-110 posts at 30 m and 7-37 posts at 90 m: well resolved at both for large dunes. The 200-300 m spacing of simple linear dunes (Almutlaq & Mulligan, via summary) is 7-10 posts at 30 m and only 2-3 at 90 m, consistent with Guth's published remark that small simple dunes are hard to discriminate in 90 m SRTM.
3. Height vs vertical error. Published COP30 relative accuracy is <2 m (slope <=20%) and <4 m (slope >20%) (Handbook). Dunes of 1-7 m (Kuwait barchans) are at or below that noise, so they are not usable features in COP30. Dunes of 24-200+ m are far above it.
4. Ripples: cm-scale wavelength vs 30 m posting is about 3 orders of magnitude finer. Not resolvable; they exist only as sub-grid roughness.
5. Crests: a "sharp brink" is, by definition, narrower than one posting at 30 m, so the DEM crest is rounded and crest height can be slightly underestimated. Not quantified (no published radius).
6. Epoch: ~1-2 m movement for large dunes between 2000 and 2011-15 is below 1 posting; for small dunes (>20 m/yr in Kuwait) COP30 positions are stale after ~1.5 years.
7. The product is a DSM from X-band InSAR. Over sandy deserts DLR states a strong impact on SAR quality (Martone et al. 2016 abstract); magnitude of penetration/bias on dry sand NOT retrieved.

### Computed-by-me results on the downloaded tiles
Method: slope = arctan of np.gradient (central difference over 2 posts = ~60 m baseline) with per-latitude metric spacing. All numbers COMPUTED-BY-ME.

Whole tiles (COP30, 12,960,000 cells each):
| Tile | mean | median | p99 | p99.9 | max | >20 deg | >25 deg | >30 deg |
|---|---|---|---|---|---|---|---|---|
| N23E053 | 4.40 | 3.31 | 18.6 | 26.9 | 41.0 | 0.73% | 0.19% | 0.020% |
| N22E053 | 5.87 | 4.92 | 22.3 | 30.3 | 43.5 | 1.53% | 0.61% | 0.122% |
| N22E054 | 6.92 | 5.62 | 28.6 | 32.3 | 46.8 | 4.43% | 2.16% | 0.501% |

AOI A (Liwa megabarchan zone, 23.02-23.17N, 53.55-53.95E, N23E053; 777,600 cells; elevation 85.6-224.8 m, relief 139 m):
- mean 6.08, median 5.16, p90 12.2, p99 23.0, p99.9 29.9, max 38.4 deg. Fraction >10/15/20/25/30 deg = 17.5% / 4.89% / 1.70% / 0.68% / 0.088%. >32 deg 0.009%, >34 deg 0.0014%.
- Same area at 90 m: official GLO-90 product: max 27.7, >20 deg 0.30%, >25 deg 0.029%, >30 deg 0. My own 3x3 block mean of COP30 gives the same (max 27.7, 0.30%, 0.037%). So going to 90 m removes essentially all >25 deg cells here.
- SRTM-derived skadi on the same cells: >20 deg 1.90%, >25 deg 0.74%, >30 deg 0.28%, max 66.5 deg (spiky noise). SRTM minus COP30 elevation: mean +1.47 m, std 4.31 m, p5/p95 -4.9/+8.7 m, correlation 0.986 (includes real change since 2000, DSM and penetration differences, and a ~0 to half-post alignment uncertainty; not separable).
AOI A-north (Liwa smaller crescentic dunes, 23.25-23.45N, 53.55-53.95E; elevation 109-194 m): >20 deg 1.84%, >25 deg 0.49%, >30 deg 0.07%, max 37.3. Peak spacing along N-S profiles (prominence >= 8 m): median 587 m (p10 340, p90 958 m); this is consistent with PP1052's published mean wavelength 0.63 km for Al Jiwa simple crescentic dunes (M21) -- a plausibility check, not validation. Median prominence 24 m (p10 10, p90 44 m).

AOI B (Rub al Khali megadunes, 22.20-22.50N, 54.20-54.60E, N22E054; 1,555,200 cells; elevation 64.3-275.6 m, relief 211 m):
- mean 7.89, median 7.24, p90 16.7, p99 29.0, p99.9 32.0, max 45.1 deg. >10/15/20/25/30 deg = 34.9% / 13.9% / 5.51% / 2.54% / 0.54%; >32 deg 0.103%; >34 deg 0.034%. Block-mean to 90 m: >20 deg 2.38%, >25 deg 0.67%, >30 deg 0.005%, max 32.0.
- Slope histogram counts per 5 deg bin from 0 to 45 deg: 598,849 / 413,098 / 327,010 / 130,523 / 46,157 / 31,201 / 8,048 / 291 / 22.
- N-S cross-sections (every 7th column): peak-to-base prominence >= 30 m: median 103 m, p10 43 m, p90 145 m, max 203 m (n=2810); adjacent crest spacing median 2.44 km (p10 1.28, p90 3.34 km). These sit inside the published ranges for megabarchans/complex linear/star dunes (100-260 m; 1-3 km), but are DSM prominence on arbitrary N-S lines, not a dune inventory.
- Steep runs (consecutive posts with forward-difference slope >= 25 deg): n=1989; median 2 posts, p90 4 posts, 45% are a single post and 70% span <=2 posts; elevation drop across a run median 31 m (p10 15 m, p90 70 m, max 139 m). So slip faces on these megadunes are present but only 1-4 posts wide.
- Slopes above the published repose angle (32-35 deg) are physically implausible for dry sand on these scales; their share is small (0.10% of cells >32 deg in B, 0.009% in A), i.e. an estimate of noise/artefact tail plus sub-pixel aliasing, not of real steeper faces.

Visual check: hillshade/slope PNGs (data/derived/A_Liwa_crescent_hillshade_slope.png, B_RubAlKhali_megadunes_hillshade_slope.png, A_wide_hillshade_slope.png) show clear crescentic/barchanoid dune fabric at 30 m. In the slope maps slip faces appear as thin, bright 1-3 post wide lines. A smooth N-S stripe near 53.78-53.80E (visible in A_wide above 23.15N) looks like a road/corridor or processing artefact; cause not determined.

### Synthetic test (SIMULATED): ideal 32 deg planar slip face of height H sampled at 30 m with random phase (4000 trials)
Maximum apparent slope, median over phases (forward-difference between adjacent posts / central difference as in the tile statistics):
| H (m) | run (m) | 30 m fwd-diff | 30 m central-diff | 90 m fwd-diff | 90 m central-diff |
|---|---|---|---|---|---|
| 3 | 4.8 | 5.7 | 2.9 | | |
| 5 | 8.0 | 9.5 | 4.8 | | |
| 10 | 16.0 | 17.9 | 9.5 | 6.3 | 3.2 |
| 20 | 32.0 | 25.9 | 18.4 | 12.5 | 6.3 |
| 30 | 48.0 | 32.0 | 25.9 | | |
| 50 | 80.0 | 32.0 | 32.0 | 23.4 | 15.5 |
| 100 | 160.0 | 32.0 | 32.0 | 32.0 | 27.1 |
Interpretation (SIMULATED, point-sampled ideal geometry, so optimistic): at 30 m a 32 deg face is recovered at full steepness only if H >= ~30 m by forward difference or >= ~50 m by central difference; 20 m faces read as ~18-26 deg; 10 m faces ~9-18 deg. At 90 m even 50 m faces read ~16-23 deg. A real DEM also averages within the cell and has noise, so expect under-estimation rather than over-estimation of slip-face slope.

### Verdict
- Dune crests/ridges and interdune corridors of Liwa and Rub al Khali megadunes (tens to 200+ m high, 0.6-3 km wavelength): RESOLVED at 30 m. At 90 m the form is visible but slopes are strongly underestimated.
- Slip faces on dunes >= ~40-50 m high: marginally resolved at 30 m (1-4 posts), slope magnitude biased low unless H >= ~50 m; locations of slip faces are detectable as thin bands of high slope. Slip faces on dunes <~20 m: not reliably resolved; slope read well below the real 32 deg. Hazard classification from 30 m slope alone will under-flag lee faces: a planner should treat "steep-slope present" as an upper-bound-safe proxy or use aspect + curvature + dune height to infer slip faces rather than trusting the slope value.
- Crest sharpness (brink): not resolvable. Ripples: not resolvable. Small barchans (1-7 m) and small simple linear dunes (10-25 m, 200-300 m spacing): at or beyond the useful limit of COP30.

## CANDIDATE_STUDY_AREAS

Both lie in downloaded COP30 tiles; coverage verified from the GeoTIFF tiepoint/pixel scale (post spacing 1/3600 deg; row index = (top - lat) x 3600, column = (lon - left) x 3600) and by the plotted hillshades.

1. Study area A: Liwa crescent margin, UAE (Abu Dhabi emirate), tile N23E053 (spans 23.0-24.0N, 53.0-54.0E; file Copernicus_DSM_COG_10_N23_00_E053_00_DEM.tif, sha256 in MANIFEST).
   - A-south: 23.02-23.17N, 53.55-53.95E (about 17 x 41 km), megabarchans/ridges, relief 139 m, centre 23.095N 53.75E (within ~0.1 deg of the Liwa point 23.1N 53.8E in the task).
   - A-north: 23.25-23.45N, 53.55-53.95E (about 22 x 41 km), smaller crescentic/barchanoid dunes with ~0.6 km spacing (matches PP1052 Al Jiwa row, M21). Gives a second dune scale in one tile.
   - Why: published Liwa dune facts exist (50-80 m high, ~0.1 m/yr, sabkha interdunes; M14-M16), the tile also has official GLO-90 and an SRTM-derived copy for degradation tests, and it is the closest of the candidates to UAE infrastructure.
2. Study area B: Rub al Khali megadune field, tile N22E054 (spans 22.0-23.0N, 54.0-55.0E), AOI 22.20-22.50N, 54.20-54.60E (about 33 x 41 km), relief 211 m, 5.5% of cells >20 deg. Stress case: tallest dunes and the thinnest slip-face bands. Its coordinates lie inside the PP1052 'Uruq al Mu'taridah region (21.38N, 53.5-55E) only loosely; I did not verify which published dune type maps exactly onto it.

Recommendation: use A (both sub-areas) as the main study area and B as the high-relief stress test. N22E053 is downloaded (whole-tile statistics only).

## GAPS

- No published numeric crest/brink radius, stoss-slope angle distribution, or slip-face-height distribution for Arabian dunes found. (Stoss slopes were not needed for the retrieved arguments; any stoss slope in simulations would be an assumption.)
- No height data in PP1052 tables; dune heights come from abstracts/secondhand tables (Lancaster via Guth) and a summary-only read of Almutlaq & Mulligan.
- No Liwa/Rub al Khali grain size, sand colour map or ripple height retrieved; nearest are Kuwait 0.23 mm and Brazil 0.2 mm.
- No dune-specific vertical accuracy for COP30. Published figure is global (LE90 <4 m), validated against ICESat GLAS; X-band penetration/bias over dry sand not quantified (Martone et al. 2016 abstract only).
- No open LiDAR/drone DEM; no open sub-metre stereo for the region.
- ASTER GDEM v3 and NASADEM accuracy numbers not retrieved; AW3D30 validated accuracy not retrieved (only the 5 m source DSM's ICESat statistics).
- GEDI and ICESat-2 access needs Earthdata Login; no ground-truth profile was downloaded, so slip-face slope bias in COP30 is only estimated by synthetic simulation and by 30 m vs 90 m vs SRTM comparison, not by lidar truth.
- Controlling Copernicus GLO-30 licence document (spacedata.copernicus.eu) not read directly; commercial-use clause unverified.
- Slope statistics use a 2-post central difference; other kernels (Horn/Zevenbergen-Thorne, forward difference) will give somewhat different tails. Not tested.
- The mean/median "frac>X deg" values depend on AOI choice; AOIs were chosen by me for visible dune texture, not randomly.

## NOT_RETRIEVED

- https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model (timeout; licence section)
- https://spacedata.copernicus.eu/documents/20126/0/GEO1988-CopernicusDEM-RP-001_ValidationReport_V1.0.pdf/edc88601-897e-82df-5604-b6b60cbecb57?t=1586527010843 (link seen in AWS readme; not fetched)
- https://data.bris.ac.uk/data/dataset/s5hqmjcdj8yo2ibzi9b4ew3sn (landing page timeout; readme and licence read from https://data.bris.ac.uk/datasets/s5hqmjcdj8yo2ibzi9b4ew3sn/)
- https://earth.jaxa.jp/policy/en.html (JAXA terms; JS shell only)
- https://www.mdpi.com/2072-4292/15/19/4653 (curl 403; content seen only through a WebFetch summary)
- https://ttu-ir.tdl.org/items/af412958-a771-4026-8241-f48e51162d63 (HTTP 403; thesis "Analysis of dune morphology within the Rub' al Khali using geospatial technology")
- https://data-ww3.ifremer.fr/BIB/Rodriguez_etal_PERS2006.pdf (HTTP 403; SRTM accuracy paper)
- https://eprints.soton.ac.uk/506673/1/Nield_etal_ripples_revision_JGR.pdf (HTTP 403; ripples)
- https://landinfo.com/?p=5368 (HTTP 403; commercial UAE 30 m DEM listing)
- https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm-1 (HTTP 403)
- https://journal.ut.ac.ir/article_95482_477f35bea1365623d36f498ba7beb633.pdf (tunnel closed)
- https://falghaleb.kau.edu.sa/Files/320/Researches/51283_21473.pdf (no response)
- https://geolsoc.figshare.com/articles/journal_contribution/Figure_S3_Gone_with_the_wind_Dune_provenance_and_sediment_recycling_in_the_northern_Rub_al-Khali_United_Arab_Emirates_Arabia_/7296959/1 (HTTP 202, empty; would have given UAE dune sand provenance/grain data)
- https://elib.dlr.de/91928/ (Martone et al. 2016 full text, TanDEM-X over sandy areas; only the abstract page read)
- https://www.planet.com/nicfi/ (fetched, but no coverage/licence statement obtained)
- https://www.usgs.gov/landsat-missions/landsat-9 (HTTP 403; Landsat resolution taken from landsat.gsfc.nasa.gov instead)
- Lancaster (1995) linear dune table (original), Sutton et al. (2013a, 2013b) slip-face experiments, Glennie (1970/2005): not located; secondhand values flagged in morphology_rows.csv.
- Bayanat dataset catalogue (https://bayanat.ae) not searched beyond the home page returning 200.
