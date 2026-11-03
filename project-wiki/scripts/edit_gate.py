"""Optional pre-edit gate: a locked path may not be edited before Wiki context and design.

Reads one Claude Code PreToolUse event (Edit/Write/MultiEdit) from stdin. Exit 2
with a reason on stderr blocks the edit and hands the reason to the model; exit 0
lets it through. A project opts in by placing `.project-wiki/edit-gate.json` at
its checkout root; without it every edit passes. The gate reads that config, the
stamp, the optional map and skip files, and runs read-only Git subcommands. It
never executes project code, writes a file or reads the edited file's contents.
Any failure of the gate itself passes the edit and says "gate unavailable": the
gate must not block a task because of its own defect.

Two predicates, reported separately:

  (a) context  - a fresh stamp lists the relative path (satellites were expanded);
  (b) design   - with `design_first`, a handwritten change exists under `wiki_root`
                 (merge-base against `base_ref`, uncommitted or untracked), after
                 removing `generated` views. Without a merge-base (no `base_ref`,
                 unrelated history) (b) is not judged. A non-empty `skip_file`
                 waives (b) only and is echoed; an empty one fails (b).

A stamp proves that context was fetched and a page diff proves that a page was
touched; neither proves understanding or a correct design. Those stay with review.
"""
from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True

MAX_EVENT = 64 * 1024
MAX_CONFIG = 64 * 1024
CONFIG_PATH = PurePosixPath('.project-wiki/edit-gate.json')
TOOLS = {'Edit', 'Write', 'MultiEdit'}
DEFAULT_STAMP_AGE_HOURS = 8.0
GIT_TIMEOUT = 5
REPO_ENV = {'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR', 'GIT_OBJECT_DIRECTORY',
            'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_NAMESPACE', 'GIT_CEILING_DIRECTORIES'}


class Unavailable(Exception):
    """The gate cannot judge; the edit passes with a visible notice."""


def glob_match(pattern: str, rel: str) -> bool:
    """Match a posix-relative path against `**`, `*` and `?` without fnmatch's `/`-crossing `*`."""
    out, i = '', 0
    while i < len(pattern):
        if pattern.startswith('**/', i):
            out, i = out + '(?:.*/)?', i + 3
        elif pattern.startswith('**', i):
            out, i = out + '.*', i + 2
        elif pattern[i] == '*':
            out, i = out + '[^/]*', i + 1
        elif pattern[i] == '?':
            out, i = out + '[^/]', i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.fullmatch(out, rel) is not None


def find_root(path: Path) -> Path | None:
    """Nearest ancestor holding `.git` (directory or worktree file); None outside any checkout."""
    probe = path if path.is_dir() else path.parent
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    for candidate in [probe, *probe.parents]:
        if (candidate / '.git').exists():
            return candidate
    return None


def read_config(root: Path) -> dict | None:
    path = root / Path(*CONFIG_PATH.parts)
    if not path.is_file():
        return None
    if path.stat().st_size > MAX_CONFIG:
        raise Unavailable('config exceeds budget')
    config = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(config, dict):
        raise Unavailable('config must be an object')
    for key, kind in (('wiki_root', str), ('locked', list), ('generated', list), ('design_first', bool),
                      ('map_file', str), ('map_row_format', str), ('base_ref', str), ('skip_file', str),
                      ('stamp', dict), ('stamp_command', str), ('design_hint', str)):
        if key in config and (type(config[key]) is not kind):
            raise Unavailable(f'config key {key} must be {kind.__name__}')
    if not config.get('wiki_root'):
        raise Unavailable('config needs wiki_root')
    for key in ('locked', 'generated'):
        if any(not isinstance(item, str) for item in config.get(key, [])):
            raise Unavailable(f'config key {key} must list strings')
    return config


def relative_posix(root: Path, raw: str) -> str | None:
    try:
        return Path(raw).relative_to(root).as_posix()
    except ValueError:
        return None


def is_locked(config: dict, root: Path, rel: str) -> bool:
    if any(glob_match(pattern, rel) for pattern in config.get('locked', [])):
        return True
    map_file = config.get('map_file')
    if map_file:
        path = root / map_file
        if path.is_file():
            row = config.get('map_row_format', '| `{path}` |').replace('{path}', rel)
            return row in path.read_text(encoding='utf-8', errors='replace')
    return False


def context_ok(config: dict, root: Path, rel: str) -> tuple[bool, str]:
    """Predicate (a): a fresh stamp lists this file."""
    stamp = config.get('stamp') or {}
    stamp_path = stamp.get('path')
    if not isinstance(stamp_path, str) or not stamp_path:
        return True, 'context: no stamp configured'
    max_age = stamp.get('max_age_hours', DEFAULT_STAMP_AGE_HOURS)
    if type(max_age) not in (int, float) or max_age <= 0:
        raise Unavailable('stamp.max_age_hours must be a positive number')
    path = root / stamp_path
    fix = config.get('stamp_command') or ('write {"files": ["' + rel + '"]} to ' + stamp_path)
    fix = fix.replace('{file}', rel).replace('{root}', str(root))
    if not path.is_file():
        return False, f'context: no stamp at {stamp_path}. Fix: {fix}'
    age_hours = (time.time() - path.stat().st_mtime) / 3600
    if age_hours >= max_age:
        return False, f'context: stamp {stamp_path} is {age_hours:.1f}h old (max {max_age:g}h). Fix: {fix}'
    try:
        files = json.loads(path.read_text(encoding='utf-8')).get('files') or []
    except (ValueError, AttributeError):
        return False, f'context: stamp {stamp_path} is not a JSON object with files[]. Fix: {fix}'
    if rel not in files:
        return False, f'context: stamp {stamp_path} does not list {rel}. Fix: {fix}'
    return True, f'context: stamp {stamp_path} lists {rel}'


def git_lines(root: Path, *args: str) -> list[str] | None:
    """Run one read-only Git subcommand; None when it fails. Optional locks are disabled so nothing is written."""
    # Inherited GIT_DIR / GIT_WORK_TREE / GIT_INDEX_FILE would point Git at another repository.
    env = {k: v for k, v in os.environ.items() if k not in REPO_ENV}
    env['GIT_OPTIONAL_LOCKS'] = '0'
    try:
        cp = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True,
                            env=env, timeout=GIT_TIMEOUT, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as error:
        raise Unavailable(f'git failed: {error.__class__.__name__}') from error
    if cp.returncode != 0:
        return None
    return [line for line in cp.stdout.splitlines() if line]


def design_ok(config: dict, root: Path) -> tuple[bool, str, bool]:
    """Predicate (b): a handwritten page under wiki_root changed since the base, uncommitted or untracked.

    Returns (ok, note, notice): `notice` asks for the note to be shown even when the edit passes.
    """
    skip = config.get('skip_file')
    if skip and (root / skip).is_file():
        reason = ' '.join((root / skip).read_text(encoding='utf-8', errors='replace')[:200].split())
        if reason:
            return True, f'design: waived by {skip}: {reason}', True
        return False, f'design: {skip} exists but holds no reason. Fix: write why the Wiki design is skipped, or remove it', False
    wiki_root = config['wiki_root'].strip('/')
    base_ref = config.get('base_ref', 'origin/main')
    generated = config.get('generated', [])
    merge_base = git_lines(root, 'merge-base', 'HEAD', base_ref)
    if not merge_base:
        return True, f'design: not judged (no merge-base of HEAD and {base_ref})', True
    changed = set(git_lines(root, 'diff', '--name-only', merge_base[0], '--', wiki_root) or [])
    changed |= set(git_lines(root, 'ls-files', '--others', '--exclude-standard', '--', wiki_root) or [])
    handwritten = sorted(path for path in changed
                         if not any(glob_match(pattern, path[len(wiki_root) + 1:]) for pattern in generated))
    if handwritten:
        return True, f'design: {len(handwritten)} handwritten change(s) under {wiki_root} (e.g. {handwritten[0]})', False
    hint = config.get('design_hint') or f'write the design on the owning page under {wiki_root} before editing code'
    skip_note = f'; or record a reason in {skip}' if skip else ''
    excluded = f' (generated excluded: {", ".join(generated)})' if generated else ''
    return False, (f'design: no handwritten change under {wiki_root} since merge-base(HEAD, {base_ref}), '
                   f'in the working tree or untracked{excluded}. Fix: {hint}{skip_note}'), False


def judge(event: dict) -> tuple[int, list[str]]:
    """Return (exit code, stderr lines). Raises Unavailable when the gate cannot judge."""
    if event.get('hook_event_name') != 'PreToolUse' or event.get('tool_name') not in TOOLS:
        return 0, []
    tool_input = event.get('tool_input')
    raw = tool_input.get('file_path') if isinstance(tool_input, dict) else None
    if not isinstance(raw, str) or not raw:
        return 0, []
    path = Path(raw)
    if not path.is_absolute():
        cwd = event.get('cwd')
        if not isinstance(cwd, str) or not Path(cwd).is_absolute():
            raise Unavailable('relative file_path without an absolute cwd')
        path = Path(cwd) / path
    root = find_root(path)
    if root is None:
        return 0, []
    config = read_config(root)
    if config is None:
        return 0, []
    rel = relative_posix(root, str(path))
    if rel is None or not is_locked(config, root, rel):
        return 0, []
    ok_a, note_a = context_ok(config, root, rel)
    ok_b, note_b, notice = design_ok(config, root) if config.get('design_first') else (True, '', False)
    if ok_a and ok_b:
        return 0, [f'project-wiki edit gate: {rel}: {note_b}'] if notice else []
    lines = [f'project-wiki edit gate: {rel} is locked by {CONFIG_PATH.as_posix()}; edit blocked']
    lines += ['- ' + note for ok, note in ((ok_a, note_a), (ok_b, note_b)) if not ok]
    return 2, lines


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(MAX_EVENT + 1)
        if len(raw) > MAX_EVENT:
            raise Unavailable('event exceeds budget')
        event = json.loads(raw.decode('utf-8'))
        if not isinstance(event, dict):
            raise Unavailable('event must be an object')
        code, lines = judge(event)
    except Unavailable as error:
        code, lines = 0, [f'project-wiki edit gate unavailable ({error}); edit not judged']
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as error:
        code, lines = 0, [f'project-wiki edit gate unavailable ({error.__class__.__name__}); edit not judged']
    for line in lines:
        print(line, file=sys.stderr)
    return code


if __name__ == '__main__':
    sys.exit(main())
