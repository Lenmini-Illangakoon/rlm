# S3-R02 preliminary H2/H5/H6 observations

Natural run `broker-6f457d2d60914ee6b68d8366892facfb`. These are retrospective Codex notes, not blinded human commitments or final labels. Formal assessments remain pending. Event `eNNNNN` means `mock-b961f9c21d024107a3a9d9a9e2dfdc51:eNNNNN` in [the raw trace](../results/broker/broker-6f457d2d60914ee6b68d8366892facfb.events.jsonl); line numbers equal event sequence numbers. The broker record is explicitly live despite the historical event-ID prefix. Evidence checksums are in [the summary](../results/S3-R02-summary.json).

## H2

**No material mismatch demonstrated; formal label inconclusive pending contract review.** Section exploration `e00009`/`e00010` correctly separates archived (4), current (320) and planned (4) records. Computation `e00015`/`e00016` parses 320 current rows with zero errors, filters 104 ACTIVE/APAC records, sorts integer IDs, and prints [3731, 4637] and 17300647. Finalization `e00021`/`e00025` returns those values normally. Every Python stderr is empty.

The generated code can catch/skip malformed values, but no skipped valid record or material loss is demonstrated in this frozen instance. The exploration prints archived IDs, yet later computation explicitly uses only `sections['Product Inventory']`; seeing distractors is not itself a scope failure. There are no plain-LM, genuine recursive-RLM or batch boundaries; those strata are non-applicable.

## H5

**Preliminarily not observed; human confirmation pending.** Actual return `e00027` contains both ascending IDs and product and matches the independent oracle. Support is the section-scoped filtering/sorting/arithmetic at `e00015`/`e00016`, not correctness alone. Exact root request **`e00019.request[-2]`** delivers the complete computed candidate, record counts and product before finalization.

Content write `e00022` → ready `e00023` → capture `e00024` → Python final result `e00025` → selection `e00026` → actual return `e00027` preserve identical text. The answer literals for the two IDs agree with computed values, and the product is formatted from the saved variable. This is voluntary iteration-3 submission, not a forced/default/depth fallback. No mandatory omission, unsupported selected result or necessary unobserved-and-unvalidated evidence is demonstrated.

## H6

**No redundant continuation demonstrated; formal label inconclusive without blinded prefix commitment.** Candidate `T_compute` is `e00016`, candidate `T_visible` is `e00019`. Full sufficiency/stability still needs the prescribed prefix-only review. After delivery the only action `e00021` formats and submits the answer. It performs no repeated search, parsing, ranking, verification delegation or task recomputation. This is final delivery, not automatically waste because a candidate already existed.

No provider/environment/resource failure occurred. An identified human reviewer must confirm contracts, support/visibility and prefix sufficiency/purpose under the unchanged rubric; no formal hypothesis absence is inferred merely from a correct final answer.
