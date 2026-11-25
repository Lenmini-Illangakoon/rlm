# S1-R03 billing reconciliation — S2-R03 ready

The single authorized generation-metadata GET returned HTTP 200. No inference request, retry or additional lookup was sent. The metadata establishes a sufficiently corroborated association with S1-R03 request `0a0a4e4a7fa14fa9bbe7c378e06bc041`, ticket `attempt-00037`.

## Identity and usage

- Generation: `gen-1795620768-3317xhBT42UcDMqARGgi`.
- Provider request: `req-1795620768-xEe8X0zbl8rFbW1txRtN`.
- Created: `2026-11-25T15:32:48.416Z` / `21:02:48.416` Sri Lanka time, 2.903377 seconds after the saved dispatch.
- The paired preceding generation, request sequence and screenshot usage agree. There is no direct generation-ID linkage in the failed local HTTP response; association uses these independent matching observations.
- One recorded upstream response: OpenAI, HTTP 200, `openai/gpt-5-2025-08-07`, non-BYOK, default tier, no preset, finish `stop` / native `completed`, not cancelled.
- Native input: 5,914; native completion: 1,829; reasoning detail: 960; cached input: 1,664. Reasoning is included in native completion and is not billed twice. Both native counts remain within the reserved bounds (24,253 / 32,768).
- Generic metadata counts (5,281 / 1,765) are preserved separately and are not substituted for native billing counts.

## Exact accounting

`total_cost` and `usage` both equal **$0.02381050**. Frozen-rate verification is exact:

`((5914 - 1664) * 1.25 + 1664 * 0.125 + 1829 * 10) / 1000000 = 0.02381050`.

The cache discount is $0.001872. Raw `upstream_inference_cost` is 0; it is preserved, not interpreted as a free request. Account billing is established by the matching total-cost/usage fields and the exact rate calculation.

The existing ledger reconciled the $0.3937958750 reservation to **$0.02568250**, the larger of exact billed cost and uncached native-token cost. It did not add the debit on top of the reservation. Protected exposure decreased by $0.3681133750.

| Item | USD |
|---|---:|
| Campaign protected exposure before | 1.4286775250 |
| Campaign protected exposure after | **1.06056415** |
| Remaining headroom against $20 | **18.93943585** |
| Original unresolved preflight reservation, unchanged | **0.44844800** |
| S1-R03 total actual reported charge, both requests | 0.04080800 |
| S1-R03 total conservative debit | 0.04412000 |

## Preservation and readiness

S1-R03 remains **operationally interrupted**, with no actual returned final answer. Metadata confirms provider completion but does not recover the missing model response, execute its code, or make the run successful. Its historical `usage_unknown` stop reason remains in the run record; only the ticket's accounting state is now reconciled. The original journal, raw trace, summaries and preliminary H2/H5/H6 observations remain unchanged.

Post-write offline checks passed: unchanged frozen policy; unchanged original journal hash; unchanged other tickets, including the exact carried preflight ticket; unchanged eight run records and historical stop reasons; exact ledger totals; successful campaign reopen; S2-R03 next in frozen order; cleanup and unresolved-exposure gates clear. An initial verification compared equivalent Decimal strings with different trailing-zero formatting and stopped before any campaign write; comparison was corrected to numeric equality. No source change or network retry was needed.

**READY FOR S2-R03 EXECUTION, subject to separate execution authorization.** No new inference is authorized by this reconciliation turn. The $2/run and $20 campaign ceilings and all stopping rules remain unchanged. No new framework code, official-source/configuration changes, tests suites, commits or pushes were made.

Evidence in this directory:

- `generation-response.raw.json`: exact received metadata body.
- `generation-lookup.json`: single-GET receipt, timestamps, HTTP status and parsed metadata.
- `lookup-once.lock`: retained one-use guard.
- `campaign-before.json`: byte-preserved prior campaign.
- `reconciliation.json`: separate before/after accounting record, verification and source hashes.

The earlier nine-run status JSON and S1-R03 summary are retained as historical snapshots before this reconciliation. This report and the current campaign ledger supersede their unresolved-billing figures only; execution and hypothesis findings remain unchanged.
