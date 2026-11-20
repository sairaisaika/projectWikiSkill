"""Exercise the authored workflow on synthetic real Git repos, not real secrets.

There is no filename classifier: disposition is a documented agent decision.
These tests guard discovery and the Git command semantics behind that decision.
"""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'project-wiki'
METHOD = SKILL / 'references/repository-hygiene.md'
FIXTURE = ROOT / 'evals/fixture-project'


class RepositoryHygieneTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / 'repo'
        self.root.mkdir()
        self.method = METHOD.read_text(encoding='utf-8')
        prefix = re.search(r'```sh\n(git --no-pager[^\n]+)\n```', self.method)
        self.assertIsNotNone(prefix)
        self.prefix = shlex.split(prefix.group(1))
        # Isolate global/system Git state; never read or alter the user's config.
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        self.env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')
        self.git('init')
        self.git('config', 'user.name', 'Synthetic Test')
        self.git('config', 'user.email', 'synthetic@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.write('tracked-output.txt', 'public baseline\n')
        self.git('add', '--', 'tracked-output.txt')
        self.git('-c', 'commit.gpgsign=false', 'commit', '-m', 'Synthetic baseline')

    def git(self, *args, codes=(0,)):
        result = subprocess.run([*self.prefix, *args], cwd=self.root,
                                env=self.env, capture_output=True)
        self.assertIn(result.returncode, codes, result.stderr.decode('utf-8', errors='replace'))
        return result

    def documented(self, start, path=None, codes=(0,)):
        # Execute the actual documented argv, not independently copied commands.
        line = next(line for line in self.method.splitlines() if line.replace('--literal-pathspecs ', '').startswith('git ' + start))
        args = shlex.split(line)[1:]
        args = [path if arg == 'path/to/file' else arg for arg in args]
        return self.git(*args, codes=codes)

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')

    def ignored(self, path, no_index=False, codes=(0,)):
        start = 'check-ignore -v --no-index' if no_index else 'check-ignore -v -- '
        return self.documented(start, path, codes).stdout.decode('utf-8')

    def query(self, root, question):
        result = subprocess.run([sys.executable, str(SKILL / 'scripts/wiki.py'),
                                 'query', '--root', str(root), '--json', question],
                                env={**self.env, 'PYTHONUTF8': '1'}, capture_output=True, check=True)
        return json.loads(result.stdout)['matches'][0]

    def test_entry_query_and_staged_diff_route_reach_one_procedure(self):
        self.assertIn('references/repository-hygiene.md', (SKILL / 'SKILL.md').read_text(encoding='utf-8'))
        entry = (FIXTURE / 'docs/wiki/engineering-entry.md').read_text(encoding='utf-8')
        self.assertIn('maintenance-closeout.md#repository-hygiene', entry)
        for root in (ROOT, FIXTURE):
            for question in ('repository hygiene', 'staged diff', '仓库卫生'):
                with self.subTest(root=root, question=question):
                    route = self.query(root, question)
                    self.assertEqual(route['id'], 'repository-hygiene')
                    self.assertEqual(route['evidence']['implementation'], 'planned')
        page = FIXTURE / 'docs/wiki/maintenance-closeout.md'
        link = re.search(r'\[repository hygiene procedure\]\(([^)]+)\)', page.read_text(encoding='utf-8'))
        self.assertEqual((page.parent / link.group(1)).resolve(), METHOD)

    def test_shared_and_repository_local_noise_have_different_rule_provenance(self):
        self.write('.gitignore', '/build/cache.bin\n')
        self.write('build/cache.bin', 'regenerable public bytes')
        self.write('scratch/local-note.txt', 'synthetic personal noise')
        exclude = Path(self.documented('rev-parse --git-path info/exclude').stdout.decode().strip())
        if not exclude.is_absolute():
            exclude = self.root / exclude
        exclude.write_text('/scratch/local-note.txt\n', encoding='utf-8')
        self.assertIn('.gitignore:1:/build/cache.bin', self.ignored('build/cache.bin'))
        self.assertIn('info/exclude:1:/scratch/local-note.txt', self.ignored('scratch/local-note.txt').replace('\\', '/'))
        self.documented('ls-files', 'build/cache.bin', codes=(1,))
        self.assertEqual(self.documented('status', 'build/cache.bin').stdout, b'!! build/cache.bin\n')
        # Config-source discovery is read-only; no global preference is invented.
        self.documented('config --show-origin', codes=(1,))

    def test_linked_worktrees_share_repository_local_exclude_in_both_directions(self):
        linked = self.root.parent / 'linked'
        self.git('worktree', 'add', '--detach', str(linked), 'HEAD')
        self.assertTrue((linked / '.git').is_file())
        paths = []
        for root in (self.root, linked):
            raw = self.git('-C', str(root), 'rev-parse', '--git-path', 'info/exclude').stdout
            path = Path(raw.decode('utf-8').strip())
            paths.append((path if path.is_absolute() else root / path).resolve())
            (root / 'personal-note.txt').write_text('synthetic public note\n', encoding='utf-8')
            (root / 'second-note.txt').write_text('synthetic public note\n', encoding='utf-8')
        self.assertEqual(paths[0], paths[1])
        # These writes only arrange synthetic state; the method proposes rules.
        paths[0].write_text('/personal-note.txt\n', encoding='utf-8')
        for root in (self.root, linked):
            result = self.git('-C', str(root), 'check-ignore', '-v', '--', 'personal-note.txt')
            self.assertIn(b'/personal-note.txt', result.stdout)
        with paths[1].open('a', encoding='utf-8') as stream:
            stream.write('/second-note.txt\n')
        for root in (self.root, linked):
            for name in ('personal-note.txt', 'second-note.txt'):
                result = self.git('-C', str(root), 'status', '--porcelain=v1',
                                  '--untracked-files=all', '--ignored', '--', name)
                self.assertEqual(result.stdout, ('!! ' + name + '\n').encode())
                self.git('-C', str(root), 'ls-files', '--error-unmatch', '--', name, codes=(1,))
        self.assertIn('linked worktrees share this file', self.method)
        self.assertIn('do not rely on this shared exclude', self.method)

    def test_child_negation_requires_traversable_ancestor_directories(self):
        self.write('.gitignore', '/tests/\n!tests/fixtures/public.json\n')
        for path in ('tests/fixtures/public.json', 'tests/fixtures/other.json', 'tests/other.txt'):
            self.write(path, 'synthetic public input\n')
        match = self.ignored('tests/fixtures/public.json')
        self.assertIn('.gitignore:1:/tests/', match)
        self.assertTrue(self.documented('status', 'tests/fixtures/public.json').stdout.startswith(b'!!'))
        rules = re.search(r'```gitignore\n([^`]+)```', self.method)
        self.assertIsNotNone(rules)
        self.write('.gitignore', rules.group(1))
        self.assertIn('!/tests/fixtures/public.json', self.ignored('tests/fixtures/public.json'))
        self.assertTrue(self.documented('status', 'tests/fixtures/public.json').stdout.startswith(b'??'))
        for path in ('tests/fixtures/other.json', 'tests/other.txt'):
            self.assertTrue(self.documented('status', path).stdout.startswith(b'!!'))

    def test_required_lockfile_example_fixture_expose_overbroad_rules(self):
        self.write('.gitignore', '*.json\n.env.*\n!tests/fixtures/public.json\n')
        for path in ('package-lock.json', '.env.example', 'tests/fixtures/public.json'):
            self.write(path, 'public synthetic input\n')
        for path in ('package-lock.json', '.env.example'):
            with self.subTest(path=path):
                self.assertIn('.gitignore:', self.ignored(path))
                self.assertTrue(self.documented('status', path).stdout.startswith(b'!!'))
                self.documented('ls-files', path, codes=(1,))
        # Verbose check-ignore reports the negation with success too: not excluded.
        self.assertIn('!tests/fixtures/public.json', self.ignored('tests/fixtures/public.json'))
        self.assertTrue(self.documented('status', 'tests/fixtures/public.json').stdout.startswith(b'??'))
        self.assertIn('required lockfiles', self.method)
        self.assertIn('do not silently accept', self.method)

    def test_tracked_ignored_conflict_does_not_untrack_or_rewrite_history(self):
        self.write('.gitignore', '/tracked-output.txt\n')
        before = self.git('rev-parse', 'HEAD').stdout
        index = (self.root / '.git/index').read_bytes()
        self.documented('ls-files', 'tracked-output.txt')
        self.assertEqual(self.ignored('tracked-output.txt', codes=(1,)), '')
        self.assertIn('/tracked-output.txt', self.ignored('tracked-output.txt', no_index=True))
        self.assertEqual(self.documented('log', 'tracked-output.txt').stdout, before)
        self.assertEqual(self.documented('status', 'tracked-output.txt').stdout, b'')
        self.assertEqual((self.root / '.git/index').read_bytes(), index)
        self.assertEqual(self.git('rev-parse', 'HEAD').stdout, before)

    def test_staged_review_reads_index_and_rechecks_late_arrivals_without_drivers(self):
        self.write('review-driver.py', 'from pathlib import Path\nPath("driver-ran").touch()\n')
        command = [sys.executable, 'review-driver.py']
        command = subprocess.list2cmdline(command) if os.name == 'nt' else shlex.join(command)
        self.git('config', 'diff.external', command)
        self.git('config', 'diff.review.textconv', command)
        self.git('config', 'core.fsmonitor', command)
        self.write('.gitattributes', 'tracked-output.txt diff=review\n')
        self.write('tracked-output.txt', 'public staged version\n')
        self.git('add', '--', 'tracked-output.txt')  # Synthetic setup, not workflow authorization.
        self.write('tracked-output.txt', 'public unstaged version\n')
        index = (self.root / '.git/index').read_bytes()
        first = self.documented('diff --cached --no-ext-diff --no-textconv --name-status').stdout
        self.assertEqual(first.split(b'\0')[:-1], [b'M', b'tracked-output.txt'])
        patch = self.documented('diff --cached --no-ext-diff --no-textconv -- ', 'tracked-output.txt').stdout
        self.assertIn(b'+public staged version', patch)
        self.assertNotIn(b'public unstaged version', patch)
        self.assertEqual((self.root / '.git/index').read_bytes(), index)
        self.assertFalse((self.root / 'driver-ran').exists())
        self.write('late output.txt', 'public late arrival\n')
        self.git('add', '--', 'late output.txt')
        second = self.documented('diff --cached --no-ext-diff --no-textconv --name-status').stdout
        self.assertNotEqual(first, second)
        self.assertIn(b'late output.txt', second.split(b'\0'))
        self.assertEqual(self.query(FIXTURE, 'staged diff')['id'], 'repository-hygiene')

    def test_staged_name_status_preserves_both_rename_paths(self):
        self.write('old name.txt', 'public rename input\n')
        self.git('add', '--', 'old name.txt')
        self.git('-c', 'commit.gpgsign=false', 'commit', '-m', 'Synthetic rename baseline')
        self.git('mv', '--', 'old name.txt', 'new name.txt')
        self.git('config', 'diff.renames', 'true')
        fields = self.documented('diff --cached --no-ext-diff --no-textconv --name-status').stdout.split(b'\0')[:-1]
        self.assertEqual(fields, [b'R100', b'old name.txt', b'new name.txt'])

    def test_literal_path_does_not_expand_wildcards(self):
        self.write('safe-one.txt', 'public\n')
        # Portable even on Windows where '*' cannot be a real filename.
        self.assertEqual(self.documented('status', 'safe-*.txt').stdout, b'')
        self.assertIn(b'safe-one.txt', self.documented('status', 'safe-one.txt').stdout)

    def test_new_and_existing_wiki_steps_preserve_one_canonical_home(self):
        template = self.method.split('> **Repository boundary:**', 1)[1].split('\n\n', 1)[0]
        self.assertIn('Machine absolute paths', template)
        self.assertIn('approved', template)
        self.assertIn('before staging and again before commit', template)
        self.write('docs/wiki/entry.md', '# Engineering entry\n\n## Maintenance\n\n> **Repository boundary:**' + template + '\n')
        self.documented('ls-files', 'docs/wiki/entry.md', codes=(1,))
        self.assertTrue(self.documented('status', 'docs/wiki/entry.md').stdout.startswith(b'??'))
        self.git('add', '--', 'docs/wiki/entry.md')
        # Existing Wiki: append missing index in the same owner, retaining authored text.
        page = self.root / 'docs/wiki/entry.md'
        original = page.read_text(encoding='utf-8')
        page.write_text(original + '\nConfiguration index: `.gitignore` missing; remote gates unverified.\n', encoding='utf-8')
        self.assertTrue(page.read_text(encoding='utf-8').startswith(original))
        self.assertEqual(list((self.root / 'docs/wiki').iterdir()), [page])
        self.documented('ls-files', 'docs/wiki/entry.md')
        self.assertIn('existing Wiki', self.method)

    def test_ignored_archive_is_still_protected_by_retention(self):
        self.write('.gitignore', '/archives/held.zip\n')
        self.write('archives/held.zip', 'synthetic sole restore copy; hold\n')
        self.assertIn('/archives/held.zip', self.ignored('archives/held.zip'))
        before = (self.root / 'archives/held.zip').read_bytes()
        result = subprocess.run([sys.executable, str(SKILL / 'scripts/storage_inventory.py'),
                                 '--root', str(self.root / 'archives'), '--exclude', 'held.zip'],
                                capture_output=True, check=True)
        report = json.loads(result.stdout)
        self.assertEqual(report['counts']['excluded'], 1)
        self.assertEqual(report['apparent_bytes'], 0)
        self.assertNotIn('held.zip', result.stdout.decode())
        self.assertEqual((self.root / 'archives/held.zip').read_bytes(), before)
        self.assertIn('Ignore, tracking and retention are independent', self.method)

    def test_new_repo_and_git_errors_remain_unknown_not_no_match(self):
        empty = self.root / 'fresh'
        empty.mkdir()
        result = subprocess.run([*self.prefix, 'init', str(empty)], env=self.env, capture_output=True)
        self.assertEqual(result.returncode, 0)
        result = subprocess.run([*self.prefix, '-C', str(empty), 'rev-parse', '--verify', 'HEAD'],
                                env=self.env, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        result = subprocess.run([*self.prefix, '-C', str(self.root / 'absent'),
                                 'check-ignore', '-v', '--', 'path'], env=self.env, capture_output=True)
        self.assertNotIn(result.returncode, (0, 1))
        self.assertIn('history is unavailable', self.method)
