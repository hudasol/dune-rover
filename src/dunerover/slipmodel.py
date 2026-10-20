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
from contextlib import contextmanager
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


# Alternative range sets (added 2026-10-18, docs/PREDICTIONS.md stage 9).  'original' is the default and is what every
# result before 2026-10-18 used.  A set is applied only on request (apply_range_set), for a separately labelled run.
_ORIGINAL = {k: v for k, v in PARAM_TABLE.items()}
RANGE_SETS = {
    "original": {},
    "widened_i0": {
        "i0": (0.81, 0.05, 1.20, "ASSUMPTION (widened 2026-10-18)",
               "Nominal 0.81 is the lower bound implied by Ishigami et al. 2009 Table I (kx 0.07 m, wheel radius 0.055 m; "
               "TM-IS09-2) under i0 = K/L with the largest contact arc; shorter contact lengths imply larger values (above 1.20 "
               "for contact lengths below about 0.058 m), so the range contains only that lower bound. The upper end 1.20 is an "
               "assumption chosen to contain it and the Dumont fitted i0 of stage 7 (5 to 95 %: 0.29 to 0.94)."),
    },
    "widened_i0_fr": {
        "i0": None,   # same as widened_i0, filled below
        "f_r": (0.12, 0.05, 0.35, "ASSUMPTION (test of the f_r range, 2026-10-18)",
                "Upper end raised from 0.25 to 0.35 to test whether the resistance range matters once i0 is widened; "
                "no retrieved source gives a transferable value."),
    },
}
RANGE_SETS["widened_i0_fr"]["i0"] = RANGE_SETS["widened_i0"]["i0"]
# Posterior range set (added 2026-10-20, docs/PREDICTIONS.md stage 15): 5, 50 and 95 % posterior quantiles of the exponential
# family calibrated on the 12 direct ascent curves comparable to dune sand (results/model_validation/part_exp_existing_mohr_coulomb_ratio_logistic_empirical/posterior_exp.json).
# SIMULATED BY ME from PUBLISHED curves of other vehicles (Heverly 2013, Inotsume 2016, Li 2008 on Mars): not a measurement for any rover in Arabia.
RANGE_SETS["posterior_2026_10_20"] = {
    "phi_deg": (36.93, 30.57, 43.74, "POSTERIOR (stage 15), lumped effective friction angle of the fitted curves", "posterior_exp.json, 5 to 95 %"),
    "f_r": (0.129, 0.033, 0.320, "POSTERIOR (stage 15)", "posterior_exp.json, 5 to 95 %"),
    "i0": (0.627, 0.327, 1.211, "POSTERIOR (stage 15)", "posterior_exp.json, 5 to 95 %"),
}


def apply_range_set(name: str) -> None:
    """Set PARAM_TABLE (in place) to a named range set; 'original' restores the default.  Used by the study CLIs."""
    if name not in RANGE_SETS:
        raise ValueError(f"unknown range set {name!r}; choose from {sorted(RANGE_SETS)}")
    PARAM_TABLE.clear(); PARAM_TABLE.update(_ORIGINAL); PARAM_TABLE.update(RANGE_SETS[name])
    _ACTIVE["name"] = name


_ACTIVE = {"name": "original"}


def active_range_set() -> str:
    return _ACTIVE["name"]


def range_set_label() -> str:
    """Text for figure footers and logs: empty under the original set, so original outputs keep their wording."""
    return "" if _ACTIVE["name"] == "original" else f" Range set {_ACTIVE['name']}."


@contextmanager
def use_range_set(name: str):
    """Apply a range set for the duration of a block and always restore the previous one."""
    prev = _ACTIVE["name"]
    apply_range_set(name)
    try:
        yield
    finally:
        apply_range_set(prev)


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


def nominal_params() -> SlipParams:
    """Nominal parameters of the active range set (equal to SlipParams() under the default 'original' set)."""
    return SlipParams(**{k: PARAM_TABLE[k][0] for k in ("phi_deg", "f_r", "i0", "i_max")})


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
