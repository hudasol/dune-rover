# Field and analog evidence: slip, sinkage, traversability on dry sand and dunes
Retrieval date for everything below: 2026-10-11. Working copies are in /home/claude/dune-rover/research/sources/.
Rows: /home/claude/dune-rover/research/raw/field_rows.csv (42 rows, 17 distinct sources). Lab rows use method_family "other" because the allowed list has no "empirical-lab" value.

## SEARCH_LOG
WebSearch queries (standard mode) and what they led to:
1. "Opportunity rover Purgatory Dune slip embedded wheels lessons learned mobility" -> Lamarre and Kelly arXiv 1805.05451 (read, no slip numbers), NASA status pages (not used).
2. "Curiosity rover wheel slip sand ripples Bagnold dunes slip percentage visual odometry slope" -> Arvidson LPSC 2016 poster (read, used), EGU2016-9711 Bagnold overview abstract (read, no mobility numbers).
3. "Arvidson Mars Science Laboratory Curiosity Rover Megaripple Crossings up to Sol 710 ..." -> CaltechAUTHORS record is metadata only (abstract only, no full text); JGR deepblue PDF returned 403.
4. "Spirit rover Troy embedded wheels terramechanics Artemis ..." -> Li and Lewis arXiv 2201.11984 (read, used descriptively); KISS PDF 404.
5. "Perseverance rover slip statistics ripples Jezero ..." -> JPL AAS 08-138 (2026) and Rapid Traverse 2023 papers (both read, used).
6. "Opportunity Purgatory Dune 2005 slip ..." -> Maimone et al. found via a later query (used).
7. "Scarecrow rover Dumont Dunes / Kelso / Death Valley ..." -> Planetary Society blog, NASA/JPL PIA15682, DesertUSA (all qualitative; no slip numbers).
8. "Curiosity Dingo Gap Hidden Valley Moon Light Valley megaripple crossing slip sinkage paper" -> nothing new with full text (Lamarre and Kelly mention them qualitatively).
9. "Cunningham Rothrock thermal inertia slip prediction ..." -> NTRS 20210006223 and RSS13 p38 are abstract-only pages (no downloads).
10. "wheeled robot slip sand dune slope experiment field trial desert Rub' al Khali OR Saudi ... UAE" -> Sensors 2016 assistive grousers paper (used), Frontiers 2024 slip-rate paper (single-wheel, not used), Rashid rover simulation arXiv 2308.12431 (UAE affiliation, single-wheel lunar-simulant rig, not used as a row).
11. "rover wheel slip versus slope angle inclined sand bed experiment ..." -> Inotsume CMU thesis (used heavily), several DEM/Chrono arXiv papers (belong to other subagents' scope; not used).
12. "Zhurong rover slip estimation ..." -> MDPI Applied Sciences paper returned 403; Nature Geoscience ESM downloaded but contains only a wheel/soil parameter table (no slip statistics).
13. "rover field test sand dune Moses Lake OR Kelso Dunes OR Great Sand Dunes OR Dumont Dunes ..." -> Dumont Dunes pages (qualitative).
14. "mobile robot dune traversal Gobi OR Tengger OR Taklamakan OR Sahara OR Namib OR Atacama ..." -> Desert RHex Tengger report (abstract page only), Berkeley ISTVS 2021 page, an escholarship PDF (returned 202 with 0 bytes).
15. "Heverly Traverse performance characterization for MSL rover ..." -> not openly retrievable; JPL 2018 TRCTL paper (used), Spirit slip WVU PDF (403), CaltechAUTHORS Li 2008 record (full PDF retrieved via files link, used).
16. "Maimone Cheng Matthies Two years of visual odometry ..." -> JPL robotics PDF (used).
17. "Lindemann Voorhees MER mobility assembly ..." -> found the 2004 JPL press piece via Mars Daily (used for SSTB-lite numbers), Leger et al. 2005 (used).
18. "Skonieczny rover slip ..." -> nothing retrievable.
19. Arabian queries: see ARABIAN_EVIDENCE.
20. "Atacama OR Gobi OR Namib OR Tengger field trial rover wheel slip ... " -> arXiv 2411.13978 (European Moon Rover System analogue campaign) surfaced but not opened (no evidence it is a sand/dune study).
Direct curl downloads that succeeded (host allowed): arxiv.org, ntrs.nasa.gov, robotics.jpl.nasa.gov, www-robotics.jpl.nasa.gov, authors.library.caltech.edu, ncbi.nlm.nih.gov/pmc (article pages), frontiersin.org, publications.ri.cmu.edu, oewf.org, esa.int, media.springernature.com, planetary.org.
Failures: kiss.caltech.edu (SSL cert error), deepblue.lib.umich.edu (403), www.kiss.caltech.edu/papers (404), mdpi.com (403), yugu.faculty.wvu.edu (403), pmc.ncbi.nlm.nih.gov new-style URL (reCAPTCHA page), openaccess.inaf.it (SSL handshake failure), escholarship.org qt1zp5c78w (HTTP 202, 0 bytes), jpl.nasa.gov PIA07999 page (403). Not retried with other commands.

## KEY_FINDINGS
1. Mars rover slip on loose sand is huge and not predictable from slope or imagery. Spirit logged 15-20 percent slip on a 19 degree slope and 95 percent on a 16 degree slope about 30 m later with no visible terrain difference (Leger et al. 2005, FLD-011/012). Perseverance recorded more than 94 percent slip at about 20 degrees on very sandy ground at Midtoya (FLD-025) and needed autonav slip limits above 50 percent on a 15-20 degree hill (FLD-024).
2. The worst entrapment cases are sand with hidden or low cohesion, not steep slope alone. Opportunity's wheels turned about 50 m of travel for 2 m of track at Purgatory ripple, and VO slip stayed at 98.9-99.5 percent over sols 463-483 (FLD-001/002). Curiosity megaripple crossings exceeded 70 percent 3D slip (FLD-018 poster), after which megaripple crossings with all wheels in sand were avoided.
3. Slip in the field is measured by visual odometry (or VO plus bundle adjustment), and VO itself fails on featureless sand. Maimone et al. introduced Slip Check from the Purgatory event; Perseverance logs 34 VO failures on 75 m of bland terrain; ESA/DFKI saw vision algorithms misbehave on smooth Sahara dunes (FLD-041). Definitions differ: Leger defines slip as reduction of distance travelled vs commanded; Li 2008 uses segment slippage relative to traversed distance; lab work uses velocity-based s = 1 - vx/vref.
4. Full-vehicle slope-bed data exist but mostly on simulants or Toyoura sand, with small rovers or heavy rovers that differ from flight vehicles. The only quantitative sand-slope plots for MER came from the SSTB-lite tilt platform (Earth, loose dry sand); the JPL release gives 90 percent uphill slip at 20 degrees and a 25 degree climbing limit (FLD-006/007), and the release says Meridiani slip behaviour matched. Numbers are from a press release, raw plots not retrieved.
5. Lab slope-bed results from CMU/Tokyo-style programs show a sharp threshold near 4-10 degrees for smooth wheels without grousers (El-Dorado-II slip about 0.9 at 4 degrees, about 0.2 with 12 grousers), and no wheeled success at the angle of repose (30 degrees) with a 23 kg rover and 296 mm wheels (FLD-030..FLD-035). Legged robots on tilt beds also degrade sharply near 20-25 degrees (FLD-036..FLD-038).
6. Slip is not monotonic in slope in the field data (Li et al. 2008 Table 6; sand-sized 10-15 degree bin lower than 5-10). Reasons given by the authors: operations avoid steep sand, VO-corrected drives, segment mix. Do not fit a clean slip-vs-slope curve to MER field aggregates.

## ARABIAN_EVIDENCE
What was found: very little, and none of it contains slip, sinkage or slope numbers for a wheeled or legged robot on Arabian dune sand.
- AMADEE-18 (Austrian Space Forum, Dhofar, Oman, Feb 2018): the Husky autonomous rover (Graz University of Technology) met much looser and softer sand than expected, got stuck from time to time, and dead-reckoning error was higher than expected. Source: public mission report section 10.8 (FLD-042). Qualitative only; the rover was a mapping proof of concept.
- Rashid lunar rover (UAE, MBRSC): news items (Gulf News, The National, 9 March 2022) report desert driving tests in Dubai and rover specs (descend 20 degree slope, 10 cm obstacle, 10 cm/s). No slip or sinkage data in the retrieved text. Not entered as a row.
- Khalifa University paper "Advance Simulation Method for Wheel-Terrain Interactions of Space Rovers: A Case Study on the UAE Rashid Rover" (arXiv 2308.12431): single-wheel test rig with lunar simulant at slip ratios 0, 0.25, 0.50, 0.75. UAE-authored but not Arabian sand and not a full-vehicle or field test; excluded from rows.
- No Rub' al Khali, Saudi, Qatari, Kuwaiti or Emirati dune trafficability study with a robot was found. No Bekker-Wong parameter set for Arabian dune sand was found by the queries below.
Queries tried: "Rub' al Khali OR Empty Quarter dunes robot mobility experiment wheel sinkage slip rover trafficability"; "wheeled robot slip sand dune slope experiment field trial desert Rub' al Khali OR Saudi Arabia OR UAE OR Oman OR Qatar rover traversability"; "UAE desert sand dune off-road vehicle OR robot tyre sinkage slip field test Abu Dhabi OR Dubai OR Liwa OR Al Ain terramechanics"; "Saudi Arabia OR Oman OR Qatar OR Kuwait desert sand wheeled robot field experiment slip dune traversability KAUST OR KFUPM OR Khalifa University OR MBRSC rover"; "AMADEE-18 Oman Dhofar Mars analog rover Husky ..."; "Arabian desert sand terramechanics Bekker parameters dune sand Saudi OR UAE OR Qatar measured cohesion friction angle bevameter"; "Khalifa University OR MBRSC OR Rashid rover desert sand dune field test wheel slip mobility UAE desert trial results". Search tool is US-only and standard mode; Arabic-language and regional journals (for example Saudi or Emirati university repositories, SAE Middle East papers) may hold more, and an SAE paper (2002-01-0284, tyre mistakes on sand) surfaced but was paywalled and not opened.
Other desert/analog findings (non-Arabian): Sahara (Erfoud, Morocco, ESA/DFKI 2018) qualitative; Dumont Dunes (Mojave) Scarecrow/SSTB-Lite tests 2012 qualitative; Tengger (Desert RHex, abstract only); Johnson Valley (JPL Rocky 8 VO test, mentioned in Maimone 2007). No Moses Lake, Kelso, Atacama, Gobi or Namib slip numbers were retrieved.

## GAPS
- Lab-to-field transfer: MER engineering slip tables from the dry-sand tilt bed worked on pure Eagle-crater sand but failed on mixed or nonhomogeneous terrain and on hidden weak deposits (Maimone 2007; Lamarre and Kelly 2018 say vision-based slip prediction fails on sand, and thermal inertia was proposed as a fix; Cunningham et al. abstract only).
- Untested or missing: slip and sinkage on real dune slip faces at the angle of repose with a full-size wheeled rover; Arabian dune sand (fine, rounded, often cemented below the surface) with any robot; Earth-gravity vs Mars-gravity comparison on the same sand with the same vehicle (Dumont Dunes weight-matched tests had no retrievable numbers); crosswind and lateral slip on dune crests; tracked robots on sand (none found).
- Slip definitions are not harmonised: wheel-odometry slip, VO slip, velocity-based s, bundle-adjusted segment slippage and distance-per-commanded-distance are used interchangeably across the rows. Slopes are local (rover pitch) in some papers and DEM-derived in others (Li 2008).
- Lab rows use simulants or Toyoura sand, small wheels and rovers, 1 rpm wheel speeds. Treat as mechanism evidence, not as dune predictions.
- Mars rows are Mars-gravity field data on Mars terrain (megaripples, cohesive crusts, sulfate deposits), not Earth dunes.

## NOT_RETRIEVED
Abstract-only numbers deliberately not recorded as rows:
- Arvidson et al. 2017, "Mars Science Laboratory Curiosity Rover Megaripple Crossings up to Sol 710 in Gale Crater", J. Field Robotics 34(3):495-518. Abstract (metadata page) mentions sinkage up to about 30 percent of the 0.50 m wheel diameter and rover-based slip up to 77 percent; full text not retrieved. https://resolver.caltech.edu/CaltechAUTHORS:20170427-101102389
- Cunningham, Nesnas, Whittaker, thermal inertia and slip prediction (NTRS 20210006223; RSS 2017 p38): abstract only, no numbers. https://ntrs.nasa.gov/citations/20210006223 and https://roboticsproceedings.org/rss13/p38.html
- Desert RHex Tengger Desert report (abstract says robots climbed 20 degree slopes with 8.5 kg payload, 27-30 degrees unreliably): full PDF not downloaded. https://repository.upenn.edu/handle/20.500.14332/34153
- Heverly et al. 2013, "Traverse Performance Characterization for the MSL Rover", J. Field Robotics 30(6):835-846 (source of slip-vs-slope tables and the Scarecrow dune tests): not found open access.
- Arvidson et al. 2014 JGR (deepblue, 403): https://deepblue.lib.umich.edu/bitstream/2027.42/108017/1/jgre20266.pdf
- Zhurong slip estimation (MDPI Applied Sciences 12(9):4789, 403): https://www.mdpi.com/2076-3417/12/9/4789
- Spirit slip analysis PDF (WVU, 403): https://yugu.faculty.wvu.edu/files/d/6ec90de4-d996-405b-b2e7-61b5ec354ad6/spirit_slip_analysis_istvstemplate__copy___to_be_submitted_.pdf
- KISS xTerramechanics PDFs (SSL or 404): https://kiss.caltech.edu/workshops/xTerra/presentations1/arvidson_poster.pdf ; https://www.kiss.caltech.edu/papers/xterramechanics/papers/simulations.pdf ; https://kiss.caltech.edu/workshops/xTerra/presentations1/lindemann.pdf (not attempted after SSL failure)
- JPL PIA07999 Purgatory image page (403): https://www.jpl.nasa.gov/images/pia07999-looking-back-at-purgatory-dune
- AGU 2014 abstract on Curiosity slip (search hit only): https://agu.confex.com/agu/fm14/webprogram/Paper16792.html
- escholarship ISTVS-type PDFs surfaced by search, 0 bytes: https://escholarship.org/content/qt1zp5c78w/qt1zp5c78w.pdf ; https://www.escholarship.org/content/qt05f4t7gq/qt05f4t7gq.pdf?t=s16ww9
- Berkeley EDG ISTVS 2021 page (not opened): https://edg.berkeley.edu/publication/istvs2021
- AMADEE-18 INAF open access paper (SSL failure): https://openaccess.inaf.it/bitstreams/61cfd538-d139-49c6-b9b1-368625e3f26c/download
- arXiv 2411.13978 (European Moon Rover System analogue test campaign): surfaced, not opened.
- SAE paper 2002-01-0284 and other Arabian-region tyre-on-sand items: paywalled or off-topic, not opened.
Row-level cautions: FLD-006/007/008 come from a 2004 JPL press release (Mars Daily repost), not the underlying plots. FLD-023 (Perseverance tilt limit linked to Scarecrow dune test) rests on PDF text with garbled line order; verify against Heverly et al. 2013. FLD-021 is a secondary citation (Kilic et al. citing Arvidson 2017).
