"""Actual cross-host newline drift: canonical text, strict package bytes and legacy receipts."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from test_plugin_package import builder, doctor, ROOT

class PackageNewlineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)

    def source(self, name, crlf=False):
        root = self.home / name
        shutil.copytree(ROOT / 'project-wiki', root / 'project-wiki', ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache'))
        (root / 'scripts').mkdir()
        for rel in ('plugin.json', 'LICENSE', 'scripts/plugin_doctor.py'):
            shutil.copyfile(ROOT / rel, root / rel)
        for file in root.rglob('*'):
            if file.is_file():
                data = file.read_bytes().replace(b'\r\n', b'\n')
                file.write_bytes(data.replace(b'\n', b'\r\n') if crlf else data)
        return root

    def test_lf_and_crlf_build_same_payload_but_preserve_distinct_input_provenance(self):
        lf, crlf = self.source('lf'), self.source('crlf', True)
        a, b = self.home/'a', self.home/'b'
        ra, rb = builder.build(a, lf), builder.build(b, crlf)
        self.assertEqual(ra['files'], rb['files'])
        self.assertEqual(ra['schema_version'], 2)
        self.assertEqual(ra['source_byte_policy'], 'utf8-crlf-to-lf-v1')
        self.assertNotEqual(ra['source_input_files'], rb['source_input_files'])
        own = doctor.inspect(b, crlf)
        cross = doctor.inspect(b, lf)
        self.assertTrue(own['source_match']); self.assertTrue(own['source_input_bytes_match'])
        self.assertTrue(cross['source_match']); self.assertTrue(cross['source_support_match'])
        self.assertFalse(cross['source_input_bytes_match'])
        self.assertEqual(cross['source_comparison'], 'utf8-crlf-to-lf-v1')
        self.assertEqual(cross['business_acceptance'], 'unverified')

    def test_real_content_change_still_fails_even_with_same_version(self):
        src = self.source('src'); out = self.home/'package'; builder.build(out, src)
        with (src/'project-wiki/SKILL.md').open('ab') as f: f.write(b'\nChanged actual instructions.\n')
        report = doctor.inspect(out, src)
        self.assertFalse(report['source_match'])
        self.assertIn('project-wiki/SKILL.md', report['source_mismatches'])

    def test_package_bytes_are_never_normalized_during_integrity_check(self):
        src = self.source('src'); out = self.home/'package'; builder.build(out, src)
        p = out/'skills/project-wiki/SKILL.md'; p.write_bytes(p.read_bytes().replace(b'\n', b'\r\n'))
        report = doctor.inspect(out, src)
        self.assertFalse(report['package_valid'])
        self.assertIn('missing_or_modified:skills/project-wiki/SKILL.md', report['issues'])

    def test_legacy_receipt_remains_raw_and_unknown_policy_is_rejected(self):
        lf, crlf = self.source('lf'), self.source('crlf', True)
        out = self.home/'package'; receipt = builder.build(out, lf)
        unknown = dict(receipt, source_byte_policy='guess-newlines-v99')
        (out/'PACKAGE-SOURCES.json').write_bytes(builder.json_bytes(unknown))
        self.assertFalse(doctor.inspect(out, lf)['package_valid'])
        receipt['schema_version'] = 1
        receipt.pop('source_byte_policy', None); receipt.pop('source_input_files', None)
        (out/'PACKAGE-SOURCES.json').write_bytes(builder.json_bytes(receipt))
        self.assertTrue(doctor.inspect(out, lf)['source_match'])
        self.assertFalse(doctor.inspect(out, crlf)['source_match'])
        self.assertEqual(doctor.inspect(out, crlf)['source_comparison'], 'raw-bytes-v1')

    def test_invalid_utf8_is_rejected_before_output_creation(self):
        src = self.source('src'); (src/'project-wiki/references/bad.md').write_bytes(b'bad\xff')
        out = self.home/'bad'
        with self.assertRaises((UnicodeError, ValueError)):
            builder.build(out, src)
        self.assertFalse(out.exists())

    def test_source_change_during_build_still_rejects_even_if_only_line_endings(self):
        src = self.source('src'); out = self.home/'package'; original = Path.write_bytes; changed = []
        def write(path, data):
            result = original(path, data)
            if path == out/'skills/project-wiki/SKILL.md' and not changed:
                original(src/'project-wiki/SKILL.md', (src/'project-wiki/SKILL.md').read_bytes().replace(b'\n', b'\r\n'))
                changed.append(True)
            return result
        with patch.object(Path, 'write_bytes', write):
            with self.assertRaisesRegex(ValueError, 'changed during build'):
                builder.build(out, src)
        self.assertEqual(changed, [True])
        self.assertFalse((out/'PACKAGE-SOURCES.json').exists())

if __name__ == '__main__': unittest.main()
