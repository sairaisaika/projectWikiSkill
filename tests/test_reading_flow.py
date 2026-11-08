"""Regression counterexamples from actual oversized/repeated/mixed reading flows."""
import base64
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
import test_context_reading as fixture
wf = fixture.wf

class ReadingFlowTests(unittest.TestCase):
    setUp = fixture.ContextReadingTests.setUp
    git = fixture.ContextReadingTests.git
    prepare = fixture.ContextReadingTests.prepare
    view = fixture.ContextReadingTests.view

    def collect(self, text, *, budget=1100, identity='page:feature', command=None):
        read = wf.reading_module()
        cursor = None
        chunks = []
        for _ in range(500):
            part = read.text_page(text, identity, command or ['python','workflow.py','show','--capture','saved.json','--view','page','--path','feature.md'], budget=budget, cursor=cursor)
            self.assertLessEqual(len(part['text'].encode('utf-8')), budget)
            self.assertEqual(part['start'], sum(len(x) for x in chunks))
            chunks.append(part['content'])
            if part['next_cursor'] is None:
                self.assertIn('COMPLETE',part['text'])
                break
            self.assertIn('--cursor', part['text'])
            cursor=part['next_cursor']
        else: self.fail('pagination failed to make progress')
        self.assertEqual(''.join(chunks), text)
        return chunks

    def test_capture_index_alias_keeps_saved_scope_and_snapshot_boundary(self):
        c=self.prepare()
        with patch.object(wf,'git',side_effect=AssertionError('snapshot must not call git')):
            expected=self.view(c,'summary',snapshot_only=True)
            self.assertEqual(self.view(c,'index',snapshot_only=True),expected)

    def test_capture_index_cli_continues_every_owner_without_changing_view(self):
        import shlex
        c=self.prepare()
        c['native_report']['impact'][0]['pages'] += [
            {'path':f'owner-{i}-'+('规则'*30)+'.md','title':'规则','symbols':[]}
            for i in range(80)]
        c['native_report_canonical_sha256']=wf.report_hash(c['native_report'])
        out=Path(self.tmp.name)/'saved context.json';wf.write_new(out,c)
        args=[sys.executable,str(wf.__file__),'show','--capture',str(out),'--view','index','--snapshot-only']
        chunks=[]
        for _ in range(30):
            cp=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(cp.returncode,0,cp.stdout+cp.stderr)
            self.assertLessEqual(len(cp.stdout.encode('utf-8')),6000)
            self.assertLessEqual(len(cp.stdout.splitlines()),60)
            start=cp.stdout.index('--- CONTENT ---\n')+len('--- CONTENT ---\n')
            end=cp.stdout.rindex('\n--- END CONTENT ---')
            chunks.append(cp.stdout[start:end])
            tail=cp.stdout[end:]
            if '\nNEXT: ' not in tail:break
            command=tail.split('\nNEXT: ',1)[1].strip()
            if sys.platform=='win32':
                import re
                args=[m.replace("''", "'") for m in re.findall(r"'((?:''|[^'])*)'",command)]
            else:args=shlex.split(command)
            self.assertEqual(args[args.index('--view')+1],'index')
            self.assertIn('--snapshot-only',args)
        else:self.fail('index continuation never completed')
        self.assertGreater(len(chunks),1)
        expected=wf.reading_module().summary_text(self.view(c,'summary',snapshot_only=True),str(out.resolve()))
        self.assertEqual(''.join(chunks),expected)

    def test_giant_unicode_line_and_section_reconstruct_without_loss(self):
        chunks=self.collect('## 巨型节\n'+'𐍈夜鹭日历'*2200+'\nTAIL\n')
        self.assertGreater(len(chunks),2)
    def test_short_lines_respect_line_budget_and_head80_keeps_next_command(self):
        read=wf.reading_module();p=read.text_page('row\n'*1000,'id',['python','show'])
        self.assertLessEqual(len(p['text'].splitlines()),60)
        self.assertIn('--cursor','\n'.join(p['text'].splitlines()[:80]))
        self.collect('row\n'*1000)
    def test_default_body_does_not_duplicate_large_authored_current_state(self):
        p=self.view(self.prepare(),'page','feature.md')
        t=wf.reading_module().render_page(p,'saved.json')
        self.assertEqual(t.count('Source behavior reviewed; runtime acceptance unknown.'),1)
    def test_summary_owners_and_omissions_are_all_reachable(self):
        v=self.view(self.prepare())
        v['files']=[{'file':f'src/f{i}.py','pages':['feature.md','consumer.md'],'unregistered':False} for i in range(300)]
        read=wf.reading_module()
        text=read.summary_text(v,'saved.json')
        self.assertLess(text.index('UNEXPANDED'),text.index('src/f299.py'))
        self.collect(text)
    def test_cursor_rejects_changed_content_and_wrong_view(self):
        read=wf.reading_module();p=read.text_page('x'*4000,'first',['python','show'],budget=800)
        for text,identity in [('y'*4000,'first'),('x'*4000,'other')]:
            with self.subTest(identity=identity),self.assertRaisesRegex(ValueError,'cursor'):
                read.text_page(text,identity,['python','show'],budget=800,cursor=p['next_cursor'])
    def test_cursor_rejects_malformed_or_nonadvancing_values(self):
        read=wf.reading_module()
        for token in ['?', 'abcd', base64.urlsafe_b64encode(b'{}').decode()]:
            with self.subTest(token=token),self.assertRaisesRegex(ValueError,'cursor'):
                read.text_page('body','id',['python','show'],cursor=token)
    def test_tiny_budget_or_overlong_command_fails_explicitly(self):
        read=wf.reading_module()
        for budget,cmd in [(20,['python']), (700,['python','x'*2000])]:
            with self.subTest(budget=budget),self.assertRaisesRegex(ValueError,'budget'):
                read.text_page('x'*5000,'id',cmd,budget=budget)
    def test_small_view_stays_complete_and_does_not_add_cursor(self):
        read=wf.reading_module();p=read.text_page('short\n','id',['python','show'])
        self.assertEqual(p['content'],'short\n');self.assertIsNone(p['next_cursor'])
    def test_page_render_returns_real_continuation_not_heading_refusal(self):
        c=self.prepare();p=self.view(c,'page','feature.md');p['body_markdown']+='\n'+'正文'*6000
        t=wf.reading_module().render_page(p,'saved.json',budget=1200)
        self.assertIn('--cursor',t);self.assertNotIn('body not delivered',t)
        self.assertIn('AUTHORED',t)
    def test_cli_large_impact_defaults_to_bounded_text_with_next_argv(self):
        c=self.prepare();c['native_report']['impact'][0]['pages'][0]['details']='符号'*7000
        c['native_report_canonical_sha256']=wf.report_hash(c['native_report'])
        out=Path(self.tmp.name)/'capture.json';wf.write_new(out,c)
        cp=subprocess.run([sys.executable,str(wf.__file__),'show','--capture',str(out),'--view','impact','--path','src/editor.py','--snapshot-only'],capture_output=True,text=True, encoding="utf-8")
        self.assertEqual(cp.returncode,0,cp.stdout+cp.stderr)
        self.assertLessEqual(len(cp.stdout.encode()),6001);self.assertIn('--cursor',cp.stdout)

    def test_identical_prepare_reuses_without_native_execution(self):
        c=self.prepare()
        with patch.object(wf,'capture',side_effect=AssertionError('redundant native execution')):
            same=self.prepare(reuse=c)
        self.assertEqual(same,c)
    def test_reuse_rejects_changed_scope_query_and_runtime_before_native(self):
        c=self.prepare()
        for files,query in [(['src/editor.py','src/new.py'],'editor'),(['src/editor.py'],'other')]:
            with self.subTest(query=query,files=files),patch.object(wf,'capture',side_effect=AssertionError('native must not run')):
                with self.assertRaisesRegex(ValueError,'request.*new|new.*request'):
                    self.prepare(files,query,reuse=c)
    def test_reuse_rejects_source_wiki_and_head_drift(self):
        c=self.prepare()
        for path in ['src/editor.py','docs/wiki/feature.md']:
            p=self.root/path;old=p.read_bytes();p.write_bytes(old+b'changed\n')
            with self.subTest(path=path),self.assertRaisesRegex(ValueError,'stale|changed'):
                self.prepare(reuse=c)
            p.write_bytes(old)
        self.git('commit','--allow-empty','-m','new head')
        with self.assertRaisesRegex(ValueError,'stale|changed'):self.prepare(reuse=c)
    def test_reuse_rejects_peer_drift_and_observed_ref_movement(self):
        c=self.prepare(observed_revisions={'main':'HEAD'})
        self.git('branch','marker')
        c2=self.prepare(observed_revisions={'main':'marker'})
        # A changed peer selection is a different request; source ref change is tested with a new commit.
        with self.assertRaisesRegex(ValueError,'request.*new|new.*request'):
            self.prepare(reuse=c,peers={'mobile':str(self.root)})
        self.assertEqual(self.prepare(reuse=c2,observed_revisions={'main':'marker'}),c2)
        other=self.git('commit-tree',self.git('rev-parse','HEAD^{tree}'),'-m','other ref target')
        self.git('update-ref','refs/heads/marker',other)
        with self.assertRaisesRegex(ValueError,'observed|revision|changed'):
            self.prepare(reuse=c2,observed_revisions={'main':'marker'})
    def test_prepare_cli_reuses_same_artifact_bytes_without_rewriting(self):
        out=Path(self.tmp.name)/'context.json'
        args=['prepare','--root',str(self.root),'--query','editor','--files','src/editor.py','--runtime-input','native.py','--native-argv',json.dumps([sys.executable,'native.py']),'--allow-native-execution','--output',str(out)]
        with redirect_stdout(io.StringIO()):self.assertEqual(wf.main(args),0)
        before=out.read_bytes();stamp=out.stat().st_mtime_ns
        with patch.object(wf,'capture',side_effect=AssertionError('redundant native')),redirect_stdout(io.StringIO()) as log:
            self.assertEqual(wf.main(args),0)
        self.assertIn('REUSED',log.getvalue());self.assertEqual(out.read_bytes(),before);self.assertEqual(out.stat().st_mtime_ns,stamp)
        self.assertNotIn('FILE → ALL DECLARED OWNER PAGES:',log.getvalue())
        self.assertNotIn('src/editor.py →',log.getvalue())
        self.assertIn('Read full context:',log.getvalue())
        with redirect_stdout(io.StringIO()) as expanded:
            self.assertEqual(wf.main(['show','--capture',str(out),'--view','summary','--format','json']),0)
        full=json.loads(expanded.getvalue())
        self.assertEqual(full['files'][0]['pages'],['feature.md','consumer.md'])
        self.assertEqual(full['unexpanded_candidates'][0]['path'],'unexpanded.md')
    def test_reuse_never_overwrites_stale_artifact_or_follows_symlink(self):
        out=Path(self.tmp.name)/'context.json';c=self.prepare();wf.write_new(out,c)
        before=out.read_bytes();(self.root/'src/editor.py').write_text('changed', encoding="utf-8")
        with self.assertRaisesRegex(ValueError,'changed|stale'):self.prepare(reuse=wf.read_json(out))
        self.assertEqual(out.read_bytes(),before)

    def test_replace_current_rotates_previous_and_notes_preserves_body(self):
        read=wf.reading_module();old=(self.root/'docs/wiki/feature.md').read_text(encoding="utf-8")
        new=read.replace_current(old,'New source contract. Runtime unknown.\n','2026-11-07T10:00:00Z')
        p=read.page_projection(new)
        self.assertEqual(p['authored_current_state'],'New source contract. Runtime unknown.')
        self.assertIn('One writer serves the reader.',p['body_markdown'])
        self.assertIn('Source behavior reviewed',p['history_markdown'])
        self.assertIn('abc1234',p['history_markdown']);self.assertIn('def5678',p['history_markdown'])
        self.assertIn('abc1234',p['latest_verification_note']['text']);self.assertEqual(p['historical_verification_notes'],[]);self.assertIn('An older not deployed claim',p['history_markdown'])
        self.assertEqual(read.replace_current(new,'New source contract. Runtime unknown.\n','different timestamp'),new)
    def test_state_rotation_handles_fences_multiple_current_and_nested_history(self):
        read=wf.reading_module();old='---\ntitle: page\n---\n# Page\n\n## Current state\nfirst\n## Mechanism\n```md\n## Current state\nexample\n```\n## 当前状态\nsecond\n## History\n### Current state\nhistorical current\n'
        new=read.replace_current(old,'Only current\n','2026-11-07Z');p=read.page_projection(new)
        self.assertTrue(new.startswith('---\ntitle: page'))
        self.assertEqual(p['authored_current_state'],'Only current')
        self.assertIn('example',p['body_markdown']);self.assertIn('first',p['history_markdown']);self.assertIn('second',p['history_markdown']);self.assertIn('historical current',p['history_markdown'])
    def test_state_input_cannot_inject_other_top_sections_or_verification_history(self):
        read=wf.reading_module()
        for state in ['', '## History\nold', '> 核验：old\n', '## Mechanism\nbody']:
            with self.subTest(state=state),self.assertRaisesRegex(ValueError,'current|state|section'):
                read.replace_current('# Page\n',state,'now')
    def test_state_plan_preview_does_not_write_and_apply_is_source_bound(self):
        c=self.prepare();p=self.root/'docs/wiki/feature.md';old=p.read_bytes()
        plan=wf.state_update(c,'feature.md','Verified source contract; live unknown.\n','2026-11-07Z')
        self.assertEqual(p.read_bytes(),old);self.assertIn('proposed_markdown',plan)
        wf.apply_state(plan)
        self.assertIn('Verified source contract',p.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError,'changed|stale'):wf.apply_state(plan)
    def test_state_update_preserves_unrelated_source_changes_and_refuses_page_drift(self):
        c=self.prepare();(self.root/'src/editor.py').write_text('intended source edit\n', encoding="utf-8")
        plan=wf.state_update(c,'feature.md','New contract.\n','now')
        self.assertEqual((self.root/'src/editor.py').read_text(encoding="utf-8"),'intended source edit\n')
        p=self.root/'docs/wiki/feature.md';p.write_text('# other writer\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError,'changed|stale'):wf.apply_state(plan)
    def test_state_apply_refuses_changed_plan_and_escaping_or_symlink_target(self):
        c=self.prepare();plan=wf.state_update(c,'feature.md','new','now')
        bad=copy.deepcopy(plan);bad['proposed_markdown']='forged'
        with self.assertRaisesRegex(ValueError,'changed|hash'):wf.apply_state(bad)
        with self.assertRaisesRegex(ValueError,'path|relative|captured'):wf.state_update(c,'../../escape.md','new','now')
    def test_snapshot_only_show_with_cursor_never_calls_git(self):
        c=self.prepare();p=Path(self.tmp.name)/'context.json';wf.write_new(p,c)
        with patch.object(wf,'git',side_effect=AssertionError('snapshot called git')),redirect_stdout(io.StringIO()) as log:
            self.assertEqual(wf.main(['show','--capture',str(p),'--view','page','--path','feature.md','--snapshot-only']),0)
        self.assertIn('Current',log.getvalue())

    def test_apply_refuses_product_file_even_with_valid_hashes(self):
        plan=wf.state_update(self.prepare(),'feature.md','new','now')
        plan['page']='src/editor.py'
        plan['expected_sha256']=wf.file_hash(self.root/'src/editor.py')
        with self.assertRaisesRegex(ValueError,'Wiki root'):wf.apply_state(plan)
    def test_atomic_apply_cleans_temporary_on_last_byte_check_failure(self):
        plan=wf.state_update(self.prepare(),'feature.md','new','now')
        before=(self.root/'docs/wiki/feature.md').read_bytes()
        with patch.object(wf,'file_hash',side_effect=[plan['expected_sha256'],'changed']):
            with self.assertRaisesRegex(ValueError,'changed'):wf.apply_state(plan)
        self.assertEqual((self.root/'docs/wiki/feature.md').read_bytes(),before)
        self.assertEqual(list((self.root/'docs/wiki').glob('.wiki-state-*')),[])

    def test_cli_continuations_reconstruct_full_impact_and_keep_snapshot_mode(self):
        import shlex
        c=self.prepare();c['native_report']['impact'][0]['pages'][0]['details']='深层规则\n'*1200
        c['native_report_canonical_sha256']=wf.report_hash(c['native_report'])
        out=Path(self.tmp.name)/'capture.json';wf.write_new(out,c)
        args=[sys.executable,str(wf.__file__),'show','--capture',str(out),'--view','impact','--path','src/editor.py','--snapshot-only']
        chunks=[]
        for _ in range(30):
            cp=subprocess.run(args,capture_output=True,text=True, encoding="utf-8")
            self.assertEqual(cp.returncode,0,cp.stdout+cp.stderr)
            self.assertLessEqual(len(cp.stdout.encode()),6001)
            self.assertLessEqual(len(cp.stdout.splitlines()),61)
            start=cp.stdout.index('--- CONTENT ---\n')+len('--- CONTENT ---\n')
            end=cp.stdout.rindex('\n--- END CONTENT ---')
            chunks.append(cp.stdout[start:end])
            tail=cp.stdout[end:]
            if '\nNEXT: ' not in tail:break
            next_command=tail.split('\nNEXT: ',1)[1].strip()
            if sys.platform=='win32':
                import re
                args=[m.replace("''","'") for m in re.findall(r"'((?:''|[^'])*)'",next_command)]
            else:args=shlex.split(next_command)
            self.assertIn('--snapshot-only',args)
        else:self.fail('CLI cursor never completed')
        expected=json.dumps(self.view(c,'impact','src/editor.py',snapshot_only=True),ensure_ascii=False,indent=2)+'\n'
        self.assertEqual(''.join(chunks),expected)
    def test_cli_state_preview_then_apply_and_second_noop(self):
        out=Path(self.tmp.name)/'context.json';wf.write_new(out,self.prepare())
        state=Path(self.tmp.name)/'state.md';state.write_text('Same-version mechanism. Live unknown.\n', encoding="utf-8")
        target=self.root/'docs/wiki/feature.md';old=target.read_bytes()
        args=['update-state','--capture',str(out),'--path','feature.md','--state-file',str(state),'--output',str(Path(self.tmp.name)/'preview.json')]
        with redirect_stdout(io.StringIO()):self.assertEqual(wf.main(args),0)
        self.assertEqual(target.read_bytes(),old)
        args[-1]=str(Path(self.tmp.name)/'applied.json')
        with redirect_stdout(io.StringIO()):self.assertEqual(wf.main(args+['--apply']),0)
        projected=wf.reading_module().page_projection(target.read_text(encoding="utf-8"))
        self.assertEqual(projected['authored_current_state'],'Same-version mechanism. Live unknown.')
        self.assertIn('abc1234',projected['history_markdown'])
        fresh=Path(self.tmp.name)/'fresh.json';wf.write_new(fresh,self.prepare())
        args[args.index('--capture')+1]=str(fresh);args[-1]=str(Path(self.tmp.name)/'noop.json')
        after=target.read_bytes();stamp=target.stat().st_mtime_ns
        with redirect_stdout(io.StringIO()):self.assertEqual(wf.main(args+['--apply']),0)
        self.assertEqual(target.read_bytes(),after);self.assertEqual(target.stat().st_mtime_ns,stamp)
    def test_reuse_different_native_argv_runtime_or_artifact_is_not_a_cache_hit(self):
        c=self.prepare()
        base=dict(root=self.root,query='editor',files=['src/editor.py'],program=[sys.executable,'native.py'],runtime_inputs=['native.py'],allow_execution=True,reuse=c)
        for changed in [{'program':['python','different.py']},{'runtime_inputs':['native.py','another.py']},{'wiki_root':'other/wiki'},{'preserve_artifacts':[str(Path(self.tmp.name)/'evidence.json')]}]:
            with self.subTest(changed=changed),patch.object(wf,'capture',side_effect=AssertionError('native must not run')):
                with self.assertRaisesRegex(ValueError,'different.*request|request.*new'):
                    wf.prepare(**{**base,**changed})
    def test_state_fences_preserve_backticks_and_all_old_notes(self):
        read=wf.reading_module()
        old='# Page\n> 核验：a｜b\n## Current state\n````md\nold code\n````\n## Body\nstable\n'
        new=read.replace_current(old,'new state','now')
        projected=read.page_projection(new)
        self.assertIn('````md\nold code\n````',projected['history_markdown'])
        self.assertIn('> 核验：a｜b',projected['history_markdown'])
        self.assertNotIn('old code',projected['body_markdown'])
    def test_source_and_page_symlinks_cannot_redirect_state_apply(self):
        plan=wf.state_update(self.prepare(),'feature.md','new','now')
        target=self.root/'docs/wiki/feature.md';other=self.root/'src/editor.py';old=other.read_bytes()
        target.unlink()
        try:target.symlink_to(other)
        except OSError:self.skipTest('symlink creation unavailable')
        with self.assertRaisesRegex(ValueError,'escapes|symlink|checkout'):wf.apply_state(plan)
        self.assertEqual(other.read_bytes(),old)

    def test_state_without_title_preserves_plain_preamble_and_is_idempotent(self):
        read=wf.reading_module()
        for old in ['Preamble stays outside state.\n','Preamble.\n## Mechanism\nBody.\n','---\ntitle: no h1\n---\nPreamble.\n']:
            new=read.replace_current(old,'Current fact.','now')
            self.assertEqual(read.page_projection(new)['authored_current_state'],'Current fact.')
            self.assertEqual(read.replace_current(new,'Current fact.','later'),new)
            self.assertIn(old.splitlines()[-1],new)
    def test_existing_middle_history_is_reused_without_duplicating_heading(self):
        read=wf.reading_module();old='# Page\n## Current state\nold\n## History\nold evidence\n## Mechanism\nstable body\n'
        new=read.replace_current(old,'new','now')
        self.assertEqual(new.count('\n## History\n'),1)
        p=read.page_projection(new);self.assertIn('stable body',p['body_markdown']);self.assertIn('old evidence',p['history_markdown']);self.assertIn('old\n',p['history_markdown'])
    def test_current_body_requires_a_closed_fence(self):
        with self.assertRaisesRegex(ValueError,'unclosed'):
            wf.reading_module().replace_current('# Page\n','```md\nexample','now')

    def test_closed_atx_headings_are_shared_by_projection_selection_and_rotation(self):
        read=wf.reading_module();old='# Page #\n   ## 当前状态 ##\nold state\n## Mechanism ##\nstable\n## 核验历史 ###\nold evidence\n'
        p=read.page_projection(old)
        self.assertEqual(p['authored_current_state'],'old state')
        self.assertIn('old evidence',p['history_markdown'])
        self.assertIn('stable',read.select_section(p['body_markdown'],'Mechanism'))
        p=read.page_projection(read.replace_current(old,'new state','now'))
        self.assertEqual(p['authored_current_state'],'new state')
        self.assertNotIn('old state',p['body_markdown']);self.assertIn('old state',p['history_markdown'])
    def test_packet_text_continuation_keeps_explicit_format(self):
        import shlex
        c=self.prepare();c['native_report']['impact'][0]['pages'][0]['details']='x'*20000
        c['native_report_canonical_sha256']=wf.report_hash(c['native_report'])
        packet=wf.start(c,'task','owner','edit',['src/editor.py'],['source evidence'],['title'])
        out=Path(self.tmp.name)/'packet.json';wf.write_new(out,packet)
        cp=subprocess.run([sys.executable,str(wf.__file__),'show','--packet',str(out),'--view','impact','--path','src/editor.py','--snapshot-only','--format','text'],capture_output=True,text=True, encoding="utf-8")
        self.assertEqual(cp.returncode,0,cp.stdout+cp.stderr)
        next_command=cp.stdout.split('\nNEXT: ',1)[1].strip()
        self.assertIn('--format',next_command)
        if sys.platform=='win32':
            import re
            argv=[m.replace("''","'") for m in re.findall(r"'((?:''|[^'])*)'",next_command)]
        else:argv=shlex.split(next_command)
        continued=subprocess.run(argv,capture_output=True,text=True, encoding="utf-8")
        self.assertEqual(continued.returncode,0,continued.stdout+continued.stderr)
        self.assertIn('DISPLAY',continued.stdout)

    def test_state_body_preserves_meaningful_indentation(self):
        read=wf.reading_module();body='    code_example()\n\nSource meaning.\n'
        new=read.replace_current('# Page\n',body,'now')
        self.assertIn('\n    code_example()\n',new)
        self.assertEqual(read.replace_current(new,body,'later'),new)

    def test_oversized_prepare_and_reuse_have_working_continuations_from_relative_path(self):
        import shlex
        folder=self.root/'context space';folder.mkdir()
        args=[sys.executable,str(wf.__file__),'prepare','--root',str(self.root),'--query','editor','--files',*[f'src/f{i}.py' for i in range(200)],'--runtime-input','native.py','--native-argv',json.dumps([sys.executable,'native.py']),'--allow-native-execution','--output','context space/context.json']
        saved=None
        for reuse in [False,True]:
            cp=subprocess.run(args,cwd=self.root,capture_output=True,text=True, encoding="utf-8")
            self.assertEqual(cp.returncode,0,cp.stdout+cp.stderr)
            self.assertLessEqual(len(cp.stdout.encode()),6000);self.assertLessEqual(len(cp.stdout.splitlines()),60)
            if reuse:self.assertIn('REUSED',cp.stdout)
            current=(folder/'context.json').read_bytes()
            if saved is not None:self.assertEqual(saved,current)
            saved=current
            if reuse:
                self.assertNotIn('FILE → ALL DECLARED OWNER PAGES:',cp.stdout)
                self.assertIn('files=200',cp.stdout)
                self.assertNotIn('\nNEXT: ',cp.stdout)
                command=cp.stdout.split('Read full context: ',1)[1].splitlines()[0]
            else:
                command=cp.stdout.split('\nNEXT: ',1)[1].strip()
            if sys.platform=='win32':
                import re
                argv=[m.replace("''","'") for m in re.findall(r"'((?:''|[^'])*)'",command)]
            else:argv=shlex.split(command)
            continued=subprocess.run(argv,cwd=Path(self.tmp.name),capture_output=True,text=True, encoding="utf-8")
            self.assertEqual(continued.returncode,0,continued.stdout+continued.stderr)
            self.assertIn('DISPLAY',continued.stdout)

    def test_locator_keeps_missing_scope_counts_and_snapshot_only_boundary(self):
        c=self.prepare();read=wf.reading_module()
        v=copy.deepcopy(read.summary(c));v['unregistered_files']=['src/unknown.py'];v['preparation']['selected_paths_with_changes']=['src/editor.py']
        compact=read.locator_summary(v)
        self.assertEqual(compact['unregistered'],1)
        self.assertEqual(compact['preparation_changes'],1)
        self.assertEqual(compact['unexpanded_candidates'],1)
        with patch.object(wf,'check_capture',side_effect=AssertionError('live read')):
            saved=wf.capture_view(c,'locator',snapshot_only=True)
        self.assertFalse(saved['current_inputs_checked'])
        self.assertIn('saved snapshot',saved['freshness'])
        text=read.render_locator(saved,'/private/context space.json',snapshot_only=True)
        command=text.split('Read full context: ',1)[1].splitlines()[0]
        if sys.platform=='win32':
            import re
            argv=[m.replace("''","'") for m in re.findall(r"'((?:''|[^'])*)'",command)]
        else:
            import shlex
            argv=shlex.split(command)
        self.assertEqual(argv[argv.index('--view')+1],'summary')
        self.assertEqual(argv[argv.index('--capture')+1],'/private/context space.json')
        self.assertIn('--snapshot-only',argv)
        self.assertIn('not redelivered or acknowledged as read',text)
        self.assertNotIn('Source behavior reviewed',text)
        self.assertLessEqual(len(text.encode('utf-8')),6000)

    def test_repository_relative_page_and_history_use_the_same_saved_key(self):
        c=self.prepare()
        with patch.object(wf,'check_capture',side_effect=AssertionError('live read')):
            for kind in ['page','history']:
                plain=wf.capture_view(c,kind,'feature.md',snapshot_only=True)
                alias=wf.capture_view(c,kind,'docs/wiki/feature.md',snapshot_only=True)
                self.assertEqual(alias,plain)
                self.assertEqual(alias['path'],'feature.md')

    def test_repository_relative_state_plan_targets_the_same_captured_file(self):
        c=self.prepare()
        plain=wf.state_update(c,'feature.md','Source corrected.','now')
        alias=wf.state_update(c,'docs/wiki/feature.md','Source corrected.','now')
        self.assertEqual(alias,plain)
        self.assertEqual(alias['page'],'docs/wiki/feature.md')
        wf.apply_state(alias)
        self.assertIn('Source corrected.',(self.root/'docs/wiki/feature.md').read_text())
        self.assertFalse((self.root/'docs/wiki/docs').exists())

    def test_unknown_and_ambiguous_page_keys_do_not_redirect(self):
        c=self.prepare()
        with self.assertRaisesRegex(ValueError,'not captured'):
            wf.capture_view(c,'page','docs/wiki/unknown.md',snapshot_only=True)
        with self.assertRaisesRegex(ValueError,'not captured'):
            wf.capture_view(c,'page','docs/wiki/../../outside.md',snapshot_only=True)
        with self.assertRaisesRegex(ValueError,'not captured') as error:
            wf.capture_view(c,'page','x'*20000,snapshot_only=True)
        self.assertLess(len(str(error.exception)),1000)
        ambiguous=copy.deepcopy(c)
        ambiguous['prepared_reading']['pages']['docs/wiki/feature.md']={}
        with self.assertRaisesRegex(ValueError,'Ambiguous'):
            wf.captured_page_key(ambiguous,'docs/wiki/feature.md')
        old=copy.deepcopy(c);old.pop('prepared_reading');old.pop('prepared_reading_sha256')
        with self.assertRaisesRegex(ValueError,'No saved page views'):
            wf.capture_view(old,'page','feature.md',snapshot_only=True)

    def test_repository_relative_cli_continuation_preserves_snapshot_only(self):
        import shlex,os,re
        page=self.root/'docs/wiki/feature.md'
        page.write_text('# Feature\n\n## Mechanism\n'+'夜鹭'*1500+'\n',encoding='utf-8')
        c=self.prepare();out=Path(self.tmp.name)/'capture space.json';wf.write_new(out,c)
        args=['show','--capture',str(out),'--view','page','--path','docs/wiki/feature.md','--section','Mechanism','--snapshot-only']
        with patch.object(wf,'check_capture',side_effect=AssertionError('live read')),redirect_stdout(io.StringIO()) as first:
            self.assertEqual(wf.main(args),0)
        command=first.getvalue().split('\nNEXT: ',1)[1].strip()
        argv=([m.replace("''","'")for m in re.findall(r"'((?:''|[^'])*)'",command)] if sys.platform=='win32' else shlex.split(command))
        self.assertIn('--snapshot-only',argv)
        self.assertEqual(argv[argv.index('--path')+1],'docs/wiki/feature.md')
        result=subprocess.run(argv,cwd=Path(self.tmp.name),env={**os.environ,'PATH':''},capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('COMPLETE VIEW',result.stdout)
        self.assertIn('saved snapshot only',result.stdout)

    def test_preamble_and_keyword_metadata_stay_outside_replaced_current_section(self):
        read=wf.reading_module();old='# Page\n\n> 关键词：date · reader\n> 核验：2026-11-01 · abc1234\nIntroductory prose.\n\n## 当前状态\nold contract\n\n## Mechanism\nImplementation.\n'
        new=read.replace_current(old,'New contract.','now')
        projected=read.page_projection(new)
        self.assertEqual(projected['authored_current_state'],'New contract.')
        self.assertLess(new.index('关键词'),new.index('## 当前状态'))
        self.assertLess(new.index('Introductory prose.'),new.index('## 当前状态'))
        self.assertIn('abc1234',projected['latest_verification_note']['text'])
    def test_new_verification_is_explicit_and_archives_previous_record(self):
        read=wf.reading_module();old='# Page\n> 核验：2026-11-01 · abc1234\n## Current state\nold\n'
        note='> 核验：2026-11-07 · def5678 source checked; runtime unknown'
        new=read.replace_current(old,'new','now',note);p=read.page_projection(new)
        self.assertIn('def5678',p['latest_verification_note']['text']);self.assertIn('abc1234',p['history_markdown'])
        self.assertEqual(read.replace_current(new,'new','later',note),new)
        for bad in ['> 核验：a｜b','> 核验：a\n> 核验：b','invented prose']:
            with self.assertRaisesRegex(ValueError,'verification'):read.replace_current(old,'new','now',bad)
    def test_missing_current_section_keeps_intro_outside_new_state(self):
        read=wf.reading_module()
        for old in ['# Page\nIntro prose.\n## Mechanism\nstable\n','# Page\nIntro prose.\n']:
            new=read.replace_current(old,'new state','now')
            self.assertEqual(read.page_projection(new)['authored_current_state'],'new state')
            self.assertLess(new.index('Intro prose.'),new.index('## Current state'))

    def test_existing_current_heading_spelling_and_self_link_are_preserved(self):
        read=wf.reading_module();old='# Page\n[当前状态](#当前状态)\n## 当前状态\nold\n## Mechanism\nstable\n'
        new=read.replace_current(old,'new','now')
        self.assertIn('[当前状态](#当前状态)',new)
        self.assertIn('\n## 当前状态\n',new)
        self.assertNotIn('\n## Current state\n',new)

    def test_legacy_capture_json_default_stays_compatible_for_active_sessions(self):
        c=self.prepare();c['prepared_reading'].pop('text_display')
        c['prepared_reading_sha256']=wf.report_hash(c['prepared_reading'])
        out=Path(self.tmp.name)/'legacy.json';wf.write_new(out,c)
        cp=subprocess.run([sys.executable,str(wf.__file__),'show','--capture',str(out),'--view','impact','--path','src/editor.py','--snapshot-only'],capture_output=True,text=True, encoding="utf-8")
        self.assertEqual(cp.returncode,0,cp.stdout+cp.stderr)
        self.assertEqual(json.loads(cp.stdout)['native_context']['impact'][0]['file'],'src/editor.py')
        bounded=subprocess.run([sys.executable,str(wf.__file__),'show','--capture',str(out),'--view','impact','--path','src/editor.py','--snapshot-only','--format','text'],capture_output=True,text=True, encoding="utf-8")
        self.assertEqual(bounded.returncode,0,bounded.stdout+bounded.stderr);self.assertIn('COMPLETE VIEW',bounded.stdout)

    def test_cli_raw_stdout_stays_within_utf8_byte_budget_and_lf_wire_format(self):
        c=self.prepare();c['native_report']['impact'][0]['pages'][0]['details']='规则'*8000
        c['native_report_canonical_sha256']=wf.report_hash(c['native_report'])
        out=Path(self.tmp.name)/'capture.json';wf.write_new(out,c)
        cp=subprocess.run([sys.executable,str(wf.__file__),'show','--capture',str(out),'--view','impact','--path','src/editor.py','--snapshot-only'],capture_output=True)
        self.assertEqual(cp.returncode,0,cp.stderr.decode('utf-8'))
        self.assertLessEqual(len(cp.stdout),6000)
        self.assertNotIn(b'\r\n',cp.stdout)
        self.assertIn('--cursor',cp.stdout.decode('utf-8'))


class SectionOutlineTests(unittest.TestCase):
    """Saved heading discovery replaces guessed --section values and whole-page reads."""
    setUp = fixture.ContextReadingTests.setUp
    git = fixture.ContextReadingTests.git
    prepare = fixture.ContextReadingTests.prepare

    def saved(self, page=None, name='saved context.json', mutate=None):
        if page is not None:
            (self.root/'docs/wiki/feature.md').write_text(page,encoding='utf-8')
        c=self.prepare()
        if mutate:
            mutate(c['prepared_reading']['pages']['feature.md'])
            c['prepared_reading_sha256']=wf.report_hash(c['prepared_reading'])
        out=Path(self.tmp.name)/name;wf.write_new(out,c)
        return out

    def run_main(self, args):
        with patch.object(wf,'git',side_effect=AssertionError('snapshot must not call git')), \
             patch.object(wf,'check_capture',side_effect=AssertionError('live read')), \
             redirect_stdout(io.StringIO()) as out:
            code=wf.main(args)
        return code,out.getvalue()

    @staticmethod
    def argv(command):
        import shlex,re
        if sys.platform=='win32':
            return [m.replace("''","'") for m in re.findall(r"'((?:''|[^'])*)'",command)]
        return shlex.split(command)

    @staticmethod
    def section_of(argv):
        for i,arg in enumerate(argv):
            if arg=='--section':return argv[i+1]
            if arg.startswith('--section='):return arg[len('--section='):]
        return None

    def open_lines(self, text):
        return [self.argv(line.split('OPEN: ',1)[1]) for line in text.splitlines() if line.lstrip().startswith('OPEN: ')]

    def test_page_section_index_lists_exact_open_commands_without_live_reads(self):
        out=self.saved()
        code,text=self.run_main(['show','--capture',str(out),'--view','page','--path','docs/wiki/feature.md','--section-index','--snapshot-only'])
        self.assertEqual(code,0,text)
        self.assertIn('COMPLETE VIEW',text)
        self.assertIn('saved snapshot only',text)
        self.assertNotIn('One writer serves the reader.',text)  # outline, not page body
        opened=self.open_lines(text)
        self.assertEqual([self.section_of(a) for a in opened],['Feature','Current state','Mechanism'])
        self.assertIn('--view history --section-index',text)
        for argv in opened:
            self.assertIn('--snapshot-only',argv);self.assertNotIn('--section-index',argv)
            self.assertEqual(argv[argv.index('--path')+1],'docs/wiki/feature.md')
            code,body=self.run_main(argv[2:])
            self.assertEqual(code,0,body);self.assertIn('SELECTED AUTHORED SECTION',body)
        self.assertIn('One writer serves the reader.',self.run_main(opened[2][2:])[1])

    def test_fenced_history_snapshot_headings_never_become_current_sections(self):
        page=('# Feature\n\n## Current state\nnew state\n\n```markdown\n## Fake current\n```\n\n## Mechanism\nm\n\n'
              '## History\n\n### State snapshot 2026-01-01\n\n````markdown\n## Current state\nold state\n## Mechanism\nold\n````\n')
        out=self.saved(page)
        code,text=self.run_main(['show','--capture',str(out),'--view','page','--path','feature.md','--section-index','--snapshot-only'])
        self.assertEqual(code,0,text)
        self.assertEqual([self.section_of(a) for a in self.open_lines(text)],['Feature','Current state','Mechanism'])
        self.assertNotIn('Fake current',text);self.assertNotIn('State snapshot',text)
        code,hist=self.run_main(['show','--capture',str(out),'--view','history','--path','feature.md','--section-index','--snapshot-only'])
        self.assertEqual(code,0,hist)
        self.assertEqual([self.section_of(a) for a in self.open_lines(hist)],['History','State snapshot 2026-01-01'])
        self.assertNotIn('Current state',hist);self.assertNotIn('Mechanism',hist)
        for argv in self.open_lines(hist):
            self.assertEqual(argv[argv.index('--view')+1],'history')
            code,body=self.run_main(argv[2:])
            self.assertEqual(code,0,body);self.assertIn('HISTORICAL EVIDENCE',body)

    def test_duplicate_and_untitled_headings_are_identified_without_failing_selectors(self):
        page='# Feature\n\n## Notes\na\n\n## Notes\nb\n\n##\nuntitled\n\n## Unique\nu\n'
        out=self.saved(page)
        with self.assertRaises(ValueError):wf.reading_module().select_section(page,'Notes')
        code,text=self.run_main(['show','--capture',str(out),'--view','page','--path','feature.md','--section-index','--snapshot-only'])
        self.assertEqual(code,0,text)
        self.assertEqual(text.count('AMBIGUOUS'),2)
        self.assertIn('UNTITLED',text)
        opened=self.open_lines(text)
        self.assertEqual([self.section_of(a) for a in opened],['Feature','Unique'])
        for argv in opened:self.assertEqual(self.run_main(argv[2:])[0],0)

    def test_missing_or_empty_outline_metadata_stays_unknown_without_reconstruction(self):
        missing=self.saved(name='missing.json',mutate=lambda p:p.pop('section_index'))
        code,text=self.run_main(['show','--capture',str(missing),'--view','page','--path','feature.md','--section-index','--snapshot-only'])
        self.assertEqual(code,0,text);self.assertIn('UNKNOWN',text);self.assertNotIn('OPEN:',text)
        self.assertNotIn('Mechanism',text)
        empty=self.saved(name='empty.json',mutate=lambda p:p.update(section_index=[]))
        code,text=self.run_main(['show','--capture',str(empty),'--view','page','--path','feature.md','--section-index','--snapshot-only'])
        self.assertEqual(code,0,text);self.assertIn('no headings recorded',text);self.assertNotIn('OPEN:',text)
        code,data=self.run_main(['show','--capture',str(missing),'--view','page','--path','feature.md','--section-index','--snapshot-only','--format','json'])
        self.assertEqual(code,0,data);self.assertEqual(json.loads(data)['section_outline']['status'],'unknown')

    def test_large_unicode_outline_continues_exactly_and_quoted_titles_round_trip(self):
        odd=["O'Brien \"quoted\" $HOME `tick`", '-leading dash', '路径 / 夜鹭 𐍈 ; & |']
        titles=[f'节 {i} '+('夜鹭日历'*12) for i in range(120)]+odd
        page='# Feature\n\n'+''.join(f'## {t}\nbody {i}\n\n' for i,t in enumerate(titles))
        out=self.saved(page,name='saved 夜鹭 context.json')
        args=['show','--capture',str(out),'--view','page','--path','docs/wiki/feature.md','--section-index','--snapshot-only']
        chunks=[]
        for _ in range(100):
            code,text=self.run_main(args)
            self.assertEqual(code,0,text)
            self.assertLessEqual(len(text.encode('utf-8')),6000);self.assertLessEqual(len(text.splitlines()),60)
            start=text.index('--- CONTENT ---\n')+len('--- CONTENT ---\n');end=text.rindex('\n--- END CONTENT ---')
            chunks.append(text[start:end]);tail=text[end:]
            if '\nNEXT: ' not in tail:break
            args=self.argv(tail.split('\nNEXT: ',1)[1].strip())[2:]
            for flag in ('--section-index','--snapshot-only'):self.assertIn(flag,args)
            self.assertEqual(args[args.index('--view')+1],'page')
            self.assertEqual(args[args.index('--path')+1],'docs/wiki/feature.md')
            self.assertEqual(args[args.index('--capture')+1],str(out.resolve()))
        else:self.fail('outline continuation never completed')
        self.assertGreater(len(chunks),2)
        whole=''.join(chunks)
        openers=self.open_lines(whole)
        self.assertEqual([self.section_of(a) for a in openers],['Feature',*titles])
        for argv,expected in zip(openers[-3:],['body 120','body 121','body 122']):
            code,body=self.run_main(argv[2:])
            self.assertEqual(code,0,body);self.assertIn(expected,body)

    def test_section_index_rejects_mixed_selection_and_other_views(self):
        out=self.saved()
        for extra in (['--view','page','--path','feature.md','--section','Mechanism'],['--view','summary'],['--view','impact','--path','src/editor.py']):
            with self.subTest(extra=extra):
                code,text=self.run_main(['show','--capture',str(out),*extra,'--section-index','--snapshot-only'])
                self.assertEqual(code,1,text);self.assertIn('--section-index',text)
        code,text=self.run_main(['show','--capture',str(out),'--view','page','--path','feature.md','--section','Nope','--snapshot-only'])
        self.assertEqual(code,1);self.assertIn('--section-index',text)

    def test_default_page_and_json_exports_are_unchanged_by_the_option(self):
        out=self.saved()
        base=['show','--capture',str(out),'--view','page','--path','feature.md','--snapshot-only']
        _,page=self.run_main(base)
        self.assertNotIn('OPEN:',page);self.assertIn('AUTHORED CURRENT STATE',page)
        _,raw=self.run_main(base+['--format','json'])
        self.assertIn('body_markdown',json.loads(raw))
        _,outline=self.run_main(base+['--section-index','--format','json'])
        data=json.loads(outline)
        self.assertNotIn('body_markdown',data)
        rows=data['section_outline']['sections']
        self.assertEqual([r['title'] for r in rows],['Feature','Current state','Mechanism'])
        for row in rows:
            code,body=self.run_main(row['open_argv'][2:])
            self.assertEqual(code,0,body)

    def test_powershell_commands_double_every_single_quote_variant(self):
        import types
        read=wf.reading_module()
        with patch.object(read,'os',types.SimpleNamespace(name='nt')):
            command=read.shell_command(['py','Owner’s ‘x’ ‚‛ it\'s'])
        self.assertEqual(command,"& 'py' 'Owner’’s ‘‘x’’ ‚‚‛‛ it''s'")

    def test_packet_page_outline_opens_with_the_same_packet(self):
        c=self.prepare()
        packet=wf.start(c,'t-1','reader','read',[],['ok'],['read'],read_only=True)
        out=Path(self.tmp.name)/'packet.json';wf.write_new(out,packet)
        code,text=self.run_main(['show','--packet',str(out),'--view','page','--path','feature.md','--section-index','--snapshot-only'])
        self.assertEqual(code,0,text)
        opened=self.open_lines(text)
        self.assertTrue(opened and all('--packet' in a for a in opened))
        self.assertEqual(self.run_main(opened[-1][2:])[0],0)
