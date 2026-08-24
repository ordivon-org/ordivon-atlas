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
```

These surfaces return **non-authoritative candidate projections**. The caller still owns semantic equivalence, relevance, novelty/admission, and whether deeper owner inspection is required. Use `check` / `refresh` when the operation actually requires owner-source currentness observation or regenerated Atlas views; do not make whole-Atlas refresh a prerequisite for every research question.

## MVP

The first MVP consumes heterogeneous owner sources. **Interlocus** (stable identity `research-owner:network`, historical name Network) lives inside the shared `ordivon-research` durability repository; Runtime lives inside the independent `ordivon-runtime` repository.

Each pilot owner exposes a corpus-relative `authority/CURRENT.json` pointer to an immutable `authority/publications/<sha256>.json` payload. The payload SHA-256 is the owner `AuthorityVersionRef`.

Atlas uses read-only source transports and checks:

1. the configured owner/authority identity;
2. the remote owner ref and exact transport commit;
3. owner `CURRENT` existence and syntax;
4. publication path safety and reachability;
5. exact publication SHA-256;
6. current-recovery target role and locator;
7. source advancement relative to a previous projection.

A source may define multiple read transports. Atlas tries them in order and still fails closed if none can establish the current remote ref.

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
PYTHONPATH=src python -m ordivon_atlas check
PYTHONPATH=src python -m ordivon_atlas refresh --out generated
PYTHONPATH=src python -m unittest discover -s tests -v
ORDIVON_ATLAS_LIVE_TESTS=1 PYTHONPATH=src python -m unittest tests.test_live -v
```

Default tests are deterministic local destructive fixtures. Live remote acceptance is explicit so temporary public-network failure is not misreported as a code regression.

The MVP intentionally has no database, daemon, web UI, or MCP. Those are consumer/materialization options to consider only after generated whole-owner projection exposes concrete interaction pressure.
