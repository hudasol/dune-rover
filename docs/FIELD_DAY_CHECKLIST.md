# Field day checklist: slope ladder on one dune stoss slope

**Status: PLANNED. Nothing here has been run.** One page, to be printed. The full protocol is `docs/FIELD_VALIDATION_PLAN.md`; the analysis rule is fixed in `docs/predictions/` before any run. Heat and dust limits of the electronics are in the sibling repository `hudasol/dhill` and are not repeated here.

## Before leaving
- [ ] Site access, permission and a named contact obtained (operator's responsibility; for a supervised run with Al Ain University see `docs/AAU_FIELD_DAY_PROPOSAL.md`, a proposal only). Slope bins chosen by RTK walk or drone map: 0, 5, 10, 15, 20, 25 degrees, each within plus or minus 2.
- [ ] Predictions file `docs/predictions/slope_ladder_predictions_2026-10-12.csv` is committed. The post calibration file is written and committed **after the 0, 5 and 10 degree runs and before the 15, 20 and 25 degree runs.**
- [ ] Run order randomised, written on the log sheet. Rover mass, wheel diameter, width, tyre type and loaded effective radius recorded on a hard surface and on level sand.
- [ ] Batteries full, spare set charged. Both RTK units tested on the car roof. Encoders and current logging tested on a bench.

## Equipment
| Group | Items |
|---|---|
| Rover | One fixed rover (5 to 25 kg, four wheels, wheels of at least 150 mm if possible), wheel encoders, motor current logging, IMU, tether and recovery line, spare wheel hardware |
| Position truth | RTK GNSS base and rover (or total station), tripod, 2 m levelled pole. Fallback: painted stakes at 0 m and 6 m, tape measure, phone video on a tripod with a scale in frame |
| Sinkage | Straight edge longer than the rut width, steel ruler, depth gauge or calipers, scale card for photos |
| Sand tests | Sieve set and scale, 100 ml cup, sample bags, drying method for moisture, funnel and protractor for repose angle, hand cone penetrometer, two plates with a set of weights for pressure sinkage, inclinometer |
| People and safety | Two people minimum, water (more than you expect), shade, sun protection, first aid kit, radio or phone with agreed check in time, vehicle recovery plan, gloves, goggles |

Costs of retrieved items are in `docs/ROVER_OPTIONS.md`; anything not listed there has an unknown cost.

## Safety
1. Never stand or place the tether below a rover on a lee face or a slope near the angle of repose (it can avalanche). Tether lines run to the side.
2. Stop at the first sign of heat illness in anyone. Schedule runs outside the hottest hours and log temperature.
3. A rover can bury itself at 20 to 25 degrees: use the recovery line, do not dig by hand under a loaded vehicle.
4. Abort rules: wind that blows sand into connectors, battery temperature warning, loss of radio contact, any safety stop by either person.

## Per run (log row in `docs/field_log_template.csv`)
- Run id, block (pilot, main), measured slope from the RTK line, heading, pass number, fresh track offset by at least two wheel widths.
- Constant wheel command, same entry speed, 6 m on the slope, from the same lower start. Ends at distance, entrapment (no progress 5 s with wheels turning, or slip above 0.8 for 3 s) or safety stop. Record the reason.
- **Slip, cheapest to best:** (1) markers: true distance over the 6 m against wheel encoder distance, slip = 1 minus true divided by encoder distance; (2) video timing of the rover past two markers against wheel speed; (3) RTK ground speed against wheel rim speed (omega times effective radius), steady state window only.
- **Sinkage:** at three marked stations in the rut, lay the straight edge across undisturbed sand and measure the depth at the wheel centreline. Photo with scale. Record as depth and as a share of wheel diameter.
- Entrapment flag, recovery needed, notes (crust, wind ripples, slope change).

## Sand characterisation (each slope station, 3 times per site where marked)
Grain size by sieve (d10, d50, d90), bulk density by known volume cup (3), moisture at 0 to 2 cm and 5 to 10 cm, crust thickness, angle of repose (3 per site), penetrometer 0 to 15 cm (5), plate pressure and sinkage set (once per site), air temperature and wind. Do **not** invent soil parameters: anything not measured is written as unknown.

## After the day
Back up the raw logs and photos the same day. Run `python3 scripts/analyze_field_runs.py runs.csv` only after the pilot block: it sets the tolerance from the pilot scatter. Report every run including entrapments and discards.
