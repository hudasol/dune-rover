# Phase 2 literature retrieval: dune morphology for 30 m DEM slip face probability

Retrieval date 2026-10-11 (as requested). All numbers below are in `phase2_morphology.csv` (ids PM01 to PM38) with passage locations. Fetched files are in `src/` (ignored through `research/phase2/.gitignore`; the repo root `.gitignore` does not cover `research/phase2/`, and I did not edit it). Values marked DERIVED are my arithmetic on retrieved numbers, not published figures. Values marked ABSTRACT were read from an abstract only. Nothing was taken from memory.

Not repeated, as instructed: angle of repose 32-35 deg (Kroy 2002), critical angle 32.2-32.35 (Pelletier 2015), Liwa height 50-80 m, Guth/Lancaster tables, USGS PP1052.

## Headline

The literature that was retrievable open access supports good numbers for stoss slope of barchans and transverse dunes, for the geometry of an active slip face (run per unit height), and for Rub' al Khali dune dimensions. It supports almost nothing for star dunes, for the fraction of crest length with an active slip face, for lee slope on rounded (inactive) faces, for brink curvature, or for coarse DEM slope bias. These are real gaps, not search failures that more of the same queries would fix; several relevant papers sit behind publisher paywalls or blocked hosts (listed at the end).

## Need 1. Stoss slope angles

| Dune type | Value | Source (CSV id) | Basis |
|---|---|---|---|
| Barchan | 8-20 deg typical | Herrmann 2002 (PM01) | SECONDARY review of Peru/Namibia/Morocco barchan fields |
| Transverse (coastal) | mean about 6 deg (tan 0.10 +/- 0.02); r = H/L0 0.062-0.110 | Parteli et al. preprint (PM02, PM06) | PUBLISHED field, tachymeter, 6 dunes, 7-10 m high |
| Linear (Niger, small) | height/half-width 0.3 +/- 0.05, so mean flank about 17 deg (14-19) | Lucas et al. 2015 (PM04) | PUBLISHED DEM (Pleiades 4 m), DERIVED angle; dunes 1-10 m high |
| Linear (Taklimakan) | H:W 0.09, stoss shallower than Namib | Potts et al. 2008 (PM05) | ABSTRACT only, ratio definition unclear |
| Generic field dunes | 2-20 deg | Kolli et al. 2026 citing Lancaster 1995, Wu 2003 (PM03) | SECONDARY, originals not retrieved |

Supported range for barchan/crescentic stoss flanks: roughly 6-20 deg, with the larger transverse field sitting at the low end (about 6 deg averaged over the whole windward side). Linear dune flank slope is only supported at about 14-19 deg for small dunes, and that is a mean over both flanks, not a stoss versus lee split.

NOT FOUND: any stoss slope distribution (histogram, percentiles) for barchan, crescentic, linear or star dunes at tens-of-metres dune height; any star dune slope number. Large-dune stoss slopes must be extrapolated, which is risky because aspect ratio is not scale invariant (Elbelrhiti: barchan H/W about 1/15 on small dunes, PM07).

## Need 2. Slip face height fraction and share of crest with an active slip face

- Transverse dunes, Lencois (PM08): Hbrink/Hcrest = 0.69, 0.98, 1.00, 0.71, 1.00, 0.54 (DERIVED from Table 1; heights are measured from the foot of the slip face). So 0.54-1.0 for six dunes of 7-10 m. Brink offset from crest dc = 0-35 m (PM11).
- Barchans (PM09): brink coincides with crest in many cases, so slip face height approaches dune height; no distribution published in what I retrieved.
- Large compound dunes, linear dunes with superimposed forms, star dunes: NOT FOUND. No retrieved source gives slip face height as a fraction of total height for dunes of 50-150 m. This matters most for the target case, since a slip face on the upper flank of a 100 m dune may be only a small fraction of its relief.
- Share of crest length with an active slip face: NOT FOUND as a number. The only quantitative-adjacent information is qualitative: Namib/Kalahari simple linear dunes of morphometric class 2 have occasional small slip faces, class 3 none (PM12). The Kreslavsky lidar abstract shows slip faces can vanish entirely from a 6 km2 area within weeks under atypical wind (PM19), so any time-averaged probability is wind regime dependent.

## Need 3. Horizontal run of the lee face and stoss to lee ratio

- Active slip face run: Ls = H / tan(repose), repose 31-35 deg, so run is 1.43-1.66 times its height (PM10; ratio DERIVED from Herrmann eq. 5). For a slip face 10 m high, run is about 14-17 m, i.e. about half of one 30 m cell.
- Barchans in SE Iran, eight dunes (PM13): Lo/Ls = 2.9-6.9 (mean 5.4, DERIVED from Table 2), measured on Google Earth imagery of small dunes (L 75-208 m); Ls definition is ambiguous so treat with caution.
- Lencois transverse dunes (PM14): stoss length L0 over slip face run 6.1-19.9, DERIVED using the paper's assumed 34 deg.
- Rub' al Khali wavelengths (PM31): mean 1.5 km at the dune-field centre falling to about 0.1 km at the margin.
- NOT FOUND: asymmetry index (stoss to lee horizontal length ratio) for linear, star or megabarchan dunes of tens of metres. The Cazenave et al. paper that computes asymmetry ratios for the Rub' al Khali (Earth Surf. Process. Landforms) is paywalled; its abstract (retrieved) gives no numbers. Beelen's arXiv preprint tabulates lee to stoss ratios for many barchan fields but the data are in a supplement I could not retrieve; it is also not peer reviewed, so I did not use it.

## Need 4. Brink and crest curvature

- Lencois (PM16): near the crest the windward profile follows y = -k1 x^2 with k1 = 0.0025, which implies a crest radius of curvature of about 200 m (DERIVED, assuming metre units). This describes the rounded crest upwind of the brink, on dunes with a slip face.
- NOT FOUND: any measured brink radius of curvature, any measured crest curvature for dunes whose slip face is inactive, any quantitative statement of how fast a brink rounds after wind reversal. The qualitative statement that slip faces disappear when wind changes is in PM19. A 30 m DEM cannot resolve a brink radius anywhere near this scale in any case.

## Need 5. Lee slopes on rounded versus active faces

- Active slip face slope from lidar (4 m baseline): sharp peak at 32.5 deg at White Sands and 29.5 deg at Great Sand Dunes (PM18). The two fields differ by 3 deg, so a fixed 32-35 deg is not universal for quartz sand.
- Same White Sands area when the slip faces were inactive: the peak is absent and slopes above 30 deg are infrequent (PM19), but no replacement lee slope value is published.
- The proposition "lee slopes 20-30 deg on non-active linear dune faces" is NOT supported by any retrieved source (PM20). Do not cite it. The Rub' al Khali paper records a "lee-slope expression" attribute per dune (in the abstract) but the text reports no values for it.
- Caution for large dunes: Dong et al. (Frontiers in Earth Science 2022, Badain Jaran, 360-430 m megadunes) say exposed beds on windward slopes dip at the repose angle, which is internal stratigraphy rather than surface slope, but it hints that very large dunes can have steep windward faces. I did not add it to the CSV because it is not a surface slope measurement; it is a lead.

## Need 6. DEM resolution versus field/lidar slope

No retrieved study compares slope estimated from SRTM, ASTER, Copernicus or any 30-90 m DEM against lidar/TLS/field slope over a dune and reports the bias (PM28, NOT FOUND). What exists is indirect:

- ASTER GDEM underestimates dune height and cross-sectional area by about 10% on average versus DGPS profiles (PM21; Namib dunes 50-102 m, Kalahari 11-20 m). This is height, not slope.
- ASTER GDEM smooths dune crests and omits the smallest dunes (PM22, ABSTRACT); minimum detectable dune height is quoted as 20-30 m (Namib) and 15 m (Badain Jaran) (PM23, SECONDARY).
- SRTM 90 m resolves breaks in slope less well than ASTER 30 m over the Liwa star dunes (PM24, qualitative).
- Vertical error figures: SRTM 16 m absolute / 10 m relative (PM25, SECONDARY); GLO-30 RMSE 1.1 m versus ICESat-2 in NW Namibia (PM27, ABSTRACT, not dune specific).
- The only lidar slope statistics found are at a 4 m baseline (PM18), which shows a distinct slip face spike. There is no published statement of what that spike becomes at 30 m.

Unsourced reasoning for the model, not a published number: a slope computed from a 30 m grid over a 3x3 window averages over 60-90 m of ground. A slip face run of 1.4-1.7 H (PM10) is shorter than one cell when H is below about 20 m, so the 30 m slope of a cell containing a slip face should fall well below repose unless the dune is high. This is a geometric expectation to be tested against your own DEM-versus-lidar data, not something I found in the literature.

## Need 7. Study area candidates

| Area / type | Values | Source (CSV id) | Basis |
|---|---|---|---|
| Rub' al Khali, all types (555 dunes) | height <5 m (margin) to >155 m (centre); spacing 0.63-8.41 km, mean 3.05; Table 1 height 67-218 m, mean 144 (table scope unclear) | Al-Masrahy and Mountney (PM29, PM30) | PUBLISHED, SRTM-based |
| Rub' al Khali compound linear (W/SW) | mean spacing 3.9 km, >130 m high, lengths to 50 km, interdune width to 1.4 km | PM32 | PUBLISHED |
| Rub' al Khali star (E/SE margin) | mean width 2.1 km, height up to 120 m | PM33 | PUBLISHED |
| Rub' al Khali compound crescentic (N/NE) | width 2.8 km, length 2.1 km, relief up to 160 m | PM34 | PUBLISHED |
| N Rub' al Khali, UAE, Oman, Saudi complex linear | 50-100 m high, spaced 2-5 km | Lancaster et al. 2004 (PM35) | ABSTRACT |
| Namib simple linear (analogue) | height mean 22 m (7-66), wavelength mean 972 m (475-2674) | PM36 via White et al. | SECONDARY |
| Namib linear (IKONOS) | width mean 736 m, spacing mean 2203 m | PM37 | ABSTRACT |

Good second study area candidate: the Rub' al Khali linear dune belt (50-130+ m high, 2-5 km spacing, UAE/Oman/Saudi), which is morphologically very different from Liwa megabarchans and star dunes. The Namib simple linear dunes (7-66 m) are a smaller-scale, better-documented analogue, and they are the only linear dune system for which a DEM-versus-field comparison exists (PM21).

Wahiba Sands, Oman: NOT FOUND (PM38). Retrieved abstracts describe linear megadunes and barchanoid dunes qualitatively but give no heights or wavelengths. Several Wahiba sources were blocked or abstract-only.

## What was blocked or not retrievable

Hesp and Hastings 1998 (barchan width, height, slope relationships; the most likely source for need 2 and 3 on barchans), Hugenholtz and Barchyn 2010 and 2012 (only abstracts, no numbers), Cazenave et al. (Rub' al Khali asymmetry, paywalled), Tsoar and Livingstone Namib/Sinai linear dune surveys (no open text), Nielson and Kocurek star dune papers, a Texas Tech thesis on Rub' al Khali dune morphology (host returned 403), the Wahiba Arabian J. Geosci. article (bot challenge), and several Iranian journal hosts (connection reset by the egress proxy). I did not try to route around any block.

## Suggested use for the model

1. Treat 6-20 deg as the prior for stoss slope on barchan and transverse flanks, and expect a 30 m DEM to report less.
2. Use run = 1.4-1.7 times slip face height to turn a height prior into a footprint; the height fraction (0.5-1.0 for 7-10 m dunes) is not known for large dunes and should be a free parameter.
3. Do not assume 20-30 deg lee slopes for inactive linear dune faces; no source supports it.
4. Calibrate DEM slope bias yourself against a lidar or UAV patch; the literature does not provide it.
