"""Offline evidence generation and integrity verification. Never enables live execution."""

import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from ..common import BRANCH, PIN, REPO, WORKSPACE, preserved_hashes, sha, write_json


def git(*args):
    result = subprocess.run(["git", "-c", f"safe.directory={REPO.as_posix()}", *args],
                            cwd=REPO, capture_output=True, check=False)
    return {"exit_code": result.returncode, "stdout": result.stdout.decode().strip(),
            "stderr": result.stderr.decode().strip()}


def artifact_inventory():
    rows = []
    paths = []
    for directory, names, files in os.walk(WORKSPACE):
        names[:] = [name for name in names if name not in {'isolation-staging', '__pycache__', '.ruff_cache'}]
        paths.extend(Path(directory) / name for name in files)
    for path in sorted(paths):
        if not path.is_file() or path.name == 'artifact-manifest.json':
            continue
        relative = path.relative_to(WORKSPACE).as_posix()
        if '__pycache__' in relative or relative.startswith('.ruff_cache/'):
            continue
        group = relative.split('/')[0]
        purpose = {
            'tasks': 'Frozen public inputs, queries, renderer and dataset provenance',
            'evaluators': 'Researcher-only independent oracle and hypothesis review schemas',
            'runners': 'Offline execution, passive observation, resource supervision and pilot gates',
            'fixtures': 'Explicitly synthetic model responses for runtime behavior tests',
            'tests': 'Deterministic benchmark, annotation, equivalence, safety and configuration tests',
            'results': 'Offline validation evidence; no natural baseline observations',
        }.get(group, 'Workspace documentation, bootstrap or integrity utility')
        rows.append({'path': relative, 'bytes': path.stat().st_size,
                     'sha256': sha(path.read_bytes()), 'purpose': purpose,
                     'retention': 'reviewable_local_and_git_trackable'})
    write_json(WORKSPACE / 'artifact-manifest.json', {'version': 1, 'files': rows,
               'excluded_from_self_hash': ['artifact-manifest.json'],
               'excluded_rebuildable_runtime': 'isolation-staging/; payload hashes retained in results/windows-stage.json',
               'large_trace_policy': 'No generated evidence is ignored. Archive raw traces with checksums before any future removal; retain a second durable copy before excluding any evidence.'})
    return len(rows)


def preflight(reuse_evidence=False):
    before = json.loads((WORKSPACE / 'results/integrity-before.json').read_text())
    after = preserved_hashes()
    branch = git('branch', '--show-current')
    source_diff = git('diff', '--exit-code', PIN, '--', 'rlm', 'tests', 'pyproject.toml', 'uv.lock')
    status = git('status', '--short', '--untracked-files=all')
    write_json(WORKSPACE / 'results/integrity-after.json', after)
    integrity = {'expected_branch': BRANCH, 'branch': branch,
                 'protected_and_m2_hashes_unchanged': before == after,
                 'protected_and_m2_file_count': len(after), 'pinned_source_diff': source_diff,
                 'git_status': status, 'head': git('rev-parse', 'HEAD')}
    write_json(WORKSPACE / 'results/integrity-verification.json', integrity)
    command = [sys.executable, '-I', '-B', str(WORKSPACE / 'offline.py'), 'test']
    if not reuse_evidence:
        tests = subprocess.run(command, cwd=REPO, capture_output=True, check=False)
        (WORKSPACE / 'results/test-output.txt').write_bytes(tests.stdout + tests.stderr)
    suite = json.loads((WORKSPACE / 'results/test-summary.json').read_text())
    equivalence = json.loads((WORKSPACE / 'results/equivalence-summary.json').read_text())
    isolation = json.loads((WORKSPACE / 'results/isolation.json').read_text())
    isolated_evidence = WORKSPACE / 'results/windows-isolation/summary.json'
    if isolated_evidence.exists():
        from .windows_boundary import verify_stage
        stage = json.loads((WORKSPACE / 'results/windows-stage.json').read_text())
        verify_stage(stage)
        isolation = json.loads(isolated_evidence.read_text())
    test_exit_code = (0 if suite['success'] else 1) if reuse_evidence else tests.returncode
    # Recheck AFTER all workers/tests, not only before them.
    final_hashes = preserved_hashes()
    integrity['post_test_hashes_unchanged'] = before == final_hashes
    write_json(WORKSPACE / 'results/integrity-verification.json', integrity)
    integrity_ok = (before == after == final_hashes and branch['stdout'] == BRANCH
                    and source_diff['exit_code'] == 0)
    report = {
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'decision': 'OFFLINE PREPARATION PARTIALLY COMPLETE — BLOCKERS REMAIN',
        'live_enabled': False, 'api_requests_made': 0, 'python': platform.python_version(),
        'platform': platform.platform(), 'test_command': command, 'test_exit_code': test_exit_code,
        'test_evidence_reused': reuse_evidence,
        'full_suite_repeated': not reuse_evidence,
        'test_summary': suite, 'equivalence_fixture_count': len(equivalence),
        'integrity_pass': integrity_ok, 'oracle_isolation_pass': isolation['isolation_pass'],
        'checkpoints': {
            'A': 'passed: frozen benchmarks and independent oracles',
            'B': 'passed: deterministic annotation rules; semantic judgments remain human review',
            'C': 'passed for tested mock boundaries; general dependency tracing is not claimed',
            'D': ('synthetic resource controls passed; Windows AppContainer isolation passed for tested paths'
                  if isolation['isolation_pass'] else 'synthetic resource controls passed; OS oracle isolation FAILED'),
            'E': 'offline evidence complete; live gate BLOCKED',
        },
        'blockers': [
            *([] if isolation['isolation_pass'] else ['No verified OS filesystem boundary.']),
            'AppContainer uses synthetic transport only; external provider/budget broker integration and per-run scratch/profile lifecycle hardening remain required before live execution.',
            'Live transport adapter, verified provider prices/token bounds/retry accounting, sampling compatibility and separate live authorization remain required. No live SDK adapter was enabled or tested.',
        ],
        'limitations': [
            'Provider usage is synthetic; a 10% reservation margin is not proof of billing safety.',
            'Snapshots omit arbitrary objects and cannot establish arbitrary computation-to-claim dependencies.',
            'Arbitrary transient in-block proposals or mutations bypassing answer callbacks are not all observable; actual captures and returned answers are the assessed boundaries.',
            'The original same-account supervisor is not a filesystem boundary. AppContainer is separately tested; neither local termination nor synthetic accounting proves remote billing cancellation.',
            'Ruff and pre-commit are unavailable in the current environment; no dependencies were installed.',
        ],
    }
    if test_exit_code != 0 or not integrity_ok:
        report['checkpoints']['E'] = 'FAILED: inspect test and integrity evidence'
    report['windows_isolation_evidence'] = str(isolated_evidence.relative_to(WORKSPACE)) if isolated_evidence.exists() else None
    report['windows_isolation_summary'] = isolation if isolated_evidence.exists() else None
    report['offline_isolation_ready'] = bool(isolation['isolation_pass'] and integrity_ok and test_exit_code == 0)
    broker_paths = ['broker-summary.json', 'broker-followup-summary.json',
                    'broker-http-check.json', 'pilot-resume-check.json']
    broker_checks = {name: json.loads((WORKSPACE / 'results' / name).read_text())
                     for name in broker_paths if (WORKSPACE / 'results' / name).exists()}
    broker_ok = len(broker_checks) == len(broker_paths) and all(row['success'] for row in broker_checks.values())
    report['broker_checks'] = broker_checks
    report['ready_for_live_preflight_review'] = bool(report['offline_isolation_ready'] and broker_ok)
    if report['ready_for_live_preflight_review']:
        report['decision'] = 'READY FOR LIVE PREFLIGHT REVIEW'
        report['checkpoints']['D'] = 'passed: external admission/accounting with pinned RLM and per-run AppContainer cleanup, using offline mocks'
        report['checkpoints']['E'] = 'ready for review; live execution disabled and unauthorized'
        report['blockers'] = [
            'Review/freeze provider model availability, endpoint behavior, worst-case prices, input-token bound method, output/reasoning-token cap and usage/cost reconciliation. Synthetic bounds/rates are not live configuration.',
            'Review the staged implementation and campaign policy, then explicitly authorize credential provisioning and any live preflight requests. Current CLI and Pilot live gates remain disabled.',
        ]
        report['live_preflight_requirements'] = 'LIVE_PREFLIGHT.md'
    write_json(WORKSPACE / 'results/offline-preflight.json', report)
    report['artifact_count'] = artifact_inventory()
    return report
