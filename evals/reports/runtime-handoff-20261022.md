# Guided runtime handoff follow-up, 2026-10-22 (C42/C43)

This is an operator-observed follow-up with a familiar coordinator and the same
engineering worker, not a blind adoption trial or an efficiency measurement.
Private host paths, identities, logs and task packets remain outside this report.
The installed payload stays 0.2.4; this report does not change runtime tools.

## Observations and boundaries

| Observation | Evidence obtained | What it does not establish |
|---|---|---|
| A refreshed mission packet and two source-bound deliveries reached one resumed engineering lead | Actual tool Read calls for four mission/input files and an explicit progress ACK naming the two exact heads and adoption order | A file copied into a task directory by itself did not establish receipt; a later inbox still lacked an observed Read ACK |
| An earlier ad-hoc repository CLI watcher ran from a handoff directory | Wrong-working-directory failures were visible; the worker retired three stale loops and resumed from the repository directory | This was not a bug in native capture: `workflow.py` already executes the native command with `cwd=root` |
| A completed check was still waited on | The summary log reported 71 checks and zero failures, while the only matching process was the wait shell; its full command contained the substring it searched for | A live PID or elapsed time did not establish useful work; a completed check did not mean the full business gate had passed |
| The coordinator retired that wait only | A separate guarded script checked the exact PID, command shape and sole process match before signalling only the waiting shell; the engineering lead was preserved | This did not implement a general orchestrator, hook or automatic packet delivery channel |
| Current source added another fix after a prior full green | A separate, revision-bound browser component probe and before/after regression isolated a new timing counterexample | Earlier green CI, packet ACK or independent mechanism checks did not certify the newly composed source, staging or native acceptance |

The first inline cleanup attempt failed shell parsing before execution. A small
file-based guarded operation then completed; this is recovery evidence, not an
error-free automation claim. The operator kept both event boundaries explicit.

## Method implications

The current [collaboration workflow](../../project-wiki/references/collaboration-workflow.md)
and [implementation](../../project-wiki/scripts/workflow.py) already separate
packet creation from dispatch and actual use. Keep that contract: capture owns
repository execution context, delegation constrains scope, and finish reconciles
actual source and evidence. Do not turn this incident into another global reading
gate or falsely claim that native capture launched or stopped the worker.

An external runtime controller should retain the execution repository, task and
session identity, owned child PID or job handle, terminal result and next safe
action separately from the wiki packet. Wait on the returned handle or explicit
completion receipt, not a substring that can match the wait command itself.
A new inbox needs its own observed consumption checkpoint; an earlier ACK cannot
cover messages created later. No such automatic runtime controller was delivered
by this follow-up, and forced interruption is not a substitute for receipt.

## Remaining evaluation

- Test an actual host-supported message channel while a worker is active and
  verify later-packet Read/ACK without duplicate sessions or shared-tree writes.
- Run a fresh successor handoff from the final adopted source, retaining private
  operational receipts separately from public method reports.
- Measure time and omissions before making efficiency claims. Component probes,
  native return closure and production journey acceptance stay distinct.

## Persistent input pilot (C44)

The current CLI help and the official [CLI reference](https://code.claude.com/docs/en/cli-reference)
expose streaming JSON input/output and replayed input messages. The official
[streaming-input guide](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)
describes queued messages in a persistent session. These capabilities were then
checked locally; documentation alone was not treated as runtime proof.

A fresh read-only subscription session received an initial synthetic file task.
After its actual Read tool call was observed, the coordinator created another
file containing a new random token and sent a second user message over the same
open stdin. The same process/session acknowledged both exact message IDs, actually
read both files and returned both tokens, then exited normally after explicit EOF
(9.67 seconds). The preliminary collector also counted two tool-result user events
as ACK candidates; the final receipt correlates only the two sent IDs. Raw events
and the preliminary receipt were retained privately, not replaced silently.

A separate private Linux transport prototype then exercised explicit queued input,
nonblocking stdin, private logs, exact-ID ACK correlation, no automatic request
replay, and explicit input closure. Five bounded checks covered duplicate IDs,
different content under the same ID, terminal/reused-run refusal, nonzero child
exit, and refusal before touching an already-live engineering session. A second
fresh read-only CLI trial through that prototype delivered two messages, observed
two actual Reads/two successful results and both random tokens, and exited 0 after
explicit EOF in 8.74 seconds. See the [sanitized receipt](stream-input-20261022.json).

This is an internal operations prototype, not an installed plugin capability,
global/distributed session lock, quota controller or permission boundary. The
already-running engineering lead was not interrupted or migrated. Its later
patch inbox still needed actual Read/adoption evidence. The prototype must be
used only after the prior owner is authoritatively terminal; there is no automatic
restart or permission escalation. Real wiki/source integration and release
acceptance remain separate. This follow-up adds no packaged runtime payload.
