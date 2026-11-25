"""Two literal provider probes. No credential discovery and no live activation flag."""

import json
import time
from decimal import Decimal
from pathlib import Path

from ..common import WORKSPACE, preserved_hashes, sha
from .broker import (
    PROVIDER_POLICY_REVISION, OpenRouterHTTP, ProviderHTTPError, atomic_record, provider_body,
    reject_provider_error, routed_body,
)
from .budget import Ledger, Limits, Rate

LIVE_PREFLIGHT_AUTHORIZED = False  # Separate authorization/review required before changing.
PROPOSAL_SHA256 = 'b44ae48f87dbf0b15c20718b6a3f08da3c246f5f22055b5d6012de2f704c8325'
LITERAL = [{'role': 'user', 'content': 'Compute 17 * 19. Reply with only the integer.'}]
MODELS = ('openai/gpt-5', 'openai/gpt-5-nano')
VERIFICATION_REVISION = 'preflight-snapshot-billing-review-3'
RESOLVED_ENDPOINTS = {MODELS[0]: {MODELS[0], 'openai/gpt-5-2025-08-07'},
                      MODELS[1]: {MODELS[1], 'openai/gpt-5-nano-2025-08-07'}}
RATES = {MODELS[0]: Rate(Decimal('1.25'), Decimal('10')),
         MODELS[1]: Rate(Decimal('0.05'), Decimal('0.40'))}
CACHE_RATES = {MODELS[0]: Decimal('0.125'), MODELS[1]: Decimal('0.005')}
LIMITS = Limits(run_usd=Decimal('0.50'), campaign_usd=Decimal('0.50'), attempts=2)


class PreflightRejected(ValueError):
    """A fixed local check label, safe to retain without exception text from HTTP."""


def literal_input_bound(model, messages):
    if model not in MODELS or messages != LITERAL:
        raise ValueError('Only the approved literal messages are allowed')
    return 64000


def require(condition, check):
    if not condition:
        raise PreflightRejected(check)


def validate_response(result, model, generation_metadata=None):
    reject_provider_error(result)
    require(isinstance(result.get('id'), str) and bool(result['id']), 'generation_id')
    require(result['model'] == model and result.get('provider') == 'OpenAI', 'model_provider')
    metadata = result['openrouter_metadata']
    require(type(metadata['attempt']) is int and metadata['attempt'] == 1, 'route_attempt')
    require(metadata['requested'] == model and metadata.get('is_byok') is False, 'route_identity')
    selected = [item for item in metadata['endpoints']['available'] if item.get('selected') is True]
    require(len(selected) == 1 and selected[0]['provider'] == 'OpenAI'
            and selected[0]['model'] in RESOLVED_ENDPOINTS[model], 'selected_route')
    require(result.get('service_tier') in (None, 'default'), 'service_tier')
    require(len(result['choices']) == 1, 'choice_count')
    choice = result['choices'][0]
    require(choice['finish_reason'] == 'stop' and choice['message']['content'].strip() == '323', 'answer')
    usage = result['usage']
    incoming, outgoing, total = (usage[k] for k in ('prompt_tokens', 'completion_tokens', 'total_tokens'))
    require(all(type(v) is int and v >= 0 for v in (incoming, outgoing, total)), 'token_types')
    require(incoming <= 64000 and outgoing <= 32768 and total == incoming + outgoing, 'token_bounds')
    reasoning = usage['completion_tokens_details']['reasoning_tokens']
    cached = usage.get('prompt_tokens_details', {}).get('cached_tokens', 0)
    require(type(reasoning) is int and reasoning >= 0, 'reasoning_tokens')
    reasoning_conflict = reasoning > outgoing
    if reasoning_conflict:
        # A conflicting detail is not an extra charge. Require the authorized lookup
        # to corroborate this generation and independently cap the additive worst case.
        require(generation_metadata is not None, 'reasoning_metadata_required')
        data = generation_metadata
        require(data.get('id') == result['id'] and data.get('provider_name') == 'OpenAI'
                and data.get('model') == selected[0]['model'] and data.get('is_byok') is False
                and data.get('cancelled') is False and data.get('finish_reason') == 'stop',
                'generation_identity')
        require(all(type(data.get(k)) is int and data[k] == v for k, v in (
            ('native_tokens_prompt', incoming), ('native_tokens_completion', outgoing),
            ('native_tokens_reasoning', reasoning), ('native_tokens_cached', cached))), 'generation_usage')
        require(outgoing + reasoning <= 32768, 'conservative_output_bound')
        require(Decimal(str(data['total_cost'])) == Decimal(str(usage['cost']))
                and Decimal(str(data['usage'])) == Decimal(str(usage['cost'])), 'generation_billing')
    require(type(cached) is int and 0 <= cached <= incoming, 'cached_tokens')
    require(usage.get('is_byok') is False, 'byok')
    require(not usage.get('server_tool_use_details') and not usage.get('deferred_tools_details'), 'extra_services')
    billed = Decimal(str(usage['cost']))
    expected = (RATES[model].cost(incoming - cached, outgoing)
                + CACHE_RATES[model] * cached / Decimal(1000000))
    require(billed.is_finite() and billed >= 0 and billed == expected, 'price_reconciliation')
    return {'verification_revision': VERIFICATION_REVISION,
            'resolved_endpoint': selected[0]['model'],
            'reasoning_tokens': reasoning, 'cached_tokens': cached,
            'reasoning_detail_conflict': reasoning_conflict,
            'reasoning_semantics': 'unresolved_detail_preserved' if reasoning_conflict else 'included_in_completion',
            'conservative_output_count': outgoing + reasoning if reasoning_conflict else outgoing,
            'billing_basis': 'native_completion_count_once',
            'nonzero_reasoning_observed': reasoning > 0,
            'service_tier_reported': result.get('service_tier'),
            'expected_cost_usd': str(expected)}


def run(transport: OpenRouterHTTP, *, evidence_path: Path | None = None, clock=time.monotonic,
        authorized_attempt_two=False, authorized_nano_followup=False):
    """No resume/retry: any retained record or interrupted lock requires review."""
    if not isinstance(transport, OpenRouterHTTP):
        raise ValueError('Only the reviewed HTTP adapter is supported')
    if not transport.synthetic and not LIVE_PREFLIGHT_AUTHORIZED:
        raise RuntimeError('LIVE DISABLED: separate credential and two-request authorization required')
    if not transport.synthetic and evidence_path is not None:
        raise ValueError('Live evidence location is fixed')
    raw = (WORKSPACE / 'provider-preflight-proposal.json').read_bytes()
    require(sha(raw) == PROPOSAL_SHA256, 'proposal_changed')
    proposal = json.loads(raw)
    preserved_hashes()
    require(not (authorized_attempt_two and authorized_nano_followup), 'ambiguous_authorization')
    run_id = 'two-request-preflight-attempt-two' if authorized_attempt_two else 'two-request-preflight'
    reassessment = None
    lookup_hash = None
    prior = None
    prior_hash = None
    limits = LIMITS
    if authorized_attempt_two:
        prior_raw = (WORKSPACE / 'results/provider-preflight/live.json').read_bytes()
        prior_hash = sha(prior_raw)
        prior = json.loads(prior_raw)
        require(prior['status'] == 'stopped' and len(prior['requests']) == 1, 'prior_attempt_state')
        require(prior['ledger']['campaign_exposure_usd'] == '0.4484480', 'prior_exposure')
        limits = Limits(run_usd=Decimal('1.00'), campaign_usd=Decimal('1.00'), attempts=2)
    live_name = 'live-attempt-two.json' if authorized_attempt_two else 'live.json'
    if authorized_nano_followup:
        prior_raw = (WORKSPACE / 'results/provider-preflight/live-attempt-two.json').read_bytes()
        prior_hash, prior = sha(prior_raw), json.loads(prior_raw)
        require(prior['failed_check'] == 'selected_route' and len(prior['requests']) == 1, 'prior_gpt5_state')
        lookup_raw = (WORKSPACE / 'results/provider-preflight/gpt5-generation-lookup.json').read_bytes()
        lookup_hash, lookup = sha(lookup_raw), json.loads(lookup_raw)
        require(lookup['status'] == 'received' and lookup['http_status'] == 200, 'generation_lookup')
        reassessment = validate_response(prior['requests'][0]['provider_response'], MODELS[0],
                                         lookup['provider_response']['data'])
        limits = Limits(run_usd=Decimal('1.00'), campaign_usd=Decimal('1.00'), attempts=1)
        run_id, live_name = 'nano-followup-after-gpt5-review', 'live-nano-followup.json'
        proposal['requests'] = proposal['requests'][1:]
    destination = evidence_path or WORKSPACE / 'results/provider-preflight' / ('offline.json' if transport.synthetic else live_name)
    destination = Path(destination)
    if destination.exists():
        raise ValueError('Existing preflight evidence requires review; no automatic rerun')
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock_path = destination.with_suffix('.lock')
    with lock_path.open('x', encoding='utf-8') as lock:
        lock.write('two-request-preflight')
    if destination.exists():
        raise ValueError('Preflight advanced while acquiring lock; review required')
    ledger = Ledger(RATES, limits, clock=clock, rates_kind='openrouter-public-prices-2026-11-24')
    if prior is not None:
        ledger.restore(prior['ledger'])
    ledger.start(run_id)
    policy = {'proposal_sha256': PROPOSAL_SHA256, 'provider_revision': PROVIDER_POLICY_REVISION,
              'literal_bound_revision': 'literal-message-full-cap-v1',
              'combined_ceiling_usd': str(limits.campaign_usd), 'prior_live_sha256': prior_hash,
              'verification_revision': VERIFICATION_REVISION, 'generation_lookup_sha256': lookup_hash,
              'source_hashes': {name: sha((WORKSPACE / 'runners' / name).read_bytes())
                                for name in ('broker.py', 'budget.py', 'provider_preflight.py')}}
    record = {'status': 'in_progress', 'synthetic_only': transport.synthetic, 'policy': policy,
              'policy_sha256': sha(json.dumps(policy, sort_keys=True).encode()), 'requests': []}
    if reassessment is not None:
        record['saved_gpt5_reassessment'] = reassessment

    def save():
        record['ledger'] = ledger.snapshot()
        record['carry_into_campaign_exposure_usd'] = str(ledger.exposure())
        atomic_record(destination, record)

    ticket = None
    try:
        save()
        for item in proposal['requests']:
            model = item['body']['model']
            body = routed_body(provider_body({'model': model, 'prompt': item['body']['messages'],
                'sampling_args': {'max_tokens': 32768}, 'node': None, 'action': None, 'slot': None}, 32768))
            require(body == item['body'], 'request_policy_changed')
            bound = literal_input_bound(model, body['messages'])
            ticket = ledger.admit(run_id, model, bound, 32768)
            row = {'body': body, 'ticket': ticket, 'accepted': False}
            record['requests'].append(row)
            save()  # durable reservation before any HTTP attempt
            timeout = min(300, ledger.runs[run_id]['deadline'] - clock())
            require(timeout > 0, 'deadline')
            started = clock()
            row['submitted_at'] = time.time()
            result = transport(body, timeout)
            row['http_status'] = 200  # the HTTP adapter returns only after status 200
            row['received_at'] = time.time()
            row['provider_response'] = result
            usage = result.get('usage') or {}
            cost = usage.get('cost')
            ledger.reconcile(ticket, usage.get('prompt_tokens') if cost is not None else None,
                             usage.get('completion_tokens') if cost is not None else None,
                             None if cost is None else Decimal(str(cost)))
            require(not ledger.runs[run_id]['stop_reason'], 'accounting_stopped')
            row['verification'] = validate_response(result, model)
            require(clock() - started < timeout, 'deadline')
            row['accepted'] = True
            save()  # next request requires successful verification AND persisted reconciliation
        record['status'] = 'passed'
    except (Exception, KeyboardInterrupt) as exc:
        if ticket and ledger.tickets[ticket]['state'] != 'reconciled':
            ledger.reconcile(ticket, None, None)
        ledger.stop(run_id, 'preflight_stopped')
        record['status'] = 'stopped'
        record['failure_type'] = type(exc).__name__  # never serialize arbitrary exception text/credentials
        if isinstance(exc, ProviderHTTPError) and record['requests']:
            record['requests'][-1]['provider_error'] = exc.diagnostics
            record['requests'][-1]['http_status'] = exc.diagnostics['http_status']
        if isinstance(exc, PreflightRejected):
            record['failed_check'] = str(exc)
    finally:
        save()
        lock_path.unlink()  # failed final save retains lock; retained record always prevents replay
    return record
