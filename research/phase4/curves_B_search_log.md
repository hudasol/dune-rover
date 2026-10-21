# Curve agent B: search log (phase 4, 2026-10-21)

Scope: single wheel test beds and tilting single wheel or small rover lab tests on dry sand or sand like simulants, slip against slope angle, or slip against a drawbar pull that the source states is equivalent to a slope. Output: 7 curve specifications in `research/phase4/digitise/` (nakashima2010 x 4, hu2025goff x 3) and `curves_B_references.csv`.

Counting rules: "hits" is the number of links or records the tool returned (for Crossref the total it reported); "screened" is the number of titles, abstracts or local files looked at; "retrieved in full" is the number of full texts opened and read; "used" is the number of sources that produced curves. The run was interrupted once by a machine restart; no work was lost.

## Searches

| # | Database or tool | Exact query string | Date | Hits | Screened | Retrieved in full | Used |
|---|---|---|---|---|---|---|---|
| 1 | Local files (research/sources, research/sources/phase3) | grep for slope, incline, tilt and slip counts in every text file | 2026-10-21 | 150 text files | 60 | 9 | 1 (hu2025goff, NTRS 20250001809) |
| 2 | WebSearch | single wheel test bed tilting slope slip ratio sand experiment grouser wheel open access | 2026-10-21 | 9 | 9 | 0 | 0 |
| 3 | WebSearch | "slope angle" "slip ratio" lunar rover wheel experiment inclined soil bin MDPI | 2026-10-21 | 10 | 10 | 2 (Kyoto repository copy of Nakashima 2010; MDPI Aerospace 12(2) 115 read with web reader) | 1 (nakashima2010) |
| 4 | WebSearch | Sutoh Nagaoka Nagatani Yoshida "Design of wheels with grousers" slope pdf | 2026-10-21 | 10 | 10 | 1 (arXiv 2605.24311) | 0 |
| 5 | WebSearch | J-STAGE rover wheel slope climbing loose soil slip ratio experiment tilting sand box Toyoura | 2026-10-21 | 10 | 10 | 0 | 0 |
| 6 | Kyoto repository DSpace API | pid/find?id=hdl:2433/126852, then bundles and bitstreams | 2026-10-21 | 1 | 1 | 1 | 1 |
| 7 | WebFetch | https://www.mdpi.com/2226-4310/12/1/71 | 2026-10-21 | 1 | 1 | 1 | 0 |
| 8 | WebFetch | https://www.mdpi.com/2226-4310/12/2/115/htm | 2026-10-21 | 1 | 1 | 1 | 0 |
| 9 | WebSearch | single wheel experiment inclined sand slope "slip ratio" "slope angle" lunar rover wheel test bed tilting Harbin experimental study | 2026-10-21 | 9 | 9 | 1 (ICRA 2007 workshop slides) | 0 |
| 10 | WebSearch | Shrivastava Goldman "Material remodeling and unconventional gaits" rover granular slope slip arXiv | 2026-10-21 | 9 | 9 | 1 (combined PDF with supplement) | 0 |
| 11 | WebSearch | NASA NTRS single wheel slope climbing test GRC-1 tilt bed wheel slip versus slope angle | 2026-10-21 | 10 | 10 | 0 (already local) | 0 |
| 12 | WebSearch | thesis pdf "slope" "single wheel" "slip ratio" sand "tilting" test bed rover wheel grouser experimental results dissertation | 2026-10-21 | 9 | 9 | 1 (Orton 2019, local copy) | 0 |
| 13 | WebFetch | https://www.preprints.org/manuscript/202411.0728 | 2026-10-21 | 1 | 1 | 1 | 0 |
| 14 | WebFetch | 2023.istvs.org papers 4595, 1453, 9268 and 2024.istvs.org paper 3773 | 2026-10-21 | 4 | 4 | 0 (abstract pages only, full papers paid) | 0 |
| 15 | WebSearch | site:jstage.jst.go.jp wheel slope loose soil slip ratio experiment inclination angle lunar rover single wheel | 2026-10-21 | 10 | 10 | 0 | 0 |
| 16 | WebSearch | "Journal of Robotics and Mechatronics" rover wheel slope climbing sand slip ratio inclination experiment | 2026-10-21 | 9 | 9 | 0 | 0 |
| 17 | WebSearch | rover wheel "slope climbing" "slip ratio" sandbox inclined "Toyoura sand" experiment open access 2022 OR 2023 OR 2024 | 2026-10-21 | 9 | 9 | 0 | 0 |
| 18 | WebSearch | Inotsume Kubota slope single wheel experiment slip prediction tilting sand arXiv | 2026-10-21 | 9 | 9 | 1 (SOKENDAI thesis A1630) | 0 |
| 19 | OpenAlex API | four search strings (wheel slope climbing loose soil; wheel slope sand slip experiment; rover slope traversability granular experiment wheel; single wheel slope test regolith simulant) | 2026-10-21 | failed, daily budget exhausted (rate limit) | 0 | 0 | 0 |
| 20 | Crossref API (query.bibliographic, 20 rows each) | wheel slope climbing loose soil experiment slip; lugged wheel sloped terrain lunar simulant experiment; planetary rover wheel slope sand traction experiment; slope traversal single wheel test bed sand | 2026-10-21 | 1167341; 365731; 595570; 2211855 | 80 | 0 | 0 |
| 21 | WebSearch | "Estimating Rover Slope Climbing Ability from Single Wheel Experiments" | 2026-10-21 | 10 | 10 | 1 (arXiv 2405.11001) | 0 (same data as hu2025goff) |
| 22 | WebFetch | https://robot.sia.cn/cn/article/id/1676 | 2026-10-21 | 1 | 1 | 0 | 0 |
| 23 | WebSearch | "Chinese Journal of Mechanical Engineering" OR "Applied Sciences" wheel slope sand "slip ratio" experiment "slope angle" lunar rover wheel climbing test results | 2026-10-21 | 10 | 10 | 1 (IMEKO 2017, local copy) | 0 |
| 24 | WebSearch | MoonRanger OR "micro-rover" tilt bed slope sand slip experiments slope angle wheel slip CMU thesis lunar simulant | 2026-10-21 | 9 | 9 | 1 (Ong 2022, read with web reader; direct download failed on the server certificate) | 0 |
| 25 | WebSearch | "slope" "slip" small rover sandbox tilted experiment "silica sand" wheel grouser height comparison open access journal | 2026-10-21 | 10 | 10 | 0 | 0 |
| 26 | WebSearch | Ishigami doctoral dissertation "Terramechanics-based Analysis and Control for Lunar/Planetary Exploration Robots" pdf | 2026-10-21 | 9 | 9 | 0 (JAXA record has no file) | 0 |

## Inclusions

- **nakashima2010** (Journal of Terramechanics 47(5), accepted manuscript): single wheel dynamometer on a tilting soil bin, FJS-1 simulant, dry bulk density 1.48 g/cm3 and friction angle 37.2 deg stated, wheels fully specified (Table 1), constant vertical load. Four experimental curves: Fig. 6(a), 6(b), 6(c) at 14.7 N and Fig. 7 at 19.6 N. Vector figure, red experiment markers found automatically; the 0 deg marker of Fig. 6(a) is hidden under a DEM square and left out.
- **hu2025goff** (Journal of Field Robotics 2025, NTRS author manuscript): Fig. 4(b) gives NASA Glenn TREC single wheel tests on level GRC-3 with the slope expressed as the traction slope arctan(DBP/N), stated by the source (emulated slope), with VIPER wheel geometry (radius 0.25 m, width 0.2 m, 24 grousers of 25 mm) and a 17.5 kg load. The same figure carries two whole rover tilt bed series (MGRU3 on GRC-1, 2021 and 2022); because this agent claimed the source, they were digitised too and are labelled as whole vehicle curves, with merged overlapping markers left out.

## Exclusions (full text read)

| Source | Reason |
|---|---|
| Iizuka and Kubota 2012, Journal of Asian Electric Vehicles 10(1) 1591 (local phase 3 copy) | single wheel on Keisa No. 5 silica sand at 0 to 20 deg, but Figs. 16 to 19 plot slip against travelled distance, not against slope; a steady value per slope would have to be invented |
| Iizuka and Kubota 2009, Journal of Asian Electric Vehicles 7(1) 1231 and 7(2) 1319 (local copies) | slip against distance per slope, and slip against Young's modulus; no slip against slope curve |
| Watanabe, Otani, Tanaka 2025, Aerospace 12(2) 115 | only 0 and 5 deg; slip plotted against wheel speed |
| Takehana et al. 2025, Aerospace 12(1) 71 and its preprint 202411.0728 | level sand bed, fixed 20 percent slip |
| Griffo and Nakka 2026, arXiv 2605.24311 | no slope tests |
| Shrivastava et al. 2020, Science Robotics (combined PDF) | poppy seeds, rover velocity against slope for a legged gait, wheel spin only gets trapped; no slip against slope |
| Yoshida 2007 ICRA workshop slides | whole rover slope traversal (agent A scope); single wheel data are slip ratio and slip angle on level ground |
| Coordinated control of slip ratio, Scientific World Journal 2014 (PMC4167808) | Figure 3 plots performance indexes against slip ratio, not slip against slope |
| Orton 2019, CMU-RI-TR-19-41 | drawbar pull against slip with no stated slope equivalence: candidate, pull only |
| Ong 2022, CMU-RI-TR-22-74 (web reader) | play sand rover runs over crests; velocity error against pitch, no controlled slope sweep |
| SOKENDAI 2013 thesis A1630 | level single wheel tests, slip against time |
| Kim, Sim, Yu 2017, IMEKO TC3/TC5/TC22 (local copy) | level single wheel tests |
| Carletti 2016 thesis (local copy) | side slip on slopes, no longitudinal slip against slope |
| NASA Best practices for testing planetary roving vehicles (NTRS 20250003470, local) | Figure 8 is a sample plot with no vehicle or soil stated |
| Freitag, Green, Melzer 1970 WES report M-70-2 (NTRS 19700020218, local) | the source states pull coefficient equals the tangent of the slope and reports single wheel and 4x4 slope tests on air dry Yuma sand, but the scanned PDF contains no figures (Figs. 69 to 73) and stops before the vehicle table; Table 4 gives summary parameters only |
| WES summary report M-70-4 (NTRS 19700027358, local) | Fig. 26 is wet sand (condition C2), outside the dry sand scope |
| JPL TM 33-477 Part I (NTRS 19710020731, local) | theory only |
| Hu et al. 2024, arXiv 2405.11001 | earlier version of hu2025goff with the same experimental data; not a new source |
| Jiao, Gao, Deng, Ding 2010, Robot 32(1) 70 to 76 (abstract page) | per the abstract, experiments at one slope (16 deg) with slip varied; full text not opened |

## Not retrieved

| Citation | Why | What would be needed |
|---|---|---|
| Wakabayashi, Kohno, Nishida 2008, Evaluation of low pressure mobility system for lunar vehicle, ISTS 2008-k-56 (source of the Fig. 7 data in nakashima2010) | conference CD, no open copy found | open copy from the authors or JAXA |
| Ishigami 2008, Terramechanics-based analysis and control for lunar/planetary exploration robots (doctoral thesis) | JAXA record has no file | open thesis copy |
| Sutoh, Nagaoka, Nagatani, Yoshida 2013, Design of wheels with grousers for planetary rovers traveling over loose soil, Journal of Terramechanics 50 | publisher paywall; only the ISTVS news page found | open accepted manuscript |
| Estimating Rover Slope Climbing Ability from Single Wheel Experiments, ISPARO 2024 (doi 10.1109/isparo60631.2024.10688321) | IEEE paywall; no open copy found | open copy |
| Fujiwara, He, Iizuka 2023, ISTVS paper 1453 (wheel walking rover on 15 to 32 deg slopes) | paid proceedings | open copy |
| Takehana et al. 2023, ISTVS paper 4595; Tanaka et al. 2024, ISTVS paper 3773 | paid proceedings (abstracts mention no slope tests) | open copy |
| Jiao, Gao, Deng, Ding 2010, Robot 32(1) (doi 10.3724/sp.j.1218.2010.00070) | PDF preview link not confirmed; abstract indicates one slope only | full text |
| Ding Liang group journal papers on slope climbing | no open full text with slope tests found in the time available | open copies |
