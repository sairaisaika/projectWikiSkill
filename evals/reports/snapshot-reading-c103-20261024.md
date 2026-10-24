# C103: permission-separated task reading

UTC2026-10-24. This is a guided engineering follow-up, not a blind trial, a
measured speedup or certification of complete agent/business adoption.

## Observed need and boundary

Two actual bounded reviews had a task-level ban on every Git command. The reader
recognized that default workflow `show` reaches a Git-backed freshness check and
did not run it. The coordinator supplied its real saved view/currentness receipt;
the reader separately consumed the packet and exact source records. Neither
receipt was substituted for the other. Old failed product probes were retained.

The existing reading command therefore needed an explicit mode suitable for this
permission boundary. Repository-readonly metadata alone did not grant permission
to run the helper's implicit Git. This was a tool/workflow friction point, not
evidence of an unauthorized command by those reviewers or a production event.

`show --snapshot-only` renders saved records without a current-check attempt. It
keeps the full selected feature and impact data, native return vocabulary,
omissions, peer/source observations and selected-evidence policy. Index expansion
commands retain the flag. Currentness is visibly **not checked**; captured matches
and hashes are not fresh observations. Foreign artifact paths remain strings in
this view. The mode does not authenticate the unsigned projection or validate a
reader's interpretation.

There is no flag on capture/start/delegate/review-template/finish. Changed inputs
and evidence still reject new dispatch through their original guards. Existing
read-only scope validation is unchanged. Coordinator checks, delivered context,
actual reading, semantic correctness and runtime acceptance remain distinct.

## Reproducible checks

The first four new interface checks produced1failure/3errors against the old
source: the CLI did not recognize the flag and `task_view` lacked its optional
argument. A separate preserved rerun has the same result. This establishes an
absent interface, not a production failure or a measurement that Git executed.

The repaired focused checks test zero live-check/hash/Git/native-subprocess calls,
mode-preserving expansions and complete native records, changed source/evidence
remaining invalid for delegation, actual CLI reading with Git absent from PATH,
rejection of the flag on delegation, foreign path record retention, retained
readonly-scope validation, and default current/stale display behavior. The default
Git-attempt spy is separate from the new mode's zero-call assertion.

Seven focused tests pass. The Windows full suite ran174 tests:172 passed and2
host symlink-permission skips; no failures. Candidate0.2.9 packaging produced22
payload files; doctor found package/source, support inputs and source input bytes
matching. Installation, hooks and adoption remain unverified by doctor.

A private candidate-helper copy replayed a fixed real read-only task packet on
Linux through actual CLI index/all/feature/impact views with an empty PATH. All
four retained the relevant original records and unchecked-currentness labels;
the saved packet bytes remained unchanged. This replay did not perform a live
source check or certify a new dispatch. Independent semantic review and actual
worker use are pending; no installation or host refresh is claimed.
Private raw commands, logs, hashes and task paths stay outside this public report.
No private account, clinical content, repository identity or session path is
included here.

## Remaining

- Independently read the new implementation and replay a fixed real task packet
  under the original worker command restriction, with new output destinations.
- Adopt source/package/host through their normal paths and inspect each layer.
- Measure real routing/read cost and interpretation quality separately; neither
  fewer synthetic calls nor rendering a packet proves a faster/correct agent.
