"""Targeted offline broker integration checks. No benchmark or old suite reruns."""

import json
import sys
import time
import unittest
from collections import Counter
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from threading import Lock
from unittest.mock import Mock, patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.official_baseline_h2_h5_h6.common import WORKSPACE, preserved_hashes, write_json
from experiments.official_baseline_h2_h5_h6.fixtures.programs import block, finish
from experiments.official_baseline_h2_h5_h6.runners.broker import OpenRouterHTTP, provider_body, routed_body, run_isolated
from experiments.official_baseline_h2_h5_h6.runners.budget import Ledger, Limits, SYNTHETIC_RATES
from experiments.official_baseline_h2_h5_h6.runners.windows_boundary import read_worker_file


class FakeProvider:
    synthetic = True

    def __init__(self, root=None, failure=None, cost=None):
        self.root = root or block(finish("'done'"))
        self.failure, self.cost = failure, cost
        self.calls = []
        self.lock = Lock()

    def __call__(self, body, timeout):
        with self.lock:
            self.calls.append(body)
        if self.failure == 'timeout':
            raise TimeoutError('synthetic timeout')
        messages = body['messages']
        instruction = str(messages[1]) if len(messages) > 1 else str(messages[0])
        if len(messages) > 1 and 'child-one' in instruction:
            content = block("a = rlm_query('leaf-instruction', 'leaf context')\nb = llm_query('deeper-plain')\n" + finish("a + ':' + b"))
        elif len(messages) > 1 and 'child-simple' in instruction:
            content = block(finish("'C'"))
        elif len(messages) > 1:
            content = self.root
        else:
            content = 'L' if 'leaf-instruction' in instruction else 'D' if 'deeper-plain' in instruction else '7' if 'plain-seven' in instruction else 'B'
            time.sleep(0.03)
        response = {'choices': [{'message': {'content': content}}]}
        if self.failure != 'unknown_usage':
            response['usage'] = {'prompt_tokens': 10, 'completion_tokens': 5}
            if self.cost is not None:
                response['usage']['cost'] = self.cost
        return response


RECORDS = []


class BrokerIntegration(unittest.TestCase):
    def execute(self, provider, limits=Limits(), ledger=None):
        ledger = ledger or Ledger(SYNTHETIC_RATES, limits)
        record = run_isolated('public broker context', 'broker integration root', ledger,
                              provider, lambda model, messages: 100)
        RECORDS.append(record['run_id'])
        self.assertTrue(all(record['cleanup'].values()), record)
        self.assertFalse(Path(record['scratch_path']).exists())
        return record, ledger

    def test_actual_runtime_routing_concurrency_and_accounting(self):
        code = """import os
from pathlib import Path
outbox = Path(os.environ['TEMP']).parent.parent / 'mailbox' / 'outbox'
denied = False
try:
    with open(outbox / 'forged.json', 'w') as stream:
        stream.write('{}')
except OSError:
    denied = True
p = llm_query('plain-seven')
b = llm_query_batched(['plain-b', 'plain-b'])
c = rlm_query('child-one', 'child context')
r = rlm_query_batched([('child-simple', 'same'), ('child-simple', 'same')])
""" + finish("str(denied) + '|' + p + '|' + ','.join(b) + '|' + c + '|' + ','.join(r)")
        provider = FakeProvider(block(code))
        record, ledger = self.execute(provider)
        self.assertEqual(record['status'], 'completed', record.get('reason') or record['result'])
        self.assertEqual(record['result']['response']['result']['response'], 'True|7|B,B|L:D|C,C')
        self.assertEqual(len(provider.calls), 9)
        self.assertEqual(Counter(c['model'] for c in provider.calls),
                         {'openai/gpt-5': 5, 'openai/gpt-5-nano': 4})
        self.assertTrue(all(c['max_completion_tokens'] == 32768 for c in provider.calls))
        tickets = list(ledger.tickets.values())
        self.assertEqual(len(tickets), 9)
        self.assertTrue(all(t['state'] == 'reconciled' and t['reserved'] == 0 for t in tickets))
        self.assertEqual(ledger.exposure(), Decimal('0.00018'))
        self.assertEqual(len(record['provider_records']), 9)
        self.assertTrue(all(r['delivered'] for r in record['provider_records']))
        self.assertTrue(any(e['kind'] == 'recursive_dispatch' for e in record['observed_prefix']))
        dispatches = [e for e in record['observed_prefix'] if e['kind'] == 'provider_dispatch']
        self.assertEqual(len(dispatches), 9)
        plain_slots = [e['slot'] for e in dispatches if e['request'] == 'plain-b']
        self.assertEqual(sorted(plain_slots), [0, 1])
        from experiments.official_baseline_h2_h5_h6.evaluators.assessment import prefix_packet
        packet = prefix_packet(record['observed_prefix'], len(record['observed_prefix']), root_visible_only=True)
        self.assertEqual(len(packet['events']), 1)
        journal = json.loads((WORKSPACE / 'results/broker' / (record['run_id'] + '.journal.json')).read_text())
        self.assertTrue(journal['finalized'])
        self.assertEqual(len(journal['ledger']['tickets']), 9)

    def test_attempt_denial_kills_instead_of_returning_helper_error(self):
        provider = FakeProvider(block("try:\n    x = llm_query('plain-seven')\nexcept Exception:\n    x = 'caught'\n" + finish("'must-not-complete'")))
        record, ledger = self.execute(provider, replace(Limits(), attempts=1))
        self.assertEqual(record['status'], 'resource_censored', record)
        self.assertEqual(record['reason'], 'attempt_limit')
        self.assertEqual(len(provider.calls), 1)
        self.assertIsNone(record['result'])
        self.assertGreater(len(record['observed_prefix']), 0)

    def test_run_and_shared_campaign_admission(self):
        provider = FakeProvider()
        record, _ = self.execute(provider, replace(Limits(), run_usd=Decimal('0.01')))
        self.assertEqual(record['reason'], 'run_budget')
        self.assertEqual(len(provider.calls), 0)
        ledger = Ledger(SYNTHETIC_RATES, replace(Limits(), campaign_usd=Decimal('0.08')))
        first, _ = self.execute(FakeProvider(cost='0.07'), ledger=ledger)
        self.assertEqual(first['status'], 'completed', first)
        restored = Ledger(SYNTHETIC_RATES, ledger.limits)
        restored.restore(ledger.snapshot())
        ledger = restored
        second_provider = FakeProvider()
        second, _ = self.execute(second_provider, ledger=ledger)
        self.assertEqual(second['reason'], 'campaign_budget')
        self.assertEqual(len(second_provider.calls), 0)
        self.assertEqual(ledger.exposure(), Decimal('0.07'))
        self.assertNotEqual(first['profile_name'], second['profile_name'])

    def test_unknown_usage_timeout_and_cost_overrun(self):
        for provider, reason in [(FakeProvider(failure='unknown_usage'), 'usage_unknown'),
                                 (FakeProvider(failure='timeout'), 'usage_unknown'),
                                 (FakeProvider(cost='0.5'), 'cost_exceeded_reservation')]:
            with self.subTest(reason=reason, failure=provider.failure):
                record, ledger = self.execute(provider)
                self.assertEqual(record['status'], 'resource_censored', record)
                self.assertEqual(record['reason'], reason)
                self.assertEqual(len(provider.calls), 1)  # no hidden retries
                if reason == 'usage_unknown':
                    self.assertGreater(next(iter(ledger.tickets.values()))['reserved'], 0)
                else:
                    self.assertEqual(ledger.exposure(), Decimal('0.5'))

    def test_unknown_model_and_deadline(self):
        provider = FakeProvider(block("x = rlm_query('child', 'ctx', model='unpriced')\n" + finish("x")))
        record, _ = self.execute(provider)
        self.assertEqual(record['reason'], 'unpriced_model')
        self.assertEqual(len(provider.calls), 1)
        record, _ = self.execute(FakeProvider(block('while True:\n    pass')), replace(Limits(), seconds=4))
        self.assertEqual(record['status'], 'resource_censored', record)
        self.assertIn('wall_clock', record['ledger']['runs'][record['run_id']]['stop_reason'])

    def test_request_policy_and_bounded_read(self):
        request = {'model': 'openai/gpt-5', 'prompt': 'hello', 'sampling_args': {'max_tokens': 32768},
                   'node': None, 'action': None, 'slot': None}
        self.assertEqual(provider_body(request, 32768)['messages'], [{'role': 'user', 'content': 'hello'}])
        for patch_value in ({'sampling_args': {'max_tokens': 999999}}, {'ticket': 'forged'},
                            {'node': float('nan')},
                            {'prompt': [{'role': 'user', 'content': {'image_url': 'not allowed'}}]}):
            with self.assertRaises(ValueError):
                provider_body({**request, **patch_value}, 32768)
        with self.assertRaises(ValueError):
            read_worker_file(WORKSPACE / 'runners/pilot.json', 2)
        connection = Mock()
        connection.getresponse.return_value.status = 200
        wire_reply = {'choices': [{'message': {'content': 'wire mock'}}],
                      'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'cost': 0.00002}, 'id': 'synthetic-id'}
        connection.getresponse.return_value.read.return_value = json.dumps(wire_reply).encode()
        with patch('http.client.HTTPSConnection', return_value=connection):
            transport = OpenRouterHTTP('SYNTHETIC-NOT-A-CREDENTIAL')
            body = provider_body(request, 32768)
            self.assertEqual(transport(body, 2), wire_reply)
            self.assertEqual(connection.request.call_args.args, ('POST', '/api/v1/chat/completions'))
            self.assertEqual(json.loads(connection.request.call_args.kwargs['body']), routed_body(body))
            connection.request.reset_mock()
            connection.getresponse.return_value.status = 429
            with self.assertRaises(RuntimeError):
                transport(body, 2)
            self.assertEqual(connection.request.call_count, 1)
            connection.getresponse.return_value.status = 200
            connection.getresponse.return_value.read.return_value = b'{"usage": NaN}'
            with self.assertRaises(ValueError):
                transport(body, 2)
            connection.request.reset_mock()
            connection.connect.side_effect = lambda: time.sleep(0.03)
            with self.assertRaises(TimeoutError):
                transport(body, 0.01)
            self.assertEqual(connection.request.call_count, 0)


if __name__ == '__main__':
    before = preserved_hashes()
    with patch('http.client.HTTPSConnection', side_effect=AssertionError('No live HTTP allowed')):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(BrokerIntegration)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    unchanged = before == preserved_hashes()
    write_json(WORKSPACE / 'results/broker-summary.json', {
        'test_methods': result.testsRun, 'success': result.wasSuccessful() and unchanged,
        'failures': [{'test': str(t), 'traceback': trace} for t, trace in result.failures + result.errors],
        'run_ids': RECORDS, 'protected_files_unchanged': unchanged, 'api_requests': 0,
        'existing_suite_repeated': False, 'datasets_or_old_equivalence_repeated': False,
    })
    raise SystemExit(not (result.wasSuccessful() and unchanged))
