"""Exports of the Dune Rover Planner for robot software: a Nav2 occupancy map (PGM and YAML), routes as KML, and a
QGroundControl mission file for ArduPilot or PX4 rovers.  SIMULATION ONLY: every file says so.

Nav2 map: TRAVERSABLE is free, BLOCKED and NO DATA are occupied, every UNKNOWN class is unknown (trinary mode), so a
robot's own costmap decides how to treat ground the map could not verify. The origin is the lower left corner of the
grid in the input's map units (metres for projected or local inputs); for geographic inputs the map is written in a
local metre frame with its origin at the lower left corner, and the YAML records the corner's longitude and latitude.
"""
from __future__ import annotations
import json, os
import numpy as np

FREE, UNKNOWN, OCCUPIED = 254, 205, 0
LABEL = "SIMULATED BY ME: model and assumption dependent, not field evidence; check every route on the ground"


def occupancy(classes: np.ndarray) -> np.ndarray:
    img = np.full(classes.shape, UNKNOWN, dtype=np.uint8)
    img[classes == 0] = FREE
    img[np.isin(classes, (1, 5))] = OCCUPIED
    return img


def write_nav2_map(a, out: str, name: str = "nav2_map") -> tuple[str, str]:
    img = occupancy(a.classes)
    nr, nc = img.shape
    pgm = os.path.join(out, name + ".pgm")
    with open(pgm, "wb") as fh:
        fh.write(f"P5\n# {LABEL}\n{nc} {nr}\n255\n".encode("ascii"))
        fh.write(img.tobytes())
    r = a.raster
    res = float(np.sqrt(a.dem.dx * a.dem.dy))
    if r.geographic:
        origin = [0.0, 0.0, 0.0]
        lon, lat = r.map_xy(nr - 0.5, -0.5)
        note = f"geographic input: local metre frame, origin at the lower left corner (longitude {float(lon):.7f}, latitude {float(lat):.7f})"
    else:
        x, y = r.map_xy(nr - 0.5, -0.5)                 # lower left corner of the lower left cell
        origin = [round(float(x), 3), round(float(y), 3), 0.0]
        note = "origin in the input's map units (metres)" + ("" if r.epsg else ", local frame without a reference system")
    yml = os.path.join(out, name + ".yaml")
    with open(yml, "w", encoding="utf-8") as fh:
        fh.write(f"# {LABEL}\n# {note}\n# free = TRAVERSABLE, occupied = BLOCKED or NO DATA, unknown = UNKNOWN (unverified ground)\n")
        fh.write(f"image: {name}.pgm\nmode: trinary\nresolution: {res:.4f}\norigin: [{origin[0]}, {origin[1]}, {origin[2]}]\n"
                 "negate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.25\n")
    return pgm, yml


def _route_lonlat(a, rp, max_points: int | None = None):
    ll = rp.lonlat(a)
    if max_points and len(ll) > max_points:
        idx = np.unique(np.linspace(0, len(ll) - 1, max_points).round().astype(int))
        ll = [ll[i] for i in idx]
    return ll


def write_kml(a, routes, path: str) -> None:
    styles = {"naive": "ff24202b", "conservative": "ff8fa26f", "risk_weighted": "ff5e32a8"}   # aabbggrr
    parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
             f"<name>Dune Rover Planner routes</name><description>{LABEL}</description>"]
    for pol, col in styles.items():
        parts.append(f'<Style id="{pol}"><LineStyle><color>{col}</color><width>3</width></LineStyle></Style>')
    for rp in routes:
        if not rp.reachable:
            continue
        coords = " ".join(f"{lon:.7f},{lat:.7f},0" for lon, lat in _route_lonlat(a, rp))
        parts.append(f"<Placemark><name>{rp.policy.replace('_', ' ')}</name><description>{rp.metrics['length_m']:.0f} m; "
                     f"{rp.metrics['cells_unknown']} UNKNOWN cells; {LABEL}</description><styleUrl>#{rp.policy}</styleUrl>"
                     f"<LineString><tessellate>1</tessellate><coordinates>{coords}</coordinates></LineString></Placemark>")
    parts.append("</Document></kml>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))


def write_qgc_plan(a, rp, path: str, max_waypoints: int = 100, cruise_speed: float = 0.5) -> dict:
    """QGroundControl .plan (mission version 2) with MAV_CMD_NAV_WAYPOINT items for a ground rover (MAV_TYPE 10)."""
    ll = _route_lonlat(a, rp, max_waypoints)
    items = [{"type": "SimpleItem", "command": 16, "frame": 3, "autoContinue": True, "doJumpId": i + 1,
              "params": [0, 0, 0, None, round(lat, 7), round(lon, 7), 0]} for i, (lon, lat) in enumerate(ll)]
    plan = {"fileType": "Plan", "version": 1, "groundStation": "QGroundControl", "comment": LABEL,
            "mission": {"version": 2, "firmwareType": 3, "vehicleType": 10, "cruiseSpeed": cruise_speed, "hoverSpeed": cruise_speed,
                        "globalPlanAltitudeMode": 1, "plannedHomePosition": [round(ll[0][1], 7), round(ll[0][0], 7), 0], "items": items},
            "geoFence": {"circles": [], "polygons": [], "version": 2}, "rallyPoints": {"points": [], "version": 2}}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(plan, fh, indent=1)
    return plan
