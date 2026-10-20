"""Build research/phase3/curves.csv from per curve specification files.

Two kinds of specification are read:

* research/phase3/digitise/<curve_id>.json: a curve read from a figure. The
  named PDF page is rasterised with pdftoppm at a fixed dpi into
  research/sources/phase3/figures/ (git ignored). Two known ticks on each
  axis give the pixel to data calibration. Marker positions are either
  (a) found automatically by colour masking inside a crop box and summarised
  in bins ("cloud" mode, for dense scatter clouds), or (b) given as seed
  pixels read by eye from the rasterised page ("points" mode), optionally
  refined to the centroid of the marker colour within a small radius.
* research/phase3/tabulated/<curve_id>.json: a curve copied from a printed
  table or text, or evaluated from a published fit.

Uncertainty per point:

* digitisation: data units per pixel times the marker radius in pixels;
* cloud mode: the digitisation term combined in quadrature with half the
  interquartile range of the masked pixels in the bin (the spread of the
  published scatter), so x_unc and y_unc are not pure reading errors there;
* tables and text: as printed (for example half the width of a printed
  slope bin), otherwise "not reported".

Usage:
    python scripts/digitise_figures.py            # write curves.csv
    python scripts/digitise_figures.py --check    # rebuild and compare
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIGITISE_DIR = os.path.join(REPO, "research", "phase3", "digitise")
TABULATED_DIR = os.path.join(REPO, "research", "phase3", "tabulated")
FIG_DIR = os.path.join(REPO, "research", "sources", "phase3", "figures")
OUT_CSV = os.path.join(REPO, "research", "phase3", "curves.csv")
DEBUG = False  # set by --debug: write mask overlays and point overlays next to the rasters
DEBUG_PTS = []

COLUMNS = [
    "curve_id", "source_key", "source_title", "source_url", "evidence_row",
    "figure_or_table", "page", "x_name", "x_unit", "y_name", "y_unit",
    "x", "y", "x_unc", "y_unc", "method", "vehicle", "wheel_diameter_m",
    "wheel_width_m", "load_per_wheel_N", "grousers", "soil", "grain_size_mm",
    "bulk_density_kg_m3", "friction_angle_deg", "preparation", "test_type",
    "gravity_g", "slope_kind", "comparable_to_dune_sand", "comparability_note",
]
META_KEYS = [c for c in COLUMNS if c not in ("x", "y", "x_unc", "y_unc", "method")]
NR = "not reported"


# ---------------------------------------------------------------- helpers

def fmt(v, nd=4):
    """Format a number with nd significant decimals, or pass a string through."""
    if isinstance(v, str):
        return v
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return NR
    r = round(float(v), nd)
    if r == 0:
        r = 0.0
    s = f"{r:.{nd}f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def rasterise(pdf_rel, page, dpi):
    pdf = os.path.join(REPO, pdf_rel)
    stem = os.path.splitext(os.path.basename(pdf))[0]
    os.makedirs(FIG_DIR, exist_ok=True)
    prefix = os.path.join(FIG_DIR, f"{stem}_p{page}_{dpi}dpi")
    png = prefix + ".png"
    if not os.path.exists(png):
        subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page),
                        "-png", "-singlefile", pdf, prefix], check=True)
    return png


class Axis:
    """Maps a pixel coordinate on one axis to a data value."""

    def __init__(self, spec):
        (self.p1, self.p2) = [float(p) for p in spec["px"]]
        (self.v1, self.v2) = [float(v) for v in spec["val"]]
        self.log = spec.get("scale", "linear") == "log"
        if self.log:
            self.v1, self.v2 = math.log10(self.v1), math.log10(self.v2)

    def to_data(self, p):
        t = (np.asarray(p, dtype=float) - self.p1) / (self.p2 - self.p1)
        v = self.v1 + t * (self.v2 - self.v1)
        return np.power(10.0, v) if self.log else v

    def per_px(self, p):
        """Absolute data units per pixel at pixel coordinate p."""
        return abs(float(self.to_data(p + 0.5)) - float(self.to_data(p - 0.5)))


def colour_mask(img, rules):
    """Union of 'include' rules minus 'exclude' rules.

    A rule is {"rgb": [r, g, b], "tol": t} (Euclidean RGB distance), or
    {"min_saturation": s} (max minus min channel), or {"max_value": v}
    (all channels at or below v, used for black markers).
    """
    def one(rule):
        if "rgb" in rule:
            d = np.sqrt(((img - np.array(rule["rgb"], dtype=float)) ** 2).sum(axis=2))
            return d <= rule["tol"]
        if "min_saturation" in rule:
            return (img.max(axis=2) - img.min(axis=2)) >= rule["min_saturation"]
        if "max_value" in rule:
            return img.max(axis=2) <= rule["max_value"]
        raise ValueError(f"unknown mask rule {rule}")

    m = np.zeros(img.shape[:2], dtype=bool)
    for r in rules.get("include", []):
        m |= one(r)
    for r in rules.get("exclude", []):
        m &= ~one(r)
    return m


# ---------------------------------------------------------------- figure curves

def digitise_figure(spec):
    m = spec["marker"]
    png = rasterise(spec["pdf"], spec["page"], spec["dpi"])
    img = np.asarray(Image.open(png).convert("RGB")).astype(float)
    ax_x, ax_y = Axis(spec["x_axis"]), Axis(spec["y_axis"])
    radius = float(m.get("marker_radius_px", 4))
    rows = []

    if m["mode"] == "points":
        mask = colour_mask(img, m["refine"]) if m.get("refine") else None
        rr = float(m.get("refine", {}).get("radius_px", radius))
        for pt in m["points"]:
            px, py = float(pt["px"][0]), float(pt["px"][1])
            if mask is not None and m["refine"].get("kind") == "errorbar_mid":
                # marker drawn with symmetric vertical error bars: x is the
                # column of the bar, y the midpoint of the contiguous bar run
                win = int(rr)
                xs = range(int(px) - win, int(px) + win + 1)
                cnt = [mask[int(py) - 3 * win:int(py) + 3 * win + 1, c].sum() for c in xs]
                col = xs[int(np.argmax(cnt))]
                colmask = mask[:, col]
                near = [r for r in range(int(py) - win, int(py) + win + 1) if colmask[r]]
                if near:
                    yy = min(near, key=lambda r: abs(r - py))
                    top = bot = yy
                    while top > 0 and colmask[top - 1]:
                        top -= 1
                    while bot < len(colmask) - 1 and colmask[bot + 1]:
                        bot += 1
                    px, py = float(col), (top + bot) / 2.0
            elif mask is not None:
                y0, y1 = int(py - rr), int(py + rr) + 1
                x0, x1 = int(px - rr), int(px + rr) + 1
                sub = mask[y0:y1, x0:x1]
                yy, xx = np.nonzero(sub)
                if len(xx) >= int(m["refine"].get("min_pixels", 5)):
                    keep = (xx + x0 - px) ** 2 + (yy + y0 - py) ** 2 <= rr * rr
                    if keep.sum() >= int(m["refine"].get("min_pixels", 5)):
                        px, py = float((xx[keep] + x0).mean()), float((yy[keep] + y0).mean())
            x, y = float(ax_x.to_data(px)), float(ax_y.to_data(py))
            xu = ax_x.per_px(px) * radius
            yu = ax_y.per_px(py) * radius
            if "x_nominal" in pt:  # value fixed by the test design, stated in the source
                x, xu = float(pt["x_nominal"]), pt.get("x_unc_nominal", NR)
            rows.append((x, y, xu, yu))
            if DEBUG:
                DEBUG_PTS.append((png, spec["meta"]["curve_id"], px, py))

    elif m["mode"] == "cloud":
        x0, y0, x1, y1 = m["crop"]
        mask = colour_mask(img, m["mask"])
        sel = np.zeros_like(mask)
        sel[y0:y1, x0:x1] = mask[y0:y1, x0:x1]
        for bx0, by0, bx1, by1 in m.get("exclude_boxes", []):
            sel[by0:by1, bx0:bx1] = False
        yy, xx = np.nonzero(sel)
        if DEBUG:
            ov = (img * 0.35 + 165).astype(np.uint8)
            ov[sel] = (255, 0, 255)
            Image.fromarray(ov[y0:y1, x0:x1]).save(png.replace(".png", f"_{spec['meta']['curve_id']}_mask.png"))
        xd, yd = ax_x.to_data(xx), ax_y.to_data(yy)
        dig_x = np.array([ax_x.per_px(p) for p in xx]) * radius
        dig_y = np.array([ax_y.per_px(p) for p in yy]) * radius
        on_x = m.get("bin_axis", "x") == "x"
        key = xd if on_x else yd
        w, start = float(m["bin_width"]), float(m["bin_start"])
        idx = np.floor((key - start) / w).astype(int)
        for b in sorted(set(idx.tolist())):
            k = idx == b
            if k.sum() < int(m.get("min_pixels", 30)):
                continue
            def stat(v, dig):
                q1, med, q3 = np.percentile(v[k], [25, 50, 75])
                return float(med), float(math.sqrt(float(np.median(dig[k])) ** 2 + ((q3 - q1) / 2) ** 2))
            mx, ux = stat(xd, dig_x)
            my, uy = stat(yd, dig_y)
            # swap_output: the binned source axis becomes the output x (for
            # example slip on the source y axis, binned, against sinkage)
            rows.append((my, mx, uy, ux) if m.get("swap_output") else (mx, my, ux, uy))
    elif m["mode"] == "components":
        # one filled marker per connected component of the colour mask
        from scipy import ndimage
        x0, y0, x1, y1 = m["crop"]
        mask = colour_mask(img, m["mask"])
        sel = np.zeros_like(mask)
        sel[y0:y1, x0:x1] = mask[y0:y1, x0:x1]
        for bx0, by0, bx1, by1 in m.get("exclude_boxes", []):
            sel[by0:by1, bx0:bx1] = False
        if m.get("open_px"):
            # morphological opening removes thin fitted lines and error bars of
            # the same colour, leaving the filled markers
            k = int(m["open_px"])
            sel = ndimage.binary_opening(sel, structure=np.ones((k, k), dtype=bool))
        lab, n = ndimage.label(sel)
        lo, hi = m.get("area_px", [20, 100000])
        boxes = []
        for i in range(1, n + 1):
            yy, xx = np.nonzero(lab == i)
            if lo <= len(xx) <= hi:
                boxes.append([xx.min(), yy.min(), xx.max(), yy.max()])
        # merge_px: fragments of one marker split by an overlapping marker of
        # another colour are joined when their bounding box centres are closer
        # than this distance
        merge = float(m.get("merge_px", 0))
        changed = merge > 0
        while changed:
            changed = False
            for a in range(len(boxes)):
                for b in range(a + 1, len(boxes)):
                    ca = ((boxes[a][0] + boxes[a][2]) / 2, (boxes[a][1] + boxes[a][3]) / 2)
                    cb = ((boxes[b][0] + boxes[b][2]) / 2, (boxes[b][1] + boxes[b][3]) / 2)
                    if math.hypot(ca[0] - cb[0], ca[1] - cb[1]) <= merge:
                        boxes[a] = [min(boxes[a][0], boxes[b][0]), min(boxes[a][1], boxes[b][1]),
                                    max(boxes[a][2], boxes[b][2]), max(boxes[a][3], boxes[b][3])]
                        del boxes[b]
                        changed = True
                        break
                if changed:
                    break
        for bx in boxes:
            # bounding box centre: equals the centroid for symmetric markers and
            # avoids the downward bias of the centroid of a triangle marker
            px, py = (bx[0] + bx[2]) / 2.0, (bx[1] + bx[3]) / 2.0
            x, y = float(ax_x.to_data(px)), float(ax_y.to_data(py))
            xu, yu = ax_x.per_px(px) * radius, ax_y.per_px(py) * radius
            rows.append((y, x, yu, xu) if m.get("swap_output") else (x, y, xu, yu))
            if DEBUG:
                DEBUG_PTS.append((png, spec["meta"]["curve_id"], px, py))
    else:
        raise ValueError(f"unknown marker mode {m['mode']}")

    # automatic marker finding (colour mask, components) is digitised_auto; seed
    # pixels read by eye (points mode) are digitised_manual even when refined
    method = spec.get("method", "digitised_manual" if m["mode"] == "points" else "digitised_auto")
    out = [dict(x=r[0], y=r[1], x_unc=r[2], y_unc=r[3], method=method) for r in rows]
    # values printed in the text or a table for the same curve and conditions
    for p in spec.get("extra_points", []):
        out.append(dict(x=p["x"], y=p["y"], x_unc=p.get("x_unc", NR), y_unc=p.get("y_unc", NR),
                        method=p["method"]))
    return out


# ---------------------------------------------------------------- tabulated curves

def tabulated(spec):
    out = []
    if "fit" in spec:
        f = spec["fit"]
        if f["type"] != "polynomial":
            raise ValueError(f["type"])
        for x in f["x"]:
            y = sum(c * x ** i for i, c in enumerate(f["coefficients"]))
            out.append(dict(x=x, y=y, x_unc=NR, y_unc=f.get("y_unc", NR), method="published_fit"))
    for p in spec.get("points", []):
        out.append(dict(x=p["x"], y=p["y"], x_unc=p.get("x_unc", NR), y_unc=p.get("y_unc", NR),
                        method=spec["method"]))
    return out


# ---------------------------------------------------------------- main

def build():
    rows = []
    specs = sorted(glob.glob(os.path.join(DIGITISE_DIR, "*.json"))) + \
        sorted(glob.glob(os.path.join(TABULATED_DIR, "*.json")))
    for path in specs:
        with open(path, encoding="utf-8") as fh:
            spec = json.load(fh)
        cid = os.path.splitext(os.path.basename(path))[0]
        if spec["meta"]["curve_id"] != cid:
            raise ValueError(f"{path}: curve_id does not match file name")
        pts = digitise_figure(spec) if path.startswith(DIGITISE_DIR) else tabulated(spec)
        pts.sort(key=lambda p: float(p["x"]))
        for chk in spec.get("text_checks", []):
            near = min(pts, key=lambda p: abs(float(p["x"]) - chk["x"]))
            print(f"  check {cid}: printed y={chk['y']} at x={chk['x']} ({chk['where']}); "
                  f"digitised y={float(near['y']):.4f} at x={float(near['x']):.3f}")
        for p in pts:
            row = {k: spec["meta"].get(k, NR) for k in META_KEYS}
            row.update(x=fmt(p["x"]), y=fmt(p["y"]), x_unc=fmt(p["x_unc"]),
                       y_unc=fmt(p["y_unc"]), method=p["method"])
            rows.append({k: str(row[k]) for k in COLUMNS})
    return rows


def write(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="rebuild into a temporary file and compare with curves.csv")
    ap.add_argument("--debug", action="store_true",
                    help="write overlay images of masks and refined points into the figures folder")
    a = ap.parse_args()
    global DEBUG
    DEBUG = a.debug
    rows = build()
    if DEBUG:
        from PIL import ImageDraw
        by_png = {}
        for png, cid, px, py in DEBUG_PTS:
            by_png.setdefault(png, []).append((cid, px, py))
        for png, pts in by_png.items():
            im = Image.open(png).convert("RGB")
            dr = ImageDraw.Draw(im)
            for cid, px, py in pts:
                dr.ellipse([px - 3, py - 3, px + 3, py + 3], outline=(0, 200, 0), width=2)
            im.save(png.replace(".png", "_points.png"))
    if a.check:
        with tempfile.TemporaryDirectory() as td:
            tmp = os.path.join(td, "curves.csv")
            write(rows, tmp)
            same = open(tmp, encoding="utf-8").read() == open(OUT_CSV, encoding="utf-8").read()
        print("curves.csv reproduced exactly" if same else "curves.csv DIFFERS from rebuild")
        sys.exit(0 if same else 1)
    write(rows, OUT_CSV)
    ids = sorted({r["curve_id"] for r in rows})
    print(f"wrote {len(rows)} points in {len(ids)} curves to {os.path.relpath(OUT_CSV, REPO)}")


if __name__ == "__main__":
    main()
