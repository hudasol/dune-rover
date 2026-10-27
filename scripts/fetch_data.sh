#!/usr/bin/env bash
# Download the Copernicus GLO-30 tiles used by the study into data/raw/ and check their SHA-256 values.
# Licence: Copernicus DEM GLO-30 free licence with attribution (c) DLR e.V. and (c) Airbus Defence and Space GmbH,
# provided under COPERNICUS by the EU and ESA. Read the provider's own terms before redistributing.
# Tiles are not committed to git (see .gitignore). Source: AWS open-data copy, no account needed.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/raw
fetch() {
  local name="$1" sha="$2"
  local url="https://copernicus-dem-30m.s3.amazonaws.com/${name%.tif}/${name}"
  if [ ! -f "data/raw/${name}" ]; then
    echo "downloading ${name}"
    curl -fSL --retry 3 -o "data/raw/${name}" "${url}"
  fi
  echo "${sha}  data/raw/${name}" | sha256sum -c -
}
fetch Copernicus_DSM_COG_10_N23_00_E053_00_DEM.tif 1b6bb95ecf03a2e89d0f10cae5cd125ffdfd49994f0dbe6ba6c3242bde699a96
fetch Copernicus_DSM_COG_10_N22_00_E054_00_DEM.tif a33e0813eb483f685034c491b78af126bb7736d64c29da0249e6eb68d679b882
fetch Copernicus_DSM_COG_10_N20_00_E052_00_DEM.tif b6c0fc66abac1032a53b6702a0b355a14ff65813f435ac6a0106e2620c90807b
# Stage 25 and 26 benchmark: GLO-30 tiles over the six North American lidar dune fields (retrieved 2026-10-27)
mkdir -p data/raw/glo30_us
fetch_us() {
  local name="$1" sha="$2"
  local url="https://copernicus-dem-30m.s3.amazonaws.com/${name%.tif}/${name}"
  if [ ! -f "data/raw/glo30_us/${name}" ]; then
    echo "downloading ${name}"
    curl -fSL --retry 3 -o "data/raw/glo30_us/${name}" "${url}"
  fi
  echo "${sha}  data/raw/glo30_us/${name}" | sha256sum -c -
}
fetch_us Copernicus_DSM_COG_10_N35_00_W117_00_DEM.tif fe8bccabf75fa8440f769bed7e5990fefa867240ff91664a51c7b2e60b46b999
fetch_us Copernicus_DSM_COG_10_N32_00_W107_00_DEM.tif 03d4e33f38cea565a3a011f4785b3578c3a8e9e8d537578db9b19602e1214fac
fetch_us Copernicus_DSM_COG_10_N34_00_W116_00_DEM.tif d33e98701a8927cd37430841d4d2c316a65641cc6889e1c492e7b9a0f660868c
fetch_us Copernicus_DSM_COG_10_N37_00_W106_00_DEM.tif 4108cfd7dd5c5cf2dbd5f082504eb5ed2b569679ec1a91a4b6bc679bb0723c12
fetch_us Copernicus_DSM_COG_10_N32_00_W116_00_DEM.tif 3b4c358d6a307c3886edcd549378dfaada7d0734beff722048e9d9e264d46b02
fetch_us Copernicus_DSM_COG_10_N39_00_W113_00_DEM.tif ed959c9dfe4202c33bacea15a96c73ee5da8bb97925f42d350db48db01d4bdfe
echo "done. Run: PYTHONPATH=src python3 -m dunerover.study --data data/raw --out results ; then PYTHONPATH=src python3 -m dunerover.study_subgrid --data data/raw --out results/subgrid"
