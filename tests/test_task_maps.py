"""Compound scope and edit precision must survive passing single-route rankings."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('task_wiki', ROOT / 'project-wiki/scripts/wiki.py')
wiki = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wiki)


class TaskMapTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = (Path(temp.name) / 'fixture').resolve()
        shutil.copytree(ROOT / 'evals/fixture-project', self.root)
        self.manifest = wiki.load(self.root)
        self.tasks = wiki.read_json(ROOT / 'evals/tasks.json')

    def test_compound_outline_reads_docs_without_source_resolution(self):
        shutil.rmtree(self.root / 'src')
        with patch.object(wiki, 'resolve_source', side_effect=AssertionError('Source read in task outline')):
            result = wiki.task_outline(self.root, wiki.load(self.root), 'interface-change')
        self.assertEqual([s['id'] for s in result['surfaces']], ['public', 'dependency', 'model', 'policy'])
        self.assertEqual(set(result['route_ids']), {'public-api', 'external-source', 'tagger', 'tag-rules'})
        self.assertIn('not inferred', result['evidence_boundary'])

    def test_missing_surface_fails_even_when_all_rankings_still_pass(self):
        self.manifest['task_maps'][0]['surfaces'].pop()
        result = wiki.evaluate(self.root, self.manifest, self.tasks)
        self.assertEqual(result['top1']['rate'], 1)
        self.assertFalse(result['passed'])
        self.assertEqual(result['task_map_cases'][0]['missing_surfaces'], ['policy'])
        self.assertEqual(result['task_map_cases'][0]['missing_routes'], ['tag-rules'])

    def test_valid_but_wrong_route_is_not_accepted_as_coverage(self):
        self.manifest['task_maps'][0]['surfaces'][2]['route_ids'] = ['wire-format']
        result = wiki.evaluate(self.root, self.manifest, self.tasks)
        self.assertFalse(result['passed'])
        self.assertEqual(result['task_map_cases'][0]['unexpected_routes'], ['wire-format'])
        self.assertEqual(result['task_map_cases'][0]['missing_routes'], ['tagger'])

    def test_invalid_map_references_and_duplicates_fail(self):
        for mutation in ('route', 'surface', 'map'):
            data = copy.deepcopy(self.manifest)
            item = data['task_maps'][0]
            if mutation == 'route':
                item['surfaces'][0]['route_ids'] = ['invented-api']
            elif mutation == 'surface':
                item['surfaces'].append(copy.deepcopy(item['surfaces'][0]))
            else:
                data['task_maps'].append(copy.deepcopy(item))
            with self.subTest(mutation=mutation), self.assertRaises(wiki.Invalid):
                wiki.task_maps(data)

    def test_broken_map_document_blocks_audit(self):
        self.manifest['task_maps'][0]['docs'] = ['docs/wiki/engineering-entry.md#absent']
        result = wiki.audit(self.root, self.manifest)
        self.assertFalse(result['ready'])
        self.assertFalse(result['task_maps'][0]['valid'])
        with self.assertRaises(wiki.Invalid):
            wiki.task_outline(self.root, self.manifest, 'unknown-task')

    def test_task_scope_change_is_snapshot_drift(self):
        current = wiki.snapshot(self.root, self.manifest)
        for path, body in zip(wiki.index_paths(self.root), [json.dumps(current), wiki.markdown_index(current)]):
            path.write_text(body, encoding='utf-8')
        self.assertFalse(wiki.is_stale(self.root, current))
        self.manifest['task_maps'][0]['surfaces'][0]['why'] = 'A changed technical dependency'
        self.assertTrue(wiki.is_stale(self.root, wiki.snapshot(self.root, self.manifest)))

    def test_edit_target_metadata_adds_no_structural_score(self):
        route = next(row for row in self.manifest['routes'] if row['id'] == 'tagger')
        source = next(s for s in route['sources'] if s['id'] == 'sanitize')
        with_metadata = wiki.score(wiki.resolve_route(self.root, route, 2))
        source.pop('edit_for')
        source.pop('visibility')
        self.assertEqual(with_metadata, wiki.score(wiki.resolve_route(self.root, route, 2)))
        for fields in ({'edit_for': []}, {'edit_for': 'guess'}, {'visibility': 'external-service'}):
            source.update(fields)
            with self.subTest(fields=fields), self.assertRaises(wiki.Invalid):
                wiki.resolve_route(self.root, route, 2)
            for key in fields:
                source.pop(key)

    def test_moved_internal_edit_target_is_recomputed(self):
        route = next(row for row in self.manifest['routes'] if row['id'] == 'tagger')
        source = next(s for s in route['sources'] if s['id'] == 'sanitize')
        before = wiki.resolve_source(self.root, source)
        path = self.root / source['path']
        path.write_text('# moved\n' + path.read_text(encoding='utf-8'), encoding='utf-8')
        after = wiki.resolve_route(self.root, route, 2)
        located = next(item for item in after['locations'] if item['id'] == 'sanitize')
        self.assertEqual(located['line'], before['line'] + 1)
        self.assertEqual(located['visibility'], 'internal')


if __name__ == '__main__':
    unittest.main()
