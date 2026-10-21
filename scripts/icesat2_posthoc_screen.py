#!/usr/bin/env python3
"""POST HOC checks of the stage 19 Arabian reading, written after the final review of 2026-10-21
(docs/REVIEW_2026-10-21.md). Nothing here changes a registered outcome.

    PYTHONPATH=src python3 scripts/icesat2_posthoc_screen.py

1. Base rate: the share of all valid segments that fall in TRAVERSABLE cells, beside the share of face crossings, and
   their ratio (a face crossing placed at random would score the base rate).
2. Noise screen: a face crossing is "isolated" when no other face crossing of the same beam pass lies within 6 m along
   the track; segments overlap by half, so a real face longer than about 15 m appears in at least two segments. The
   TRAVERSABLE share is recomputed on the non isolated crossings between 28 and 35 deg (the published range of
   angles of repose of dry sand ends near 35 deg).
3. Kelso equivalent of the Copernicus gap: for ICESat-2 segments at 28 deg or more inside the passes of the
   validation, the along track slope of the lidar surface block averaged to 30 m (as a 30 m DEM would show it) and of
   the one metre lidar on the same line.
Output: results/icesat2/posthoc_screen.csv and posthoc_kelso_gap.csv. PUBLISHED data scored by SIMULATED BY ME code.
"""
from __future__ import annotations
import csv, os, sys
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import icesat2_profiles as I  # noqa: E402

OUT = I.OUT


def screen():
    met = {r["area"]: r for r in csv.DictReader(open(os.path.join(OUT, "arabia_metrics.csv"))) if r["length_m"] == "10"}
    rows = []
    for a in ("A", "B", "C"):
        f = pd.read_csv(os.path.join(OUT, f"face_segments_{a}_L10.csv")).sort_values(["track", "x_atc"])
        iso = np.ones(len(f), bool)
        for _, g in f.groupby("track"):
            x = g["x_atc"].values; idx = g.index.values
            near = np.zeros(len(x), bool)
            near[1:] |= np.diff(x) <= 6.0; near[:-1] |= np.diff(x) <= 6.0
            iso[f.index.get_indexer(idx)] = ~near
        keep = (~iso) & (f["abs_slope_deg"].values <= 35.0)
        base = float(met[a]["all_in_traversable_original"])
        trav_all = float(np.mean(f["class_original"].values == 0))
        trav_keep = float(np.mean(f["class_original"].values[keep] == 0)) if keep.sum() else float("nan")
        rows.append({"area": a, "face_crossings": len(f), "isolated_share": round(float(iso.mean()), 4),
                     "kept_non_isolated_28_35deg": int(keep.sum()),
                     "base_rate_all_segments_in_traversable": round(base, 4),
                     "faces_in_traversable_all": round(trav_all, 4), "ratio_to_base_all": round(trav_all / base, 3),
                     "faces_in_traversable_kept": round(trav_keep, 4), "ratio_to_base_kept": round(trav_keep / base, 3)})
    with open(os.path.join(OUT, "posthoc_screen.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r)


def kelso_gap():
    import tifffile
    from pyproj import Transformer
    v = I.VALIDATION["Kelso"]
    d = I.load_segments("Kelso", 10)
    t = np.array(d["time"], dtype="datetime64[ns]")
    d = d[(t >= np.datetime64(v["t0"][:19])) & (t <= np.datetime64(v["t1"][:19]))].reset_index(drop=True)
    p = tifffile.TiffFile(os.path.join(I.LIDAR, v["tile"])).pages[0]
    tie, sc = p.tags["ModelTiepointTag"].value, p.tags["ModelPixelScaleTag"].value
    e0, n0, px = float(tie[3]), float(tie[4]), float(sc[0])
    z = p.asarray().astype(np.float32); z[z < -1000] = np.nan
    k = 30; nr, nc = (z.shape[0] // k) * k, (z.shape[1] // k) * k
    z30 = np.nanmean(z[:nr, :nc].reshape(nr // k, k, nc // k, k), axis=(1, 3))
    E, N = Transformer.from_crs(4326, v["epsg"], always_xy=True).transform(d["lon"].values, d["lat"].values)
    win = v["window"]
    m = (E >= win[0]) & (E <= win[1]) & (N >= win[2]) & (N <= win[3]) & (np.abs(d["slope_deg"].values) >= 28.0)
    a = np.radians(d["az"].values[m])[:, None]
    s1 = np.arange(-5.0, 5.01, 1.0); s30 = np.arange(-15.0, 15.01, 1.0)
    def line(zz, step, s):
        Es, Ns = E[m][:, None] + s[None, :] * np.sin(a), N[m][:, None] + s[None, :] * np.cos(a)
        return I.line_fit_slope(I.bilinear(zz, (n0 - Ns) / step - 0.5, (Es - e0) / step - 0.5), s)
    l1, l30 = np.abs(line(z, 1.0, s1)), np.abs(line(z30, 30.0, s30))
    is2 = np.abs(d["slope_deg"].values[m])
    ok = np.isfinite(l1) & np.isfinite(l30)
    row = {"site": "Kelso", "passes": int(d[m]["track"].nunique()), "is2_segments_28deg": int(m.sum()),
           "median_is2_deg": round(float(np.median(is2[ok])), 2), "median_lidar_1m_same_line_deg": round(float(np.median(l1[ok])), 2),
           "median_lidar_30m_block_same_line_deg": round(float(np.median(l30[ok])), 2),
           "median_is2_minus_lidar30_deg": round(float(np.median(is2[ok] - l30[ok])), 2),
           "median_lidar1_minus_lidar30_deg": round(float(np.median(l1[ok] - l30[ok])), 2)}
    with open(os.path.join(OUT, "posthoc_kelso_gap.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(row)); w.writeheader(); w.writerow(row)
    print(row)


if __name__ == "__main__":
    screen()
    kelso_gap()
