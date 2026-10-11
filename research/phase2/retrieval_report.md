# Phase 2 retrieval report

Retrieval session date used in files: 2026-10-11. All quotes are 12 words or fewer. Numbers below were read from the retrieved text named in each item (or, where marked "computed", derived by arithmetic from numbers printed in that text).

Housekeeping notes
- `research/phase2/` is NOT gitignored: `.gitignore` only ignores `research/sources/` and `research/verify_sources/`, and `git status` shows `research/phase2/` as untracked. I did not edit `.gitignore`. Do not `git add` this folder until it is ignored or the downloaded PDFs are removed.
- A `research/phase2/src/` folder (A23nature, A30, P20, P28 files) appeared during my session. I did not create it.
- Local copies: `kern.pdf`, `kern.txt`, `kern_raw.txt`, `cop/` (licence PDF, handbook, AWS readme, CDSE page), `oa/` (probe outputs, JPL MSL slides), `wong/` (secondary papers checked for item 2).

## Summary table

| # | Item | Status |
|---|------|--------|
| 1 | Copernicus DEM GLO-30 licence | FULL TEXT READ |
| 2 | Wong dry-sand Bekker/Wong table | NOT RETRIEVED (no open reprint with a verifiable citation found) |
| 3 | Wong and Reece 1967 | NOT RETRIEVED |
| 4 | Ishigami 2007 and Ishigami, Nagatani, Yoshida 2009 | NOT RETRIEVED |
| 5 | Yu et al. 3D-RFT | ABSTRACT ONLY (and the paper is a journal paper, see below) |
| 6 | Heverly et al. 2013 | NOT RETRIEVED (a related JPL slide deck by Heverly was read) |
| 7 | Takehana et al. 2025 | NOT RETRIEVED (open access, but publisher blocks the proxy); ISTVS 2024 conference precursor ABSTRACT ONLY |
| 8 | Kern et al. 2026, arXiv 2601.04547 | FULL TEXT READ |

---

## 1. Copernicus DEM GLO-30 licence: FULL TEXT READ

Controlling text found:
- Licence name (heading in the licence document): "Licence for Copernicus DEM instance COP-DEM-GLO-30-F Global 30m Full, Free & Open", sub-titled "Licence for the use of the Copernicus WorldDEM-30".
- Where: PDF "Copernicus Contributing Mission Data Access" licences bundle, PDF pages 22 to 24 (of 24). The GLO-30-F licence starts on page 22; Articles 3 to 8 are on page 23; Article 9 on page 24.
- URL used: https://dataspace.copernicus.eu/sites/default/files/media/files/2025-06/copernicus_contributing_mission_data_access_v2_cop_dem_licenses.pdf (saved as `cop/cop_dem_licenses.pdf`). The bundle's first licence (restrictive CCM terms) is dated "Issue date: 21/02/2025"; the GLO-30-F licence text itself carries no issue date.
- Linked from: https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM ("Licensing and citation guidelines" section says GLO-30 and GLO-90 "are available worldwide with a free license"). The DOI https://doi.org/10.5270/ESA-c5d3d65 resolves to this same CDSE page.
- AWS Open Data registry entry https://registry.opendata.aws/copernicus-dem/ (License field) says GLO-30 Public and GLO-90 are free to the general public under "the terms and conditions of the Licence", and its link points to the CDSE page above. The registry is therefore not itself the licence. The AWS dataset provides "GLO-30 Public", a subset (a small set of tiles for specific countries is not released); the readme is https://copernicus-dem-30m.s3.amazonaws.com/readme.html.
- Not reachable: spacedata.copernicus.eu (connection reset by the proxy, three paths tried, not retried further). The Copernicus DEM Product Handbook v5.0 (29.11.2022, `cop/handbook.pdf`, from dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf) was read for licence terms: it contains no licence text (no match for "licen[cs]e"). It is a technical document only.

Extracted terms (GLO-30-F licence, page.article):
- Commercial use: permitted in effect. Article 4 (p.23) grants non-exclusive rights of reproduction, distribution, communication to the General Public, and adaptation, modification and combination with other data. Article 5 (p.23): rights are "free of charge". "General Public" is defined (Art. 2, p.22) as any natural or legal person. A text search of the whole GLO-30-F section for "commerc", "non-comm" and "profit" returned nothing, so no commercial restriction exists. The text is silent on the word "commercial" rather than granting it expressly. Article 3: rights are worldwide and without limitation in time.
- Redistribution of derived products: allowed. Article 4(b) and 4(d) plus Article 6(b), 6(c) and 6(e) (p.23) attach conditions: modified or adapted data need the "produced using" notice; redistributors must pass the no-liability sentence to recipients; and anyone sub-granting distribution rights must bind subsequent users to the same obligations. Article 6(d): do not imply official endorsement by the Provider, Licensor or Copernicus bodies.
- Attribution wording required (Art. 6(a), p.23), for communicating or distributing the data: the notice begins "© DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018" and continues with the "provided under COPERNICUS by the European Union and ESA" clause ending "all rights reserved". Verbatim text is at line 1155 of `cop/lic.txt` (pdftotext of page 23). The same notice appears on the CDSE page.
- Attribution for adapted or modified data (Art. 6(b), p.23): a notice that begins "produced using Copernicus WorldDEM-30" followed by the same copyright and "provided under COPERNICUS" wording as above (verbatim at line 1158 of `cop/lic.txt`).
- Liability sentence (Art. 6(c), p.23) must be added to any licence or legal notice when distributing to the public; it says the organisations in charge of Copernicus "do not incur any liability" for use of the data (verbatim in `cop/lic.txt`).
- Warranty (Art. 7, p.23): data supplied "as is"; user indemnifies Licensor, Copernicus entities and Provider.
- IPR (Art. 9, p.24): Provider (Airbus) keeps IPR; no right to Provider trademarks or logos unless authorised; Copernicus trademark used under its separate trademark licence.
- Termination (p.24): breach of obligations lets the Licensor terminate, with loss of rights.
- Scope limits: the 10 m resolution (WorldDEM-10) is expressly excluded from this licence (Preamble, p.22) and is under separate, restricted terms. Other licences in the same PDF (COP-DEM-GLO-30-R, EEA-10-R, and the older GLO-90 licence) are different documents; the restrictive licences earlier in the same PDF (the CCM licence on pp.1-8 and GLO-30-R/EEA-10-R) contain non-commercial wording (for example on pp.5-6 and near line 738 of `cop/lic.txt`) that does NOT apply to GLO-30-F. Confirm the tiles you use are the Free and Open instance (GLO-30 Public on AWS is derived from COP-DEM_GLO-30-DGED per the AWS readme).
- Handbook facts (for context): vertical datum EGM2008 (EPSG 3855), DSM not DTM (handbook spec tables and CDSE page).

## 2. Wong, Theory of Ground Vehicles, dry-sand Bekker/Wong table: NOT RETRIEVED

No open source that both reprints Wong's table and cites it was verified.
Sources fetched and read, none acceptable as a Wong reprint:
- https://arxiv.org/pdf/2606.06790, Table 2 (p.10): dry sand column cites Jia, Smith and Peng, Robotica 2013 (ref [51]), with values the authors state were manually adjusted for n, c and phi. Not Wong.
- https://www.atlantis-press.com/article/25838612.pdf (Sun, Di, Cui, MEITA 2015), Table 1, p.986: lists a "Dry sand" column with n 1.1, c 1.0 kPa, phi 30.0 deg, kc 0.9, kphi 1523.4, k 0.025 m. The table has no citation to Wong, units are garbled ("kPa/ m n -1"), and Wong is cited only for pressure theory. Do not use as Wong's table.
- https://proceedings.sbmac.org.br/sbmac/article/download/4643/4704/9082 (Rodrigues and Lopes, CNMAC 2024), Table 1: cites Wong 2022 but the Sand row repeats the Clay kc value and has no c, phi, K. Unreliable.
- https://arxiv.org/pdf/2510.12169 Table I uses "Loose dune sand", values not from Wong. https://arxiv.org/pdf/1901.10667 and https://crablab.gatech.edu/pages/publications/pdf/Terramechanics-2019.pdf cite Wong but contain no dry-sand parameter table.
- Blocked: apps.dtic.mil ADA566231 and AD1082843 (bot challenge pages), birzeit.edu repository (403), mjae.journals.ekb.eg PDF (connection reset).

To fetch and upload: J. Y. Wong, "Theory of Ground Vehicles", 4th ed., Wiley, 2008 (ISBN 978-0-470-17038-0), chapter 2 (terrain-vehicle table of Bekker/Janosi parameters: n, kc, kphi, c, phi, K); or 5th ed. 2022. Alternative: J. Y. Wong, "Terramechanics and Off-Road Vehicle Engineering", 2nd ed., Butterworth-Heinemann, 2010. Please upload the page(s) containing the terrain parameters table.

## 3. Wong and Reece 1967: NOT RETRIEVED

Identified record (verified through Unpaywall and Semantic Scholar metadata): J. Y. Wong and A. R. Reece, "Prediction of rigid wheel performance based on the analysis of soil-wheel stresses part I. Performance of driven rigid wheels", Journal of Terramechanics 4(1), 1967, pp. 81-98, DOI 10.1016/0022-4898(67)90105-X. Unpaywall: no open-access location. Semantic Scholar: closed. ScienceDirect returns 403 to the proxy. No repository copy found. Part II (towed wheels) is a different paper, not retrieved.
To fetch and upload: the DOI above (ScienceDirect or institutional access).

## 4. Ishigami 2007 and Ishigami, Nagatani, Yoshida 2009: NOT RETRIEVED

Identified records:
- G. Ishigami, A. Miwa, K. Nagatani, K. Yoshida, "Terramechanics-based model for steering maneuver of planetary exploration rovers on loose soil", J. Field Robotics 24(3):233-250, 2007, DOI 10.1002/rob.20187. Unpaywall: not OA; Semantic Scholar: closed.
- G. Ishigami, K. Nagatani, K. Yoshida, "Slope traversal controls for planetary exploration rover on sandy terrain", J. Field Robotics 26(3), 2009 (pages 264-286 per the reference list of https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1320261/pdf), DOI 10.1002/rob.20277. Unpaywall: not OA.
Other routes tried and what they gave:
- Ishigami PhD thesis record (Tohoku 2008) at https://repository.exst.jaxa.jp/dspace/handle/a-is/35905: abstract only, "no files".
- Yoshida ICRA 2007 workshop slides (https://ewh.ieee.org/conf/icra/2007/workshops/SpaceRobotics/07Yoshida/ICRAWorkshop-Yoshida.pdf, read in full, 39 pp.): no soil parameters. It lists slope tests at "Slope angle [deg] 5.0 / 7.5 / 10.0" but no slip numbers in the text layer. Not usable for numbers.
- Sakayori and Ishigami 2024 (Frontiers, open access) uses Toyoura sand in a single-wheel testbed and cites the 2009 paper but does not print Bekker/Wong parameters; not a substitute.
To fetch and upload: both DOIs above (Wiley), or the Ishigami thesis (Tohoku Univ., 2008, "Terramechanics-based analysis and control for lunar/planetary exploration robots") if a full text can be obtained.

## 5. Yu, Pavlov, Kim, Johnson, 3D-RFT and sand deformation: ABSTRACT ONLY

Important correction to the brief: https://2024.istvs.org/submissions/papers/2919 is a different paper ("Accurate Rover Mobility Analysis Using HILS-DRFT with Real-Time Parameter Tuning Approach", Fuke, Ishikawa, Ishigami). I also listed all 52 papers on the ISTVS 2024 submissions site; none is the Yu et al. paper. The Yu paper is a journal article: Q. Yu, C. Pavlov, W. Kim, A. M. Johnson, "Modeling wheeled locomotion in granular media using 3D-RFT and sand deformation", Journal of Terramechanics, vol. 115, article 100987, 2024, DOI 10.1016/j.jterra.2024.100987 (confirmed by Semantic Scholar, the CMU CV https://www.andrew.cmu.edu/user/amj1/JohnsonAaronCV.pdf and the ISTVS publication-news page https://istvs.org/publication-news/modeling-wheeled-locomotion-in-granular-media-using-3d-rft-and-sand-deformation, which could only be read through the web fetch tool, not curl).
- What was read: the ISTVS summary and abstract only. It states the method (a sand deformation simulator for the soil surface combined with 3D-RFT, real-time force computation at 60 Hz). The text I could read reports NO prediction errors for slip, drawbar pull or sinkage. Prediction errors: not obtained.
- Unpaywall lists only a publisher landing page (accepted version, no PDF link). No arXiv version (arXiv API searches empty). CMU lab and personal publication pages render without links in static HTML.
To fetch and upload: DOI 10.1016/j.jterra.2024.100987 (https://www.sciencedirect.com/science/article/pii/S0022489824000296). The accepted manuscript may be requestable from the authors (Aaron Johnson, CMU Robomechanics Lab).

## 6. Heverly et al. 2013, J. Field Robotics 30(6): NOT RETRIEVED

Identified record (verified via Unpaywall and Semantic Scholar): M. Heverly, J. Matthews, J. Lin, D. Fuller, M. Maimone, J. Biesiadecki, J. Leichty, "Traverse Performance Characterization for the Mars Science Laboratory Rover", J. Field Robotics 30(6), 2013, DOI 10.1002/rob.21481. Not OA. Not found in NTRS (empty results) or the JPL Open Repository (dataverse.jpl.nasa.gov; searched by title and author).
Related open document that WAS read (not the JFR paper): M. C. Heverly, "Introduction to mobility for MSL", JPL slides dated 2012-09-10, JPL Open Repository hdl:2014/43242, file https://dataverse.jpl.nasa.gov/api/access/datafile/3819 (saved `oa/msl_mobility_intro.pdf`). Slide 21 ("Physical Hazards for the Rover"):
- Text: traversable slopes "< ~12.5 deg on sand" and "< ~25 deg on bedrock".
- Figure: "Dumont Dunes - Scarecrow Forward/Upslope", slip (%) against slope (deg), caption "Slip vs Slope curve for Scarecrow rover on wind blown sand". Values below are my visual read-offs from the plot (approximate, no data table printed): about 0-25 % slip near 5 deg, about 5-40 % near 8 deg, about 30-60 % near 13 deg, about 40-80 % at 14-15 deg, about 70-90 % near 17-19 deg, about 90-97 % near 22 deg.
- Because this is a slide image with approximate read-offs, and is not one of the 8 requested items, I did not put it in the CSV.
To fetch and upload: DOI 10.1002/rob.21481 (Wiley); JPL authors may supply the accepted version.

## 7. Takehana et al. 2025, J. Terramechanics 120, 101084: NOT RETRIEVED

Identified record: K. Takehana, G. Kenny, K. Sawa, J. Hurrell, K. Uno, S. Santra, K. Yoshida, "Grouser wheel high-speed traction performance: DEM simulation and experimental result", Journal of Terramechanics vol. 120, 101084, Oct 2025, DOI 10.1016/j.jterra.2025.101084, PII S0022489825000400 (author list from https://www.r-info.tohoku.ac.jp/en/7729cf0e46d3bd37e41d48a9b7a56830.html and the Elsevier API metadata).
- Open access: Elsevier API metadata (https://api.elsevier.com/content/article/doi/10.1016/j.jterra.2025.101084) states openaccess true, licence http://creativecommons.org/licenses/by/4.0/; Unpaywall lists a publisher published version. But https://www.sciencedirect.com/science/article/pii/S0022489825000400 (and the /pdfft route) returned HTTP 403 (bot protection, 833 KB HTML), and the Elsevier full-text API needs a key (401). I did not try to bypass this. The web fetch tool could not be used for that URL (permission request was not answered). No copy in arXiv, Europe PMC or Semantic Scholar.
- Conference precursor, ABSTRACT ONLY: Takehana, Sawa, Uno, Santra, Yoshida, "Evaluation of grouser wheel traction performance at high-speed by single-wheel test", ISTVS 2024, paper 0412, https://2024.istvs.org/submissions/papers/0412, DOI 10.56884/94WT27WY. Abstract says single-wheel tests up to about 1 m/s, three wheels (no, low, high grouser), traction coefficient and efficiency versus slip, and efficiency peaking "around a slip ratio of approximately 5% to 10%". No soil parameters or numbers beyond that. Full paper is purchase-only (ISTVS).
To fetch and upload: the CC BY 4.0 article at https://doi.org/10.1016/j.jterra.2025.101084 (PDF from a normal browser).

## 8. Kern et al. 2026, arXiv 2601.04547: FULL TEXT READ

URL used: https://arxiv.org/pdf/2601.04547 (v1, 7 pages, submitted 8 Jan 2026; abstract page https://arxiv.org/abs/2601.04547). Authors: J. M. Kern, J. M. Hurrell, S. Santra, K. Takehana, K. Uno, K. Yoshida. The arXiv comment says it is the author's version of a manuscript accepted at the International Conference on Space Robotics 2025 (iSpaRo 2025). Title: "Data-Driven Terramechanics Approach Towards a Realistic Real-Time Simulator for Lunar Rovers".

Equation 3, as printed (PDF p.3, Sec. III.B "Regression Models", left-hand side of the equation labelled (3)): s(vw .alpha) = (0.00522 vw + 0.00105) alpha^2 + s(vw). Coefficients printed: 0.00522 and 0.00105. Equation 2 (same page): s(vw) = 0.0265 vw + 0.0256. Equation 4 (sinkage, same page): z(s, Fz) = -33.56 s - 0.9291 (Fz - Fref) - 3.11, with z "expressed in millimeters (mm)".

Surrounding text: The text says alpha's effect was "captured by fitting a second-order polynomial" with coefficients parameterized by vw, and that the fits used averaged values from 16 independent experimental runs.

Unit of alpha: NOT stated anywhere in the text. Searches of the full text for "radian", "rad", "degree" in the model section found nothing near Eq. 3; the only unit given for slopes is degrees where the tests and validation range are described (Sec. III.A, p.3, and Sec. IV, p.5), and in the abstract ("slopes up to 20 deg"). So the unit of alpha is implicitly degrees by the surrounding use, but it is an inference, not a printed definition. Computed check (arithmetic from the printed coefficients, mine): if alpha is in radians, the slope term at 18 deg (0.314 rad) and vw = 0.47 m/s is about 0.0003 and total slip about 0.038, so slope would have almost no effect, contradicting the paper's premise that slope matters; if in degrees, slip at vw = 0.47 m/s is about 0.13 (5 deg), 0.39 (10 deg), 0.83 (15 deg) and 1.17 (18 deg). At vw = 0.23 m/s: 0.09 (5 deg), 0.26 (10 deg), 0.54 (15 deg), 0.76 (18 deg). A slip ratio above 1 at the stated edge of the tested envelope is outside the definition in Eq. 1 for climbing (slip = 1 - v/(omega R)), so the fit is only usable below roughly 15 to 17 deg at 0.47 m/s unless slower speeds were used at 18 deg (the text does not say).

Dimensional consistency: not as printed. s is dimensionless and alpha^2 carries the square of the angle unit, so the bracket (0.00522 vw + 0.00105) must have units of 1/(angle unit)^2, and its first term must further carry 1/(m/s). Likewise Eq. 2 needs 1/(m/s) on 0.0265. The paper prints no units for any coefficient; it is an empirical polynomial with hidden units, consistent only with vw in m/s and alpha in degrees (inferred). The equation is also even in alpha, so it gives the same slip for uphill and downhill slopes, although the conclusions mention "upward and downward slopes".

Ranges tested (Sec. III.A, p.3): flat terrain at wheel velocities vw = omega R of 0.23 to 1.17 m/s; slopes 0 to 18 deg at speeds up to 0.47 m/s; plus rapid acceleration and deceleration trials. Sec. IV states the simulation was checked on inclined terrain "up to 20 deg", which is beyond the 18 deg field range. Soil: Tohoku Silica No.5 dry loose silica sand, 20 m x 20 m area about 0.3 m deep; rover EX1, four wheels, 21.63 kg. Slip uses effective radius including grouser height (Eq. 1 discussion). No Bekker or Mohr-Coulomb soil parameters are reported.

Validation numbers (Sec. IV, p.5): flat slip error "below 0.02%" for speeds up to 1.17 m/s; slope mean absolute error 0.22 % for slopes up to 20 deg; average sinkage error 0.25 mm for contact force within +/-5 N of the 8.72 N reference load under lunar gravity. These compare the simulator with the paper's own regression models, not with independent field data. The only simulator-vs-field comparison is Fig. 7 (flat, vw = 1.17 m/s, qualitative). The conclusions state the regression models are "based on dry silica sand", unlike lunar regolith.

CSV rows: 7 candidate rows written to `phase2_rows.csv` (P2-001 to P2-007), all from this paper because it is the only FULL TEXT READ item reporting mobility results.
