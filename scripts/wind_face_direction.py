#!/usr/bin/env python3
"""Stage 13 (docs/PREDICTIONS.md): slip face dip direction against the resultant sand drift direction.

    PYTHONPATH=src python3 scripts/wind_face_direction.py

Wind: PUBLISHED ERA5 reanalysis, hourly 10 m wind 2015 to 2024, through the free Open-Meteo archive API
(https://archive-api.open-meteo.com, ERA5 is produced by ECMWF for the Copernicus Climate Change Service; see
docs/DATA_AND_LICENSES.md). Raw responses are cached in data/raw/wind/ (git ignored).
Faces: SIMULATED BY ME from USGS 3DEP one metre lidar (three North American sites) and Copernicus GLO 30 (areas A, B, C).
Drift potential per hour ~ U^2 (U - Ut) for U > Ut, Ut = 6.0 m/s at 10 m (ASSUMPTION, fixed in stage 13).
Outputs: results/wind_azimuth/ (face_vs_wind.csv, summary.json, run_log.txt, figures/).
"""
from __future__ import annotations
import csv, json, os, sys, time, urllib.request
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dunerover.terrain import horn_gradient  # noqa: E402
from dunerover.dem import load_tile, crop  # noqa: E402
from dunerover.study_subgrid import AREAS, TILES  # noqa: E402
import terrain_validation_lidar as TV  # noqa: E402

OUT = os.path.join(ROOT, "results", "wind_azimuth")
WIND = os.path.join(ROOT, "data", "raw", "wind")
UT = 6.0
HIT_DEG = 45.0
# window centres (lat, lon) for the wind series; lidar centres converted from the UTM window centres with pyproj (NAD83 UTM to WGS84)
CENTRES = {"WhiteSands": (32.824, -106.291), "Dumont": (35.655, -116.266), "Kelso": (34.910, -115.720),
           "A_south_Liwa": (23.095, 53.75), "B_RubAlKhali_megadunes": (22.35, 54.40), "C_RubAlKhali_linear": (20.475, 52.50)}
PRED = {"WhiteSands": "T13-1", "Dumont": "T13-2", "Kelso": "T13-3", "A_south_Liwa": "T13-4", "B_RubAlKhali_megadunes": "T13-5", "C_RubAlKhali_linear": "T13-6"}


def fetch(site, lat, lon):
    os.makedirs(WIND, exist_ok=True)
    path = os.path.join(WIND, f"{site}_era5_2015_2024.json")
    if not os.path.exists(path):
        url = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date=2015-01-01&end_date=2024-12-31"
               "&hourly=wind_speed_10m,wind_direction_10m&models=era5&wind_speed_unit=ms&timezone=GMT")
        with urllib.request.urlopen(url, timeout=300) as r:
            open(path, "wb").write(r.read())
    return json.load(open(path)), path


def drift(d):
    u = np.array(d["hourly"]["wind_speed_10m"], dtype=float); th = np.array(d["hourly"]["wind_direction_10m"], dtype=float)
    ok = np.isfinite(u) & np.isfinite(th)
    u, th = u[ok], th[ok]
    q = np.where(u > UT, u ** 2 * (u - UT), 0.0)
    to = np.radians((th + 180.0) % 360.0)                     # direction the sand moves toward
    ve, vn = (q * np.sin(to)).sum(), (q * np.cos(to)).sum()
    rdd = (np.degrees(np.arctan2(ve, vn)) + 360) % 360
    return {"hours": int(ok.sum()), "share_hours_above_threshold": float((u > UT).mean()), "rdd_deg": float(rdd),
            "rdp_over_dp": float(np.hypot(ve, vn) / q.sum()) if q.sum() > 0 else float("nan"), "lat_used": d.get("latitude"), "lon_used": d.get("longitude")}


def circ(az_deg):
    a = np.radians(az_deg)
    s, c = np.sin(a).mean(), np.cos(a).mean()
    return float((np.degrees(np.arctan2(s, c)) + 360) % 360), float(np.hypot(s, c))


def face_azimuths_lidar(site):
    fname, win, _ = TV.SITES[site]
    z, _ = TV.load_window(fname, win)
    z = np.where(np.isnan(z), np.nanmean(z), z)
    ge, gn = horn_gradient(z, 1.0, 1.0)
    s = np.degrees(np.arctan(np.hypot(ge, gn)))
    m = s >= 28.0
    return (np.degrees(np.arctan2(-ge[m], -gn[m])) + 360) % 360, "one metre lidar, posts at 28 deg or steeper"


def face_azimuths_cop(area):
    tk, la0, la1, lo0, lo1 = AREAS[area][:5]
    dem = crop(load_tile(os.path.join(ROOT, "data", "raw", TILES[tk])), la0, la1, lo0, lo1)
    z = np.nan_to_num(dem.z, nan=np.nanmean(dem.z))
    ge, gn = horn_gradient(z, dem.dx, dem.dy)
    s = np.degrees(np.arctan(np.hypot(ge, gn)))
    m = s >= 15.0
    return (np.degrees(np.arctan2(-ge[m], -gn[m])) + 360) % 360, "Copernicus GLO 30, posts at 15 deg or steeper"


def main():
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    log = open(os.path.join(OUT, "run_log.txt"), "w")
    rows = []
    for site, (lat, lon) in CENTRES.items():
        d, path = fetch(site, lat, lon)
        w = drift(d)
        az, how = face_azimuths_lidar(site) if site in TV.SITES else face_azimuths_cop(site)
        mean_az, R = circ(az)
        diff = abs((mean_az - w["rdd_deg"] + 180) % 360 - 180)
        hist, edges = np.histogram(az, bins=36, range=(0, 360))
        rows.append({"site": site, "prediction": PRED[site], "face_source": how, "face_posts": int(az.size), "face_mean_dip_azimuth_deg": round(mean_az, 1),
                     "face_resultant_length_R": round(R, 3), "rdd_deg": round(w["rdd_deg"], 1), "rdp_over_dp": round(w["rdp_over_dp"], 3),
                     "share_hours_above_threshold": round(w["share_hours_above_threshold"], 4), "angular_difference_deg": round(diff, 1),
                     "hit": bool(diff <= HIT_DEG), "wind_hours": w["hours"], "era5_grid_lat": w["lat_used"], "era5_grid_lon": w["lon_used"],
                     "face_modal_10deg_bin_deg": float(edges[np.argmax(hist)] + 5)})
        msg = f"{site}: faces {az.size} mean dip {mean_az:.0f} deg (R {R:.2f}), RDD {w['rdd_deg']:.0f} deg (RDP/DP {w['rdp_over_dp']:.2f}), difference {diff:.0f} deg"
        print(msg, flush=True); log.write(msg + "\n")
        rows[-1]["_az"] = az
    # rose figure
    fig, axes = plt.subplots(2, 3, subplot_kw={"projection": "polar"}, figsize=(10, 7), facecolor="#fffafb")
    for ax, r in zip(axes.ravel(), rows):
        ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
        h, e = np.histogram(r["_az"], bins=36, range=(0, 360))
        ax.bar(np.radians(e[:-1] + 5), h / h.max(), width=np.radians(10), color="#e8a5bb", edgecolor="#c9769a", lw=0.4)
        ax.plot([np.radians(r["rdd_deg"])] * 2, [0, 1.05], color="#5b3a78", lw=2.2)
        ax.plot([np.radians(r["face_mean_dip_azimuth_deg"])] * 2, [0, r["face_resultant_length_R"] * 1.05], color="#a8325e", lw=2.2)
        ax.set_yticks([]); ax.set_title(f"{r['site']}\nhit: {'yes' if r['hit'] else 'no'}, difference {r['angular_difference_deg']:.0f} deg", fontsize=8.5, color="#2b2024")
    fig.text(0.01, 0.01, "Pink: face dip azimuth histogram. Plum line: resultant sand drift direction (ERA5 2015 to 2024, Ut 6 m/s). Wine line: mean face dip, length = R.\n"
             "Faces SIMULATED BY ME from PUBLISHED elevation data; wind PUBLISHED reanalysis.", fontsize=7.5, color="#2b2024")
    fig.savefig(os.path.join(OUT, "figures", "fig_face_vs_wind.png"), dpi=130, bbox_inches="tight")
    for r in rows: r.pop("_az")
    with open(os.path.join(OUT, "face_vs_wind.csv"), "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
    json.dump({"ut_m_s": UT, "hit_deg": HIT_DEG, "hits": sum(r["hit"] for r in rows), "sites": len(rows),
               "retrieved": time.strftime("%Y-%m-%d")}, open(os.path.join(OUT, "summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
