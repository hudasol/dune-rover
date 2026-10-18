### 8.7 Phase 2: what the elevation model cannot see (SIMULATED BY ME, model assumption dependent)

> **SIMULATION ONLY, model assumption dependent.** Everything below describes a synthetic detector and a model, validated only against synthetic truth. No lidar, drone or field profile of a real Arabian slip face was retrieved, so the detector has never been tested against reality. The predictions for this stage were committed before the code was run (`docs/PREDICTIONS.md`, stage 2) and the hits and misses are recorded there.

**Problem.** A 30 m GLO-30 post spacing cannot resolve an active slip face, whose horizontal run is only about 1.4 to 1.7 times its height (morphology row PM10): a few metres to a few tens of metres. A cell that contains a face reads as a gentle slope. The phase 1 map was therefore binary and optimistic.

**Sub grid face probability.** For each cell I estimate the probability that an unresolved active face (28 degrees or steeper) lies inside the cell from four features the DEM does see: slope, crest convexity along the steepest direction, slope break (largest change of the signed slope component between the cell and its eight neighbours) and local relief in a 7 by 7 window (a proxy for dune height). The mapping is a logistic regression fitted on a synthetic ensemble of straight crested asymmetric dunes (stoss, brink, active face, apron, flat interdune) that are sampled the way a DEM samples them (mean over a post, or a point sample), separately for each posting (`src/dunerover/subgrid.py`). Truth in the ensemble is known exactly. Every range used is in Table 8.7a; only the stoss slope, the active face slope and part of the face height fraction have a published basis (retrieved morphology rows), and the rest are labelled assumptions. The share of dune crests that carry an active face is **not published** (not found), so the baseline assumes all of them do (pi = 1, the worst case) and the result is shown for pi = 0.6 and 0.3.

**Table 8.7a: ranges of the sub grid ensemble.**

{{TABLE:subgrid_params}}

**Three classes.** For each of 256 Latin hypercube draws of the four assumed slip parameters (friction angle, f_r, i0, i_max; fixed seeds 20261014, 20261015 and 20261016) a cell is passable if at least 4 of its 8 headings are passable; q is the share of draws in which it is passable. **BLOCKED** if q is at most 0.05. **TRAVERSABLE** if q is at least 0.95 and the face probability is below tau = 0.20. **UNKNOWN** otherwise, with the cause recorded: assumption sensitive (q between 0.05 and 0.95), sub grid face risk (face probability at least tau), or both. The threshold tau is a free choice; the coverage versus certainty table shows what it trades. Third area **C** is a window of linear dunes in the Saudi Arabian Rub' al Khali (20.40 to 20.55 N, 52.30 to 52.70 E, tile N20E052; not in the UAE), chosen because the UAE tiles held here show star and network dunes. It has a different morphology from windows A and B and is a robustness check, not a study of the UAE.

**Table 8.7b: class shares by DEM posting.** Coarser postings are block means of the 30 m grid (a stand in for GLO-90; the real GLO-90 product differs).

{{TABLE:class_shares}}

At 30 m the UNKNOWN share is {{VAL:unk_A_30}} in A south Liwa, {{VAL:unk_B_30}} in B (megadunes) and {{VAL:unk_C_30}} in C (linear dunes); BLOCKED is {{VAL:blk_A_30}}, {{VAL:blk_B_30}} and {{VAL:blk_C_30}}. The BLOCKED class is almost empty because the 30 m map hardly contains slopes the model calls impassable in every draw: that is a statement about what the DEM can show, not about the dunes (section 5 and the sub grid problem above). At 60 and 90 m the UNKNOWN share is {{VAL:unk_A_60}} and {{VAL:unk_A_90}} (A), {{VAL:unk_B_60}} and {{VAL:unk_B_90}} (B), {{VAL:unk_C_60}} and {{VAL:unk_C_90}} (C). It is not monotone in A, because coarser cells average out relief and slope break and the detector, trained per posting, also shifts.

**How much of the map is robust to the four assumed parameters.** Slope based verdicts (before the sub grid step) are unanimous across the draws for {{VAL:uni_A_30}} (A), {{VAL:uni_B_30}} (B) and {{VAL:uni_C_30}} (C) of cells at 30 m; only {{VAL:sens_A_30}}, {{VAL:sens_B_30}} and {{VAL:sens_C_30}} are sensitive to them. Under the original ranges (i0 0.05 to 0.40, f_r 0.05 to 0.25), the slip parameters therefore matter far less for the three class map than the **resolution and the face question** (with the widened ranges of 2026-10-18 this no longer holds; see the end of this section), because almost every 30 m cell is gentle enough to pass under every assumed parameter set. This does not contradict the phase 1 sensitivity result (the climbing limit itself varies from 7.6 to 34.7 degrees across the ranges): the DEM simply rarely shows slopes near that limit.

**Table 8.7c: robustness to the four assumed slip parameters.**

{{TABLE:robust}}

**Sensitivity to the sub grid assumptions.** The UNKNOWN share (30 m) when the share of crests with an active face falls from 1.0 to 0.3 is {{VAL:unkpi03_A_30}} (A), {{VAL:unkpi03_B_30}} (B) and {{VAL:unkpi03_C_30}} (C). The most important choice is the definition of "inside the cell". The pre registered definition counts a face only if it lies within the cell itself. A **post hoc variant** (added after the baseline result was seen, so not pre registered) counts a face within one post of the cell, which is closer to the question a route cares about; it gives UNKNOWN shares of {{VAL:unk3_A_30}} (A), {{VAL:unk3_B_30}} (B) and {{VAL:unk3_C_30}} (C) at 30 m. Both are shown because the plausible range is wide.

**Table 8.7d: UNKNOWN share under the sub grid variants.**

{{TABLE:scen}}

**Coverage versus certainty.** Coverage is the share of cells that are not UNKNOWN. Certainty is the share of cells declared face free that are truly face free. On the synthetic ensemble (known truth) and on the real maps (model expected certainty, not a measured accuracy):

{{TABLE:cc_synth}}

{{TABLE:cc_map}}

**Detector skill on held out synthetic profiles.** The detector separates cells with and without a face better than chance (AUC well above 0.5) and better than always predicting the base rate (Brier). It was also tested on ensembles with a different prior than the one it was trained on (gentle and steep dunes, and a lower share of active faces), where the skill changes only moderately. **This is skill against the synthetic world it was trained on; it is not evidence about real dunes.**

{{TABLE:detector}}

**Effect on routes.** Treating UNKNOWN cells as impassable, the share of the 10 origin destination pairs per window that stay reachable is:

{{TABLE:reach}}

**Widened slip scale range (2026-10-18; SIMULATED BY ME, simulation only, model assumption dependent).** The three class map was recomputed with the widened i0 range (0.05 to 1.20) and with f_r also widened (0.05 to 0.35), same seeds, detector and rules (`results/subgrid_widened_i0/`, `results/subgrid_widened_i0_fr/`; stage 9). The original shares above are unchanged.

{{TABLE:rs_phase2}}

At 30 m the UNKNOWN share in A rises from {{VAL:rs_o_unk_A}} to {{VAL:rs_w_unk_A}} with the widened i0 range, and to {{VAL:rs_wf_unk_A}} when f_r is widened as well; BLOCKED stays near zero. The pre registered prediction of a small rise missed badly (W9-5, W9-7). The added UNKNOWN is assumption sensitive, not sub grid face risk: once the assumed ranges are this wide, most cells change verdict between draws. In the widened_i0_fr set 12.1 % (A), 9.0 % (B) and 11.3 % (C) of draws cannot move on level ground (`results/range_set_diagnostics/immobile_on_level.csv`), more than the 5 % a TRAVERSABLE cell may fail, so its 90 % shares mostly reflect those draws, not the terrain; in the widened_i0 set the share is 1 to 2 %. The map's certainty is therefore set by how well the slip parameters of the actual vehicle are known.

**What this section establishes and does not.** It establishes that, under stated assumptions about dune shape, a 30 m DEM leaves a modest share of cells (about a tenth in the Liwa and megadune windows, a few percent in the linear dune window) with a face probability above 0.20, that this share rises to roughly a quarter to a third if a face within one post counts, and that it is driven by the assumed morphology and the cell definition far more than by the four slip parameters. It does **not** establish that any cell is safe: a TRAVERSABLE cell has a face probability below 0.20, not zero. No claim is made that the detector would find real faces; the way to test it is to compare it with an RTK or drone profile of a real dune (planned in `docs/FIELD_VALIDATION_PLAN.md` and as milestone M5 of `docs/PROPOSAL_EDGE.md`).
