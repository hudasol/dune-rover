#!/usr/bin/env python3
"""Reduced particle (DEM) attempt on the CPU of this machine (W5 of docs/PLAN_2026-10-21.md): time one step of a
single wheel on a small bed of spheres in Project Chrono (pychrono 9.0.1, ChSystemSMC) and extrapolate to one slope run.
Hard limit: 200 steps or 5 minutes. SIMULATED BY ME; this measures cost, not slip.

    /opt/mm/chrono/bin/python scripts/chrono_dem_cpu_timing.py
"""
import json, os, time
import pychrono as chrono

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R_GRAIN, NX, NY, NZ = 0.01, 40, 10, 4          # 1600 spheres of 10 mm radius (sand grains are about 0.2 mm)
DT, STEPS, LIMIT_S = 1e-4, 200, 300.0
s = chrono.ChSystemSMC()
s.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
s.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))
mat = chrono.ChContactMaterialSMC(); mat.SetFriction(0.6); mat.SetYoungModulus(1e7)
box = chrono.ChBodyEasyBox(1.0, 0.25, 0.02, 1000, True, True, mat); box.SetFixed(True); box.SetPos(chrono.ChVector3d(0, 0, -0.01)); s.Add(box)
n = 0
for i in range(NX):
    for j in range(NY):
        for k in range(NZ):
            b = chrono.ChBodyEasySphere(R_GRAIN, 2600, True, True, mat)
            b.SetPos(chrono.ChVector3d(-0.4 + i * 2.05 * R_GRAIN, -0.1 + j * 2.05 * R_GRAIN, R_GRAIN + k * 2.05 * R_GRAIN)); s.Add(b); n += 1
wheel = chrono.ChBodyEasyCylinder(chrono.ChAxis_Y, 0.1, 0.08, 1000, True, True, mat); wheel.SetPos(chrono.ChVector3d(-0.3, 0, 0.2)); s.Add(wheel)
t0 = time.time(); done = 0
while done < STEPS and time.time() - t0 < LIMIT_S:
    s.DoStepDynamics(DT); done += 1
wall = time.time() - t0
per = wall / done
res = {"label": "SIMULATED BY ME: CPU cost of a reduced DEM wheel case, not a slip result", "spheres": n, "grain_radius_m": R_GRAIN, "dt_s": DT,
       "steps_done": done, "wall_s": round(wall, 1), "ms_per_step": round(1000 * per, 1),
       "hours_for_one_4s_slope_run": round(4.0 / DT * per / 3600, 2),
       "note": "a sand like bed would need far smaller grains (millions of particles); the GPU notebook notebooks/chrono_dem_gpu.ipynb is the route"}
os.makedirs(os.path.join(ROOT, "results", "chrono_dem"), exist_ok=True)
json.dump(res, open(os.path.join(ROOT, "results", "chrono_dem", "cpu_timing.json"), "w"), indent=1)
print(json.dumps(res))
