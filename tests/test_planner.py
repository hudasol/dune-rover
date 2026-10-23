"""Tests of the Dune Rover Planner (src/dunerover/planner.py, report.py, cli.py).  SYNTHETIC inputs only."""
import csv
import json
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dunerover import planner as P  # noqa: E402
from dunerover import fieldanalysis as FA  # noqa: E402
from dunerover.cli import synthetic_dunes, main as cli_main  # noqa: E402


@pytest.fixture(scope="module")
def dunes():
    return P.raster_from_array(synthetic_dunes(n=200, posting=2.0), 2.0, "SYNTHETIC")


def test_resolution_gate_by_posting(dunes):
    fine = P.raster_from_array(synthetic_dunes(n=120, posting=1.0), 1.0, "SYNTHETIC")
    assert P.assess(fine, 5).gate["status"] == "RESOLVED"
    assert P.assess(P.coarsen_raster(dunes, 5), n_draws=32).gate["status"] == "DETECTOR"
    a30 = P.assess(P.coarsen_raster(dunes, 15), n_draws=32)
    assert a30.gate["status"] == "COARSE" and "NOT verified" in a30.gate["message"]


def test_resolved_faces_follow_the_truth_rule(dunes):
    a = P.assess(dunes, 10, n_draws=32)
    assert a.face_source == "resolved from the input"
    assert set(np.unique(a.face_prob)) <= {0.0, 1.0} and a.face_prob.mean() > 0.05   # the synthetic lee faces are found


def test_conservative_route_stays_on_traversable_cells(dunes):
    a = P.assess(P.coarsen_raster(dunes, 5), n_draws=32)
    nr, nc = a.classes.shape
    c = int(np.argmax((a.classes == 0).mean(axis=0)))              # a column along a stoss slope, parallel to the ridges
    rows = np.flatnonzero(a.classes[:, c] == 0)
    s, g = (int(rows[0]), c), (int(rows[-1]), c)
    rp = P.plan(a, s, g, "conservative")
    assert rp.reachable
    assert (a.classes[rp.rc[:, 0], rp.rc[:, 1]] == 0).all()
    assert rp.metrics["cells_unknown"] == 0 and rp.metrics["length_m"] >= rp.metrics["straight_m"] - 1e-6
    naive = P.plan(a, s, g, "naive")
    assert naive.reachable
    steps = np.abs(np.diff(naive.rc, axis=0)).max(axis=1)
    assert (steps == 1).all()                                       # a connected 8 neighbour path


def test_coarse_map_always_warns(dunes):
    a = P.assess(P.coarsen_raster(dunes, 15), n_draws=32)
    rp = P.plan(a, (1, 1), (a.classes.shape[0] - 2, a.classes.shape[1] - 2), "naive")
    assert any("Resolution gate" in w for w in rp.warnings)


def test_profile_from_synthetic_runs_recovers_truth():
    d = FA.synthetic_runs(seed=11, f_r=0.14, i0=0.22, phi=33.0, sigma=0.03)
    prof = P.profile_from_runs(d, n_boot=60)
    assert prof.label.startswith("MEASURED")
    assert abs(prof.nominal["f_r"] - 0.14) < 0.05 and abs(prof.nominal["i0"] - 0.22) < 0.1
    for k in P.KEYS:
        assert prof.ranges[k][0] <= prof.nominal[k] <= prof.ranges[k][1]


def test_profile_round_trip_and_validation(tmp_path):
    prof = P.builtin_profile("published-posterior")
    f = tmp_path / "p.json"; prof.save(str(f))
    back = P.VehicleProfile.load(str(f))
    assert back.ranges == prof.ranges and back.nominal == prof.nominal
    bad = prof.to_dict(); bad["nominal"]["i0"] = 9.0
    f2 = tmp_path / "bad.json"; f2.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        P.VehicleProfile.load(str(f2))
    with pytest.raises(ValueError):
        P.builtin_profile("no-such-profile")


def test_profile_draws_can_move_on_level_ground():
    for name in P.BUILTIN_PROFILES:
        for p in P.builtin_profile(name).draws(64):
            assert p.f_r / p.mu_max <= 1.0 - np.exp(-p.i_max / p.i0) + 1e-12


def _write_geotiff(path, z, lon0=53.5, lat0=23.2, step=1.0 / 3600):
    import tifffile
    gk = (1, 1, 0, 3, 1024, 0, 1, 2, 1025, 0, 1, 1, 2048, 0, 1, 4326)
    tifffile.imwrite(path, z.astype(np.float32), extratags=[(33550, "d", 3, (step, step, 0.0), False),
                                                            (33922, "d", 6, (0, 0, 0, lon0, lat0, 0), False), (34735, "H", len(gk), gk, False)])


def test_geotiff_round_trip_and_cli(tmp_path):
    z = synthetic_dunes(n=150, posting=30.0)
    f = tmp_path / "dem.tif"; _write_geotiff(str(f), z)
    r = P.read_raster(str(f))
    assert r.geographic and r.epsg == 4326 and 25 < r.dx_m < 32
    out = tmp_path / "out"
    cli_main(["plan", str(f), "--start-rc", "75,3", "--goal-rc", "75,146", "--draws", "24", "--out", str(out)])
    for name in ("report.html", "map.png", "classes.tif", "summary.json", "routes.geojson"):
        assert (out / name).exists()
    summ = json.loads((out / "summary.json").read_text())
    assert summ["resolution_gate"]["status"] == "COARSE" and len(summ["routes"]) == 3
    gj = json.loads((out / "routes.geojson").read_text())
    lon, lat = gj["features"][0]["geometry"]["coordinates"][0]
    assert 53.4 < lon < 53.6 and 23.0 < lat < 23.3
    back = P.read_raster(str(out / "classes.tif"))
    assert back.shape == (150, 150) and abs(back.x0 - r.x0) < 1e-9 and abs(back.y0 - r.y0) < 1e-9
    html = (out / "report.html").read_text()
    assert "SIMULATED BY ME" in html and "Resolution gate: COARSE" in html


def test_cli_vehicle_calibrate(tmp_path):
    d = FA.synthetic_runs(seed=5)
    f = tmp_path / "runs.csv"
    with open(f, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(FA.REQUIRED)
        for i in range(len(d["run_id"])):
            w.writerow([d["run_id"][i], d["slope_deg"][i], d["v_true_mps"][i], d["wheel_omega_rad_s"][i], d["r_eff_m"][i], int(d["entrapped"][i]), d["phi_deg"][i]])
    out = tmp_path / "rover.json"
    cli_main(["vehicle", "calibrate", str(f), "--name", "test-rover", "--out", str(out)])
    assert P.VehicleProfile.load(str(out)).name == "test-rover"


def test_evidence_card_is_current():
    import build_evidence_card as B
    card = json.load(open(P.EVIDENCE_CARD, encoding="utf-8"))
    assert card == json.loads(json.dumps(B.build(), sort_keys=True))


def test_generated_sentences_have_no_missing_values():
    import phase3_values as P3
    v = P3.values()
    for k, val in v.items():
        if isinstance(val, str) and ("sentence" in k or k.endswith("_line")):
            assert "n/a" not in val, k
