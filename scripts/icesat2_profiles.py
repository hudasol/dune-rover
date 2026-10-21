#!/usr/bin/env python3
"""Stage 19 (docs/PREDICTIONS.md): ICESat-2 along track slope profiles as terrain truth.

    python3 scripts/icesat2_profiles.py fetch [--targets WhiteSands,Kelso,A,B,C] [--lengths 10,20]
    PYTHONPATH=src python3 scripts/icesat2_profiles.py analyse

fetch: asks the public SlideRule Earth service (no login) for ATL06 style segments computed on demand from ICESat-2
ATL03 photons (surface type land, high confidence photons, segment length 10 m with a 5 m step, or 20 m with a
10 m step), one request per target and calendar year, cached as GeoParquet under data/raw/icesat2/ (git ignored).
Every cached file and its SHA-256 is listed in results/icesat2/fetch_manifest.csv.

analyse: (1) validation against USGS one metre lidar at White Sands and Kelso on passes near the lidar date, with
the method bar fixed in stage 19; (2) the Arabian areas A, B and C: face crossings, the apparent slope correction
from the stage 13 face dip direction, the 30 m three class map class of every segment (original and posterior range
sets, rebuilt exactly as in phase 2) and the Copernicus slope along the same track.

PUBLISHED data (ICESat-2, USGS 3DEP, Copernicus GLO 30) scored by code of this repository: SIMULATED BY ME.
"""
from __future__ import annotations
import argparse, csv, glob, hashlib, json, math, os, sys, time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "icesat2")
LIDAR = os.path.join(ROOT, "data", "raw", "lidar")
OUT = os.path.join(ROOT, "results", "icesat2")

VALIDATION = {   # stage 19: lidar tile, UTM zone EPSG, stage 12 window, ICESat-2 pass dates (lidar date plus or minus about a year)
    "WhiteSands": dict(tile="USGS_1M_13_x37y364_NM_WhiteSandsNM_2020_D20.tif", epsg=32613, window=(378400, 379900, 3630400, 3634600),
                       t0="2019-01-18T00:00:00Z", t1="2021-01-19T23:59:59Z", lidar_dates="2020-01-18 to 2020-01-19"),
    "Kelso": dict(tile="USGS_1M_11_x61y387_CA_FEMAR9Southeast_D24.tif", epsg=32611, window=(615000, 618600, 3862400, 3865100),
                  t0="2023-04-06T00:00:00Z", t1="2026-09-06T23:59:59Z", lidar_dates="2024-04-06 to 2025-09-06"),
}
ARABIA_DATES = ("2018-10-14T00:00:00Z", "2026-10-21T23:59:59Z")
FACE_DIP_AZ = {"A": 157.0, "B": 167.8, "C": 151.0}   # stage 13, results/wind_azimuth/face_vs_wind.csv
LENGTHS = {10: 5.0, 20: 10.0}                         # segment length: step
FACE_DEG, FALLBACK_DEG, RUN_DEG = 28.0, 20.0, 20.0
MIN_VALID_WINDOW, MIN_FACES = 200, 30
CLASS_NAMES = {0: "TRAVERSABLE", 1: "BLOCKED", 2: "UNKNOWN", 3: "UNKNOWN", 4: "UNKNOWN"}
PINK = {"bg": "#fffafb", "sakura": "#e8a5bb", "rose": "#c9769a", "deep": "#a8325e", "plum": "#5b3a78", "wine": "#7a1f45", "pearl": "#f4e9ec", "ink": "#2b2024"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------ fetch

def _sliderule():
    """SlideRule client session that uses this machine's proxy settings (trust_env); no login is needed."""
    import sliderule.session as SS
    orig = SS.Session.__init__
    def init(self, *a, **k):
        k.setdefault("trust_env", True); k.setdefault("rqst_timeout", (20, 600)); orig(self, *a, **k)
    SS.Session.__init__ = init
    import sliderule
    from sliderule import icesat2
    if not sliderule.init("slideruleearth.io", verbose=False):
        raise SystemExit("SlideRule Earth is not reachable from this machine; see docs/ICESAT2_GUIDE.md for the manual route")
    return icesat2


def target_polygon(name):
    """Lon and lat polygon of a target: the whole lidar tile for the validation sites, the phase 2 window for an area."""
    if name in VALIDATION:
        from pyproj import Transformer
        import tifffile
        v = VALIDATION[name]
        p = tifffile.TiffFile(os.path.join(LIDAR, v["tile"])).pages[0]
        tie, sc = p.tags["ModelTiepointTag"].value, p.tags["ModelPixelScaleTag"].value
        e0, n1 = float(tie[3]), float(tie[4]); e1, n0 = e0 + p.shape[1] * float(sc[0]), n1 - p.shape[0] * float(sc[1])
        t = Transformer.from_crs(v["epsg"], 4326, always_xy=True)
        corners = [(e0, n0), (e1, n0), (e1, n1), (e0, n1), (e0, n0)]
        return [dict(lon=a, lat=b) for a, b in (t.transform(x, y) for x, y in corners)], v["t0"], v["t1"]
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from dunerover.study_subgrid import AREAS
    key = [k for k in AREAS if k.startswith(name + "_")][0]
    _, la0, la1, lo0, lo1 = AREAS[key][:5]
    poly = [dict(lon=lo0, lat=la0), dict(lon=lo1, lat=la0), dict(lon=lo1, lat=la1), dict(lon=lo0, lat=la1), dict(lon=lo0, lat=la0)]
    return poly, *ARABIA_DATES


def fetch(targets, lengths):
    icesat2 = _sliderule()
    os.makedirs(RAW, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    for name in targets:
        poly, t0, t1 = target_polygon(name)
        for L in lengths:
            for y in range(int(t0[:4]), int(t1[:4]) + 1):
                a = max(t0, f"{y}-01-01T00:00:00Z"); b = min(t1, f"{y}-12-31T23:59:59Z")
                f = os.path.join(RAW, f"{name}_L{L}_{y}.parquet")
                if os.path.exists(f) or a > b:
                    continue
                parms = {"poly": poly, "srt": 0, "cnf": 4, "ats": 5.0, "cnt": 10, "len": float(L), "res": LENGTHS[L], "t0": a, "t1": b}
                for attempt in range(2):
                    try:
                        st = time.time(); gdf = icesat2.atl06p(parms); break
                    except Exception as e:   # one retry, then the gap is logged
                        print(f"{name} L{L} {y}: request failed ({e})", flush=True); gdf = None
                if gdf is None:
                    continue
                gdf.to_parquet(f + ".part"); os.replace(f + ".part", f)
                print(f"{name} L{L} {y}: {len(gdf)} segments in {time.time() - st:.0f} s", flush=True)
    write_manifest()


def write_manifest():
    rows = []
    for f in sorted(glob.glob(os.path.join(RAW, "*.parquet"))):
        import pyarrow.parquet as pq
        rows.append({"file": os.path.relpath(f, ROOT), "segments": pq.ParquetFile(f).metadata.num_rows, "sha256": sha256(f)})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "fetch_manifest.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "segments", "sha256"]); w.writeheader(); w.writerows(rows)


# ------------------------------------------------------------------ segments

def load_segments(name, L):
    """All cached segments of a target as a pandas frame with lon, lat, time, slope and the track azimuth."""
    import geopandas as gpd, pandas as pd
    fs = sorted(glob.glob(os.path.join(RAW, f"{name}_L{L}_*.parquet")))
    if not fs:
        return None
    parts = []
    for f in fs:
        g = gpd.read_parquet(f)
        if len(g) == 0:
            continue
        d = pd.DataFrame({"lon": g.geometry.x.values, "lat": g.geometry.y.values, "time": g.index.values, "rgt": g["rgt"].values,
                          "cycle": g["cycle"].values, "gt": g["gt"].values, "x_atc": g["x_atc"].values, "h": g["h_mean"].values,
                          "dhdx": g["dh_fit_dx"].values, "n_ph": g["n_fit_photons"].values})
        parts.append(d)
    d = pd.concat(parts, ignore_index=True)
    d = d[np.isfinite(d["dhdx"]) & np.isfinite(d["h"])].copy()
    d["slope_deg"] = np.degrees(np.arctan(d["dhdx"]))
    d.sort_values(["rgt", "cycle", "gt", "x_atc"], inplace=True)
    # local metric coordinates for the azimuth (equirectangular about the target centre)
    lat0 = float(d["lat"].mean())
    e = (d["lon"].values - d["lon"].mean()) * 111320.0 * math.cos(math.radians(lat0))
    n = (d["lat"].values - lat0) * 110540.0
    az = np.full(len(d), np.nan)
    key = (d["rgt"].astype(np.int64) * 1000 + d["cycle"].astype(np.int64)) * 100 + d["gt"].astype(np.int64)
    d["track"] = key.values
    idx = np.arange(len(d))
    for _, ii in d.groupby("track").indices.items():
        ii = idx[ii]
        if len(ii) < 2:
            continue
        de, dn = np.gradient(e[ii]), np.gradient(n[ii])
        az[ii] = np.degrees(np.arctan2(de, dn)) % 360.0   # direction of increasing x_atc
    d["az"] = az
    return d[np.isfinite(d["az"])].reset_index(drop=True)


def line_fit_slope(zs, s):
    """Slope angle (deg) of the least squares line z(s); NaN if any sample is missing."""
    ok = np.isfinite(zs).all(axis=1)
    sc = s - s.mean()
    b = ((zs - zs.mean(axis=1, keepdims=True)) * sc).sum(axis=1) / (sc ** 2).sum()
    out = np.degrees(np.arctan(b)); out[~ok] = np.nan
    return out


def bilinear(z, r, c):
    r0, c0 = np.floor(r).astype(int), np.floor(c).astype(int)
    ok = (r0 >= 0) & (c0 >= 0) & (r0 < z.shape[0] - 1) & (c0 < z.shape[1] - 1)
    out = np.full(r.shape, np.nan)
    r0c, c0c = np.clip(r0, 0, z.shape[0] - 2), np.clip(c0, 0, z.shape[1] - 2)
    fr, fc = r - r0c, c - c0c
    v = (z[r0c, c0c] * (1 - fr) * (1 - fc) + z[r0c + 1, c0c] * fr * (1 - fc) + z[r0c, c0c + 1] * (1 - fr) * fc + z[r0c + 1, c0c + 1] * fr * fc)
    out[ok] = v[ok]
    return out


# ------------------------------------------------------------------ validation

def validation(L):
    import tifffile
    from pyproj import Transformer
    rows, samples = [], {}
    for site, v in VALIDATION.items():
        d = load_segments(site, L)
        if d is None:
            rows.append({"site": site, "length_m": L, "status": "no data fetched"}); continue
        t = np.array(d["time"], dtype="datetime64[ns]")
        d = d[(t >= np.datetime64(v["t0"][:19])) & (t <= np.datetime64(v["t1"][:19]))].reset_index(drop=True)
        p = tifffile.TiffFile(os.path.join(LIDAR, v["tile"])).pages[0]
        tie, sc = p.tags["ModelTiepointTag"].value, p.tags["ModelPixelScaleTag"].value
        e0, n0, px = float(tie[3]), float(tie[4]), float(sc[0])
        z = p.asarray().astype(np.float32); z[z < -1000] = np.nan
        tr = Transformer.from_crs(4326, v["epsg"], always_xy=True)
        d = d.reset_index(drop=True)
        E, N = tr.transform(d["lon"].values, d["lat"].values)
        s = np.arange(-L / 2, L / 2 + 0.01, 1.0)
        a = np.radians(d["az"].values)[:, None]
        Es, Ns = E[:, None] + s[None, :] * np.sin(a), N[:, None] + s[None, :] * np.cos(a)
        zs = bilinear(z, (n0 - Ns) / px - 0.5, (Es - e0) / px - 0.5)   # pixel centres (PixelIsArea tiepoint at the corner)
        lid = line_fit_slope(zs, s)
        win = v["window"]
        inwin = (E >= win[0]) & (E <= win[1]) & (N >= win[2]) & (N <= win[3])
        ok = np.isfinite(lid)
        use = ok & inwin
        scope = "stage 12 window"
        if use.sum() < MIN_VALID_WINDOW:
            use, scope = ok, "whole tile (fewer than 200 valid segments in the window, rule of stage 19)"
        x, y = d["slope_deg"].values[use], lid[use]
        # POST HOC sensitivities (clarification of stage 19, after the midpoint review): footprint averaged lidar,
        # an along track offset per pass, and the reverse conditioning on steep ICESat-2 segments
        def lidar_line(off_along=0.0, off_cross=0.0):
            Es2 = E[:, None] + (s[None, :] + off_along) * np.sin(a) + off_cross * np.cos(a)
            Ns2 = N[:, None] + (s[None, :] + off_along) * np.cos(a) - off_cross * np.sin(a)
            return line_fit_slope(bilinear(z, (n0 - Ns2) / px - 0.5, (Es2 - e0) / px - 0.5), s)
        foot = np.nanmean(np.stack([lidar_line(0.0, c) for c in np.arange(-5.0, 5.01, 1.0)]), axis=0)[use]
        offs = np.arange(-10.0, 10.01, 1.0)
        shifted = np.stack([lidar_line(o, 0.0)[use] for o in offs])
        tracks = d["track"].values[use]; best = np.full(len(x), np.nan)
        for tk in np.unique(tracks):
            m = tracks == tk
            if m.sum() < 10:
                continue
            sc = [np.nanmean(np.abs(x[m] - shifted[j][m])) for j in range(len(offs))]
            best[m] = shifted[int(np.nanargmin(sc))][m]
        steep_is2 = np.abs(x) >= 28.0
        near_max = np.nanmax(np.abs(shifted), axis=0)
        ok_f, ok_b = np.isfinite(foot), np.isfinite(best)
        posthoc = {"posthoc_r_footprint": round(float(np.corrcoef(x[ok_f], foot[ok_f])[0, 1]), 4) if ok_f.sum() > 2 else "",
                   "posthoc_mad_footprint_deg": round(float(np.median(np.abs(x[ok_f] - foot[ok_f]))), 3) if ok_f.sum() else "",
                   "posthoc_r_best_offset": round(float(np.corrcoef(x[ok_b], best[ok_b])[0, 1]), 4) if ok_b.sum() > 2 else "",
                   "posthoc_mad_best_offset_deg": round(float(np.median(np.abs(x[ok_b] - best[ok_b]))), 3) if ok_b.sum() else "",
                   "posthoc_is2_segments_28deg": int(steep_is2.sum()),
                   "posthoc_median_steepest_lidar_within_10m_of_is2_28deg": round(float(np.nanmedian(near_max[steep_is2])), 2) if steep_is2.sum() else ""}
        r = float(np.corrcoef(x, y)[0, 1]) if use.sum() > 2 else float("nan")
        mad = float(np.median(np.abs(x - y)))
        steep = np.abs(y) >= 20.0
        ratio = float(np.median(np.abs(x[steep]) / np.abs(y[steep]))) if steep.sum() else float("nan")
        passed = (r >= 0.80) and (mad <= 2.0) and (ratio >= 0.75 if np.isfinite(ratio) else True)   # an unscored part (iii) is not a failure (clarification)
        rows.append({"site": site, "length_m": L, "status": "ok", "scope": scope, "passes_in_dates": int(d[use]["track"].nunique()),
                     "valid_segments": int(use.sum()), "pearson_r": round(r, 4), "median_abs_diff_deg": round(mad, 3),
                     "steep_segments_lidar_20deg": int(steep.sum()), "median_ratio_steep": round(ratio, 4),
                     "p95_abs_icesat2_deg": round(float(np.percentile(np.abs(x), 95)), 2), "p95_abs_lidar_deg": round(float(np.percentile(np.abs(y), 95)), 2),
                     "max_abs_lidar_deg": round(float(np.max(np.abs(y))), 2), "max_abs_icesat2_deg": round(float(np.max(np.abs(x))), 2),
                     "bar_r_ge_0.80": r >= 0.80, "bar_mad_le_2.0": mad <= 2.0, "bar_ratio_ge_0.75": ratio >= 0.75, "method_passes": passed,
                     "lidar_dates": v["lidar_dates"], "icesat2_dates": f"{v['t0'][:10]} to {v['t1'][:10]}", **posthoc})
        samples[site] = (x, y)
        del z
    return rows, samples


# ------------------------------------------------------------------ Arabia

def class_maps():
    """30 m three class maps of areas A, B, C, rebuilt exactly as phase 2 (block 1), for two range sets."""
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from dunerover.dem import load_tile, crop
    from dunerover.slipmodel import use_range_set
    from dunerover.study_subgrid import AREAS, TILES, N_DRAWS
    from dunerover import traverse as TR, subgrid as SG, threeclass as TC
    out = {}
    for key, (tk, la0, la1, lo0, lo1, sep, seed, desc) in AREAS.items():
        dem = crop(load_tile(os.path.join(ROOT, "data", "raw", TILES[tk])), la0, la1, lo0, lo1)
        eg = TR.precompute_edges(dem)
        dm = round(0.5 * (dem.dx + dem.dy), 1)
        F = SG.features_2d(np.nan_to_num(dem.z, nan=np.nanmean(dem.z)), dem.dx, dem.dy)
        p0 = SG.fit(dm, "base", 1.0).predict(F)
        maps = {}
        for rs in ("original", "posterior_2026_10_20"):
            with use_range_set(rs):
                q = TC.q_pass(eg, TC.lhs_draws(N_DRAWS, seed))
            maps[rs] = TC.classify(q, p0).reshape(dem.shape)
        out[key[0]] = (dem, maps, p0.reshape(dem.shape))
    return out


def arabia(L, maps):
    rows, runs_all, seg_all = [], {}, {}
    for a in ("A", "B", "C"):
        d = load_segments(a, L)
        if d is None:
            rows.append({"area": a, "length_m": L, "status": "no data fetched"}); continue
        dem, cm, pf = maps[a]
        # Copernicus slope along the same track, 30 m line, 1 m steps
        s = np.arange(-15.0, 15.01, 1.0)
        zs = np.empty((len(d), len(s)), dtype=np.float64)
        for c0 in range(0, len(d), 100000):   # in chunks, to bound memory; same values as one pass
            sl_ = slice(c0, c0 + 100000)
            az = np.radians(d["az"].values[sl_])[:, None]
            dlat = (s[None, :] * np.cos(az)) / (dem.dy / dem.dlat)
            dlon = (s[None, :] * np.sin(az)) / (dem.dx / dem.dlon)
            lat, lon = d["lat"].values[sl_][:, None] + dlat, d["lon"].values[sl_][:, None] + dlon
            zs[sl_] = bilinear(dem.z, (dem.lat_top - lat) / dem.dlat, (lon - dem.lon_left) / dem.dlon)
        d["cop_slope_deg"] = line_fit_slope(zs, s)
        rr = np.rint((dem.lat_top - d["lat"].values) / dem.dlat).astype(int); cc = np.rint((d["lon"].values - dem.lon_left) / dem.dlon).astype(int)
        inside = (rr >= 0) & (cc >= 0) & (rr < dem.shape[0]) & (cc < dem.shape[1])
        d = d[inside & np.isfinite(d["cop_slope_deg"]).values].reset_index(drop=True); rr, cc = rr[inside], cc[inside]
        rr, cc = rr[np.isfinite(zs[inside]).all(axis=1)], cc[np.isfinite(zs[inside]).all(axis=1)]
        for rs, m in cm.items():
            d[f"class_{rs}"] = m[rr, cc]
        d["face_prob"] = pf[rr, cc]
        app = np.abs(d["slope_deg"].values)
        # downhill direction of the track at the segment and the apparent slope correction
        down = np.where(d["dhdx"].values > 0, (d["az"].values + 180.0) % 360.0, d["az"].values)
        corr = {}
        for shift in (0.0, -30.0, 30.0):
            dd = np.abs((down - (FACE_DIP_AZ[a] + shift) + 180.0) % 360.0 - 180.0)
            c = np.where(dd <= 60.0, np.degrees(np.arctan(np.tan(np.radians(app)) / np.cos(np.radians(dd)))), np.nan)
            corr[shift] = c
        d["corr_slope_deg"] = corr[0.0]
        dd0 = np.abs((down - FACE_DIP_AZ[a] + 180.0) % 360.0 - 180.0)
        thr = FACE_DEG if (app >= FACE_DEG).sum() >= MIN_FACES else FALLBACK_DEG
        face = app >= thr
        # runs of consecutive segments of one beam with raw slope of 20 deg or more
        step = LENGTHS[L]
        runs = []
        tr_, xa = d["track"].values, d["x_atc"].values
        steep = app >= RUN_DEG
        i = 0
        while i < len(d):
            if not steep[i]:
                i += 1; continue
            j = i
            while j + 1 < len(d) and steep[j + 1] and tr_[j + 1] == tr_[i] and xa[j + 1] - xa[j] <= step * 1.1:
                j += 1
            seg = slice(i, j + 1)
            runs.append({"raw_max": float(app[seg].max()), **{f"corr_max_{int(k)}": float(np.nanmax(v[seg])) if np.isfinite(v[seg]).any() else np.nan for k, v in corr.items()}})
            i = j + 1
        runs_all[a] = runs
        dd_runs = dd0[(app >= RUN_DEG) & (dd0 <= 60.0)]
        fs = d[face]
        os.makedirs(OUT, exist_ok=True)
        fs.assign(area=a, abs_slope_deg=app[face].round(2), class_original=fs["class_original"], class_posterior=fs["class_posterior_2026_10_20"])[
            ["area", "lat", "lon", "track", "x_atc", "abs_slope_deg", "corr_slope_deg", "cop_slope_deg", "class_original", "class_posterior", "face_prob"]].round(
            {"lat": 6, "lon": 6, "x_atc": 1, "corr_slope_deg": 2, "cop_slope_deg": 2, "face_prob": 4}).astype({"x_atc": "float64"}).to_csv(os.path.join(OUT, f"face_segments_{a}_L{L}.csv"), index=False)
        seg_all[a] = d
        def cls_share(rs, k, mask):
            return round(float(np.isin(d[f"class_{rs}"].values[mask], k).mean()), 4) if mask.sum() else float("nan")
        cop = np.abs(d["cop_slope_deg"].values)
        cm0 = [r["corr_max_0"] for r in runs if np.isfinite(r["corr_max_0"])]
        row = {"area": a, "length_m": L, "status": "ok", "passes": int(d["track"].nunique()), "valid_segments": len(d),
               "face_threshold_deg": thr, "face_segments": int(face.sum()), "face_segments_28deg": int((app >= 28).sum()),
               "segments_ge_20deg": int((app >= 20).sum()), "max_abs_slope_deg": round(float(app.max()), 2),
               "faces_in_traversable_original": cls_share("original", [0], face), "faces_in_unknown_original": cls_share("original", [2, 3, 4], face),
               "faces_in_blocked_original": cls_share("original", [1], face),
               "faces_in_traversable_posterior": cls_share("posterior_2026_10_20", [0], face), "faces_in_unknown_posterior": cls_share("posterior_2026_10_20", [2, 3, 4], face),
               "all_in_traversable_original": cls_share("original", [0], np.ones(len(d), bool)),
               "median_face_prob_on_faces": round(float(np.median(d["face_prob"].values[face])), 4) if face.sum() else float("nan"),
               "median_face_prob_all": round(float(np.median(d["face_prob"].values)), 4),
               "median_is2_minus_cop_on_faces_deg": round(float(np.median(app[face] - cop[face])), 2) if face.sum() else float("nan"),
               "p95_abs_is2_deg": round(float(np.percentile(app, 95)), 2), "p95_abs_cop_deg": round(float(np.percentile(cop, 95)), 2),
               "runs_ge_20deg": len(runs), "runs_corrected": len(cm0),
               "median_run_raw_max_deg": round(float(np.median([r["raw_max"] for r in runs])), 2) if runs else float("nan"),
               "median_run_corr_max_deg": round(float(np.median(cm0)), 2) if cm0 else float("nan"),
               "median_run_corr_max_dip_minus30_deg": round(float(np.nanmedian([r["corr_max_-30"] for r in runs])), 2) if runs else float("nan"),
               "median_run_corr_max_dip_plus30_deg": round(float(np.nanmedian([r["corr_max_30"] for r in runs])), 2) if runs else float("nan"),
               "face_dip_azimuth_stage13_deg": FACE_DIP_AZ[a],
               # POST HOC (after the first Arabian run showed segments steeper than sand can stand): quality of the face set
               "posthoc_face_share_above_40deg": round(float((app[face] > 40.0).mean()), 4) if face.sum() else "",
               "posthoc_faces_28_40_in_traversable_original": cls_share("original", [0], face & (app <= 40.0)),
               "posthoc_faces_28_40_n": int((face & (app <= 40.0)).sum()),
               "posthoc_runs_corrected_with_d_over_45deg": round(float(np.mean(dd_runs > 45.0)), 4) if len(dd_runs) else ""}
        rows.append(row)
    return rows, runs_all, seg_all


# ------------------------------------------------------------------ figures

def figures(val_samples, seg_all, runs_all):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fd = os.path.join(OUT, "figures"); os.makedirs(fd, exist_ok=True)
    plt.rcParams.update({"figure.facecolor": PINK["bg"], "axes.facecolor": PINK["pearl"], "axes.edgecolor": PINK["ink"], "font.size": 9})
    if val_samples:
        fig, axs = plt.subplots(1, len(val_samples), figsize=(4.2 * len(val_samples), 4.0))
        axs = np.atleast_1d(axs)
        for ax, (site, (x, y)) in zip(axs, val_samples.items()):
            ax.scatter(y, x, s=2, color=PINK["rose"], alpha=0.35, linewidths=0)
            lim = max(5, float(np.nanpercentile(np.abs(np.r_[x, y]), 99.9)))
            ax.plot([-lim, lim], [-lim, lim], color=PINK["plum"], lw=1)
            ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
            ax.set_xlabel("lidar along track slope, deg"); ax.set_ylabel("ICESat-2 along track slope, deg"); ax.set_title(site)
        fig.suptitle("ICESat-2 (10 m segments) against one metre lidar on the same line. SIMULATED BY ME on PUBLISHED data.", fontsize=8)
        fig.tight_layout(); fig.savefig(os.path.join(fd, "fig_validation_scatter.png"), dpi=150); plt.close(fig)
    if seg_all:
        fig, ax = plt.subplots(figsize=(6.5, 3.8))
        bins = np.arange(0, 41, 1.0)
        cols = {"A": PINK["deep"], "B": PINK["plum"], "C": PINK["sakura"]}
        for a, d in seg_all.items():
            ax.hist(np.abs(d["slope_deg"].values), bins=bins, histtype="step", lw=1.6, color=cols[a], density=True, label=f"{a}, ICESat-2 10 m")
            ax.hist(np.abs(d["cop_slope_deg"].values), bins=bins, histtype="step", lw=1.0, ls="--", color=cols[a], density=True, label=f"{a}, Copernicus 30 m")
        ax.set_yscale("log"); ax.axvline(28, color=PINK["ink"], lw=0.8, ls=":")
        ax.set_xlabel("absolute along track slope, deg"); ax.set_ylabel("density (log)"); ax.legend(fontsize=7, ncol=2)
        ax.set_title("Arabian areas: slope along ICESat-2 tracks at 10 m against Copernicus 30 m", fontsize=9)
        fig.tight_layout(); fig.savefig(os.path.join(fd, "fig_arabia_slope_distributions.png"), dpi=150); plt.close(fig)
        # one example profile: the pass of area A with the most face segments
        d = seg_all.get("A")
        if d is not None and len(d):
            f = d[np.abs(d["slope_deg"]) >= 20]
            if len(f):
                tk = f["track"].value_counts().index[0]
                p = d[d["track"] == tk]
                k = int(np.argmax(np.abs(p["slope_deg"].values)))
                x0 = p["x_atc"].values[k]
                q = p[np.abs(p["x_atc"] - x0) <= 1500]
                fig, ax = plt.subplots(figsize=(7, 3.2))
                ax.plot((q["x_atc"] - x0) / 1000.0, q["h"], color=PINK["deep"], lw=1)
                st = np.abs(q["slope_deg"]) >= 28
                ax.scatter((q["x_atc"][st] - x0) / 1000.0, q["h"][st], s=8, color=PINK["plum"], zorder=3, label="segments at 28 deg or steeper")
                ax.set_xlabel("distance along track, km"); ax.set_ylabel("height, m"); ax.legend(fontsize=7)
                ax.set_title(f"Area A (Liwa): one ICESat-2 profile, track key {tk}", fontsize=9)
                fig.tight_layout(); fig.savefig(os.path.join(fd, "fig_arabia_example_profile.png"), dpi=150); plt.close(fig)


def write_csv(path, rows):
    if not rows:
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)


def runlog(msg):
    """Timestamped run log (added after the final review of 2026-10-21; earlier runs are not in it)."""
    with open(os.path.join(OUT, "run_log.txt"), "a") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S %z')} {msg}\n")


def analyse(lengths=(10, 20)):
    os.makedirs(OUT, exist_ok=True)
    runlog(f"analyse started; lengths {list(lengths)}")
    val_rows, samples10 = [], {}
    for L in lengths:
        r, smp = validation(L)
        val_rows += r
        if L == 10:
            samples10 = smp
    write_csv(os.path.join(OUT, "validation_metrics.csv"), val_rows)
    ok10 = [r for r in val_rows if r["length_m"] == 10 and r.get("status") == "ok" and r["valid_segments"] >= MIN_VALID_WINDOW]
    method_ok = bool(ok10) and all(r["method_passes"] for r in ok10)
    maps = class_maps()
    ar_rows, runs10, seg10 = [], {}, {}
    for L in lengths:
        r, runs, segs = arabia(L, maps)
        ar_rows += r
        if L == 10:
            runs10, seg10 = runs, segs
    for r in ar_rows:
        r["method_validated"] = method_ok
    write_csv(os.path.join(OUT, "arabia_metrics.csv"), ar_rows)
    run_rows = [{"area": a, **x} for a, rr in runs10.items() for x in rr]
    import pandas as pd
    pd.DataFrame(run_rows).round(3).to_csv(os.path.join(OUT, "arabia_face_runs_10m.csv"), index=False)
    figures(samples10, seg10, runs10)
    write_manifest()
    json.dump({"label": "PUBLISHED data scored by code of this repository: SIMULATED BY ME", "stage": 19, "method_validated": method_ok,
               "service": "SlideRule Earth public cluster (slideruleearth.io), atl06p", "parameters": {"srt": 0, "cnf": 4, "ats": 5.0, "cnt": 10, "lengths_steps_m": LENGTHS},
               "face_deg": FACE_DEG, "fallback_deg": FALLBACK_DEG, "face_dip_azimuth_stage13": FACE_DIP_AZ, "validation": VALIDATION, "arabia_dates": ARABIA_DATES},
              open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=str)
    runlog(f"analyse finished; method validated {method_ok}; validation rows {len(val_rows)}; Arabian rows {len(ar_rows)}")
    print("method validated:", method_ok)
    for r in val_rows + ar_rows:
        print(r)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fetch", "analyse", "manifest"])
    ap.add_argument("--targets", default="WhiteSands,Kelso,A,B,C")
    ap.add_argument("--lengths", default="10,20")
    a = ap.parse_args()
    if a.cmd == "fetch":
        fetch(a.targets.split(","), [int(x) for x in a.lengths.split(",")])
    elif a.cmd == "manifest":
        write_manifest()
    else:
        analyse(tuple(int(x) for x in a.lengths.split(",")))
