# Repeated explicit file groups

A coordinator used the actual capture CLI with multiple `--files` groups while
preparing coupled-project work. The parser kept only the final group, so the
native router validated an already incomplete selection. The returned capture
was inspected and corrected before implementation. This was a guided operational
discovery, not an independent blind trial or a measured efficiency claim.

The old parser is covered by three real-CLI controls. The repeated nonempty and
empty-later cases failed; the single/absent/empty compatibility control passed.
The candidate accumulates groups in the one existing argument declaration,
then reuses existing path normalization, deduplication and native routing. The
same three tests pass, including the full selected satellite/source-hash keys.
An initial test mistakenly repeated a missing path in its final group, masking
part of the loss; it was corrected before the parser fix. Earlier output is
retained privately rather than counted as a valid nonempty-group negative.

This boundary is explicit input preservation. It does not infer missing files,
certify that every consumer was declared, change allowed-path permissions or
replace semantic review. A coordinator must still inspect the actual capture
and reconcile the real diff. Existing start, delegation, reading and finish
checks remain in place. The local full suite ran202 tests:200 passed and two
host-dependent symlink cases were explicitly skipped. All12 fixture tests
passed; the curated navigation check retained20/20 known routes and4/4 unknown
rejections. These are local source controls, not the cross-platform CI matrix.
Package closure and normal source adoption are recorded separately; no installed
host or running scoped worker has been changed by this candidate.
