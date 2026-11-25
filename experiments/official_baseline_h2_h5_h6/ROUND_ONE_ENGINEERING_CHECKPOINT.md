# Round 1 engineering checkpoint

**PASS with documented limitations. Round 2 is not authorized or started.** This checkpoint reviews saved evidence from S1-R01, S2-R01 and S3-R01; it adds no provider requests, model probes, run replays or test-suite executions. Frozen scenarios, queries, configuration, official source and all earlier observations remain unchanged.

## Completed executions

| Run | Outcome / correctness | Root iterations | Calls (root / plain) | Official seconds | Reported provider cost | Conservative debit |
|---|---|---:|---|---:|---:|---:|
| S1-R01 | Completed / correct | 4 | 4 / 0 | 76.404 | $0.08246875 | $0.09902875 |
| S2-R01 | Completed / correct | 8 | 8 / 2 | 444.481 | $0.17427805 | $0.20135005 |
| S3-R01 | Completed / correct | 3 | 3 / 0 | 38.112 | $0.03427350 | $0.03873750 |
| Total | 3 completed | 15 | 15 / 2 | — | **$0.29102030** | **$0.33911630** |

Across 17 calls: 89,758 prompt tokens and 83,502 completion tokens, totaling 173,260. Native completion usage already includes reasoning; nested trajectory summaries are not billed again. Conservative accounting retains uncached input pricing, while provider-reported charges include cache discounts.

Campaign exposure is **$0.78794540**, comprising $0.33911630 conservative pilot debits plus the exact once-imported $0.44882910 preflight exposure. The latter retains **$0.4484480 unresolved reservation** and $0.00038110 known preflight charges. Known provider-reported inference charges including preflight are $0.29140140; these are response-derived figures, not an additional account-billing lookup. Remaining protected headroom against $20 is **$19.21205460**. No new unresolved pilot request exists and the old reservation was not released.

## Verified engineering gates

The [machine-readable checkpoint](results/round-one-engineering-checkpoint.json) records the checks, per-run hashes and metrics.

- **Execution integrity:** expected three runs each retained once; no active run or campaign lock; actual imported class `rlm.core.rlm.RLM` and all 35 official runtime hashes match in every AppContainer run. All 90 protected files, frozen implementation hashes, campaign identity and dataset/query/oracle checksums remain unchanged. RootCheck is false in every runtime identity. Cleanup succeeded for every run.
- **Evidence completeness:** all 125 JSONL events are contiguous with unique IDs and match their parsed records. Python start/result pairs are present. Every provider request is correlated to an exact dispatched prompt and returned content. Generation/request IDs are unique across runs; all journals are finalized and worker-response archives match their records. Iterations, plain calls, stdout/stderr, root-visible histories, finalization and actual returns are preserved. S1/S2 immutable evidence hashes still match their summaries; their historic mutable campaign snapshots remain referenced at their original hashes, with prior artifact manifests preserved.
- **Provider controls and usage:** all 17 saved responses were rechecked offline against the frozen OpenAI-only/no-fallback route, approved dated endpoint policy, exact reviewed price, native usage consistency, input/completion bounds and recorded verification. There are no new telemetry conflicts. All pilot tickets reconcile once with zero outstanding reservation; no adapter retries or duplicate generation/request IDs appear.
- **Cost and resource limits:** every run is below $2, 24 attempts and 900 seconds; all request input bounds are at most 64,000 and completion caps remain 32,768. Cumulative exposure remains below $20. All actual returns pass their independent scenario oracle.
- **Censoring:** **0 of 3 runs are resource-censored**, below the approved cumulative threshold of two at a round boundary. S2's second nano subcall has `finish_reason=length` at its per-request output cap; the run recovered and completed. This action-level constraint remains documented separately and is not silently converted into a run-level censor or unconstrained reasoning failure.

## Limits and research interpretation

No genuine recursive child or batch occurred naturally in Round 1. Their absence is not an evidence-capture failure; the previously passing offline coverage remains retained and was not repeated. Private unreturned model reasoning, arbitrary-object memory and every transient Python dependency are outside full observation. Formal H2/H6 blinded commitments and human H5 confirmation remain pending and do not alter the engineering checkpoint result.

S2 has a confirmed prose-for-JSON mismatch candidate, a generated SyntaxError, an output-capped extraction and successful deterministic recovery. H5 preliminarily shows supported complete acceptance in all three runs. H6 notes distinguish useful verification/final delivery from uncertain extra planning; no formal positive is manufactured. See the separate [S1](evaluators/S1-R01-preliminary-observations.md), [S2](evaluators/S2-R01-preliminary-observations.md) and [S3](evaluators/S3-R01-preliminary-observations.md) notes. Correct answers alone do not establish hypothesis absence.

## Continuation gate

The existing progression gate still returns `stop_for_round_one_engineering_review` without an explicit continuation flag. With this completed engineering review acknowledged, the next permitted ID is **S2-R02**, followed by S3-R02 and S1-R02. No persisted configuration or campaign approval switch was changed.

Separate authorization for **S2-R02 only**, including acknowledgement of this checkpoint and retaining the carried exposure/limits, is required before using:

```powershell
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/live_baseline.py --authorize-run S2-R02 --engineering-checkpoint-approved
```

That command has not been executed. Keep the existing nine-run order and cumulative two-censored-runs stopping rule; never replace runs or increase budgets automatically. No source edits, commits or pushes were made.
