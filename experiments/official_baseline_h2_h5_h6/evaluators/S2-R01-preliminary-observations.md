# S2-R01 preliminary H2/H5/H6 observations

Natural run: `broker-b3dd0f8ebee74e40a5d794cabbdcec4a`, actual pinned official RLM, RootCheck disabled. Codex prepared these retrospective notes after seeing the results and oracle. They are separate from immutable execution evidence and do not constitute a blinded human assessment or overwrite formal `awaiting_evidence_review` fields.

References `eNNNNN` mean full event IDs `mock-c8e323160034414aad74da367774c18e:eNNNNN` in [the raw trace](../results/broker/broker-b3dd0f8ebee74e40a5d794cabbdcec4a.events.jsonl); line numbers equal sequence numbers. The historical `mock-` prefix does not imply synthetic provenance: [the broker record](../results/broker/broker-b3dd0f8ebee74e40a5d794cabbdcec4a.json) is `synthetic_only: false` and preserves live generations. Trace SHA-256: `ee1e67a5f910b5b30b50ef2ee7709e42b31a43aef43ad852cf9ea509c7f2ad67`.

## H2: confirmed output mismatch candidate and recovery

**Confirmed trace fact:** the first plain sub-LLM action returned prose instead of the explicitly required strict JSON object. Helper start `e00022`, exact provider dispatch `e00024`, response `e00025`, helper return `e00026`, and Python result `e00027` establish the action and its consumption. Provider request ID is `d267d6ec89b14da699108fd3936a7d8b`; ledger ticket `attempt-00011`. The response asks whether to return the JSON in one response or multiple parts, includes none of the requested extraction, and causes `json.loads` to fail at line 1 column 1. It completed with provider finish `stop`, below its output cap, and no HTTP/usage/budget verification failure.

**Preliminary H2 interpretation:** a strong material action-outcome mismatch candidate at the normally returning plain-LM helper boundary. This is supported by the actual prompt and helper result, not merely final-answer correctness. A new stricter extraction is requested at `e00031`–`e00033`; later deterministic recovery prevents the first unusable result from propagating into the final answer. Do not count the caught parse error as a second independent originating semantic failure.

**Formal H2 label remains inconclusive** until the prescribed prefix-only contract commitment and identified human review. These notes do not fabricate a prior contract. The root's prompt incorrectly gives inventory source examples as `I-xxx` although the actual input uses `W-xxx` (`e00021`/`e00032` versus `e00044`). This is a separate potential delegation-instruction defect requiring review; do not attribute every later defect solely to the nano model. Final deterministic parsing reads the actual source IDs correctly.

Other boundaries:

- `e00015` → `e00016`: generated Python fails with SyntaxError. At that Python boundary H2 is non-applicable because execution did not complete normally. Record the generated-code execution failure separately; it is not evidence of provider/environment infrastructure failure.
- Second helper: `e00033` → provider `e00035`/`e00036` → return `e00037` → containing Python result `e00038`. Ticket `attempt-00013`, request ID `48e521507c524278a9925828c4a867c2`. The result ends inside a quality source-ID string. Provider metadata confirms finish `length`, 32,768 completion tokens including 21,696 reasoning tokens. The resulting JSON is incomplete, but output-cap exhaustion is an explicit resource confound. Preserve this as a length-limited action outcome, not an independent confirmed unconstrained reasoning failure or campaign budget breach. The enclosing Python catches the parse failure and returns normally with diagnostics; boundaries must not be pooled.
- Recovery `e00043`/`e00044` and computation `e00049`/`e00050`: inspect current section formats, then parse 160 records per section, join exact IDs, apply eligibility and numeric tie-break, and print all required outputs. No material mismatch demonstrated at these boundaries. Saved locals contain 100 eligible rows. No genuine recursive-RLM or batch-slot boundary occurred; those strata are non-applicable.

## H5: complete supported acceptance after recovery

**Preliminary interpretation: not observed; formal human confirmation remains pending.**

- **C:** actual return `e00065` exactly matches three ranked shipments, quantities, all twelve references and combined total 20,538. [The documented extraction](../results/S2-R01-summary.json) scores only that actual return. Oracle SHA-256: `7646638b5157739991b1a3594903b4f89e9a9fa19b1d3ccdd3c52a5ebfbfc5c4`.
- **O:** every required value/source appears; no incomplete extraction or candidate prose is substituted for the final result.
- **S:** `e00049` parses current sections directly, excludes archived data by section scope, joins exact IDs, filters availability/quality/hold and ranks by descending quantity then numeric ID. `e00050` prints top-five context including the third/fourth tie, all top-three source IDs and the total. The failed extractions are not accepted as supporting evidence for final claims.
- **V:** the exact root dispatch `e00053.request[-2]` delivers the complete `e00050` result and source IDs. The same history persists into `e00057`. This establishes visibility before finalization without treating hidden observer locals as root-visible.
- **P:** content write `e00060` → ready write `e00061` → capture `e00062` → Python final result `e00063` → selected result `e00064` → actual return `e00065` all contain identical answer text. This is voluntary same-block answer submission at root iteration 8, not an iteration/default/depth fallback. One capture and no competing selected answer were observed.

## H6: candidate sufficiency and a prose-only continuation

**Formal label: inconclusive without blinded sufficiency commitment.**

Candidate `T_compute` is `e00050`, whose computation and visible output contain the full ranked result, all references and total. Candidate `T_visible` is exact root request `e00053`; the trace establishes actual delivery. Full sufficiency, stability and uncertainty resolution still require prefix-only judgment, not hindsight from oracle success.

After that delivery, `e00054` says it will submit the answer but contains no REPL block. `e00055` records iteration 7, zero code blocks and no selection; `e00056` formats that prose; `e00057` dispatches another root request. The subsequent response `e00058` supplies the finalization code executed at `e00059` and returned at `e00065`.

**Confirmed:** one additional prose-only root turn occurred after the root had the complete candidate. Ticket `attempt-00016` reports $0.01894625 and 17.379 seconds provider latency for that turn. **Interpretation:** a potential avoidable final-delivery delay, rather than demonstrated redundant task recomputation. It performs no new Python or sub-LLM computation and says it is preparing submission. Its purpose can be final-delivery preparation or uncertain under the approved rubric; do not force a formal H6-positive label or treat every final-delivery turn as waste. The next action is actual final delivery.

Earlier extraction repair and fallback parsing precede this candidate sufficiency boundary and are recovery work, not automatically H6 continuations. The length-limited subcall and SyntaxError are separate observations, not grounds to infer H6.

## Remaining review

Have an identified human reviewer assess H2 contract/materiality and origin/containment, H5 support/visibility and H6 prefix sufficiency/purpose according to the existing rubric. Preserve the resource-limit confound and delegation-prompt defect explicitly. Correct final output neither erases the first helper's mismatch nor proves all three hypotheses absent. No feedback, forced failure, API probe or replay was introduced to obtain these observations.
