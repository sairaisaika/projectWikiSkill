# Native selected-source consistency, C91

This is a familiar coordinator's actual coupled-project exercise, not a blind
navigation, speedup or business-acceptance trial. The framework change is generic;
project identities, host paths, user data and raw private reports are not copied
into this public evaluation.

## Observed gap and intended boundary

The existing0.2.6 helper correctly pinned explicitly declared root/peer snapshots,
and documented that correct pairing remained the caller's responsibility. In an
actual exercise the native router selected another client checkout through its
ambient configuration. Its reported path/revision disagreed with the declared
peer while capture and a properly formed read-only start both succeeded. No
mismatched task was dispatched. An initial characterization command omitted the
required acceptance/capability arguments; that rejection was a caller fixture
error, and the corrected command used the same immutable capture.

The missing capability was comparison of those two existing observations, not
source attestation or authority to select a different repository. Candidate0.2.7
adds an explicit adapter argument, `--native-source-context <JSON-pointer>`, for
native `{label: {root, revision}}` records. Labels are opaque. Every selected root
and peer must match; missing, stale, contradictory and unavailable observations
are not treated as empty success. Legacy adapters retain `not_requested`.

## Actual evidence

- The candidate CLI rejected the same actual mismatched native selection with
  exit1 and created no capture file. The correctly selected pair captured with
  exit0, then passed read-only start and displayed the matched comparison in its
  index. This used the original local task router and actual Git snapshots.
- Eight new focused tests cover arbitrary native labels, wrong peer selection,
  old revision, unknown/conflicting metadata, a peer named `root`, missing/bad
  pointer, comparison retention and the real CLI option. The first48-test workflow
  run had47pass/1fail: policy retention was present in review preparation but
  missing in final reconciliation. The regression was preserved and the final
  path fixed; its isolated replay then passed.
- The final complete Python suite ran150 tests, with149 passed and1 existing
  skip. Candidate packaging and source-aware doctor both exited0, with valid
  package bytes/source and no doctor issues. Windows Python3.13 was the observed
  local runtime; the normal CI matrix remains a separate adoption requirement.
- Matching observations follow index, full/feature/impact views and delegation.
  Final capture/reconciliation cannot silently drop the selected comparison policy.
  Native context, omitted candidates and complete satellite scope are preserved.

## Deliberate limits

The comparison only checks reported checkout identities against selected snapshot
identities. It does not trace physical reads, establish that a deployment pair is
correct, prove agent comprehension or certify source semantics. Existing input
hash freshness and actual-diff reconciliation remain separate checks. The
characterization and candidate replay did not modify project repositories,
install plugins, change hooks/trust, publish credentials, deploy the product or
interact with devices.

Normal source/main adoption and installed host updates are pending at this
candidate checkpoint. The observed Windows host stays on0.2.6 and the active
scoped Linux worker stays on0.2.4. Doctor installation, hook, context delivery,
agent use, semantic review and business layers remain unverified unless proved
by separate evidence. This report does not close the coupled product's feature
gaps or the overall user goal.
