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
echo "done. Run: PYTHONPATH=src python3 -m dunerover.study --data data/raw --out results ; then PYTHONPATH=src python3 -m dunerover.study_subgrid --data data/raw --out results/subgrid"
