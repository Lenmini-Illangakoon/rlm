# Separately authorized provider preflight: attempt two

**FAILED verification; stopped after GPT-5.** GPT-5-nano was not dispatched. There was no HTTP error: the provider returned HTTP **200**, answer `323`, finish reason `stop`. The exact local rejection label was **`selected_route`**.

The user authorized the existing project `.env` credential and a $1.00 combined preflight ceiling including the previous unresolved $0.448448. The new entrypoint reads only the named credential into the parent adapter, without environment injection or credential output. It uses an exclusive retained entry lock and a separate live journal. The driver's existing ledger restore carries the original unresolved ticket into the new budget. The previous live journal and all its evidence remain unchanged. The live authorization gate was enabled only in the entrypoint process and cleared on exit; its source default remains false. No pilot activation occurred.

## Actual evidence

| Field | Provider response / recorded result |
| --- | --- |
| Fresh submitted requests | 1, GPT-5 only |
| HTTP status | 200 |
| Generation ID | `gen-1795585741-7mec5Vzt2WQV4Xtu5Z43` |
| Requested / top-level returned model | `openai/gpt-5` |
| Provider / selected provider | OpenAI / OpenAI |
| Selected endpoint model | `openai/gpt-5-2025-08-07` |
| Routing attempt | 1 |
| BYOK | false |
| Answer | `323` |
| Prompt / completion / total tokens | 19 / 32 / 51 |
| Reported reasoning tokens | 94 |
| Cached tokens | 0 |
| Response-reported inference cost | $0.00034375 |
| Previous unresolved reservation | $0.448448, unchanged |
| Combined ledger exposure | $0.44879175 |
| Combined authorized ceiling | $1.00 |

The selected endpoint's dated model name differs from the exact alias expected by the existing `selected_route` gate. This is a response-metadata mismatch; it does not establish that OpenRouter routed to a different model family. No alias acceptance or model substitution was introduced after observing the failure.

Separately, 94 reasoning tokens exceed the reported 32 completion tokens. The existing assumption requires reasoning tokens to be included within completion tokens. That check was not reached because route validation failed first. The reported charge equals `(19 * 1.25 + 32 * 10) / 1,000,000 = $0.00034375`, and matches the response's upstream cost breakdown. The journal reconciled that reported cost before validation, as designed; this is not an independent account/billing reconciliation and does not resolve the reasoning-token semantics. Do not silently add reasoning tokens again or change the accounting assumption.

The request preserved OpenAI-only routing, no fallbacks, required parameter support, price ceilings, exact literal input, 32,768 completion cap, conservative 64,000 input bound, existing timeout and no-retry semantics. Maximum old exposure plus both fresh reservations was $0.91483392, within the new ceiling.

## Evidence and minimum remaining steps

- [Separate live journal with complete provider response and ledger](results/provider-preflight/live-attempt-two.json).
- [Authorization and implementation hashes](results/provider-preflight/attempt-two-authorization.json).
- [Only new offline delta check](results/attempt-two-delta-check.json): synthetic `.env` parsing and carried-reservation admission passed; completed tests were not repeated.
- [Final preservation and outcome record](results/provider-preflight/attempt-two-outcome.json).

Before another live request, review the exact dated endpoint identity and the completion/reasoning billing semantics against this saved response. Any accepted alias mapping or accounting change needs a narrow documented protocol adjustment and a focused offline fixture check. Obtain fresh explicit live authorization after that review; this attempt is stopped, not resumable. No further requests or provider lookups were made after the failure.

The nine-run pilot still requires a successful reviewed provider preflight for both configured models, a general conservative input bound, campaign policy identity and carried-forward exposure, and separate pilot authorization. Existing datasets, H2/H5/H6 protocols, order, budgets, round-one checkpoint and censoring stop rule remain unchanged. No official RLM changes, RootCheck implementation, commits or pushes occurred.
