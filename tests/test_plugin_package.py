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


if __name__ == '__main__':
    unittest.main()
