# S1-R01 execution result

S1-R01 completed normally and returned the correct complete answer: **60 selected orders, 1,361 outstanding units**. Both exact ascending membership and total match the existing researcher-only S1 oracle. Scoring used only the actual returned answer after execution; no answer correction or oracle feedback was supplied to the model.

Only S1-R01 was authorized and executed. No retries, subsequent runs, provider probes, official-source edits, commits or pushes were performed.

| Measurement | Result |
|---|---|
| Live run | `broker-eaa4d3f974474c0e807569e72ddf4432` |
| Official source pin | `e11f1a8f8ee4490686e16dd6463233abe08a07eb` |
| Runtime | Actual `rlm.core.rlm.RLM` inside Windows AppContainer; RootCheck disabled |
| Provider / resolved endpoint | OpenAI / `openai/gpt-5-2025-08-07` for all four requests |
| Root iterations / provider requests | 4 / 4 |
| Generated Python execution blocks | 4, plus 2 environment setup blocks; all captured stderr empty |
| Delegation | None: no plain sub-LLM calls, recursive child nodes, batches or GPT-5-nano requests |
| Official completion latency | 76.404 seconds |
| AppContainer job elapsed time | 79.578 seconds; excludes parent staging/cleanup |
| Usage | 23,719 prompt + 6,938 completion = 30,657 tokens |
| Reasoning / cached input detail | 3,584 reasoning tokens included in completion; 14,720 cached prompt tokens |
| Provider-reported inference charge | **$0.08246875** |
| Conservative run ledger debit | **$0.09902875** |
| Campaign exposure after run | **$0.54785785**, including carried preflight exposure $0.44882910 |
| Old unresolved reservation | **$0.4484480**, unchanged |
| New unresolved requests | None; all four pilot tickets reconciled |

The ledger conservatively uses uncached input rates, so its debit exceeds the provider-reported charge by $0.01656000. This is retained budget protection, not an additional charge. Reasoning tokens were not added again to completion-token cost. All four requests passed routing, price, usage and budget verification; none had the earlier reasoning-detail conflict. Costs come from saved provider responses, not a separate account lookup.

## Evidence and verification

- [Structured result and exact answer extraction](results/S1-R01-summary.json): correctness, timings, usage, per-request generation IDs, verification, source identity, evidence hashes and hypothesis review status.
- [Complete broker record](results/broker/broker-eaa4d3f974474c0e807569e72ddf4432.json): exact requests, raw provider responses, routing metadata, ledger and observed execution.
- [Chronological raw events](results/broker/broker-eaa4d3f974474c0e807569e72ddf4432.events.jsonl): 33 ordered events with action/node references, generated code, full REPL output, iteration decisions, root-visible request histories and actual return.
- [Worker response and official trajectory](results/broker/broker-eaa4d3f974474c0e807569e72ddf4432.worker-response.json).
- [Durable provider journal](results/broker/broker-eaa4d3f974474c0e807569e72ddf4432.journal.json).
- [Campaign accounting](results/campaigns/official-baseline-v1.json): exactly one completed baseline run; no active run.

Post-run evidence checks confirmed raw events match the parsed record, unique event IDs and contiguous sequence numbers, the actual-return event matches the worker answer, all 90 protected hashes and frozen implementation hashes remain unchanged, and all 35 official runtime hashes match the actual imported AppContainer runtime. Profile, scratch and payload cleanup completed successfully. No test suites were repeated.

The saved verification is finalized: the exact actual-return extraction matches the independent oracle's complete ascending set and total; all eight referenced evidence hashes match. The existing 243-entry artifact manifest also verified before report updates. Neither the oracle solver nor any experiment or API request was repeated for this finalization.

[Separate preliminary H2/H5/H6 notes](evaluators/S1-R01-preliminary-observations.md) link observations to exact trace events. H2 has no demonstrated material action mismatch; H5 provisionally shows supported, complete acceptance; H6 has no demonstrated redundant computation after complete root-visible delivery. H2/H6 formal labels remain inconclusive without the prescribed blinded commitments, and H5 awaits human confirmation. These retrospective notes do not replace protocol-compliant assessment or infer hypotheses from correctness alone.

The observer's historical `mock-` event-ID prefix does not indicate synthetic execution: this broker record is explicitly `synthetic_only: false` and contains the live provider generations. The constant `exception_detail` text describes an observation limitation, not an exception.

## Next step

S2-R01 is next in the unchanged nine-run sequence and requires separate explicit authorization. There is no new unresolved pilot exposure or cleanup blocker. Retain the existing carried reservation, $2/run and $20 campaign limits, the round-one checkpoint after S3-R01, and the approved resource-censoring stop rule. No further live requests are authorized by S1-R01 approval.
