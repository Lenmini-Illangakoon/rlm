# RLM-Minimal versus official RLM: Campaign A comparison

Campaign A execution is complete: nine frozen slots retained, eight correct completions and one operationally interrupted S1-R03. This document records the explanatory comparison discussed after execution. It is an outcome-aware interpretation of saved evidence, not a controlled causal comparison or a formal hypothesis assessment. No new experiments were performed for this document.

## Formal assessment status

**Formal H2/H5/H6 assessment remains pending.** The commit-preparation review found no completed natural-run formal assessment records in the repository's research, experiment or documentation trees. The [final campaign status](results/nine-run-campaign-status.json) sets `formal_hypothesis_classifications_finalized` to false; individual run records retain pending assessment fields. [Existing per-run observations](NINE_RUN_CAMPAIGN_STATUS.md#preliminary-h2h5h6-observations) are retrospective and explicitly preliminary. `results/assessment-fixtures.json` contains synthetic annotation examples, not completed natural-run reviews.

The [prescribed rubric](evaluators/RUBRIC.md) requires identified reviewers and trace/hash references, pre-result H2 contract commitments, prefix-based H6 sufficiency commitments before reviewing later continuation, and human H5 support/visibility judgments. Those records were not found. Correctness checks and retrospective comments do not substitute for this workflow. Existing preliminary labels and historical classifications are preserved.

## What the two studies actually show

The historical Phase 3 [consolidated analysis](../../../rlm-minimal/rlm-minimal/experiments/phase3_failure_analysis/PHASE3_CONSOLIDATED_ANALYSIS_DRAFT.md), sections 1, 3 and 4, did not confirm all H1-H6. It reported H2 in 1/3 EXP-3B runs, H5 in 1/3 EXP-3E runs, H6 in 1/3 EXP-3F runs, and H4 in three researcher-assessed calls across three EXP-3D runs. H1 was not demonstrated; H3 had no established positive transition. These hypothesis-specific denominators must not be pooled into one failure rate.

Campaign A focused on H2/H5/H6. It produced two plain sub-LLM calls, both in S2-R01, and zero genuine child RLM executions. Most successful trajectories inspected the context, generated deterministic Python, parsed/joined/filtered/ranked or calculated, and returned a correct answer. The [nine-slot report](NINE_RUN_CAMPAIGN_STATUS.md) records strategies, usage, correctness and operational limitations for every slot.

S2-R01 preserves a similar action-outcome problem to the historical H2 example: a normally returning helper supplied prose rather than the requested structured extraction. This is a **strong preliminary candidate**, not a finalized H2 label. In its [trace](results/broker/broker-b3dd0f8ebee74e40a5d794cabbdcec4a.events.jsonl), `e00022` starts the helper, `e00024` dispatches, `e00025` receives prose, `e00026` returns it and `e00027` records the caught JSON parsing failure. Later Python recovery produces the correct final answer. The second helper hits the completion cap and is resource-confounded. A later prose-only turn (`e00054`-`e00055`, followed by another dispatch at `e00057`) is a potential avoidable continuation, without established redundant task computation. See the [separate preliminary assessment](evaluators/S2-R01-preliminary-observations.md) for exact IDs and caveats, including the root's inventory-prefix instruction defect.

## Explanatory factors

| Factor | Evidence | Interpretation and limit |
|---|---|---|
| Strategy and delegated-action exposure | Only two plain helper calls and no recursive children in Campaign A; deterministic parsing dominates. | Most runs bypass the semantic extraction boundary implicated in several historical failures. This limits exposure; it does not demonstrate that such failures are impossible. |
| Different prompts | Minimal's frozen prompt strongly encourages sub-LLM use. Official [orchestrator instructions](../../rlm/utils/prompts.py) explicitly allow direct Python/regex when sufficient, while also encouraging delegation where appropriate. | Prompt differences plausibly influence strategy. Their independent causal effect was not tested. |
| Different finalization interfaces | Minimal uses `FINAL(...)` / `FINAL_VAR(...)`; official uses `answer["content"]` / `answer["ready"]`. Historical consolidation sections 4.2, 4.5 and 4.6 describe incomplete variable-only delivery, acceptance behavior and continuation associated with terminal-marker handling. | Interfaces create different failure opportunities. No ablation establishes which interface accounts for the observed difference, and official finalization is not a general evidence validator. |
| Different tasks and coverage | [Frozen protocol](protocol.md): S1 reuses historical EXP-3B seed-301 context/query; S2 is the approved S2-v2 revision; S3 preserves EXP-3F seed-701 context but adds explicit public coverage to the query. | Task clarity and semantic demands can affect behavior. S1 reuse and related S3 tasks mean task structure alone cannot explain the difference. |
| Different resource/provider conditions | Historical EXP-3B manifest uses GPT-5/GPT-5-nano aliases with `max_completion_tokens: null`; Campaign A has a 32,768 completion cap, approved snapshots, OpenAI-only routing and host accounting. | Model labels alone do not establish identical endpoints, request semantics or conditions. The capped S2-R01 helper is a concrete confound. No evidence establishes that a stronger model caused the improvement. |
| Few repetitions and different assessment status | Three runs per scenario, one operational interruption; historical positives were case-level findings, while Campaign A labels remain preliminary. | Strategy variation can change observed cases. No significance test or controlled failure-rate reduction is established. Final-answer correctness cannot erase intermediate failures. |

## Historical terminology: helper calls versus recursive RLM execution

Minimal's historical traces call `llm_query` activity "recursive." Its frozen EXP-3B `Sub_RLM.completion` sends a single LM completion request; it does not instantiate a child REPL and iterative RLM loop. It is structurally closer to official `llm_query` than official `rlm_query`. Preserve the original historical labels, but do not count those calls as demonstrated multi-level iterative RLM execution. Campaign A's zero recursive child calls must not be contrasted with Minimal's historical counter as though both counters measured the same behavior.

This interpretation was checked against the archived EXP-3B source snapshot, not inferred from the class name. The snapshot hashes match its manifest. The current sibling Minimal working `repl.py` differs from that frozen snapshot; the archived version is the authority for this comparison.

## Bounded conclusion

Campaign A demonstrates effective deterministic processing of these frozen tasks by the pinned official runtime, with one strong semantic action-outcome candidate, a possible continuation candidate, and an operational interruption. It does not isolate controller reliability, establish absence of H2/H5/H6, compare all H1-H6, or evaluate genuine recursive reasoning. Plausible contributors are prompting, finalization, task coverage, provider/resource conditions and stochastic strategy selection. Their separate contributions remain unmeasured.

The historical results remain valid within their documented configurations and review limitations. The official results cannot be interpreted as evidence that the main codebase fixed all historical mechanisms. No additional experiment, formal relabeling or Campaign B execution is authorized or performed by this document.

## Historical source identity and portability

The relative historical links require the sibling `rlm-minimal/rlm-minimal` archive; that archive is outside this scoped commit. Retain it in the research backup alongside Campaign A. SHA-256 references:

| Historical artifact | SHA-256 |
|---|---|
| Phase 3 consolidated analysis, inspected revision | `5d6c721336becada5d73c1829ac90c89ceaa499a80a704ac7b358e8ddad5e613` |
| EXP-3B frozen `source_snapshot/rlm/repl.py` | `f52f8ea9681c5853209067bdacda0416713fffd6c58d1adadbf0f59a56abeab7` |
| EXP-3B frozen `source_snapshot/rlm/utils/prompts.py` | `3f23c8fbd644cb9191e227a485ae8feb3a0c807093e1690c3649ed44ef747819` |

The snapshots and `run_configuration` are under `experiments/phase3_failure_analysis/exp3b_outcome_mismatch/instances/seed_301/` in that archive. Its recorded baseline source revision is `dd2f5ab3a47c5e170dd178807b4e3b1ee088a1be`. Official Campaign A pin is `e11f1a8f8ee4490686e16dd6463233abe08a07eb`; the campaign's raw evidence hashes and policy identity are retained in [the machine-readable report](results/nine-run-campaign-status.json) and [artifact manifest](artifact-manifest.json).
