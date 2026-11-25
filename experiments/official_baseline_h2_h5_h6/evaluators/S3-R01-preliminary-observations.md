# S3-R01 preliminary H2/H5/H6 observations

Natural official-RLM run `broker-deb1b866c6344031816958a484472db8`, RootCheck disabled. These are Codex's retrospective preliminary observations after viewing outcomes and the oracle, not a blinded human assessment. Formal run assessment fields remain `awaiting_evidence_review`.

Event `eNNNNN` denotes `mock-fb61e15aeb8b483682bb22156ef0c59f:eNNNNN` in [the raw trace](../results/broker/broker-deb1b866c6344031816958a484472db8.events.jsonl). Sequence numbers equal JSONL line numbers. Trace SHA-256: `1c39a695bb0de291c29c31c7fe96ceb895c6a650e8efd148506a7a8921e1936e`. The historical event-ID prefix does not make this a synthetic run: [the broker record](../results/broker/broker-deb1b866c6344031816958a484472db8.json) is explicitly live and retains its provider generations.

## H2: action outcomes

**Preliminary observation: no demonstrated material action-outcome mismatch. Formal label remains inconclusive pending the prescribed contract review.**

- Exploration `e00009` → `e00010` locates the real Product Inventory section and confirms 320 JSON lines, while separately counting four archived and four planned records.
- Computation `e00015` → `e00016` parses that section, filters exact ACTIVE/APAC values, sorts integer IDs and computes their product. It returns normally, reports 320 parsed records and 104 eligible records, and prints the two IDs and product. Saved builtin locals independently preserve those computed values.
- Verification/finalization `e00021` → `e00025` prints the two selected records with ACTIVE/APAC fields, then formats and submits the answer. Captured stderr is empty for every Python boundary.

The computation includes catch-and-skip branches for JSON parsing and integer conversion. They are generic potential loss points, but no loss is demonstrated here: 320 parsed records and the 104 eligible IDs agree with the independent oracle. Do not turn an unexercised vulnerability into an observed H2 failure. No plain-LM, recursive-RLM or batch-slot boundary occurred; those strata are non-applicable in this run.

## H5: actual acceptance boundary

**Preliminary interpretation: not observed; formal human confirmation remains pending.**

- **C:** actual return `e00027` is `Product IDs: 3731, 4637; Product: 17300647`. The anchored extraction in [the summary](../results/S3-R01-summary.json) matches both required fields of the independent S3 oracle.
- **O:** both IDs in ascending numeric order and the product are present. No mandatory output was omitted.
- **S:** section-scoped computation `e00015` and result `e00016` support selection and arithmetic. The final verification `e00021`/`e00025` checks the recorded selected rows; it does not consult an oracle or external validation service.
- **V:** `e00019.request[-2]` actually delivers the parsed count, eligible count, first ten sorted IDs, two selected IDs and product to the root before finalization. Final same-block verification output is captured in `e00025` but is not delivered in a later root request. The existing rubric permits supported deterministic same-block computation; absence of an additional root turn is not itself an H5 visibility failure.
- **P:** content write `e00022` → ready write `e00023` → candidate `e00024` → Python final result `e00025` → selection `e00026` → actual return `e00027` preserve identical content. This is voluntary same-block submission in iteration 3, not a forced/default/depth path.

## H6: candidate sufficiency and final verification

**Formal label: inconclusive without a blinded prefix commitment. Preliminary review finds no demonstrated redundant continuation.**

Candidate `T_compute` is `e00016`; candidate `T_visible` is actual root dispatch `e00019`, which contains all requested outputs and diagnostic support. Full sufficiency, stability and material uncertainty must be judged from a prefix-only review rather than hindsight from final correctness.

The only subsequent generated action, `e00021`, checks the selected records and delivers the final answer in one block. Its purpose is useful verification plus final delivery, or mixed pending human review. It neither repeats the full parsing/ranking computation nor makes another delegation. A final deterministic check and submission are not automatically redundant simply because a candidate already exists. No later root continuation follows capture/selection/return.

## Review status and operational evidence

An identified human reviewer must confirm H2 contracts, H5 support/visibility and H6 sufficiency/purpose under the approved rubric. Negative and inconclusive interpretations remain explicit. No provider/environment failure, output-limit truncation, run-level censoring or forced termination occurred. The observations were obtained solely from this natural trajectory; no scenario or model-visible feedback was modified.
