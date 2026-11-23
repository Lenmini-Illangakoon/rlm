# M2 probe inventory

**30 original executed cases: PASS. Four original tool exits: 0. Recovered source: 4/4. Newly extracted saved-script reproduction: PENDING for all 30.** This inventory adds no new execution evidence.

Original identifiers and full PASS payloads are preserved without renaming in [original-probe-runs.json](test-results/original-probe-runs.json). Archival IDs I10a and I10b distinguish original `I10_wrapper_uncaught` and `I10_wrapper_caught`; both originally used the I10 stem. There are 30 cases, not 29 or 31.

Each table's behavior column states the expected assertions and the originally observed outcome. Exact assertions, harness setup and generated input strings are the unmodified statements at the cited extracted-script lines. The shared context gives official functions, inputs and mocked components; it applies to each row in that group.

| Evidence run | Original output chunk | Original exit | Cases | Recovered original code | Extracted script reproduction |
| --- | --- | --- | --- | --- | --- |
| cp4 | bba6c6 | 0 | 9 | Command body and Python assertions available | PENDING |
| cp2 | 5832be | 0 | 12 | Command body and Python assertions available | PENDING |
| delivery_identity_accounting | 67f722 | 0 | 7 | Command body and Python assertions available | PENDING |
| accounting_extra | a7fcf1 | 0 | 2 | Command body and Python assertions available | PENDING |

## Finalization (F1–F9)

CP4; RLM.completion/_completion_turn/_default_answer/_check_iteration_limits/_check_timeout and LocalREPL.execute_code/_AnswerDict. Shared harness uses MockLM scripted responses, captures REPLResult objects and root request copies, patches core.get_client/get_environment, and uses an in-memory logger. Root max_iterations=1 unless noted. Exact inputs/assertions are retained in cp4.py.

Script: [probes/cp4.py](probes/cp4.py). Original command/output run: `cp4`.

| Archival ID | Research question | Expected / originally observed | Exact assertion lines |
| --- | --- | --- | --- |
| F1 | Can readiness survive a later execution error? | A captured and returned; ValueError after-ready remains in stderr; exactly one request, no next-turn feedback. | 52–54 |
| F2 | Can mutable dictionary content differ from the candidate? | A captured/returned; dictionary content B after mutation without ready reassignment. | 58–59 |
| F3 | Which of two separately captured block candidates is selected? | Blocks produce [A,B], root returns A; first result's answer locals now contain B. | 63–64 |
| F4 | What returns at iteration exhaustion? | Normal candidate absent; second raw response is the fenced raise RuntimeError('DEFAULT_CODE_MUST_NOT_RUN') text; returned verbatim, not executed; default log has zero blocks. | 69–71 |
| F5 | Does max_errors beat a captured final? | max_errors=1; captured A plus error; ErrorThresholdExceededError, no returned final, no logged iteration. | 75–76 |
| F6 | Does token limit beat a captured final? | max_tokens=1, mock usage 20 tokens; captured A; TokenLimitExceededError, no returned final/log. | 80–81 |
| F7 | Does cost limit beat a captured final? | CostLM reports 0.02 with max_budget=0.01; captured A; BudgetExceededError and no final return. | 106 |
| F8 | Is timeout checked again before final return? | Fake clock advances to 2 with timeout 1; A returned normally, execution_time 2. | 117 |
| F9 | When does a nonfinal timeout overrun stop? | Fake time 2, timeout 1, max_iterations=2; no candidate, TimeoutExceededError before next turn, no final return. | 131 |

## Pre-return rejection and interruption (I1–I11, with two I10 variants)

CP1/CP2/CP4. I1–I8 use LMHandler, LocalREPL helpers and, for core-leaf mode, RLM._subcall at max_depth=1. MockLM producer/callback raises ProbeReject after recording a synthetic candidate. Batched input contains bad then good; good returns OK. The shared assertions test error-string substitution, ordering, finalization and recorded-call counts. I10 adds an outer helper wrapper; I11 exercises RLM's multi-block controller.

Script: [probes/cp2.py](probes/cp2.py). Original command/output run: `cp2`.

| Archival ID | Research question | Expected / originally observed | Exact assertion lines |
| --- | --- | --- | --- |
| I1 | Plain single helper rejects before return? | Original payload withheld, Error: REJECTED consumed; downstream and ready run; zero recorded calls. | 47–51 |
| I2 | Plain batched helper rejects one slot? | Bad slot becomes Error: llm() call failed - REJECTED; good slot OK; downstream/final run; one recorded call. | 47–53 |
| I3 | Recursive callback single rejects? | Error: RLM query failed - REJECTED consumed; downstream/final run; zero recorded calls. | 47–51 |
| I4 | Recursive callback batch rejects one slot? | Same recursive error string plus OK; downstream/final run; one recorded call. | 47–53 |
| I5 | Recursive helper without callback falls back? | Plain single error substitution; downstream/final run; zero recorded calls. | 47–51 |
| I6 | Recursive batch without callback falls back? | Plain batch error substitution plus OK; downstream/final run; one recorded call. | 47–53 |
| I7 | Core recursive leaf fallback rejects? | Error: LM query failed at max depth - REJECTED returned normally; downstream/final run; one error-text completion recorded. | 47–51 |
| I8 | Core recursive leaf batch rejects one slot? | Same leaf error string plus OK; downstream/final run; two completions recorded. | 47–53 |
| I9 | Is rejection text typed as failure? | REJECTED: explanation can be final; one completion whose error is None. | 62–63 |
| I10a | Can an outer uncaught wrapper stop consumption? | Original helper completion recorded; raw payload withheld, value absent, downstream absent, no final; stderr ProbeReject. | 79,83 |
| I10b | Can generated Python catch that wrapper exception? | Raw payload still withheld/value absent; caught and downstream events occur; AFTER final. | 79,81 |
| I11 | Does one failed block stop the rest of the turn? | First block has ProbeReject and no candidate; second produces SECOND; root returns SECOND. | 113–114 |

## Feedback, state and recursive accounting (D1–D7)

D1: completion/format_iteration/format_execution_result with scripted MockLM and environment capture. D2: RLMLogger.log and RLMIteration.to_dict with a live prompt list. D3: LocalREPL execution with a deep-copied control. D4: actual child RLM and MeterLM usage, wrapping the parent's limit check. D5: fake perf_counter/response delays. D6/D7: actual single/batch child RLM execution, mocked factories and note/capture callbacks; no remote model.

Script: [probes/delivery_identity_accounting.py](probes/delivery_identity_accounting.py). Original command/output run: `delivery_identity_accounting`.

| Archival ID | Research question | Expected / originally observed | Exact assertion lines |
| --- | --- | --- | --- |
| D1 | What exactly reaches the next root request? | Two blocks; 20,005 x characters hide raw HIDDEN_STDERR at 20,000-character per-block cap; SECOND survives; exact assistant/user/Turn 2 request asserted; SCRIPTED_REPAIR is a programmed response. | 33–36,52–53 |
| D2 | Does in-memory history remain immutable? | Logger prompt is the original list; append changes old entry; previously serialized JSON string is stable. | 63–65 |
| D3 | Are locals snapshots and failed execution atomic? | Old list becomes [1,2,3], deep copy stays [1]; failed new_binding absent; later rebinding [99] does not replace old reference. | 73,75–76,78 |
| D4 | Does parent usage include recursive child usage? | Root/child distinct clients each called once: child cost before check .03, parent after .01; root returns .01 and 10 input tokens vs distinct total .04/40; child metadata retains .03. | 105–108 |
| D5 | Does reported execution_time include the default call? | Fake first turn 2 and default 7; RAW_FINAL returned; outer 9, reported 2, omitted 7. | 121 |
| D6 | Does actual child completion precede consumption and readiness? | Single dispatch:A < child_body:A < available:A < consume:A < ready:A; final A. | 153–155 |
| D7 | Does each batched child precede ordered result consumption? | Each A/B dispatch < body < availability < consume:A|B < ready:A|B; final A|B. Cross-child event interleaving is not fixed. | 153–155 |

## Additional resource-accounting cases (D8–D9)

CP1/CP2/CP4 accounting. D8 uses an actual mocked child RLM and separate Meter clients with configured parent budget .035. D9 uses LMHandler/send_lm_request_batched, a BatchMeter and fake shared perf_counter; per-call input/duration fixtures are (15,2) and (40,8).

Script: [probes/accounting_extra.py](probes/accounting_extra.py). Original command/output run: `accounting_extra`.

| Archival ID | Research question | Expected / originally observed | Exact assertion lines |
| --- | --- | --- | --- |
| D8 | Can distinct recursive costs exceed configured budget while finalizing? | Synthetic aggregate .04 > .035; root reports .01 and returns A normally. | 28,30 |
| D9 | Are batch per-slot usage and latency exact? | Ordered responses OK:first/OK:second; metadata input tokens [40,40] vs aggregate 55; durations [5,5] vs fixtures [2,8]. | 55,58–59 |

## Evidence limits applicable to every original case

The recovered tool inputs and outputs support these original assertions at the pinned baseline, with mocked models. No paid calls, RootCheck implementation or natural-failure observations are implied. Original code was transcribed from accessible conversation tool inputs; byte-for-byte independent session-export verification and original execution-time hashes are unavailable. Current archive hashes attest only the newly saved artifacts.

I1–I8 reject inside a producer/callback, not after a real provider result. I10 demonstrates the outer wrapper boundary. D6/D7 demonstrate actual recursive ordering with no validation. D1's repair is scripted, not evidence that a language model understands or acts correctly on validation feedback. D2 does not test disk log durability. Accounting fixtures are synthetic, not financial/provider measurements. Batch traces can interleave differently while satisfying the original partial-order assertions. All saved-script reproduction statuses remain pending.

## Pending additional test: P-CP4-REPEATED-READY

This exact same-block case is not present in the recovered 30-case source and has not been executed:

```python
answer["content"] = "A"
answer["ready"] = True
answer["content"] = "B"
answer["ready"] = True
```

Source-derived expectation: final candidate **"B"**, because each truthy ready assignment calls the capture callback and overwrites the single captured value. This differs from F2 (no second ready assignment) and F3 (separate blocks). The baseline retains the latest captured candidate, not a list of capture events.

Proposed protocol, requiring separate approval/execution: reuse the F-series MockLM/environment harness, one scripted root response containing this one block, max_iterations=1. Assert REPLResult.final_answer == "B", returned response == "B", empty stderr, one root request, and no execution-limit exception. If asserting capture events == ["A", "B"], additionally wrap the answer dictionary's existing _on_ready callback with a spy that records each argument and delegates to the original callback (as the D6/D7 instrumentation does). Without that extra spy, the baseline's retained value cannot prove both events. Status: **PENDING — expected result from source only; no PASS/output/exit record exists.**

## Future implementation acceptance tests

These are proposed requirements, not added/executed probes: every helper/fallback and batch slot retains a typed attempted-call record; rejected outcomes cannot reach authorized consumers; a rejected action prevents later actions under the enforced protocol; dependency invalidation survives partial mutation; every final-return path passes H5; rejection feedback is actually included in a bounded next request; exhaustion returns explicitly uncertified; recursive resource totals have stable ownership. Host-protocol tests and controlled model-recovery evaluation are still needed.
