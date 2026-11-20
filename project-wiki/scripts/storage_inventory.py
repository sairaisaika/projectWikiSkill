#!/usr/bin/env python3
"""Bounded, read-only apparent-size inventory for an explicitly selected project."""
import argparse
from collections import deque
import json
import os
from pathlib import Path
import stat
import unicodedata

REPARSE_POINT = 0x400
REPORT_LIMIT = 25


def is_link(info):
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & REPARSE_POINT
    )


def root_directory(path):
    root = Path(path).absolute()
    if root == root.parent or ".." in root.parts:
        raise ValueError("select an explicit project directory, not a filesystem root or '..' path")
    for item in (*reversed(root.parents), root):
        info = item.lstat()
        if is_link(info) or not stat.S_ISDIR(info.st_mode):
            raise ValueError("root and its ancestors must be real directories, not links/reparse points")
    return root, info.st_dev


def path_part(name):
    return unicodedata.normalize("NFC", unicodedata.normalize("NFC", name).casefold())


def exclusion(path):
    # A single portable spelling, never a glob, rooted path or parent traversal.
    # On Windows refuse spellings that the filesystem can alias or reinterpret.
    parts = tuple(path.split("/"))
    if ("\\" in path or ":" in path or "\0" in path
            or any(not part or part in (".", "..") for part in parts)
            or (os.name == "nt" and any(part.endswith((".", " ")) for part in parts))):
        raise ValueError("--exclude needs a project-relative path with '/' separators")
    return tuple(map(path_part, parts))


def restricted_int(maximum):
    def parse(value):
        try:
            result = int(value)
        except ValueError:
            result = 0
        if not 1 <= result <= maximum:
            raise argparse.ArgumentTypeError(f"must be an integer between 1 and {maximum}")
        return result
    return parse


def inventory(path, max_entries, max_depth, exclude=()):
    root, root_dev = root_directory(path)
    excluded = {exclusion(value) for value in exclude}
    counts = dict(entries=0, excluded=0, links_or_reparse=0, foreign_filesystems=0,
                  other_special=0, errors=0, depth_cutoff_dirs=0)
    rows = []
    reasons = set()
    queue = deque()

    def scan(directory, parts=(), owner=None):
        try:
            # Best-effort refuse changed directories; a live tree is not a snapshot.
            current = directory.lstat()
            if is_link(current) or not stat.S_ISDIR(current.st_mode) or current.st_dev != root_dev:
                raise OSError("directory changed while scanning")
            with os.scandir(directory) as children:
                for child in children:
                    counts["entries"] += 1
                    child_parts = (*parts, path_part(child.name))
                    if child_parts in excluded:
                        counts["excluded"] += 1
                    else:
                        visit(child, child_parts, owner)
                    if counts["entries"] >= max_entries:
                        reasons.add("entry_budget_reached")
                        if owner is not None:
                            owner["partial"] = True
                        return False
            return True
        except OSError:
            counts["errors"] += 1
            reasons.add("unreadable_or_changed_entries")
            if owner is not None:
                owner["partial"] = True
            return False

    def visit(child, parts, owner):
        try:
            # DirEntry.stat() does not fill st_dev on Windows.
            info = os.lstat(child.path)
        except OSError:
            counts["errors"] += 1
            reasons.add("unreadable_or_changed_entries")
            if owner is not None:
                owner["partial"] = True
            return
        if is_link(info):
            counts["links_or_reparse"] += 1
            return
        if info.st_dev != root_dev:
            counts["foreign_filesystems"] += 1
            return
        directory = stat.S_ISDIR(info.st_mode)
        if not directory and not stat.S_ISREG(info.st_mode):
            counts["other_special"] += 1
            return
        if owner is None:
            owner = dict(name=child.name, kind="directory" if directory else "file",
                         apparent_bytes=0, partial=False)
            rows.append(owner)
        if directory:
            if len(parts) >= max_depth:
                owner["partial"] = True
                counts["depth_cutoff_dirs"] += 1
                reasons.add("depth_bound_reached")
            else:
                queue.append((Path(child.path), parts, owner))
        else:
            owner["apparent_bytes"] += info.st_size

    root_entries_complete = scan(root)
    while queue and counts["entries"] < max_entries:
        scan(*queue.popleft())
    for _, _, owner in queue:
        owner["partial"] = True
    rows.sort(key=lambda row: (-row["apparent_bytes"], row["name"]))
    return {
        "status": "partial" if reasons else "complete_within_scan_policy",
        "partial_reasons": sorted(reasons),
        "apparent_bytes": sum(row["apparent_bytes"] for row in rows),
        "allocated_bytes": None,
        "reclaimable_bytes": None,
        "root_entries_complete": root_entries_complete,
        "max_entries": max_entries,
        "max_depth": max_depth,
        "counts": counts,
        "ranked_immediate_children": rows[:REPORT_LIMIT],
        "omitted_ranked_children": max(0, len(rows) - REPORT_LIMIT),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Read metadata only and rank an explicit project's immediate children by scanned apparent bytes (JSON).",
        epilog="Immediate children are visited first, then subtrees breadth-first. The live scan is not a snapshot: "
        "enumeration order affects partial results. Top rows rank scanned bytes only. "
        "Link/reparse entries and different-device entries are skipped; same-device mounts may be included. "
        "Hard links are counted per name. Apparent bytes are not allocated or reclaimable bytes. "
        "This does not determine usage, ownership, safety to remove, or complete coverage of a changing tree.",
    )
    parser.add_argument("--root", required=True, help="project directory; links/reparse points in root path are rejected")
    parser.add_argument("--max-entries", type=restricted_int(100_000), default=10_000,
                        help="global encounter budget including skips (default: 10000; max: 100000)")
    parser.add_argument("--max-depth", type=restricted_int(32), default=4,
                        help="maximum descendant depth, immediate children = 1 (default: 4; max: 32)")
    parser.add_argument("--exclude", action="append", default=[], metavar="RELATIVE/PATH",
                        help="repeatable literal child path with '/' separators, omitted before explicit metadata inspection; case-insensitive and Unicode-normalized on every platform")
    args = parser.parse_args()
    try:
        result = inventory(args.root, args.max_entries, args.max_depth, args.exclude)
    except OSError:
        parser.error("could not inspect the specified project root")
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
