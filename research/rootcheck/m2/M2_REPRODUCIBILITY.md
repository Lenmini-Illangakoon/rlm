# M2 reproducibility and provenance

## Current verification status — 2026-11-23

**The saved original 30 diagnostic cases have now been reproduced: 30 PASS, 0 failed.** All four Python processes and the successful runner invocation exited 0. A new, separate repeated-readiness test also passed: capture events ["A", "B"], retained candidate "B", returned answer "B".

See [final reproduction verification](M2_REPRODUCTION_VERIFICATION.md) for all 30 original/reproduced comparisons, interpretation and remaining gaps; [comparison JSON](test-results/reproduction-verification-2026-11-23.json), [supplementary evidence](test-results/supplementary-repeated-readiness-2026-11-23.json) and [exact commands](test-results/reproduction-commands.txt) preserve the execution evidence.

The initial bare runner invocation exited 1 at Git ownership preflight, before any probe. The successful invocation used a process-local forward-slash safe.directory setting. No persistent Git configuration, runner, original source script or original execution record was changed. D7's cross-child availability order varied, while the original partial-order assertions and final A|B still passed. 29/30 decoded original observation payloads matched exactly; the sole difference is scheduling, not a behavioral discrepancy.

Raw runner outputs remain under ignored test-results/local/. Their complete records are also retained in the Git-eligible comparison JSON. No upstream tests were rerun during this verification. Passing these diagnostics confirms the recorded baseline behavior, including hazards; it is not evidence that H2/H5/H6 validation or recovery is correct.

**CONDITIONAL GO remains.** Natural official-runtime failures, successful real-model recovery and the proposed enforcement/adapters remain unestablished. The supplementary test is not added to the original 30 count.

## Archive-creation record — prior state

The text below preserves the earlier archive-creation state and plan. Its "pending", "not executed", "all 16 files" and future-tense reproduction statements refer to the archive before this separately authorized verification. The current status above and the linked final report supersede those status labels without rewriting original evidence.

**Archive written 2026-11-23. The reproduction runner and extracted scripts have not been executed.** Static parsing and integrity checks are distinct from reproduction. Original execution timestamps were not separately recovered.

## Evidence classes and coverage

| Class | What is saved | Status |
| --- | --- | --- |
| Original executed probe results | Four tool result objects, unchanged stdout strings, exit codes and chunk metadata in `test-results/original-probe-runs.json` | 30 original PASS rows; all four exits 0 |
| Recovered original source | Four decoded original PowerShell tool-call command bodies in `test-results/original-tool-inputs.txt` | All assertions and generated inputs recoverable; conversation transcription rather than independent session export |
| Newly extracted scripts | Four Python files under `probes/` | Mechanical extraction only; no logic refactoring or added assertions |
| Reconstructed probe tests | None | No missing probe logic was silently recreated |
| New archival tooling | `reproduce.ps1`, documentation, inventory, JSON manifests and hashes | Created later for preservation; not part of original executions |
| Later saved-script results | None currently | PENDING; future runner outputs go to ignored `test-results/local/` |
| Repeated-readiness test | Proposed protocol in inventory | PENDING, expected B from source only |

Original probe counts: cp4=9, cp2=12, delivery_identity_accounting=7, accounting_extra=2. Archival I10a/I10b map to original I10_wrapper_uncaught/I10_wrapper_caught. Original source strings and stdout keep those original identifiers.

## Recovery and exact transformations

Source was recovered from accessible preceding M2 conversation tool inputs and outputs. It was not recovered from Git, an existing script, or an independently exported session file. No session export or original execution-time code digest is claimed.

1. Transcribe the decoded original PowerShell command bodies as text. The enclosing JavaScript string escaping/tool orchestration is not a separate preserved artifact.
2. Preserve the environment prefix and PowerShell here-string/pipeline in the original-command record. The first three commands set PYTHON_DOTENV_DISABLED, PYTHONDONTWRITEBYTECODE and PYTEST_DISABLE_PLUGIN_AUTOLOAD to 1; accounting_extra originally sets only the first two.
3. For each executable Python file, take the substring after the opening `@'\n` and before the final `\n'@ |` in that recovered command. Remove only the PowerShell prefix, delimiters and Python-stdin invocation; append one final LF. Save UTF-8 with LF. No imports, identifiers, assertions, comments, order or logic are rewritten, and the scripts are not formatted.
4. Preserve each original tool result object as JSON. JSON escaping/indentation is archival serialization; decoding its output field yields the recovered stdout string. Parsed case mappings and status labels are newly added metadata, separate from that object.
5. Add a newly written safety/reproduction wrapper. It uses fresh processes and guards in addition to the original test-time patches; it is not claimed to reproduce original process setup byte for byte.
6. Calculate SHA-256 artifact digests after writing. They establish current artifact identity and cannot attest what hashes or stdin bytes existed during the original runs. The manifest excludes itself to avoid self-reference; its separate final digest may be reported externally.

No secret redactions were required by the scoped scan. No .env files or credentials were read. Absolute local repository paths in original commands and test headers are retained as provenance. Automated pattern scanning does not constitute a historical session authenticity attestation.

## Existing upstream test evidence

Original selected runs: **134 passed + 21 passed = 155 unique tests**. Subsequent selected reruns: **28 passed + 4 passed = 32 tests**, all a subset of those 155, not 187 unique tests. `upstream-nodeids.txt` preserves the recovered collection identities and the 32-node subset; collection is not a replacement for execution logs.

`original-offline-runs.txt` preserves recovered pytest command segments, the retained 134-run tail, complete retained 28-run chunks, the 4-run tool output including subsequent read-only inspection, and the transcript-reported 21-run summary. The first 134-run chunk and the raw 21-run stdout are not included. These gaps are explicit; no missing upstream stdout is fabricated.

Original selection excludes in_process/subprocess/IPython/Docker variants as documented in that record. This is not a full-suite or cloud-environment verification. No upstream tests were rerun to build the archive.

## Execution environment and configuration

`environment-current.json` is an archive-time environment inspection, not an original package lock snapshot. It records current CPython 3.12.4, Windows AMD64, relevant installed distribution versions, and 64 protected upstream files with baseline Git blob OIDs and current working-file SHA-256 values. The original pytest headers independently establish Python 3.12.4, pytest 9.2.0, pluggy 1.7.0 and win32 only. Full original dependency versions, OS build and process environment were not captured. Current metadata cannot fill those gaps retrospectively.

The recovered probes instantiate the baseline defaults unless explicitly overridden: local environment, persistent=False, compaction=False, stream=False, experimental_spec_ptc=False, orchestrator=True; max_depth=1 and max_iterations=30 in the constructor. The F-series harness overrides iterations to 1. These defaults are inferred from the pinned source plus the recovered calls, not a separately recorded original settings dump. No live backend is created: backend labels are inert because factories are patched to MockLM.

| Probe group | Explicit configuration and fixtures |
| --- | --- |
| F1–F4 | Harness iterations 1, scripted REPL responses; F4 adds one default response; captured results and copied requests. |
| F5/F6/F7 | max_errors=1; max_tokens=1 with mock total 20; max_budget=.01 with synthetic cost .02, respectively. |
| F8/F9 | max_timeout=1, fake clock 0→2; iterations 1 for final / 2 for nonfinal. |
| I1–I8 | Four helper modes × single/batch; leaf parent max_depth=1; synthetic bad/good slots; ProbeReject exception. |
| I9/I10a/I10b | Direct LocalREPL callback/wrapper; no root request required; ordinary rejection text / caught and uncaught wrapper. |
| I11 | Root iterations 1, two code blocks, wrapped helper rejection, second final. |
| D1 | Root iterations 2; first turn two blocks and exact formatted feedback; programmed second response. |
| D2/D3 | In-memory history/list mutations, serialized/deep-copied controls; no model request. |
| D4 | max_depth=2, iterations=1, max_budget=1; root usage 10 input/5 output/.01, child 30/7/.03 per call. |
| D5 | iterations=1; fake first call 2 seconds plus default 7. |
| D6/D7 | max_depth=2, iterations=1; actual mocked child REPLs, custom note callbacks and partial-order assertions. |
| D8 | max_depth=2, iterations=1, max_budget=.035; distinct client synthetic costs .01/.03. |
| D9 | Direct batch handler; fixtures 15/40 input tokens and 2/8 fake seconds; no root completion. |

Unset budget/token/error/timeout limits are None by the pinned constructor. Child inheritance and fallback behavior are part of the tests/source under review, not proof of strict global budget enforcement. Direct LocalREPL/LMHandler cases have no root settings where not instantiated. See saved source for every exact mocked response, override and assertion.

## Offline reproduction design — pending separate execution

The new `reproduce.ps1` checks the expected branch, pinned commit availability, protected upstream diff and archive/source hashes. Later evidence-only commits may advance HEAD without altering pinned upstream files. It uses the existing virtual environment and installs nothing. It requires enabled Python assertions and launches one fresh `python -I -B` process per selected script.

Before importing RLM, the bootstrap disables dotenv loading (environment switch and patched entry point), blocks .env-file access, non-loopback socket operations/name resolution, datagrams and child-process launches. It replaces both client factories with a fail-closed stub; the unchanged probe scripts then patch core.get_client to their existing MockLM factories. Numeric loopback TCP remains allowed for the actual LMHandler sockets. These are guards for reviewed mock-only scripts, not a security sandbox for hostile arbitrary code or a general upstream-suite runner.

The runner compares each output's ordered original case identifiers and PASS status/count, plus process exit 0. Original assertions provide the behavioral checks. It does not require identical concurrent event interleavings or tool wall times. A failure must be recorded and investigated; do not silently edit the recovered probe logic to obtain a pass.

After separate approval/review, proposed invocation from the repository root:

```powershell
& .\research\rootcheck\m2\reproduce.ps1
# Or select a single original source group:
& .\research\rootcheck\m2\reproduce.ps1 -Probe cp4
```

These commands have **not** been run during archive creation. A successful future invocation creates timestamped JSON records under the scoped ignored directory `test-results/local/`, clearly marked as later reproduction. It does not rewrite original evidence or automatically change this archive's pending status. Review and preserve later results through a separately authorized update.

## Integrity and storage policy

All 16 archive files are intended for Git tracking; generated local reproduction outputs alone are ignored by the scoped `.gitignore`. No virtual environment, credential file, binary trace, dataset copy or future milestone directory is included. No files are staged, committed or pushed.

Static verification checks Python ASTs, PowerShell syntax and embedded-bootstrap AST, all 30 unique archival mappings, original output/exit consistency, mechanical extraction equality, JSON validity, archive digests and protected-source identity. It does not import/execute the probes, invoke pytest, exercise safety guards dynamically, or establish saved-script reproduction.

The manifest inventories every other archive artifact by path, size and SHA-256 and records provenance/status separately. It is an integrity index, not a signed attestation. If Git changes line endings or content, saved-file hashes must be checked and any normalization documented before later reproduction.

Review [decision](M2_DECISION_RECORD.md), [matrix](M2_CP_FEASIBILITY_MATRIX.md), [inventory](M2_PROBE_INVENTORY.md) and [manifest](evidence-manifest.json) together. The repeated-readiness prediction, natural H2/H5/H6 failure occurrence and successful real-model recovery remain unexecuted/unestablished.
