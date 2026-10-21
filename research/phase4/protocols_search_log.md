# Search log, protocols (phase 4, 2026-10-21)

Scope: sources for two draft protocols, `docs/DRONE_SURVEY_PROTOCOL.md (written as a draft under research/phase4/drafts/ and moved there)` (drone photogrammetry of one dune with OpenDroneMap) and `docs/SAND_LAB_PROTOCOL.md` (angle of repose, bulk density, moisture, sieving, direct shear). The phase 3 rules in `research/phase3/AGENT_BRIEF.md` apply: full text only, live check of every DOI or URL, free access only, files only under `research/sources/phase4/`.

Output: 24 references in `research/phase4/protocols_references.csv` (5 OpenDroneMap documentation pages, 6 open access papers for the drone protocol plus 1 official GCAA page, 2 USDA manuals, 6 ASTM summary pages, 4 open access papers and 1 thesis already in the evidence table for the sand protocol). No evidence rows were written; these sources support methods, not new findings. Downloaded files are under `research/sources/phase4/protocols/`.

The run was interrupted once by a machine restart; all downloaded files were intact afterwards and the work continued from them.

## Searches

Hits returned is the number of results the tool showed. Screened means titles or landing pages checked. Retrieved means the full text (or, for web pages, the full page) was opened. Used means the source supports at least one step of a protocol.

| # | Database or tool | Exact query string or request | Date | Hits returned | Screened | Retrieved in full | Used |
|---|---|---|---|---|---|---|---|
| 1 | Direct fetch | docs.opendronemap.org pages: arguments, gcp, flying, outputs, tutorials, large | 2026-10-21 | 6 | 6 | 6 | 5 |
| 2 | WebSearch | UAV structure from motion photogrammetry sand dunes accuracy ground control points open access | 2026-10-21 | 9 | 9 | 0 | 0 |
| 3 | WebSearch | USGS unoccupied aircraft systems structure from motion photogrammetry data collection guide ground control check points report | 2026-10-21 | 10 | 10 | 0 | 0 |
| 4 | WebSearch | GCAA UAE unmanned aircraft system regulation drone registration permit official | 2026-10-21 | 9 | 9 | 1 | 1 |
| 5 | OpenAlex API (works by DOI) | 10.1002/esp.4637; 10.1002/esp.3609; 10.3390/rs10101606; 10.3390/rs11030239 | 2026-10-21 | 4 | 4 | 3 | 3 |
| 6 | Figshare API | article 9460049 (submitted version of 10.1002/esp.4637) | 2026-10-21 | 1 | 1 | 1 | 1 |
| 7 | WebSearch | UAV photogrammetry barchan dune DEM accuracy check points RMSE desert remote sensing mdpi | 2026-10-21 | 9 | 9 | 1 | 1 |
| 8 | WebSearch | coastal dune UAV SfM ground control points number vertical accuracy sand low texture study open access | 2026-10-21 | 9 | 9 | 2 | 1 |
| 9 | WebSearch | ASPRS Positional Accuracy Standards for Digital Geospatial Data Edition 2 Version 2 2024 pdf free download | 2026-10-21 | 9 | 9 | 0 | 0 |
| 10 | WebSearch | USDA NRCS Soil Quality Test Kit Guide pdf bulk density soil water content | 2026-10-21 | 9 | 9 | 2 | 2 |
| 11 | WebSearch | EM 1110-2-1906 Laboratory Soils Testing USACE pdf direct shear grain size | 2026-10-21 | 9 | 9 | 0 | 0 |
| 12 | WebSearch | angle of repose sand measurement fixed funnel method tilting box comparison open access paper | 2026-10-21 | 10 | 10 | 0 | 0 |
| 13 | WebSearch | "angle of repose" "fixed funnel" sand experimental method height diameter cone open access mdpi OR frontiers OR plos | 2026-10-21 | 10 | 10 | 1 | 1 |
| 14 | WebSearch | "tilting box" OR "tilting table" angle of repose granular material dry sand measurement method paper pdf | 2026-10-21 | 9 | 9 | 0 | 0 |
| 15 | WebSearch | regolith simulant angle of repose measured funnel pile height base diameter tan method repeated measurements open access journal | 2026-10-21 | 9 | 9 | 2 | 2 |
| 16 | Direct fetch | store.astm.org summary pages: d2216-19, d6913_d6913m-17, d3080_d3080m-23, d7263-21, d2937-17e02, c1444-00r23, d4253-16e01 | 2026-10-21 | 7 | 7 | 6 | 6 |
| 17 | Crossref API (query.bibliographic) | Experimental Study on the Minimum Required Specimen Width to Maximum Particle Size Ratio in Direct Shear Tests | 2026-10-21 | 2 | 2 | 1 | 1 |
| 18 | Crossref API (query.bibliographic) | Fundamental study on the effect of grain size distribution on angle of repose Kajiyama | 2026-10-21 | 2 | 2 | 0 (DOI of row 13 source resolved) | 0 |
| 19 | Crossref API (works by DOI) | 10.1002/esp.4637; 10.3390/rs10101606; 10.3390/rs11030239; 10.3390/drones5010007; 10.5194/isprs-archives-XLI-B1-1127-2016; 10.3389/frspt.2024.1303964; 10.3390/geosciences15060207; 10.3390/civileng3010005; 10.1002/esp.3609 | 2026-10-21 | 9 | 9 | not applicable (check only) | not applicable |
| 20 | Local file (phase 3 copy, read only) | research/sources/phase3/sanddunes/kfupm_dcpt.pdf, sections 3.3.4 and 5.1.2 | 2026-10-21 | 1 | 1 | 1 | 1 |

Notes on rows: in row 1 the page "large" (large datasets) was read but not needed. In row 8 the second retrieved item was a conference slide deck, excluded. In row 10 the two retrieved items are the Soil Quality Test Kit Guide and the Kellogg Soil Survey Laboratory Methods Manual (SSIR 42), both from nrcs.usda.gov; the host www.nrcs.usda.gov returned empty replies, the host without "www" worked. In row 16 the C1444 page returned HTTP 404 and the D4253 page shows the standard as withdrawn in 2025.

## Inclusion and exclusion

Included:

- Official software documentation (OpenDroneMap) for every processing option and default quoted.
- Open access peer reviewed papers that report UAV photogrammetry accuracy against independent check data, preferably on sand or high relief terrain (Sanz-Ablanedo et al. 2018; Nesbit and Hugenholtz 2019; Gafurov 2021, a dune complex; Long et al. 2016, a sand bank), and the reporting guidelines of James et al. (2019).
- The official UAE GCAA page, because the brief allowed UAE permission details only from a retrieved official source.
- Free official soil method manuals (USDA NRCS SSIR 42 and the Soil Quality Test Kit Guide) for density, moisture and sieving.
- ASTM summary pages, only to name standards by number and title and to quote their scope; the full standards were not read.
- Open access papers on the angle of repose (Kajiyama et al. 2024; Pawlowski et al. 2025; Louca et al. 2024) and on direct shear practice (Deiminiat et al. 2022); the thesis behind SND-021 to SND-024 for direct shear conditions on a dune sand.

Excluded:

- Osiberu, Choi and Ren, "Effects of Vegetation and Wind on Assessing Coastal Dune Changes Using UAV and Total Station Surveys" (PDF on lrgvdc.org): a slide presentation, not a paper; downloaded, read briefly and deleted.
- Search engine snippets, news articles about GCAA rules (gulfnews.com, khaleejtimes.com) and third party drone law summaries (uavcoach.com, bayut.com): secondary, not official.
- Gillan, Karl, Elaksher and Duniway (2017), Remote Sensing 9(5), 437 (USGS publications record screened): dryland erosion plots rather than dunes; screened only.
- USGS ground control point data releases (rows 3): data records, no method text.
- Commercial guidance pages (bettersizeinstruments.com) and a patent on angle of repose apparatus: not open method descriptions of the kind required.
- The ODM Docker image name: the documentation uses a placeholder, so the draft keeps the placeholder.

## Not retrieved

| Citation | Why | What would be needed |
|---|---|---|
| James, M. R., Robson, S. (2014). Mitigating systematic error in topographic models derived from UAV and ground based image networks. Earth Surface Processes and Landforms 39(10), 1413 to 1420. DOI 10.1002/esp.3609 (CC BY 4.0) | publisher PDF and full text pages returned HTTP 403 to this session; repository copies listed by OpenAlex were not tried within the time limit | open the publisher copy from another network or one of the repository copies; until then its advice is used only as summarised in the ODM documentation |
| ASPRS Positional Accuracy Standards for Digital Geospatial Data, Edition 2, Version 2 (2024) | announcement pages found; no PDF link found on the ASPRS news page | the free PDF from the ASPRS website, to align the accuracy report with a published standard |
| U.S. Army Corps of Engineers EM 1110-2-1906, Laboratory Soils Testing | publications.usace.army.mil answered "Access Denied" (HTTP 403 from the server) | a reachable copy of this public domain manual, which would give full open procedures for direct shear, sieving and water content |
| Kajiyama et al. (2024), publisher copy at e3s-conferences.org | HTTP 403 | not needed; the ISSMGE online library copy of the same paper was read in full |
| ASTM C1444 (angle of repose of mold powders, withdrawn 2005 according to Kajiyama et al. 2024) | the ASTM page returned HTTP 404 | the official page, before naming the standard in a protocol |
| ISO angle of repose standards (for example for solid fertilizers or for powders and granules) | only a third party catalogue page was found; no ISO page opened | the iso.org page with the title, then the decision whether to name it |
| Easter, Long-Fox, Britt, Brisset (2024), The effect of particle size distribution on lunar regolith simulant angle of repose. Advances in Space Research. DOI 10.1016/j.asr.2024.06.042 | found by Crossref; open access status not checked | an open copy |
| Long-Fox et al. (2023), cited by Louca et al. (2024) for the 500 g angle of repose tests | not searched within the time limit | search and open access check |
| Ground control point requirements for structure from motion derived topography in low slope coastal environments (PeerJ Preprints 1444) | the page served a browser challenge to this session | open the preprint PDF from another network |
| Rules of emirate level civil aviation authorities (for example Dubai) | not searched | the official authority page, before any statement beyond "obtain the required permissions" |
