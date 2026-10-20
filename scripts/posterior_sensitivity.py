#!/usr/bin/env python3
"""POST HOC (after the midpoint review of 2026-10-20): how much does the posterior range set depend on the Mars
curves (0.38 g, Li 2008 counted twice) and the lunar simulant curve (Scarab on GRC-1)?  Re fits the exponential family
on the Earth sand curves only (Heverly 2013 Dumont and Marsyard, Inotsume 2016 El Dorado on Toyoura sand).
Output: results/model_validation/posthoc_posterior_earth_sand.json.  SIMULATED BY ME.
"""
import json, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
import model_validation as MV  # noqa: E402
from dunerover.models import FAMILIES  # noqa: E402

fam = FAMILIES["exp_existing"]
cs = [c for c in MV.load_curves() if c["method"] != "published_fit" and c["kind"] == "direct ascent"
      and c["source"] in ("heverly2013", "inotsume2016") and "scarab" not in c["id"]]
post = MV.sample_posterior(fam, cs, MV.SEED + 11)
q = {p.name: [float(np.exp(v)) if p.log else float(v) for v in np.percentile(post[:, k], [5, 50, 95])] for k, p in enumerate(fam.params)}
q["s"] = [float(v) for v in np.percentile(post[:, -1], [5, 50, 95])]
out = {"label": "POST HOC sensitivity of the stage 15 posterior: Earth sand curves only", "curves": [c["id"] for c in cs], "quantiles_5_50_95": q}
json.dump(out, open(os.path.join(ROOT, "results", "model_validation", "posthoc_posterior_earth_sand.json"), "w"), indent=1)
print(json.dumps(q))
