"""Independent-review counterexamples: format coherence and source evidence stay separate."""
import hashlib
import json
from pathlib import Path
from unittest.mock import patch
import test_package_newlines as newline_tests
from test_plugin_package import builder, doctor

class PackageIntegrityTests(newline_tests.PackageNewlineTests):
    # Inherit fixture helpers, not the parent's six test methods (removed below).
    def test_rewriting_only_payload_hash_inventory_cannot_hide_unbound_code(self):
        for case in ('skill', 'support', 'extra', 'host'):
            with self.subTest(case=case):
                src=self.source('source-'+case); out=self.home/('package-'+case); receipt=builder.build(out,src)
                target={'skill':'skills/project-wiki/SKILL.md','support':'scripts/plugin_doctor.py','extra':'scripts/unlisted.py','host':'.codex-plugin/plugin.json'}[case]
                if case=='host':
                    value=json.loads((out/target).read_text());value['skills']='./elsewhere/'
                    data=builder.json_bytes(value)
                else:data=b'Changed actual source or unlisted code.\n'
                (out/target).write_bytes(data);receipt['files'][target]=hashlib.sha256(data).hexdigest()
                (out/'PACKAGE-SOURCES.json').write_bytes(builder.json_bytes(receipt))
                report=doctor.inspect(out,src)
                self.assertFalse(report['package_valid'],case)

    def test_invalid_source_text_does_not_invalidate_intact_package_evidence(self):
        src=self.source('src');out=self.home/'package';builder.build(out,src)
        (src/'project-wiki/SKILL.md').write_bytes(b'invalid\xff')
        report=doctor.inspect(out,src)
        self.assertTrue(report['package_valid'])
        self.assertFalse(report['source_match'])
        self.assertTrue(report['source_identity_match'])
        self.assertIn('project-wiki/SKILL.md',report['source_text_errors'])

    def test_malformed_source_identity_does_not_crash_or_revoke_package_integrity(self):
        src=self.source('src');out=self.home/'package';builder.build(out,src)
        (src/'plugin.json').write_bytes(b'[]')
        report=doctor.inspect(out,src)
        self.assertTrue(report['package_valid'])
        self.assertFalse(report['source_identity_match'])
        self.assertIn('source_error',report)

    def test_schema_bool_and_float_do_not_silently_select_receipt_formats(self):
        src=self.source('src');out=self.home/'package';receipt=builder.build(out,src)
        for value in (True,2.0):
            with self.subTest(value=value):
                (out/'PACKAGE-SOURCES.json').write_bytes(builder.json_bytes(dict(receipt,schema_version=value)))
                self.assertFalse(doctor.inspect(out)['package_valid'])

    def test_malformed_receipt_returns_report_instead_of_traceback(self):
        src=self.source('src');out=self.home/'package';builder.build(out,src)
        (out/'PACKAGE-SOURCES.json').write_bytes(b'[]')
        self.assertFalse(doctor.inspect(out)['package_valid'])

    def test_builder_non_string_identity_is_a_handled_validation_error(self):
        src=self.source('src');identity=json.loads((src/'plugin.json').read_text());identity['name']=[]
        (src/'plugin.json').write_bytes(builder.json_bytes(identity))
        with self.assertRaises(ValueError):builder.build(self.home/'bad',src)
        self.assertFalse((self.home/'bad').exists())

    def test_lone_cr_is_rejected_instead_of_becoming_new_crlf_after_normalization(self):
        src=self.source('src');(src/'project-wiki/references/lone-cr.md').write_bytes(b'a\r\r\nb')
        with self.assertRaises(ValueError):builder.build(self.home/'bad',src)
        self.assertFalse((self.home/'bad').exists())

    def test_added_source_during_build_prevents_completed_receipt(self):
        src=self.source('src');out=self.home/'package';original=Path.write_bytes;changed=[]
        def write(path,data):
            result=original(path,data)
            if path.resolve()==(out/'skills/project-wiki/SKILL.md').resolve() and not changed:
                original(src/'project-wiki/references/added.md',b'new source added during build\n');changed.append(True)
            return result
        with patch.object(Path,'write_bytes',write):
            with self.assertRaisesRegex(ValueError,'inventory changed'):builder.build(out,src)
        self.assertEqual(changed,[True]);self.assertFalse((out/'PACKAGE-SOURCES.json').exists())

# Use only the parent's setUp/source fixture; don't duplicate its test collection.
for _name in list(newline_tests.PackageNewlineTests.__dict__):
    if _name.startswith('test_'):
        setattr(PackageIntegrityTests,_name,None)
