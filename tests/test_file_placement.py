"""Public synthetic placement intent + real Git semantics; no runtime classifier."""
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
import test_plugin_package as package_tests
import test_repository_hygiene as hygiene


class FilePlacementTests(unittest.TestCase):
    setUp = hygiene.RepositoryHygieneTests.setUp
    git = hygiene.RepositoryHygieneTests.git
    write = hygiene.RepositoryHygieneTests.write
    documented = hygiene.RepositoryHygieneTests.documented
    ignored = hygiene.RepositoryHygieneTests.ignored

    def placement_rows(self):
        page = (hygiene.FIXTURE / 'docs/wiki/maintenance-closeout.md').read_text(encoding='utf-8')
        section = page.split('### File placement', 1)[1].split('\n### ', 1)[0]
        return {cells[0]: cells[1:] for line in section.splitlines() if line.startswith('| ')
                for cells in [[cell.strip() for cell in line.strip('|').split('|')]]}

    def path_for(self, purpose):
        cells = self.placement_rows()[purpose]
        self.assertTrue(cells[1] and cells[2])  # owner and retention/rule source
        return re.findall(r'`([^`]+)`', cells[0])[0]

    def query(self, skill, question):
        p = subprocess.run([sys.executable, str(skill / 'scripts/wiki.py'), 'query',
                            '--root', str(hygiene.FIXTURE), '--json', question],
                           capture_output=True, env={**self.env, 'PYTHONUTF8': '1'}, check=True)
        return json.loads(p.stdout)['matches']

    def test_default_menu_and_native_queries_reach_same_placement_owner(self):
        package = self.root.parent / 'package'
        package_tests.builder.build(package)
        skill = package / 'skills/project-wiki'
        entry = (skill / 'SKILL.md').read_text(encoding='utf-8')
        menu = entry.split('## Choose the work', 1)[1].split('\n## ', 1)[0]
        self.assertIn('**Place a file:**', menu)
        self.assertIn('Maintenance', menu)
        self.assertIn('File placement', menu)
        self.assertIn('references/repository-hygiene.md#file-placement', menu)
        native = (hygiene.FIXTURE / 'docs/wiki/engineering-entry.md').read_text(encoding='utf-8')
        self.assertIn('(maintenance-closeout.md#file-placement)', native)
        for question in ('Where should I write this generated output?',
                         'Where is personal scratch stored?', '新文件放哪里？',
                         '生成报告放哪里？', '仅本地文件放哪里？',
                         '生成的报告和个人临时文件应该放在哪里？',
                         '临时写一份无敏感内容的个人笔记，应该放在哪里？',
                         '新生成的公开报告可以重新生成，应该保存到什么位置？'):
            route = self.query(skill, question)[0]
            self.assertEqual(route['id'], 'repository-hygiene')
            self.assertIn('docs/wiki/maintenance-closeout.md#file-placement', route['docs'])
        self.assertIn('Shared generated report', self.placement_rows())
        manifest = json.loads((package / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertNotIn('hooks', manifest)

    def test_named_report_team_rule_personal_scope_and_required_inputs(self):
        report = self.path_for('Shared generated report')
        personal = self.path_for('Harmless personal scratch')
        # Arrange this project's approved locations/rules before the write request.
        # Only disposable Git fixtures are configured; no consumer ignore is edited.
        self.write('.gitignore', '/' + report + '\n')
        raw = self.documented('rev-parse --git-path info/exclude').stdout.decode().strip()
        exclude = Path(raw)
        exclude = exclude if exclude.is_absolute() else self.root / exclude
        exclude.write_text('/' + personal + '\n', encoding='utf-8')
        self.write(report, 'synthetic reproducible report\n')
        self.write(personal, 'synthetic harmless note\n')
        self.assertIn('.gitignore:1:', self.ignored(report))
        self.assertIn('info/exclude:1:', self.ignored(personal).replace('\\', '/'))
        self.assertEqual(self.documented('status', report).stdout, ('!! ' + report + '\n').encode())
        # A guessed root-level output is not the owner-selected destination.
        self.assertNotEqual(report, Path(report).name)
        self.assertEqual(self.ignored(Path(report).name, codes=(1,)), '')
        for path in ('.env.example', 'package-lock.json', 'tests/fixtures/public.json'):
            self.write(path, 'public synthetic input\n')
            self.assertEqual(self.ignored(path, codes=(1,)), '')
            self.assertTrue(self.documented('status', path).stdout.startswith(b'??'))
            self.git('add', '--', path)  # Test setup proves trackability, without force.
            self.documented('ls-files', path)
        self.assertIn('linked worktrees share', self.method)
        self.assertIn('not necessarily isolated to one worktree', self.method)

    def test_sensitive_or_unapproved_location_is_not_granted_by_ignore_or_visibility(self):
        row = self.placement_rows()['Customer export / private durable data']
        self.assertEqual(re.findall(r'`([^`]+)`', row[0]), [])
        self.assertIn('No approved in-clone home', row[0])
        # Ignore can match even a nonexistent candidate: it grants no storage authority.
        self.write('.gitignore', '/customer-export.csv\n')
        before = self.git('ls-files', '-z').stdout
        for visibility in ('public', 'private', 'internal', 'unknown'):
            with self.subTest(visibility=visibility):
                self.assertIn(visibility, row[2])
                self.ignored('customer-export.csv')
                self.assertFalse((self.root / 'customer-export.csv').exists())
        self.assertEqual(self.git('ls-files', '-z').stdout, before)
        self.assertIn('unapproved location blocks the write', self.method)

    def test_ordinary_text_edit_has_no_extra_route_or_material(self):
        entry = (hygiene.SKILL / 'SKILL.md').read_text(encoding='utf-8')
        self.assertLess(entry.index('## Keep the entry proportional'), entry.index('## Choose the work'))
        for question in ('Fix punctuation in a known README sentence',
                         'Correct a spelling mistake in an existing comment',
                         'Fix a typo in an existing file',
                         '修改现有注释中的错字', '修正 README 的标点'):
            self.assertEqual(self.query(hygiene.SKILL, question), [])
        self.assertIn('Do not add a specialist read or record', entry)
        self.assertIn("project's mandatory gates", entry)
