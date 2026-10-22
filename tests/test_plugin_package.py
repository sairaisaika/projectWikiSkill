"""Package closure is a lower evidence layer than host activation or agent use."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = module('package_plugin')
doctor = module('plugin_doctor')


class PluginPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)

    def package(self):
        out = self.home / 'package'
        builder.build(out)
        return out

    def test_same_canonical_skill_for_both_hosts_and_no_activation_claim(self):
        out = self.package()
        report = doctor.inspect(out, ROOT)
        self.assertTrue(report['package_valid'])
        self.assertTrue(report['source_match'])
        for host in ('claude', 'codex'):
            manifest = json.loads((out / f'.{host}-plugin/plugin.json').read_text())
            self.assertEqual(manifest['name'], 'project-wiki')
            self.assertEqual(manifest['skills'], './skills/')
            self.assertNotIn('hooks', manifest)
        self.assertEqual((out / 'skills/project-wiki/SKILL.md').read_bytes(), (ROOT / 'project-wiki/SKILL.md').read_bytes())
        for layer in ('installation', 'hook_execution', 'agent_use', 'semantic_review', 'business_acceptance'):
            self.assertEqual(report[layer], 'unverified')

    def test_output_is_not_overwritten(self):
        out = self.package()
        before = (out / 'PACKAGE-SOURCES.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'already exists'):
            builder.build(out)
        self.assertEqual((out / 'PACKAGE-SOURCES.json').read_bytes(), before)

    def test_outputs_inside_source_are_rejected_before_creation(self):
        with self.assertRaisesRegex(ValueError, 'outside'):
            builder.build(ROOT / 'never-create-this-package')
        self.assertFalse((ROOT / 'never-create-this-package').exists())

    def test_tampered_and_extra_payload_are_reported(self):
        out = self.package()
        (out / 'skills/project-wiki/SKILL.md').write_text('wrong version')
        (out / 'unexpected.txt').write_text('unexpected')
        report = doctor.inspect(out)
        self.assertFalse(report['package_valid'])
        self.assertIn('missing_or_modified:skills/project-wiki/SKILL.md', report['issues'])
        self.assertIn('unexpected_file:unexpected.txt', report['issues'])

    def test_old_installed_copy_is_detected_against_current_source(self):
        out = self.package()
        src = self.home / 'source'
        shutil.copytree(ROOT / 'project-wiki', src / 'project-wiki', ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copyfile(ROOT / 'plugin.json', src / 'plugin.json')
        (src / 'project-wiki/SKILL.md').write_text('changed canonical instructions')
        report = doctor.inspect(out, src)
        self.assertTrue(report['package_valid'])
        self.assertFalse(report['source_match'])

    def test_missing_receipt_and_traversal_receipt_fail_closed(self):
        out = self.package()
        receipt = out / 'PACKAGE-SOURCES.json'
        receipt.unlink()
        self.assertFalse(doctor.inspect(out)['package_valid'])

    def test_empty_component_inventory_cannot_claim_validity(self):
        out = self.package()
        receipt = out / 'PACKAGE-SOURCES.json'
        receipt.write_text(json.dumps({'schema_version': 1, 'name': 'x', 'version': '1', 'files': {}}))
        self.assertFalse(doctor.inspect(out)['package_valid'])
        receipt.write_text(json.dumps({'schema_version': 1, 'name': 'x', 'version': '1', 'files': {'../outside': 'x'}}))
        self.assertFalse(doctor.inspect(out)['package_valid'])

    def test_source_symlink_or_hidden_file_cannot_be_smuggled_into_package(self):
        src = self.home / 'source'
        shutil.copytree(ROOT / 'project-wiki', src / 'project-wiki', ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copyfile(ROOT / 'plugin.json', src / 'plugin.json')
        shutil.copyfile(ROOT / 'LICENSE', src / 'LICENSE')
        (src / 'project-wiki/.env').write_text('fixture only')
        with self.assertRaisesRegex(ValueError, 'hidden'):
            builder.build(self.home / 'bad', src)
        self.assertFalse((self.home / 'bad').exists())

    def test_host_observation_requires_real_matching_init_and_tool_result_events(self):
        out=self.package()
        version=json.loads((out/'plugin.json').read_text())['version']
        lines=[{'type':'system','subtype':'init','plugins':[{'name':'project-wiki','version':version,'path':str(out.resolve()),'source':'project-wiki@inline'}]},
               {'type':'assistant','message':{'content':[{'type':'tool_use','id':'s1','name':'Skill','input':{'skill':'project-wiki:project-wiki'}}]}},
               {'type':'user','message':{'content':[{'type':'tool_result','tool_use_id':'s1','content':'Launching skill: project-wiki:project-wiki'}]}},
               {'type':'result','is_error':False}]
        log=self.home/'scoped.jsonl'
        log.write_text('\n'.join(json.dumps(x) for x in lines),encoding='utf-8')
        result=doctor.inspect_claude_transcript(log,out,'project-wiki',version)
        self.assertTrue(result['package_identity_matched'])
        self.assertTrue(result['skill_launch_result_observed'])
        self.assertEqual(result['permanent_installation'],'not established')
        self.assertFalse(doctor.inspect_claude_transcript(log,out,'project-wiki','999.0.0')['skill_launch_result_observed'])
        lines[2]['message']['content'][0]['is_error']=True
        log.write_text('\n'.join(json.dumps(x) for x in lines),encoding='utf-8')
        self.assertFalse(doctor.inspect_claude_transcript(log,out,'project-wiki',version)['skill_launch_result_observed'])
        lines[2]['message']['content'][0].pop('is_error')
        lines[1]['type']='user'
        log.write_text('\n'.join(json.dumps(x) for x in lines),encoding='utf-8')
        self.assertFalse(doctor.inspect_claude_transcript(log,out,'project-wiki',version)['skill_launch_result_observed'])

    def test_a_model_saying_it_loaded_is_not_a_host_loading_receipt(self):
        log=self.home/'claim.jsonl'
        log.write_text(json.dumps({'type':'result','is_error':False,'result':'I loaded the plugin and read everything.'}),encoding='utf-8')
        result=doctor.inspect_claude_transcript(log,self.home/'absent','project-wiki','0.2.0')
        self.assertFalse(result['package_identity_matched'])
        self.assertFalse(result['skill_launch_result_observed'])

    def test_changed_support_tool_is_detected_even_when_skill_and_version_match(self):
        out = self.package()
        source = self.home / 'support-source'
        shutil.copytree(ROOT / 'project-wiki', source / 'project-wiki', ignore=shutil.ignore_patterns('__pycache__'))
        (source / 'scripts').mkdir()
        for rel in ('plugin.json', 'LICENSE', 'scripts/plugin_doctor.py'):
            shutil.copyfile(ROOT / rel, source / rel)
        (source / 'scripts/plugin_doctor.py').write_text('different support implementation')
        report = doctor.inspect(out, source)
        self.assertTrue(report['package_valid'])
        self.assertTrue(report['source_match'])
        self.assertTrue(report['source_identity_match'])
        self.assertFalse(report['source_support_match'])
        self.assertEqual(report['source_support_mismatches'], ['scripts/plugin_doctor.py'])


if __name__ == '__main__':
    unittest.main()
