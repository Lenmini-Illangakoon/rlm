# Frozen offline protocol

Baseline pin: `e11f1a8f8ee4490686e16dd6463233abe08a07eb`. Branch: `experiment/official-rlm-h2-h5-h6-baseline`. Official runtime, prompts and upstream tests remain unchanged. Local environment; speculative PTC, persistence, compaction and RootCheck disabled. All current outputs are synthetic engineering evidence.

## Tasks

S1 is exact EXP-3B seed-301 context and query. The independent solver joins exact Order IDs, deduplicates/validates Record IDs, filters posted shipments, approved refunds and open orders, excludes orphans and selects strictly positive balances. It reconstructs 60 IDs totaling 1,361; membership agrees with the archived oracle.

S2 is the approved S2-v2 shipment dossier, not S2-v1. The renderer version `S2-v2.1-renderer` names this implementation revision; it does not designate a changed scenario. It uses the approved SHA-256 permutation of visible indices 1–160, latent quantity/status rules including the i=156 tie, four independently ordered sections and eight archived notes. The independent parser imports no generator code. It reads the final note text, checks exact joins and source associations, excludes archives, filters eligibility and ranks by quantity descending then numeric ID ascending. It finds 100 eligible shipments and SH-10106 / SH-10068 / SH-10097 with quantities 6,883 / 6,846 / 6,809 and total 20,538. SH-10138 loses the tie; SH-10128 has insufficient stock. All selected R/W/Q/H source references are preserved.

S3 preserves EXP-3F seed-701 context bytes and appends the approved public coverage specification to the historical query. It is a controlled historical variant. The oracle validates 320 inventory records and 4+4 excluded records, exact ACTIVE/APAC scope, unique numeric IDs and ordered minima 3731/4637 with product 17,300,647.

Frozen contexts and queries are the only task data given to the runtime. Oracles and assessment records are researcher-only. No live use of this layout is permitted until an OS boundary prevents runtime access to them.

## Pilot and gates

| Round | Execution order |
| --- | --- |
| 1 | S1-R01 → S2-R01 → S3-R01 |
| 2 | S2-R02 → S3-R02 → S1-R02 |
| 3 | S3-R03 → S1-R03 → S2-R03 |

After round one, stop for an engineering review of instrumentation, source integrity and cost controls, independent of whether desired failures occurred. At the end of **any** round, if **two or more runs cumulatively are resource-censored**, stop further pilot execution and review the protocol. Preserve completed and censored runs. Do not automatically raise budgets or replace runs. Version material changes and do not silently pool affected runs. This threshold was explicitly confirmed by the user on 2026-11-24.

Preserve operational failures, infrastructure failures, cancellations and resource censoring separately from hypothesis labels. All runs support all applicable hypotheses. Insufficient delegated-action exposure is a limitation of H2 delegation strata, not an observed absence of all H2. If H6 sufficiency cannot be established, use non-applicable or inconclusive with reasons; do not count extra turns as waste.

## Runtime and resource envelope

Provisional model identifiers: root `openai/gpt-5`, depth-one plain calls `openai/gpt-5-nano`, provider OpenRouter. Genuine recursive children inherit the main model. At the recursive depth limit the pinned runtime chooses the other backend. Deeper plain calls follow the pinned LMHandler routing, which differs from genuine-recursion routing. No routing is rewritten. Recursive concurrency remains 4 and plain-batch concurrency 16.

Limits: $2 per run; $20 per campaign; 24 provider attempts per run including descendants; 64,000 input and 32,768 completion tokens per request; 900 seconds per run; depth 2; 10 iterations per RLM instance. Completion cap is passed to the synthetic clients through the same sampling configuration. Test fixtures explicitly override iteration count only when testing limit behavior. No temperature/seed or live compatibility claims are made.

The parent-owned Decimal ledger reserves `(input_bound × input_rate + output_bound × output_rate) × 1.10` before dispatch under one lock, across concurrent calls and all descendants. Reconcile actual known usage and release only the unused reservation. Unknown usage retains the reservation and stops new dispatch; cancellation retains unresolved in-flight exposure. Observed usage beyond the bound is accounted honestly and stops the run. Each retry would require a new ticket; a future SDK adapter must disable hidden retries or expose every retry to the supervisor. No built-in RLM cost aggregate is used as the admission guarantee.

Mock clients use explicitly synthetic rates and synthetic token counts/bounds, not tokenization of the real prompt and not actual provider prices. The ledger rejects unpriced model overrides. Parent supervision kills the worker on admission denial, timeout or cancellation, so a denied child call cannot be converted into an ordinary model-visible error string and execution cannot resume. A safety-censored prefix is not a completed natural run. Remote provider cancellation and billing cannot be established with mocks.

## Isolation and live preflight blockers

The original negative probe executes `open()` on an absolute researcher-canary path through ordinary LocalREPL and succeeds. It remains a negative control in the existing suite. The Windows AppContainer boundary now passes all nine protected-path probes and all 21 affected behavioral comparisons; the default offline mock entry point requires it. See [Windows isolation evidence and limits](WINDOWS_ISOLATION.md).

The boundary stages pinned runtime copies and allowlisted support files, with read/execute payload permissions, writable low-integrity scratch, no inherited handles/environment, zero AppContainer capabilities and a one-process Job. Official RLM source remains unchanged. An experiment-only tempfile adapter inherits scratch ACLs so LocalREPL can create/read public context. Canary and denied-handle tests verify oracle/assessment path protection; no real credentials were read. Earlier import guards and same-account supervision alone remain insufficient.

The `broker-integration-1` engineering revision connects the isolated official RLM to external provider admission/accounting and uses fresh per-run profile/scratch cleanup. [Targeted evidence and exact live-preflight requirements](LIVE_PREFLIGHT.md) replace the earlier implementation blockers. The original pickle supervisor remains only a trusted-fixture utility. Live is still disabled; provider model/rate/bound/usage/timeout facts and explicit authorization remain required. Public tasks, pinned source, pilot order, limits and stop rules are unchanged. Material protocol changes require versioning and affected runs must not be silently pooled.