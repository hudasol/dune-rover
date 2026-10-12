# Spot check of five evidence rows (2026-10-12)

Rows chosen by the author. Each was compared with the source PDF supplied by the author (a local folder named "sourced evidence"), read in full text. The checker was Claude working from the author's files, so this is a fresh read of the sources but not an independent human check.

| Row | Source file | Checked | Result |
|---|---|---|---|
| FLD-004 | LIRjgre08.pdf | 18.71 m slip over 91.42 m (20.5 %), Opportunity, Eagle Crater, loose soils and steep crater wall, introduction paragraph | Correct. The text gives no crater diameter, which the corrected row already states |
| LRN-017 | 2011.01872v1.pdf | 93.0 % mIoU; 2375 images split 1647, 320, 408; wheel width 150 mm, radius 140 mm; 11 test routes; full scale errors 12.5 % and 10.8 %; interval probabilities 0.585 and 0.623; motion capture, lugged driving wheels with a follower | Correct |
| SIM-005 | 2407.18903v1.pdf | Plates of 0.2 m and 0.3 m radius, DEM particle radius 0.005 m, relative error below 2 % of the maximum force, annulus shear loads 25 to 200 kg with 100 kg shown in one frame | Correct. Table 4 values on p. 14 were not rechecked |
| TM-020 | EasyChair-Preprint-14770.pdf | D 150 mm, B 80 mm, 24 grousers of 8.5 mm, mass 10.2309 kg, FJS-1, coarse grain factor 15 (6 used in calibration), RMSE 0.015 at 10 degrees and 2 pi rad/s, Fig. 4a range 0.015 to 0.070 with the maximum at 5 degrees and pi rad/s | Correct |
| TM-022 | 2016_12_Carletti.pdf | Moonraker PFM2 about 7 kg, wheel radius 9 cm, width 8 cm, 15 grousers 2 cm long, 2.0 x 1.0 x 0.08 m tiltable sandbox with Toyura sand, Table 4 base model 14.76 % at 10 degrees | Minor error found. Table 4 sums the error on side slip and travelled distance; it does not give a side slip only error. Metric label corrected |

Outcome: 4 of 5 rows fully correct, 1 of 5 with a minor label error, now corrected (`research/corrections.csv`). This sample of five is too small to change the 144 row error rate reported in `research/verification_log.md`.
