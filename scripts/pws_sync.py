"""pws-sync --check: offline package comparison, never an installer.

Run this checker from a reviewed checkout, never from the candidate package.
A caller-pinned release receipt is the trust input; hashes alone prove no origin.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
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


def check(target: Path, candidate: Path | None, trusted_digest: str | None) -> dict:
    result = {'status': 'no_trusted_input', 'installation': 'not performed',
              'session_loading': 'unverified', 'network': 'not used',
              'trust': 'caller must independently authenticate the pinned receipt'}
    if candidate is None or trusted_digest is None:
        return result
    try:
        if candidate.is_symlink():
            raise ValueError('Aliased candidate')
        directory = candidate.is_dir()
        receipt = read_receipt(candidate / 'release-receipt.json' if directory else candidate,
                               trusted_digest)
        expected = receipt['package_receipt']
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
        if target.is_symlink() or not plugin_doctor.inspect(target)['package_valid']:
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
    parser.add_argument('--target', required=True, type=Path, help='Explicit installed package directory')
    parser.add_argument('--candidate', type=Path, help='Offline bundle directory or release-receipt.json')
    parser.add_argument('--trusted-receipt-sha256', help='Digest obtained through an independently trusted channel')
    args = parser.parse_args()
    result = check(args.target, args.candidate, args.trusted_receipt_sha256)
    print(json.dumps(result, ensure_ascii=True))
    return 0 if result['status'] == 'same' else 1 if result['status'] in ('different', 'not_installed') else 2


if __name__ == '__main__':
    sys.exit(main())
