"""Explicit CLI. Never imports a provider SDK or enables a live mode."""

import argparse
import json
import sys
import time
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare','test','mock','packet','preflight','live'])
    parser.add_argument('--pattern', default='test_*.py')
    parser.add_argument('--scenario', choices=['S1','S2-v2','S3'], default='S3')
    parser.add_argument('--trace', type=Path)
    parser.add_argument('--through', type=int)
    parser.add_argument('--root-visible-only', action='store_true')
    parser.add_argument('--reuse-evidence', action='store_true', help='Refresh preflight from saved tests without repeating the suite')
    args = parser.parse_args()
    if args.command == 'live':
        raise SystemExit('LIVE DISABLED: separate authorization and verified OS isolation/provider preflight required.')
    from experiments.official_baseline_h2_h5_h6.common import WORKSPACE, write_json
    if args.command == 'prepare':
        from experiments.official_baseline_h2_h5_h6.tasks.prepare import prepare
        print(prepare())
    elif args.command == 'test':
        started = time.perf_counter()
        suite = unittest.defaultTestLoader.discover(str(WORKSPACE/'tests'), pattern=args.pattern)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        write_json(WORKSPACE/'results/test-summary.json', {
            'pattern': args.pattern, 'test_methods': result.testsRun,
            'failure_count': len(result.failures), 'error_count': len(result.errors),
            'skip_count': len(result.skipped), 'success': result.wasSuccessful(),
            'elapsed_seconds': time.perf_counter()-started,
            'failures': [{'test': str(test), 'traceback': trace} for test, trace in result.failures + result.errors],
            'synthetic_only': True,
        })
        raise SystemExit(not result.wasSuccessful())
    elif args.command == 'mock':
        from experiments.official_baseline_h2_h5_h6.runners.mock import run_scenario
        print(run_scenario(args.scenario))
    elif args.command == 'packet':
        from experiments.official_baseline_h2_h5_h6.evaluators.assessment import prefix_packet
        if args.trace is None or args.through is None:
            parser.error('packet requires --trace and --through')
        trace = json.loads(args.trace.read_text(encoding='utf-8'))
        events = trace['instrumented']['events'] if 'instrumented' in trace else trace['observed_prefix']
        packet = prefix_packet(events, args.through, root_visible_only=args.root_visible_only)
        path = WORKSPACE/'results/review-packets'/f'{packet["sha256"]}.json'
        write_json(path, packet)
        print(path)
    else:
        from experiments.official_baseline_h2_h5_h6.runners.preflight import preflight
        report = preflight(reuse_evidence=args.reuse_evidence)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        raise SystemExit(2)  # never mistaken for live authorization/readiness


if __name__ == '__main__':
    main()
