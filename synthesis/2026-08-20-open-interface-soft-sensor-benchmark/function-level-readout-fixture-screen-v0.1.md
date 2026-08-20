# Function-Level Resistance Readout + Fixture Geometry Screen v0.1

Status: neutral pre-purchase engineering screen. This does not select vendors/SKUs, alter C0/G0, or set scientific epsilon/eta.

## 1. Resistance readout authority

### Topology

Use a ratiometric divider per selected channel:

`Vexc -> Rref -> Rx -> GND`,

with both divider node `Vnode` and excitation `Vexc` measured by the owner-side ADC path. Reconstruct

`Rx = Rref * Vnode / (Vexc - Vnode)`.

The goal is not a particular ADC board; it is calibrated resistance authority across the owner pilot envelope.

### Range policy

- Primary scientific pilot range remains 1 kOhm–100 kOhm.
- Electronics fallback envelope remains 100 Ohm–1 MOhm.
- Provide a precision reference-resistor bank spanning decades (functionally 100 Ohm / 1 kOhm / 10 kOhm / 100 kOhm / 1 MOhm class, exact values not frozen).
- Select and freeze the reference/excitation range for each sensing channel from neutral calibration before hidden-arm execution. Do not outcome-adapt range selection inside scientific episodes.
- Keep the divider ratio away from rails; a working engineering screen is roughly 0.1 <= Vnode/Vexc <= 0.9.

### Excitation/self-heating

- Use a stable low-voltage excitation and freeze it by neutral calibration.
- Establish a sensor-power ceiling before scientific runs. As a screening anchor, <=100 uW in the primary 1 kOhm–100 kOhm range is desirable unless material calibration establishes a different safe value.
- Low-resistance fallback may require lower excitation; high-resistance fallback requires leakage characterization.

### Conversion throughput

- Resolution screen remains >=16 effective ADC bits for the slow resistance channels unless owner calibration justifies a different architecture.
- Required authority is aggregate throughput at the frozen per-channel sample rate, including MUX settling and bounded channel skew.
- A 16-bit ADS1115-class converter is technically plausible but is multiplexed and tops out at 860 SPS. A single four-channel device therefore has little engineering margin if four channels are each demanded at 200 Hz; use a lower frozen rate, multiple converters, or a faster/simultaneous architecture rather than silently undersampling.

### Switching/contact/leakage

- Switching must preserve identical lineage across hidden arms and not expose range/port identity to the agent.
- Primary 1–100 kOhm operation can use a calibrated low-leakage switch/relay path if repeatability passes.
- Near 100 Ohm, contact/on-resistance can become target-relevant: use Kelvin/four-wire authority or an explicit contact-resistance bound/correction before admitting that range.
- Near 1 MOhm, switch/input leakage can become target-relevant: use relay/ultralow-leakage authority or bound the leakage error prospectively.

### Calibration receipt

Before owner scientific calibration:

1. open/short sanity;
2. known precision-resistor checks bracketing every admitted range;
3. repeated connect/remount/contact tests;
4. excitation and reference drift checks;
5. channel-to-channel swap and mirror audit;
6. neutral sensor resistance + noise/self-heating run;
7. exact firmware/range/excitation/calibration digest freeze.

Owner may retain yL/yR, aux raw resistance, range and excitation diagnostics. Agent-facing I0 still exposes only frozen mirror-even aggregates. Auxiliary q* readout remains absent from I0 until admissible materialization.

## 2. Neutral mechanical geometry screen

For vendor-independent pre-purchase screening only, use the standard rectangular-beam three-point small-deflection flexural-strain relation as an equivalent-span approximation:

`epsilon_f = 6 D d / L^2`, hence `D = epsilon_f L^2 / (6 d)`,

where `D` is center deflection, `d` thickness, `L` effective bend span. The final two-axis mirror fixture is not literally a three-point coupon test; empirical camera/load calibration owns the final mapping.

### Travel-screen examples

- L=60 mm, d=1.0 mm, epsilon=0.5% -> D≈3 mm.
- L=60 mm, d=1.0 mm, epsilon=1.0% -> D≈6 mm.
- L=60 mm, d=0.5 mm, epsilon=0.5% -> D≈6 mm.
- L=60 mm, d=0.5 mm, epsilon=1.0% -> D≈12 mm.
- L=80 mm, d=0.5 mm, epsilon=1.0% -> D≈21.3 mm; travel fits 30 mm but D/L≈0.27, so the small-deflection approximation is already poor.
- L=80 mm, d=0.2 mm, epsilon=1.0% -> D≈53.3 mm; reject against a 30-mm-travel reference route before purchase.

### Recommended first owner-pilot box

Start neutral engineering around:

- effective bend span near 60 mm;
- thickness 0.5–1.0 mm;
- width within the existing 15–30 mm envelope;
- surface-strain screen 0.5–1.0%;
- equivalent deflection 3–12 mm.

This keeps travel far inside the current 30-mm reference actuator envelope and keeps deflection materially larger than the cited ±0.2-mm position-accuracy reference. It is an engineering starting box, not a frozen scientific specimen definition.

### Admission consequences

- Do not choose an ultra-thin/long specimen that forces >30 mm travel merely because it is easy to source.
- Do not use actuator maximum force as target load; soft specimens may need far less. Select load-cell range downward only after owner neutral force pilot.
- Require mirror-mounted geometry, independent cartridges, keyed datum/pogo contacts and active-state camera firewall.
- Existing Integrated Camera is owner-only neutral registration/geometry authority; active-state image data remain denied to the agent.
- If actual nonlinear geometry departs from the equivalent-span estimate, freeze the empirical displacement/curvature/load map before agent-visible trials rather than patching the formula.

## 3. Current decision boundary

These screens reduce pre-purchase uncertainty but do not authorize procurement. They should be applied equally to local and delegated physical routes. Provider/local hardware is admitted only when the same readout, mirror, hidden-label, replica and source-fence semantics survive.
