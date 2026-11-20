"""Default-package reachability and off-topic controls; not agent-use proof."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import test_plugin_package as package_tests

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'evals/fixture-project'


class LogContractNavigationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.package = Path(temp.name) / 'package'
        package_tests.builder.build(self.package)
        self.skill = self.package / 'skills/project-wiki'
        self.entry = (self.skill / 'SKILL.md').read_text(encoding='utf-8')

    def query(self, text):
        result = subprocess.run([sys.executable, str(self.skill / 'scripts/wiki.py'), 'query',
                                 '--root', str(FIXTURE), '--json', text], capture_output=True,
                                env={**os.environ, 'PYTHONUTF8': '1'}, check=True)
        return json.loads(result.stdout)['matches']

    def test_packaged_entry_reaches_contract_sources_samples_and_focused_check(self):
        target = re.search(r'\[evidence-to-contract path\]\(([^)]+)\)', self.entry).group(1)
        path, anchor = target.split('#')
        owner = self.skill / path
        self.assertTrue(owner.is_file())
        self.assertEqual(anchor, 'debug-from-evidence-to-a-technical-contract')
        method = owner.read_text(encoding='utf-8')
        self.assertIn('Logs are evidence, not the specification', method)
        for query in ('log contract debugging', '日志契约'):
            route = self.query(query)[0]
            self.assertEqual(route['id'], 'public-api')
            self.assertIn('docs/wiki/interfaces.md#diagnostic-evidence', route['docs'])
            roles = {location['role']: location['symbol'] for location in route['locations']}
            self.assertEqual(roles, {'declaration': 'ArticleSource.list_articles',
                                     'implementation': 'get_articles', 'consumer': 'read_articles'})
        page = (FIXTURE / 'docs/wiki/interfaces.md').read_text(encoding='utf-8')
        sample_link = re.search(r'\[the synthetic packets\]\(([^)]+)\)', page).group(1)
        samples = json.loads((FIXTURE / 'docs/wiki' / sample_link).read_text(encoding='utf-8'))
        self.assertFalse(samples['runtime_evidence'])
        self.assertEqual(len(samples['packets']), 6)
        command = re.search(r'`(python -m unittest discover -s tests -p test_diagnostic_evidence.py -v)`', page)
        self.assertIsNotNone(command)
        result = subprocess.run([sys.executable, *command.group(1).split()[1:]], cwd=FIXTURE,
                                capture_output=True, env={**os.environ, 'PYTHONUTF8': '1'})
        self.assertEqual(result.returncode, 0, 'The routed offline diagnostic check failed')

    def test_ordinary_edit_has_early_skip_and_no_diagnostic_query_match(self):
        self.assertLess(self.entry.index('## Keep the entry proportional'),
                        self.entry.index('## File-first entry'))
        cue = self.entry.split('## Keep the entry proportional', 1)[1].split('\n## ', 1)[0]
        self.assertIn("project's existing lightweight path", cue)
        self.assertIn('Do not add a specialist read or record', cue)
        self.assertIn("project's mandatory gates", cue)
        self.assertIn('staging or publication hygiene trigger', cue)
        # Counterfactual query, not a requirement to query for a spelling-only edit.
        for query in ('Fix punctuation in a known README sentence', 'Correct a spelling mistake in an existing comment'):
            self.assertEqual(self.query(query), [])
        for name in ('maintenance.md', 'wiki-evolution.md'):
            text = (self.skill / 'references' / name).read_text(encoding='utf-8')
            self.assertIn('../SKILL.md#keep-the-entry-proportional', text)
