# Phase 2 rover and measurement kit sourcing

Companion file: `phase2_rover_options.csv` (39 rows: 20 platform rows, 19 kit rows).

## Method and rules applied

- A price or specification was recorded only if it was read on a retrieved vendor or documentation page. Anything else is `unknown`.
- Currency is as shown. Where a page showed only `$`, the currency column says "$ only" (or USD where the page metadata said USD). Nothing was converted between currencies.
- Unit conversions (lb to kg, inch to mm, ft/min to m/s) were done by me and are labelled "derived" in the CSV.
- Pages were fetched with curl through the proxy. Two SuperDroid pages returned HTTP 403 to curl and were read through the WebFetch tool, so those values are that tool's quotes of the page.
- No memory was used for any price or specification.

### Date deviation (please note)

The brief says to record 2026-10-11 as the retrieval date. The calendar date rolled over to 2026-10-12 partway through the session. Rows fetched before the rollover carry 2026-10-11. Rows fetched after carry 2026-10-12 (mostly the kit parts, plus the RobotLAB and Bunker Mini platform pages). I kept the true date rather than stamping everything 2026-10-11.

## What could not be priced (marked unknown)

| Item | Why |
|---|---|
| AgileX Scout Mini, Scout 2.0, Hunter SE on global.agilex.ai | Pages show a `$0.00 USD` placeholder and "Contact Us sales@agilex.ai". Treated as unpriced. (Scout Mini was priced through three resellers.) |
| ArduSimple simpleRTK2B kit | ardusimple.com returns HTTP 403 "Just a moment" (bot challenge) to curl on every URL tried, and WebFetch permission was not granted. Price, kit contents and UAE shipping are unknown. SparkFun ZED-F9P boards are listed instead. |
| Rover Robotics 4WD Rover Zero | The 4WD product URL I tried returned 404. Only the 2WD Rover Zero page was read. |
| Hunter SE mass, Scout 2.0 mass, Scout Mini wheel diameter, ROSbot XL wheel diameter, Sawppy wheel and mass, JPL OSR mass | Not stated on any retrieved page. |
| Traxxas X-Maxx tyre diameter and ROS conversion | Not retrieved. The OzRC page does not state the currency in the retrieved text. |
| 3 cm2 cone for the Gilson penetrometer (HMA-272) | Listed as an accessory but its price was not read. |
| Whether any vendor ships to the UAE | No retrieved vendor page states UAE shipping in a product or policy sentence. Tiger Supplies (tripod, total station) and Tindie list "United Arab Emirates" in a country selector, which is weaker than a shipping statement. SparkFun, Adafruit and Open Electronics describe international shipping generally and say duties and taxes fall on the customer. Everything else is unknown. |
| Sand slip or mobility results for any listed platform | See next section. |

## Sand slip results: none found

Two searches targeted sand slip, sinkage or mobility results for Leo Rover, Jackal, Scout Mini and the JPL Open Source Rover. I opened three of the papers that came back (arXiv 2202.08495, arXiv 2308.12431, Frontiers in Robotics and AI 2024, doi 10.3389/frobt.2024.1320261). None of them named any platform in this list (the Frontiers paper uses a 38.5 kg differential-suspension rover). So `sand_results_source` is "none found in retrieved sources" for every platform. This is a limited search, not proof that no such result exists. Fictionlab runs a "Research papers" page for Leo Rover that I did not open.

## Source conflicts worth knowing

- **Scout Mini** has three different spec sets: AgileX page (10 kg payload, 1.5 m/s, 3 h; the same page also says 10 km/h), the AgileX PDF manual (20 kg body, 107 mm clearance, up to 20 km/h), OpenELAB (23 kg, 3.0 m/s, 115 mm), RobotLAB (23 to 26 kg, 2.7 m/s, 115 mm). MYBOTSHOP says about 20 kg and about 100 mm. Wheel diameter is not given in any of them. Order a unit with the vendor's confirmation of mass and tyre size before relying on any of these.
- **Bunker Mini 2.0** (Generation Robots): the page says payload 25 kg in text and 35 kg in the spec block, and weight 55 kg.
- **Rover Zero** page: the table lists "75kg" and "11kg" under Weight, Payload Capacity and Unit Weight headings, so I could not tell which is which.
- **Pololu 24v13** page quotes about 40 mV/A for current sense in one place and 20 mV/A and 10 mV/A in a variant table.

## Platform suitability (reasoned only from retrieved specs; every line is a judgement)

Test needs assumed: 5 to 25 kg, four wheels, wheels of at least 150 mm preferred, able to run slowly and steadily on sand while logging wheel speed, motor current, GNSS position and pitch.

| Platform | Price as shown | Mass | Wheel dia. | Judgement |
|---|---|---|---|---|
| Raph Rover 1.0 | EUR 12 950 | 12.5 kg | ~170 mm x ~80 mm | Best spec match on mass and wheel size, with 80 mm clearance and a 10 kg payload for load changes. Highest cost of the in-class set and the Ackermann layout is less convenient for pure straight-line tests. Sand not mentioned by the vendor. |
| Clearpath Jackal | EUR 17,472.00 incl. VAT (14,560.00 excl.) | 17 kg | 194 mm (width unknown) | Wheel size is good and the platform is documented as outdoor. Clearance of 65 mm is small for soft sand, and the price is the highest here. Skid steer. Docs list wheel odometry, motor currents and IMU as available data. |
| Leo Rover 1.9 | EUR 5 499 assembled (4 799 kit) | ~7 kg | ~125 mm x ~70 mm | Cheapest of the commercial research-grade rovers with clear docs and open source firmware. Wheel is below the 150 mm preference, but the docs say other tyres can be fitted (with different speed and force). Payload is only ~5 kg and speed ~0.4 m/s, which is slow but suits a slip test. |
| AgileX Scout Mini | EUR 3.999,00 (OpenELAB), EUR 5.950,00 (MYBOTSHOP), USD 4,500 (RobotLAB) | 20 to 26 kg depending on source | unknown | Mass is at or above the top of the class and the wheel size is unverified, so it cannot be judged suitable until confirmed. Low IP rating (IP22 on two pages). Speed is high, so low-speed control must be checked. |
| SuperDroid 4WD 52 mm motors | USD (page shows $) 1,993.39 | ~26.8 kg (derived) | 254 mm (derived, pneumatic) | Large pneumatic wheels and a low price. About 1.8 kg over the class. Pneumatic tyre pressure becomes an experimental variable (judgement). No sensors listed on the retrieved text, so encoders and current logging would be added. |
| SuperDroid IG32-SB6 6WD | USD (page shows $) 904.79 | ~14.1 kg (derived) | 152.4 mm (derived) | Cheap commercial option that just meets the wheel preference. Six wheel skid steer adds scrub on turns, so use straight runs only. |
| JPL Open Source Rover | ~$1600 (docs); $1421.18 parts, excl. shipping | unknown | 144 mm x 52 mm | Cheap, documented, six wheel rocker bogie. Wheels are just under the preference and width is narrow. Mass unknown. Rocker bogie load sharing complicates per-wheel sinkage interpretation. Build time and sourcing from goBILDA are on the user. |
| Rover Robotics Rover Zero (2WD page) | USD 6,999.99 | 11 or 75 kg (ambiguous) | 254 mm front | Large wheels but the 2WD layout with rear casters does not give four driven wheels for slip logging, and the page advises against bad weather. 4WD variant unpriced. |
| Traxxas X-Maxx 8S | $2,184.95 sale (currency not stated) | ~8.7 kg (derived, review) | unknown | Plausible ROS conversion base with big tyres and a small mass, but top speed and runtime (23 min measured by the review) are mismatched to slow slip tests, and no ROS or sensor path was retrieved. Needs ESC speed limiting. Low-cost hobby end. |
| Husarion ROSbot XL | EUR 5,472.00 incl. VAT (4,560.00 excl.) | 5.38 kg | unknown | Vendor states indoor use. Clearance 32 mm. Not suitable for sand (the vendor's own intended use). |
| Sawppy | USD (page shows $) 500 target | unknown | unknown | Interesting as a cheap DIY scale model, but nothing retrieved supports field use on sand and dimensions were not read. |
| Waveshare UGV02 | $149.99 | 2 kg | 80 mm | Far below class. Only useful for a bench or small box trial. |
| Hiwonder Large Metal 4WD | $199.99 | 1.9 kg | unknown | Mecanum wheels and 1.9 kg: not suitable. |
| Husarion Panther | EUR 24,000.00 incl. VAT | 55 kg | 365 mm | Out of class. Included for the research-grade end only. |
| AgileX Bunker Mini 2.0 | EUR 9,360.00 incl. VAT | 55 kg (spec block) | tracked | Out of class and tracked; the only page that mentions sand does so as an ingress rating. |
| AgileX Scout 2.0, Hunter SE | unknown | unknown | unknown | Payload of 50 kg suggests they are above 25 kg. Unpriced. |

Overall (judgement): for a real sand slip experiment the retrieved specs favour Raph (cost aside), the Jackal (if clearance is acceptable on firm dune sand), the SuperDroid platforms, or a custom or DIY chassis. Leo is the cheapest sensible ROS option if the small wheel is accepted or replaced. Scout Mini needs mass and wheel confirmation first.

## Kit items as retrieved

| Item | Price as shown | Source |
|---|---|---|
| SparkFun GPS-RTK2 board ZED-F9P (one) | USD 259.95 | sparkfun.com/products/15136 |
| SparkFun GNSS multiband antenna SPK6618H (one) | USD 169.95 | sparkfun.com/products/21801 |
| SparkFun RTK Facet (enclosed) | USD 739.95 | sparkfun.com/sparkfun-rtk-facet.html |
| ArduSimple simpleRTK2B kit | unknown | blocked, see above |
| Adafruit BNO055 9-axis IMU | USD 29.95 | adafruit.com/product/4646 |
| Pololu Romi encoder pair, 12 CPR | USD 9.95 | pololu.com/product/3542 |
| Pololu G2 motor driver 24v13 (current sense output) | USD 44.95 | pololu.com/product/2992 |
| Pololu Simple motor controller 24v23 | USD 204.14 (End-of-Life Rationing) | pololu.com/product/1383 |
| Adafruit INA260 current sensor | USD 9.95 | adafruit.com/product/4226 |
| 100 kg S-type load cell | EUR 52.46 excl. VAT | store.open-electronics.org |
| SparkFun HX711 amplifier | USD 4.95 | sparkfun.com/products/13879 |
| Gilson static cone penetrometer HM-559A | USD 800.00 | globalgilson.com |
| Forney 10 sieve soils kit | USD 786 | store.forneyonline.com |
| Cuisena 5 kg kitchen scale | AUD 19.05 | jbhifi.com.au |
| Wixey WR300 angle gauge | USD 37.00 | wickededgeusa.com |
| Bosch GIM60 inclinometer | GBP 123.54 ex VAT, 148.25 inc VAT | datapowertools.co.uk |
| Olimex 150 mm digital caliper | EUR 15.00 | olimex.com |
| NAT96 survey tripod | USD 165 | tigersupplies.com |
| Stonex R25LR total station | USD 4,800 (list 6,000) | tigersupplies.com |

Totals are not given across currencies. As a same-currency illustration only: a SparkFun RTK pair of two ZED-F9P boards and two antennas adds to USD 859.80 before any radio or NTRIP subscription.

Fit notes (judgement):

- The Romi encoders fit small Pololu gearmotors only. A larger rover needs encoders matched to its own motors.
- The Forney kit is gravel-heavy (3 in down to #200). For dune sand only the finer sieves apply, so a fine-range stack would likely be a better buy.
- A 150 mm caliper cannot measure sinkage in a track on its own; the depth gauge item was not priced separately.
- A gauge cone penetrometer gives a cone index, not full Bekker parameters.
