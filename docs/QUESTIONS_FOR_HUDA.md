# Questions for Huda

Each item states the exact decision, file or access needed. Nothing below blocks the work done overnight; each was logged and work continued.

1. **Slip scale range (simulation parameter, your decision).** Ishigami 2009 Table I gives a shear deformation modulus kx = 0.07 m for Toyoura sand with a 5.5 cm wheel. Under the model's definition (i0 = K / contact length) that implies i0 of at least 0.81, while the assumed range in `src/dunerover/slipmodel.py` is 0.05 to 0.40. Both anchors (report section 8.8) show the model predicting too little slip on sand slopes. Do you want the i0 range (and possibly the f_r range) widened and the phase 1 and phase 2 studies re run with a new dated prediction set? Answer yes or no; nothing was changed overnight.
2. **FLD-HV13-5 validation type.** The verifier found the row mixes JPL Marsyard results (lab) and the Tecopa result (field). I set the value to `lab and field`. Would you rather split it into two rows (one lab, one field)? Answer: keep, or split.
3. **Second human spot check.** Please check at least three of the 26 supplementary rows yourself against the PDFs (suggested: FLD-HV13-1, TM-IS09-3, TM-TK5), using `research/spot_check_2_worksheet.md` as the format, and record the result in a new file `research/spot_check_3.md`.
