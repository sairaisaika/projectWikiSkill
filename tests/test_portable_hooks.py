"""Portable manifest declarations are distinct from byte-valid installation."""
import json
from pathlib import Path
import tempfile
import unittest
from test_plugin_package import builder, doctor, ROOT


class PortableHookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)

    def test_optional_profile_declares_openai_hooks_in_selected_portable_manifest(self):
        pkg = self.home / 'optional'
        receipt = builder.build(pkg, with_hooks=True, hook_layout='portable')
        manifest = json.loads((pkg / 'plugin.json').read_text())
        self.assertEqual(manifest.get('extensions', {}).get('com.openai', {}).get('hooks'), './hooks/codex.json')
        report = doctor.inspect(pkg, ROOT)
        self.assertTrue(report['package_valid'], report)
        self.assertTrue(report['source_identity_match'], report)
        self.assertEqual(receipt.get('root_manifest_projection'), 'portable-openai-hooks-v1')

    def test_plain_profile_keeps_canonical_identity_without_optional_hook_declaration(self):
        pkg = self.home / 'plain'
        builder.build(pkg)
        self.assertEqual(json.loads((pkg / 'plugin.json').read_text()), json.loads((ROOT / 'plugin.json').read_text()))
        self.assertTrue(doctor.inspect(pkg, ROOT)['package_valid'])

    def test_altered_projection_and_rehashed_wrong_hook_path_are_rejected(self):
        pkg = self.home / 'altered'
        receipt = builder.build(pkg, with_hooks=True, hook_layout='portable')
        value = json.loads((pkg / 'plugin.json').read_text())
        value['extensions']['com.openai']['hooks'] = './elsewhere.json'
        data = builder.json_bytes(value)
        (pkg / 'plugin.json').write_bytes(data)
        receipt['files']['plugin.json'] = builder.digest(data)
        (pkg / 'PACKAGE-SOURCES.json').write_bytes(builder.json_bytes(receipt))
        self.assertFalse(doctor.inspect(pkg)['package_valid'])

    def test_legacy_hook_package_identity_projection_stays_inspectable(self):
        pkg = self.home / 'legacy'
        receipt = builder.build(pkg, with_hooks=True, hook_layout='portable')
        # Reconstruct the previous unsigned receipt representation; payload
        # helpers remain source-bound. This is format compatibility, not a claim
        # that a historical package or its hooks ran on a host.
        receipt.pop('root_manifest_projection', None)
        data = builder.json_bytes(receipt['canonical_identity'])
        (pkg / 'plugin.json').write_bytes(data)
        receipt['files']['plugin.json'] = builder.digest(data)
        (pkg / 'PACKAGE-SOURCES.json').write_bytes(builder.json_bytes(receipt))
        self.assertTrue(doctor.inspect(pkg, ROOT)['package_valid'])


if __name__ == '__main__':
    unittest.main()
