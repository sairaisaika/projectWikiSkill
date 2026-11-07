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

Eight new cases check exact application and unchanged artifact bytes/mtime, a
changed loose body file, unrelated source edits, stale originals, tampered plans,
no-op source mtime, no native/Git/state recomputation, legacy plans and receipt argv.
Full source, matrix CI, packages, host exchange and actual fresh use are separate
checkpoints. Locale defaults and arbitrary caller shell filtering remain known
friction; they are not claimed fixed by this command.
