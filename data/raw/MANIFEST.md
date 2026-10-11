# Raw data manifest (dune-rover)
Retrieval date for all files: 2026-10-11. All downloaded unauthenticated with curl from the hosts below; sizes are as served (Content-Length).
Licences were read from the provider pages listed in research/raw/data_audit.csv (not from memory); see that file for licence_url.

| filename | URL | bytes | retrieval_date | licence (short) | sha256 |
|---|---|---|---|---|---|
| Copernicus_DSM_COG_10_N23_00_E053_00_DEM.tif | https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N23_00_E053_00_DEM/Copernicus_DSM_COG_10_N23_00_E053_00_DEM.tif | 48561117 | 2026-10-11 | Copernicus GLO-30 free licence; attribution notice required (WorldDEM-30 (c) DLR/Airbus) | 1b6bb95ecf03a2e89d0f10cae5cd125ffdfd49994f0dbe6ba6c3242bde699a96 |
| Copernicus_DSM_COG_10_N22_00_E053_00_DEM.tif | https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N22_00_E053_00_DEM/Copernicus_DSM_COG_10_N22_00_E053_00_DEM.tif | 49450340 | 2026-10-11 | same as above | 7c26fc16425d639c5a06fadf5126211d786a0f97da179884c3e70aa983bb0faf |
| Copernicus_DSM_COG_10_N22_00_E054_00_DEM.tif | https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N22_00_E054_00_DEM/Copernicus_DSM_COG_10_N22_00_E054_00_DEM.tif | 48277338 | 2026-10-11 | same as above | a33e0813eb483f685034c491b78af126bb7736d64c29da0249e6eb68d679b882 |
| Copernicus_DSM_COG_30_N23_00_E053_00_DEM.tif (GLO-90, 3 arcsec) | https://copernicus-dem-90m.s3.amazonaws.com/Copernicus_DSM_COG_30_N23_00_E053_00_DEM/Copernicus_DSM_COG_30_N23_00_E053_00_DEM.tif | 5646288 | 2026-10-11 | same as above | 174bb8d89e2d9729b175b06b123ad5458186f2574a118de9c9cbdb9e01107b48 |
| N23E053.hgt.gz (Mapzen/Tilezen "skadi", SRTM-derived 1 arcsec) | https://s3.amazonaws.com/elevation-tiles-prod/skadi/N23/N23E053.hgt.gz | 8310302 | 2026-10-11 | Tilezen/joerd attribution terms (SRTM data courtesy USGS); see licence_url in audit | 3dbbc0d152b7b0116f7522f6051af01e4648bd292af60bb2d09c1b6d8f39d99b |
| Copernicus_DSM_COG_10_N20_00_E052_00_DEM.tif (phase 2, area C linear dunes) | https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N20_00_E052_00_DEM/Copernicus_DSM_COG_10_N20_00_E052_00_DEM.tif | 45931228 | 2026-10-12 | COP-DEM-GLO-30-F, read in full (docs/DATA_AND_LICENSES.md) | b6c0fc66abac1032a53b6702a0b355a14ff65813f435ac6a0106e2620c90807b |

Notes
- Tile naming: the COP30 tile "N23_00_E053" has its top-left post at 24.0N, 53.0E (GeoTIFF GTRasterTypeGeoKey = IsPoint, tiepoint 53.0, 24.0), i.e. it spans 23.0-24.0N, 53.0-54.0E (bottom row removed by the AWS repackaging: 3600x3600 posts). Name = lower-left corner.
- "skadi" N23E053.hgt: 3601x3601 big-endian int16, row 0 = 24.0N; gunzipped size 25,934,402 bytes (= 3601*3601*2).
- Derived products (slope statistics, hillshade PNGs) are in /home/claude/dune-rover/data/derived/ and are COMPUTED-BY-ME.
- (not committed) data/derived/tileList.txt was a copy of https://copernicus-dem-30m.s3.amazonaws.com/tileList.txt (26,450 lines) retrieved 2026-10-11 to check coverage.
