"""Opt-in review receipts on the public offline fixture, using real temporary Git."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('review_wiki', REPO / 'project-wiki/scripts/wiki.py')
wiki = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wiki)


class SectionReviewTests(unittest.TestCase):
    def setUp(self):
        try:
            capability = subprocess.run(['git', '--no-lazy-fetch', '--version'], capture_output=True, timeout=15)
        except (OSError, subprocess.TimeoutExpired):
            self.skipTest('Opt-in tests require Git 2.45+ with --no-lazy-fetch support')
        if capability.returncode:
            self.skipTest('Opt-in tests require Git 2.45+ with --no-lazy-fetch support')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = (Path(self.temp.name) / 'fixture').resolve()
        shutil.copytree(REPO / 'evals/fixture-project', self.root, ignore=shutil.ignore_patterns('__pycache__'))
        self.manifest = wiki.load(self.root)
        self.row = self.manifest['routes'][0]
        self.rule = self.row['rules'][0]
        self.rule['review'] = {'section': 'docs/wiki/interfaces.md#public-api'}
        self.save()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Synthetic reviewer')
        self.git('config', 'user.email', 'review@example.invalid')
        self.commit()
        self.initial = self.git('rev-parse', 'HEAD').strip()
        self.assertEqual(self.call('review', 'public-api', 'failure-not-empty', '--revision', self.initial,
                                   '--repository-url', 'https://example.invalid/public-fixture')[0], 0)
        self.reload()
        self.assertEqual(self.call('build')[0], 0)

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], capture_output=True, text=True, check=True).stdout

    def commit(self):
        self.git('add', '--all')
        self.git('commit', '-qm', 'Synthetic fixture revision')

    def call(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = wiki.main([*args, '--root', str(self.root)])
        return code, json.loads(out.getvalue())

    def save(self):
        (self.root / 'docs/wiki/routes.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def reload(self):
        self.manifest = wiki.load(self.root)
        self.row = self.manifest['routes'][0]
        self.rule = self.row['rules'][0]

    def edit(self, path, before, after):
        p = self.root / path
        data = p.read_text(encoding='utf-8')
        self.assertIn(before, data)
        p.write_text(data.replace(before, after), encoding='utf-8')

    def find(self):
        return self.call('find', 'client failures', '--json')

    def test_reviewed_locators_and_non_mutating_reads(self):
        before = (self.root / 'docs/wiki/routes.json').read_bytes()
        code, result = self.find()
        self.assertEqual(code, 0)
        receipt = result['section_reviews']['rules'][0]
        self.assertEqual(receipt['status'], 'reviewed')
        self.assertEqual(receipt['reviewed_revision'], self.initial)
        self.assertTrue(all('#L' in x['locator'] for x in receipt['current']))
        self.assertTrue(all('/blob/' + self.initial + '/' in x['url'] for x in receipt['reviewed']))
        self.assertEqual(self.call('check', '--reviews')[0], 0)
        self.assertEqual(before, (self.root / 'docs/wiki/routes.json').read_bytes())
        rendered = wiki.find_text(result)
        self.assertIn('live: [src/service.py:', rendered)
        self.assertIn('/blob/' + self.initial + '/', rendered)

    def test_same_count_behavior_drift_survives_rebuild_and_requires_review(self):
        baseline = self.rule['review']['baseline']
        self.edit('src/service.py', "{'ok': False, 'error': 'unavailable'}", "{'ok': True, 'data': []}")
        self.assertEqual(self.find()[1]['reason'], 'needs_review')
        actual = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_contracts.py'], cwd=self.root, capture_output=True)
        self.assertNotEqual(actual.returncode, 0, 'The real fixture contract must fail on this mutation')
        self.assertEqual(self.call('build')[0], 0)
        self.assertEqual(self.find()[1]['reason'], 'needs_review')
        self.assertEqual(self.call('check')[0], 0)  # Default structure-only contract remains compatible.
        self.assertEqual(self.call('check', '--reviews')[0], 1)
        self.assertEqual(wiki.load(self.root)['routes'][0]['rules'][0]['review']['baseline'], baseline)
        self.assertEqual(self.call('review', 'public-api', 'failure-not-empty', '--revision', self.initial)[0], 1)
        # Recording review attests a human's check; it never rewrites behavior/rules or runs tests.
        self.commit()
        revision = self.git('rev-parse', 'HEAD').strip()
        self.assertEqual(self.call('review', 'public-api', 'failure-not-empty', '--revision', revision)[0], 0)
        self.call('build')
        self.assertEqual(self.call('check', '--reviews')[0], 0)
        self.assertEqual(self.find()[0], 0)
        self.assertIn("{'ok': True, 'data': []}", (self.root / 'src/service.py').read_text())

    def test_authored_prose_change_without_source_change(self):
        self.edit('docs/wiki/interfaces.md', '`None` from the source means unavailable', '`None` from the source means success')
        self.assertEqual(self.find()[1]['reason'], 'needs_review')
        self.call('build')
        self.assertEqual(self.call('check', '--reviews')[0], 1)
        self.assertIn('section changed', self.find()[1]['section_reviews']['rules'][0]['reasons'])

    def test_test_only_change_and_newline_policy(self):
        p = self.root / 'tests/test_contracts.py'
        p.write_bytes(p.read_bytes().replace(b'\n', b'\r\n'))
        self.assertEqual(self.call('check', '--reviews')[0], 0)
        p.write_text(p.read_text() + '\n# Changed test expectation under review.\n')
        self.call('build')
        self.assertEqual(self.call('check', '--reviews')[0], 1)
        self.assertIn('test:tests/test_contracts.py changed', self.find()[1]['section_reviews']['rules'][0]['reasons'])

    def test_adjacent_prose_and_unselected_source_body_do_not_flag(self):
        self.edit('docs/wiki/interfaces.md', 'counts is optional.', 'counts remains an optional capability.')
        p = self.root / 'src/service.py'
        p.write_text(p.read_text() + '\ndef unrelated():\n    return 7\n')
        self.call('build')
        self.assertEqual(self.call('check', '--reviews')[0], 0)
        self.assertEqual(self.find()[0], 0)

    def test_pure_symbol_move_updates_live_locator_preserves_reviewed_link(self):
        baseline = self.rule['review']['baseline']
        p = self.root / 'src/service.py'
        old = p.read_text()
        (self.root / 'src/moved.py').write_text('# Position moved.\n\n' + old)
        p.unlink()
        # No scanner guesses a new owner: update declared route paths, preserving source IDs.
        for row in self.manifest['routes']:
            for source in row.get('sources', []):
                if source['path'] == 'src/service.py':
                    source['path'] = 'src/moved.py'
            for observation in row.get('evidence', {}).get('observations', []):
                if observation['reference'] == 'src/service.py':
                    observation['reference'] = 'src/moved.py'
        self.save()
        self.assertEqual(self.call('build')[0], 0)
        code, result = self.find()
        self.assertEqual(code, 0, result)
        review = result['section_reviews']['rules'][0]
        now = next(t for t in review['current'] if t['key'] == 'source:service')
        prior = next(t for t in review['reviewed'] if t['key'] == 'source:service')
        self.assertEqual(now['path'], 'src/moved.py')
        self.assertEqual(now['line'], prior['line'] + 2)
        self.assertIn('src/service.py#L', prior['url'])
        self.assertEqual(self.call('check', '--reviews')[0], 0)
        self.assertEqual(self.rule['review']['baseline'], baseline)

    def test_missing_or_ambiguous_source_fails_closed(self):
        p = self.root / 'src/service.py'
        original = p.read_text()
        for candidate in ['', original + '\ndef get_articles(source, query):\n    return None\n']:
            p.write_text(candidate)
            self.assertEqual(self.find()[1]['reason'], 'needs_review')
            self.assertEqual(self.call('check', '--reviews')[0], 1)

    def test_missing_and_duplicate_section_fail_closed(self):
        p = self.root / 'docs/wiki/interfaces.md';original = p.read_text()
        for data in [original.replace('id="public-api"', 'id="renamed"'), original + '\n<a id="public-api"></a>\n## Duplicate\nOther text.\n']:
            p.write_text(data)
            self.assertEqual(self.find()[1]['reason'], 'needs_review')
            self.assertEqual(self.call('check', '--reviews')[0], 1)

    def test_missing_review_commit_and_corrupt_receipt_fail_closed(self):
        baseline = copy.deepcopy(self.rule['review']['baseline'])
        for key, value in [('revision', '0' * 40), ('targets', []), ('targets', [{'key': 'section'}])]:
            with self.subTest(key=key, value=value):
                self.rule['review']['baseline'] = copy.deepcopy(baseline)
                self.rule['review']['baseline'][key] = value;self.save()
                self.assertEqual(self.find()[1]['reason'], 'needs_review')
                self.assertEqual(self.call('check', '--reviews')[0], 1)

    def test_explicit_review_requires_committed_selected_prose_and_rule(self):
        before = (self.root / 'docs/wiki/routes.json').read_bytes()
        self.edit('docs/wiki/interfaces.md', 'Inputs are the injected source', 'Inputs include the injected source')
        self.assertEqual(self.call('review', 'public-api', 'failure-not-empty', '--revision', self.initial)[0], 1)
        self.assertEqual(before, (self.root / 'docs/wiki/routes.json').read_bytes())
        self.rule['statement'] += ' A changed rule.';self.save()
        self.assertEqual(self.call('review', 'public-api', 'failure-not-empty', '--revision', self.initial)[0], 1)

    def test_selected_config_needle_is_whole_file_evidence(self):
        (self.root / 'config.json').write_text('{"mode": "safe", "limit": 2}\n')
        self.row['sources'].append({'id': 'config', 'path': 'config.json', 'needle': '"mode"',
                                    'role': 'contract', 'reason': 'Synthetic configuration evidence'})
        self.rule['source_ids'].append('config');self.save();self.commit()
        revision = self.git('rev-parse', 'HEAD').strip()
        self.assertEqual(self.call('review', 'public-api', 'failure-not-empty', '--revision', revision)[0], 0)
        self.call('build')
        self.assertEqual(self.find()[0], 0)
        self.edit('config.json', '"limit": 2', '"limit": 3')
        self.call('build')
        self.assertEqual(self.find()[1]['reason'], 'needs_review')
        self.assertEqual(self.call('status')[1]['closed_reason'], 'needs_review')

    def test_changed_selection_and_tampered_fingerprint_are_not_fresh(self):
        baseline = copy.deepcopy(self.rule['review']['baseline'])
        self.rule['review']['baseline']['targets'][0]['sha256'] = '0' * 64
        self.save();self.call('build')
        self.assertEqual(self.find()[1]['reason'], 'needs_review')
        self.rule['review']['baseline'] = copy.deepcopy(baseline)
        self.rule['review']['baseline']['targets'][0]['line'] = True
        self.save();self.call('build')
        self.assertEqual(self.find()[1]['reason'], 'needs_review')
        self.rule['review']['baseline'] = baseline
        self.rule['tests'].append('tests/test_diagnostic_evidence.py');self.save();self.call('build')
        self.assertEqual(self.find()[1]['reason'], 'needs_review')
        self.assertEqual(self.call('review', 'public-api', 'failure-not-empty', '--revision', self.initial)[0], 1)

    def test_no_opt_in_retains_existing_find_and_check_without_git(self):
        del self.rule['review'];self.save()
        (self.root / '.git').rename(self.root.parent / 'saved-git')
        self.assertEqual(self.call('build')[0], 0)
        self.assertEqual(self.find()[0], 0)
        self.assertNotIn('section_reviews', self.find()[1])
        self.assertEqual(self.call('check')[0], 0)
        self.assertEqual(self.call('check', '--reviews')[0], 0)

    def test_opt_in_executes_only_fixed_read_only_git_queries(self):
        with mock.patch.object(wiki.subprocess, 'run', wraps=subprocess.run) as run:
            self.assertEqual(self.find()[0], 0)
            self.assertEqual(self.call('check', '--reviews')[0], 0)
            self.assertEqual(self.call('review', 'public-api', 'failure-not-empty', '--revision', self.initial)[0], 0)
        self.assertTrue(run.call_args_list)
        for call in run.call_args_list:
            argv = call.args[0]
            self.assertEqual(argv[:6], ['git', '--no-optional-locks', '--no-replace-objects', '--no-lazy-fetch', '-C', str(self.root)])
            self.assertIn(argv[6], ['show', 'rev-parse'])
            self.assertFalse(call.kwargs.get('shell', False))

    def test_review_requires_committed_opt_in_and_exact_section(self):
        self.rule['review']['section'] = 'docs/wiki/interfaces.md#diagnostic-evidence'
        self.save()
        before = (self.root / 'docs/wiki/routes.json').read_bytes()
        self.assertEqual(self.call('review', 'public-api', 'failure-not-empty', '--revision', self.initial)[0], 1)
        self.assertEqual(before, (self.root / 'docs/wiki/routes.json').read_bytes())
        del self.rule['review'];self.save();self.commit()
        no_opt_in = self.git('rev-parse', 'HEAD').strip()
        self.rule['review'] = {'section': 'docs/wiki/interfaces.md#public-api'};self.save()
        before = (self.root / 'docs/wiki/routes.json').read_bytes()
        self.assertEqual(self.call('review', 'public-api', 'failure-not-empty', '--revision', no_opt_in)[0], 1)
        self.assertEqual(before, (self.root / 'docs/wiki/routes.json').read_bytes())

    def test_unreviewed_opt_in_does_not_claim_fresh(self):
        del self.rule['review']['baseline'];self.save();self.call('build')
        self.assertEqual(self.find()[1]['reason'], 'needs_review')
        self.assertEqual(self.call('check', '--reviews')[0], 1)


class NonOptInSectionReviewTests(unittest.TestCase):
    """No Git executable or capability probe is needed for the default path."""
    call = SectionReviewTests.call
    save = SectionReviewTests.save
    find = SectionReviewTests.find

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = (Path(self.temp.name) / 'fixture').resolve()
        shutil.copytree(REPO / 'evals/fixture-project', self.root, ignore=shutil.ignore_patterns('__pycache__'))
        self.manifest = wiki.load(self.root)
        self.row = self.manifest['routes'][0]

    def test_fresh_non_git_fixture_needs_no_git_capability(self):
        self.assertFalse((self.root / '.git').exists())
        with mock.patch.object(wiki.subprocess, 'run', side_effect=AssertionError('No opt-in, no subprocess')):
            self.assertEqual(self.call('build')[0], 0)
            self.assertEqual(self.find()[0], 0)
            self.assertNotIn('section_reviews', self.find()[1])
            self.assertEqual(self.call('check')[0], 0)
            self.assertEqual(self.call('check', '--reviews')[0], 0)

    def test_malformed_non_opted_in_rules_keep_invalid_wiki_result(self):
        for rules in [None, [None], ['review']]:
            self.row['rules'] = rules;self.save()
            result = self.find()
            self.assertEqual(result[0], 1)
            self.assertEqual(result[1]['reason'], 'invalid_wiki')


if __name__ == '__main__':
    unittest.main()
