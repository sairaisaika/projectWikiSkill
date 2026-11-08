# Capture index alias: real command mismatch

2026-11-07. During the SoulNest task, the installed0.2.27 CLI advertised index but `show --capture ... --view index` returned Unsupported context view. This was a real helper incompatibility, not caller misuse or native output truncation. Two new regressions failed before the fix (one exception, one CLI failure); focused50 passed after it.

The implementation aliases capture index to the existing summary projection and renderer. Large Unicode owner inventories are reconstructed without loss via exact NEXT commands retaining index and snapshot-only. Explicit JSON is complete. Packet index, lifecycle delivery, freshness boundaries and mutation permissions are unchanged. No reminder, gate, hook, updater or host permission was added. Full suite, package/matrix and real replay are recorded separately when observed. Existing host/session instructions are not assumed updated by source changes.

Actual candidate replay of the original SoulNest context-post-draft-files capture with index + snapshot-only completed successfully and retained all four selected files/owners. This is coordinator replay of a historical capture, not a fresh worker-use observation. Full371 tests passed locally (one platform skip), maintainer Wiki build/check passed; release matrix/install remain pending.
