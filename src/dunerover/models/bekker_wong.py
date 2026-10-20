"""Family (b): rigid wheel terramechanics in the Bekker, Wong and Reece tradition, as written by Ishigami et al. 2007.

For a wheel of radius R and width b carrying normal load Wn = W cos(slope) at slip i (no rebound, exit angle 0):

    entry angle      theta1 = arccos(1 - z / R)
    max stress angle theta_m = (a0 + a1 i) theta1
    normal stress    sigma(theta) = (kc / b + kphi) R^n (cos(theta*) - cos(theta1))^n,
                     theta* = theta in front of theta_m, mapped linearly behind it (Wong and Reece)
    shear            tau = (c + sigma tan(phi)) (1 - exp(-j / K)),  j = R [(theta1 - theta) - (1 - i)(sin(theta1) - sin(theta))]
    vertical force   Fz = R b integral (sigma cos + tau sin) dtheta, solved for z so that Fz = Wn
    drawbar pull     DP = R b integral (tau cos - sigma sin) dtheta

The climbing slip is the i at which DP equals the slope load W sin(slope); if DP stays below it up to i = 0.99 the wheel
is entrapped (slip 1).  Direct ascent only.  Grousers, bulldozing, multi pass and dynamic sinkage are not modelled.

Parameter sets are PUBLISHED (named rows); calibration varies phi, K, cohesion and a common multiplier of kc and kphi.
"""
from __future__ import annotations
import numpy as np
from .base import Family, Param

SOIL_SETS = {  # name: kc N/m^(n+1), kphi N/m^(n+2), n, c Pa, phi deg, K m, a0, a1, source
    "toyoura_ishigami2007": (1.37e3, 8.14e5, 1.00, 800.0, 37.2, 0.036, 0.40, 0.15,
                             "Ishigami et al. 2007 Table I (TM-IS07-1); K is kx at zero slip angle"),
    "dem_calibrated_zhang2024": (-4957.0, 235605.0, 0.883, 21.872, 21.259, 0.0062, 0.40, 0.15,
                                 "Zhang et al. 2024 Table 4 (SIM-005), a simulated material; a0 and a1 from Ishigami 2007 (ASSUMPTION)"),
}
NQ = 160
_U = (np.arange(NQ) + 0.5) / NQ    # midpoint rule on [0, 1]


def _forces(z, i, R, b, kc, kphi, n, c, phi, K, a0, a1):
    """Vertical force and drawbar pull for arrays z, i of the same shape (N)."""
    z = np.clip(z, 1e-7, 0.999 * R)
    th1 = np.arccos(1.0 - z / R)[..., None]
    thm = (a0 + a1 * np.asarray(i, dtype=float))[..., None] * th1
    th = _U[None, :] * th1                                   # 0 .. theta1
    front = th >= thm
    thstar = np.where(front, th, th1 - th / np.maximum(thm, 1e-12) * (th1 - thm))
    base = np.clip(np.cos(thstar) - np.cos(th1), 0.0, None)
    sig = (kc / b + kphi) * R ** n * base ** n
    sig = np.clip(sig, 0.0, None)
    j = R * ((th1 - th) - (1.0 - np.asarray(i, dtype=float)[..., None]) * (np.sin(th1) - np.sin(th)))
    tau = (c + sig * np.tan(np.radians(phi))) * (1.0 - np.exp(-np.clip(j, 0.0, None) / K))
    dth = th1[..., 0] / NQ
    fz = R * b * (sig * np.cos(th) + tau * np.sin(th)).sum(axis=-1) * dth
    dp = R * b * (tau * np.cos(th) - sig * np.sin(th)).sum(axis=-1) * dth
    return fz, dp


def climbing_slip(slopes_deg, R, b, W, kc, kphi, n, c, phi, K, a0=0.4, a1=0.15, emulated=False):
    """Slip needed to climb each slope (direct ascent); 1.0 where the wheel cannot climb (entrapment)."""
    s = np.radians(np.asarray(slopes_deg, dtype=float))
    wn = W * (np.ones_like(s) if emulated else np.cos(s))
    target = W * np.sin(s)

    def dp_at(i):
        lo, hi = np.full(s.shape, 1e-7), np.full(s.shape, 0.999 * R)
        for _ in range(40):                                   # bisection on sinkage: Fz increases with z
            mid = 0.5 * (lo + hi)
            fz, _ = _forces(mid, i, R, b, kc, kphi, n, c, phi, K, a0, a1)
            big = fz > wn
            hi = np.where(big, mid, hi); lo = np.where(big, lo, mid)
        z = 0.5 * (lo + hi)
        return _forces(z, i, R, b, kc, kphi, n, c, phi, K, a0, a1)[1], z

    dp_max, _ = dp_at(np.full(s.shape, 0.99))
    ilo, ihi = np.zeros(s.shape), np.full(s.shape, 0.99)
    dp0, _ = dp_at(ilo)
    for _ in range(30):                                       # bisection on slip: DP increases with i
        mid = 0.5 * (ilo + ihi)
        dp, _ = dp_at(mid)
        up = dp < target
        ilo = np.where(up, mid, ilo); ihi = np.where(up, ihi, mid)
    out = 0.5 * (ilo + ihi)
    out = np.where(dp0 >= target, 0.0, out)
    return np.where(dp_max < target, 1.0, out)


class BekkerWong(Family):
    name = "bekker_wong"
    description = "Rigid wheel Bekker, Wong and Reece stress model (Ishigami et al. 2007 form); needs wheel radius, width and load."
    params = (Param("phi_deg", 20.0, 45.0, 37.2, basis="published range; nominal from TM-IS07-1"),
              Param("K_m", 0.001, 0.10, 0.036, log=True, basis="published range of Janosi K (0.0006 to 0.045 m in retrieved papers); nominal TM-IS07-1"),
              Param("c_Pa", 0.0, 1500.0, 800.0, basis="dry sand cohesion, nominal TM-IS07-1"),
              Param("k_mult", 0.1, 10.0, 1.0, log=True, basis="ASSUMPTION, common multiplier of kc and kphi of the soil set"))

    def nominal(self, ctx=None):
        kc, kphi, n, c, phi, K, a0, a1, _ = SOIL_SETS[(ctx or {}).get("soil_set", "toyoura_ishigami2007")]
        return {"phi_deg": phi, "K_m": K, "c_Pa": c, "k_mult": 1.0}

    def applies(self, slope_kind):
        return slope_kind in ("direct ascent", "emulated by pull")

    def _slip(self, s, slope_kind, ctx, th):
        kc, kphi, n, c, phi, K, a0, a1, _ = SOIL_SETS[ctx.get("soil_set", "toyoura_ishigami2007")]
        return climbing_slip(s, ctx["radius_m"], ctx["width_m"], ctx["load_N"], kc * th["k_mult"], kphi * th["k_mult"], n,
                             th["c_Pa"], th["phi_deg"], th["K_m"], a0, a1, emulated=(slope_kind == "emulated by pull"))
