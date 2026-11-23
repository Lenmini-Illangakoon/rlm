# M2 archived-probe reproduction verification

Verification date: **2026-11-23**. Baseline: `e11f1a8f8ee4490686e16dd6463233abe08a07eb`. Branch: `research/m2-runtime-feasibility`.

**Result: all four reproduction Python processes exited 0. The new supplementary repeated-readiness test also passed, exit 0.** All 30 original diagnostic assertions passed on reproduction. Twenty-nine decoded observation payloads matched exactly, while D7 exhibited a permitted concurrency scheduling difference without violating the tested invariants. One initial invocation failed before any probe ran.

This is later reproduction evidence. Original command bodies, four recovered source scripts, original outputs, environment snapshot and upstream test records remain unchanged. Pending labels in the original archive-creation decision/matrix/inventory and original-tool-result metadata describe that earlier state; this report, the current reproducibility record and manifest supply the later verification status.

## Execution commands and exit codes

The first command was `& '.\research\rootcheck\m2\reproduce.ps1'`: shell exit **1**, zero probe processes started. Git rejected the runner's backslash-form safe.directory under the sandbox account. This was a preflight failure, not a failed case or a changed branch. Account/SID details are omitted from tracked diagnostics; the failure record is explicitly an excerpt/summary.

The unchanged runner succeeded with a process-local Git setting:

```powershell
$env:GIT_CONFIG_COUNT='1'
$env:GIT_CONFIG_KEY_0='safe.directory'
$env:GIT_CONFIG_VALUE_0='D:/iit/4th Year/FYP/RLM/rlm'
& '.\research\rootcheck\m2\reproduce.ps1'
```

No persistent Git configuration was written. This process-local override is part of the verified reproduction command; the bare command remains unsuitable on this sandbox account. The runner has not been patched to hide the limitation.

Git also emitted a permission warning for the user-global ignore file. It did not block reproduction; the repository-scoped ignore rule is verified separately.

| Executed process | Original diagnostic count | Exit | Result |
| --- | --- | --- | --- |
| Initial bare runner preflight | 0 executed | 1 | Git ownership failure |
| Runner with process-local override | 30 | 0 | PASS |
| Python: cp4.py | 9 | 0 | PASS |
| Python: cp2.py | 12 | 0 | PASS |
| Python: delivery_identity_accounting.py | 7 | 0 | PASS |
| Python: accounting_extra.py | 2 | 0 | PASS |
| Python: new supplementary repeated-readiness script | 1 separate new case | 0 | PASS |

[Exact command record](test-results/reproduction-commands.txt) preserves both attempts and the exact supplementary invocation. The runner uses the existing interpreter with `-I -B -`, a script path and its SHA-256; stdin contains the guarded bootstrap in the unchanged runner. Interpreter/environment headers, timestamps and each per-script exit code are preserved in [comparison JSON](test-results/reproduction-verification-2026-11-23.json).

## Original versus reproduced observations

All rows below have original assertion status **PASS** and reproduced assertion status **PASS**. This is a diagnostic assertion status, not a certification that baseline behavior satisfies RootCheck requirements. The JSON record preserves every original and new observed field, including complete event arrays and error text.

| Archival ID | Original observed result | Newly reproduced result |
| --- | --- | --- |
| F1 | Captured/returned A despite ValueError; no next request. | Captured/returned A despite ValueError; no next request. |
| F2 | Captured/returned A; answer dictionary later contains B. | Captured/returned A; answer dictionary later contains B. |
| F3 | Separate blocks capture [A,B]; root returns A; earlier locals show B. | Separate blocks capture [A,B]; root returns A; earlier locals show B. |
| F4 | No normal candidate; fenced DEFAULT_CODE_MUST_NOT_RUN text returned raw, not executed. | No normal candidate; fenced DEFAULT_CODE_MUST_NOT_RUN text returned raw, not executed. |
| F5 | Captured A; ErrorThresholdExceededError; no final return/log. | Captured A; ErrorThresholdExceededError; no final return/log. |
| F6 | Captured A; 20 tokens exceed limit 1; TokenLimitExceededError. | Captured A; 20 tokens exceed limit 1; TokenLimitExceededError. |
| F7 | Captured A; cost .02 exceeds .01; BudgetExceededError. | Captured A; cost .02 exceeds .01; BudgetExceededError. |
| F8 | Timeout 1, fake elapsed 2; A returned normally. | Timeout 1, fake elapsed 2; A returned normally. |
| F9 | Nonfinal overrun; TimeoutExceededError before next turn. | Nonfinal overrun; TimeoutExceededError before next turn. |
| I1 | Error: REJECTED consumed/finalized; failed call omitted (0 records). | Error: REJECTED consumed/finalized; failed call omitted (0 records). |
| I2 | Bad error-text slot + OK; consumption/finalization continue (1 record). | Bad error-text slot + OK; consumption/finalization continue (1 record). |
| I3 | Recursive callback error text consumed/finalized (0 records). | Recursive callback error text consumed/finalized (0 records). |
| I4 | Recursive callback batch error text + OK; finalization (1 record). | Recursive callback batch error text + OK; finalization (1 record). |
| I5 | No-callback fallback error text consumed/finalized (0 records). | No-callback fallback error text consumed/finalized (0 records). |
| I6 | No-callback batch fallback error text + OK; finalization (1 record). | No-callback batch fallback error text + OK; finalization (1 record). |
| I7 | Core leaf error text consumed/finalized (1 record). | Core leaf error text consumed/finalized (1 record). |
| I8 | Core leaf batch error text + OK; finalization (2 records). | Core leaf batch error text + OK; finalization (2 records). |
| I9 | REJECTED: explanation is final; recorded error is None. | REJECTED: explanation is final; recorded error is None. |
| I10a | Outer uncaught wrapper withholds payload and stops block; no final. | Outer uncaught wrapper withholds payload and stops block; no final. |
| I10b | Generated catch continues; payload withheld but final AFTER. | Generated catch continues; payload withheld but final AFTER. |
| I11 | First block fails; second block executes and returns SECOND. | First block fails; second block executes and returns SECOND. |
| D1 | Raw error hidden by 20,000-char cap; SECOND delivered; scripted repair. | Raw error hidden by 20,000-char cap; SECOND delivered; scripted repair. |
| D2 | Live prompt alias changes old memory entry; serialized string stable. | Live prompt alias changes old memory entry; serialized string stable. |
| D3 | Earlier list mutates to [1,2,3]; frozen [1]; failed new binding absent. | Earlier list mutates to [1,2,3]; frozen [1]; failed new binding absent. |
| D4 | Root reports cost .01/input 10; distinct clients total .04/input 40. | Root reports cost .01/input 10; distinct clients total .04/input 40. |
| D5 | Raw default returned; fake outer time 9, reported 2 (omits 7). | Raw default returned; fake outer time 9, reported 2 (omits 7). |
| D6 | dispatch < child body < availability < consumption < ready; final A. | dispatch < child body < availability < consumption < ready; final A. |
| D7 | Availability B then A; both per-child orders pass; final A\|B. | Availability A then B; both per-child orders pass; final A\|B. |
| D8 | Distinct cost .04 exceeds budget .035; root reports .01, returns A. | Distinct cost .04 exceeds budget .035; root reports .01, returns A. |
| D9 | Slot inputs [40,40] vs total 55; durations [5,5] vs fixture [2,8]. | Slot inputs [40,40] vs total 55; durations [5,5] vs fixture [2,8]. |

F4's exact multiline raw candidate is retained in the comparison JSON: fenced `repl` text containing `raise RuntimeError('DEFAULT_CODE_MUST_NOT_RUN')`. Neither execution ran that statement. I10a/I10b retain original identifiers `I10_wrapper_uncaught`/`I10_wrapper_caught`; the source and outputs were not renamed.

**Deviation:** 29/30 decoded observation payloads match exactly. D7 differs only in the order of the cross-child availability events (original B,A; reproduced A,B). The original probe asserts each child's dispatch → body → available → ordered batch consumption → readiness, not a fixed ordering between children. Both traces satisfy the original assertions and return A|B. JSON decoding normalizes number spelling/whitespace; no byte-identical stdout claim is made.

Passing assertions reproduce limitations as well as normal behavior. F1 confirms acceptance despite a later error; I1–I9 confirm error strings can be consumed/finalized; I10b/I11 confirm interruption bypass; D4/D8/D9 confirm accounting limitations. These passes do not establish semantic H2/H5 correctness, safe rollback, a validated provenance ledger or implemented RootCheck intervention.

## New supplementary test — separate from the original 30

Source: [supplementary_repeated_readiness.py](probes/supplementary_repeated_readiness.py). Evidence: [supplementary result](test-results/supplementary-repeated-readiness-2026-11-23.json). This is newly authored test logic, not recovered original source.

The test supplies exactly one mocked response containing the A/ready, blank line, B/ready sequence. A delegating spy wraps the existing answer dictionary's `_on_ready` callback; it records each argument and calls the original capture callback. No runtime source is modified.

Observed and asserted:

- Capture events: `["A", "B"]`.
- Retained `REPLResult.final_answer`: `"B"`.
- Final dictionary content and root completion response: `"B"`.
- Empty stderr, one executed block and one mocked model call.
- Python and shell exit codes: 0.

This confirms the prior source-derived expectation. Baseline storage retains the latest candidate; the added spy is what proves both capture events. The baseline docstring's “first time” wording does not describe the observed callback behavior on repeated truthy assignments. No docstring/source change is made.

The supplementary command reuses the runner's guarded Python bootstrap without rerunning the original four scripts. Its exact executed command is preserved in the command record; it remains independently reproducible from the saved script.

## Offline safety and evidence preservation

The inspected original scripts use MockLM, MockLM subclasses, synthetic callbacks/usage/clocks and actual local runtime/LMHandler components. The local socket protocol is deliberately exercised rather than mocked away. No provider client or paid service is needed.

Before RLM imports, the bootstrap disables dotenv via environment and a patched entry point, blocks .env-file reads, non-loopback sockets/name resolution, datagrams and child-process launches, and replaces both LM client factories with a rejecting stub. Existing test-time factory patches supply the mocks. Successful completion means no registered guard violation remained. No negative guard test attempted an external connection, and these guards are not claimed to sandbox hostile arbitrary code.

The runner writes only timestamped records under ignored `test-results/local/`; original record paths cannot be selected as its output paths. Inspection plus the post-execution hash comparison confirms all 16 archive-creation files were unchanged by execution. This task then updates only the current M2 reproducibility document/manifest and adds later reproduction evidence plus the supplementary script.

The four local runner records remain ignored (12,180 bytes total). Their complete decoded records and hashes are also preserved in the Git-eligible comparison JSON, so a reviewed commit can retain the evidence without adding ignored local files. The supplementary tool stdout/exit record is separately saved. No original record is replaced with reproduced output.

## Integrity, scope and remaining limits

After all execution, all 64 protected runtime/test/dependency files match their recorded SHA-256 values. Git diff against the pinned baseline is empty for `rlm/`, `tests/`, `pyproject.toml` and `uv.lock`. The unrelated `experiments/m2/smoke_test.py` has the same byte hash, size and exact modification time; the experiments file set is unchanged. Nanosecond timestamps are stored as decimal strings to preserve precision across tools.

Archive artifact hashes are recalculated only after the authorized record writes. The original four scripts, runner, original execution records, historical decision/matrix/inventory and environment snapshot retain their pre-verification hashes. No original historical RLM-Minimal record, upstream prompt/source/test, dependency or unrelated experiment is edited. No file is staged; no branch, commit, push or merge operation is performed. The scoped scan checks Git-eligible evidence and local reproduction outputs for common credential/private-key/token patterns without reading credential files.

This closes the saved-probe reproduction gap and the specific repeated-readiness gap. Existing upstream tests were not rerun here: their 155 original unique tests and 32 overlapping reruns remain historical evidence, not additional counts. Missing original upstream raw-log portions and the original conversation-transcription authenticity limit remain documented.

**CONDITIONAL GO remains unchanged.** Natural official-runtime H2/H5/H6 failure occurrence, real-model recovery, end-to-end validators, host-enforced abort, rollback/dependency invalidation, full finalization gates and strict global accounting remain unverified/unimplemented. Shipment-readiness remains a candidate family. H6 retains equal observational importance in the next baseline study while its MVP intervention remains deferred.

The evidence is ready for a reviewed Git commit with the process-local command requirement documented. Formal M2 closure remains the user's decision; successful diagnostic reproduction does not upgrade the research recommendation to unconditional GO.
