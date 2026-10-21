"""Model families for slip against slope on dry sand, behind one interface (stage 15, docs/PREDICTIONS.md).

Every family maps (slope in degrees, slope kind, context, parameters) to a predicted slip ratio in [0, 1],
with 1 meaning entrapment (no progress).  SIMULATION ONLY, model assumption dependent.

    from dunerover.models import FAMILIES
    fam = FAMILIES["bekker_wong"]
    fam.predict(slopes_deg, "direct ascent", ctx, fam.nominal(ctx))

`ctx` is a dict describing the vehicle and soil of one curve: radius_m, width_m, load_N, gravity_g, and the soil
parameter set name for the Bekker Wong family.  Families ignore context they do not use.
"""
from .base import Family, Param
from .exp_model import ExpModel
from .bekker_wong import BekkerWong
from .baselines import MohrCoulombRatio, Logistic

from .mobility import MobilityPull, MobilityLogistic

FAMILIES = {f.name: f for f in (ExpModel(), BekkerWong(), MohrCoulombRatio(), Logistic())}
# stage 22 (2026-10-21): families that use the strength to load number of the granular scaling laws; kept apart so the
# stage 15 runs and their output folders are unchanged
EXTRA_FAMILIES = {f.name: f for f in (MobilityPull(), MobilityLogistic())}
__all__ = ["Family", "Param", "FAMILIES", "EXTRA_FAMILIES"]
