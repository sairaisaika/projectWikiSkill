"""pws-sync --check: offline package comparison, never an installer.

Run this checker from a reviewed checkout, never from the candidate package.
A caller-pinned release receipt is the trust input; hashes alone prove no origin.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

# Checking must not even create Python's import cache beside this trusted tool.
sys.dont_write_bytecode = True
import plugin_doctor

REPOSITORY = 'sairaisaika/projectWikiSkill'
REPOSITORY_ID = 1466210381
SHA = re.compile(r'[0-9a-f]{40}')
DIGEST = re.compile(r'[0-9a-f]{64}')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_receipt(path: Path, trusted_digest: str) -> dict:
    if not DIGEST.fullmatch(trusted_digest) or path.is_symlink():
        raise ValueError('Invalid trust pin or aliased receipt')
    raw = path.read_bytes()
    if sha256(raw) != trusted_digest:
        raise ValueError('Receipt differs from independently trusted digest')
    receipt = json.loads(raw)
    if (receipt['schema_version'] != 1 or receipt['repository'] != REPOSITORY
            or receipt['repository_id'] != REPOSITORY_ID
            or not SHA.fullmatch(receipt['source_commit'])
            or not re.fullmatch(r'\d+\.\d+\.\d+', receipt['version'])
            or receipt['profile'] != 'no-hooks'
            or not DIGEST.fullmatch(receipt['archive_sha256'])):
        raise ValueError('Unsupported release receipt')
    package = receipt['package_receipt']
    if (package['schema_version'] != 2 or package['name'] != 'project-wiki'
            or package['version'] != receipt['version']
            or package['lifecycle_hooks'] is not False
            or package['root_manifest_projection'] != 'canonical-identity-v1'
            or not package['files']):
        raise ValueError('Incomplete package receipt')
    # Identity/closure are not invented here: doctor validates actual package bytes.
    return receipt


def standalone_inventory(receipt: dict) -> dict:
    """Project the authenticated builder inventory; no alternate source manifest."""
    expected = {}
    for name, digest in receipt['package_receipt']['canonical_skill_files'].items():
        relative = PurePosixPath(name)
        if (relative.parts[:1] != ('project-wiki',) or len(relative.parts) < 2
                or '..' in relative.parts or '\\' in name or relative.as_posix() != name
                or not DIGEST.fullmatch(digest)):
            raise ValueError('Invalid canonical skill inventory')
        target = '/'.join(relative.parts[1:])
        if receipt['package_receipt']['files'].get('skills/project-wiki/' + target) != digest:
            raise ValueError('Unbound skill projection')
        expected[target] = digest
    projected = {name.removeprefix('skills/project-wiki/'): digest
                 for name, digest in receipt['package_receipt']['files'].items()
                 if name.startswith('skills/project-wiki/')}
    if not expected or 'SKILL.md' not in expected or projected != expected:
        raise ValueError('Incomplete skill projection')
    if receipt['package_receipt']['source_byte_policy'] != plugin_doctor.SOURCE_BYTE_POLICY:
        raise ValueError('Unsupported canonical byte policy')
    return expected


def standalone_check(target: Path, expected: dict) -> str:
    if (target.is_symlink() or not target.is_dir()
            or target.resolve() != target.absolute().parent.resolve() / target.name):
        return 'invalid_target'
    root = target.resolve()
    actual = {}
    for path in root.rglob('*'):
        # Refuse aliases even within ignored cache directories; never read them.
        if path.is_symlink() or path.resolve() != path.absolute():
            return 'invalid_target'
        relative = path.relative_to(root)
        # These are the builder's existing non-distribution cache exclusions.
        # No other extra files are silently accepted, and nothing is deleted.
        if any(part in ('__pycache__', '.pytest_cache') for part in relative.parts):
            continue
        if path.is_dir():
            continue
        if not path.is_file():
            return 'invalid_target'
        actual[relative.as_posix()] = path
    if set(actual) != set(expected):
        return 'invalid_target'
    hashes = {name: sha256(plugin_doctor.canonical_source_bytes(path.read_bytes()))
              for name, path in actual.items()}
    return 'same' if hashes == expected else 'different'


def check(target: Path, candidate: Path | None, trusted_digest: str | None,
          target_kind: str = 'package') -> dict:
    result = {'status': 'no_trusted_input', 'installation': 'not performed',
              'session_loading': 'unverified', 'network': 'not used',
              'trust': 'caller must independently authenticate the pinned receipt',
              'target_kind': target_kind, 'comparison': 'files only; host loading is not observed'}
    if candidate is None or trusted_digest is None:
        return result
    try:
        if candidate.is_symlink() or candidate.resolve() != candidate.absolute().parent.resolve() / candidate.name:
            raise ValueError('Aliased candidate')
        directory = candidate.is_dir()
        receipt = read_receipt(candidate / 'release-receipt.json' if directory else candidate,
                               trusted_digest)
        expected = receipt['package_receipt']
        skill_expected = standalone_inventory(receipt)
        if target_kind not in ('package', 'standalone-skill'):
            raise ValueError('Unsupported target kind')
        result.update(version=receipt['version'], source_commit=receipt['source_commit'],
                      candidate_verification='package bytes' if directory else 'pinned receipt only')
        if directory:
            package = candidate / 'package'
            if package.is_symlink() or not plugin_doctor.inspect(package)['package_valid']:
                raise ValueError('Candidate package invalid')
            if json.loads((package / 'PACKAGE-SOURCES.json').read_text(encoding='utf-8')) != expected:
                raise ValueError('Candidate receipt differs')
            archive = candidate / 'package.zip'
            if not archive.is_file() or archive.is_symlink() or sha256(archive.read_bytes()) != receipt['archive_sha256']:
                raise ValueError('Candidate archive differs')
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return {**result, 'status': 'invalid_candidate'}
    try:
        if not target.exists() and not target.is_symlink():
            return {**result, 'status': 'not_installed'}
        if target_kind == 'standalone-skill':
            return {**result, 'status': standalone_check(target, skill_expected),
                    'ignored_existing_cache_names': ['__pycache__', '.pytest_cache'],
                    'byte_policy': plugin_doctor.SOURCE_BYTE_POLICY}
        if (target.is_symlink() or target.resolve() != target.absolute().parent.resolve() / target.name
                or not plugin_doctor.inspect(target)['package_valid']):
            return {**result, 'status': 'invalid_target'}
        actual = json.loads((target / 'PACKAGE-SOURCES.json').read_text(encoding='utf-8'))
    except (OSError, ValueError, KeyError, TypeError):
        return {**result, 'status': 'invalid_target'}
    # Full receipt equality includes complete inventories and source provenance;
    # equal version strings alone can never mean equal bytes.
    return {**result, 'status': 'same' if actual == expected else 'different'}


def main() -> int:
    parser = argparse.ArgumentParser(prog='pws-sync', description=__doc__)
    parser.add_argument('--check', required=True, action='store_true')
    parser.add_argument('--target', required=True, type=Path, help='Explicit local target directory')
    parser.add_argument('--target-kind', choices=('package', 'standalone-skill'), default='package')
    parser.add_argument('--candidate', type=Path, help='Offline bundle directory or release-receipt.json')
    parser.add_argument('--trusted-receipt-sha256', help='Digest obtained through an independently trusted channel')
    args = parser.parse_args()
    result = check(args.target, args.candidate, args.trusted_receipt_sha256, args.target_kind)
    print(json.dumps(result, ensure_ascii=True))
    return 0 if result['status'] == 'same' else 1 if result['status'] in ('different', 'not_installed') else 2


if __name__ == '__main__':
    sys.exit(main())
