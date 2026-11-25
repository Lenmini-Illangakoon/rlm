"""Affected checks only. Invoked explicitly by isolation_check.py --test.

Not part of the generic test discovery: requires registered Windows AppContainer.
"""

import json
import os
import re
import socket

from experiments.official_baseline_h2_h5_h6.common import WORKSPACE, preserved_hashes, sha, write_json
from experiments.official_baseline_h2_h5_h6.fixtures.programs import FIXTURES, block
from experiments.official_baseline_h2_h5_h6.runners.windows_boundary import launch


def comparable(value):
    if isinstance(value, list):
        return [comparable(x) for x in value]
    if isinstance(value, dict):
        return {k: comparable(v) for k, v in value.items()
                if k not in {'timestamp', 'execution_time', 'iteration_time'}}
    if isinstance(value, str) and value.startswith('<_io.TextIOWrapper name='):
        # Bootstrap file objects live under different legitimate temporary roots.
        return re.sub(r"name='.*?context_(\d+)\.txt'", r"name='<private-temp>/context_\1.txt'", value)
    return value


def payload(result):
    assert result['exit_code'] == 0, result
    assert result['response'] and result['response']['ok'], result
    return result['response']['result']


def captures_by_node(events):
    nodes = {e['event_id']: (e['depth'], json.dumps(e['inputs'], sort_keys=True), e['slot'])
             for e in events if e['kind'] == 'node_start'}
    captures = {}
    for event in events:
        if event['kind'] == 'candidate_capture':
            captures.setdefault(nodes[event['node']], []).append(event['content'])
    return captures


def run(stage, access_only=False):
    before = preserved_hashes()
    output = WORKSPACE / 'results/windows-isolation'
    output.mkdir(exist_ok=True)
    private = WORKSPACE / 'isolation-private'
    protected = []
    for relative in ('oracles/answer.txt', 'assessments/labels.json', 'credentials/keys.txt', '.env'):
        path = private / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('SYNTHETIC CANARY, NO REAL SECRETS', encoding='utf-8')
        protected.append(path)
    protected.extend([WORKSPACE / 'evaluators/oracle_results/S1.json',
                      WORKSPACE / 'evaluators/oracle_results/S2-v2.json',
                      WORKSPACE / 'evaluators/oracle_results/S3.json',
                      WORKSPACE / 'results/assessment-fixtures.json',
                      WORKSPACE / 'results/researcher-only-canary.txt'])
    assert all(p.is_file() for p in protected)
    hashes = {str(p): sha(p.read_bytes()) for p in protected}
    server = socket.socket()
    server.bind(('127.0.0.1', 0))
    server.listen()
    code = f'''
import ctypes as C
from ctypes import wintypes as W
import json, os, socket, subprocess, sys
k = C.WinDLL('kernel32', use_last_error=True)
a = C.WinDLL('advapi32', use_last_error=True)
k.GetCurrentProcess.restype = W.HANDLE
k.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
k.OpenProcess.restype = W.HANDLE
k.CloseHandle.argtypes = [W.HANDLE]
k.CreateFileW.argtypes = [W.LPCWSTR, W.DWORD, W.DWORD, C.c_void_p, W.DWORD, W.DWORD, W.HANDLE]
k.CreateFileW.restype = W.HANDLE
a.OpenProcessToken.argtypes = [W.HANDLE, W.DWORD, C.POINTER(W.HANDLE)]
a.GetTokenInformation.argtypes = [W.HANDLE, C.c_int, C.c_void_p, W.DWORD, C.POINTER(W.DWORD)]
token = W.HANDLE()
assert a.OpenProcessToken(k.GetCurrentProcess(), 8, C.byref(token))
flag, size = W.DWORD(), W.DWORD()
assert a.GetTokenInformation(token, 29, C.byref(flag), C.sizeof(flag), C.byref(size))
k.CloseHandle(token)
checks = {{'appcontainer_token': bool(flag.value), 'files': []}}
for path in {list(map(str, protected))!r}:
    row = {{'path': path}}
    try:
        handle = open(path, 'rb')
        handle.close()
        row['python_denied'] = False
    except OSError as exc:
        row['python_denied'] = type(exc).__name__ == 'PermissionError'
    for label, target, rights in [('native_read', path, 0x80000000), ('extended_path_read', chr(92) * 2 + '?' + chr(92) + path, 0x80000000), ('acl_write', path, 0x40000)]:
        handle = k.CreateFileW(target, rights, 7, None, 3, 0x80, None)
        row[label] = {{'denied': handle == C.c_void_p(-1).value, 'error': C.get_last_error()}}
        if handle != C.c_void_p(-1).value:
            k.CloseHandle(handle)
    checks['files'].append(row)
handle = k.OpenProcess(0x10 | 0x400, False, {os.getpid()})
checks['parent_process_memory_denied'] = not bool(handle)
if handle:
    k.CloseHandle(handle)
try:
    subprocess.run([sys.executable, '-c', 'pass'], check=True, timeout=2)
    checks['child_process_denied'] = False
except OSError as exc:
    checks['child_process_denied'] = True
    checks['child_process_error'] = exc.winerror
try:
    with socket.socket() as peer:
        peer.settimeout(0.5)
        peer.connect(('127.0.0.1', {server.getsockname()[1]}))
    checks['host_service_denied'] = False
except OSError as exc:
    checks['host_service_denied'] = True
    checks['host_service_error'] = exc.winerror
checks['environment_names'] = sorted(os.environ)
with open('scratch-test.txt', 'w', encoding='utf-8') as public:
    public.write('public scratch')
with open('scratch-test.txt', encoding='utf-8') as public:
    checks['scratch_read_write'] = public.read() == 'public scratch'
checks['public_context'] = context
answer['content'] = json.dumps(checks, sort_keys=True)
answer['ready'] = True
'''
    compile(code, '<isolation-probe>', 'exec')
    try:
        result = launch(stage, {'operation': 'probe', 'fixture': {
            'name': 'os_isolation', 'responses': [block(code)], 'expected': None}}, timeout=15)
    finally:
        server.close()
    write_json(output / 'access-probe.json', result)
    runtime = payload(result)
    assert runtime['error'] is None, {'error': runtime['error'], 'python_errors': [e.get('stderr') for e in runtime['events'] if e.get('kind') == 'python_result']}
    assert runtime['response'] is not None, runtime
    access = json.loads(runtime['response'])
    assert access['appcontainer_token']
    for row in access['files']:
        assert row['python_denied'], row
        for key in ('native_read', 'extended_path_read', 'acl_write'):
            assert row[key]['denied'] and row[key]['error'] == 5, row
    for key in ('parent_process_memory_denied', 'child_process_denied', 'host_service_denied', 'scratch_read_write'):
        assert access[key], (key, access)
    assert access['public_context'] == 'fixture context'
    allowed_environment = {'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'USERPROFILE', 'PATH', 'LOCALAPPDATA', 'APPDATA'}
    assert set(access['environment_names']) <= allowed_environment, access['environment_names']
    assert hashes == {str(p): sha(p.read_bytes()) for p in protected}
    print(f'PASS: AppContainer token; {len(protected)} protected paths through Python/native/extended paths; ACL tampering; process/memory/host-service denial; public scratch', flush=True)
    if access_only:
        assert before == preserved_hashes()
        prior = json.loads((output / 'summary.json').read_text())
        prior['protected_path_count'] = len(protected)
        prior['access_probe_refreshed_without_repeating_equivalence'] = True
        write_json(output / 'summary.json', prior)
        return prior
    comparisons = []
    for fixture in FIXTURES:
        row = launch(stage, {'operation': 'fixture', 'fixture': fixture.name}, timeout=15)
        write_json(output / (fixture.name + '.json'), row)
        isolated = payload(row)
        prior = json.loads((WORKSPACE / 'results/equivalence' / (fixture.name + '.json')).read_text(encoding='utf-8'))
        control = prior['control']
        assert isolated['response'] == control['response'] == fixture.expected, fixture.name
        assert isolated['error'] == control['error'] == fixture.error, fixture.name
        def ordered(requests):
            return sorted(json.dumps({k:v for k,v in r.items() if k != 'attempt'}, sort_keys=True) for r in requests)
        assert ordered(isolated['requests']) == ordered(control['requests']), fixture.name
        assert comparable(isolated['trajectory']) == comparable(control['trajectory']), fixture.name
        before_captures = captures_by_node(prior['instrumented']['events'])
        after_captures = captures_by_node(isolated['events'])
        assert before_captures == after_captures, fixture.name
        comparisons.append({'fixture': fixture.name, 'passed': True, 'elapsed_seconds': row['elapsed_seconds']})
        print('PASS: ' + fixture.name, flush=True)
    try:
        launch(stage, {'operation': 'probe', 'fixture': {'name': 'hang', 'responses': [block('while True:\n    pass')], 'expected': None}}, timeout=2)
        raise AssertionError('Expected timeout')
    except TimeoutError:
        print('PASS: external job timeout', flush=True)
    assert before == preserved_hashes()
    summary = {'isolation_pass': True, 'protected_path_count': len(protected),
               'equivalence_pass_count': len(comparisons), 'equivalence_fail_count': 0,
               'comparisons': comparisons, 'external_timeout_pass': True,
               'protected_hashes_unchanged': True, 'no_live_requests': True,
               'credentials_tested': 'synthetic canaries and strict environment allowlist; no real credential opened',
               'baseline_suite_repeated': False, 'parent_host_service_denied': access['host_service_denied'],
               'boundary': 'AppContainer, zero capabilities, clean environment, no inherited handles, one-process kill-on-close Job'}
    write_json(output / 'summary.json', summary)
    return summary
