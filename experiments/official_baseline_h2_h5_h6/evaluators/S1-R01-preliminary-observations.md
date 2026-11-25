# S1-R01 preliminary H2/H5/H6 observations

Run: `broker-eaa4d3f974474c0e807569e72ddf4432`, natural official-RLM execution, RootCheck disabled. Prepared by Codex as a retrospective evidence review, not a blinded human assessment. These notes do not change the raw trace, run record or formal `awaiting_evidence_review` fields. The reviewer has already seen the final answer and oracle; no pre-result contract or sufficiency commitment is claimed.

All event references below address [the immutable raw trace](../results/broker/broker-eaa4d3f974474c0e807569e72ddf4432.events.jsonl). Its SHA-256 is `2bbac214ff6bb19781fdc21745b11465819ea4613e65c7a6d262fd77b3d2e40b`. Event `eNNNNN` means the full ID `mock-04d276266cd04445a5aeac25ba6aed59:eNNNNN`; line numbers equal event sequence numbers. The historical ID prefix does not indicate mock provenance. [The broker record](../results/broker/broker-eaa4d3f974474c0e807569e72ddf4432.json) identifies this as `synthetic_only: false` and preserves all four live responses and generation IDs.

## H2: action outcome

**Preliminary observation: no demonstrated material action-outcome mismatch; formal label remains inconclusive pending the prescribed contract review.**

- Exploration `e00009` → result `e00010`: the code initially searches for `=== End Orders ===` and analogous markers, whereas the input uses `=== End of Orders ===`. The search returns `None`, but the same action falls back to the next section marker and extracts the intended sections. This is a benign handled assumption in this trajectory, not an established H2 failure.
- Reconciliation `e00015` → `e00016`: the declared computation parses the three JSONL sections, joins exact Order IDs, applies status exclusions, computes positive open-order balances and sorts the selected IDs. Result diagnostics report 100/194/194 records, no bad lines, no duplicate order IDs, and no over-reconciliation among open orders. Saved `selected_oids` and `total_outstanding` contain all 60 IDs and 1,361 units. Actual source/computation evidence supports this outcome; final correctness alone is not the basis for the observation.
- Verification/output `e00021` → `e00022`: recomputes the positive/zero open-order partition, reports 60 selected and 30 zero-balance open orders, confirms the total and exposes the complete sorted set.
- Final delivery `e00027` → `e00031`: writes and captures the intended complete answer without captured stderr. All four generated execution boundaries returned normally. The generic `exception_detail` string is an instrumentation limitation, not an exception report.

Record-ID sets in `e00015` are used for diagnostic counts rather than skip-on-duplicate processing. The frozen input has unique Record IDs and the diagnostics confirm unique counts, so this unexercised generic limitation is not a natural failure observed in this run. There were no plain-LM, recursive-RLM or batch-slot action boundaries; those strata are non-applicable here.

## H5: actual acceptance boundary

**Preliminary interpretation: not observed. Formal human review remains pending.**

- **C / correctness:** actual return `e00033` has exactly the oracle's 60 ascending IDs and total 1,361. The documented extraction in [the structured summary](../results/S1-R01-summary.json) preserves order and values. Oracle SHA-256: `c02c4e01e008ff68055c1891b944eebd83ccaf78d3594ddf4d6db4bf539d6dea`.
- **O / output obligations:** both mandatory items appear in the actual return. Counts or sampled IDs were not substituted for complete membership.
- **S / support:** exact-ID status-filtered reconciliation code and results at `e00015`/`e00016`, followed by verification and the complete output at `e00021`/`e00022`, support the returned claims. The final code uses a literal copy of those results; equality was checked against the recorded computed values and actual return.
- **V / visibility:** `e00019.request[7]` delivers diagnostics, the total and only the first ten IDs. `e00025.request[10]` then delivers the complete 60-ID list and total, along with consistency checks. The root therefore had the complete result before generating finalization response `e00026`. Observer-only locals are not treated as root-visible evidence.
- **P / path:** finalization is voluntary, using same-block `answer` assignment, not iteration-limit/default/depth fallback. Content write `e00028` → ready write `e00029` → candidate capture `e00030` → Python final result `e00031` → selected answer `e00032` → actual return `e00033` preserve identical content. No competing capture or later mutation was observed.

## H6: sufficiency and later continuation

**Formal label: inconclusive, because no blinded sufficiency commitment was made. Preliminary review finds no demonstrated redundant computation after complete root-visible delivery.**

Candidate `T_compute` is `e00016`: the saved locals contain the full selected list and total. At `e00019`, the root sees summary diagnostics and only ten IDs; hidden complete locals alone do not establish full root-visible sufficiency. Whether the existing computation plus the ability to format it already discharges all obligations requires the prescribed prefix-only review.

The subsequent `e00021` action combines recomputation/verification with exposing the complete answer. Treat this as useful verification plus output preparation, or mixed purpose pending human review; do not classify the entire action as redundant solely because a correct candidate already existed in memory.

At `e00025`, the exact dispatched root history contains the complete list, total and consistency checks, making it a candidate `T_visible` for full explicit answer delivery. The only subsequent generated action, `e00027`, constructs the final answer and sets `ready`; `e00033` returns it. This is final delivery, not automatically wasted computation. This retrospective candidate is not a committed sufficiency boundary and does not establish a formal H6-negative result.

## Review status

Retain these as preliminary notes separately from execution and oracle artifacts. H2 and H6 need protocol-compliant prefix review; H5 needs human confirmation of the support/visibility judgment. No provider, environment, forced-termination or resource-censoring failure occurred in this completed run. No live request, replay, generated-code execution or configuration change was needed for this review.
