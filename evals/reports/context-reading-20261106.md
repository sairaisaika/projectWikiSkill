# Context-reading source evaluation (2026-11-06)

Status authority: [current state](../../docs/wiki/status.md#current-state).

## Problem and scope

Real use exposed file context fetched after edits, scope lost to line truncation,
and dated verification notes read as current deployment. This source slice adds
usable preparation and reading views; it does not add a gate or update a host.
Private consumer evidence stays outside this public repository.

## Counterexamples and acceptance

The old source failed the omission-first index, missing-format diagnostics and
prefix help tests; the new APIs were absent. The initial 15-case baseline had
4 failures / 10 errors, with malformed-manifest behavior already passing. Focused
behavior now covers complete file owners on query miss, existing changes,
source drift, snapshot-only page reading without Git/filesystem probes, history
separation, product headings containing "history", revision observations without
capability promotion, saved-view tampering, transport/display budgets, exact
native impact failure diagnostics and write-new-only output.

A later budget test initially hit the existing native-report budget before the
new saved-reading budget; inject a valid already-captured native context to test
that distinct boundary. This was test-harness correction, not a product fix.

## PR45 review

Reviewed exact bf2d12b against fc310fe: eight documentation files, no helper/hook
or test mutation. The rules accurately distinguish native-project ownership and
unimplemented gate gaps; no blocking documentation defect found in the changed
text. Passing its checks does not implement its proposed mechanisms. This branch
stacks on that candidate without altering its branch. The previously documented
omitted-last index gap is addressed here; the pre-edit shell-write and unbound
waiver limitations remain unchanged and explicitly outside this slice.

## Verification boundary

Focused and full-suite, fixture, maintainer Wiki, package closure and exact CI
receipts are summarized in the final PR. A bounded real native-router replay is
performed only in an isolated source clone: complete scope and saved views are
compared to original native records, not to a cut terminal excerpt. No active
worker's router/stamp, source checkout, installation or hooks are changed.
This is not a fresh-agent adoption trial, and no token or efficiency gain is claimed.

## Bounded integration replay

In an isolated consumer snapshot, the compact view retained all three selected
files, all seven declared owner edges, fourteen unexpanded candidates and the
one unregistered input. Default delivery was 3,692 bytes; the same query and file
scope's full native text was 64,157 bytes. These are different views: page bodies
are intentionally not delivered by the index and must be requested. This is a
transport observation, not a token-saving or task-success measurement.

A saved owner page exposed six older verification notes independently of its
body and left current state unknown (no authored current-state section). Ten
body qualifiers remained review candidates; none was automatically promoted.
A second preparation after deliberate tracked/new-file edits in the isolated
clone named both existing changes and left prior reading unestablished.
Regression cases also cover fenced headings and section expansion when separate
current-state metadata exceeds the display budget.

## Source verification receipts

- Python source suite: 280 tests, passed with one pre-existing platform skip;
  25 focused context-reading cases are included.
- Fixture suite: 12 tests passed; curated routing evaluation: 24/24 locations,
  20/20 top-one known queries and 4/4 unknown rejections. These are self-tests.
- Maintainer and fixture Wiki checks pass; generated route indexes rebuilt.
- Plain, legacy-hook and portable-hook packages match source and identity 0.2.20
  under doctor. This is package closure, not installation or hook execution.
- Cross-platform CI remains a separate observation on the final PR head.

## Maintainer routing correction

The final self-query `prepare` initially returned zero candidates: the route had
only the longer phrase "file-first preparation". The failed result was retained
before adding the command's exact name to that existing route. Replay now reaches
workflow-capture, with no new route or selector change. This informed repair is
not independent retrieval validation.

## Cross-platform correction

The first final-head Windows run failed one new path-basis assertion: the fixture
used the runner's short temporary pathname while capture correctly stored its
resolved long pathname. The assertion now compares the resolved expected Path,
retaining the check that the reported base identifies the real selected root.
No production path policy was changed. Final-head CI is re-run after this test
portability repair; earlier Linux success is not substituted for that result.
