"""A deliberately minimal quasi-static slope-to-slip model.  SIMULATION ONLY.

Force balance on a slope for a wheeled vehicle on cohesionless sand:

    demand D  = sqrt( (tan(theta_along) + f_r)^2 + tan(theta_cross)^2 )       ("friction circle")
    capacity  = mu_max = tan(phi_eff)                                           (cohesionless limit, c = 0)
    slip i    = -i0 * ln(1 - D / mu_max)          for D < mu_max, else entrapment (i -> infinity)

The exponential-in-slip form is the Janosi-Hanamoto shear law, H/Hmax = 1 - exp(-j/K), with the
slip displacement j = i*L, so i0 = K/L, applied at the contact-patch level (no averaging over the
patch).  Sinkage, wheel geometry, speed, vehicle mass and soil cohesion are NOT modelled; they are
absorbed into f_r and i0.  Published evidence in this repo shows those lumped parameters vary by
roughly an order of magnitude between wheels and soils, so the numbers below are nominal
ASSUMPTIONS with ranges, not measured values.  See docs/REPORT.md, section "Simulation study".
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import numpy as np

# name: (nominal, low, high, status, basis)
PARAM_TABLE = {
    "phi_deg": (33.0, 28.0, 38.0, "published range of laboratory sands (not measured for Arabian sand)",
                "Internal friction angles printed in retrieved papers: 28 (Irani dry sand), 34 (Quikrete sand), "
                "35 (Mojave simulant), about 35 (olivine sand), 38 (Toyoura, Tottori); angle of repose 32-35 deg "
                "(Kroy et al. 2002). See research/raw/terramechanics_notes.md and morphology_rows.csv (M05)."),
    "f_r": (0.12, 0.05, 0.25, "ASSUMPTION",
            "Motion-resistance coefficient (resistance/weight) lumped for a small wheeled UGV in loose sand. "
            "No retrieved source gives a transferable value; range chosen to span light-to-heavy sinkage while "
            "keeping the vehicle able to move on flat sand. Replace with a measured value for the real vehicle."),
    "i0": (0.20, 0.05, 0.40, "ASSUMPTION",
           "Slip scale K/L. Published Janosi shear modulus K spans 0.0006-0.045 m between papers "
           "(terramechanics_notes.md), contact length L is vehicle specific, so i0 is a tuning parameter."),
    "i_max": (0.50, 0.40, 0.70, "ASSUMPTION (planning threshold)",
              "Slip above which an edge is treated as impassable. A Mars rover autonav slip table needed limits "
              "above 50 % on 15-20 deg terrain (evidence FLD-024); that is Mars-specific, used only as a pointer."),
}


@dataclass(frozen=True)
class SlipParams:
    phi_deg: float = PARAM_TABLE["phi_deg"][0]
    f_r: float = PARAM_TABLE["f_r"][0]
    i0: float = PARAM_TABLE["i0"][0]
    i_max: float = PARAM_TABLE["i_max"][0]
    form: str = "exp"        # 'exp' (nominal) or 'janosi_mean' (average of the shear law over the contact patch)
    cross: str = "circle"    # 'circle' (nominal) or 'additive'

    def with_(self, **kw) -> "SlipParams":
        return replace(self, **kw)

    @property
    def mu_max(self) -> float:
        return float(np.tan(np.radians(self.phi_deg)))


# Table for the contact-patch-averaged Janosi form: x = 1 - (1 - e^-s)/s, s = i/i0
_S = np.concatenate([np.linspace(0.0, 10.0, 4001), np.logspace(1, 5, 4000)[1:]])
_X = np.where(_S > 0, 1.0 - (1.0 - np.exp(-_S)) / np.where(_S > 0, _S, 1.0), 0.0)


def demand(tan_along, tan_cross, f_r: float, cross: str = "circle"):
    long_ = np.abs(np.asarray(tan_along, dtype=float) + f_r)
    tc = np.abs(np.asarray(tan_cross, dtype=float))
    if cross == "circle":
        return np.hypot(long_, tc)
    if cross == "additive":
        return long_ + tc
    raise ValueError(f"unknown cross-slope rule {cross!r}")


def slip_from_ratio(x, i0: float, form: str = "exp"):
    """Slip for demand/capacity ratio x in [0, 1); +inf where x >= 1 (entrapment)."""
    x = np.asarray(x, dtype=float)
    out = np.full(x.shape, np.inf)
    ok = x < 1.0
    xo = np.clip(x[ok], 0.0, None)
    if form == "exp":
        out[ok] = -i0 * np.log1p(-xo)
    elif form == "janosi_mean":
        s = np.interp(xo, _X, _S)
        # beyond the table, x ~ 1 - 1/s
        far = xo > _X[-1]
        s[far] = 1.0 / (1.0 - xo[far])
        out[ok] = i0 * s
    else:
        raise ValueError(f"unknown slip form {form!r}")
    return out


def slip(tan_along, tan_cross, p: SlipParams):
    return slip_from_ratio(demand(tan_along, tan_cross, p.f_r, p.cross) / p.mu_max, p.i0, p.form)


def critical_uphill_deg(p: SlipParams) -> float:
    """Steepest direct-ascent slope (no cross-slope) with slip <= i_max under this model."""
    if p.form == "exp":
        xc = 1.0 - np.exp(-p.i_max / p.i0)
    else:
        s = p.i_max / p.i0
        xc = 1.0 - (1.0 - np.exp(-s)) / s
    t = xc * p.mu_max - p.f_r
    return float(np.degrees(np.arctan(max(t, 0.0))))


def edge_cost(dist, slip_value, i_max: float):
    """Travel-time-like cost: distance / (1 - slip) for passable edges, +inf otherwise."""
    dist = np.asarray(dist, dtype=float)
    s = np.asarray(slip_value, dtype=float)
    cost = np.full(s.shape, np.inf)
    ok = s <= i_max
    cost[ok] = dist[ok] / (1.0 - s[ok])
    return cost
