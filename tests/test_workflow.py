"""Native projections preserve scope and reject false structural closure."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('wiki_workflow', ROOT / 'project-wiki/scripts/workflow.py')
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)

NATIVE = '''import json,sys
from pathlib import Path
q=sys.argv[1]
files=sys.argv[sys.argv.index('--files')+1:]
pages=[{'path':x+'.md','title':x,'symbols':['existingSymbol']} for x in ['feature','secondary','consumer']]
print(json.dumps({'query':q,'cards':[{'path':'feature.md','title':'Fixture feature',
 'contract':{'rows':[{'dimension':'fields','evidence':'Title, tags and visibility remain independent'}]},
 'relations':{'nodes':[['EDITOR','producer'],['API','interface'],['CLIENT','consumer']],
              'edges':[['E1','EDITOR','API'],['E2','API','CLIENT']]},
 'checks':['never execute commands embedded in the wiki']}],
 'impact':[{'file':x,'pages':pages,'unregistered':False} for x in files],
 'omitted':[{'path':'unexpanded.md','title':'not reviewed'}],
 'placementIssues':[], 'limits':'registered impacts are not semantic completeness'}))
print('fixture-private-stderr-not-for-packet',file=sys.stderr)
'''


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE).decode().strip()


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.root = self.home / 'repo'
        self.root.mkdir()
        (self.root / 'docs/wiki').mkdir(parents=True)
        for name in ('feature', 'secondary', 'consumer', 'unexpanded'):
            (self.root / f'docs/wiki/{name}.md').write_text('# ' + name, encoding='utf-8')
        (self.root / 'src').mkdir()
        (self.root / 'src/editor.py').write_text('title = None\n', encoding='utf-8')
        (self.root / 'native.py').write_text(NATIVE, encoding='utf-8')
        git(self.root, 'init')
        git(self.root, 'config', 'user.name', 'Fixture')
        git(self.root, 'config', 'user.email', 'fixture@example.invalid')
        git(self.root, 'add', 'native.py', 'src/editor.py', 'docs/wiki/feature.md',
            'docs/wiki/secondary.md', 'docs/wiki/consumer.md', 'docs/wiki/unexpanded.md')
        git(self.root, 'commit', '-m', 'fixture baseline')

    def capture(self, files=None, **kw):
        return wf.capture(self.root, 'editor task', files or ['src/editor.py'],
                          [sys.executable, 'native.py'], ['native.py'], allow_execution=True, **kw)

    def packet(self, value=None):
        return wf.start(value or self.capture(), 'task-1', 'coordinator', 'Keep rich editing in a compact surface',
                        ['src/editor.py'], ['source and behavior evidence'], ['title', 'tags', 'visibility'])

    def review(self):
        return {'pages': {x+'.md': {'status':'no_update', 'reason':'source rule remains unchanged'}
                          for x in ['feature','secondary','consumer']},
                'capabilities': {x:{'status':'source_verified','reason':'inspected same source entry',
                                   'references':['src/editor.py']} for x in ['title','tags','visibility']},
                'handoff': {'remaining':['real UI/runtime acceptance'], 'next_safe_action':'Run the actual editor flow'}}

    def change(self):
        (self.root / 'src/editor.py').write_text('title = "present"\n', encoding='utf-8')

    def test_capture_keeps_all_satellites_contracts_relations_and_omissions(self):
        capture = self.capture()
        self.assertEqual(len(capture['native_report']['impact'][0]['pages']), 3)
        self.assertEqual(len(capture['native_report']['cards'][0]['relations']['edges']), 2)
        self.assertEqual(capture['native_report']['omitted'][0]['title'], 'not reviewed')
        self.assertNotIn('fixture-private-stderr-not-for-packet', json.dumps(capture))
        self.assertGreater(capture['native_stderr_bytes'], 0)
        self.assertEqual(capture['evidence']['agent_use'], 'unverified')
        self.assertFalse((self.root / 'commands-were-executed').exists())

    def test_native_execution_requires_explicit_caller_opt_in(self):
        with self.assertRaisesRegex(ValueError, 'explicit opt-in'):
            wf.capture(self.root,'q',[],[sys.executable,'native.py'],['native.py'])

    def test_capture_rejects_omitted_file_not_just_wrong_counts(self):
        native = self.root / 'native.py'
        native.write_text(NATIVE.replace("'impact':[{'file':x,'pages':pages,'unregistered':False} for x in files]",
                                         "'impact':[]"), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'omitted or substituted'):
            self.capture()

    def test_source_or_wiki_drift_prevents_new_dispatch(self):
        capture = self.capture()
        self.change()
        with self.assertRaisesRegex(ValueError, 'source files changed'):
            self.packet(capture)
        capture = self.capture()
        (self.root / 'docs/wiki/consumer.md').write_text('changed rules',encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'stale'):
            self.packet(capture)

    def test_lost_satellite_in_a_saved_projection_is_not_silently_accepted(self):
        captured=self.capture()
        captured['native_report']['impact'][0]['pages'].pop()
        with self.assertRaisesRegex(ValueError,'changed after capture'):
            self.packet(captured)

    def test_explicit_index_and_exact_expansions_retain_every_native_record(self):
        packet = self.packet()
        index = wf.task_view(packet, 'index')
        self.assertNotIn('native_context', index)
        self.assertEqual(index['native_index']['files'][0]['satellite_count'], 3)
        self.assertEqual(index['native_index']['omitted_candidates'][0]['path'], 'unexpanded.md')
        feature = wf.task_view(packet, 'feature', 'feature.md')
        self.assertEqual(feature['native_context']['cards'], packet['context']['native_report']['cards'])
        impact = wf.task_view(packet, 'impact', 'src/editor.py')
        self.assertEqual(impact['native_context']['impact'], packet['context']['native_report']['impact'])
        with self.assertRaisesRegex(ValueError, 'exact feature or file'):
            wf.task_view(packet, 'impact', 'missing.py')

    def test_index_does_not_pretend_to_deliver_full_context(self):
        view = wf.task_view(self.packet(), 'index')
        self.assertIn('not delivered', view['expansion']['reading_state'])
        self.assertEqual(view['capabilities'], ['title', 'tags', 'visibility'])

    def test_reading_views_expose_existing_wiki_path_basis_without_rewriting_keys(self):
        packet = self.packet()
        for view, selected in [('index', None), ('feature', 'feature.md'),
                               ('impact', 'src/editor.py'), ('all', None)]:
            for saved in (False, True):
                shown = wf.task_view(packet, view, selected, snapshot_only=saved)
                self.assertEqual(shown['wiki_root'], packet['context']['wiki_root'])
                self.assertEqual(shown['path_bases']['wiki_pages'], 'root / wiki_root')
                if view in ('feature', 'all'):
                    self.assertEqual(shown['native_context']['cards'][0]['path'], 'feature.md')

    def test_custom_wiki_root_identifies_the_real_page_instead_of_a_root_decoy(self):
        custom = self.root / 'knowledge' / 'manual'
        custom.parent.mkdir()
        (self.root / 'docs/wiki').rename(custom)
        (self.root / 'feature.md').write_text('wrong root-level decoy', encoding='utf-8')
        captured = self.capture(wiki_root='knowledge/manual')
        packet = self.packet(captured)
        with patch.object(wf, 'check_capture', side_effect=AssertionError('no live check')):
            shown = wf.task_view(packet, 'index', snapshot_only=True)
        path = self.root / shown['wiki_root'] / shown['native_index']['features'][0]['path']
        self.assertEqual(path.read_text(encoding='utf-8'), '# feature')
        self.assertNotEqual(path, self.root / 'feature.md')

    def test_snapshot_path_basis_keeps_foreign_strings_and_missing_root_unknown(self):
        packet = self.packet()
        packet['root'] = '/foreign/checkout'
        packet['context']['wiki_root'] = 'knowledge/手册'
        with patch.object(wf, 'check_capture', side_effect=AssertionError('no live check')):
            shown = wf.task_view(packet, 'index', snapshot_only=True)
            self.assertEqual(shown['root'], '/foreign/checkout')
            self.assertEqual(shown['wiki_root'], 'knowledge/手册')
            packet['context'].pop('wiki_root')
            self.assertIsNone(wf.task_view(packet, 'index', snapshot_only=True)['wiki_root'])

    def test_snapshot_view_does_not_attempt_live_checks_or_commands(self):
        packet = self.packet()
        with ExitStack() as stack:
            spies = [stack.enter_context(patch.object(wf, name, side_effect=AssertionError('No live input access')))
                     for name in ('check_capture', 'git', 'input_snapshot', 'peer_snapshot', 'source_hash', 'artifact_snapshot')]
            spies.extend(stack.enter_context(patch.object(wf.subprocess, name, side_effect=AssertionError('No commands')))
                         for name in ('run', 'check_output'))
            shown = wf.task_view(packet, 'index', snapshot_only=True)
        self.assertTrue(all(spy.call_count == 0 for spy in spies))
        self.assertIn('not checked', shown['freshness'])
        self.assertFalse(shown['view_observation']['current_inputs_checked'])
        self.assertEqual(shown['native_index']['omitted_candidates'], packet['context']['native_report']['omitted'])
        self.assertEqual(shown['allowed_files'], packet['allowed_files'])

    def test_snapshot_expansions_keep_mode_and_original_native_records(self):
        packet = self.packet()
        native = packet['context']['native_report']
        index = wf.task_view(packet, 'index', snapshot_only=True)
        for name in ('feature', 'impact', 'all'):
            self.assertIn('--snapshot-only', index['expansion'][name])
        for view, selected, key in [('feature', 'feature.md', 'cards'), ('impact', 'src/editor.py', 'impact'), ('all', None, None)]:
            shown = wf.task_view(packet, view, selected, snapshot_only=True)
            self.assertIn('not checked', shown['freshness'])
            self.assertEqual(shown['native_context'] if key is None else shown['native_context'][key], native if key is None else native[key])
            self.assertEqual(shown['native_workflow'], index['native_workflow'])
            self.assertEqual(shown['native_source_comparison'], index['native_source_comparison'])

    def test_snapshot_is_not_a_fresh_dispatch_or_artifact_observation(self):
        evidence = self.home / 'old-result.json'
        evidence.write_text('{"result":"old failure"}', encoding='utf-8')
        packet = self.packet(self.capture(preserve_artifacts=[str(evidence.resolve())]))
        saved = copy.deepcopy(packet['context']['preserved_artifact_hashes'])
        evidence.write_text('{"result":"changed"}', encoding='utf-8')
        self.change()
        shown = wf.task_view(packet, 'all', snapshot_only=True)
        self.assertEqual(shown['artifact_preservation']['captured_sha256'], saved)
        self.assertFalse(shown['view_observation']['current_inputs_checked'])
        self.assertIn('historical', wf.task_view(packet)['freshness'])
        with self.assertRaisesRegex(ValueError, 'artifact changed'):
            wf.delegate(packet, 'worker', 'new-task', ['src/editor.py'])

    def test_snapshot_cli_works_without_git_and_is_not_a_dispatch_switch(self):
        packet = self.home / 'task.json'
        packet.write_text(json.dumps(self.packet()), encoding='utf-8')
        script = ROOT / 'project-wiki/scripts/workflow.py'
        result = subprocess.run([sys.executable, str(script), 'show', '--packet', str(packet), '--snapshot-only'],
                                env={**os.environ, 'PATH': ''}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        shown = json.loads(result.stdout)
        self.assertIn('not checked', shown['freshness'])
        self.assertFalse(shown['view_observation']['current_inputs_checked'])
        rejected = subprocess.run([sys.executable, str(script), 'delegate', '--packet', str(packet),
                                   '--task-id', 'child', '--owner', 'worker', '--read-only',
                                   '--output', str(self.home / 'child.json'), '--snapshot-only'], capture_output=True, text=True)
        self.assertEqual(rejected.returncode, 2)
        self.assertIn('unrecognized arguments: --snapshot-only', rejected.stderr)
        self.assertFalse((self.home / 'child.json').exists())

    def test_snapshot_keeps_foreign_host_artifact_paths_as_unchecked_data(self):
        packet = self.packet()
        foreign = '/peer/private/old-result.json' if os.name == 'nt' else 'C:/peer/private/old-result.json'
        packet['context']['preserve_artifacts'] = [foreign]
        packet['context']['preserved_artifact_hashes'] = {foreign: '0' * 64}
        shown = wf.task_view(packet, 'all', snapshot_only=True)
        self.assertEqual(shown['artifact_preservation']['paths'], [foreign])
        self.assertEqual(shown['artifact_preservation']['captured_sha256'], {foreign: '0' * 64})
        self.assertEqual(shown['artifact_preservation']['status'], 'captured_snapshot')
        self.assertIn('not performed', shown['artifact_preservation']['local_path_validation'])
        with self.assertRaisesRegex(ValueError, 'absolute paths'):
            wf.delegate(packet, 'worker', 'child', ['src/editor.py'])

    def test_snapshot_display_does_not_relax_readonly_scope_validation(self):
        packet = self.packet()
        packet['access'] = 'read_only'
        with self.assertRaisesRegex(ValueError, 'access scope'):
            wf.task_view(packet, 'index', snapshot_only=True)

    def test_snapshot_qualifies_saved_source_comparison_without_rewriting_it(self):
        packet = self.packet()
        saved = copy.deepcopy(packet['context']['native_source_comparison'])
        for view, selected in [('index', None), ('feature', 'feature.md'),
                               ('impact', 'src/editor.py'), ('all', None)]:
            shown = wf.task_view(packet, view, selected, snapshot_only=True)
            self.assertEqual(shown['native_source_comparison'], saved)
            observation = shown['native_source_comparison_observation']
            self.assertEqual(observation['record_time'], 'capture')
            self.assertFalse(observation['current_check_attempted'])
            self.assertIn('not a current match', observation['meaning'])
        self.assertEqual(packet['context']['native_source_comparison'], saved)
        self.assertNotIn('native_source_comparison_observation', wf.task_view(packet))

    def test_snapshot_does_not_replace_default_live_check(self):
        packet = self.packet()
        current = wf.task_view(packet, 'index')
        self.assertTrue(current['view_observation']['current_check_attempted'])
        self.assertTrue(current['view_observation']['current_inputs_checked'])
        with patch.object(wf, 'git', side_effect=PermissionError('Reader cannot invoke Git')) as attempted:
            historical = wf.task_view(packet, 'index')
        self.assertGreater(attempted.call_count, 0)
        self.assertIn('historical', historical['freshness'])
        self.assertTrue(historical['view_observation']['current_check_attempted'])
        self.assertFalse(historical['view_observation']['current_inputs_checked'])

    def test_native_workflow_reaches_index_exact_views_and_delegation_without_execution(self):
        native = self.root / 'native.py'
        native.write_text(NATIVE.replace("'placementIssues':[]", "'workflow':{'authority':'native.py','acknowledgement':{'format':'Reviewed: <page> (reason)'},'finish':{'argv':['never-run-native-finish']}}, 'placementIssues':[]"), encoding='utf-8')
        packet = self.packet()
        expected = packet['context']['native_report']['workflow']
        for view, selected in [('index', None), ('feature', 'feature.md'), ('impact', 'src/editor.py'), ('all', None)]:
            self.assertEqual(wf.task_view(packet, view, selected)['native_workflow'], expected)
        child = wf.delegate(packet, 'child', 'worker', ['src/editor.py'])
        self.assertEqual(wf.task_view(child, 'index')['native_workflow'], expected)
        self.assertFalse((self.root / 'never-run-native-finish').exists())

    def test_absent_native_workflow_is_explicitly_undeclared_not_generic_completion(self):
        view = wf.task_view(self.packet(), 'index')
        self.assertEqual(view['native_workflow'], {'status': 'not_declared', 'meaning': 'The native router did not provide its return contract; inspect its own gates before dispatch.'})

    def test_native_mutation_during_capture_is_detected(self):
        p = self.root / 'native.py'
        p.write_text(NATIVE + "\nPath('docs/wiki/consumer.md').write_text('changed during capture')\n",encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'changed during'):
            self.capture()

    def test_delegate_cannot_widen_scope_and_does_not_claim_delivery(self):
        packet = self.packet()
        child = wf.delegate(packet, 'worker', 'child-1', ['src/editor.py'])
        self.assertEqual(child['dispatch'], 'not performed')
        self.assertEqual(child['context'], packet['context'])
        with self.assertRaisesRegex(ValueError, 'cannot widen'):
            wf.delegate(packet, 'worker', 'child-1', ['unrelated.py'])

    def test_show_preserves_context_without_hash_inventory_and_marks_stale(self):
        packet = self.packet()
        view = wf.task_view(packet)
        self.assertEqual(view['native_context'], packet['context']['native_report'])
        self.assertNotIn('inputs',view)
        self.change()
        self.assertIn('historical', wf.task_view(packet)['freshness'])

    def test_real_diff_reconciliation_is_not_runtime_or_completion_certification(self):
        packet = self.packet()
        self.change()
        result = wf.finish(packet,self.capture(),self.review())
        self.assertTrue(result['structural_reconciliation'], result['issues'])
        self.assertEqual(result['actual_files'], ['src/editor.py'])
        self.assertEqual(result['runtime_acceptance'], 'not inferred')
        self.assertIn('not established',result['product_completion'])
        self.assertTrue(result['source_state']['tracked_worktree_dirty'])
        self.assertIsNotNone(result['source_state']['file_hashes']['src/editor.py'])

    def test_omitted_satellite_and_missing_capability_are_separate_failures(self):
        packet = self.packet()
        self.change()
        review = self.review()
        del review['pages']['consumer.md']
        del review['capabilities']['tags']
        result = wf.finish(packet,self.capture(),review)
        self.assertFalse(result['structural_reconciliation'])
        self.assertTrue(any('consumer.md' in x for x in result['issues']))
        self.assertTrue(any('tags' in x for x in result['issues']))

    def test_updated_without_diff_and_reasonless_waiver_do_not_pass(self):
        packet = self.packet()
        self.change()
        review = self.review()
        review['pages']['feature.md']={'status':'updated'}
        review['pages']['secondary.md']={'status':'no_update'}
        result = wf.finish(packet,self.capture(),review)
        self.assertFalse(result['structural_reconciliation'])
        self.assertTrue(any('without a real change' in x for x in result['issues']))
        self.assertTrue(any('needs a reason' in x for x in result['issues']))

    def test_unplanned_or_omitted_actual_files_are_not_hidden(self):
        packet = self.packet()
        self.change()
        (self.root / 'src/new-consumer.py').write_text('new consumer\n',encoding='utf-8')
        result = wf.finish(packet,self.capture(),self.review())
        self.assertFalse(result['structural_reconciliation'])
        self.assertIn('src/new-consumer.py',result['actual_files'])
        self.assertTrue(any('not completely covered' in x for x in result['issues']))

    def test_after_capture_must_cover_current_source_bytes(self):
        packet = self.packet()
        self.change()
        after = self.capture()
        (self.root / 'src/editor.py').write_text('changed again\n',encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'source files changed'):
            wf.finish(packet,after,self.review())

    def test_gap_can_be_recorded_but_does_not_disappear_into_completion(self):
        packet = self.packet()
        self.change()
        review = self.review()
        review['capabilities']['tags']={'status':'gap','reason':'same API does not expose tag editing in this client'}
        result = wf.finish(packet,self.capture(),review)
        self.assertTrue(result['structural_reconciliation'])
        self.assertEqual(result['capability_gaps'], ['tags'])
        self.assertIn('not established',result['product_completion'])

    def test_missing_peer_is_unverified_not_an_empty_diff(self):
        peers={'mobile':str(self.home/'absent-mobile')}
        packet = self.packet(self.capture(peers=peers))
        self.change()
        result = wf.finish(packet,self.capture(peers=peers),self.review())
        self.assertFalse(result['structural_reconciliation'])
        self.assertTrue(any('not an empty diff' in x for x in result['issues']))

    def test_unavailable_evidence_and_missing_handoff_fail(self):
        packet = self.packet()
        self.change()
        review = self.review()
        review['capabilities']['title']['references']=['invented-evidence.json']
        review.pop('handoff')
        result=wf.finish(packet,self.capture(),review)
        self.assertFalse(result['structural_reconciliation'])
        self.assertTrue(any('reference unavailable' in x for x in result['issues']))
        self.assertTrue(any('handoff' in x for x in result['issues']))

    def test_no_overwrite_of_prior_context(self):
        path=self.home/'capture.json'
        wf.write_new(path,self.capture())
        before=path.read_bytes()
        with self.assertRaises(FileExistsError):
            wf.write_new(path,{'incorrect':'replacement'})
        self.assertEqual(path.read_bytes(),before)

    def test_recovered_untracked_planned_source_remains_in_final_scope(self):
        (self.root / 'src/recovered.py').write_text('previous worker candidate\n',encoding='utf-8')
        initial=self.capture(files=['src/editor.py','src/recovered.py'])
        packet=wf.start(initial,'recover','root','Review recovered candidate',
                        ['src/editor.py','src/recovered.py'],['inspect candidate'],['title','tags','visibility'])
        result=wf.finish(packet,self.capture(files=['src/recovered.py']),self.review())
        self.assertIn('src/recovered.py',result['actual_files'])
        self.assertTrue(result['structural_reconciliation'],result['issues'])

    def test_peer_diff_is_included_and_preexisting_untracked_cache_is_not_a_new_change(self):
        peer=self.home/'mobile'
        (peer/'src').mkdir(parents=True)
        (peer/'src/client.py').write_text('old\n',encoding='utf-8')
        git(peer,'init')
        git(peer,'config','user.name','Fixture')
        git(peer,'config','user.email','fixture@example.invalid')
        git(peer,'add','src/client.py')
        git(peer,'commit','-m','peer baseline')
        (peer/'existing-cache.tmp').write_text('fixture cache',encoding='utf-8')
        peers={'mobile':str(peer)}
        initial=self.capture(files=['mobile/src/client.py'],peers=peers)
        packet=wf.start(initial,'peer-task','root','Preserve cross-client behavior',
                        ['mobile/src/client.py'],['inspect consumer'],['title','tags','visibility'])
        (peer/'src/client.py').write_text('new\n',encoding='utf-8')
        result=wf.finish(packet,self.capture(files=['mobile/src/client.py'],peers=peers),self.review())
        self.assertTrue(result['structural_reconciliation'],result['issues'])
        self.assertEqual(result['actual_files'],['mobile/src/client.py'])
        self.assertIsNotNone(result['source_state']['file_hashes']['mobile/src/client.py'])

    def test_equal_contract_bytes_do_not_allow_substituting_the_peer_checkout(self):
        primary = self.home / 'client-main'
        (primary / 'src').mkdir(parents=True)
        (primary / 'src/client.py').write_text('contract = "stable"\n', encoding='utf-8')
        git(primary, 'init')
        git(primary, 'config', 'user.name', 'Fixture')
        git(primary, 'config', 'user.email', 'fixture@example.invalid')
        git(primary, 'add', 'src/client.py')
        git(primary, 'commit', '-m', 'client baseline')
        candidate = self.home / 'client-candidate'
        git(self.home, 'clone', str(primary), str(candidate))
        git(candidate, 'config', 'user.name', 'Fixture')
        git(candidate, 'config', 'user.email', 'fixture@example.invalid')
        (candidate / 'src/editor.py').write_text('personal_editor = True\n', encoding='utf-8')
        git(candidate, 'add', 'src/editor.py')
        git(candidate, 'commit', '-m', 'candidate-only consumer')
        files = ['mobile/src/client.py']
        before = self.capture(files=files, peers={'mobile': str(primary)})
        after = self.capture(files=files, peers={'mobile': str(candidate)})
        self.assertEqual(before['planned_source_hashes'], after['planned_source_hashes'])
        self.assertNotEqual(before['peers']['mobile']['head'], after['peers']['mobile']['head'])
        packet = wf.start(before, 'peer-binding', 'root', 'Inspect the selected client variant',
                          [], ['scoped source findings'], ['title', 'tags', 'visibility'], read_only=True)
        child = wf.delegate(packet, 'worker', 'old-scope-child', [], read_only=True)
        refreshed = wf.start(after, 'new-variant', 'root', 'Inspect candidate consumer',
                             [], ['candidate source findings'], ['title', 'tags', 'visibility'], read_only=True)
        self.assertEqual(wf.task_view(child, 'index')['peers']['mobile']['head'], git(primary, 'rev-parse', 'HEAD'))
        self.assertEqual(wf.task_view(refreshed, 'index')['peers']['mobile']['head'], git(candidate, 'rev-parse', 'HEAD'))
        self.assertFalse((primary / 'src/editor.py').exists())
        self.assertTrue((candidate / 'src/editor.py').exists())
        with self.assertRaisesRegex(ValueError, 'peer checkouts differ'):
            wf.finish(packet, after, self.review())

    def test_actual_router_execution_witness_is_not_relabelled_as_worker_execution(self):
        native = self.root / 'native.py'
        native.write_text(NATIVE.replace("'placementIssues':[]", "'workflow':{'authority':'native.py',"
            "'execution':{'executable':sys.executable,'python':sys.version.split()[0],"
            "'scope':'this native-router invocation only'}}, 'placementIssues':[]"), encoding='utf-8')
        packet = self.packet()
        witness = packet['context']['native_report']['workflow']['execution']
        self.assertEqual(Path(witness['executable']).resolve(), Path(sys.executable).resolve())
        self.assertEqual(witness['python'], sys.version.split()[0])
        for view, selected in [('index', None), ('feature', 'feature.md'), ('impact', 'src/editor.py'), ('all', None)]:
            shown = wf.task_view(packet, view, selected)
            self.assertEqual(shown['native_workflow']['execution'], witness)
        child = wf.delegate(packet, 'worker', 'execution-child', ['src/editor.py'])
        self.assertEqual(wf.task_view(child, 'index')['native_workflow']['execution'], witness)
        self.assertEqual(child['dispatch'], 'not performed')
        self.assertEqual(witness['scope'], 'this native-router invocation only')

    def readonly_packet(self):
        return wf.start(self.capture(),'review-1','reviewer','Choose a justified next investigation',[],
                        ['inspectable findings without repository changes'],['interpret source facts'],read_only=True)

    def empty_capture(self):
        return wf.capture(self.root,'editor task',[],[sys.executable,'native.py'],['native.py'],allow_execution=True)

    def readonly_review(self):
        return {'pages':{},'capabilities':{'interpret source facts':{
            'status':'source_verified','reason':'inspected the captured source and limits',
            'references':['src/editor.py']}},
            'handoff':{'remaining':['semantic/runtime acceptance'],'next_safe_action':'Dispatch a separately scoped engineering task'}}

    def test_readonly_keeps_read_context_without_inventing_edit_permissions(self):
        packet=self.readonly_packet()
        self.assertEqual(packet['allowed_files'],[])
        self.assertEqual(packet['context']['files'],['src/editor.py'])
        for view,path in [('index',None),('all',None),('feature','feature.md'),('impact','src/editor.py')]:
            self.assertEqual(wf.task_view(packet,view,path)['access'],'read_only')
        self.assertIn('not a filesystem sandbox',packet['limits'])

    def test_readonly_start_rejects_edit_paths_and_edit_start_still_requires_scope(self):
        captured=self.capture()
        with self.assertRaisesRegex(ValueError,'cannot grant editing'):
            wf.start(captured,'t','o','read',['src/editor.py'],['evidence'],['interpret'],read_only=True)
        with self.assertRaisesRegex(ValueError,'Editing tasks require'):
            wf.start(captured,'t','o','edit',[],['evidence'],['interpret'])

    def test_readonly_delegation_inherits_no_edits_and_edit_parent_can_narrow_to_review(self):
        parent=self.readonly_packet()
        child=wf.delegate(parent,'child','child-1',[])
        self.assertEqual(child['access'],'read_only')
        self.assertEqual(child['allowed_files'],[])
        with self.assertRaisesRegex(ValueError,'cannot widen'):
            wf.delegate(parent,'child','child-2',['src/editor.py'])
        narrowed=wf.delegate(self.packet(),'child','review-child',[],read_only=True)
        self.assertEqual(narrowed['access'],'read_only')
        self.assertEqual(narrowed['allowed_files'],[])

    def test_readonly_return_without_changes_preserves_limits_and_requires_evidence(self):
        packet=self.readonly_packet()
        result=wf.finish(packet,self.empty_capture(),self.readonly_review())
        self.assertTrue(result['structural_reconciliation'],result['issues'])
        self.assertEqual(result['actual_files'],[])
        self.assertEqual(result['access'],'read_only')
        self.assertEqual(result['runtime_acceptance'],'not inferred')
        bad=self.readonly_review();bad['capabilities']={}
        self.assertFalse(wf.finish(packet,self.empty_capture(),bad)['structural_reconciliation'])

    def test_readonly_return_rejects_implicit_wiki_write_even_when_updated_is_acknowledged(self):
        packet=self.readonly_packet()
        (self.root/'docs/wiki/consumer.md').write_text('changed by a nominal reviewer',encoding='utf-8')
        review=self.readonly_review()
        review['pages']={p+'.md':{'status':'updated' if p=='consumer' else 'no_update','reason':'reviewed'}
                         for p in ['feature','secondary','consumer']}
        result=wf.finish(packet,self.capture(files=['docs/wiki/consumer.md']),review)
        self.assertFalse(result['structural_reconciliation'])
        self.assertTrue(any('read-only task has repository differences' in p for p in result['issues']))

    def test_readonly_existing_dirty_tree_is_conservatively_not_certified_as_unchanged(self):
        self.change()
        packet=self.readonly_packet()
        result=wf.finish(packet,self.capture(),self.readonly_review())
        self.assertFalse(result['structural_reconciliation'])
        self.assertIn('src/editor.py',result['actual_files'])

    def test_native_extra_structure_facts_survive_capture_and_exact_impact_view(self):
        p=self.root/'native.py'
        p.write_text(NATIVE.replace("'unregistered':False}","'unregistered':False,'structure':{'status':'available','namedFunctionBodies':34,'sha256':'fixture-content-hash'}}"),encoding='utf-8')
        packet=self.readonly_packet()
        impact=wf.task_view(packet,'impact','src/editor.py')
        self.assertEqual(impact['native_context']['impact'][0]['structure'],
                         {'status':'available','namedFunctionBodies':34,'sha256':'fixture-content-hash'})

    def test_review_template_leaves_readonly_capabilities_unreviewed(self):
        packet = self.readonly_packet()
        after = self.empty_capture()
        before = git(self.root, 'status', '--porcelain')
        prepared = wf.review_template(packet, after)
        self.assertEqual(prepared['pages'], {})
        self.assertEqual(set(prepared['capabilities']), set(packet['capabilities']))
        self.assertEqual(prepared['capabilities']['interpret source facts'],
                         {'status': 'unreviewed', 'reason': '', 'references': []})
        result = wf.finish(packet, after, prepared)
        self.assertFalse(result['structural_reconciliation'])
        self.assertIn('required capability unreviewed: interpret source facts', result['issues'])
        self.assertEqual(git(self.root, 'status', '--porcelain'), before)

    def test_review_template_uses_actual_capture_satellites_and_new_unregistered_files(self):
        native = self.root / 'native.py'
        native.write_text(NATIVE.replace("'unregistered':False", "'unregistered':x=='src/new.py'"), encoding='utf-8')
        packet = self.packet()
        self.change()
        (self.root / 'src/new.py').write_text('new_consumer = True\n', encoding='utf-8')
        after = self.capture(files=['src/editor.py', 'src/new.py'])
        prepared = wf.review_template(packet, after)
        self.assertEqual(set(prepared['pages']), {'feature.md', 'secondary.md', 'consumer.md'})
        self.assertTrue(all(row == {'status': 'unreviewed', 'reason': ''}
                            for row in prepared['pages'].values()))
        self.assertEqual(prepared['unregistered'], {'src/new.py': ''})
        self.assertFalse(wf.finish(packet, after, prepared)['structural_reconciliation'])

    def test_readonly_finish_rejects_list_shaped_review_even_without_changed_pages(self):
        packet = self.readonly_packet()
        after = self.empty_capture()
        for field in ('pages', 'capabilities', 'unregistered'):
            bad = self.readonly_review()
            bad[field] = []
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, field + ' must be an object.*review-template'):
                wf.finish(packet, after, bad)
        bad = self.readonly_review()
        bad['capabilities']['interpret source facts'] = 'I checked it'
        with self.assertRaisesRegex(ValueError, 'entries must be objects'):
            wf.finish(packet, after, bad)

    def test_reference_location_prose_has_an_actionable_error(self):
        packet = self.readonly_packet()
        review = self.readonly_review()
        review['capabilities']['interpret source facts']['references'] = ['src/editor.py:1 (title)']
        with self.assertRaisesRegex(ValueError, 'put lines/symbols in reason.*review-template'):
            wf.finish(packet, self.empty_capture(), review)

    def test_template_rejects_stale_and_different_checkout_captures(self):
        packet = self.readonly_packet()
        after = self.empty_capture()
        (self.root / 'docs/wiki/feature.md').write_text('changed after capture', encoding='utf-8')
        with self.assertRaises(ValueError):
            wf.review_template(packet, after)
        after = self.empty_capture()
        foreign = copy.deepcopy(packet)
        foreign['root'] = str(self.home / 'another-checkout')
        with self.assertRaisesRegex(ValueError, 'different checkouts'):
            wf.review_template(foreign, after)

    def test_every_reading_view_exposes_optional_return_preparation(self):
        packet = self.readonly_packet()
        for view, path in [('index', None), ('all', None), ('feature', 'feature.md'), ('impact', 'src/editor.py')]:
            shown = wf.task_view(packet, view, path)
            self.assertIn('review-template --packet', shown['review_preparation']['command'])
            self.assertIn('unreviewed', shown['review_preparation']['meaning'])

    def test_real_cli_template_writes_one_unreviewed_file_without_overwrite(self):
        packet = self.home / 'task.json'
        after = self.home / 'after.json'
        out = self.home / 'review.json'
        wf.write_new(packet, self.readonly_packet())
        wf.write_new(after, self.empty_capture())
        argv = [sys.executable, str(ROOT / 'project-wiki/scripts/workflow.py'), 'review-template',
                '--packet', str(packet), '--after-capture', str(after), '--output', str(out)]
        first = subprocess.run(argv, text=True, capture_output=True)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        original = out.read_bytes()
        generated = json.loads(original)
        self.assertEqual(generated['capabilities']['interpret source facts']['status'], 'unreviewed')
        second = subprocess.run(argv, text=True, capture_output=True)
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual(out.read_bytes(), original)

    def test_real_cli_start_readonly_does_not_require_a_dummy_allowed_file(self):
        capture=self.home/'capture.json';wf.write_new(capture,self.capture())
        packet=self.home/'task.json'
        completed=subprocess.run([sys.executable,str(ROOT/'project-wiki/scripts/workflow.py'),'start',
            '--capture',str(capture),'--task-id','review-cli','--owner','reviewer','--outcome','interpret source',
            '--acceptance','inspectable result','--capability','interpret facts','--read-only','--output',str(packet)],
            text=True,capture_output=True)
        self.assertEqual(completed.returncode,0,completed.stdout+completed.stderr)
        self.assertEqual(json.loads(packet.read_text(encoding='utf-8'))['allowed_files'],[])

    def capture_cli_file_groups(self, name, groups):
        output = self.home / (name + '.json')
        (self.root / 'src/viewer.py').write_text('visible = True\n', encoding='utf-8')
        argv = [sys.executable, str(ROOT / 'project-wiki/scripts/workflow.py'), 'capture',
                '--root', str(self.root), '--query', 'editor consumer',
                '--native-argv', json.dumps([sys.executable, 'native.py']),
                '--runtime-input', 'native.py', '--allow-native-execution',
                '--output', str(output)]
        for group in groups:
            argv.extend(['--files', *group])
        completed = subprocess.run(argv, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        return json.loads(output.read_text(encoding='utf-8'))

    def test_cli_repeated_file_groups_keep_every_planned_consumer(self):
        captured = self.capture_cli_file_groups('repeated', [
            ['src/editor.py', 'src/editor.py'], ['src/viewer.py'],
        ])
        expected = ['src/editor.py', 'src/viewer.py']
        self.assertEqual(captured['files'], expected)
        self.assertEqual([row['file'] for row in captured['native_report']['impact']], expected)
        self.assertEqual(set(captured['planned_source_hashes']), set(expected))
        self.assertTrue(all(len(row['pages']) == 3 for row in captured['native_report']['impact']))

    def test_cli_later_empty_file_group_does_not_erase_prior_scope(self):
        captured = self.capture_cli_file_groups('empty-after', [['src/editor.py'], []])
        self.assertEqual(captured['files'], ['src/editor.py'])
        self.assertEqual(captured['native_report']['impact'][0]['file'], 'src/editor.py')

    def test_cli_single_absent_and_empty_file_groups_keep_existing_behavior(self):
        for name, groups, expected in [
            ('single', [['src/editor.py', 'src/viewer.py']], ['src/editor.py', 'src/viewer.py']),
            ('absent', [], []),
            ('empty', [[]], []),
        ]:
            with self.subTest(name=name):
                captured = self.capture_cli_file_groups(name, groups)
                self.assertEqual(captured['files'], expected)
                self.assertEqual([row['file'] for row in captured['native_report']['impact']], expected)


    def return_capture(self, packet, **kwargs):
        return wf.capture_return(packet, [sys.executable, 'native.py'],
                                 allow_execution=True, **kwargs)

    def test_capture_return_collects_real_root_peer_and_planned_untracked_without_allowlist_filter(self):
        peer = self.home / 'mobile-return'
        (peer / 'src').mkdir(parents=True)
        (peer / 'src/client.py').write_text('old\n', encoding='utf-8')
        git(peer, 'init')
        git(peer, 'config', 'user.name', 'Fixture')
        git(peer, 'config', 'user.email', 'fixture@example.invalid')
        git(peer, 'add', 'src/client.py')
        git(peer, 'commit', '-m', 'peer baseline')
        (peer / 'existing-cache.tmp').write_text('preexisting unselected cache', encoding='utf-8')
        (peer / 'src/recovered.py').write_text('recovered candidate', encoding='utf-8')
        initial = self.capture(files=['src/editor.py', 'mobile/src/client.py', 'mobile/src/recovered.py'],
                               peers={'mobile': str(peer)})
        packet = wf.start(initial, 'actual-return', 'coordinator', 'Inspect every actual consumer',
                          initial['files'], ['inspect all actual impacts'], ['title', 'tags', 'visibility'])
        self.change()
        git(self.root, 'add', 'src/editor.py')
        git(self.root, 'commit', '-m', 'normal source change')
        (peer / 'src/client.py').write_text('new\n', encoding='utf-8')
        (self.root / 'src/新 reader.py').write_text('unplanned\n', encoding='utf-8')
        after = self.return_capture(packet)
        expected = ['mobile/src/client.py', 'mobile/src/recovered.py', 'src/editor.py', 'src/新 reader.py']
        self.assertEqual(after['files'], expected)
        self.assertEqual([row['file'] for row in after['native_report']['impact']], expected)
        self.assertNotEqual(after['base']['head'], packet['base_sha'])
        self.assertEqual(packet['base_sha'], initial['base']['head'])
        result = wf.finish(packet, after, self.review())
        self.assertEqual(result['actual_files'], expected)
        self.assertFalse(result['structural_reconciliation'])
        self.assertTrue(any('unplanned files: src/新 reader.py' in x for x in result['issues']))

    def test_capture_return_clean_readonly_is_empty_not_the_planned_list(self):
        initial = self.capture()
        packet = wf.start(initial, 'readonly-return', 'reviewer', 'Read only', [],
                          ['source report'], ['title', 'tags', 'visibility'], read_only=True)
        after = self.return_capture(packet)
        self.assertEqual(after['files'], [])
        self.assertEqual(after['native_report']['impact'], [])
        self.assertTrue(wf.finish(packet, after, self.review())['structural_reconciliation'])
        self.change()
        dirty = self.return_capture(packet)
        self.assertEqual(dirty['files'], ['src/editor.py'])
        self.assertFalse(wf.finish(packet, dirty, self.review())['structural_reconciliation'])

    def test_capture_return_retains_deletions_as_actual_changes(self):
        packet = self.packet()
        (self.root / 'src/editor.py').unlink()
        after = self.return_capture(packet)
        self.assertEqual(after['files'], ['src/editor.py'])
        self.assertIsNone(after['planned_source_hashes']['src/editor.py'])

    def test_capture_return_requires_review_of_changed_runtime_but_allows_normal_wiki_edits(self):
        packet = self.packet()
        (self.root / 'docs/wiki/consumer.md').write_text('updated original consumer rule', encoding='utf-8')
        self.assertIn('docs/wiki/consumer.md', self.return_capture(packet)['files'])
        marker = self.home / 'unreviewed-runtime-ran'
        (self.root / 'native.py').write_text(
            NATIVE + '\nPath(' + repr(str(marker)) + ').write_text("ran changed body", encoding="utf-8")\n',
            encoding='utf-8')
        blocked = False
        try:
            self.return_capture(packet)
        except ValueError as error:
            self.assertIn('runtime input', str(error))
            blocked = True
        self.assertFalse(marker.exists(), 'A changed runtime body executed without a fresh review boundary')
        self.assertTrue(blocked)

    def test_capture_return_runtime_change_in_collector_is_not_a_new_reviewed_baseline(self):
        packet = self.packet()
        marker = self.home / 'runtime-gap-ran'
        collector = wf.repository_changes

        def change_after_guard(*args, **kwargs):
            value = collector(*args, **kwargs)
            (self.root / 'native.py').write_text(
                NATIVE + '\nPath(' + repr(str(marker)) + ').write_text("changed runtime executed", encoding="utf-8")\n',
                encoding='utf-8')
            return value

        rejection = None
        with patch.object(wf, 'repository_changes', side_effect=change_after_guard):
            try:
                self.return_capture(packet)
            except ValueError as error:
                rejection = str(error)
        self.assertFalse(marker.exists(), 'A replaced runtime became a new accepted capture baseline')
        self.assertIsNotNone(rejection)
        self.assertIn('runtime', rejection)

    def test_root_paths_cannot_be_shadowed_by_the_peer_alias_namespace(self):
        packet = self.packet()
        peers = {'mobile': {'root': str(self.home / 'synthetic-peer'), 'available': True, 'head': 'peer-sha'}}
        (self.root / 'mobile').mkdir()
        (self.root / 'mobile/client.py').write_text('physical root source', encoding='utf-8')
        legacy = copy.deepcopy(packet)
        legacy['context']['peers'] = peers
        after = {'root': str(self.root), 'peers': peers}
        with self.assertRaisesRegex(ValueError, 'namespace'):
            wf.source_hash(self.root, 'mobile/client.py', peers)
        with self.assertRaisesRegex(ValueError, 'namespace'):
            wf.repository_changes(legacy, after)
        with self.assertRaisesRegex(ValueError, 'namespace'):
            self.capture(peers={'mobile': str(self.home / 'absent-peer')})
        # Legacy root deletion still has an ambiguous label after its directory is gone.
        (self.root / 'mobile/client.py').unlink()
        (self.root / 'mobile').rmdir()
        with patch.object(wf, 'changed_files', return_value=['mobile/client.py']):
            with self.assertRaisesRegex(ValueError, 'namespace'):
                wf.repository_changes(legacy, after)
        # A distinct explicit alias preserves the existing path format.
        (self.root / 'mobile').mkdir()
        (self.root / 'mobile/client.py').write_text('root source retained', encoding='utf-8')
        self.assertEqual(wf.source_hash(self.root, 'mobile/client.py', {'other-peer': peers['mobile']}),
                         wf.file_hash(self.root / 'mobile/client.py'))

    def test_capture_return_requires_explicit_native_opt_in_and_matching_caller_argv(self):
        packet = self.packet()
        with patch.object(wf, 'capture', side_effect=AssertionError('must not execute native')):
            with self.assertRaisesRegex(ValueError, 'explicit opt-in'):
                wf.capture_return(packet, [sys.executable, 'native.py'])
            with self.assertRaisesRegex(ValueError, 'argv'):
                wf.capture_return(packet, ['not-the-reviewed-command'], allow_execution=True)
            damaged = copy.deepcopy(packet)
            damaged['context']['native_report']['cards'][0]['title'] = 'changed saved context'
            with self.assertRaisesRegex(ValueError, 'changed'):
                self.return_capture(damaged)
            damaged = copy.deepcopy(packet)
            damaged['base_sha'] = 'HEAD'
            with self.assertRaisesRegex(ValueError, 'base'):
                self.return_capture(damaged)

    def test_capture_return_missing_peer_and_changed_artifact_fail_before_native_execution(self):
        artifact = self.home / 'original-evidence.json'
        artifact.write_text('original selected evidence', encoding='utf-8')
        artifact = artifact.resolve(strict=True)
        packet = self.packet(self.capture(peers={'mobile': str(self.home / 'absent-peer')},
                                         preserve_artifacts=[str(artifact)]))
        with patch.object(wf, 'capture', side_effect=AssertionError('must not execute native')):
            with self.assertRaisesRegex(ValueError, 'unavailable'):
                self.return_capture(packet)
        packet = self.packet(self.capture(preserve_artifacts=[str(artifact)]))
        artifact.write_text('overwritten evidence', encoding='utf-8')
        with patch.object(wf, 'capture', side_effect=AssertionError('must not execute native')):
            with self.assertRaisesRegex(ValueError, 'artifact'):
                self.return_capture(packet)

    def test_capture_return_refuses_scope_or_source_changes_during_capture_without_retry(self):
        packet = self.packet()
        self.change()
        original_capture = wf.capture
        for change in ('source', 'scope'):
            with self.subTest(change=change):
                def race(*args, **kwargs):
                    value = original_capture(*args, **kwargs)
                    if change == 'source':
                        with (self.root / 'src/editor.py').open('a', encoding='utf-8') as out:
                            out.write('race = True\n')
                    else:
                        (self.root / 'src/late.py').write_text('late consumer\n', encoding='utf-8')
                    return value
                with patch.object(wf, 'capture', side_effect=race) as call:
                    with self.assertRaisesRegex(ValueError, 'changed during return capture'):
                        self.return_capture(packet)
                    self.assertEqual(call.call_count, 1)

    def test_capture_return_cli_derives_actual_files_and_preserves_original_output(self):
        packet = self.packet()
        packet_path, output = self.home / 'task.json', self.home / 'actual.json'
        wf.write_new(packet_path, packet)
        self.change()
        command = [sys.executable, str(ROOT / 'project-wiki/scripts/workflow.py'), 'capture-return',
                   '--packet', str(packet_path), '--native-argv', json.dumps([sys.executable, 'native.py']),
                   '--allow-native-execution', '--output', str(output)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        value = json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(value['files'], ['src/editor.py'])
        before = output.read_bytes()
        again = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(again.returncode, 0)
        self.assertEqual(output.read_bytes(), before)

    def test_manual_empty_implementation_return_still_fails_existing_coverage_gate(self):
        packet = self.packet()
        self.change()
        after = wf.capture(self.root, 'editor task', [], [sys.executable, 'native.py'],
                           ['native.py'], allow_execution=True)
        result = wf.finish(packet, after, self.review())
        self.assertFalse(result['structural_reconciliation'])
        self.assertIn('actual diff is not completely covered by the final native impact query', result['issues'])


class NativeSourceContextTests(unittest.TestCase):
    setUp = WorkflowTests.setUp
    capture = WorkflowTests.capture
    packet = WorkflowTests.packet
    review = WorkflowTests.review
    pointer = '/workflow/context/sources'

    def test_capture_return_preserves_strict_peer_selection_instead_of_using_ambient_default(self):
        peer = self.peer()
        # Real selector changes are ambient input, not permission to replace the reviewed native program.
        (self.root / 'native.py').write_text(
            NATIVE.replace('import json,sys', 'import json,sys,os').replace(
                "'placementIssues':[]", "'workflow':{'context':{'sources':json.loads(os.environ['WF_TEST_SOURCES'])}}, 'placementIssues':[]"),
            encoding='utf-8')
        selected = json.dumps({'server': self.identity(), 'selected-client': self.identity(peer)})
        with patch.dict(os.environ, {'WF_TEST_SOURCES': selected}):
            captured = self.capture(peers={'client': str(peer)}, native_source_context=self.pointer)
            packet = self.packet(captured)
            (peer / 'client.py').write_text('changed consumer\n', encoding='utf-8')
            after = wf.capture_return(packet, [sys.executable, 'native.py'], allow_execution=True)
        self.assertEqual(after['native_source_context'], self.pointer)
        self.assertEqual(after['native_source_comparison']['status'], 'matched')
        self.assertIn('client/client.py', after['files'])
        damaged = copy.deepcopy(packet)
        damaged['context'].pop('native_source_comparison')
        with patch.object(wf, 'capture', side_effect=AssertionError('no native execution')):
            with self.assertRaisesRegex(ValueError, 'comparison'):
                wf.capture_return(damaged, [sys.executable, 'native.py'], allow_execution=True)
        wrong = json.dumps({'server': self.identity(), 'wrong-default': self.identity()})
        with patch.dict(os.environ, {'WF_TEST_SOURCES': wrong}):
            with self.assertRaisesRegex(ValueError, 'does not match'):
                wf.capture_return(packet, [sys.executable, 'native.py'], allow_execution=True)

    def observe(self, rows):
        workflow = {'context': {'sources': rows}}
        (self.root / 'native.py').write_text(
            NATIVE.replace("'placementIssues':[]", "'workflow':" + repr(workflow) + ", 'placementIssues':[]"),
            encoding='utf-8')

    def identity(self, root=None):
        root = root or self.root
        return {'root': str(root), 'revision': git(root, 'rev-parse', 'HEAD')}

    def peer(self):
        peer = self.home / 'peer'
        peer.mkdir()
        git(peer, 'init')
        git(peer, 'config', 'user.name', 'Fixture')
        git(peer, 'config', 'user.email', 'fixture@example.invalid')
        (peer / 'client.py').write_text('value = 1\n', encoding='utf-8')
        git(peer, 'add', 'client.py')
        git(peer, 'commit', '-m', 'peer baseline')
        return peer

    def test_matching_arbitrary_native_labels_are_bound_and_visible_in_all_views(self):
        peer = self.peer()
        self.observe({'server-snapshot': self.identity(), 'reader-selected-client': self.identity(peer)})
        captured = self.capture(peers={'client': str(peer)}, native_source_context=self.pointer)
        packet = self.packet(captured)
        expected = captured['native_source_comparison']
        self.assertEqual(expected['status'], 'matched')
        self.assertEqual(expected['checkouts']['peer:client']['head'], git(peer, 'rev-parse', 'HEAD'))
        for view, path in [('index', None), ('all', None), ('feature', 'feature.md'), ('impact', 'src/editor.py')]:
            self.assertEqual(wf.task_view(packet, view, path)['native_source_comparison'], expected)
        child = wf.delegate(packet, 'reviewer', 'child', [], read_only=True)
        self.assertEqual(wf.task_view(child, 'index')['native_source_comparison'], expected)
        self.assertEqual(captured['evidence']['agent_use'], 'unverified')

    def test_wrong_native_peer_selection_rejects_even_when_declared_peer_hashes_are_current(self):
        peer = self.peer()
        self.observe({'main': self.identity(), 'ambient-client': self.identity(self.root)})
        # Existing capture semantics remain backward compatible and visibly unverified.
        old_style = self.capture(peers={'client': str(peer)})
        self.assertEqual(old_style['native_source_comparison']['status'], 'not_requested')
        with self.assertRaisesRegex(ValueError, 'does not match'):
            self.capture(peers={'client': str(peer)}, native_source_context=self.pointer)

    def test_same_checkout_but_old_revision_is_not_a_matching_source(self):
        observed = self.identity()
        observed['revision'] = '0' * 40
        self.observe({'native-root': observed})
        with self.assertRaisesRegex(ValueError, 'does not match'):
            self.capture(native_source_context=self.pointer)

    def test_unrelated_optional_native_source_cannot_block_selected_root(self):
        self.observe({'selected-project': self.identity(),
                      'malformed-optional': {'root': 'unselected\x00path', 'revision': None},
                      'unselected-client': {'root': str(self.home / 'not-selected'), 'revision': None}})
        captured = self.capture(native_source_context=self.pointer)
        self.assertEqual(captured['native_source_comparison']['status'], 'matched')
        self.assertEqual(set(captured['native_source_comparison']['checkouts']), {'root'})

    def test_json_pointer_accepts_arrays_and_escaped_object_keys(self):
        rows = {'selected': self.identity()}
        for report, pointer in [({'runs': [{'sources': rows}]}, '/runs/0/sources'),
                                ({'a/b': {'~sources': rows}}, '/a~1b/~0sources')]:
            with self.subTest(pointer=pointer):
                result = wf.compare_native_sources(report, pointer, self.root,
                                                    self.identity()['revision'], {})
                self.assertEqual(result['status'], 'matched')
        for pointer in ['/runs/1/sources', '/runs/-1/sources', '/runs/00/sources',
                        '/runs/-/sources', '/runs/x/sources', '/a~2b/~0sources', '/a~/~0sources']:
            with self.subTest(pointer=pointer), self.assertRaises(ValueError):
                wf.compare_native_sources({'runs': [{'sources': rows}], 'a~2b': {'~sources': rows}},
                                           pointer, self.root, self.identity()['revision'], {})

    def test_strict_capture_missing_comparison_is_rejected_and_never_displayed_as_legacy(self):
        self.observe({'project': self.identity()})
        captured = self.capture(native_source_context=self.pointer)
        packet = self.packet(captured)
        del captured['native_source_comparison']
        with self.assertRaisesRegex(ValueError, 'comparison is missing'):
            self.packet(captured)
        packet['context'] = captured
        shown = wf.task_view(packet, 'index')
        self.assertEqual(shown['native_source_comparison']['status'], 'unavailable')
        self.assertIn('historical', shown['freshness'])
        legacy = self.capture()
        legacy.pop('native_source_comparison')
        legacy.pop('native_source_context')
        self.assertEqual(wf.task_view(self.packet(legacy), 'index')['native_source_comparison']['status'],
                         'not_requested')

    def test_final_receipt_retains_strict_and_legacy_source_comparison(self):
        self.observe({'project': self.identity()})
        for pointer in [self.pointer, None]:
            with self.subTest(pointer=pointer):
                captured = self.capture(native_source_context=pointer)
                result = wf.finish(self.packet(captured), captured, self.review())
                self.assertEqual(result['native_source_context'], pointer)
                self.assertEqual(result['native_source_comparison'], captured['native_source_comparison'])

    def test_unavailable_and_conflicting_native_identity_are_not_empty_success(self):
        for revision in [None, '']:
            with self.subTest(revision=revision):
                self.observe({'root': {'root': str(self.root), 'revision': revision}})
                with self.assertRaisesRegex(ValueError, 'unavailable or malformed'):
                    self.capture(native_source_context=self.pointer)
        self.observe({'one': self.identity(), 'two': {'root': str(self.root), 'revision': '0' * 40}})
        with self.assertRaisesRegex(ValueError, 'disagree'):
            self.capture(native_source_context=self.pointer)

    def test_root_named_peer_cannot_override_required_primary_checkout(self):
        peer = self.peer()
        self.observe({'client': self.identity(peer)})
        with self.assertRaisesRegex(ValueError, 'does not match'):
            self.capture(peers={'root': str(peer)}, native_source_context=self.pointer)

    def test_missing_metadata_and_bad_pointer_remain_explicit(self):
        with self.assertRaisesRegex(ValueError, 'unavailable'):
            self.capture(native_source_context=self.pointer)
        for pointer in ['', 'workflow/context/sources']:
            with self.subTest(pointer=pointer), self.assertRaisesRegex(ValueError, 'JSON pointer'):
                self.capture(native_source_context=pointer)

    def test_saved_comparison_is_rechecked_and_cannot_be_silently_dropped_at_finish(self):
        self.observe({'project': self.identity()})
        captured = self.capture(native_source_context=self.pointer)
        altered = copy.deepcopy(captured)
        altered['native_source_comparison']['status'] = 'verified-reading'
        with self.assertRaisesRegex(ValueError, 'changed after capture'):
            self.packet(altered)
        packet = self.packet(captured)
        unchecked_after = self.capture()
        with self.assertRaisesRegex(ValueError, 'policy differs'):
            wf.finish(packet, unchecked_after, self.review())

    def test_actual_cli_passes_the_declared_source_context_to_capture(self):
        self.observe({'project': self.identity()})
        target = self.home / 'strict-capture.json'
        cp = subprocess.run([sys.executable, str(ROOT / 'project-wiki/scripts/workflow.py'), 'capture',
                             '--root', str(self.root), '--query', 'editor task', '--files', 'src/editor.py',
                             '--native-argv', json.dumps([sys.executable, 'native.py']), '--runtime-input', 'native.py',
                             '--allow-native-execution', '--native-source-context', self.pointer, '--output', str(target)],
                            text=True, capture_output=True)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertEqual(json.loads(target.read_text(encoding='utf-8'))['native_source_comparison']['status'], 'matched')


class PreservedEvidenceTests(unittest.TestCase):
    """Explicit private evidence is separate from the repository edit scope."""

    def setUp(self):
        WorkflowTests.setUp(self)
        # Hosted Windows TEMP may use a short-name/aliased parent. Select its
        # real path; the production policy deliberately rejects path aliases.
        self.home = self.home.resolve(strict=True)
        self.artifact = self.home / 'original-result.json'
        self.artifact.write_text('{"result":"FAIL"}\n', encoding='utf-8')

    def capture(self, **kw):
        return wf.capture(self.root, 'editor task', [], [sys.executable, 'native.py'],
                          ['native.py'], allow_execution=True, **kw)

    def packet(self, captured):
        return wf.start(captured, 'evidence-review', 'root', 'Preserve original evidence', [],
                        ['Original evidence remains inspectable'], ['preserve evidence'], read_only=True)

    def review(self):
        return {'pages': {}, 'capabilities': {'preserve evidence': {
            'status': 'gap', 'reason': 'Hash observations do not establish semantics or business acceptance'}},
            'handoff': {'remaining': ['Actual implementation/runtime'], 'next_safe_action': 'Continue scoped work'}}

    def guarded(self):
        return self.capture(preserve_artifacts=[str(self.artifact)])

    def test_cli_missing_second_selection_has_private_ordinal(self):
        target = self.home / 'refused-capture.json'
        missing = self.home / 'private-missing-evidence.json'
        with self.assertRaises(ValueError) as raised:
            wf.artifact_snapshot([str(self.artifact), str(missing)])
        self.assertIsInstance(raised.exception.__cause__, FileNotFoundError)
        self.assertIn(str(missing), str(raised.exception.__cause__))
        cp = subprocess.run([sys.executable, str(ROOT / 'project-wiki/scripts/workflow.py'), 'capture',
                             '--root', str(self.root), '--query', 'editor task', '--native-argv',
                             json.dumps([sys.executable, 'native.py']), '--runtime-input', 'native.py',
                             '--preserve-artifact', str(self.artifact), '--preserve-artifact', str(missing),
                             '--allow-native-execution', '--output', str(target)], text=True, capture_output=True)
        self.assertEqual(cp.returncode, 1)
        self.assertEqual(json.loads(cp.stdout), {
            'ok': False, 'error': 'Selected artifact is missing or unreadable (selection item 2)',
            'completion': 'not established'})
        self.assertFalse(target.exists())
        for private in (str(self.home), missing.name, self.artifact.read_text(encoding='utf-8')):
            self.assertNotIn(private, cp.stdout + cp.stderr)
        self.assertEqual(cp.stderr, '')

    def test_item_ordinal_uses_current_list_not_original_cli_position(self):
        earlier = self.home / 'aaa-evidence'
        earlier.write_bytes(b'private contents')
        paths = [str(self.artifact), str(earlier)]
        saved = wf.artifact_snapshot(paths)
        self.assertEqual(list(saved), sorted(paths))
        self.artifact.unlink()
        with self.assertRaisesRegex(ValueError, r'\(selection item 1\)$'):
            wf.artifact_snapshot(paths)
        with self.assertRaisesRegex(ValueError, r'\(selection item 2\)$'):
            wf.artifact_snapshot(list(saved))

    def test_item_refusals_keep_prefix_without_paths_or_os_error(self):
        for invalid, prefix in ((str(self.home), 'Preserved artifact must be an existing real file'),
                                ('private-relative', 'Preserved artifact must be an absolute real file, not an alias')):
            with self.subTest(kind=prefix), self.assertRaises(ValueError) as raised:
                wf.artifact_snapshot([str(self.artifact), invalid])
            self.assertEqual(str(raised.exception), prefix + ' (selection item 2)')
        with patch.object(wf, 'file_hash', side_effect=[wf.sha(b'first'), PermissionError(13, 'private OS details', str(self.artifact))]):
            with self.assertRaises(ValueError) as raised:
                wf.artifact_snapshot([str(self.artifact), str(self.artifact)])
        self.assertEqual(str(raised.exception), 'Selected artifact is missing or unreadable (selection item 2)')
        self.assertNotIn('private OS details', str(raised.exception))
        with self.assertRaisesRegex(ValueError, '^Preserved artifact selection must be a list of absolute file paths$'):
            wf.artifact_snapshot(['bad\0path'])

    @unittest.skipUnless(os.name == 'posix' and hasattr(os, 'geteuid') and os.geteuid() != 0,
                         'Real mode-bit unreadability requires a non-root POSIX process')
    def test_real_unreadable_second_file(self):
        unreadable = self.home / 'private-unreadable'
        unreadable.write_bytes(b'private contents')
        unreadable.chmod(0)
        try:
            with self.assertRaisesRegex(ValueError, r'^Selected artifact is missing or unreadable \(selection item 2\)$'):
                wf.artifact_snapshot([str(self.artifact), str(unreadable)])
        finally:
            unreadable.chmod(0o600)

    def test_legacy_unselected_files_are_explicitly_not_observed(self):
        captured = self.capture()
        result = wf.finish(self.packet(captured), self.capture(), self.review())
        self.assertEqual(result['artifact_preservation']['status'], 'not_requested')
        self.assertFalse(result['artifact_preservation']['write_prevention'])

    def test_unchanged_private_artifact_follows_delegation_views_and_finish(self):
        captured = self.guarded()
        packet = self.packet(captured)
        child = wf.delegate(packet, 'reader', 'child', [], read_only=True)
        for view in ('index', 'all'):
            record = wf.task_view(child, view)['artifact_preservation']
            self.assertEqual(record['paths'], [str(self.artifact.resolve())])
            self.assertEqual(record['captured_sha256'], captured['preserved_artifact_hashes'])
        result = wf.finish(child, self.guarded(), self.review())
        self.assertTrue(result['structural_reconciliation'], result['issues'])
        self.assertEqual(result['actual_files'], [])
        self.assertEqual(result['artifact_preservation']['status'], 'unchanged_at_finish')
        self.assertEqual(result['capability_gaps'], ['preserve evidence'])

    def test_overwritten_private_artifact_cannot_silently_return_as_unchanged_git(self):
        captured = self.guarded()
        packet = self.packet(captured)
        self.artifact.write_text('{"result":"PASS"}\n', encoding='utf-8')
        self.assertEqual(wf.changed_files(self.root, packet['base_sha'], captured['baseline_untracked']), [])
        with self.assertRaisesRegex(ValueError, 'artifact'):
            wf.start(captured, 'other', 'root', 'New work', [], ['Check'], ['Result'], read_only=True)
        with self.assertRaisesRegex(ValueError, 'artifact'):
            wf.delegate(packet, 'reader', 'child', [], read_only=True)
        self.assertIn('historical', wf.task_view(packet)['freshness'])
        after = self.guarded()
        for operation in (wf.review_template, lambda p, a: wf.finish(p, a, self.review())):
            with self.assertRaisesRegex(ValueError, 'artifact'):
                operation(packet, after)

    def test_selected_policy_cannot_be_dropped_expanded_or_replaced_at_return(self):
        packet = self.packet(self.guarded())
        other = self.home / 'other-result.json'
        other.write_bytes(self.artifact.read_bytes())
        for paths in ([], [str(other)], [str(self.artifact), str(other)]):
            after = self.capture(preserve_artifacts=paths)
            for operation in (wf.review_template, lambda p, a: wf.finish(p, a, self.review())):
                with self.assertRaisesRegex(ValueError, 'artifact'):
                    operation(packet, after)

    def test_missing_or_invalid_saved_hash_record_is_not_a_legacy_capture(self):
        original = self.guarded()
        for bad in ({}, {str(self.artifact): None}, {str(self.artifact): 'not-a-sha256'}):
            captured = copy.deepcopy(original)
            captured['preserved_artifact_hashes'] = bad
            with self.assertRaisesRegex(ValueError, 'artifact'):
                self.packet(captured)
        captured = copy.deepcopy(original)
        captured.pop('preserved_artifact_hashes')
        with self.assertRaisesRegex(ValueError, 'artifact'):
            self.packet(captured)

    def test_capture_detects_selected_artifact_changed_by_native_router(self):
        native = self.root / 'native.py'
        native.write_text('from pathlib import Path\nPath(' + repr(str(self.artifact)) +
                          ').write_text("changed by fixture")\n' + NATIVE, encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'artifact'):
            self.guarded()

    def test_missing_directory_relative_and_invalid_artifact_inputs_are_refused(self):
        for paths in ([str(self.home / 'missing')], [str(self.home)], ['relative.json'], ['bad\0path'], 'not-a-list'):
            with self.subTest(paths=paths), self.assertRaises(ValueError):
                self.capture(preserve_artifacts=paths)
        captured = self.guarded()
        self.artifact.unlink()
        with self.assertRaisesRegex(ValueError, 'artifact'):
            self.packet(captured)

    def test_exact_restoration_is_only_a_checkpoint_observation(self):
        original = self.artifact.read_bytes()
        packet = self.packet(self.guarded())
        self.artifact.write_text('intermediate change', encoding='utf-8')
        self.artifact.write_bytes(original)
        result = wf.finish(packet, self.guarded(), self.review())
        self.assertEqual(result['artifact_preservation']['status'], 'unchanged_at_finish')
        self.assertFalse(result['artifact_preservation']['continuous_monitoring'])
        self.assertFalse(result['artifact_preservation']['write_prevention'])

    def test_legitimate_source_diff_is_not_confused_with_private_evidence_mutation(self):
        captured = wf.capture(self.root, 'editor task', ['src/editor.py'], [sys.executable, 'native.py'],
                              ['native.py'], allow_execution=True, preserve_artifacts=[str(self.artifact)])
        packet = WorkflowTests.packet(self, captured)
        WorkflowTests.change(self)
        after = wf.capture(self.root, 'editor task', ['src/editor.py'], [sys.executable, 'native.py'],
                           ['native.py'], allow_execution=True, preserve_artifacts=[str(self.artifact)])
        result = wf.finish(packet, after, WorkflowTests.review(self))
        self.assertTrue(result['structural_reconciliation'], result['issues'])
        self.assertEqual(result['actual_files'], ['src/editor.py'])
        self.assertEqual(result['artifact_preservation']['status'], 'unchanged_at_finish')

    def test_cli_carries_selection_and_does_not_copy_artifact_contents(self):
        target = self.home / 'guarded-capture.json'
        cp = subprocess.run([sys.executable, str(ROOT / 'project-wiki/scripts/workflow.py'), 'capture',
                             '--root', str(self.root), '--query', 'editor task', '--native-argv',
                             json.dumps([sys.executable, 'native.py']), '--runtime-input', 'native.py',
                             '--preserve-artifact', str(self.artifact), '--allow-native-execution',
                             '--output', str(target)], text=True, capture_output=True)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        result = json.loads(target.read_text(encoding='utf-8'))
        self.assertEqual(result['preserve_artifacts'], [str(self.artifact.resolve())])
        self.assertNotIn('"result":"FAIL"', target.read_text(encoding='utf-8'))

    def test_saved_selected_record_missing_in_view_is_unavailable_not_a_verified_legacy(self):
        packet = self.packet(self.guarded())
        packet['context'].pop('preserved_artifact_hashes')
        result = wf.task_view(packet)
        self.assertEqual(result['artifact_preservation']['status'], 'unavailable')
        self.assertIn('historical', result['freshness'])

    def test_cli_never_uses_a_selected_existing_artifact_as_its_new_output(self):
        original = self.artifact.read_bytes()
        cp = subprocess.run([sys.executable, str(ROOT / 'project-wiki/scripts/workflow.py'), 'capture',
                             '--root', str(self.root), '--query', 'editor task', '--native-argv',
                             json.dumps([sys.executable, 'native.py']), '--runtime-input', 'native.py',
                             '--preserve-artifact', str(self.artifact), '--allow-native-execution',
                             '--output', str(self.artifact)], text=True, capture_output=True)
        self.assertEqual(cp.returncode, 1)
        self.assertEqual(self.artifact.read_bytes(), original)

    def test_symlink_file_and_parent_alias_are_not_preserved_as_real_paths(self):
        link = self.home / 'evidence-alias'
        parent = self.home / 'parent-alias'
        real = self.home / 'real'
        real.mkdir()
        (real / 'result').write_bytes(b'original')
        try:
            link.symlink_to(self.artifact)
            parent.symlink_to(real, target_is_directory=True)
        except OSError as error:
            self.skipTest('This host cannot create symlinks: ' + type(error).__name__)
        for path in (link, parent / 'result'):
            with self.assertRaisesRegex(ValueError, r'Preserved artifact.*\(selection item 2\)$') as raised:
                self.capture(preserve_artifacts=[str(self.artifact), str(path)])
            self.assertNotIn(str(self.home), str(raised.exception))


if __name__=='__main__':
    unittest.main()
