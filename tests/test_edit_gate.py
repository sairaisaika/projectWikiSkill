"""The pre-edit gate blocks only configured locked paths and never blocks on its own defects."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'project-wiki/scripts/edit_gate.py'


@unittest.skipUnless(shutil.which('git'), 'git is required for the fixture checkout')
class EditGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name).resolve()
        self.repo = self.home / 'checkout'
        self.repo.mkdir()
        # The fixture must never touch the real repository or user Git config:
        # drop inherited GIT_* variables (hooks export GIT_DIR) and point global
        # config at an empty file inside the temporary directory.
        (self.home / 'gitconfig').write_text('', encoding='utf-8')
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        self.env.update({'GIT_CONFIG_GLOBAL': str(self.home / 'gitconfig'), 'GIT_CONFIG_NOSYSTEM': '1',
                         'HOME': str(self.home)})
        self.git('init', '-q', '-b', 'main')
        self.write('src/app.py', 'print(1)\n')
        self.write('docs/wiki/file-map.md', '| `scripts/tool.sh` | [1](01.md) |\n')
        self.write('docs/wiki/index.md', 'generated\n')
        self.write('docs/wiki/01-feature.md', '# Feature\n')
        self.write('scripts/tool.sh', 'echo\n')
        self.write('README.md', 'readme\n')
        self.write('.gitignore', '.project-wiki/\n')
        self.git('add', '.')
        self.git('-c', 'user.name=fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-q', '-m', 'base')
        self.git('update-ref', 'refs/remotes/origin/main', 'HEAD')
        self.config = {'wiki_root': 'docs/wiki', 'locked': ['src/**', 'contracts/**'],
                       'map_file': 'docs/wiki/file-map.md', 'map_row_format': '| `{path}` |',
                       'stamp': {'path': '.project-wiki/stamp.json', 'max_age_hours': 8},
                       'stamp_command': 'python3 tools/route.py "<words>" --files {file}',
                       'design_first': True, 'generated': ['file-map.md', 'index.md'],
                       'base_ref': 'origin/main', 'skip_file': '.project-wiki/design.skip'}

    def git(self, *args):
        cp = subprocess.run(['git', '-C', str(self.repo), *args], capture_output=True, text=True, env=self.env)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        return cp.stdout

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def configure(self, **overrides):
        self.write('.project-wiki/edit-gate.json', json.dumps({**self.config, **overrides}))

    def stamp(self, *files, age_hours=0.0):
        path = self.write('.project-wiki/stamp.json', json.dumps({'at': 'fixture', 'files': list(files)}))
        if age_hours:
            stamp_time = time.time() - age_hours * 3600
            os.utime(path, (stamp_time, stamp_time))

    def run_gate(self, rel='src/app.py', tool='Write', event=None):
        payload = event if event is not None else json.dumps({
            'hook_event_name': 'PreToolUse', 'tool_name': tool, 'cwd': str(self.repo),
            'tool_input': {'file_path': str(self.repo / rel), 'content': 'SECRET-CONTENT-NEVER-ECHOED'}})
        before = self.snapshot()
        cp = subprocess.run([sys.executable, str(ENTRY)], input=payload, text=True, capture_output=True,
                            env=self.env, cwd=str(self.home))
        self.assertEqual(before, self.snapshot(), 'the gate must not write anything')
        self.assertEqual(cp.stdout, '')
        self.assertNotIn('SECRET-CONTENT', cp.stderr)
        return cp.returncode, cp.stderr

    def snapshot(self):
        return {p: p.read_bytes() for p in self.home.rglob('*') if p.is_file()}

    def test_without_config_every_edit_passes_silently(self):
        self.assertEqual(self.run_gate(), (0, ''))

    def test_unlocked_paths_and_other_events_pass_without_predicates(self):
        self.configure()
        self.assertEqual(self.run_gate('README.md'), (0, ''))
        self.assertEqual(self.run_gate('docs/wiki/01-feature.md'), (0, ''))
        self.assertEqual(self.run_gate(tool='Read'), (0, ''))
        other = json.dumps({'hook_event_name': 'PostToolUse', 'tool_name': 'Write',
                            'tool_input': {'file_path': str(self.repo / 'src/app.py')}})
        self.assertEqual(self.run_gate(event=other), (0, ''))

    def test_missing_stamp_blocks_and_names_the_unlock_command(self):
        self.configure()
        code, err = self.run_gate()
        self.assertEqual(code, 2)
        self.assertIn('src/app.py is locked', err)
        self.assertIn('context: no stamp at .project-wiki/stamp.json', err)
        self.assertIn('python3 tools/route.py "<words>" --files src/app.py', err)

    def test_stale_stamp_and_stamp_for_another_file_block(self):
        self.configure()
        self.stamp('src/other.py')
        code, err = self.run_gate()
        self.assertEqual(code, 2)
        self.assertIn('does not list src/app.py', err)
        self.stamp('src/app.py', age_hours=9)
        code, err = self.run_gate()
        self.assertEqual(code, 2)
        self.assertIn('old (max 8h)', err)

    def test_stamp_without_wiki_change_blocks_and_points_at_the_page(self):
        self.configure()
        self.stamp('src/app.py')
        code, err = self.run_gate()
        self.assertEqual(code, 2)
        self.assertNotIn('context:', err)
        self.assertIn('design: no handwritten change under docs/wiki since merge-base(HEAD, origin/main)', err)
        self.assertIn('generated excluded: file-map.md, index.md', err)
        self.assertIn('write the design on the owning page under docs/wiki', err)
        self.assertIn('.project-wiki/design.skip', err)

    def test_both_missing_predicates_are_reported_together(self):
        self.configure()
        code, err = self.run_gate()
        self.assertEqual(code, 2)
        self.assertIn('- context:', err)
        self.assertIn('- design:', err)

    def test_generated_view_changes_alone_do_not_count_as_design(self):
        self.configure()
        self.stamp('src/app.py')
        self.write('docs/wiki/file-map.md', '| `scripts/tool.sh` | [1](01.md) |\n| `src/app.py` | [1](01.md) |\n')
        self.write('docs/wiki/index.md', 'regenerated\n')
        code, err = self.run_gate()
        self.assertEqual(code, 2)
        self.assertIn('design: no handwritten change', err)

    def test_handwritten_page_change_passes_whether_uncommitted_untracked_or_committed_on_branch(self):
        self.configure()
        self.stamp('src/app.py')
        self.write('docs/wiki/01-feature.md', '# Feature\n\nDesign: add X.\n')
        self.assertEqual(self.run_gate(), (0, ''))
        self.git('checkout', '-q', '--', 'docs/wiki/01-feature.md')
        self.write('docs/wiki/02-new.md', '# New page\n')
        self.assertEqual(self.run_gate(), (0, ''))
        self.git('add', 'docs/wiki/02-new.md')
        self.git('-c', 'user.name=fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-q', '-m', 'design')
        self.assertEqual(self.run_gate(), (0, ''))
        # A page change already on the base ref is not this branch's design.
        self.git('update-ref', 'refs/remotes/origin/main', 'HEAD')
        code, err = self.run_gate()
        self.assertEqual(code, 2)
        self.assertIn('design: no handwritten change', err)

    def test_design_first_off_needs_only_the_stamp(self):
        self.configure(design_first=False)
        self.stamp('src/app.py')
        self.assertEqual(self.run_gate(), (0, ''))

    def test_map_referenced_file_outside_locked_globs_is_locked_too(self):
        self.configure()
        code, err = self.run_gate('scripts/tool.sh')
        self.assertEqual(code, 2)
        self.assertIn('scripts/tool.sh is locked', err)
        self.assertEqual(self.run_gate('scripts/unlisted.sh'), (0, ''))

    def test_skip_file_with_reason_waives_design_only_and_echoes_it_but_empty_reason_blocks(self):
        self.configure()
        self.stamp('src/app.py')
        self.write('.project-wiki/design.skip', 'pure refactor:\nthe owning page already covers it\n')
        code, err = self.run_gate()
        self.assertEqual(code, 0)
        self.assertIn('design: waived by .project-wiki/design.skip: pure refactor: the owning page already covers it', err)
        self.write('.project-wiki/design.skip', '  \n')
        code, err = self.run_gate()
        self.assertEqual(code, 2)
        self.assertIn('- design: .project-wiki/design.skip exists but holds no reason', err)
        self.assertNotIn('- context:', err)

    def test_skip_file_does_not_waive_the_context_stamp(self):
        self.configure()
        self.write('.project-wiki/design.skip', 'pure refactor\n')
        code, err = self.run_gate()
        self.assertEqual(code, 2)
        self.assertIn('- context: no stamp', err)
        self.assertNotIn('- design:', err)

    def test_broken_config_or_event_passes_with_a_visible_unavailable_notice(self):
        self.write('.project-wiki/edit-gate.json', '{not json')
        code, err = self.run_gate()
        self.assertEqual(code, 0)
        self.assertIn('gate unavailable', err)
        self.write('.project-wiki/edit-gate.json', json.dumps({'locked': ['src/**']}))
        code, err = self.run_gate()
        self.assertEqual(code, 0)
        self.assertIn('gate unavailable', err)
        self.assertIn('wiki_root', err)
        self.configure(locked='src/**')
        code, err = self.run_gate()
        self.assertEqual(code, 0)
        self.assertIn('gate unavailable', err)
        self.configure()
        for raw in ['not-json', '[]', 'x' * (64 * 1024 + 1)]:
            code, err = self.run_gate(event=raw)
            self.assertEqual(code, 0, raw[:20])
            self.assertIn('gate unavailable', err)

    def test_missing_base_ref_leaves_design_unjudged_with_a_visible_note(self):
        self.configure(base_ref='refs/remotes/origin/absent')
        self.stamp('src/app.py')
        code, err = self.run_gate()
        self.assertEqual(code, 0)
        self.assertIn('design: not judged (no merge-base of HEAD and refs/remotes/origin/absent)', err)
        # The context predicate still applies without a base.
        self.stamp('src/other.py')
        code, err = self.run_gate()
        self.assertEqual(code, 2)
        self.assertIn('does not list src/app.py', err)

    def test_inherited_git_dir_does_not_redirect_the_gate(self):
        # Git hooks export GIT_DIR; the gate must still judge the checkout that owns file_path.
        other = self.home / 'other'
        other.mkdir()
        subprocess.run(['git', 'init', '-q', str(other)], env=self.env, check=True, capture_output=True)
        self.configure()
        self.stamp('src/app.py')
        self.write('docs/wiki/01-feature.md', '# Feature\n\nDesign.\n')
        payload = json.dumps({'hook_event_name': 'PreToolUse', 'tool_name': 'Edit',
                              'tool_input': {'file_path': str(self.repo / 'src/app.py')}})
        cp = subprocess.run([sys.executable, str(ENTRY)], input=payload, text=True, capture_output=True,
                            env={**self.env, 'GIT_DIR': str(other / '.git')})
        self.assertEqual((cp.returncode, cp.stderr), (0, ''))

    def test_packaged_hook_command_runs_the_gate_from_the_plugin_root(self):
        config = json.loads((ROOT / 'hooks/claude.json').read_text(encoding='utf-8'))
        groups = config['hooks']['PreToolUse']
        self.assertEqual(groups[0]['matcher'], 'Edit|Write|MultiEdit')
        command = groups[0]['hooks'][0]['command']
        self.assertIn('edit_gate.py', command)
        code = command.split(' -c "', 1)[1][:-1]
        plugin_root = self.home / 'plugin'
        target = plugin_root / 'skills/project-wiki/scripts'
        target.mkdir(parents=True)
        shutil.copyfile(ENTRY, target / 'edit_gate.py')
        self.configure()
        event = json.dumps({'hook_event_name': 'PreToolUse', 'tool_name': 'Edit',
                            'tool_input': {'file_path': str(self.repo / 'src/app.py')}})
        cp = subprocess.run([sys.executable, '-c', code], input=event, text=True, capture_output=True,
                            env={**self.env, 'CLAUDE_PLUGIN_ROOT': str(plugin_root)})
        self.assertEqual(cp.returncode, 2, cp.stderr)
        self.assertIn('src/app.py is locked', cp.stderr)


if __name__ == '__main__':
    unittest.main()
