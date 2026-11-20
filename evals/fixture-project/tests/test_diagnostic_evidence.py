"""Synthetic samples + executable offline checks, never production evidence."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from service import get_articles
from client import read_articles
from diagnostic_example import SOURCE_HASHES, assess, event


class DiagnosticEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.packets = json.loads((ROOT / 'docs/wiki/diagnostic-samples.json').read_text(encoding='utf-8'))['packets']

    def test_contract_snapshot_binds_actual_producer_and_consumer_bytes(self):
        for path, expected in SOURCE_HASHES.items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected)
        self.assertEqual(set(SOURCE_HASHES), {'src/ports.py', 'src/service.py', 'src/client.py'})

    def test_actual_offline_success_error_and_legacy_mapping(self):
        for rows in ([], ['synthetic'], None):
            class Source:
                def list_articles(self, query):
                    return rows
            result = get_articles(Source(), {})
            # One operation: pass its produced result to the actual consumer.
            client = read_articles(lambda source, query: result, Source(), {})
            packet = {'coverage': 'complete', 'events': [event('article-service', result.get('data')),
                                                        event('legacy-client', client)]}
            expected = 'consistent_error' if rows is None else 'consistent_success'
            self.assertEqual(assess(packet)['status'], expected)
            self.assertEqual(assess(packet)['runtime'], 'unverified')
        class BrokenSource:
            def list_articles(self, query):
                raise RuntimeError('synthetic failure; no log assertion output')
        with self.assertRaises(RuntimeError):
            get_articles(BrokenSource(), {})

    def test_authored_packets_distinguish_success_error_and_mismatch(self):
        expected = {'packet-a': 'consistent_success', 'packet-b': 'consistent_error',
                    'packet-c': 'contract_mismatch', 'packet-d': 'unknown',
                    'packet-e': 'unknown', 'packet-f': 'unusable'}
        for packet in self.packets:
            self.assertEqual(assess(packet)['status'], expected[packet['id']])
            self.assertEqual(assess(packet)['runtime'], 'unverified')

    def test_noisy_ambiguous_or_versionless_evidence_is_not_accepted(self):
        good = self.packets[0]
        noisy = copy.deepcopy(good)
        noisy['events'].append(copy.deepcopy(noisy['events'][0]))
        self.assertEqual(assess(noisy)['status'], 'unusable')
        for key, value in [('contract', 'unverified-v2'), ('correlation_id', 'synthetic-op-2')]:
            bad = copy.deepcopy(good)
            bad['events'][1][key] = value
            self.assertEqual(assess(bad)['status'], 'unusable')

    def test_accepted_or_queued_is_not_succeeded(self):
        for outcome in ('accepted', 'queued'):
            packet = copy.deepcopy(self.packets[3])
            packet['events'][0]['outcome'] = outcome
            report = assess(packet)
            self.assertEqual(report['status'], 'unknown')
            self.assertEqual(report['observed'], ['service.accepted:' + outcome])

    def test_missing_filtered_sampled_dropped_evidence_means_unknown(self):
        for coverage in ('complete', 'filtered', 'sampled', 'dropped', 'unknown'):
            report = assess({'coverage': coverage, 'events': []})
            self.assertEqual(report['status'], 'unknown')
            self.assertEqual(report['observed'], [])
            self.assertEqual(report['runtime'], 'unverified')

    def test_unsafe_fields_and_identifiers_fail_without_echoing_values(self):
        marker = 'SYNTHETIC_PRIVATE_CANARY'
        for field in ('client_payload', 'credential', 'correlation_id', 'error_code'):
            bad = copy.deepcopy(self.packets[0])
            bad['events'][0][field] = marker
            report = assess(bad)
            output = json.dumps(report)
            self.assertEqual(report['status'], 'unusable')
            self.assertTrue(marker not in output, 'Diagnostic output exposed excluded material')
            self.assertTrue(field not in output, 'Diagnostic output exposed unapproved input field')
