# S2-R03 execution result

**Completed and correct. Campaign A execution is closed.** The actual returned answer matches the independent S2-v2 oracle: SH-10106 (6,883; R/W/Q/H-106), SH-10068 (6,846; R/W/Q/H-068), SH-10097 (6,809; R/W/Q/H-097), in order; total **20,538**. All twelve source IDs were extracted individually from the actual answer and checked. No returned values were corrected or sorted by the evaluator.

| Measurement | Result |
|---|---|
| Run | `broker-c473538e26a441fdb32395f07a6451ee` |
| Runtime | Pinned `rlm.core.rlm.RLM` inside AppContainer; RootCheck disabled |
| Official pin | `e11f1a8f8ee4490686e16dd6463233abe08a07eb` |
| Provider / resolved endpoint | OpenAI / `openai/gpt-5-2025-08-07` |
| Root iterations / provider calls | 3 / 3 |
| Plain sub-LLM / genuine recursive RLM calls | 0 / 0 |
| Generated Python / setup blocks | 3 / 2 |
| Official completion / AppContainer job seconds | 49.874188 / 52.719 |
| Prompt / completion / total tokens | 11,013 / 4,601 / 15,614 |
| Reasoning included in completion / cached input | 2,816 / 5,376 |
| Provider-reported charge | **$0.05372825** |
| Conservative run debit | **$0.05977625** |
| Campaign protected exposure after run | **$1.12034040** |

The root inspected section formats, parsed the four current sections with Python, joined all 160 shipment IDs, filtered 100 eligible shipments, ranked them using the numeric tie-break, printed complete source evidence and total, then formatted and submitted that computed result. The initial plan mentioned sub-LLM extraction; actual execution used no delegation. No Python error, capped completion, provider error, telemetry conflict or run-level resource censoring occurred. All three calls passed frozen routing, usage, price and budget checks and reconciled normally. All profile/scratch/payload cleanup passed.

Conservative accounting exceeds the actual reported charge by $0.00604800 because it retains uncached input pricing. It is not an additional charge. Native reasoning is counted once. The original $0.448448 preflight hold remains; S1-R03's separately verified reconciliation remains intact and its run status remains operational failure.

## Evidence and verification

- [Structured summary, exact actual-answer extraction, metrics, hashes and post-run checks](results/S2-R03-summary.json).
- [Full broker record: dispatched prompts and raw provider responses](results/broker/broker-c473538e26a441fdb32395f07a6451ee.json).
- [Chronological trace, 27 events](results/broker/broker-c473538e26a441fdb32395f07a6451ee.events.jsonl).
- [Official trajectory and worker response](results/broker/broker-c473538e26a441fdb32395f07a6451ee.worker-response.json).
- [Finalized provider journal](results/broker/broker-c473538e26a441fdb32395f07a6451ee.journal.json).
- [Separate preliminary hypothesis observations](evaluators/S2-R03-preliminary-observations.md).

Targeted saved-evidence checks passed: all 90 protected hashes and frozen campaign identity, 35 imported runtime hashes, exact prompt/response correspondence, trace order, worker/journal agreement, root-visible computed evidence, captured/selected/actual answer equality, independent oracle correctness, accounting bounds, cleanup and final progression `complete`. No completed suite or inference request was repeated. No further experiment is started; formal H2/H5/H6 classifications remain pending.
