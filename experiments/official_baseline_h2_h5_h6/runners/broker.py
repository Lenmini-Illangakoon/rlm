"""Parent-only provider admission and JSON transport. No environment/credential discovery.

The CLI exercises this with synthetic transports only. HTTP is an explicit,
single-attempt adapter for later approved preflight, never enabled by a flag here.
"""

import http.client
import json
import os
import re
import shutil
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path
from threading import Event, Timer

from ..common import WORKSPACE, preserved_hashes, sha, write_json
from .budget import AdmissionDenied, Ledger
from .pilot_policy import PilotVerificationError, verify_usage
from .windows_boundary import (
    U, appcontainer_sid, grant_stage, launch, low_directory, read_worker_file,
    register_profile, strict_json, verify_stage,
)

MAX_REQUEST_BYTES = 8 * 1024 * 1024
MAX_EVIDENCE_BYTES = 64 * 1024 * 1024
PROVIDER_POLICY_REVISION = 'openai-preflight-policy-1'
PROVIDER_PRICES = {'openai/gpt-5': (1.25, 10), 'openai/gpt-5-nano': (0.05, 0.40)}


def routed_body(body):
    """Host-owned policy; never accept worker routing or unpriced models."""
    if set(body) not in ({'model', 'messages', 'max_completion_tokens'},
                         {'model', 'messages', 'max_completion_tokens', 'provider'}):
        raise ValueError('Unexpected provider body fields')
    if body['model'] not in PROVIDER_PRICES or type(body['max_completion_tokens']) is not int or body['max_completion_tokens'] != 32768:
        raise ValueError('Unapproved model or completion cap')
    incoming, outgoing = PROVIDER_PRICES[body['model']]
    policy = {'only': ['openai'], 'allow_fallbacks': False, 'require_parameters': True,
              'max_price': {'prompt': incoming, 'completion': outgoing}}
    if 'provider' in body and body['provider'] != policy:
        raise ValueError('Provider policy override refused')
    return {**body, 'provider': policy}


def reject_provider_error(result):
    """Explicit failures are not successful text, even when usage is available."""
    if result.get('error') is not None or any(
        choice.get('error') is not None or choice.get('finish_reason') == 'error'
        for choice in result.get('choices', [])
    ):
        raise ValueError('Provider returned an error')


def atomic_record(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open('wb') as stream:
        stream.write((json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode())
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def provider_body(request, completion_cap):
    if set(request) != {'model', 'prompt', 'sampling_args', 'node', 'action', 'slot'}:
        raise ValueError('Unexpected broker request fields')
    if (not isinstance(request['model'], str)
        or any(request[k] is not None and not isinstance(request[k], str) for k in ('node', 'action'))
        or (request['slot'] is not None and type(request['slot']) is not int)):
        raise ValueError('Invalid broker identity/correlation fields')
    prompt = request['prompt']
    messages = [{'role': 'user', 'content': prompt}] if isinstance(prompt, str) else prompt
    if not isinstance(messages, list) or not all(
        isinstance(m, dict) and set(m) == {'role', 'content'}
        and m['role'] in {'system', 'user', 'assistant'} and isinstance(m['content'], str)
        for m in messages
    ):
        raise ValueError('Baseline accepts text chat messages only')
    if request['sampling_args'] != {'max_tokens': completion_cap}:
        raise ValueError('Worker sampling policy differs from frozen configuration')
    # Match pinned OpenAIClient._prepare_request/_normalize_sampling_args.
    return {'model': request['model'], 'messages': messages,
            'max_completion_tokens': completion_cap}


class ProviderHTTPError(RuntimeError):
    """Only bounded, sanitized diagnostics may leave the credential-owning adapter."""

    def __init__(self, status, raw, api_key):
        category = {400: 'request_validation', 401: 'authentication', 402: 'billing',
                    403: 'authorization', 404: 'not_found', 408: 'timeout',
                    429: 'rate_limit', 504: 'timeout'}.get(
                        status, 'server_error' if status >= 500 else 'http_error')
        message = 'Provider error message unavailable'
        code = None
        if len(raw) > MAX_REQUEST_BYTES:
            category, message = 'response_too_large', 'Response exceeded the local size limit'
        else:
            try:
                payload = strict_json(raw)
                error = payload.get('error') if isinstance(payload, dict) else None
                if isinstance(error, dict):
                    if type(error.get('code')) is int:
                        code = error['code']
                    candidate = error.get('message')
                    if isinstance(candidate, str):
                        # Redact before truncation; never retain bodies, headers or metadata.
                        candidate = candidate.replace(api_key, '[REDACTED]')
                        candidate = re.sub(r'(?i)bearer\s+\S+', 'Bearer [REDACTED]', candidate)
                        candidate = re.sub(r'(?i)sk-[^\s"\'<>]+', '[REDACTED]', candidate)
                        candidate = re.sub(r'[A-Za-z0-9_+/=.-]{24,}', '[REDACTED]', candidate)
                        message = ''.join(c if 32 <= ord(c) < 127 else ' ' for c in candidate)[:500]
            except (ValueError, UnicodeError):
                pass  # Non-JSON error bodies are deliberately never recorded.
        self.diagnostics = {'http_status': status, 'category': category,
                            'provider_code': code, 'message': message}
        super().__init__('Provider HTTP failure; usage unresolved')


class OpenRouterHTTP:
    """Explicit credential argument, fixed endpoint, no proxy discovery or retries.

    Construct only during a separately authorized live preflight. Never serialized.
    """
    synthetic = False
    policy_revision = PROVIDER_POLICY_REVISION

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError('Explicit provider credential required')
        self.api_key = api_key

    def __call__(self, body, timeout):
        body = routed_body(body)
        if timeout <= 0:
            raise TimeoutError('Provider deadline expired before connection')
        connection = http.client.HTTPSConnection('openrouter.ai', timeout=timeout)
        expired = Event()

        def abort():
            expired.set()
            if connection.sock is not None:
                try:
                    connection.sock.shutdown(2)
                except OSError:
                    pass  # socket may have closed concurrently

        deadline = Timer(timeout, abort)
        deadline.daemon = True
        deadline.start()
        try:
            connection.connect()
            if expired.is_set():
                raise TimeoutError('Provider deadline expired before dispatch')
            connection.request('POST', '/api/v1/chat/completions',
                               body=json.dumps(body, ensure_ascii=False).encode('utf-8'),
                               headers={'Content-Type': 'application/json',
                                        'X-OpenRouter-Metadata': 'enabled',
                                        'Authorization': 'Bearer ' + self.api_key})
            response = connection.getresponse()
            raw = response.read(MAX_REQUEST_BYTES + 1)
            if len(raw) > MAX_REQUEST_BYTES or response.status != 200:
                raise ProviderHTTPError(response.status, raw, self.api_key)
            return strict_json(raw)
        finally:
            deadline.cancel()
            connection.close()


class Broker:
    def __init__(self, mailbox, ledger, run_id, transport, input_bound):
        self.mailbox, self.ledger, self.run_id = mailbox, ledger, run_id
        self.transport, self.input_bound = transport, input_bound
        self.pool = ThreadPoolExecutor(max_workers=ledger.limits.attempts)
        self.pending, self.seen, self.records = {}, set(), []

    def checkpoint(self, finalized=False):
        atomic_record(WORKSPACE / 'results/broker' / (self.run_id + '.journal.json'),
                      {'run_id': self.run_id, 'finalized': finalized,
                       'ledger': self.ledger.snapshot(), 'provider_records': self.records})

    def settle(self):
        for future, (identifier, ticket, record) in list(self.pending.items()):
            if not future.done():
                continue
            del self.pending[future]
            reservation = self.ledger.tickets[ticket]['reserved']
            try:
                result = future.result()
                record['received_at'] = time.time()
                record['provider_response'] = result
                usage = result.get('usage') or {}
                incoming, outgoing = usage.get('prompt_tokens'), usage.get('completion_tokens')
                cost = usage.get('cost')
                if not self.transport.synthetic and cost is None:
                    incoming = outgoing = None
                self.ledger.reconcile(ticket, incoming, outgoing,
                                      None if cost is None else Decimal(str(cost)))
                if self.ledger.runs[self.run_id]['stop_reason']:
                    continue
                reject_provider_error(result)
                if getattr(self.transport, 'pilot_policy_revision', None):
                    record['verification'] = verify_usage(result, record['body']['model'], self.ledger.tickets[ticket])
                content = result['choices'][0]['message']['content']
                if not isinstance(content, str):
                    raise ValueError('Missing textual completion')
                # Outbox and its parent are not writable by the worker.
                destination = self.mailbox / 'outbox' / (identifier + '.json')
                temporary = destination.with_suffix('.tmp')
                write_json(temporary, {'content': content, 'usage': usage})
                temporary.replace(destination)
                record['delivered'] = True
            except Exception as exc:
                record['failure_type'] = type(exc).__name__
                if isinstance(exc, ProviderHTTPError):
                    record['provider_error'] = exc.diagnostics
                row = self.ledger.tickets[ticket]
                if isinstance(exc, PilotVerificationError):
                    record['verification_failure'] = exc.check
                    if exc.budget_uncertain and row['state'] == 'reconciled':
                        # Keep known spending plus the remainder of the original hold.
                        row['reserved'] = max(Decimal(0), reservation - row['spent'])
                        row['state'] = 'usage_uncertain'
                        self.ledger.stop(self.run_id, 'telemetry_budget_uncertain')
                if row['state'] != 'reconciled':
                    self.ledger.reconcile(ticket, None, None)
                self.ledger.stop(self.run_id, 'provider_failure')
            finally:
                self.checkpoint()

    def poll(self):
        self.settle()
        if self.ledger.clock() >= self.ledger.runs[self.run_id]['deadline']:
            self.ledger.stop(self.run_id, 'wall_clock')
        reason = self.ledger.runs[self.run_id]['stop_reason']
        if reason:
            raise AdmissionDenied(reason)
        paths = list((self.mailbox / 'inbox').glob('*.json'))
        if len(paths) > self.ledger.limits.attempts + 1:
            raise ValueError('Broker inbox overflow')
        for path in paths:
            identifier = path.stem
            if identifier in self.seen:
                continue
            if not re.fullmatch('[0-9a-f]{32}', identifier):
                raise ValueError('Invalid request identifier')
            request = strict_json(read_worker_file(path, MAX_REQUEST_BYTES))
            body = provider_body(request, self.ledger.limits.output_tokens)
            if isinstance(self.transport, OpenRouterHTTP):
                body = routed_body(body)  # journal the exact enforced policy before dispatch
            # Bounds, rates, model allowlist, ticket identity and usage are host-owned.
            bound = self.input_bound(body['model'], body['messages'])
            ticket = self.ledger.admit(self.run_id, body['model'], bound,
                                       self.ledger.limits.output_tokens)
            self.seen.add(identifier)
            record = {'request_id': identifier, 'ticket': ticket, 'body': body,
                      'worker_correlation': {k: request[k] for k in ('node', 'action', 'slot')},
                      'delivered': False, 'dispatched_at': time.time()}
            self.records.append(record)
            self.checkpoint()  # durable reservation BEFORE submitting any provider request
            timeout = min(300, self.ledger.runs[self.run_id]['deadline'] - self.ledger.clock())
            if timeout <= 0:
                self.ledger.stop(self.run_id, 'wall_clock')
                raise AdmissionDenied('wall_clock')
            atomic_record(self.mailbox / 'outbox' / (identifier + '.admitted.json'), {'ticket': ticket})
            future = self.pool.submit(self.transport, body, timeout)
            self.pending[future] = (identifier, ticket, record)

    def close(self):
        # Terminating local Python cannot prove remote cancellation. Drain bounded
        # attempts to preserve late usage; unknown reservations remain held.
        self.pool.shutdown(wait=True, cancel_futures=False)
        self.settle()


def run_isolated(context, query, ledger: Ledger, transport, input_bound, run_id=None):
    protected = preserved_hashes()
    stage = json.loads((WORKSPACE / 'results/windows-stage.json').read_text())
    verify_stage(stage)
    run_id = run_id or 'broker-' + uuid.uuid4().hex
    if not re.fullmatch('broker-[0-9a-f]{32}', run_id):
        raise ValueError('Invalid run identifier')
    ledger.start(run_id)
    root = Path(stage['root']).resolve()
    area = root / ('run-' + uuid.uuid4().hex)
    area.mkdir()
    work, mailbox = area / 'work', area / 'mailbox'
    mailbox.mkdir()
    name = 'RootCheck.Pilot.' + area.name
    identity = appcontainer_sid(name)
    run_stage = {**stage, 'root': str(area), 'work': str(work), 'appcontainer_sid': identity,
                 'profile_name': name, 'profile_registered': False}
    broker = None
    registered = False
    result = None
    status, reason = 'infrastructure_failed', None
    cleanup = {'profile_deleted': False, 'scratch_deleted': False, 'payload_grant_removed': False}
    events = []
    trace_files = {}
    evidence_captured = True
    try:
        # A private verified copy avoids changing the ACL of the prior stage and
        # gives this Windows user ownership of the per-run payload ACL.
        shutil.copytree(root / 'payload', area / 'payload')
        # Keep the original verified stage intact; overlay only the two reviewed
        # experiment observers in this disposable private copy, never official RLM.
        run_stage['files'] = dict(stage['files'])
        for name in ('observe.py', 'broker_client.py'):
            relative = 'payload/repo/experiments/official_baseline_h2_h5_h6/runners/' + name
            data = (WORKSPACE / 'runners' / name).read_bytes()
            (area / relative).write_bytes(data)
            run_stage['files'][relative] = sha(data)
        verify_stage(run_stage)
        for directory in (work, mailbox / 'inbox', mailbox / 'outbox'):
            low_directory(directory)
        for relative in ('temp', 'profile'):
            (work / relative).mkdir()
        register_profile(run_stage)
        registered = True
        grant_stage(area / 'payload', identity, 0x1200A9)
        grant_stage(work, identity, 0x1301BF)
        grant_stage(mailbox / 'inbox', identity, 0x1301BF)
        grant_stage(mailbox / 'outbox', identity, 0x1200A9)
        broker = Broker(mailbox, ledger, run_id, transport, input_bound)
        result = launch(run_stage, {'operation': 'broker', 'context': context, 'query': query,
                                   'runtime_hashes': {k: v for k, v in protected.items() if k.startswith('rlm/')},
                                   'mailbox': str(mailbox), 'synthetic_only': transport.synthetic},
                        timeout=ledger.limits.seconds, poll=broker.poll)
        if result['exit_code'] == 0 and result['response'] and result['response']['ok']:
            status = 'completed'
        else:
            status, reason = 'operational_failure', 'worker_failure'
    except (AdmissionDenied, TimeoutError) as exc:
        reason = str(exc)
        status = 'operational_failure' if reason in {'provider_failure', 'usage_unknown', 'invalid_usage'} else 'resource_censored'
        ledger.stop(run_id, reason)
    except KeyboardInterrupt:
        status, reason = 'cancelled', 'cancelled'
        ledger.stop(run_id, reason)
    except Exception as exc:
        reason = type(exc).__name__ + ': ' + str(exc)
        ledger.stop(run_id, 'infrastructure_failed')
    finally:
        if broker:
            if status != 'completed':
                ledger.stop(run_id, reason or status)
            broker.close()
        try:
            path = work / 'events.jsonl'
            if path.exists():
                raw = read_worker_file(path, MAX_EVIDENCE_BYTES)
                archive = WORKSPACE / 'results/broker' / (run_id + '.events.jsonl')
                archive.parent.mkdir(parents=True, exist_ok=True)
                archive.write_bytes(raw)  # retain even an interrupted last line verbatim
                trace_files['events'] = str(archive)
                events = [strict_json(line) for line in raw.split(b'\n')[:-1]]
            path = work / 'response.json'
            if path.exists():
                archive = WORKSPACE / 'results/broker' / (run_id + '.worker-response.json')
                archive.write_bytes(read_worker_file(path, MAX_EVIDENCE_BYTES))
                trace_files['worker_response'] = str(archive)
        except Exception as exc:
            evidence_captured = False
            status, reason = 'infrastructure_failed', 'event_capture_' + type(exc).__name__
        stopped = ledger.runs[run_id]['stop_reason']
        if stopped and status == 'completed':
            status, reason = 'resource_censored', stopped
        record = {'run_id': run_id, 'synthetic_only': transport.synthetic, 'status': status,
                  'reason': reason, 'result': result, 'observed_prefix': events,
                  'trace_files': trace_files, 'evidence_captured': evidence_captured,
                  'worker_overlay_hashes': {name: sha((WORKSPACE / 'runners' / name).read_bytes())
                                           for name in ('observe.py', 'broker_client.py')},
                  'provider_records': broker.records if broker else [], 'ledger': ledger.snapshot(),
                  'cleanup': cleanup, 'profile_name': name, 'scratch_path': str(area),
                  'protocol_version': 'broker-integration-2-provider-policy',
                  'provider_policy_revision': getattr(transport, 'policy_revision', None)}
        destination = WORKSPACE / 'results/broker' / (run_id + '.json')
        # Preserve completed/censored evidence before deleting temporary files.
        atomic_record(destination, record)
        cleanup_errors = []
        try:
            if registered:
                error = U.DeleteAppContainerProfile(name)
                if error < 0:
                    raise OSError(f'DeleteAppContainerProfile HRESULT {error:#x}')
            cleanup['profile_deleted'] = True
        except Exception as exc:
            cleanup_errors.append(type(exc).__name__ + ': ' + str(exc))
        try:
            if not evidence_captured:
                raise RuntimeError('Scratch retained because evidence archival failed')
            target = area.resolve()
            if target.parent != root or not target.name.startswith('run-') or area.is_symlink() or area.is_junction():
                raise ValueError('Refusing cleanup outside this run staging directory')
            # Python 3.12 on Windows removes directory junctions without traversing them.
            shutil.rmtree(target)
            cleanup['scratch_deleted'] = True
            cleanup['payload_grant_removed'] = True  # private payload deleted with its ACL
        except Exception as exc:
            cleanup_errors.append(type(exc).__name__ + ': ' + str(exc))
        if cleanup_errors:
            record['cleanup_error'] = cleanup_errors
            record['infrastructure_failure'] = 'lifecycle_cleanup_failed'
        atomic_record(destination, record)
        if broker:
            broker.checkpoint(finalized=True)
    return record


class CannedTransport:
    synthetic = True

    def __call__(self, body, timeout):
        return {'choices': [{'message': {'content': "```repl\nprint(len(context))\nanswer['content'] = 'OFFLINE TRANSPORT ONLY'\nanswer['ready'] = True\n```"}}],
                'usage': {'prompt_tokens': 10, 'completion_tokens': 5}}


def run_transport_scenario(scenario):
    from .budget import SYNTHETIC_RATES
    from .config import load_task

    context, query = load_task(scenario)
    record = run_isolated(context, query, Ledger(SYNTHETIC_RATES), CannedTransport(),
                          lambda model, messages: 100)
    if record['status'] != 'completed' or not all(record['cleanup'].values()):
        raise RuntimeError(f"Broker mock failed: {record['run_id']}")
    return str(WORKSPACE / 'results/broker' / (record['run_id'] + '.json'))
