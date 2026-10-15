"""Checks of the published anchor inputs and the comparison helpers (scripts/anchor_comparisons.py)."""
import importlib.util, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("anchor_comparisons", os.path.join(ROOT, "scripts", "anchor_comparisons.py"))
AC = importlib.util.module_from_spec(spec); spec.loader.exec_module(AC)


def test_dumont_cubic_reproduces_the_text_statements():
    # Heverly et al. 2013, Sec 6.3: below 50 % under 12.5 deg, about 75 % at 16 deg, about 90 % at 20 deg
    assert AC.dumont(12.4) < 0.5
    assert abs(AC.dumont(16.0) - 0.75) < 0.03
    assert abs(AC.dumont(20.0) - 0.90) < 0.02


def test_model_grid_matches_scalar_model():
    P = {"phi_deg": np.array([33.0, 28.0]), "f_r": np.array([0.12, 0.25]), "i0": np.array([0.2, 0.4])}
    for cross in (False, True):
        G = AC.model_grid([5.0, 15.0], P, cross=cross)
        for i in range(2):
            for j, sl in enumerate((5.0, 15.0)):
                assert abs(G[i, j] - AC.model_slip(sl, P["phi_deg"][i], P["f_r"][i], P["i0"][i], cross=cross)) < 1e-9


def test_crossing_interpolates():
    assert abs(AC.crossing(np.array([0.0, 1.0]), np.array([0.0, 1.0])) - 0.5) < 1e-12
    assert AC.crossing(np.array([0.0, 1.0]), np.array([0.0, 0.4])) is None


def test_ishigami_i0_bound():
    assert abs(AC.ISH_I0_LOW - 0.07 / (0.055 * np.pi / 2)) < 1e-12 and AC.ISH_I0_LOW > PARAM_HIGH_I0()


def PARAM_HIGH_I0():
    from dunerover.slipmodel import PARAM_TABLE
    return PARAM_TABLE["i0"][2]
