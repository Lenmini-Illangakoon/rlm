# Provider preflight: final saved-response reassessment

**PASSED for provider routing, literal completion, corroborated GPT-5 billing and bounded reported usage, with a retained GPT-5 reasoning-telemetry caveat.** Neither a full RLM pilot nor universal correctness of provider token-detail telemetry is established.

This stage made exactly one authorized read-only generation lookup and one authorized GPT-5-nano inference request. GPT-5 inference was not repeated. There were no retries or additional authenticated API calls. Credentials remained in the parent process and were not logged or injected into the worker environment.

| Evidence | GPT-5 | GPT-5-nano |
| --- | --- | --- |
| HTTP status / answer | 200 / `323` | 200 / `323` |
| Actual selected provider | OpenAI, routing attempt 1 | OpenAI, routing attempt 1 |
| Requested alias | `openai/gpt-5` | `openai/gpt-5-nano` |
| Resolved endpoint | `openai/gpt-5-2025-08-07` | `openai/gpt-5-nano-2025-08-07` |
| Native prompt / completion | 19 / 32 | 19 / 91 |
| Reported reasoning detail | 94, inconsistent with completion count | 64, within completion count |
| Cached tokens / BYOK | 0 / false | 0 / false |
| Reported charge | $0.00034375, corroborated by generation lookup | $0.00003735, exact response/rate reconciliation |
| Saved-response verdict | Accepted with telemetry caveat, revision 2 | Passed, revision 3 |

Known successful inference charges sum to **$0.00038110**. The original failed attempt's unresolved **$0.448448** reservation remains held. Combined ledger exposure is **$0.44882910**, leaving **$0.55117090** under the authorized $1.00 ceiling. No reservation was released based on the user's earlier zero-activity account observation.

## Verification changes and preserved evidence

[Revision 2](PREFLIGHT_VERIFICATION_REVISION_2.md) accepts the explicitly approved GPT-5 snapshot, preserves all usage fields, corroborates the generation's bill, and bounds the conflicting output details conservatively without charging reasoning twice. The lookup repeated rather than explained the 94/32 discrepancy. The accepted record therefore retains `reasoning_detail_conflict: true`; this is not evidence that the two fields share a consistent counting basis. The bill matches 19 input and 32 output tokens at the reviewed rates. A conservative additive count of 126 is below the 32,768 cap. No genuine reported budget overrun was observed or ignored.

Revision 3 (`preflight-snapshot-billing-review-3`) extends the same exact snapshot-name treatment to the observed nano endpoint `openai/gpt-5-nano-2025-08-07`. The request and returned top-level alias remain `openai/gpt-5-nano`, one selected endpoint must be OpenAI, and no arbitrary date, provider or model family is accepted. The [OpenRouter nano page](https://openrouter.ai/openai/gpt-5-nano) records its August 7, 2025 release; the saved response records the exact selected endpoint. The change is a local verification mapping, not a request substitution. The original nano journal still records the initial `selected_route` rejection; a separate reassessment passes all remaining gates without another inference or metadata lookup.

- [Original GPT-5 response and ledger](results/provider-preflight/live-attempt-two.json), unchanged.
- [One generation lookup, full returned metadata](results/provider-preflight/gpt5-generation-lookup.json).
- [GPT-5 reassessment](results/provider-preflight/gpt5-reassessment-v2.json).
- [Nano response and carried ledger](results/provider-preflight/live-nano-followup.json), unchanged after dispatch.
- [Nano reassessment](results/provider-preflight/nano-reassessment-v3.json).
- [Final outcome and integrity evidence](results/provider-preflight/final-reassessment-outcome.json).

Only seven new revision-2 checks and three new nano snapshot checks ran. They cover the saved GPT-5 acceptance, missing/wrong metadata, changed billing, unknown snapshot, conservative token-bound rejection, nano-only carry-forward, and nano acceptance/rejection of other snapshots. Previously completed suites were not repeated.

## Minimum pilot prerequisites, tied to the current code

1. **General input bound:** `literal_input_bound` deliberately accepts only the 17-by-19 probe. Supply a reviewed host bound for the actual text message lists produced by official RLM, including framing, that rejects anything beyond the frozen 64,000-token cap. Do not reuse the literal-only function or assert a full-cap bound for arbitrary messages. This remains unimplemented.
2. **Campaign identity and exposure:** `Pilot.__init__` currently hashes config, limits, rates, synthetic status and bound revision; it does not include provider routing policy or resolved-endpoint verification. Add those identities and import the latest cumulative ledger exactly once, retaining the original reservation and both known charges against the $20 campaign ceiling. `Pilot.run_next` currently blocks on *any* reserved ticket, so merely importing this ledger will block. Before activation, explicitly authorize either reconciliation of that old ticket or a narrowly reviewed treatment of prior stopped preflight exposure that still counts it against budget. Do not remove the reservation or disable interruption protection generally. The current authorization increased preflight exposure only; it did not approve this pilot gate change.
3. **Telemetry policy for the pilot:** retain native billed counts and raw detail fields, never double-count reasoning costs, and enforce input/output/cost bounds. Carry the documented GPT-5 detail caveat into the run report. Decide the minimal fail-stop treatment of future conflicting details without automatically issuing metadata lookups; the one lookup authorization is exhausted. Do not silently treat the saved-response exception as universal validation of future responses.
4. **Separate pilot activation:** after those narrow host changes and focused delta checks, obtain explicit authorization to activate the existing one-run-at-a-time path. No need to rerun datasets, oracle generation, behavioral equivalence or Windows isolation suites unless a relevant boundary changes. Keep the nine-run order, $2/run and $20 campaign limits, round-one checkpoint and cumulative two-resource-censored-runs stop rule unchanged.

The official RLM source, experimental datasets, protocols and earlier evidence remain unchanged. No RootCheck implementation, pilot execution, commits or pushes occurred. Source live gates remain disabled. Future work can start with the host input-bound and campaign-policy deltas; another GPT-5 or nano probe is not needed merely to recheck the snapshot names.
