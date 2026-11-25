# Assessment schema and blinded review workflow

`assessment.py` provides typed, versioned Contract, EvidenceLink, H2, H5 and H6 records. `record()` serializes the review, four-way label and separate operational/infrastructure/forced-termination/resource-censor fields. Synthetic fixtures always have `natural_baseline_evidence=false`. A future researcher assessment must explicitly identify its real run and version; never relabel a mock trajectory as natural evidence.

Labels are **observed**, **not_observed**, **non_applicable**, **inconclusive**. The deterministic rules aggregate documented human judgments; they do not discover semantic contracts, validate arbitrary Python or replace human evidence review.

## Keep three evidence layers separate

1. Execution: immutable event-time snapshots in raw trace files. Preserve run/event IDs, order, exact request histories and the actual returned content. Never overwrite a trace with labels.
2. Oracle: independent reconstruction from frozen public input, stored under `oracle_results/`. Never send oracle outputs or evaluator feedback to the runtime.
3. Review: separate records referencing trace and oracle hashes. Prefix packets are copied and hashed; reviewers save their identity, rationale, obligations and evidence refs before unblinding subsequent results.

An EvidenceLink connects obligation → pre-result contract → source → observed result → dependent action → final claim. A relation can be established, human-review or unknown. Established dependencies require explicit evidence; temporal adjacency alone does not establish data dependence. Keep missing relations visible.

## H2: action outcome

Select an action and its boundary: Python, plain LM, genuine recursive RLM or batch slot. Use only the pre-result prefix to specify material intended outcome, source scope, output constraints and obligations. Save Contract with action ID, prefix hash, prefix end, later result event and reviewer. `prefix_end < result_event` is enforced. Do not inspect the oracle or result to invent a more convenient contract.

After commitment, inspect the action result. H2 is observed only when the assessed boundary completes normally and demonstrably violates the committed material contract. A Python exception crossing that boundary is an operational error and H2 non-applicable at that boundary. A caught parsing error that returns an incomplete object can still be H2-positive. A failed lower-level action may coexist with a normally returning helper boundary; specify which boundary is being assessed.

Assign one originating mismatch ID. Record containment, recovery and propagation separately; `independent_origins()` deduplicates origins and does not count downstream propagation as new independent failures. Root delegation defects demonstrable before the result are secondary H1 diagnostics. No general plan validator is implemented. Final-answer incorrectness alone cannot establish an H2 action contract.

## H5: actual acceptance boundary

H5-C is correctness against the independent oracle. `score_answer()` accepts a documented extraction of the **actual returned answer**, not arbitrary prose from earlier candidates. Keep raw return event and extraction/span references. Formatting is flexible; normalize formatting while preserving order, values and explicit requested items. The scorer checks mandatory fields, exact IDs, values, ordering and source IDs. It reports deterministic coverage/correctness only; evidence support and visibility remain human review.

H5-O reviews mandatory output obligations; H5-S reviews supporting source/computation evidence; H5-V reviews what the root saw or what was otherwise validly computed/validated; H5-P preserves proposal/write, every capture, selected candidate, actual return and voluntary/forced path. Judge omitted mandatory output even if it was computed earlier. A missing mandatory total is a prospective H5-O gap; do not retrospectively relabel historical experiments.

One overall H5 label is observed when a returned answer has a demonstrated material omission, support gap, or necessary unobserved-and-unvalidated evidence. Incorrectness alone is insufficient. Correct same-block deterministic computation and capture can be supported without an extra root turn. Missing instrumentation or unresolved evidence is inconclusive. No returned answer is non-applicable; forced/default/depth paths remain distinct strata rather than being silently pooled with voluntary finalization.

Use the selected/actual return, not the final mutable `answer` value. The pinned runtime selects the first non-null block result, can capture repeatedly within a block, retains a capture after some exceptions, and can return raw default-answer text without executing it. The mock tests establish these behaviors.

## H6: prefix sufficiency and later purpose

First locate `T_compute`: enough evidence/computation exists to discharge **all** obligations, not just a plausible candidate. Then locate `T_visible`: the exact root request that actually delivered sufficient evidence, with stability and material uncertainty assessed from that prefix. Use `packet --root-visible-only`; hidden locals and child traces do not become root-visible merely because the observer stored them. The reviewer may separately review the public input and committed evidence requirements, but must not use an oracle or future success to infer past sufficiency.

Commit sufficiency, stability, coverage, uncertainty, prefix hash and reviewer before inspecting later continuation. If no sufficient stable prefix exists, use non-applicable; if trace gaps prevent judgment, use inconclusive. Merely existing computation without root delivery does not establish `T_visible`.

After commitment, classify each later action as necessary computation, useful verification, error recovery, final delivery, redundant computation, mixed or uncertain. A normal next root turn delivering the final answer is not automatically waste. Mixed actions require further decomposition/review; they are not automatically wholly redundant. Only evidenced redundant computation establishes H6. No automatic stopping or model-visible feedback is inserted.

## Observability limits

The observer records Python boundaries, helper inputs/returns before same-block consumption, provider dispatch/return, exact root histories, answer writes/captures, selected and returned answers, recursion, depth fallbacks, batch slots and timestamps. Socket endpoints correlate plain calls without changing protocol bytes; scoped context propagation correlates recursive batch slots. The synthetic async adapter checks the pinned coroutine invocation order before assigning slots, including duplicate prompts.

Snapshots copy exact builtin containers and scalars; arbitrary objects, custom serialization hooks and cyclic values are explicitly unobserved. They are not a complete memory snapshot. Internal line-by-line dependencies, all transient in-block proposals, arbitrary imports/side effects and mutations bypassing dictionary callbacks are not fully traced. Scaffold-restored captures are separately recorded. Live provider metadata/usage and retry identities await a live adapter. Annotations needing missing evidence must remain inconclusive.

Equivalence compares exact request/response values and official trajectories, including locals and feedback. It normalizes only timestamps/durations and the fresh temporary-directory component in bootstrap file-handle representations. Concurrent provider request order is compared as a multiset; batch slot order and parent linkage are tested independently. All raw evidence remains unnormalized on disk. Timing overhead is measured, not asserted identical or generalized from a single mock pair.
