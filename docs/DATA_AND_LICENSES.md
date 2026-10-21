# Data and software licences

Retrieval date for everything below: 2026-10-11 (the GLO-30 licence text and the area C tile, 2026-10-12). Dataset licences were read from provider pages by the data audit step (`research/raw/data_audit.csv` has the page URLs). Library licences were read from the installed package metadata. Nothing here is legal advice; read the provider's own terms before redistributing or using commercially.

## Datasets used by the code

| Dataset | Used for | Licence (as read) | Notes |
|---|---|---|---|
| Copernicus DEM GLO-30, tiles N23E053, N22E054 (phase 1) and N20E052 (phase 2, area C) (AWS open data copy, 1 arcsec, DSM from TanDEM-X, acquired Dec 2010 to Jan 2015) | All simulation results in `results/` | **Read in full (phase 2):** "Licence for Copernicus DEM instance COP-DEM-GLO-30-F Global 30m Full, Free and Open", pages 22 to 24 of the Copernicus Data Space "Contributing Mission Data Access" licence bundle (https://dataspace.copernicus.eu/sites/default/files/media/files/2025-06/copernicus_contributing_mission_data_access_v2_cop_dem_licenses.pdf). Worldwide, free of charge, no time limit; rights of reproduction, distribution, communication to the public, adaptation and combination (Articles 3 to 5). Conditions (Article 6): the notice "(c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018, provided under COPERNICUS by the European Union and ESA, all rights reserved" when communicating or distributing the data; for modified or adapted data the notice "produced using Copernicus WorldDEM-30" plus the same wording; the no liability sentence passed on to recipients; no implied official endorsement. Data supplied "as is" (Article 7). | The licence text contains no restriction on commercial use and does not mention it either: commercial use is permitted in effect, by silence, not by an express statement. The restrictive non commercial licences in the same bundle (the contributing mission licence and GLO-30-R) are different documents and do not apply to the Free and Open instance. The AWS "GLO-30 Public" copy used here is derived from the COP-DEM GLO-30-DGED product; that it is the Free and Open instance is the AWS registry's statement, which points to the same Copernicus page. The older sources (Earth Engine, AWS registry) were consistent with this reading. The 10 m WorldDEM product is excluded from this licence and is not used. Tiles are not committed to git; `data/raw/MANIFEST.md` has URLs and SHA-256 values. Attribution notice used in the figures: "Copernicus GLO-30 (c) DLR/Airbus; processing by this repo" (shortened for figure footers; the full notice is above and must be used when redistributing derived data). |

## Datasets downloaded or inspected for the audit only (not used in `results/`)

| Dataset | Licence as read | Used? |
|---|---|---|
| Copernicus GLO-90 tile N23E053 | Same family as GLO-30 | Resolution comparison in the data audit only |
| SRTM derived "skadi" tile N23E053 (Tilezen/joerd) | Attribution terms of the joerd project; SRTM courtesy USGS | Cross check in the data audit only |
| Copernicus GLO-30 tiles N22E053, N21E051, N21E053, N21E054 | As GLO-30 | Whole tile statistics (N22E053) and a visual search for linear dunes (the N21 tiles, shown as hillshade only, not used in `results/`) |
| NASADEM, ASTER GDEM v3, ICESat-2, GEDI | Free with an Earthdata login (EOSDIS terms) | Not downloaded |
| ALOS AW3D30 v4.1 | Free after registration under JAXA terms (terms page not read) | Not downloaded |
| TanDEM-X 90 m (DLR) | Scientific use only, registration | Not downloaded |
| FABDEM v1-2 | CC BY-NC-SA 4.0 | Not downloaded |
| Sentinel-2 L2A | Free, full and open | Catalogue search only |
| Maxar Open Data | CC BY-NC 4.0, event based, no Gulf events found | Catalogue read only |
| SoilGrids 2.0 sand fraction | CC BY 4.0 | Header request only |
| Abu Dhabi SDI open data (habitat/geology polygons) | Licence field empty in the service metadata | Service metadata only |

Not open or not found: Pleiades Neo (commercial), airborne LiDAR or drone DEMs over the Rub' al Khali (none found), a sand colour or grain size map of the Empty Quarter (not found).

## Software

| Library | Version | Licence | Where read |
|---|---|---|---|
| numpy | 2.5.3 | BSD-3-Clause (bundled components under 0BSD, MIT, Zlib, CC0-1.0) | package metadata |
| scipy | 1.18.1 | BSD (classifier "OSI Approved :: BSD License") | package metadata |
| matplotlib | 3.11.2 | Matplotlib licence (classifier "Python Software Foundation License") | package metadata |
| tifffile | 2026.9.15 | BSD-3-Clause | package metadata |
| imagecodecs | 2026.10.10 | BSD-3-Clause | package metadata |
| pytest (development only) | 9.1.1 | MIT | package metadata |

**Environment used for the 2026-10-15 work** (verification of the 26 supplementary rows, `scripts/anchor_comparisons.py`, the revised ladder and power study, the report rebuild). Versions and licences read from the installed package metadata on 2026-10-15; earlier results were produced with the versions in the table above and were not re run except where stated in `docs/PREDICTIONS.md`.

| Library or tool | Version | Licence as read | Use |
|---|---|---|---|
| numpy | 2.4.2 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 (License-Expression field) | all new scripts |
| scipy | 1.17.0 | BSD (classifier "OSI Approved :: BSD License") | Latin hypercube draws, bounded least squares |
| matplotlib | 3.10.8 | Matplotlib licence (classifier "Python Software Foundation License") | figures in `results/anchors/figures/` |
| tifffile | 2026.9.20 | BSD-3-Clause | imported by the package; installed so the tests run |
| imagecodecs | 2026.10.10 | BSD-3-Clause | installed with tifffile |
| pytest (development only) | 9.1.0 | MIT | tests |
| pypdf | 6.14.2 | BSD-3-Clause | reading the supplied PDFs during verification only; not used by repository code |
| pdftotext (Xpdf tools, Glyph and Cog) | 4.00 | not read (no licence file found on this machine) | reading the supplied PDFs during verification only; not used by repository code |
| pandoc (from pypandoc_binary) | 3.9 | GPL version 2 or later, with noted exceptions (its bundled COPYRIGHT.txt); the pypandoc_binary wrapper 1.17 is MIT | building `docs/REPORT.pdf` and `docs/EXECUTIVE_BRIEF.pdf` with `scripts/build_pdf.py`; a tool run locally, not distributed |
| playwright (with its Chromium build) | 1.64.0 | Apache-2.0 (package metadata); Chromium's own licence not read | PDF rendering in `scripts/build_pdf.py`; not distributed |
| pyee, greenlet (playwright dependencies) | 14.0.0, 3.5.6 | MIT; MIT AND PSF-2.0 | as above |

**Elevation tiles for stage 7.** The three GLO-30 tiles were downloaded again on 2026-10-15 with `scripts/fetch_data.sh` (SHA-256 values matched `data/raw/MANIFEST.md`) for `scripts/study_dumont_prior.py`; they are not committed and the licence terms above apply.

**Published papers supplied by the author (2026-10-13)** and read for numbers: Heverly et al. 2013, Ishigami et al. 2007 and 2009 (Journal of Field Robotics, Wiley), Yu et al. 2024 and Takehana et al. 2025 (Journal of Terramechanics, Elsevier). They remain under their publishers' terms; the PDFs are not committed and no figure or passage is reproduced beyond short attributed numbers in `research/evidence.csv`. The Dumont Dunes cubic coefficients (FLD-HV13-1) are used as published numbers in `scripts/anchor_comparisons.py` and `src/dunerover/fieldanalysis.py` (synthetic truth `dumont`).

Project Chrono (BSD 3-clause, verified from its LICENSE file) was reviewed in the literature step; from 2026-10-20 it is used by `scripts/chrono_wheel_slope.py` (stage 14, see below).

## Datasets mentioned in the literature review

RELLIS-3D (CC BY-NC-SA 3.0), TAIL (GPLv3), TartanDrive (MIT shown on the repository, dataset terms not verified), AI4Mars and the Perseverance driving set (no licence stated). See `research/raw/learning_notes.md`. None is redistributed here.

## This repository

**All rights reserved (decided by the author, 2026-10-12):** the repository is public for reading and review. Code, documents, tables and figures may not be used, modified, distributed or sold without prior written permission (`LICENSE`, `LICENSE-DOCS.md`); anyone wishing to do so should contact the author first. Third party material keeps its own terms: the GLO-30 notice above applies to anything derived from the elevation data, and quotations and numbers in the evidence table remain the property of their sources. Source PDFs and raw downloads are not distributed (`scripts/check_repo_hygiene.py` fails the CI job if they are committed). An earlier commit (ed7eedb, 2026-10-12) carried a proposed MIT licence, which was replaced by the all rights reserved notice the same day (commit cb3370c); the history was left as it is.

No new dataset or library was added for the 2026-10-18 work; it used the environment recorded above. The original phase 1 and phase 2 runs were made in an earlier environment (Python 3.13.16 is recorded in their summaries); the 2026-10-18 runs used Python 3.13.0 with numpy 2.4.2 and scipy 1.17.0. An independent rerun of the original phase 2 in the 2026-10-18 environment reproduced the committed class shares byte for byte (second review, `docs/REVIEW_2026-10-18.md`).

## Added 2026-10-20

| Data or tool | Licence as read | Retrieved | Use |
|---|---|---|---|
| USGS 3DEP one metre DEM tiles USGS_1M_11_x56y395_CA_FEMAR9Southeast_D24, USGS_1M_13_x37y364_NM_WhiteSandsNM_2020_D20, USGS_1M_11_x61y387_CA_FEMAR9Southeast_D24 (and x57y395, downloaded, not used) | public domain ("All 3DEP products are public domain", TNM Access API product description) | 2026-10-20 from https://prd-tnm.s3.amazonaws.com via https://tnmaccess.nationalmap.gov/api/v1/products | stages 12, 13 and 17; not committed (`data/raw/lidar/`, git ignored); SHA-256 in `results/terrain_validation/summary.json` |
| ERA5 hourly 10 m wind through the Open-Meteo archive API (https://archive-api.open-meteo.com), 2015 to 2024 | Open-Meteo API data CC BY 4.0 (its licence page, read 2026-10-20), weather reanalysis from the Copernicus Climate Change Service under the Copernicus licence; attribution: Weather data by Open-Meteo.com, ERA5 by ECMWF for C3S | 2026-10-20 | stage 13; raw responses not committed (`data/raw/wind/`, git ignored) |
| Project Chrono, pychrono 9.0.1 (conda package from the projectchrono channel) | BSD 3-Clause (package metadata, `conda-meta`) | 2026-10-20 | stage 14 single wheel simulation, run in a separate environment; not distributed |
| micromamba 2.9.0 | BSD 3-Clause (project licence, not re read on this machine) | 2026-10-20 from GitHub releases | installing pychrono only |
| emcee 3.1.6 | MIT (package metadata) | 2026-10-20 | MCMC calibration in `scripts/model_validation.py` (stage 15) |
| pyproj 3.8.0 | licence field empty in package metadata; not used by repository code | 2026-10-20 | one off conversion of the lidar window centres to latitude and longitude, written into `scripts/wind_face_direction.py` |

New papers read for evidence rows in phase 3 are listed with their licences in `research/phase3/*_references.csv`. The PDFs are kept in `research/sources/phase3/` (git ignored) and are not distributed.

**Digitised curves (`research/phase3/curves.csv`, `research/phase3/digitise/`, `research/phase3/tabulated/`).** These files hold numbers read from published figures and tables (marker coordinates and calibration points), not images or text of the sources; each point carries its source, figure and page. Licences as recorded by Crossref on 2026-10-20, or as found:

| Source key | Source | Licence as read |
|---|---|---|
| heverly2013 | Heverly et al. 2013, J. Field Robotics, doi 10.1002/rob.21481 | Wiley terms and conditions (Crossref licence field); PDF supplied by the author |
| ishigami2007 | Ishigami et al. 2007, J. Field Robotics, doi 10.1002/rob.20187 | Wiley terms and conditions (Crossref); PDF supplied by the author |
| li2008 | Li et al. 2008, J. Geophys. Res., doi 10.1029/2008JE003097 | Wiley terms and conditions (Crossref) |
| hurrell2025 | Hurrell et al. 2025, Space Science Reviews, doi 10.1007/s11214-025-01164-8 | CC BY 4.0 (Crossref) |
| takehana2025 | Takehana et al. 2025, J. Terramechanics, doi 10.1016/j.jterra.2025.101084 | CC BY 4.0 for the version of record (Crossref) |
| inotsume2016 | Inotsume, MSc thesis 2016, CMU Robotics Institute publications page | no licence statement found; not checked further |
| yoshida2010 | Yoshida, workshop slides, ICRA 2010 | no licence statement found; not checked further |

Short factual extracts of this kind are used with attribution; the repository's all rights reserved notice does not extend to them.

## Added 2026-10-21

| Item | Use | Terms (as checked) |
|---|---|---|
| ICESat-2 ATL03 photon data (NASA), processed on demand into ATL06 style segments by the public SlideRule Earth service | Stage 19 (`scripts/icesat2_profiles.py`); cached under `data/raw/icesat2/` (git ignored), checksums in `results/icesat2/fetch_manifest.csv` | NASA Earth science data, free and open; no login used. SlideRule Python client `sliderule` 5.6.3 (PyPI licence field: BSD-3-Clause) |
| USGS 3DEP one metre DEM tiles of Great Sand Dunes (CO_SanLuisJuanMiguel_2020_D20), Algodones (CA_SaltonSea_EarthMRI_2021_D21) and Little Sahara (UT_StatewideCenSouth_2020_A20) | Stage 20; fetched by `scripts/fetch_lidar.sh` with SHA-256 | USGS, public domain (as the stage 12 tiles) |
| Three further candidate tiles (Great Sand Dunes x44y418, Coral Pink x34y411, Monahans x70y350) | Downloaded to choose the windows; not used in any metric (reasons in stage 20) | USGS, public domain |
| ROS 2 Jazzy through RoboStack (conda, free) | `demo/ros2/` smoke test | Free open source packages; licences as stated by each package (not checked individually here) |
| DEM-Engine (`deme` on PyPI) | `notebooks/chrono_dem_gpu.ipynb` (not run here) | BSD-3-Clause (SPDX line in the DEM-Engine sources read on 2026-10-21) |
| Digitised curves of seven new sources (`research/phase4/`) | Stages 21 and 22 | Numbers read from figures of retrieved full texts; the figures themselves are not copied into the repository; source licences in `research/phase4/curves_*_references.csv` |
