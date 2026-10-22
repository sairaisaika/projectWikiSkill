"""Inspect a package and optional source checkout without enabling or running hooks."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

MAX_TRANSCRIPT = 4 * 1024 * 1024


def inspect_claude_transcript(path: Path, package: Path, name: str, version: str) -> dict:
    """Report matched events, not permanent installation or semantic compliance."""
    observation = {'kind': 'provided-local-cli-transcript', 'package_identity_matched': False,
                   'skill_launch_result_observed': False, 'terminal_success_observed': False,
                   'permanent_installation': 'not established', 'semantic_compliance': 'not established'}
    if path.stat().st_size > MAX_TRANSCRIPT:
        raise ValueError('Scoped transcript exceeds inspection budget')
    data = path.read_bytes()
    observation['transcript_sha256'] = hashlib.sha256(data).hexdigest()
    calls = set()
    launched = set()
    for line in data.decode('utf-8-sig').splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get('type') == 'system' and row.get('subtype') == 'init':
            for plugin in row.get('plugins', []):
                if plugin.get('name') == name and plugin.get('version') == version and plugin.get('path') == str(package.resolve()):
                    observation['package_identity_matched'] = True
                    observation['load_source'] = plugin.get('source', 'unreported')
            observation['host_version'] = row.get('claude_code_version', 'unreported')
        content = row.get('message', {}).get('content', [])
        if isinstance(content, list):
            for block in content:
                if row.get('type') == 'assistant' and observation['package_identity_matched'] and block.get('type') == 'tool_use' and block.get('name') == 'Skill':
                    skill = block.get('input', {}).get('skill', '')
                    if isinstance(skill, str) and skill.startswith(name + ':'):
                        calls.add(block['id'])
                if row.get('type') == 'user' and block.get('type') == 'tool_result' and block.get('tool_use_id') in calls and not block.get('is_error'):
                    if 'Launching skill: ' + name + ':' in str(block.get('content', '')):
                        launched.add(block['tool_use_id'])
        if row.get('type') == 'result' and row.get('is_error') is False:
            observation['terminal_success_observed'] = True
    observation['skill_launch_result_observed'] = bool(launched) and observation['package_identity_matched']
    observation['limits'] = 'Unsigned supplied transcript; one invocation only. No hook trust, native routing, agent correctness or business acceptance inferred.'
    return observation


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
            current = {path.relative_to(source).as_posix()
                       for path in (source / 'project-wiki').rglob('*')
                       if path.is_file() and '__pycache__' not in path.parts and '.pytest_cache' not in path.parts}
            for name in sorted(current - set(receipt['canonical_skill_files'])):
                mismatches.append('not_in_package:' + name)
            report['source_match'] = not mismatches
            report['source_mismatches'] = mismatches
            support = receipt.get('canonical_support_files')
            report['source_support_match'] = 'unverified legacy receipt'
            if support is not None:
                if not isinstance(support, dict) or set(support) != {'plugin.json', 'LICENSE', 'scripts/plugin_doctor.py'}:
                    raise ValueError('Invalid canonical support input inventory')
                support_mismatches = []
                for name, expected_hash in support.items():
                    path = source / name
                    if path.is_symlink() or not path.resolve().is_relative_to(source):
                        raise ValueError('Canonical support input escapes checkout')
                    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
                        support_mismatches.append(name)
                report['source_support_match'] = not support_mismatches
                report['source_support_mismatches'] = support_mismatches
            identity = json.loads((source / 'plugin.json').read_text(encoding='utf-8'))
            report['source_version'] = identity.get('version')
            report['source_identity_match'] = (identity.get('name') == receipt['name'] and identity.get('version') == receipt['version'])
        report['payload_files'] = len(expected)
    except (OSError, ValueError, KeyError, TypeError) as error:
        report['package_valid'] = False
        report['issues'].append(type(error).__name__ + ': invalid or incomplete package')
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, type=Path)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--claude-transcript', type=Path, help='Inspect actual scoped CLI events; never infer global installation')
    args = parser.parse_args()
    report = inspect(args.package, args.source)
    if args.claude_transcript is not None:
        if not report['package_valid']:
            report['cli_observation'] = {'error': 'Package integrity must pass before matching host events'}
        else:
            try:
                report['cli_observation'] = inspect_claude_transcript(args.claude_transcript, args.package, report['name'], report['version'])
            except (OSError, ValueError, KeyError, TypeError, AttributeError):
                report['cli_observation'] = {'error': 'Scoped host transcript unavailable or invalid; use remains unverified'}
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report['package_valid'] and report.get('source_match', True) and report.get('source_support_match') is not False and report.get('source_identity_match', True) else 1


if __name__ == '__main__':
    sys.exit(main())
