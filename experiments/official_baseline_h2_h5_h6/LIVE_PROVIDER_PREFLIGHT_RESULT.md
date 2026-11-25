# OpenRouter provider preflight result

Follow-up: [the offline failure investigation](PROVIDER_FAILURE_INVESTIGATION.md) records the user's subsequent zero-activity account check and the now-tested diagnostic fixes. The execution evidence and reservation described below are unchanged; references to the adapter's diagnostic limitation describe the implementation used for this attempt.

**INCONCLUSIVE — stopped on the first GPT-5 attempt. GPT-5-nano was not attempted.**

The user authorized at most two sequential requests with a $0.50 combined inference ceiling and supplied the key through the requested local hidden-entry console. Account billing settings were confirmed by the user, not queried through an API. The driver ran once. No retries, substitutions, diagnostic API calls or pilot runs followed the failure. The preflight activation gate has been disabled again; pilot gates remain disabled.

## Preserved execution evidence

| Item | Recorded result |
| --- | --- |
| Submitted request | `openai/gpt-5`, 2026-11-25 01:39:03 UTC (07:09:03 Asia/Colombo) |
| Requested provider policy | OpenAI only; fallback disabled; required parameter support; price ceilings $1.25 input / $10 output per million |
| Admitted transport attempts | 1 |
| Driver result | `stopped`, `RuntimeError`, ledger stop reason `usage_unknown` |
| Accepted response | None |
| Actual provider route / resolved model | Unknown; no provider response retained |
| Token usage / reasoning usage | Unknown |
| Actual billed inference cost | Unknown; **not established as $0** |
| Unresolved reserved exposure | **$0.4484480**, retained against the authorized $0.50 ceiling and eventual $20 campaign envelope |
| GPT-5-nano | Not dispatched |

The ledger's `spent: "0"` means no cost was reconciled; it is not evidence of zero billing. Keep the reservation until reliable account evidence resolves it. Do not reset or delete the attempt to rerun it.

The authoritative [live journal](results/provider-preflight/live.json) contains the exact request, admission ticket, active implementation/policy hashes, submission time and unresolved ledger. [Credential-handoff receipt](results/provider-preflight/credential-handoff.json) records one driver invocation after hidden local entry, without the key. [Account confirmation](results/provider-preflight/account-confirmation.json) records only the user's supplied settings. [Final outcome/integrity record](results/provider-preflight/live-outcome.json) records the stopped state and gate reset.

## Diagnostic limitation

The current HTTP adapter raises `RuntimeError` on a non-200 status or oversized response, and does not return the response to the driver. The driver records the exception type without its text. Consequently this attempt has **no retained HTTP status, provider error body, generation ID, actual routing metadata, tokens or billed cost**. The precise rejection/failure cause cannot be established from the journal. It would be incorrect to claim that OpenAI actually served the request or that any particular HTTP error occurred.

This is a limitation of our error-evidence capture, not a passed provider verification. All evidence that was actually captured is retained; missing response evidence cannot be reconstructed locally. No additional provider request was made to investigate it.

## Credential handling and local launch repair

The key was entered only in the user's local console with echo disabled. The helper refuses fallback to echoed input, does not read `.env`, and passes the key in parent memory to the HTTP adapter. It does not serialize the key or authorization header. The adapter's key reference is cleared on exit; the local process has exited. This is not a claim of cryptographic memory erasure.

The first console launch stopped before key entry due to a local hash-check type error. The helper was corrected and checked offline with a mocked prompt and mocked driver; no provider call or real credential was involved in that check. The [failed launch record](results/provider-preflight/credential-entry-before-input-failure.json), its lock, and [offline handoff check](results/provider-preflight/handoff-offline-check.json) are preserved. Reopening that local prompt did not retry a provider request. The later actual driver invocation admitted exactly one attempt.

## Minimum next steps

1. Review the existing OpenRouter account Activity/billing entry around the submission time manually, and retain a credential-free record of its status, model/provider, usage and charge if available. No account/API lookup was authorized or performed by the agent. Absence of an entry alone should not automatically release unresolved exposure.
2. Fix only the offline HTTP failure-evidence path to preserve the status and bounded, credential-redacted provider error/generation metadata. Verify that change with fake HTTP errors, retaining the no-retry and stop rules. Do not loosen request/response gates based on speculation about this failure.
3. Review the reconciled exposure and available failure evidence, then obtain **new explicit authorization** before any further provider request, including GPT-5-nano. The current two-request sequence stopped; no automatic continuation is permitted.
4. The official nine-run pilot remains blocked pending a successful reviewed provider preflight, a general conservative input bound, a campaign policy identity covering the host routing policy, carried-forward preflight exposure and separate pilot approval. Preserve the approved order, budgets, round-one checkpoint and round-end censoring rule.

No official RLM source, dataset or H2/H5/H6 protocol was changed. No RootCheck implementation, commit or push was performed.
