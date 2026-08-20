# PPD Method-Combination Protocol v0.1

## Objective

Measure whether combining epistemic transformations expands the support of useful separator/repair proposals relative to a narrower incumbent generator, while preserving temporal isolation and claim-specific adjudication.

The target is **proposal-support expansion**, not majority-vote accuracy.

## Frozen information boundary

For a historical case with cutoff `t0`, construct:

- `A0`: source-fenced evidence dated at or before `t0`;
- `B1`: adjudication evidence strictly after `t0`;
- no generator may inspect `B1` before its proposal set is frozen.

For q_008, the released upstream evidence-graph question is already a historically frozen proposal. Our current analysis is allowed to inspect the future only to calibrate the combination protocol; it must not be represented as a new prospective discovery result.

## Generator families

The experiment should compare **support sets**, not model names.

1. `G_polarity`: proposes pressure only when pre-cutoff claims have opposite outcome polarity.
2. `G_consensus`: treats cross-dataset same-direction replication as stronger incumbent standing unless explicit contradiction exists.
3. `G_genealogy`: asks whether physically distinct datasets still share retrieval/model/calibration assumptions or inferential lineage.
4. `G_multiverse`: proposes a bounded family of alternative admissible analysis/retrieval assumptions on retained data.
5. `G_countermodel`: constructs a common-mode-error rival world capable of producing apparently concordant cross-dataset results.
6. `G_orthogonal`: proposes a target-preserving modality or dataset whose error genealogy is materially different.

`G_polarity` and `G_consensus` are negative-control generator classes here. q_008 has same-direction pre-cutoff water claims, so a pure polarity trigger should not fire.

## Candidate representation

Each candidate is a typed repair program, not one global atomic label:

```text
precondition -> operation -> claim-level effect -> next admissible operation
```

Example abstract program:

```text
subsolar claim appears cross-dataset stable
-> vary retrieval/systematics assumptions on retained data
-> if standing becomes model-sensitive, downgrade atmospheric-property claim
-> acquire independent high-resolution constraint
-> ground abundance claim
```

## Metrics

Keep metrics separate.

### Proposal support gain

For generator `Gi`, let `P_i(A0)` be its frozen proposal support. Ecology support is:

`P_ecology(A0) = union_i P_i(A0)`.

Support expansion exists only if a useful future-supported proposal lies in `P_ecology \ P_incumbent`.

### Resolution-component coverage

Define future resolution components from source-fenced `B1`, not from generator language. For q_008 the documented components are:

- retained/new spectral reanalysis with improved systematics/model averaging;
- alternate retrieval frameworks/assumptions;
- independent high-resolution spectroscopic constraint.

A generator gets component coverage only for a proposal frozen before future reveal whose requested discriminator maps to that component.

### False-route burden

Count proposals that require target-changing evidence, violate source fences, or would be expensive but non-discriminating. Do not reward proposal count itself.

### Common-mode novelty

Record whether a generator explicitly identifies a dependency invisible to the incumbent representation, such as shared retrieval assumptions despite independent physical datasets.

## Combination experiment

Use factorial ablations rather than one monolithic PPD agent:

- temporal fence only;
- temporal + genealogy;
- temporal + multiverse;
- temporal + countermodel;
- temporal + genealogy + multiverse;
- temporal + genealogy + countermodel + orthogonal retrieval;
- full ecology union.

The question is whether particular compositions create candidates absent from narrower supports.

## q_008 calibration expectation

The real historical resolution implies the following calibration target:

`IndependentDatasets != IndependentInferenceAssumptions`.

A useful combination should be capable of proposing both:

1. vary/reanalyse retrieval assumptions on existing/archival spectra;
2. obtain an independently grounded spectroscopic constraint.

This is a **calibration expectation known from the future**. It is not a prospective score for our present generator.

## Reopen condition

This local experiment reopens the broad open-interface theory only if a method combination reveals a selective-repair distinction that cannot be represented by existing claim-relative, lineage/common-mode, representation, measurement and validation responsibilities.
