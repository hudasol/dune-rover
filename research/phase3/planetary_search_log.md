# Planetary topic: search log (phase 3, 2026-10-20)

Topic: rover traverses and entrapment on sand and dunes on Mars, the Moon and Earth analog sites. Output: `planetary_rows.csv` (PLN-001 to PLN-071, 71 rows from 17 sources) and `planetary_references.csv`.

Counting rules used below: "hits" is the number the tool reported (total results for APIs, number of links returned for web search); "screened" is the number of titles or records looked at; "retrieved in full" is the number of full texts downloaded or opened and read; "used" is the number of sources that produced rows. All searches were run on 2026-10-20.

## Searches

| # | Database or tool | Exact query string | Date | Hits | Screened | Retrieved in full | Used |
|---|---|---|---|---|---|---|---|
| 1 | OpenAlex API (works search) | Spirit rover embedded Troy Home Plate Scamander (and four other lead queries) | 2026-10-20 | failed, HTTP 429 rate limit on every attempt | 0 | 0 | 0 |
| 2 | Crossref API (query.bibliographic) | Spirit Mars Rover Mission overview selected results northern Home Plate Winter Haven Scamander | 2026-10-20 | 32474 | 4 | 1 | 1 |
| 3 | Crossref API | Opportunity Mars Rover mission overview Purgatory ripple traverses Endeavour | 2026-10-20 | 530073 | 4 | 1 | 1 |
| 4 | Crossref API | Mars Science Laboratory Curiosity rover megaripple crossings sol 710 | 2026-10-20 | 10011983 | 4 | 0 | 0 |
| 5 | Crossref API | Surface characteristics Zhurong Mars rover traverse Utopia Planitia | 2026-10-20 | 2524647 | 4 | 0 | 0 |
| 6 | Crossref API | Sullivan cemented friable soils Troy Spirit | 2026-10-20 | 366084 | 4 | 0 | 0 |
| 7 | Crossref API | Yutu-2 rover locomotive exploration lunar farside slip | 2026-10-20 | 370762 | 5 | 0 | 0 |
| 8 | Crossref API | Yutu rover wheel sinkage lunar soil Chang'e-3 terramechanics | 2026-10-20 | 1456113 | 5 | 0 | 0 |
| 9 | Crossref API | Perseverance rover sand ripple slip autonomous navigation Jezero | 2026-10-20 | 503574 | 5 | 0 | 0 |
| 10 | Crossref API | Curiosity Bagnold dune campaign sand mobility Namib dune | 2026-10-20 | 386396 | 5 | 0 | 0 |
| 11 | Crossref API | Zhurong rover sand dune trapped mobility | 2026-10-20 | 347106 | 5 | 0 | 0 |
| 12 | Crossref API (DOI finding for retrieved texts) | Mars Curiosity Rover Mobility Trends During the First Seven Years Rankin; Mars Exploration Rover surface operations driving Opportunity at Meridiani Planum; Learning to predict slip for ground robots Angelova; Slip Modeling and Estimation for a Planetary Exploration Rover: Experimental Results from Mt. Etna; Data-driven surface traversability analysis for Mars 2020 landing site selection | 2026-10-20 | 115226; 2228377; 3315247; 498253; not printed | 3 each | 0 (DOI lookup only) | 0 |
| 13 | AGU / Wiley PDF endpoint (curl) | https://agupubs.onlinelibrary.wiley.com/doi/pdfdirect/10.1029/2010JE003633 and .../10.1029/2010JE003746 | 2026-10-20 | HTTP 403 | 2 | 0 | 0 |
| 14 | WebSearch | Arvidson "Megaripple Crossings up to Sol 710" pdf | 2026-10-20 | 9 | 9 | 0 (repository record is metadata only) | 0 |
| 15 | WebSearch | Arvidson "Spirit Mars Rover Mission: Overview and selected results from the northern Home Plate" pdf | 2026-10-20 | 10 | 10 | 1 (Smithsonian repository copy, read with web reader) | 1 |
| 16 | WebSearch | "Mars Curiosity" rover mobility trends Hidden Valley sand slip pdf robotics.jpl.nasa.gov | 2026-10-20 | 10 | 10 | 2 (IEEE Aerospace 2020 and JFR 2021 manuscript) | 1 |
| 17 | WebSearch | Zhurong rover wheel slip sinkage terramechanics Utopia Planitia open access | 2026-10-20 | 9 | 9 | 1 (Research Square preprint) | 1 |
| 18 | WebSearch | "Opportunity Mars Rover mission: Overview and selected results from Purgatory ripple to traverses to Endeavour crater" pdf | 2026-10-20 | 9 | 9 | 1 (institutional repository PDF) | 1 |
| 19 | WebSearch | Yutu-2 lunar rover wheel slip ratio sinkage measured traverse terramechanics regolith | 2026-10-20 | 10 | 10 | 1 (Nature Communications 2024) | 1 |
| 20 | WebSearch | Biesiadecki "Driving Opportunity at Meridiani Planum" pdf | 2026-10-20 | 10 | 10 | 1 | 1 |
| 21 | WebSearch | Curiosity Bagnold dunes Namib dune rover drive slip wheel sinkage Arvidson | 2026-10-20 | 10 | 10 | 1 (PMC5815393 via Europe PMC full text XML) | 1 |
| 22 | NTRS API | rover sand dune mobility slip | 2026-10-20 | 3 | 3 | 0 | 0 |
| 23 | NTRS API | Mars rover megaripple sand slip | 2026-10-20 | 0 | 0 | 0 | 0 |
| 24 | NTRS API | Perseverance sand slip drive | 2026-10-20 | 0 | 0 | 0 | 0 |
| 25 | WebSearch | Sullivan 2011 "Cohesions, friction angles, and other physical properties of Martian regolith from Mars Exploration Rover wheel trenches and wheel scuffs" pdf | 2026-10-20 | 10 | 10 | 0 | 0 |
| 26 | WebSearch | Angelova Matthies Helmick Perona "Learning and prediction of slip from visual information" Journal of Field Robotics pdf | 2026-10-20 | 10 | 10 | 1 (ICRA 2006 paper in institutional repository; JFR version metadata only; DTIC copy HTTP 403; thesis page connection reset) | 1 |
| 27 | WebSearch | planetary rover prototype field test sand dunes slip measured Nakatajima OR Kelso OR Atacama OR Tengger wheeled rover | 2026-10-20 | 9 | 9 | 0 | 0 |
| 28 | Caltech authors repository API | Arvidson Curiosity terrain physical properties first 360 sols | 2026-10-20 | 6 shown | 6 | 1 | 1 |
| 29 | Caltech authors repository API | Arvidson wheel damage Curiosity | 2026-10-20 | 6 shown | 6 | 1 (Arvidson et al. 2017 J. Terramechanics) | 0 |
| 30 | Caltech authors repository API | Sullivan cohesions friction angles wheel trenches | 2026-10-20 | 6 shown | 6 | 0 | 0 |
| 31 | Caltech authors repository API | Arvidson Spirit Husband Hill mobility | 2026-10-20 | 6 shown | 6 | 1 (Arvidson et al. 2008 Spirit overview) | 0 |
| 32 | Caltech authors repository API | Arvidson megaripple | 2026-10-20 | 6 shown | 6 | 1 (Arvidson et al. 2006 Spirit overview) | 0 |
| 33 | NTRS API | megaripple | 2026-10-20 | 4 | 4 | 0 | 0 |
| 34 | NTRS API | Hidden Valley Curiosity | 2026-10-20 | 0 | 0 | 0 | 0 |
| 35 | NTRS API | Bagnold dunes rover | 2026-10-20 | 9 | 9 | 1 (20180007625, one page abstract) | 0 |
| 36 | NTRS API | rover slip sand dunes | 2026-10-20 | 2 | 2 | 0 | 0 |
| 37 | NTRS API | Scarecrow Dumont | 2026-10-20 | 0 | 0 | 0 | 0 |
| 38 | WebSearch | Perseverance rover driving sand ripples slip Séítah OR "Mars 2020" mobility sand wheel slip pdf robotics.jpl.nasa.gov | 2026-10-20 | 9 | 9 | 0 (relevant hits already in evidence.csv) | 0 |
| 39 | WebSearch | field test rover sand dunes Earth analog wheel slip measured planetary rover dune traverse results open access | 2026-10-20 | 9 | 9 | 1 (DLR elib, Mt. Etna) | 1 |
| 40 | NTRS API | Mobility performance of the lunar roving vehicle Apollo 15 | 2026-10-20 | 6 | 6 | 1 (19730008090) | 1 |
| 41 | NTRS API | lunar roving vehicle Apollo 16 mobility performance slip | 2026-10-20 | 0 | 0 | 0 | 0 |
| 42 | NTRS API | Sojourner rover soil mechanics wheel | 2026-10-20 | 0 | 0 | 0 | 0 |
| 43 | arXiv API | all:rover AND all:dune | 2026-10-20 | 7 | 7 | 0 | 0 |
| 44 | arXiv API | all:rover AND all:sand AND all:field AND all:slip | 2026-10-20 | 0 | 0 | 0 | 0 |
| 45 | arXiv API | all:Mars AND all:rover AND all:sand AND all:embedding | 2026-10-20 | 0 | 0 | 0 | 0 |
| 46 | WebSearch | Cunningham Nesnas Whittaker "Improving slip prediction on Mars using thermal inertia measurements" pdf | 2026-10-20 | 10 | 10 | 1 (RSS 2017 proceedings PDF) | 1 |
| 47 | WebSearch | Cunningham "Locally-adaptive slip prediction for planetary rovers using Gaussian processes" Curiosity pdf | 2026-10-20 | 9 | 9 | 1 (arXiv 2409.19455 retrieved from an earlier hit list) | 0 |
| 48 | WebSearch | Perseverance rover "Séítah" sand ripples drive slip autonomous navigation paper pdf | 2026-10-20 | 10 | 10 | 0 | 0 |
| 49 | WebSearch | Sojourner rover technology experiments wheel sinkage slip soil mechanics Mars Pathfinder results pdf | 2026-10-20 | 9 | 9 | 1 (PDS rover technology experiments document) | 0 |
| 50 | WebSearch | Rocky 7 Mars rover prototype field test Mojave sand dune slope slip results | 2026-10-20 | 10 | 10 | 0 | 0 |
| 51 | WebSearch | lpi.usra.edu meetings lpsc Curiosity rover slip sand Bagnold dunes drive Namib dune mobility abstract | 2026-10-20 | 10 | 10 | 1 (EGU2016-9711 abstract) | 0 |
| 52 | WebSearch | lpi.usra.edu lpsc Perseverance rover wheel slip sand terramechanics Jezero abstract | 2026-10-20 | 10 | 10 | 0 | 0 |
| 53 | WebSearch | lpi.usra.edu lpsc Opportunity rover ripple slip sinkage Meridiani terramechanics Arvidson abstract pdf | 2026-10-20 | 9 | 9 | 1 (Zhou et al. 2014 on the Keck Institute site; a Spirit slip analysis manuscript returned HTTP 403) | 1 |
| 54 | NTRS API | Perseverance autonomous navigation | 2026-10-20 | 4 | 4 | 0 (no downloads) | 0 |
| 55 | NTRS API | Mars 2020 rover driving | 2026-10-20 | 11 | 11 | 0 (no downloads for relevant records) | 0 |
| 56 | NTRS API | Curiosity megaripple | 2026-10-20 | 0 | 0 | 0 | 0 |
| 57 | WebSearch | "Mars 2020 Site-Specific Mission Performance Analysis" "Surface Traversability" pdf | 2026-10-20 | 10 | 10 | 2 (Ono et al. 2016; McHenry et al. 2020 AAS preprint) | 1 |
| 58 | WebSearch | "Rimmed Wheel Performance on the Mars Science Laboratory Scarecrow Rover" pdf | 2026-10-20 | 9 | 9 | 1 | 0 |
| 59 | WebSearch | "megaripple crossings" Curiosity "Journal of Field Robotics" Arvidson 2017 accepted manuscript pdf jpl OR wustl OR ntrs | 2026-10-20 | 9 | 9 | 0 | 0 |
| 60 | Keck Institute xTerramechanics workshop page | https://www.kiss.caltech.edu/workshops/xTerra/xTerra.html (list of PDFs) | 2026-10-20 | 17 PDFs listed | 17 | 1 (workshop final report) | 0 |
| 61 | WebSearch | Rothrock Ono "SPOC: Deep Learning-based Terrain Classification for Mars Rover Missions" pdf slip | 2026-10-20 | 9 | 9 | 0 | 0 |
| 62 | WebSearch | Higa Ono "Vision-based estimation of driving energy for planetary rovers using deep learning and terramechanics" Curiosity slip sand | 2026-10-20 | 10 | 10 | 0 | 0 |
| 63 | WebSearch | Stein Arvidson 2013 Scarecrow Dumont Dunes slip terramechanics Lunar and Planetary Science Conference abstract pdf | 2026-10-20 | 9 | 9 | 0 | 0 |
| 64 | WebSearch | FASTER project planetary rover field trial sand slip scout rover results paper pdf soil trafficability | 2026-10-20 | 9 | 9 | 1 (Nevatia et al. ICRA 2013 workshop paper) | 0 |
| 65 | WebSearch | Chang'e-3 Yutu rover wheel sinkage slip lunar regolith in situ terramechanics results open access | 2026-10-20 | 10 | 10 | 1 (Gao et al. 2016 accepted manuscript, institutional repository) | 1 |
| 66 | DOAJ record page (web reader) | https://doaj.org/article/847e91f74cf64d47bb8488d87fe8b89c | 2026-10-20 | 1 | 1 | 0 (general wheel sinkage model, no rover field data) | 0 |
| 67 | WebSearch | Verma Maimone "Autonomous robotics is driving Perseverance rover's progress on Mars" pdf | 2026-10-20 | 10 | 10 | 2 (Verma et al. 2023 and 2025 IEEE Aerospace author copies; the Science Robotics paper itself was not found open) | 2 |

Live identity checks: every used source was resolved by a Crossref DOI lookup (api.crossref.org/works/DOI) on 2026-10-20, except the Apollo 15 LRV report, which has no DOI and was resolved by opening its NTRS API record and PDF. OpenAlex returned HTTP 429 for the whole session and could not be used.

## Inclusion and exclusion reasons

Included (17 sources, all read in full or, for long mission overviews, read in full for the mobility sections and skimmed elsewhere):

- Ding et al. 2021 preprint (Zhurong): rover measured slip ratio, sinkage, inferred soil parameters and dune geometry on Mars.
- Rankin et al. 2021 (Curiosity seven year mobility trends): mission slip statistics, Hidden Valley ripple sand slip, progress and sinkage, operating rules.
- Arvidson et al. 2010 (Spirit at Troy): slip, extrication progress, force balance at the embedding site.
- Arvidson et al. 2011 (Opportunity, Purgatory to Endeavour): ripple flank slip, sinkage and fitted terramechanics parameters.
- Biesiadecki et al. 2005 (Opportunity driving at Meridiani): 100 percent slip in crater sand and the diagonal ascent tactic.
- Angelova et al. 2006 (ICRA): slip prediction accuracy on natural sandy slopes in the Mojave and slip on flat deep sand. This paper had been on an earlier not retrieved list.
- Arvidson et al. 2014 (Curiosity first 360 sols): sandy slope planning threshold and sinkage.
- Ding et al. 2024 (Yutu-2 digital twin): lunar sinkage, slip, inferred regolith strength and prediction accuracy of arrival point.
- Ehlmann et al. 2017 (Bagnold dunes grain properties): grain size of active Martian dune sand and the operational rule against driving on the dunes.
- Bussmann et al. 2018 (LRU at Mt. Etna): slip model parameters and odometry accuracy on loose volcanic soil and slopes.
- Costes et al. 1972 (Apollo 15 LRV): lunar field slip bias, sinkage, spinout depth and slopes driven.
- Cunningham et al. 2017 (RSS): Curiosity slip in sand by site and slip prediction error with and without thermal inertia.
- Zhou et al. 2014 (Simulations of Mars Rover Traverses): Dumont Dunes field slip vs dune face slope for a MER test rover, slip measurement error, tuned dune sand parameters, and the Opportunity sol 2143 ripple fit.
- Ono et al. 2016 (Mars 2020 traversability): dune slope planning value and orbital terrain classification accuracy.
- Gao et al. 2016 (Chang'E-3 soil strength from images): Yutu and Lunokhod-1 track sinkage and soil stiffness from photoclinometry.
- Verma et al. 2023 (Mars 2020 robotic operations, first year and a half): Perseverance slip events crossing a Seitah sand ripple and slip fault counts in sand.
- Verma et al. 2025 (Perseverance first extended mission): excessive slip faults on steep loose sandy slopes and drive rates in ripple laden complex terrain.

Excluded after reading:

- Rankin et al. 2020, IEEE Aerospace (Driving Curiosity): shorter conference version of the 2021 journal paper; duplicate findings.
- Arvidson et al. 2008 (Spirit to the Columbia Hills) and Arvidson et al. 2006 (Spirit landing site to Backstay Rock): only qualitative mentions of slip; no usable numbers for sand mobility.
- Arvidson et al. 2017, J. Terramechanics (Curiosity wheel damage): damage linked to sharp sandstone outcrops and drive kinematics, not to sand; sand mobility statements cite other papers.
- Graser, Rimmed Wheel Performance on the MSL Scarecrow Rover: laboratory Mars Yard tests; the authors excluded quantitative sand results.
- McHenry et al. 2020 (Mars 2020 autonomous navigation, AAS preprint): no sand mobility numbers.
- Lamarre and Kelly 2024 (arXiv 2409.19455): review that restates Curiosity events from other papers (secondary citation).
- Keck Institute xTerramechanics final report: no new quantitative field data.
- PDS Sojourner rover technology experiments document: experiment descriptions without results.
- Nevatia et al. 2013 (FASTER system concept, ICRA workshop): concept paper without field results.
- Lopez-Arreguin et al. 2019 (Results in Physics, sinkage on Earth and Moon): general model paper, no rover traverse data; not pursued.
- Lapotre and Rampe 2018 (NTRS 20180007625) and Bridges et al. EGU2016-9711: one page abstracts with no mobility numbers.
- Within used sources, values that the authors cite from other papers were not turned into rows: kx 28 mm for Dumont dune sand in Arvidson et al. 2014 (cited from Stein et al. 2013), the 10 cm ripple amplitude rule in Ono et al. 2016 (cited from the megaripple paper), and the Mars Yard 20 degree climb limit quoted in Zhou et al. 2014 (cited from Lindemann et al. 2006).
- Findings already in `research/evidence.csv` were not repeated: Purgatory slip and duration (FLD-001, FLD-002), Curiosity default slip limit (FLD-020), Arvidson LPSC 2016 megaripple slip (FLD-018), Heverly et al. 2013 Scarecrow rows.

## Not retrieved

| Citation | Why | What would be needed |
|---|---|---|
| Arvidson R. E., Zhou F., Stein N. T., Heverly M., et al. (2017). Mars Science Laboratory Curiosity Rover Megaripple Crossings up to Sol 710 in Gale Crater. Journal of Field Robotics, doi 10.1002/rob.21647 | Publisher paywall; Caltech repository record is metadata only; no author manuscript found on JPL, NTRS or elsewhere | Library access or an author manuscript |
| Sullivan R., et al. (2011). Cohesions, friction angles, and other physical properties of Martian regolith from Mars Exploration Rover wheel trenches and wheel scuffs. Journal of Geophysical Research (DOI not confirmed in this session) | No open copy found; AGU PDF endpoint returns HTTP 403 to the shell | AGU free back issue access through a browser, or a repository copy |
| Angelova A., Matthies L., Helmick D., Perona P. (2007). Learning and prediction of slip from visual information. Journal of Field Robotics 24, 205 to 231 | Caltech record is metadata only; DTIC copy (ADA593494) returned HTTP 403 | Library access, or retry the DTIC PDF from a browser |
| Angelova A. (2008). Visual Prediction of Rover Slip: Learning Algorithms and Field Experiments. PhD thesis (thesis.library.caltech.edu/3886) | Connection reset by the proxy on two attempts | Retry the thesis repository later |
| Ding L., et al. (2022). Surface characteristics of the Zhurong Mars rover traverse at Utopia Planitia. Nature Geoscience 15, doi 10.1038/s41561-022-00905-6 | Published version is paywalled; the CC BY preprint of the same work was used instead | Library access to check whether values changed between preprint and journal version |
| Spirit slip analysis manuscript prepared for ISTVS (file spirit_slip_analysis_istvstemplate on a faculty web server; authors not visible because the file could not be opened) | HTTP 403 | Browser access to the faculty file server |
| Moore H. J., et al. (1999). Soil-like deposits observed by Sojourner, the Pathfinder rover. Journal of Geophysical Research | No open copy found; AGU blocked from the shell | AGU back issue access |
| Verma V., et al. (2023). Autonomous robotics is driving Perseverance rover's progress on Mars. Science Robotics; and the Mars 2020 enhanced autonomous navigation papers listed in NTRS | No open copy found; NTRS records have no downloadable files (two IEEE Aerospace operations papers by the same team were used instead) | Author manuscripts or NTRS uploads |
