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

## 2026-10-19 implementation follow-up

SoulNest adopted native behavior scopes in four existing pages (MFA, profile,
Web release and staging). One integration assertion required every pilot to keep
pending wording even after actual acceptance. Removing that maturity assertion
retained authored-scope presence, dictionary links and full source-to-card
projection checks. This is a document-contract correction, not expanded product
acceptance across every role, tier or client.

Actual `wiki-task --files` use exposed another adoption gap: seven login-helper
consumers and an export test had been listed as bare paths in chapter sources,
which the native `path » symbol` parser did not index. Real symbol entries now
resolve those eight files to the owning pages through the existing model and CLI;
the consent caller also reaches its consent page. The final native documentation
suite passed 325 checks and the reader built 218 pages with 1425 source views.
Rendered prose or a source-view page alone had not established map registration.

Web PR13/PR14 adopted mandatory main-push CI plus artifact-bound staged E2E/SEO
gates and the unsqueezed focused editor. Production application source is
`9c187708bc9d`; wiki closeout is `97ac17edb927`. The exact-source stage ran 23
actual passes without skips, flaky results or helper login retries. A user-filled
production patient test account verified the focused view, draft retention,
unsaved preview and restored content after reload without submitting a save.
Calendar, real CAPTCHA activation, native-client and remaining audience coverage
stay open. These are fitted implementation/acceptance observations, not an
independent blind trial or evidence of reduced agent working time.

Earlier attempt evidence stays separate: a retained premerge navigation failure
cannot explain a later same-case failure whose details were overwritten. The
new production candidate's first raw gate report was captured privately before
replacement could occur; permanent per-attempt archival remains follow-up work.

## 2026-10-19 optional language and method route pilot

SoulNest PR16 adds wiki 1.9 as a short disambiguation route: product vocabulary
links to root CONTEXT, actor/resource terms to the existing 1.7 dictionary, and
review/test/deployment/delivery wording to the existing methods. It adds no
authorization registry, business-state enum, forbidden-word scanner or startup
reading requirement. The actual query `wiki用词 方法词典` reaches 1.9 first.

The candidate passed 326 native documentation checks (219 pages); the existing
root-sidebar check first rejected the missing new-page registration and passed
after the link was added. The private reader on a separate loopback port showed
candidate `ab379c01a831`, the same page and a rendered routing diagram, with the
existing domain/method links. This records authored structure, actual routing
and reader adoption in a review candidate, not main or application deployment.

Its concrete example retains a separate evidence boundary: PR15's original
fixed-clock booking spec fails with a real 409 collision against the same 9c
application; candidate specs select actual availability and observe three
passing booking/reschedule flows including owned cancellation/readback. That
does not close unrelated schema drift, full consultation journeys or native
acceptance. These were familiar-author trials; no independent comprehension,
time saving or causal efficiency result was measured. The optional approach is
now guidance in native-wiki-adoption, rather than another required entry layer.
