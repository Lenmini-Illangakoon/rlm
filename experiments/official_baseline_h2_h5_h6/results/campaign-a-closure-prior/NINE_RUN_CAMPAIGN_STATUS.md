> **Accounting update after authorized metadata reconciliation:** S2-R03 is ready for separately authorized execution. Campaign protected exposure is **$1.06056415**; the original **$0.448448** preflight hold remains. S1-R03 stays operationally interrupted. See the [reconciliation report](results/reconciliation/S1-R03/RECONCILIATION_REPORT.md). The text and linked status JSON below are the preserved pre-reconciliation historical snapshot.

# Nine-run campaign execution status — blocked during Round 3

**Campaign incomplete: seven runs completed correctly, S1-R03 stopped operationally, and S2-R03 has not executed.** Round 3 started in the approved order, with S3-R03 followed by S1-R03. The second root request of S1-R03 failed with `IncompleteRead`, leaving new pilot usage/billing unknown. The existing accounting safeguard blocks the remaining slot. No request was retried, failed run replaced, scenario changed or unresolved reservation released. Formal hypothesis classifications are not finalized.

## All nine planned slots

| Run | Outcome / actual-answer correctness | Completed root iterations | Root requests / plain subcalls / genuine recursive calls | Official seconds | Known provider charge | Known conservative debit | New unresolved hold |
|---|---|---:|---|---:|---:|---:|---:|
| [S1-R01](S1_R01_EXECUTION_RESULT.md) | Completed / correct | 4 | 4 / 0 / 0 | 76.404 | $0.08246875 | $0.09902875 | $0 |
| [S2-R01](S2_R01_EXECUTION_RESULT.md) | Completed / correct | 8 | 8 / 2 / 0 | 444.481 | $0.17427805 | $0.20135005 | $0 |
| [S3-R01](S3_R01_EXECUTION_RESULT.md) | Completed / correct | 3 | 3 / 0 / 0 | 38.112 | $0.03427350 | $0.03873750 | $0 |
| [S2-R02](S2_R02_EXECUTION_RESULT.md) | Completed / correct | 5 | 5 / 0 / 0 | 75.125 | $0.07901500 | $0.09485500 | $0 |
| [S3-R02](S3_R02_EXECUTION_RESULT.md) | Completed / correct | 3 | 3 / 0 / 0 | 32.870 | $0.03122600 | $0.03713000 | $0 |
| [S1-R02](S1_R02_EXECUTION_RESULT.md) | Completed / correct | 3 | 3 / 0 / 0 | 43.423 | $0.04527075 | $0.05347875 | $0 |
| [S3-R03](S3_R03_EXECUTION_RESULT.md) | Completed / correct | 4 | 4 / 0 / 0 | 41.669 | $0.03900300 | $0.04303500 | $0 |
| [S1-R03](S1_R03_EXECUTION_RESULT.md) | Operational failure / no actual answer, unassessable | 1 observed; total unavailable | 2 dispatched, 1 returned / 0 / 0 | Unavailable | $0.01699750 known only | $0.01843750 known only | **$0.3937958750** |
| S2-R03 | **Not executed: accounting blocker** | — | 0 / 0 / 0 | — | — | — | — |

All seven completed answers match their independent oracle: S1 requires the 60-ID set and total 1,361; S2 requires the correct ranked top three, quantities, twelve source IDs and total 20,538; S3 requires ascending IDs 3731/4637 and product 17,300,647. A missing answer in S1-R03 is not scored as an incorrect returned answer and is not replaced with its intermediate plan or the oracle. S2-R03 has no execution evidence and is not a negative research observation.

## Execution strategies and recovery

- **S1-R01:** explore, reconcile JSONL by exact IDs/status, recompute/check, expose full set and finalize.
- **S2-R01:** generated SyntaxError, first plain nano response supplies prose instead of strict JSON, revised extraction reaches output cap, then successful recovery using deterministic regex parsing. A prose-only turn precedes eventual finalization. The second subcall is explicitly resource-confounded.
- **S3-R01:** inspect section counts, parse/filter/sort/multiply, verify selected rows and finalize.
- **S2-R02:** inspect/parse four current sections, join/filter/rank, expose source/total payload, verify and finalize.
- **S3-R02:** inspect sections, parse/filter/sort/multiply, directly submit computed result.
- **S1-R02:** inspect, exact-ID/status reconciliation, sanity checks and direct same-block complete-set formatting/submission. Full-list observer state is not falsely treated as a later root-visible message.
- **S3-R03:** initial prose-only planning turn, then exploration, filtering/arithmetic and direct final delivery. The early planning turn occurs before sufficiency and is not an H6-positive continuation.
- **S1-R03:** successful section exploration, followed by an incomplete HTTP read on the second root request. No task-level reconciliation or finalization is recorded. The host stops without feeding partial provider text back as success.

No genuine recursive child RLM or batch occurred naturally. The two plain sub-LLM calls occurred in S2-R01 only; they must not be counted as recursive RLM calls. All executed runtimes were the pinned actual official `rlm.core.rlm.RLM` inside AppContainer with RootCheck disabled and unchanged configuration.

## Usage, latency and accounting

There are **34 dispatched provider attempts**, **33 delivered complete responses**, and **one unknown response**. Requested models comprise 32 root GPT-5 requests and two plain GPT-5-nano calls. Seven completed runs account for 30 root iterations; the failed run contributes one additional completed iteration in its prefix. Its next root request was dispatched, but total iterations and final completion latency are unavailable.

Known usage is **139,723 prompt + 101,950 completion = 241,673 tokens**. This excludes unknown usage for `attempt-00037`; it is not a complete campaign usage total. Native completion usage already includes reasoning. Official completion times in the table describe successful RLM completions; failed S1-R03 has no final official/job duration. Its first provider call took 15.419 seconds, which is not the duration of the failed run.

Known reported pilot inference cost is **$0.50253255**, with **$0.58605255** known conservative pilot debit. The latter retains uncached input pricing; the $0.08352000 difference is protective accounting, not another provider charge. Round 3 so far has $0.05600050 known reported charge and $0.06147250 known conservative debit, plus the unresolved new hold.

Campaign protected exposure is **$1.4286775250**:

- $0.58605255 known conservative pilot debit;
- **$0.3937958750 new unresolved S1-R03 hold**;
- $0.44882910 once-imported preflight exposure, including **$0.4484480 original unresolved reservation** and $0.00038110 known preflight charges.

Known response-reported inference charges including preflight are $0.50291365, excluding both unknown requests. Protected headroom against $20 is $18.5713224750. Every run's known debit plus retained hold remains below $2. No additional account/billing lookup was made, and unknown charges are not silently recorded as zero.

## Preliminary H2/H5/H6 observations

| Run | H2 | H5 | H6 |
|---|---|---|---|
| [S1-R01](evaluators/S1-R01-preliminary-observations.md) | None demonstrated | Provisionally not observed | None demonstrated |
| [S2-R01](evaluators/S2-R01-preliminary-observations.md) | Strong prose-for-JSON mismatch candidate | Provisionally not observed | Potential avoidable prose-only continuation; redundancy not established |
| [S3-R01](evaluators/S3-R01-preliminary-observations.md) | None demonstrated | Provisionally not observed | None demonstrated |
| [S2-R02](evaluators/S2-R02-preliminary-observations.md) | None demonstrated | Provisionally not observed | None demonstrated |
| [S3-R02](evaluators/S3-R02-preliminary-observations.md) | None demonstrated | Provisionally not observed | None demonstrated |
| [S1-R02](evaluators/S1-R02-preliminary-observations.md) | None demonstrated | Provisionally not observed; supported same-block formatting | None demonstrated |
| [S3-R03](evaluators/S3-R03-preliminary-observations.md) | None demonstrated | Provisionally not observed | None demonstrated; early plan is before sufficiency |
| [S1-R03](evaluators/S1-R03-preliminary-observations.md) | No mismatch shown in exploration; interrupted remainder inconclusive | No returned answer; acceptance not assessable | Interrupted before sufficient computation; not assessable |
| S2-R03 | Not assessed: unexecuted | Not assessed: unexecuted | Not assessed: unexecuted |

These are retrospective preliminary notes with exact trace references, not finalized formal classifications. Blinded H2 contracts/H6 sufficiency commitments and human H5 support/visibility confirmation remain outstanding. Correct answers do not prove mechanism absence; HTTP read failure and output limits are kept separate from semantic findings.

## Resource censoring and evidence completeness

**Zero of eight retained attempts are run-level resource-censored.** The cumulative threshold of two has not been triggered so far. Round 3 is incomplete, so its prescribed end-of-round checkpoint has not been reached. S1-R03 is retained as operational failure/unknown usage, not recoded as resource censoring. S2-R01's output-limited helper remains separately documented.

[Machine-readable nine-slot status](results/nine-run-campaign-status.json) links all retained records, summaries, preliminary notes and hashes. All **262 available chronological events**, exact dispatched prompts, complete received provider responses, generated Python and captured outputs/errors, root-visible histories, finalization decisions and available usage/timing are preserved. All eight provider journals are finalized; cleanup passed for all attempts. Actual 35-file runtime identities, 90 protected files and frozen implementation/policy match. Previous raw evidence and preliminary observations remain unchanged.

For failed S1-R03, the archived prefix ends at second dispatch `e00013`: there is no complete/partial second HTTP body, provider generation ID/usage/cost/status, final worker response, final answer or final elapsed metric. These limitations are explicit. They prevent claiming full successful-run evidence or a complete nine-run result; no missing evidence is fabricated.

## Progression blocker and next minimum step

The saved failure is **`IncompleteRead`**, request `0a0a4e4a7fa14fa9bbe7c378e06bc041`, ticket **`attempt-00037`**. It indicates an incomplete HTTP response read; the saved diagnostics do not establish an HTTP status, provider message, cause attribution, non-execution or zero charge.

**S2-R03 must remain blocked until verified usage/billing evidence permits reconciliation under the unchanged accounting policy.** Neither the remaining budget nor prior Round 3 authorization overrides that safeguard. Keep both unresolved holds, retain S1-R03 as the original failed attempt, and do not retry or replace it. No new provider lookup is authorized or performed by this investigation; any additional lookup needs separate authorization. The last inference slot may proceed only after the blocker is resolved under the existing protocol. No source/configuration edits, commits or pushes were made.
