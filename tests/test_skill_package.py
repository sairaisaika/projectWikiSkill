"""Keep the distributed skill self-contained and its entry resources reachable."""
import importlib.util
import json
from pathlib import Path
import re
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


if __name__ == '__main__':
    unittest.main()
