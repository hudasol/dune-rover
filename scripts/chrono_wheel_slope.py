#!/usr/bin/env python3
"""Stage 14 (docs/PREDICTIONS.md): single rigid wheel climbing a sand slope in Project Chrono (Soil Contact Model).

Run with a Python that has pychrono 9.0.1 (free, BSD 3 licence; installed from the projectchrono conda channel):

    micromamba create -p /opt/mm/chrono -c projectchrono -c conda-forge python=3.12 pychrono=9.0.1 numpy
    /opt/mm/chrono/bin/python scripts/chrono_wheel_slope.py            # full sweep and checks
    /opt/mm/chrono/bin/python scripts/chrono_wheel_slope.py --quick    # three slopes, for a smoke test

SIMULATED BY ME with an independent simulator.  Wheel dimensions and soil parameter sets are PUBLISHED (rows named
below); the smooth wheel, the rig, the speed and the SCM elastic and damping constants are ASSUMPTIONS.
Outputs: results/chrono_scm/sweep.csv, checks.csv, run_log.txt.  Deterministic (no random numbers).
"""
from __future__ import annotations
import argparse, csv, math, os, platform, time

import pychrono as chrono
import pychrono.vehicle as veh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "chrono_scm")
G = 9.81
WHEELS = {  # name: radius m, width m, load N, SCM grid m, source
    "W1_scarecrow_like": (0.25, 0.40, 556.0, 0.02, "Heverly et al. 2013 (FLD-HV13-5a): 50 cm diameter, 40 cm wide, 340 kg over six wheels"),
    "W2_ishigami_like": (0.055, 0.064, 29.8, 0.01, "Ishigami et al. 2009 (TM-IS09-2): radius 0.055 m, width 0.064 m, wheel load 29.8 N"),
}
SOILS = {  # name: Kphi, Kc, n, cohesion Pa, phi deg, Janosi K m, source
    "S1_toyoura_ishigami2007": (8.14e5, 1.37e3, 1.00, 800.0, 37.2, 0.036, "Ishigami et al. 2007 Table I (TM-IS07-1), kx at zero slip angle"),
    "S2_dem_calibrated_zhang2024": (235605.0, -4957.0, 0.883, 21.872, 21.259, 0.0062, "Zhang et al. 2024 Table 4 (SIM-005), calibrated to a DEM material"),
}
E_ELASTIC, DAMPING = 2e8, 3e4      # Chrono example defaults (ASSUMPTION)
SLOPES = [i * 2.5 for i in range(13)]
SPEED, T_END, T_SETTLE, T_AVG0, DT = 0.2, 8.0, 1.0, 2.0, 1e-3


def run(slope_deg, wheel, soil, speed=SPEED, grid=None, t_end=T_END):
    R, W, load, grid0, _ = WHEELS[wheel]
    kphi, kc, n, coh, phi, K, _ = SOILS[soil]
    grid = grid or grid0
    th = math.radians(slope_deg)
    s = chrono.ChSystemSMC()
    s.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
    s.SetGravitationalAcceleration(chrono.ChVector3d(-G * math.sin(th), 0, -G * math.cos(th)))   # uphill is +x
    ground = chrono.ChBody(); ground.SetFixed(True); s.Add(ground)
    mat = chrono.ChContactMaterialSMC()
    x0 = -1.0
    wheel_b = chrono.ChBodyEasyCylinder(chrono.ChAxis_Y, R, W, 1000, True, True, mat)
    wheel_b.SetPos(chrono.ChVector3d(x0, 0, R + 0.005)); wheel_b.SetMass(0.2 * load / G); s.Add(wheel_b)
    carrier = chrono.ChBody(); carrier.SetPos(chrono.ChVector3d(x0, 0, R + 0.005)); carrier.SetMass(0.8 * load / G)
    carrier.SetInertiaXX(chrono.ChVector3d(1, 1, 1)); s.Add(carrier)
    guide = chrono.ChLinkMateGeneric(False, True, False, True, True, True)   # free along x and z only
    guide.Initialize(ground, carrier, chrono.ChFramed(chrono.ChVector3d(x0, 0, R), chrono.QUNIT)); s.Add(guide)
    motor = chrono.ChLinkMotorRotationSpeed()
    motor.Initialize(wheel_b, carrier, chrono.ChFramed(chrono.ChVector3d(x0, 0, R + 0.005), chrono.QuatFromAngleX(-math.pi / 2)))
    fspeed = chrono.ChFunctionConst(0.0); motor.SetSpeedFunction(fspeed); s.Add(motor)
    terrain = veh.SCMTerrain(s)
    terrain.SetSoilParameters(kphi, kc, n, coh, phi, K, E_ELASTIC, DAMPING)
    terrain.Initialize(2.0 + speed * t_end * 1.2 + 4 * R, 1.0 + 2 * W, grid)
    terrain.AddActiveDomain(wheel_b, chrono.ChVector3d(0, 0, 0), chrono.ChVector3d(2 * R + 0.3, W + 0.3, 1.0))
    t, started, xs = 0.0, False, []
    t0 = time.time()
    while t < t_end:
        if not started and t >= T_SETTLE:
            fspeed.SetConstant(speed / R); started = True
        s.DoStepDynamics(DT); t += DT
        if t >= T_AVG0:
            xs.append((t, carrier.GetPos().x))
    v = (xs[-1][1] - xs[0][1]) / (xs[-1][0] - xs[0][0])
    sinkage = R + 0.005 - wheel_b.GetPos().z
    return {"slope_deg": slope_deg, "wheel": wheel, "soil": soil, "speed_m_s": speed, "grid_m": grid,
            "forward_speed_m_s": round(v, 5), "slip": round(1.0 - v / speed, 4), "entrapped": bool(1.0 - v / speed >= 0.9),
            "sinkage_m": round(sinkage, 4), "wall_s": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--quick", action="store_true"); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(OUT, "run_log.txt"), "w")
    def say(m):
        print(m, flush=True); log.write(m + "\n"); log.flush()
    say(f"stage 14 sweep started {time.strftime('%Y-%m-%d %H:%M:%S')}; pychrono {getattr(chrono, '__version__', '9.0.1')}; python {platform.python_version()}")
    slopes = [0.0, 10.0, 20.0] if a.quick else SLOPES
    rows = []
    for wheel in WHEELS:
        for soil in SOILS:
            for sl in slopes:
                r = run(sl, wheel, soil); rows.append(r)
                say(f"{wheel} {soil} {sl:5.1f} deg: slip {r['slip']:.3f} sinkage {r['sinkage_m']:.4f} m [{r['wall_s']} s]")
                if r["slip"] >= 0.995 and sl >= 10:   # no progress at all: steeper slopes are entrapped too, skip them to bound the run time
                    for sl2 in [x for x in slopes if x > sl]:
                        rows.append({"slope_deg": sl2, "wheel": wheel, "soil": soil, "speed_m_s": SPEED, "grid_m": WHEELS[wheel][3], "forward_speed_m_s": "",
                                     "slip": "", "entrapped": "not run (entrapped at a lower slope)", "sinkage_m": "", "wall_s": 0})
                    break
    with open(os.path.join(OUT, "sweep.csv" if not a.quick else "sweep_quick.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    if not a.quick:
        checks = []
        for sl in (5.0, 15.0, 25.0):
            for label, kw in (("grid 0.01 m", {"grid": 0.01}), ("speed 0.05 m/s", {"speed": 0.05, "t_end": 14.0})):
                r = run(sl, "W1_scarecrow_like", "S1_toyoura_ishigami2007", **kw); r["check"] = label; checks.append(r)
                say(f"check {label} {sl} deg: slip {r['slip']:.3f} [{r['wall_s']} s]")
        with open(os.path.join(OUT, "checks.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(checks[0])); w.writeheader(); w.writerows(checks)
    say(f"done {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
