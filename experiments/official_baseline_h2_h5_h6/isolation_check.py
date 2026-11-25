"""Explicit Windows isolation probe entry point; never runs a live model."""

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.official_baseline_h2_h5_h6.common import WORKSPACE, write_json
from experiments.official_baseline_h2_h5_h6.runners.windows_boundary import build_stage, launch, register_profile, verify_stage


def main():
    path = WORKSPACE / 'results/windows-stage.json'
    stage = json.loads(path.read_text()) if path.exists() else build_stage()
    write_json(path, stage)
    try:
        if '--register-profile' in sys.argv:
            stage = register_profile(stage)
            write_json(path, stage)
        verify_stage(stage)
        if '--test' in sys.argv:
            from experiments.official_baseline_h2_h5_h6.tests.check_windows_isolation import run
            print(json.dumps(run(stage, access_only='--access-only' in sys.argv), indent=2))
            return
        request = {'operation': 'startup'}
        if '--diagnostic' in sys.argv:
            request = {'operation': 'diagnostic'}
        if '--fixture' in sys.argv:
            request = {'operation': 'fixture', 'fixture': sys.argv[sys.argv.index('--fixture') + 1]}
        result = launch(stage, request)
    except Exception as exc:
        result = {'error': str(exc)[:3000], 'type': type(exc).__name__}
        if '--test' in sys.argv:
            write_json(WORKSPACE / 'results/windows-check-failure.json', result)
            print(json.dumps(result, indent=2))
            raise SystemExit(1)
    write_json(WORKSPACE / 'results/windows-startup.json', result)
    print(json.dumps(result, indent=2))
    if 'error' in result or result.get('exit_code', 0) != 0:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
