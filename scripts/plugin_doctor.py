"""Inspect a package and optional source checkout without enabling or running hooks."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

MAX_TRANSCRIPT = 4 * 1024 * 1024
MAX_HOST_INVENTORY = 4 * 1024 * 1024
SOURCE_BYTE_POLICY = 'utf8-crlf-to-lf-v1'


def inspect_codex_inventory(path: Path, name: str, version: str, marketplace: str) -> dict:
    """Read caller-captured official CLI JSON; never execute its source paths.

    The file is unsigned and may be old or filtered. A matching record is an
    installation/enabling observation only, not proof of the selected cache
    bytes, hooks, context consumption or semantic correctness.
    """
    if not marketplace or '@' in marketplace:
        raise ValueError('Explicit marketplace identity is required')
    if path.stat().st_size > MAX_HOST_INVENTORY:
        raise ValueError('Host inventory exceeds inspection budget')
    raw = path.read_bytes()
    data = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(data, dict) or not isinstance(data.get('installed'), list):
        raise ValueError('Invalid Codex plugin inventory')
    plugin_id = name + '@' + marketplace
    matches = []
    for row in data['installed']:
        if not isinstance(row, dict):
            raise ValueError('Invalid installed plugin record')
        # Matching IDs must also agree with the explicit component identities.
        if row.get('pluginId') != plugin_id:
            continue
        if row.get('name') != name or row.get('marketplaceName') != marketplace:
            raise ValueError('Inconsistent plugin identity')
        if (type(row.get('installed')) is not bool or type(row.get('enabled')) is not bool
                or not isinstance(row.get('version'), str) or not row['version'].strip()
                or (row['enabled'] and not row['installed'])):
            raise ValueError('Invalid installed plugin state')
        matches.append(row)
    if len(matches) > 1:
        raise ValueError('Target plugin inventory is ambiguous')
    row = matches[0] if matches else None
    return {
        'kind': 'provided-codex-plugin-inventory',
        'inventory_sha256': hashlib.sha256(raw).hexdigest(),
        'plugin_id': plugin_id,
        'selected_package_version': version,
        'record_present': row is not None,
        'state': 'record_observed' if row is not None else 'not_listed_in_supplied_inventory',
        'reported_installed': row['installed'] if row else None,
        'reported_enabled': row['enabled'] if row else None,
        'reported_version': row['version'] if row else None,
        'package_version_matched': bool(row and row['version'] == version),
        'host_version': 'unreported',
        'hook_trust': 'not established', 'hook_execution': 'not established',
        'context_delivery': 'not established', 'agent_use': 'not established',
        'semantic_review': 'not established', 'business_acceptance': 'not established',
        'limits': 'Unsigned supplied snapshot; capture time, freshness and completeness are not authenticated. '
                  'Absence is not global uninstall evidence. Matching version does not bind cache bytes '
                  'or prove hooks, context delivery, agent adoption, semantics or business acceptance.',
    }


def inspect_codex_version(path: Path) -> dict:
    """Optional caller-captured `codex --version` stdout, separate from inventory."""
    if path.stat().st_size > 512:
        raise ValueError('Host version exceeds inspection budget')
    raw = path.read_bytes()
    text = raw.decode('utf-8-sig').strip()
    if not text.startswith('codex-cli ') or not text[10:].strip() or any(ord(c) < 32 for c in text):
        raise ValueError('Invalid Codex version output')
    return {'reported': text, 'stdout_sha256': hashlib.sha256(raw).hexdigest(),
            'limits': 'Caller-supplied unsigned version stdout, not execution attestation.'}


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


def canonical_source_bytes(data: bytes) -> bytes:
    """Decode the receipt's fixed text format without loading package code.

    This deliberately mirrors the builder's three-line format operation so an
    inspector never imports or runs the candidate package to verify its bytes.
    """
    data.decode('utf-8')
    result = data.replace(b'\r\n', b'\n')
    if b'\r' in result:
        raise ValueError('Lone CR is not supported by the source byte policy')
    return result


def inspect(package: Path, source: Path | None = None) -> dict:
    package = package.resolve()
    report = {'schema_version': 1, 'package_valid': False, 'issues': [],
              'installation': 'unverified', 'hook_trust': 'unverified',
              'hook_execution': 'unverified', 'context_delivery': 'unverified',
              'agent_use': 'unverified', 'semantic_review': 'unverified',
              'business_acceptance': 'unverified'}
    try:
        receipt = json.loads((package / 'PACKAGE-SOURCES.json').read_text(encoding='utf-8'))
        if not isinstance(receipt, dict):
            raise ValueError('Receipt must be an object')
        schema = receipt.get('schema_version')
        if type(schema) is not int or schema not in (1, 2) or not isinstance(receipt.get('files'), dict):
            raise ValueError('Unsupported package receipt')
        normalized = schema == 2
        projection = receipt.get('root_manifest_projection', 'canonical-identity-v1')
        if projection not in ('canonical-identity-v1', 'portable-openai-hooks-v1'):
            raise ValueError('Unsupported root manifest projection')
        with_hooks = receipt.get('lifecycle_hooks', False)
        if type(with_hooks) is not bool:
            raise ValueError('Invalid hook package profile')
        if projection == 'portable-openai-hooks-v1' and (not normalized or not with_hooks):
            raise ValueError('Portable hook projection requires a normalized hook profile')
        report['root_manifest_projection'] = projection
        hook_inputs = {'hooks/codex.json', 'hooks/claude.json'} if with_hooks else set()
        support_names = {'plugin.json', 'LICENSE', 'scripts/plugin_doctor.py'} | hook_inputs
        report['hook_configuration'] = 'optional definitions present; trust and execution unverified' if with_hooks else 'not included'
        if normalized:
            if receipt.get('source_byte_policy') != SOURCE_BYTE_POLICY:
                raise ValueError('Unsupported source byte policy')
            source_inputs = receipt.get('source_input_files')
            skill_inputs = receipt.get('canonical_skill_files')
            support_inputs = receipt.get('canonical_support_files')
            if not all(isinstance(x, dict) for x in (source_inputs, skill_inputs, support_inputs)):
                raise ValueError('Missing source input provenance')
            if set(source_inputs) != set(skill_inputs) | set(support_inputs):
                raise ValueError('Incomplete source input provenance')
        if not isinstance(receipt.get('name'), str) or not isinstance(receipt.get('version'), str):
            raise ValueError('Receipt identity must contain strings')
        report.update(name=receipt['name'], version=receipt['version'])
        expected = receipt['files']
        required = {'plugin.json', 'LICENSE', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json',
                    'skills/project-wiki/SKILL.md', 'skills/project-wiki/scripts/wiki.py', 'scripts/plugin_doctor.py'}
        if with_hooks:
            required |= hook_inputs | {'skills/project-wiki/scripts/lifecycle.py', 'skills/project-wiki/scripts/workflow.py'}
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
        # Bind the payload inventory back to its canonical inputs, rather than
        # accepting an independently rehashed files[] as proof of source closure.
        skill_sources = receipt.get('canonical_skill_files')
        if not isinstance(skill_sources, dict):
            raise ValueError('Canonical skill inventory is missing')
        projected = set()
        for name, sha in skill_sources.items():
            rel = PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts or '\\' in name or rel.parts[:1] != ('project-wiki',) or rel.as_posix() != name:
                raise ValueError('Unsafe canonical source entry')
            target = 'skills/project-wiki/' + '/'.join(rel.parts[1:])
            projected.add(target)
            if expected.get(target) != sha:
                raise ValueError('Payload does not match canonical skill projection')
        supports = receipt.get('canonical_support_files')
        if supports is not None:
            if not isinstance(supports, dict) or set(supports) != support_names:
                raise ValueError('Invalid canonical support input inventory')
            for name in {'LICENSE', 'scripts/plugin_doctor.py'} | hook_inputs:
                if expected.get(name) != supports[name]:
                    raise ValueError('Payload does not match canonical support projection')
        if set(expected) != projected | support_names | {'.claude-plugin/plugin.json', '.codex-plugin/plugin.json'}:
            raise ValueError('Payload contains an unbound projection')
        package_identity = json.loads((package / 'plugin.json').read_text(encoding='utf-8'))
        if not isinstance(package_identity, dict) or package_identity.get('name') != receipt['name'] or package_identity.get('version') != receipt['version']:
            raise ValueError('Package identity does not match receipt')
        canonical_identity = receipt.get('canonical_identity') if normalized else package_identity
        if normalized:
            if not isinstance(canonical_identity, dict):
                raise ValueError('Canonical identity must be an object')
            expected_identity = canonical_identity
            if projection == 'portable-openai-hooks-v1':
                # Data-only mirror of the declared projection; do not import or
                # execute package builder/hook code while inspecting its bytes.
                extensions = canonical_identity.get('extensions', {})
                if not isinstance(extensions, dict) or not isinstance(extensions.get('com.openai', {}), dict):
                    raise ValueError('Invalid canonical OpenAI extension')
                expected_identity = {**canonical_identity, 'extensions': {**extensions, 'com.openai': {
                    **extensions.get('com.openai', {}), 'hooks': './hooks/codex.json'}}}
            if package_identity != expected_identity:
                raise ValueError('Package identity does not match canonical projection')
        host_identity = {key: package_identity[key] for key in ('name', 'version', 'description', 'author', 'license')}
        for host in ('claude', 'codex'):
            manifest = json.loads((package / f'.{host}-plugin/plugin.json').read_text(encoding='utf-8'))
            overlay = {'hooks': './hooks/' + host + '.json'} if with_hooks else {}
            if manifest != {**host_identity, 'skills': './skills/', **overlay}:
                raise ValueError('Host manifest does not match canonical projection')
        report['package_valid'] = not report['issues']
        if source is not None:
            try:
                source = source.resolve()
                report['source_comparison'] = SOURCE_BYTE_POLICY if normalized else 'raw-bytes-v1'
                def source_digest(path: Path) -> str | None:
                    data = path.read_bytes()
                    if normalized:
                        try:
                            data = canonical_source_bytes(data)
                        except (UnicodeError, ValueError):
                            report.setdefault('source_text_errors', []).append(path.relative_to(source).as_posix())
                            return None
                    return hashlib.sha256(data).hexdigest()
                mismatches = []
                for name, sha in receipt['canonical_skill_files'].items():
                    rel = PurePosixPath(name)
                    if rel.is_absolute() or '..' in rel.parts or '\\' in name or rel.parts[:1] != ('project-wiki',):
                        raise ValueError('Unsafe canonical source entry')
                    path = source / name
                    if path.is_symlink() or not path.resolve().is_relative_to(source):
                        raise ValueError('Source entry escapes checkout')
                    if not path.is_file() or source_digest(path) != sha:
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
                    if not isinstance(support, dict) or set(support) != support_names:
                        raise ValueError('Invalid canonical support input inventory')
                    support_mismatches = []
                    for name, expected_hash in support.items():
                        path = source / name
                        if path.is_symlink() or not path.resolve().is_relative_to(source):
                            raise ValueError('Canonical support input escapes checkout')
                        if not path.is_file() or source_digest(path) != expected_hash:
                            support_mismatches.append(name)
                    report['source_support_match'] = not support_mismatches
                    report['source_support_mismatches'] = support_mismatches
                if normalized:
                    # Keys were checked against exactly the validated canonical inventories above.
                    raw_mismatches = []
                    for name, expected_hash in source_inputs.items():
                        path = source / name
                        if path.is_symlink() or not path.resolve().is_relative_to(source):
                            raise ValueError('Source input escapes checkout')
                        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
                            raw_mismatches.append(name)
                    report['source_input_bytes_match'] = not raw_mismatches
                    report['source_input_byte_mismatches'] = raw_mismatches
                identity = json.loads((source / 'plugin.json').read_text(encoding='utf-8'))
                if not isinstance(identity, dict):
                    raise ValueError('Source identity must be an object')
                report['source_version'] = identity.get('version')
                report['source_identity_match'] = (identity == canonical_identity)
            except (OSError, ValueError, KeyError, TypeError) as error:
                report['source_match'] = False
                report['source_support_match'] = False
                report['source_identity_match'] = False
                report['source_error'] = type(error).__name__ + ': source inspection failed'
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
    parser.add_argument('--codex-inventory', type=Path, help='Read saved `codex plugin list --json` stdout; no host commands are executed')
    parser.add_argument('--codex-marketplace', help='Explicit marketplace identity for the selected plugin; required with --codex-inventory')
    parser.add_argument('--codex-version-file', type=Path, help='Optional saved `codex --version` stdout, only with --codex-inventory')
    args = parser.parse_args()
    if bool(args.codex_inventory) != bool(args.codex_marketplace):
        parser.error('--codex-inventory and --codex-marketplace must be provided together')
    if args.codex_version_file and not args.codex_inventory:
        parser.error('--codex-version-file requires --codex-inventory')
    report = inspect(args.package, args.source)
    if args.codex_inventory is not None:
        if not report['package_valid']:
            report['codex_observation'] = {'error': 'Package integrity must pass before matching host inventory'}
        else:
            try:
                observation = inspect_codex_inventory(args.codex_inventory, report['name'], report['version'], args.codex_marketplace)
                if args.codex_version_file is not None:
                    observation['host_version'] = inspect_codex_version(args.codex_version_file)
                report['codex_observation'] = observation
            except (OSError, ValueError, KeyError, TypeError, UnicodeError):
                report['codex_observation'] = {'error': 'Supplied Codex inventory/version unavailable or invalid; host state remains unverified'}
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
