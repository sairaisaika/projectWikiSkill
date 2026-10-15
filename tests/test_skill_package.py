"""Keep the distributed skill self-contained and its entry resources reachable."""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'project-wiki'
spec = importlib.util.spec_from_file_location('package_wiki', SKILL / 'scripts/wiki.py')
wiki = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wiki)


class SkillPackageTests(unittest.TestCase):
    def test_entry_and_metadata_are_installable_without_private_paths(self):
        content = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(content.startswith('---\nname: project-wiki\n'))
        self.assertRegex(content, r'(?m)^description: .+')
        self.assertNotIn('[TODO', content)
        metadata = (SKILL / 'agents/openai.yaml').read_text(encoding='utf-8')
        self.assertIn('$project-wiki', metadata)
        self.assertNotIn('allow_implicit_invocation: false', metadata)
        self.assertTrue((SKILL / 'scripts/wiki.py').is_file())

    def test_distributed_markdown_links_stay_within_package_and_resolve(self):
        files = [ROOT / 'README.md', *SKILL.rglob('*.md')]
        for path in files:
            content = path.read_text(encoding='utf-8')
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
                if re.match(r'https?://', target):
                    continue
                name, _, anchor = target.partition('#')
                resolved = (path.parent / name).resolve()
                with self.subTest(path=path.name, target=target):
                    self.assertTrue(resolved.is_relative_to(ROOT))
                    self.assertTrue(resolved.is_file())
                    if anchor:
                        self.assertIn(anchor, wiki.anchors(resolved.read_text(encoding='utf-8')))

    def test_committed_fixture_index_matches_source(self):
        root = (ROOT / 'evals/fixture-project').resolve()
        manifest = wiki.load(root)
        self.assertFalse(wiki.is_stale(root, wiki.snapshot(root, manifest)))

    def test_saved_synthetic_reports_are_reproducible(self):
        root = (ROOT / 'evals/fixture-project').resolve()
        manifest = wiki.load(root)
        reports = {
            'fixture-structure': wiki.audit(root, manifest),
            'fixture-routing': wiki.evaluate(root, manifest, wiki.read_json(ROOT / 'evals/tasks.json')),
        }
        for name, current in reports.items():
            with self.subTest(report=name):
                saved = json.loads((ROOT / 'evals/reports' / (name + '.json')).read_text(encoding='utf-8'))
                self.assertEqual(current, saved)

    def test_cli_emits_utf8_even_with_legacy_windows_stdout_encoding(self):
        environment = dict(os.environ, PYTHONIOENCODING='cp1252')
        result = subprocess.run(
            [sys.executable, str(SKILL / 'scripts/wiki.py'), 'evaluate',
             '--root', str(ROOT / 'evals/fixture-project'), '--tasks', str(ROOT / 'evals/tasks.json')],
            capture_output=True, env=environment, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', errors='replace'))
        report = json.loads(result.stdout.decode('utf-8'))
        self.assertTrue(report['passed'])
        self.assertTrue(any('换文献源' in item['query'] for item in report['tasks']))

    def test_saved_render_receipt_matches_current_diagram_sources(self):
        root = (ROOT / 'evals/fixture-project').resolve()
        manifest = wiki.load(root)
        files = list(dict.fromkeys(diagram['path'].split('#')[0]
                                  for row in manifest['routes'] for diagram in row.get('diagrams', [])))
        expected = []
        for file in files:
            content = (root / file).read_text(encoding='utf-8')
            for code in re.findall(r'```mermaid\n([\s\S]*?)```', content):
                expected.append((file, hashlib.sha256(code.encode('utf-8')).hexdigest()))
        report = json.loads((ROOT / 'evals/reports/diagram-rendering.json').read_text(encoding='utf-8'))
        self.assertEqual([(item['file'], item['source_sha256']) for item in report['diagrams']], expected)
        self.assertEqual(report['rendered'], report['total'])
        self.assertEqual(report['total'], 6)
        self.assertTrue(all(item['parsed'] and item['rendered'] for item in report['diagrams']))


if __name__ == '__main__':
    unittest.main()
