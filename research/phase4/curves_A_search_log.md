# Curve agent A: search log (whole vehicle slip against slope), 2026-10-21

Scope: whole vehicle or rover slip against slope (natural dune or field tests on Earth sand, constructed slopes and tilt beds with whole rovers, Mars rover traverse slip with a gravity warning). Single wheel test beds were left to agent B.

The run was interrupted once by a machine restart; all files written before the restart were kept and the work continued from them.

## Searches

| Database or tool | Exact query string | Date | Hits returned | Screened | Retrieved in full | Used |
|---|---|---|---|---|---|---|
| Repository full text corpus (open access PDFs already downloaded under research/sources, text extracts) | figure captions matching `(fig\|figure) N` with `slip\|slippage\|travel reduction` and `slope\|tilt\|inclin\|pitch\|grade` | 2026-10-21 | 17 files | 17 | 17 (already local) | 2 (caruso2023, creager2017) |
| Same corpus, planetary and field files | captions with `slip\|slippage` in 23 named field and Mars rover files | 2026-10-21 | 11 files | 11 | 11 | 1 (cunningham2017) |
| Same corpus, J-STAGE files | captions with `slip\|slope\|incline` in 17 J-STAGE and JSME files | 2026-10-21 | 12 files | 12 | 12 | 2 (watanabe2026, sutoh2012) |
| Crossref API | works/10.3390/robotics12050125; works/10.1299/transjsme.25-00224; works/10.1299/jsmermd.2012._1A2-L06_1 | 2026-10-21 | 3 records | 3 | n/a | 3 resolved |
| NTRS API | api/citations/20180000349 | 2026-10-21 | 1 record | 1 | n/a | 1 resolved |
| URL check | https://roboticsproceedings.org/rss13/p38.pdf | 2026-10-21 | HTTP 200 PDF | 1 | n/a | 1 resolved |

No new web searches were run: the repository already held open full texts that met the scope, and time went to verified digitisation. Every source used was opened in full from the PDF (page renders checked for the values used, not only the text extract).

## Inclusions

- watanabe2026 (Trans. JSME 2026): 1.5 kg four wheeled rover, seven wheel widths (3 to 60 mm), 120 mm wheels with 12 lugs of 10 mm, tilting beds of silica sand (Fig. 9c) and FJS-1 (Fig. 10c), 0 to 30 deg. Whole rover, Earth sand, wheel size and load known. 14 curves.
- caruso2023 (Robotics 2023, CC BY): Archimede four wheeled rover on a tilting section of a planetary sandbox, granular lava (1 to 5 mm) and EAC-1A, 0 to 20 deg, two wheel speeds, Fig. 12 medians. 4 curves.
- creager2017 (NASA/TM): Scarab 400 kg on the SLOPE tilt bed in loose GRC-1, rear wheel slip against actual slope for angles of attack 10, 30, 60, 90 deg (Fig. 11). 4 curves; the 90 deg curve is flagged as probably the same runs as inotsume2016.
- sutoh2012 (JSME Robomec 2012): 4.0 kg two wheeled rover, 150 mm by 100 mm wheels, lugs 0 to 48 at 5 mm height, Toyoura sand tilting box, Fig. 5a. 6 curves, 2 to 4 clear points each.
- cunningham2017 (RSS 2017): Curiosity slip against slope in sand at 9 Gale crater sites (Fig. 7 top), summarised as 2 deg bin medians. 1 curve, Mars gravity.

## Exclusions and reasons

- arvidson2014 (JGR Planets, Curiosity first 360 sols), Fig. 16: all terrain scatter, mostly hard ground, not sand; the overlaid Scarecrow lines are the heverly2013 data already used. Claim released.
- Graser, rimmed wheel Scarecrow (pln_rimmed_scarecrow): slip on gravel and stone only, not sand.
- Zhurong surface characterisation (pln_zhurong_rs): slip along the route, not against slope.
- Ding Yutu-2 (pln_yutu2_ncomms2024): slip angle model in supplementary figures, no slip against slope data in the main text read.
- jstage_jrobomech_36_2_36_334 (JAXA excavation rover): tracked vehicle, outside wheeled scope.
- jstage_tastj_19_4_19_19.469 (hinge type rover): slip for step climbing, not against slope.
- Iizuka and Kubota JAEV papers (7.1231, 7.1319, 10.1591): single wheel tester, left to agent B.
- Bussmann Etna 2018: slip model calibration on volcanic ground, no slip against slope curve found in captions.
- Scout rover cooperation (scout_rover): legged RHex model predictions, not wheeled data.
- Creager best practices 2025 (ntrs_20250003470) Fig. 8: labelled a sample plot, not a dataset.
- Hu et al. gravitational offset (ntrs_20250001809): simulation only; also claimed by agent B.

## Not digitised in this run (open, in scope, left for follow up)

- sutoh2012 Fig. 5b (Toyoura sand, 15 mm lugs) and Fig. 6a, 6b (FJS-1): same layout as Fig. 5a; heavy marker overlap in a 1 bit scan; about 5 to 15 more short curves possible.
- caruso2023 Fig. 13: box plots pooled over speed; same runs as Fig. 12, so not added.

## Not retrieved

- Shrivastava et al. 2020, Science Robotics 5, eabb6163 (wheeled robophysical rover on granular slopes): not opened in this run; would need an open author copy.
- Lindemann et al. 2006, Mars Exploration Rover mobility development (IEEE Robotics and Automation Magazine): MER tilt table slip against slope; no open copy located in this run.
- Angelova et al. 2007, Learning and prediction of slip from visual information (JFR 24(3)): the local file named angelova_jfr.pdf is a different paper (Helmick et al., Terrain adaptive navigation); the JFR paper itself was not opened.
- Yutu-2 and Chang'e slip against slope traverse analyses: not located as open full text in this run.
