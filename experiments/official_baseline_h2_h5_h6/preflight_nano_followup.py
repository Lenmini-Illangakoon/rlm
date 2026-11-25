"""One authorized nano request, conditional on saved GPT-5 reassessment; no retry."""

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.official_baseline_h2_h5_h6.common import REPO, WORKSPACE, sha
from experiments.official_baseline_h2_h5_h6.preflight_attempt_two import read_parent_key
from experiments.official_baseline_h2_h5_h6.runners import provider_preflight as preflight
from experiments.official_baseline_h2_h5_h6.runners.broker import OpenRouterHTTP, atomic_record


def main():
    folder = WORKSPACE / 'results/provider-preflight'
    key, transport = '', None
    try:
        if (folder / 'live-nano-followup.json').exists():
            raise ValueError('Existing followup evidence prevents replay')
        with (folder / 'nano-followup-entry.lock').open('x', encoding='utf-8') as lock:
            lock.write('One user-authorized conditional nano request; no retry')
        atomic_record(folder / 'nano-followup-authorization.json', {
            'authorization': 'User approved one nano request after GPT-5 reassessment; no repeated GPT-5',
            'combined_ceiling_usd': '1.00', 'maximum_requests': 1, 'retries': 0,
            'verification_revision': preflight.VERIFICATION_REVISION,
            'source_hashes': {name: sha((WORKSPACE / name).read_bytes()) for name in (
                'preflight_nano_followup.py', 'runners/provider_preflight.py', 'runners/broker.py',
                'runners/budget.py', 'preflight_attempt_two.py')}})
        key = read_parent_key(REPO / '.env')
        transport = OpenRouterHTTP(key)
        preflight.LIVE_PREFLIGHT_AUTHORIZED = True
        result = preflight.run(transport, authorized_nano_followup=True)
        print(json.dumps({'status': result['status'], 'fresh_requests': len(result['requests']),
                          'failure_type': result.get('failure_type'), 'failed_check': result.get('failed_check'),
                          'combined_exposure_usd': result['carry_into_campaign_exposure_usd'],
                          'http_error': result['requests'][-1].get('provider_error') if result['requests'] else None}))
    except (Exception, KeyboardInterrupt) as exc:
        print(json.dumps({'status': 'entry_stopped', 'failure_type': type(exc).__name__}))
    finally:
        preflight.LIVE_PREFLIGHT_AUTHORIZED = False
        if transport is not None:
            transport.api_key = ''
        key = ''


if __name__ == '__main__':
    main()
