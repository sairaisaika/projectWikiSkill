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

    def test_real_cli_start_readonly_does_not_require_a_dummy_allowed_file(self):
        capture=self.home/'capture.json';wf.write_new(capture,self.capture())
        packet=self.home/'task.json'
        completed=subprocess.run([sys.executable,str(ROOT/'project-wiki/scripts/workflow.py'),'start',
            '--capture',str(capture),'--task-id','review-cli','--owner','reviewer','--outcome','interpret source',
            '--acceptance','inspectable result','--capability','interpret facts','--read-only','--output',str(packet)],
            text=True,capture_output=True)
        self.assertEqual(completed.returncode,0,completed.stdout+completed.stderr)
        self.assertEqual(json.loads(packet.read_text(encoding='utf-8'))['allowed_files'],[])


if __name__=='__main__':
    unittest.main()
