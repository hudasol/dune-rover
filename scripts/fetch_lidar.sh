#!/usr/bin/env bash
# Download the USGS 3DEP one metre DEM tiles used in stages 12, 13, 17, 19 and 20 (public domain) into data/raw/lidar/
# (git ignored) and check their SHA-256 against the values recorded in results/terrain_validation*/summary.json.
set -e
cd "$(dirname "$0")/.."
mkdir -p data/raw/lidar
B=https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects
while read -r proj tile sha; do
  f=data/raw/lidar/$tile
  [ -f "$f" ] || curl -sSL -o "$f" "$B/$proj/TIFF/$tile"
  echo "$sha  $f" | sha256sum -c -
done <<'LIST'
CA_FEMAR9Southeast_D24 USGS_1M_11_x56y395_CA_FEMAR9Southeast_D24.tif 92bf61b84f66b8911aa111aeea24f6b73ba374e18facf1e51ad361bbbe19c93a
NM_WhiteSandsNM_2020_D20 USGS_1M_13_x37y364_NM_WhiteSandsNM_2020_D20.tif 8a49fdeed74e4a9b77749e7b0641618d9d19d8dd20dfa280f7be738afd9bd9af
CA_FEMAR9Southeast_D24 USGS_1M_11_x61y387_CA_FEMAR9Southeast_D24.tif ffb88a0dda813af158cdcff08778565fe078baa75ac616568d6c61e061479e96
CO_SanLuisJuanMiguel_2020_D20 USGS_1M_13_x45y418_CO_SanLuisJuanMiguel_2020_D20.tif 56e7e5f399cfcc1c2516908f730842e7d68aedfb4393974e3010b3a492d42530
CA_SaltonSea_EarthMRI_2021_D21 USGS_1M_11_x67y365_CA_SaltonSea_EarthMRI_2021_D21.tif e6cae0c6a40555b1789d4988ba7b0bcbb7b77281199380217f7593c535b3803e
UT_StatewideCenSouth_2020_A20 USGS_1M_12_x38y440_UT_StatewideCenSouth_2020_A20.tif f310411a99f88467720889adb04d8ef8b5155de4e80324cd7820a59f52be0c5a
LIST
