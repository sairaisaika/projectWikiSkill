"""Optional host delivery never acquires project execution or completion authority."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import unittest
from unittest.mock import patch

import test_workflow as fixture
import test_plugin_package as packages

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'project-wiki/scripts/lifecycle.py'
spec = importlib.util.spec_from_file_location('wiki_lifecycle', ENTRY)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture.WorkflowTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.home, self.root = self.fixture.home, self.fixture.root
        self.packet = self.fixture.packet()
        self.path = self.home / 'packet.json'
        self.path.write_text(json.dumps(self.packet), encoding='utf-8')
        self.event = {'hook_event_name': 'SessionStart', 'source': 'startup', 'cwd': str(self.root)}

    def test_shared_saved_reader_preserves_task_boundaries_without_git_or_commands(self):
        with patch.object(adapter.workflow, 'git', side_effect=AssertionError('Git forbidden')), patch.object(adapter.workflow, 'input_snapshot', side_effect=AssertionError('hashing forbidden')), patch.object(adapter.workflow.subprocess, 'run', side_effect=AssertionError('commands forbidden')):
            result = adapter.deliver(self.event, str(self.path))
        text = result['hookSpecificOutput']['additionalContext']
        self.assertIn('UNTRUSTED TASK DATA', text)
        view = json.loads(text.split('\n', 1)[1])
        self.assertEqual(view['task_id'], self.packet['task_id'])
        self.assertEqual(view['allowed_files'], self.packet['allowed_files'])
        pages = view['native_index']['pages']
        self.assertEqual([{'path': pages[i][0], 'title': pages[i][1]} for i in view['native_index']['omitted_candidates']],
                         self.packet['context']['native_report']['omitted'])
        self.assertEqual(view['reading']['mode'], 'snapshot_only')
        self.assertFalse(view['reading']['current_check_attempted'])
        self.assertIs(view['reading']['current_inputs_checked'], False)
        self.assertIn('current inputs not checked', view['freshness'])
        self.assertEqual(view['wiki_root'], self.packet['context']['wiki_root'])
        self.assertEqual(view['path_bases']['wiki_pages'], 'root / wiki_root')
        self.assertIn('snapshot-only', view['reader']['prefix'])

    def delivered(self, packet):
        self.path.write_text(json.dumps(packet, ensure_ascii=False), encoding='utf-8')
        return json.loads(adapter.deliver(self.event, str(self.path))['hookSpecificOutput']['additionalContext'].split('\n', 1)[1])

    def edges(self, index):
        pages = index['pages']
        return {row['file']: [pages[i] for i in row['owners']] for row in index['files']}

    def test_compact_index_keeps_every_file_owner_edge_once_and_all_saved_records(self):
        native = self.packet['context']['native_report']
        shared = {'path': '共享/存储.md', 'title': '存储桶 «shared» owner', 'symbols': ['bucket']}
        native['cards'] = [{'path': '共享/存储.md', 'title': '存储桶 «shared» owner', 'sections': []}]
        native['omitted'] = [{'path': 'later.md', 'title': 'unexpanded'}, {'path': 'notitle.md'}]
        first, second = native['impact'][0]['file'], 'unregistered/new.ts'
        native['impact'] = [
            {'file': first, 'pages': [shared, {'path': 'a.md', 'title': 'A', 'symbols': ['x']}], 'unregistered': False,
             'invariants': ['INV_1'], 'futureField': {'kept': True}},
            {'file': second, 'pages': [shared], 'unregistered': True}]
        self.packet['context']['files'] = [first, 'selected/without-record.ts']
        full = adapter.workflow.task_view(self.packet, 'index', snapshot_only=True)
        view = self.delivered(self.packet)
        index = view['native_index']
        # Every edge, including a page shared by both files, is preserved; the shared label is stored once.
        self.assertEqual(self.edges(index), {first: [['共享/存储.md', '存储桶 «shared» owner'], ['a.md', 'A']],
                                             second: [['共享/存储.md', '存储桶 «shared» owner']]})
        self.assertEqual(sum(page == ['共享/存储.md', '存储桶 «shared» owner'] for page in index['pages']), 1)
        self.assertEqual([len(row['owners']) for row in index['files']], [row['satellite_count'] for row in full['native_index']['files']])
        self.assertEqual([index['pages'][i] for i in index['features']], [['共享/存储.md', '存储桶 «shared» owner']])
        self.assertEqual([index['pages'][i] for i in index['omitted_candidates']], [['later.md', 'unexpanded'], ['notitle.md', None]])
        rows = {row['file']: row for row in index['files']}
        self.assertIs(rows[second]['unregistered'], True)
        self.assertIs(rows[second]['selected'], False)
        self.assertNotIn('selected', rows[first])
        self.assertEqual(rows[first]['invariants'], ['INV_1'])
        self.assertEqual(rows[first]['futureField'], {'kept': True})
        self.assertEqual(index['selected_without_record'], ['selected/without-record.ts'])
        self.assertEqual(index['limits'], full['native_index']['limits'])
        self.assertEqual(index['placementIssues'], full['native_index']['placementIssues'])
        # Packet-saved records and source observations stay verbatim.
        for key in ['task_id', 'owner', 'root', 'wiki_root', 'path_bases', 'access', 'base_sha', 'peers', 'freshness',
                    'outcome', 'allowed_files', 'capabilities', 'acceptance', 'limits', 'native_source_comparison']:
            self.assertEqual(view[key], full[key], key)
        self.assertEqual(view['artifact_preservation'], {k: v for k, v in full['artifact_preservation'].items()
                                                         if k not in ('limits', 'local_path_validation')})
        for key in ['feature', 'impact', 'all']:
            self.assertEqual(f"show --packet <same-packet> --snapshot-only {view['reader'][key]}", full['expansion'][key])
        self.assertEqual(view['reader']['review_preparation'], full['review_preparation']['command'] + ' --format text')

    def lookup(self, record, dotted):
        for key in dotted.split('.'):
            record = record[key]
        return record

    def test_operational_instructions_are_named_not_delivered_and_resolve_in_existing_views(self):
        contract = {'schemaVersion': 1, 'status': 'declared', 'authority': ['scripts/contract.ts'],
                    'finish': {'argv': ['bash', 'finish.sh'], 'meaning': 'run after edits'},
                    'acknowledgement': {'marker': 'Checked:', 'example': 'Checked: 页（理由）'},
                    'pushGate': {'argv': ['gate']}, 'reader': {'argv': ['build']}, 'limits': 'zero exit is insufficient',
                    'futureOp': {'x': 1},
                    'context': {'status': 'observed', 'capturedAt': '2026-01-01T00:00:00Z', 'wikiRoot': '/w/docs/wiki',
                                'sources': {'web': {'root': '/w', 'revision': 'a' * 40, 'modified': 0},
                                            'mobile': {'root': '/m', 'revision': 'b' * 40, 'untracked': 1}},
                                'execution': {'runtime': 'node', 'version': 'v1'}, 'limits': '来源观察'}}
        hashed = json.loads(json.dumps(self.packet['context']['native_report']))
        self.packet['context']['native_report']['workflow'] = contract
        self.packet['access'], self.packet['allowed_files'] = 'read_only', []
        self.packet['read_only_baseline'] = {'status': 'no_differences_observed', 'difference_count': 0,
                                             'completion_certificate': False, 'meaning': 'm', 'limits': 'l'}
        before = json.loads(json.dumps(self.packet))
        index = adapter.workflow.task_view(self.packet, 'index', snapshot_only=True)
        compact = adapter.compact_index(index, self.packet)
        self.assertEqual(self.packet, before)  # neither the packet nor the public view is mutated
        self.assertEqual(index, adapter.workflow.task_view(before, 'index', snapshot_only=True))
        view = self.delivered(self.packet)
        self.assertEqual(view, {**json.loads(json.dumps(compact)), 'index_delivered': True})
        # Source/runtime observations, capture time/status and identity stay inline.
        self.assertEqual(view['native_workflow'], {**{k: contract[k] for k in ('schemaVersion', 'status', 'authority')},
                                                      'context': {k: v for k, v in contract['context'].items() if k != 'limits'}})
        self.assertEqual((view['access'], view['allowed_files']), ('read_only', []))
        self.assertEqual(view['read_only_baseline'], {'status': 'no_differences_observed', 'difference_count': 0,
                                                      'completion_certificate': False})
        self.assertIs(view['reading']['current_inputs_checked'], False)
        self.assertIn('not checked', view['freshness'])
        deferred = view['not_delivered']
        self.assertEqual(deferred['status'], 'NOT DELIVERED')
        self.assertEqual(sorted(deferred['all']), sorted(['native_workflow.' + k for k in ('finish', 'acknowledgement', 'pushGate', 'reader', 'limits', 'futureOp')]
                                                         + ['native_workflow.context.limits', 'artifact_preservation.limits', 'review_preparation.meaning']))
        self.assertEqual(deferred['summary'], ['task_scope.return_requirements', 'read_only_baseline.meaning', 'read_only_baseline.limits'])
        flat = json.dumps(view, ensure_ascii=False)
        for name in ['finish.sh', 'Checked:', 'zero exit']:
            self.assertNotIn(name, flat)
        # Every deferred name resolves to the original saved value in the named existing snapshot view.
        for reader, names in [('all', deferred['all']), ('summary', deferred['summary'])]:
            # The summary reader re-verifies the saved native report hash; its
            # deferred fields live outside that report.
            source = before if reader == 'all' else {**before, 'context': {**before['context'], 'native_report': hashed}}
            shown = adapter.workflow.task_view(source, reader, snapshot_only=True)
            for name in names:
                head, key = name.split('.', 1)
                original = self.lookup({'native_workflow': contract, 'task_scope': {'return_requirements': before['return_requirements']},
                                        'read_only_baseline': before['read_only_baseline'],
                                        'artifact_preservation': index['artifact_preservation'],
                                        'review_preparation': index['review_preparation']}[head], key)
                self.assertEqual(self.lookup(shown, name), original, name)

    def test_large_operational_contract_alone_does_not_block_routing_delivery(self):
        self.packet['context']['native_report']['workflow'] = {
            'status': 'declared', 'finish': {'meaning': 'x' * (adapter.MAX_CONTEXT * 2)},
            'context': {'status': 'observed', 'sources': {'web': {'root': '/w', 'revision': 'c' * 40}}}}
        view = self.delivered(self.packet)
        self.assertEqual(view['native_workflow']['context']['sources']['web']['revision'], 'c' * 40)
        self.assertIn('native_workflow.finish', view['not_delivered']['all'])
        self.assertTrue(self.edges(view['native_index']))

    def test_large_provenance_prose_defers_but_observations_and_bounded_reader_are_delivered(self):
        context = {'status': 'observed', 'sources': {'web': {'root': '/w', 'revision': 'e' * 40}},
                   'execution': {'runtime': 'node', 'version': 'v22'}, 'limits': 'provenance ' * 2000}
        self.packet['context']['native_report']['workflow'] = {'status': 'declared', 'context': context}
        view = self.delivered(self.packet)
        self.assertIs(view['index_delivered'], True)
        self.assertEqual(view['native_workflow']['context'], {k: v for k, v in context.items() if k != 'limits'})
        self.assertIn('native_workflow.context.limits', view['not_delivered']['all'])
        self.assertIn('--format text', view['reader']['prefix'])
        self.assertIn('--format text', view['reader']['review_preparation'])
        self.assertEqual(view['reader']['program'], [sys.executable, str(Path(adapter.workflow.__file__).resolve())])

    def test_oversized_source_observations_still_opt_out(self):
        self.packet['context']['native_report']['workflow'] = {
            'status': 'declared', 'context': {'sources': {'web': {'root': '/' + '观' * adapter.MAX_CONTEXT}}}}
        data = self.delivered(self.packet)
        self.assertIs(data['index_delivered'], False)
        self.assertNotIn('native_workflow', data)

    def test_native_metadata_cannot_shadow_owner_edges_or_selected_scope(self):
        native = self.packet['context']['native_report']
        path = native['impact'][0]['file']
        native['impact'][0].update({'owners': ['native-value'], 'selected': False, 'native_fields': {'nested': [1]}})
        before = json.loads(json.dumps(self.packet))
        view = self.delivered(self.packet)
        row = next(r for r in view['native_index']['files'] if r['file'] == path)
        self.assertTrue(all(isinstance(i, int) for i in row['owners']))
        self.assertNotIn('selected', row)
        self.assertEqual(row['native_fields'], {'owners': ['native-value'], 'selected': False, 'native_fields': {'nested': [1]}})
        self.assertEqual(self.packet, before)

    def test_same_path_with_different_saved_titles_is_not_merged(self):
        native = self.packet['context']['native_report']
        native['impact'][0]['pages'] = [{'path': 'p.md', 'title': 'one'}, {'path': 'p.md', 'title': 'two'}, {'path': 'p.md'}]
        index = self.delivered(self.packet)['native_index']
        self.assertEqual(self.edges(index)[native['impact'][0]['file']], [['p.md', 'one'], ['p.md', 'two'], ['p.md', None]])

    def test_many_owners_overflow_opts_out_without_listing_selected_paths(self):
        native = self.packet['context']['native_report']
        native['impact'][0]['pages'] = [{'path': f'页/{n}.md', 'title': '标题' * 10} for n in range(200)]
        data = self.delivered(self.packet)
        self.assertIs(data['index_delivered'], False)
        self.assertGreater(data['index_bytes'], data['budget_bytes'])
        self.assertEqual(data['budget_bytes'], adapter.MAX_CONTEXT)
        self.assertEqual(set(data), {'packet_selection', 'index_delivered', 'reason', 'index_bytes', 'budget_bytes', 'current_inputs_checked'})

    def test_malformed_native_rows_fail_visibly_without_contents(self):
        env = {**os.environ, 'PROJECT_WIKI_PACKET': str(self.path)}
        for bad in [['sensitive-row'], [{'file': 'f', 'pages': ['sensitive-page']}], [{'file': 'f'}], [{'file': 'f', 'pages': [{'title': 'sensitive-page'}]}]]:
            self.packet['context']['native_report']['impact'] = bad
            self.path.write_text(json.dumps(self.packet), encoding='utf-8')
            cp = subprocess.run([sys.executable, str(ENTRY)], input=json.dumps(self.event), text=True, capture_output=True, env=env)
            self.assertEqual(cp.returncode, 0)
            self.assertIn('not delivered', json.loads(cp.stdout)['systemMessage'])
            self.assertNotIn('sensitive', cp.stdout + cp.stderr)

    def test_no_selection_and_other_events_are_quiet(self):
        with patch.object(adapter.workflow, 'read_json', side_effect=AssertionError('must not read')):
            self.assertIsNone(adapter.deliver(self.event, None))
            self.assertIsNone(adapter.deliver({**self.event, 'hook_event_name': 'Stop'}, str(self.path)))

    def test_subdirectory_allowed_but_other_checkout_is_not(self):
        self.assertIsNotNone(adapter.deliver({**self.event, 'cwd': str(self.root / 'src')}, str(self.path)))
        with self.assertRaisesRegex(ValueError, 'another workspace'):
            adapter.deliver({**self.event, 'cwd': str(self.home)}, str(self.path))

    def test_relative_missing_bad_source_and_nonpacket_are_rejected(self):
        for selected in ['packet.json', str(self.home / 'absent.json')]:
            with self.assertRaises(ValueError):
                adapter.deliver(self.event, selected)
        with self.assertRaisesRegex(ValueError, 'start source'):
            adapter.deliver({**self.event, 'source': 'invented'}, str(self.path))
        self.path.write_text('{}', encoding='utf-8')
        with self.assertRaises(ValueError):
            adapter.deliver(self.event, str(self.path))

    def test_large_index_is_explicitly_undelivered_not_silently_clipped(self):
        self.packet['outcome'] = 'x' * (adapter.MAX_CONTEXT + 100)
        self.path.write_text(json.dumps(self.packet), encoding='utf-8')
        result = adapter.deliver(self.event, str(self.path))
        data = json.loads(result['hookSpecificOutput']['additionalContext'].split('\n', 1)[1])
        self.assertIs(data['index_delivered'], False)
        self.assertIs(data['current_inputs_checked'], False)
        self.assertEqual(data['packet_selection'], 'PROJECT_WIKI_PACKET')

    def test_unicode_packet_path_cannot_expand_the_overflow_notice(self):
        # Keep the synthetic path below Linux's filesystem byte limit while its
        # ASCII-escaped form would still overflow the former fallback.
        selected = str(self.home.joinpath(*(['文' * 20] * 60), 'packet.json'))
        self.assertLess(len(selected), 4096)
        self.assertGreater(len(json.dumps(selected).encode('utf-8')), adapter.MAX_CONTEXT)
        self.packet['outcome'] = 'x' * (adapter.MAX_CONTEXT + 100)
        with patch.object(adapter.Path, 'is_file', return_value=True), patch.object(adapter.workflow, 'read_json', return_value=self.packet):
            result = adapter.deliver(self.event, selected)
        context = result['hookSpecificOutput']['additionalContext']
        data = json.loads(context.split('\n', 1)[1])
        self.assertIs(data['index_delivered'], False)
        self.assertEqual(data['packet_selection'], 'PROJECT_WIKI_PACKET')
        self.assertNotIn(selected, context)
        self.assertLess(len(context.encode('utf-8')), adapter.MAX_CONTEXT)

    def test_cli_delivery_emits_json_without_writes_or_raw_event(self):
        before = {p: p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
        env = {**os.environ, 'PROJECT_WIKI_PACKET': str(self.path)}
        event = {**self.event, 'transcript_path': 'sensitive-ignored', 'session_id': 'private-ignored'}
        cp = subprocess.run([sys.executable, str(ENTRY)], input=json.dumps(event), text=True, capture_output=True, env=env)
        self.assertEqual(cp.returncode, 0)
        self.assertEqual(cp.stderr, '')
        result = json.loads(cp.stdout)
        self.assertEqual(result['hookSpecificOutput']['hookEventName'], 'SessionStart')
        self.assertNotIn('private-ignored', cp.stdout)
        self.assertNotIn('sensitive-ignored', cp.stdout)
        self.assertEqual(before, {p: p.read_bytes() for p in self.home.rglob('*') if p.is_file()})

    def test_bad_event_visible_failure_does_not_echo_secrets_or_block(self):
        env = {**os.environ, 'PROJECT_WIKI_PACKET': str(self.path)}
        for raw in ['sensitive-malformed', 'x' * (adapter.MAX_EVENT + 1), '[]']:
            cp = subprocess.run([sys.executable, str(ENTRY)], input=raw, text=True, capture_output=True, env=env)
            self.assertEqual(cp.returncode, 0)
            self.assertIn('not delivered', json.loads(cp.stdout)['systemMessage'])
            self.assertNotIn('sensitive-malformed', cp.stdout + cp.stderr)
            self.assertNotIn('hookSpecificOutput', json.loads(cp.stdout))

    def test_optional_package_profiles_keep_original_default_and_doctor_layers(self):
        for enabled in [False, True]:
            out = self.home / ('hooks' if enabled else 'plain')
            packages.builder.build(out, with_hooks=enabled)
            report = packages.doctor.inspect(out, ROOT)
            self.assertTrue(report['package_valid'], report)
            self.assertTrue(report['source_support_match'])
            for host in ['claude', 'codex']:
                manifest = json.loads((out / f'.{host}-plugin/plugin.json').read_text())
                self.assertEqual('hooks' in manifest, enabled)
                if enabled:
                    config = json.loads((out / manifest['hooks']).read_text())
                    # Codex carries delivery only; Claude also declares the optional pre-edit gate.
                    self.assertEqual(list(config['hooks']), {'claude': ['SessionStart', 'PreToolUse'], 'codex': ['SessionStart']}[host])
            for layer in ['installation', 'hook_trust', 'hook_execution', 'context_delivery', 'agent_use', 'semantic_review', 'business_acceptance']:
                self.assertEqual(report[layer], 'unverified')

    def test_packaged_runpy_entry_resolves_sibling_and_keeps_package_readonly(self):
        out = self.home / 'packaged'
        packages.builder.build(out, with_hooks=True)
        config = json.loads((out / 'hooks/codex.json').read_text())
        command = config['hooks']['SessionStart'][0]['hooks'][0]['commandWindows']
        # Execute the exact Python payload inside the actual generated command;
        # shell parsing/host invocation and trust are separate acceptance layers.
        code = command.split(' -c "', 1)[1][:-1]
        env = {**os.environ, 'CLAUDE_PLUGIN_ROOT': str(out), 'PROJECT_WIKI_PACKET': str(self.path)}
        cp = subprocess.run([sys.executable, '-c', code], input=json.dumps(self.event), text=True, capture_output=True, env=env)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn('hookSpecificOutput', json.loads(cp.stdout))
        self.assertTrue(packages.doctor.inspect(out, ROOT)['package_valid'])

    def test_modified_hook_and_forged_profile_cannot_pass_package_closure(self):
        out = self.home / 'changed'
        packages.builder.build(out, with_hooks=True)
        p = out / 'hooks/codex.json'
        p.write_text('{}')
        self.assertFalse(packages.doctor.inspect(out)['package_valid'])
        receipt = out / 'PACKAGE-SOURCES.json'
        value = json.loads(receipt.read_text())
        value['lifecycle_hooks'] = 'true'
        receipt.write_text(json.dumps(value))
        self.assertFalse(packages.doctor.inspect(out)['package_valid'])

    @unittest.skipUnless(os.name == 'nt', 'Windows directory-junction regression')
    def test_windows_junction_cannot_import_external_canonical_skill_in_either_profile(self):
        source = self.home / 'junction-source'
        source.mkdir()
        (source / 'scripts').mkdir()
        external = self.home / 'external-skill'
        shutil.copytree(ROOT / 'project-wiki', external, ignore=shutil.ignore_patterns('__pycache__'))
        (external / 'outside-marker.md').write_text('Synthetic outside-scope marker')
        for name in ['plugin.json', 'LICENSE', 'scripts/plugin_doctor.py']:
            shutil.copyfile(ROOT / name, source / name)
        link = source / 'project-wiki'
        cp = subprocess.run(['cmd.exe', '/c', 'mklink', '/J', str(link), str(external)], capture_output=True, text=True)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        # Remove only the verified fixture junction itself, never recurse into
        # its target. The normal temporary-directory cleanup owns actual files.
        self.addCleanup(os.rmdir, link)
        self.assertFalse(link.is_symlink())
        for enabled in [False, True]:
            out = self.home / ('rejected-hooks' if enabled else 'rejected-default')
            with self.assertRaisesRegex(ValueError, 'alias or escape'):
                packages.builder.build(out, source, with_hooks=enabled)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
