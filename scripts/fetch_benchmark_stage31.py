#!/usr/bin/env python3
"""Fetch the two extra free 30 m products of stage 31 part e (docs/PREDICTIONS.md) for the six lidar dune windows.

    PYTHONPATH=src python3 scripts/fetch_benchmark_stage31.py

Products (PUBLISHED, free; crops are read remotely from cloud optimised GeoTIFFs on their own grid, nothing else is
downloaded):
  AW3D30   JAXA ALOS World 3D 30 m digital surface model (optical stereo), Microsoft Planetary Computer collection
           alos-dem (free licence of JAXA, attribution required)
  FABDEM   FABDEM v1.2 (Copernicus GLO-30 with forest and building heights removed, University of Bristol; free for
           non commercial use), read from the public mirror links-ads/fabdem on Hugging Face, whose tiles are stated to
           keep the original pixel values
Outputs (git ignored): data/raw/extra/aw3d30/<site>.tif, data/raw/extra/fabdem/<site>.tif and entries in
data/raw/extra/MANIFEST.json (source, SHA-256 of every crop).
"""
from __future__ import annotations
import json, math, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
import fetch_benchmark_extra as FX  # noqa: E402
import benchmark_detection as BD  # noqa: E402

FAB = "https://huggingface.co/buckets/links-ads/fabdem/resolve/tiles"


def fabdem_tile(lat, lon):
    """FABDEM tiles are named by their south west corner and grouped in 10 degree folders."""
    la, lo = math.floor(lat), math.floor(lon)
    f_la, f_lo = 10 * math.floor(la / 10), 10 * math.floor(lo / 10)

    def ns(v):
        return f"{'N' if v >= 0 else 'S'}{abs(v):02d}"

    def ew(v):
        return f"{'E' if v >= 0 else 'W'}{abs(v):03d}"
    folder = f"{ns(f_la)}{ew(f_lo)}-{ns(f_la + 10)}{ew(f_lo + 10)}_FABDEM_V1-2"
    return f"{FAB}/{folder}/{ns(la)}{ew(lo)}_FABDEM_V1-2.tif"


def main():
    from pystac_client import Client
    import planetary_computer as pc
    man_path = os.path.join(FX.OUT, "MANIFEST.json")
    manifest = json.load(open(man_path)) if os.path.exists(man_path) else {}
    pcs = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
    for site in BD.SITES:
        t0 = time.time()
        win, epsg, bbox = FX.site_geometry(site)
        # AW3D30
        p = os.path.join(FX.OUT, "aw3d30", f"{site}.tif"); os.makedirs(os.path.dirname(p), exist_ok=True)
        items = list(pcs.search(collections=["alos-dem"], bbox=bbox).items())
        assert len(items) == 1, (site, [i.id for i in items])
        if not os.path.exists(p):
            FX.crop_native(items[0].assets["data"].href, bbox, p)
        manifest[f"AW3D30|{site}"] = {"source": f"planetarycomputer alos-dem {items[0].id}", "sha256": FX.sha256(p),
                                      "retrieved": time.strftime("%Y-%m-%d")}
        # FABDEM
        tiles = sorted({fabdem_tile(la, lo) for lo in (bbox[0], bbox[2]) for la in (bbox[1], bbox[3])})
        assert len(tiles) == 1, (site, tiles)
        p = os.path.join(FX.OUT, "fabdem", f"{site}.tif"); os.makedirs(os.path.dirname(p), exist_ok=True)
        if not os.path.exists(p):
            FX.crop_native("/vsicurl/" + tiles[0], bbox, p)
        manifest[f"FABDEM|{site}"] = {"source": tiles[0], "sha256": FX.sha256(p), "retrieved": time.strftime("%Y-%m-%d")}
        json.dump(manifest, open(man_path, "w"), indent=1)
        print(f"{site}: done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
