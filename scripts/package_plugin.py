"""Build an internal plugin from the canonical skill; no host configuration writes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {'__pycache__', '.pytest_cache'}
PAYLOAD_SUFFIXES = {'.md', '.py', '.yaml', '.yml', '.json'}
SOURCE_BYTE_POLICY = 'utf8-crlf-to-lf-v1'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_source_bytes(data: bytes) -> bytes:
    """The format's sole text transform: validate UTF-8 and replace CRLF pairs.

    Other bytes, including literal backslash escapes, are retained; lone CR fails.
    Raw inputs are separately hashed for build freshness; package bytes stay strict.
    """
    data.decode('utf-8')
    result = data.replace(b'\r\n', b'\n')
    if b'\r' in result:
        raise ValueError('Lone CR is not supported by the source byte policy')
    return result


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def build(output: Path, source: Path = ROOT) -> dict:
    source, output = source.resolve(), output.resolve()
    if output.is_relative_to(source):
        raise ValueError('Build outside the source checkout; do not package into canonical inputs')
    if output.exists():
        raise ValueError('Output already exists; choose a new candidate directory')
    if not output.parent.is_dir():
        raise ValueError('Output parent must already exist')
    if any((source / name).is_symlink() for name in ('plugin.json', 'LICENSE', 'project-wiki')):
        raise ValueError('Canonical package roots must not be symlinks')
    identity = json.loads((source / 'plugin.json').read_text(encoding='utf-8'))
    if not isinstance(identity, dict) or not isinstance(identity.get('name'), str) or not isinstance(identity.get('version'), str):
        raise ValueError('Plugin name and version must be strings in an object')
    if not re.fullmatch(r'[a-z][a-z0-9-]*', identity['name']):
        raise ValueError('Invalid plugin identity')
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[\w.-]+)?', identity['version']):
        raise ValueError('Invalid plugin version')
    skill = source / 'project-wiki'
    if not (skill / 'SKILL.md').is_file():
        raise ValueError('Canonical skill entry is missing')
    payload = {}
    source_hashes = {}
    input_hashes = {}
    for path in sorted(skill.rglob('*')):
        # Even a link to a file inside the skill is refused: archives must stand alone.
        if path.is_symlink():
            raise ValueError('Symlinks are not plugin payload')
        if any(part in IGNORED_PARTS for part in path.relative_to(skill).parts):
            continue
        if not path.is_file():
            continue
        if path.suffix not in PAYLOAD_SUFFIXES or any(part.startswith('.') for part in path.relative_to(skill).parts):
            raise ValueError('Unlisted or hidden file in canonical skill payload')
        target = 'skills/project-wiki/' + path.relative_to(skill).as_posix()
        raw = path.read_bytes()
        name = path.relative_to(source).as_posix()
        input_hashes[name] = digest(raw)
        data = canonical_source_bytes(raw)
        payload[target] = data
        source_hashes[name] = digest(data)
    support = ('plugin.json', 'LICENSE', 'scripts/plugin_doctor.py')
    for name in support:
        path = source / name
        if path.is_symlink() or not path.resolve().is_relative_to(source):
            raise ValueError('Canonical package support input escapes checkout')
    support_inputs = {name: (source / name).read_bytes() for name in support}
    input_hashes.update({name: digest(data) for name, data in support_inputs.items()})
    support_bytes = {name: canonical_source_bytes(data) for name, data in support_inputs.items()}
    if json.loads(support_bytes['plugin.json']) != identity:
        raise ValueError('Canonical identity changed during build')
    support_hashes = {name: digest(data) for name, data in support_bytes.items()}
    payload['plugin.json'] = json_bytes(identity)
    payload['LICENSE'] = support_bytes['LICENSE']
    payload['scripts/plugin_doctor.py'] = support_bytes['scripts/plugin_doctor.py']
    host_identity = {key: identity[key] for key in ('name', 'version', 'description', 'author', 'license')}
    payload['.claude-plugin/plugin.json'] = json_bytes({**host_identity, 'skills': './skills/'})
    payload['.codex-plugin/plugin.json'] = json_bytes({**host_identity, 'skills': './skills/'})
    receipt = {
        'schema_version': 2,
        'source_byte_policy': SOURCE_BYTE_POLICY,
        'canonical_identity': identity,
        'source_input_files': dict(sorted(input_hashes.items())),
        'name': identity['name'],
        'version': identity['version'],
        'files': {name: digest(data) for name, data in sorted(payload.items())},
        'canonical_skill_files': source_hashes,
        'canonical_support_files': support_hashes,
        'limits': ['not installed or enabled', 'no hook configuration', 'no MCP server',
                   'hashes establish payload closure, not semantic correctness or host adoption'],
    }
    # Exclusive creation never replaces an existing installation. A partial output
    # lacks the final receipt and is rejected by doctor; no crash-atomic claim.
    output.mkdir()
    for name, data in payload.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    # Input closure includes additions, not just mutations of already-listed files.
    current_inputs = set(support)
    if any((source / name).is_symlink() for name in ('plugin.json', 'LICENSE', 'project-wiki')):
        raise ValueError('Canonical package inventory changed during build')
    for path in skill.rglob('*'):
        if path.is_symlink():
            raise ValueError('Canonical package inventory changed during build')
        if any(part in IGNORED_PARTS for part in path.relative_to(skill).parts):
            continue
        if path.is_file():
            current_inputs.add(path.relative_to(source).as_posix())
    if current_inputs != set(input_hashes):
        raise ValueError('Canonical package inventory changed during build')
    # Do not label a moving canonical input as a coherent snapshot.
    for name, expected in input_hashes.items():
        if digest((source / name).read_bytes()) != expected:
            raise ValueError('Canonical skill changed during build; output is incomplete')
    (output / 'PACKAGE-SOURCES.json').write_bytes(json_bytes(receipt))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        receipt = build(args.output)
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=True))
        return 1
    print(json.dumps({'ok': True, 'name': receipt['name'], 'version': receipt['version'],
                      'payload_files': len(receipt['files']), 'host_installation': 'not performed'}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
