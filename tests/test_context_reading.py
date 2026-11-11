"""Usable context delivery without another gate or implicit native execution."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('context_workflow', ROOT/'project-wiki/scripts/workflow.py')
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)

NATIVE = '''import json,sys
q=sys.argv[1]; files=sys.argv[sys.argv.index('--files')+1:]
print(json.dumps({'query':q,'cards':[] if q=='unknown' else [{'path':'feature.md','title':'Editor'}],
 'impact':[{'file':f,'pages':[{'path':'feature.md','title':'Editor'},{'path':'consumer.md','title':'Reader'}], 'unregistered':False} for f in files],
 'omitted':[{'path':'unexpanded.md','title':'Not yet read'}], 'placementIssues':[], 'limits':'registered scope only'}))
'''
PAGE = '''# Feature
> 核验：2026-11-06 · abc1234 工作树，未部署｜2026-10-01 · def5678 旧记录

## Current state
Source behavior reviewed; runtime acceptance unknown.

## Mechanism
One writer serves the reader.

## History
An older not deployed claim retained for provenance.
'''

class ContextReadingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'repo'; self.root.mkdir()
        (self.root/'docs/wiki').mkdir(parents=True); (self.root/'src').mkdir()
        for name,text in [('feature',PAGE),('consumer','# Reader\n'),('unexpanded','# Candidate\n')]:
            (self.root/f'docs/wiki/{name}.md').write_text(text,encoding='utf-8')
        (self.root/'native.py').write_text(NATIVE,encoding='utf-8')
        (self.root/'src/editor.py').write_text('title = None\n',encoding='utf-8')
        self.git('init'); self.git('config','user.name','Fixture'); self.git('config','user.email','fixture@example.invalid')
        self.git('add','.'); self.git('commit','-m','baseline')
    def git(self,*args):
        return subprocess.check_output(['git','-C',str(self.root),*args],stderr=subprocess.PIPE).decode().strip()
    def prepare(self,files=None,query='editor',**kw):
        return wf.prepare(self.root,query,files or ['src/editor.py'],[sys.executable,'native.py'],['native.py'],allow_execution=True,**kw)
    def view(self,value,view='summary',path=None,**kw):
        return wf.capture_view(value,view,path,**kw)
    def test_index_places_omissions_before_long_metadata(self):
        c=wf.capture(self.root,'editor',['src/editor.py'],[sys.executable,'native.py'],['native.py'],allow_execution=True)
        p=wf.start(c,'task','owner','edit',['src/editor.py'],['source evidence'],['title'])
        v=wf.task_view(p,'index')
        self.assertEqual(next(iter(v)),'native_index')
        self.assertEqual(next(iter(v['native_index'])),'omitted_candidates')
    def test_prepare_has_no_packet_ceremony_and_keeps_every_owner(self):
        c=self.prepare();v=self.view(c)
        self.assertEqual(c['kind'],'native-wiki-capture')
        self.assertEqual(v['files'][0]['pages'],['feature.md','consumer.md'])
        self.assertEqual(v['unexpanded_candidates'][0]['path'],'unexpanded.md')
        self.assertEqual(v['preparation']['selected_paths_with_changes'],[])
        self.assertEqual(c['evidence']['agent_use'],'unverified')
        self.assertEqual(v['path_bases']['wiki_root'],'docs/wiki')
        self.assertEqual(Path(v['path_bases']['source_root']),self.root.resolve())
    def test_unknown_query_still_delivers_file_context(self):
        v=self.view(self.prepare(query='unknown'))
        self.assertEqual(v['files'][0]['file'],'src/editor.py')
        self.assertEqual(len(v['files'][0]['pages']),2)
    def test_existing_changes_cannot_be_reported_as_pre_edit_reading(self):
        (self.root/'src/editor.py').write_text('title = "changed"\n')
        (self.root/'src/new.py').write_text('new = True\n')
        v=self.view(self.prepare(['src/editor.py','src/new.py']))
        self.assertEqual(v['preparation']['selected_paths_with_changes'],['src/editor.py','src/new.py'])
        self.assertEqual(v['preparation']['reading_before_edits'],'not established')
    def test_page_default_separates_history_without_promoting_claims(self):
        c=self.prepare(observed_revisions={'deployed':'HEAD'})
        p=self.view(c,'page','feature.md')
        self.assertIn('One writer',p['body_markdown'])
        self.assertNotIn('An older not deployed',p['body_markdown'])
        self.assertIn('runtime acceptance unknown',p['authored_current_state'])
        self.assertIn('未部署',p['latest_verification_note']['text'])
        self.assertEqual(p['currentness'],'authored claims; not independently verified')
        h=self.view(c,'history','feature.md')
        self.assertIn('An older not deployed',h['history_markdown'])
        self.assertIn('旧记录',h['historical_verification_notes'][0]['text'])
    def test_absent_current_section_is_unknown_not_latest_stamp(self):
        (self.root/'docs/wiki/feature.md').write_text('# F\n> Reviewed: 2020-01-01 old not deployed\n',encoding='utf-8')
        p=self.view(self.prepare(),'page','feature.md')
        self.assertIsNone(p['authored_current_state'])
        self.assertIn('not independently verified',p['currentness'])
    def test_snapshot_page_does_not_read_git_or_live_pages(self):
        c=self.prepare()
        (self.root/'docs/wiki/feature.md').unlink()
        with patch.object(wf,'git',side_effect=AssertionError('must not invoke Git')):
            p=self.view(c,'page','feature.md',snapshot_only=True)
        self.assertIn('One writer',p['body_markdown'])
        self.assertFalse(p['current_inputs_checked'])
    def test_selected_source_change_is_reported_as_historical(self):
        c=self.prepare();(self.root/'src/editor.py').write_text('changed = True\n')
        self.assertFalse(self.view(c)['current_inputs_checked'])
        self.assertIn('historical',self.view(c)['freshness'])
    def test_history_named_product_feature_is_not_hidden_as_evidence(self):
        text='# History editor\n## Version history behavior\nCurrent feature detail.\n'
        (self.root/'docs/wiki/feature.md').write_text(text)
        p=self.view(self.prepare(),'page','feature.md')
        self.assertIn('Current feature detail',p['body_markdown'])
        self.assertEqual(p['history_markdown'],'')
    def test_page_budget_delivers_explicit_partial_body_and_continuation(self):
        c=self.prepare();p=self.view(c,'page','feature.md')
        p['body_markdown']+='x'*9000
        text=wf.reading_module().render_page(p,'context.json',budget=1000)
        self.assertIn('PARTIAL',text);self.assertIn('--cursor',text)
        self.assertLessEqual(len(text.encode('utf-8')),1000)
    def test_section_expansion_ignores_code_block_headings(self):
        text='## Mechanism\nExample:\n```markdown\n## Mechanism\n# fake end\n```\nActual detail.\n## Other\nOutside.\n'
        selected=wf.reading_module().select_section(text,'Mechanism')
        self.assertIn('Actual detail',selected);self.assertNotIn('Outside',selected)
    def test_projection_does_not_treat_fenced_history_as_real_history(self):
        p=wf.reading_module().page_projection('# F\n````markdown\n```\n## History\nExample only.\n````\n## Mechanism\nReal body.\n')
        self.assertEqual(p['history_markdown'],'')
        self.assertIn('Real body',p['body_markdown'])
        self.assertEqual([x['title'] for x in p['section_index']],['F','Mechanism'])
    def test_selected_section_is_not_blocked_by_large_state_metadata(self):
        p=self.view(self.prepare(),'page','feature.md')
        p['authored_current_state']='x'*9000
        text=wf.reading_module().render_page(p,'context.json',section='Mechanism',budget=1000)
        self.assertIn('One writer serves',text);self.assertNotIn('not delivered',text)
    def test_impact_mismatch_names_missing_extra_and_counts(self):
        c=self.prepare();r=copy.deepcopy(c['native_report']);r['impact'][0]['file']='src/wrong.py'
        with self.assertRaisesRegex(ValueError,'requested=1, returned=1.*editor.py.*wrong.py'):
            wf.validate_native(r,'editor',['src/editor.py'],self.root,'docs/wiki')
    def test_live_stale_view_is_historical(self):
        c=self.prepare();(self.root/'docs/wiki/feature.md').write_text('# changed\n')
        v=self.view(c)
        self.assertFalse(v['current_inputs_checked']);self.assertIn('historical',v['freshness'])
    def test_saved_page_tamper_is_rejected(self):
        c=self.prepare();c['prepared_reading']['pages']['feature.md']['body_markdown']='forged'
        with self.assertRaisesRegex(ValueError,'reading.*changed'):self.view(c,snapshot_only=True)
    def test_large_summary_is_explicitly_partial_with_continuation(self):
        v=self.view(self.prepare())
        v['files']=[{'file':f'src/item{i}.py','pages':['feature.md'],'unregistered':False} for i in range(1000)]
        text=wf.render_context_summary(v,'saved-context.json',budget=700)
        self.assertIn('PARTIAL',text);self.assertIn('--cursor',text)
        self.assertIn('saved-context.json',text)
        self.assertLessEqual(len(text.encode('utf-8')),700)
    def test_unregistered_input_is_visible_in_complete_index(self):
        native=(self.root/'native.py').read_text()
        native=native.replace("'pages':[{'path'", "'pages':[] if f=='src/unknown.py' else [{'path'",1)
        native=native.replace("'unregistered':False", "'unregistered':f=='src/unknown.py'",1)
        (self.root/'native.py').write_text(native)
        v=self.view(self.prepare(['src/editor.py','src/unknown.py']))
        self.assertEqual(v['unregistered_files'],['src/unknown.py'])
        self.assertEqual(len(v['files']),2)
    def test_saved_context_budget_refuses_instead_of_writing_unreadable_capture(self):
        captured=wf.capture(self.root,'editor',['src/editor.py'],[sys.executable,'native.py'],['native.py'],allow_execution=True)
        with patch.object(wf,'capture',return_value=captured), patch.object(wf,'MAX_REPORT',100):
            with self.assertRaisesRegex(ValueError,'saved-artifact budget'):
                self.prepare()
    def test_observed_revision_does_not_promote_old_deployment_claim(self):
        c=self.prepare(observed_revisions={'deployed':'HEAD'})
        text=wf.render_context_summary(self.view(c),'context.json')
        self.assertIn('CALLER-DECLARED',text)
        self.assertIn('未部署',self.view(c,'page','feature.md')['latest_verification_note']['text'])
    def test_prepare_refuses_implicit_execution_with_or_without_files(self):
        for files in ([],['src/editor.py']):
            with self.subTest(files=files),patch.object(wf.subprocess,'run',side_effect=AssertionError('native ran')):
                with self.assertRaisesRegex(ValueError,'opt-in'):wf.prepare(self.root,'editor',files,[sys.executable,'native.py'],['native.py'])
                with self.assertRaisesRegex(ValueError,'runtime-input'):wf.prepare(self.root,'editor',files,[sys.executable,'native.py'],[],allow_execution=True)
    def test_capture_help_explains_prefix_and_automatic_arguments(self):
        cp=subprocess.run([sys.executable,str(ROOT/'project-wiki/scripts/workflow.py'),'capture','--help'],text=True,capture_output=True)
        self.assertEqual(cp.returncode,0);self.assertIn('prefix',cp.stdout);self.assertIn('--json',cp.stdout)
    def test_prepare_cli_writes_new_context_and_prints_compact_scope(self):
        out=Path(self.tmp.name)/'context.json'
        args=[sys.executable,str(ROOT/'project-wiki/scripts/workflow.py'),'prepare','--root',str(self.root),'--query','editor','--files','src/editor.py','--runtime-input','native.py','--native-argv',json.dumps([sys.executable,'native.py']),'--allow-native-execution','--output',str(out)]
        cp=subprocess.run(args,text=True,capture_output=True);self.assertEqual(cp.returncode,0,cp.stdout+cp.stderr)
        self.assertIn('UNEXPANDED',cp.stdout);self.assertIn('src/editor.py',cp.stdout)
        self.assertNotIn('native_report_canonical_sha256',cp.stdout)
        before=out.read_bytes();cp=subprocess.run(args,text=True,capture_output=True)
        self.assertEqual(cp.returncode,0);self.assertIn('REUSED',cp.stdout);self.assertEqual(out.read_bytes(),before)
    def test_native_manifest_absence_has_actionable_nonmutating_result(self):
        (self.root/'docs/wiki/INDEX.md').write_text('# Native index\n')
        cp=subprocess.run([sys.executable,str(ROOT/'project-wiki/scripts/wiki.py'),'audit','--root',str(self.root)],text=True,capture_output=True)
        self.assertEqual(cp.returncode,2)
        r=json.loads(cp.stdout);self.assertEqual(r['error_code'],'helper_manifest_missing')
        self.assertIn('prepare',r['next_step']);self.assertFalse((self.root/'docs/wiki/routes.json').exists())
    def test_corrupt_manifest_is_still_an_error_not_native_adoption(self):
        (self.root/'docs/wiki/routes.json').write_text('{broken')
        cp=subprocess.run([sys.executable,str(ROOT/'project-wiki/scripts/wiki.py'),'audit','--root',str(self.root)],text=True,capture_output=True)
        self.assertEqual(cp.returncode,1);self.assertFalse(json.loads(cp.stdout)['valid'])


    def unregistered_router(self):
        (self.root/'native.py').write_text("import json,sys\nq=sys.argv[1];fs=sys.argv[sys.argv.index('--files')+1:]\nprint(json.dumps({'query':q,'cards':[],'impact':[{'file':f,'pages':[],'unregistered':True} for f in fs],'omitted':[],'placementIssues':[],'limits':'registered scope only'}))\n",encoding='utf-8')
    def test_explicit_wiki_selection_is_readable_without_inventing_ownership(self):
        self.unregistered_router()
        (self.root/'docs/wiki/selected.md').write_text('# Selected\n## Current state\nCandidate only.\n## Mechanism\nThe selected document itself.\n',encoding='utf-8')
        c=self.prepare(['docs/wiki/selected.md'],query='unknown')
        v=self.view(c);p=self.view(c,'page','selected.md')
        self.assertEqual(v['unregistered_files'],['docs/wiki/selected.md'])
        self.assertEqual(v['files'][0]['pages'],[])
        self.assertIn('Candidate only.',p['authored_current_state'])
        self.assertIn('The selected document itself.',p['body_markdown'])
        self.assertEqual(v['selected_wiki_pages'],[{'file':'docs/wiki/selected.md','path':'selected.md','status':'captured'}])
        self.assertIn('not owner declarations',wf.render_context_summary(v,'saved.json'))
    def test_explicit_wiki_selection_deduplicates_an_existing_native_page(self):
        c=self.prepare(['src/editor.py','docs/wiki/feature.md'])
        self.assertEqual(list(c['prepared_reading']['pages']),['consumer.md','feature.md'])
        self.assertEqual(self.view(c)['selected_wiki_pages'][0]['path'],'feature.md')
    def test_missing_planned_wiki_page_is_explicit_and_is_not_created(self):
        self.unregistered_router();c=self.prepare(['docs/wiki/future.md'])
        self.assertEqual(self.view(c)['selected_wiki_pages'],[{'file':'docs/wiki/future.md','path':'future.md','status':'not present in Wiki snapshot'}])
        self.assertFalse((self.root/'docs/wiki/future.md').exists())
        with self.assertRaisesRegex(ValueError,'not present in.*snapshot'):self.view(c,'page','future.md')
    def test_directly_selected_page_can_be_read_after_source_disappears(self):
        self.unregistered_router();p=self.root/'docs/wiki/selected.md';p.write_text(PAGE,encoding='utf-8')
        c=self.prepare(['docs/wiki/selected.md']);p.unlink()
        with patch.object(wf,'git',side_effect=AssertionError('no live reads')):
            v=self.view(c,'page','selected.md',snapshot_only=True)
        self.assertIn('One writer serves',v['body_markdown']);self.assertFalse(v['current_inputs_checked'])
    def test_similarly_named_directory_is_not_a_selected_wiki_page(self):
        self.unregistered_router();p=self.root/'docs/wiki-other/private.md';p.parent.mkdir();p.write_text('# Outside\nnot Wiki content\n')
        c=self.prepare(['docs/wiki-other/private.md'])
        self.assertEqual(self.view(c)['selected_wiki_pages'],[])
        self.assertNotIn('not Wiki content',json.dumps(c))
    def test_explicit_pages_follow_the_configured_wiki_root(self):
        self.unregistered_router();wiki=self.root/'knowledge';wiki.mkdir();(wiki/'selected.md').write_text(PAGE,encoding='utf-8')
        c=self.prepare(['knowledge/selected.md'],wiki_root='knowledge')
        self.assertIn('One writer serves',self.view(c,'page','selected.md')['body_markdown'])
        self.assertEqual(self.view(c)['selected_wiki_pages'][0]['path'],'selected.md')
    def test_large_direct_page_continues_and_still_supports_selected_section(self):
        self.unregistered_router();(self.root/'docs/wiki/large.md').write_text('# Long\n## Large\n'+'x'*9000+'\n## Needed\nExact detail.\n',encoding='utf-8')
        c=self.prepare(['docs/wiki/large.md']);p=self.view(c,'page','large.md')
        full=wf.reading_module().render_page(p,'saved.json')
        self.assertIn('PARTIAL',full);self.assertIn('--cursor',full);self.assertLessEqual(len(full.encode('utf-8')),6000)
        self.assertIn('Exact detail',wf.reading_module().render_page(p,'saved.json',section='Needed'))
    def test_explicit_verification_history_headings_are_separated(self):
        for heading in ['核验历史','Verification history','Review history']:
            with self.subTest(heading=heading):
                p=wf.reading_module().page_projection('# F\n## Current state\nCandidate.\n## '+heading+'\nOld pending branch.\n## Mechanism\nNow.\n')
                self.assertNotIn('Old pending',p['body_markdown'])
                self.assertIn('Old pending',p['history_markdown'])
                self.assertNotIn('Old pending',p['authored_current_state'])

    def test_verification_note_inside_explicit_history_is_not_promoted_or_lost(self):
        p=wf.reading_module().page_projection('# F\n## Current state\nCandidate.\n## 核验历史\n> 核验：2020-01-01 old pending branch\n')
        self.assertIsNone(p['latest_verification_note'])
        self.assertIn('2020-01-01 old pending branch',p['history_markdown'])
        p['freshness']='snapshot'
        self.assertIn('2020-01-01 old pending branch',wf.reading_module().render_page(p,'saved.json',history=True))

    def test_summary_does_not_report_no_history_after_notes_move_to_history(self):
        (self.root/'docs/wiki/feature.md').write_text('# F\n## Current state\nCandidate.\n## 核验历史\n> 核验：2020-01-01 older review\n',encoding='utf-8')
        v=self.view(self.prepare());page=next(p for p in v['pages'] if p['path']=='feature.md')
        self.assertEqual(page['historical_notes'],0)
        self.assertTrue(page['history_present'])
        self.assertIn('history=present; older notes=0',wf.render_context_summary(v,'saved.json'))
    def test_missing_selected_page_error_names_actual_snapshot_gap(self):
        self.unregistered_router();c=self.prepare(['docs/wiki/future.md'])
        with self.assertRaisesRegex(ValueError,'not present in.*snapshot.*future.md'):
            self.view(c,'page','future.md')

if __name__=='__main__':unittest.main()


class DatedCurrentSectionTests(unittest.TestCase):
    def test_dated_localized_sections_are_authored_claims_with_visible_date(self):
        reading = wf.reading_module()
        for title in ['当前状态（2026-11-06）', '现状 (2026-11-06)', 'Current state (2026-11-06)', 'Current status（2026-11-06）']:
            with self.subTest(title=title):
                text = '# Release\n## '+title+'\nOld deployment claim.\n## Mechanism\nOne writer.\n'
                view = reading.page_projection(text)
                self.assertEqual(view['authored_current_state'], 'Old deployment claim.')
                view.update({'path':'release.md','freshness':'saved snapshot only'})
                shown = reading.render_page(view, 'saved.json')
                self.assertIn('Declared current section: '+title, shown)
                self.assertIn('not independently verified', shown)

    def test_dated_replacement_archives_old_title_and_does_not_keep_its_date_on_new_state(self):
        reading = wf.reading_module()
        old = '# Release\n## 当前状态（2026-11-06）\nOld deployment claim.\n## Mechanism\nOne writer.\n'
        new = reading.replace_current(old, 'New source evidence; runtime unknown.', '2026-11-07')
        self.assertEqual(reading.page_projection(new)['authored_current_state'], 'New source evidence; runtime unknown.')
        self.assertIn('## 当前状态\n', new)
        self.assertIn('## 当前状态（2026-11-06）\nOld deployment claim.', reading.page_projection(new)['history_markdown'])
        self.assertIn('## Mechanism\nOne writer.', new)
        self.assertEqual(reading.replace_current(new, 'New source evidence; runtime unknown.', 'later'), new)

    def test_qualified_nondate_headings_and_fenced_or_historical_dates_are_not_current(self):
        reading = wf.reading_module()
        for title in ['Current state (planned)', '当前验收位置（2026-11-06）', '历史当前状态（2026-11-06）']:
            self.assertIsNone(reading.page_projection('# Page\n## '+title+'\nclaim\n')['authored_current_state'])
        text = '# Page\n```markdown\n## 当前状态（2026-11-06）\nquoted\n```\n## History\n### Current state (2026-11-05)\nhistorical\n'
        self.assertIsNone(reading.page_projection(text)['authored_current_state'])


    def test_older_saved_unknown_projection_is_not_reinterpreted_by_new_reader(self):
        reading = wf.reading_module()
        text = '# Page\n## 当前状态（2026-11-06）\nOld claim.\n'
        old_view = reading.page_projection(text)
        old_view.update({'authored_current_state':None,'path':'page.md','freshness':'saved snapshot only'})
        shown = reading.render_page(old_view, 'old.json')
        self.assertNotIn('Declared current section:', shown)
        self.assertIn('Not declared; do not infer it', shown)
        self.assertEqual(reading.replace_current(text, 'Old claim.', 'later'), text)
        undated = reading.page_projection('# Page\n## Current state\nClaim.\n')
        undated.update({'path':'page.md','freshness':'saved snapshot only'})
        self.assertNotIn('Declared current section:', reading.render_page(undated, 'undated.json'))
