# Failure Ecology

Failure families are observational classes for diagnosis and recovery. They are not one scalar risk taxonomy and they do not imply that every failure has one cause.

| Ref | Failure family | Observable signature | Discriminant | Consequence type | Representative recovery direction |
|---|---|---|---|---|---|
| `MO-F01` | Wrong / Incomplete Representation or Problem Frame | Research remains coherent inside a frame but counterexamples/residuals show the frame itself is mis-specified. | Distinguish from ordinary negative result: the failure attacks the problem decomposition/evaluator/owner representation, not merely one hypothesis. | semantic / epistemic | fresh representation or whole-space search; discriminating regime; minimal repair |
| `MO-F02` | Premature Route / Project / Foundation Promotion | A candidate acquires durable route/project/Foundation standing before dependencies or falsifiers justify it. | Differs from `MO-F04`: the promotion can be explicit, but it is epistemically premature rather than silently inherited. | semantic standing | cancel/noncanonical status; dependency correction; fresh restart |
| `MO-F03` | Stale Continuity / Currentness Confusion | A historically valid handoff/READY state is resumed after later owner truth has moved. | Historical continuity remains true; current semantic recovery points elsewhere. | recovery / currentness | resolve owner-current authority; preserve old continuity only as history |
| `MO-F04` | Silent Escalation | Weak/local standing silently acquires stronger commitment authority without an explicit promotion decision. | No explicit high-standing decision can be reconstructed at the commitment boundary. | semantic + effect | require explicit target/authority/currentness/recovery basis before commitment |
| `MO-F05` | Explicit Overcommitment | An explicit standing exists but grants more irreversible authority than the evidence/intent justifies. | Unlike silent escalation, commitment authority is explicit but too broad. | effect / retention | separate retirement/change standing from annihilation; preserve admissible option/history |
| `MO-F06` | Evaluator / Apparatus / Workflow Bias | Search/evaluation favors what is measurable, Agent-friendly, easy to score or convenient for apparatus rather than what best resolves the question. | The bias enters through the evaluator/measurement/workflow, not necessarily the candidate theory. | epistemic / measurement | challenge evaluator/apparatus; use natural/cheap evidence; independent holdout/reality checks |
| `MO-F07` | Discovery / Anti-Rediscovery Failure | Relevant negative/superseded knowledge exists but cannot be recovered from a new paraphrase or owner-unknown query. | Preservation succeeded; discovery failed. Keyword presence alone is insufficient. | recovery / information | Process Lineage + owner-unknown discovery hooks + causal rationale |
| `MO-F08` | Implementation / Mutation Error | Intended semantic decision is reasonable but code/config/file mutation is mechanically wrong. | Do not reopen theory solely because implementation failed. | mechanical | tests, static checks, exact diffs/effects, Runtime/Git recovery |
| `MO-F09` | Retention / Capability Confusion | Preserving history is conflated with preserving live capability, sensitive bytes or revocable access. | Audit lineage may be valuable while the capability itself must be destroyed. | retention / security | apply retention admissibility; preserve lineage != preserve capability |
| `MO-F10` | Survivorship / Documentation Bias | Conclusions about research quality/failure rates are drawn from memorable, well-documented survivors. | Distributional claim changes when fixed-window/balanced sampling is used. | methodological inference | fixed-window/task-trajectory sampling; explicit denominators; reject naive keyword statistics |

## Non-collapse rules

```text
MO-F01 != MO-F08        # representation failure != implementation bug
MO-F02 != MO-F04        # premature explicit promotion != silent escalation
MO-F04 != MO-F05        # silent escalation != explicit overcommitment
MO-F07 != raw data loss # discoverability can fail even when bytes survive
MO-F09 != delete history
MO-F10 != explanation for every observed correction
```

A real episode can instantiate more than one family. `INTERACTION-MAP.md` records only recurrent, bounded relations that have evidential support.
