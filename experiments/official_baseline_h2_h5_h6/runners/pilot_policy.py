"""Host-only frozen bounds and response checks; never transforms model messages."""

import json
from decimal import Decimal

from ..common import PIN, WORKSPACE, preserved_hashes, sha

BOUND_REVISION = 'ascii-json-bytes-plus-1024-and-128-per-message-v1'
TELEMETRY_REVISION = 'native-cost-once-conservative-detail-bound-v1'
PILOT_POLICY_REVISION = 'official-baseline-live-host-v1'
PREFLIGHT_PATH = 'results/provider-preflight/live-nano-followup.json'


class PilotVerificationError(ValueError):
    def __init__(self, check, budget_uncertain=False):
        self.check, self.budget_uncertain = check, budget_uncertain
        super().__init__(check)


def require(condition, check, budget_uncertain=False):
    if not condition:
        raise PilotVerificationError(check, budget_uncertain)


def input_bound(model, messages):
    from .provider_preflight import MODELS
    require(model in MODELS and isinstance(messages, list) and bool(messages), 'text_messages_required')
    require(all(isinstance(m, dict) and set(m) == {'role', 'content'}
                and m['role'] in {'system', 'user', 'assistant'} and isinstance(m['content'], str)
                for m in messages), 'text_messages_required')
    # ASCII-escaped JSON is >= the UTF-8 content byte count. Byte-level BPE
    # cannot produce more content tokens than bytes. Reserve framing separately.
    # Return the full bound: Ledger.admit rejects >64,000, never clips the prompt.
    return len(json.dumps(messages, ensure_ascii=True, separators=(',', ':')).encode('ascii')) + 1024 + 128 * len(messages)


def verify_usage(result, model, ticket):
    from .provider_preflight import CACHE_RATES, RATES, RESOLVED_ENDPOINTS
    metadata = result.get('openrouter_metadata') or {}
    selected = [row for row in metadata.get('endpoints', {}).get('available', []) if row.get('selected') is True]
    require(result.get('model') == model and result.get('provider') == 'OpenAI'
            and metadata.get('requested') == model and type(metadata.get('attempt')) is int
            and metadata['attempt'] == 1 and metadata.get('is_byok') is False
            and len(selected) == 1 and selected[0].get('provider') == 'OpenAI'
            and selected[0].get('model') in RESOLVED_ENDPOINTS[model], 'provider_route')
    require(isinstance(result.get('id'), str) and bool(result['id']), 'generation_identity')
    require(result.get('service_tier') in (None, 'default'), 'service_tier')
    choices = result.get('choices')
    require(isinstance(choices, list) and len(choices) == 1
            and choices[0].get('finish_reason') in ('stop', 'length')
            and isinstance(choices[0].get('message', {}).get('content'), str), 'provider_completion')
    usage = result.get('usage') or {}
    incoming, outgoing, total = (usage.get(k) for k in ('prompt_tokens', 'completion_tokens', 'total_tokens'))
    reasoning = (usage.get('completion_tokens_details') or {}).get('reasoning_tokens')
    cached = (usage.get('prompt_tokens_details') or {}).get('cached_tokens', 0)
    require(all(type(v) is int and v >= 0 for v in (incoming, outgoing, total, reasoning, cached)), 'usage_types', True)
    require(total == incoming + outgoing and cached <= incoming, 'usage_consistency', True)
    conflict = reasoning > outgoing
    conservative_output = outgoing + reasoning if conflict else outgoing
    require(incoming <= ticket['input_bound'] and conservative_output <= ticket['output_bound'], 'usage_bound', True)
    require(usage.get('is_byok') is False and not usage.get('server_tool_use_details')
            and not usage.get('deferred_tools_details'), 'billing_services', True)
    billed = Decimal(str(usage.get('cost')))
    expected = RATES[model].cost(incoming - cached, outgoing) + CACHE_RATES[model] * cached / Decimal(1000000)
    require(billed.is_finite() and billed >= 0 and billed == expected, 'price_reconciliation', True)
    return {'revision': TELEMETRY_REVISION, 'resolved_endpoint': selected[0]['model'],
            'reasoning_detail_conflict': conflict, 'reasoning_tokens': reasoning,
            'conservative_output_count': conservative_output, 'native_completion_tokens': outgoing,
            'billing_basis': 'native_completion_once', 'reported_cost_usd': str(billed),
            'expected_cost_usd': str(expected)}


def preflight_seed():
    raw = (WORKSPACE / PREFLIGHT_PATH).read_bytes()
    record = json.loads(raw)
    snapshot = record['ledger']
    require(snapshot['campaign_exposure_usd'] == '0.44882910' and len(snapshot['tickets']) == 3, 'preflight_seed')
    require(snapshot['tickets']['attempt-00001']['state'] == 'usage_unknown'
            and snapshot['tickets']['attempt-00001']['reserved'] == '0.4484480', 'preflight_reservation')
    require(all(snapshot['tickets'][k]['state'] == 'reconciled' for k in ('attempt-00002', 'attempt-00003')), 'preflight_known_charges')
    return sha(raw), snapshot


def identity():
    from .broker import PROVIDER_POLICY_REVISION, routed_body
    from .provider_preflight import MODELS, RESOLVED_ENDPOINTS
    seed_hash, snapshot = preflight_seed()
    sources = ('runners/broker.py', 'runners/budget.py', 'runners/pilot_runner.py',
               'runners/pilot_policy.py', 'runners/provider_preflight.py', 'runners/observe.py',
               'runners/broker_client.py', 'runners/windows_boundary.py', 'live_baseline.py',
               'preflight_attempt_two.py', 'preflight_key_entry.py')
    return {'revision': PILOT_POLICY_REVISION, 'upstream_pin': PIN, 'rootcheck': False,
            'provider_policy_revision': PROVIDER_POLICY_REVISION,
            'routing': {m: routed_body({'model': m, 'messages': [], 'max_completion_tokens': 32768})['provider'] for m in MODELS},
            'approved_endpoints': {m: sorted(v) for m, v in RESOLVED_ENDPOINTS.items()},
            'input_bound_revision': BOUND_REVISION, 'telemetry_revision': TELEMETRY_REVISION,
            'preflight_seed_sha256': seed_hash, 'approved_carried_ticket': snapshot['tickets']['attempt-00001'],
            'source_hashes': {name: sha((WORKSPACE / name).read_bytes()) for name in sources},
            'protected_hashes': preserved_hashes(),
            'datasets_sha256': sha((WORKSPACE / 'tasks/dataset_manifest.json').read_bytes())}
