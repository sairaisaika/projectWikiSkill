# Cross-checkout newline provenance, 2026-10-22

## Observed boundary

A fresh clean source worktree was compared with an actual installed0.2.4 package.
Doctor reported a valid22-file package, matching identity/version, three skill
source mismatches and one support mismatch. Each of those four differences was
CRLF versus LF: normalizing CRLF pairs made the text byte-identical. The package
was internally coherent with its own receipt. This was not evidence of changed
instructions, installation failure or successful agent use. Raw host paths and
cache inventory remain private.

The builder copied worktree bytes verbatim. Consequently checkouts with equivalent
text but different Git/OS newline treatment produced different payload hashes.
A later clean checkout then failed exact source comparison against that package.
The strict old result was correct for bytes; its lack of a defined portable text
policy made cross-checkout provenance hard to use.

## Candidate format and unchanged strict boundaries

Version0.2.5 introduces receipt schema2 with the explicit
`source_byte_policy: utf8-crlf-to-lf-v1`:

- Validate UTF-8, replace CRLF pairs with LF, retain every other byte. Literal
  backslash escapes, whitespace, Unicode and content are not otherwise rewritten.
  Invalid UTF-8 or a lone CR fails before output creation; rejecting lone CR
  prevents a new CRLF pair appearing after normalization.
- Hash canonical source/support text and emit that canonical payload. Hash raw
  input bytes separately as `source_input_files`. Recheck those raw bytes before
  completing a build, so even newline-only input mutation during the build is
  still rejected. Additions to the source inventory during the build also reject
  completion.
- Doctor verifies installed/package file bytes exactly against their receipt.
  It never normalizes a modified package to let it pass. For schema2 source
  comparisons only, apply the declared text policy and report raw input equality
  separately as `source_input_bytes_match` and its mismatch list.
- Schema1 remains exact raw comparison. Unknown schema2 policy or incomplete raw
  input provenance fails closed. Material source edits remain mismatches even
  when identity/version is unchanged.

Thus LF and CRLF checkouts can have identical payload files while their raw input
provenance receipts differ. This is not a claim that those distinct receipts or
whole archives must have the same hash. The fixed format decoder appears in the
builder and standalone doctor; their conformance is tested. Doctor deliberately
never imports candidate package code just to inspect it.

The on-disk0.2.4 cache is not modified in place. The new package needs normal
source adoption, packaging and authorized host update. Existing source workers
can keep their explicitly pinned0.2.4 package until their bounded task ends.
No hook trust or semantic/runtime acceptance is inferred from any hash.

## Actual regression scope

Six focused cases initially had three failures: LF/CRLF payload equality, invalid
UTF-8 rejection and unknown-policy rejection. The existing semantic-change,
strict package-tampering and moving-input cases passed before this change and
continue to pass afterward. All six now pass, including legacy raw receipts,
separate raw provenance and rejection of a newline-only mid-build mutation.

This is one actual host mismatch plus controlled cross-checkout fixtures, not
new installed0.2.5 adoption, full cross-host runtime acceptance or a measured
reduction in task effort. Full existing tests and exact remote CI are reported
separately in the candidate PR; no old green is inherited by the new version.

## Independent review and closure corrections

A separately launched read-only reviewer inspected a frozen first candidate and
ran17 focused checks plus temporary probes. Original source hashes remained26/26
unchanged; the host wrote only its private plan/result record outside that source
copy. This was a source review, not a filesystem sandbox or host-activation test.

It found a pre-existing coherence gap: independently rewriting payload `files`
hashes could keep package/source flags true while the declared canonical maps
remained unchanged. The revised inspector cross-binds every skill and support
projection, rejects unbound files, and checks generated host manifests and full
identity projections. This is internal consistency of an unsigned receipt, not
proof of authenticity against someone who can rewrite every source/hash claim.

The review also found source UTF-8 errors incorrectly revoking package integrity,
noninteger schema tags, malformed receipt/identity exceptions, a non-idempotent
lone-CR boundary and additions missed during build. Root regression cases first
reproduced these results, then passed with the corrections. Source text problems
now remain source mismatches/errors while an intact package retains its integrity
evidence. The old raw-equality test was updated to the defined canonical text
contract; raw schema1 and tampered package negatives remain strict.

The frozen first candidate and original findings remain available privately.
A corrected candidate still requires fresh exact CI, normal adoption and explicit
host validation/update. It is not the installed0.2.4 package.

The first exact CI rejected two Windows mutation tests: their injection matched
the unresolved temporary path against the builder's resolved output path, so the
intended mutation did not occur. Compare resolved fixture paths and retain the
explicit assertion that injection happened. Preserve the failed runs; this test
harness correction does not relax the builder's rejection of changing inputs.
