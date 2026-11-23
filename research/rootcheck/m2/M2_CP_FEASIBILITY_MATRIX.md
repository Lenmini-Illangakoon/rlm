# M2 checkpoint feasibility matrix

All source references below refer to pinned commit `e11f1a8f8ee4490686e16dd6463233abe08a07eb`, not an assumed future adapter. Line references identify entry points; nearby branches matter. Original probe IDs, outcomes and assertion locations are in [the inventory](M2_PROBE_INVENTORY.md). Existing test commands and retention limits are in [the test record](test-results/original-offline-runs.txt).

## Historical crosswalk

Historical terms are preserved from Phase 3 §9.2, “Candidate checkpoints — B0-minimal mapping; official mapping pending M2”, in `rlm-minimal/experiments/phase3_failure_analysis/PHASE3_CONSOLIDATED_ANALYSIS_DRAFT.md`. That file is not relabelled or modified.

| Historical Phase 3 checkpoint | Original meaning | Relationship to current M2 definitions |
| --- | --- | --- |
| CP0 | Before any code from a root response | Pre-execution response gate; no identical M2 task-entry checkpoint. Retained as an extra protocol/H6 candidate. |
| CP1 | After each REPL block | Post-block observation supports M2 CP2/CP3/CP4; too late to ensure pre-consumption H2 interception. |
| CP2 | Before/after a recursive call | Split into M2 CP1 dispatch and M2 CP2 result return; M2 also distinguishes plain calls and depth fallbacks. |
| CP3 | Between iterations / before request delivery | M2 CP3 feedback delivery and recovery. |
| CP4 | Before accepting final output | M2 CP4 final-answer acceptance, including official runtime's separate return paths. |

M2 CP0 task entry and contract binding is an additional explicit scope; it must not be read back into historical CP0.

## Consolidated verdicts

| M2 checkpoint | Baseline state and source boundary | Evidence | Confirmed capability / demonstrated intervention | Missing adapter or controller behavior | Verdict |
| --- | --- | --- | --- | --- | --- |
| CP0 — Task entry and contract binding | `RLM.completion` line 385, `_setup_prompt` 359; `LocalREPL.load_context/add_context` 415/419. Task payload, root instruction and environment context are available. | Context/depth tests in original 155 and rerun 32 verify instruction/context preservation and child propagation. No semantic contract validator was tested. | Observe/bind a reviewed task and source identity at host entry; JSON context handling is not a provenance ledger. | New contract registry, source version/digest, task obligations and run ID. Validate inputs and preserve their association across children. | **Feasible with adapter; semantic contract binding absent.** |
| CP1 — Dispatch | `LocalREPL._llm_query/_llm_query_batched` 265/291; `_rlm_query/_rlm_query_batched` 323/349; `RLM._subcall` 812. Evaluated prompts, recursive context, optional model, depth and callback/fallback mode are available. | Dispatch/context/depth and batching tests; I1–I8, D6–D7. | Observe or wrap single/batch dispatch; recursive children finish before their values are consumed; batch returned values retain input-slot ordering. | Assign run/parent/child/call/batch/slot IDs before attempts; record failures and fallback kind; propagate contracts and dependencies; implement explicit denial policy. | **Feasible bounded integration; identities/denial semantics require work.** |
| CP2 — Result return and outcome validation | Same helpers, before returning strings into Python; `_subcall` leaf branch 842 and child completion 952. Post-block `execute_code` 563 is later. | I1–I11 (I10a/I10b variants), D6–D7; error/failed-pending-call upstream tests. | Result interception/withholding is possible; outer wrapper interrupts an uncaught block. Existing catches turn rejection into consumable strings; generated catches and later blocks bypass interruption. | Typed execution and validation status, immutable result snapshot, pre-consumption contract validation, enforced protocol, whole-turn abort, dependency invalidation. No rollback implementation exists. | **Conditional for restricted structured tasks; unrestricted Python enforcement is not established.** |
| CP3 — Feedback delivery and recovery | `completion` 514 appends assistant response and `format_iteration` output; next turn adds its prompt; `format_iteration` 25 caps each block at 20,000 characters. Available raw results exceed delivered text. | Formatting tests and D1 verify the exact next request; F1/I11 show when ordinary next-turn feedback does not occur. | Raw error creation and actual request inclusion can be distinguished. D1's scripted mock takes a repair branch after checking the request. | Separate uncropped validation feedback/evidence IDs, request-delivery record, bounded revision policy. Rejected finals must bypass return and reach an explicit next request; no controller implementation or real-model recovery is established. | **Delivery observable; reliable rejection/recovery requires controller changes.** |
| CP4 — Final-answer acceptance | `_AnswerDict.__setitem__` 47/`_capture_answer` 251; `execute_code` 594; `completion` limits 469 and first-candidate scan 475, return 493; `_default_answer` 767/`_fallback_answer` 792. | F1–F9, D5/D8 and answer/depth/limit upstream tests. Repeated-readiness remains pending. | Capture and final selection can be observed/gated at host boundaries. A captured candidate can coexist with error or state mutation. Limit and fallback precedence are known in tested paths. | Central gate over actual selected immutable candidate, evidence and unresolved errors on every supported return route. Explicit rejection, exhaustion and uncertified outcomes; do not silently override limits. | **Conditional and essential for H5; no existing evidence-sufficiency gate.** |

Source links: [controller](../../../rlm/core/rlm.py), [LocalREPL](../../../rlm/environments/local_repl.py), [formatter](../../../rlm/utils/parsing.py), [handler](../../../rlm/core/lm_handler.py), [types](../../../rlm/core/types.py), [logger](../../../rlm/logger/rlm_logger.py). Immutable [upstream controller reference](https://github.com/alexzhang13/rlm/blob/e11f1a8f8ee4490686e16dd6463233abe08a07eb/rlm/core/rlm.py#L385).

## CP2 timing and intervention strength

Single recursive order is dispatch → child execution → returned child candidate available → helper string returned → generated Python consumption → possible same-block readiness. D6/D7 exercise actual child RLMs using mocked clients; D7 proves each child's partial order, not one deterministic cross-thread trace. Batched helper results are consumed after the batch completes. Plain calls return LM responses without a child REPL. A missing recursive callback falls back through plain LM helpers; `_subcall` at maximum depth has its own plain-completion branch, before non-leaf remaining-budget/timeout setup.

I1–I8 inject an exception at the mocked producer/callback and exercise each catch path; they are not eight implementations of a validator after a real model result. I10a/I10b place an explicit wrapper after an actual helper return and before return to generated code. D6/D7 establish real recursive timing without adding validation. Their combined evidence supports an interception location, not an implemented end-to-end H2 system.

| Capability | M2 evidence and limit |
| --- | --- |
| Detect invalid outcome | Deterministic rejection stubs exist. General semantic H2 detection is unverified. |
| Withhold raw payload | Demonstrated. A replacement error string can still be consumed and finalized. |
| Interrupt current block | Demonstrated only for an uncaught outer-wrapper exception. Python can catch it. |
| Stop later blocks in the same response | Not provided by that exception; I11 executes the second block and returns SECOND. |
| Prevent dependent contamination / roll back | Not implemented. Shared mutable objects can change even on failed execution (D3). |
| Deliver feedback to root | Normal nonfinal feedback is observed in D1; rejection requires a controller path that actually makes another request. |
| Achieve bounded successful recovery | Scripted mock behavior only. New controller policy and model-based evaluation are required. |

The structured-task MVP must enforce its restricted action protocol in host code. Prompt instructions alone cannot guarantee these properties for arbitrary Python.

## CP4 route and precedence record

F1 captures/returns A despite a subsequent ValueError. F2 captures A then changes dictionary content to B without another ready assignment, so the actual return remains A. F3 executes two blocks, captures A and B, then selects A; prior locals can already show B. Do not infer candidate identity from the latest answer dictionary.

Error/token/cost checks run after the whole turn but before candidate selection and logging. F5–F7 capture A yet raise, returning no final answer. Timeout is checked before a turn: F8 returns A after a synthetic overrun, while F9 raises at the next turn when no final was produced. These checks are not hard interruption of running Python.

At iteration exhaustion, `_default_answer()` makes an extra LM request and returns its raw string, without executing returned code (F4). The recorded end time precedes that call (D5); ordinary post-turn checks are not repeated around that extra request. At entry depth limit, `_fallback_answer()` bypasses the iterative environment. Recursive leaf fallback is another plain-call path. A final gate must cover or explicitly exclude each path, including exception/uncertified termination; those exclusions must be enforced.

Same-block repeated readiness A/ready, B/ready is **not an executed case**. The source-derived expected final candidate is B; a capture-event assertion needs added instrumentation. See the pending protocol in the inventory.

## Feedback, evidence and accounting requirements

Feedback created in a REPL result, feedback actually included in the next request, and feedback acted on are three separate facts. Each code block is formatted and truncated independently; a large stdout prefix can hide stderr while a second block's feedback is still delivered (D1). Same-turn acceptance normally prevents that next request. A rejected final requires controller changes to suppress return, retain evidence, reset candidate state under a defined policy, stop remaining work where required, append compact explicit feedback and make a bounded next request.

Failed helper calls can be absent from `rlm_calls`; error-text completions may instead appear as ordinary successful records (I1–I9). Recursive batches order successful metadata by slot but omit failed entries, so list position is insufficient identity. Add a record for every attempted slot and separately distinguish rejected proposals from attempted external calls.

`REPLResult.locals` is a shallow copy; in-place changes affect earlier results, including before errors. Rebinding and failed new assignments behave differently (D3). `RLMIteration.to_dict()`/in-memory logger entries can retain the live prompt list; serializing at one moment does not make future in-memory entries immutable (D2). D2 tests an in-memory JSON serialization snapshot, not disk logger durability.

D4 observes child cost 0.03 being overwritten by parent-handler cost 0.01 at a budget check: returned root totals 0.01/10 input tokens omit distinct child totals of 0.03/30. D8 returns normally with synthetic distinct total 0.04 above a configured 0.035 budget. Child parameter propagation is not a shared global ledger. D9 observes batch slot usage 40/40 with aggregate 55, and duration estimates 5/5 for fixture durations 2/8. Shared last-usage and averaged wall time cannot certify per-slot accounting. Avoid summing nested totals or parallel durations without ownership rules.

Minimum proposed immutable evidence fields:

- Run, iteration, block, proposal, attempted call, batch and input-slot IDs; parent/child identity, depth, call kind and fallback kind.
- Contract/task version; source identity/version/digest; evaluated instruction/context references and selected model.
- Raw result snapshot/reference/digest; typed execution status and error; separate `PASS/FAIL/UNCERTAIN` validation verdict, rule/version, supporting evidence and uncertainty.
- Dependency IDs/state versions, invalidation status and evidence delivery to consumers.
- Candidate ID, immutable content/digest, capture and selection event order, supporting evidence, validation and finalization/termination status.
- Feedback identity/content, request ID, inclusion/truncation status and delivery event; acted-upon status only where independently observed.
- Per-attempt start/end and monotonic duration, provider usage where available, model/token/cost ownership and aggregate-budget policy.

Controller actions such as `ACCEPT`, `REQUEST_REVISION` and `RETURN_UNCERTIFIED` are separate from validation verdicts. These fields are proposed RootCheck functionality, not a description of baseline metadata.

## H2, H5 and H6 locations

H2: CP0 binds subgoal requirements; CP1 associates contracts and source inputs; CP2 is the primary result-validation/interception point; post-block state supports evidence/dependency updates but cannot undo consumption.

H5: CP0 binds final obligations; CP2 gathers validated supporting results; CP3 can expose missing evidence; CP4 validates the actual selected final candidate on every supported route. A pre-execution response gate can prevent extra work, but it is not a substitute for validating actual execution evidence.

H6: historical CP0 before code, M2 CP1 before dispatch and M2 CP3 before the next root request remain candidate observation/advice points. No redundancy judgment, safe-stop intervention or utility inference is established. H6 observation belongs in the next official-baseline study; H6 intervention remains deferred.
