import unittest

from experiments.official_baseline_h2_h5_h6.common import WORKSPACE, write_json
from experiments.official_baseline_h2_h5_h6.fixtures.programs import FIXTURES
from experiments.official_baseline_h2_h5_h6.runners.mock import canonical, run_fixture


class InstrumentationTests(unittest.TestCase):
    def test_equivalence(self):
        summaries = []
        for fixture in FIXTURES:
            with self.subTest(fixture=fixture.name):
                control = run_fixture(fixture, instrumented=False)
                observed = run_fixture(fixture)
                write_json(WORKSPACE / "results/equivalence" / (fixture.name + ".json"),
                           {"control": control, "instrumented": observed})
                self.assertEqual(control["response"], fixture.expected)
                self.assertEqual(control["error"], fixture.error)
                for key in ("response", "error", "requests", "trajectory"):
                    # Concurrent child order can vary; compare the provider multiset separately.
                    if key == "requests":
                        import json
                        def ordered(rows):
                            return sorted(json.dumps({k: v for k, v in r.items() if k != "attempt"}, sort_keys=True) for r in rows)
                        self.assertEqual(ordered(control[key]), ordered(observed[key]))
                    else:
                        self.assertEqual(canonical(control[key]), canonical(observed[key]))
                events = observed["events"]
                captures = [e["content"] for e in events if e["kind"] == "candidate_capture"]
                if fixture.name in {"multiple_blocks", "repeated_capture"}:
                    self.assertEqual(captures, ["A", "B"])
                if fixture.name == "rebound_answer":
                    self.assertEqual(captures, ['rebound'])
                if fixture.name == "mutable_snapshot":
                    values = [e["locals"]["x"] for e in events if e["kind"] == "python_result" and e["phase"] == "execution"]
                    self.assertEqual(values, [[1], [1, 2]])
                if fixture.name == "truncated_feedback":
                    underlying = next(e for e in events if e["kind"] == "python_result" and e["phase"] == "execution")
                    self.assertGreater(len(underlying["stdout"]), 20000)
                    self.assertIn("TAIL_MARKER", underlying["stderr"])
                    feedback = str(observed["requests"][1]["prompt"])
                    self.assertLess(feedback.count("x"), 22000)
                if fixture.name == "depth_fallback":
                    self.assertTrue(any(e.get("route") == "depth_limit_plain" for e in events))
                if fixture.name in {"plain_batch", "duplicate_plain_slots", "reordered_plain_slots"}:
                    child_events = [e for e in events if e["kind"] == "provider_dispatch" and isinstance(e["request"], str)]
                    self.assertEqual(sorted(e["slot"] for e in child_events), list(range(len(child_events))))
                    self.assertEqual(len({e["action"] for e in child_events}), 1)
                    self.assertIsNotNone(child_events[0]["action"])
                    if fixture.name == "reordered_plain_slots":
                        self.assertEqual([e["slot"] for e in child_events], [1, 0])
                if fixture.name in {"recursive_batch", "duplicate_recursive_slots"}:
                    child_events = [e for e in events if e["kind"] == "recursive_dispatch"]
                    self.assertEqual(sorted(e["slot"] for e in child_events), [0, 1])
                    self.assertIsNotNone(child_events[0]["action"])
                    self.assertEqual(len({e["action"] for e in child_events}), 1)
                summaries.append({"fixture": fixture.name, "pass": True,
                                  "control_seconds": control["elapsed_s"],
                                  "observed_seconds": observed["elapsed_s"],
                                  "overhead_seconds": observed["elapsed_s"] - control["elapsed_s"],
                                  "event_count": len(events)})
        write_json(WORKSPACE / "results/equivalence-summary.json", summaries)
