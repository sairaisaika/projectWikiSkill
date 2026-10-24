"""Current-host layout projects one source identity without a portable root."""
import json
from pathlib import Path
import tempfile
import unittest
from test_plugin_package import builder, doctor, ROOT


class LegacyHookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)

    def test_default_hook_profile_is_legacy_but_both_host_identities_match_source(self):
        pkg = self.home / 'legacy'
        receipt = builder.build(pkg, with_hooks=True)
        self.assertFalse((pkg / 'plugin.json').exists())
        self.assertNotIn('plugin.json', receipt['files'])
        self.assertIn('plugin.json', receipt['canonical_support_files'])
        self.assertEqual(receipt['root_manifest_projection'], 'legacy-host-hooks-v1')
        canonical = json.loads((ROOT / 'plugin.json').read_text())
        self.assertEqual(receipt['canonical_identity'], canonical)
        for host in ['codex', 'claude']:
            manifest = json.loads((pkg / f'.{host}-plugin/plugin.json').read_text())
            self.assertEqual(manifest['version'], canonical['version'])
            self.assertEqual(manifest['hooks'], f'./hooks/{host}.json')
        report = doctor.inspect(pkg, ROOT)
        self.assertTrue(report['package_valid'], report)
        self.assertTrue(report['source_identity_match'], report)
        self.assertTrue(report['source_support_match'], report)
        self.assertEqual(report['hook_execution'], 'unverified')

    def test_adding_a_portable_root_to_legacy_profile_is_not_silently_accepted(self):
        pkg = self.home / 'mixed'
        builder.build(pkg, with_hooks=True)
        (pkg / 'plugin.json').write_text(json.dumps(json.loads((ROOT / 'plugin.json').read_text())))
        report = doctor.inspect(pkg)
        self.assertFalse(report['package_valid'])
        self.assertIn('unexpected_file:plugin.json', report['issues'])

    def test_legacy_requires_schema2_hook_profile_and_canonical_identity(self):
        pkg = self.home / 'invalid'
        receipt = builder.build(pkg, with_hooks=True)
        for patch in [{'schema_version': 1}, {'lifecycle_hooks': False}, {'canonical_identity': None}]:
            value = {**receipt, **patch}
            (pkg / 'PACKAGE-SOURCES.json').write_bytes(builder.json_bytes(value))
            self.assertFalse(doctor.inspect(pkg)['package_valid'])

    def test_plain_profile_stays_portable_and_explicit_portable_hook_profile_stays_available(self):
        plain, portable = self.home / 'plain', self.home / 'portable'
        builder.build(plain)
        self.assertTrue((plain / 'plugin.json').is_file())
        receipt = builder.build(portable, with_hooks=True, hook_layout='portable')
        self.assertTrue((portable / 'plugin.json').is_file())
        self.assertEqual(receipt['root_manifest_projection'], 'portable-openai-hooks-v1')
        self.assertTrue(doctor.inspect(portable, ROOT)['package_valid'])

    def test_layout_cannot_be_misused_without_hooks_or_with_unknown_container(self):
        for args in [{'hook_layout': 'portable'}, {'with_hooks': True, 'hook_layout': 'invented'}]:
            with self.assertRaises(ValueError):
                builder.build(self.home / 'rejected', **args)
        self.assertFalse((self.home / 'rejected').exists())


if __name__ == '__main__':
    unittest.main()
