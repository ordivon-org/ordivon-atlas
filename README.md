# Ordivon Atlas

Ordivon Atlas is the **generated institutional, exploration, history, and recovery projection** over owner-native research authority surfaces.

Atlas is deliberately not a second research corpus and not a semantic source of truth. Owners publish their own current authority version and recovery surface; Atlas verifies those source fences and produces regenerable views plus Research Observatory health diagnostics.

## Agent first interface

For ordinary prior-work recovery, a fresh Agent should **not** begin by replaying research chronology or regenerating every Atlas view. Start from the smallest retrieval representation that matches the current operation:

```bash
# See how Atlas currently represents retrieval and which owner-curated coordinates
# can help the caller author bounded query variants. This does not translate intent.
PYTHONPATH=src python -m ordivon_atlas retrieval-authoring-context

# Search prior-result candidates. Query variants are caller-authored; Atlas does not
# infer that they are semantically equivalent or grant novelty/research standing.
PYTHONPATH=src python -m ordivon_atlas first-look "<query>"
PYTHONPATH=src python -m ordivon_atlas first-look-many "<variant-1>" "<variant-2>"

# After selecting one bounded candidate, inspect that exact candidate rather than
# widening immediately to arbitrary repository reads.
PYTHONPATH=src python -m ordivon_atlas inspect-candidate "<query>" "<path>" "<locator>"

# When the operation needs a current owner-source fence, hydrate only that owner.
# Selectors are mechanical registry/locator aliases, not semantic query translation.
PYTHONPATH=src python -m ordivon_atlas check-owner Interlocus
# Expand owner bytes only when the operation actually needs them:
PYTHONPATH=src python -m ordivon_atlas check-owner Interlocus --include-publication
```

`check-owner` defaults to a bounded currentness capsule (identity, source/authority fence, recovery locator and health) rather than echoing the full owner publication into Agent context. These surfaces return **non-authoritative candidate projections**. The caller still owns semantic equivalence, relevance, novelty/admission, and whether deeper owner inspection is required. Use `check-owner <selector>` for owner-scoped currentness, `check` for an explicit whole-registry observation, and `refresh` only when regenerated Atlas views are required; do not make whole-Atlas hydration a prerequisite for every research question.

Representation adequacy remains consumer-owned. Atlas previously exposed an experimental generic `select-representation` helper that accepted caller-declared distinctions, costs and profiles and then chose the cheapest adequate row. A destructive consumer census found no current external/source consumer: the real P2 pressure had already been satisfied by bounded owner-scoped projections such as `check-owner`, while the generic selector merely re-expressed caller policy inside Atlas. The helper is therefore retired; historical P2 evidence and its example remain recoverable as provenance, not as a current Atlas command.

The same surface audit keeps `retrieval_representation_profile()` and `retrieval_coordinate_profile()` as implementation components of the consumed `retrieval-authoring-context`, but retires their standalone CLI commands. No current consumer invoked the components independently, so exposing them as separate Agent operations only duplicated internal decomposition.

## MVP

The first MVP consumes heterogeneous owner sources. **Interlocus** (stable identity `research-owner:network`, historical name Network) has the standalone current physical home `ordivon-interlocus`; Runtime has the independent `ordivon-runtime` repository. Atlas configuration binds physical source locators separately from semantic owner identity, so the Network → Interlocus name/physical transition does not rename `research-owner:network`.

Each pilot owner exposes a corpus-relative `authority/CURRENT.json` pointer to an immutable `authority/publications/<sha256>.json` payload. The payload SHA-256 is the owner `AuthorityVersionRef`.

Atlas uses read-only source transports and checks:

1. the configured owner/authority identity;
2. the remote owner ref and exact transport commit;
3. owner `CURRENT` existence and syntax;
4. publication path safety and reachability;
5. exact publication SHA-256;
6. current-recovery target role and locator;
7. source advancement relative to a previous projection.

A source may define multiple read transports. Remote-backed sources use `remote_git`; private canonical repositories may use `local_git`, which resolves an explicit local Git ref to one exact commit and reads committed bytes rather than the working tree. Atlas fails closed when the selected transport cannot establish an exact source revision.

`local_git` is a currentness transport, not a claim of public release, cross-machine distribution, or backup durability. Source distribution topology remains owner/source metadata; whether Atlas can prove currentness is an Atlas consumer capability. For declared `git-multi-ref-aggregate` publications, Atlas additionally verifies the aggregate-manifest digest and every exact revision/path/byte/SHA anchor mechanically before returning `CURRENT_TO_SOURCE`.

## Owner coverage and institutional topology

The admitted research source registry is deliberately **not** the complete owner topology. `config/sources.json` contains only owners that expose an owner-native immutable **research authority** publication. Atlas must not manufacture research standing merely because a repository has another legitimate institutional responsibility.

To prevent the opposite failure — a real, deferred, or non-research owner disappearing from institutional representation — Atlas keeps two separate non-authoritative planes:

- `config/owner-frontier.json` classifies the discovered repository universe for coverage/reconciliation. `INSTITUTIONAL_OWNER_REPRESENTED` is a terminal coverage state distinct from `NON_OWNER` and from research-owner admission states.
- `config/institutional-owners.json` records source-fenced references for non-research institutional owner facets. It points back to owner-native recovery surfaces and never becomes semantic authority itself.

`institutional-owner-topology.json` merges registered research-authority facets with represented non-research facets without pretending the facets are mutually exclusive repository types. A future Host, Runtime, or other repository may expose additional institutional facets without losing its research-owner identity. Verification levels remain explicit: research rows are backed by immutable owner publications; non-research rows prove exact Git source plus owner-native recovery presence.

```bash
# Classify the current repository universe without remote owner observation.
PYTHONPATH=src python -m ordivon_atlas coverage-check

# Verify non-research institutional source fences independently of research authority currentness.
PYTHONPATH=src python -m ordivon_atlas topology-check

# refresh writes both coverage and topology projections alongside research views.
PYTHONPATH=src python -m ordivon_atlas refresh --out generated
PYTHONPATH=src python -m ordivon_atlas show coverage --out generated
PYTHONPATH=src python -m ordivon_atlas show topology --out generated
```

The coverage audit scans configured local discovery roots and reports any repository that is neither a registered research-owner source nor explicitly classified in the frontier as `UNCLASSIFIED_REPOSITORY`. Missing discovery roots fail closed rather than being interpreted as an empty repository universe. A temporary admission deferral must carry reconsideration triggers. The key separation is:

```text
repository discovery / cross-owner recognition
        -> non-authoritative coverage frontier
        -> owner-side boundary adjudication
        -> research authority? -> owner-native immutable publication -> sources.json
        -> non-research institutional authority? -> source-fenced owner recovery -> institutional topology
```

Thus `absence from sources.json` no longer means `absence from Reality`, and `institutional owner` no longer implies `research owner`. Atlas still cannot create semantic authority. Source-fenced recovery proves only that the referenced owner boundary exists at an exact source revision; Web publication admission, Workstation live physical currentness, and projected-owner semantics remain with their actual authorities.

## Federated refresh semantics

Projection health is **per owner**, not one global all-or-nothing bit. A healthy owner may advance even while another owner is temporarily unavailable.

- `CURRENT_TO_SOURCE`: the owner publication is verified at its current source fence.
- `SOURCE_ADVANCED_STALE`: a retained prior Atlas version differs from the newly verified owner version.
- `CURRENTNESS_UNKNOWN`: the current authority fence cannot be proven.
- `BROKEN_POINTER`: a declared current/publication/recovery binding is internally broken.
- `AUTHORITY_CHANGED_UNRESOLVED`: configured and observed authority identities conflict.

When a source is unhealthy and a prior source-fenced projection exists, Atlas retains that owner's last-known rows with `retainedFromPreviousProjection=true` and sets their `projectionCurrentness` to the unhealthy state. The old bytes remain useful recovery/history material but are **not presented as current truth**. Other healthy owners may refresh normally in the same global snapshot.

## Result classification

Result standing, epistemic verdict, evidence scope, and structural role are projected from authority-qualified statements targeting the exact `ResultRef`. Atlas does not inherit a closeout-wide status onto every result. If an owner publication lacks explicit result classification, the result remains discoverable with `classificationHealth=UNKNOWN` rather than receiving fabricated standing.

## Curated synthesis

[`synthesis/`](synthesis/) is a Git-durable, manually curated **non-authoritative cross-owner synthesis layer**. It exists to preserve high-value conceptual compression, Human-facing explanation, and prior-result/anti-rediscovery guidance that would otherwise remain trapped in conversations or be repeatedly re-derived.

Synthesis entries do not replace owner-current publications and must be repaired or marked stale when their source owners materially advance.

## Generated views

`ordivon-atlas refresh` produces:

- `owner-map.json`
- `owner-coverage.json`
- `institutional-owner-topology.json`
- `current-recovery.json`
- `results.json`
- `closure.json`
- `negative-history.json`
- `history.json`
- `projection-health.json`
- `projection-health-latest.json`
- `atlas.json`

Every semantic projection row carries the owner `AuthorityVersionRef` or an explicitly retained last-known source fence. When an owner publication declares `CANONICAL_NAME`, `CANONICAL_REFERENT`, or `HISTORICAL_NAME`, `owner-map.json` projects those as descriptive metadata while preserving the stable `ownerResearchRef` identity. Generated files are projections, never owner truth. The `generated/` directory is intentionally Git-ignored.

## Use

```bash
scripts/owner-environment bootstrap
scripts/owner-environment doctor
scripts/owner-environment test
.venv/bin/ordivon-atlas check-owner Interlocus
.venv/bin/ordivon-atlas check
.venv/bin/ordivon-atlas refresh --out generated
ORDIVON_ATLAS_LIVE_TESTS=1 .venv/bin/python -m unittest tests.test_live -v
```

`scripts/owner-environment` is the canonical repository-owned environment entrypoint. `cold-start` uses a fresh temporary venv, so passing it proves Atlas does not depend on an ambient `PYTHONPATH` or previously warmed Workspace.

Default tests are deterministic local destructive fixtures. Live remote acceptance is explicit so temporary public-network failure is not misreported as a code regression.

The MVP intentionally has no database, daemon, web UI, or MCP. Those remain consumer/materialization options, not roadmap items. Reopen them only when a real consumer exposes interaction pressure that the current bounded first-look, owner-scoped currentness, regenerable views, and ordinary library/CLI composition cannot resolve; whole-owner hydration is not a prerequisite for discovering that pressure.
