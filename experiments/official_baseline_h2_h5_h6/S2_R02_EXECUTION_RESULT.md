# S2-R02 execution result

**Completed and correct.** The actual answer matches the independent S2-v2 oracle: SH-10106 (6,883; R/W/Q/H-106), SH-10068 (6,846; R/W/Q/H-068), SH-10097 (6,809; R/W/Q/H-097), in that order; total **20,538**. All twelve source IDs were individually extracted and checked. Formatting was parsed without correcting or sorting the returned values.

| Measurement | Result |
|---|---|
| Run | `broker-0c0113ea621747e2ace2fa3de8d4bbcb` |
| Runtime | Pinned `rlm.core.rlm.RLM` in AppContainer; RootCheck false |
| Official pin | `e11f1a8f8ee4490686e16dd6463233abe08a07eb` |
| Provider / resolved endpoint | OpenAI / `openai/gpt-5-2025-08-07` |
| Root iterations / provider calls | 5 / 5 |
| Delegation / generated Python blocks | None / 5 (plus 2 setup blocks) |
| Official / AppContainer job seconds | 75.125 / 77.500 |
| Prompt / completion / total tokens | 20,436 / 6,931 / 27,367 |
| Reasoning included in completion / cached input | 3,968 / 14,080 |
| Provider-reported charge | **$0.07901500** |
| Conservative run ledger debit | **$0.09485500** |
| Campaign exposure at completion | **$0.88280040** |

Conservative accounting retains uncached input pricing; its $0.01584000 difference from reported cost is budget protection, not another charge. Native reasoning tokens are charged once. All five tickets reconciled, all routing/price/usage/budget checks passed, and no new unknown reservation or telemetry conflict occurred. Carried preflight exposure $0.44882910 and its unresolved $0.4484480 reservation remain unchanged. All $2/run, $20/campaign and other frozen limits were respected.

The root probed the context, parsed the four current sections, joined all 160 IDs with no missing notes, filtered 100 eligible shipments, ranked them, printed the top three with all source IDs and total, then verified and submitted the answer. No Python stderr, output-cap finish, HTTP failure, run-level censoring, forced termination or cleanup failure occurred. The initial prose suggested a sub-LLM extraction, but actual execution used Python only; plans are not counted as calls.

## Preserved evidence

- [Structured summary, exact extraction and per-call metrics](results/S2-R02-summary.json).
- [Full broker record: exact prompts and raw provider responses](results/broker/broker-0c0113ea621747e2ace2fa3de8d4bbcb.json).
- [Chronological raw trace, 39 events](results/broker/broker-0c0113ea621747e2ace2fa3de8d4bbcb.events.jsonl).
- [Worker response and official trajectory](results/broker/broker-0c0113ea621747e2ace2fa3de8d4bbcb.worker-response.json).
- [Finalized provider journal](results/broker/broker-0c0113ea621747e2ace2fa3de8d4bbcb.journal.json).
- [Separate preliminary H2/H5/H6 observations](evaluators/S2-R02-preliminary-observations.md).

Post-run evidence checks verified the 90 protected hashes and frozen implementation/policy, actual imported 35-file runtime identity, exact prompt/response correspondence, raw event ordering and result pairs, captured/selected/actual answer equality, archived worker response, finalized journal and independent oracle agreement. All profile/scratch/payload cleanup passed. No prior execution, preflight probe or completed suite was repeated, and no experimental configuration or official source changed.

This is the first authorized Round 2 run. The existing progression gate permits S3-R02 next under the user's Round 2 authorization; no retries or replacement were made.
