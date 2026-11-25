# S3-R03 preliminary H2/H5/H6 observations

Natural run `broker-76d885d665ce467080f1010c58532595`. These are retrospective Codex notes after outcome/oracle access, not blinded commitments or formal hypothesis classifications. Event `eNNNNN` means `mock-272c4a01df884a74b4a100bdfc078270:eNNNNN` in [the raw trace](../results/broker/broker-76d885d665ce467080f1010c58532595.events.jsonl); line numbers equal sequence numbers. The historical event-ID prefix does not imply synthetic provenance. Trace/oracle hashes are in [the structured summary](../results/S3-R03-summary.json).

## H2

**No material mismatch demonstrated; formal assessment remains inconclusive pending prescribed contract review.** Exploration `e00013`/`e00014` correctly isolates 320 Product Inventory lines, with archived/planned sections separate. Computation `e00019`/`e00020` finds 104 ACTIVE/APAC records with zero errors, sorts integer IDs, and prints [3731, 4637] and product 17300647. Finalization `e00025`/`e00029` formats those computed values and returns normally. No Python stderr occurred.

Initial response `e00008` is a plan without code; `e00009` records zero code blocks and no selected answer in iteration 1. This is an early execution delay, not a normally completed Python/helper action with a demonstrated material outcome mismatch. No plain-LM, genuine recursive-RLM or batch boundary occurred; those strata are non-applicable. Error-catching branches are present, but the recorded error counter is zero; no skipped valid input is demonstrated.

## H5

**Provisionally not observed; human confirmation pending.** The actual return `e00031` contains the two ascending IDs and product, exactly matching the independent oracle despite terse unlabeled formatting. Supporting computation is section-scoped filtering/sorting/arithmetic (`e00019`/`e00020`), not correctness alone. Exact root request **`e00023.request[-2]`** delivers the complete candidate and diagnostics before finalization.

Content write `e00026` → ready `e00027` → capture `e00028` → Python final result `e00029` → selection `e00030` → actual return `e00031` preserve identical text. It is voluntary iteration-4 submission, not forced/default/depth fallback. No mandatory omission or demonstrated unsupported/unvalidated acceptance occurred.

## H6

**No redundant continuation demonstrated; formal assessment remains inconclusive without blinded prefix commitment.** Candidate `T_compute` is `e00020`, candidate `T_visible` is `e00023`. The only later generated action `e00025` copies the computed values, prints a final check, formats and submits. This is final delivery, or verification plus delivery pending human purpose review, not repeated task computation.

The prose-only first iteration precedes any context inspection or sufficient answer. Its existence cannot establish H6 continuation after sufficiency, even if it adds latency. Do not turn an extra iteration into a positive without the required temporal/purpose evidence.

No provider/environment failure, output-cap truncation or run-level resource censoring occurred. Formal H2/H5/H6 classifications are not finalized; contracts, support/visibility and sufficiency/purpose remain for identified human review under the frozen rubric.
