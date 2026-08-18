# Ordivon Atlas

Ordivon Atlas is the **generated institutional, exploration, history, and recovery projection** over owner-native research authority surfaces.

Atlas is deliberately not a second research corpus and not a semantic source of truth. Owners publish their own current authority version and recovery surface; Atlas verifies those source fences and produces regenerable views plus Research Observatory health diagnostics.

## MVP

The first MVP consumes two live heterogeneous owner sources:

- Network inside the shared `ordivon-research` durability repository.
- Runtime inside the independent `ordivon-runtime` repository.

Each pilot owner exposes a corpus-relative `authority/CURRENT.json` pointer to an immutable `authority/publications/<sha256>.json` payload. The payload SHA-256 is the owner `AuthorityVersionRef`.

Atlas checks:

1. the configured owner/authority identity;
2. the remote owner ref and exact transport commit;
3. owner `CURRENT` existence and syntax;
4. publication path safety and reachability;
5. exact publication SHA-256;
6. current-recovery target role and locator;
7. source advancement relative to a previous projection.

It fails closed into `CURRENTNESS_UNKNOWN`, `BROKEN_POINTER`, or `AUTHORITY_CHANGED_UNRESOLVED`; a prior projection that differs from a healthy current owner version is `SOURCE_ADVANCED_STALE`.

## Generated views

`ordivon-atlas refresh` produces:

- `owner-map.json`
- `current-recovery.json`
- `results.json`
- `closure.json`
- `negative-history.json`
- `history.json`
- `projection-health.json`
- `atlas.json`

Every semantic projection row carries the owner `AuthorityVersionRef` and source transport revision. Generated files are projections, never owner truth.

## Use

```bash
PYTHONPATH=src python -m ordivon_atlas check
PYTHONPATH=src python -m ordivon_atlas refresh --out generated
PYTHONPATH=src python -m unittest discover -s tests -v
```

The MVP intentionally has no database, daemon, web UI, or MCP. Those are consumer/materialization options to consider only after the generated projection proves useful under real research load.
