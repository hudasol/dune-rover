# Independent redigitisation of 12 phase 4 curves (verification sample)

Date: 2026-10-21. Input: `research/phase4/redigitise_sample.csv`.

## Method

- Every page was rasterised again with `pdftoppm -r 300` into `research/sources/phase4/verify_figures/` (one page at a time). No file of the first digitisation (specs, curves_new.csv, its overlays or search logs) was opened.
- Axes were calibrated on gridlines drawn at labelled tick values, found as pixel columns or rows with a high share of grey or dotted pixels; the pair of values used is written in each `x_axis.note` and `y_axis.note`.
- Markers were located by colour masks, morphological opening, pixel maps and close zooms of the raster; seed pixels are written in `marker.points` (mode `points`, no `refine` block, so the comparison reads exactly the pixels listed). The identification rule for each series is in `marker.identification`.
- Each spec was run through `digitise_figure()` of `scripts/digitise_figures.py` (with the figure folder pointed at `verify_figures/`), and every point was checked on an overlay drawn by the verifier: `verify_figures/<curve_id>_verify_overlay.png` (green cross per point, magenta lines on the calibration gridlines).
- `meta.y_unit` is `percent` for creager2017 (axis in percent) and `ratio` for all others (the CSV value `fraction` for hu2025goff is written as `ratio`).
- Points that are partly hidden but whose centre follows from a visible edge plus the known marker size are kept and named below; markers that are not visible at all are left out.

## Per curve

| curve_id | series identified | points | ambiguity |
|---|---|---|---|
| caruso2023_fig12a_lava_w1 | panel (a), blue open circles, omega 1 = 1.2 rad/s | 5 (0 to 20 deg) | circles at 0, 5, 15 deg partly covered by the orange triangles; centre from the visible arc and the 34 px diameter |
| caruso2023_fig12a_lava_w2 | panel (a), orange open triangles, omega 2 = 2.4 rad/s | 5 (0 to 20 deg) | triangle centre taken as the bounding box centre (MATLAB style); the area centroid would give slip about 0.008 lower |
| creager2017_fig11_scarab_aoa10 | dark blue filled squares, beta = 10 deg | 5 | point near (-0.9 deg, -1.8 percent) mostly under the orange diamond; centre from its visible top and left edges |
| creager2017_fig11_scarab_aoa30 | dark red filled circles, beta = 30 deg | 4 | the point near (-0.9 deg, -1.5 percent) is implied by the red line but the circle is fully covered; left out |
| hu2025goff_fig4b_mgru3_2022_grc1 | black filled circles, "MGRU3 2022 SLOPElab Tests, GRC1" (not the 2021 triangles) | 7 | two lowest circles touch 2021 triangles; centred from the free left edge and the 21 px diameter |
| hu2025goff_fig4b_trec_singlewheel_grc3 | black stars, "TREC Nominal Tests, GRC3" | 17 | several stars share one slip value (two at 0.1, 0.3, 0.6, 0.7, 0.8; three overlapping at 0.4); all kept. Star centre = centre of the circumscribed circle, refined by a shape fit within 4 px |
| sutoh2012_fig5a_toyoura_lh5_lug3 | panel (a), open triangles, 3 lugs | 4 (8, 12, 16, 20 deg) | 16 deg from the visible base only, 20 deg from the visible apex only (inferred); 0, 4, 24 deg hidden in clusters, left out |
| sutoh2012_fig5a_toyoura_lh5_lug6 | panel (a), filled squares, 6 lugs | 6 (0 to 20 deg) | 0 and 4 deg squares sit in stacks of filled markers, centre from the flat top edge and the 17 px side (inferred); 24 deg left out (merged with the frame, lower edge hidden) |
| watanabe2026_fig9c_silica_b3 | panel (c), red filled circles, b3 | 7 (0 to 30 deg) | none; drawn last, always fully visible |
| watanabe2026_fig9c_silica_b5 | panel (c), black filled squares, b5 | 7 (0 to 30 deg) | at 0 to 20 deg the red b3 circle covers part of the square; centre from the visible edges and the 16 px side |
| watanabe2026_fig9c_silica_b30 | panel (c), orange plus signs, b30 | 7 (0 to 30 deg) | 5, 10, 15 deg from the visible horizontal arm; 0 deg from two arm tips only (least certain point) |
| watanabe2026_fig10c_fjs1_b30 | panel (c), orange plus signs, b30 | 2 (15, 20 deg) | 0, 5, 10 deg completely hidden under other series; left out |

## Special format note

hu2025goff Fig. 4(b) has slip on the horizontal axis and slope on the vertical axis. Because `points` mode in `digitise_figures.py` has no `swap_output`, both hu2025goff specs give each point as `px = [row, column]`, with `x_axis` calibrated on pixel rows (slope) and `y_axis` on pixel columns (slip); this is stated in `marker.swap_note` and in the axis notes. The output x is therefore slope and y slip, as the CSV implies. A `refine` block must not be added to these two specs.

Total: 76 points in 12 curves.
