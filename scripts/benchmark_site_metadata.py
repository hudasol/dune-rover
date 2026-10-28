#!/usr/bin/env python3
"""Site metadata table of the benchmark (review finding M15): window centre, extent, relief, lidar project and
acquisition period (USGS ScienceBase record of each 1 m DEM tile, queried through The National Map API), the GLO-30 tile
and the imagery scenes of stage 27.

    PYTHONPATH=src python3 scripts/benchmark_site_metadata.py

Output: results/benchmark/site_metadata.csv. PUBLISHED metadata; the table is mine.
"""
from __future__ import annotations
import csv, json, os, sys, urllib.request
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
import benchmark_detection as BD  # noqa: E402


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def main():
    from pyproj import Transformer
    from dunerover import benchmark as B
    man = json.load(open(os.path.join(ROOT, "data", "raw", "extra", "MANIFEST.json")))
    rows = []
    for site, (fname, win, tile) in BD.SITES.items():
        z1, e0, n0, epsg = BD.load_lidar_window(fname, win)
        lon, lat = Transformer.from_crs(epsg, 4326, always_xy=True).transform((win[0] + win[1]) / 2, (win[2] + win[3]) / 2)
        title = fname.replace(".tif", "").replace("USGS_1M_", "USGS 1 Meter ").replace("_x", " x").replace("_CA", " CA").replace("_NM", " NM").replace("_CO", " CO").replace("_UT", " UT")
        q = f"https://tnmaccess.nationalmap.gov/api/v1/products?datasets=Digital%20Elevation%20Model%20(DEM)%201%20meter&bbox={lon - 0.002},{lat - 0.002},{lon + 0.002},{lat + 0.002}&max=20"
        items = get(q).get("items", [])
        key = fname.replace(".tif", "").split("_", 4)[-1]
        it = next((i for i in items if key in i["title"].replace(" ", "_")), None)
        start = end = sb = ""
        if it:
            sb = it["metaUrl"]
            d = {x.get("type"): x.get("dateString") for x in get(sb + "?format=json").get("dates", [])}
            start, end = d.get("Start", ""), d.get("End", "")
        steep, _ = B.steep_posts(z1, np.isnan(z1))
        rows.append({"site": site, "centre_lat": round(lat, 4), "centre_lon": round(lon, 4), "epsg": epsg,
                     "extent_km": f"{(win[1] - win[0]) / 1000:g} x {(win[3] - win[2]) / 1000:g}", "area_km2": round((win[1] - win[0]) * (win[3] - win[2]) / 1e6, 1),
                     "relief_m": round(float(np.nanmax(z1) - np.nanmin(z1)), 0), "lidar_tile": fname.replace(".tif", ""),
                     "lidar_project": key, "acquisition_start": start, "acquisition_end": end, "sciencebase": sb,
                     "glo30_tile": tile.replace(".tif", ""), "sentinel2_scene": man.get(f"S2|{site}", {}).get("source", "").split()[-1],
                     "sentinel2_date": man.get(f"S2|{site}", {}).get("date", "")[:10], "naip_year": man.get(f"NAIP|{site}", {}).get("year", "")})
        print(site, start, end, flush=True)
    os.makedirs(os.path.join(ROOT, "results", "benchmark"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "benchmark", "site_metadata.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
