# Minimum OpenRouter preflight review

**Implementation update, 2026-11-25:** the approved minimum fixes are now complete and tested offline. See [the current authorization handoff](TWO_REQUEST_PREFLIGHT_AUTHORIZATION.md): **READY FOR TWO-REQUEST LIVE PREFLIGHT AUTHORIZATION**, with live execution disabled. The review findings and proposal below are retained as the historical basis; the response defect, host routing enforcement and narrow driver implementation blockers have been resolved. General pilot bounds and live empirical verification remain outstanding.

Review date: 2026-11-24. Revision: `openrouter-preflight-proposal-1`.
Finalized: 2026-11-25, retaining the original proposal bodies and arithmetic.
**Prepared for review; not executable approval.** Public documentation was consulted; no credentials, account settings or API endpoints were accessed. Runtime code, pilot configuration, official source and completed test evidence remain unchanged. This supplements [LIVE_PREFLIGHT.md](LIVE_PREFLIGHT.md); the historical offline-ready decision does not certify the provider facts below through live execution.

## Verified public configuration

| Requested model | Proposed upstream provider | Input / million | Output / million | Cache read / million | Published context |
| --- | --- | ---: | ---: | ---: | ---: |
| `openai/gpt-5` | OpenAI | $1.25 | $10.00 | $0.125 | 400K |
| `openai/gpt-5-nano` | OpenAI | $0.05 | $0.40 | $0.005 | 400K |

These are the published OpenAI endpoint rates, not weighted averages. Both model pages also list Azure; Nano additionally lists OpenAI Flex. Availability to this account and the resolved model version remain untested. Keep the approved identifiers and record the returned model/fingerprint; do not silently substitute a dated identifier or another model. Sources: [GPT-5](https://openrouter.ai/openai/gpt-5), [GPT-5 Nano](https://openrouter.ai/openai/gpt-5-nano).

Propose `provider.only: ["openai"]`, `allow_fallbacks: false`, `require_parameters: true`, and per-model `max_price` filters matching the table. A base slug permits eligible endpoints of that provider; it is not a regional or immutable endpoint pin. The documentation says base slugs do not themselves opt into service tiers. Record the actual selected route. These host routing restrictions require an explicit versioned configuration decision before pilot collection. They do not alter RLM's root/secondary selection or recursion. [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection).

The API documents `max_completion_tokens`. The current broker correctly preserves the pinned client's `max_tokens` normalization. Its omission of `stream` uses non-streaming behavior. Keep temperature, seed, reasoning effort, tools, plugins, model fallbacks and service tier unspecified. No new sampling settings are proposed. Account-level overrides/BYOK remain uninspected; the eventual operator must confirm ordinary OpenRouter credit billing and no request-altering preset before dispatch. [Chat request reference](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion).

Reasoning consumes the same completion budget as visible output and is billed. Use `usage.completion_tokens` once; do not add `completion_tokens_details.reasoning_tokens` again. A reasoning-only response may be empty with `finish_reason: "length"`; that is not a successful probe. Omitted reasoning configuration is preserved, not asserted to be a known fixed effort. [Reasoning accounting](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens).

Usage is documented as automatic on both APIs; `usage.include` is deprecated, so its absence is not a broker defect. Expect native prompt/completion counts, optional detail breakdowns, and `usage.cost`. Preserve the raw response. Cost is the account charge; upstream cost is a distinct field. Do not accept BYOK for this proposal because another provider bill would escape the intended account-only accounting. [Usage accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting). Credits are USD-denominated; credit-purchase fees and taxes are separate from inference charges. No purchase/top-up is authorized. [Credit units](https://openrouter.ai/support/), [pricing and fees](https://openrouter.ai/pricing).

## Exact proposed requests and exposure

[provider-preflight-proposal.json](provider-preflight-proposal.json) contains the exact two JSON bodies and non-secret headers. It is inert review data, not a runner configuration. Send at most two sequential POSTs to `https://openrouter.ai/api/v1/chat/completions`: GPT-5 first, Nano only after the first request passes all checks and its usage is reconciled. The single user message is:

> Compute 17 * 19. Reply with only the integer.

Expected visible answer: `323`. Each body uses the existing **32,768** completion cap, plus the proposed provider restrictions. This tests acceptance of the actual pilot cap instead of substituting a smaller one. Add `X-OpenRouter-Metadata: enabled` for routing evidence. The authorization header is supplied only after separate credential approval and is never included in saved evidence. This header is documented in the [chat reference](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion).

The minimum probe directly exercises the parent request builder, ledger and HTTP transport. It does not launch a model-driven RLM loop, which could create extra calls. Official RLM integration/routing already has preserved offline evidence. These two calls validate provider transport and accounting only; they do not replace a pilot run or demonstrate live end-to-end RLM equivalence.

**Proposed total inference spending authorization: $0.50, maximum two attempts, no retries/replacements.** Reserve the entire approved 64,000-input allowance for each literal request, and the entire 32,768-completion allowance, with the existing 10% margin:

| Model | Unmargined maximum at stated bounds/rates | Reservation |
| --- | ---: | ---: |
| GPT-5 | $0.407680 | $0.44844800 |
| GPT-5 Nano | $0.01630720 | $0.017937920 |
| Combined | $0.42398720 | **$0.466385920** |

Formula: `(input_bound * input_rate + completion_cap * output_rate) / 1,000,000 * 1.10`. Reserve uncached input prices. Reconcile using the greater of reported charge and uncached rate-derived cost, as the current ledger does. This is conservative exposure, not necessarily the actual bill. The expected charge for a short answer is much lower, but unknown reasoning length prevents an exact forecast.

The literal-only bound method is proposed as `literal-message-full-cap-v1`: reject any messages other than the exact single message in the proposal, then reserve 64,000 tokens. That provides substantial framing headroom for this tiny ASCII prompt; it is an engineering assumption requiring review, not a provider-certified token count. It must never be reused as a bound for arbitrary RLM messages. There is no request-side input-token limit in this body. Reported prompt usage is an after-the-fact check, not pre-dispatch enforcement. The 8 MiB mailbox limit and `len(text)/4` are not conservative token bounds.

For the actual pilot, a reviewed host bound covering full messages, roles, framing and growing histories is still required. UTF-8 byte counting may bound text under a verified byte-level tokenizer, but does not alone certify provider framing. Reject over-bound requests rather than truncate, compact or change prompts. The approved combined allowance of 96,768 tokens is below the published 400K context, but this does not prove acceptance or enforcement of the output cap. A tiny response verifies cap acceptance, not worst-case enforcement.

Retain preflight records separately, with actual/unknown exposure charged against the existing $20 total envelope; do not reset campaign exposure or count these as any of the nine runs. The $2/run pilot limit is unchanged. The $0.50 ceiling is conditional on the provider honoring rates/caps; post-response overrun detection cannot undo a bill. `max_price` filters rates, not total spend. Any unresolved first attempt prevents the second.

## Broker audit and minimum remaining work

| Code boundary | Finding | Smallest required action |
| --- | --- | --- |
| `broker.provider_body` | Only emits model/messages/completion cap. Defaults therefore permit provider fallback; no price filter is sent. | Add the reviewed host-owned provider policy to the final body before journaling/dispatch. Worker requests must not supply it. |
| `OpenRouterHTTP` | One local HTTPS attempt, no application retry or redirect following; no metadata opt-in header. | Add the fixed routing-metadata header. Preserve credential injection and no retry. |
| `Broker.settle` | Raw response is saved, but actual model/provider, BYOK and finish/error fields are not checked. A partial error with string content and valid usage can be delivered as success. | Reconcile known usage, then reject provider-error envelopes/choices before delivery. Check the proposed route and response acceptance in the preflight driver. Preserve normal official handling of non-error length-limited text in pilot runs. |
| `Broker.settle` / `Ledger` | Completion total is counted once; absent live cost/tokens retains exposure and stops. Uncached price reconciliation is conservative. | Keep this behavior. Preflight additionally checks total/detail consistency and records reasoning/cache counts. No new usage flag is needed. |
| `Broker.poll` / live input bounds | The only supplied bound in the mock entry point is synthetic `100`; the general live bound is missing. | For the two probes only, enforce exact literal messages and reserve the full input cap. Resolve the general bound before any pilot approval. |
| `Pilot` policy fingerprint | Rates/limits/config/bound revision are covered, but a future transport routing policy/header/timeout revision is not currently part of the identity. | Include the reviewed host policy revision before creating live campaign state. Keep old synthetic state separate. |
| Evidence timing | `dispatched_at` and the worker admission event are emitted before the HTTP task actually sends. Non-200 bodies/IDs are discarded. | Treat these as admitted/submitted attempts, not proof of upstream invocation. Keep unknown exposure; use returned routing metadata for successful probes. Do not claim internal provider retries are observable. |
| Live entry points | `Pilot.run_next` refuses non-synthetic transport; CLI remains disabled. No bounded two-probe entry point exists. | After offline fixes and review, prepare only a narrow two-request driver using existing components; no live pilot gate release is needed for these probes. Separate approval is mandatory before supplying credentials or dispatching it. |

These are review findings; no runtime fix or gate change was made in this documentation-only phase. The smallest safe alternative to a general preflight framework is the literal two-request driver just described. At implementation time, only targeted fake-HTTP checks for the exact outgoing policy, partial-error rejection and literal/budget gating are needed; no benchmark, isolation or full-suite rerun is warranted by host-only changes.

The response-handling finding is now reproduced, not merely inferred: [targeted offline evidence](results/provider-response-review.json) exercises the actual `Broker.settle` and `Ledger` with completed futures. Both a top-level provider error and a choice-level error, each with `finish_reason: "error"`, partial text and valid usage/cost, were delivered as ordinary content with no stop reason. A healthy response control was delivered correctly. Network constructors were blocked; only filesystem publication/checkpoint operations were mocked. These two erroneous deliveries confirm an unresolved defect; they are not passing safety tests. No runtime fix was applied in this review task.

The [saved arithmetic/configuration validation](results/provider-preflight-review-validation.json) had already completed before interruption: exact Decimal reservations and admission through the existing ledger passed. It was retained without rerunning the calculation. The proposal JSON remains byte-identical. [Final review integrity](results/provider-preflight-review-final.json) records the final document/manifest checks and preserved implementation/evidence. Prior full, isolation and behavioral suites were not repeated.

OpenRouter documents errors inside HTTP 200 bodies, including partial content, so success cannot be inferred solely from status and string content. [Error semantics](https://openrouter.ai/docs/api_reference/errors-and-debugging). It documents failed fallback attempts as uncharged for model tokens, but that does not make upstream attempts identical to local broker tickets. [Billing policy](https://openrouter.ai/pricing).

## Timeout semantics and evidence required

Keep the current per-attempt `min(300 seconds, remaining run time)` and 900-second overall deadline. No deliberate timeout probe or additional request is proposed. The socket timer closes active sockets and checks expiry after connect. It cannot forcibly bound Windows DNS resolution while no socket exists, and `Broker.close()` waits for threads. Thus 300 seconds is not a proven hard process-return bound. For this supervised two-call preflight, stop on a timeout, retain the reservation, and require review; do not add a process supervisor solely to claim stronger timeout guarantees.

Non-streaming cancellation does **not** stop remote generation/billing according to [OpenRouter's cancellation documentation](https://openrouter.ai/docs/api_reference/streaming). Preserve the full unknown reservation even after killing a local worker. No automatic generation-lookup call, retry, fallback or cap increase is authorized. A normal successful probe cannot demonstrate cancellation behavior or prove absence of undocumented upstream internal retries.

For each successful probe retain the exact sanitized request and policy revision/hash; admission ticket/reservation; send/receive timing and HTTP status; generation ID; requested/returned model and fingerprint; provider/routing metadata including attempt count and selected endpoint; service tier and BYOK status; full usage/cost/details; finish reason and answer; reconciled ledger snapshot. Require:

1. One local attempt; returned routing metadata indicates one route attempt with OpenAI selected. Any missing or ambiguous routing evidence stops review without a replacement call.
2. No error envelope/choice, one textual answer equal to `323` after surrounding-whitespace stripping, and `finish_reason: "stop"`. A length/refusal/error outcome is inconclusive, not a baseline result.
3. Integer nonnegative prompt/completion counts within 64,000/32,768; total equals their sum; reasoning is a subset of completion usage and cached tokens a subset of prompt usage. Record a missing reasoning breakdown as unverified. Zero reasoning is valid but does not empirically verify nonzero reasoning billing; do not force extra calls.
4. Finite nonnegative `usage.cost`, ordinary credit billing (`is_byok: false`), no unexpected tools/fees/route, and reported charge consistent with observed uncached/cached/reasoning-inclusive usage at the reviewed rates, allowing documented precision. If details cannot explain a discrepancy, stop for review rather than loosen a tolerance.
5. Reconciliation and durable evidence complete before admitting the second call; combined actual plus unresolved exposure remains within $0.50 and is carried into total campaign accounting.

The two-call plan is ready for review, **not ready for dispatch**: the small host-policy/error-check/driver changes above, the limited input-bound assumption and separate credential/request approval remain outstanding. General live input bounds and a final reviewed campaign identity also block the nine-run pilot. Preserve its sequence, round-one checkpoint, cumulative two-censored-runs round-end stop rule, existing budgets and all prior evidence. No protocol change or result pooling is implicit in approving a provider probe.
