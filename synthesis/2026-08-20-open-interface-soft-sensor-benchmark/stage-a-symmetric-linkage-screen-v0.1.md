# Stage-A Symmetric Linkage Screen v0.1

Status: vendor-neutral mirror-linkage engineering screen. Not final fixture geometry or procurement authorization.

## Objective

Map small body-side geometric displacements into several millimetres of actuator travel so actuator position uncertainty does not dominate H1 mirror calibration, while keeping the two sides mechanically identical.

## Candidate 4:1 displacement-reduction linkage

Use two identical mirror-mounted rocker/lever modules. Each actuator drives the long-motion input; the specimen-side contact/cable output moves approximately one quarter of actuator stroke. A practical geometric implementation can use identical lever parts flipped by the mirror transform, e.g. ~4:1 effective arm ratio, with matched pivots/bearings, hard stops and keyed datum. Exact dimensions are owner-pilot variables.

The same part and fastener stack should be used on left/right. Do not independently hand-tune lever geometry after arm outcomes.

## Circular/equivalent-span travel screen

For screening only, with arc length/effective bend span L and radius R:

`chord = 2 R sin(L/(2R))`;

per-side geometric shortening `s = (L - chord)/2`;

4:1 actuator stroke `a ~= 4 s`.

Surface strain screen uses `epsilon ~= t/(2R)`. Final fixture curvature/load is owner-camera/load calibrated and may not follow an exact circular arc.

### L = 60 mm, t = 0.5 mm

| strain screen | R | body-side s | 4:1 actuator stroke |
|---:|---:|---:|---:|
| 0.5% | 50.0 mm | ~1.77 mm | ~7.07 mm |
| 0.75% | 33.3 mm | ~3.89 mm | ~15.56 mm |
| 1.0% | 25.0 mm | ~6.70 mm | ~26.80 mm |

This maps the primary 0.5–1.0% owner pilot into ~7–27 mm of a 30-mm-travel reference axis, leaving travel margin and materially increasing displacement relative to the cited ±0.2-mm position-accuracy screen.

## Position-error screen

At 4:1, ±0.2 mm actuator position uncertainty maps to approximately ±0.05 mm specimen-side uncertainty per actuator. Worst-case differential left-right uncertainty is ~0.10 mm before empirical pair calibration. Relative to the nominal body-side shift above, this is roughly:

- 5.7% at 0.5% strain;
- 2.6% at 0.75% strain;
- 1.5% at 1.0% strain.

Therefore the first H1 mirror-authority pilot should preferentially calibrate around the middle/high part of the neutral strain envelope (roughly 0.75–1.0%) before using the lowest-strain condition as an authority verdict. If low-strain H1 is scientifically required, use tighter closed-loop position/geometry correction or a higher-accuracy axis rather than relaxing the mirror-null criterion.

## Thin-body consequence

For L=60 mm and t=0.2 mm, 0.2% strain already gives R=50 mm and ~7.07 mm actuator stroke at 4:1. A 30-mm stroke reaches only about 0.43% under this circular screen. Thus the thinnest 0.2-mm body is not a good first choice if the owner wants 0.5–1.0% strain with a 4:1/30-mm route. A ~0.5-mm effective thickness is the cleaner first neutral mechanical pilot; thinner bodies remain a later branch with a different ratio/actuator geometry.

## Mirror construction rules

- identical left/right linkage parts, mirrored installation;
- common body coordinate datum and keyed cartridge mount;
- matched pivot/bearing/fastener stack;
- symmetric hard stops and cable routing;
- independent force/load grounding on both physical paths;
- owner-only neutral camera fiducials for transfer-function calibration; active-state imagery remains firewalled from the agent;
- calibrate left/right transfer functions `s_L(command)` and `s_R(command)` on a dummy/neutral body before scientific runs; do not infer equality from CAD symmetry alone.

## Admission test

The 4:1 ratio is admitted only if owner calibration shows the commanded mirror pair produces a matched curvature/load path with margin relative to the later old-interface blindness threshold. If backlash/compliance/pivot friction dominates, change linkage/axis before benchmark admission; do not compensate by letting the agent see side-specific calibration state.
