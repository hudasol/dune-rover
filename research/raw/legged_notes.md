# Legged / tracked / wheel-design evidence for dune-rover (secondary scope)
Rows: 24 in legged_rows.csv (LEG-001..LEG-024), 12 distinct sources. Retrieval date 2026-10-11. Working copies in <repository root>/research/sources/.

## SEARCH_LOG
- WebSearch: RHex/SandBot on sand; quadruped/granular/dune; Qian/Goldman appendage design; ANYmal/Spot/Unitree sand slope; wheel-leg hybrids on sand; wheel-vs-leg RFT; legged field tests White Sands; tracked vs wheeled sand; sandfish swimming robots; tracked robot slope climbing; learned quadruped on deformable terrain; tracked-vs-wheeled drawbar (extended).
- Downloaded and read (pdftotext): arXiv 1303.7276 (leg_kinematics), 0905.4950 (li2009), Goldman SPIE 7679 (spie_goldman), arXiv 2603.06928 (granular_slopes_legged), arXiv 2106.01974 (kolvenbach_martian), Frontiers frobt.2021.740927 (frontiers_hop), arXiv 2609.10286 (gmloco), Ritsumeikan thesis k_1348 (ritsu_wheelleg), Yoshida ICRA2010 slides (yoshida_traction), Skonieczny IROS2012 (skonieczny2012), arXiv 2306.02167 (velocity_traction), arXiv 2310.00033 (oriwheelbot). Also read but yielded no row: Qian 2015 Bioinspir. Biomim. (qian_bb), Li-Zhang-Goldman RFT arXiv 1911.00079, COTS legged arXiv 2106.07182, Kim and Lee arXiv 2107.02955 (simulation on elastic tiles, not sand), Jia et al. Robotica 2012 (wheel model only), Hwang et al. arXiv 2604.02744 (not sand).
- No retrieval failures on allowed hosts (arXiv, IEEE ewh, CMU, Ritsumeikan, Frontiers, gatech). One transient HTTP/2 error on arXiv fetch, resolved by retrying. DTIC ADA460934 returned HTML, not a PDF.

## KEY_FINDINGS
1. Gait/limb design dominates legged performance on loose granular media, more than robot mass. Same SandBot: ~2 cm/s with a hard-ground gait vs ~8 cm/s with soft-ground gait (LEG-001, LEG-002); ~20 cm/s vs ~2 cm/s for a 5% change in packing fraction (LEG-003, LEG-004). Sprawled DASH reached ~5 BL/s where upright RoACH managed ~5 cm/s on the same loose bed (LEG-005, LEG-006). All lab poppy-seed beds, not dune sand.
2. On slopes the failure mode is slip, not sinkage. A 350 g hexapod on 300 um glass beads lost ~30% speed at 10-15 deg and ~two thirds by 20-24 deg (15.7 to ~5 cm/s) because shear resistance falls and anchoring is delayed (LEG-007..009). SpaceBok (22 kg) showed the same: planar feet slipped near the soil friction angle and energy per distance about tripled above ~20 deg; point feet sank up to 120 mm but resisted slip (LEG-010, LEG-012, LEG-013).
3. Foot area and foot-pad grousers trade sinkage against traction for legs: large planar feet limit sinkage on collapsible soil; 12 mm grousers raised foot traction coefficient 22% on ES-3 sand-like simulant (LEG-011). Trot was >2x more energy efficient than static walk below ~20 deg but riskier above (LEG-012, LEG-013).
4. For wheels, larger diameter and width strongly cut slip on Toyoura sand at equivalent slope loads: D 116 mm to 327 mm gave slip 0.741 to 0.056 at 12 deg equivalent (LEG-017, LEG-018); width 50 to 150 mm gave 0.471 to 0.247 at 14 deg (LEG-019, LEG-020). Narrow wheels fail where wide ones climb (OriWheelBot, 17 deg only at 72 mm; LEG-023, LEG-024). Grouser count has a saturation point (about 24 for 13 mm grousers on a 114 mm radius wheel, LEG-021). Flexible wheel gave >2x drawbar pull and 18% lower sinkage than rigid at 1 m/s on olivine sand (LEG-022).
5. Tracks vs wheels: the only retrieved direct comparison (Yoshida slides, Toyoura sand, mono-crawler vs four inline wheels) concludes tracks outperform wheels on soft sand with much smaller sinkage resistance, but the quantitative slip numbers on the key slide are not unambiguously attributable (see GAPS), so no track row recorded. Wheel-paddle hybrid on field sand reached ~1 BL/s (24 kg) but sand was the least efficient terrain (LEG-016). A humanoid with an RFT-trained policy walked on real dry sand at up to 2.5 m/s commanded where a rigid-contact policy failed above 1.5 m/s (LEG-015, field, learning).

## GAPS
- No numeric legged-robot data on real dunes or natural loose sand slopes with sinkage and success rates (ANYmal, Spot, Unitree quadrupeds). Roberts and Koditschek mention White Sands/Tengger trips and motor overheating but give no field CoT number in the retrieved text.
- Absolute cost of transport for legged vehicles on sand not extracted (SpaceBok reports relative changes; Goldman SPIE gives CoT only graphically). Roberts and Koditschek report jump energy savings, not horizontal CoT.
- Tracked vehicles on sand: no extractable numeric rows (sinkage, motion resistance, drawbar). The Yoshida slide 33 pair (slip 0.054 vs 0.774, 9 kg, 10 deg) is ambiguous: the image appears to show wheel on the left and track on the right, which conflicts with the stated conclusion that tracks outperform wheels, so it was not recorded. Graphical drawbar-pull curves not digitized.
- Sand-swimming (sandfish) robots are subsurface locomotion and were not treated as traversability evidence.
- Wheel diameter/width effects come from one slide deck (Toyoura sand, parameters not reported on slides) and a small origami wheel with uncharacterized sand; no peer-reviewed numeric diameter/width sweep on dune-like sand retrieved. Wheel mass not stated for Yoshida wheel series.
- Non-pneumatic/flexible tire numbers on dry sand are limited to the olivine single-wheel test (LEG-022); no Whegs or RHex-on-dune numbers.
- No direct same-vehicle wheel-vs-leg-vs-track comparison on dry sand.
- Intermediate values not in rows: Yoshida D=202 mm slip 0.229 (12 deg), width 100 mm slip 0.320 (14 deg); Liao 15 deg 10.5 cm/s and 20 deg 4.98 cm/s; Skonieczny 10 mm grousers predicted minimum 29, 6 mm predicted 42 (consistent with experiment, observed rising to 48).

## NOT_RETRIEVED
Abstract/snippet-only or paywalled; no numbers recorded.
- https://www.sciencedirect.com/science/article/abs/pii/S0094114X18312783 (power consumption of tracked and wheeled small robots on deformable terrains)
- https://www.sciencedirect.com/science/article/abs/pii/S0022489818300624 (experimental study of a tracked mobile robot's mobility)
- https://www.sciencedirect.com/science/article/pii/S277237552200096X (locomotion system comparison, agricultural drawbar works)
- https://elib.dlr.de/128403 (full text not open; the arXiv version 2306.02167 was used instead)
- https://kyutech.repo.nii.ac.jp/record/2000944/files/sei_k_486.pdf (wheel/track agricultural thesis; PDF 16.8 MB not read)
- https://apps.dtic.mil/sti/pdfs/ADA460934.pdf and https://apps.dtic.mil/sti/pdfs/ADP004261.pdf (returned HTML, not read)
- https://par.nsf.gov/servlets/purl/10100725 and https://asu.elsevierpure.com/en/publications/mechanics-of-bipedal-and-quadrupedal-locomotion-on-dry-and-wet-gr (search hits only; animal locomotion)
- https://research-collection.ethz.ch/handle/20.500.11850/625001 (Towards Legged Locomotion on Steep Planetary Terrain; record page only)
- https://research-collection.ethz.ch/bitstream/handle/20.500.11850/355281/IROS19___Dynamic_Locomotion_on_Slippery_Ground.pdf (not read)
- https://repository.upenn.edu/ese_reports/23 (RHex Slips on Granular Media; record only)
- https://news.oregonstate.edu/news/researchers-are-teaching-robots-walk-mars-sand-new-mexico (news item, snippet only)
- https://www.researchgate.net/publication/224090983 and https://k-nagatani.org/pdf/2009-IROS-AYA-online.pdf (drawbar of wheeled robots on sand; not fetched)
