"""Saved state review must not require printing a page-sized plan or live source."""
import copy
import io
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
import test_context_reading as fixture
wf = fixture.wf


def plan_for(old, new):
    return {'schema_version':1,'kind':'wiki-current-state-update','root':'unavailable-root',
            'page':'docs/wiki/feature.md','wiki_root':'docs/wiki',
            'expected_sha256':wf.sha(old.encode('utf-8')),'original_markdown':old,
            'proposed_sha256':wf.sha(new.encode('utf-8')),'proposed_markdown':new,
            'changed':old!=new,'recorded_at':'recorded-only'}


def next_argv(text):
    tail = text[text.rindex('\n--- END CONTENT ---'):]
    if '\nNEXT: ' not in tail: return None
    cmd = tail.split('\nNEXT: ',1)[1].strip()
    return ([m.replace("''", "'") for m in re.findall(r"'((?:''|[^'])*)'",cmd)]
            if sys.platform=='win32' else shlex.split(cmd))


class StatePreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.path=self.root/'plan with spaces.json'
        self.plan=plan_for('# Page\nold\n','# Page\n'+('\U00010348\u591c\u9e6d\n'*2400))
        self.path.write_text(json.dumps(self.plan,ensure_ascii=False),encoding='utf-8')
    def cli(self,*args):
        out=io.StringIO()
        with redirect_stdout(out):code=wf.main(['show-state','--plan',str(self.path),*args])
        return code,out.getvalue()
    def test_saved_proposal_and_diff_are_exact_and_do_not_claim_application(self):
        for view in ['diff','proposed']:
            shown=wf.state_preview(self.plan,view)
            self.assertIn('application or deployment is not established',shown['limits'])
        self.assertEqual(wf.state_preview(self.plan,'proposed')['markdown'],self.plan['proposed_markdown'])
        diff=wf.state_preview(self.plan)['markdown']
        self.assertIn('-old\n',diff);self.assertIn('+'+self.plan['proposed_markdown'].splitlines()[1],diff)
    def test_large_cli_views_are_bounded_and_reconstruct_every_saved_character(self):
        for view in ['diff','proposed']:
            with self.subTest(view=view):
                args=[sys.executable,str(Path(wf.__file__).resolve()),'show-state','--plan',self.path.name,'--view',view]
                chunks=[]
                for _ in range(100):
                    cp=subprocess.run(args,cwd=self.root,capture_output=True,encoding='utf-8')
                    self.assertEqual(cp.returncode,0,cp.stdout+cp.stderr)
                    self.assertLessEqual(len(cp.stdout.encode('utf-8')),6000)
                    self.assertLessEqual(len(cp.stdout.splitlines()),60)
                    a=cp.stdout.index('--- CONTENT ---\n')+len('--- CONTENT ---\n');b=cp.stdout.rindex('\n--- END CONTENT ---')
                    chunks.append(cp.stdout[a:b]);args=next_argv(cp.stdout)
                    if args is None: self.assertIn('COMPLETE',cp.stdout);break
                    self.assertIn('--format',args);self.assertEqual(args[args.index('--view')+1],view)
                else:self.fail('saved state pagination never completed')
                shown=wf.state_preview(self.plan,view)
                self.assertEqual(''.join(chunks),'SAVED STATE PREVIEW — '+view+'\n'+shown['limits']+'\n\n'+shown['markdown'])
    def test_cursors_reject_cross_view_and_changed_saved_plan(self):
        code,text=self.cli();self.assertEqual(code,0)
        cursor=next_argv(text)[-1]
        with self.assertRaises(ValueError):
            wf.reading_module().text_page('other','other',[],cursor=cursor)
        with redirect_stdout(io.StringIO()):self.assertEqual(wf.main(['show-state','--plan',str(self.path),'--view','proposed','--cursor',cursor]),1)
        self.plan['proposed_markdown']+='changed\n';self.plan['proposed_sha256']=wf.sha(self.plan['proposed_markdown'].encode())
        self.path.write_text(json.dumps(self.plan),encoding='utf-8')
        with redirect_stdout(io.StringIO()):self.assertEqual(wf.main(['show-state','--plan',str(self.path),'--cursor',cursor]),1)
    def test_explicit_json_is_complete_export_and_rejects_text_cursor(self):
        code,text=self.cli('--format','json');self.assertEqual(code,0)
        self.assertGreater(len(text.encode()),6000)
        self.assertEqual(json.loads(text)['markdown'],wf.state_preview(self.plan)['markdown'])
        code,_=self.cli('--format','json','--cursor','not-allowed');self.assertEqual(code,1)
    def test_legacy_plan_can_read_proposed_but_never_fabricates_original_diff(self):
        del self.plan['original_markdown'];self.path.write_text(json.dumps(self.plan),encoding='utf-8')
        self.assertEqual(self.cli('--view','proposed')[0],0)
        code,text=self.cli();self.assertEqual(code,1);self.assertIn('--view proposed',text)
    def test_plan_kind_and_saved_source_or_proposal_hash_are_checked(self):
        for changes in [{'kind':'other'},{'schema_version':2},{'original_markdown':'tampered'},
                        {'proposed_markdown':'tampered'},{'expected_sha256':'wrong'},{'proposed_sha256':'wrong'}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):wf.state_preview({**self.plan,**changes})
    def test_pure_read_never_accesses_current_source_or_runs_native_or_apply(self):
        stamp=self.path.stat().st_mtime_ns;before=self.path.read_bytes()
        with patch.object(wf,'git',side_effect=AssertionError('no Git')),\
             patch.object(wf,'capture',side_effect=AssertionError('no native')),\
             patch.object(wf,'within',side_effect=AssertionError('no source')),\
             patch.object(wf,'apply_state',side_effect=AssertionError('no write')):
            self.assertEqual(self.cli()[0],0)
        self.assertEqual(self.path.read_bytes(),before);self.assertEqual(self.path.stat().st_mtime_ns,stamp)
    def test_same_saved_bytes_have_explicit_no_change_diff(self):
        p=plan_for('same\n','same\n');self.assertEqual(wf.state_preview(p)['markdown'],'(no changes)\n')
    def test_missing_final_newline_is_visible_in_diff(self):
        d=wf.state_preview(plan_for('old','new'))['markdown']
        self.assertIn('-old\n\\ No newline at end of file\n+new\n\\ No newline at end of file\n',d)
    def test_archive_is_outside_following_generated_block_and_survives_regeneration(self):
        old = '# Page\n## Current state\nOLD SOURCE CLAIM\n## History\nearlier record\n\n<!-- page-satellites:begin -->\n## Generated\nold generated text\n<!-- page-satellites:end -->\n'
        updated = wf.reading_module().replace_current(old,'new source claim','now')
        self.assertLess(updated.index('### State snapshot'),updated.index('<!-- page-satellites:begin -->'))
        regenerated = re.sub(r'<!-- page-satellites:begin -->.*?<!-- page-satellites:end -->',
                             '<!-- page-satellites:begin -->\n## Generated\nnew generation\n<!-- page-satellites:end -->',updated,flags=re.S)
        projected = wf.reading_module().page_projection(regenerated)
        self.assertIn('OLD SOURCE CLAIM',projected['history_markdown'])
        self.assertEqual(projected['authored_current_state'],'new source claim')
        self.assertIn('earlier record',regenerated)
    def test_new_history_without_existing_section_is_after_complete_generated_block(self):
        old = '# Page\n## Current state\nold claim\n<!-- generated:begin -->\n## Generated\nrows\n<!-- generated:end -->\n'
        updated = wf.reading_module().replace_current(old,'new claim','now')
        self.assertGreater(updated.index('### State snapshot'),updated.index('<!-- generated:end -->'))
        self.assertIn('old claim',wf.reading_module().page_projection(updated)['history_markdown'])
    def test_current_section_preserves_following_generated_opener_and_projection(self):
        old = '# Page\n## Current state\nold claim\n<!-- generated:begin -->\n## Generated\nrows\n<!-- generated:end -->\n'
        projected = wf.reading_module().page_projection(old)
        self.assertEqual(projected['authored_current_state'],'old claim')
        updated = wf.reading_module().replace_current(old,'new claim','now')
        self.assertIn('<!-- generated:begin -->\n## Generated\nrows\n<!-- generated:end -->',updated)
        regenerated = re.sub(r'<!-- generated:begin -->.*?<!-- generated:end -->',
                             '<!-- generated:begin -->\n## Generated\nnew rows\n<!-- generated:end -->',updated,flags=re.S)
        self.assertIn('old claim',wf.reading_module().page_projection(regenerated)['history_markdown'])
    def test_generated_begin_inside_fenced_current_example_is_literal(self):
        old = '# Page\n## Current state\nold claim\n```html\n<!-- generated:begin -->\n```\nmore old claims\n## Body\nstable\n'
        updated = wf.reading_module().replace_current(old,'new claim','now')
        history = wf.reading_module().page_projection(updated)['history_markdown']
        self.assertIn('more old claims',history);self.assertIn('```html\n<!-- generated:begin -->\n```',history)
        self.assertNotIn('more old claims',wf.reading_module().page_projection(updated)['authored_current_state'])
    def test_begin_generated_marker_bounds_authored_current(self):
        old = '# Page\n## Current state\nold claim\n<!-- BEGIN GENERATED -->\n## Generated\nrows\n<!-- END GENERATED -->\n'
        self.assertEqual(wf.reading_module().page_projection(old)['authored_current_state'],'old claim')
        updated=wf.reading_module().replace_current(old,'new claim','now')
        self.assertIn('<!-- BEGIN GENERATED -->\n## Generated',updated)
    def test_giant_single_unicode_line_respects_binary_wire_budget(self):
        self.path.write_text(json.dumps(plan_for('old\n','\U00010348\u591c\u9e6d'*8000)),encoding='utf-8')
        cp=subprocess.run([sys.executable,str(wf.__file__),'show-state','--plan',str(self.path)],capture_output=True)
        self.assertEqual(cp.returncode,0,cp.stderr);self.assertLessEqual(len(cp.stdout),6000)
        self.assertIn(b'PARTIAL',cp.stdout);self.assertNotIn(b'\r\n',cp.stdout)


class StatePreviewIntegrationTests(unittest.TestCase):
    setUp=fixture.ContextReadingTests.setUp
    git=fixture.ContextReadingTests.git
    prepare=fixture.ContextReadingTests.prepare
    def test_original_is_exact_and_compact_receipt_routes_to_pure_preview_after_apply(self):
        capture=Path(self.tmp.name)/'context.json';wf.write_new(capture,self.prepare())
        page=self.root/'docs/wiki/feature.md';old=page.read_bytes()
        state=Path(self.tmp.name)/'state.md';state.write_text('Current source behavior; live unknown.\n',encoding='utf-8')
        out=Path(self.tmp.name)/'state-plan.json';stdout=io.StringIO()
        with redirect_stdout(stdout):self.assertEqual(wf.main(['update-state','--capture',str(capture),'--path','feature.md','--state-file',str(state),'--output',str(out),'--apply']),0)
        saved=json.loads(out.read_text(encoding='utf-8'));receipt=json.loads(stdout.getvalue())
        self.assertEqual(saved['original_markdown'].encode('utf-8'),old)
        self.assertLess(len(stdout.getvalue().encode()),6000);self.assertNotIn('proposed_markdown',receipt)
        changed=page.read_bytes();page.unlink() # a saved review is still readable without live source
        with redirect_stdout(io.StringIO()):self.assertEqual(wf.main(receipt['read_preview_argv'][2:]),0)
        self.assertFalse(page.exists());self.assertNotEqual(changed,old)
    def test_oversized_artifact_fails_before_creating_plan_or_applying_source(self):
        capture=Path(self.tmp.name)/'context.json';wf.write_new(capture,self.prepare())
        page=self.root/'docs/wiki/feature.md';old=page.read_bytes();out=Path(self.tmp.name)/'too-large.json'
        state=Path(self.tmp.name)/'state.md';state.write_text('new source\n',encoding='utf-8')
        with patch.object(wf,'MAX_REPORT',400),redirect_stdout(io.StringIO()):
            # Capture itself must remain readable; force only the write budget boundary.
            with patch.object(wf,'read_json',return_value=json.loads(capture.read_text(encoding='utf-8'))):
                code=wf.main(['update-state','--capture',str(capture),'--path','feature.md','--state-file',str(state),'--output',str(out),'--apply'])
        self.assertEqual(code,1);self.assertFalse(out.exists());self.assertEqual(page.read_bytes(),old)
