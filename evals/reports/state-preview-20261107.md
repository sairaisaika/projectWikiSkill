# Saved state-preview reading (0.2.23)

Current source/host/delivery/use state is maintained in the
[version status table](../../docs/wiki/status.md#current-state). The observations
below are dated checkpoints and do not override it.

## Actual task feedback and corrected attribution

A fresh guided task after the account reset loaded0.2.22 with the installed
payload identity verified. Both primary implementation-file impacts and the
owning page original were read before product edits. The worker used its existing
prepared capture rather than rerunning the initial native query. A later fresh
capture was legitimate because the design changed the page bytes.

Limitations remain visible: a new test file triggered the host's old native-command
hint and the worker used `tail`; some secondary documentation contexts were
collected after editing. Zero platform truncation markers is not proof that such
shell output was complete. The worker used direct Read for the long owning page,
so this task did not independently demonstrate cursor use or same-output cache
reuse. No general efficiency or causal improvement is inferred.

The worker also inspected a saved state proposal by printing its diff. Initial
coordinator attribution to `update-state` stdout was wrong: source inspection
confirmed it already returned a compact receipt. That design assumption was
corrected before implementation. The missing mechanism was a bounded reader for
saved proposals/diffs, rather than another instruction to read carefully.

## Implemented behavior

New state plans retain exact original Markdown and its existing expected hash.
`show-state --plan PATH --view diff|proposed` checks saved hashes and reads only the
artifact; it never checks live project inputs, reruns a native command or applies
a write. The existing6000 UTF-8 byte/60-line pager provides content/view-bound
NEXT commands. Missing final newlines are explicit in diffs. Reading after apply
still shows captured original/proposed bytes, not an inferred live state.

The compact operation receipt retains its existing fields and adds an exact
reader argv. Explicit JSON is a full export. Older plans remain readable as
proposals; a diff without a captured original is refused instead of reconstructed.
The existing4MiB transport budget fails before source apply if the artifact is too
large. State source-byte/apply semantics are otherwise unchanged.

## Source verification checkpoint

Seventeen new cases cover full Unicode diff/proposal reconstruction through actual
CLI continuations, wire byte/line budgets, relative paths, content/view-bound
cursors, hash rejection, legacy proposals, explicit JSON, no-change and newline
handling, no live/native/write operations on reads, compact receipts and source
preservation at the artifact budget boundary. The full Linux suite passed351 cases
with one platform skip. Source CI, packages, installation and fresh0.2.23 worker
use follow this checkpoint and must be recorded separately.


### Native regeneration counterexample

Independent return review found that0.2.22 placed the old state snapshot between
the next generated block's opener and its heading. The actual native generator
then removed it while structural checks stayed green. The saved worker proposal
still contained the original, so the loss was recoverable and must not be reported
as successful history retention. An isolated replay on the same real page confirms
old behavior: present before generation, absent afterward. With0.2.23 the full old
current state remains after the real generator and251 native document/link checks
pass. No active developer tree was changed by the replay.

New snapshots now go immediately under the authored history heading. Recognized
name:begin/BEGIN comments also bound current projection/replacement, preserving
the following generated opener; fenced examples remain literal. Two existing pure
behaviors fail by assertion on0.2.22 (current projection included the opener and
replacement consumed it), and pass with the correction. These checks supplement
the real generator counterexample, not replace it. Arbitrary unrecognized native
marker formats remain outside this heuristic and need their native adapter.
