# Windows offline isolation and reproducibility

This records the completed isolation phase. The current integrated broker and per-run cleanup are described in [LIVE_PREFLIGHT.md](LIVE_PREFLIGHT.md). The original isolation/equivalence checks were preserved and not rerun for broker integration.

The ordinary LocalREPL process could read the researcher canary because it ran as the researcher. Its builtin namespace exposes `open` and `__import__`; changing the working directory and executing in a separate Python namespace does not remove Windows file permissions. The original negative-control evidence remains in `results/isolation.json`. No official RLM source was changed to fix this.

## Implemented boundary

`runners/windows_boundary.py` launches a staged Python 3.12 worker in a dedicated Windows AppContainer with zero capabilities. It creates the process suspended, assigns a one-process, kill-on-close Job with UI restrictions, then resumes it. No parent handles or environment variables are inherited. The explicit environment contains only Windows/runtime paths and empty scratch profile paths, with no credentials. There is no unrestricted fallback.

The staged payload contains exact copies of the pinned `rlm` Python files, the existing Python runtime and required installed packages, and an explicit allowlist of experiment support files. It excludes oracles, assessments, results, credentials and dotenv files. Only this new staging tree receives AppContainer ACL entries: read/execute for payload and modify for low-integrity scratch. Researcher-file and official-source ACLs remain unchanged. Each launch verifies payload hashes and the inventory through the supported entry points. Public task context and query enter through JSON. Output is JSON, never a pickle deserialized by the host.

The per-user profile is `RootCheck.Offline.c6ed1074140b457b818118023c0a94eb`. Creation of its Windows profile metadata was explicitly approved during this task. No firewall exemption, network capability, administrative account or live SDK was enabled. `results/windows-stage.json` records the current local stage, SID and payload hashes; `results/windows-stage-before-broker.json` retains the prior manifest; `isolation-staging/` contains rebuildable local copies and is ignored by Git. It is not portable evidence: moving machines requires a fresh stage/profile and rerunning affected checks.

CPython 3.12.4's mode-0700 temporary directory DACL excludes this AppContainer, even when it creates the directory. The experiment-only `temp_permissions.py` adapter preserves exclusive randomized temporary-directory creation but inherits the protected scratch ACL using mode 0777. It supports string paths under scratch. This is an explicit filesystem policy adaptation, not a change to official RLM files. Arbitrary tempfile callers outside this contract are not claimed compatible.

## Verified results

`results/windows-isolation/summary.json` and the adjacent raw traces record:

- **9 protected paths denied** through Python `open`, native `CreateFileW` and extended Windows paths: the original canary, synthetic oracle/assessment/credential/dotenv files, all three real oracle JSON paths and the existing assessment fixture. Native reads and ACL-write attempts return access denied. Real credential files were never opened; credential tests use synthetic canaries and an environment allowlist.
- AppContainer token present; parent-process memory access, child-process creation and connection to a separate host-loopback service denied. Public context, scratch read/write and the official same-container LMHandler remain usable.
- **21/21 behavioral comparisons passed**, covering plain and recursive helpers, batches, duplicate/reordered slots, captures, mutations, errors, cancellation and fallbacks. Model request multisets, actual returns/errors, official trajectories and ordered captures within each node match saved uninstrumented controls. Only timing and bootstrap temporary paths are normalized; concurrent cross-node event order is not treated as deterministic.
- External timeout terminates an infinite generated-Python loop. All 90 protected source/M2 files remain unchanged.
- **3/3 default CLI transport checks passed** for S1, S2-v2 and S3 after routing `offline.py mock` through the boundary. Responses are canned `OFFLINE TRANSPORT ONLY`; these are not benchmark reruns or natural observations.
- Missing profile registration, altered payload hashes and inventory mismatches fail closed. All 29 experiment Python sources parse. `results/windows-isolation/final-verification.json` records preflight exit 2 (the expected live block), offline isolation readiness and unchanged source integrity.

The 21 comparisons and timeout completed during this isolation repair. After final entry-point cleanup, only the expanded nine-path access probe and three public-context transport checks were rerun. The previous 30-method full suite and benchmark preparation were not repeated. Earlier failed startup diagnostics remain retained; the successful summary supersedes them for the current staged configuration.

## Reproduce only affected checks

Run under the Windows user that registered the AppContainer, using the existing environment. In Codex, the restricted tool account cannot use the researcher's registered profile; these native process tests used the approved execution context. No administrator session or dependency installation was required.

```powershell
# Existing stage: full affected isolation/equivalence checks (not the full suite).
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/isolation_check.py --test
# Access-only follow-up; requires the existing equivalence summary.
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/isolation_check.py --test --access-only
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py mock --scenario S1
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py mock --scenario S2-v2
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py mock --scenario S3
# Reuse saved full-suite evidence; refresh source integrity, stage verification and reports.
.\.venv\Scripts\python.exe -I -B experiments/official_baseline_h2_h5_h6/offline.py preflight --reuse-evidence
```

Preflight still exits **2** because live execution is blocked. On a fresh checkout without `results/windows-stage.json`, `isolation_check.py --register-profile --test` builds a new stage and registers its per-user profile before testing. That command intentionally creates Windows profile metadata outside the repository. Do not reuse another machine's absolute-path manifest. Hash/inventory failures require explicit staged-copy regeneration and revalidation, never automatic fallback or silent acceptance. Run this offline harness sequentially.

## Limits and remaining blockers

This resolves the tested researcher-filesystem leak for offline synthetic execution. It is not a general hostile-code sandbox certification. AppContainer may access Windows resources granted to all app packages; this implementation is not a filesystem mount containing only the payload. Researcher data must not be separately granted to this container/all app packages. Native denial probes remain an essential readiness check.

The subsequent broker integration is complete for offline review: the parent owns provider dispatch and accounting, while the worker uses a BaseLM JSON transport. The earlier multiprocessing/pickle supervisor remains a historical trusted-fixture test harness. See [current integration evidence and live-preflight requirements](LIVE_PREFLIGHT.md).

The earlier isolated fixture launcher reuses its test stage. The current broker path instead uses a private verified runtime copy, fresh scratch/mailboxes and an ephemeral AppContainer profile for every run, then removes them after preserving evidence. No earlier test stage/evidence was deleted. Worker event logs still are not a tamper-proof audit channel; provider admission/accounting now resides outside that process. Remote provider semantics and credential/live authorization remain review requirements. Ruff/pre-commit remain unavailable.

The approved nine-run order, round-one engineering checkpoint and cumulative stop threshold of **two or more resource-censored runs at the end of any round** are unchanged. No completed/censored runs are replaced, no budgets raised, and material protocol changes require versioning and separate treatment.

Platform references: [AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation), [process security capabilities](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-security_capabilities), and [Job objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects). Local readiness is based on the recorded probes, not documentation alone.
