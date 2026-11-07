# Dated current-state heading repair

Real consumer: Mindbridge wiki20.2 `## 当前状态（2026-11-06）` was not recognized by the shared CURRENT matcher. A replacement inserted a second Current state while leaving the old deployment claim under a still-current heading. This was a parser/rotation miss, not a request for another checklist.

The common matcher now accepts ISO-dated current aliases. Reading displays the declared heading; changed-state rotation archives the original dated heading/body and removes its old date from the replacement heading. Same-content updates remain no-ops. Historical/fenced/nondate headings stay outside current state; old saved unknown projections are not retrospectively reinterpreted.

Four regressions, including localized variants, old/new body separation, exact archival and idempotence. Old source produced five failing subcases; valid red/green logs were retained outside the repository. Source checks/CI, installation, native-entry adoption and live product acceptance remain separate in the status page.
