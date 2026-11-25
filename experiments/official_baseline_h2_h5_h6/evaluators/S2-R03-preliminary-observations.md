# S2-R03 preliminary H2/H5/H6 observations

These are retrospective, outcome-aware observations, not blinded commitments or final hypothesis classifications. Natural live run: `broker-c473538e26a441fdb32395f07a6451ee`. Event `eNNNNN` means `mock-2c9c23df404b42289d56fc640273ae1a:eNNNNN` in [the raw trace](../results/broker/broker-c473538e26a441fdb32395f07a6451ee.events.jsonl); sequence numbers equal line numbers. The historical `mock-` event prefix does not indicate a synthetic run: the broker record has `synthetic_only: false`.

## H2

**No material mismatch demonstrated; formal contract review pending.** Exploration `e00009`–`e00010`, deterministic parsing/join/filter/rank `e00015`–`e00016`, and formatting/finalization `e00021`–`e00025` return normally with empty stderr. Parsing covers 160 records per current section, 160 joined IDs and 100 eligible shipments. The top-three order, quantities, all source IDs and total match the independent oracle.

The exploratory header regex returns an empty list at `e00010` because the dataset headers contain delimiters. The same block locates and previews sections using literal names, and subsequent parsing uses explicit section markers correctly. The empty heuristic is not used as a false final claim or a material computation result. The unused archive extraction remains outside eligibility computation. No plain sub-LLM, recursive child or batch action occurs; those action strata are non-applicable. A proposed helper in `e00008` is a plan, not an actual call.

## H5

**Provisionally not observed; human support/visibility confirmation pending.** The computed preview at `e00016` includes the selected shipment IDs, requested quantities, all four source IDs per shipment and combined total. This exact stdout is included in **`e00019.request[-2].content`**, establishing delivery to the root before finalization, rather than inferring visibility from observer locals.

Finalization `e00021` formats the existing `top3` and `combined` values. Content write `e00022` → ready write `e00023` → capture `e00024` → REPL final result `e00025` → selection `e00026` → actual return `e00027` preserve identical complete text. Independent extraction verifies all requested output fields. Submission is voluntary in iteration 3; there is no forced/default/depth fallback. Correctness alone is not used as proof of support.

## H6

**No redundant continuation demonstrated; formal prefix review pending.** Candidate full-result computation is `e00016`; root-visible delivery is `e00019`. The subsequent action `e00021` formats and submits the computed result without reranking, re-extracting, rechecking the full dataset or making a delegated call. Final answer delivery is useful remaining work. Three iterations alone do not establish redundancy. No repeated full computation after candidate sufficiency is observed.

There is no provider/environment failure or resource censoring in this run. Formal H2 contracts, H5 evidence assessment and H6 sufficiency/purpose classifications remain open under the existing human-review rubric. No formal campaign hypothesis label is finalized here.
