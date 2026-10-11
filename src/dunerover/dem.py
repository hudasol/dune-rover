"""Loading and handling Copernicus GLO-30 style GeoTIFF tiles without GDAL."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import tifffile

WGS84_A = 6378137.0
WGS84_E2 = 0.00669437999014


def metres_per_degree(lat_deg: float) -> tuple[float, float]:
    """(metres per degree of longitude, metres per degree of latitude) on WGS84."""
    phi = np.radians(lat_deg)
    s2 = np.sin(phi) ** 2
    n = WGS84_A / np.sqrt(1.0 - WGS84_E2 * s2)                       # prime-vertical radius
    m = WGS84_A * (1.0 - WGS84_E2) / (1.0 - WGS84_E2 * s2) ** 1.5    # meridional radius
    return float(np.radians(1.0) * n * np.cos(phi)), float(np.radians(1.0) * m)


@dataclass
class Dem:
    z: np.ndarray        # elevation, metres, float64, NaN = no data
    lat_top: float       # latitude of row 0 (post centre)
    lon_left: float      # longitude of column 0
    dlat: float          # degrees per post (positive, rows run south)
    dlon: float          # degrees per post (positive, columns run east)
    dx: float            # metres per post, east-west, at window centre latitude
    dy: float            # metres per post, north-south
    source: str = ""

    @property
    def shape(self):
        return self.z.shape

    def latlon(self, r: float, c: float) -> tuple[float, float]:
        return self.lat_top - r * self.dlat, self.lon_left + c * self.dlon

    def rowcol(self, lat: float, lon: float) -> tuple[int, int]:
        return int(round((self.lat_top - lat) / self.dlat)), int(round((lon - self.lon_left) / self.dlon))


def _spacing(lat_centre: float, dlat: float, dlon: float) -> tuple[float, float]:
    mlon, mlat = metres_per_degree(lat_centre)
    return mlon * dlon, mlat * dlat


def load_tile(path: str) -> Dem:
    """Read a whole single-band GeoTIFF tile (EPSG:4326, point-registered tiepoint)."""
    with tifffile.TiffFile(path) as tf:
        page = tf.pages[0]
        z = page.asarray().astype(np.float64)
        scale = page.tags["ModelPixelScaleTag"].value
        tie = page.tags["ModelTiepointTag"].value
    z[~np.isfinite(z)] = np.nan
    lon_left, lat_top = float(tie[3]), float(tie[4])
    dlon, dlat = float(scale[0]), float(scale[1])
    lat_c = lat_top - 0.5 * z.shape[0] * dlat
    dx, dy = _spacing(lat_c, dlat, dlon)
    return Dem(z, lat_top, lon_left, dlat, dlon, dx, dy, source=str(path))


def crop(dem: Dem, lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> Dem:
    r0, c0 = dem.rowcol(lat_max, lon_min)
    r1, c1 = dem.rowcol(lat_min, lon_max)
    r0, c0 = max(r0, 0), max(c0, 0)
    r1, c1 = min(r1 + 1, dem.shape[0]), min(c1 + 1, dem.shape[1])
    if r1 <= r0 or c1 <= c0:
        raise ValueError("requested window lies outside the tile")
    z = dem.z[r0:r1, c0:c1].copy()
    lat_top, lon_left = dem.latlon(r0, c0)
    lat_c = lat_top - 0.5 * z.shape[0] * dem.dlat
    dx, dy = _spacing(lat_c, dem.dlat, dem.dlon)
    return Dem(z, lat_top, lon_left, dem.dlat, dem.dlon, dx, dy, source=dem.source)


def coarsen(dem: Dem, k: int) -> Dem:
    """Block-mean aggregation by integer factor k (a crude stand-in for a coarser DEM)."""
    if k == 1:
        return dem
    nr, nc = (dem.z.shape[0] // k) * k, (dem.z.shape[1] // k) * k
    z = dem.z[:nr, :nc].reshape(nr // k, k, nc // k, k).mean(axis=(1, 3))
    return Dem(z, dem.lat_top - 0.5 * (k - 1) * dem.dlat, dem.lon_left + 0.5 * (k - 1) * dem.dlon,
               dem.dlat * k, dem.dlon * k, dem.dx * k, dem.dy * k, source=dem.source + f"|block_mean_{k}")


def add_correlated_noise(dem: Dem, sigma_m: float, corr_posts: float, seed: int) -> Dem:
    """Add spatially correlated Gaussian noise (std sigma_m) - an ASSUMED stand-in for DEM error."""
    if sigma_m <= 0:
        return dem
    from scipy.ndimage import gaussian_filter
    rng = np.random.default_rng(seed)
    f = rng.standard_normal(dem.z.shape)
    if corr_posts > 0:
        f = gaussian_filter(f, corr_posts, mode="reflect")
    f = f / f.std() * sigma_m
    return Dem(dem.z + f, dem.lat_top, dem.lon_left, dem.dlat, dem.dlon, dem.dx, dem.dy, dem.source + f"|noise{sigma_m}")
