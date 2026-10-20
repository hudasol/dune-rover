# Completeness of the research (2026-10-20)

Generated from `docs/src/completeness_template.md` by `scripts/build_report.py`; the facts in each row come from result files, the scores are working judgements against the criteria written next to them (criteria set before scoring), for the author to revise. A score is out of 10. Nothing here claims field validation.

| Part | Criteria for a full score | State (from the files) | Score |
|---|---|---|---|
| Literature and evidence | At least 300 rows read in full, a logged search, an error rate, a human spot check, the key classical sources retrieved | 494 rows from 174 sources; search protocol and flow logged; material error rate of new rows 9.3 %; human spot check prepared, not done; Wong and Reece 1967, the Wong dry sand table, Sullivan 2011 and Arvidson 2017 not retrieved | 8 |
| Quantitative curves | At least 8 curves from 4 sources, uncertainty recorded, at least one curve on Arabian sand | 26 curves from 7 sources with uncertainty; none on Arabian sand | 6 |
| Model validity (SIMULATED BY ME against PUBLISHED curves) | A model family passes a pre registered held out test on comparable data | exponential fails (held out median 0.24); Mohr Coulomb ratio fails (held out median 0.23); logistic fails (held out median 0.24); Bekker Wong fails (held out median 0.20) | 3 |
| Independent simulation | An independent simulator and a discrete element check, agreement explained | Chrono run with published wheels and soils; discrete element check not run; the gap between Chrono and the Bekker Wong family is not explained | 5 |
| Terrain validation | The map tested against real high resolution terrain, including Arabian dunes | Tested on three North American dune fields with one metre lidar (much better at 10 m than at 30 m); not tested in Arabia | 6 |
| Field data | Measured slip on dune sand for the project's own vehicle | None | 0 |
| Robotics value | Planner policies tested against real terrain with pre registered metrics | Three policies on three lidar sites; 30 m maps no safer than naive; at 10 m the conservative policy was safer on matched pairs at two of three sites (post hoc) | 5 |
| Reproducibility | Code, seeds, generated documents checked in CI, data identified with checksums and licences, fetch scripts for every input | Code, seeds, CI checks of the generated documents and the manuscript, checksums and licences in place; lidar and wind are fetched by scripts; the Chrono run needs a separate conda environment; raw downloads are not redistributed | 8 |
| Writing | A manuscript with every negative result, numbers checked by script, an external review | `manuscript/MANUSCRIPT.md` with a number check; adversarial reviews by fresh agents; no human external review | 7 |
| Proposal | Work packages, success criteria, risks, no unretrieved costs, partner needs | `docs/PROPOSAL_ROBOTICS.md` and `docs/PROPOSAL_EDGE.md`; nothing sent; no partner contacted | 7 |

**Overall: 5.5 out of 10** (the unweighted mean of the rows). The research is complete as a desk study: the evidence base, the validation of the available models and the resolution test are done and their failures are reported. It is not complete as an empirical study, because the one measurement that every result points to, a slip curve for the project's own vehicle on Gulf dune sand with a fine survey of the same dune, does not exist yet.

## Exact remaining gaps

1. Field slip data for the project's vehicle on Gulf dune sand, with soil tests (the slope ladder, `docs/FIELD_VALIDATION_PLAN.md`).
2. A 10 m or finer survey of an Arabian dune, to test the map and detector on Arabian terrain.
3. A decision on the field adequacy rule (question 7) before any field day.
4. The human spot check of 20 rows (`research/spot_check_inter_rater.md`) and spot check 3.
5. The Wong dry sand table with a legible title and page, and Wong and Reece 1967, if the Bekker Wong family is to be defended.
6. A discrete element single wheel check, to explain the gap between Chrono and the Bekker Wong family.
7. An external human review of the manuscript.
