"""Reject precise-looking engineering models with inconsistent declared constraints."""
import copy
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('deep_wiki', ROOT / 'project-wiki/scripts/wiki.py')
wiki = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wiki)


class EngineeringDepthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = (Path(self.temp.name) / 'project').resolve()
        shutil.copytree(ROOT / 'evals/fixture-project', self.root, ignore=shutil.ignore_patterns('__pycache__'))
        rows = wiki.load(self.root)['routes']
        self.recovery = copy.deepcopy(next(row for row in rows if row['id'] == 'recovery'))
        self.wire = copy.deepcopy(next(row for row in rows if row['id'] == 'wire-format'))

    def resolve(self, row):
        return wiki.resolve_route(self.root, row, 2)['engineering_metrics']

    def test_pair_coverage_is_scoped_and_does_not_claim_guard_proof(self):
        result = self.resolve(self.recovery)['lifecycle']
        self.assertEqual((result['specified_pairs'], result['total_pairs']), (25, 25))
        self.assertEqual(result['transitions'], 7)
        self.assertEqual(result['unknown_pairs'], 0)
        self.assertEqual(result['unreachable_declared_states'], [])
        self.assertEqual(result['guard_exhaustiveness'], 'not verified')

    def test_complete_claim_rejects_missing_pair(self):
        self.recovery['engineering']['lifecycle']['rejected'].pop()
        with self.assertRaisesRegex(wiki.Invalid, 'unclassified'):
            self.resolve(self.recovery)

    def test_partial_model_reports_unknown_and_unclassified_separately(self):
        model = self.recovery['engineering']['lifecycle']
        model['coverage_claim'] = 'partial'
        model['rejected'].pop()
        item = model['rejected'].pop()
        model['unknown'].append({key: item[key] for key in ('from', 'event', 'reason')})
        result = self.resolve(self.recovery)['lifecycle']
        self.assertEqual((result['specified_pairs'], result['unknown_pairs'], result['unclassified_pairs']), (23, 1, 1))

    def test_unknown_states_and_empty_guards_fail(self):
        for key, value in [('to', 'invented'), ('event', 'not-an-event'), ('guard', '')]:
            row = copy.deepcopy(self.recovery)
            row['engineering']['lifecycle']['transitions'][0][key] = value
            with self.subTest(key=key), self.assertRaises(wiki.Invalid):
                self.resolve(row)

    def test_rejected_pair_cannot_also_have_a_transition(self):
        self.recovery['engineering']['lifecycle']['rejected'].append(
            {'from': 'idle', 'event': 'start', 'reason': 'contradiction', 'source_ids': ['handler']})
        with self.assertRaisesRegex(wiki.Invalid, 'overlap'):
            self.resolve(self.recovery)

    def test_duplicate_guard_does_not_silently_cover_a_branch(self):
        step = copy.deepcopy(self.recovery['engineering']['lifecycle']['transitions'][0])
        step['id'] = 'duplicate-branch'
        self.recovery['engineering']['lifecycle']['transitions'].append(step)
        with self.assertRaisesRegex(wiki.Invalid, 'distinct guards'):
            self.resolve(self.recovery)

    def test_wire_fields_are_source_linked_but_not_claimed_runtime_conformant(self):
        result = self.resolve(self.wire)['data_contract']
        self.assertEqual((result['fields'], result['source_linked_fields']), (4, 4))
        self.assertTrue(result['geometry_only'])
        self.assertEqual(result['semantic_conformance'], 'not verified')

    def test_layout_overflow_and_overlap_fail(self):
        for offset in [0, 7]:
            row = copy.deepcopy(self.wire)
            row['engineering']['data_contract']['fields'][-1]['offset_bytes'] = offset
            with self.subTest(offset=offset), self.assertRaises(wiki.Invalid):
                self.resolve(row)

    def test_byte_offsets_without_layout_fail(self):
        del self.wire['engineering']['data_contract']['layout']
        with self.assertRaisesRegex(wiki.Invalid, 'declared layout'):
            self.resolve(self.wire)

    def test_fields_require_units_nullability_and_source_provenance(self):
        for key, value in [('unit', ''), ('nullable', 'false'), ('source_ids', ['not-a-source'])]:
            row = copy.deepcopy(self.wire)
            row['engineering']['data_contract']['fields'][0][key] = value
            with self.subTest(key=key), self.assertRaises(wiki.Invalid):
                self.resolve(row)

    def test_configured_values_are_not_measured_values(self):
        result = self.resolve(self.recovery)['execution']
        self.assertEqual(result['limits_by_kind'], {'target': 0, 'configured': 2, 'measured': 0})
        self.recovery['engineering']['execution']['limits'][0]['kind'] = 'measured'
        with self.assertRaisesRegex(wiki.Invalid, 'method and evidence_refs'):
            self.resolve(self.recovery)

    def test_measurement_reference_is_checked_without_certifying_claim(self):
        limit = self.recovery['engineering']['execution']['limits'][0]
        limit.update(kind='measured', method='Hypothetical referenced method, not executed by helper', evidence_refs=['missing.md'])
        with self.assertRaisesRegex(wiki.Invalid, 'Missing reference'):
            self.resolve(self.recovery)
        limit['evidence_refs'] = ['docs/wiki/engineering-contracts.md#recovery']
        self.assertEqual(self.resolve(self.recovery)['execution']['performance_or_measurement_truth'], 'not verified')

    def test_limits_require_finite_value_and_unit(self):
        for key, value in [('value', True), ('value', float('inf')), ('unit', '')]:
            row = copy.deepcopy(self.recovery)
            row['engineering']['execution']['limits'][0][key] = value
            with self.subTest(key=key), self.assertRaises(wiki.Invalid):
                self.resolve(row)

    def test_ownership_requires_lifetime_and_release(self):
        del self.recovery['engineering']['execution']['ownership'][0]['release']
        with self.assertRaisesRegex(wiki.Invalid, 'release'):
            self.resolve(self.recovery)

    def test_adr_requires_rationale_alternatives_and_revisit_trigger(self):
        for key in ['context', 'alternatives', 'revisit_when']:
            row = copy.deepcopy(self.recovery)
            del row['engineering']['decisions'][0][key]
            with self.subTest(key=key), self.assertRaises(wiki.Invalid):
                self.resolve(row)

    def test_diagram_bindings_reject_nonexistent_source(self):
        self.recovery['diagrams'][0]['source_ids'] = ['fictional-runtime']
        with self.assertRaisesRegex(wiki.Invalid, 'Diagram source_ids'):
            self.resolve(self.recovery)

    def test_unknown_engineering_profile_is_not_ignored(self):
        self.recovery['engineering']['lifecyle'] = {}
        with self.assertRaisesRegex(wiki.Invalid, 'Unknown engineering profile'):
            self.resolve(self.recovery)

    def test_optional_profiles_do_not_inflate_or_penalize_base_score(self):
        row = wiki.resolve_route(self.root, self.recovery, 2)
        before = wiki.score(row)
        self.recovery.pop('engineering')
        after = wiki.score(wiki.resolve_route(self.root, self.recovery, 2))
        self.assertEqual(before, after)

    def test_parameter_domain_and_validation_scope_are_explicit(self):
        result = self.resolve(self.recovery)['lifecycle']
        self.assertEqual(result['context_parameters'], 1)
        self.assertIn('parameter combinations', result['coverage_scope'])
        del self.recovery['engineering']['lifecycle']['parameters'][0]['domain']
        with self.assertRaisesRegex(wiki.Invalid, 'validation_scope'):
            self.resolve(self.recovery)

    def test_six_view_policy_detects_missing_views(self):
        manifest = wiki.load(self.root)
        report = wiki.audit(self.root, manifest)
        self.assertTrue(report['ready'])
        self.assertEqual(len(report['diagram_coverage']['documented_kinds']), 6)
        row = next(row for row in manifest['routes'] if row['id'] == 'wire-format')
        row.pop('diagrams')
        report = wiki.audit(self.root, manifest)
        self.assertFalse(report['ready'])
        self.assertEqual(report['diagram_coverage']['missing_kinds'], ['data-model'])

    def test_applicability_waiver_is_not_counted_as_a_diagram(self):
        manifest = wiki.load(self.root)
        row = next(row for row in manifest['routes'] if row['id'] == 'wire-format')
        row.pop('diagrams')
        manifest['diagram_policy']['not_applicable'] = [{'kind': 'data-model', 'reason': 'Explicit task-scoped exception for this isolated test.'}]
        report = wiki.audit(self.root, manifest)
        self.assertTrue(report['ready'])
        self.assertNotIn('data-model', report['diagram_coverage']['documented_kinds'])
        self.assertEqual(report['diagram_coverage']['not_applicable'][0]['kind'], 'data-model')

    def test_policy_is_optional_for_simple_existing_routes(self):
        manifest = wiki.load(self.root)
        manifest.pop('diagram_policy')
        manifest['routes'] = [row for row in manifest['routes'] if row['id'] == 'tagger']
        report = wiki.audit(self.root, manifest)
        self.assertTrue(report['ready'])
        self.assertEqual(report['diagram_coverage']['required_kinds'], [])

    def test_malformed_six_view_policy_is_rejected(self):
        path = self.root / 'docs/wiki/routes.json'
        content = wiki.load(self.root)
        content['diagram_policy']['required_kinds'].append('fake-graph')
        import json
        path.write_text(json.dumps(content), encoding='utf-8')
        with self.assertRaisesRegex(wiki.Invalid, 'supported diagram kinds'):
            wiki.load(self.root)


if __name__ == '__main__':
    unittest.main()
