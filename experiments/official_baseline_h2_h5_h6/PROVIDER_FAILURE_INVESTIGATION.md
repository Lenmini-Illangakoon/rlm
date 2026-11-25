# Failed provider request: offline investigation

Status: diagnostic fixes verified offline; original provider preflight remains **INCONCLUSIVE**. No retry is enabled or authorized by this investigation.

The user reports checking OpenRouter after the failed request: today's Activity shows zero requests and $0.00 spent, no GPT-5 log matches approximately 07:09, and the credit balance remains $2.92. These are user-reported account observations, not an API reconciliation. They support a failure before inference, but do not identify its HTTP status or automatically release the reserved exposure.

## Likely cause and limits of the evidence

The best-supported explanation is an HTTP rejection before inference, such as authentication, request validation or routing rejection. The adapter explicitly raised `RuntimeError` for non-200 responses or a response exceeding 8 MiB. The live journal retained only that exception type. An oversized successful response is less consistent with the account observations; a specific 401, invalid key or routing defect cannot be established. No missing status or response body can be recovered from the existing local evidence.

The hidden-entry receipt confirms that entry passed the original nonempty/no-whitespace check. Thus an empty key was not accepted on that path. Inspection and mocking of the installed Windows `getpass.win_getpass` show no fixed length truncation: input accumulates until Enter, Backspace removes a character, and other control characters can become input. Tests covered 10,000 characters, Backspace, empty entry, early newline and a Ctrl-V character. An incomplete paste, quotation marks or a non-whitespace control character could previously pass validation. This establishes a possibility, not what the user actually entered. The real key was not read or reconstructed.

## Minimal implementation change

- `preflight_key_entry.validate_entry` now rejects empty input, whitespace, control/non-ASCII characters, quotes and a Bearer prefix. It neither trims nor repairs input, guesses a provider key length, nor logs key content or length. A printable partial, incorrect or revoked key still cannot be authenticated offline.
- `runners/broker.ProviderHTTPError` retains HTTP status, a locally classified error category, an integer provider error code when present, and at most 500 characters of sanitized JSON `error.message`. Exact credential matches, Bearer values, key-like strings and long opaque tokens are redacted before truncation; control characters are removed. Raw bodies, headers and arbitrary provider metadata are discarded. Non-JSON/malformed error bodies receive a fixed message. Oversized responses receive a fixed size-limit diagnostic.
- The preflight driver and `Broker.settle` persist those structured diagnostics. Errors never become successful content. Unknown usage keeps its reservation and stops execution. This does not change routing, request payloads, timeouts, recursion or retry behavior. Transport failures without an HTTP response still retain their exception type; they do not invent an HTTP status. No generalized provider logging or retry framework was added.

Four new targeted offline test methods passed, including eight HTTP error statuses, non-JSON/oversized responses, a successful-response control, redaction, Windows console behavior, driver stop-before-second-request and broker non-delivery. Socket creation was forbidden, and HTTPS was replaced only by explicit mocks. Existing completed suites were not rerun. See [test evidence](results/provider-diagnostics-check.json).

All files under `results/provider-preflight/`, including the original journal, locks, handoff receipts and outcome, remain byte-for-byte unchanged. The original ticket remains `usage_unknown`, with **$0.448448** reserved. Neither zero observed account activity nor the mock results were written into that ledger as a known zero charge. The 90 protected files remain unchanged.

## Retry blockers and smallest next steps

1. Review and explicitly reconcile the original unknown exposure using adequate account/billing evidence, preserving the original journal and an auditable separate reconciliation record. No reconciliation or reservation release was performed here. Under the current $0.50 combined ceiling, only **$0.051552** remains available; another GPT-5 attempt requires **$0.448448**, so it cannot be admitted within that envelope while the original reservation remains unresolved.
2. Prepare a separately reviewed retry record and authorization tied to the updated source hashes, with exposure carried forward. Existing journal/entry locks deliberately block replay, and the old authorization hashes no longer match the modified implementation. Do not delete locks, overwrite evidence or reset the ledger to bypass these checks. A narrow reviewed retry entrypoint/record is still needed after accounting disposition; it was not introduced in this diagnostic-only task.
3. Obtain new explicit approval for the exact request sequence, remaining combined ceiling and a fresh local masked credential handoff. Do not reuse the stopped session's approval or automatically dispatch GPT-5-nano. The live gate remains false.

The diagnostic change is ready for review, but a live retry is **not yet execution-ready**. No API requests, credential access, `.env` reads, accounting resets, official RLM modifications, RootCheck implementation, commits or pushes occurred. The nine-run pilot remains disabled and retains its separate preflight, accounting and authorization prerequisites.
