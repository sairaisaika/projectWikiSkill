"""Synthetic review exercises for the authored visibility procedure.

This test-only metadata interpreter binds fixtures to the shipped decision table;
it is not a production classifier, access check, scanner or secret detector.
No remote is contacted. Real Git only reads/configures disposable repositories.
"""
import json
import re
import test_repository_hygiene as hygiene
import unittest


class RepositoryVisibilityTests(unittest.TestCase):
    setUp = hygiene.RepositoryHygieneTests.setUp
    git = hygiene.RepositoryHygieneTests.git
    write = hygiene.RepositoryHygieneTests.write
    documented = hygiene.RepositoryHygieneTests.documented
    query = hygiene.RepositoryHygieneTests.query

    def rows(self):
        rows = dict(re.findall(r'^\| (public|private|internal|unknown) \| (.+) \|$',
                               self.method, re.M))
        self.assertEqual(set(rows), {'public', 'private', 'internal', 'unknown'})
        return rows

    def metadata(self, visibility, repo='example/project'):
        return {'status': 200, 'account_verified': True, 'repository_full_name': repo,
                'repository_id': 123, 'visibility': visibility, 'permissions': {'pull': True}}

    def observed(self, payload, intended='example/project'):
        # Test oracle: an incomplete/mismatched observation must select unknown.
        valid = (payload.get('status') == 200 and payload.get('account_verified') is True
                 and payload.get('repository_full_name') == intended
                 and payload.get('repository_id') is not None
                 and payload.get('permissions', {}).get('pull') is True)
        value = payload.get('visibility') if valid else 'unknown'
        return value if value in self.rows() else 'unknown'

    def push_urls(self, explicit=None):
        branch = self.git('symbolic-ref', '--short', 'HEAD').stdout.decode().strip()
        remote = explicit
        for key in (f'branch.{branch}.pushRemote', 'remote.pushDefault', f'branch.{branch}.remote'):
            if remote:
                break
            result = self.git('config', '--get', key, codes=(0, 1))
            remote = result.stdout.decode().strip()
        if not remote:
            return []  # No invented origin or visibility for a local-only repo.
        return self.git('remote', 'get-url', '--push', '--all', remote).stdout.decode().splitlines()

    def test_entry_and_four_checkpoints_reach_one_visibility_table(self):
        self.rows()
        section = self.method.split('## Classify at each task boundary', 1)[1].split('\n| Class', 1)[0]
        checkpoints = re.split(r'\n[1-4]\. ', '\n' + section)[1:]
        self.assertEqual(len(checkpoints), 4)
        for checkpoint in checkpoints:
            self.assertRegex(checkpoint.lower(), r'visibility|destination')
        template = self.method.split('> **Repository boundary:**', 1)[1].split('\n\n', 1)[0]
        self.assertIn('#visibility-and-publication-scope', template)
        for root in (hygiene.ROOT, hygiene.FIXTURE):
            for question in ('repository visibility', '仓库可见性'):
                self.assertEqual(self.query(root, question)['id'], 'repository-hygiene')
        native = (hygiene.SKILL / 'references/native-wiki-adoption.md').read_text(encoding='utf-8')
        self.assertIn('repository-hygiene.md#wiki-boundary-and-configuration-index', native)

    def test_public_private_internal_and_unknown_metadata_select_distinct_rows(self):
        rows = self.rows()
        for visibility in rows:
            payload = json.loads(json.dumps(self.metadata(visibility)))
            self.assertEqual(self.observed(payload), visibility)
        self.assertIn('explicitly approved for public', rows['public'])
        for visibility in ('private', 'internal'):
            self.assertIn('business-authorized', rows[visibility])
            self.assertIn('actual audience', rows[visibility])
        self.assertIn('not a personal private repository', rows['internal'])
        self.assertIn('public restrictions', rows['unknown'])
        self.assertIn('block publication', rows['unknown'])

    def test_url_clone_empty_denied_and_wrong_account_or_repo_prove_nothing(self):
        invalid = [{}, {'status': 403}, {'clone_succeeded': True, 'url': 'https://example.invalid/private/project'}]
        for key, value in [('account_verified', False), ('repository_full_name', 'example/other'),
                           ('repository_id', None), ('permissions', {}), ('visibility', 'unspecified')]:
            payload = self.metadata('private')
            payload[key] = value
            invalid.append(payload)
        for payload in invalid:
            self.assertEqual(self.observed(payload), 'unknown')
        self.assertEqual(self.push_urls(), [])
        self.assertIn('A local-only path does not waive this review', self.method)

    def test_actual_push_and_explicit_destination_override_origin(self):
        urls = {'origin': 'https://example.invalid/team/private.git',
                'publish': 'https://example.invalid/team/public.git',
                'fork': 'https://example.invalid/contributor/fork.git'}
        for name, url in urls.items():
            self.git('remote', 'add', name, url)
        branch = self.git('symbolic-ref', '--short', 'HEAD').stdout.decode().strip()
        self.git('config', f'branch.{branch}.remote', 'origin')
        self.git('config', 'remote.pushDefault', 'publish')
        self.assertEqual(self.push_urls(), [urls['publish']])
        self.git('config', f'branch.{branch}.pushRemote', 'fork')
        self.assertEqual(self.push_urls(), [urls['fork']])
        self.assertEqual(self.push_urls(explicit='publish'), [urls['publish']])
        self.git('config', 'url.https://example.invalid/team/public.git.pushInsteadOf', 'publish-alias:')
        self.git('remote', 'set-url', 'publish', 'publish-alias:')
        self.assertEqual(self.push_urls(explicit='publish'), [urls['publish']])
        self.assertIn('branch.BRANCH.pushRemote', self.method)
        self.assertIn('remote.pushDefault', self.method)
        self.assertIn('remote get-url --push --all', self.method)

    def test_multiple_push_urls_and_pr_fork_use_strictest_scope(self):
        self.git('remote', 'add', 'publish', 'https://example.invalid/team/read.git')
        urls = ['https://example.invalid/team/private.git', 'https://example.invalid/team/public.git']
        for url in urls:
            self.git('config', '--add', 'remote.publish.pushurl', url)
        self.assertEqual(self.push_urls('publish'), urls)
        metadata = [self.metadata('private'), self.metadata('public', 'example/upstream')]
        observed = [self.observed(row, row['repository_full_name']) for row in metadata]
        self.assertEqual(observed, ['private', 'public'])
        self.assertIn('strictest content limit across all', self.method)
        self.assertIn('PR base and fork/head', self.method)
        # A separate public PR destination remains public even with a private source.
        self.assertIn('explicitly approved for public', self.rows()[observed[1]])

    def test_destination_visibility_account_or_audience_change_requires_recheck(self):
        self.git('remote', 'add', 'publish', 'https://example.invalid/example/project.git')
        previous = self.push_urls('publish')
        baseline = self.metadata('private')
        self.assertEqual(self.observed(baseline), 'private')
        self.git('remote', 'set-url', '--push', 'publish',
                 'https://example.invalid/example/new-target.git')
        self.assertNotEqual(self.push_urls('publish'), previous)
        # Old private metadata cannot vouch for the changed destination.
        self.assertEqual(self.observed(baseline, 'example/new-target'), 'unknown')
        fresh = self.metadata('public', 'example/new-target')
        self.assertEqual(self.observed(fresh, 'example/new-target'), 'public')
        fresh['account_verified'] = False
        self.assertEqual(self.observed(fresh, 'example/new-target'), 'unknown')
        self.assertIn('Recheck when the target, account, visibility or audience changes', self.method)
        self.assertIn('immediately before publication', self.method)
        self.assertIn('authorized for every actual recipient group', self.method)

    def test_synthetic_release_audience_can_be_wider_than_private_source(self):
        source = self.metadata('private')
        release = {'source_repo': 'example/project', 'destination': 'example/downloads',
                   'visibility': 'public', 'audience': 'anyone', 'asset': 'synthetic-summary.txt'}
        self.assertEqual(self.observed(source), 'private')
        self.assertEqual(self.observed(self.metadata(release['visibility'], release['destination']),
                                       release['destination']), 'public')
        self.assertIn('explicitly approved for public', self.rows()[release['visibility']])
        for surface in ('PR/diff', 'attachments', 'logs', 'CI artifacts', 'release'):
            self.assertIn(surface, self.method)
        for forbidden in ('credentials', 'raw personal/user data', 'private logs', 'backups'):
            self.assertIn(forbidden, self.method)
        self.assertIn('None of these rows relaxes', self.method)

    def test_tracked_content_stays_tracked_across_visibility_or_ignore_changes(self):
        before = (self.root / '.git/index').read_bytes()
        for visibility in ('public', 'private', 'internal', 'unknown'):
            self.assertEqual(self.observed(self.metadata(visibility)), visibility)
            self.write('.gitignore', '/tracked-output.txt\n')
            self.documented('ls-files', 'tracked-output.txt')
            match = self.documented('check-ignore -v --no-index', 'tracked-output.txt').stdout
            self.assertIn(b'/tracked-output.txt', match)
        self.assertEqual((self.root / '.git/index').read_bytes(), before)
        self.assertIn('Visibility, ignore, retention and authorization are independent', self.method)

    def scaffold_templates(self):
        rows = re.findall(r'^\| (AGENTS.md|PROJECT.md|PRODUCT.md) \| (.+?) \| (.+?) \|$',
                          self.method, re.M)
        self.assertEqual({row[0] for row in rows}, {'AGENTS.md', 'PROJECT.md', 'PRODUCT.md'})
        return rows

    def test_setup_scaffolds_follow_visibility_without_filename_bans(self):
        templates = self.scaffold_templates()
        for visibility in ('public', 'private', 'internal', 'unknown'):
            observed = self.observed(self.metadata(visibility))
            column = 1 if observed in ('public', 'unknown') else 2
            for row in templates:
                self.write(row[0], row[column] + '\n')
            self.git('add', '--', *(row[0] for row in templates))
            for row in templates:
                self.documented('ls-files', row[0])
                self.assertEqual((self.root / row[0]).read_text(encoding='utf-8'), row[column] + '\n')
        self.assertIn('none of these filenames is a ban', self.method)
        self.assertIn('preferable to separate copies on every machine', self.method)
        self.assertIn('must disclose neither private', self.method)
        self.assertIn('Unknown visibility uses the public-safe skeleton', self.method)
        self.assertIn('secrets, real customer records', self.method)

    def test_existing_scaffold_conflict_preserves_files_tracking_and_history(self):
        names = [row[0] for row in self.scaffold_templates()]
        for name in names:
            self.write(name, 'Synthetic existing internal decision; owner review pending.\n')
        self.git('add', '--', *names)
        self.git('-c', 'commit.gpgsign=false', 'commit', '-m', 'Synthetic existing scaffold')
        self.write('.gitignore', '/PROJECT.md\n')
        original = {name: (self.root / name).read_bytes() for name in [*names, '.gitignore']}
        head = self.git('rev-parse', 'HEAD').stdout
        index = (self.root / '.git/index').read_bytes()
        for visibility in ('public', 'private'):
            self.assertEqual(self.observed(self.metadata(visibility)), visibility)
            for name in names:
                self.documented('ls-files', name)
                self.documented('status', name)
        self.assertEqual(self.git('rev-parse', 'HEAD').stdout, head)
        self.assertEqual((self.root / '.git/index').read_bytes(), index)
        for name, content in original.items():
            self.assertEqual((self.root / name).read_bytes(), content)
        self.assertIn('Do not automatically move, delete,', self.method)
        self.assertIn('private does not remove prior public exposure or repair Git history', self.method)
