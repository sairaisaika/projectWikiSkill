# SoulNest native wiki audit · 2026-10-15

This is a familiar-reviewer application of the skill to an existing wiki, not an
independent adoption trial or a schema-2 structural score.

The wiki has a native TypeScript model, responsibility-based chapters, diagram
catalog, producer/consumer tables, reverse file-to-page impacts, mention-coverage
ratchets and change-touch checks. It should keep those strengths rather than
migrate to a second handwritten manifest. The skill's helper does not natively
ingest this representation; that compatibility dimension is not measured as pass.

## Observed work

- Restored 176 interrupted review pages from six worktrees; another group's 30
  pages already matched main. Carried-forward review is distinguished from fresh
  source sampling. A clean primary tree had hidden this outstanding work.
- Repaired a real Docker build failure: wiki tooling imported shared helpers from
  a test directory omitted from packaging. Local test success had not proved the
  build's dependency closure. The isolated production build completed.
- Verified that a rolled-back migration dry run was documented as active database
  access control. Read-only catalog inspection contradicted that claim; the wiki
  now separates written migration, installed schema and live behavior.
- Corrected an interface-equivalence claim: a wrapper reused identity resolution
  but projected away role and test-partition fields before calling its handler.
- Reconciled stale page-ownership rules and cross-page summary counts without
  removing the project's founder-authorized workflow.

## Measurements and limits

Native model: 211 chapter/leaf pages and 265 cataloged diagrams (260 in chapters, five on the entry page). Mention coverage
after recovery: 243/298 API routes, 116/149 tables and 88/138 registered source
files. These are string-mention counts, not semantic coverage.

A 12-question self-test exercised the **actual browser search input handler** with
DOM/fetch stubs and the generated native index: ten mapped questions, two unknown
controls. Initial top-1 was 5/10, top-2 10/10, unknown rejection 2/2. A general
explanation-before-source ordering for concept/symbol queries (explicit file
paths still prefer source) changed top-1 to 8/10, with top-2 and rejection unchanged.
No per-question aliases were added. Two queries still need the second result.
Natural-language understanding, independent use, elapsed-time savings and full
diagram semantics were not measured.

The skill suite ran 66 tests successfully with one host-permission symlink skip
(65 executed tests passed). The new guidance is documentation; no claim is made
that the Python helper now understands the native TypeScript wiki schema.

## Feedback incorporated

See [native wiki adoption](../../project-wiki/references/native-wiki-adoption.md):
respect native representations; recover base/main/review states; follow declarations
through reachable writers and real consumers; keep return/throw/catch boundaries
and deployment evidence separate; use native mention/touch checks without inflating
their meaning. Producer/consumer matrices and reverse impact maps are useful
portable techniques from this project, not lower-grade substitutes for routes.json.

Remaining limitations: no native adapter, no independent blind trial, no causal
speed comparison and no full page-by-page or arrow-by-arrow semantic certification.
