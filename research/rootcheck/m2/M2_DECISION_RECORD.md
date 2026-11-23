# M2 decision record — CONDITIONAL GO

Archive date: 2026-11-23. Official baseline: `e11f1a8f8ee4490686e16dd6463233abe08a07eb`; branch: `research/m2-runtime-feasibility`; upstream: <https://github.com/alexzhang13/rlm>. Archive additions do not redefine the pinned implementation.

**Decision: preserve CONDITIONAL GO for a bounded LocalREPL RootCheck design prioritizing H2 and H5.** M2 supports proceeding to M3 architecture and a separately controlled official-runtime baseline study. Saved-script reproduction remains pending; this archive does not claim the reproducibility closure has been completed.

## What the evidence establishes

The official runtime offers task entry, helper dispatch/return, post-execution feedback and final-return boundaries. Original evidence comprises 155 unique selected upstream offline tests, 32 later overlapping rerun tests, and 30 deterministic mock-based cases. All 30 original probe PASS rows and four exit-0 tool records were recovered with their command bodies. The four saved Python scripts are new mechanical extractions of those command bodies and have not been executed as archived scripts.

The probes establish pre-return withholding and limited uncaught-exception interruption. A rejection inside existing helper/child paths commonly becomes an ordinary error string: generated Python can consume it and finalize in the same block. An outer helper wrapper can withhold the payload and interrupt an uncaught block, but Python can catch its exception. The controller can then execute later blocks. No RootCheck validator, host-enforced turn abort, rollback, dependency invalidation, or successful model-directed recovery has been implemented.

Source and probes establish finalization hazards: captured content can survive an exception, differ from mutable answer state, or compete with a later block's candidate. Some limits precede acceptance, whereas timeout is checked at the next turn. Iteration exhaustion and depth fallback use separate answer paths. H5 must validate the actual selected return value and its provenance on every supported route.

## Two research conclusions

**Technical feasibility:** suitable observation and bounded interception locations exist. Reliable H2/H5 enforcement requires explicit contracts, immutable evidence and controller changes. The checkpoint matrix records those requirements rather than treating them as baseline features.

**Natural failure occurrence:** it has not been established that H2, H5 or H6 failures occur naturally on this official baseline. Mocked boundary tests demonstrate runtime behavior under specified inputs; they do not estimate failure frequency, validate semantic judgments, or transfer historical RLM-Minimal failure results to official RLM. Historical findings remain motivation.

## Initial MVP scope proposal

Use one reviewed structured-record task family with deterministic predicates, explicit subgoal contracts, immutable source/version identities and a schema for the final answer. Shipment-readiness is a **candidate family**, pending task selection and review.

Start with `environment="local"`, `experimental_spec_ptc=False`, no streaming, no compaction and no cross-completion persistence. Use a host-enforced execution protocol: restricted helper/result use, explicit call/slot identities, one controlled block/action per turn or an equivalent host-controlled abort between actions, and no acceptance through raw fallback or error-text success. Supporting arbitrary generated Python with strong interruption, rollback or absence-of-contamination guarantees is outside this MVP.

H2 validates each declared subgoal result before authorized consumption, with `PASS/FAIL/UNCERTAIN` distinct from controller action. H5 checks the actual immutable candidate against required validated evidence, unresolved failures and dependencies before return. Rejected or exhausted answers must carry an explicit uncertified outcome rather than implicit success.

## Blockers and manageable requirements

| Category | Status and consequence |
| --- | --- |
| Arbitrary Python intervention guarantees | Blocker for unrestricted support. Catchable exceptions, later blocks and partial mutation prevent a defensible whole-turn/rollback claim. Restrict and enforce the execution protocol. |
| Complete final acceptance | Release blocker until all normal/default/depth/limit routes are covered and tested; raw fallback cannot bypass H5. |
| Evidence identity and state integrity | Required M3 work: stable call/batch/slot/candidate IDs, error-attempt records, immutable snapshots and dependency invalidation. Baseline metadata is incomplete. |
| Feedback and recovery | Required M3 controller work: suppress acceptance on rejection, issue compact explicit feedback on a bounded next request, record delivery, and return an uncertified outcome on exhausted recovery. Successful model recovery is unverified. |
| Resource enforcement | Required bounded ledger and policy. Recursive totals, shared-client batch metrics and default-answer timing are insufficient for strict global guarantees. |
| Reproducibility | Saved-script execution and verification remain a separate pending step. Repeated-readiness is a pending proposed test. |
| Natural failures and effectiveness | Separate experimental evidence required before claims about official-runtime failures or RootCheck benefit. |

## H6 preserved for the next study

Candidate observation locations are historical CP0 before generated code, M2 CP1 before call dispatch, and M2 CP3 before the next root request. They could compare proposed work/inputs with prior evidence or advise continuation/finalization. Evidence computed in Python is not automatically delivered to the root, and repetition alone does not prove unnecessary work.

H6 has equal observational importance alongside H2/H5 in the forthcoming official-runtime baseline failure-characterization study. H6 intervention implementation remains deferred beyond the December H2/H5 MVP. No redundancy detector, evidence-aware stopping policy or safe termination intervention has been verified.

## Conditions for an upgrade

Verify saved-script reproduction; execute the separately proposed repeated-readiness test with explicit instrumentation; select and review one task family; implement and test the enforced protocol, rejection/feedback path, immutable evidence ledger and complete acceptance gate. Controlled official-baseline observations must establish the studied failure mechanisms before effectiveness claims. These are distinct from the technical feasibility decision.

Historical research records, runtime code, prompts, dependencies and existing tests are unchanged. No experiment, reproduction run, paid model call, branch operation, commit or push was performed to create this archive. See [reproducibility](M2_REPRODUCIBILITY.md), [case inventory](M2_PROBE_INVENTORY.md) and [checkpoint matrix](M2_CP_FEASIBILITY_MATRIX.md).
