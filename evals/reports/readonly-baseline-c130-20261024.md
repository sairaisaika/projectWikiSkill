# Read-only baseline advice before review

## Observed problem

A coordinator selected a recovered working overlay for a read-only review.
Selected bytes stayed unchanged during the review, but final reconciliation
correctly rejected an unchanged-return claim: implementation differences already
existed relative to the captured Git commit. The historical failure remains a
failure. This was a coordinator baseline-selection error, not evidence that the
reviewer edited the project or that a product test failed.

The original helper permitted this useful source inspection without explaining
the existing final-return mismatch at task creation. Late discovery wastes review
effort and invites conflating equal selected hashes with an unchanged repository.

## Generic change

The candidate uses one `repository_changes` collector for both final
reconciliation and early read-only advice. `start --read-only` and read-only
delegation record existing Git-base differences, declared peer availability and
planned untracked source files. Delegation recomputes the advice. The saved
observation includes a labelled bounded path sample and does not replace the
complete planned-file/satellite inventory.

Source inspection remains allowed. No files are committed, cleaned, hidden or
automatically granted edit permission. Final reconciliation still recomputes
changes; neither a saved clean claim nor this new observation can override it.
Every display retains the saved advisory. Snapshot-only display remains free of
Git, native commands and live hashing, while older packets report an unavailable
observation rather than an invented clean baseline.

## Recorded source exercises

- Before the change, six focused controls produced **five failures and one
  passing editing-task control**: early advice was absent, including when a
  parent carried a stale clean claim. This is a synthetic test of the missing
  capability, separate from the historical real return failure.
- After the change, **eight focused tests passed**. They cover dirty and clean
  roots, dirty/unavailable peers, planned untracked source versus pre-existing
  unselected cache files, recomputation on delegation, bounded samples, legacy
  packet display, command-free saved views, and unchanged-return rejection after
  later edits. An intermediate refactor missed a local peer variable; its two
  test errors were retained and corrected before this result.
- The original and candidate CLI were also run against the same unchanged real
  recovered capture. The original produced no early advisory; the candidate
  reported **24 existing differences** with an explicitly truncated sample.
  Both returned empty edit permissions and `dispatch: not performed`. The prior
  failed reconciliation was not rewritten or rerun into a green certificate.
- Full local unit run: **210 tests, 208 passed and two skipped** because this
  Windows host cannot create the symlinks needed by those existing controls.
  These skips are not passing symlink evidence; the normal Linux/Windows CI
  matrix must report its own result.

## Limits and adoption

This is a familiar coordinator exercise, not an independent blind review,
measured time/token saving, full source reading, continuous monitoring or product
acceptance. It moves an existing predicate earlier; it does not prove that the
coordinator chooses the correct source snapshot or that the native impact map is
semantically complete. No active worker or installed host was updated by these
source exercises. Installation, normal hook review, lifecycle delivery, reader
use, semantic correctness and business behavior remain separate evidence layers.
