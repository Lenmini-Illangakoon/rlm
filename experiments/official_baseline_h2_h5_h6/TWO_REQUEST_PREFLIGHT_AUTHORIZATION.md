# Two-request live preflight authorization handoff

**Execution outcome:** [INCONCLUSIVE; stopped on GPT-5](LIVE_PROVIDER_PREFLIGHT_RESULT.md). One attempt was admitted, no provider usage/cost was available, and $0.4484480 remains reserved. GPT-5-nano was not attempted. The preflight gate has been disabled again and the pilot remains disabled. The earlier preparation/activation entries below are historical; further provider requests require a new review and explicit authorization.

**Activation update:** the user has now authorized the documented two-request preflight with the $0.50 combined ceiling. Only `LIVE_PREFLIGHT_AUTHORIZED` has been activated; all pilot gates remain disabled. Execution is awaiting selection of the secure credential source and confirmation of ordinary credit billing without BYOK/request-altering presets. No credential has been accessed and no provider request has been sent. [Activation evidence](results/provider-preflight/authorization.json) records the approved scope and before/after source hashes. The preparation record below is retained as historical context.

2026-11-25 — **READY FOR TWO-REQUEST LIVE PREFLIGHT AUTHORIZATION.** Implementation is complete for the bounded provider probe. Live execution and credential access are not authorized or enabled. The nine-run pilot remains disabled.

## Implemented scope

The exact [proposal](provider-preflight-proposal.json) remains byte-identical. [The driver](runners/provider_preflight.py) pins its SHA-256, permits only its single literal message, and makes GPT-5 then GPT-5-nano requests sequentially through the existing request builder, ledger and `OpenRouterHTTP`. It does not start RLM, run generated Python, stage data or create Windows profiles. Previously verified official-RLM execution and isolation are preserved.

Each request reserves 64,000 input and 32,768 completion tokens. Maximum combined reserved exposure is **$0.466385920**, including the 10% margin, inside the **$0.50** combined ceiling. The fixed two-attempt limit permits no retries. The second request requires the first to pass response verification and durable reconciliation. A retained record or interrupted lock prevents automatic replay. The host policy, proposal and implementation hashes are journaled; actual/unknown exposure is explicitly retained for later inclusion in the $20 campaign envelope.

The host supplies OpenAI-only routing, no provider fallback, required parameter support and model-specific price ceilings. The HTTP adapter independently enforces that policy, adds the routing-metadata header and retains the fixed endpoint and one-attempt behavior. The broker journals the enforced body before submitting the HTTP task. Worker routing overrides are refused.

`Broker.settle` now accounts for known usage before rejecting top-level errors, choice errors or `finish_reason: "error"`. Partial error text never reaches the outbox. Missing usage remains reserved. Normal non-error length-limited text retains official baseline handling. New broker records identify engineering revision `broker-integration-2-provider-policy`; previous records remain unchanged.

The probe additionally requires the expected model/provider, one selected OpenAI route attempt, non-BYOK accounting, a generation ID, a normal `323` answer, consistent token/detail counts, and a charge matching reviewed rates. Reasoning is already included in completion usage and is never added twice. Cached input is checked at its reviewed discounted rate; ledger exposure still uses the conservative uncached cost. Failed checks retain the full response and stop the probe without a replacement call.

## Targeted validation

- [Five new methods passed](results/provider-preflight-check-62d2747cb9294f4a8515d24b31c94d0b.json): exact two-request wire bodies and metadata; durable admission and sequencing; provider-error rejection with known/unknown usage; ordinary length handling; literal/policy/live gates; stale-lock/replay refusal; combined reservations and attempt limit; deadline before dispatch; and 13 response/HTTP failure variants that prevent the second call.
- [One affected existing HTTP method passed](results/provider-preflight-http-regression.json): fixed HTTP shape, 429 without retry, strict JSON rejection, and no dispatch after a late connection. Its wire assertion was updated only to expect the newly enforced routing object.
- Sockets were forbidden; HTTP connections were mocks. No real credentials or provider requests were used. Prior benchmark, full, equivalence and AppContainer suites were not repeated. [Final integrity evidence](results/provider-preflight-implementation-final.json) covers protected files, unchanged proposal/pilot settings and retained evidence.

To reproduce only the new checks, run:

```powershell
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/provider_preflight_check.py
```

This writes a new uniquely named offline summary. It does not enable the driver for live use. Ruff/pre-commit remain unavailable and are not claimed as passed.

## Unresolved assumptions and deliberate stops

The full 64,000-token reservation is an engineering bound for this exact tiny literal, not a certified general tokenizer/framing bound. No other messages are accepted. This cannot serve as the nine-run pilot's full-message input estimator.

Public model/rate documentation was reviewed on 2026-11-24; account availability and actual routing metadata remain untested. Returned model IDs must exactly match the proposal. A dated alias, absent required metadata/reasoning details, unexplained billing difference or changed endpoint behavior stops the probe for review, rather than broadening acceptance. Zero reasoning tokens are valid but do not demonstrate nonzero reasoning billing. Missing service-tier metadata is recorded as unknown; an explicitly reported tier other than default is refused. Cost comparison uses exact Decimal equality; even a rounding discrepancy stops review without automatically introducing a tolerance.

The 300-second socket deadline is bounded by the remaining 900-second run allowance. Windows DNS resolution can outlast a socket deadline; these tests do not prove a hard process-return deadline. Non-streaming remote processing/billing can continue after a local timeout. Unknown exposure remains reserved. Provider cap/price enforcement and hidden internal provider behavior cannot be proven by mocks; overrun detection cannot reverse a charge. No live timeout stress test, extra lookup or automatic reconciliation API call is included.

## Steps requiring separate authorization

1. Approve credential provisioning to the parent adapter and **at most these two requests under the $0.50 combined inference ceiling**, accepting the limited literal-bound and timeout assumptions. This is not authorization for pilot runs, model substitutions, retries, top-ups or extra diagnostic API calls. Confirm ordinary OpenRouter credit billing with no request-altering account preset/BYOK; this account state has not been accessed.
2. Only after that approval, release `LIVE_PREFLIGHT_AUTHORIZED` in `runners/provider_preflight.py` in a reviewed activation change. Keep `pilot.json`, `offline.py live` and the `Pilot` gate disabled. Record the new driver hash; the journal captures it automatically. The current constant is **False**; there is no CLI switch or environment-variable activation.
3. Provision the explicitly approved credential in parent memory using the agreed handoff. The driver never reads dotenv, environment credentials, credential files or a credential store. Invoke `provider_preflight.run(OpenRouterHTTP(key))` once through the local Python entry function, without an alternate evidence path. Never log the key or authorization header. No credential source has been selected or accessed yet.
4. Retain `results/provider-preflight/live.json` and any interruption lock. Stop on any failed check, unknown usage or timeout. Do not delete evidence to rerun. Review the returned routing/usage/charge evidence and carry its `carry_into_campaign_exposure_usd` into the eventual total campaign accounting before approving any pilot. The driver reports that carry-forward amount; it does not silently modify a pilot campaign.

No remaining implementation blocker prevents requesting authorization for these two probes. Live empirical facts remain unverified by design. The nine-run pilot still requires a general conservative input bound, a live campaign identity covering the host policy, accounted preflight exposure and separate pilot approval. Its budgets, order, round-one checkpoint and cumulative two-resource-censored-runs round-end stop rule remain unchanged.
