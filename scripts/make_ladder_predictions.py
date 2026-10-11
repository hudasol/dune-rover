#!/usr/bin/env python3
"""Write the dated, pre-data slope ladder predictions.  SIMULATED-BY-ME; PLANNED field protocol; no field data used.

Two blocks per slope:
  (1) prior predictive slip from the assumption ranges alone (what to expect before any calibration), with the friction
      angle unknown (28 to 38 deg) and measured (33 plus or minus 2 deg, a placeholder for the soil test);
  (2) the error band of the pre-registered protocol (calibrate on 0, 5, 10 deg runs, predict 15, 20, 25 deg), from
      synthetic truths drawn from the prior with noise sigma 0.06 (an assumption until the pilot measures it).
This is a prediction of the MODEL under stated assumptions, not of any real vehicle.  After the 0, 5 and 10 degree runs, run
`python3 scripts/make_ladder_predictions.py --calibrate runs.csv` to write the post calibration file BEFORE the steep runs.
"""
import argparse, csv, datetime, json, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dunerover import fieldanalysis as FA

ap = argparse.ArgumentParser(); ap.add_argument("--date", default=None); ap.add_argument("--calibrate", default=None)
a = ap.parse_args()
date = a.date or datetime.date.today().isoformat()
outdir = os.path.join(ROOT, "docs", "predictions"); os.makedirs(outdir, exist_ok=True)

if a.calibrate:       # post calibration predictions from real data (written before the steep runs)
    d = FA.load_runs(a.calibrate)
    s = FA.observed_slip(d); cal = (d["slope_deg"] <= FA.CALIB_MAX_DEG) & ~d["entrapped"]
    phi = float(np.median(d["phi_deg"]))
    f_r, i0 = FA.calibrate(d["slope_deg"][cal], s[cal], phi)
    sig, src = FA.pilot_sigma(d); tol = FA.tolerance_from_pilot(sig)
    rows = [{"slope_deg": th, "predicted_slip": float(FA.model_slip(th, f_r, i0, phi)), "interval_lo": max(float(FA.model_slip(th, f_r, i0, phi)) - tol, -0.05),
             "interval_hi": min(float(FA.model_slip(th, f_r, i0, phi)) + tol, 1.0), "interval_meaning": "predicted slip plus or minus the pre-registered tolerance (3 x pilot sigma)",
             "f_r_fit": f_r, "i0_fit": i0, "phi_deg_used": phi, "tolerance": tol, "sigma_pilot": sig, "date": date} for th in (15, 20, 25)]
    fn = os.path.join(outdir, f"slope_ladder_post_calibration_{date}.csv")
    with open(fn, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("wrote", fn); sys.exit(0)

unk, ent_unk = FA.prior_predictive(phi_range=(28.0, 38.0))
kn, ent_kn = FA.prior_predictive(phi_range=(31.0, 35.0), seed=20261019)
band = FA.protocol_error_band(phi_known=True)
rows = []
for th in FA.LADDER:
    r = {"slope_deg": th, "role": "calibration" if th <= 10 else "held out prediction",
         "prior_p05_phi_unknown": unk[th][0], "prior_p50_phi_unknown": unk[th][1], "prior_p95_phi_unknown": unk[th][2], "prior_P_entrapment_phi_unknown": unk[th][3],
         "prior_p05_phi_33pm2": kn[th][0], "prior_p50_phi_33pm2": kn[th][1], "prior_p95_phi_33pm2": kn[th][2], "prior_P_entrapment_phi_33pm2": kn[th][3]}
    if th in band:
        r.update({"protocol_error_p05_sigma0.06": band[th][0], "protocol_error_p50_sigma0.06": band[th][1], "protocol_error_p95_sigma0.06": band[th][2], "protocol_synthetic_n": band[th][3]})
    rows.append(r)
fn = os.path.join(outdir, f"slope_ladder_predictions_{date}.csv")
keys = []
for r in rows:
    for k in r:
        if k not in keys: keys.append(k)
with open(fn, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
summ = {"date": date, "label": "SIMULATED-BY-ME prior predictions of the slip model; PLANNED field ladder; no field data exist",
        "entrapment_slope_deg_phi_unknown": {"p05": float(np.nanpercentile(ent_unk, 5)), "p50": float(np.nanmedian(ent_unk)), "p95": float(np.nanpercentile(ent_unk, 95)), "share_no_entrapment_below_45deg": float(np.mean(np.isnan(ent_unk)))},
        "entrapment_slope_deg_phi_33pm2": {"p05": float(np.nanpercentile(ent_kn, 5)), "p50": float(np.nanmedian(ent_kn)), "p95": float(np.nanpercentile(ent_kn, 95))},
        "seeds": {"prior_unknown_phi": 20261017, "prior_known_phi": 20261019, "protocol_band": 20261018}}
json.dump(summ, open(os.path.join(outdir, f"slope_ladder_predictions_{date}.json"), "w"), indent=1)
print(json.dumps(summ, indent=1)); print("wrote", fn)
