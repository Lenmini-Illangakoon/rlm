# Offline implementation report

**READY FOR LIVE S1-R01 BASELINE EXECUTION, pending exact-run authorization.** The host now applies a conservative general text-message bound, frozen provider/snapshot/source identity, exact-once $0.44882910 preflight carry-forward, and fail-stop telemetry/budget checks. The sole approved old unknown ticket is retained; unresolved pilot requests still block progression. Four new host tests and the targeted AppContainer evidence check passed. Actual imported `rlm.core.rlm.RLM` identity and 35 runtime hashes were verified inside AppContainer; 90 protected files and previous evidence remain intact. The prepared campaign has no pilot runs. Full/root-visible execution evidence is distinguished, and all three hypotheses remain pending evidence review for every real run. See [first-run command, evidence coverage, checks and authorization gate](S1_R01_EXECUTION_READINESS.md). No API calls or credential access occurred during this preparation. Earlier statuses below are historical.

**Latest provider verdict: PASSED with a recorded GPT-5 reasoning-telemetry caveat.** One authorized generation lookup corroborated the saved GPT-5 charge and snapshot; GPT-5 inference was not repeated. One authorized nano request returned HTTP 200 and `323`. Separate saved-response reassessments accept the exact dated endpoints, preserving the original gate-failure journals. Known charges total $0.00038110; including the unchanged unknown $0.448448 reservation, exposure is $0.44882910 under the $1.00 ceiling. Ten essential new offline checks passed; completed suites were not repeated. The pilot remains disabled pending a general prompt bound, provider-aware campaign identity/exposure handling, the documented telemetry treatment and separate authorization. See [final results and concrete remaining pilot prerequisites](PROVIDER_PREFLIGHT_FINAL_RESULT.md). Earlier status entries below are historical.

**Latest authorized live attempt: FAILED verification.** Under the user's increased $1.00 combined ceiling, the separately recorded GPT-5 request returned HTTP 200 and `323`, but stopped on `selected_route`: the selected OpenAI endpoint reports `openai/gpt-5-2025-08-07` rather than the requested alias. GPT-5-nano was not sent. Response-reported cost was $0.00034375; the previous $0.448448 reservation is unchanged, giving combined ledger exposure $0.44879175. Reasoning usage (94) also exceeds completion usage (32), leaving the inclusion assumption unresolved. The source live gate and pilot remain disabled. See [complete attempt-two results and next minimum requirements](LIVE_PREFLIGHT_ATTEMPT_TWO_RESULT.md). Only the new carry-forward/credential-parser delta was checked offline; previous suites were not repeated. No automatic retry or post-failure provider lookup occurred.

**Offline failure investigation completed:** four new targeted mock tests passed for Windows hidden-entry validation, sanitized HTTP diagnostics and fail-stop accounting. The user's zero-activity/unchanged-credit observations favor rejection before inference; the original missing HTTP status prevents identifying a specific authentication or routing failure. All original live evidence and the unresolved **$0.448448** reservation are preserved. Live execution remains disabled. A retry requires accounting disposition, a separate reviewed run record/source authorization and fresh explicit approval; it cannot fit the existing $0.50 envelope with the old reservation still held. See [findings, implementation changes and retry blockers](PROVIDER_FAILURE_INVESTIGATION.md) and [offline results](results/provider-diagnostics-check.json). Historical status entries below describe earlier stages.

**Live provider preflight outcome: INCONCLUSIVE.** The authorized local hidden-entry handoff completed and the driver stopped after one GPT-5 attempt with `RuntimeError` and `usage_unknown`. GPT-5-nano was not dispatched. Actual provider routing, token usage and billed cost are unavailable; $0.4484480 remains reserved, not recorded as a known charge. A diagnostic limitation in the adapter/driver discarded the HTTP status/error body; the exact cause cannot be established locally. No retry or additional API lookup was made. The preflight gate is disabled again, all pilot gates remain disabled, and existing live evidence prevents replay. See [the complete outcome, limitations and minimum next steps](LIVE_PROVIDER_PREFLIGHT_RESULT.md). The earlier offline-ready and activation entries below are preserved as historical records.

**Authorized preflight activation:** the user approved at most the two documented requests under the $0.50 ceiling. The preflight-only gate is now enabled; the nine-run pilot remains disabled. Integrity of all 177 previously indexed artifacts and 90 protected files passed before activation. The only runtime change is the approved gate assignment. Secure credential-source selection and account-billing confirmation are pending; zero credentials accessed and zero requests dispatched. See [activation evidence](results/provider-preflight/authorization.json). No provider outcome is established yet.

**Current status, 2026-11-25: READY FOR TWO-REQUEST LIVE PREFLIGHT AUTHORIZATION.** [The authorization handoff](TWO_REQUEST_PREFLIGHT_AUTHORIZATION.md) supersedes the historical unresolved-defect status below. `Broker.settle` now rejects explicit provider errors after accounting for known usage; normal non-error length-limited completions are preserved. Host routing/price enforcement and routing metadata are implemented. `runners/provider_preflight.py` pins the unchanged proposal, accepts only its literal input, journals before dispatch, enforces the $0.50/two-attempt ceiling, validates responses and prevents replay. Its live gate remains false; no credential is discovered or read.

Five targeted fake-HTTP/response methods and one affected existing HTTP regression passed. Previous datasets, protocols, raw results and completed suites were preserved, not rerun. The original defect reproduction remains retained as historical evidence. No official RLM or staged worker source changed. Actual provider availability, alias/metadata shape, cap enforcement, input-framing assumptions and remote timeout billing remain empirical limitations; strict checks stop rather than adapt or retry. General pilot input bounds, campaign policy identity and exposure carry-forward remain pilot prerequisites. Exact authorization/provisioning/activation steps and evidence links are in the handoff. No live calls, credential access, RootCheck implementation, commits or pushes occurred.

**READY FOR LIVE PREFLIGHT REVIEW.** The external provider/budget broker now drives the actual pinned official RLM inside a fresh AppContainer for each run. Targeted offline checks pass for routing, accounting, admission, persistent campaign exposure and cleanup. Prior datasets, oracles, equivalence and isolation evidence were preserved. Live execution remains disabled. See [the concise execution map, essential files and exact review requirements](LIVE_PREFLIGHT.md).

Subsequent review, 2026-11-24: [PROVIDER_PREFLIGHT_REVIEW.md](PROVIDER_PREFLIGHT_REVIEW.md) verifies public OpenRouter model/rate/accounting documentation and supplies an inert [two-request proposal](provider-preflight-proposal.json), capped at $0.50 with $0.466385920 reserved exposure. Runtime code and pilot settings were not changed. Dispatch remains blocked on explicit host routing/price policy, routing metadata, partial-error response checks, the literal-only input-bound review, a narrow driver and separate credential/request approval. General live message bounds and campaign policy identity remain pilot blockers. Existing offline passes do not cover these newly identified live-provider gaps. No credential/API access, benchmark regeneration or completed test-suite rerun occurred in this review phase.

Finalized 2026-11-25: the saved arithmetic/configuration validation was already complete and was reused. A [targeted offline reproduction](results/provider-response-review.json) confirmed both top-level and choice-level provider errors can be delivered as ordinary partial text when usage is valid; the healthy control passed. This defect remains unfixed and blocks live dispatch. No HTTP transport was constructed; sockets/HTTPS were forbidden in the reproduction. The exact two-request proposal remains unchanged. See [final integrity evidence](results/provider-preflight-review-final.json). Recommendation: complete only the listed offline host-policy/response-check/driver work, then seek separate approval for credential provisioning and at most two live requests under the $0.50 cap. The nine-run pilot remains disabled and requires its own readiness review.

## A. Artifact inventory

[artifact-manifest.json](artifact-manifest.json) enumerates reviewable experiment artifacts with purpose, size and SHA-256; rebuildable staging copies are excluded. All repository changes are inside this experiment directory. The approved per-user AppContainer profile also creates Windows metadata outside the repository. The implementation groups are:

| Files | Purpose |
| --- | --- |
| `README.md`, `protocol.md`, this report | Commands, approved protocol, findings and blockers |
| `offline.py`, `common.py`, package `__init__.py` files | Explicit offline CLI, serialization, hashes and package imports |
| `tasks/generate.py`, `tasks/prepare.py` | Deterministic S2 renderer, checksum-verified historical input recovery and acceptance |
| `tasks/data/{S1,S2-v2,S3}/{context,query}.txt`, `tasks/dataset_manifest.json` | Six frozen public files and provenance |
| `evaluators/oracles.py`, `evaluators/oracle_results/*.json` | Independent serialized-input solvers and researcher-only answers |
| `evaluators/assessment.py`, `evaluators/RUBRIC.md` | Typed review schemas, four-way labels, evidence relationships and blinded workflow |
| `fixtures/programs.py` | 21 canned runtime behaviors, separate from natural-run configuration |
| `runners/mock.py`, `runners/observe.py`, `runners/offline_guard.py` | Synthetic BaseLM adapter, passive observation and accidental-live-call guards |
| `runners/budget.py`, `runners/broker.py`, `runners/pilot_runner.py` | External provider admission, one-attempt HTTP transport, campaign accounting and approved progression |
| `runners/broker_client.py` | Worker BaseLM adapter; invokes the actual pinned RLM without rewriting recursion or routing |
| `runners/supervisor.py` | Retained earlier trusted-fixture supervisor; not the provider path |
| `runners/config.py`, `runners/pilot.json` | Verified task loading, unchanged nine-run order and approved round gates |
| `runners/preflight.py` | Offline report, saved-evidence refresh, integrity check and artifact inventory |
| `runners/windows_boundary.py`, `runners/isolation_worker.py`, `runners/temp_permissions.py` | AppContainer process boundary, JSON worker and scratch-directory adapter |
| `isolation_check.py`, `tests/check_windows_isolation.py`, `WINDOWS_ISOLATION.md` | Affected isolation/equivalence checks and reproducibility |
| `tests/test_{benchmarks,assessment,instrumentation,safety,config}.py` | Deterministic checkpoint validation |
| `results/*`, `results/equivalence/*`, `results/mock/*` | Full raw traces, summaries, synthetic review fixtures, canary and integrity evidence |

Research evidence remains Git-trackable. Only rebuildable `isolation-staging/` runtime copies are ignored; their hashes are retained in `results/windows-stage.json`. Larger future traces require the durable-copy/checksum procedure in README before exclusion.

## B. Dataset and oracle verification

| Scenario | Actual context SHA-256 | Actual query SHA-256 |
| --- | --- | --- |
| S1 | `c5118358cb1320e901483b37cbdef3577d1db8188a18f6b9bcd7b873a89ceaff` | `2b2906e3bef0677692633e3f297321b87a5651230ff51dd38ff81d668ae10a65` |
| S2-v2 | `2910a820abaa38032ab01ffd07eb603e06b53a3f683b3f8210808bdd58c44069` | `bfcf433d53cbfa8e808d51140ad485b59d6f9392a968819ef2be74a3c1461627` |
| S3 | `55075334b0f7080a790dda9a4b5582de41cd7a7ce38f424a9af39c52f4dd9009` | `5303ebc516868daec4aaabc730cfbb04bbf28d478b38524d4403676d006ed36b` |

S1 independently reconstructs exactly the archived 60-ID set and total **1,361**. The original Git blobs match the approved checksums; the CRLF-converted historical working files were neither normalized in place nor modified.

S2 independently reconstructs **100 eligible** current shipments, ranks **SH-10106 (6,883), SH-10068 (6,846), SH-10097 (6,809)** and totals **20,538**. R/W/Q/H references are checked against parsed source notes. SH-10138 loses the 6,809 tie; SH-10128 fails inventory; eight archived shipments are excluded. Repeated rendering is byte-identical, UTF-8 without BOM, LF with one final newline. Corrupt/duplicate/missing notes, incorrect section ends, wrong source references, wrong tie choices and incomplete outputs are tested. Mutating a source quantity changes the independently computed eligibility and result.

S3 verifies all **320 inventory records**, four archived and four planned records, **104 eligible** ACTIVE/APAC records, minima **3731 and 4637**, and product **17,300,647**. Original context bytes are preserved; the refined public query is versioned as a controlled variant.

## C. Evaluation infrastructure

H2 records pre-result contracts by action stratum, normal completion, semantic mismatch, origin, recovery, containment and propagation. H5 separately records C/O/S/V/P and scores the actual return; incorrectness alone is not an overall positive. H6 commits a sufficient stable prefix and root-visible delivery before reviewing later purpose. Exact source-to-claim relations require evidence; unsupported dependencies remain unknown.

Human fields are explicit: reviewer, rationale, materiality, supporting refs and prefix hash. Automatically checked output values/cardinality and typed label rules are separated from semantic judgments. Review packets exclude future events; H6 packets additionally exclude computed-but-undelivered values. Execution traces, independent oracles and researcher annotations are distinct artifacts. See [rubric](evaluators/RUBRIC.md) and [synthetic annotation examples](results/assessment-fixtures.json).

## D. Instrumentation verification

The previously completed [test summary](results/test-summary.json) and [full output](results/test-output.txt) are preserved. That suite contains **30 test methods**, including **21 control-versus-instrumented fixture pairs**, plus supervised resource-censor comparisons. Each scenario also has a supervised transport-only mock record.

Observation boundaries cover exact provider requests/outputs, parent/depth identities, plain/genuine/depth-fallback routing, socket correlation, batch slots including duplicate inputs and reordered completion, Python setup/execution/results, immutable builtin snapshots, helper returns before same-block consumption, root request history/feedback, answer writes/captures, scaffold-restored captures, iteration selection and actual returned content. Provider timing and synthetic usage are recorded. [Per-fixture overhead measurements](results/equivalence-summary.json) retain both durations; they are small-sample engineering measurements, not a production overhead guarantee.

Comparisons preserve model-visible messages and outcomes. Only timing and fresh bootstrap temporary-directory names are normalized for comparison; raw evidence is retained. Concurrent provider call order is compared as a multiset with explicit slot/parent assertions. Tests cover errors, recovery, same-block finalization, multiple blocks, repeated captures, mutation after capture, replaced answer dict, feedback truncation, iteration/depth fallback, cancellation and resource censoring.

Limitations remain: arbitrary-object snapshots, every transient in-block mutation, complete instruction-level dependencies and live provider metadata/retry behavior are not established. These are documented review gaps, not silently inferred observations. No validation feedback or extra model-visible print is injected.

## E. Resource and isolation tests

The synthetic ledger tests the approved **$2/run, $20/campaign, 24 attempts, 64,000 input, 32,768 output, 900 seconds** envelope and **10%** reservation margin. Concurrent pre-dispatch admission is atomic, descendants share the parent ledger, known usage reconciles, unknown usage holds its reservation and stops dispatch, and cancellation preserves unresolved exposure. Over-bound usage is recorded and stops execution. The external supervisor terminates a hung worker and kills on denial without converting it into a recoverable helper error.

The live prices, token bounds, provider retries and billing behavior are **not verified**. All rates and usage in these tests are synthetic.

The original same-account LocalREPL could read the dummy researcher canary: its normal `open`/imports retained researcher Windows permissions. That failure is preserved in [original evidence](results/isolation.json). AppContainer now denies all nine tested protected paths through Python, native and extended-path access, and denies ACL tampering, parent-memory access, child processes and a separate host service. Public scratch/context and same-container helper communication work. [Current isolation summary](results/windows-isolation/summary.json) records 21/21 equivalent behaviors and external timeout success. No real credentials were opened. All three default mock transports passed; see [transport evidence](results/windows-isolation/transport-summary.json).

The AppContainer transport and parent-owned ledger are now integrated. New [broker checks](results/broker-summary.json) pass with real pinned RLM and a synthetic external provider: nine calls follow expected routing and are accounted exactly once. Attempt/run/campaign caps, restored exposure, unpriced calls, unknown usage, timeout and reported-cost overrun are enforced externally. [Final focused checks](results/broker-followup-summary.json) preserve provider events, duplicate batch slots and root-visible assessment packets. New per-run identities, private verified runtime copies and scratch/mailboxes are removed after evidence capture. Windows ownership prevented changing ACLs on the prior stage, so that stage is retained unchanged and private copies are used. Unknown usage retains reservations; interrupted or changed campaigns require review. [Recovery evidence](results/pilot-resume-check.json) confirms those gates. No RootCheck or validator feedback is introduced.

The approved stop rule is implemented: **two or more resource-censored runs cumulatively by the end of any pilot round** stop further execution for protocol review. Completed/censored runs are retained; budgets and runs are never automatically replaced; material changes require versioning and separate treatment. The round-one engineering checkpoint and nine-run sequence are unchanged.

## F. Reproducibility

The current reproduction and review checklist is [LIVE_PREFLIGHT.md](LIVE_PREFLIGHT.md). This phase ran six new broker integration methods, three focused follow-up methods, a fake-HTTP deadline/strict-JSON check, a campaign restoration/gate check and one existing ledger reconciliation regression. Overlapping follow-ups validate the final changed paths; they are not additional behavioral fixture suites. The 30-method full suite, original 21 equivalence pairs, nine protected-path probes, datasets and oracles were not repeated. `offline.py preflight --reuse-evidence` refreshes the report and integrity without rerunning them. Preflight still exits 2 because no live execution is enabled or authorized.

Ruff and pre-commit are unavailable in this environment. No dependency or upstream configuration was changed to install them. Those style/hook checks are not claimed as passed.

The completed isolation-phase [entry-point checks](results/windows-isolation/entrypoint-checks.json) passed: altered payload hashes, inventory mismatches and missing profile registration are refused; all 29 experiment Python sources parse. [Final verification](results/windows-isolation/final-verification.json) confirms the expected preflight exit code 2, offline isolation readiness, unchanged 90-file integrity, empty official-source diff and no staged changes.

## G. Git/source integrity

The branch remains `experiment/official-rlm-h2-h5-h6-baseline`, HEAD `fc6ba8bcaaf4a163a5afa9030d00e2103364b9ea`. Pinned runtime/tests/dependency-file diff is empty against the official pin. All **90 captured files** remain byte-identical: 64 protected baseline files plus M2 evidence and the unrelated `experiments/m2/smoke_test.py`. Historical Phase 3 files were only read. Nothing was staged, committed or pushed. See [before](results/integrity-before.json), [after](results/integrity-after.json) and [verification](results/integrity-verification.json).

The current [broker final verification](results/broker-final-verification.json) confirms **READY FOR LIVE PREFLIGHT REVIEW**, expected exit code 2, all 33 experiment Python files parsing, no remaining per-run directories, and unchanged 90-file/source integrity. No prior datasets or completed suites were repeated.

## H. Preflight decision

| Area | Decision |
| --- | --- |
| Benchmarks and independent evaluators | Ready for offline use |
| Assessment schemas/workflow | Ready; semantic judgments require human review |
| Instrumentation | Verified for the tested mock boundaries; capture gaps documented |
| Resource safeguards | Verified with synthetic rates/usage and external mock supervision |
| Oracle/filesystem isolation | **Passed for nine tested paths under AppContainer** |
| AppContainer runtime behavior | **21/21 comparisons and 3/3 default transports passed** |
| Joint isolation/resource integration | Passed with targeted offline mocks; per-run lifecycle cleanup verified |
| Live provider | HTTP adapter verified with fake connection; model/pricing/bounds/usage/timeout behavior still requires live-preflight review |
| Live pilot | Disabled and not authorized |

**READY FOR LIVE PREFLIGHT REVIEW. LIVE EXECUTION REMAINS DISABLED.**

## I. S1-R01 execution handoff

The preceding phase-specific readiness statements describe their historical checkpoints. Following the separately approved provider preflight and S1-R01 authorization, the first real baseline run completed with the actual pinned official RLM in AppContainer and RootCheck disabled. See [the finalized S1-R01 report](S1_R01_EXECUTION_RESULT.md) and [structured results](results/S1-R01-summary.json).

Exact membership of all 60 selected orders and total 1,361 match the independent oracle. Four root iterations made four GPT-5 requests through OpenAI, resolving to `openai/gpt-5-2025-08-07`; there was no delegation. Official completion time was 76.404 seconds and AppContainer job time 79.578 seconds. Provider-reported cost was $0.08246875; conservative accounting retained $0.09902875. Campaign exposure is $0.54785785 including unchanged carried preflight exposure and the unresolved $0.4484480 reservation. All new requests reconciled and cleanup succeeded.

Raw responses, chronological execution, actual return, usage, routing and reconciliation are preserved under run `broker-eaa4d3f974474c0e807569e72ddf4432`. [Preliminary hypothesis observations](evaluators/S1-R01-preliminary-observations.md) are separate from raw execution and formal assessments. Required blinded H2/H6 review and human confirmation of H5 remain outstanding; no formal hypothesis result is inferred from answer correctness.

Finalization checked the saved answer and evidence hashes only. No execution, API request, completed test suite or oracle reconstruction was repeated; configuration and official source remain unchanged. S2-R01 has not started and requires separate authorization.

## J. S2-R01 execution handoff

Following separate S2-R01-only authorization, the second baseline run completed with the same frozen policy, pinned official RLM and RootCheck disabled. The [S2-R01 execution report](S2_R01_EXECUTION_RESULT.md) and [structured summary](results/S2-R01-summary.json) preserve the actual return, oracle score, per-call usage and evidence references. Exact ranking, quantities, all twelve source IDs and total 20,538 match the independent S2-v2 oracle.

Eight root iterations made eight GPT-5 calls and two plain GPT-5-nano subcalls; no genuine recursive child RLM or batch occurred. Official completion time was 444.481 seconds, with AppContainer job time 447.110 seconds. Provider-reported cost was $0.17427805; conservative run accounting is $0.20135005. Cumulative campaign exposure is $0.74920790, retaining the original unresolved $0.4484480 reservation. All new requests reconciled and lifecycle cleanup succeeded.

The natural trajectory includes a generated SyntaxError, a normally returning subcall that supplied prose instead of requested JSON, a second revised-prompt subcall that reached its completion cap, and successful fallback to deterministic Python parsing. There were no transport retries or operator replays. [Separate preliminary observations](evaluators/S2-R01-preliminary-observations.md) distinguish the confirmed first output mismatch from formal H2 assessment, the resource confound on the second subcall, supported complete final acceptance, and a prose-only continuation after full candidate visibility. Required human/blinded review remains pending.

Post-run verification confirmed unchanged protected/runtime/implementation hashes, exact actual-answer extraction and scoring, trace ordering and capture/selection/return identity. No previous run, preflight check or completed suite was repeated. S3-R01 has not started and requires separate authorization; the round-one checkpoint still follows that run. No experimental configuration or official-source modification, commit or push was made.

## K. S3-R01 and Round 1 engineering checkpoint

Following separate authorization, [S3-R01](S3_R01_EXECUTION_RESULT.md) completed correctly: IDs 3731 and 4637, product 17300647. Three root GPT-5 calls, three iterations and no delegation took 38.112 seconds official completion time (40.547 seconds AppContainer job). Provider-reported cost is $0.03427350; conservative accounting is $0.03873750. Exact prompts/responses, code/results, finalization, actual answer and usage are retained under `broker-deb1b866c6344031816958a484472db8`; [preliminary observations](evaluators/S3-R01-preliminary-observations.md) remain separate from formal review.

The planned [Round 1 engineering checkpoint](ROUND_ONE_ENGINEERING_CHECKPOINT.md) **passed with documented limitations**. Three correct completed runs retain 125 chronological events and 17 uniquely identified provider calls; raw archives, prompt/response correspondence, iteration counts, actual returns, cleanup, 90 protected hashes, each 35-file runtime identity, frozen datasets and campaign/implementation identity verify. Saved routing, price, token bounds and usage reconcile offline for all calls. No suites, probes or earlier inference were repeated.

Total reported pilot cost is $0.29102030 and conservative pilot debit $0.33911630. Campaign exposure is $0.78794540 including unchanged carried preflight exposure and the unresolved $0.4484480 reservation. There are no new unresolved pilot tickets and zero run-level resource-censored runs; S2's output-capped subcall remains a separate resource-confounded action. No natural recursive/batch execution occurred, and formal human hypothesis review remains pending.

Round 2 has not started. The unchanged gate requires explicit checkpoint continuation plus separate S2-R02 authorization. No scenario, configuration, official source, prior raw execution or prior preliminary observation was changed; no retry, commit or push occurred.

## L. Authorized Round 2 completion

After the user approved engineering-checkpoint continuation and Round 2 only, S2-R02, S3-R02 and S1-R02 executed sequentially in that exact order. Each completed, passed independent actual-answer oracle scoring, retained a full raw record/trace/worker response/finalized provider journal, and received a structured summary, execution report and separate retrospective H2/H5/H6 notes. Per-run source/runtime, evidence, usage/accounting and cleanup checks passed before progression. No previous execution, preflight probe or completed test suite was repeated.

The [six-run report](ROUND_TWO_SIX_RUN_SUMMARY.md) and [machine-readable consolidation](results/round-two-six-run-summary.json) preserve metrics and exact evidence references. Round 2 reported cost is $0.15551175 with conservative debit $0.18546375. Across six correct completed runs, reported cost is $0.44653205 and conservative debit $0.52458005. Campaign exposure is $0.97340915 including unchanged preflight exposure and the old unresolved $0.4484480 reservation. No new pilot exposure remains unresolved.

The cumulative end-of-Round-2 censoring count is **0/6**, below the approved threshold of two; the stop rule is not triggered. S2-R01's output-limited subcall remains separately documented and is not a run-level censor. No new material H2 mismatch or redundant H6 continuation is demonstrated in Round 2; H5 is provisionally not observed, with all formal human/blinded review caveats retained. Existing findings were neither erased nor used to redesign scenarios.

All 90 protected files, frozen host implementation/policy, source/runtime identity, datasets and experimental configuration remain unchanged. No retry, replacement, budget increase, official-source edit, commit or push occurred. **Round 3 has not started and is not authorized; execution stops after six retained runs.**

## M. Authorized Round 3 interrupted by unknown pilot usage

After separate Round 3 authorization, [S3-R03](S3_R03_EXECUTION_RESULT.md) completed correctly in four root iterations/calls without delegation: 41.669 seconds official completion, $0.03900300 reported cost and $0.04303500 conservative debit. Its raw record, trace, worker response, finalized journal, oracle extraction and separate preliminary notes are preserved. The extra initial prose-only plan precedes sufficiency and is not a demonstrated H6 failure.

The next approved run, [S1-R03](S1_R03_EXECUTION_RESULT.md), completed one exploratory iteration, then its second root HTTP read failed with saved type `IncompleteRead`. It retained `operational_failure / usage_unknown`, no actual returned answer and no final worker response. Its known first-call charge is $0.01699750 and conservative debit $0.01843750; **$0.3937958750 remains reserved on attempt-00037**. No retry or replacement occurred. The unchanged unresolved-pilot gate blocks S2-R03, which has not started.

The [nine-slot campaign status](NINE_RUN_CAMPAIGN_STATUS.md) and [machine-readable record](results/nine-run-campaign-status.json) document seven correct completed runs, one operationally failed retained attempt and one unexecuted slot. Known reported pilot cost is $0.50253255, known conservative debit $0.58605255, and campaign protected exposure $1.4286775250 including the new hold and unchanged preflight exposure. The zero run-level censor count has not triggered the threshold; Round 3's end boundary has not been reached.

All available evidence, prior observations, runtime/protected/source hashes and cleanup checks pass, but the failed HTTP body/status/generation/usage and final elapsed/result are unavailable and explicitly documented. This is operational interruption, not a confirmed H2/H5/H6 reasoning finding. Formal classifications remain pending. Scenarios, frozen runtime/host implementation and limits were not changed; no extra provider probe, reservation release, source edit, commit or push was made. Progression requires verified accounting reconciliation under the existing policy; no further request has been sent.


## N. Campaign A closed after authorized S2-R03

S2-R03 completed correctly in three root iterations, no delegation, 49.874188 official seconds / 52.719 job seconds; 11,013 input and 4,601 completion tokens; $0.05372825 reported cost and $0.05977625 conservative debit. Targeted saved-evidence checks passed for oracle output, root-visible payload, prompt/response and candidate/actual-return equality, 35 runtime/90 protected hashes, frozen policy, accounting, cleanup and final progression. No completed suite or provider probe was repeated.

All nine frozen slots are retained: eight correct completions and one operationally interrupted S1-R03. S1-R03 billing was separately reconciled while its original journal/classification and reconciliation evidence were preserved. Total pilot reported charge is $0.58007130; conservative pilot debit $0.67151130. Protected exposure is $1.12034040 including the original unresolved $0.448448 preflight hold and $0.00038110 known preflight charges. No new pilot hold remains. Cumulative run-level resource censoring is 0/9, below the threshold of 2. The campaign progression is complete; no further experiment is authorized or started.

See [final nine-slot report](NINE_RUN_CAMPAIGN_STATUS.md), [machine-readable report](results/nine-run-campaign-status.json), [S2-R03 report](S2_R03_EXECUTION_RESULT.md), and [preliminary notes](evaluators/S2-R03-preliminary-observations.md). Full available evidence is retained; S1-R03 second response content and final elapsed/answer remain unavailable. Formal H2/H5/H6 classifications are pending. No official source, configuration, datasets or implementation infrastructure changed; no retries, commits or pushes.
