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

## Initial source acceptance (before independent review)
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
The original Claude iOS owner subsequently read the packet, inspected image/receipt/Wiki consistency, updated the two business pages and original task records, and returned the six scoped paths. Root reviewed the actual diff and unchanged selected hashes; capture-return and finish returned structural_reconciliation=true with no issues or capability gaps. This establishes the scoped evidence-return workflow, not product completion. The image remains an OS confirmation dialog; no JS callback or authenticated journey is thereby accepted. No host install/trust/hooks changed.

Package validation: default skill-only0.2.18 package built successfully with23 payload files; current doctor reports package/source/support/input bytes/identity matching. Hooks were not included, installation was not performed, and host execution/delivery layers remain unverified.

## Windows CI portability rework
Root reported CI40968530564 at83613b24589b0f65abf1a2c916cbe3469a418e35: Windows3.13 job123779103149 failed only the new cause-string assertion. WinError2 formats the filename using repr, so its escaped backslashes do not match the raw path string. Ubuntu3.10/3.13 passed; Windows3.10 was cancelled by fail-fast. This is a test assertion portability defect, not a demonstrated runtime diagnostic/privacy failure.
The test now compares `Path(cause.filename)` directly to the selected missing Path. It still proves the cause is FileNotFoundError and retains the actual subprocess assertions: exact safe JSON, exit1, no capture output, no path/name/content in stdout/stderr, and empty stderr. workflow.py remains SHA256 c5017764570b57fecb847d3c92869bd8e3f60db3b478a3a3fcbbb701dfcab8c2.
Focused PreservedEvidenceTests rerun on Linux:17 passed, including the real CLI case. Windows CI rerun remains pending; this local result is not Windows acceptance. No commit/push or host configuration change was performed in this rework. Prior independent review and real preparation adoption receipts above are preserved.
Efficiency: exact CI file/assertion mapped directly to the existing test; no new tool, policy, or broad source investigation was needed. No token/cost measurement.

## Actual task return and efficiency review
The iOS task used candidate workflow.py c5017764 throughout capture, start, worker reading, return and finish. The original Claude owner updated the actual image links and an inline image while retaining the OS confirmation versus JavaScript callback boundary. The native index was 10,159 bytes, feature view 44,019 bytes, two impact views 8,973 and 8,960 bytes; the selected task projection was 79,626 bytes. These are output bytes, not token counts or a demonstrated saving. The owner did not need the separate 75,293-byte full capture after reading the projection.

This task also exposed a separate missing startup screenshot in the mobile audit directory. Root preserved the completed six-path return, scoped the follow-up in the original mobile task, and copied the existing original image. A bounded scan of the two relevant audit directories in both repositories verified five screenshot references against declared hashes. The initial diagnostic helped locate an explicitly selected missing file; it did not automatically discover every JSON dependency. Shared site rendering and full product journeys remain separate pending work.

Evidence remains in the original product task records and coordinator handoff: 20261029-ios-evidence-closure/{actual-missing-refusal.json,return.json,review.json,reconciliation.json,related-screenshot-check.json}. No user intervention was needed for the routine image repair. No measured before/after latency, total context reduction, token or fee improvement is asserted.
