# Getting the ICESat-2 profiles of stage 19 (free; no paid service)

`scripts/icesat2_profiles.py fetch` normally does everything: it asks the public SlideRule Earth service (https://slideruleearth.io, free, no login) to compute ATL06 style segments from the ICESat-2 ATL03 photons on demand, one request per target and year, and caches them under `data/raw/icesat2/` (git ignored), with the SHA-256 of every file in `results/icesat2/fetch_manifest.csv`. On 2026-10-21 it worked from the cloud machine of the session.

If SlideRule cannot be reached from your machine:

1. Install the client: `pip install sliderule` (free). The script sets the client to use your proxy settings.
2. Check the service: open https://sliderule.slideruleearth.io/source/version in a browser; it should show a version number.
3. Run `python3 scripts/icesat2_profiles.py fetch --targets WhiteSands,Kelso,A,B,C --lengths 10`; a target and year already cached is skipped, so the command can be repeated.
4. If the service is down, the same segments can be made from the NASA ATL03 granules: create a free NASA Earthdata account (https://urs.earthdata.nasa.gov), set the token in an environment variable `EARTHDATA_TOKEN` (never commit it), and use the free `earthaccess` Python package to download the ATL03 granules that cross the polygons printed by `target_polygon()` in the script. This route needs a local ATL06 style processing step that this repository does not include; SlideRule is the supported route.
5. After fetching, run `PYTHONPATH=src python3 scripts/icesat2_profiles.py analyse` and compare `results/icesat2/fetch_manifest.csv` with the committed one: the same SHA-256 means the same data.

Data: ICESat-2 ATL03 (NASA, distributed by NSIDC), processed on demand by SlideRule Earth; see `docs/DATA_AND_LICENSES.md` for the terms.
