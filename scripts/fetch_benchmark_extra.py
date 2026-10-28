#!/usr/bin/env python3
"""Fetch the extra free inputs of stage 27 (docs/PREDICTIONS.md) for the six lidar dune windows of stages 25 and 26.

    PYTHONPATH=src python3 scripts/fetch_benchmark_extra.py

Products (all PUBLISHED, free, no account; crops are read remotely from cloud optimised GeoTIFFs, nothing else is
downloaded):
  3DEP13   USGS 3DEP 1/3 arc second DEM (about 10 m; public domain), prd-tnm.s3.amazonaws.com, native geographic grid
  NASADEM  NASADEM 1 arc second (SRTM 2000 reprocessed; public domain), Microsoft Planetary Computer, native grid
  S2       Sentinel-2 L2A surface reflectance, bands B02 B03 B04 B08 (10 m; Copernicus free licence), Element 84 Earth
           Search; one scene per site: the lidar year (or the nearest year with a scene), cloud cover below 5 %, lowest
           sun elevation (strongest shading of lee faces); resampled bilinearly to the 10 m grid of the window
  NAIP     USDA NAIP aerial imagery, red green blue near infrared (0.6 m to 1 m; public domain), Planetary Computer; the
           most recent year covering the window; resampled bilinearly to the one metre grid of the lidar window
Outputs (git ignored): data/raw/extra/<product>/<site>.tif and data/raw/extra/MANIFEST.json (source item, date, URL,
SHA-256 of every crop).
"""
from __future__ import annotations
import hashlib, json, os, sys, time
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
os.environ.setdefault("CURL_CA_BUNDLE", "/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else None
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
import rasterio  # noqa: E402
from rasterio.windows import from_bounds  # noqa: E402
from rasterio.warp import reproject, Resampling, transform_bounds  # noqa: E402
from rasterio.transform import from_origin  # noqa: E402
import benchmark_detection as BD  # noqa: E402

OUT = os.path.join(ROOT, "data", "raw", "extra")
MARGIN_DEG = 0.01
LIDAR_YEAR = {"Dumont": 2024, "WhiteSands": 2020, "Kelso": 2024, "GreatSandDunes": 2020, "Algodones": 2021, "LittleSahara": 2020}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def site_geometry(site):
    fname, win, _ = BD.SITES[site]
    import tifffile
    from dunerover import planner as PL
    with tifffile.TiffFile(os.path.join(BD.RAW, "lidar", fname)) as tf:
        keys, _ = PL._geokeys(tf.pages[0])
    epsg = int(keys.get(3072))
    lon0, lat0, lon1, lat1 = transform_bounds(f"EPSG:{epsg}", "EPSG:4326", win[0], win[2], win[1], win[3], densify_pts=21)
    return win, epsg, (lon0 - MARGIN_DEG, lat0 - MARGIN_DEG, lon1 + MARGIN_DEG, lat1 + MARGIN_DEG)


def crop_native(url, bbox, path, band_names=None):
    """Crop a geographic COG to bbox (lon/lat) on its own grid, no resampling."""
    with rasterio.open(url) as ds:
        b = transform_bounds("EPSG:4326", ds.crs, *bbox, densify_pts=21)
        w = from_bounds(*b, ds.transform).round_offsets().round_lengths()
        a = ds.read(window=w)
        prof = ds.profile.copy()
        prof.update(height=a.shape[1], width=a.shape[2], transform=ds.window_transform(w), driver="GTiff",
                    compress="deflate", tiled=False)
        for k in ("blockxsize", "blockysize", "interleave"):
            prof.pop(k, None)
        with rasterio.open(path, "w", **prof) as dst:
            dst.write(a)
            dst.update_tags(AREA_OR_POINT=ds.tags().get("AREA_OR_POINT", ""), SOURCE=url)


def warp_to_window(urls, win, epsg, res, path, nodata=0):
    """Bilinear resampling of one or more rasters (bands stacked in order) to the window grid at res metres."""
    w, h = int(round((win[1] - win[0]) / res)), int(round((win[3] - win[2]) / res))
    dst_t = from_origin(win[0], win[3], res, res)
    bands = []
    for url in urls:
        with rasterio.open(url) as ds:
            for bi in range(1, ds.count + 1):
                dst = np.zeros((h, w), np.float32)
                reproject(rasterio.band(ds, bi), dst, dst_transform=dst_t, dst_crs=f"EPSG:{epsg}",
                          resampling=Resampling.bilinear, src_nodata=ds.nodata if ds.nodata is not None else nodata, dst_nodata=np.nan)
                bands.append(dst)
    a = np.stack(bands)
    with rasterio.open(path, "w", driver="GTiff", height=h, width=w, count=a.shape[0], dtype="float32",
                       crs=f"EPSG:{epsg}", transform=dst_t, compress="deflate", nodata=np.nan) as dst:
        dst.write(a)


def mosaic_items_to_window(items, asset, win, epsg, res, path):
    """Several tiles of one product: warp each and keep the first valid value per pixel."""
    w, h = int(round((win[1] - win[0]) / res)), int(round((win[3] - win[2]) / res))
    dst_t = from_origin(win[0], win[3], res, res)
    out = None
    for it in items:
        url = it.assets[asset].href
        with rasterio.open(url) as ds:
            stack = []
            for bi in range(1, ds.count + 1):
                dst = np.full((h, w), np.nan, np.float32)
                reproject(rasterio.band(ds, bi), dst, dst_transform=dst_t, dst_crs=f"EPSG:{epsg}",
                          resampling=Resampling.bilinear, src_nodata=ds.nodata if ds.nodata is not None else 0, dst_nodata=np.nan)
                stack.append(dst)
        a = np.stack(stack)
        out = a if out is None else np.where(np.isnan(out), a, out)
    with rasterio.open(path, "w", driver="GTiff", height=h, width=w, count=out.shape[0], dtype="float32",
                       crs=f"EPSG:{epsg}", transform=dst_t, compress="deflate", nodata=np.nan) as dst:
        dst.write(out)
    return float(np.isnan(out[0]).mean())


def main():
    from pystac_client import Client
    import planetary_computer as pc
    os.makedirs(OUT, exist_ok=True)
    man_path = os.path.join(OUT, "MANIFEST.json")
    manifest = json.load(open(man_path)) if os.path.exists(man_path) else {}
    pcs = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
    es = Client.open("https://earth-search.aws.element84.com/v1")
    for site in BD.SITES:
        win, epsg, bbox = site_geometry(site)
        t0 = time.time()
        # 3DEP 1/3 arc second: the 1 x 1 degree tile named by its north west corner
        import math
        tiles = sorted({f"n{math.ceil(lat):02d}w{math.ceil(-lon):03d}" for lon in (bbox[0], bbox[2]) for lat in (bbox[1], bbox[3])})
        assert len(tiles) == 1, (site, tiles)
        url = f"/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/{tiles[0]}/USGS_13_{tiles[0]}.tif"
        p = os.path.join(OUT, "3dep13", f"{site}.tif"); os.makedirs(os.path.dirname(p), exist_ok=True)
        if not os.path.exists(p):
            crop_native(url, bbox, p)
        manifest[f"3DEP13|{site}"] = {"source": url.replace("/vsicurl/", ""), "sha256": sha256(p), "retrieved": time.strftime("%Y-%m-%d")}
        # NASADEM
        items = list(pcs.search(collections=["nasadem"], bbox=bbox).items())
        assert len(items) == 1, (site, [i.id for i in items])
        p = os.path.join(OUT, "nasadem", f"{site}.tif"); os.makedirs(os.path.dirname(p), exist_ok=True)
        if not os.path.exists(p):
            crop_native(items[0].assets["elevation"].href, bbox, p)
        manifest[f"NASADEM|{site}"] = {"source": f"planetarycomputer nasadem {items[0].id}", "sha256": sha256(p), "retrieved": time.strftime("%Y-%m-%d")}
        # Sentinel-2 L2A
        p = os.path.join(OUT, "s2", f"{site}.tif"); os.makedirs(os.path.dirname(p), exist_ok=True)
        if not os.path.exists(p):
            chosen = None
            for dy in (0, 1, -1, 2, -2):
                yr = LIDAR_YEAR[site] + dy
                its = [i for i in es.search(collections=["sentinel-2-l2a"], intersects={"type": "Point", "coordinates": [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]},
                                            datetime=f"{yr}-01-01/{yr}-12-31", query={"eo:cloud_cover": {"lt": 5}}, max_items=400).items()]
                # the scene must contain the whole window
                from shapely.geometry import shape, box
                its = [i for i in its if shape(i.geometry).contains(box(*bbox))]
                if its:
                    chosen = min(its, key=lambda i: (i.properties.get("view:sun_elevation", 90), i.id))
                    break
            assert chosen is not None, site
            urls = [chosen.assets[b].href for b in ("blue", "green", "red", "nir")]
            warp_to_window(urls, win, epsg, 10.0, p)
            manifest[f"S2|{site}"] = {"source": f"earth-search sentinel-2-l2a {chosen.id}", "date": chosen.properties["datetime"],
                                      "sun_elevation": chosen.properties.get("view:sun_elevation"), "sun_azimuth": chosen.properties.get("view:sun_azimuth"),
                                      "cloud_cover": chosen.properties.get("eo:cloud_cover"), "sha256": sha256(p), "retrieved": time.strftime("%Y-%m-%d")}
        # NAIP: most recent year covering the window (all quarter quads of that year)
        p = os.path.join(OUT, "naip", f"{site}.tif"); os.makedirs(os.path.dirname(p), exist_ok=True)
        if not os.path.exists(p):
            its = list(pcs.search(collections=["naip"], bbox=bbox).items())
            yr = max(int(i.properties["naip:year"]) for i in its)
            sel = sorted([i for i in its if int(i.properties["naip:year"]) == yr], key=lambda i: i.id)
            void = mosaic_items_to_window(sel, "image", win, epsg, 1.0, p)
            manifest[f"NAIP|{site}"] = {"source": "planetarycomputer naip " + ", ".join(i.id for i in sel), "year": yr,
                                        "resolution_m": sel[0].properties.get("gsd"), "void_share": round(void, 4),
                                        "sha256": sha256(p), "retrieved": time.strftime("%Y-%m-%d")}
        json.dump(manifest, open(man_path, "w"), indent=1)
        print(f"{site}: done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
