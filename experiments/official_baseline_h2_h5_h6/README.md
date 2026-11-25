# Official RLM baseline: offline preparation

**READY FOR LIVE PREFLIGHT REVIEW.** The pinned official RLM now runs through the external provider/budget broker in a fresh AppContainer per run. Targeted offline integration checks passed. Live execution remains disabled. No live APIs, real credentials, RootCheck, official-source changes, commits or pushes were involved. Start with [LIVE_PREFLIGHT.md](LIVE_PREFLIGHT.md) for how execution works, essential files and the exact review requirements.

The original same-account LocalREPL leaked the researcher canary. AppContainer now denies all nine protected-path probes and preserves all 21 tested runtime behaviors. Live execution remains disabled. See [current preflight](results/offline-preflight.json), [Windows isolation/reproducibility](WINDOWS_ISOLATION.md), [original failure evidence](results/isolation.json) and the [implementation report](IMPLEMENTATION_REPORT.md).

## Reproduce from the repository root

For current incremental verification, use the targeted commands in [LIVE_PREFLIGHT.md](LIVE_PREFLIGHT.md). The commands below are full reproduction instructions; completed benchmark/full-suite work was not rerun for this repair. AppContainer mocks require the registered profile and staged runtime described there.

Use the existing Python 3.12 virtual environment. No dependency installation is required for these standard-library unittest tests and the already-installed RLM dependencies.

```powershell
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py prepare
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py test
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py mock --scenario S1
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py mock --scenario S2-v2
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py mock --scenario S3
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py preflight
```

`prepare` checks the original sibling `rlm-minimal/rlm-minimal` archive and its frozen oracles, regenerates S2 twice and independently reconstructs all answers. S1's archive working files have CRLF conversion; preparation retrieves the checksum-matching Git blobs instead. It never edits that archive. The frozen copies and ordinary tests can be used without rebuilding the historical checkout. The `test` command returns 0 on success. `preflight` deliberately returns **2** because live readiness remains blocked, even when all offline tests pass. `live` always refuses execution regardless of environment variables or credentials.

`mock` loads checksum-verified public data and the exact query, then invokes the real official RLM through the integrated parent broker and a canned provider. It does not solve or score the task and receives no oracle. The broker owns admission, provider dispatch and accounting; the worker has no credentials or provider network access. Each run gets a private verified payload copy, unique AppContainer identity and scratch/mailboxes, all removed after evidence is retained. Synthetic rates and bounds must not be reused as live configuration. `runners/pilot_runner.py` provides one-run-at-a-time campaign persistence and the unchanged nine-run gates; its live path remains disabled.

For individual checkpoints, append `--pattern test_benchmarks.py`, `test_assessment.py`, `test_instrumentation.py`, `test_safety.py` or `test_config.py` to `test`.

## Evidence and annotation

- [Dataset manifest](tasks/dataset_manifest.json): exact context/query/oracle hashes and historical provenance.
- [Protocol](protocol.md) and [pilot configuration](runners/pilot.json): unchanged pilot order, runtime limits and gates.
- [Assessment rubric](evaluators/RUBRIC.md): pre-result H2 contracts, actual-return H5 review and prefix-only H6 workflow.
- [Windows isolation summary](results/windows-isolation/summary.json) and [isolated public-context transports](results/windows-isolation/transport-summary.json).
- [Equivalence summary](results/equivalence-summary.json): each behavioral comparison and measured overhead.
- [Full test output](results/test-output.txt), [test summary](results/test-summary.json) and [integrity verification](results/integrity-verification.json).
- [Artifact manifest](artifact-manifest.json): reviewable artifacts, purpose, size and SHA-256; excludes its own recursive hash and rebuildable staging copies.

Generate a blinded packet from a selected evidence prefix:

```powershell
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py packet --trace experiments/official_baseline_h2_h5_h6/results/equivalence/mutable_snapshot.json --through 10
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py packet --trace experiments/official_baseline_h2_h5_h6/results/equivalence/mutable_snapshot.json --through 10 --root-visible-only
```

Choose the boundary from the event index, not from the known correct answer. H6 root-visible packets contain only exact root request histories; computed-but-undelivered values are excluded. Commit the reviewer, rationale, evidence references and prefix hash in a separate assessment record before opening later events or the oracle. This is an auditable researcher workflow, not cryptographic blinding against someone already possessing the full archive.

All current evidence, including raw mock traces, remains local and Git-trackable; nothing is staged. Deterministic datasets are small. Raw traces live separately in `results/equivalence/` and `results/mock/`; they contain variable timing and IDs. Research evidence is retained. Only rebuildable `isolation-staging/` runtime copies are ignored; their hashes are recorded in `results/windows-stage.json`. Before excluding larger future traces, copy them to durable research storage, verify their SHA-256 against the retained manifest, record the archive URI, and maintain a second durable copy. Re-running tests replaces the named fixture traces and summaries; archive a completed evidence set before a new protocol version. Run-specific mock traces have unique filenames.
