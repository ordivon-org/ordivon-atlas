# Mechanism / Failure Interaction Map

This is a **bounded observational relation map**, not a universal causal DAG. Edges are retained only where the mature corpus repeatedly supports the relation.

Allowed relation vocabulary at M0:

`ENABLES`, `INHIBITS`, `COMPENSATES_FOR`, `CONFOUNDS`, `EXPOSES`, `DEPENDS_ON`, `CAN_FAIL_WITHOUT`.

| From | Relation | To | Observation |
|---|---|---|---|
| `MO-M01` Permissive Exploration | `ENABLES` | `MO-M02` Representation Challenge | Low-cost inquiry keeps alternative framings alive before durable promotion. |
| `MO-M02` Representation Challenge | `EXPOSES` | `MO-F01` Representation Failure | Fresh whole-space or evaluator challenge can reveal that the frame, not merely a hypothesis, was wrong. |
| `MO-M03` Typed Negative Knowledge | `COMPENSATES_FOR` | `MO-F07` Anti-Rediscovery Failure | Preserved why-not/reopen lineage reduces rediscovery only when future discovery paths exist. |
| `MO-M04` Typed Standing | `INHIBITS` | `MO-F02` Premature Promotion | Explicit separation of usefulness/currentness/Foundation/effect standing creates places to withhold promotion. |
| `MO-M05` SMC | `DEPENDS_ON` | `MO-M04` Typed Standing | Commitment cannot be bounded by standing if the relevant standing dimension is collapsed or unavailable. |
| `MO-M05` SMC | `INHIBITS` | `MO-F04` Silent Escalation | Contemporaneous promotion/effect checks reduce implicit acquisition of stronger commitment. |
| `MO-M05` SMC | `CAN_FAIL_WITHOUT` | `MO-F08` Implementation Error | Correct standing control does not guarantee correct mutation. |
| `MO-M06` Human–Agent Judgment | `CAN_FAIL_WITHOUT` | `MO-F05` Explicit Overcommitment | Joint agreement can still authorize too much irreversible change. |
| `MO-M07` Memory/Currentness/Recovery Separation | `COMPENSATES_FOR` | `MO-F03` Stale Continuity | Owner-current recovery prevents historical continuity from becoming current route authority. |
| `MO-M07` Memory/Currentness/Recovery Separation | `EXPOSES` | `MO-F07` Discovery Failure | Once owner-known recovery works, missing owner-unknown/paraphrase discovery becomes visible as a separate problem. |
| `MO-M08` Engineering/Effect Boundary | `INHIBITS` | `MO-F05` Explicit Overcommitment | Separate consumption/effect standing prevents theory truth from becoming automatic irreversible authority. |
| `MO-M09` Verification/Recoverability | `COMPENSATES_FOR` | `MO-F08` Implementation Error | Exact tests/receipts/snapshots bound diagnosis and repair after mechanical faults. |
| `MO-M10` Survivorship/Workload Selection | `CONFOUNDS` | naive prevalence claims about all mechanisms/failures | Selected survivors can make self-correction appear more common or more dramatic than fixed-window evidence supports. |

## Important absence

No edge here means:

- the mechanism is sufficient for research quality;
- the failure family is prevented universally;
- one mechanism causally dominates all others;
- this graph is a required execution sequence.

The strongest current explanation remains plural: multiple mechanisms interact, while workload selection changes what is visible to retrospective analysis.
