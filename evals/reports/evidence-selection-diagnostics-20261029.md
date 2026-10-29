---
type: Evaluation
---
# Selected-evidence diagnostic ordinal — bounded self-test

## Source and problem
Base b8a1782ac032db61bd2216681c316cb6823fe503; candidate source version 0.2.18.
The observed real capture correctly refused missing selected evidence but returned
only `Selected artifact is missing or unreadable`. Later caller-guessed incorrect
paths caused the same unlocated refusal. Treat this as one diagnostic deficiency,
not multiple production incidents; correcting guessed paths remains the caller's
responsibility. Public fixtures contain no real product paths or evidence contents.

## Plan and smallest seam
[Plan](../../docs/EVIDENCE_SELECTION_DIAGNOSTICS_PLAN.md) began with the native
[Selected evidence reference](../../project-wiki/references/collaboration-workflow.md#selected-evidence-files).
Only `artifact_snapshot` per-item messages change: append `(selection item N)`
to each existing safe prefix. List-level validation, JSON keys, exit 1, hashing,
sorted unique saved policy, write-new-only and refusal rules remain unchanged.
No new lookup, permission, retry, installation, hook or skill-instruction change.

An ordinal names the list being checked. Initial capture uses repeated input order;
after native execution and in saved-policy consumers it uses sorted unique paths.
It is not a shell argv offset and is not always the original input position.

## Reproduction and checks
- Actual subprocess CLI with two selections, first existing and second missing:
  old implementation exits 1 with unchanged JSON envelope but fails the new exact
  ordinal assertion. The candidate passes that same subprocess assertion, still
  exits 1, writes no output file, emits no stderr or selected path/content.
- Ordering regression deliberately reverses input/sorted order: the same deleted
  file is item 1 in the input list and item 2 in the saved list.
- Existing-file directory, relative path, symlink and parent alias remain refused;
  suffix identifies the second selection. Malformed selection-list shape retains
  the old list-level message, without a guessed ordinal.
- PermissionError injection checks generic message and no OS detail reflection;
  non-root POSIX mode-bit unreadability also ran. Real symlink checks ran on Linux.
- Existing legacy/unselected, overwrite detection, saved views, return policy and
  write-new-only cases remain in the focused class (actual name PreservedEvidenceTests).
- Focused class: 17 tests passed. Initial complete suite: 239 tests, one failure
  because this new README report link had been added before its target existed;
  one Windows directory-junction skip. This was a documentation staging error,
  not a product-policy failure. Final suite result is recorded below after rerun.

Reproduction commands (repository root):
```sh
python3 -m unittest discover -s tests -p test_workflow.py -k cli_missing_second_selection -v
python3 -m unittest discover -s tests -p test_workflow.py -k PreservedEvidenceTests -v
python3 -m unittest discover -s tests -v
```

## Boundaries and next adoption
This is an author self-test, including real subprocess and Linux filesystem probes.
Windows ACL/unreadability and junction behavior were not exercised here; portable
injection is not Windows runtime proof. Original frozen delivery installation is
untouched. Candidate has not been installed, published or independently adopted.
Next evidence is another real coordinator handoff using this exact candidate,
checking that the ordinal helps locate an input while refusal still holds; retain
its actual result separately rather than treating this fixture as adoption.

## Knowledge and efficiency return
README led to Selected evidence and then artifact_snapshot/capture/check consumers;
no business Wiki copy or whole-repository source scan was needed. An initial combined
read was truncated; bounded reads recovered the relevant rules/test class. The class
name supplied in the task differed from the real source and was corrected before
execution. Tests exposed the missing report target, which was then created. The
reference now documents order and privacy limits at the original task route.
No timing, token saving or monetary cost claim was measured.

## Final source acceptance
Python 3.12.3 on Linux: complete suite ran 239 tests, OK with one existing
Windows directory-junction skip. The last rerun includes explicit proof that the
missing-file exception cause contains the selected absolute fixture path while
the real subprocess CLI returns only the safe JSON error and empty stderr.
PermissionError injection also carries a filename. No trace or underlying OS
message is serialized. `git diff --check` passed.

The existing 0.2.17 product reader adoption is separate evidence for old
capabilities, not adoption of this 0.2.18 diagnostic. Independent review and the
next real diagnostic handoff remain pending. No commit, push or installation
was performed by this slice.

## Independent review and next real handoff
An independent reader reran17 focused tests, three additional actual CLI cases, and the full239-test suite (one Windows junction test skipped on Linux). Eight source/document files retained their hashes through review. The reader independently checked a post-router deletion whose selected item number changes after saved sorting, legacy success, and write-new-only refusal. A plan/PROJECT test-class name was corrected afterwards; implementation remained frozen.

The next real task discovered that both the Web and mobile copies of an iOS URL acceptance receipt named a screenshot absent from their audit directories, although the original image still existed in the handoff. This was a coordinator evidence-return omission; previous Markdown/HTML anchor checks did not validate this JSON reference.
Candidate helper hash c5017764570b57fecb847d3c92869bd8e3f60db3b478a3a3fcbbb701dfcab8c2 was used in that task. Its first actual capture selected the receipt followed by the missing referenced image and returned exit1, the original error prefix plus selection item2, empty stderr, and no capture output. The coordinator mapped that item to its explicit selection, copied the existing original image into both audit directories, and checked the receipt SHA without retaking or editing the image. Capture and start then passed. This is a real preparation use of the new diagnostic, not automatic discovery, copying, or proof of semantic acceptance.
The original Claude iOS owner is now reading that packet and checking actual image/receipt/Wiki consistency. Worker return and final reconciliation are still pending. The image remains an OS confirmation dialog; no JS callback or authenticated journey is thereby accepted. No host install/trust/hooks changed.

Package validation: default skill-only0.2.18 package built successfully with23 payload files; current doctor reports package/source/support/input bytes/identity matching. Hooks were not included, installation was not performed, and host execution/delivery layers remain unverified.
