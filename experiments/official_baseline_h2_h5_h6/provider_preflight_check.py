"""Targeted offline checks only. Socket access is forbidden throughout the suite."""

import json
import sys
import tempfile
import unittest
import uuid
from concurrent.futures import Future
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.official_baseline_h2_h5_h6.common import WORKSPACE, preserved_hashes, write_json
from experiments.official_baseline_h2_h5_h6.runners import broker, provider_preflight as preflight
from experiments.official_baseline_h2_h5_h6.runners.budget import AdmissionDenied, Ledger


class OfflineHTTP(broker.OpenRouterHTTP):
    synthetic = True


def response(model, cached=0):
    cost = preflight.RATES[model].cost(10 - cached, 5) + preflight.CACHE_RATES[model] * cached / Decimal(1000000)
    return {'id': 'offline-fixture', 'model': model, 'provider': 'OpenAI', 'service_tier': 'default',
            'openrouter_metadata': {'attempt': 1, 'requested': model, 'is_byok': False,
                'endpoints': {'available': [{'selected': True, 'provider': 'OpenAI', 'model': model}]}},
            'choices': [{'finish_reason': 'stop', 'message': {'content': '323'}}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15,
                      'completion_tokens_details': {'reasoning_tokens': 3},
                      'prompt_tokens_details': {'cached_tokens': cached}, 'cost': float(cost), 'is_byok': False}}


class ProviderPreflightChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='provider-check-', dir=WORKSPACE / 'results')
        self.root = Path(self.temporary.name).resolve()
        assert self.root.parent == (WORKSPACE / 'results').resolve()
        self.addCleanup(self.temporary.cleanup)
        self.path = self.root / 'record.json'
        self.connections = []

    def execute(self, replies, *, status=200, clock=None):
        def connection(host, timeout):
            self.assertEqual(host, 'openrouter.ai')
            self.assertGreater(timeout, 0)
            self.assertLessEqual(timeout, 300)
            conn = Mock()
            conn.sock = None
            conn.getresponse.return_value.status = status
            reply = replies[len(self.connections)]
            if isinstance(reply, Exception):
                conn.getresponse.return_value.read.side_effect = reply
            else:
                conn.getresponse.return_value.read.return_value = json.dumps(reply).encode()

            def dispatched(*args, **kwargs):
                saved = json.loads(self.path.read_text())
                self.assertEqual(saved['status'], 'in_progress')
                self.assertEqual(len(saved['requests']), len(self.connections))
                row = saved['requests'][-1]
                ticket = saved['ledger']['tickets'][row['ticket']]
                self.assertEqual(ticket['state'], 'in_flight')
                self.assertGreater(Decimal(ticket['reserved']), 0)
                self.assertEqual(row['body'], json.loads(kwargs['body']))
                self.assertEqual(kwargs['headers']['X-OpenRouter-Metadata'], 'enabled')
                self.assertEqual(args, ('POST', '/api/v1/chat/completions'))
                if len(self.connections) == 2:
                    self.assertTrue(saved['requests'][0]['accepted'])
                    previous = saved['requests'][0]['ticket']
                    self.assertEqual(saved['ledger']['tickets'][previous]['state'], 'reconciled')
            conn.request.side_effect = dispatched
            self.connections.append(conn)
            return conn

        with patch('http.client.HTTPSConnection', side_effect=connection):
            options = {} if clock is None else {'clock': clock}
            return preflight.run(OfflineHTTP('SYNTHETIC-NOT-A-CREDENTIAL'), evidence_path=self.path, **options)

    def test_two_requests_policy_accounting_and_no_replay(self):
        result = self.execute([response(preflight.MODELS[0]), response(preflight.MODELS[1], cached=2)])
        self.assertEqual(result['status'], 'passed', result)
        self.assertEqual(len(self.connections), 2)
        proposal = json.loads((WORKSPACE / 'provider-preflight-proposal.json').read_text())
        for actual, expected in zip(result['requests'], proposal['requests']):
            self.assertEqual(actual['body'], expected['body'])
            self.assertEqual(actual['verification']['reasoning_tokens'], 3)
        self.assertEqual(result['ledger']['campaign_exposure_usd'], '0.0000650')
        self.assertEqual(len(result['ledger']['tickets']), 2)
        with patch('http.client.HTTPSConnection', side_effect=AssertionError('Replay must not dispatch')):
            with self.assertRaises(ValueError):
                preflight.run(OfflineHTTP('SYNTHETIC-NOT-A-CREDENTIAL'), evidence_path=self.path)
        self.assertNotIn('SYNTHETIC-NOT-A-CREDENTIAL', self.path.read_text())

    def test_broker_errors_never_delivered_and_length_preserved(self):
        for kind in ('top', 'choice', 'finish', 'missing_usage', 'length', 'stop'):
            with self.subTest(kind=kind):
                result = response(preflight.MODELS[0])
                error = {'code': 502, 'message': 'synthetic interruption'}
                if kind == 'top':
                    result['error'] = error
                if kind == 'choice':
                    result['choices'][0]['error'] = error
                if kind in ('finish', 'missing_usage'):
                    result['choices'][0]['finish_reason'] = 'error'
                if kind == 'missing_usage':
                    del result['usage']
                if kind == 'length':
                    result['choices'][0]['finish_reason'] = 'length'
                mailbox = self.root / kind
                (mailbox / 'outbox').mkdir(parents=True)
                ledger = Ledger(preflight.RATES)
                ledger.start(kind)
                ticket = ledger.admit(kind, preflight.MODELS[0], 64000, 32768)
                instance = broker.Broker(mailbox, ledger, kind, SimpleNamespace(synthetic=False), preflight.literal_input_bound)
                future = Future()
                future.set_result(result)
                record = {'delivered': False}
                instance.records.append(record)
                instance.pending[future] = ('a' * 32, ticket, record)
                with patch.object(broker, 'WORKSPACE', self.root):
                    instance.settle()
                    instance.close()
                delivered = kind in ('length', 'stop')
                self.assertEqual(record['delivered'], delivered)
                self.assertEqual((mailbox / 'outbox' / ('a' * 32 + '.json')).exists(), delivered)
                self.assertEqual(record['provider_response'], result)
                if kind == 'missing_usage':
                    self.assertGreater(ledger.tickets[ticket]['reserved'], 0)
                else:
                    self.assertEqual(ledger.tickets[ticket]['state'], 'reconciled')
                    self.assertEqual(ledger.tickets[ticket]['spent'], Decimal('0.0000625'))
                if not delivered:
                    self.assertIsNotNone(ledger.runs[kind]['stop_reason'])

    def test_failure_stops_without_second_call_and_retains_exposure(self):
        for kind in ('top_error', 'choice_error', 'missing_cost', 'missing_reasoning', 'route', 'attempt',
                     'price', 'overrun', 'token_bound', 'byok', 'length', 'http_429', 'timeout'):
            with self.subTest(kind=kind):
                self.path = self.root / (kind + '.json')
                self.connections = []
                reply = response(preflight.MODELS[0])
                if kind == 'top_error':
                    reply['error'] = {'code': 502}
                elif kind == 'choice_error':
                    reply['choices'][0]['error'] = {'code': 502}
                elif kind == 'missing_cost':
                    del reply['usage']['cost']
                elif kind == 'missing_reasoning':
                    del reply['usage']['completion_tokens_details']
                elif kind == 'route':
                    reply['provider'] = 'Azure'
                elif kind == 'attempt':
                    reply['openrouter_metadata']['attempt'] = 2
                elif kind == 'price':
                    reply['usage']['cost'] = 0.01
                elif kind == 'overrun':
                    reply['usage']['cost'] = 0.51
                elif kind == 'token_bound':
                    reply['usage']['completion_tokens'] = 32769
                elif kind == 'byok':
                    reply['usage']['is_byok'] = True
                elif kind == 'length':
                    reply['choices'][0]['finish_reason'] = 'length'
                elif kind == 'timeout':
                    reply = TimeoutError('synthetic timeout')
                record = self.execute([reply], status=429 if kind == 'http_429' else 200)
                self.assertEqual(record['status'], 'stopped', record)
                self.assertEqual(len(self.connections), 1)
                self.assertFalse(record['requests'][0]['accepted'])
                ticket = next(iter(record['ledger']['tickets'].values()))
                if kind in ('missing_cost', 'http_429', 'timeout'):
                    self.assertEqual(Decimal(ticket['reserved']), Decimal('0.44844800'))
                if kind == 'overrun':
                    self.assertEqual(Decimal(ticket['spent']), Decimal('0.51'))

    def test_literal_policy_price_and_activation_gates(self):
        with self.assertRaises(RuntimeError):
            preflight.run(broker.OpenRouterHTTP('SYNTHETIC-NOT-A-CREDENTIAL'), evidence_path=self.path)
        self.assertFalse(self.path.exists())
        self.assertEqual(preflight.literal_input_bound(preflight.MODELS[0], preflight.LITERAL), 64000)
        with self.assertRaises(ValueError):
            preflight.literal_input_bound(preflight.MODELS[0], [{'role': 'user', 'content': 'different'}])
        proposal = json.loads((WORKSPACE / 'provider-preflight-proposal.json').read_text())
        original = proposal['requests'][0]['body']
        for change in ({'model': 'unpriced'}, {'max_completion_tokens': 1}, {'temperature': 0},
                       {'provider': {'only': ['azure']}}, {'provider': {**original['provider'], 'allow_fallbacks': True}},
                       {'provider': {**original['provider'], 'max_price': {'prompt': 100, 'completion': 100}}}):
            with self.assertRaises(ValueError):
                OfflineHTTP('SYNTHETIC-NOT-A-CREDENTIAL')({**original, **change}, 1)
        worker = {'model': preflight.MODELS[0], 'prompt': preflight.LITERAL, 'sampling_args': {'max_tokens': 32768},
                  'node': None, 'action': None, 'slot': None, 'provider': original['provider']}
        with self.assertRaises(ValueError):
            broker.provider_body(worker, 32768)
        lock = self.path.with_suffix('.lock')
        lock.write_text('interrupted', encoding='utf-8')
        with self.assertRaises(FileExistsError):
            preflight.run(OfflineHTTP('SYNTHETIC-NOT-A-CREDENTIAL'), evidence_path=self.path)
        self.assertEqual(lock.read_text(), 'interrupted')

    def test_deadline_before_dispatch_and_shared_reservations(self):
        class Clock:
            calls = 0

            def __call__(self):
                self.calls += 1
                return 0 if self.calls == 1 else 901

        result = self.execute([], clock=Clock())
        self.assertEqual(result['status'], 'stopped')
        self.assertEqual(len(self.connections), 0)
        ledger = Ledger(preflight.RATES, preflight.LIMITS)
        ledger.start('reservation-check')
        for model in preflight.MODELS:
            ledger.admit('reservation-check', model, 64000, 32768)
        self.assertEqual(ledger.exposure(), Decimal('0.466385920'))
        with self.assertRaises(AdmissionDenied):
            ledger.admit('reservation-check', preflight.MODELS[0], 64000, 32768)
        self.assertEqual(ledger.runs['reservation-check']['attempts'], 2)


if __name__ == '__main__':
    before = preserved_hashes()
    with (patch('socket.socket', side_effect=AssertionError('No network allowed')),
          patch('http.client.HTTPSConnection', side_effect=AssertionError('Only explicit fake HTTP allowed'))):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProviderPreflightChecks)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    unchanged = before == preserved_hashes()
    destination = WORKSPACE / 'results' / ('provider-preflight-check-' + uuid.uuid4().hex + '.json')
    write_json(destination, {'test_methods': result.testsRun, 'success': result.wasSuccessful() and unchanged,
        'failures': [{'test': str(t), 'traceback': trace} for t, trace in result.failures + result.errors],
        'protected_files_unchanged': unchanged, 'provider_api_requests': 0, 'credential_access': False,
        'prior_full_or_isolation_suites_repeated': False})
    print(destination)
    raise SystemExit(not (result.wasSuccessful() and unchanged))
