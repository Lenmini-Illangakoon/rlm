import copy
import json
import unittest

from experiments.official_baseline_h2_h5_h6.common import WORKSPACE, sha
from experiments.official_baseline_h2_h5_h6.evaluators.oracles import SOLVERS, score_answer
from experiments.official_baseline_h2_h5_h6.tasks.generate import generate_s2


class Benchmarks(unittest.TestCase):
    def test_frozen_hashes_and_oracle_reconstruction(self):
        manifest = json.loads((WORKSPACE/'tasks/dataset_manifest.json').read_text())
        for scenario, entry in manifest['scenarios'].items():
            with self.subTest(scenario=scenario):
                context = (WORKSPACE/'tasks/data'/scenario/'context.txt').read_bytes()
                query = (WORKSPACE/'tasks/data'/scenario/'query.txt').read_bytes()
                oracle = json.loads((WORKSPACE/'evaluators/oracle_results'/f'{scenario}.json').read_text())
                self.assertEqual(sha(context),entry['context_sha256'])
                self.assertEqual(sha(query),entry['query_sha256'])
                self.assertEqual(SOLVERS[scenario](context),oracle)

    def test_repeat_generation(self):
        self.assertEqual(generate_s2(), generate_s2())
        self.assertEqual(generate_s2(),(WORKSPACE/'tasks/data/S2-v2/context.txt').read_bytes())

    def test_s2_boundaries_and_provenance(self):
        oracle = SOLVERS['S2-v2'](generate_s2())
        self.assertEqual(oracle['eligible_count'],100)
        self.assertEqual(oracle['total'],20538)
        self.assertEqual(oracle['ranked_ids'][:4],['SH-10106','SH-10068','SH-10097','SH-10138'])
        self.assertFalse(oracle['joined']['SH-10128']['eligible'])
        self.assertEqual(len(oracle['excluded_archives']),8)
        for row in oracle['selected']:
            self.assertEqual(row['sources'],[f'{p}-{int(row["id"][3:])-10000:03d}' for p in 'RWQH'])

    def test_missing_and_wrong_answers(self):
        for scenario in SOLVERS:
            oracle = json.loads((WORKSPACE/'evaluators/oracle_results'/f'{scenario}.json').read_text())
            answer = copy.deepcopy(oracle)
            self.assertEqual(score_answer(scenario, answer, oracle)['correctness'],'correct')
            field = 'product' if scenario == 'S3' else 'total'
            answer[field] += 1
            self.assertEqual(score_answer(scenario, answer, oracle)['correctness'],'incorrect')
            del answer[field]
            self.assertEqual(score_answer(scenario, answer, oracle)['output_coverage'],'incomplete')

    def test_wrong_selected_source_and_tie(self):
        oracle = SOLVERS['S2-v2'](generate_s2())
        answer = copy.deepcopy(oracle)
        answer['selected'][2]['id'] = 'SH-10138'
        self.assertEqual(score_answer('S2-v2',answer,oracle)['correctness'],'incorrect')
        answer = copy.deepcopy(oracle)
        answer['selected'][0]['sources'][0] = 'R-001'
        self.assertEqual(score_answer('S2-v2',answer,oracle)['correctness'],'incorrect')

    def test_parser_rejects_missing_duplicate_and_corrupt_notes(self):
        data = generate_s2()
        lines = data.splitlines()
        idx = next(i for i,line in enumerate(lines) if line.startswith(b'R-'))
        for modified in [lines[:idx]+lines[idx+1:], lines[:idx]+[lines[idx]]+lines[idx:], [line.replace(b'quality status APPROVED',b'quality status UNKNOWN') for line in lines]]:
            with self.assertRaises(ValueError):
                SOLVERS['S2-v2'](b'\n'.join(modified)+b'\n')

    def test_mutated_source_changes_oracle(self):
        data = generate_s2().replace(b'SH-10106: 6883 units requested.',b'SH-10106: 8883 units requested.')
        # k=106 is even: mutate its actual template, proving the solver reads bytes.
        data = data.replace(b'SH-10106 requires shipment of 6883 units.',b'SH-10106 requires shipment of 8883 units.')
        oracle = SOLVERS['S2-v2'](data)
        self.assertFalse(oracle['joined']['SH-10106']['eligible'])
        self.assertNotEqual(oracle['total'],20538)

    def test_scope_end_marker_corruptions(self):
        data = generate_s2()
        for modified in (data.replace(b'=== End Shipment Requests ===', b'=== End Wrong ==='),
                         data.replace(b'=== End Shipment Requests ===\n', b''),
                         data.replace(b'=== End Archived Shipments ===\n', b'')):
            with self.assertRaises(ValueError):
                SOLVERS['S2-v2'](modified)

    def test_explicit_output_cardinality_and_source_coverage(self):
        oracle = SOLVERS['S2-v2'](generate_s2())
        answer = copy.deepcopy(oracle)
        answer['selected'] = []
        self.assertEqual(score_answer('S2-v2', answer, oracle)['output_coverage'], 'incomplete')
        answer = copy.deepcopy(oracle)
        answer['selected'][0]['sources'].pop()
        self.assertEqual(score_answer('S2-v2', answer, oracle)['output_coverage'], 'incomplete')
