# C3 E1b — Final adjudication

**Status:** valid sealed discriminator pilot complete.

## Frozen question

E1b tests only `B_spontaneous`: with one fixed unchanged actor, after a deterministic selector has identified a reusable strategy, does coherent post-selection suppression of that strategy and all external residual carriers still permit same-episode exact regeneration from unchanged primitive operations?

## Apparatus validity

Pilot-1 was invalidated prospectively because it passed a bare JSON schema where Harness required a structured completion contract. E1b changed only that apparatus boundary to `{mode: structured-result-v1, resultKind: c3-e1b-program, resultSchema: ...}`. Frozen Harness actor `09414f06a622397cdfd95dda4d52484f8ef0e9a1` was reconstructed byte-exactly with pinned protocol dependency `420dc356cb664d75db0f34f356156baebe5843db`; contract tests passed 6/6 and a generic non-efficacy currentness canary completed with the frozen DeepSeek model/config.

The sealed 8-instance tranche then passed post-seal execution integrity: all eight precommitted provider request digests matched, all effective models were `deepseek-v4-flash`, all finish reasons were `tool_calls`, and all Runtime tool-call counts were zero.

## Frozen primary endpoint

Primary endpoint: number of certified `B_spontaneous` reconstructions among the four prospectively assigned SUPPRESS instances.

Observed:

- SUPPRESS: **0 / 4 certified**. All four returned structurally valid, within-budget primitive programs, but none was functionally equivalent to the target on the full 8-state domain.
- USE sanity/ceiling arm: **4 / 4 certified**. All four reconstructed the unique shortest length-4 target program exactly.

Therefore: `NO_CERTIFIED_B_SPONTANEOUS_IN_PILOT`.

## Interpretation ceiling

This is a discriminator pilot, not a population-rate estimate. It provides no positive evidence for `B_spontaneous` under this frozen fresh finite-transformer constitution. The perfect USE/SUPPRESS separation is bounded evidence that access to the selected reusable strategy materially changed behavior in this pilot and, critically, confirms that the corrected task/output apparatus was operational.

It does **not** establish that the model can never regenerate a suppressed strategy, does not estimate a universal regeneration probability, and does not establish or refute open-interface/basis escape, robotics transfer, or general algorithmic competence. No retries, repair prompts, post-outcome retuning, or Pilot-1 instance reuse are admitted.

## Evidence anchors

- E1b prereg SHA-256: `d1789258434559daeadca90a5e04720087d87366c7b4302ef6500a48cd0ab84f`
- Seed commitment SHA-256: `0cfc32aea6ab03c965d53b0f05e5fc4b094ec02fc16533b26e9deb82ae1be597`
- Public manifest SHA-256: `7043285a7ce1e18d450a0c5d42bdfd994dbf3e9433ee76070c911b5410caef26`
- Materialization audit SHA-256: `c58b20c9207283e096db6b2cc309b045a45f7ee92b45515193daad02f595c9e4`
- Runner SHA-256: `1ba7d0325765f364965d90a1381d1f4869ad8005a74b98eb01c0d30a7b4f7847`
- Execution Seal SHA-256: `58e8d1807f4a2c3b20a8240df48efdad59d63ff1ecd0787557de76fa82504bb1`
- Post-seal integrity audit SHA-256: `c431cd3ca7cb543b743f65acb8f6dd00c70fc0c3581d450e4cbe9989189abd15`
- Efficacy result summary SHA-256: `55b27ef89bbaaebf4f5c469bedbd6e9d5f1c879576d5648b23f4ec7b63550c4b`
