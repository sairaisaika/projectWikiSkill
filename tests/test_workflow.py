"""Native projections preserve scope and reject false structural closure."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

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


class NativeSourceContextTests(unittest.TestCase):
    setUp = WorkflowTests.setUp
    capture = WorkflowTests.capture
    packet = WorkflowTests.packet
    review = WorkflowTests.review
    pointer = '/workflow/context/sources'

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


if __name__=='__main__':
    unittest.main()
