import unittest
from unittest.mock import patch

from experiments.official_baseline_h2_h5_h6.runners.config import PILOT_ORDER, load_config, load_task, progression


class ConfigurationTests(unittest.TestCase):
    def test_frozen_order_tasks_and_disabled_live(self):
        config = load_config()
        self.assertEqual(config['pilot_order'], list(PILOT_ORDER))
        self.assertFalse(config['live_enabled'])
        for scenario in ('S1', 'S2-v2', 'S3'):
            context, query = load_task(scenario)
            self.assertTrue(context and query)

    def test_round_one_checkpoint_retains_failed_runs(self):
        records = [{'pilot_id': k, 'status': 'infrastructure_failed'} for k in PILOT_ORDER[:3]]
        self.assertEqual(progression(records), 'stop_for_round_one_engineering_review')
        with self.assertRaises(ValueError):
            progression(records[1:])

    def test_censor_rule_fail_closed_until_approved_value_restored(self):
        records = [{'pilot_id': k, 'status': 'resource_censored'} for k in PILOT_ORDER[:3]]
        config = load_config()
        config['excessive_censoring_stop_count'] = None
        with patch('experiments.official_baseline_h2_h5_h6.runners.config.load_config', return_value=config):
            self.assertEqual(progression(records, True), 'blocked_missing_approved_censoring_threshold')
        config['excessive_censoring_stop_count'] = 2
        with patch('experiments.official_baseline_h2_h5_h6.runners.config.load_config', return_value=config):
            self.assertEqual(progression(records, True), 'stop_excessive_resource_censoring')
            self.assertEqual(progression(records[:2]), PILOT_ORDER[2])

    def test_confirmed_cumulative_round_end_rule(self):
        self.assertEqual(load_config()['excessive_censoring_stop_count'], 2)
        records = [{'pilot_id': k, 'status': 'completed'} for k in PILOT_ORDER[:6]]
        records[0]['status'] = records[3]['status'] = 'resource_censored'
        self.assertEqual(progression(records[:3]), 'stop_for_round_one_engineering_review')
        self.assertEqual(progression(records[:5], True), PILOT_ORDER[5])
        self.assertEqual(progression(records, True), 'stop_excessive_resource_censoring')
