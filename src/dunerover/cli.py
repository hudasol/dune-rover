"""Command line of the Dune Rover Planner.  SIMULATION ONLY.

    dunerover plan DEM.tif [--posting 10] [--vehicle assumed|published-posterior|profile.json]
                   [--start LON,LAT --goal LON,LAT | --start-rc R,C --goal-rc R,C] [--policy all]
                   [--window XMIN,XMAX,YMIN,YMAX] [--coarsen K] [--out folder]
    dunerover assess DEM.tif [same options, no route]
    dunerover vehicle calibrate RUNS.csv --name my-rover --out my-rover.json
    dunerover vehicle show assumed|published-posterior|profile.json
    dunerover demo [--out folder]

(Without installing: PYTHONPATH=src python3 -m dunerover.cli ...)  Outputs in --out: report.html (open in a browser),
map.png, classes.tif (GeoTIFF class map), routes.geojson (routes in WGS84 when the input has a reference system) and
summary.json.  Every output carries the label SIMULATED BY ME and the resolution gate.
"""
from __future__ import annotations
import argparse, json, os, sys

import numpy as np

from . import planner as P


def _pair(s, kind=float):
    a, b = (kind(x) for x in s.split(","))
    return a, b


def _profile(name):
    if name in P.BUILTIN_PROFILES:
        return P.builtin_profile(name)
    if os.path.exists(name):
        return P.VehicleProfile.load(name)
    raise SystemExit(f"vehicle profile {name!r} is neither a built in profile {P.BUILTIN_PROFILES} nor a file")


def _load(args):
    r = P.read_raster(args.dem)
    if args.window:
        x0, x1, y0, y1 = (float(v) for v in args.window.split(","))
        r = P.crop_map(r, x0, x1, y0, y1)
    if args.coarsen and args.coarsen > 1:
        r = P.coarsen_raster(r, args.coarsen)
    return r


def _points(args, a):
    if args.start and args.goal:
        s, g = _pair(args.start), _pair(args.goal)
        return {"lon": s[0], "lat": s[1]} if (a.raster.geographic or a.raster.epsg) else {"x": s[0], "y": s[1]}, \
               {"lon": g[0], "lat": g[1]} if (a.raster.geographic or a.raster.epsg) else {"x": g[0], "y": g[1]}
    if args.start_rc and args.goal_rc:
        return _pair(args.start_rc, int), _pair(args.goal_rc, int)
    return None, None


def cmd_assess(args, with_route=False):
    from .report import write_outputs
    r = _load(args)
    a = P.assess(r, args.posting, _profile(args.vehicle), n_draws=args.draws, seed=args.seed)
    routes = []
    if with_route:
        s, g = _points(args, a)
        if s is None:
            raise SystemExit("give --start and --goal (longitude,latitude, or map x,y without a reference system) or --start-rc and --goal-rc")
        pols = P.POLICIES if args.policy == "all" else (args.policy,)
        routes = [P.plan(a, s, g, p) for p in pols]
    summ = write_outputs(a, routes, args.out, args.title)
    print(f"{a.gate['status']}: {a.gate['message']}")
    print("class shares:", ", ".join(f"{k} {100 * v:.1f} %" for k, v in summ["class_shares"].items()))
    for rp in routes:
        print(f"route {rp.policy}: " + (f"{rp.metrics['length_m']:.0f} m, {rp.metrics['cells_unknown']} UNKNOWN cells" if rp.reachable else rp.metrics["reason"]))
    print(f"outputs in {args.out}: report.html, map.png, classes.tif, summary.json" + (", routes.geojson" if routes else ""))


def cmd_vehicle(args):
    if args.action == "show":
        print(json.dumps(_profile(args.target).to_dict(), indent=1)); return
    from . import fieldanalysis as FA
    d = FA.load_runs(args.target)
    prof = P.profile_from_runs(d, name=args.name)
    out = args.out or f"{args.name}.json"
    prof.save(out)
    print(f"wrote {out}: f_r {prof.nominal['f_r']:.3f} ({prof.ranges['f_r'][0]:.3f} to {prof.ranges['f_r'][1]:.3f}), "
          f"i0 {prof.nominal['i0']:.3f} ({prof.ranges['i0'][0]:.3f} to {prof.ranges['i0'][1]:.3f}), friction angle {prof.nominal['phi_deg']:.1f} deg; "
          f"nominal climbing limit {prof.critical_uphill_deg():.1f} deg")


def synthetic_dunes(n: int = 400, posting: float = 2.0, seed: int = 20261023) -> np.ndarray:
    """A SYNTHETIC transverse dune field (asymmetric ridges with a 32 degree lee face), used only when no lidar is fetched."""
    rng = np.random.default_rng(seed)
    x = np.arange(n) * posting
    y = np.arange(n) * posting
    X, Y = np.meshgrid(x, y)
    lam, H = 160.0, 14.0
    phase = (X + 25.0 * np.sin(2 * np.pi * Y / 700.0) + rng.uniform(0, lam)) % lam
    stoss = lam * 0.8
    tl = np.tan(np.radians(32.0))
    z = np.where(phase < stoss, H * phase / stoss, np.maximum(H - (phase - stoss) * tl, 0.0))
    return z + 0.3 * rng.standard_normal(z.shape)


def cmd_demo(args):
    """Kelso Dunes lidar (if fetched with scripts/fetch_lidar.sh) or a synthetic dune field: the same ground assessed at 10 m
    and at 30 m, with the three policies between the same two points."""
    from .report import write_outputs
    tile = os.path.join(os.getcwd(), "data", "raw", "lidar", "USGS_1M_11_x61y387_CA_FEMAR9Southeast_D24.tif")
    if os.path.exists(tile):
        base = P.crop_map(P.read_raster(tile), 615000, 618600, 3862400, 3865100)
        label = "Kelso Dunes lidar (USGS 3DEP, PUBLISHED)"
    else:
        base = P.raster_from_array(synthetic_dunes(), 2.0, "SYNTHETIC dune field")
        label = "SYNTHETIC dune field (lidar not fetched)"
    for k_m in (10, 30):
        r = P.coarsen_raster(base, int(round(k_m / base.dx_m)))
        a = P.assess(r, profile=_profile(args.vehicle), n_draws=args.draws, seed=args.seed)
        nr, nc = a.classes.shape
        s, g = (nr // 2, 2), (nr // 2, nc - 3)
        routes = [P.plan(a, s, g, p) for p in P.POLICIES]
        out = os.path.join(args.out, f"{k_m}m")
        write_outputs(a, routes, out, f"Demo: {label}, as a {k_m} m map")
        print(f"{k_m} m: {a.gate['status']}; report in {out}/report.html")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="dunerover", description="Dune Rover Planner (SIMULATION ONLY): slip face risk, three class map and routes on dune terrain")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "assess"):
        p = sub.add_parser(name)
        p.add_argument("dem"); p.add_argument("--posting", type=float, default=None, help="analysis posting in metres (an integer multiple of the input)")
        p.add_argument("--vehicle", default="assumed"); p.add_argument("--window", default="", help="xmin,xmax,ymin,ymax in map units")
        p.add_argument("--coarsen", type=int, default=0, help="block mean the input by this factor first (what a coarser model would hold)")
        p.add_argument("--draws", type=int, default=128); p.add_argument("--seed", type=int, default=20261023)
        p.add_argument("--out", default="dunerover_out"); p.add_argument("--title", default="Dune Rover Planner report")
        if name == "plan":
            p.add_argument("--start"); p.add_argument("--goal"); p.add_argument("--start-rc"); p.add_argument("--goal-rc")
            p.add_argument("--policy", default="all", choices=("all",) + P.POLICIES)
    v = sub.add_parser("vehicle"); v.add_argument("action", choices=("calibrate", "show")); v.add_argument("target")
    v.add_argument("--name", default="field-calibrated"); v.add_argument("--out", default="")
    d = sub.add_parser("demo"); d.add_argument("--out", default="dunerover_demo"); d.add_argument("--vehicle", default="assumed")
    d.add_argument("--draws", type=int, default=128); d.add_argument("--seed", type=int, default=20261023)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "plan":
            cmd_assess(args, True)
        elif args.cmd == "assess":
            cmd_assess(args, False)
        elif args.cmd == "vehicle":
            cmd_vehicle(args)
        else:
            cmd_demo(args)
    except ValueError as exc:
        raise SystemExit(f"error: {exc}")


if __name__ == "__main__":
    main()
