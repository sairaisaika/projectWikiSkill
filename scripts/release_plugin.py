"""Plan a no-hooks PWS release; publication is opt-in, main-only and fail-closed.

The existing builder/doctor own package contents. No PR artifacts, downloaded
code, host configuration or installation is used. Local --bundle is write-new.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import urllib.parse
import zipfile

sys.dont_write_bytecode = True
import package_plugin as builder
import plugin_doctor as doctor
from pws_sync import REPOSITORY, REPOSITORY_ID, SHA, sha256, read_receipt

ROOT = Path(__file__).resolve().parents[1]
API = 'https://api.github.com/repos/' + REPOSITORY
EXPECTED_JOBS = {f'check ({os_name}, {version})' for os_name in
                 ('ubuntu-latest', 'windows-latest', 'macos-latest') for version in ('3.10', '3.13')}


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def semver(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', value):
        raise ValueError('A numeric three-part release version is required')
    return tuple(int(x) for x in value.split('.'))


def distribution(source: Path, package: Path) -> dict:
    receipt = builder.build(package, source)  # canonical no-hooks profile
    report = doctor.inspect(package, source)
    if not all(report.get(key) is True for key in ('package_valid', 'source_match',
               'source_support_match', 'source_input_bytes_match', 'source_identity_match')):
        raise ValueError('Package/source verification failed')
    identity = receipt['canonical_identity']
    catalog = json.loads((source / '.claude-plugin/marketplace.json').read_text(encoding='utf-8'))
    if catalog['plugins'] != [{**{k: identity[k] for k in ('name', 'version', 'description')},
                              'source': './', 'skills': ['./project-wiki/']}]:
        raise ValueError('Marketplace and canonical manifest disagree')
    semver(identity['version'])
    # Derive the input closure from the existing builder, never a second inventory.
    # Remove only version identity to distinguish a real input change from a bump.
    identity_without_version = {k: v for k, v in identity.items() if k != 'version'}
    catalog['plugins'][0].pop('version')
    inputs = {**receipt['canonical_skill_files'], **receipt['canonical_support_files']}
    inputs['plugin.json'] = sha256(builder.json_bytes(identity_without_version))
    inputs['.claude-plugin/marketplace.json'] = sha256(builder.json_bytes(catalog))
    # A projection implementation change also needs review/versioning, even when
    # it happens to produce the same bytes for today's inputs.
    inputs['scripts/package_plugin.py'] = sha256(builder.canonical_source_bytes(
        (source / 'scripts/package_plugin.py').read_bytes()))
    return {'version': identity['version'], 'inputs_sha256': sha256(builder.json_bytes(inputs)),
            'package_receipt': receipt}


@contextmanager
def snapshot(source: Path, commit: str):
    """Materialize exact tracked blobs, ignoring checkout files and archive attributes."""
    if not SHA.fullmatch(commit):
        raise ValueError('Exact commit required')
    with tempfile.TemporaryDirectory() as tmp:
        root = (Path(tmp) / 'source').resolve()  # macOS temporary roots may have aliases
        root.mkdir()
        listing = subprocess.check_output(['git', '-C', str(source), 'ls-tree', '-rz', '--full-tree', commit])
        entries = []
        for entry in listing.split(b'\0'):
            if not entry:
                continue
            metadata, raw_name = entry.split(b'\t', 1)
            mode, kind, object_id = metadata.decode('ascii').split()
            name = raw_name.decode('utf-8')
            relative = PurePosixPath(name)
            if (mode not in ('100644', '100755') or kind != 'blob'
                    or not SHA.fullmatch(object_id) or relative.is_absolute()
                    or '..' in relative.parts or '\\' in name or relative.as_posix() != name):
                raise ValueError('Unsupported tracked path, alias or submodule')
            entries.append((name, object_id))
        raw = subprocess.check_output(['git', '-C', str(source), 'cat-file', '--batch'],
                                      input=''.join(oid + '\n' for _, oid in entries).encode('ascii'))
        offset = 0
        for name, oid in entries:
            end = raw.index(b'\n', offset)
            actual_oid, kind, length = raw[offset:end].decode('ascii').split()
            size = int(length)
            start = end + 1
            data = raw[start:start + size]
            if actual_oid != oid or kind != 'blob' or len(data) != size or raw[start + size:start + size + 1] != b'\n':
                raise ValueError('Incomplete Git blob response')
            path = root / name
            if not path.resolve().is_relative_to(root):
                raise ValueError('Tracked path escapes snapshot')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            offset = start + size + 1
        if offset != len(raw):
            raise ValueError('Unexpected Git blob response')
        yield root


def describe_commit(source: Path, commit: str) -> dict:
    with snapshot(source, commit) as tree, tempfile.TemporaryDirectory() as tmp:
        return distribution(tree, Path(tmp) / 'package')


def bundle(source: Path, output: Path, commit: str) -> dict:
    if not SHA.fullmatch(commit) or git(source, 'rev-parse', 'HEAD') != commit:
        raise ValueError('Bundle source must be the exact checked-out commit')
    if git(source, 'status', '--porcelain', '--untracked-files=normal'):
        raise ValueError('Bundle source must be clean')
    if output.resolve().is_relative_to(source.resolve()) or output.exists():
        raise ValueError('Choose a new output outside the checkout')
    output.mkdir()
    with snapshot(source, commit) as tree:
        description = distribution(tree, output / 'package')
    archive_path = output / 'package.zip'
    with zipfile.ZipFile(archive_path, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((output / 'package').rglob('*')):
            if path.is_file():
                info = zipfile.ZipInfo(path.relative_to(output / 'package').as_posix(), (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
    receipt = {'schema_version': 1, 'repository': REPOSITORY, 'repository_id': REPOSITORY_ID,
               'source_commit': commit, 'version': description['version'], 'profile': 'no-hooks',
               'inputs_sha256': description['inputs_sha256'],
               'archive_sha256': sha256(archive_path.read_bytes()),
               'package_receipt': description['package_receipt'],
               'trust_boundary': 'Authenticate this receipt via the canonical GitHub release or independent review; hashes alone are not signatures.'}
    (output / 'release-receipt.json').write_bytes(builder.json_bytes(receipt))
    return receipt


def decision(current: dict, previous: dict | None, before: dict) -> str:
    if previous is None:
        return 'bootstrap_required'  # Never turn the existing version into a first release.
    changed = current['inputs_sha256'] != previous['inputs_sha256']
    version = semver(current['version'])
    prior = semver(previous['version'])
    if not changed:
        if version != prior:
            raise ValueError('Version-only changes are not a distribution release')
        return 'no_distribution_change'
    if version <= prior:
        raise ValueError('Changed distribution requires a reviewed increasing version in both manifests')
    if current['inputs_sha256'] == before['inputs_sha256']:
        raise ValueError('Unreleased earlier inputs require explicit review; no automatic backfill')
    if version <= semver(before['version']):
        raise ValueError('This push must include the reviewed version increase; no earlier bump reuse')
    return 'release'


class AssetRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlsplit(newurl)
        if parsed.scheme != 'https' or parsed.hostname not in (
                'release-assets.githubusercontent.com', 'objects.githubusercontent.com'):
            raise ValueError('Unexpected asset redirect')
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        redirected.remove_header('Authorization')
        return redirected


class GitHub:
    """Fixed-repository API adapter. No external URLs or downloaded code execution."""
    def __init__(self, token: str):
        self.token = token

    def request(self, path: str, method: str = 'GET', data=None, binary: bool = False):
        url = API + path
        headers = {'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + self.token,
                   'X-GitHub-Api-Version': '2022-11-28'}
        if binary:
            # Asset IDs come only from this verified repository's release object.
            headers['Accept'] = 'application/octet-stream'
        payload = json.dumps(data).encode() if data is not None else None
        opener = urllib.request.build_opener(AssetRedirect())
        with opener.open(urllib.request.Request(url, data=payload, headers=headers,
                                               method=method), timeout=30) as response:
            raw = response.read()
        return raw if binary else json.loads(raw)

    def upload(self, release_id: int, name: str, data: bytes):
        if name not in ('package.zip', 'release-receipt.json') or type(release_id) is not int:
            raise ValueError('Unexpected upload target')
        url = f'https://uploads.github.com/repos/{REPOSITORY}/releases/{release_id}/assets?name={name}'
        request = urllib.request.Request(url, data=data, method='POST', headers={
            'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/octet-stream',
            'Accept': 'application/vnd.github+json'})
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)


def bounded_list(api: GitHub, path: str) -> list:
    result = api.request(path + ('&' if '?' in path else '?') + 'per_page=100')
    if not isinstance(result, list) or len(result) >= 100:
        raise ValueError('Ambiguous or oversized release/PR inventory')
    return result


def guard(api: GitHub, source: Path, env: dict, event: dict) -> str:
    commit = env.get('GITHUB_SHA', '')
    if (env.get('GITHUB_REPOSITORY') != REPOSITORY or env.get('GITHUB_REPOSITORY_ID') != str(REPOSITORY_ID)
            or env.get('GITHUB_EVENT_NAME') != 'push' or env.get('GITHUB_REF') != 'refs/heads/main'
            or not SHA.fullmatch(commit) or event.get('after') != commit
            or event.get('ref') != 'refs/heads/main' or event.get('forced') is not False
            or event.get('deleted') is not False or event.get('repository', {}).get('id') != REPOSITORY_ID
            or not SHA.fullmatch(event.get('before', '')) or set(event['before']) == {'0'}):
        raise ValueError('Only an ordinary canonical main push is eligible')
    repo = api.request('')
    if repo['id'] != REPOSITORY_ID or repo['full_name'] != REPOSITORY or repo['visibility'] != 'public' or repo['default_branch'] != 'main':
        raise ValueError('Repository identity or audience changed')
    if api.request('/git/ref/heads/main')['object']['sha'] != commit or git(source, 'rev-parse', 'HEAD') != commit:
        raise ValueError('Stale main or checkout')
    subprocess.run(['git', '-C', str(source), 'merge-base', '--is-ancestor', event['before'], commit], check=True)
    if git(source, 'status', '--porcelain', '--untracked-files=normal'):
        raise ValueError('Checkout is not clean')
    pulls = bounded_list(api, '/commits/' + commit + '/pulls')
    if not any(p.get('merged_at') and p.get('merge_commit_sha') == commit
               and p['base']['ref'] == 'main' and p['base']['repo']['id'] == REPOSITORY_ID for p in pulls):
        raise ValueError('Exact commit is not a confirmed merged PR into canonical main')
    run_id = env.get('GITHUB_RUN_ID', '')
    if not run_id.isdigit():
        raise ValueError('Missing workflow run')
    run = api.request('/actions/runs/' + run_id)
    if (run['event'] != 'push' or run['head_sha'] != commit or run['head_branch'] != 'main'
            or run['path'] != '.github/workflows/check.yml' or run['repository']['id'] != REPOSITORY_ID):
        raise ValueError('Wrong workflow run identity')
    jobs = api.request('/actions/runs/' + run_id + '/jobs?per_page=100')
    if jobs['total_count'] >= 100:
        raise ValueError('Incomplete job inventory')
    checks = [j for j in jobs['jobs'] if j['name'] in EXPECTED_JOBS]
    if len(checks) != 6 or {j['name'] for j in checks} != EXPECTED_JOBS or any(j['conclusion'] != 'success' for j in checks):
        raise ValueError('All six exact-run matrix jobs must succeed')
    return commit


def released_receipt(api: GitHub, release: dict) -> dict:
    if release['draft'] or release['prerelease']:
        raise ValueError('Not a completed formal release')
    version = release['tag_name'].removeprefix('v')
    semver(version)
    if release['tag_name'] != 'v' + version:
        raise ValueError('Unexpected release tag')
    tag = api.request('/git/ref/tags/v' + version)['object']
    if tag['type'] != 'commit' or not SHA.fullmatch(tag['sha']):
        raise ValueError('Baseline needs an exact lightweight commit tag')
    assets = {a['name']: a for a in release['assets']}
    if len(assets) != len(release['assets']) or set(assets) != {'package.zip', 'release-receipt.json'}:
        raise ValueError('Incomplete or unexpected release assets')
    raw = api.request('/releases/assets/' + str(assets['release-receipt.json']['id']), binary=True)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'receipt.json'
        path.write_bytes(raw)
        receipt = read_receipt(path, sha256(raw))  # authenticated API is this trust boundary
    archive_digest = assets['package.zip'].get('digest')
    if (receipt['version'] != version or receipt['source_commit'] != tag['sha']
            or release['target_commitish'] != tag['sha']
            or archive_digest != 'sha256:' + receipt['archive_sha256']):
        raise ValueError('Release/tag/asset identity mismatch')
    return receipt


def inventory_identity(releases: list, own_id: int | None = None) -> list:
    """Release baseline identity, excluding only this attempt's separately verified draft."""
    records = []
    for item in releases:
        if item['id'] == own_id:
            continue
        records.append({key: item[key] for key in
                        ('id', 'tag_name', 'target_commitish', 'draft', 'prerelease')})
        records[-1]['assets'] = sorted(
            ({key: asset.get(key) for key in ('id', 'name', 'digest')} for asset in item['assets']),
            key=lambda asset: asset['id'])
    return sorted(records, key=lambda item: item['id'])


def recheck_baseline(api: GitHub, initial: list, baseline_release: dict,
                     previous: dict, own_id: int | None = None) -> None:
    live = bounded_list(api, '/releases')
    if (inventory_identity(live, own_id) != inventory_identity(initial)
            or released_receipt(api, baseline_release) != previous):
        raise ValueError('Release baseline changed; stop for independent review')


def run_github(api: GitHub, source: Path, env: dict, event: dict, publish: bool = False) -> dict:
    commit = guard(api, source, env, event)
    releases = bounded_list(api, '/releases')
    formal = [r for r in releases if not r['draft'] and not r['prerelease']]
    # Unrecognized formal releases are not silently skipped as older history.
    formal.sort(key=lambda r: semver(r['tag_name'].removeprefix('v')), reverse=True)
    if len({r['tag_name'] for r in formal}) != len(formal):
        raise ValueError('Ambiguous formal release inventory')
    previous = released_receipt(api, formal[0]) if formal else None
    current = describe_commit(source, commit)
    before = describe_commit(source, event['before'])
    if previous:
        subprocess.run(['git', '-C', str(source), 'merge-base', '--is-ancestor', previous['source_commit'], commit], check=True)
        baseline = describe_commit(source, previous['source_commit'])
        if (baseline['inputs_sha256'] != previous['inputs_sha256']
                or baseline['package_receipt'] != previous['package_receipt']):
            raise ValueError('Baseline cannot be reproduced by current canonical builder')
        if previous['source_commit'] == commit:
            return {'status': 'already_released', 'source_commit': commit, 'published': False}
    status = decision(current, previous, before)
    if status != 'release':
        return {'status': status, 'source_commit': commit, 'published': False}
    tag = 'v' + current['version']
    # Drafts, tags or partial failed releases are never resumed/overwritten blindly.
    if any(r['tag_name'] == tag for r in releases):
        raise ValueError('Version already has a release or draft')
    try:
        api.request('/git/ref/tags/' + tag)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
    else:
        raise ValueError('Version already has a tag; manual recovery required')
    if not publish or env.get('PWS_RELEASE_ENABLED') != 'true':
        return {'status': 'ready_dry_run' if not publish else 'publication_disabled', 'source_commit': commit, 'published': False}
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / 'bundle'
        receipt = bundle(source, output, commit)
        if any(receipt[key] != current[key] for key in ('version', 'inputs_sha256', 'package_receipt')):
            raise ValueError('Bundle differs from approved descriptor')
        guard(api, source, env, event)  # recheck live main, permissions boundary and CI before first write
        recheck_baseline(api, releases, formal[0], previous)
        api.request('/git/refs', 'POST', {'ref': 'refs/tags/' + tag, 'sha': commit})
        release = api.request('/releases', 'POST', {'tag_name': tag, 'target_commitish': commit,
                    'name': tag, 'draft': True, 'prerelease': False,
                    'body': 'No-hooks package from ' + commit + '. Verify release-receipt.json before comparing or installing.'})
        for name in ('package.zip', 'release-receipt.json'):
            data = (output / name).read_bytes()
            asset = api.upload(release['id'], name, data)
            if asset.get('state') != 'uploaded' or asset.get('digest') != 'sha256:' + sha256(data):
                raise ValueError('Upload not verified; draft retained for manual recovery')
        guard(api, source, env, event)
        recheck_baseline(api, releases, formal[0], previous, release['id'])
        pending = api.request('/releases/' + str(release['id']))
        if not pending['draft'] or released_receipt(api, {**pending, 'draft': False}) != receipt:
            raise ValueError('Draft or assets changed before publication')
        api.request('/releases/' + str(release['id']), 'PATCH', {'draft': False, 'make_latest': 'true'})
        completed = api.request('/releases/' + str(release['id']))
        if released_receipt(api, completed) != receipt:
            raise ValueError('Publication readback differs; outcome needs inspection')
    return {'status': 'released', 'source_commit': commit, 'version': receipt['version'], 'published': True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--github', action='store_true', help='Read live event/release metadata; default is dry run')
    mode.add_argument('--bundle', type=Path, help='Write a new local offline bundle; does not publish')
    parser.add_argument('--publish', action='store_true', help='Also requires the reviewed workflow enable switch')
    args = parser.parse_args()
    try:
        if args.bundle:
            if args.publish:
                raise ValueError('Local bundle cannot publish')
            receipt = bundle(ROOT, args.bundle, git(ROOT, 'rev-parse', 'HEAD'))
            result = {'status': 'local_bundle_only', 'source_commit': receipt['source_commit'],
                      'trusted_receipt_sha256': sha256((args.bundle / 'release-receipt.json').read_bytes()),
                      'published': False}
        else:
            event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
            result = run_github(GitHub(os.environ['GH_TOKEN']), ROOT, dict(os.environ), event, args.publish)
        print(json.dumps(result))
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.CalledProcessError):
        # Never echo tokens, raw responses, payloads or local private paths.
        print(json.dumps({'status': 'blocked',
                          'published': None if args.github and args.publish and os.environ.get('PWS_RELEASE_ENABLED') == 'true' else False,
                          'reason': 'gate or API failed; publication may be uncertain after a write; inspect remote tag/draft/release before retry'}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
