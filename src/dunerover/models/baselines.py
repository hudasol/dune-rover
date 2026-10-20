"""Families (c): two deliberately simple baselines.

MohrCoulombRatio: slip equals the traction demand ratio (tan(slope) + f_r) / tan(phi), capped at 1 (entrapment when the
demand reaches the Mohr Coulomb limit of a cohesionless sand).  Logistic: a purely empirical S curve in slope with two
parameters (slope at 50 % slip and a width); it has no physics and no transfer rule, so it can only be fitted and tested.
"""
from __future__ import annotations
import numpy as np
from .base import Family, Param


class MohrCoulombRatio(Family):
    name = "mohr_coulomb_ratio"
    description = "slip = (tan(slope) + f_r) / tan(phi), capped at 1; side slope uses the friction circle demand."
    params = (Param("phi_deg", 20.0, 45.0, 33.0, basis="published range of sand friction angles"),
              Param("f_r", 0.0, 0.40, 0.12, basis="ASSUMPTION"))
    slope_kinds = ("direct ascent", "side slope", "emulated by pull")

    def _slip(self, s, slope_kind, ctx, th):
        t = np.tan(np.radians(s))
        d = np.hypot(th["f_r"], t) if slope_kind == "side slope" else t + th["f_r"]
        return d / np.tan(np.radians(th["phi_deg"]))


class Logistic(Family):
    name = "logistic_empirical"
    description = "slip = 1 / (1 + exp(-(slope - s50) / w)); empirical, no physics."
    params = (Param("s50_deg", 2.0, 35.0, 15.0, basis="ASSUMPTION"), Param("w_deg", 0.5, 15.0, 4.0, basis="ASSUMPTION"))
    slope_kinds = ("direct ascent", "side slope", "emulated by pull")

    def _slip(self, s, slope_kind, ctx, th):
        return 1.0 / (1.0 + np.exp(-(s - th["s50_deg"]) / th["w_deg"]))
