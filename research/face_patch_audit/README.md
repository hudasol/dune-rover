# Face patch audit (for a human rater)

**Why.** Every benchmark result of stages 25 to 28 is scored on "face patches": groups of at least 10 one metre lidar posts steeper than 28 degrees. That is steep ground, not necessarily a sand slip face. Rock outcrops, off road vehicle ruts and cut banks, vegetated mounds, creek banks and lidar artefacts can also be steep. This audit measures what share of the patches really are slip faces, so the paper can report label precision (review finding M4 in `docs/REVIEW_2026-10-28.md`).

**What to rate.** `worksheet.csv` lists 100 patches per site (600 in total), sampled at random within three size classes before anyone looked at them (`scripts/build_audit_pack.py`, seed 20261028). Each code (for example `DUM-001`) has one row of three chips in `data/derived/face_patch_audit/audit_<site>.pdf`. The chips are 90 m across with north up: NAIP colour imagery, lidar hillshade, and lidar slope. The patch is outlined in pink. Regenerate the PDFs with `PYTHONPATH=src python3 scripts/build_audit_pack.py`; they are not committed.

**How to rate.** Fill in `class` with one of:

| Class | Meaning |
|---|---|
| `slip_face` | the lee face of a dune at or near the angle of repose (a sharp brink, a smooth steep face, sand below) |
| `other_sand_scarp` | steep sand that is not a lee face: a blowout wall, a wind scoured flank, a cut in sand by water |
| `rock` | bedrock, boulders, a rocky hillside |
| `vegetation_or_pedestal` | a vegetated mound, a pedestal held by roots, a shrub coppice dune flank |
| `anthropogenic` | a road cut, a berm, off road vehicle ruts or a track edge, a building |
| `artefact` | a lidar or interpolation artefact (stripes, a pit, a spike, water) |
| `unsure` | cannot tell from the chips |

Then fill in `confidence_1_to_3` (1 = a guess, 3 = sure), `rater` (initials) and an optional `note`. Rate on your own first; a second rater should fill a copy of the sheet without seeing the first ratings, so agreement can be measured (Cohen's kappa).

**What the build will do with it.** Label precision per site (share of patches that are `slip_face` or `other_sand_scarp`), weighted by `inclusion_weight` to stand for all patches and for face area, with Wilson intervals; agreement between raters; and a rerun of the main results with the patches classed `rock`, `anthropogenic` or `artefact` removed from the truth. No result changes until the ratings exist.
