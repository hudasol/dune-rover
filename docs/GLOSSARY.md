# Glossary for newcomers

Plain-language definitions of the terms used in `REPORT.md`. Where a term has several competing definitions in the literature, the difference is said, because many numbers in the evidence table are not comparable for exactly that reason.

## The basic quantities

**Slip (slip ratio).** How much a wheel turns without moving the vehicle forward. The most common definition is `slip = 1 - (actual forward speed) / (wheel rim speed)`. Zero means perfect rolling; 1 (100 %) means the wheels spin and the vehicle goes nowhere. Papers also use "distance lost against distance commanded" and "visual-odometry slip" (the camera says you moved less than the wheel encoders say). These are close but not identical, so the evidence table flags them.

**Skid.** The opposite effect: the wheel turns less than the vehicle moves, for example when braking or sliding downhill. Negative slip in most definitions.

**Side-slip.** Sideways sliding on a cross-slope. Measured as an angle or as a distance lost sideways.

**Sinkage.** How deep the wheel or foot sinks into the ground, usually in millimetres or as a share of wheel diameter. Sinkage makes the wheel climb out of its own rut, which is a major part of **motion resistance**.

**Motion resistance.** The force the soil exerts against rolling, from pushing sand aside and compacting it. Expressed as a force or as a coefficient (force divided by weight).

**Drawbar pull.** The pulling force a vehicle has left over after paying for motion resistance. A vehicle with zero drawbar pull can move itself but cannot tow anything or climb. On a slope, part of the vehicle's own weight acts like a load being towed.

**Traction (gross traction).** The total push the wheel gets from shearing the soil. Drawbar pull is traction minus motion resistance.

**Traversability.** Whether, and at what cost, a robot can cross a patch of terrain. In this project it means a slope-and-slip-based yes/no/cost, not a general-purpose obstacle map.

**Entrapment.** Getting stuck: the wheels dig in and the vehicle cannot recover. On sand it is the worst case, and in several Mars rover events it happened on modest slopes.

**Angle of repose.** The steepest slope a pile of dry loose sand holds. For aeolian (wind-blown) sand it is about 32 to 35 degrees. Dune lee faces (slip faces) sit near this angle.

**Slip face (lee face).** The steep downwind side of a dune, close to the angle of repose, where sand avalanches. It ends at a sharp **brink** (the crest edge).

**Stoss side.** The gentler upwind side of a dune.

**Crest.** The top line of a dune ridge.

**Interdune.** The flatter ground between dunes. In Liwa this can include sabkha (salt flat with a shallow water table), which behaves very differently from loose sand.

## Soil and terramechanics terms

**Terramechanics.** The science of how vehicles interact with soft ground. Founded by Bekker in the 1950s and 60s.

**Bekker pressure-sinkage model.** An equation relating the pressure under a plate or wheel to how deep it sinks, using soil constants `kc`, `kphi` and `n`. Fitted by pushing plates into the soil.

**Wong-Reece model.** An extension of Bekker's approach for rolling wheels, which integrates stresses under the wheel contact patch.

**Janosi-Hanamoto shear law.** An equation for how much shear stress the soil can give as the wheel slips, rising from zero and levelling off at the soil's shear strength. Its shape constant `K` (the shear deformation modulus) controls how quickly it saturates. Published values of `K` differ by roughly two orders of magnitude, so it is usually tuned rather than measured.

**Internal friction angle (phi).** How strongly sand grains lock together. Typical values for dry sands in the retrieved papers are 28 to 38 degrees. Cohesion is near zero for clean dry sand.

**Bevameter.** A device that presses a plate into soil and shears it, to measure the Bekker and shear constants.

**Resistive force theory (RFT).** A method from granular physics: the force on a small element of a wheel or leg moving through dry grains depends on its depth, orientation and direction of motion, using a fitted force-response surface. Sums the forces over the whole wheel. Works well for slow movement in dry grains and is much faster than particle simulation.

**Quasi-static.** Ignores speed and inertia. Most classical wheel-soil models are quasi-static; measurements show real wheels lose traction as speed increases, so they are not.

## Simulation terms

**DEM (discrete element method).** Simulates every sand grain (or a scaled-up stand-in for groups of grains) as a particle with contact forces. Accurate but very slow.

**SCM (soil contact model).** A fast deformable-terrain model in Project Chrono that uses a Bekker-Wong-style formula for each point of a terrain grid.

**CRM (continuum representation model).** A Chrono model that treats the sand as a continuous material (SPH particles) with a granular flow law, with fewer tuning knobs than DEM.

**Project Chrono.** An open-source (BSD-licensed) physics simulation library with vehicle and terrain modules.

**Real-time factor.** Wall-clock time divided by simulated time. A value of 1 means real time; 1000 means a thousand seconds of computing per simulated second.

**Sim-to-real gap.** The difference between what a simulation predicts and what happens in the real world. The central worry of this review.

## Data and measurement terms

**DEM (digital elevation model).** Confusingly, the same letters. A grid of ground heights. In this repository "DEM" in the data sections always means elevation model; for particle simulation the text says "discrete element method".

**DSM / DTM.** Surface model (top of trees, buildings, sand) versus terrain model (bare ground). Copernicus GLO-30 is a DSM.

**Posting.** The spacing between grid points of an elevation model. Copernicus GLO-30 is about 30 m.

**Horn method.** A standard way to compute slope from a grid using the 3x3 neighbourhood of each cell.

**Visual odometry (VO).** Estimating how far a vehicle moved from camera images. Mars rovers use it to measure slip. It can fail on bland, featureless sand.

**RTK GNSS.** Satellite positioning with a correction signal that gives centimetre accuracy. Useful as ground truth for slip.

**Held-out test.** Data not used in training or fitting, used to check how well a model predicts new cases. A split by terrain type (train without sand, test on sand) is a much harder and more honest test than a random split.

## Words used for evidence in this project

**PUBLISHED.** A number found in a source that was retrieved and read.

**SIMULATED-BY-ME.** Output of code in this repository. Depends on the stated model assumptions. Never field evidence.

**PLANNED.** A protocol that has not been run.

**Validation type.** `lab` (bench, soil bin, tilt bed), `field` (real vehicle on real terrain, including Mars), `simulation-only`, `sim-vs-lab`, `sim-vs-field`.

**Comparability warning.** A note on a table row listing why that number should not be compared directly with another row (different wheel, soil, slope definition, slip definition, gravity or metric).
