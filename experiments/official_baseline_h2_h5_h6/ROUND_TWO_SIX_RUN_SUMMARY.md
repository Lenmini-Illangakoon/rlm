# Round 2 completion and six-run summary

**Round 2 completed in the exact authorized order: S2-R02, S3-R02, S1-R02. All six baseline executions so far completed and returned correct complete answers. Round 3 has not started.** No datasets, queries, models, official source or experimental configuration were modified based on observations. RootCheck remained disabled in the pinned official RLM inside AppContainer.

## Execution results

| Run | Actual-answer oracle result | Root iterations | Calls: root / plain | Official seconds | Provider-reported cost | Conservative debit |
|---|---|---:|---|---:|---:|---:|
| [S1-R01](S1_R01_EXECUTION_RESULT.md) | Correct: 60 IDs, total 1,361 | 4 | 4 / 0 | 76.404 | $0.08246875 | $0.09902875 |
| [S2-R01](S2_R01_EXECUTION_RESULT.md) | Correct: top 3, quantities, 12 references, total 20,538 | 8 | 8 / 2 | 444.481 | $0.17427805 | $0.20135005 |
| [S3-R01](S3_R01_EXECUTION_RESULT.md) | Correct: 3731, 4637; product 17,300,647 | 3 | 3 / 0 | 38.112 | $0.03427350 | $0.03873750 |
| [S2-R02](S2_R02_EXECUTION_RESULT.md) | Correct: top 3, quantities, 12 references, total 20,538 | 5 | 5 / 0 | 75.125 | $0.07901500 | $0.09485500 |
| [S3-R02](S3_R02_EXECUTION_RESULT.md) | Correct: 3731, 4637; product 17,300,647 | 3 | 3 / 0 | 32.870 | $0.03122600 | $0.03713000 |
| [S1-R02](S1_R02_EXECUTION_RESULT.md) | Correct: 60 IDs, total 1,361 | 3 | 3 / 0 | 43.423 | $0.04527075 | $0.05347875 |

Round 2 alone used 11 root GPT-5 calls in 11 iterations, with no plain subcalls, recursive children or batches. It consumed 39,731 prompt and 13,580 completion tokens. Reported cost was **$0.15551175** and conservative debit **$0.18546375**. All three runs had empty Python stderr, normal completion, verified usage/routing, reconciled requests and successful cleanup. The natural execution paths differed from Round 1 without any intervention or prompt redesign.

Across all six runs: **28 provider calls** (26 root GPT-5, 2 plain GPT-5-nano), **26 root iterations**, **218 raw chronological events**, and **129,489 prompt + 97,082 completion = 226,571 tokens**. No genuine recursive child or batch occurred naturally. The approved resolved endpoints remained `openai/gpt-5-2025-08-07` and, where used in S2-R01, `openai/gpt-5-nano-2025-08-07`, routed through OpenAI only without fallback.

## Costs and campaign accounting

Six-run provider-reported inference cost is **$0.44653205**. Conservative pilot debit is **$0.52458005**; uncached input pricing accounts for the $0.07804800 protective difference. Native completion usage already includes reasoning; it is not charged a second time or added again from nested trajectory summaries.

Campaign exposure is **$0.97340915** = conservative pilot debit $0.52458005 + once-imported preflight exposure $0.44882910. The preflight exposure retains the unchanged **$0.4484480 unresolved reservation** and $0.00038110 known preflight charges. Known response-reported inference charges including those preflight charges are $0.44691315. These figures do not claim an independent account-billing lookup. Remaining protected headroom against $20 is **$19.02659085**.

All actual run debits remain below $2. Every pilot ticket reconciles with zero remaining reservation, no new unknown exposure, and no telemetry conflict. All runs are below 24 attempts and 900 seconds, and recorded input bounds/completion caps respect 64,000/32,768. No budget was increased, reservation released, request retried, run replaced or provider probe made during Round 2.

## Cumulative resource-censoring rule

At the end of Round 2, **0 of 6 runs are resource-censored**. The prescribed threshold is **two or more cumulatively by the end of any round**. **The resource-censoring stop rule is not triggered.**

S2-R01's second nano subcall ended with `finish_reason=length` at its request completion cap. Its parent run recovered and completed, so it remains an explicitly resource-confounded action outcome, not a run-level resource-censored record or an unconstrained reasoning finding. No retained run is omitted from this count.

## Preliminary hypothesis observations

| Run | H2 | H5 | H6 |
|---|---|---|---|
| [S1-R01](evaluators/S1-R01-preliminary-observations.md) | None demonstrated | Provisionally not observed | None demonstrated |
| [S2-R01](evaluators/S2-R01-preliminary-observations.md) | **Strong prose-for-JSON mismatch candidate** | Provisionally not observed | Potential avoidable prose-only continuation; redundant computation not established |
| [S3-R01](evaluators/S3-R01-preliminary-observations.md) | None demonstrated | Provisionally not observed | None demonstrated |
| [S2-R02](evaluators/S2-R02-preliminary-observations.md) | None demonstrated | Provisionally not observed | None demonstrated |
| [S3-R02](evaluators/S3-R02-preliminary-observations.md) | None demonstrated | Provisionally not observed | None demonstrated |
| [S1-R02](evaluators/S1-R02-preliminary-observations.md) | None demonstrated | Provisionally not observed | None demonstrated |

Each separate note identifies exact event/action references and actual root-visible histories. These are retrospective preliminary observations, not formal blinded assessments. H2/H6 remain inconclusive pending the prescribed contract/sufficiency review; H5 awaits human support/visibility confirmation. Correct answers do not establish that a mechanism is absent. S1-R02's complete set is printed and directly submitted within the same block, after the root had seen only a sample: the notes preserve that distinction and do not falsely claim full-list root visibility or automatically count supported deterministic finalization as a visibility failure.

## Evidence preservation and integrity

[Machine-readable consolidated results](results/round-two-six-run-summary.json) link every run's summary, raw record, raw trace, preliminary notes and checksums. Each execution report links the worker response and finalized journal as well. Exact prompts/responses, generated Python, full captured stdout/stderr, plain-call correlation, root request histories, final captures/selections/actual answers, native usage, price verification and timing remain on disk. Previous raw executions, preliminary notes and Round 1 checkpoint are preserved.

Post-run checks verified all new provider prompts/delivered responses against the trace, journal/worker archival, chronology/result pairs, runtime identity and oracle scoring. Consolidation verified all six immutable evidence references, unique request/generation IDs, actual-return consistency and cumulative accounting. Frozen implementation/policy and 90 protected files remain unchanged; each runtime reports all 35 matching official source hashes. Cleanup passed for all six runs. Historical campaign-file hashes in earlier summaries refer to their execution-time mutable snapshots; those earlier hashes were not rewritten to pretend the campaign never advanced.

No prior execution, completed suite or preflight request was repeated. Observability limitations remain: private unreturned reasoning, arbitrary-object state and all transient Python dependencies are not fully captured. Absence of natural recursive/batch calls is not a failed capture test; prior offline equivalence/isolation evidence is retained without rerunning it.

## Authorization boundary

No execution/accounting blocker remains from Round 2, and the censoring rule does not mandate protocol review. **Execution nevertheless stops here because the user explicitly excluded Round 3.** The nominal next run is S3-R03 and requires separate authorization. No Round 3 command was issued. No source modification, commit or push occurred.
