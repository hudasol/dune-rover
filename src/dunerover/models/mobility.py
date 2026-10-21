"""Families (d), stage 22 (docs/PREDICTIONS.md): slip against slope through one dimensionless strength to load number.

Both families use the number Pi = rho g b r^2 / W (soil bulk density rho, gravity g, wheel width b, wheel radius r,
load per wheel W), the mass group of the granular scaling laws (Slonaker et al. 2017, Eqs. 1, 7 and 8, with L = r and
D = b; Hu et al. 2025, Eq. 1) written with the load as a weight; see research/phase4/scaling_laws_notes.md.  The laws
are similarity laws: they say which group matters, not the shape or the level of the curve.  The curve shapes and the
log dependence on Pi below are proposals of this repository (ASSUMPTION), in the reduced forms of the notes (no
friction angle term, no grouser term, resistance exponent fixed at 1), because most published curves do not report
friction angle, grouser height or a penetration gradient.  rho is the curve's reported bulk density, or 1600 kg/m3
when it is not reported (ASSUMPTION, stated per curve in the results).  SIMULATION ONLY, model assumption dependent.

MobilityPull (family A, reduced): the slope is treated as a drawbar demand tan(slope) per unit normal load, and an
exponential pull against slip curve tan(slope) = mu_max (1 - exp(-s / s_k)) - rho_r is inverted:
    s = -s_k ln(1 - (tan(slope) + rho_r) / mu_max), and s = 1 when tan(slope) + rho_r >= mu_max,
    mu_max = m0 + m1 ln(Pi), rho_r = r0 / Pi.
MobilityLogistic (family B, reduced): s = 1 / (1 + exp(-(tan(slope) - t50) / w)), t50 = a0 + a1 ln(Pi).
"""
from __future__ import annotations
import numpy as np
from .base import Family, Param

RHO_DEFAULT = 1600.0
G_EARTH = 9.81


def mobility_number(ctx: dict) -> float:
    rho = ctx.get("density_kg_m3") or RHO_DEFAULT
    return rho * G_EARTH * ctx["width_m"] * ctx["radius_m"] ** 2 / ctx["load_N"]


class MobilityPull(Family):
    name = "mobility_pull"
    description = "drawbar equivalence of the slope with an exponential pull against slip curve whose limit and resistance depend on Pi = rho g b r^2 / W"
    params = (Param("m0", 0.05, 1.5, 0.6, basis="ASSUMPTION"), Param("m1", -0.5, 0.5, 0.1, basis="ASSUMPTION"),
              Param("r0", 1e-3, 1.0, 0.03, log=True, basis="ASSUMPTION"), Param("s_k", 0.02, 2.0, 0.3, log=True, basis="ASSUMPTION"))
    slope_kinds = ("direct ascent", "emulated by pull")
    needs = ("radius_m", "width_m", "load_N")

    def _slip(self, s, slope_kind, ctx, th):
        pi = mobility_number(ctx)
        mu = th["m0"] + th["m1"] * np.log(pi)
        demand = np.tan(np.radians(s)) + th["r0"] / pi
        frac = demand / mu if mu > 0 else np.full_like(s, np.inf)
        out = np.where(frac < 1.0, -th["s_k"] * np.log(np.clip(1.0 - frac, 1e-12, None)), 1.0)
        return np.where(frac <= 0, 0.0, out)


class MobilityLogistic(Family):
    name = "mobility_logistic"
    description = "logistic in tan(slope) whose midpoint depends on ln(Pi), Pi = rho g b r^2 / W"
    params = (Param("a0", -0.5, 1.5, 0.3, basis="ASSUMPTION"), Param("a1", -0.5, 0.5, 0.05, basis="ASSUMPTION"),
              Param("w", 0.01, 1.0, 0.08, log=True, basis="ASSUMPTION"))
    slope_kinds = ("direct ascent", "emulated by pull")
    needs = ("radius_m", "width_m", "load_N")

    def _slip(self, s, slope_kind, ctx, th):
        t50 = th["a0"] + th["a1"] * np.log(mobility_number(ctx))
        return 1.0 / (1.0 + np.exp(-(np.tan(np.radians(s)) - t50) / th["w"]))
