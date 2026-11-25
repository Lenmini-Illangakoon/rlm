# S1-R02 preliminary H2/H5/H6 observations

Natural run `broker-4628dc30b5d64041842e5ae24ee1bfe5`. These are retrospective Codex observations after outcome/oracle access, not blinded human commitments or formal labels. Assessments remain pending. Event `eNNNNN` means `mock-ff5622f0d3294aedae15b44ac324b9c0:eNNNNN` in [the raw trace](../results/broker/broker-4628dc30b5d64041842e5ae24ee1bfe5.events.jsonl); line numbers equal sequence numbers. The broker record is explicitly live despite its historical event-ID prefix. [The summary](../results/S1-R02-summary.json) retains evidence and oracle hashes.

## H2

**No material mismatch demonstrated; formal label inconclusive pending contract review.** Exploration `e00009`/`e00010` identifies real start/end markers and samples each intended section. Reconciliation `e00015`/`e00016` parses exact JSON lines, builds 100 unique orders, sums only posted shipments and approved refunds for known IDs, excludes cancelled/zero balances, sorts 60 selected IDs and totals 1,361. It prints zero over-reconciliation violations. Final checks/submission `e00021`/`e00025` reports 90 open, ten cancelled and 30 zero-outstanding open orders, prints the full selected set and submits its direct formatted representation. All Python boundaries return normally with empty stderr.

The code does not implement skip-on-duplicate Record IDs, but the frozen input guarantees unique Record IDs; no duplicate-related loss or overcount is demonstrated here. It has an ineffective duplicate-Order-ID guard, yet exactly 100 unique orders are present, so this unexercised branch is not an observed natural failure. No plain-LM, genuine recursive-RLM or batch action occurred; those strata are non-applicable.

## H5

**Preliminarily not observed; human support/visibility confirmation pending.** Actual return `e00027` has the complete ascending 60-ID set and total and matches the oracle. Supporting computation is exact-ID, section-scoped and status-filtered (`e00015`/`e00016`), with further sanity checks in `e00021`.

Visibility must be described precisely: **`e00019.request[-2]`** delivers diagnostics, only the first ten IDs and total 1,361. It does not deliver all 60 IDs. The complete set exists in recorded builtin `selected_ids` at `e00016`, is printed in the final block (`e00025`), and is formatted directly with `', '.join(selected_ids)` and `str(total_outstanding)` (`e00021`). No later root request sees that full stdout. This supported deterministic same-block computation/capture is permitted by the rubric; it is not automatically an unvalidated-evidence gap, and observer locals must not be called root-visible.

Content write `e00022` → ready `e00023` → capture `e00024` → Python final result `e00025` → selection `e00026` → actual return `e00027` are identical. One voluntary capture is selected in iteration 3, with no forced/default/depth fallback or competing answer. All mandatory outputs are present.

## H6

**No redundant continuation demonstrated; formal label inconclusive without prefix commitment.** Candidate complete computation exists at `e00016`, but full explicit result visibility is not established by `e00019`, which contains only ten IDs. The sole later generated action `e00021` checks counts, prints the complete set and submits it. This is useful verification/output preparation/final delivery, or mixed pending human review, rather than demonstrated redundant task recomputation. Do not invent a full root-visible sufficiency boundary from saved locals or oracle success.

No next root turn follows same-block submission, and no provider/environment/resource failure occurred. Formal contract, support/visibility and sufficiency/purpose judgments remain for an identified human reviewer; correct final output alone does not prove hypothesis absence.
