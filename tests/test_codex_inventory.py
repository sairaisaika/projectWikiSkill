"""An official inventory snapshot is one observation, never agent adoption."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('inventory_doctor', ROOT / 'scripts/plugin_doctor.py')
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)


class CodexInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'inventory.json'
        self.row = {'pluginId': 'project-wiki@fixture-market', 'name': 'project-wiki',
                    'marketplaceName': 'fixture-market', 'version': '1.2.3',
                    'installed': True, 'enabled': True, 'source': {'path': 'must-not-be-executed'}}

    def inspect(self, rows=None, **extra):
        self.path.write_text(json.dumps({'installed': [self.row] if rows is None else rows, **extra}), encoding='utf-8')
        return doctor.inspect_codex_inventory(self.path, 'project-wiki', '1.2.3', 'fixture-market')

    def test_matches_exact_package_and_marketplace_but_not_higher_layers(self):
        result = self.inspect()
        self.assertEqual(result['kind'], 'provided-codex-plugin-inventory')
        self.assertTrue(result['record_present'])
        self.assertTrue(result['reported_installed'])
        self.assertTrue(result['reported_enabled'])
        self.assertTrue(result['package_version_matched'])
        self.assertEqual(result['reported_version'], '1.2.3')
        self.assertEqual(result['hook_execution'], 'not established')
        self.assertEqual(result['agent_use'], 'not established')
        self.assertEqual(result['host_version'], 'unreported')
        self.assertNotIn('source', result)

    def test_old_version_is_reported_without_claiming_selected_package_installed(self):
        self.row['version'] = '1.0.0'
        result = self.inspect()
        self.assertTrue(result['reported_installed'])
        self.assertFalse(result['package_version_matched'])
        self.assertEqual(result['reported_version'], '1.0.0')

    def test_other_marketplace_is_not_selected_even_with_same_name_and_version(self):
        self.row.update(pluginId='project-wiki@other', marketplaceName='other')
        result = self.inspect()
        self.assertFalse(result['record_present'])
        self.assertEqual(result['state'], 'not_listed_in_supplied_inventory')
        self.assertIsNone(result['reported_installed'])

    def test_available_or_model_claim_is_not_an_installed_record(self):
        result = self.inspect([], available=[self.row], result='Plugin loaded successfully')
        self.assertFalse(result['record_present'])
        self.assertFalse(result['package_version_matched'])

    def test_disabled_installation_is_retained(self):
        self.row['enabled'] = False
        result = self.inspect()
        self.assertTrue(result['reported_installed'])
        self.assertFalse(result['reported_enabled'])

    def test_duplicate_target_records_are_ambiguous(self):
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            self.inspect([self.row, self.row.copy()])

    def test_string_booleans_and_inconsistent_identity_are_rejected(self):
        for key, value in [('installed', 'true'), ('enabled', 1), ('name', 'other'),
                           ('marketplaceName', 'other'), ('version', '')]:
            with self.subTest(key=key):
                row = {**self.row, key: value}
                with self.assertRaises(ValueError):
                    self.inspect([row])

    def test_malformed_and_oversized_input_fail_before_a_positive_observation(self):
        for content in ['[]', '{"installed":{}}', '{"installed":[null]}', '{"result":"loaded"}', '{']:
            with self.subTest(content=content):
                self.path.write_text(content, encoding='utf-8')
                with self.assertRaises(ValueError):
                    doctor.inspect_codex_inventory(self.path, 'project-wiki', '1.2.3', 'fixture-market')
        self.path.write_bytes(b' ' * (doctor.MAX_HOST_INVENTORY + 1))
        with self.assertRaisesRegex(ValueError, 'budget'):
            doctor.inspect_codex_inventory(self.path, 'project-wiki', '1.2.3', 'fixture-market')

    def test_host_version_needs_separate_bounded_stdout_evidence(self):
        p = self.path.parent / 'version.txt'
        p.write_text('codex-cli 1.2.3\n', encoding='utf-8')
        result = doctor.inspect_codex_version(p)
        self.assertEqual(result['reported'], 'codex-cli 1.2.3')
        for value in ['loaded', 'codex-cli ', 'codex-cli 1\nsecond command', 'codex-cli \x1b1', 'x' * 513]:
            with self.subTest(value=value[:30]):
                p.write_text(value, encoding='utf-8')
                with self.assertRaises(ValueError):
                    doctor.inspect_codex_version(p)

    def test_cli_reports_only_supplied_host_observation_and_keeps_layers_separate(self):
        build_spec = importlib.util.spec_from_file_location('inventory_builder', ROOT / 'scripts/package_plugin.py')
        builder = importlib.util.module_from_spec(build_spec)
        build_spec.loader.exec_module(builder)
        package = self.path.parent / 'package'
        builder.build(package)
        version = json.loads((package / 'plugin.json').read_text())['version']
        self.row['version'] = version
        self.inspect()
        version_file = self.path.parent / 'version.txt'
        version_file.write_text('codex-cli 1.2.3\n', encoding='utf-8')
        argv = [sys.executable, str(ROOT / 'scripts/plugin_doctor.py'), '--package', str(package),
                '--codex-inventory', str(self.path), '--codex-marketplace', 'fixture-market',
                '--codex-version-file', str(version_file)]
        result = subprocess.run(argv, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report['codex_observation']['package_version_matched'])
        self.assertEqual(report['codex_observation']['host_version']['reported'], 'codex-cli 1.2.3')
        for layer in ['installation', 'hook_trust', 'hook_execution', 'context_delivery', 'agent_use', 'semantic_review', 'business_acceptance']:
            self.assertEqual(report[layer], 'unverified')
        # Tampered selected bytes cannot receive a positive host observation.
        (package / 'plugin.json').write_text('{}')
        bad = json.loads(subprocess.run(argv, capture_output=True, text=True, check=False).stdout)
        self.assertFalse(bad['package_valid'])
        self.assertIn('error', bad['codex_observation'])
        self.assertNotIn('record_present', bad['codex_observation'])

    def test_cli_requires_explicit_inventory_marketplace_pair(self):
        argv = [sys.executable, str(ROOT / 'scripts/plugin_doctor.py'), '--package', str(self.path.parent)]
        for extra in [['--codex-inventory', str(self.path)], ['--codex-marketplace', 'fixture-market'],
                      ['--codex-version-file', str(self.path)]]:
            result = subprocess.run(argv + extra, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('"package_valid"', result.stdout)


if __name__ == '__main__':
    unittest.main()
