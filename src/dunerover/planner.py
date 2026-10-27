"""Dune Rover Planner: the research of this repository packaged as a planning tool.  SIMULATION ONLY.

Give it an elevation model (a Copernicus GLO-30 tile, a USGS lidar tile or a drone survey exported as GeoTIFF) and a
vehicle profile, and it returns, per grid cell, the slope, the probability of an unresolved slip face, the three class
map (TRAVERSABLE, BLOCKED, UNKNOWN) and, between two points, a route with its risks.  Every output carries a
resolution gate built from the lidar tests of this repository: a map coarser than 10 m is never reported as verified
traversable, because on six North American dune fields a 30 m map called 36 to 80 % of the cells with a steep face
TRAVERSABLE (docs/REPORT.md, sections 13 and 14).

Three ways to describe the vehicle (VehicleProfile):
  * "assumed": the assumption ranges of the simulation study (slipmodel.PARAM_TABLE, original set);
  * "published-posterior": the posterior of the exponential family fitted to published curves of other vehicles
    (stage 15); this widens the uncertainty, it does not describe any real vehicle in Arabia;
  * from field runs: f_r and i0 fitted to the vehicle's own runs up to 10 degrees (the field kit), with bootstrap
    ranges; this is the only profile that describes a real vehicle, and only on the sand it was measured on.

Labels: the maps and routes are SIMULATED BY ME; the evidence card quoted in every report is generated from result
files by scripts/build_evidence_card.py.  Nothing here is a safety case for a real vehicle.
"""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field, asdict
from functools import lru_cache

import numpy as np
from scipy.sparse import diags
from scipy.sparse.csgraph import dijkstra
from scipy.stats import qmc

from .dem import Dem, metres_per_degree
from .slipmodel import SlipParams, RANGE_SETS, _ORIGINAL, critical_uphill_deg
from .terrain import slope_deg as _slope_deg
from . import traverse as TR
from . import subgrid as SG
from . import threeclass as TC

KEYS = ("phi_deg", "f_r", "i0", "i_max")
RESOLVED_MAX_M = 2.0          # a DEM at this posting or finer resolves faces directly (truth rule of stage 12)
VERIFIED_MAX_M = 10.0         # coarser than this: TRAVERSABLE is never reported as verified (resolution gate)
FACE_MIN_AREA_M2 = 10.0       # stage 12 truth: at least 10 square metres of slope at FACE_TRUTH_DEG or steeper
RISK_W = 5.0                  # risk weighted policy: cost multiplied by 1 + RISK_W x face probability (stage 17)
POLICIES = ("naive", "conservative", "risk_weighted")
DOWNHILL_WARN_DEG = 25.0      # a route descending a grade this steep gets a warning (near the angle of repose of dry sand)
DOWNHILL_CUT_DEG = 28.0       # conservative and risk weighted routes never descend a grade this steep (the face truth angle)
DUMONT_50PCT_SLIP_DEG = 12.6  # PUBLISHED: the Dumont Dunes cubic of Heverly et al. 2013 crosses 50 % slip here (README, stage 5)
NODATA_SHARE = 0.5            # an analysis cell with more than this share of void posts is NO DATA
CLASS_NAMES = {0: "TRAVERSABLE", 1: "BLOCKED", 2: "UNKNOWN (assumption sensitive)", 3: "UNKNOWN (slip face risk)", 4: "UNKNOWN (both)",
               5: "NO DATA"}
EVIDENCE_CARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "evidence_card.json")


# ---------------------------------------------------------------------------------------------------------------------
# vehicle profiles
# ---------------------------------------------------------------------------------------------------------------------
@dataclass
class VehicleProfile:
    name: str
    label: str                                   # ASSUMPTION, PUBLISHED POSTERIOR (other vehicles) or MEASURED (field runs)
    ranges: dict                                 # key -> [low, high]
    nominal: dict                                # key -> value used for routing costs
    notes: str = ""
    source: str = ""
    pairs: list | None = None      # bootstrap pairs [f_r, i0] of a field calibration, sampled jointly (they trade off)
    heldout: dict | None = None    # error of the calibrated model on the runs above 10 degrees, when there are any

    def draws(self, n: int = 128, seed: int = 20261023, reject_immobile: bool = True) -> list[SlipParams]:
        """Latin hypercube draws inside the ranges; by default draws that cannot move on level ground are dropped
        (question 8 of the study), drawing up to three times n from the same seed. A field calibrated profile draws
        f_r and i0 jointly from its bootstrap pairs."""
        u = qmc.LatinHypercube(d=4, seed=seed).random(3 * n if reject_immobile else n)
        out = [SlipParams(**{k: self.ranges[k][0] + u[j, i] * (self.ranges[k][1] - self.ranges[k][0]) for i, k in enumerate(KEYS)})
               for j in range(len(u))]
        if self.pairs:
            pr = np.asarray(self.pairs, dtype=float)
            pick = np.random.default_rng(seed).integers(0, len(pr), len(out))
            out = [p.with_(f_r=float(pr[m, 0]), i0=float(pr[m, 1])) for p, m in zip(out, pick)]
        if reject_immobile:
            out = [p for p in out if p.f_r / p.mu_max <= 1.0 - np.exp(-p.i_max / p.i0)][:n]
            if not out:
                raise ValueError("no parameter draw of this profile can move on level ground")
        return out

    def nominal_params(self) -> SlipParams:
        return SlipParams(**{k: float(self.nominal[k]) for k in KEYS})

    def critical_uphill_deg(self) -> float:
        return critical_uphill_deg(self.nominal_params())

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=1)

    @classmethod
    def load(cls, path: str) -> "VehicleProfile":
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        missing = [k for k in KEYS if k not in d.get("ranges", {}) or k not in d.get("nominal", {})]
        if missing:
            raise ValueError(f"profile {path} lacks ranges or nominal values for {missing}")
        for k in KEYS:
            lo, hi = d["ranges"][k]
            if not lo <= d["nominal"][k] <= hi:
                raise ValueError(f"profile {path}: nominal {k} lies outside its range")
        return cls(**d)


def _table_profile(name, label, table, notes, source) -> VehicleProfile:
    return VehicleProfile(name, label, {k: [float(table[k][1]), float(table[k][2])] for k in KEYS},
                          {k: float(table[k][0]) for k in KEYS}, notes, source)


def builtin_profile(name: str) -> VehicleProfile:
    if name == "assumed":
        return _table_profile("assumed", "ASSUMPTION", _ORIGINAL,
                              "Assumption ranges of the simulation study for a small wheeled robot on loose dry sand; not measured.",
                              "src/dunerover/slipmodel.py PARAM_TABLE (original set)")
    if name == "published-posterior":
        t = dict(_ORIGINAL); t.update(RANGE_SETS["posterior_2026_10_20"])
        return _table_profile("published-posterior", "PUBLISHED POSTERIOR (other vehicles)", t,
                              "5 to 95 % posterior of the exponential family fitted to published slip curves of other vehicles "
                              "(stage 15); wider and more honest than the assumed set, but not a description of any rover in Arabia.",
                              "results/model_validation/part_exp_existing_mohr_coulomb_ratio_logistic_empirical/posterior_exp.json")
    raise ValueError(f"unknown built in profile {name!r}; choose 'assumed' or 'published-posterior', or calibrate one from field runs")


BUILTIN_PROFILES = ("assumed", "published-posterior")


def profile_from_runs(d: dict, name: str = "field-calibrated", n_boot: int = 400, seed: int = 20261023,
                      i_max_range=(0.40, 0.70), i_max_nominal: float = 0.50) -> VehicleProfile:
    """Fit f_r and i0 to the vehicle's own runs at 10 degrees or less (fieldanalysis.calibrate, friction angle from the
    soil tests), with 5 to 95 % ranges from a bootstrap over runs.  d is the dict of fieldanalysis.load_runs."""
    from . import fieldanalysis as FA
    slope = np.asarray(d["slope_deg"], dtype=float)
    s = FA.observed_slip(d)
    ent = np.asarray(d["entrapped"], dtype=bool)
    cal = (slope <= FA.CALIB_MAX_DEG) & ~ent
    if cal.sum() < 5:
        raise ValueError("need at least 5 runs at 10 degrees or less without entrapment to calibrate a vehicle profile")
    phis = np.asarray(d["phi_deg"], dtype=float)
    phi = float(np.median(phis))
    f_r, i0 = FA.calibrate(slope[cal], s[cal], phi)
    rng = np.random.default_rng(seed)
    idx = np.flatnonzero(cal)
    bf, bi = [], []
    for _ in range(n_boot):
        b = rng.choice(idx, size=idx.size, replace=True)
        x = FA.calibrate(slope[b], s[b], phi)
        bf.append(x[0]); bi.append(x[1])
    q = lambda v: [float(np.percentile(v, 5)), float(np.percentile(v, 95))]  # noqa: E731
    phi_r = [float(np.min(phis)), float(np.max(phis))] if np.ptp(phis) > 0 else [phi - 1.0, phi + 1.0]
    fr_r, i0_r = q(bf), q(bi)
    fr_r = [min(fr_r[0], f_r, min(bf)), max(fr_r[1], f_r, max(bf))]; i0_r = [min(i0_r[0], i0, min(bi)), max(i0_r[1], i0, max(bi))]
    test = (slope > FA.CALIB_MAX_DEG)
    held = None
    if test.sum() >= 3:
        err = np.minimum(FA.model_slip(slope[test], f_r, i0, phi), 1.0) - s[test]
        held = {"runs": int(test.sum()), "mae": round(float(np.mean(np.abs(err))), 4), "rmse": round(float(np.sqrt(np.mean(err ** 2))), 4),
                "note": "error of the calibrated model on the vehicle's own runs above 10 degrees (not used in the fit)"}
    return VehicleProfile(name, "MEASURED f_r and i0 (runs at 10 degrees or less, one vehicle, one site); i_max ASSUMED",
                          {"phi_deg": phi_r, "f_r": fr_r, "i0": i0_r, "i_max": [float(i_max_range[0]), float(i_max_range[1])]},
                          {"phi_deg": phi, "f_r": f_r, "i0": i0, "i_max": float(i_max_nominal)},
                          f"Fitted on {int(cal.sum())} runs at 10 degrees or less; bootstrap 5 to 95 % ranges over {n_boot} resamples. "
                          "f_r and i0 are drawn jointly from the bootstrap pairs because they trade off on gentle slopes; i_max is the study's assumption range. "
                          "The calibration bounds are the assumption ranges of the study (fieldanalysis.calibrate); a fit at a bound "
                          "means the bound, not the data, decided the value. Valid for this vehicle on the sand it was measured on.",
                          "field runs", [[round(float(a_), 5), round(float(b_), 5)] for a_, b_ in zip(bf, bi)], held)


# ---------------------------------------------------------------------------------------------------------------------
# rasters
# ---------------------------------------------------------------------------------------------------------------------
@dataclass
class Raster:
    z: np.ndarray            # elevation, metres, NaN = no data; row 0 is the north (top) row
    x0: float                # map coordinate of the centre of post (0, 0): longitude or easting
    y0: float                # latitude or northing
    px: float                # post spacing in map units, columns (positive)
    py: float                # post spacing in map units, rows (positive; rows run south)
    epsg: int | None         # coordinate reference system, when the file declares one
    geographic: bool         # True when map units are degrees
    dx_m: float              # post spacing in metres, east
    dy_m: float              # post spacing in metres, north
    source: str = ""
    geokeys: tuple | None = None
    geo_double: tuple | None = None   # GeoDoubleParamsTag, kept so a written GeoTIFF has no dangling keys
    geo_ascii: str | None = None      # GeoAsciiParamsTag
    warnings: tuple = ()

    @property
    def shape(self):
        return self.z.shape

    def map_xy(self, r, c):
        return self.x0 + np.asarray(c) * self.px, self.y0 - np.asarray(r) * self.py

    def rowcol(self, x, y):
        return int(round((self.y0 - y) / self.py)), int(round((x - self.x0) / self.px))

    def to_lonlat(self, x, y):
        if self.geographic or self.epsg is None:
            return np.asarray(x), np.asarray(y)
        from pyproj import Transformer
        return Transformer.from_crs(self.epsg, 4326, always_xy=True).transform(x, y)

    def from_lonlat(self, lon, lat):
        if self.geographic:
            return lon, lat
        if self.epsg is None:
            raise ValueError("this raster declares no coordinate reference system: give start and goal as row,col")
        from pyproj import Transformer
        return Transformer.from_crs(4326, self.epsg, always_xy=True).transform(lon, lat)


def _geokeys(page):
    t = page.tags.get("GeoKeyDirectoryTag")
    if t is None:
        return {}, None
    v = list(t.value)
    keys = {}
    for i in range(1, v[3] + 1):
        k, loc, cnt, val = v[4 * i: 4 * i + 4]
        if loc == 0:
            keys[k] = val
    return keys, tuple(v)


def read_raster(path: str) -> Raster:
    """Read a single band GeoTIFF without GDAL: model pixel scale and tiepoint tags, GeoKeys for the reference system
    (geographic EPSG:4326 tiles such as Copernicus GLO-30, or projected tiles such as USGS 3DEP and drone surveys)."""
    import tifffile
    with tifffile.TiffFile(path) as tf:
        page = tf.pages[0]
        z = page.asarray().astype(np.float64)
        if z.ndim == 3:
            z = z[..., 0]
        if "ModelPixelScaleTag" not in page.tags or "ModelTiepointTag" not in page.tags:
            raise ValueError(f"{path} is not a GeoTIFF: it has no model pixel scale or tiepoint tag (export the elevation model as a GeoTIFF)")
        scale = page.tags["ModelPixelScaleTag"].value
        tie = page.tags["ModelTiepointTag"].value
        nod = page.tags.get("GDAL_NODATA")
        keys, raw = _geokeys(page)
        gd = page.tags.get("GeoDoubleParamsTag"); ga = page.tags.get("GeoAsciiParamsTag")
        geo_double = tuple(gd.value) if gd is not None else None
        geo_ascii = str(ga.value) if ga is not None else None
    if nod is not None:
        try:
            z[z == float(str(nod.value).strip("\x00 "))] = np.nan
        except ValueError:
            pass
    z[~np.isfinite(z) | (z < -1000)] = np.nan
    raster_is_area = keys.get(1025, 1) == 1          # GTRasterTypeGeoKey: 1 pixel is area, 2 pixel is point
    px, py = float(scale[0]), float(scale[1])
    x0, y0 = float(tie[3]), float(tie[4])
    if raster_is_area:
        x0 += 0.5 * px; y0 -= 0.5 * py
    warns = []
    if not keys:   # never guess degrees from small numbers: a GeoTIFF without GeoKeys is read as a local frame in metres
        geographic = False
        warns.append("The file declares no reference system (no GeoKeys): its units are taken as metres in a local frame; give start and goal as row,col.")
    else:
        geographic = keys.get(1024) == 2
        unit = keys.get(3076)
        if not geographic and unit not in (None, 9001):
            raise ValueError(f"{path}: projected linear unit code {unit} is not metres (9001); reproject the elevation model to metres")
    epsg = keys.get(2048) if geographic else keys.get(3072)
    if geographic:
        epsg = epsg or 4326
        mlon, mlat = metres_per_degree(y0 - 0.5 * z.shape[0] * py)
        dx, dy = mlon * px, mlat * py
    else:
        dx, dy = px, py
    return Raster(z, x0, y0, px, py, epsg, geographic, float(dx), float(dy), str(path), raw, geo_double, geo_ascii, tuple(warns))


def raster_from_array(z, posting_m: float, source: str = "array") -> Raster:
    """A raster in local metres (no reference system): row 0 north, column 0 west, origin at post (0, 0)."""
    return Raster(np.asarray(z, dtype=float), 0.0, 0.0, float(posting_m), float(posting_m), None, False, float(posting_m), float(posting_m), source)


def crop(r: Raster, rows: slice, cols: slice) -> Raster:
    x0, y0 = r.map_xy(rows.start or 0, cols.start or 0)
    return Raster(r.z[rows, cols].copy(), float(x0), float(y0), r.px, r.py, r.epsg, r.geographic, r.dx_m, r.dy_m, r.source, r.geokeys,
                  r.geo_double, r.geo_ascii, r.warnings)


def crop_map(r: Raster, xmin: float, xmax: float, ymin: float, ymax: float) -> Raster:
    """Crop to a window in map units (degrees for geographic rasters, metres for projected ones)."""
    r0, c0 = r.rowcol(xmin, ymax); r1, c1 = r.rowcol(xmax, ymin)
    r0, c0 = max(r0, 0), max(c0, 0); r1, c1 = min(r1 + 1, r.shape[0]), min(c1 + 1, r.shape[1])
    if r1 - r0 < 3 or c1 - c0 < 3:
        raise ValueError("the window lies outside the raster or is too small")
    return crop(r, slice(r0, r1), slice(c0, c1))


def coarsen_raster(r: Raster, k: int) -> Raster:
    """Block mean by an integer factor: what a coarser elevation model of the same ground would hold (used to test
    what a 10 m or 30 m map can see, against the faces the fine input resolves)."""
    if k <= 1:
        return r
    void = np.isnan(r.z)
    zc = _block(_fill_nearest(r.z), k)
    vc = _block(void.astype(float), k) > NODATA_SHARE
    zc[vc] = np.nan                                  # a coarse model keeps its voids
    return Raster(zc, r.x0 + 0.5 * (k - 1) * r.px, r.y0 - 0.5 * (k - 1) * r.py, r.px * k, r.py * k, r.epsg, r.geographic,
                  r.dx_m * k, r.dy_m * k, r.source + f"|block_mean_{k}", r.geokeys, r.geo_double, r.geo_ascii, r.warnings)


def _fill_nearest(z):
    """Fill voids with the nearest valid elevation (no artificial cliffs at void edges, unlike a mean fill)."""
    void = np.isnan(z)
    if not void.any():
        return z
    from scipy.ndimage import distance_transform_edt
    idx = distance_transform_edt(void, return_distances=False, return_indices=True)
    return z[tuple(idx)]


def _block_max(a, k):
    nr, nc = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    return a[:nr, :nc].reshape(nr // k, k, nc // k, k).max(axis=(1, 3))


def _block(a, k, how="mean"):
    nr, nc = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    b = a[:nr, :nc].reshape(nr // k, k, nc // k, k)
    return np.nanmean(b, axis=(1, 3)) if how == "mean" else np.nansum(b, axis=(1, 3))


# ---------------------------------------------------------------------------------------------------------------------
# assessment
# ---------------------------------------------------------------------------------------------------------------------
@lru_cache(maxsize=8)
def face_detector(posting_m: float) -> SG.FaceModel:
    """The stage 2 sub grid slip face detector, trained on synthetic dunes at this posting (deterministic)."""
    return SG.fit(float(posting_m), "base", 1.0)


def load_evidence_card() -> dict:
    with open(EVIDENCE_CARD, encoding="utf-8") as fh:
        return json.load(fh)


def resolution_gate(native_m: float, posting_m: float) -> dict:
    """What the map may claim at this posting, from the lidar tests of the study (evidence card)."""
    card = load_evidence_card()
    lid = card["lidar_tests"]
    near = min(lid["by_posting_m"], key=lambda k: abs(float(k) - posting_m))
    ev = lid["by_posting_m"][near]
    if native_m <= RESOLVED_MAX_M:
        status, msg = "RESOLVED", (f"The input resolves slip faces directly ({native_m:g} m posts): a cell is a face cell when at least "
                                   f"{FACE_MIN_AREA_M2:g} square metres of it are {SG.FACE_TRUTH_DEG:g} degrees or steeper, the truth rule of the lidar tests.")
    elif posting_m <= VERIFIED_MAX_M:
        status, msg = "DETECTOR", (f"Faces at {posting_m:g} m are estimated by the sub grid detector. On {lid['n_fields']} North American lidar dune fields, "
                                   f"a map at about {near} m still called {ev['miss_min']} to {ev['miss_max']} of the face cells TRAVERSABLE. "
                                   "Use onboard sensing as well.")
    else:
        status, msg = "COARSE", (f"Coarser than {VERIFIED_MAX_M:g} m: TRAVERSABLE here is NOT verified. On {lid['n_fields']} North American lidar dune "
                                 f"fields, a map at about {near} m called {ev['miss_min']} to {ev['miss_max']} of the cells with a steep slip face "
                                 "TRAVERSABLE. Survey the operating area at 10 m or finer before trusting a route.")
    return {"status": status, "message": msg, "evidence_posting_m": float(near), "evidence": ev}


@dataclass
class Assessment:
    raster: Raster                 # the input at the analysis posting
    posting_m: float
    native_m: float
    k: int                         # block factor from the input posts to the analysis posting
    profile: VehicleProfile
    slope_deg: np.ndarray
    q_pass: np.ndarray             # share of parameter draws for which the cell is passable
    face_prob: np.ndarray          # sub grid face probability (or 0/1 resolved face mask)
    face_source: str               # 'detector' or 'resolved from the input'
    classes: np.ndarray            # 0..4, see CLASS_NAMES
    gate: dict
    tau: float
    n_draws: int
    seed: int
    dem: Dem = field(repr=False, default=None)
    eg: TR.EdgeGeometry = field(repr=False, default=None)

    def shares(self) -> dict:
        n = self.classes.size
        out = {CLASS_NAMES[c]: float((self.classes == c).sum() / n) for c in CLASS_NAMES}
        out["UNKNOWN (total)"] = float(np.isin(self.classes, (2, 3, 4)).sum() / n)
        return out

    def summary(self) -> dict:
        return {"label": "SIMULATED BY ME: model and assumption dependent, not field evidence",
                "source": self.raster.source, "grid": list(self.classes.shape), "native_posting_m": round(self.native_m, 3),
                "analysis_posting_m": round(self.posting_m, 3), "block_factor": self.k, "face_source": self.face_source,
                "resolution_gate": self.gate, "vehicle_profile": self.profile.to_dict(),
                "critical_uphill_deg_nominal": round(self.profile.critical_uphill_deg(), 2),
                "critical_uphill_deg_published_posterior": round(builtin_profile("published-posterior").critical_uphill_deg(), 2),
                "dumont_field_curve_50pct_slip_deg_published": DUMONT_50PCT_SLIP_DEG,
                "class_shares": {k: round(v, 4) for k, v in self.shares().items()},
                "slope_deg_p95": round(float(np.nanpercentile(self.slope_deg, 95)), 2),
                "n_parameter_draws": self.n_draws, "seed": self.seed, "face_probability_threshold": self.tau,
                "input_warnings": list(self.raster.warnings)}


def assess(raster: Raster, posting_m: float | None = None, profile: VehicleProfile | None = None, n_draws: int = 128,
           seed: int = 20261023, tau: float = TC.TAU) -> Assessment:
    """Slope, face probability and the three class map of a DEM at a chosen posting (an integer multiple of the input)."""
    profile = profile or builtin_profile("assumed")
    native = float(np.sqrt(raster.dx_m * raster.dy_m))
    k = 1 if posting_m is None else max(1, int(round(posting_m / native)))
    z1 = raster.z
    if np.isnan(z1).all():
        raise ValueError("the elevation model holds no valid data")
    if n_draws < 8:
        raise ValueError("use at least 8 parameter draws")
    void = np.isnan(z1)
    zf = _fill_nearest(z1)
    zc = _block(zf, k) if k > 1 else zf
    nodata = (_block(void.astype(float), k) > NODATA_SHARE) if k > 1 else void
    dx, dy = raster.dx_m * k, raster.dy_m * k
    posting = float(np.sqrt(dx * dy))
    if min(zc.shape) < 3:
        raise ValueError("the window is too small for this posting (fewer than 3 cells across)")
    dem = Dem(zc, 0.0, 0.0, 1.0, 1.0, float(dx), float(dy), source=raster.source)
    eg = TR.precompute_edges(dem)
    draws = profile.draws(n_draws, seed)
    q = TC.q_pass(eg, draws)
    if native <= RESOLVED_MAX_M:
        steep = ((_slope_deg(zf, raster.dx_m, raster.dy_m) >= SG.FACE_TRUTH_DEG) & ~void).astype(float)
        post_area = raster.dx_m * raster.dy_m
        if dx * dy >= FACE_MIN_AREA_M2:      # the cell is large enough: the truth rule of the lidar tests, per cell
            pf = ((_block(steep, k, "sum") if k > 1 else steep) * post_area >= FACE_MIN_AREA_M2).astype(float)
        else:                                # finer cells: the same 10 square metre rule over a moving footprint, then the cell maximum
            from scipy.ndimage import uniform_filter
            w = int(np.ceil(np.sqrt(FACE_MIN_AREA_M2 / post_area)))
            face = (uniform_filter(steep, size=w, mode="constant") * w * w * post_area >= FACE_MIN_AREA_M2 - 1e-9).astype(float)
            pf = _block_max(face, k) if k > 1 else face
        src = "resolved from the input"
    else:
        model = face_detector(round(posting, 1))
        pf, src = model.predict(SG.features_2d(zc, float(dx), float(dy))), "detector"
    cls = TC.classify(q, pf, tau)
    nodata = nodata[:cls.shape[0], :cls.shape[1]]
    cls[nodata] = 5
    out_r = Raster(zc, raster.x0 + 0.5 * (k - 1) * raster.px, raster.y0 - 0.5 * (k - 1) * raster.py, raster.px * k, raster.py * k,
                   raster.epsg, raster.geographic, float(dx), float(dy), raster.source, raster.geokeys, raster.geo_double, raster.geo_ascii,
                   raster.warnings)
    return Assessment(out_r, posting, native, k, profile, _slope_deg(zc, dx, dy), q, pf, src, cls,
                      resolution_gate(native, posting), tau, len(draws), seed, dem, eg)


# ---------------------------------------------------------------------------------------------------------------------
# routes
# ---------------------------------------------------------------------------------------------------------------------
def policy_graph(a: Assessment, policy: str):
    """Routing graph of a policy. Every policy drops NO DATA cells. naive: the slip model only (stage 17). conservative:
    TRAVERSABLE cells only. risk weighted: no BLOCKED cells, cost raised by the face probability. Both cautious policies
    also never descend a grade of DOWNHILL_CUT_DEG or more between two cells (added for the product; not part of stage 17)."""
    if policy not in POLICIES:
        raise ValueError(f"unknown policy {policy!r}; choose from {POLICIES}")
    p = a.profile.nominal_params()
    from scipy.sparse import csr_matrix
    from .slipmodel import slip as _slip, edge_cost
    cut = -np.tan(np.radians(DOWNHILL_CUT_DEG))
    rows, cols, vals = [], [], []
    for s, d, dist, ta, tc in zip(a.eg.src, a.eg.dst, a.eg.dist, a.eg.tan_a, a.eg.tan_c):
        cost = edge_cost(dist, _slip(ta, tc, p), p.i_max)
        ok = np.isfinite(cost)
        if policy != "naive":
            ok &= np.asarray(ta) > cut
        rows.append(s[ok]); cols.append(d[ok]); vals.append(cost[ok])
    n = a.classes.size
    g = csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))
    c = a.classes.ravel()
    keep = (c != 5) if policy == "naive" else (c == 0) if policy == "conservative" else ((c != 1) & (c != 5))
    keep = keep.astype(float)
    g2 = (diags(keep) @ g @ diags(keep)).tocsr()
    if policy == "risk_weighted":
        g2 = g2.multiply(1.0 + RISK_W * a.face_prob.ravel()[None, :]).tocsr()
    g2.eliminate_zeros()
    return g2


@dataclass
class RoutePlan:
    policy: str
    start_rc: tuple
    goal_rc: tuple
    reachable: bool
    rc: np.ndarray | None
    metrics: dict
    warnings: list

    def lonlat(self, a: Assessment):
        if self.rc is None:
            return []
        x, y = a.raster.map_xy(self.rc[:, 0], self.rc[:, 1])
        lon, lat = a.raster.to_lonlat(x, y)
        return [[float(u), float(v)] for u, v in zip(np.atleast_1d(lon), np.atleast_1d(lat))]

    def geojson(self, a: Assessment) -> dict:
        props = {"policy": self.policy, "label": "SIMULATED BY ME", **self.metrics, "warnings": self.warnings,
                 "resolution_gate": a.gate["status"], "vehicle_profile": a.profile.name}
        geom = {"type": "LineString", "coordinates": self.lonlat(a)} if self.reachable else None
        crs_note = "WGS84 longitude, latitude" if (a.raster.geographic or a.raster.epsg) else "local grid metres (no reference system in the input)"
        return {"type": "FeatureCollection", "crs_note": crs_note,
                "features": [{"type": "Feature", "geometry": geom, "properties": props}]}


def _cell(a: Assessment, pt) -> tuple:
    """pt is (row, col) in analysis cells, or {'lon':..,'lat':..}, or {'x':..,'y':..} in map units."""
    if isinstance(pt, dict):
        if "lon" in pt:
            x, y = a.raster.from_lonlat(pt["lon"], pt["lat"])
        else:
            x, y = pt["x"], pt["y"]
        r, c = a.raster.rowcol(float(x), float(y))
    else:
        r, c = int(pt[0]), int(pt[1])
    if not (0 <= r < a.classes.shape[0] and 0 <= c < a.classes.shape[1]):
        raise ValueError(f"point {pt} lies outside the map")
    return r, c


def plan(a: Assessment, start, goal, policy: str = "conservative") -> RoutePlan:
    g = policy_graph(a, policy)
    s, t = _cell(a, start), _cell(a, goal)
    if s == t:
        raise ValueError("start and goal fall in the same cell")
    nr, nc = a.classes.shape
    dist, pred = dijkstra(g, directed=True, indices=s[0] * nc + s[1], return_predecessors=True)
    straight = float(np.hypot((t[1] - s[1]) * a.dem.dx, (t[0] - s[0]) * a.dem.dy))
    warn = []
    if a.gate["status"] == "COARSE":
        warn.append("Resolution gate: the map is coarser than 10 m, so TRAVERSABLE cells on this route are not verified.")
    if a.gate["status"] == "RESOLVED" and a.posting_m > VERIFIED_MAX_M:
        warn.append(f"Faces are resolved from the fine input, but grades on a {a.posting_m:g} m grid understate the grades the rover meets.")
    if a.profile.label.startswith("ASSUMPTION"):
        warn.append("Vehicle profile is an assumption, not a measurement: calibrate one from the vehicle's own slope runs.")
    tt = t[0] * nc + t[1]
    if not np.isfinite(dist[tt]):
        ends = [CLASS_NAMES[int(a.classes[x])] for x in (s, t)]
        if policy == "conservative" and any(e != "TRAVERSABLE" for e in ends):
            why = f"the start is {ends[0]} and the goal is {ends[1]}; the conservative policy uses TRAVERSABLE cells only"
        elif any(e == "NO DATA" for e in ends):
            why = "the start or the goal lies in a NO DATA cell"
        else:
            why = ("no route through TRAVERSABLE cells without a steep descent" if policy == "conservative" else "no route under this policy")
        return RoutePlan(policy, s, t, False, None, {"straight_m": round(straight, 1), "reason": why}, warn)
    path = [tt]
    while path[-1] != s[0] * nc + s[1]:
        path.append(int(pred[path[-1]]))
    rc = np.column_stack(np.divmod(np.array(path[::-1]), nc))
    seg = np.hypot(np.diff(rc[:, 1]) * a.dem.dx, np.diff(rc[:, 0]) * a.dem.dy)
    z = a.dem.z[rc[:, 0], rc[:, 1]]
    grade = np.degrees(np.arctan(np.diff(z) / np.where(seg > 0, seg, np.nan))) if len(seg) else np.array([0.0])
    cls = a.classes[rc[:, 0], rc[:, 1]]
    pf = a.face_prob[rc[:, 0], rc[:, 1]]
    crit = a.profile.critical_uphill_deg()
    m = {"length_m": round(float(seg.sum()), 1), "straight_m": round(straight, 1),
         "length_ratio": round(float(seg.sum() / straight), 3) if straight > 0 else None,
         "max_uphill_grade_deg": round(float(np.nanmax(np.clip(grade, 0, None))) if len(seg) else 0.0, 2),
         "max_downhill_grade_deg": round(float(np.nanmax(np.clip(-grade, 0, None))) if len(seg) else 0.0, 2),
         "critical_uphill_deg_nominal": round(crit, 2),
         "cells": int(len(rc)), "cells_traversable": int((cls == 0).sum()), "cells_unknown": int(np.isin(cls, (2, 3, 4)).sum()),
         "cells_blocked": int((cls == 1).sum()), "cells_no_data": int((cls == 5).sum()), "cells_face_risk": int((pf >= a.tau).sum()),
         "max_face_probability": round(float(pf.max()), 3), "cost": round(float(dist[tt]), 1)}
    if m["cells_unknown"]:
        warn.append(f"The route crosses {m['cells_unknown']} UNKNOWN cells: slow down and sense ahead there.")
    if m["cells_face_risk"]:
        warn.append(f"{m['cells_face_risk']} cells on the route may hide a slip face of {SG.FACE_TRUTH_DEG:g} degrees or more.")
    if m["max_downhill_grade_deg"] >= DOWNHILL_WARN_DEG:
        warn.append(f"The route descends a {m['max_downhill_grade_deg']} deg grade at {a.posting_m:g} m: lee faces of dunes are the main hazard "
                    "for a descending wheeled rover; check this section on the ground.")
    if m["max_uphill_grade_deg"] > 0.8 * crit:
        warn.append(f"The steepest uphill grade on the route ({m['max_uphill_grade_deg']} deg at {a.posting_m:g} m) is within 20 % of "
                    f"the nominal climbing limit ({crit:.1f} deg); real grades at metre scale are steeper than the map shows.")
    return RoutePlan(policy, s, t, True, rc, m, warn)


def compare_policies(a: Assessment, start, goal) -> list[RoutePlan]:
    return [plan(a, start, goal, p) for p in POLICIES]
