# Reading-flow repair (0.2.22)

## Problem and resulting behavior

Guided real work still clipped long shell output, repeated native queries over
unchanged inputs and appended historical provenance into current sections. This
revision changes the existing reader and update mechanics, without another gate.
The maintainer Wiki architecture design was committed before implementation.

- New prepared captures opt into bounded text (6000 UTF-8 bytes/60 lines), with
  exact continuation commands for long indexes, records, sections and Unicode
  lines. Cursor identity includes saved text and view selection. Snapshot-only and
  explicit format survive continuation. Older captures/raw-native/packet JSON
  defaults stay compatible with active clients; explicit text bounds them too.
- Repeating prepare at its existing output reuses only an exact current request,
  including source/peer/runtime closure, helper identity and observed refs. No
  native command or artifact/time rewrite occurs on a hit. Stale/different evidence
  remains immutable and requires a distinct output.
- update-state previews caller-authored current content, then optionally applies
  against the exact original Wiki bytes. It preserves current heading spelling,
  preamble and metadata; previous state and older notes remain verbatim in fenced
  history. One latest recorded note remains compatible with native readers; an
  explicit caller-supplied replacement archives the previous note. Neither note
  nor current prose is inferred as business truth or deployment acceptance.

## Source regressions and controls

Forty-three new cases cover reconstruction of long Unicode text, byte/line budgets,
view-bound cursors, real CLI continuations from relative paths and reuse output,
legacy JSON compatibility, no redundant native execution, changed inputs/refs and
requests, immutable stale evidence, native heading anchors/preamble, state/history
retention, no-op updates, preview/apply, optimistic stale-write rejection and scope.

Five concrete old-behavior tests were run on the previous source independently:
duplicate default current output, undelivered large page, unbounded default impact,
failed same-output prepare and closed-ATX state projection all failed by assertion,
without relying on missing new APIs. New transform APIs have separate new behavior
and preservation tests. Four existing expectations intentionally changed from
refusal/nonreuse to explicit bounded continuation/current reuse.

## Native coordinator replay

A separate stable consumer checkout used its real native router through a reviewed
counting wrapper. First prepare made one native call, identical reuse made none,
and all subsequent reading left the total at one. Actual saved authored body
(22,031 characters) reconstructed over seven parts; history (4,197 characters)
over two. Each CLI part stayed within6000 bytes/60 lines and continuation preserved
snapshot-only mode. This is coordinator replay, not independent worker adoption.

An isolated application of the state operation to a real Wiki page exposed two
first-pass defects: metadata/preamble could fall into current state, and replacing
a localized heading broke existing section anchors. Both now have regressions.
Native provenance readers also need one latest recorded header, so the transform
keeps it rather than letting an older historical header become first by accident.
After applying caller-explicit provenance and regenerating the native index, the
native completeness/rendered-link checks passed251 cases. The initial failures
are retained privately; no active developer checkout was altered.

## Verification and remaining acceptance

Final full source, fixture, packaging and platform-CI receipts are recorded after
the source checkpoint. Host update and post-reset fresh-task use remain pending.
The old host stays pinned until a helper-idle atomic exchange; no settings, running
session, account or unrelated task is restarted. No background updater is added.

Reading a chunk is not proof an agent understood it; a current capture is only as
complete as its declared input closure. State writing cannot certify supplied
facts. No token/time savings or causal comparison is claimed. A fresh available
worker must validate actual use on an unrelated owned task before adoption closes.


## Initial source checkpoint verification

The final source suite ran333 cases successfully with one explicit platform skip;
42 reading-flow regressions are included. Before/after SHA256 over both runtime
modules, entry/reference, identity and tests stayed identical during this run.
Fixture12, fixture check/evaluate and maintainer Wiki build/check passed. Real
native reading replay and251 state/render checks are scoped above; they do not
stand in for host installation or a fresh real worker. Packaging and platform CI
follow the source checkpoint; adoption remains pending.


## Windows follow-up

First source CI passed Linux but failed on Windows3.13. New test readers used the
Windows locale codec for UTF-8 subprocess output and Markdown, causing a decode
exception, mojibake byte inflation and a false missing-history assertion. Test I/O
now explicitly uses UTF-8. Runtime stdout also explicitly uses LF, so Windows CRLF
translation cannot exceed the promised wire-byte limit; a new binary stdout test
checks the actual bytes. Budgets and preservation assertions were retained, not
relaxed. Final source/matrix verification must pass before host update.
