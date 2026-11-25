# Official RLM pilot: review handoff

**Current readiness:** [READY FOR LIVE S1-R01 BASELINE EXECUTION](S1_R01_EXECUTION_READINESS.md), pending explicit authorization for that one run. The minimum input-bound, campaign-policy, carried-exposure and telemetry prerequisites are implemented and checked offline. The prepared campaign starts with $0.44882910 exposure and zero pilot runs. Use the exact command in that handoff; no provider probe or pilot has been executed during this preparation.

**Latest handoff:** the two configured provider models have passed saved-response reassessment, with a retained GPT-5 reasoning-detail caveat. Known inference charges are $0.00038110; combined exposure including the original unknown reservation is $0.44882910. See [final provider results and the four concrete remaining pilot prerequisites](PROVIDER_PREFLIGHT_FINAL_RESULT.md). No repeated inference is needed for snapshot verification. The pilot remains disabled; historical readiness statements below are superseded by that result.

**Current two-request status:** [READY FOR TWO-REQUEST LIVE PREFLIGHT AUTHORIZATION](TWO_REQUEST_PREFLIGHT_AUTHORIZATION.md). The approved host fixes and bounded driver passed targeted offline checks. Live and pilot gates remain disabled. The historical integration/review handoff below is preserved; its former provider-policy/driver implementation gaps are resolved for the two literal probes only.

**READY FOR LIVE PREFLIGHT REVIEW.** The minimum external broker, persistent campaign accounting and per-run lifecycle are implemented and tested offline. This is not authorization to load credentials or send live requests. `offline.py live` and the `Pilot` live gate still refuse execution.

The subsequent [public-provider review and exact two-request proposal](PROVIDER_PREFLIGHT_REVIEW.md) identifies host routing, response-validation and input-bound requirements still outstanding before dispatch. Published prices and semantics have now been reviewed; real-provider behavior remains untested. The proposed combined preflight ceiling is $0.50. This is an inert proposal, not activation or a change to the nine-run protocol.

## How the real RLM runs

1. The parent loads the checksum-verified public context/query and the unchanged pilot configuration. It verifies the pinned source and staged payload, creates a private copy of the verified runtime, registers a fresh zero-capability AppContainer identity and prepares scratch plus JSON mailboxes.
2. Inside that AppContainer, `isolation_worker.py` calls `broker_client.run()`. This imports the actual pinned `rlm.core.rlm.RLM`, constructs it with the approved arguments, and invokes `runtime.completion(context, root_prompt=query)`. The only client substitution is the experiment's `BaseLM` transport adapter through the existing client factory. Official REPL execution, prompts, model selection, recursion, depth fallback, iteration limits, batches and return selection remain in official RLM.
3. Each client call publishes a JSON completion request. The parent validates its model, messages and sampling fields, computes the input bound using the reviewed host function, and reserves the existing ledger's budget before submitting a provider attempt. Descendants and concurrent helpers share this ledger. Worker-supplied prices, token estimates, credentials, URLs or ticket IDs are not accepted.
4. The parent alone makes the provider request. The HTTP adapter uses the pinned client's text-message shape and `max_tokens` to `max_completion_tokens` normalization, a fixed OpenRouter endpoint, one attempt, and explicit credential injection. There is no dotenv, environment-key or proxy discovery. No real credential has been supplied and this adapter has only used a fake HTTP connection during testing.
5. The parent reconciles provider usage and cost before releasing output. Accounting conservatively uses the greater of rate-derived cost and reported cost. Missing usage/cost, over-bound consumption, admission denial or deadline stops further dispatch and terminates the RLM worker. Unknown exposure remains reserved. A budget denial is never returned as a recoverable helper string.
6. Provider records, event prefixes, returned results and accounting are saved outside the worker's permissions. The process exits, its AppContainer profile is deleted, and its private runtime/scratch/mailboxes are deleted. Runs leave the shared verified stage unchanged. Its allowlist was explicitly refreshed for the broker client, with the prior manifest retained. Cleanup errors block campaign progression and are retained separately from the execution outcome.

The parent journals reservations before dispatch and saves campaign accounting between invocations. `Pilot.run_next()` performs one run, in the existing nine-run order, using the same campaign ledger after restart. Interrupted campaigns require review rather than resetting exposure. Unknown reservations also block further dispatch pending reconciliation. The round-one checkpoint and cumulative **two resource-censored runs at the end of any round** rule are unchanged. All completed, failed and censored records remain retained; no automatic replacements or budget increases occur.

## Essential files versus artifacts

| Purpose | Files needed |
| --- | --- |
| Official execution | Unmodified `rlm/` at the recorded pin, existing Python runtime and required installed dependencies |
| Host provider/accounting | `runners/broker.py`, `runners/budget.py`, `runners/pilot_runner.py` |
| Windows boundary and worker | `runners/windows_boundary.py`, `runners/isolation_worker.py`, `runners/broker_client.py`, `runners/temp_permissions.py` |
| Existing protocol and observation | `runners/config.py`, `runners/pilot.json`, `runners/observe.py`, `runners/offline_guard.py`, `common.py`, package initializers |
| Public run inputs | `tasks/data/*/{context,query}.txt`, `tasks/dataset_manifest.json`; only selected public text enters the worker |
| Rebuildable local runtime | `isolation-staging/`, verified against `results/windows-stage.json`; each broker run uses a temporary private copy |
| Generated research evidence | `results/broker/*.json`, journals, campaign state, summaries and artifact manifest; retain these, but do not put them in the worker |
| Test/development utilities | `broker_check.py`, `isolation_check.py`, `tests/`, `fixtures/`, old mock supervisor and historical mock traces; not the live provider path |
| Researcher-only evaluation | `evaluators/`, oracle JSON and assessments; not required by the worker and never staged |

`offline.py mock --scenario ...` now uses the integrated broker with a canned provider. Its bounds and usage are intentionally synthetic. The older fixture tools remain available for reviewing existing evidence. No baseline dataset, oracle, original behavioral fixture suite or original isolation suite was regenerated during this broker work.

## Targeted evidence

- [Six broker checks](results/broker-summary.json): actual official-RLM routing and nine accounted calls; attempt and run/campaign admission; restored campaign exposure; unknown usage; timeout without retry; reported-cost overrun; unpriced model and deadline gates; request validation and bounded file reads.
- [Focused final checks](results/broker-followup-summary.json): provider observation events, duplicate batch slots and root-visible assessment packets; admission denial kills instead of becoming a helper error; fake HTTP request shape. Per-run profile and scratch cleanup passed.
- [HTTP deadline check](results/broker-http-check.json): fake connection only; a connection finishing after its deadline cannot dispatch a request. HTTP failure causes one attempt, with no automatic retry.
- [Campaign recovery check](results/pilot-resume-check.json): saved exposure restored; interrupted campaign, changed policy and unresolved exposure all block progression. No pilot run was executed by this check.
- The existing ledger's focused reconciliation/unknown-usage/overrun regression passed. The completed 30-method full suite, 21 original equivalence pairs and nine original protected-path checks were preserved, not rerun.

[Final verification](results/broker-final-verification.json) confirms the review-ready decision, all 90 protected files unchanged, no official-source diff, no staged changes and no remaining per-run scratch directories.

The engineering revision is `broker-integration-1`, recorded on new run evidence. Earlier isolation results and stage manifest are preserved separately. These synthetic records must never be pooled with natural baseline runs.

## Exact live-preflight requirements

Before any live request, review and record:

1. **Provider configuration:** confirm availability and exact semantics of the provisional root `openai/gpt-5` and secondary `openai/gpt-5-nano` identifiers through OpenRouter. Confirm the selected provider routes, no undisclosed billed retries/fallbacks, accepted `max_completion_tokens`, treatment of reasoning tokens, text-only response shape, usage fields and cost units. No temperature/seed or routing change is introduced by this implementation. Version material changes before collecting runs.
2. **Prices and conservative bounds:** supply reviewed per-model upper-bound rates and a host-side input-bound callable with a recorded method/version covering complete messages and provider framing. The synthetic `100`-token bound is not suitable for live use. Verify the 64,000 input and 32,768 completion caps and the 10% reservation margin against those facts. Confirm returned cost covers the charged request; a missing or invalid value must remain unresolved. If the approved $2/$20 envelope cannot safely admit calls, stop for protocol review; do not raise it automatically.
3. **Source and configuration:** inspect the final implementation/manifest, verify the pinned source hashes, current staged payload and approved pilot settings. Supply the same reviewed policy to one persisted campaign. The policy fingerprint covers rates, limits, config, synthetic/live mode and bound-method revision. Do not repurpose synthetic campaign state for live runs.
4. **Operational readiness:** run as the Windows user able to create/delete the tested per-run profiles. Confirm successful cleanup and no unfinished campaign marker. Confirm provider connect/read timeout behavior; the host closes active sockets at its deadline and waits for attempts to settle. OS DNS/connect behavior and remote billing cancellation have not been demonstrated by offline mocks. A terminated local worker does not prove a remote request was unbilled. Reconcile or review unknown exposure before continuing.
5. **Authorization and credential handoff:** obtain explicit authorization for credential provisioning and separately specified live preflight requests. Supply the credential only to the parent HTTP adapter. Current code does not discover or read it. Release the explicit live gate only after that review; adding an environment variable or credential is not activation. Any preflight calls consume approved/accounted exposure and are not silently substituted for pilot runs.
6. **Pilot review:** approve the reviewed configuration and evidence, then invoke one run at a time through `Pilot`. Honor the round-one engineering review and existing round-end stop rule. Preserve all statuses and version material protocol changes without silently pooling affected runs.

These are live configuration, authorization and provider-validation requirements. No additional service, container platform, benchmark redesign or RootCheck implementation is needed for the review handoff. Ruff/pre-commit remain unavailable; they are not claimed as passed. Worker event logs remain observations from the RLM process, not a tamper-proof audit channel; the authoritative admission/provider ledger is external.

## Offline reproduction

The targeted checks use existing dependencies and create/delete temporary AppContainer profiles under the registering Windows user:

```powershell
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/broker_check.py
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py preflight --reuse-evidence
```

The first command runs only the new broker checks. The second reuses completed evidence and refreshes integrity/reporting. It still exits **2** because live execution is disabled, even when the decision is **READY FOR LIVE PREFLIGHT REVIEW**.
