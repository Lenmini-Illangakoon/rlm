"""Materialize approved data; acceptance fails on any oracle discrepancy."""

import json
import subprocess
from pathlib import Path

from ..common import REPO, WORKSPACE, preserved_hashes, sha, write_json
from ..evaluators.oracles import SOLVERS, VERSION as EVALUATOR_VERSION
from .generate import S2_QUERY, S3_SPEC, VERSION, generate_s2

EXPECTED = {
    'S1': ('c5118358cb1320e901483b37cbdef3577d1db8188a18f6b9bcd7b873a89ceaff', '2b2906e3bef0677692633e3f297321b87a5651230ff51dd38ff81d668ae10a65'),
    'S3': ('55075334b0f7080a790dda9a4b5582de41cd7a7ce38f424a9af39c52f4dd9009', 'ea496d7451d275dd1ecf72c90c9b6f7a271c5812cfe80950194ac3b15572e4ce'),
}


def historical_bytes(history: Path, relative: str, expected: str) -> tuple[bytes, dict]:
    source = history / relative
    data = source.read_bytes()
    provenance = {'path': relative, 'working_sha256': sha(data)}
    if sha(data) != expected:
        # The archive's Git object, not newline normalization, is the authority.
        command = ['git', '-c', f'safe.directory={history.as_posix()}', '-C', str(history)]
        revision = subprocess.run(command + ['rev-parse','HEAD'], check=True, capture_output=True).stdout.decode().strip()
        data = subprocess.run(command + ['show', f'{revision}:{relative}'], check=True, capture_output=True).stdout
        provenance.update({'retrieval': 'git_blob', 'commit': revision})
    else:
        provenance['retrieval'] = 'archive_file'
    if sha(data) != expected:
        raise ValueError(f'Historical checksum mismatch: {relative}')
    provenance['frozen_sha256'] = sha(data)
    return data, provenance


def prepare() -> dict:
    before = WORKSPACE / 'results/integrity-before.json'
    current = preserved_hashes()
    if before.exists():
        if json.loads(before.read_text()) != current:
            raise ValueError('Protected files changed since preparation began')
    else:
        write_json(before, current)
    history = REPO.parent / 'rlm-minimal/rlm-minimal'
    manifest = {'version': 'approved-offline-1', 'accepted': False, 'scenarios': {}}
    inputs = {}
    for scenario, family, seed in [('S1','exp3b_outcome_mismatch',301), ('S3','exp3f_over_iteration',701)]:
        folder = f'experiments/phase3_failure_analysis/{family}/instances/seed_{seed}'
        target = WORKSPACE / 'tasks/data' / scenario
        provenance = {}
        payload = []
        for name, expected in zip(['context.txt','query.txt'],EXPECTED[scenario]):
            frozen = target / name
            if frozen.exists() and (scenario == 'S1' or name == 'context.txt'):
                data = frozen.read_bytes()
                if sha(data) != expected:
                    raise ValueError(f'Existing frozen file changed: {frozen}')
                old = WORKSPACE / 'tasks/dataset_manifest.json'
                provenance[name] = json.loads(old.read_text())['scenarios'][scenario]['provenance'][name]
            else:
                data, provenance[name] = historical_bytes(history, f'{folder}/{name}', expected)
            payload.append(data)
        if scenario == 'S3':
            payload[1] = payload[1].rstrip(b'\r\n') + b'\n\n' + S3_SPEC.encode()
        inputs[scenario] = (*payload, provenance)
    first, second = generate_s2(), generate_s2()
    if first != second:
        raise ValueError('S2 nondeterministic generation')
    inputs['S2-v2'] = (first, S2_QUERY.encode(), {'method': VERSION})
    for scenario in ['S1','S2-v2','S3']:
        context, query, provenance = inputs[scenario]
        oracle = SOLVERS[scenario](context)
        if scenario == 'S1':
            historical = json.loads((history / 'experiments/phase3_failure_analysis/exp3b_outcome_mismatch/instances/seed_301/oracle.json').read_text())
            if oracle['selected_ids'] != historical['final_sorted_order_ids'] or oracle['total'] != 1361 or len(oracle['selected_ids']) != 60:
                raise ValueError('S1 oracle discrepancy')
        elif scenario == 'S2-v2':
            expected_selected = [
                {'id':'SH-10106','requested':6883,'sources':['R-106','W-106','Q-106','H-106']},
                {'id':'SH-10068','requested':6846,'sources':['R-068','W-068','Q-068','H-068']},
                {'id':'SH-10097','requested':6809,'sources':['R-097','W-097','Q-097','H-097']},
            ]
            if oracle['selected'] != expected_selected or oracle['total'] != 20538 or oracle['eligible_count'] != 100:
                raise ValueError('S2 oracle discrepancy; acceptance stopped')
            if oracle['ranked_ids'][3] != 'SH-10138' or oracle['joined']['SH-10128']['eligible']:
                raise ValueError('S2 boundary discrepancy')
        elif oracle['selected_ids'] != [3731,4637] or oracle['product'] != 17300647 or oracle['eligible_count'] != 104:
            raise ValueError('S3 oracle discrepancy')
        target = WORKSPACE / 'tasks/data' / scenario
        target.mkdir(parents=True, exist_ok=True)
        (target/'context.txt').write_bytes(context)
        (target/'query.txt').write_bytes(query)
        oracle_path = WORKSPACE / 'evaluators/oracle_results' / f'{scenario}.json'
        write_json(oracle_path, oracle)
        manifest['scenarios'][scenario] = {
            'context_sha256':sha(context), 'query_sha256':sha(query), 'context_bytes':len(context), 'query_bytes':len(query),
            'oracle_sha256':sha(oracle_path.read_bytes()), 'generator_version': VERSION if scenario == 'S2-v2' else 'frozen-historical-bytes-1',
            'evaluator_version': EVALUATOR_VERSION, 'provenance':provenance,
        }
    manifest['accepted'] = True
    write_json(WORKSPACE/'tasks/dataset_manifest.json', manifest)
    return manifest
