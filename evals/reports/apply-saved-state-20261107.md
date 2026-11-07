# Applying a reviewed saved state (0.2.24)

Current adoption is recorded only in the [version table](../../docs/wiki/status.md#current-state).

A real0.2.23 documentation task used the saved-preview reader and NEXT commands,
but still filtered some displayed chunks. It also had to extract verification text
and resend state arguments to apply after review. The repeated parameter handling
was unnecessary and could regenerate a different proposal. This follow-up exposes
the existing saved-plan applier as `apply-state --plan PATH`, and supplies its argv
in the existing compact receipt. No new collection, policy gate or updater is added.

The exact reviewed artifact remains unchanged. Existing kind/proposal hash,
Wiki-root/symlink and original-page-byte checks still apply; stale source refuses
rather than silently refreshing. The combined update-state --apply stays compatible.
The operation certifies neither caller-authored semantics nor human business approval.

Nine new cases check exact application and unchanged artifact bytes/mtime, a
changed loose body file, unrelated source edits, stale originals, tampered plans,
no-op source mtime, no native/Git/state recomputation, legacy plans and receipt argv.
Full source, matrix CI, packages, host exchange and actual fresh use are separate
checkpoints. Locale defaults and arbitrary caller shell filtering remain known
friction; they are not claimed fixed by this command.


Windows follow-up: two new assertions used read_text, which normalizes CRLF,
against a plan intentionally retaining original line endings. Exact-byte application
already passed. The assertions now compare bytes, and an explicit CRLF source case
runs on every platform. No application semantics or preservation assertion was
relaxed. Final matrix/host evidence supersedes the first candidate.


### Final source and exact-plan task

Final d5866cf ran360 Linux source cases with one platform skip; nine new cases also
passed on local Windows. All four Ubuntu/Windows Python3.10/3.13 jobs passed in
[final CI](https://github.com/sairaisaika/projectWikiSkill/actions/runs/42377141265).
Three final package profiles match source, support, input bytes and identity.
Merge675abca has the same tree as the tested head. One Linux manual copy was
atomically exchanged with21/21 hashes, old copy retained and settings unchanged;
no original session was restarted or marketplace/updater enabled.

A fresh guided finalization task loaded0.2.24 and the verified payload. It read the
approved saved diff in two complete bounded parts, called apply-state exactly once,
and called neither prepare nor update-state. The artifact hash stayed unchanged;
source bytes matched the expected original before apply and the proposed hash
immediately afterward. Full native generation left those bytes unchanged and
retained the original Current and earlier restored history. An independent return
check repeated the hash, single-current, old-heading and history assertions on the
returned checkpoint. The task was real documentation closure with a coordinator
reviewed plan, not a blind semantic task, live product acceptance or a causal
performance experiment. Locale defaults, earlier caller filtering and secondary
context omissions remain explicit limits.
