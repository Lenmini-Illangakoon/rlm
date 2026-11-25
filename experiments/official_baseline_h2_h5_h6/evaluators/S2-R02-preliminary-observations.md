# S2-R02 preliminary H2/H5/H6 observations

Natural run `broker-0c0113ea621747e2ace2fa3de8d4bbcb`. These are Codex's retrospective notes after observing the outcome/oracle, not blinded human commitments or final labels. The formal run assessment remains pending.

Event `eNNNNN` means `mock-dd686059d6544afbba4a6d929c11f1c9:eNNNNN` in [the immutable raw trace](../results/broker/broker-0c0113ea621747e2ace2fa3de8d4bbcb.events.jsonl); sequence numbers equal line numbers. Despite the historical ID prefix, the broker record is `synthetic_only: false`. Trace and oracle hashes are in [the structured summary](../results/S2-R02-summary.json).

## H2

**No material mismatch demonstrated; formal label inconclusive pending prescribed contract review.** Exploration `e00009`/`e00010`, section parsing `e00015`/`e00016`, joining/filtering/ranking `e00021`/`e00022`, payload preparation `e00027`/`e00028` and verification/finalization `e00033`/`e00037` all return normally with empty stderr. Four sections contain 160 parsed records each, their exact-ID intersection is 160 with no missing-note lists, and 100 eligible rows are ranked with the requested numeric tie-break. Output preparation includes the total and all source references.

The exploratory heuristic counts literal `Shipment ID` mentions as zero (`e00010`), while the actual records use `SH-xxxxx`; this is not used as a shipment count or final claim. Later parsing uses the actual format correctly. Do not promote this handled exploratory mismatch into a material failure. No plain-LM, genuine recursive-RLM or batch action occurred; those strata are non-applicable. The initial delegation plan at `e00008` is not an executed helper call.

## H5

**Preliminarily not observed; human confirmation pending.** Correctness and output coverage are exact for three ordered shipments, quantities, twelve source IDs and total (actual return `e00039`). Support comes from section parsing and join/filter/rank computation, not oracle feedback. At `e00025` the root receives the top-five ranking, but not all selected source IDs or total. At **`e00031.request[-2]`** it receives the complete top-three payload and total printed by `e00028`, before finalization. Hidden locals are not treated as delivered evidence.

Content write `e00034` → ready `e00035` → capture `e00036` → Python final result `e00037` → selection `e00038` → actual return `e00039` preserve identical complete text. This is voluntary submission in iteration 5, not forced/default/depth fallback. The final block prints selected eligibility fields and then submits in the same block; an extra root turn is not required merely to repeat that deterministic verification.

## H6

**No redundant continuation demonstrated; formal label inconclusive without blinded prefix review.** Candidate full-output `T_compute` is `e00028`, with `T_visible` at `e00031`. The earlier `e00022` has a ranking and observer locals but not every requested output in delivered stdout; do not assume full root-visible sufficiency there.

After complete delivery, the only generated action `e00033` verifies selected eligibility fields and formats/submits the final answer. Its purpose is useful verification plus final delivery, or mixed pending human review. No additional full ranking or delegation follows. Preparing and exposing the total/source payload at `e00027` is needed output preparation, not automatically redundant because ranking already existed. No formal H6 positive is inferred from the run's five iterations.

No provider/environment failure or resource censoring occurred. Formal H2 contracts, H5 support/visibility and H6 prefix sufficiency/purpose still require an identified human reviewer under the unchanged rubric.
