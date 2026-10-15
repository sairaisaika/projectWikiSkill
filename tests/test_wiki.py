"""Behavioral acceptance of the standalone helper using isolated project copies."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
HELPER = REPO / 'project-wiki/scripts/wiki.py'
spec = importlib.util.spec_from_file_location('wiki', HELPER)
wiki = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wiki)


class WikiTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'project'
        shutil.copytree(REPO / 'evals/fixture-project', self.root, ignore=shutil.ignore_patterns('__pycache__'))
        self.root = self.root.resolve()
        self.manifest = wiki.load(self.root)

    def call(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = wiki.main([*args, '--root', str(self.root)])
        return code, output.getvalue()

    def save_manifest(self):
        (self.root / 'docs/wiki/routes.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def test_fixture_structure_and_honest_missing_ts_tests(self):
        report = wiki.audit(self.root, self.manifest)
        self.assertTrue(report['ready'])
        self.assertEqual(report['route_count'], 7)
        scores = {row['id']: row['score']['total'] for row in report['routes']}
        self.assertEqual(scores['external-source'], 92)
        self.assertEqual(scores['public-api'], 100)
        self.assertEqual(report['semantic_accuracy'], 'not measured')

    def test_routing_questions_and_unknown_controls(self):
        report = wiki.evaluate(self.root, self.manifest, wiki.read_json(REPO / 'evals/tasks.json'))
        self.assertTrue(report['passed'])
        self.assertEqual(report['top1']['numerator'], 20)
        self.assertEqual(report['top1']['denominator'], 20)
        self.assertEqual(report['unknown_rejection']['numerator'], 4)
        self.assertLessEqual(report['max_response_words'], 450)

    def test_moved_python_symbol_resolves_new_position(self):
        entry = self.manifest['routes'][0]['sources'][1]
        old = wiki.resolve_source(self.root, entry)
        path = self.root / entry['path']
        path.write_text('# moved\n\n' + path.read_text(encoding='utf-8'), encoding='utf-8')
        new = wiki.resolve_source(self.root, entry)
        self.assertEqual(new['line'], old['line'] + 2)
        self.assertNotEqual(new['sha256'], old['sha256'])

    def test_nested_class_and_async_symbol(self):
        path = self.root / 'src/nested.py'
        path.write_text('class Repository:\n    async def load(self):\n        return []\n', encoding='utf-8')
        self.assertEqual(wiki.resolve_source(self.root, {'path': 'src/nested.py', 'symbol': 'Repository.load'})['line'], 2)

    def test_missing_python_symbol_is_not_guessed(self):
        with self.assertRaisesRegex(wiki.Invalid, 'got 0'):
            wiki.resolve_source(self.root, {'path': 'src/service.py', 'symbol': 'missing'})

    def test_duplicate_typescript_needle_is_not_first_match(self):
        path = self.root / 'src/provider.ts'
        path.write_text(path.read_text(encoding='utf-8') + '\nexport interface ExternalSource {}\n', encoding='utf-8')
        with self.assertRaisesRegex(wiki.Invalid, 'got 2'):
            wiki.resolve_source(self.root, self.manifest['routes'][1]['sources'][0])

    def test_unsupported_language_symbol_instructs_use_needle(self):
        with self.assertRaisesRegex(wiki.Invalid, 'unique needle'):
            wiki.resolve_source(self.root, {'path': 'src/provider.ts', 'symbol': 'ExternalSource'})

    def test_exactly_one_locator_is_required(self):
        for entry in [{'path': 'src/service.py'}, {'path': 'src/service.py', 'symbol': 'get_articles', 'needle': 'def get_articles'}]:
            with self.subTest(entry=entry), self.assertRaises(wiki.Invalid):
                wiki.resolve_source(self.root, entry)

    def test_anchors_ignore_code_and_handle_explicit_and_duplicate_headings(self):
        content = '<a id="explicit"></a>\n# Heading\n# Heading\n```md\n# Fake\n```\n# 中文说明\n'
        self.assertEqual(wiki.anchors(content), {'explicit', 'heading', 'heading-1', '中文说明'})

    def test_missing_anchor_and_reference_fail(self):
        for reference in ['docs/wiki/interfaces.md#absent', 'tests/missing.py']:
            with self.subTest(reference=reference), self.assertRaises(wiki.Invalid):
                wiki.verify_ref(self.root, reference)

    def test_root_escape_and_absolute_paths_are_rejected(self):
        for name in ['../outside.py', '/etc/passwd', 'C:/private.txt', 'C:private.txt', 'src\\service.py']:
            with self.subTest(name=name), self.assertRaises(wiki.Invalid):
                wiki.local(self.root, name)

    def test_symlink_escape_is_rejected(self):
        outside = Path(self.temporary.name) / 'outside.txt'
        outside.write_text('outside', encoding='utf-8')
        link = self.root / 'src/link.py'
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest('Host does not permit unprivileged symlinks')
        with self.assertRaises(wiki.Invalid):
            wiki.resolve_source(self.root, {'path': 'src/link.py', 'needle': 'outside'})

    def test_stale_and_tampered_indexes_fail_without_repair(self):
        self.assertEqual(self.call('build')[0], 0)
        self.assertEqual(self.call('check')[0], 0)
        index = self.root / 'docs/wiki/route-index.md'
        index.write_text('tampered', encoding='utf-8')
        self.assertEqual(self.call('check')[0], 1)
        self.assertEqual(index.read_text(encoding='utf-8'), 'tampered')
        self.assertEqual(self.call('build')[0], 0)
        source = self.root / 'src/service.py'
        source.write_text('# moved\n' + source.read_text(encoding='utf-8'), encoding='utf-8')
        self.assertEqual(self.call('check')[0], 1)
        self.assertEqual(self.call('build')[0], 0)
        self.assertEqual(self.call('check')[0], 0)

    def test_crlf_lf_and_bom_do_not_cause_source_drift(self):
        entry = self.manifest['routes'][0]['sources'][1]
        path = self.root / entry['path']
        old = wiki.resolve_source(self.root, entry)
        path.write_bytes(b'\xef\xbb\xbf' + path.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
        self.assertEqual(wiki.resolve_source(self.root, entry)['sha256'], old['sha256'])

    def test_query_only_resolves_selected_route_and_preserves_warnings(self):
        self.manifest['routes'][1]['sources'][0]['needle'] = 'missing declaration'
        self.save_manifest()
        self.assertEqual(self.call('query', 'legacy client')[0], 0)
        code, output = self.call('query', 'external source')
        self.assertEqual(code, 1)
        self.assertIn('WARNING', output)
        self.assertIn('docs/wiki/interfaces.md#external-source', output)

    def test_invalid_selected_rule_does_not_hide_doc_pointer(self):
        self.manifest['routes'][0]['rules'] = 'invalid'
        self.save_manifest()
        code, output = self.call('query', 'legacy client')
        self.assertEqual(code, 1)
        self.assertIn('docs/wiki/interfaces.md#public-api', output)

    def test_legacy_audit_is_not_schema2_readiness(self):
        self.manifest['schema_version'] = 1
        for row in self.manifest['routes']:
            for key in ('kind', 'interface', 'rules', 'evidence', 'unknowns', 'reviewed_at', 'impact'):
                row.pop(key, None)
            row['checks'] = ['python -m unittest discover -s tests']
        self.save_manifest()
        self.assertEqual(self.call('query', 'legacy client')[0], 0)
        code, output = self.call('audit')
        report = json.loads(output)
        self.assertEqual(code, 1)
        self.assertEqual(report['mode'], 'legacy-gap-analysis')
        self.assertIsNone(report['structural_average'])
        self.assertIn('interface', report['routes'][0]['gaps'])
        self.assertEqual(self.call('build')[0], 1)

    def test_missing_contract_is_a_hard_interface_failure(self):
        del self.manifest['routes'][0]['interface']['errors']
        report = wiki.audit(self.root, self.manifest)
        self.assertFalse(report['ready'])
        self.assertFalse(report['routes'][0]['valid'])

    def test_one_low_score_is_not_hidden_by_average(self):
        row = self.manifest['routes'][0]
        for key in ('impact', 'checks', 'tests', 'aliases', 'reviewed_at'):
            row.pop(key, None)
        report = wiki.audit(self.root, self.manifest)
        self.assertFalse(report['ready'])
        self.assertLess(report['structural_minimum'], 85)
        self.assertGreater(report['structural_average'], report['structural_minimum'])

    def test_rule_provenance_and_evidence_paths_must_exist(self):
        row = copy.deepcopy(self.manifest['routes'][0])
        row['rules'][0]['source_ids'] = ['invented']
        with self.assertRaises(wiki.Invalid):
            wiki.resolve_route(self.root, row, 2)
        row = copy.deepcopy(self.manifest['routes'][0])
        row['evidence']['observations'][0]['reference'] = 'missing-receipt.md'
        with self.assertRaises(wiki.Invalid):
            wiki.resolve_route(self.root, row, 2)

    def test_plan_cannot_claim_live_verification(self):
        row = copy.deepcopy(self.manifest['routes'][0])
        row.update(kind='plan', sources=[], rules=[dict(id='proposal', statement='Proposed new result API.', source_ids=[], proposed=True)])
        row.pop('diagrams', None)  # Implemented diagram bindings do not belong to this source-free plan.
        row['plan'] = dict(outcomes=['Preserve detailed errors'], dependencies=[], interfaces=['Proposed additive client result'], deliverables=['Client and compatibility cases'], exit_evidence=['Offline compatibility tests'], unknowns=['Error union undecided'])
        row['evidence']['implementation'] = 'planned'
        row['evidence']['observations'] = []
        resolved = wiki.resolve_route(self.root, row, 2)
        self.assertFalse(resolved['locations'])
        row['evidence']['observations'] = [dict(level='live-verified', reference='src/service.py', claim='Live', revision='x', observed_at='2026-10-14')]
        with self.assertRaises(wiki.Invalid):
            wiki.resolve_route(self.root, row, 2)

    def test_plan_missing_delivery_or_acceptance_is_rejected(self):
        row = copy.deepcopy(self.manifest['routes'][0])
        row.update(kind='plan', sources=[], rules=[])
        row['evidence'] = dict(implementation='planned', observations=[])
        with self.assertRaisesRegex(wiki.Invalid, 'Plans require'):
            wiki.resolve_route(self.root, row, 2)

    def test_commands_are_data_never_executed(self):
        marker = self.root / 'SHOULD_NOT_EXIST'
        self.manifest['routes'][0]['checks'] = [dict(command='touch SHOULD_NOT_EXIST', scope='Must remain data only')]
        self.save_manifest()
        self.call('audit')
        self.call('query', 'legacy client')
        self.call('build')
        self.assertFalse(marker.exists())

    def test_evaluation_failure_and_denominators(self):
        tasks = wiki.read_json(REPO / 'evals/tasks.json')
        tasks['tasks'][0]['expected_routes'] = ['tagger']
        report = wiki.evaluate(self.root, self.manifest, tasks)
        self.assertEqual(report['top1']['numerator'], 19)
        self.assertEqual(report['top1']['denominator'], 20)
        tasks['thresholds']['min_top1'] = 1
        self.assertFalse(wiki.evaluate(self.root, self.manifest, tasks)['passed'])

    def test_small_evaluation_and_missing_unknown_controls_fail(self):
        tasks = wiki.read_json(REPO / 'evals/tasks.json')
        tasks['tasks'] = tasks['tasks'][:2]
        self.assertFalse(wiki.evaluate(self.root, self.manifest, tasks)['passed'])

    def test_malformed_input_returns_nonzero_without_traceback(self):
        for value in [[], {'schema_version': True}, {'schema_version': 2, 'project': 'x', 'routes': [{}, {}]}]:
            (self.root / 'docs/wiki/routes.json').write_text(json.dumps(value), encoding='utf-8')
            code, output = self.call('audit')
            self.assertEqual(code, 1)
            self.assertFalse(json.loads(output)['valid'])

    def test_bad_review_date_is_not_freshness_credit(self):
        self.manifest['routes'][0]['reviewed_at'] = '2026-02-30'
        self.assertFalse(wiki.audit(self.root, self.manifest)['ready'])

    def test_failure_contract_cannot_silently_omit_thrown_behavior(self):
        del self.manifest['routes'][0]['interface']['failure_modes']['thrown']
        self.assertFalse(wiki.audit(self.root, self.manifest)['ready'])

    def test_compound_query_discloses_truncation(self):
        question = 'legacy client external source model suggestions trust policy'
        code, output = self.call('query', question)
        self.assertEqual(code, 0)
        self.assertIn('Showing top 2 of 4', output)
        self.assertIn('Split compound requests', output)
        _, output = self.call('query', question, '--json')
        self.assertTrue(json.loads(output)['truncated'])


if __name__ == '__main__':
    unittest.main()
