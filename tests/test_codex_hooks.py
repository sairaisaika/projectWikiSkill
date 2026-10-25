"""Supplied hook listings are observations, not installation or execution proof."""
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
spec = importlib.util.spec_from_file_location('hooks_doctor', ROOT / 'scripts/plugin_doctor.py')
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)


class CodexHooksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # Windows CI may expose TEMP through a short-name/junction spelling.
        # Bind fixture source strings to the selected canonical package path;
        # the inspector must not resolve arbitrary paths received from a listing.
        self.home = Path(self.temp.name).resolve()
        self.package = self.home / 'package'
        self.path = self.home / 'hooks.json'
        self.row = {'pluginId': 'project-wiki@fixture-market', 'eventName': 'sessionStart',
                    'source': 'plugin', 'sourcePath': str(self.package / 'hooks/codex.json'),
                    'handlerType': 'command', 'enabled': True, 'trustStatus': 'trusted',
                    'command': 'MUST NOT EXECUTE OR COPY', 'currentHash': 'sha256:' + 'a' * 64}
        self.data = {'id': 9, 'result': {'data': [{'cwd': '/chosen/work', 'hooks': [self.row]}]}}

    def observe(self, data=None, cwd='/chosen/work'):
        self.path.write_text(json.dumps(self.data if data is None else data), encoding='utf-8')
        return doctor.inspect_codex_hooks(self.path, self.package, 'project-wiki', 'fixture-market', cwd)

    def test_matching_listing_retains_only_lower_evidence_layer(self):
        result = self.observe()
        self.assertTrue(result['record_present'])
        self.assertTrue(result['selected_package_source_path_matched'])
        self.assertEqual(result['reported_trust_status'], 'trusted')
        self.assertEqual(result['reported_definition_hash'], self.row['currentHash'])
        for layer in ['hook_execution', 'context_delivery', 'agent_use', 'semantic_review', 'business_acceptance']:
            self.assertEqual(result[layer], 'not established')
        self.assertNotIn('MUST NOT EXECUTE', json.dumps(result))
        self.assertIn('not a package-file checksum', result['limits'])

    def test_result_body_without_jsonrpc_envelope_is_supported(self):
        self.assertTrue(self.observe(self.data['result'])['record_present'])

    def test_disabled_untrusted_and_modified_states_are_not_promoted(self):
        for trust in ['trusted', 'untrusted', 'modified']:
            for enabled in [True, False]:
                with self.subTest(trust=trust, enabled=enabled):
                    self.row.update(trustStatus=trust, enabled=enabled)
                    result = self.observe()
                    self.assertEqual(result['reported_trust_status'], trust)
                    self.assertEqual(result['reported_enabled'], enabled)
                    self.assertEqual(result['hook_execution'], 'not established')

    def test_wrong_plugin_event_or_cwd_is_absent_not_global_uninstall(self):
        for key, value in [('pluginId', 'project-wiki@other'), ('eventName', 'postToolUse')]:
            with self.subTest(key=key):
                original = self.row[key]
                self.row[key] = value
                result = self.observe()
                self.assertFalse(result['record_present'])
                self.assertIsNone(result['reported_trust_status'])
                self.row[key] = original
        result = self.observe(cwd='/other/work')
        self.assertFalse(result['cwd_present'])
        self.assertFalse(result['record_present'])

    def test_source_path_must_match_selected_package_without_disk_access(self):
        self.row['sourcePath'] = str(self.home / 'different-version/hooks/codex.json')
        with self.assertRaisesRegex(ValueError, 'differs'):
            self.observe()
        self.row['sourcePath'] = '//network-host/private/hooks/codex.json'
        with self.assertRaisesRegex(ValueError, 'Network'):
            self.observe()
        self.assertFalse((self.home / 'different-version').exists())

    def test_duplicates_or_partial_error_cannot_select_convenient_record(self):
        group = self.data['result']['data'][0]
        group['hooks'].append(self.row.copy())
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            self.observe()
        group['hooks'].pop()
        self.data['result']['data'].append(copy.deepcopy(group))
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            self.observe()
        self.data['result']['data'].pop()
        group['errors'] = ['partial load failure']
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            self.observe()

    def test_invalid_target_fields_fail_closed(self):
        for key, value in [('enabled', 'true'), ('enabled', 1), ('trustStatus', 'accepted'),
                           ('currentHash', 'a' * 64), ('currentHash', 'sha256:bad'),
                           ('source', 'user'), ('handlerType', 'prompt'), ('sourcePath', None)]:
            with self.subTest(key=key, value=value):
                original = self.row[key]
                self.row[key] = value
                with self.assertRaises(ValueError):
                    self.observe()
                self.row[key] = original

    def test_local_path_comparison_is_host_independent_and_lexical(self):
        self.assertEqual(doctor.local_path_key('C:\\Users\\Test\\hooks\\codex.json'),
                         doctor.local_path_key('c:/users/test/hooks/codex.json'))
        self.assertNotEqual(doctor.local_path_key('/Work/A'), doctor.local_path_key('/work/a'))
        for value in ['relative/path', 'C:relative', '//server/share/file', '\\\\server\\share',
                      '/work/../secret', 'C:/work/./file', '/work/\x00file', '', None]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                doctor.local_path_key(value)

    def test_local_path_comparison_does_not_guess_short_name_or_symlink_aliases(self):
        self.assertNotEqual(doctor.local_path_key('C:/Users/RUNNER~1/Temp/package/hooks/codex.json'),
                            doctor.local_path_key('C:/Users/runneradmin/Temp/package/hooks/codex.json'))
        self.assertNotEqual(doctor.local_path_key('/alias/package/hooks/codex.json'),
                            doctor.local_path_key('/real/package/hooks/codex.json'))

    def test_captured_paths_and_commands_never_become_io_targets(self):
        # Write input before mocking. Only the explicitly supplied JSON may be read.
        self.path.write_text(json.dumps(self.data), encoding='utf-8')
        original_open = Path.open
        reads = []
        def bounded_read(path, *args, **kwargs):
            reads.append(path)
            self.assertEqual(path, self.path)
            return original_open(path, *args, **kwargs)
        with patch.object(Path, 'open', bounded_read), patch.object(subprocess, 'run', side_effect=AssertionError('execution')):
            self.assertTrue(doctor.inspect_codex_hooks(self.path, self.package, 'project-wiki', 'fixture-market', '/chosen/work')['record_present'])
        self.assertEqual(reads, [self.path])

    def test_malformed_and_oversized_snapshots_cannot_produce_positive_observation(self):
        for value in [[], {}, {'result': []}, {'error': {}}, {'data': [] , 'error': None},
                      {'data': [None]}, {'data': [{'cwd': '/chosen/work', 'hooks': {}}]}]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.observe(value)
        self.path.write_bytes(b' ' * (doctor.MAX_HOST_HOOKS + 1))
        with self.assertRaisesRegex(ValueError, 'budget'):
            doctor.inspect_codex_hooks(self.path, self.package, 'project-wiki', 'fixture-market', '/chosen/work')

    def test_cli_requires_complete_explicit_selection(self):
        base = [sys.executable, str(ROOT / 'scripts/plugin_doctor.py'), '--package', str(self.package)]
        for args in [['--codex-hooks', str(self.path)], ['--codex-hooks-cwd', '/chosen/work'],
                     ['--codex-hooks', str(self.path), '--codex-hooks-cwd', '/chosen/work']]:
            with self.subTest(args=args):
                result = subprocess.run(base + args, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stdout)

    def test_cli_keeps_package_integrity_and_host_evidence_separate(self):
        builder_spec = importlib.util.spec_from_file_location('hooks_builder', ROOT / 'scripts/package_plugin.py')
        builder = importlib.util.module_from_spec(builder_spec)
        builder_spec.loader.exec_module(builder)
        builder.build(self.package, with_hooks=True)
        version = json.loads((self.package / 'PACKAGE-SOURCES.json').read_text())['version']
        inventory = self.home / 'inventory.json'
        installed = {'pluginId': 'project-wiki@fixture-market', 'name': 'project-wiki',
                     'marketplaceName': 'fixture-market', 'installed': True, 'enabled': True, 'version': version}
        def save_inventory():
            inventory.write_text(json.dumps({'installed': [installed]}), encoding='utf-8')
        save_inventory()
        self.observe()
        argv = [sys.executable, str(ROOT / 'scripts/plugin_doctor.py'), '--package', str(self.package),
                '--codex-inventory', str(inventory), '--codex-marketplace', 'fixture-market',
                '--codex-hooks', str(self.path), '--codex-hooks-cwd', '/chosen/work']
        def cli():
            result = subprocess.run(argv, capture_output=True, text=True)
            return result.returncode, json.loads(result.stdout)
        rc, report = cli()
        self.assertEqual(rc, 0)
        self.assertTrue(report['codex_hooks_observation']['record_present'])
        for layer in ['installation', 'hook_trust', 'hook_execution', 'context_delivery', 'agent_use', 'semantic_review', 'business_acceptance']:
            self.assertEqual(report[layer], 'unverified')
        installed['version'] = '0.0.0'
        save_inventory()
        rc, report = cli()
        self.assertEqual(rc, 0)  # Host mismatch does not invalidate valid package bytes.
        self.assertIn('error', report['codex_hooks_observation'])
        installed['version'] = version
        save_inventory()
        self.row['trustStatus'] = 'unknown'
        self.path.write_text(json.dumps(self.data), encoding='utf-8')
        rc, report = cli()
        self.assertEqual(rc, 0)
        self.assertIn('error', report['codex_hooks_observation'])
        (self.package / 'hooks/codex.json').write_text('{}', encoding='utf-8')
        rc, report = cli()
        self.assertEqual(rc, 1)
        self.assertFalse(report['package_valid'])
        self.assertIn('error', report['codex_hooks_observation'])


if __name__ == '__main__':
    unittest.main()
