"""Offline-only regression checks for credential entry and HTTP error journals."""

import getpass
import json
import sys
import tempfile
import unittest
from concurrent.futures import Future
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.official_baseline_h2_h5_h6.common import WORKSPACE, preserved_hashes, sha, write_json
from experiments.official_baseline_h2_h5_h6.preflight_key_entry import validate_entry
from experiments.official_baseline_h2_h5_h6.provider_preflight_check import OfflineHTTP, response
from experiments.official_baseline_h2_h5_h6.runners import broker, provider_preflight as preflight
from experiments.official_baseline_h2_h5_h6.runners.budget import Ledger

FAKE_KEY = 'SYNTHETIC-NOT-A-CREDENTIAL'


class DiagnosticsChecks(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='diagnostics-', dir=WORKSPACE / 'results')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def fake_connection(self, status, payload):
        connection = Mock()
        connection.sock = None
        connection.getresponse.return_value.status = status
        connection.getresponse.return_value.read.return_value = payload
        return connection

    def test_windows_entry_and_validation(self):
        # Exercise the actual installed Windows getpass loop with fake console characters.
        for characters, expected in [('abc\bD\r', 'abD'), ('x' * 10000 + '\r', 'x' * 10000),
                                     ('\r', ''), ('partial\nignored', 'partial'), ('\x16\r', '\x16')]:
            with patch.object(getpass.sys, 'stdin', getpass.sys.__stdin__), \
                 patch.object(getpass.msvcrt, 'getwch', side_effect=iter(characters)), \
                 patch.object(getpass.msvcrt, 'putwch') as output:
                self.assertEqual(getpass.win_getpass('Prompt: '), expected)
                self.assertEqual(''.join(call.args[0] for call in output.call_args_list), 'Prompt: \r\n')
        for value in ('', ' key', 'key\t', '\x16', 'key\x00', 'key\x7f', 'kéy', '"key"', "'key'", 'Bearer key'):
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                validate_entry(value)
        validate_entry(FAKE_KEY)
        validate_entry('partial')  # Offline syntax checks cannot establish validity/completeness.

    def test_http_diagnostics_are_bounded_and_redacted(self):
        body = json.loads((WORKSPACE / 'provider-preflight-proposal.json').read_text())['requests'][0]['body']
        for status, category in ((400, 'request_validation'), (401, 'authentication'), (402, 'billing'),
                                 (403, 'authorization'), (404, 'not_found'), (429, 'rate_limit'),
                                 (503, 'server_error'), (504, 'timeout')):
            raw = json.dumps({'error': {'code': status, 'message': 'Rejected ' + FAKE_KEY
                + ' Bearer another-secret\n' + 'A' * 1000, 'metadata': {'secret': FAKE_KEY}}}).encode()
            connection = self.fake_connection(status, raw)
            with patch('http.client.HTTPSConnection', return_value=connection), self.assertRaises(broker.ProviderHTTPError) as caught:
                OfflineHTTP(FAKE_KEY)(body, 10)
            diagnostic = caught.exception.diagnostics
            self.assertEqual(diagnostic['http_status'], status)
            self.assertEqual(diagnostic['category'], category)
            self.assertEqual(diagnostic['provider_code'], status)
            self.assertLessEqual(len(diagnostic['message']), 500)
            self.assertNotIn(FAKE_KEY, json.dumps(diagnostic))
            self.assertNotIn('another-secret', json.dumps(diagnostic))
            self.assertNotIn('metadata', diagnostic)
            connection.request.assert_called_once()
            connection.close.assert_called_once()
        for raw in (b'<html>private error body</html>', b'[]', b'{"error":"private"}'):
            error = broker.ProviderHTTPError(502, raw, FAKE_KEY)
            self.assertEqual(error.diagnostics['message'], 'Provider error message unavailable')
        error = broker.ProviderHTTPError(200, b'x' * (broker.MAX_REQUEST_BYTES + 1), FAKE_KEY)
        self.assertEqual(error.diagnostics['category'], 'response_too_large')
        connection = self.fake_connection(200, json.dumps(response(preflight.MODELS[0])).encode())
        with patch('http.client.HTTPSConnection', return_value=connection):
            self.assertEqual(OfflineHTTP(FAKE_KEY)(body, 10), response(preflight.MODELS[0]))

    def test_driver_persists_error_and_stops_with_reservation(self):
        connection = self.fake_connection(401, json.dumps({'error': {
            'code': 401, 'message': 'Invalid credential: ' + FAKE_KEY}}).encode())
        path = self.root / 'journal.json'
        with patch('http.client.HTTPSConnection', return_value=connection) as factory:
            result = preflight.run(OfflineHTTP(FAKE_KEY), evidence_path=path)
        factory.assert_called_once()
        connection.request.assert_called_once()
        self.assertEqual(result['status'], 'stopped')
        self.assertEqual(len(result['requests']), 1)
        row = result['requests'][0]
        self.assertFalse(row['accepted'])
        self.assertEqual(row['http_status'], 401)
        self.assertEqual(row['provider_error']['category'], 'authentication')
        ticket = result['ledger']['tickets'][row['ticket']]
        self.assertEqual(ticket['state'], 'usage_unknown')
        self.assertEqual(Decimal(ticket['reserved']), Decimal('0.448448'))
        self.assertNotIn(FAKE_KEY, path.read_text())
        self.assertEqual(json.loads(path.read_text()), result)
        self.assertFalse(preflight.LIVE_PREFLIGHT_AUTHORIZED)

    def test_broker_persists_error_without_delivery(self):
        ledger = Ledger(preflight.RATES)
        ledger.start('diagnostics')
        ticket = ledger.admit('diagnostics', preflight.MODELS[0], 64000, 32768)
        (self.root / 'outbox').mkdir()
        instance = broker.Broker(self.root, ledger, 'diagnostics', SimpleNamespace(synthetic=False), preflight.literal_input_bound)
        self.addCleanup(instance.pool.shutdown)
        future = Future()
        future.set_exception(broker.ProviderHTTPError(400, b'{"error":{"message":"Invalid request"}}', FAKE_KEY))
        record = {'delivered': False}
        instance.records.append(record)
        instance.pending[future] = ('a' * 32, ticket, record)
        with patch.object(broker, 'WORKSPACE', self.root):
            instance.settle()
        saved = json.loads((self.root / 'results/broker/diagnostics.journal.json').read_text())
        self.assertEqual(saved['provider_records'][0]['provider_error']['http_status'], 400)
        self.assertFalse(record['delivered'])
        self.assertEqual(list((self.root / 'outbox').iterdir()), [])
        self.assertEqual(ledger.tickets[ticket]['state'], 'usage_unknown')
        self.assertEqual(ledger.exposure(), Decimal('0.448448'))


if __name__ == '__main__':
    before = preserved_hashes()
    live_folder = WORKSPACE / 'results/provider-preflight'
    original = {p.name: sha(p.read_bytes()) for p in live_folder.iterdir() if p.is_file()}
    with patch('socket.socket', side_effect=AssertionError('Network forbidden')), \
         patch('http.client.HTTPSConnection', side_effect=AssertionError('Only explicit fake HTTP permitted')):
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DiagnosticsChecks))
    unchanged = before == preserved_hashes()
    live_unchanged = original == {p.name: sha(p.read_bytes()) for p in live_folder.iterdir() if p.is_file()}
    write_json(WORKSPACE / 'results/provider-diagnostics-check.json', {
        'tests_run': result.testsRun, 'success': result.wasSuccessful(),
        'failures': len(result.failures), 'errors': len(result.errors),
        'protected_files_unchanged': unchanged, 'live_evidence_unchanged': live_unchanged,
        'provider_api_requests': 0, 'credential_access': False,
        'old_reservation_usd': '0.448448', 'live_gate_enabled': preflight.LIVE_PREFLIGHT_AUTHORIZED})
    raise SystemExit(not (result.wasSuccessful() and unchanged and live_unchanged))
