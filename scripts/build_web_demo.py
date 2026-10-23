#!/usr/bin/env python3
"""Build the interactive web demo of the Dune Rover Planner (demo/web/dune_rover_planner.html) from the fetched lidar.

    PYTHONPATH=src python3 scripts/build_web_demo.py

For four North American dune fields (USGS 3DEP one metre lidar, PUBLISHED, public domain), the planner assesses the same
ground as a 10 m and as a 30 m elevation model (block means of the lidar), and plans one route between two gentle low
cells with each policy. The faces the map should have flagged come from the one metre lidar (at least 10 square metres of
slope at 28 degrees or more in a cell, the truth rule of stage 12). The slip panel shows the slip model bands of the two
built in vehicle profiles beside the PUBLISHED Dumont Dunes field points.

This is a demonstration of the product, SIMULATED BY ME on PUBLISHED data. It is not a registered test: the registered
tests are stages 12, 17 and 20 of docs/PREDICTIONS.md (their numbers differ slightly, because the product uses 128
mobile parameter draws and its own seed). Outputs: demo/web/dune_rover_planner.html and results/planner_demo/metrics.json.
"""
from __future__ import annotations
import base64, csv, io, json, os, sys, time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover import planner as P  # noqa: E402
from dunerover import traverse as TR  # noqa: E402
from dunerover.terrain import hillshade  # noqa: E402
from dunerover.slipmodel import slip  # noqa: E402

LIDAR = os.path.join(ROOT, "data", "raw", "lidar")
SITES = {
    "Kelso": ("Kelso Dunes, California", "USGS_1M_11_x61y387_CA_FEMAR9Southeast_D24.tif", (615000, 618600, 3862400, 3865100)),
    "WhiteSands": ("White Sands, New Mexico", "USGS_1M_13_x37y364_NM_WhiteSandsNM_2020_D20.tif", (378400, 379900, 3630400, 3634600)),
    "Algodones": ("Algodones Dunes, California", "USGS_1M_11_x67y365_CA_SaltonSea_EarthMRI_2021_D21.tif", (675500, 679500, 3641500, 3646500)),
    "GreatSandDunes": ("Great Sand Dunes, Colorado", "USGS_1M_13_x45y418_CO_SanLuisJuanMiguel_2020_D20.tif", (450000, 454000, 4176300, 4180000)),
}
POSTINGS = (10, 30)
CLASS_RGBA = {0: (169, 205, 189, 150), 1: (122, 31, 69, 220), 2: (169, 143, 209, 200), 3: (238, 122, 168, 200), 4: (91, 58, 120, 220)}
SEED_OD = 20261023
OUT_HTML = os.path.join(ROOT, "demo", "web", "dune_rover_planner.html")
TEMPLATE = os.path.join(ROOT, "demo", "web", "template.html")
OUT_JSON = os.path.join(ROOT, "results", "planner_demo", "metrics.json")


def png(rgba: np.ndarray) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    buf = io.BytesIO()
    plt.imsave(buf, rgba, format="png")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def hill_png(z, dx, dy):
    hs = hillshade(z, dx, dy)
    base = np.array([251, 243, 246]) / 255.0          # pearl
    ink = np.array([91, 58, 120]) / 255.0             # plum
    rgb = base[None, None, :] * (0.55 + 0.45 * hs[..., None]) + ink[None, None, :] * (0.25 * (1 - hs[..., None]))
    return png(np.clip(np.dstack([rgb, np.ones(hs.shape)]), 0, 1))


def class_png(cls):
    rgba = np.zeros(cls.shape + (4,))
    for k, c in CLASS_RGBA.items():
        rgba[cls == k] = np.array(c) / 255.0
    return png(rgba)


def truth_png(truth):
    """True faces drawn in ink at 5 m, so the overlay never hides the class map and never looks like a class."""
    rgba = np.zeros(truth.shape + (4,))
    rgba[truth.astype(bool)] = (0.10, 0.06, 0.08, 0.78)
    return png(rgba)


def slip_bands():
    slopes = np.round(np.arange(0.0, 30.01, 0.5), 2)
    out = {"slopes": slopes.tolist(), "profiles": {}}
    for name in P.BUILTIN_PROFILES:
        prof = P.builtin_profile(name)
        S = np.array([np.minimum(slip(np.tan(np.radians(slopes)), 0.0, p), 1.0) for p in prof.draws(256, SEED_OD)])
        nom = np.minimum(slip(np.tan(np.radians(slopes)), 0.0, prof.nominal_params()), 1.0)
        out["profiles"][name] = {"label": prof.label, "p5": np.percentile(S, 5, axis=0).round(4).tolist(),
                                 "p50": np.percentile(S, 50, axis=0).round(4).tolist(), "p95": np.percentile(S, 95, axis=0).round(4).tolist(),
                                 "nominal": nom.round(4).tolist(), "critical_uphill_deg": round(prof.critical_uphill_deg(), 2)}
    pts = []
    with open(os.path.join(ROOT, "research", "phase3", "curves.csv"), newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["curve_id"] == "heverly2013_fig12_scarecrow_dumont":
                pts.append([round(float(r["x"]), 2), round(float(r["y"]) / 100.0, 4), round(float(r["y_unc"]) / 100.0, 4)])
    out["dumont"] = {"label": "PUBLISHED: Heverly et al. 2013, Figure 12, Scarecrow test rover (340 kg) on Dumont Dunes (FLD-HV13-1, FLD-HV13-2); digitised",
                     "points": pts}
    return out


def main():
    t0 = time.time()
    data = {"generated": time.strftime("%Y-%m-%d"), "sites": {}, "slip": slip_bands(), "card": P.load_evidence_card()}
    metrics = {"label": "SIMULATED BY ME on PUBLISHED USGS 3DEP lidar; a product demonstration, not a registered test", "sites": {}}
    for key, (title, tile, win) in SITES.items():
        path = os.path.join(LIDAR, tile)
        if not os.path.exists(path):
            print(f"{key}: lidar not fetched ({tile}); run scripts/fetch_lidar.sh"); continue
        base = P.crop_map(P.read_raster(path), *win)
        site = {"title": title, "tile": tile, "window_utm": list(win), "postings": {}}
        msite = {}
        a30 = P.assess(P.coarsen_raster(base, 30))
        truth5 = P.assess(base, 5, n_draws=8).face_prob > 0.5          # display layer: faces resolved from the lidar, at 5 m
        truth5_png = truth_png(truth5)
        (s30, g30), = TR.select_od_pairs(a30.dem, 1, SEED_OD, min_sep_m=0.55 * max(a30.dem.dx * a30.classes.shape[1], a30.dem.dy * a30.classes.shape[0]))
        for k in POSTINGS:
            a = a30 if k == 30 else P.assess(P.coarsen_raster(base, k))
            truth = P.assess(base, k, n_draws=8).face_prob > 0.5      # faces resolved from the one metre lidar (draws unused here)
            nr, nc = min(a.classes.shape[0], truth.shape[0]), min(a.classes.shape[1], truth.shape[1])
            cls, tr = a.classes[:nr, :nc], truth[:nr, :nc]
            f = 30 // k
            s, g = (s30[0] * f + f // 2, s30[1] * f + f // 2), (g30[0] * f + f // 2, g30[1] * f + f // 2)
            routes = []
            for pol in P.POLICIES:
                rp = P.plan(a, s, g, pol)
                r = {"policy": pol, "reachable": rp.reachable, **{m: rp.metrics.get(m) for m in ("length_m", "cells_unknown", "cells_face_risk", "max_uphill_grade_deg")}}
                if rp.reachable:
                    rc = rp.rc[(rp.rc[:, 0] < nr) & (rp.rc[:, 1] < nc)]
                    r["faces_crossed"] = int(tr[rc[:, 0], rc[:, 1]].sum())
                    r["path"] = (((rp.rc + 0.5) * k).round(1)).tolist()
                routes.append(r)
            sh = a.shares()
            met = {"gate": a.gate["status"], "cells": [int(nr), int(nc)],
                   "miss_rate": round(float(((cls == 0) & tr).sum() / max(tr.sum(), 1)), 4),
                   "false_safe": round(float(((cls == 0) & tr).sum() / max((cls == 0).sum(), 1)), 4),
                   "face_cells": int(tr.sum()), "share_traversable": round(sh["TRAVERSABLE"], 4), "share_unknown": round(sh["UNKNOWN (total)"], 4),
                   "share_blocked": round(sh["BLOCKED"], 4),
                   "routes": [{kk: vv for kk, vv in r.items() if kk != "path"} for r in routes]}
            msite[str(k)] = met
            site["postings"][str(k)] = {**met, "routes": routes, "gate_message": a.gate["message"], "size_m": [round(nr * a.dem.dy), round(nc * a.dem.dx)],
                                        "hill": hill_png(a.dem.z[:nr, :nc], a.dem.dx, a.dem.dy), "classes": class_png(cls), "truth": truth5_png,
                                        "start": [(s[0] + 0.5) * k, (s[1] + 0.5) * k], "goal": [(g[0] + 0.5) * k, (g[1] + 0.5) * k]}
            print(f"{key} {k} m: miss {met['miss_rate']:.2f}, routes " + ", ".join(f"{r['policy']} {r.get('faces_crossed', 'none')}" for r in routes), flush=True)
        data["sites"][key] = site
        metrics["sites"][key] = msite
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=1)
    html = open(TEMPLATE, encoding="utf-8").read().replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    html = ('<!doctype html>\n<html lang="en"><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + html + "\n</html>\n")
    with open(OUT_HTML, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"wrote {OUT_HTML} ({os.path.getsize(OUT_HTML) / 1e6:.2f} MB) in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
