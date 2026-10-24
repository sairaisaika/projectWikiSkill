"""The existing return predicate must be visible before readonly work is dispatched."""
import unittest
from unittest.mock import patch

import test_workflow as fixtures

wf, git = fixtures.wf, fixtures.git

class ReadonlyBaselineTests(unittest.TestCase):
    setUp = fixtures.WorkflowTests.setUp
    capture = fixtures.WorkflowTests.capture
    packet = fixtures.WorkflowTests.packet
    change = fixtures.WorkflowTests.change
    readonly_packet = fixtures.WorkflowTests.readonly_packet
    empty_capture = fixtures.WorkflowTests.empty_capture
    readonly_review = fixtures.WorkflowTests.readonly_review
    def test_dirty_root_advisory_precedes_readonly_work_and_does_not_clean_it(self):
        self.change()
        before = git(self.root, 'status', '--porcelain')
        packet = self.readonly_packet()
        observed = packet.get('read_only_baseline', {})
        self.assertEqual(observed.get('status'), 'differences')
        self.assertEqual(observed['difference_count'], 1)
        self.assertIn('src/editor.py', observed['path_sample'])
        self.assertIn('unchanged', observed['meaning'])
        self.assertEqual(git(self.root, 'status', '--porcelain'), before)
        self.assertFalse(wf.finish(packet, self.capture(), self.readonly_review())['structural_reconciliation'])

    def test_readonly_delegation_recomputes_observation_instead_of_copying_parent_claim(self):
        parent = self.packet()
        (self.root / 'unplanned.txt').write_text('synthetic work already present', encoding='utf-8')
        parent['read_only_baseline'] = {'status': 'no_differences_observed'}
        child = wf.delegate(parent, 'reviewer', 'review-child', [], read_only=True)
        self.assertEqual(child.get('read_only_baseline', {}).get('status'), 'differences')
        self.assertIn('unplanned.txt', child['read_only_baseline']['path_sample'])
        self.assertEqual(child['allowed_files'], [])
        self.assertEqual(child['dispatch'], 'not performed')

    def test_clean_observation_is_saved_in_every_view_without_claiming_future_acceptance(self):
        packet = self.readonly_packet()
        observed = packet.get('read_only_baseline', {})
        self.assertEqual(observed.get('status'), 'no_differences_observed')
        self.assertFalse(observed['completion_certificate'])
        for view, name in [('all', None), ('index', None), ('feature', 'feature.md'), ('impact', 'src/editor.py')]:
            with patch.object(wf, 'git', side_effect=AssertionError('snapshot reader invoked Git')):
                rendered = wf.task_view(packet, view, name, snapshot_only=True)
            self.assertEqual(rendered['read_only_baseline'], observed)
            self.assertFalse(rendered['view_observation']['current_check_attempted'])
        self.change()
        result = wf.finish(packet, self.capture(), self.readonly_review())
        self.assertFalse(result['structural_reconciliation'])

    def test_legacy_snapshot_does_not_invent_a_clean_baseline_or_probe_git(self):
        packet = self.readonly_packet()
        packet.pop('read_only_baseline', None)
        with patch.object(wf, 'git', side_effect=AssertionError('legacy snapshot invoked Git')):
            rendered = wf.task_view(packet, 'index', snapshot_only=True)
        self.assertEqual(rendered.get('read_only_baseline', {}).get('status'), 'unavailable')

    def test_planned_untracked_file_warns_but_existing_unselected_cache_is_not_new_scope(self):
        (self.root / 'scratch.tmp').write_text('existing unselected cache', encoding='utf-8')
        captured = self.capture()
        packet = wf.start(captured, 'read', 'reviewer', 'read source', [], ['findings'], ['facts'], read_only=True)
        self.assertEqual(packet.get('read_only_baseline', {}).get('status'), 'no_differences_observed')
        (self.root / 'src/new.py').write_text('new source', encoding='utf-8')
        captured = self.capture(files=['src/new.py'])
        packet = wf.start(captured, 'read-new', 'reviewer', 'read new source', [], ['findings'], ['facts'], read_only=True)
        self.assertEqual(packet.get('read_only_baseline', {}).get('status'), 'differences')
        self.assertEqual(packet['read_only_baseline']['path_sample'], ['src/new.py'])

    def test_edit_packet_has_no_readonly_advisory(self):
        self.assertNotIn('read_only_baseline', self.packet())

    def test_dirty_peer_and_missing_peer_follow_the_existing_return_scope(self):
        peer = self.home / 'mobile'
        (peer / 'src').mkdir(parents=True)
        (peer / 'src/client.py').write_text('old\n', encoding='utf-8')
        git(peer, 'init')
        git(peer, 'config', 'user.name', 'Fixture')
        git(peer, 'config', 'user.email', 'fixture@example.invalid')
        git(peer, 'add', 'src/client.py')
        git(peer, 'commit', '-m', 'peer baseline')
        (peer / 'src/client.py').write_text('new\n', encoding='utf-8')
        captured = self.capture(files=['mobile/src/client.py'], peers={'mobile': str(peer)})
        packet = wf.start(captured, 'read-peer', 'reviewer', 'read peer', [], ['findings'], ['facts'], read_only=True)
        self.assertEqual(packet['read_only_baseline']['status'], 'differences')
        self.assertEqual(packet['read_only_baseline']['path_sample'], ['mobile/src/client.py'])
        captured = self.capture(peers={'mobile': str(self.home / 'missing')})
        packet = wf.start(captured, 'missing-peer', 'reviewer', 'read peer', [], ['findings'], ['facts'], read_only=True)
        self.assertEqual(packet['read_only_baseline']['status'], 'unavailable')
        self.assertEqual(packet['read_only_baseline']['unavailable_peers'], ['mobile'])

    def test_advisory_sample_is_explicit_and_never_replaces_full_impact_or_permissions(self):
        for i in range(11):
            (self.root / ('change-%02d.txt' % i)).write_text('new\n', encoding='utf-8')
        captured = self.capture()
        # These were already-untracked before capture, so unchanged and unselected
        # files are intentionally not final-return differences.
        packet = wf.start(captured, 'read', 'reviewer', 'read source', [], ['findings'], ['facts'], read_only=True)
        for i in range(11):
            (self.root / ('later-%02d.txt' % i)).write_text('new\n', encoding='utf-8')
        child = wf.delegate(packet, 'reviewer', 'later-read', [], read_only=True)
        observed = child['read_only_baseline']
        self.assertEqual(observed['difference_count'], 11)
        self.assertEqual(len(observed['path_sample']), 8)
        self.assertTrue(observed['path_sample_truncated'])
        self.assertEqual(child['context']['files'], ['src/editor.py'])
        self.assertEqual(child['allowed_files'], [])
