"""One run at a time; durable campaign accounting and unchanged approved gates."""

import json
from dataclasses import asdict
from decimal import Decimal

from ..common import WORKSPACE, sha
from .broker import atomic_record, run_isolated
from .config import load_config, load_task, progression


class Pilot:
    def __init__(self, name, ledger, transport, input_bound, bound_revision):
        if not name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in name):
            raise ValueError('Invalid campaign name')
        self.path = WORKSPACE / 'results/campaigns' / (name + '.json')
        self.ledger, self.transport, self.input_bound = ledger, transport, input_bound
        self.carried_ticket = None
        policy = {'config': load_config(), 'limits': asdict(ledger.limits),
                  'rates': {k: asdict(v) for k, v in ledger.rates.items()},
                  'synthetic': transport.synthetic, 'bound_revision': bound_revision}
        seed = None
        if not transport.synthetic:
            from .pilot_policy import BOUND_REVISION, identity, preflight_seed
            if bound_revision != BOUND_REVISION or policy['config']['rootcheck']:
                raise ValueError('Unapproved live bound or RootCheck configuration')
            policy['live_host'] = identity()
            _, seed = preflight_seed()
            self.carried_ticket = seed['tickets']['attempt-00001']
        self.policy = policy
        self.policy_hash = sha(json.dumps(policy, default=str, sort_keys=True).encode())
        self.records = []
        if self.path.exists():
            saved = json.loads(self.path.read_text())
            if saved['policy_hash'] != self.policy_hash or saved.get('active_run'):
                raise ValueError('Campaign changed or interrupted; review retained evidence before resuming')
            self.records = saved['records']
            ledger.restore(saved['ledger'])
        elif seed is not None:
            ledger.restore(seed)  # only on first creation, never on campaign reopen
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.with_suffix('.seed.lock').open('x', encoding='utf-8') as lock:
                lock.write('Preflight exposure imported once; retain this receipt')
            if self.path.exists():
                raise ValueError('Campaign appeared while seeding')
            self.save()

    def save(self, active_run=None):
        atomic_record(self.path, {'policy_hash': self.policy_hash, 'policy': json.loads(json.dumps(self.policy, default=str)), 'records': self.records,
                                 'ledger': self.ledger.snapshot(), 'active_run': active_run,
                                 'synthetic_only': self.transport.synthetic})

    def run_next(self, engineering_checkpoint_passed=False, authorized_run_id=None):
        if not self.transport.synthetic:
            from .broker import OpenRouterHTTP
            from .pilot_policy import PILOT_POLICY_REVISION
            if authorized_run_id is None or not isinstance(self.transport, OpenRouterHTTP) or getattr(self.transport, 'pilot_policy_revision', None) != PILOT_POLICY_REVISION:
                raise RuntimeError('LIVE DISABLED: exact-run authorization and reviewed adapter required')
        next_id = progression(self.records, engineering_checkpoint_passed)
        if not self.transport.synthetic and authorized_run_id != next_id:
            raise ValueError('Authorization must match the next unexecuted run')
        if next_id.startswith(('stop_', 'blocked_')) or next_id == 'complete':
            raise ValueError(next_id)
        if any(not all(row['cleanup'].values()) for row in self.records):
            raise ValueError('Previous lifecycle cleanup requires review')
        tickets = self.ledger.snapshot()['tickets']
        if any(Decimal(row['reserved']) and not (key == 'attempt-00001' and row == self.carried_ticket)
               for key, row in tickets.items()):
            raise ValueError('Unresolved provider exposure requires review before further dispatch')
        lock_path = self.path.with_suffix('.lock')
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        # A crash leaves the lock and active marker. Never guess away in-flight cost.
        with lock_path.open('x', encoding='utf-8') as lock:
            lock.write(next_id)
        try:
            # Reject another process that advanced this campaign after construction.
            if self.path.exists():
                current = json.loads(self.path.read_text())
                if current['records'] != self.records or current.get('active_run'):
                    raise ValueError('Campaign advanced; reopen the saved ledger')
            self.save(active_run=next_id)
            scenario = {'S1': 'S1', 'S2': 'S2-v2', 'S3': 'S3'}[next_id.split('-')[0]]
            context, query = load_task(scenario)
            record = run_isolated(context, query, self.ledger, self.transport, self.input_bound)
            record['pilot_id'] = next_id
            record['campaign_policy_hash'] = self.policy_hash
            record['assessments_required'] = {h: 'awaiting_evidence_review' for h in ('H2', 'H5', 'H6')}
            atomic_record(WORKSPACE / 'results/broker' / (record['run_id'] + '.json'), record)
            self.records.append({'pilot_id': next_id, 'run_id': record['run_id'],
                                 'status': record['status'], 'cleanup': record['cleanup']})
            self.save()
            return record
        finally:
            lock_path.unlink()
