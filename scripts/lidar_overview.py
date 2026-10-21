#!/usr/bin/env python3
"""Overview slope images (20 m block means) of one metre lidar tiles, used only to choose the analysis window of a new
dune field before any metric is computed (the procedure of stage 12, repeated for stage 20).

    python3 scripts/lidar_overview.py TILE.tif [TILE.tif ...]

Writes results/terrain_validation_phase4/overview/<tile>_slope20m.png with UTM grid lines every kilometre.
"""
import os, sys
import numpy as np
import tifffile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "terrain_validation_phase4", "overview")


def main(files):
    os.makedirs(OUT, exist_ok=True)
    for f in files:
        p = tifffile.TiffFile(f).pages[0]
        tie, sc = p.tags["ModelTiepointTag"].value, p.tags["ModelPixelScaleTag"].value
        e0, n0, d = float(tie[3]), float(tie[4]), float(sc[0])
        z = p.asarray().astype(np.float32); z[z < -1000] = np.nan
        k = int(round(20 / d)); nr, nc = (z.shape[0] // k) * k, (z.shape[1] // k) * k
        zb = np.nanmean(z[:nr, :nc].reshape(nr // k, k, nc // k, k), axis=(1, 3)); del z
        gy, gx = np.gradient(zb, 20.0)
        s = np.degrees(np.arctan(np.hypot(gx, gy)))
        fig, ax = plt.subplots(figsize=(8, 8))
        ext = (e0, e0 + nc * d, n0 - nr * d, n0)
        im = ax.imshow(s, extent=ext, cmap="RdPu", vmin=0, vmax=25)
        ax.set_xticks(np.arange(np.ceil(ext[0] / 1000) * 1000, ext[1], 1000)); ax.set_yticks(np.arange(np.ceil(ext[2] / 1000) * 1000, ext[3], 1000))
        ax.tick_params(labelsize=6); plt.setp(ax.get_xticklabels(), rotation=90); ax.grid(color="#5b3a78", lw=0.3)
        plt.colorbar(im, ax=ax, shrink=0.7, label="slope at 20 m, deg")
        ax.set_title(os.path.basename(f), fontsize=8)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, os.path.basename(f).replace(".tif", "_slope20m.png")), dpi=110); plt.close(fig)
        print(os.path.basename(f), "extent", ext)


if __name__ == "__main__":
    main(sys.argv[1:])
