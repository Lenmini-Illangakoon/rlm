"""Prepare a frozen live campaign, or execute exactly one explicitly authorized run."""

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.official_baseline_h2_h5_h6.common import REPO, WORKSPACE
from experiments.official_baseline_h2_h5_h6.preflight_attempt_two import read_parent_key
from experiments.official_baseline_h2_h5_h6.runners.broker import OpenRouterHTTP, PROVIDER_POLICY_REVISION
from experiments.official_baseline_h2_h5_h6.runners.budget import Ledger, Limits
from experiments.official_baseline_h2_h5_h6.runners.config import PILOT_ORDER, progression
from experiments.official_baseline_h2_h5_h6.runners.pilot_policy import BOUND_REVISION, PILOT_POLICY_REVISION, input_bound
from experiments.official_baseline_h2_h5_h6.runners.pilot_runner import Pilot
from experiments.official_baseline_h2_h5_h6.runners.provider_preflight import RATES
from experiments.official_baseline_h2_h5_h6.runners.windows_boundary import verify_stage


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--authorize-run', choices=PILOT_ORDER)  # exactly one run; never a loop
    parser.add_argument('--engineering-checkpoint-approved', action='store_true')
    args = parser.parse_args()
    key, transport = '', None
    try:
        descriptor = SimpleNamespace(synthetic=False, policy_revision=PROVIDER_POLICY_REVISION,
                                     pilot_policy_revision=PILOT_POLICY_REVISION)
        ledger = Ledger(RATES, Limits(), rates_kind='openrouter-public-prices-2026-11-24')
        pilot = Pilot('official-baseline-v1', ledger, descriptor, input_bound, BOUND_REVISION)
        verify_stage(json.loads((WORKSPACE / 'results/windows-stage.json').read_text()))
        next_id = progression(pilot.records, args.engineering_checkpoint_approved)
        if args.prepare:
            print(json.dumps({'status': 'prepared', 'next_run': next_id, 'policy_hash': pilot.policy_hash,
                              'exposure_usd': str(ledger.exposure()), 'credential_access': False}))
            return
        if args.authorize_run != next_id:
            raise ValueError('Authorization does not match next run; no repeat permitted')
        key = read_parent_key(REPO / '.env')
        transport = OpenRouterHTTP(key)
        transport.pilot_policy_revision = PILOT_POLICY_REVISION
        pilot.transport = transport
        record = pilot.run_next(authorized_run_id=args.authorize_run,
                                engineering_checkpoint_passed=args.engineering_checkpoint_approved)
        print(json.dumps({'pilot_id': record['pilot_id'], 'run_id': record['run_id'],
                          'status': record['status'], 'reason': record['reason'],
                          'exposure_usd': str(ledger.exposure())}))
    except (Exception, KeyboardInterrupt) as exc:
        # Provider errors belong in the sanitized journals, never arbitrary tracebacks.
        print(json.dumps({'status': 'stopped', 'failure_type': type(exc).__name__}))
        raise SystemExit(1)
    finally:
        if transport is not None:
            transport.api_key = ''
        key = ''


if __name__ == '__main__':
    main()
