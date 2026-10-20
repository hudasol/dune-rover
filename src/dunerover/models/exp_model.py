"""Family (a): the repository's existing quasi static model (slipmodel.py), exponential slip law, unchanged."""
from __future__ import annotations
import numpy as np
from .base import Family, Param
from ..slipmodel import SlipParams, slip


class ExpModel(Family):
    name = "exp_existing"
    description = ("Friction circle demand over tan(phi) capacity, slip = -i0 ln(1 - demand/capacity) (Janosi law at the contact "
                   "patch); the model used for every map in this repository.")
    params = (Param("phi_deg", 20.0, 45.0, 33.0, basis="published range of sand friction angles (wider than PARAM_TABLE for calibration)"),
              Param("f_r", 0.0, 0.40, 0.12, basis="ASSUMPTION, motion resistance ratio"),
              Param("i0", 0.02, 2.0, 0.20, log=True, basis="ASSUMPTION, slip scale K/L"))
    slope_kinds = ("direct ascent", "side slope", "emulated by pull")

    def _slip(self, s, slope_kind, ctx, th):
        t = np.tan(np.radians(s))
        p = SlipParams(phi_deg=th["phi_deg"], f_r=th["f_r"], i0=th["i0"])
        if slope_kind == "side slope":
            return slip(np.zeros_like(t), t, p)
        return slip(t, np.zeros_like(t), p)
