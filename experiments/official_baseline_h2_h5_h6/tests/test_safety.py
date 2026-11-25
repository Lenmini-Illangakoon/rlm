import importlib
import socket
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from decimal import Decimal as D

from experiments.official_baseline_h2_h5_h6.common import WORKSPACE, write_json
from experiments.official_baseline_h2_h5_h6.fixtures.programs import FIXTURES, Fixture, block
from experiments.official_baseline_h2_h5_h6.runners.budget import AdmissionDenied, Ledger, Limits, Rate, SYNTHETIC_RATES
from experiments.official_baseline_h2_h5_h6.runners.supervisor import supervised_run


class BudgetTests(unittest.TestCase):
    def ledger(self, **kwargs):
        ledger = Ledger({"m": Rate(D("10"), D("10"))}, Limits(**kwargs))
        ledger.start("r")
        return ledger

    def test_atomic_concurrent_reservations(self):
        ledger = self.ledger()
        def reserve(_):
            try:
                return ledger.admit("r", "m", 64000, 32768)
            except AdmissionDenied:
                return None
        with ThreadPoolExecutor(max_workers=16) as pool:
            admitted = [x for x in pool.map(reserve, range(32)) if x]
        self.assertEqual(len(admitted), 1)  # each reservation is $1.064448
        self.assertEqual(ledger.runs["r"]["attempts"], 1)
        self.assertEqual(ledger.exposure(), D("1.064448"))
        self.assertEqual(ledger.runs["r"]["stop_reason"], "run_budget")

    def test_attempt_cap_and_recursive_shared_ledger(self):
        ledger = self.ledger()
        for _ in range(24):
            ticket = ledger.admit("r", "m", 1, 1)
            ledger.reconcile(ticket, 1, 1)
        with self.assertRaisesRegex(AdmissionDenied, "attempt_limit"):
            ledger.admit("r", "m", 1, 1)
        self.assertEqual(ledger.runs["r"]["attempts"], 24)

    def test_campaign_ceiling(self):
        ledger = self.ledger()
        for i in range(18):
            rid = "r" if i == 0 else f"r{i}"
            if i:
                ledger.start(rid)
            ledger.admit(rid, "m", 64000, 32768)
        ledger.start("last")
        with self.assertRaisesRegex(AdmissionDenied, "campaign_budget"):
            ledger.admit("last", "m", 64000, 32768)
        self.assertLessEqual(ledger.exposure(), D("20"))

    def test_reconciliation_unknown_and_overrun(self):
        ledger = self.ledger()
        ticket = ledger.admit("r", "m", 64000, 32768)
        ledger.reconcile(ticket, 10, 5)
        self.assertEqual(ledger.exposure(), D("0.00015"))
        with self.assertRaises(ValueError):
            ledger.reconcile(ticket, 10, 5)
        ticket = ledger.admit("r", "m", 64000, 32768)
        held = ledger.exposure()
        ledger.reconcile(ticket, None, None)
        self.assertEqual(ledger.exposure(), held)
        with self.assertRaisesRegex(AdmissionDenied, "usage_unknown"):
            ledger.admit("r", "m", 1, 1)
        other = self.ledger()
        ticket = other.admit("r", "m", 1, 1)
        other.reconcile(ticket, 2, 1)
        self.assertEqual(other.runs["r"]["stop_reason"], "usage_exceeded_reserved_bounds")
        self.assertEqual(other.exposure(), D("0.00003"))

    def test_token_caps_unpriced_timeout_cancel(self):
        for model, inp, out, reason in [("m", 64001, 1, "token_bound"), ("m", 1, 32769, "token_bound"), ("other", 1, 1, "unpriced_model")]:
            with self.subTest(reason=reason), self.assertRaisesRegex(AdmissionDenied, reason):
                self.ledger().admit("r", model, inp, out)
        now = [0.0]
        ledger = Ledger(SYNTHETIC_RATES, clock=lambda: now[0])
        ledger.start("r")
        now[0] = 900
        with self.assertRaisesRegex(AdmissionDenied, "wall_clock"):
            ledger.admit("r", "openai/gpt-5", 1, 1)
        ledger = self.ledger()
        ledger.admit("r", "m", 2, 2)
        held = ledger.exposure()
        ledger.stop("r", "cancelled")
        self.assertEqual(ledger.exposure(), held)
        with self.assertRaisesRegex(AdmissionDenied, "cancelled"):
            ledger.admit("r", "m", 1, 1)


class SupervisionTests(unittest.TestCase):
    def test_recursive_attempts_and_censor_equivalence(self):
        fixture = next(f for f in FIXTURES if f.name == "depth_fallback")
        completed = supervised_run(fixture)
        self.assertEqual(completed["status"], "completed", completed)
        run = completed["ledger"]["runs"][completed["run_id"]]
        self.assertEqual(run["attempts"], 3)
        rows = []
        for observed in (False, True):
            ledger = Ledger(SYNTHETIC_RATES, replace(Limits(), attempts=1))
            row = supervised_run(fixture, ledger=ledger, instrumented=observed)
            rows.append(row)
            self.assertEqual(row["status"], "resource_censored", row)
            self.assertEqual(row["reason"], "attempt_limit")
            self.assertTrue(row["worker_terminated"])
            self.assertEqual(len(row["ledger"]["tickets"]), 1)
        write_json(WORKSPACE / "results/supervision.json", {"recursive_success": completed, "censor_equivalence": rows})

    def test_external_timeout_and_cancel(self):
        fixture = Fixture("hang", [block("while True:\n    pass")], None)
        ledger = Ledger(SYNTHETIC_RATES, replace(Limits(), seconds=2))
        timeout = supervised_run(fixture, ledger=ledger)
        self.assertEqual((timeout["status"], timeout["reason"]), ("resource_censored", "wall_clock"))
        self.assertTrue(timeout["worker_terminated"])
        cancelled = supervised_run(fixture, cancel_after_dispatches=1)
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertTrue(cancelled["worker_terminated"])
        write_json(WORKSPACE / "results/cancellation.json", {"timeout": timeout, "cancelled": cancelled})


class OfflineBoundaryTests(unittest.TestCase):
    def test_live_accident_guards(self):
        from experiments.official_baseline_h2_h5_h6.runners.offline_guard import install
        install()
        with self.assertRaises(ImportError):
            importlib.import_module("rlm.clients.openai")
        with self.assertRaises(PermissionError), socket.socket() as sock:
            sock.connect(("192.0.2.1", 443))  # denied by audit before any remote connect
        with self.assertRaises(PermissionError):
            open(WORKSPACE / ".env", encoding="utf-8")  # nonexistent; denied before file access

    def test_actual_local_repl_isolation_probe(self):
        from experiments.official_baseline_h2_h5_h6.runners.offline_guard import install
        install()
        from rlm.environments.local_repl import LocalREPL
        canary = WORKSPACE / "results/researcher-only-canary.txt"
        canary.write_text("DUMMY RESEARCH CANARY -- NO ORACLE ANSWERS", encoding="utf-8")
        env = LocalREPL(context_payload="legitimate public input")
        try:
            result = env.execute_code(f"print(open({str(canary)!r}, encoding='utf-8').read())")
        finally:
            env.cleanup()
        readable = "DUMMY RESEARCH CANARY" in result.stdout
        write_json(WORKSPACE / "results/isolation.json", {
            "tested_boundary": "current Windows account + unmodified LocalREPL",
            "canary_readable": readable, "oracle_files_opened": False,
            "isolation_pass": not readable, "live_preflight": "BLOCKED",
            "stdout": result.stdout, "stderr": result.stderr,
            "required_next_step": "OS-enforced restricted worker identity or minimal mounted filesystem, followed by compatibility and adversarial read tests",
        })
        self.assertTrue(readable, "Environment changed: investigate and revalidate isolation")
