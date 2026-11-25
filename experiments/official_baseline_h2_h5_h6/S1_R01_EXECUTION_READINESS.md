# S1-R01 live baseline execution readiness

**READY FOR LIVE S1-R01 BASELINE EXECUTION, pending explicit authorization to execute that run.** No provider probe, API request, credential access or pilot run occurred during this preparation. RootCheck remains disabled. The official RLM source and frozen experimental configuration/datasets were not changed.

The prepared campaign is [official-baseline-v1](results/campaigns/official-baseline-v1.json), with no pilot records and no active run. Its initial cumulative exposure is **$0.44882910**, including the unchanged **$0.448448** unknown reservation and $0.00038110 known preflight charges. This exposure was imported once against the **$20** campaign ceiling. Each actual pilot run retains its own **$2** limit, 24 provider attempts, 64,000 input-token ceiling, 32,768 completion cap and 900-second deadline. The existing nine-run sequence, round-one engineering checkpoint and cumulative two-resource-censored-runs stopping rule are unchanged.

## Exact first-run command

From the repository root, after authorizing S1-R01:

```powershell
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/live_baseline.py --authorize-run S1-R01
```

Suggested authorization: **“Execute S1-R01 only under the existing $2/run and $20 campaign limits, retaining the carried preflight exposure. Use the existing project .env key securely. Do not automatically start the next run or retry failed provider requests.”**

The command loads only `OPENROUTER_API_KEY` into the parent adapter after campaign/stage/next-run checks. It never copies the key into the worker environment or logs it. It executes one run and exits; the same command cannot repeat S1-R01 after a retained result. Interrupted active runs and locks require review. Subsequent runs require their own exact-run command/authorization. After three runs, continuation also requires the existing engineering checkpoint approval. Neither `offline.py live` nor the historical config's global live flag was enabled.

## Minimum implementation now complete

- **Input bound:** ASCII-escaped JSON message bytes + 1,024 global framing tokens + 128 per message. Only the already-approved text roles/content shape is accepted. The byte count conservatively bounds byte-level tokenization of content; the explicit framing allowance covers the simple chat envelope under the approved no-preset/no-extra-tools policy. It is an admission bound, not a tokenizer estimate or a proof about undisclosed future provider transforms. `Ledger.admit` rejects a bound above 64,000 before dispatch. Nothing truncates, rewrites or repairs the prompt. This intentionally can censor earlier than a native-token estimate. Reported usage exceeding the reserved bound stops execution.
- **Frozen campaign identity:** includes approved provider routing/no-fallback/price policy, exact approved model endpoint names, bound and telemetry revisions, host/observer source hashes, protected-source hashes, dataset-manifest hash, frozen config/limits/rates and preflight seed identity. Reopening a campaign with a different identity fails. The supplemental live host policy supplies the approved provider details without rewriting historical config fields.
- **Exact-once carry-forward:** only the exact original `attempt-00001` record imported from the cumulative preflight journal is exempt from the “unresolved exposure blocks progression” gate. Its entire reservation remains counted. Any new unresolved pilot ticket, altered carried ticket, active campaign or interrupted state still blocks progression. A retained seed lock prevents silently reseeding a missing campaign.
- **Telemetry:** raw usage/provider metadata are retained. Native completion cost is counted once, with the existing conservative uncached-vs-reported reconciliation. If reasoning detail exceeds completion, the separate conservative sum must fit the reserved completion cap; the conflict is recorded, not presented as explained. Prices, token types/totals, input/output bounds, services, provider route and snapshot are checked. Missing/invalid/uncertain budget data stops delivery; the remaining original hold stays reserved alongside any known spend. Genuine reported cost/bound overruns also stop. No automatic metadata queries or retries are introduced. Routing/provider failures remain operational evidence, not findings about RLM reasoning.
- **Runtime authenticity:** inside AppContainer, the worker hashes the 35 pinned runtime files supplied by the parent and verifies the imported class is `rlm.core.rlm.RLM`. It records the actual staged import path and hashes before completion. Official source, prompts, execution, recursion, routing decisions and final-answer selection remain in pinned RLM. Only the existing client factory adapter and passive observers are external. The original cached stage is preserved; two updated experiment observer files are overlaid in the disposable private run copy and hashed before launch. The existing equivalence and isolation evidence is reused.

## Research evidence coverage

| Required evidence | Preserved source |
| --- | --- |
| Root and sub-LM full prompts/responses | Parent `provider_records` retains exact request bodies, complete provider responses and worker correlation; `provider_dispatch`/`provider_return` link delivered content by request ID, node, action and batch slot |
| Generated Python, full REPL stdout/stderr, runtime errors | `python_start`, `python_result` and raised/failure events; official trajectory and archived worker response retain structured execution results |
| Recursive execution | Node start/parent/depth, recursive dispatch/result, helper start/return, batch-slot correlation, child trajectory metadata and per-node iteration events |
| Full result versus what the root actually received | Full `python_result` is distinct from `formatted_results`; the latter is produced by the official formatter exactly once. The next root `provider_dispatch` supplies the authoritative delivered message history. Prepared-but-undelivered output is not treated as root-visible |
| Finalization and actual return | Candidate captures, answer-write attempts, iteration selection, default/fallback paths and `actual_return`; the returned worker response is retained separately |
| Usage, costs, latency, iteration counts | Per-attempt raw usage/cost and ledger, dispatch/receive times, worker elapsed times, per-node iteration number/time and official final execution time/count. Do not add nested usage summaries to the authoritative provider ledger a second time |
| Chronology and trace references | Monotonic event sequence/timestamps, unique event/action/node IDs, request IDs, batch slots, parent provider journal, raw JSONL and raw worker-response archive paths |

The new targeted AppContainer check confirms a full 24,000-character output plus `ZeroDivisionError` remains in research evidence while the root receives the official truncated REPL-output message. It also confirms recursive metadata, two root iterations, four accounted synthetic calls, final selection/return and successful scratch/profile cleanup. This is a synthetic instrumentation check, not a natural H2/H5/H6 observation. Observer snapshots deliberately avoid invoking arbitrary user-object representation hooks; non-builtin locals are marked unobserved, while official serialized execution results remain available. Censored/interrupted runs retain the completed event prefix and raw partial final line. If evidence archival fails or exceeds its safety bound, scratch is retained and the run is marked infrastructure failure instead of deleting uncaptured evidence.

Each actual run records all **H2/H5/H6 assessments as pending evidence review**, regardless of scenario. Apply the existing observed/not-observed/non-applicable/inconclusive scheme wherever applicable, including negative cases. Preserve operational failures and resource censoring separately. Use committed pre-result prefixes for contracts and root-visible evidence for H6; do not infer root awareness from hidden locals or child output. No expected failure is injected, and no oracle/assessment enters the worker.

## Verification and remaining blockers

Four new host-policy tests passed and the new AppContainer evidence check passed. Two mistakes in that new fixture's assertions were corrected: failed-block variable persistence and searching for a tail marker in assistant source code rather than only the REPL-output message. Their failed-check records and raw executions are preserved; the final assertion correction was checked against the already completed runtime evidence, without another AppContainer execution. Existing completed suites were not rerun. The previous 21 equivalence cases remain passing evidence, and 90 protected files remain unchanged.

Evidence: [host checks](results/pilot-policy-check.json), [AppContainer evidence check](results/pilot-runtime-evidence-check.json), [runtime trace reference](results/pilot-runtime-evidence-reference.json), [existing equivalence evidence](results/equivalence-summary.json), [final integrity/readiness record](results/s1-r01-readiness.json).

No implementation blocker remains for S1-R01. The remaining gate is explicit live-run authorization. Ruff is not installed in the existing virtual environment; no tool or dependency was installed for this task. Import/syntax checks and the targeted runtime checks passed. No commits or pushes were made.
