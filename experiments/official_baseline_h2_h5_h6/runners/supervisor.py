"""Parent owns admission and terminates a mock worker on denial/timeout/cancellation.

This process boundary controls resources. It does NOT restrict the worker's filesystem.
"""

import multiprocessing
import time
import uuid
from threading import Lock

from .budget import AdmissionDenied, Ledger, SYNTHETIC_RATES


class LedgerProxy:
    def __init__(self, connection, run_id):
        self.connection = connection
        self.run_id = run_id
        self.lock = Lock()

    def rpc(self, operation, args):
        with self.lock:
            self.connection.send({"kind": "rpc", "operation": operation, "args": args})
            return self.connection.recv()

    def admit(self, *args):
        return self.rpc("admit", args)

    def reconcile(self, *args):
        return self.rpc("reconcile", args)

    def emit(self, event):
        with self.lock:
            self.connection.send({"kind": "event", "event": event})


def worker(connection, run_id, fixture, instrumented, context, query):
    from .mock import run_fixture

    proxy = LedgerProxy(connection, run_id)
    try:
        result = run_fixture(fixture, instrumented=instrumented, ledger=proxy,
                             context=context, query=query, sink=proxy.emit)
        connection.send({"kind": "result", "result": result})
    except BaseException as exc:
        connection.send({"kind": "worker_failure", "exception_type": type(exc).__name__})
    finally:
        connection.close()


def supervised_run(fixture, ledger=None, instrumented=True, cancel_after_dispatches=None,
                   context="fixture context", query="fixture root"):
    ledger = ledger or Ledger(SYNTHETIC_RATES)
    run_id = "supervised-mock-" + uuid.uuid4().hex
    ledger.start(run_id)
    parent, child = multiprocessing.get_context("spawn").Pipe()
    process = multiprocessing.get_context("spawn").Process(
        target=worker, args=(child, run_id, fixture, instrumented, context, query))
    process.start()
    child.close()
    events = []
    result = None
    status, reason = "infrastructure_failed", "worker_exited_without_result"
    try:
        while process.is_alive() or parent.poll():
            if ledger.clock() >= ledger.runs[run_id]["deadline"]:
                ledger.stop(run_id, "wall_clock")
            stopped = ledger.runs[run_id]["stop_reason"]
            if stopped:
                status, reason = ("cancelled" if stopped == "cancelled" else "resource_censored"), stopped
                break
            if not parent.poll(0.02):
                continue
            try:
                message = parent.recv()
            except EOFError:
                break
            if message["kind"] == "rpc":
                try:
                    reply = getattr(ledger, message["operation"])(*message["args"])
                except AdmissionDenied as exc:
                    status, reason = "resource_censored", str(exc)
                    break  # do not turn a denial into a model-visible helper error string
                parent.send(reply)
            elif message["kind"] == "event":
                events.append(message["event"])
                if cancel_after_dispatches is not None and sum(e["kind"] == "provider_dispatch" for e in events) >= cancel_after_dispatches:
                    ledger.stop(run_id, "cancelled")
            elif message["kind"] == "result":
                result = message["result"]
                status = "completed" if result["error"] is None else "operational_failure"
                reason = result["error"]
                break
            else:
                reason = message["exception_type"]
                break
    finally:
        if process.is_alive():
            if status != "completed":
                process.terminate()
            process.join(timeout=3)
            if process.is_alive():
                process.kill()
                process.join(timeout=3)
        else:
            process.join()
        if status != "completed":
            ledger.stop(run_id, reason or status)
        parent.close()
    return {"run_id": run_id, "synthetic_only": True, "status": status, "reason": reason,
            "result": result, "observed_prefix": events, "ledger": ledger.snapshot(),
            "worker_terminated": not process.is_alive(), "recorded_at_unix": time.time()}
