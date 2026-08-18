# External Exploration Reference Model

This directory contains **non-authoritative external coordinate models** used by Ordivon Atlas to reason about possible exploration space.

It is not the World / Reality research owner, not an Ordivon ontology of reality, and not a replacement for owner-native research authority.

## v0 foundational disciplines

`foundational-disciplines-v0.json` starts with a **Seed Wave 0** of Mathematics, Philosophy, Physics, Biology, Chemistry and Engineering. These six were chosen to stress-test the schema; they are **not** the complete set of foundational disciplines. The foundational-domain census remains explicitly open and its eventual root count is unknown. The model is intentionally bounded and open-world.

### Relation discipline

- Wikipedia outline membership is imported as `TOPICAL_MEMBER_OF`, not `SUBCLASS_OF`.
- `SUBCLASS_OF` is reserved for sources with explicit class semantics such as Wikidata P279.
- Cross-domain spaces are first-class `OVERLAP_SPACE` nodes and may belong to multiple domains without a single canonical parent.
- `NOT_REPRESENTED` never means `DOES_NOT_EXIST`.

### Separation from Atlas owner truth

The reference model may later receive `ORDIVON_CROSSWALK` and `COVERAGE_ASSESSMENT` records, but those are projections/comparisons. External sources cannot admit, supersede, withdraw or reopen Ordivon research results.

### Deferred

Social/political/institutional expansion remains later. Before that expansion, Atlas must first conduct a broad **Foundational Knowledge Space Census** rather than deepening only the original six seeds.
