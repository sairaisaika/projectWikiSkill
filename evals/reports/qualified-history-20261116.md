# Qualified history boundary — 2026-11-16

## Actual failure

A guided real audit used the new compact reader but selected a page containing several archival containers. The existing parser recognized the plain history label, then ended that container at a same-level heading named History: followed by an archival description. Because the qualified heading was not recognized, its old not-implemented claims entered current body text. This is a parser defect, separate from genuinely stale authored current paragraphs.

The final reader only continues an already explicit history container when a same-level heading uses an existing label and an ASCII/fullwidth colon, including a bare colon. Standalone Archive: supported export and History: back-button support stay in current body outside an active archive; immediately following an explicit archive at the same level, they continue it. Fenced headings stay literal. The exact global matcher used for choosing a state-snapshot owner and validating authored state remains unchanged; page projection and heading rows share the contextual rule. The planner now resets at generated-block openers as the reader already did, including unqualified archives; this intentionally aligns their previous disagreement.

## Returned candidate and independent source review

The first global-regex candidate passed410 unit tests, but a scoped genuine Opus review exercised its shared write-planner callers. It confirmed that a new state snapshot moved under the wrong qualified archive, standalone product subtitles became hidden, and valid current-body subtitles became rejected. Root returned that implementation rather than publishing it. New controls against the returned candidate give3 failures/2 errors. A first revised run also exposed one over-specific test expecting nested headings in the existing authored-state projection; its two assertions were corrected to preserve actual Markdown and the existing projection contract. The contextual revision passed47 focused tests. A second Opus pass then found a generated-block boundary where the reader reset history but the planner did not; its old-source counterexample fails before the one-line scanner alignment. The final48 focused tests pass, including bare-colon continuation, both write-planner regressions and generated-boundary agreement.

## Counterexamples and same-source replay

The initial three controls reproduce five failures on the original reader. Final controls additionally keep state snapshots under their original archive, accept supported product subtitles in current bodies, and retain both fresh-capture and fenced-code behaviour.

On the exact same frozen real Markdown, current body falls from100571 to95120 UTF-8 bytes and history grows from63460 to68911. The exact old not-implemented claim moves into history, and the authored Current state is unchanged. This is evidence separation, not a claim of general output or token savings. The remaining95 KB current body is still large.

Older prepared projections remain unchanged evidence. Fresh preparation is required to obtain the corrected projection; source freshness is not semantic correctness.

## Real-use limits observed separately

The audit invoked the installed Skill and explicitly selected the uninstalled compact candidate reader. It followed an index but aggregated continuations into one host result, which was truncated; it selected an omitted page as a feature and received an explicit error; it skipped all planned per-file impact views and read only selected page sections. A private35-part page dump is not proof of full reading. The first run hit its turn limit without delivery; a bounded continuation then returned a partial source audit.

Thus the compact-source replay remains valid, but natural file-first use and independent cold-start adoption remain unproven. No reminder or gate was added to certify those behaviours. The parser fix closes the concrete history leak; output aggregation, reading selection and remaining source/runtime gaps stay explicit.

## Verification

Final focused48 pass after the original five failures and the returned-candidate regressions. Root final413 collected/412 executed/1 existing skip, fixture12/check/evaluation, maintainer check and all three0.2.36 package/source doctors pass. A third scoped Opus review confirms the returned source regressions are resolved, with no further actionable issue in inspected scope. Exact platform/main CI remains separately pending; see version status. No global Skill installation or original feature-session change has occurred in this source change.

## Post-merge observation

The exact platform/main matrices and later Linux static installation are now verified separately in the [installed/use follow-up](installed-036-observation-20261116.md). The source-checkpoint pending statements above are historical; current version status remains in docs/wiki/status.md.
