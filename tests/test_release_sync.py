"""Offline release state machine and read-only package checks; never publishes."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import release_plugin as release
import pws_sync as sync


class ReleaseSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.source = self.home / 'source'
        self.source.mkdir()
        for name in ('project-wiki', 'scripts', '.claude-plugin'):
            shutil.copytree(ROOT / name, self.source / name,
                            ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache'))
        for name in ('plugin.json', 'LICENSE'):
            shutil.copyfile(ROOT / name, self.source / name)
        # Fix the synthetic baseline independently of future real release versions.
        for name in ('plugin.json', '.claude-plugin/marketplace.json'):
            path = self.source / name
            data = json.loads(path.read_text())
            (data['plugins'][0] if 'plugins' in data else data)['version'] = '0.2.39'
            path.write_text(json.dumps(data))
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Synthetic', '-c', 'user.email=fixture@users.noreply.github.com',
                 'commit', '-qm', 'synthetic base')
        self.base = self.git('rev-parse', 'HEAD')

    def git(self, *args):
        return release.git(self.source, *args)

    def commit(self):
        self.git('add', '.')
        self.git('-c', 'user.name=Synthetic', '-c', 'user.email=fixture@users.noreply.github.com',
                 'commit', '-qm', 'synthetic change')
        return self.git('rev-parse', 'HEAD')

    def bundle(self):
        output = self.home / 'bundle'
        receipt = release.bundle(self.source, output, self.base)
        pin = sync.sha256((output / 'release-receipt.json').read_bytes())
        return output, receipt, pin

    def metadata(self, commit):
        env = {'GITHUB_REPOSITORY': sync.REPOSITORY, 'GITHUB_REPOSITORY_ID': str(sync.REPOSITORY_ID),
               'GITHUB_EVENT_NAME': 'push', 'GITHUB_REF': 'refs/heads/main', 'GITHUB_SHA': commit,
               'GITHUB_RUN_ID': '42', 'PWS_RELEASE_ENABLED': 'true'}
        event = {'after': commit, 'before': self.base, 'ref': 'refs/heads/main',
                 'forced': False, 'deleted': False, 'repository': {'id': sync.REPOSITORY_ID}}
        return env, event

    def test_offline_same_different_missing_untrusted_and_no_writes(self):
        output, receipt, pin = self.bundle()
        target = self.home / 'installed'
        shutil.copytree(output / 'package', target)
        before = {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.home.rglob('*') if p.is_file()}
        for candidate in (output, output / 'release-receipt.json'):
            self.assertEqual(sync.check(target, candidate, pin)['status'], 'same')
        self.assertEqual(sync.check(self.home / 'absent', output, pin)['status'], 'not_installed')
        self.assertEqual(sync.check(target, output, None)['status'], 'no_trusted_input')
        self.assertEqual(sync.check(target, output, '0' * 64)['status'], 'invalid_candidate')
        after = {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.home.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        # Same version, different canonical bytes is different, never "up to date".
        (self.source / 'project-wiki/SKILL.md').write_text('Synthetic different skill\n')
        other = self.home / 'other'
        release.builder.build(other, self.source)
        self.assertEqual(sync.check(other, output, pin)['status'], 'different')

    def test_damage_partial_coverage_and_missing_archive_cannot_be_same(self):
        output, receipt, pin = self.bundle()
        target = self.home / 'installed'
        shutil.copytree(output / 'package', target)
        (output / 'package/skills/project-wiki/SKILL.md').unlink()
        self.assertEqual(sync.check(target, output, pin)['status'], 'invalid_candidate')
        shutil.copyfile(target / 'skills/project-wiki/SKILL.md', output / 'package/skills/project-wiki/SKILL.md')
        (output / 'package.zip').unlink()
        self.assertEqual(sync.check(target, output, pin)['status'], 'invalid_candidate')
        receipt['package_receipt']['files'].pop('skills/project-wiki/SKILL.md')
        path = output / 'release-receipt.json'
        path.write_bytes(release.builder.json_bytes(receipt))
        # Even an explicitly pinned incomplete receipt cannot equal a valid target.
        self.assertNotEqual(sync.check(target, path, sync.sha256(path.read_bytes()))['status'], 'same')
        (target / 'LICENSE').unlink()
        self.assertEqual(sync.check(target, path, sync.sha256(path.read_bytes()))['status'], 'invalid_target')

    def test_candidate_python_is_never_executed_and_cli_does_not_write_cache(self):
        marker = self.home / 'must-not-exist'
        (self.source / 'project-wiki/scripts/wiki.py').write_text('raise RuntimeError("never execute candidate")\n')
        self.base = self.commit()
        output, receipt, pin = self.bundle()
        code = subprocess.run([sys.executable, str(ROOT / 'scripts/pws-sync'), '--check',
                               '--target', str(output / 'package'), '--candidate', str(output),
                               '--trusted-receipt-sha256', pin], capture_output=True, text=True)
        self.assertEqual(code.returncode, 0, code.stdout + code.stderr)
        self.assertEqual(json.loads(code.stdout)['status'], 'same')
        self.assertFalse(marker.exists())
        self.assertFalse(list(output.rglob('__pycache__')))

    def test_bundle_is_reproducible_no_hooks_and_new_only(self):
        output, receipt, pin = self.bundle()
        other = self.home / 'second'
        self.assertEqual(release.bundle(self.source, other, self.base), receipt)
        self.assertEqual((other / 'package.zip').read_bytes(), (output / 'package.zip').read_bytes())
        self.assertFalse(receipt['package_receipt']['lifecycle_hooks'])
        self.assertNotIn('hooks/claude.json', receipt['package_receipt']['files'])
        with self.assertRaises(ValueError):
            release.bundle(self.source, output, self.base)

    def test_actual_wiki_test_only_inputs_do_not_release_or_bump(self):
        before = release.describe_commit(self.source, self.base)
        (self.source / 'docs').mkdir()
        (self.source / 'docs/wiki.md').write_text('Synthetic maintainer wiki')
        (self.source / 'tests').mkdir()
        (self.source / 'tests/test_example.py').write_text('# synthetic test')
        current = release.describe_commit(self.source, self.commit())
        self.assertEqual(release.decision(current, before, before), 'no_distribution_change')
        self.assertEqual(release.decision(current, None, before), 'bootstrap_required')

    def test_numeric_version_real_changes_and_no_backfill(self):
        previous = {'version': '0.2.9', 'inputs_sha256': 'old'}
        current = {'version': '0.2.10', 'inputs_sha256': 'new'}
        self.assertEqual(release.decision(current, previous, previous), 'release')
        for version in ('0.2.9', '0.2.8', '00.2.10', '0.2.10-rc1'):
            with self.subTest(version=version), self.assertRaises(ValueError):
                release.decision({**current, 'version': version}, previous, previous)
        with self.assertRaisesRegex(ValueError, 'backfill'):
            release.decision(current, previous, current)
        with self.assertRaisesRegex(ValueError, 'Version-only'):
            release.decision({**current, 'inputs_sha256': 'old'}, previous, previous)

    def test_actual_input_change_requires_both_manifest_versions(self):
        old = release.describe_commit(self.source, self.base)
        (self.source / 'project-wiki/SKILL.md').write_text('Synthetic changed distribution')
        current = release.describe_commit(self.source, self.commit())
        with self.assertRaisesRegex(ValueError, 'increasing'):
            release.decision(current, old, old)
        path = self.source / 'plugin.json'
        identity = json.loads(path.read_text())
        identity['version'] = '0.2.40'
        path.write_text(json.dumps(identity))
        with self.assertRaisesRegex(ValueError, 'Marketplace'):
            release.describe_commit(self.source, self.commit())
        path = self.source / '.claude-plugin/marketplace.json'
        catalog = json.loads(path.read_text())
        catalog['plugins'][0]['version'] = identity['version']
        path.write_text(json.dumps(catalog))
        new = release.describe_commit(self.source, self.commit())
        self.assertEqual(release.decision(new, old, old), 'release')

    def test_live_guard_refuses_external_pr_stale_unmerged_and_failed_matrix(self):
        env, event = self.metadata(self.base)
        api = FakeGitHub(self.base)
        self.assertEqual(release.guard(api, self.source, env, event), self.base)
        for update in ({'GITHUB_EVENT_NAME': 'pull_request'}, {'GITHUB_REF': 'refs/heads/feature'},
                       {'GITHUB_REPOSITORY_ID': '1420071963'}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                release.guard(api, self.source, {**env, **update}, event)
        for mutation in ('stale', 'unmerged', 'failed', 'missing', 'workflow', 'private'):
            api.mutation = mutation
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                release.guard(api, self.source, env, event)
        self.assertEqual(api.writes, [])

    def test_no_release_record_and_complete_duplicate_never_write(self):
        env, event = self.metadata(self.base)
        api = FakeGitHub(self.base)
        self.assertEqual(release.run_github(api, self.source, env, event, True)['status'], 'bootstrap_required')
        output, receipt, pin = self.bundle()
        api.seed(receipt)
        self.assertEqual(release.run_github(api, self.source, env, event, True)['status'], 'already_released')
        self.assertEqual(api.writes, [])
        api.assets[2] = b'corrupt'
        with self.assertRaises(ValueError):
            release.run_github(api, self.source, env, event, True)

    def test_disabled_dry_run_dangling_tag_draft_and_failed_upload(self):
        output, baseline, pin = self.bundle()
        (self.source / 'project-wiki/SKILL.md').write_text('Synthetic changed distribution')
        for name in ('plugin.json', '.claude-plugin/marketplace.json'):
            path = self.source / name
            data = json.loads(path.read_text())
            (data['plugins'][0] if 'plugins' in data else data)['version'] = '0.2.40'
            path.write_text(json.dumps(data))
        commit = self.commit()
        env, event = self.metadata(commit)
        api = FakeGitHub(commit)
        api.seed(baseline)
        self.assertEqual(release.run_github(api, self.source, env, event)['status'], 'ready_dry_run')
        self.assertEqual(release.run_github(api, self.source, {**env, 'PWS_RELEASE_ENABLED': 'false'}, event, True)['status'], 'publication_disabled')
        self.assertEqual(api.writes, [])
        api.tags['v0.2.40'] = commit
        with self.assertRaisesRegex(ValueError, 'tag'):
            release.run_github(api, self.source, env, event, True)
        del api.tags['v0.2.40']
        api.releases.append({'tag_name': 'v0.2.40', 'draft': True, 'prerelease': False})
        with self.assertRaisesRegex(ValueError, 'draft'):
            release.run_github(api, self.source, env, event, True)
        api.releases.pop()
        api.fail_upload = True
        with self.assertRaisesRegex(ValueError, 'Upload'):
            release.run_github(api, self.source, env, event, True)
        self.assertFalse(any(method == 'PATCH' for method, path in api.writes))
        self.assertTrue(api.releases[-1]['draft'])
        with self.assertRaises(ValueError):
            release.run_github(api, self.source, env, event, True)

    def test_synthetic_publication_completes_then_duplicate_has_no_new_writes(self):
        output, baseline, pin = self.bundle()
        (self.source / 'project-wiki/SKILL.md').write_text('Synthetic next payload')
        self.commit()  # Multi-commit push: payload and version land in separate commits.
        for name in ('plugin.json', '.claude-plugin/marketplace.json'):
            path = self.source / name
            data = json.loads(path.read_text())
            (data['plugins'][0] if 'plugins' in data else data)['version'] = '0.2.40'
            path.write_text(json.dumps(data))
        commit = self.commit()
        env, event = self.metadata(commit)
        api = FakeGitHub(commit)
        api.seed(baseline)
        self.assertEqual(release.run_github(api, self.source, env, event, True)['status'], 'released')
        self.assertFalse(api.releases[-1]['draft'])
        writes = list(api.writes)
        self.assertEqual(release.run_github(api, self.source, env, event, True)['status'], 'already_released')
        self.assertEqual(api.writes, writes)

    def test_asset_redirect_drops_token_and_rejects_other_origins(self):
        req = release.urllib.request.Request('https://api.github.com/synthetic',
                                             headers={'Authorization': 'Bearer SYNTHETIC'})
        redirect = release.AssetRedirect()
        result = redirect.redirect_request(req, None, 302, 'redirect', {},
                                            'https://release-assets.githubusercontent.com/synthetic')
        self.assertIsNone(result.get_header('Authorization'))
        with self.assertRaises(ValueError):
            redirect.redirect_request(req, None, 302, 'redirect', {}, 'https://example.com/synthetic')

    def test_workflow_gates_are_local_main_only_and_disabled(self):
        workflow = (ROOT / '.github/workflows/check.yml').read_text()
        for required in ('needs: check', "github.event_name == 'push'", "github.ref == 'refs/heads/main'",
                         "github.repository_id == '1466210381'", "needs.check.result == 'success'",
                         "PWS_RELEASE_ENABLED: 'false'", 'cancel-in-progress: false', 'persist-credentials: false'):
            self.assertIn(required, workflow)
        self.assertNotIn('workflow_run:', workflow)
        self.assertNotIn('download-artifact', workflow)
        self.assertNotIn('secrets.', workflow)
        self.assertEqual(workflow.count('contents: write'), 1)


class FakeGitHub:
    """Synthetic API adapter; every publication call stays in memory."""
    def __init__(self, commit):
        self.commit = commit
        self.mutation = ''
        self.writes = []
        self.releases = []
        self.tags = {}
        self.assets = {}
        self.fail_upload = False

    def seed(self, receipt):
        tag = 'v' + receipt['version']
        self.tags[tag] = receipt['source_commit']
        self.assets[2] = release.builder.json_bytes(receipt)
        self.releases = [{'id': 1, 'tag_name': tag, 'target_commitish': receipt['source_commit'],
                          'draft': False, 'prerelease': False, 'assets': [
                              {'name': 'package.zip', 'id': 1, 'digest': 'sha256:' + receipt['archive_sha256']},
                              {'name': 'release-receipt.json', 'id': 2}]}]

    def request(self, path, method='GET', data=None, binary=False):
        if method != 'GET':
            self.writes.append((method, path))
            if path == '/git/refs':
                self.tags[data['ref'].removeprefix('refs/tags/')] = data['sha']
                return {}
            if path == '/releases':
                record = {**data, 'id': 3, 'assets': []}
                self.releases.append(record)
                return record
            if method == 'PATCH' and path == '/releases/3':
                self.releases[-1].update(data)
                return self.releases[-1]
            raise AssertionError('Unexpected mutation')
        if path == '':
            return {'id': sync.REPOSITORY_ID, 'full_name': sync.REPOSITORY,
                    'visibility': 'private' if self.mutation == 'private' else 'public', 'default_branch': 'main'}
        if path == '/git/ref/heads/main':
            return {'object': {'sha': '0' * 40 if self.mutation == 'stale' else self.commit}}
        if path.startswith('/commits/'):
            return [] if self.mutation == 'unmerged' else [{'merged_at': 'synthetic', 'merge_commit_sha': self.commit,
                    'base': {'ref': 'main', 'repo': {'id': sync.REPOSITORY_ID}}}]
        if path == '/actions/runs/42':
            return {'event': 'push', 'head_sha': self.commit, 'head_branch': 'main',
                    'path': 'other' if self.mutation == 'workflow' else '.github/workflows/check.yml',
                    'repository': {'id': sync.REPOSITORY_ID}}
        if path.startswith('/actions/runs/42/jobs'):
            jobs = [{'name': n, 'conclusion': 'failure' if self.mutation == 'failed' else 'success'} for n in release.EXPECTED_JOBS]
            return {'total_count': len(jobs), 'jobs': jobs[:-1] if self.mutation == 'missing' else jobs}
        if path == '/releases/3':
            return self.releases[-1]
        if path.startswith('/releases?'):
            return self.releases
        if path.startswith('/git/ref/tags/'):
            tag = path.removeprefix('/git/ref/tags/')
            if tag not in self.tags:
                raise urllib.error.HTTPError('synthetic', 404, 'absent', {}, None)
            return {'object': {'type': 'commit', 'sha': self.tags[tag]}}
        if path.startswith('/releases/assets/'):
            return self.assets[int(path.rsplit('/', 1)[1])]
        raise AssertionError('Unexpected read: ' + path)

    def upload(self, release_id, name, data):
        self.writes.append(('UPLOAD', name))
        asset = {'state': 'failed' if self.fail_upload else 'uploaded',
                 'digest': 'sha256:' + hashlib.sha256(data).hexdigest(),
                 'name': name, 'id': len(self.assets) + 10}
        self.assets[asset['id']] = data
        self.releases[-1]['assets'].append(asset)
        return asset
