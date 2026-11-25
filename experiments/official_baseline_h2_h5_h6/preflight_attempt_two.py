"""One separately authorized parent-only attempt; never loads keys into the environment."""

import json
import sys
from pathlib import Path

from dotenv.parser import parse_stream

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.official_baseline_h2_h5_h6.common import REPO, WORKSPACE, sha
from experiments.official_baseline_h2_h5_h6.preflight_key_entry import validate_entry
from experiments.official_baseline_h2_h5_h6.runners import provider_preflight
from experiments.official_baseline_h2_h5_h6.runners.broker import OpenRouterHTTP, atomic_record


def read_parent_key(path):
    matches = []
    with path.open(encoding='utf-8-sig') as stream:
        for binding in parse_stream(stream):
            if binding.error:
                raise ValueError('Credential file syntax invalid')
            if binding.key == 'OPENROUTER_API_KEY':
                matches.append(binding.value)
    if len(matches) != 1 or not isinstance(matches[0], str):
        raise ValueError('Exactly one provider credential assignment required')
    key = matches[0]
    validate_entry(key)
    return key


def main():
    folder = WORKSPACE / 'results/provider-preflight'
    key = ''
    transport = None
    try:
        if (folder / 'live-attempt-two.json').exists():
            raise ValueError('Attempt already recorded; no replay')
        with (folder / 'attempt-two-entry.lock').open('x', encoding='utf-8') as lock:
            lock.write('One authorized entry; retained permanently; no automatic retries')
        atomic_record(folder / 'attempt-two-authorization.json', {
            'authorization': 'User explicitly approved fresh GPT-5 then gated GPT-5-nano',
            'combined_ceiling_usd': '1.00', 'carried_unresolved_usd': '0.448448',
            'maximum_fresh_requests': 2, 'retries': 0, 'pilot_authorized': False,
            'credential_source': 'Project .env OPENROUTER_API_KEY; parent adapter only',
            'prior_live_sha256': sha((folder / 'live.json').read_bytes()),
            'source_hashes': {name: sha((WORKSPACE / name).read_bytes()) for name in (
                'preflight_attempt_two.py', 'runners/provider_preflight.py', 'runners/broker.py',
                'runners/budget.py', 'preflight_key_entry.py')}})
        key = read_parent_key(REPO / '.env')
        transport = OpenRouterHTTP(key)
        # Authorization applies only to this process; source and pilot gates stay false.
        provider_preflight.LIVE_PREFLIGHT_AUTHORIZED = True
        result = provider_preflight.run(transport, authorized_attempt_two=True)
        print(json.dumps({'status': result['status'], 'fresh_attempts': len(result['requests']),
                          'failure_type': result.get('failure_type'), 'failed_check': result.get('failed_check'),
                          'combined_exposure_usd': result['carry_into_campaign_exposure_usd'],
                          'http_error': result['requests'][-1].get('provider_error') if result['requests'] else None}))
    except (Exception, KeyboardInterrupt) as exc:
        # Fixed category only: never print credential/parser/HTTP exception text.
        print(json.dumps({'status': 'entry_stopped', 'failure_type': type(exc).__name__}))
    finally:
        provider_preflight.LIVE_PREFLIGHT_AUTHORIZED = False
        if transport is not None:
            transport.api_key = ''
        key = ''


if __name__ == '__main__':
    main()
