"""Opt-in diagram presence and declared-file suggestions, not semantic enforcement."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('diagram_wiki', ROOT / 'project-wiki/scripts/wiki.py')
wiki = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wiki)


class DiagramLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = (Path(self.temp.name) / 'project').resolve()
        shutil.copytree(ROOT / 'evals/fixture-project', self.root, ignore=shutil.ignore_patterns('__pycache__'))
        self.manifest = wiki.load(self.root)
        self.row = self.manifest['routes'][0]

    def test_new_domain_missing_required_diagram_is_pending_and_not_ready(self):
        self.row['diagram_requirement'] = {'level': 'section', 'required': True, 'reason': 'New business domain boundary'}
        self.row['diagrams'] = []
        report = wiki.audit(self.root, self.manifest)
        self.assertFalse(report['ready'])
        self.assertIn('Required diagram missing', report['routes'][0]['error'])

    def test_canonical_diagram_on_other_page_satisfies_presence_only(self):
        self.row['diagram_requirement'] = {'level': 'section', 'required': True, 'reason': 'Shared canonical flow'}
        self.assertTrue(wiki.audit(self.root, self.manifest)['ready'])

    def test_faq_explicit_exemption_and_legacy_no_requirement(self):
        self.row['diagrams'] = []
        self.manifest.pop('diagram_policy')
        self.assertTrue(wiki.audit(self.root, self.manifest)['ready'])
        self.row['diagram_requirement'] = {'level': 'page', 'required': False, 'reason': 'FAQ links existing domain explanation; no new behavior'}
        self.assertTrue(wiki.audit(self.root, self.manifest)['ready'])
        self.row['diagram_requirement']['reason'] = ''
        self.assertFalse(wiki.audit(self.root, self.manifest)['ready'])

    def test_broken_canonical_anchor_and_unknown_source_id_fail(self):
        for key, value in [('path', 'docs/wiki/project-views.md#missing'), ('source_ids', ['missing'])]:
            row = copy.deepcopy(self.row)
            row['diagrams'][0][key] = value
            with self.subTest(key=key), self.assertRaises(wiki.Invalid):
                wiki.resolve_route(self.root, row, 2)

    def test_source_ids_filter_exact_diagrams_and_leave_review_pending(self):
        report = wiki.diagram_review(self.root, self.manifest, ['src/recovery.py'])
        paths = {item['path'] for item in report['candidates']}
        self.assertIn('docs/wiki/engineering-contracts.md#recovery-state', paths)
        self.assertNotIn('docs/wiki/project-views.md#deployment', paths)
        self.assertTrue(all(item['disposition'] == 'pending' for item in report['candidates']))

    def test_behavior_and_copy_changes_have_same_candidates_not_forced_redraw(self):
        path = self.root / 'src/service.py'
        before = wiki.diagram_review(self.root, self.manifest, ['src/service.py'])
        path.write_text('# Copy-only change', encoding='utf-8')
        self.assertEqual(before, wiki.diagram_review(self.root, self.manifest, ['src/service.py']))
        path.write_text('raise RuntimeError("Changed behavior")', encoding='utf-8')
        self.assertEqual(before, wiki.diagram_review(self.root, self.manifest, ['src/service.py']))
        path.unlink()
        self.assertEqual(before, wiki.diagram_review(self.root, self.manifest, ['src/service.py']))
        self.assertIn('reviewed unchanged', before['finish'])

    def test_docs_page_and_unknown_paths_are_not_claimed_semantically_complete(self):
        report = wiki.diagram_review(self.root, self.manifest, ['docs/wiki/project-views.md', 'new/unknown.py'])
        self.assertGreater(report['candidate_count'], 0)
        self.assertEqual(report['unmapped_file_count'], 1)
        self.assertIn('not semantic', report['scope'])

    def test_deterministic_pagination_and_byte_budget(self):
        diagram = self.row['diagrams'][0]
        self.row['diagrams'] = [dict(diagram, path=diagram['path'] + str(i)) for i in range(100)]
        whole = wiki.diagram_review(self.root, self.manifest, ['src/service.py'])
        rows, offset = [], 0
        while True:
            report = wiki.diagram_review(self.root, self.manifest, ['src/service.py'], offset, 3)
            self.assertLess(len(json.dumps(report).encode()), 12000)
            rows.extend(report['candidates'])
            if report['next_offset'] is None:
                break
            self.assertGreater(report['next_offset'], offset)
            offset = report['next_offset']
        self.assertEqual(len(rows), whole['candidate_count'])
        self.assertEqual(len({(r['route_id'], r['path']) for r in rows}), len(rows))

    def test_invalid_input_limits_and_traversal_are_rejected(self):
        for paths in [['../outside.py'], ['src/a.py'] * 257, ['x' * 1025]]:
            with self.subTest(paths=paths[:1]), self.assertRaises(wiki.Invalid):
                wiki.diagram_review(self.root, self.manifest, paths)

    def test_other_section_mermaid_does_not_satisfy_empty_target(self):
        page = self.root / 'docs/wiki/empty-scope.md'
        page.write_text('# Empty scope\nNo diagram here.\n# Other scope\n```mermaid\nflowchart LR\n A-->B\n```\n', encoding='utf-8')
        self.row['diagrams'][0]['path'] = 'docs/wiki/empty-scope.md#empty-scope'
        self.row['diagram_requirement'] = {'level': 'section', 'required': True, 'reason': 'Declared boundary view'}
        report = wiki.audit(self.root, self.manifest)
        self.assertFalse(report['ready'])
        self.assertIn('selected section', report['routes'][0]['error'])
        self.assertEqual(report['diagram_coverage']['renderer_verification'], 'not performed by helper')

    def test_audit_cli_exposes_paginated_review_without_mutation(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        cp = subprocess.run([sys.executable, '-B', str(ROOT / 'project-wiki/scripts/wiki.py'), 'audit',
                             '--root', str(self.root), '--changed-file', 'src/service.py', '--diagram-limit', '1'],
                            capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(cp.returncode, 0, cp.stderr)
        review = json.loads(cp.stdout)['diagram_review']
        self.assertEqual(len(review['candidates']), 1)
        self.assertTrue(review['truncated'])
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_required_presence_rejects_empty_unclosed_and_wrong_duplicate_section(self):
        self.row['diagram_requirement'] = {'level': 'page', 'required': True, 'reason': 'Behavior view'}
        self.row['diagrams'][0]['path'] = 'docs/wiki/presence.md#view-1'
        page = self.root / 'docs/wiki/presence.md'
        for body in ['```mermaid\n```', '```mermaid\nflowchart LR\n A-->B', 'Only text']:
            page.write_text('# View\n```mermaid\nflowchart LR\n A-->B\n```\n# View\n' + body, encoding='utf-8')
            with self.subTest(body=body), self.assertRaises(wiki.Invalid):
                wiki.resolve_route(self.root, self.row, 2)
        page.write_text('# View\nText\n# View\n## Nested\n```mermaid\nflowchart LR\n A-->B\n```\n', encoding='utf-8')
        wiki.resolve_route(self.root, self.row, 2)

    def test_audit_cli_retains_invalid_route_report_instead_of_traceback(self):
        for malformed in ('source', 'diagram'):
            manifest = copy.deepcopy(self.manifest)
            if malformed == 'source':
                manifest['routes'][0]['sources'] = ['not a source record']
            else:
                manifest['routes'][0]['diagrams'][0]['path'] = None
            (self.root / 'docs/wiki/routes.json').write_text(json.dumps(manifest), encoding='utf-8')
            cp = subprocess.run([sys.executable, '-B', str(ROOT / 'project-wiki/scripts/wiki.py'), 'audit',
                                 '--root', str(self.root), '--changed-file', 'src/service.py'],
                                capture_output=True, text=True, encoding='utf-8')
            with self.subTest(malformed=malformed):
                self.assertEqual(cp.returncode, 1)
                self.assertNotIn('Traceback', cp.stderr)
                result = json.loads(cp.stdout)
                self.assertFalse(result['routes'][0]['valid'])
                self.assertEqual(result['diagram_review']['unavailable_route_count'], 1)


class UndeclaredMermaidReviewTests(unittest.TestCase):
    """Mermaid drawn directly in Wiki pages is reachable from a changed file by its literal name."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = (Path(self.temp.name) / 'project').resolve()
        shutil.copytree(ROOT / 'evals/fixture-project', self.root, ignore=shutil.ignore_patterns('__pycache__'))
        self.manifest = wiki.load(self.root)
        self.page = self.root / 'docs/wiki/native-architecture.md'
        self.page.write_text(
            '# Architecture\nProse naming src/recovery.py outside any drawing.\n'
            '## Module graph\n```mermaid\nflowchart LR\n  A["service.py"] --> B["src/recovery.py"]\n```\n'
            '## Unrelated\n```mermaid\nflowchart LR\n  X["myservice.py"] --> Y["other"]\n```\n'
            '## Listing\n```text\nservice.py\n```\n', encoding='utf-8')

    def native(self, *paths):
        report = wiki.diagram_review(self.root, self.manifest, list(paths), 0, 50)
        return report, [item for item in report['candidates'] if item['route_id'] is None]

    def test_a_drawing_that_names_the_changed_file_is_suggested_by_section(self):
        report, rows = self.native('src/service.py')
        self.assertEqual([item['path'] for item in rows], ['docs/wiki/native-architecture.md#module-graph'])
        self.assertEqual(rows[0]['disposition'], 'pending')
        self.assertIn('undeclared Mermaid', rows[0]['basis'])
        self.assertIn('undeclared Mermaid', report['scope'])
        self.assertEqual(report['undeclared_pages_skipped'], 0)

    def test_the_full_path_matches_and_a_longer_name_does_not(self):
        _, rows = self.native('src/recovery.py')
        self.assertEqual([item['path'] for item in rows], ['docs/wiki/native-architecture.md#module-graph'])
        _, rows = self.native('lib/myservice.py')
        self.assertEqual([item['path'] for item in rows], ['docs/wiki/native-architecture.md#unrelated'])

    def test_prose_and_other_fences_are_not_drawings(self):
        self.page.write_text('# Architecture\nservice.py is described here.\n```text\nservice.py\n```\n', encoding='utf-8')
        _, rows = self.native('src/service.py')
        self.assertEqual(rows, [])

    def test_a_file_only_a_drawing_names_is_mapped_not_unmapped(self):
        self.page.write_text('# Architecture\n```mermaid\nflowchart LR\n  A["brand_new.py"] --> B\n```\n', encoding='utf-8')
        report, rows = self.native('src/brand_new.py', 'src/never_mentioned.py')
        self.assertEqual([item['path'] for item in rows], ['docs/wiki/native-architecture.md#architecture'])
        self.assertEqual(report['unmapped_file_count'], 1)

    def test_a_declared_diagram_section_is_not_suggested_twice(self):
        declared = self.manifest['routes'][0]['diagrams'][0]['path']
        name, _, fragment = declared.partition('#')
        page = self.root / name
        page.write_text(page.read_text(encoding='utf-8').replace('```mermaid\n', '```mermaid\n%% service.py\n'),
                        encoding='utf-8')
        _, rows = self.native('src/service.py')
        self.assertNotIn(declared, [item['path'] for item in rows])

    def test_an_oversized_page_is_skipped_and_counted(self):
        self.page.write_text('# Big\n```mermaid\nflowchart LR\n  A["service.py"]\n```\n' + 'x' * (1024 * 1024),
                             encoding='utf-8')
        report, rows = self.native('src/service.py')
        self.assertEqual(rows, [])
        self.assertEqual(report['undeclared_pages_skipped'], 1)

    def test_the_review_is_deterministic_and_reads_only(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        first, _ = self.native('src/service.py', 'src/recovery.py')
        second, _ = self.native('src/recovery.py', 'src/service.py')
        self.assertEqual(first, second)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
