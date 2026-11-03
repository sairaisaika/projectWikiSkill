"""Revision-bound native wiki context, delegation and diff reconciliation.

Capture and capture-return run an explicit caller-supplied native command, with
opt-in and no shell. Other operations inspect projections and Git, except saved-only
show views, which do not inspect live inputs; none edits project sources,
installs hooks, executes wiki check commands or certifies a worker's claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

MAX_REPORT = 4 * 1024 * 1024


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def report_hash(report: dict) -> str:
    return sha(json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8'))


def read_json(path: Path) -> dict:
    if path.stat().st_size > MAX_REPORT:
        raise ValueError('Report exceeds the 4 MiB transport budget; nothing was truncated')
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(value, dict):
        raise ValueError('Report must be an object')
    return value


def relative(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError('Expected a repository-relative path string')
    p = PurePosixPath(value)
    if not value or p.is_absolute() or '..' in p.parts or '\\' in value or ':' in value or p.as_posix() != value:
        raise ValueError('Expected a normalized repository-relative path')
    return value


def within(root: Path, name: str) -> Path:
    path = root / relative(name)
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Input escapes the selected checkout')
    return path


def file_hash(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(256 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def artifact_snapshot(paths: list[str] | None) -> dict[str, str]:
    """Hash only explicitly selected existing real files; never copy contents."""
    if paths is None:
        paths = []
    if not isinstance(paths, list) or not all(isinstance(x, str) and x and '\0' not in x for x in paths):
        raise ValueError('Preserved artifact selection must be a list of absolute file paths')
    result = {}
    # Ordinals follow this checkpoint's list, not necessarily original CLI order.
    for ordinal, name in enumerate(paths, 1):
        item = f' (selection item {ordinal})'
        path = Path(name)
        try:
            if not path.is_absolute() or '..' in path.parts or path.is_symlink():
                raise ValueError('Preserved artifact must be an absolute real file, not an alias' + item)
            resolved = path.resolve(strict=True)
            if path != resolved or not resolved.is_file():
                raise ValueError('Preserved artifact must be an existing real file' + item)
            digest = file_hash(resolved)
        except OSError as error:
            raise ValueError('Selected artifact is missing or unreadable' + item) from error
        if digest is None:
            raise ValueError('Selected artifact is not a file' + item)
        result[str(resolved)] = digest
    return dict(sorted(result.items()))


def artifact_fields(value: dict, *, native_paths: bool = True) -> tuple[list[str], dict[str, str]]:
    paths = value.get('preserve_artifacts', [])
    hashes = value.get('preserved_artifact_hashes', {})
    if (not isinstance(paths, list) or not all(isinstance(x, str) and x and '\0' not in x for x in paths)
            or paths != sorted(set(paths)) or not isinstance(hashes, dict) or set(hashes) != set(paths)):
        raise ValueError('Preserved artifact policy or saved hash record is invalid/missing')
    for name in paths:
        if native_paths and (not Path(name).is_absolute() or '..' in Path(name).parts):
            raise ValueError('Preserved artifact policy requires absolute paths')
        digest = hashes[name]
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Preserved artifact saved hash is invalid')
    return paths, hashes


def check_artifact_return(before: dict, after: dict) -> None:
    old_paths, old_hashes = artifact_fields(before)
    paths, hashes = artifact_fields(after)
    if old_paths != paths:
        raise ValueError('Preserved artifact selection differs between start and return')
    if old_hashes != hashes:
        raise ValueError('Preserved artifact bytes changed between start and return')


def artifact_observation(value: dict, status: str = 'captured', *, native_paths: bool = True) -> dict:
    try:
        paths, hashes = artifact_fields(value, native_paths=native_paths)
    except ValueError:
        return {'status': 'unavailable', 'meaning': 'Selected artifact hash record is invalid/missing; recapture before dispatch.'}
    return {'status': status if paths else 'not_requested', 'paths': paths,
            'captured_sha256': hashes, 'continuous_monitoring': False, 'write_prevention': False,
            'limits': 'Selected bytes at observation boundaries only. Not original provenance, continuous immutability, a sandbox, semantic accuracy or business acceptance. Unselected files and changes restored between observations are not detected.'}


def git(root: Path, *args: str) -> bytes:
    # Avoid user fsmonitor hooks and diff/pager helpers. No Git write commands.
    return subprocess.check_output(['git', '--no-pager', '-c', 'core.fsmonitor=false',
                                    '-c', 'core.quotepath=false', '-C', str(root), *args],
                                   stderr=subprocess.PIPE, timeout=30)


def head(root: Path) -> str:
    return git(root, 'rev-parse', '--verify', 'HEAD').decode().strip()


def untracked(root: Path) -> list[str]:
    return [x.decode('utf-8') for x in git(root, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0') if x]


def input_snapshot(root: Path, wiki_root: str, runtime_inputs: list[str]) -> dict:
    wiki = within(root, wiki_root)
    if not wiki.is_dir():
        raise ValueError('Native wiki directory is unavailable')
    paths = set(runtime_inputs)
    for path in wiki.rglob('*.md'):
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError('Wiki input escapes checkout')
        paths.add(path.relative_to(root).as_posix())
    hashes = {}
    for name in sorted(paths):
        path = within(root, name)
        if not path.is_file():
            raise ValueError('Declared wiki/runtime input is missing')
        hashes[name] = file_hash(path)
    return {'head': head(root), 'inputs': hashes}


def peer_snapshot(peers: dict[str, str]) -> dict:
    result = {}
    for alias, folder in peers.items():
        if '/' in relative(alias):
            raise ValueError('Peer alias must be one path component')
        path = Path(folder).resolve()
        available = path.is_dir()
        result[alias] = {'root': str(path), 'available': available, 'head': head(path) if available else None}
    return result


def check_peer_namespace(root: Path, peers: dict, root_files=()) -> None:
    """Keep one physical source per existing root/alias label; never guess precedence."""
    for alias in peers:
        if '/' in relative(alias):
            raise ValueError('Peer alias must be one path component')
        path = root / alias
        if (path.exists() or path.is_symlink()
                or any(relative(name).partition('/')[0] == alias for name in root_files)):
            raise ValueError('Root/peer namespace collision; select a distinct explicit peer alias and recapture')


def source_hash(root: Path, name: str, peers: dict) -> str | None:
    relative(name)
    check_peer_namespace(root, peers)
    alias, _, rest = name.partition('/')
    if alias in peers:
        peer = peers[alias]
        return file_hash(within(Path(peer['root']), rest)) if peer['available'] and rest else None
    return file_hash(within(root, name))


def validate_native(report: dict, query: str, files: list[str], root: Path, wiki_root: str) -> None:
    if report.get('query') != query:
        raise ValueError('Native query does not match the requested task')
    for name in ('cards', 'impact', 'omitted', 'placementIssues'):
        if not isinstance(report.get(name), list):
            raise ValueError('Unsupported native task-card report')
    if not isinstance(report.get('limits'), str) or not report['limits']:
        raise ValueError('Native evidence limits are required')
    actual = [row['file'] for row in report['impact']]
    if len(actual) != len(set(actual)) or set(actual) != set(files):
        raise ValueError('Native impact omitted or substituted requested files')
    wiki = within(root, wiki_root)
    for card in report['cards']:
        if not isinstance(card.get('title'), str):
            raise ValueError('Native card title is missing')
        if not within(wiki, card['path']).is_file():
            raise ValueError('Native feature page is unavailable')
    for row in report['impact']:
        relative(row['file'])
        if not isinstance(row.get('unregistered'), bool) or not isinstance(row.get('pages'), list):
            raise ValueError('Native registration state must be explicit')
        if not row['unregistered'] and not row['pages']:
            raise ValueError('Empty registered impact is not evidence of no impact')
        for page in row['pages']:
            if not within(wiki, page['path']).is_file():
                raise ValueError('Native satellite page is unavailable')


def compare_native_sources(report: dict, pointer: str | None, root: Path, head: str, peers: dict) -> dict:
    """Compare caller-selected native observations, not physical reads or deployment fitness.

    The optional JSON pointer is adapter configuration supplied by the caller, never
    a command taken from project text. Each selected record has root/revision; record
    labels are deliberately opaque so projects keep their native repository names.
    """
    if pointer is None:
        return {'status': 'not_requested', 'meaning': 'Native source observations have not been compared with declared checkouts.'}
    if not isinstance(pointer, str) or not pointer.startswith('/'):
        raise ValueError('Native source context requires a nonempty JSON pointer')
    observed = report
    for token in pointer[1:].split('/'):
        if any(not part or part[0] not in '01' for part in token.split('~')[1:]):
            raise ValueError('Native source context contains an invalid JSON pointer escape')
        token = token.replace('~1', '/').replace('~0', '~')
        if isinstance(observed, dict) and token in observed:
            observed = observed[token]
        elif (isinstance(observed, list) and token.isascii() and token.isdecimal()
              and (token == '0' or not token.startswith('0')) and int(token) < len(observed)):
            observed = observed[int(token)]
        else:
            raise ValueError('Declared native source context is unavailable')
    if not isinstance(observed, dict) or not observed:
        raise ValueError('Native source observations must be a nonempty object')
    selected = [('root', {'root': str(root.resolve()), 'head': head, 'available': True})]
    selected.extend(('peer:' + alias, row) for alias, row in peers.items())
    if any(not row['available'] for _, row in selected):
        raise ValueError('Selected checkout is unavailable for native source comparison')
    selected_roots = {str(Path(row['root']).resolve()) for _, row in selected}
    by_root = {}
    for row in observed.values():
        if not isinstance(row, dict) or not isinstance(row.get('root'), str) or not row['root']:
            continue  # Cannot satisfy a selected identity; unrelated optional context is not a gate.
        try:
            folder = str(Path(row['root']).resolve())
        except (OSError, ValueError):
            continue  # Malformed paths cannot satisfy a selected identity.
        if folder not in selected_roots:
            continue
        if not isinstance(row.get('revision'), str) or not row['revision']:
            raise ValueError('Native source identity is unavailable or malformed')
        revision = row['revision']
        if folder in by_root and by_root[folder] != revision:
            raise ValueError('Native source observations disagree about one checkout')
        by_root[folder] = revision
    matched = {}
    for alias, row in selected:
        folder = str(Path(row['root']).resolve())
        if by_root.get(folder) != row['head']:
            raise ValueError('Native source observation does not match a selected checkout')
        matched[alias] = {'root': folder, 'head': row['head']}
    return {'status': 'matched', 'pointer': pointer, 'checkouts': matched,
            'meaning': 'Reported checkout identities match selected snapshots; physical reads, correct deployment pairing, agent use and semantic accuracy remain unverified.'}


def capture(root: Path, query: str, files: list[str], program: list[str], runtime_inputs: list[str],
            *, wiki_root: str = 'docs/wiki', allow_execution: bool = False, peers: dict[str, str] | None = None,
            native_source_context: str | None = None, preserve_artifacts: list[str] | None = None,
            reviewed_runtime_inputs: dict[str, str] | None = None) -> dict:
    root = root.resolve()
    if not allow_execution:
        raise ValueError('Native execution requires explicit opt-in; wiki text is never executable configuration')
    if not isinstance(program, list) or not program or not all(isinstance(x, str) and x for x in program) or not runtime_inputs:
        raise ValueError('Declare native argv and its reviewed runtime inputs')
    if not query.strip() or query.startswith('-'):
        raise ValueError('A non-option task query is required')
    files = sorted(set(relative(f) for f in files))
    before = input_snapshot(root, wiki_root, runtime_inputs)
    if (reviewed_runtime_inputs is not None
            and (set(reviewed_runtime_inputs) != set(runtime_inputs)
                 or {name: before['inputs'].get(name) for name in runtime_inputs} != reviewed_runtime_inputs)):
        raise ValueError('Declared native runtime inputs differ from the reviewed return baseline')
    peer_before = peer_snapshot(peers or {})
    check_peer_namespace(root, peer_before)
    artifact_before = artifact_snapshot(preserve_artifacts)
    if (reviewed_runtime_inputs is not None
            and any(file_hash(within(root, name)) != old for name, old in reviewed_runtime_inputs.items())):
        raise ValueError('Declared native runtime inputs changed before native execution')
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        result = subprocess.run([*program, query, '--json', '--files', *files], cwd=root,
                                stdout=stdout, stderr=stderr, timeout=60, shell=False)
        if stdout.tell() > MAX_REPORT:
            raise ValueError('Native report exceeds budget; no context was silently truncated')
        stdout.seek(0)
        raw = stdout.read()
        # Never reflect native exception text or ambient credentials into a packet.
        stderr_bytes = stderr.tell()
    after = input_snapshot(root, wiki_root, runtime_inputs)
    if artifact_before != artifact_snapshot(list(artifact_before)):
        raise ValueError('Preserved artifact changed during native capture')
    if before != after or peer_before != peer_snapshot(peers or {}):
        raise ValueError('Wiki/runtime inputs changed during native capture; retry from a stable snapshot')
    report = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(report, dict):
        raise ValueError('Native report must be an object')
    validate_native(report, query, files, root, wiki_root)
    native_sources = compare_native_sources(report, native_source_context, root, before['head'], peer_before)
    return {'schema_version': 1, 'kind': 'native-wiki-capture', 'root': str(root),
            'wiki_root': wiki_root, 'query': query, 'files': files,
            'base': before, 'runtime_inputs': runtime_inputs,
            'native_argv': program, 'native_exit_code': result.returncode,
            'peers': peer_before,
            'baseline_peer_untracked': {alias: untracked(Path(row['root'])) if row['available'] else []
                                        for alias, row in peer_before.items()},
            'native_stderr_bytes': stderr_bytes, 'native_report_sha256': sha(raw),
            'native_report_canonical_sha256': report_hash(report),
            'native_report': report, 'baseline_untracked': untracked(root),
            'native_source_context': native_source_context, 'native_source_comparison': native_sources,
            'preserve_artifacts': list(artifact_before), 'preserved_artifact_hashes': artifact_before,
            'planned_source_hashes': {f: source_hash(root, f, peer_before) for f in files},
            'evidence': {'context_generated': True, 'context_delivered': 'unverified',
                         'agent_use': 'unverified', 'semantic_accuracy': 'unverified',
                         'runtime_acceptance': 'unverified'},
            'limits': ['native command may write its own local task stamp',
                       'declared runtime input closure, not an inferred import graph',
                       'unsigned local projection; not a trust or completion certificate']}


def check_capture(value: dict, *, require_current: bool = True) -> Path:
    if value.get('kind') != 'native-wiki-capture' or value.get('schema_version') != 1:
        raise ValueError('Expected a native wiki capture')
    root = Path(value['root']).resolve()
    artifact_paths, artifact_hashes = artifact_fields(value)
    if require_current and artifact_snapshot(artifact_paths) != artifact_hashes:
        raise ValueError('Preserved artifact changed after capture')
    if report_hash(value['native_report']) != value.get('native_report_canonical_sha256'):
        raise ValueError('Native context was changed after capture; regenerate instead of editing its projection')
    if require_current and input_snapshot(root, value['wiki_root'], value['runtime_inputs']) != value['base']:
        raise ValueError('Capture is stale for this checkout or wiki/runtime inputs')
    peers = value.get('peers', {})
    if require_current:
        check_peer_namespace(root, peers)
    if require_current and peers != peer_snapshot({alias: row['root'] for alias, row in peers.items()}):
        raise ValueError('Peer checkout identity changed after capture')
    if require_current and any(source_hash(root, name, peers) != old for name, old in value['planned_source_hashes'].items()):
        raise ValueError('Captured source files changed after capture')
    validate_native(value['native_report'], value['query'], value['files'], root, value['wiki_root'])
    expected_sources = compare_native_sources(value['native_report'], value.get('native_source_context'),
                                              root, value['base']['head'], peers)
    if value.get('native_source_context') is not None and 'native_source_comparison' not in value:
        raise ValueError('Strict native source comparison is missing; recapture before dispatch')
    if value.get('native_source_comparison', expected_sources) != expected_sources:
        raise ValueError('Native source comparison changed after capture')
    return root


def start(value: dict, task_id: str, owner: str, outcome: str, allowed: list[str],
          acceptance: list[str], capabilities: list[str], *, read_only: bool = False) -> dict:
    root = check_capture(value)
    if not all(isinstance(x, str) and x.strip() for x in [task_id, owner, outcome, *acceptance, *capabilities]):
        raise ValueError('Task identity, outcome and nonempty acceptance/capability entries are required')
    if not acceptance or not capabilities:
        raise ValueError('Explicit user-visible capabilities and exit evidence are required')
    allowed = sorted(set(relative(f) for f in allowed))
    if read_only and allowed:
        raise ValueError('Read-only tasks cannot grant editing paths')
    if not read_only and not allowed:
        raise ValueError('Editing tasks require explicit allowed files; use --read-only for a review')
    if not read_only and not set(value['files']).issubset(allowed):
        raise ValueError('Allowed files cannot omit the planned files')
    packet = {'schema_version': 1, 'kind': 'wiki-work-packet', 'task_id': task_id, 'owner': owner,
            'root': str(root), 'base_sha': value['base']['head'], 'outcome': outcome,
            'access': 'read_only' if read_only else 'edit',
            'allowed_files': allowed, 'acceptance': acceptance, 'capabilities': capabilities,
            'context': value, 'dispatch': 'not performed',
            'return_requirements': [('read-only: no repository edits; findings requiring changes go to a separately scoped task'
                                     if read_only else 'actual diff and exact source revision'),
                                    'capability evidence or explicit gaps',
                                    'each satellite updated or justified in the native wiki',
                                    'preserve selected evidence files; inspect embedded probe output paths and write each new raw run to a distinct destination',
                                    'verification, remaining work and next safe action'],
            'limits': 'A created or sent packet does not establish that a worker read or applied it. Access is task scope, not a filesystem sandbox.'}
    if read_only:
        packet['read_only_baseline'] = readonly_baseline(packet, 'start')
    return packet


def delegate(packet: dict, owner: str, task_id: str, allowed: list[str], *, read_only: bool = False) -> dict:
    if packet.get('kind') != 'wiki-work-packet':
        raise ValueError('Expected a wiki work packet')
    check_capture(packet['context'])
    allowed = sorted(set(relative(f) for f in allowed))
    access = packet.get('access', 'edit')
    if access not in ('edit', 'read_only') or (access == 'read_only' and packet['allowed_files']):
        raise ValueError('Invalid task access scope')
    read_only = read_only or access == 'read_only'
    if read_only and allowed:
        raise ValueError('Read-only delegation cannot widen editing scope')
    if not owner.strip() or not task_id.strip() or (not read_only and not allowed) or not set(allowed).issubset(packet['allowed_files']):
        raise ValueError('Delegation must name an owner/task and cannot widen the editing scope')
    child = {**packet, 'task_id': task_id, 'owner': owner, 'parent_task_id': packet['task_id'],
            'access': 'read_only' if read_only else 'edit', 'allowed_files': allowed, 'dispatch': 'not performed'}
    if read_only:
        child['read_only_baseline'] = readonly_baseline(child, 'delegate')
    return child


def changed_files(root: Path, base: str, baseline_untracked: list[str]) -> list[str]:
    # Resolve to a commit before passing a caller value to diff; never treat it as an option.
    if not base or base.startswith('-'):
        raise ValueError('Invalid base revision')
    commit = git(root, 'rev-parse', '--verify', base + '^{commit}').decode().strip()
    names = [x.decode('utf-8') for x in git(root, 'diff', '--no-ext-diff', '--name-only', '-z', commit, '--').split(b'\0') if x]
    return sorted(set(names) | (set(untracked(root)) - set(baseline_untracked)))


def repository_changes(packet: dict, after: dict) -> tuple[list[str], list[str]]:
    """One Git-base/planned-untracked predicate for early advice and final return."""
    root = Path(after['root']).resolve()
    actual = changed_files(root, packet['base_sha'], packet['context']['baseline_untracked'])
    peer_start = packet['context'].get('peers', {})
    peer_end = after.get('peers', {})
    check_peer_namespace(root, peer_start, actual)
    if set(peer_start) != set(peer_end):
        raise ValueError('Start/end peer scope differs')
    missing_peers = []
    for alias, peer in peer_start.items():
        if not peer['available'] or not peer_end[alias]['available']:
            missing_peers.append(alias)
            continue
        if peer['root'] != peer_end[alias]['root']:
            raise ValueError('Start/end peer checkouts differ')
        baseline = packet['context'].get('baseline_peer_untracked', {}).get(alias, [])
        actual.extend(alias + '/' + f for f in changed_files(Path(peer['root']), peer['head'], baseline))
    # Already-untracked planned files count even when present before capture.
    for name, old in packet['context']['planned_source_hashes'].items():
        alias, _, rest = name.partition('/')
        declared_untracked = name in packet['context']['baseline_untracked']
        if alias in peer_start:
            declared_untracked = rest in packet['context'].get('baseline_peer_untracked', {}).get(alias, [])
        if (source_hash(root, name, peer_end) != old or (declared_untracked and old is not None)) and name not in actual:
            actual.append(name)
    return sorted(set(actual)), sorted(missing_peers)


def capture_return(packet: dict, program: list[str], *, allow_execution: bool = False) -> dict:
    """Coordinator recapture using the existing final collector, never a planned-file subset.

    The caller supplies the reviewed argv again and explicitly permits native
    execution. No command is selected from Wiki text or silently trusted from a
    mutable packet. This prepares context; finish still independently reconciles.
    """
    if not allow_execution:
        raise ValueError('Native execution requires explicit opt-in for return capture')
    if packet.get('kind') != 'wiki-work-packet' or packet.get('schema_version') != 1:
        raise ValueError('Expected a wiki work packet')
    context = packet['context']
    if context.get('kind') != 'native-wiki-capture' or context.get('schema_version') != 1:
        raise ValueError('Expected the original native capture')
    if not program or program != context.get('native_argv'):
        raise ValueError('Explicit native argv differs from the saved reviewed command')
    root = Path(packet['root']).resolve()
    if str(root) != context['root'] or packet['base_sha'] != context['base']['head']:
        raise ValueError('Task base or checkout differs from its original capture')
    if report_hash(context['native_report']) != context.get('native_report_canonical_sha256'):
        raise ValueError('Native context changed after capture; do not edit saved projections')
    # Reusing a reviewed argv is not permission to run a replaced program body.
    # Normal Wiki/source changes are expected; changed declared runtime inputs
    # need the existing explicit manual capture/review boundary instead.
    reviewed_runtime = {}
    for name in context['runtime_inputs']:
        expected = context['base'].get('inputs', {}).get(name)
        if not expected or file_hash(within(root, name)) != expected:
            raise ValueError('Declared native runtime input changed or is unverified; review it and use a new manual capture/phase')
        reviewed_runtime[name] = expected
    pointer = context.get('native_source_context')
    saved_sources = compare_native_sources(context['native_report'], pointer, root,
                                           context['base']['head'], context.get('peers', {}))
    if ((pointer is not None and 'native_source_comparison' not in context)
            or context.get('native_source_comparison', saved_sources) != saved_sources):
        raise ValueError('Saved native source comparison is unavailable or changed')
    paths, preserved = artifact_fields(context)
    if artifact_snapshot(paths) != preserved:
        raise ValueError('Selected artifact bytes changed since task capture')
    peers = {alias: row['root'] for alias, row in context.get('peers', {}).items()}
    before = {'root': str(root), 'peers': peer_snapshot(peers)}
    before_head = head(root)
    actual, missing = repository_changes(packet, before)
    if missing:
        raise ValueError('Selected peers unavailable for return capture: ' + ', '.join(missing))
    before_hashes = {name: source_hash(root, name, before['peers']) for name in actual}
    # Reuse capture's validation, explicit source comparison and artifact/input
    # observations. No allowlist intersection: unplanned files must reach finish.
    result = capture(root, context['query'], actual, program, context['runtime_inputs'],
                     wiki_root=context['wiki_root'], allow_execution=True, peers=peers,
                     native_source_context=pointer, preserve_artifacts=paths,
                     reviewed_runtime_inputs=reviewed_runtime)
    after = {'root': str(root), 'peers': peer_snapshot(peers)}
    final, missing = repository_changes(packet, after)
    after_head = head(root)
    if (missing or final != actual or before_head != after_head
            or before['peers'] != after['peers'] or result['peers'] != after['peers']
            or result['base']['head'] != after_head
            or before_hashes != {name: source_hash(root, name, after['peers']) for name in final}
            or artifact_snapshot(paths) != preserved):
        raise ValueError('Source or diff changed during return capture; use a stable snapshot')
    result['return_scope'] = {
        'selection': 'actual_diff', 'task_id': packet['task_id'], 'base_sha': packet['base_sha'],
        'collector': 'repository_changes', 'file_count': len(actual),
        'limits': 'Coordinator Git/hash observations at boundaries, not continuous monitoring, semantic review or completion. Finish still independently rechecks actual scope.',
    }
    return result


def readonly_baseline(packet: dict, stage: str) -> dict:
    """Coordinator observation, not a new permission or an unchanged certificate."""
    actual, missing = repository_changes(packet, packet['context'])
    status = 'unavailable' if missing else 'differences' if actual else 'no_differences_observed'
    return {
        'status': status, 'observed_at': stage, 'difference_count': len(actual),
        'path_sample': actual[:8], 'path_sample_truncated': len(actual) > 8,
        'unavailable_peers': missing, 'completion_certificate': False,
        'meaning': ('Existing finish cannot accept an unchanged read-only return with these Git-base differences or unavailable peers. '
                    'Inspection is still allowed; use an honestly identified clean committed review snapshot if unchanged return is required.'
                    if actual or missing else
                    'No differences observed by the existing return predicate at this boundary; later changes still require final reconciliation.'),
        'limits': 'Saved coordinator observation only; not continuous monitoring, currentness, filesystem enforcement, provenance or semantic/runtime acceptance. No files were committed, cleaned or excluded. The path sample is not the task impact inventory.',
    }


def review_template(packet: dict, after: dict) -> dict:
    """Prepare fields, never attest that a page/capability has been reviewed."""
    if packet.get('kind') != 'wiki-work-packet':
        raise ValueError('Expected a wiki work packet')
    access = packet.get('access', 'edit')
    if access not in ('edit', 'read_only') or (access == 'read_only' and packet['allowed_files']):
        raise ValueError('Invalid task access scope')
    root = check_capture(after)
    check_artifact_return(packet['context'], after)
    if str(root) != packet['root'] or after['wiki_root'] != packet['context']['wiki_root']:
        raise ValueError('Start/end captures refer to different checkouts or native wikis')
    if after.get('native_source_context') != packet['context'].get('native_source_context'):
        raise ValueError('Start/end native source comparison policy differs')
    report = after['native_report']
    pages = sorted({page['path'] for row in report['impact'] for page in row['pages']})
    return {
        'kind': 'wiki-review-template', 'task_id': packet['task_id'],
        'artifact_preservation': artifact_observation(after, 'unchanged_at_review_preparation'),
        'pages': {p: {'status': 'unreviewed', 'reason': ''} for p in pages},
        'capabilities': {c: {'status': 'unreviewed', 'reason': '', 'references': []}
                         for c in packet['capabilities']},
        'unregistered': {r['file']: '' for r in report['impact'] if r['unregistered']},
        'handoff': {'remaining': [], 'next_safe_action': ''},
        'guidance': {
            'pages': 'Object keyed by native page path. Use updated only for a real diff, or no_update with an inspected reason.',
            'capabilities': 'Object keyed by exact task capability. Use source_verified, runtime_verified, gap or not_applicable and a nonempty reason.',
            'references': 'Verified claims require reachable repository-relative file paths, optionally prefixed by a declared peer alias. Put line ranges and symbols in reason, not in the path.',
            'limits': 'All placeholders are unreviewed. This does not establish correct final diff scope, source truth, agent use or product acceptance. Run finish after actual review.',
        },
    }


def finish(packet: dict, after: dict, review: dict) -> dict:
    # Reject a human-readable list even when an empty actual diff would otherwise
    # skip it. A container shape is not a semantic review or a completion stamp.
    for field in ('pages', 'capabilities', 'unregistered'):
        if field in review and not isinstance(review[field], dict):
            raise ValueError(f'Review {field} must be an object keyed by page/capability/file, not a list; use review-template to prepare unreviewed fields')
    for field in ('pages', 'capabilities'):
        if any(not isinstance(row, dict) for row in review.get(field, {}).values()):
            raise ValueError(f'Review {field} entries must be objects; use review-template')
    if packet.get('kind') != 'wiki-work-packet':
        raise ValueError('Expected a wiki work packet')
    access = packet.get('access', 'edit')
    if access not in ('edit', 'read_only') or (access == 'read_only' and packet['allowed_files']):
        raise ValueError('Invalid task access scope')
    root = check_capture(after)
    check_artifact_return(packet['context'], after)
    if str(root) != packet['root'] or after['wiki_root'] != packet['context']['wiki_root']:
        raise ValueError('Start/end captures refer to different checkouts or native wikis')
    if after.get('native_source_context') != packet['context'].get('native_source_context'):
        raise ValueError('Start/end native source comparison policy differs')
    actual, missing_peers = repository_changes(packet, after)
    peer_end = after.get('peers', {})
    problems = []
    if access == 'read_only' and actual:
        problems.append('read-only task has repository differences relative to the captured Git base; not accepted as unchanged')
    if missing_peers:
        problems.append('peer sources unavailable; not an empty diff: ' + ', '.join(missing_peers))
    if set(after['files']) != set(actual):
        problems.append('actual diff is not completely covered by the final native impact query')
    report = after['native_report']
    pages = {page['path'] for row in report['impact'] for page in row['pages']}
    wiki_paths = {after['wiki_root'] + '/' + page for page in pages}
    outside = set(actual) - set(packet['allowed_files']) - wiki_paths
    if outside:
        problems.append('unplanned files: ' + ', '.join(sorted(outside)))
    decisions = review.get('pages', {})
    for page in sorted(pages):
        decision = decisions.get(page, {})
        if decision.get('status') == 'updated':
            if after['wiki_root'] + '/' + page not in actual:
                problems.append('page marked updated without a real change: ' + page)
        elif decision.get('status') == 'no_update':
            if not isinstance(decision.get('reason'), str) or not decision['reason'].strip():
                problems.append('no-update decision needs a reason: ' + page)
        else:
            problems.append('satellite has no reconciled disposition: ' + page)
    for capability in packet['capabilities']:
        decision = review.get('capabilities', {}).get(capability, {})
        if decision.get('status') not in ('source_verified', 'runtime_verified', 'gap', 'not_applicable'):
            problems.append('required capability unreviewed: ' + capability)
        elif not isinstance(decision.get('reason'), str) or not decision['reason'].strip():
            problems.append('capability decision needs evidence or a reason: ' + capability)
        elif decision['status'] in ('source_verified', 'runtime_verified'):
            refs = decision.get('references', [])
            if not isinstance(refs, list) or not refs:
                problems.append('verified capability lacks inspectable references: ' + capability)
            else:
                for ref in refs:
                    try:
                        relative(ref)
                    except ValueError as error:
                        raise ValueError('Capability references must be repository-relative file paths; put lines/symbols in reason, not the reference path; use review-template') from error
                    if not source_hash(root, ref, peer_end):
                        problems.append('capability reference unavailable: ' + ref)
    gaps = [name for name, row in review.get('capabilities', {}).items() if row.get('status') == 'gap']
    unregistered = [row['file'] for row in report['impact'] if row['unregistered']]
    justifications = review.get('unregistered', {})
    for name in unregistered:
        if not isinstance(justifications.get(name), str) or not justifications[name].strip():
            problems.append('unregistered file needs routing repair or a justified scope explanation: ' + name)
    if report['placementIssues'] or after['native_exit_code'] != 0:
        problems.append('native navigation still reports a failure or source placement issues')
    handoff = review.get('handoff')
    if not isinstance(handoff, dict) or not isinstance(handoff.get('remaining'), list) or not handoff.get('next_safe_action'):
        problems.append('handoff requires remaining work and a next safe action')
    source_state = {'head_sha': head(root),
                    'differs_from_task_base': bool(actual),
                    'tracked_worktree_dirty': bool(git(root, 'diff', '--no-ext-diff', '--name-only', 'HEAD', '--').strip()),
                    'untracked_file_count': len(untracked(root)),
                    'file_hashes': {f: source_hash(root, f, peer_end) for f in actual},
                    'peers': peer_end}
    return {'schema_version': 1, 'kind': 'wiki-work-reconciliation', 'task_id': packet['task_id'],
            'access': access,
            'artifact_preservation': artifact_observation(after, 'unchanged_at_finish'),
            'native_source_context': after.get('native_source_context'),
            'native_source_comparison': compare_native_sources(after['native_report'], after.get('native_source_context'),
                                                               root, after['base']['head'], peer_end),
            'base_sha': packet['base_sha'], 'head_sha': head(root), 'actual_files': actual,
            'structural_reconciliation': not problems, 'issues': problems, 'capability_gaps': gaps,
            'review': review, 'native_omitted_candidates': report['omitted'],
            'semantic_review': 'worker/reviewer claims preserved; not independently certified',
            'runtime_acceptance': 'not inferred', 'handoff': review.get('handoff'),
            'source_state': source_state, 'product_completion': 'not established by structural reconciliation',
            'limits': 'No project files edited or checks executed. Structural closure is not product completion.'}


def write_new(path: Path, value: dict) -> None:
    encoded = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if len(encoded.encode('utf-8')) > MAX_REPORT:
        raise ValueError('Packet exceeds transport budget; no output was written or truncated')
    with path.open('x', encoding='utf-8', newline='\n') as out:
        out.write(encoded)


def task_view(packet: dict, view: str = 'all', path: str | None = None, *, snapshot_only: bool = False) -> dict:
    """Expose full native records or an explicit index; never silently clip them."""
    if packet.get('kind') != 'wiki-work-packet':
        raise ValueError('Expected a wiki work packet')
    if packet.get('access', 'edit') not in ('edit', 'read_only') or (packet.get('access') == 'read_only' and packet['allowed_files']):
        raise ValueError('Invalid task access scope')
    current = False
    if snapshot_only:
        # A constrained reader may be forbidden to invoke even read-only Git.
        # Render stored context without probing live inputs. This mode is never
        # used by capture/start/delegate/review-template/finish.
        freshness = 'saved snapshot only; current inputs not checked; coordinator must validate before new dispatch or acceptance'
    else:
        freshness = 'current for declared inputs'
        try:
            check_capture(packet['context'])
            current = True
        except (OSError, ValueError, KeyError, subprocess.SubprocessError):
            freshness = 'stale or unavailable; this is a historical projection, recapture before new work'
    result = {'task_id': packet['task_id'], 'owner': packet['owner'], 'root': packet['root'],
            'wiki_root': packet['context'].get('wiki_root'),
            'path_bases': {
                'wiki_pages': 'root / wiki_root',
                'source_files': 'root, or peers[alias].root after a declared alias/ prefix',
                'limits': 'Saved bases only; no existence or currentness claim. A missing wiki_root is unknown, not a default. Keep original native keys for --path.',
            },
            'access': packet.get('access', 'edit'),
            'base_sha': packet['base_sha'], 'peers': packet['context'].get('peers', {}),
            'freshness': freshness, 'outcome': packet['outcome'],
            'allowed_files': packet['allowed_files'], 'capabilities': packet['capabilities'],
            'acceptance': packet['acceptance'], 'native_context': packet['context']['native_report'],
            'return_requirements': packet['return_requirements'], 'limits': packet['limits']}
    if packet.get('access') == 'read_only':
        result['read_only_baseline'] = packet.get('read_only_baseline', {
            'status': 'unavailable', 'completion_certificate': False,
            'meaning': 'This older packet has no saved read-only baseline observation; no clean baseline is inferred.',
        })
    result['view_observation'] = {
        'mode': 'snapshot_only' if snapshot_only else 'live_check',
        'current_check_attempted': not snapshot_only,
        'current_inputs_checked': current,
        'limits': 'Saved source-identity and artifact records describe capture-time observations, not a new live check. Rendering is not authenticated provenance, permission, physical reading, semantic review or business acceptance.',
    }
    native = packet['context']['native_report']
    # Preserve the native project's own finish/acknowledgement vocabulary in every
    # reading view. These are quoted requirements, never commands to execute here.
    result['native_workflow'] = native.get('workflow', {
        'status': 'not_declared',
        'meaning': 'The native router did not provide its return contract; inspect its own gates before dispatch.',
    })
    result['native_source_comparison'] = packet['context'].get('native_source_comparison', {
        'status': 'unavailable' if packet['context'].get('native_source_context') is not None else 'not_requested',
        'meaning': 'Strict comparison record is missing; recapture before dispatch.'
                   if packet['context'].get('native_source_context') is not None else
                   'Native source observations have not been compared with declared checkouts.'})
    if snapshot_only:
        result['native_source_comparison_observation'] = {
            'record_time': 'capture', 'current_check_attempted': False,
            'meaning': 'native_source_comparison is preserved capture-time data, not a current match; reading does not recompute or authenticate that record.',
        }
    # Foreign-host path strings are retained as saved data in snapshot views,
    # not validated as local paths. Live dispatch/return use the original policy.
    result['artifact_preservation'] = artifact_observation(
        packet['context'], 'captured_snapshot' if snapshot_only else 'captured', native_paths=not snapshot_only)
    if snapshot_only:
        result['artifact_preservation']['local_path_validation'] = 'not performed; saved path strings only'
    result['review_preparation'] = {
        'command': 'review-template --packet <same-packet> --after-capture <current-final-capture> --output <new-review.json>',
        'meaning': 'Optional unreviewed skeleton for the actual return. Does not fill decisions or replace the native finish/commit gate.',
    }
    if view == 'index':
        result.pop('native_context')
        result['native_index'] = {
            'features': [{'path': row['path'], 'title': row['title']} for row in native['cards']],
            'files': [{'file': row['file'], 'satellite_count': len(row['pages']),
                       'unregistered': row['unregistered']} for row in native['impact']],
            'omitted_candidates': native['omitted'], 'placementIssues': native['placementIssues'],
            'limits': native['limits']}
        mode_flag = ' --snapshot-only' if snapshot_only else ''
        result['expansion'] = {'feature': 'show --packet <same-packet>' + mode_flag + ' --view feature --path <feature-path>',
                               'impact': 'show --packet <same-packet>' + mode_flag + ' --view impact --path <file>',
                               'all': 'show --packet <same-packet>' + mode_flag + ' --view all',
                               'reading_state': 'Index only; full feature records and satellites are not delivered in this view.'}
    elif view in ('feature', 'impact'):
        key = 'cards' if view == 'feature' else 'impact'
        field = 'path' if view == 'feature' else 'file'
        rows = [row for row in native[key] if row[field] == path]
        if len(rows) != 1:
            raise ValueError('Select one exact feature or file from the index')
        result['native_context'] = {key: rows, 'limits': native['limits']}
        result['expansion'] = {'reading_state': 'Selected native record only; other records remain available from the index.'}
    elif view != 'all':
        raise ValueError('Unsupported task view')
    return result


def main(argv=None) -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    cap = subs.add_parser('capture')
    cap.add_argument('--root', type=Path, required=True)
    cap.add_argument('--wiki-root', default='docs/wiki')
    cap.add_argument('--query', required=True)
    cap.add_argument('--files', action='extend', nargs='*', default=[],
                     help='Planned file groups accumulate; repeating the option never replaces earlier paths')
    cap.add_argument('--runtime-input', action='append', default=[])
    cap.add_argument('--native-argv', required=True, help='Explicit JSON argv; never read from wiki text')
    cap.add_argument('--allow-native-execution', action='store_true')
    cap.add_argument('--peer', action='append', default=[], help='Explicit alias=checkout; missing is not an empty diff')
    cap.add_argument('--native-source-context', help='Caller-selected JSON pointer to native {label: {root, revision}} observations; compare every selected checkout')
    cap.add_argument('--preserve-artifact', action='append', default=[], help='Explicit absolute existing evidence file to hash-check; no write prevention or continuous monitoring')
    rec = subs.add_parser('capture-return', help='Coordinator: recapture every actual diff file across the task root/peers using the original final collector')
    rec.add_argument('--packet', type=Path, required=True)
    rec.add_argument('--native-argv', required=True, help='Explicit reviewed JSON argv, must equal the original capture; never execute a command selected from Wiki text')
    rec.add_argument('--allow-native-execution', action='store_true', help='Explicit coordinator opt-in; not permitted for a worker forbidden Git/native execution')
    sta = subs.add_parser('start')
    sta.add_argument('--capture', type=Path, required=True)
    sta.add_argument('--outcome', required=True)
    sta.add_argument('--acceptance', action='append', required=True)
    sta.add_argument('--capability', action='append', required=True)
    de = subs.add_parser('delegate')
    de.add_argument('--packet', type=Path, required=True)
    for sub in (sta, de):
        sub.add_argument('--task-id', required=True)
        sub.add_argument('--owner', required=True)
        sub.add_argument('--allow-file', action='append', default=[])
        sub.add_argument('--read-only', action='store_true', help='Review only: no editing paths; metadata is not a sandbox')
    end = subs.add_parser('finish')
    end.add_argument('--packet', type=Path, required=True)
    end.add_argument('--after-capture', type=Path, required=True)
    end.add_argument('--review', type=Path, required=True)
    template = subs.add_parser('review-template', help='Prepare unreviewed return fields from a final native capture; never mark work verified')
    template.add_argument('--packet', type=Path, required=True)
    template.add_argument('--after-capture', type=Path, required=True)
    show = subs.add_parser('show')
    show.add_argument('--packet', type=Path, required=True)
    show.add_argument('--view', choices=('index', 'feature', 'impact', 'all'), default='index')
    show.add_argument('--path', help='Exact feature path or impacted file from the index')
    show.add_argument('--snapshot-only', action='store_true', help='Render saved records without Git/live-input checks; never establishes currentness or authorizes new work')
    for sub in (cap, rec, sta, de, end, template):
        sub.add_argument('--output', type=Path, required=True, help='New private projection path; never overwrite')
    args = parser.parse_args(argv)
    try:
        if args.command == 'show':
            print(json.dumps(task_view(read_json(args.packet), args.view, args.path, snapshot_only=args.snapshot_only), ensure_ascii=False, indent=2))
            return 0
        if args.command == 'capture':
            result = capture(args.root, args.query, args.files, json.loads(args.native_argv), args.runtime_input,
                             wiki_root=args.wiki_root, allow_execution=args.allow_native_execution,
                             peers=dict(entry.split('=', 1) for entry in args.peer),
                             native_source_context=args.native_source_context, preserve_artifacts=args.preserve_artifact)
        elif args.command == 'capture-return':
            result = capture_return(read_json(args.packet), json.loads(args.native_argv),
                                    allow_execution=args.allow_native_execution)
        elif args.command == 'start':
            result = start(read_json(args.capture), args.task_id, args.owner, args.outcome, args.allow_file,
                           args.acceptance, args.capability, read_only=args.read_only)
        elif args.command == 'delegate':
            result = delegate(read_json(args.packet), args.owner, args.task_id, args.allow_file, read_only=args.read_only)
        elif args.command == 'review-template':
            result = review_template(read_json(args.packet), read_json(args.after_capture))
        else:
            result = finish(read_json(args.packet), read_json(args.after_capture), read_json(args.review))
        write_new(args.output, result)
        print(json.dumps({'ok': True, 'kind': result['kind'], 'output': str(args.output),
                          'limits': result.get('limits', 'packet delivery/use not verified')}, ensure_ascii=False))
        return 1 if result.get('structural_reconciliation') is False else 0
    except ValueError as error:
        print(json.dumps({'ok': False, 'error': str(error), 'completion': 'not established'}, ensure_ascii=True))
        return 1
    except (OSError, KeyError, TypeError, AttributeError, subprocess.SubprocessError):
        print(json.dumps({'ok': False, 'error': 'Declared input, native process or report unavailable/invalid; no completion claim.'}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
