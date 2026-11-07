# Dated current-state heading repair

Real consumer: Mindbridge wiki20.2 `## 当前状态（2026-11-06）` was not recognized by the shared CURRENT matcher. A replacement inserted a second Current state while leaving the old deployment claim under a still-current heading. This was a parser/rotation miss, not a request for another checklist.

The common matcher now accepts ISO-dated current aliases. Reading displays the declared heading; changed-state rotation archives the original dated heading/body and removes its old date from the replacement heading. Same-content updates remain no-ops. Historical/fenced/nondate headings stay outside current state; old saved unknown projections are not retrospectively reinterpreted.

Four regressions, including localized variants, old/new body separation, exact archival and idempotence. Old source produced five failing subcases; valid red/green logs were retained outside the repository. Source checks/CI, installation, native-entry adoption and live product acceptance remain separate in the status page.

## Real saved-page replay and caller-format counterexample

With installed0.2.27, the selected release-page current section returned as a complete1589-character view, excluding the older production snapshot. Its selected historical view was read in two contiguous spans0:3318 and3318:6064, totaling6064 characters with no gap or duplicate; snapshot-only continuation did not recollect the native index. This verifies the saved-view boundary, not independent semantic review or every historical statement in the source.

A subsequent caller-data audit found that nine manually archived blocks across four pages contained same-level Markdown headings. Those headings correctly ended the parser's History section, putting old statements back into the body. This was a manual archive construction error; automatic update-state already encloses its snapshots. The existing literal fenced-snapshot format repaired the data: each original block remained verbatim in history and was absent from body; authored-link checks passed. No parser guessing, new gate or inferred deployment state was added. Thus the earlier two-part reading was not claimed as proof that all source history was classified correctly.

The original Claude session still reported a model limit at19:53Z without a new reset time. Installation and Codex replay are separate from fresh natural Claude adoption; no extra model probe or paid-credit action was used for this observation.
