#!/usr/bin/env python3
"""Build manuscript/MANUSCRIPT.md (and, with --pdf, manuscript/MANUSCRIPT.pdf) from manuscript/src/manuscript.md.

    PYTHONPATH=src python3 scripts/build_manuscript.py [--pdf]

Every {{VAL:key}} is filled from scripts/build_report.values() (earlier stages) and scripts/phase3_values.values()
(2026-10-20 stages); {{TABLE:...}} and {{FIG:...}} are generated here from result files; {{REFERENCES}} lists the
sources of every evidence row id cited in the text plus the datasets and software used.  Deterministic; no network.
"""
from __future__ import annotations
import csv, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_report as BR  # noqa: E402
import phase3_values as P3  # noqa: E402

MS = os.path.join(ROOT, "manuscript")
DATE = "2026-10-21"
FAM_NAMES = {"exp_existing": "Exponential (existing model)", "bekker_wong": "Bekker Wong rigid wheel", "mohr_coulomb_ratio": "Mohr Coulomb ratio",
             "logistic_empirical": "Logistic, empirical"}
FIGS = {
    "fits": ("../results/model_validation/part_exp_existing_mohr_coulomb_ratio_logistic_empirical/figures/fig_family_fits.png",
             "Per curve best fits of three families to the published curves (points with digitisation uncertainty). A good fit shows shape capacity, not predictive skill. SIMULATED BY ME against PUBLISHED curves."),
    "chrono": ("../results/chrono_scm/figures/fig_chrono_vs_published.png",
               "Single wheel slip against slope in Project Chrono (points), the Bekker Wong family with the same wheel and soil (dashed), the existing model (dotted) and the Dumont Dunes curve (PUBLISHED, green)."),
    "lidar": ("../results/terrain_validation/figures/fig_lidar_class_maps_30m.png",
              "Three class maps at 30 m over three real dune fields; black outlines mark cells that contain a face of 28 degrees or more in the one metre lidar. SIMULATED BY ME on PUBLISHED USGS 3DEP data."),
    "routes": ("../results/planner/figures/fig_routes_30m.png", "First six routes per policy over the 30 m three class map. SIMULATED BY ME."),
    "icesat2": ("../results/icesat2/figures/fig_arabia_slope_distributions.png",
                "Absolute along track slope over the three Arabian windows: ICESat-2 10 m segments (solid) against the Copernicus 30 m surface on the same tracks (dashed); the dotted line marks 28 degrees. PUBLISHED data, SIMULATED BY ME scoring; the ICESat-2 method failed its own lidar validation."),
    "loop": ("../results/closed_loop/figures/fig_slip_estimator.png",
             "Online slip estimate from odometry against position fixes (0.3 m noise) against the true slip over the same 10 m, in the closed loop demonstration. SIMULATED BY ME; the true rover is a model."),
    "wind": ("../results/wind_azimuth/figures/fig_face_vs_wind.png",
             "Slip face dip directions (pink) against the resultant sand drift direction from ERA5 (plum) and the mean face dip (wine)."),
}
EXTERNAL = [
    "U.S. Geological Survey, 3D Elevation Program one metre DEM tiles USGS_1M_11_x56y395_CA_FEMAR9Southeast_D24, USGS_1M_13_x37y364_NM_WhiteSandsNM_2020_D20, USGS_1M_11_x61y387_CA_FEMAR9Southeast_D24 (public domain), https://www.usgs.gov/3d-elevation-program, retrieved 2026-10-20.",
    "European Space Agency and Airbus, Copernicus DEM GLO-30, https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model, retrieved 2026-10-11 and 2026-10-15 (licence in docs/DATA_AND_LICENSES.md).",
    "ECMWF, ERA5 hourly reanalysis (Copernicus Climate Change Service), accessed through the Open-Meteo archive API, https://open-meteo.com (data CC BY 4.0), retrieved 2026-10-20.",
    "U.S. Geological Survey, 3D Elevation Program one metre DEM tiles USGS_1M_13_x45y418_CO_SanLuisJuanMiguel_2020_D20, USGS_1M_11_x67y365_CA_SaltonSea_EarthMRI_2021_D21, USGS_1M_12_x38y440_UT_StatewideCenSouth_2020_A20 (public domain), https://www.usgs.gov/3d-elevation-program, retrieved 2026-10-21.",
    "NASA, ICESat-2 ATL03 geolocated photon data, processed on demand into ATL06 style segments by the public SlideRule Earth service (Python client sliderule 5.6.3, BSD 3-Clause), https://slideruleearth.io, retrieved 2026-10-21 (docs/ICESAT2_GUIDE.md).",
    "Project Chrono, pychrono 9.0.1, https://projectchrono.org (BSD 3-Clause).",
    "emcee 3.1.6, affine invariant MCMC ensemble sampler (MIT licence).",
]


def t_families():
    rows = []
    for fam, label in FAM_NAMES.items():
        for part in ("part_exp_existing_mohr_coulomb_ratio_logistic_empirical", "part_bekker_wong"):
            p = os.path.join(ROOT, "results", "model_validation", part, "summary.json")
            if os.path.exists(p):
                import json
                d = json.load(open(p))["families"].get(fam)
                if d:
                    rows.append([label, d["heldout_curves"], f"{d['median_nominal_rmse']:.2f}", f"{d['median_fit_rmse']:.2f}", f"{d['median_heldout_rmse']:.2f}",
                                 f"{d['pooled_coverage90']:.2f}", "passes" if d["survives"] else "fails"])
    return ("Table 1. Model families on the published slip against slope curves (SIMULATED BY ME against PUBLISHED curves). Bar fixed before the run: median held out error at most 0.15 and coverage at least 0.80.\n\n"
            + BR.md_table(["Family", "Held out curves", "Median error, nominal", "Median error, own fit", "Median error, held out", "90 % interval coverage", "Bar"], rows))


def t_lidar():
    rows = []
    for r in BR.rd("results/terrain_validation/metrics.csv"):
        rows.append([r["site"], r["posting_m"], f"{float(r['auc']):.2f}", f"{100*float(r['true_face_rate']):.1f} %", f"{100*float(r['mean_predicted_face_probability']):.1f} %",
                     f"{100*float(r['share_traversable']):.1f} %", f"{100*float(r['face_rate_in_traversable']):.1f} %", f"{100*float(r['face_rate_in_unknown']):.1f} %",
                     f"{100*float(r['share_traversable'])*float(r['face_rate_in_traversable'])/float(r['true_face_rate']):.0f} %"])
    return ("Table 2. Slip face detector and three class map against one metre lidar truth (SIMULATED BY ME on PUBLISHED USGS 3DEP data; North American dune fields).\n\n"
            + BR.md_table(["Site", "Posting, m", "AUC", "True face rate", "Mean predicted probability", "TRAVERSABLE share", "Share of TRAVERSABLE cells with a face", "Share of UNKNOWN cells with a face", "Miss rate (face cells called TRAVERSABLE)"], rows))


LOCO_IDS = ["MOB-043", "TM3-067", "TM3-071", "FLD-HV13-1", "FLD-025", "LEG-007", "LEG-008", "LEG-009", "LEG-013"]


def t_locomotion():
    """Wheeled, tracked and legged results on sand, PUBLISHED rows only, never compared numerically across rows."""
    ev = {r["id"]: r for r in BR.rd("research/evidence.csv")}
    rows = [[i, BR.esc(ev[i]["vehicle_or_wheel"], 70), BR.esc(ev[i]["slope_deg"], 24), BR.esc(ev[i]["metric"], 80), BR.esc(ev[i]["value"] + " " + ev[i]["unit"], 60),
             ev[i]["validation_type"]] for i in LOCO_IDS if i in ev]
    return ("Wheeled, tracked and legged locomotion on sand (PUBLISHED rows only; vehicles, soils and metrics differ, so the rows are not comparable with each other).\n\n"
            + BR.md_table(["Row", "Vehicle", "Slope, deg", "Metric", "Value", "Validation"], rows))


def curve_and_law_sources():
    """Sources of the digitised curves (both rounds) and of the scaling law rows, from the curve files and the
    reference lists written when they were retrieved (research/phase4/*_references.csv)."""
    out = {}
    for r in BR.rd("research/phase3/curves.csv"):
        out.setdefault(r["source_url"].strip(), r["source_title"].strip())
    for f in ("research/phase4/curves_A_references.csv", "research/phase4/curves_B_references.csv", "research/phase4/scaling_references.csv"):
        for r in BR.rd(f):
            doi = r.get("doi", "").strip()
            url = f"https://doi.org/{doi}" if doi.startswith("10.") else r["url"].strip()   # a DOI field may hold a note such as "none"
            out.setdefault(url, r["citation"].strip())
    return out


def _same(a, b):
    wa = {w for w in re.findall(r"[a-z]{4,}", a.lower())}; wb = {w for w in re.findall(r"[a-z]{4,}", b.lower())}
    return bool(wa and wb) and len(wa & wb) >= 0.6 * min(len(wa), len(wb))


def references(text, ev):
    ids = set(re.findall(r"\b(?:FLD|TM|SIM|LRN|LEG|PLN|TM3|MOB|SND|DUN|MAP|ENV)-[A-Za-z0-9]+(?:-[0-9a-z]+)?\b", text))
    by, titles = {}, {}
    for r in ev:
        if r["id"] in ids:   # one entry per source address, so one paper recorded under two title spellings is listed once
            url = r["source_url"].strip()
            url = next((u for u, ts in titles.items() if any(_same(r["source_title"], x) for x in ts)), url)
            by.setdefault(url, []).append(r["id"]); titles.setdefault(url, set()).add(r["source_title"].strip())
    for url, title in curve_and_law_sources().items():   # skip a source already listed under another address or spelling
        if url in by or any(_same(title, x) for v in titles.values() for x in v):
            continue
        by[url] = []; titles[url] = {title}
    def label(url):
        return sorted(titles[url])[0]
    out = []
    for i, url in enumerate(sorted(by, key=lambda u: label(u).lower()), 1):
        rows = f" (rows {', '.join(sorted(by[url]))})" if by[url] else " (digitised curves or scaling law notes)"
        out.append(f"{i}. {label(url)} {url}{rows}")
    n = len(out)
    out += [f"{n + i}. {e}" for i, e in enumerate(EXTERNAL, 1)]
    out.append("")
    out.append("Groups of rows cited by prefix (PLN, TM3, MOB, SND, DUN, MAP, ENV, SCL rows) are listed with their sources in `research/evidence.csv` and in Appendix C of `docs/REPORT.md`.")
    return "\n".join(out)


def extra_values(v):
    curves = {}
    for r in BR.rd("research/phase3/curves.csv"):
        curves.setdefault(r["curve_id"], r["source_key"])
    v["dc_ncurves"] = len(curves); v["dc_nsources"] = len(set(curves.values()))
    v["dc_npoints"] = len(BR.rd("research/phase3/curves.csv"))
    import model_validation as MV
    cs = [c for c in MV.load_curves() if c["method"] != "published_fit"]
    v["mv_ncurves"] = len(cs); v["mv_nsources"] = len({c["source"] for c in cs})
    v["post_s_med"] = v.get("post_s", "n/a").split(" ")[0]
    v["build_date"] = DATE
    import benchmark_values as BV          # 2026-10-27: stages 25 and 26 (bm_ keys)
    v.update(BV.values())
    return v


def build(pdf=False):
    ev = BR.rd("research/evidence.csv")
    v = BR.values(ev); v.update(P3.values()); v = extra_values(v)
    t = open(os.path.join(MS, "src", "manuscript.md"), encoding="utf-8").read()
    t = t.replace("{{TABLE:families}}", t_families()).replace("{{TABLE:lidar}}", t_lidar()).replace("{{TABLE:locomotion}}", t_locomotion())
    for k, (path, cap) in FIGS.items():
        fig = f"![{cap}]({path})" if os.path.exists(os.path.join(MS, path)) else f"*Figure not available: {path} has not been produced.*"
        t = t.replace("{{FIG:%s}}" % k, fig)
    for k, val in v.items():
        t = t.replace("{{VAL:%s}}" % k, str(val))
    left = sorted(set(re.findall(r"\{\{VAL:[^}]*\}\}", t)))
    t = t.replace("{{REFERENCES}}", references(t, ev))
    open(os.path.join(MS, "MANUSCRIPT.md"), "w", encoding="utf-8").write(t)
    if left:
        print("UNRESOLVED (result not yet produced):", left)
    if pdf:
        import build_pdf as BP
        html = os.path.join(MS, "MANUSCRIPT.html")
        BP.to_html(t, html, "Wheeled rover slip on dune sand")
        BP.html_to_pdf(html, os.path.join(MS, "MANUSCRIPT.pdf"))
        BP.compress(os.path.join(MS, "MANUSCRIPT.pdf"))
        os.remove(html)
    return left


if __name__ == "__main__":
    left = build("--pdf" in sys.argv)
    sys.exit(1 if left and "--strict" in sys.argv else 0)
