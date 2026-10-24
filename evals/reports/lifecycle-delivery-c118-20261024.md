# Optional lifecycle delivery candidate and canonical-input boundary

## Scope and design

The existing workflow already carries task identity, owner, allowed paths,
source/peer observations, native return requirements and unresolved impacts.
This candidate adds an opt-in internal package profile that can deliver its
saved index at session startup/resume/compaction. It uses the original
`task_view(..., snapshot_only=True)` rather than another router or task registry.
The normal skill-only profile remains available. No host configuration, trust,
active worker, model credentials or publishing authority is changed by building.

The adapter requires one explicit packet environment variable and matching local
workspace. It neither invokes Git/native routing nor executes quoted page
commands, reads transcripts, scans a Wiki or writes an import cache. Task JSON is
labelled untrusted data. Invalid delivery is visible and nonblocking; an oversized
index is explicitly undelivered, with a pointer to the original reader. The final
index budget is 6 KiB of ASCII JSON plus a short wrapper. Host preview/token
limits and trusted triggering remain separate observations.

## Checks actually performed

- Initial Windows Python 3.13 suite: 185 tests, 183 passed and two pre-existing
  unprivileged-symbolic-link skips. Fixture behavior tests: 12 passed. Fixture
  Wiki structure/drift and declared navigation checks passed. These are not a
  full product or host-lifecycle acceptance result.
- Initial focused adapter/package checks: ten passed. They exercised the actual
  saved reader with Git/source hashing/subprocess calls forbidden, workspace
  mismatch, explicit opt-out, malformed/budget failures, optional host profiles,
  closure tampering and packaged sibling-module loading.
- The exact generated Windows `commandWindows` string ran under PowerShell with
  a synthetic fixture task. Separately, the exact generated Unix command ran on
  Linux with a real previously captured private task: one feature, two impacted
  files and three omitted candidates remained visible. It reported saved-only
  currentness unchecked; the protected packet and checkout identity remained
  unchanged. Package-only inspection still passed after execution.
- Those command replays supplied hook-shaped input directly. They were **not**
  trusted host hook invocations, injected developer-context receipts, physical
  reading evidence or fresh task dispatch. The initial command replays preceded
  the conservative context-budget refinement; final replay is tracked separately.

## Independent review and retained failure

A separately scoped read-only reviewer checked ten selected source hashes before
and after its review, with no Git, package commands, tests, host or source edits.
It reproduced the Windows directory-junction primitive: `is_symlink()` can be
false while `rglob()` reads outside the selected canonical skill tree. The shared
builder traversal affected both package profiles; its historical introduction
was not attributed from memory.

The coordinator then reproduced the full pre-fix builder behavior using only a
synthetic external marker: the marker was copied into a package. No real private
source was involved. The failure and original package were retained. The repair
rejects resolved aliases/escapes before any canonical input is read and during
the final inventory/byte checks. A new Windows junction regression covers both
profiles; the final focused suite passed all eleven cases. Replaying the same
retained synthetic source against the repaired builder rejected both profiles
before creating an output directory.

The reviewer also identified a host-budget uncertainty, without claiming a
character limit or observed host truncation. The coordinator reduced the adapter
budget and preserved the distinction between adapter output and actual host
delivery. No command-execution defect was found in the inspected saved-reader
path; that bounded result is not a general security audit.

A follow-up independently confirmed the junction source repair and found one
remaining output-bound defect: a valid long Unicode path expanded the overflow
JSON to 10,837 bytes despite the 6 KiB index cap. That failure was retained too.
The final fallback references only the fixed environment selector, not an
expanded path. A targeted long-Unicode-path regression now checks the full
wrapped overflow output. Replaying the final adapter on the same retained valid
1,874-character synthetic path produced a 599-byte wrapped notice, with its
original packet unchanged. This does not establish observed host truncation.

After the junction repair, the complete local suite ran 186 tests: 184 passed,
the same two Windows symbolic-link cases skipped; fixture and navigation checks
passed. A documentation trailing-blank-line check initially failed and was fixed.
After the final overflow repair, all twelve focused lifecycle cases passed.
Normal final-head cross-platform CI is still recorded separately.
The first source CI failed on Linux because the synthetic long-path regression
itself exceeded that filesystem's byte limit before reaching the mocked reader;
the production entry already handles such `OSError` as a delivery warning. The
fixture was shortened below that limit while retaining an ASCII-escaped size
above the former overflow budget. The original failure is retained, not labelled
flaky or erased by a same-source retry.

## Remaining acceptance

Normal source/PR/main CI, optional package/source closure, installation and actual
host triggering have separate evidence. Official Codex documentation requires
review/trust of the exact non-managed hook definition. No trust records or bypass
flags were used. Linux Claude's normal trust/policy and interpreter availability
also apply; an active scoped engineering worker was not upgraded.

Fresh-process delivery, reader expansion/use, correct task adoption, comparative
cost/missed-link improvements, automatic lifecycle breadth and business acceptance
remain unverified. Existing explicit CLI task packages remain the fallback.

References: [Codex hooks](https://learn.chatgpt.com/docs/hooks),
[manual plugin packaging](https://developers.openai.com/plugins/build/plugins),
[Claude hooks](https://code.claude.com/docs/en/hooks).
