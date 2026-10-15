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

Project Chrono (BSD 3-clause, verified from its LICENSE file) was reviewed in the literature step but is **not** used by this repository's code.

## Datasets mentioned in the literature review

RELLIS-3D (CC BY-NC-SA 3.0), TAIL (GPLv3), TartanDrive (MIT shown on the repository, dataset terms not verified), AI4Mars and the Perseverance driving set (no licence stated). See `research/raw/learning_notes.md`. None is redistributed here.

## This repository

**All rights reserved (decided by the author, 2026-10-12):** the repository is public for reading and review. Code, documents, tables and figures may not be used, modified, distributed or sold without prior written permission (`LICENSE`, `LICENSE-DOCS.md`); anyone wishing to do so should contact the author first. Third party material keeps its own terms: the GLO-30 notice above applies to anything derived from the elevation data, and quotations and numbers in the evidence table remain the property of their sources. Source PDFs and raw downloads are not distributed (`scripts/check_repo_hygiene.py` fails the CI job if they are committed).
