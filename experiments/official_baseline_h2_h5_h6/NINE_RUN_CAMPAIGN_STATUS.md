# Campaign A ? final nine-slot execution report

**Campaign A is closed: nine authorized slots retained, eight completed with correct answers, and S1-R03 operationally interrupted.** No run was retried or replaced. All pilot request usage and billing are now reconciled. The original preflight reservation remains held. Formal hypothesis classifications remain pending.

## Outcomes, execution and costs

| Run | Outcome | Root iterations | Root / plain sub-LLM / recursive calls | Official seconds | Actual reported USD | Conservative debit USD |
|---|---|---:|---|---:|---:|---:|
| [S1-R01](S1_R01_EXECUTION_RESULT.md) | Correct | 4 | 4 / 0 / 0 | 76.404 | $0.08246875 | $0.09902875 |
| [S2-R01](S2_R01_EXECUTION_RESULT.md) | Correct | 8 | 8 / 2 / 0 | 444.481 | $0.17427805 | $0.20135005 |
| [S3-R01](S3_R01_EXECUTION_RESULT.md) | Correct | 3 | 3 / 0 / 0 | 38.112 | $0.03427350 | $0.03873750 |
| [S2-R02](S2_R02_EXECUTION_RESULT.md) | Correct | 5 | 5 / 0 / 0 | 75.125 | $0.07901500 | $0.09485500 |
| [S3-R02](S3_R02_EXECUTION_RESULT.md) | Correct | 3 | 3 / 0 / 0 | 32.870 | $0.03122600 | $0.03713000 |
| [S1-R02](S1_R02_EXECUTION_RESULT.md) | Correct | 3 | 3 / 0 / 0 | 43.423 | $0.04527075 | $0.05347875 |
| [S3-R03](S3_R03_EXECUTION_RESULT.md) | Correct | 4 | 4 / 0 / 0 | 41.669 | $0.03900300 | $0.04303500 |
| [S1-R03](S1_R03_EXECUTION_RESULT.md) | Operational interruption; no final answer | 1 observed; total unavailable | 2 / 0 / 0 | Unavailable | $0.04080800 | $0.04412000 |
| [S2-R03](S2_R03_EXECUTION_RESULT.md) | Correct | 3 | 3 / 0 / 0 | 49.874 | $0.05372825 | $0.05977625 |

All eight returned answers match their independent scenario oracle. S1 returns the complete 60-ID set and total 1,361. S2 returns the correct ordered three shipments, quantities, twelve source IDs and total 20,538. S3 returns IDs 3731/4637 and product 17,300,647. S1-R03 has no returned answer and is unassessable for answer correctness; it is not counted as an incorrect returned answer or omitted from the nine-slot denominator. The observed completion rate is 8/9, with correctness 8/8 among completed runs. These small-sample observations do not establish a general success rate.

## Execution strategies and recovery

- **S1-R01:** Explore; JSONL exact-ID/status reconciliation; recompute/check and expose full set; finalize.
- **S2-R01:** Generated SyntaxError; plain nano returns prose; revised extraction reaches output cap; recover with deterministic regex parsing; prose-only planning turn; finalize.
- **S3-R01:** Inspect section counts; parse/filter/sort/multiply; verify selected rows and finalize.
- **S2-R02:** Inspect; parse four sections; exact-ID join/filter/rank; expose source/total payload; verify and finalize.
- **S3-R02:** Inspect sections; parse/filter/sort/multiply; submit computed answer.
- **S1-R02:** Inspect sections; exact-ID/status reconciliation; sanity checks and direct same-block complete-set formatting/submission.
- **S3-R03:** Initial prose-only plan; explore; parse/filter/sort/multiply; direct final formatting/submission.
- **S1-R03:** Explore sections successfully; second response read fails with IncompleteRead before further code or final answer. Later metadata confirms provider completion and reconciles billing only; no replay or replacement.
- **S2-R03:** Inspect; deterministic parse of four current sections; join/filter/rank and expose full source/total evidence; format and submit. No errors or actual delegation.

Actual delegation comprises **two plain GPT-5-nano calls, both in S2-R01, and zero recursive child RLM calls or batches** across Campaign A. Proposed delegation in model prose is not counted as execution. S2-R01 recovers from generated SyntaxError and helper extraction problems through later deterministic parsing within the same official RLM trajectory; this is not an adapter retry. All executed runtimes used pinned official `rlm.core.rlm.RLM` in AppContainer with RootCheck disabled. Frozen datasets, query prompts, model configuration, routing and experimental order were preserved.

## Usage, latency and accounting

The campaign dispatched **37 provider requests**: 35 root GPT-5 and two plain GPT-5-nano. **36 complete provider responses reached the runtime**; S1-R03's second response did not. Billing and native token usage are known for all 37 requests after the separately authorized metadata reconciliation. There are **33 root iterations in completed runs**, plus one completed prefix iteration in interrupted S1-R03; its full iteration total is unavailable.

Native tokens: **156,650 input + 108,380 completion = 265,030 total**. Native completion counts include reasoning; reasoning detail is never added a second time to cost. Raw provider usage and any detail conflicts remain preserved. S1-R03's separate metadata uses native counts rather than its different generic token counts.

- Actual reported pilot inference charges: **$0.58007130**.
- Conservative pilot debit: **$0.67151130**.
- Known preflight charges: **$0.00038110**; known charges including preflight: **$0.58045240**.
- Original unresolved preflight reservation: **$0.44844800**, unchanged.
- Protected campaign exposure: **$1.12034040**; remaining against $20: **$18.87965960**.
- New unresolved pilot reservations: **$0**. All $2/run and $20 campaign limits were respected. Reservations and conservative excess are not represented as actual charges.

Successful official completion durations range from 32.870 to 444.481 seconds; their sum is 801.957 seconds. Successful AppContainer job durations sum to 823.063 seconds. S1-R03 final official/job duration is unavailable, so neither sum is a full campaign elapsed time. Per-call and per-run available latencies are retained in summaries and journals. Metadata provider-generation duration is not substituted for missing RLM completion duration.

## Operational interruption and reconciliation

S1-R03 second request `0a0a4e4a7fa14fa9bbe7c378e06bc041` failed locally with `IncompleteRead`. The worker received no usable response and returned no final answer. Later, one explicitly authorized metadata GET corroborated generation `gen-1795620768-3317xhBT42UcDMqARGgi`, OpenAI GPT-5 snapshot, successful provider completion and exact $0.02381050 charge. Ticket `attempt-00037` was reconciled from a $0.3937958750 hold to the conservative $0.02568250 debit. This recovers accounting, not missing content or research execution. The original journal and interrupted classification remain unchanged. See [separate reconciliation report](results/reconciliation/S1-R03/RECONCILIATION_REPORT.md).

## Preliminary H2/H5/H6 observations

| Run | H2 | H5 | H6 |
|---|---|---|---|
| [S1-R01](evaluators/S1-R01-preliminary-observations.md) | no material mismatch demonstrated | provisionally not observed | no redundant continuation demonstrated |
| [S2-R01](evaluators/S2-R01-preliminary-observations.md) | strong prose-for-JSON mismatch candidate; not formally classified | provisionally not observed | potential avoidable prose-only continuation; redundant computation unestablished |
| [S3-R01](evaluators/S3-R01-preliminary-observations.md) | no material mismatch demonstrated | provisionally not observed | no redundant continuation demonstrated |
| [S2-R02](evaluators/S2-R02-preliminary-observations.md) | no material mismatch demonstrated | provisionally not observed | no redundant continuation demonstrated |
| [S3-R02](evaluators/S3-R02-preliminary-observations.md) | no material mismatch demonstrated | provisionally not observed | no redundant continuation demonstrated |
| [S1-R02](evaluators/S1-R02-preliminary-observations.md) | no material mismatch demonstrated | provisionally not observed | no redundant continuation demonstrated |
| [S3-R03](evaluators/S3-R03-preliminary-observations.md) | no material mismatch demonstrated | provisionally not observed | no redundant continuation demonstrated |
| [S1-R03](evaluators/S1-R03-preliminary-observations.md) | completed exploration shows no material mismatch; interrupted remainder inconclusive | not assessable: no actual return / no-return stratum | not assessable over incomplete trajectory; no sufficient candidate established |
| [S2-R03](evaluators/S2-R03-preliminary-observations.md) | No material mismatch demonstrated; formal contract review pending | Provisionally not observed; complete computed payload visible before finalization; human review pending | No redundant continuation demonstrated; final action formats and delivers existing result; formal prefix review pending |

The strongest candidate remains S2-R01?s normally returned prose response to an explicit JSON extraction request. Its other capped helper response is resource-confounded; generated SyntaxError and the S1-R03 HTTP failure are kept separate from semantic H2 evidence. S2-R01 also contains a potential avoidable prose-only continuation, but redundant computation is not established. No completed run preliminarily demonstrates H5; support and root-visible evidence still require formal human review. Other runs show no material H2 mismatch or redundant H6 continuation demonstrated in retrospective review. Absence of a demonstrated mechanism does not establish universal absence.

S2-R03 exact evidence: parse/join/filter/rank `e00015`?`e00016`; full source/total payload delivered at `e00019.request[-2].content`; final formatting `e00021`, capture `e00024`, selection `e00026`, actual return `e00027`. The final action delivers the already computed answer without reranking. Its separate preliminary note documents exploratory heuristics and visibility limitations. All hypotheses were considered wherever applicable across all slots; S1-R03?s missing remainder and no-return stratum remain explicitly unassessable. No formal hypothesis classification is finalized.

## Resource censoring, evidence and closure

**Cumulative run-level resource censoring: 0/9; prescribed stop threshold: 2.** Round 3 boundary has been reached and the threshold is not triggered. S2-R01?s length-limited helper is retained as action-level censoring; S1-R03 is an operational interruption. All nine lifecycle cleanups passed.

All **289 available chronological raw events**, exact dispatched prompts, received raw model responses, generated Python, REPL output/errors, recursive/delegation instrumentation, actual root-visible histories, finalization/candidate decisions, returned answers and usage are retained. The eight successful runs have full worker responses and trajectories. S1-R03 retains its 13-event prefix ending at second dispatch and separate billing metadata; its missing second model content, final answer, final worker response and elapsed time remain missing. Evidence is complete for available observations, with this documented operational gap.

[Machine-readable final report](results/nine-run-campaign-status.json) contains per-slot metrics and immutable evidence hashes. [S2-R03 execution report](S2_R03_EXECUTION_RESULT.md) and [structured summary](results/S2-R03-summary.json) link the final run?s raw files and targeted checks. Earlier campaign-status and manifest snapshots are preserved in `results/campaign-a-closure-prior/`. Existing per-run reports are historical evidence; for S1-R03 accounting, use its reconciliation record and this final report.

The final frozen progression is **`complete`**, with no active run or campaign execution lock. Campaign A execution is stopped. The original preflight hold remains unresolved under its approved carried-exposure exception; formal blinded H2/H6 review and H5 support/visibility confirmation remain analysis work. No additional inference, retry, replacement, provider probe, official-source/configuration change, RootCheck implementation, commit or push was performed.
