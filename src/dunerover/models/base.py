"""Common interface of the slip model families."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Param:
    name: str
    low: float
    high: float
    nominal: float
    log: bool = False          # sample and calibrate on a log scale
    basis: str = ""            # PUBLISHED source or ASSUMPTION


class Family:
    """A model family.  Subclasses set name, description, params and implement _slip."""
    name = "base"
    description = ""
    params: tuple = ()
    slope_kinds = ("direct ascent",)

    def names(self):
        return [p.name for p in self.params]

    def nominal(self, ctx=None) -> dict:
        return {p.name: p.nominal for p in self.params}

    def bounds(self):
        return [(p.low, p.high) for p in self.params]

    def applies(self, slope_kind: str) -> bool:
        return slope_kind in self.slope_kinds

    def predict(self, slopes_deg, slope_kind: str, ctx: dict, theta: dict) -> np.ndarray:
        if not self.applies(slope_kind):
            raise ValueError(f"{self.name} does not model slope kind {slope_kind!r}")
        s = np.asarray(slopes_deg, dtype=float)
        out = np.asarray(self._slip(s, slope_kind, ctx, theta), dtype=float)
        return np.clip(np.nan_to_num(out, nan=1.0, posinf=1.0), 0.0, 1.0)

    def _slip(self, s, slope_kind, ctx, theta):
        raise NotImplementedError
