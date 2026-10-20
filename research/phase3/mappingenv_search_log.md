# Search log, topic mappingenv (terrain mapping and traversability; heat, dust and sun effects)

Phase 3 evidence extraction, 2026-10-20. Row ids MAP-001 to MAP-036 (terrain mapping, traversability, DEM resolution, risk aware planning) and ENV-001 to ENV-017 (dust, heat, sun) in `mappingenv_rows.csv`. All rows were written from full text read on 2026-10-20; downloaded files are under `research/sources/phase3/mappingenv/`.

## Searches

| # | Database or tool | Exact query string | Date | Hits returned | Screened | Retrieved in full | Used |
|---|---|---|---|---|---|---|---|
| 1 | OpenAlex API (8 queries: SPOC; Stanley; risk aware planning; dust lidar; dust filtering; Mars 2020 traversability; self supervised terrain classification; DEM resolution slope underestimation) | e.g. `SPOC deep learning terrain classification Mars rover` | 2026-10-20 | 0 (API refused: free daily budget for this network exhausted) | 0 | 0 | 0 |
| 2 | arXiv API (7 queries) | e.g. `abs:traversability AND abs:desert`; `abs:lidar AND abs:dust AND abs:"airborne"` | 2026-10-20 | 0 (empty responses) | 0 | 0 | 0 |
| 3 | WebSearch | `risk-aware path planning probabilistic fusion traversability prediction planetary rovers heterogeneous terrains arXiv` | 2026-10-20 | 10 | 3 | 2 | 2 |
| 4 | WebSearch | `SPOC deep learning-based terrain classification Mars rover missions Rothrock pdf` | 2026-10-20 | 9 | 4 | 2 | 0 |
| 5 | WebSearch | `LiDAR dust airborne particulates behaviour off-road vehicle filtering intensity range open access` | 2026-10-20 | 9 | 3 | 1 (via Europe PMC XML) | 1 |
| 6 | WebSearch | `effect of DEM resolution on slope estimation underestimation steep slopes open access` | 2026-10-20 | 10 | 3 | 2 | 2 |
| 7 | WebSearch | `"Stanley: The robot that won the DARPA Grand Challenge" pdf false positives laser terrain` | 2026-10-20 | 9 | 2 | 1 | 1 |
| 8 | WebSearch | `"Data-driven surface traversability analysis for Mars 2020 landing site selection" pdf` | 2026-10-20 | 9 | 1 | 1 | 1 |
| 9 | WebSearch | `"When the dust settles" LiDAR fine airborne particulates Phillips pdf` | 2026-10-20 | 9 | 3 | 1 | 1 |
| 10 | WebSearch | `HiRISE DTM slope baseline dependence rover traversability landing site slopes 1 m baseline` | 2026-10-20 | 10 | 4 | 1 | 1 |
| 11 | WebSearch | `Argonne ambient temperature 95°F impact energy consumption battery electric vehicle Lohse-Busch osti.gov pdf` | 2026-10-20 | 9 | 3 | 0 | 0 |
| 12 | WebSearch | `mobile robot field test desert high ambient temperature motor overheating battery temperature measured rover Atacama` | 2026-10-20 | 10 | 3 | 1 | 1 |
| 13 | WebSearch | `soiling rate photovoltaic UAE desert measured percent per day open access dust accumulation` | 2026-10-20 | 9 | 3 | 1 | 1 |
| 14 | WebSearch | `airborne particle classification LiDAR point clouds deep learning dust smoke Stanislas arXiv` | 2026-10-20 | 10 | 1 | 1 | 1 |
| 15 | WebSearch | `Cunningham "slip prediction" Mars thermal inertia Curiosity Gaussian process pdf` | 2026-10-20 | 10 | 2 | 1 | 1 |
| 16 | WebSearch | `terrain classification sand desert unmanned ground vehicle accuracy lidar camera field dataset arXiv` | 2026-10-20 | 9 | 4 | 2 (third, a DTIC report, returned an HTML block page) | 1 |
| 17 | WebSearch | `sandstorm dust degradation camera object detection performance drop mAP dataset arXiv` | 2026-10-20 | 9 | 3 | 1 | 0 |
| 18 | NASA NTRS API | `solar array dust Mars Exploration Rover performance` | 2026-10-20 | 10 | 3 | 0 (no downloadable PDF listed for the two relevant records) | 0 |
| 19 | WebSearch | `effect of DEM resolution on rover path planning traversability map path length slope lunar Mars study` | 2026-10-20 | 9 | 4 | 2 (NTRS 20120008542, NTRS 20060053991) | 1 |
| 20 | WebSearch | `Opportunity rover solar array dust factor per sol degradation rate measured pdf` | 2026-10-20 | 10 | 3 | 2 (NTRS 20190029200 and its abstract version 20190028687; HAL copy of Lorenz et al. blocked) | 1 |
| 21 | WebSearch | `lithium-ion battery robot vehicle hot desert ambient temperature field measurement pack temperature 50 °C electric vehicle Middle East study open access` | 2026-10-20 | 9 | 3 | 0 (repository returned an error page) | 0 |
| 22 | WebSearch | `Desert RATS field test rover dust heat Arizona vehicle performance NTRS lessons learned temperature` | 2026-10-20 | 9 | 4 | 3 (NTRS 20090012335, 20100042197, 20230017073) | 0 |
| 23 | WebSearch | `SPOC "Soil Property and Object Classification" Mars rover terrain classification accuracy JPL pdf` | 2026-10-20 | 10 | 2 | 0 | 0 |
| 24 | WebSearch | `camera image quality dust deposition lens off-road vehicle perception experiment contrast degradation measured` | 2026-10-20 | 9 | 2 | 0 | 0 |
| 25 | WebSearch | `LiDAR sensor performance high ambient temperature climate chamber test range accuracy degradation 50 °C open access` | 2026-10-20 | 9 | 2 | 0 | 0 |
| 26 | WebSearch | `electric vehicle hot weather 35 °C range reduction air conditioning measured dynamometer study open access battery electric` | 2026-10-20 | 10 | 1 | 0 (results were news items, excluded) | 0 |
| 27 | Europe PMC REST | `(traversability OR "terrain classification") AND (desert OR sand OR dune) AND OPEN_ACCESS:y` | 2026-10-20 | 93 | 12 | 1 (PMC13004946, published version of row source endo2024, used for a value check only) | 0 new |
| 28 | Europe PMC REST | `"unmanned ground vehicle" AND (temperature OR thermal) AND (desert OR "hot") AND OPEN_ACCESS:y` | 2026-10-20 | 22 | 12 | 0 | 0 |
| 29 | Europe PMC REST | `lidar AND dust AND (mining OR "off-road" OR desert) AND OPEN_ACCESS:y` | 2026-10-20 | 381 | 12 | 1 (PMC12567788) | 1 |
| 30 | Europe PMC REST | `"slip" AND (rover OR "mobile robot") AND (sand OR desert) AND OPEN_ACCESS:y` | 2026-10-20 | 81 | 12 | 1 (PMC10713549) | 1 |
| 31 | WebSearch | `MBZIRC Abu Dhabi outdoor robots heat overheating temperature lessons learned field report arXiv` | 2026-10-20 | 9 | 2 | 1 (arXiv 2105.11979) | 0 |
| 32 | WebSearch | `rover field trial desert electronics temperature measured solar heating enclosure "°C" Atacama Mojave Sahara robot paper` | 2026-10-20 | 10 | 4 | 2 (third, a Sahara analog study, failed to download) | 2 |
| 33 | Europe PMC REST | `("enclosed vehicle" OR "parked vehicle" OR "hot vehicle") AND (dashboard OR "cabin temperature") AND OPEN_ACCESS:y` | 2026-10-20 | 11 | 3 | 1 (PMC6204985) | 1 |
| 34 | Europe PMC REST | `("path planning" OR "route planning") AND (desert OR dune) AND ("digital elevation" OR DEM OR satellite) AND OPEN_ACCESS:y` | 2026-10-20 | 47 | 12 | 0 | 0 |
| 35 | Europe PMC REST | `(lidar OR camera) AND ("sand storm" OR sandstorm OR "dust storm") AND (detection OR perception) AND OPEN_ACCESS:y` | 2026-10-20 | 123 | 12 | 2 (PMC13568439, PMC12749240) | 1 |
| 36 | Europe PMC REST | `("DEM resolution" OR "grid resolution") AND slope AND (accuracy OR error) AND (lidar OR UAV) AND OPEN_ACCESS:y` | 2026-10-20 | 114 | 12 | 0 | 0 |
| 37 | USGS Publications Warehouse pages and publisher PDF links | records 70034779 (HiRISE meter scale slopes) and 70177060 (InSight local slopes) | 2026-10-20 | 2 | 2 | 0 (publisher PDF links returned HTML pages) | 0 |
| 38 | WebSearch | `UAV photogrammetry sand dune DEM resolution slope angle slip face measured comparison open access` | 2026-10-20 | 9 | 3 | 1 (arXiv 1910.06186) | 1 |
| 39 | WebSearch | `lidar dust performance degradation range detection probability measured dust concentration visibility experiment open access arXiv` | 2026-10-20 | 10 | 3 | 0 (already held or thesis pages only) | 0 |
| 40 | WebSearch | `Urmson "A robust approach to high-speed navigation for unrehearsed desert terrain" pdf` | 2026-10-20 | 10 | 3 | 0 (author PDFs did not download) | 0 |
| 41 | WebSearch | `"Data-driven mobility risk prediction for planetary rovers" Skonieczny pdf` | 2026-10-20 | 10 | 3 | 1 (repository PDF of Lui et al.; the Skonieczny paper itself was not found open) | 1 |
| 42 | Crossref API (bibliographic queries, used to find DOIs, not to discover sources) | titles of Ono 2016, Endo 2023, Stanislas 2019, McMillon-Brown 2019, Wettergreen 2005 and 2008, Hadj-Bachir 2021 | 2026-10-20 | 3 per query | not applicable | not applicable | not applicable |

Totals: 24 distinct sources used, 53 rows (36 MAP, 17 ENV).

## Inclusion reasons

- Quantitative terrain classification or traversability results with a stated accuracy, error, success rate or entrapment measure (Endo 2023 and 2024, Ono 2016, Thrun 2006, Cunningham 2017, Chebolu 2026).
- Quantitative effect of DEM resolution or slope algorithm on slope values (Tang 2013, Wang and Wu 2017, Sadeghi poster), and map based planning outcomes in the field (Ono 2016, Hoffman 2012, Wettergreen 2005 and 2008, Lee 2023 for slip aware planning, Lui 2015 for uncertainty aware planning on a real rover).
- Measured dust effects on lidar (Hadj-Bachir 2021, Afzalaghaeinaeini 2022, Stanislas 2019, Cavieres 2025), measured dust soiling of solar panels in the UAE and on Mars (Shah 2020, McMillon-Brown 2019), measured heat on robots and closed vehicles in sun (Qian 2026, Vanos 2018), measured ambient temperature at an inland UAE site (Shah 2020), camera detection under sandstorm imagery (Song 2026), and drone mapping accuracy and map ageing on dunes (Grohmann 2020).
- Mars and lunar evidence kept with a gravity and terrain warning in `comparability_warning`.

## Exclusion reasons (screened and read, no row)

- arXiv 2410.17738 (hybrid traversability architecture for Mars rovers): simulation demonstration without a reported accuracy or traverse outcome.
- arXiv 1805.05451 (solar rover autonomy review): review of other work; no new measured numbers.
- arXiv 2409.18253 (UAV assisted terrain awareness): non desert terrain; sand only mentioned in passing.
- arXiv 2411.14095 (weather adaptive representation learning): no sand or dust conditions.
- Europe PMC PMC12749240 (YOLO and Faster R-CNN robustness on DAWN): sandstorm images pooled with other weather; no per condition sandstorm result found.
- arXiv 2105.11979 (NimbRo UGV at MBZIRC 2020): no heat, dust or terrain measurements; "heat" refers to the fire fighting target.
- NTRS 20090012335, 20100042197, 20230017073 (Desert RATS reports 2003, 2008, 2022): human factors and operations content; slope and heat remarks are qualitative crew comments, no measured vehicle heat or dust numbers.
- NTRS 20060053991 (human robot site survey): no map resolution or traverse outcome numbers relevant to the topic.
- Ono 2016 statements on MSL slope limits (about 20 degrees on bedrock, about 10 degrees on large sand dunes, ripples of 10 cm or more to be avoided) are cited from another source inside that paper, so no row was written from them (rule 1, secondary citation).
- Wettergreen 2005 Fig. 4 caption claim of slope climbing up to the angle of repose (about 30 degrees): a capability statement without a measurement.
- Angelova et al. slip prediction (RSS 2006) and AI4Mars: already in `research/evidence.csv` (LRN-003 to LRN-005 and LRN-012); not repeated.

## Not retrieved

| Citation | Why | What would be needed |
|---|---|---|
| Rothrock B. et al. SPOC: Deep Learning-based Terrain Classification for Mars Rover Missions. AIAA SPACE 2016 (as cited in Endo 2024, ref. list). | No open full text found (two searches); only citations and news. | A JPL or NTRS hosted copy, or library access to AIAA. |
| Phillips T.G., Guenther N., McAree P.R. When the dust settles: the four behaviors of lidar in the presence of fine airborne particulates. Journal of Field Robotics 34(5), 2017. | No open copy located; publisher page only. | Author repository copy or library access. |
| Lander and rover histories of dust accumulation on and removal from solar arrays on Mars (HAL hal-03369920; authors and venue not confirmed because the record could not be opened). | HAL and INTA repository copies returned an automated bot check page. | Manual download of the HAL PDF in a browser. |
| Argonne vehicle testing of ambient temperature effects on battery electric vehicle energy use (SAE paper 2013-01-1462 as listed by search; title and authors not confirmed). | SAE paywall; the Argonne research highlight page returned a JavaScript bot check. | An OSTI full text copy or the Argonne page opened in a browser. |
| Abdelhay, master's thesis listed by search (topic: electric vehicles in hot desert conditions; title not confirmed). | Repository returned an error page. | Manual download from the repository. |
| Hunveyor-4 analogue field study in the Sahara (Austrian Space Forum MARS2013 archive). | Download link did not return a file. | Manual download from the mission archive. |
| Kirk R.L. et al. Ultrahigh resolution topographic mapping of Mars with MRO HiRISE stereo images (JGR 2008), and the InSight local slopes analysis (USGS). | Only catalogue pages reached within the time box; slope versus baseline figures not read. | Open copies from USGS publications warehouse. |
| NTRS 20050186821 and 20090026397 (MER solar array dust and performance). | NTRS lists no downloadable full text. | Full text from the conference publisher or NASA. |
| Urmson C. et al. A Robust Approach to High-Speed Navigation for Unrehearsed Desert Terrain (as listed by search; venue not confirmed) and High Speed Navigation of Unrehearsed Terrain: Red Team Technology for Grand Challenge 2004. | Author PDFs on the institute site did not download from this machine. | Manual download.|
| DTIC ADA582379 (terrain classification from aerial data, as listed by search). | DTIC returned an HTML block page instead of the PDF. | Manual download from DTIC. |
