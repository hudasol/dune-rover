#!/usr/bin/env python3
"""Which lidar collection the USGS 1/3 arc second DEM (R10) was made from inside each benchmark window.

    PYTHONPATH=src python3 scripts/check_r10_source.py

Reads the source footprint file (GeoPackage) that USGS publishes next to every 1/3 arc second tile, intersects it with
the lidar window of each site and writes results/benchmark/r10_source.csv: the share of the window covered by each
source work package, its collection dates, and whether it is the same work package as the one metre lidar used as truth.
PUBLISHED metadata; the footprint files are kept under data/raw/extra/3dep13_src/ (not in the repository).
"""
from __future__ import annotations
import csv, json, os, sys, urllib.request
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
import benchmark_detection as BD  # noqa: E402

SRC = os.path.join(ROOT, "data", "raw", "extra", "3dep13_src")
OUT = os.path.join(ROOT, "results", "benchmark", "r10_source.csv")


def main():
    import geopandas as gpd
    from shapely.geometry import box
    os.makedirs(SRC, exist_ok=True)
    man = json.load(open(os.path.join(ROOT, "data", "raw", "extra", "MANIFEST.json")))
    meta = {r["site"]: r for r in csv.DictReader(open(os.path.join(ROOT, "results", "benchmark", "site_metadata.csv")))}
    rows = []
    for site, (fname, win, _) in BD.SITES.items():
        url = man[f"3DEP13|{site}"]["source"].replace(".tif", ".gpkg")
        path = os.path.join(SRC, os.path.basename(url))
        if not os.path.exists(path):
            urllib.request.urlretrieve(url, path)
        epsg = int(meta[site]["epsg"])
        g = gpd.read_file(path).to_crs(epsg)
        wbox = box(win[0], win[2], win[1], win[3])
        g["share"] = g.geometry.intersection(wbox).area / wbox.area
        for _, r in g[g["share"] > 0.001].sort_values("share", ascending=False).iterrows():
            rows.append({"site": site, "workpackage": r["workpackage"], "method": r["p_method"], "collect_start": str(r["collect_start"])[:10],
                         "collect_end": str(r["collect_end"])[:10], "window_share": round(float(r["share"]), 4),
                         "same_as_truth_lidar": r["workpackage"] == meta[site]["lidar_project"], "truth_lidar_project": meta[site]["lidar_project"]})
        print(site, [(x["workpackage"], x["window_share"]) for x in rows if x["site"] == site])
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
