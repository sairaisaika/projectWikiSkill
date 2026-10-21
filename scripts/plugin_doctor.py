"""Inspect a package and optional source checkout without enabling or running hooks."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


def inspect(package: Path, source: Path | None = None) -> dict:
    package = package.resolve()
    report = {'schema_version': 1, 'package_valid': False, 'issues': [],
              'installation': 'unverified', 'hook_trust': 'unverified',
              'hook_execution': 'unverified', 'context_delivery': 'unverified',
              'agent_use': 'unverified', 'semantic_review': 'unverified',
              'business_acceptance': 'unverified'}
    try:
        receipt = json.loads((package / 'PACKAGE-SOURCES.json').read_text(encoding='utf-8'))
        if receipt.get('schema_version') != 1 or not isinstance(receipt.get('files'), dict):
            raise ValueError('Unsupported package receipt')
        report.update(name=receipt['name'], version=receipt['version'])
        expected = receipt['files']
        required = {'plugin.json', 'LICENSE', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json',
                    'skills/project-wiki/SKILL.md', 'skills/project-wiki/scripts/wiki.py', 'scripts/plugin_doctor.py'}
        if not required.issubset(expected):
            raise ValueError('Required plugin component is missing')
        for name, sha in expected.items():
            rel = PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts or '\\' in name or not rel.parts:
                raise ValueError('Unsafe package entry')
            path = package / name
            if not path.resolve().is_relative_to(package) or path.is_symlink():
                raise ValueError('Package entry escapes its root')
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != sha:
                report['issues'].append('missing_or_modified:' + name)
        actual = set()
        for path in package.rglob('*'):
            if path.is_symlink():
                raise ValueError('Package contains symlink')
            if path.is_file():
                actual.add(path.relative_to(package).as_posix())
        for name in sorted(actual - set(expected) - {'PACKAGE-SOURCES.json'}):
            report['issues'].append('unexpected_file:' + name)
        report['package_valid'] = not report['issues']
        if source is not None:
            source = source.resolve()
            mismatches = []
            for name, sha in receipt['canonical_skill_files'].items():
                rel = PurePosixPath(name)
                if rel.is_absolute() or '..' in rel.parts or '\\' in name or rel.parts[:1] != ('project-wiki',):
                    raise ValueError('Unsafe canonical source entry')
                path = source / name
                if path.is_symlink() or not path.resolve().is_relative_to(source):
                    raise ValueError('Source entry escapes checkout')
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != sha:
                    mismatches.append(name)
            report['source_match'] = not mismatches
            current = {path.relative_to(source).as_posix()
                       for path in (source / 'project-wiki').rglob('*')
                       if path.is_file() and '__pycache__' not in path.parts and '.pytest_cache' not in path.parts}
            for name in sorted(current - set(receipt['canonical_skill_files'])):
                mismatches.append('not_in_package:' + name)
            report['source_match'] = not mismatches
            report['source_mismatches'] = mismatches
        report['payload_files'] = len(expected)
    except (OSError, ValueError, KeyError, TypeError) as error:
        report['package_valid'] = False
        report['issues'].append(type(error).__name__ + ': invalid or incomplete package')
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, type=Path)
    parser.add_argument('--source', type=Path)
    args = parser.parse_args()
    report = inspect(args.package, args.source)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report['package_valid'] and report.get('source_match', True) else 1


if __name__ == '__main__':
    sys.exit(main())
