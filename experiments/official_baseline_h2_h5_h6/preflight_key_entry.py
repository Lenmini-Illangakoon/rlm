"""User-authorized local console handoff; key stays in this parent process only."""

import getpass
import json
import sys
import warnings
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.official_baseline_h2_h5_h6.common import WORKSPACE, sha
from experiments.official_baseline_h2_h5_h6.runners.broker import OpenRouterHTTP, atomic_record
from experiments.official_baseline_h2_h5_h6.runners import provider_preflight


def validate_entry(key):
    """Reject obvious entry mistakes without guessing a provider key length."""
    if (not key or any(not 33 <= ord(character) <= 126 for character in key)
            or any(character in key for character in ('"', "'"))
            or key.lower().startswith('bearer')):
        raise ValueError('Malformed credential entry refused')


def main():
    folder = WORKSPACE / 'results/provider-preflight'
    receipt = folder / 'credential-handoff.json'
    key = ''
    transport = None
    state = {'status': 'checking', 'credential_source': 'local_hidden_console',
             'credential_received': False, 'secret_written_to_disk': False,
             'spending_cap_usd': '0.50', 'maximum_provider_requests': 2}
    try:
        if not sys.stdin.isatty():
            raise RuntimeError('A local interactive console is required')
        if receipt.exists() or (folder / 'live.json').exists() or (folder / 'live.lock').exists():
            raise RuntimeError('Existing handoff or live evidence requires review')
        with (folder / 'credential-entry.lock').open('x', encoding='utf-8') as lock:
            lock.write('One authorized local entry session; do not automatically relaunch')
        approved = json.loads((folder / 'authorization.json').read_text())
        expected = json.loads((WORKSPACE / 'results/provider-preflight-implementation-final.json').read_text())['implementation_hashes']
        expected['runners/provider_preflight.py'] = approved['source_sha256_after_activation']
        if any(sha((WORKSPACE / name).read_bytes()) != digest for name, digest in expected.items()):
            raise RuntimeError('Implementation changed since authorization')
        if not provider_preflight.LIVE_PREFLIGHT_AUTHORIZED:
            raise RuntimeError('Preflight authorization gate is disabled')
        state['status'] = 'waiting_for_hidden_entry'
        atomic_record(receipt, state)
        print('RootCheck: approved OpenRouter provider preflight only.')
        print('At most GPT-5 then GPT-5-nano; combined ceiling USD 0.50; no retries.')
        print('Enter your key locally. Characters will not be displayed or saved.')
        warnings.simplefilter('error', getpass.GetPassWarning)  # never fall back to echoed input
        key = getpass.getpass('OpenRouter API key (hidden; Enter submits): ')
        validate_entry(key)
        state['credential_received'] = True
        state['status'] = 'executing_authorized_preflight'
        atomic_record(receipt, state)
        transport = OpenRouterHTTP(key)
        result = provider_preflight.run(transport)  # exactly one driver invocation; no resume or retry
        state['status'] = 'finished'
        state['driver_status'] = result['status']
        state['admitted_attempts'] = len(result['requests'])
        atomic_record(receipt, state)
        print('Preflight finished. Evidence saved locally for review.')
    except (Exception, KeyboardInterrupt) as exc:
        # Never print arbitrary exception text or a traceback from credential/HTTP code.
        state['status'] = 'stopped'
        state['failure_type'] = type(exc).__name__
        # The separate entry lock is deliberately retained to prevent automatic replay.
        atomic_record(folder / 'credential-entry-stop.json', state)
        print('Stopped. No automatic retry. Review local evidence before any further action.')
    finally:
        if transport is not None:
            transport.api_key = ''
        key = ''


if __name__ == '__main__':
    main()
