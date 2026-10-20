## Notes, exclusions and doubts

### Reproducing the tables

1. The source PDFs must be present under `research/sources/phase3/` (git ignored): `heverly2013.pdf`, `ishigami2007.pdf`, `inotsume_thesis.pdf` (copy of `research/sources/hiroaki_thesis.pdf`), `yoshida2010_slides.pdf` (copy of `research/sources/yoshida_traction.pdf`), `1-s2.0-S0022489825000400-main.pdf`, `LIRjgre08.pdf`, `hurrell2025.pdf` (copy of `research/sources/hurrell.pdf`). The supplied PDFs come from the author's sourced evidence folder.
2. `python scripts/digitise_figures.py` rasterises each named page with pdftoppm into `research/sources/phase3/figures/` and rewrites `research/phase3/curves.csv`; `--check` rebuilds and compares byte for byte; `--debug` writes mask and point overlays next to the rasters for visual audit.
3. `python scripts/build_data_catalog.py` rewrites this catalogue.

`research/phase3/sand_parameters.csv` is a hand transcription of printed tables and is not generated.

### Printed values used as checks

Where the source prints a value that is also plotted, the digitised value was compared (printed by the digitiser). Yoshida slides: 0.741, 0.229, 0.320, 0.056, 0.471 and 0.247 were reproduced within 0.001 in slip. Inotsume Appendix B text: "close to 0.9" (digitised 0.869) and "around 0.2" (digitised 0.219) at 4 deg. Heverly Sec 6.3 text: about 75 percent at 16 deg and about 90 percent at 20 deg; the binned Figure 12 medians are 79 percent (16 to 17 deg bin) and 91 percent (20 to 21 deg bin), the cubic fit gives 73 percent at 16 deg.

### Doubts

* Heverly Figure 12: the polynomial fit line is drawn over the markers; pixels under it were removed by colour, which can shift bin medians slightly. Bins pool eight runs at roughly constant slope.
* Li et al. Table 6: the authors state that BA slippage is biased low on steep drives because VO corrections were already in the telemetry; the VO based Figure 11a medians are higher in the 10 to 18 deg range for fine grain terrain.
* Takehana et al.: blue (0.2 m/s) markers hidden under other speeds were lost (low grouser wheel at slip 0.2 and 0.5) or merged from fragments.
* Ishigami 2007: overlapping repeat runs merge into one marker; the soil is a lunar simulant, not Toyoura sand as the brief expected. Ishigami 2009 Table I (Toyoura sand) prints kc and kphi without units; a later thesis copy of the same set prints kphi0 = 120.54, ten times smaller than 1,203.54.
* Scarab: the 90 deg angle of attack markers sit on the right frame line; x values are the actual slopes from Table 3.2 rather than digitised.
* Yoshida slides are a workshop presentation, not a peer reviewed paper, and slope is emulated by a horizontal load on level sand.

### Sources looked at and not turned into curves

* Wong table images in the sourced evidence folder. `the table of Bekker and Janosi parameters for dry sand.png` is a dark themed rendered table with no book title, no table number and no page; its dry sand row reads kc 0.99 kN/m^(n+1), kphi 1528.43 kN/m^(n+2), n 1.1, c 1.0 kPa, phi 28 deg, K 0.011 m. `Wong_TGV_4ed_ch2_table_photo.jpg.jpeg` is a typeset "Table 1. Bekker and Janosi Hanamoto parameters for dry sand" with three rounded "Example" columns, no units for kc and kphi and no book page. The PDF `Wong table ... dry sand.pdf` is a print of a local HTML file titled "Theory of Ground Vehicles, Chapter 2, Page 89" with a "Table 2.1" whose dry sand rows (standard, loose, dense) disagree with the other two images. None of the three is a scan of the book page, and they disagree with each other, so no values were taken. A scan or photograph of the printed book table is needed.
* EasyChair preprint 14770 (Omura and Ishigami 2024): simulation only slip against slope for granular scaling laws in low gravity; not digitised for lack of time.
* 2407.18903 (Zhang et al.): DEM and SCM simulation drawbar pull and slope against slip (Figures 27 to 29); not digitised (simulation only); its calibrated SCM set is in the parameter table.
* 1-s2.0-S0022489824000296 (Yu et al. 2024, 3D RFT): forces against slip angle on sand, not slip against slope or drawbar against slip in straight driving; not used.
* 2011.01872 (Zhou et al.): terrain property inference; its Table II fixed non dominant parameters (kc 100 kPa/m^(N-1), kphi 1400 kPa/m^N, c 1 kPa, K 16 mm) are assumed values, not measurements of a sand, so not listed.
* 2016_12_Carletti.pdf: soil parameters are copied from Ishigami (secondary); sandbox slope tests for the Moonraker rover were not digitised for lack of time (evidence row TM-022 covers one result).
* Ishigami 2009 slope traversal: only a single text value (slip ratio about 0.5 on a 10 deg side slope with steering); no curve.
* Jia et al. (Robotica 2012) and an SBMAC 2025 paper list sand parameters taken from other papers or textbooks (secondary), so they are not listed.
