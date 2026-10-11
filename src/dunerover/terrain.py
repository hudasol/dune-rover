"""Terrain derivatives (Horn 1981, 3x3) on a regular grid."""
from __future__ import annotations
import numpy as np


def horn_gradient(z: np.ndarray, dx: float, dy: float) -> tuple[np.ndarray, np.ndarray]:
    """Return (dz/dEast, dz/dNorth). Rows run south, columns run east. Edges use replicated padding."""
    zp = np.pad(z, 1, mode="edge")
    a, b, c = zp[:-2, :-2], zp[:-2, 1:-1], zp[:-2, 2:]
    d, f = zp[1:-1, :-2], zp[1:-1, 2:]
    g, h, i = zp[2:, :-2], zp[2:, 1:-1], zp[2:, 2:]
    dz_de = ((c + 2 * f + i) - (a + 2 * d + g)) / (8.0 * dx)
    dz_dsouth = ((g + 2 * h + i) - (a + 2 * b + c)) / (8.0 * dy)
    return dz_de, -dz_dsouth


def slope_deg(z: np.ndarray, dx: float, dy: float) -> np.ndarray:
    ge, gn = horn_gradient(z, dx, dy)
    return np.degrees(np.arctan(np.hypot(ge, gn)))


def aspect_deg(z: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """Downslope direction, degrees clockwise from north."""
    ge, gn = horn_gradient(z, dx, dy)
    return (np.degrees(np.arctan2(-ge, -gn)) + 360.0) % 360.0


def hillshade(z: np.ndarray, dx: float, dy: float, azimuth_deg: float = 315.0, altitude_deg: float = 35.0) -> np.ndarray:
    ge, gn = horn_gradient(z, dx, dy)
    slope = np.arctan(np.hypot(ge, gn))
    aspect = np.arctan2(-ge, -gn)
    az, alt = np.radians(azimuth_deg), np.radians(altitude_deg)
    hs = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)
    return np.clip(hs, 0, 1)
