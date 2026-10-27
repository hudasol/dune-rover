"""Outputs of the Dune Rover Planner: map figure, GeoTIFF class map, GeoJSON routes and a self contained HTML report.
SIMULATION ONLY: every output says so."""
from __future__ import annotations
import base64, html, io, json, os
import numpy as np

from .planner import Assessment, RoutePlan, CLASS_NAMES, load_evidence_card
from . import planner as P
from .terrain import hillshade

PINK = {"bg": "#fffafb", "pearl": "#fbf3f6", "sakura": "#e8a5bb", "rose": "#c9769a", "deep": "#a8325e", "plum": "#5b3a78",
        "sage": "#6fa28f", "ink": "#2b2024", "muted": "#7d6470"}
CLASS_COLORS = {0: "#a9cdbd", 1: "#7a1f45", 2: "#a98fd1", 3: "#ee7aa8", 4: "#5b3a78", 5: "#bdb3b8"}
ROUTE_COLORS = {"naive": "#2b2024", "conservative": "#6fa28f", "risk_weighted": "#a8325e"}


def map_figure(a: Assessment, routes: list[RoutePlan] | None = None, path: str | None = None, title: str = "") -> bytes:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6), dpi=120, facecolor=PINK["bg"])
    ext = [0, a.classes.shape[1] * a.dem.dx, a.classes.shape[0] * a.dem.dy, 0]
    hs = hillshade(a.dem.z, a.dem.dx, a.dem.dy)
    ax = axes[0]
    ax.imshow(hs, cmap="gray", extent=ext, vmin=0, vmax=1)
    ax.imshow(a.classes, cmap=ListedColormap([CLASS_COLORS[k] for k in range(6)]), vmin=-0.5, vmax=5.5, alpha=0.72, extent=ext, interpolation="nearest")
    for rp in routes or []:
        if rp.reachable:
            ax.plot((rp.rc[:, 1] + 0.5) * a.dem.dx, (rp.rc[:, 0] + 0.5) * a.dem.dy, color=ROUTE_COLORS[rp.policy], lw=2.0, label=f"route: {rp.policy.replace('_', ' ')}")
    if routes:
        s, t = routes[0].start_rc, routes[0].goal_rc
        ax.scatter([(s[1] + 0.5) * a.dem.dx, (t[1] + 0.5) * a.dem.dx], [(s[0] + 0.5) * a.dem.dy, (t[0] + 0.5) * a.dem.dy],
                   c=[PINK["deep"], PINK["plum"]], s=55, edgecolor="white", zorder=5)
    hand = [Patch(color=CLASS_COLORS[k], label=CLASS_NAMES[k]) for k in range(6) if k < 5 or (a.classes == 5).any()]
    leg = ax.legend(handles=hand + ax.get_legend_handles_labels()[0], fontsize=7, loc="lower left", framealpha=0.9)
    leg.get_frame().set_facecolor(PINK["pearl"])
    ax.set_title(f"Three class map at {a.posting_m:.0f} m ({a.gate['status']})", fontsize=10, color=PINK["ink"])
    ax.set_xlabel("m east"); ax.set_ylabel("m south")
    ax = axes[1]
    im = ax.imshow(a.face_prob, cmap="RdPu", vmin=0, vmax=1, extent=ext)
    ax.set_title("Slip face probability" + (" (resolved from the input)" if a.face_source != "detector" else " (sub grid detector)"), fontsize=10, color=PINK["ink"])
    ax.set_xlabel("m east")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    fig.suptitle((title + "  |  " if title else "") + "SIMULATED BY ME: model and assumption dependent, not field evidence", fontsize=9, color=PINK["muted"])
    fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor=fig.get_facecolor()); plt.close(fig)
    data = buf.getvalue()
    if path:
        with open(path, "wb") as fh:
            fh.write(data)
    return data


def _geotags(r) -> list:
    """GeoTIFF tags that place a grid of the analysis raster r in its reference system (empty for a local frame)."""
    extratags = []
    if r.geokeys is not None or r.geographic:
        is_area = True
        keys = r.geokeys
        if keys:
            v = list(keys)
            for i in range(1, v[3] + 1):
                if v[4 * i] == 1025 and v[4 * i + 1] == 0:
                    is_area = v[4 * i + 3] == 1
        tx, ty = (r.x0 - 0.5 * r.px, r.y0 + 0.5 * r.py) if is_area else (r.x0, r.y0)
        extratags = [(33550, "d", 3, (r.px, r.py, 0.0), False), (33922, "d", 6, (0.0, 0.0, 0.0, tx, ty, 0.0), False)]
        if keys:
            extratags.append((34735, "H", len(keys), tuple(keys), False))
            if r.geo_double:
                extratags.append((34736, "d", len(r.geo_double), tuple(r.geo_double), False))
            if r.geo_ascii:
                extratags.append((34737, "s", 0, r.geo_ascii, False))
        else:   # geographic WGS84, pixel is area
            gk = (1, 1, 0, 3, 1024, 0, 1, 2, 1025, 0, 1, 1, 2048, 0, 1, 4326)
            extratags.append((34735, "H", len(gk), gk, False))
    return extratags


def write_class_geotiff(a: Assessment, path: str) -> None:
    """The class map as a uint8 GeoTIFF with the reference system of the input (when it declares one)."""
    import tifffile
    tifffile.imwrite(path, a.classes.astype(np.uint8), extratags=_geotags(a.raster), description="dunerover three class map: "
                     + "; ".join(f"{k}={v}" for k, v in CLASS_NAMES.items()) + "; SIMULATED BY ME")


def write_float_geotiff(a: Assessment, values: np.ndarray, path: str, what: str) -> None:
    """A float32 layer (face probability, share of passable draws) on the analysis grid, georeferenced like the classes."""
    import tifffile
    tifffile.imwrite(path, np.asarray(values, dtype=np.float32), extratags=_geotags(a.raster),
                     description=f"dunerover {what}; SIMULATED BY ME")


def _img(data: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(data).decode()


def html_report(a: Assessment, routes: list[RoutePlan], fig_png: bytes, title: str = "Dune Rover Planner report") -> str:
    e = html.escape
    card = load_evidence_card()
    lid = card["lidar_tests"]
    s = a.summary()
    gate_col = {"RESOLVED": PINK["sage"], "DETECTOR": PINK["rose"], "COARSE": PINK["deep"]}[a.gate["status"]]
    rows_cls = "".join(f"<tr><td><span class=sw style='background:{CLASS_COLORS[k]}'></span>{e(CLASS_NAMES[k])}</td><td>{100 * v:.1f} %</td></tr>"
                       for k, v in zip(range(6), [s["class_shares"][CLASS_NAMES[k]] for k in range(6)]))
    prof = a.profile
    rows_prof = "".join(f"<tr><td>{k}</td><td>{prof.nominal[k]:.3g}</td><td>{prof.ranges[k][0]:.3g} to {prof.ranges[k][1]:.3g}</td></tr>" for k in ("phi_deg", "f_r", "i0", "i_max"))
    rt = ""
    for rp in routes:
        m = rp.metrics
        if rp.reachable:
            ratio = f" ({m['length_ratio']:.2f} x straight)" if m.get("length_ratio") else ""
            rt += (f"<tr><td>{e(rp.policy.replace('_', ' '))}</td><td>{m['length_m']:.0f} m{ratio}</td>"
                   f"<td>{m['max_uphill_grade_deg']:.1f} deg</td><td>{m['cells_unknown']}</td><td>{m['cells_face_risk']}</td><td>{m['max_face_probability']:.2f}</td></tr>")
        else:
            rt += f"<tr><td>{e(rp.policy.replace('_', ' '))}</td><td colspan=5>no route: {e(m.get('reason', ''))}</td></tr>"
    warns = sorted({w for rp in routes for w in rp.warnings})
    warn_html = "".join(f"<li>{e(w)}</li>" for w in warns)
    ev_rows = "".join(f"<tr><td>{p} m</td><td>{d['miss_min']} to {d['miss_max']}</td><td>{d['false_safe_min']} to {d['false_safe_max']}</td><td>{d['auc_min']} to {d['auc_max']}</td></tr>"
                      for p, d in sorted(lid["by_posting_m"].items(), key=lambda x: float(x[0])))
    sm = card["slip_models"]
    route_block = (f"<h2>Routes</h2><table><tr><th>Policy</th><th>Length</th><th>Steepest uphill grade at {a.posting_m:.0f} m</th><th>UNKNOWN cells</th>"
                   f"<th>Face risk cells</th><th>Highest face probability</th></tr>{rt}</table>"
                   f"<p class=note>Policies: naive (the slip model only), conservative (TRAVERSABLE cells only), risk weighted (avoids BLOCKED, "
                   f"cost raised by the face probability); the two cautious policies never descend a grade of 28 degrees or more. In the registered "
                   f"test on three lidar dune fields (stage 17), no policy was reliably safer than naive on 30 m maps. The nominal climbing limit of "
                   f"this profile is {prof.critical_uphill_deg():.1f} degrees; with the published posterior of other vehicles it is "
                   f"{P.builtin_profile('published-posterior').critical_uphill_deg():.1f} degrees, and the Dumont Dunes field curve of a real "
                   f"rover reaches 50 % slip at {P.DUMONT_50PCT_SLIP_DEG:g} degrees (PUBLISHED).</p>") if routes else ""
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{e(title)}</title><style>
body{{font-family:Inter,Segoe UI,Arial,sans-serif;background:{PINK['bg']};color:{PINK['ink']};margin:0;padding:24px;line-height:1.5}}
main{{max-width:1100px;margin:auto}} h1{{color:{PINK['deep']};margin:0 0 4px}} h2{{color:{PINK['plum']};margin-top:28px}}
.banner{{background:{PINK['pearl']};border:1px solid {PINK['sakura']};border-radius:10px;padding:10px 14px;font-size:14px}}
.gate{{border-left:6px solid {gate_col};background:white;border-radius:8px;padding:12px 16px;margin:14px 0}}
table{{border-collapse:collapse;background:white;border-radius:8px;overflow:hidden;font-size:14px;margin:8px 0}}
th,td{{padding:6px 10px;border-bottom:1px solid {PINK['pearl']};text-align:left}} th{{background:{PINK['pearl']};color:{PINK['plum']}}}
.sw{{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:middle}}
img{{max-width:100%;border-radius:10px;border:1px solid {PINK['sakura']}}} .note{{color:{PINK['muted']};font-size:13px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}} @media(max-width:800px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>{e(title)}</h1>
<div class=banner><b>SIMULATED BY ME</b>: model and assumption dependent, not field evidence and not a safety case. Input: <code>{e(os.path.basename(a.raster.source.split('|')[0]))}</code>,
{a.native_m:.2g} m posts, analysed at {a.posting_m:.3g} m ({a.classes.shape[0]} x {a.classes.shape[1]} cells). Vehicle profile: <b>{e(prof.name)}</b> ({e(prof.label)}).</div>
<div class=gate><b>Resolution gate: {a.gate['status']}</b><br>{e(a.gate['message'])}</div>
<img src="{_img(fig_png)}" alt="Three class map, routes and slip face probability">
{route_block}
{"<h2>Warnings</h2><ul>" + warn_html + "</ul>" if warn_html else ""}
{"<p class=note>Input: " + e(" ".join(a.raster.warnings)) + "</p>" if a.raster.warnings else ""}
<div class=grid><div><h2>Class shares</h2><table>{rows_cls}</table>
<p class=note>A cell is TRAVERSABLE when at least four of its eight headings are passable in at least 95 % of {a.n_draws} parameter draws and its slip face
probability is below {a.tau:g}; BLOCKED when passable in at most 5 % of draws; UNKNOWN otherwise.</p></div>
<div><h2>Vehicle profile</h2><table><tr><th>Parameter</th><th>Nominal</th><th>Range</th></tr>{rows_prof}</table><p class=note>{e(prof.notes)}</p></div></div>
<h2>What the evidence says about this kind of map</h2>
<table><tr><th>Posting</th><th>Face cells called TRAVERSABLE</th><th>TRAVERSABLE cells with a face</th><th>Detector AUC</th></tr>{ev_rows}</table>
<p class=note>{e(lid['what'])} {lid['n_fields']} fields. Slip models: on {sm['n_heldout_curves']} published curves from {sm['n_studies']} studies, model families
calibrated on other studies missed a held out study by {sm['three_families_heldout']} slip (bar 0.15); {e(sm['verdict'])}. Source: {e(card['label'])}.</p>
<p class=note>Generated by the dunerover planner (hudasol/dune-rover). Seed {a.seed}. All rights reserved.</p>
</main></body></html>"""


def write_outputs(a: Assessment, routes: list[RoutePlan], out: str, title: str = "Dune Rover Planner report") -> dict:
    os.makedirs(out, exist_ok=True)
    png = map_figure(a, routes, os.path.join(out, "map.png"), title)
    write_class_geotiff(a, os.path.join(out, "classes.tif"))
    write_float_geotiff(a, a.face_prob, os.path.join(out, "face_probability.tif"), "slip face probability (0 to 1)")
    write_float_geotiff(a, a.q_pass, os.path.join(out, "q_pass.tif"), "share of vehicle parameter draws for which the cell is passable")
    from . import exports as X
    X.write_nav2_map(a, out)
    summ = a.summary()
    summ["routes"] = [{"policy": rp.policy, "reachable": rp.reachable, **rp.metrics, "warnings": rp.warnings} for rp in routes]
    with open(os.path.join(out, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summ, fh, indent=1, default=float)
    if routes:
        fc = {"type": "FeatureCollection", "features": []}
        for rp in routes:
            g = rp.geojson(a); fc["crs_note"] = g["crs_note"]; fc["features"] += g["features"]
        with open(os.path.join(out, "routes.geojson"), "w", encoding="utf-8") as fh:
            json.dump(fc, fh, indent=1)
        if a.raster.geographic or a.raster.epsg:
            X.write_kml(a, routes, os.path.join(out, "routes.kml"))
            for rp in routes:
                if rp.reachable:
                    X.write_qgc_plan(a, rp, os.path.join(out, f"mission_{rp.policy}.plan"))
    with open(os.path.join(out, "report.html"), "w", encoding="utf-8") as fh:
        fh.write(html_report(a, routes, png, title))
    return summ
