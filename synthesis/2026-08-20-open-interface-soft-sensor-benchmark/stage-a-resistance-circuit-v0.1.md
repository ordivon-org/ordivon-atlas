# Stage-A Resistance Readout Circuit Sheet v0.1

Status: vendor-neutral owner engineering contract. Not procurement authorization and not a scientific threshold.

## Primary 1–100 kOhm topology

Per sensing channel use a fixed ratiometric divider:

`2.5-V-class stable Vexc -> precision 10-kOhm-class Rref -> Rsensor -> analog ground`.

Measure both sensor node `Vs` and `Vexc`; reconstruct:

`Rs = Rref * Vs / (Vexc - Vs)`.

Reference nominal values are not vendor-frozen. Start with <=0.1% tolerance / low-tempco Rref class and validate the complete path against traceable/known standards.

### Pilot numerical screen

At Vexc=2.5 V and Rref=10 kOhm:

| Rs | Vs | sensor dissipation | delta Vs for +3% Rs |
|---:|---:|---:|---:|
| 1 kOhm | ~0.227 V | ~51.7 uW | ~6.18 mV |
| 10 kOhm | 1.250 V | ~156 uW | ~18.47 mV |
| 100 kOhm | ~2.273 V | ~51.7 uW | ~6.03 mV |

These values show usable voltage margin; they do not prove material self-heating is negligible. Neutral sensor drift/hysteresis testing owns that decision. If ~0.156 mW around 10 kOhm materially perturbs the sensor, lower Vexc or a different frozen range is required before scientific runs.

## Channel architecture

Preferred physical architecture avoids outcome-dependent series switching in the scientific sensor path:

- dedicated identical divider/reference branch for yL;
- dedicated identical divider/reference branch for yR;
- dedicated auxiliary q* divider/readout branch physically present owner-side but excluded from I0 before admissible materialization;
- measured Vexc/reference monitor;
- load-cell/force acquisition on a separate bridge ADC path;
- actuator position feedback on separate owner channels.

If one multiplexed ADC is used, total conversion rate, settling and channel skew must meet the frozen per-channel sample rate. A 16-bit 860-SPS 4-channel multiplexed ADC is only a feasibility anchor: 4x200-Hz operation consumes almost all nominal conversion capacity. Prefer either a lower frozen rate after owner bandwidth calibration, multiple converters, or a faster architecture.

## Calibration-resistor path

Provide an owner-only calibration connector/relay route that substitutes known standards for the sensor without adding series impedance during normal measurement. Minimum primary standards: ~1 kOhm, ~10 kOhm and ~100 kOhm, each with known tolerance/tempco.

Before agent-visible runs:

1. open/short sanity;
2. complete-path standard-resistor reconstruction;
3. Vexc monitor consistency;
4. repeated pogo/remount test;
5. yL/yR channel swap and mirror-null audit;
6. neutral sensor noise/drift/self-heating run;
7. firmware/filter/sample-rate/reference/calibration digest freeze.

## Fallback range

The 100-Ohm–1-MOhm fallback is electronics coverage, not automatic scientific admission.

- Near 100 Ohm, pogo/wire/switch resistance is no longer negligible: require Kelvin/four-wire authority or an explicit complete-path contact bound.
- Near 1 MOhm, input/switch leakage becomes material: require relay/ultralow-leakage authority or an owner-measured leakage correction/bound.
- Any alternate range is chosen from neutral calibration and frozen per channel/cartridge before hidden-arm execution. No target-dependent autoranging.

## Grounding / EMI / timing

- Keep analogue reference/ADC return separate from motor-current return until one defined star point.
- Use twisted sensor pairs and, if needed, single-ended shield termination at the owner electronics side.
- Characterize resistance noise with motors disabled, holding position, and moving; if motor EMI is material, freeze dwell-window sampling or hardware filtering prospectively.
- Timestamp conversion-complete events and actuator/load samples from one monotonic owner clock; expose no side/arm semantics in filenames, timing errors or channel order.

## Firewall semantics

Owner may retain yL/yR, aux raw resistance, Vexc, range, load and actuator diagnostics. Agent I0 receives only the frozen mirror-even scientific projection. The auxiliary channel becomes scientific only after the appropriate WP-I/WP-G materialization/admission transition.
