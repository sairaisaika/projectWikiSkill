# Saved current-section view, 2026-11-17

Source candidate only, from an isolated branch. Local source and package checks are recorded below. Nothing here was merged, remote-CI-verified on other platforms, or installed. It makes no claim about adoption or efficiency.

## Observed defect (pilot project, generic)

Agents reading the pilot project's saved Wiki pages kept guessing an English
`Current state` heading. The authored headings actually used `Current`, `Current status`,
`当前状态`, `现状` or dated current labels. The existing `--section-index` outline plus an exact
`--section` read did work, but it cost an extra discovery step. On long pages, older status
text further buried the current claims.

## Change

`show --capture|--packet PATH --view current --path PAGE` reuses the saved page projection,
the existing `CURRENT` labels, the `saved_headings` parsing and the existing pager. It
returns `selected` only when the saved body has exactly one authored, nonhistorical
current heading. Otherwise it returns `unknown` or `ambiguous`, together with the
outline, page and history reader commands. The contract lives in
[architecture.md#task-views](../../docs/wiki/architecture.md#task-views).

## Controls

| Control set | Prior source | After |
|---|---|---|
| `CurrentViewTests`: 9 tests (labels incl. Chinese/dated, history/fenced, multiple/nested/generated-reset, missing/mismatched/malformed metadata plus legacy capture, stale freshness, long Unicode continuation and cursor mismatch, option conflicts, packet parity, unchanged views and summary hint) | Original source: 1 failure + 24 errors (the view did not exist) | 9 pass |
| `CurrentGeneratedBoundaryTests`: 5 tests | First candidate: 5 failing subcases in 3 tests (generated-only heading selected as authored; generated block included in the section; authored heading reported ambiguous beside a generated duplicate). The fenced-marker and unchanged-projection controls already passed and are kept as preservation checks | 5 pass |
| Same-capture output comparison, original source vs repaired source, 50 existing view invocations (capture/packet; page/history/section/outline/summary/impact/feature/all/locator/index; text/JSON) | — | 46 identical. The 4 that differ are summary/index text, by the one intended Expand hint. Capture fields differ only in timestamps and the existing `reader_sha256` reader binding |

The first candidate stopped at a turn cap before delivery. That is recorded as partial
work. It was neither a quota exhaustion nor an accepted delivery. An independent pure
counterexample (a current heading inside a generated block being reported as authored)
led to the generated-boundary repair.

## Limits

- Generated blocks use saved unfenced begin/end markers with matching names and nested balance. Mismatched closes cannot expose current claims; an unclosed opener counts as generated through the end of the body. This is a saved-text convention, not execution of a generator.
- Existing `page_projection`, `authored_current_state`, page/history text and JSON, and older capture bytes are deliberately unchanged. They still treat generated text the same way as before.
- Selecting a section does not mean it was read and does not verify it. Its declared dates and claims are not certified.

## Independent nested-boundary return

Root reproduced two further controls (three failed subcases) against the delivered candidate: an inner close exposed an outer generated Current heading, and unmatched named/generic closes also exposed it. A current-view-only name stack repairs both; a positive control preserves an authored heading after the matching outer close. The earlier projection/default JSON is unchanged. Final combined validation is recorded in the current status owner after execution.

## Guided saved-snapshot replay

Root opened three real pilot snapshots through the stable current selector without supplying headings. It selected the original Chinese current labels and exact authored spans (178, 760 and 1,913 characters), keeping current-input checking false in snapshot-only mode. This is a guided frozen replay, not independent natural adoption, whole-page reading, live production proof or the six-pair handoff experiment.

## Final local source closure

Root independently ran the full original unit suite:436 collected,435 executed and one existing platform skip, exit0; fixture12/12, fixture check/evaluate and maintainer check all exit0. Default, legacy-hooks and portable-hooks packages each built and passed source-bound doctor (six exit0 results). The16 current-view controls pass after the two independent nested-boundary controls were added. These are local source/package results, not platform CI, installation or six-pair handoff proof.

## First platform CI failure and Windows reproduction

The initial PR Windows3.13 job failed the new long-section assertion; Linux passed and fail-fast canceled a companion job. Root reproduced on Windows3.13: the saved section contained93 CR characters, while the fixture expected only LF. The reader retained the original CRLF correctly. The test now compares the fully reassembled section exactly to the saved body span, without normalizing the product output or weakening byte preservation. This is a fixture portability correction, not a pager-data-loss fix. The failed platform attempt remains evidence; replacement exact-head CI is separate.

The subsequent local Windows16-control run reached another POSIX-only fixture assumption in reverse cursor parsing. It now reuses the existing platform-aware argv reader rather than splitting an unquoted flag. This correction also changes no product code. Both local platform reruns and the replacement CI are evaluated separately.
