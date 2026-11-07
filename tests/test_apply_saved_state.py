"""Real-task regression: applying a review must not rebuild it from loose args."""
import copy
import io
import json
from pathlib import Path
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
import test_context_reading as fixture
wf=fixture.wf

class ApplySavedStateTests(unittest.TestCase):
    setUp=fixture.ContextReadingTests.setUp
    git=fixture.ContextReadingTests.git
    prepare=fixture.ContextReadingTests.prepare
    def saved(self,current='Reviewed source behavior; live unknown.'):
        page=self.root/'docs/wiki/feature.md';plan=wf.state_update(self.prepare(),'feature.md',current,'reviewed-at')
        path=Path(self.tmp.name)/'reviewed plan.json';wf.write_new(path,plan)
        return page,plan,path
    def apply(self,path):
        buf=io.StringIO()
        with redirect_stdout(buf):code=wf.main(['apply-state','--plan',str(path)])
        return code,json.loads(buf.getvalue())
    def test_exact_reviewed_bytes_are_applied_without_rewriting_plan(self):
        page,plan,path=self.saved();saved=path.read_bytes();stamp=path.stat().st_mtime_ns
        code,receipt=self.apply(path);self.assertEqual(code,0)
        self.assertEqual(page.read_bytes(),plan['proposed_markdown'].encode())
        self.assertEqual(path.read_bytes(),saved);self.assertEqual(path.stat().st_mtime_ns,stamp)
        self.assertEqual(receipt['proposed_sha256'],plan['proposed_sha256']);self.assertTrue(receipt['applied'])
    def test_body_file_and_external_runtime_changes_are_not_reinterpreted(self):
        page,plan,path=self.saved();body=Path(self.tmp.name)/'body.md';body.write_text('DIFFERENT later body',encoding='utf-8')
        (self.root/'src/editor.py').write_text('unrelated source edit',encoding='utf-8')
        self.assertEqual(self.apply(path)[0],0);self.assertEqual(page.read_text(encoding='utf-8'),plan['proposed_markdown'])
    def test_stale_source_is_rejected_without_overwriting_it_or_the_plan(self):
        page,plan,path=self.saved();page.write_text('other actor page',encoding='utf-8');saved=path.read_bytes()
        code,receipt=self.apply(path);self.assertEqual(code,1)
        self.assertIn('stale',receipt['error']);self.assertEqual(page.read_text(encoding='utf-8'),'other actor page');self.assertEqual(path.read_bytes(),saved)
    def test_tampered_proposal_or_wrong_plan_kind_cannot_write(self):
        page,plan,path=self.saved();before=page.read_bytes()
        for change in [{'proposed_markdown':'tampered'},{'kind':'other'}]:
            path.write_text(json.dumps({**plan,**change}),encoding='utf-8')
            self.assertEqual(self.apply(path)[0],1);self.assertEqual(page.read_bytes(),before)
    def test_saved_noop_keeps_source_mtime(self):
        page,plan,path=self.saved();wf.apply_state(plan)
        fresh=wf.state_update(self.prepare(),'feature.md','Reviewed source behavior; live unknown.','next-record')
        path2=Path(self.tmp.name)/'noop.json';wf.write_new(path2,fresh);self.assertFalse(fresh['changed'])
        stamp=page.stat().st_mtime_ns;self.assertEqual(self.apply(path2)[0],0);self.assertEqual(page.stat().st_mtime_ns,stamp)
    def test_no_native_git_or_state_recomputation_is_called(self):
        page,plan,path=self.saved()
        with patch.object(wf,'git',side_effect=AssertionError('no Git')),\
             patch.object(wf,'capture',side_effect=AssertionError('no native')),\
             patch.object(wf,'state_update',side_effect=AssertionError('no rebuild')):
            self.assertEqual(self.apply(path)[0],0)
    def test_legacy_plan_without_original_snapshot_still_applies(self):
        page,plan,path=self.saved();del plan['original_markdown'];path.write_text(json.dumps(plan),encoding='utf-8')
        self.assertEqual(self.apply(path)[0],0);self.assertEqual(page.read_text(encoding='utf-8'),plan['proposed_markdown'])
    def test_preview_receipt_supplies_apply_command_for_that_exact_artifact(self):
        capture=Path(self.tmp.name)/'context.json';wf.write_new(capture,self.prepare());state=Path(self.tmp.name)/'state.md';state.write_text('Reviewed source; live unknown.',encoding='utf-8');out=Path(self.tmp.name)/'preview.json';buf=io.StringIO()
        with redirect_stdout(buf):self.assertEqual(wf.main(['update-state','--capture',str(capture),'--path','feature.md','--state-file',str(state),'--output',str(out)]),0)
        receipt=json.loads(buf.getvalue());state.write_text('different later body',encoding='utf-8')
        with redirect_stdout(io.StringIO()):self.assertEqual(wf.main(receipt['apply_preview_argv'][2:]),0)
        self.assertIn('Reviewed source; live unknown.',(self.root/'docs/wiki/feature.md').read_text(encoding='utf-8'))
        self.assertNotIn('different later body',(self.root/'docs/wiki/feature.md').read_text(encoding='utf-8'))
