# Data and software licences

Retrieval date for everything below: 2026-10-11. Dataset licences were read from provider pages by the data-audit step (`research/raw/data_audit.csv` has the page URLs). Library licences were read from the installed package metadata. Nothing here is legal advice; read the provider's own terms before redistributing or using commercially.

## Datasets used by the code

| Dataset | Used for | Licence (as read) | Notes |
|---|---|---|---|
| Copernicus DEM GLO-30, tiles N23E053 and N22E054 (AWS open-data copy, 1 arcsec, DSM from TanDEM-X, acquired Dec 2010 to Jan 2015) | All simulation results in `results/` | Free licence with an attribution notice: (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018, provided under COPERNICUS by the EU and ESA, plus a notice if the data are modified | The controlling licence document on spacedata.copernicus.eu timed out and was not read directly; the text above comes from the Earth Engine, Copernicus Data Space and AWS pages. Commercial-use terms are therefore unverified. Tiles are not committed to git; `data/raw/MANIFEST.md` has URLs and SHA-256 values. |

## Datasets downloaded or inspected for the audit only (not used in `results/`)

| Dataset | Licence as read | Used? |
|---|---|---|
| Copernicus GLO-90 tile N23E053 | Same family as GLO-30 | Resolution comparison in the data audit only |
| SRTM-derived "skadi" tile N23E053 (Tilezen/joerd) | Attribution terms of the joerd project; SRTM courtesy USGS | Cross-check in the data audit only |
| Copernicus GLO-30 tile N22E053 | As GLO-30 | Whole-tile statistics in the data audit only |
| NASADEM, ASTER GDEM v3, ICESat-2, GEDI | Free with an Earthdata login (EOSDIS terms) | Not downloaded |
| ALOS AW3D30 v4.1 | Free after registration under JAXA terms (terms page not read) | Not downloaded |
| TanDEM-X 90 m (DLR) | Scientific use only, registration | Not downloaded |
| FABDEM v1-2 | CC BY-NC-SA 4.0 | Not downloaded |
| Sentinel-2 L2A | Free, full and open | Catalogue search only |
| Maxar Open Data | CC BY-NC 4.0, event-based, no Gulf events found | Catalogue read only |
| SoilGrids 2.0 sand fraction | CC BY 4.0 | Header request only |
| Abu Dhabi SDI open data (habitat/geology polygons) | Licence field empty in the service metadata | Service metadata only |

Not open or not found: Pleiades Neo (commercial), airborne LiDAR or drone DEMs over the Rub' al Khali (none found), a sand-colour or grain-size map of the Empty Quarter (not found).

## Software

| Library | Version | Licence | Where read |
|---|---|---|---|
| numpy | 2.5.3 | BSD-3-Clause (bundled components under 0BSD, MIT, Zlib, CC0-1.0) | package metadata |
| scipy | 1.18.1 | BSD (classifier "OSI Approved :: BSD License") | package metadata |
| matplotlib | 3.11.2 | Matplotlib licence (classifier "Python Software Foundation License") | package metadata |
| tifffile | 2026.9.15 | BSD-3-Clause | package metadata |
| imagecodecs | 2026.10.10 | BSD-3-Clause | package metadata |
| pytest (development only) | 9.1.1 | MIT | package metadata |

Project Chrono (BSD 3-clause, verified from its LICENSE file) was reviewed in the literature step but is **not** used by this repository's code.

## Datasets mentioned in the literature review

RELLIS-3D (CC BY-NC-SA 3.0), TAIL (GPLv3), TartanDrive (MIT shown on the repository, dataset terms not verified), AI4Mars and the Perseverance driving set (no licence stated). See `research/raw/learning_notes.md`. None is redistributed here.

## This repository

No licence has been chosen for the code and documents yet. Until one is added, all rights are reserved by default. Add a `LICENSE` file before sharing it publicly.
