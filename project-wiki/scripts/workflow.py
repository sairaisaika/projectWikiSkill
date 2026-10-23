"""Revision-bound native wiki context, delegation and diff reconciliation.

Only capture runs a caller-supplied native command, with explicit opt-in and no
shell. Other operations inspect projections and Git; none edits project sources,
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


def source_hash(root: Path, name: str, peers: dict) -> str | None:
    relative(name)
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
        folder = str(Path(row['root']).resolve())
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
            native_source_context: str | None = None) -> dict:
    root = root.resolve()
    if not allow_execution:
        raise ValueError('Native execution requires explicit opt-in; wiki text is never executable configuration')
    if not isinstance(program, list) or not program or not all(isinstance(x, str) and x for x in program) or not runtime_inputs:
        raise ValueError('Declare native argv and its reviewed runtime inputs')
    if not query.strip() or query.startswith('-'):
        raise ValueError('A non-option task query is required')
    files = sorted(set(relative(f) for f in files))
    before = input_snapshot(root, wiki_root, runtime_inputs)
    peer_before = peer_snapshot(peers or {})
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
    if report_hash(value['native_report']) != value.get('native_report_canonical_sha256'):
        raise ValueError('Native context was changed after capture; regenerate instead of editing its projection')
    if require_current and input_snapshot(root, value['wiki_root'], value['runtime_inputs']) != value['base']:
        raise ValueError('Capture is stale for this checkout or wiki/runtime inputs')
    peers = value.get('peers', {})
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
    return {'schema_version': 1, 'kind': 'wiki-work-packet', 'task_id': task_id, 'owner': owner,
            'root': str(root), 'base_sha': value['base']['head'], 'outcome': outcome,
            'access': 'read_only' if read_only else 'edit',
            'allowed_files': allowed, 'acceptance': acceptance, 'capabilities': capabilities,
            'context': value, 'dispatch': 'not performed',
            'return_requirements': [('read-only: no repository edits; findings requiring changes go to a separately scoped task'
                                     if read_only else 'actual diff and exact source revision'),
                                    'capability evidence or explicit gaps',
                                    'each satellite updated or justified in the native wiki',
                                    'verification, remaining work and next safe action'],
            'limits': 'A created or sent packet does not establish that a worker read or applied it. Access is task scope, not a filesystem sandbox.'}


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
    return {**packet, 'task_id': task_id, 'owner': owner, 'parent_task_id': packet['task_id'],
            'access': 'read_only' if read_only else 'edit', 'allowed_files': allowed, 'dispatch': 'not performed'}


def changed_files(root: Path, base: str, baseline_untracked: list[str]) -> list[str]:
    # Resolve to a commit before passing a caller value to diff; never treat it as an option.
    if not base or base.startswith('-'):
        raise ValueError('Invalid base revision')
    commit = git(root, 'rev-parse', '--verify', base + '^{commit}').decode().strip()
    names = [x.decode('utf-8') for x in git(root, 'diff', '--no-ext-diff', '--name-only', '-z', commit, '--').split(b'\0') if x]
    return sorted(set(names) | (set(untracked(root)) - set(baseline_untracked)))


def review_template(packet: dict, after: dict) -> dict:
    """Prepare fields, never attest that a page/capability has been reviewed."""
    if packet.get('kind') != 'wiki-work-packet':
        raise ValueError('Expected a wiki work packet')
    access = packet.get('access', 'edit')
    if access not in ('edit', 'read_only') or (access == 'read_only' and packet['allowed_files']):
        raise ValueError('Invalid task access scope')
    root = check_capture(after)
    if str(root) != packet['root'] or after['wiki_root'] != packet['context']['wiki_root']:
        raise ValueError('Start/end captures refer to different checkouts or native wikis')
    if after.get('native_source_context') != packet['context'].get('native_source_context'):
        raise ValueError('Start/end native source comparison policy differs')
    report = after['native_report']
    pages = sorted({page['path'] for row in report['impact'] for page in row['pages']})
    return {
        'kind': 'wiki-review-template', 'task_id': packet['task_id'],
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
    if str(root) != packet['root'] or after['wiki_root'] != packet['context']['wiki_root']:
        raise ValueError('Start/end captures refer to different checkouts or native wikis')
    actual = changed_files(root, packet['base_sha'], packet['context']['baseline_untracked'])
    if after.get('native_source_context') != packet['context'].get('native_source_context'):
        raise ValueError('Start/end native source comparison policy differs')
    peer_start = packet['context'].get('peers', {})
    peer_end = after.get('peers', {})
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
    # An already-untracked planned file can still change after the start snapshot.
    for name, old in packet['context']['planned_source_hashes'].items():
        alias, _, rest = name.partition('/')
        declared_untracked = name in packet['context']['baseline_untracked']
        if alias in peer_start:
            declared_untracked = rest in packet['context'].get('baseline_peer_untracked', {}).get(alias, [])
        if (source_hash(root, name, peer_end) != old or (declared_untracked and old is not None)) and name not in actual:
            actual.append(name)
    actual = sorted(set(actual))
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


def task_view(packet: dict, view: str = 'all', path: str | None = None) -> dict:
    """Expose full native records or an explicit index; never silently clip them."""
    if packet.get('kind') != 'wiki-work-packet':
        raise ValueError('Expected a wiki work packet')
    if packet.get('access', 'edit') not in ('edit', 'read_only') or (packet.get('access') == 'read_only' and packet['allowed_files']):
        raise ValueError('Invalid task access scope')
    freshness = 'current for declared inputs'
    try:
        check_capture(packet['context'])
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        freshness = 'stale or unavailable; this is a historical projection, recapture before new work'
    result = {'task_id': packet['task_id'], 'owner': packet['owner'], 'root': packet['root'],
            'access': packet.get('access', 'edit'),
            'base_sha': packet['base_sha'], 'peers': packet['context'].get('peers', {}),
            'freshness': freshness, 'outcome': packet['outcome'],
            'allowed_files': packet['allowed_files'], 'capabilities': packet['capabilities'],
            'acceptance': packet['acceptance'], 'native_context': packet['context']['native_report'],
            'return_requirements': packet['return_requirements'], 'limits': packet['limits']}
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
        result['expansion'] = {'feature': 'show --packet <same-packet> --view feature --path <feature-path>',
                               'impact': 'show --packet <same-packet> --view impact --path <file>',
                               'all': 'show --packet <same-packet> --view all',
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
    cap.add_argument('--files', nargs='*', default=[])
    cap.add_argument('--runtime-input', action='append', default=[])
    cap.add_argument('--native-argv', required=True, help='Explicit JSON argv; never read from wiki text')
    cap.add_argument('--allow-native-execution', action='store_true')
    cap.add_argument('--peer', action='append', default=[], help='Explicit alias=checkout; missing is not an empty diff')
    cap.add_argument('--native-source-context', help='Caller-selected JSON pointer to native {label: {root, revision}} observations; compare every selected checkout')
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
    for sub in (cap, sta, de, end, template):
        sub.add_argument('--output', type=Path, required=True, help='New private projection path; never overwrite')
    args = parser.parse_args(argv)
    try:
        if args.command == 'show':
            print(json.dumps(task_view(read_json(args.packet), args.view, args.path), ensure_ascii=False, indent=2))
            return 0
        if args.command == 'capture':
            result = capture(args.root, args.query, args.files, json.loads(args.native_argv), args.runtime_input,
                             wiki_root=args.wiki_root, allow_execution=args.allow_native_execution,
                             peers=dict(entry.split('=', 1) for entry in args.peer),
                             native_source_context=args.native_source_context)
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
