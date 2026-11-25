"""Exactly one explicitly authorized read-only lookup; no inference or retries."""

import http.client
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.official_baseline_h2_h5_h6.common import REPO, WORKSPACE, sha
from experiments.official_baseline_h2_h5_h6.preflight_attempt_two import read_parent_key
from experiments.official_baseline_h2_h5_h6.runners.broker import MAX_REQUEST_BYTES, ProviderHTTPError, atomic_record
from experiments.official_baseline_h2_h5_h6.runners.windows_boundary import strict_json

GENERATION_ID = 'gen-1795585741-7mec5Vzt2WQV4Xtu5Z43'


def main():
    folder = WORKSPACE / 'results/provider-preflight'
    path = folder / 'gpt5-generation-lookup.json'
    key = ''
    connection = None
    record = {'status': 'prepared', 'generation_id': GENERATION_ID,
              'authorization': 'One user-authorized read-only lookup of existing GPT-5 generation',
              'method': 'GET', 'maximum_requests': 1, 'retries': 0}
    if path.exists():
        print('Lookup already recorded; no replay')
        return
    with path.with_suffix('.lock').open('x', encoding='utf-8') as lock:
        lock.write('One lookup only; retained lock prevents replay')
    try:
        prior = json.loads((folder / 'live-attempt-two.json').read_text())
        assert prior['requests'][0]['provider_response']['id'] == GENERATION_ID
        record['prior_journal_sha256'] = sha((folder / 'live-attempt-two.json').read_bytes())
        atomic_record(path, record)
        key = read_parent_key(REPO / '.env')
        connection = http.client.HTTPSConnection('openrouter.ai', timeout=30)
        record['status'], record['submitted_at'] = 'submitted', time.time()
        atomic_record(path, record)
        connection.request('GET', '/api/v1/generation?' + urlencode({'id': GENERATION_ID}),
                           headers={'Authorization': 'Bearer ' + key})
        response = connection.getresponse()
        raw = response.read(MAX_REQUEST_BYTES + 1)
        record['http_status'], record['received_at'] = response.status, time.time()
        if response.status != 200 or len(raw) > MAX_REQUEST_BYTES:
            raise ProviderHTTPError(response.status, raw, key)
        if key.encode() in raw:
            raise ValueError('Credential reflection refused')
        record['provider_response'] = strict_json(raw)
        record['status'] = 'received'
    except Exception as exc:
        record['status'], record['failure_type'] = 'stopped', type(exc).__name__
        if isinstance(exc, ProviderHTTPError):
            record['provider_error'] = exc.diagnostics
    finally:
        if connection is not None:
            connection.close()
        key = ''
        atomic_record(path, record)
    data = record.get('provider_response', {}).get('data', {})
    fields = ('id', 'model', 'provider_name', 'total_cost', 'usage', 'upstream_inference_cost',
              'native_tokens_prompt', 'native_tokens_completion', 'native_tokens_reasoning',
              'native_tokens_cached', 'tokens_prompt', 'tokens_completion', 'is_byok', 'finish_reason')
    print(json.dumps({'status': record['status'], 'http_status': record.get('http_status'),
                      'provider_error': record.get('provider_error'), 'data': {k:data.get(k) for k in fields}}))


if __name__ == '__main__':
    main()
