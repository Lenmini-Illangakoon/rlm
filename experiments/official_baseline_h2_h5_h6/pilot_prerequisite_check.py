"""Only the new pilot policy, accounting, and observer deltas. No live transport."""

import copy
import json
import sys
import tempfile
import unittest
from concurrent.futures import Future
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.official_baseline_h2_h5_h6.common import WORKSPACE, preserved_hashes, write_json
from experiments.official_baseline_h2_h5_h6.runners import broker, pilot_policy as policy, pilot_runner
from experiments.official_baseline_h2_h5_h6.runners.budget import AdmissionDenied, Ledger, Limits, SYNTHETIC_RATES
from experiments.official_baseline_h2_h5_h6.runners.provider_preflight import MODELS, RATES


def saved_response():
    return json.loads((WORKSPACE / 'results/provider-preflight/live-attempt-two.json').read_text())['requests'][0]['provider_response']


class PolicyChecks(unittest.TestCase):
    def test_general_input_bound_and_cap_without_prompt_changes(self):
        messages = [{'role': 'system', 'content': 'system'}, {'role': 'user', 'content': '漢字🙂\n\\"'}]
        before = copy.deepcopy(messages)
        bound = policy.input_bound(MODELS[0], messages)
        self.assertGreater(bound, sum(len(m['content'].encode()) for m in messages) + 1024)
        self.assertEqual(messages, before)
        empty = [{'role': 'user', 'content': ''}]
        allowance = policy.input_bound(MODELS[0], empty)
        exact = [{'role': 'user', 'content': 'x' * (64000 - allowance)}]
        self.assertEqual(policy.input_bound(MODELS[0], exact), 64000)
        ledger = Ledger(RATES)
        ledger.start('bound')
        ledger.admit('bound', MODELS[0], policy.input_bound(MODELS[0], exact), 32768)
        exact[0]['content'] += 'x'
        with self.assertRaises(AdmissionDenied):
            ledger.admit('bound', MODELS[0], policy.input_bound(MODELS[0], exact), 32768)
        self.assertEqual(ledger.runs['bound']['attempts'], 1)

    def test_usage_conflict_cost_once_and_failure_gates(self):
        response = saved_response()
        ticket = {'input_bound': 2000, 'output_bound': 32768}
        checked = policy.verify_usage(response, MODELS[0], ticket)
        self.assertTrue(checked['reasoning_detail_conflict'])
        self.assertEqual(checked['conservative_output_count'], 126)
        self.assertEqual(checked['reported_cost_usd'], '0.00034375')
        for kind in ('reasoning_bound', 'cost', 'total', 'route'):
            value = copy.deepcopy(response)
            if kind == 'reasoning_bound': value['usage']['completion_tokens_details']['reasoning_tokens'] = 32768
            if kind == 'cost': value['usage']['cost'] = 0.5
            if kind == 'total': value['usage']['total_tokens'] += 1
            if kind == 'route': value['provider'] = 'Unapproved'
            with self.subTest(kind=kind), self.assertRaises(policy.PilotVerificationError):
                policy.verify_usage(value, MODELS[0], ticket)

    def test_broker_uncertainty_retains_hold_and_raw_evidence(self):
        with tempfile.TemporaryDirectory(dir=WORKSPACE / 'results') as temporary:
            root = Path(temporary)
            (root / 'outbox').mkdir()
            ledger = Ledger(RATES)
            ledger.start('uncertain')
            ticket = ledger.admit('uncertain', MODELS[0], 2000, 32768)
            reserved = ledger.exposure()
            value = saved_response()
            value['usage']['completion_tokens_details']['reasoning_tokens'] = 32768
            instance = broker.Broker(root, ledger, 'uncertain', SimpleNamespace(synthetic=False, pilot_policy_revision=policy.PILOT_POLICY_REVISION), policy.input_bound)
            future = Future()
            future.set_result(value)
            record = {'body': {'model': MODELS[0]}, 'delivered': False}
            instance.records.append(record)
            instance.pending[future] = ('a' * 32, ticket, record)
            with patch.object(broker, 'WORKSPACE', root):
                instance.settle()
                instance.close()
            self.assertEqual(ledger.exposure(), reserved)
            self.assertEqual(record['provider_response'], value)
            self.assertFalse(record['delivered'])
            self.assertEqual(list((root / 'outbox').iterdir()), [])
            self.assertEqual(ledger.runs['uncertain']['stop_reason'], 'telemetry_budget_uncertain')

    def test_campaign_seed_once_exact_exception_and_exact_run_authorization(self):
        transport = broker.OpenRouterHTTP('SYNTHETIC-NOT-A-CREDENTIAL')
        transport.pilot_policy_revision = policy.PILOT_POLICY_REVISION
        def new_ledger():
            return Ledger(RATES, Limits(), rates_kind='openrouter-public-prices-2026-11-24')
        with tempfile.TemporaryDirectory(dir=WORKSPACE / 'results') as temporary, patch.object(pilot_runner, 'WORKSPACE', Path(temporary)):
            first = pilot_runner.Pilot('check', new_ledger(), transport, policy.input_bound, policy.BOUND_REVISION)
            again = pilot_runner.Pilot('check', new_ledger(), transport, policy.input_bound, policy.BOUND_REVISION)
            self.assertEqual(again.ledger.exposure(), Decimal('0.44882910'))
            self.assertEqual(len(again.ledger.tickets), 3)
            self.assertEqual(first.policy_hash, again.policy_hash)
            self.assertIn('approved_endpoints', again.policy['live_host'])
            with self.assertRaises(RuntimeError): again.run_next()
            with self.assertRaises(ValueError): again.run_next(authorized_run_id='S2-R01')
            fake = {'run_id': 'broker-' + 'b' * 32, 'status': 'completed', 'cleanup': {'all': True}}
            with patch.object(pilot_runner, 'run_isolated', return_value=fake) as run:
                again.run_next(authorized_run_id='S1-R01')
                run.assert_called_once()
                with self.assertRaises(ValueError): again.run_next(authorized_run_id='S1-R01')
            resumed = pilot_runner.Pilot('check', new_ledger(), transport, policy.input_bound, policy.BOUND_REVISION)
            resumed.ledger.start('unresolved-pilot')
            ticket = resumed.ledger.admit('unresolved-pilot', MODELS[0], 2000, 32768)
            resumed.ledger.reconcile(ticket, None, None)
            with self.assertRaisesRegex(ValueError, 'Unresolved provider exposure'):
                resumed.run_next(authorized_run_id='S2-R01')


class EvidenceProvider:
    synthetic = True
    def __init__(self):
        self.root_turn = 0
    def __call__(self, body, timeout):
        messages = body['messages']
        if len(messages) == 1:
            content = 'PLAIN'
        elif 'child-evidence' in str(messages[1]):
            content = "```repl\nanswer['content'] = 'CHILD'\nanswer['ready'] = True\n```"
        else:
            self.root_turn += 1
            content = ("```repl\nx = llm_query('plain-evidence')\ny = rlm_query('child-evidence', 'public child')\nprint('PREFIX' + 'x' * 24000 + 'TAIL')\n1 / 0\n```" if self.root_turn == 1 else
                       "```repl\nanswer['content'] = 'RECOVERED'\nanswer['ready'] = True\n```")
        return {'choices': [{'message': {'content': content}}], 'usage': {'prompt_tokens': 10, 'completion_tokens': 5}}


class RuntimeEvidenceCheck(unittest.TestCase):
    def test_actual_appcontainer_identity_and_research_evidence(self):
        if '--reassess-runtime' in sys.argv:
            reference = json.loads((WORKSPACE / 'results/pilot-runtime-evidence-reference.json').read_text())
            record = json.loads((WORKSPACE / 'results/broker' / (reference['run_id'] + '.json')).read_text())
        else:
            record = broker.run_isolated('public context', 'root evidence check', Ledger(SYNTHETIC_RATES), EvidenceProvider(), policy.input_bound)
        write_json(WORKSPACE / 'results/pilot-runtime-evidence-reference.json', {'run_id': record['run_id'], 'status': record['status']})
        self.assertEqual(record['status'], 'completed', record['result'] or record['reason'])
        self.assertTrue(all(record['cleanup'].values()))
        self.assertEqual(record['result']['boundary'], 'appcontainer-job')
        result = record['result']['response']['result']
        self.assertEqual(result['response'], 'RECOVERED')
        self.assertEqual(result['iteration_count'], 2)
        events = record['observed_prefix']
        self.assertEqual([e['seq'] for e in events], list(range(1, len(events) + 1)))
        identity = next(e for e in events if e['kind'] == 'runtime_identity')
        self.assertEqual(identity['class_module'], 'rlm.core.rlm')
        self.assertEqual(identity['class_name'], 'RLM')
        self.assertFalse(identity['rootcheck'])
        self.assertIn('payload', identity['source_file'])
        self.assertEqual(identity['source_hashes']['rlm/core/rlm.py'], preserved_hashes()['rlm/core/rlm.py'])
        py = next(e for e in events if e['kind'] == 'python_result' and 'PREFIX' in e.get('stdout', ''))
        self.assertIn('TAIL', py['stdout'])
        self.assertIn('ZeroDivisionError', py['stderr'])
        self.assertIsNotNone(py['action'])
        self.assertTrue(any(e['kind'] == 'recursive_result' and e.get('metadata') for e in events))
        self.assertTrue(any(e['kind'] == 'iteration_selection' and e['iteration_time'] is not None for e in events))
        formatted = next(e for e in events if e['kind'] == 'formatted_results')
        # The generated assistant code contains the literal TAIL; only the user
        # REPL-output message is truncated by the official formatter.
        self.assertTrue(all('TAIL' not in m['content'] for m in formatted['messages'] if m['role'] == 'user'))
        root = next(e['event_id'] for e in events if e['kind'] == 'node_start' and e['depth'] == 0)
        dispatches = [e for e in events if e['kind'] == 'provider_dispatch' and e['owner_node'] == root and isinstance(e['request'], list)]
        self.assertEqual(len(dispatches), 2)
        for message in formatted['messages']:
            self.assertIn(message, dispatches[1]['request'])
        self.assertTrue(any(e['kind'] == 'actual_return' and e['node'] == root and e['content'] == result['response'] for e in events))
        self.assertEqual(len(record['provider_records']), 4)
        self.assertTrue(all(Path(p).exists() for p in record['trace_files'].values()))


if __name__ == '__main__':
    runtime = '--runtime' in sys.argv or '--reassess-runtime' in sys.argv
    before = preserved_hashes()
    # The AppContainer needs local sockets; its unchanged offline guard blocks internet.
    guard = patch('http.client.HTTPSConnection', side_effect=AssertionError('No provider calls allowed'))
    with guard:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RuntimeEvidenceCheck if runtime else PolicyChecks))
    unchanged = before == preserved_hashes()
    write_json(WORKSPACE / 'results' / ('pilot-runtime-evidence-check.json' if runtime else 'pilot-policy-check.json'),
               {'tests_run': result.testsRun, 'success': result.wasSuccessful(), 'protected_files_unchanged': unchanged,
                'provider_api_requests': 0, 'credential_access': False, 'completed_suites_repeated': False,
                'runtime_evidence_reused': '--reassess-runtime' in sys.argv,
                'failures': [str(t) for t, _ in result.failures + result.errors]})
    raise SystemExit(not (result.wasSuccessful() and unchanged))
