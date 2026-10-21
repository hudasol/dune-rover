#!/usr/bin/env python3
"""Pick the random third of the phase 4 curves that a separate verifier digitises again (seed 20261021), and compare
the two readings once the verifier's specification files exist.

    python3 scripts/select_redigitise.py select    # writes research/phase4/redigitise_sample.csv
    python3 scripts/select_redigitise.py compare   # writes research/phase4/redigitise_agreement.csv
"""
from __future__ import annotations
import csv, glob, json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P4 = os.path.join(ROOT, "research", "phase4")
SEED = 20261021
BRIEF_KEYS = ("source_key", "source_title", "source_url", "figure_or_table", "page", "x_name", "x_unit", "y_name", "y_unit", "vehicle", "soil")


def select():
    specs = sorted(glob.glob(os.path.join(P4, "digitise", "*.json")) + glob.glob(os.path.join(P4, "tabulated", "*.json")))
    ids = [os.path.splitext(os.path.basename(s))[0] for s in specs]
    rng = np.random.default_rng(SEED)
    k = int(np.ceil(len(ids) / 3))
    pick = sorted(rng.choice(len(ids), size=k, replace=False).tolist())
    rows = []
    for i in pick:
        sp = json.load(open(specs[i]))
        rows.append({"curve_id": ids[i], "pdf": sp.get("pdf", ""), "pdf_page": sp.get("page", ""), **{k_: sp["meta"].get(k_, "") for k_ in BRIEF_KEYS}})
    with open(os.path.join(P4, "redigitise_sample.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"{k} of {len(ids)} curves selected")


def compare():
    import importlib.util
    spec = importlib.util.spec_from_file_location("dg", os.path.join(ROOT, "scripts", "digitise_figures.py"))
    dg = importlib.util.module_from_spec(spec); spec.loader.exec_module(dg)
    dg.FIG_DIR = os.path.join(ROOT, "research", "sources", "phase4", "figures")
    out = []
    for r in csv.DictReader(open(os.path.join(P4, "redigitise_sample.csv"))):
        cid = r["curve_id"]
        a = json.load(open(os.path.join(P4, "digitise", cid + ".json")))
        vp = os.path.join(P4, "verify_digitise", cid + ".json")
        if not os.path.exists(vp):
            out.append({"curve_id": cid, "status": "not redigitised"}); continue
        b = json.load(open(vp))
        pa, pb = dg.digitise_figure(a), dg.digitise_figure(b)
        xa, ya = np.array([float(p["x"]) for p in pa]), np.array([float(p["y"]) for p in pa])
        xb, yb = np.array([float(p["x"]) for p in pb]), np.array([float(p["y"]) for p in pb])
        scale = 100.0 if a["meta"].get("y_unit") == "percent" else 1.0
        # match every point of reading A to the nearest point of reading B in x (within 1 deg)
        dx, dy, matched = [], [], 0
        for x, y in zip(xa, ya):
            j = int(np.argmin(np.abs(xb - x))) if len(xb) else -1
            if j >= 0 and abs(xb[j] - x) <= 1.0:
                matched += 1; dx.append(xb[j] - x); dy.append((yb[j] - y) / scale)
        out.append({"curve_id": cid, "status": "compared", "points_original": len(pa), "points_verifier": len(pb), "matched_within_1deg": matched,
                    "median_abs_dx_deg": round(float(np.median(np.abs(dx))), 3) if dx else "",
                    "median_abs_dslip_ratio": round(float(np.median(np.abs(dy))), 4) if dy else "",
                    "max_abs_dslip_ratio": round(float(np.max(np.abs(dy))), 4) if dy else ""})
    with open(os.path.join(P4, "redigitise_agreement.csv"), "w", newline="") as fh:
        keys = list(dict.fromkeys(k for r in out for k in r))
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(out)
    for r in out:
        print(r)


if __name__ == "__main__":
    {"select": select, "compare": compare}[sys.argv[1]]()
