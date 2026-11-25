import unittest
from dataclasses import replace

from experiments.official_baseline_h2_h5_h6.common import WORKSPACE, write_json

from experiments.official_baseline_h2_h5_h6.evaluators.assessment import (
    Contract, H2, H5, H6, Label, independent_origins, prefix_packet, record,
)


class AssessmentTests(unittest.TestCase):
    def contract(self, stratum="python"):
        return Contract("a1", stratum, 3, 5, "sum all input records", ("total",),
                        ("event:3",), "fixture-reviewer", "fixture-prefix-hash")

    def test_h2_strata_and_origin_deduplication(self):
        rows = [H2(self.contract(s), True, True, ["event:5"], origin_id="origin-1")
                for s in ("python", "plain_lm", "recursive_rlm", "batch_slot")]
        self.assertTrue(all(r.label() == Label.OBSERVED for r in rows))
        rows.append(H2(self.contract(), True, True, ["event:7"], propagated_from="origin-1"))
        self.assertEqual(independent_origins(rows), {"origin-1"})

    def test_h2_boundary_and_blinding(self):
        self.assertEqual(H2(self.contract(), False, True, ["e"]).label(), Label.NON_APPLICABLE)
        self.assertEqual(H2(self.contract(), None, True, ["e"]).label(), Label.INCONCLUSIVE)
        self.assertEqual(H2(self.contract(), True, False, ["e"]).label(), Label.NOT_OBSERVED)
        with self.assertRaises(ValueError):
            replace(self.contract(), prefix_end=5).validate()
        # A caught parser exception returning an incomplete value completes normally.
        self.assertEqual(H2(self.contract(), True, True, ["caught"], "o").label(), Label.OBSERVED)

    def test_h5_actual_return_and_missing_obligations(self):
        base = H5("return:9", "same_block", "correct", False, False, False, ["e"], "human")
        self.assertEqual(base.label(), Label.NOT_OBSERVED)
        self.assertEqual(replace(base, correctness="incorrect").label(), Label.NOT_OBSERVED)
        self.assertEqual(replace(base, material_omission=True).label(), Label.OBSERVED)
        self.assertEqual(replace(base, necessary_unobserved_unvalidated=True).label(), Label.OBSERVED)
        self.assertEqual(replace(base, material_support_gap=None).label(), Label.INCONCLUSIVE)
        self.assertEqual(replace(base, actual_return_ref=None).label(), Label.INCONCLUSIVE)
        self.assertEqual(replace(base, path="no_return").label(), Label.NON_APPLICABLE)
        for path in ("iteration_default", "depth_fallback", "forced_termination"):
            self.assertEqual(record(replace(base, path=path))["review"]["path"], path)

    def test_h6_prefix_stability_and_purpose(self):
        base = H6(2, 4, "hash", True, True, True, True, "human", ["request:4"])
        for purpose in ("necessary_computation", "useful_verification", "error_recovery", "final_delivery"):
            self.assertEqual(replace(base, actions=[{"event": 5, "purpose": purpose, "evidence_refs": ["e"]}]).label(), Label.NOT_OBSERVED)
        self.assertEqual(replace(base, actions=[{"event": 5, "purpose": "redundant_computation", "evidence_refs": ["e"]}]).label(), Label.OBSERVED)
        self.assertEqual(replace(base, stable=False).label(), Label.NON_APPLICABLE)
        self.assertEqual(replace(base, t_visible=None).label(), Label.INCONCLUSIVE)

    def test_prefix_packet_excludes_future_and_is_immutable(self):
        events = [{"seq": 1, "v": [1]}, {"seq": 2, "secret_future": "answer"}]
        packet = prefix_packet(events, 1)
        events[0]["v"].append(2)
        self.assertEqual(packet["events"], [{"seq": 1, "v": [1]}])

    def test_h6_packet_contains_only_delivered_root_histories(self):
        events = [
            {'seq': 1, 'event_id': 'root', 'kind': 'node_start', 'depth': 0},
            {'seq': 2, 'kind': 'python_result', 'locals': {'hidden': 'not root-visible'}},
            {'seq': 3, 'kind': 'provider_dispatch', 'owner_node': 'child', 'request': []},
            {'seq': 4, 'kind': 'provider_dispatch', 'owner_node': 'root', 'request': [{'role': 'user', 'content': 'visible'}]},
            {'seq': 5, 'kind': 'provider_dispatch', 'owner_node': 'root', 'request': [{'role': 'user', 'content': 'future'}]},
        ]
        self.assertEqual(prefix_packet(events, 4, True)['events'], [events[3]])

    def test_serialized_review_examples(self):
        reviews = [
            H2(self.contract(), True, True, ['synthetic-result'], origin_id='synthetic-origin'),
            H5('synthetic-return', 'same_block', 'correct', True, False, False,
               ['synthetic-missing-total'], 'fixture-reviewer'),
            H6(2, 4, 'synthetic-prefix-hash', True, True, True, True, 'fixture-reviewer',
               ['synthetic-request'], [{'event': 5, 'purpose': 'final_delivery', 'evidence_refs': ['synthetic-final']}]),
        ]
        records = [record(r) for r in reviews]
        self.assertEqual([r['label'] for r in records], ['observed', 'observed', 'not_observed'])
        self.assertTrue(all(not r['natural_baseline_evidence'] for r in records))
        write_json(WORKSPACE/'results/assessment-fixtures.json', records)
