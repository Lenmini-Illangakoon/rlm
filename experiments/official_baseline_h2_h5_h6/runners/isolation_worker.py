"""Allowlisted restricted-process entry point. Only JSON is exchanged with the host."""

import json
import sys
import traceback
from pathlib import Path

sys.dont_write_bytecode = True


def main():
    work = Path(sys.argv[1])
    try:
        request = json.loads((work / "request.json").read_text(encoding="utf-8"))
        if request.get('appcontainer_sid'):
            from experiments.official_baseline_h2_h5_h6.runners.temp_permissions import install as install_temp_permissions
            install_temp_permissions(work, request['appcontainer_sid'])
        if request["operation"] == "startup":
            result = {"python": sys.version, "paths": sys.path}
        elif request['operation'] == 'broker':
            from experiments.official_baseline_h2_h5_h6.runners.broker_client import run
            result = run(request, work)
        elif request['operation'] == 'diagnostic':
            import socket
            result = {}
            try:
                with socket.socket() as server, socket.socket() as client:
                    server.bind(('127.0.0.1', 0))
                    server.listen()
                    client.connect(server.getsockname())
                    peer, _ = server.accept()
                    peer.close()
                result['loopback'] = 'ok'
            except Exception:
                result['loopback'] = traceback.format_exc()
            try:
                from experiments.official_baseline_h2_h5_h6.runners.offline_guard import install
                install()
                from rlm.environments.local_repl import LocalREPL
                env = LocalREPL(context_payload='public input')
                try:
                    repl = env.execute_code('print(6 * 7)')
                    result['local_repl'] = {'stdout': repl.stdout, 'stderr': repl.stderr}
                finally:
                    env.cleanup()
            except Exception:
                result['local_repl'] = traceback.format_exc()
        else:
            from experiments.official_baseline_h2_h5_h6.runners.mock import run_fixture
            from experiments.official_baseline_h2_h5_h6.fixtures.programs import FIXTURES, Fixture
            if request["operation"] == "fixture":
                fixture = next(f for f in FIXTURES if f.name == request["fixture"])
            elif request["operation"] == "probe":
                fixture = Fixture(**request["fixture"])
            else:
                raise ValueError("Unknown operation")
            result = run_fixture(fixture, instrumented=request.get("instrumented", True),
                                 context=request.get('context', 'fixture context'),
                                 query=request.get('query', 'fixture root'))
        response = {"ok": True, "result": result}
    except BaseException:
        response = {"ok": False, "traceback": traceback.format_exc()}
    (work / "response.json").write_text(json.dumps(response, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
