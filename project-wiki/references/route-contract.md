# Structured engineering routes (schema 2)

Use `docs/wiki/routes.json` as the curated manifest. Use a small engineering entry
to explain query vocabulary; keep large explanations feature-local. Source declarations
and explanations have different jobs: a file list alone is not an engineering wiki.

When a technical boundary needs diagnostics, link its existing owner to the
[evidence-to-contract path](engineering-depth.md#debug-from-evidence-to-a-technical-contract).
Use native schema/tests and safe observations; no new route fields or logging
schema are required. Logs do not replace the contract.

## Record shape

```json
{
  "schema_version": 2,
  "project": "Example",
  "quality": {"min_structural_score": 85, "max_query_words": 450},
  "routes": [{
    "id": "public-api",
    "title": "Public request failures",
    "kind": "interface",
    "aliases": ["HTTP errors", "client failures"],
    "sources": [
      {"id": "port", "role": "declaration", "path": "src/ports.py", "symbol": "ArticleSource", "reason": "Public dependency shape"},
      {"id": "service", "role": "implementation", "path": "src/service.py", "symbol": "load_articles", "reason": "Maps dependency results"},
      {"id": "client", "role": "consumer", "path": "src/client.py", "symbol": "read_articles", "reason": "Consumes service failure"}
    ],
    "docs": ["docs/wiki/interfaces.md#public-api"],
    "interface": {
      "inputs": ["Article query"], "outputs": ["Result with articles"],
      "errors": ["Unavailable differs from empty"],
      "failure_modes": {"returned": ["Unavailable result"], "thrown": ["Dependency exceptions propagate"], "unsupported": ["No capability negotiation"]},
      "compatibility": "Keep existing data/null consumers working."
    },
    "rules": [{"id": "failure-not-empty", "statement": "Do not turn unavailable into zero articles.", "source_ids": ["service"], "tests": ["tests/test_service.py"]}],
    "impact": ["Client errors and empty-state copy must stay aligned."],
    "tests": ["tests/test_service.py"],
    "checks": [{"command": "python -m unittest discover -s tests", "scope": "Offline service mapping; not a live-provider check."}],
    "boundary": "Mocked transport does not verify real-provider behavior.",
    "unknowns": ["Live-provider failure behavior has not been observed."],
    "evidence": {"implementation": "implemented", "observations": [
      {"level": "source", "reference": "src/service.py", "claim": "Mapping implementation exists.", "revision": "reviewed revision", "observed_at": "2026-10-14"}
    ]},
    "reviewed_at": "2026-10-14"
  }]
}
```

This is a shape example, not an assertion that these paths exist in your project.
The repository's `evals/fixture-project/` provides a complete navigation fixture.
Adapt records to actual code; do not populate fields with guessed paths.

## Field semantics

- `kind`: interface, behavior, architecture, or plan. An implemented interface
  should locate its declaration and implementation separately; one source may serve
  both roles through two records. Pure functions do not need invented callers:
  state a justified non-applicability in impact/unknowns and report the scoring limit.
- Source IDs are unique within a route. Roles: declaration, implementation, caller,
  consumer, contract. `reason` explains why the editor should open that position.
  Optional `visibility` (public/internal) and nonempty `edit_for` string arrays
  identify declared edit seams; they do not prove sufficient impact coverage or
  increase the baseline score. See [change navigation](change-navigation.md).
- Choose exactly one `symbol` or `needle`. Python symbols use class/function
  qualification (`Repository.load`). Other languages use an exact declaration-line
  substring with one match. Duplicate needles fail; do not silently use the first.
- Source/test/doc/evidence paths are repository-relative and root-confined.
  Symlink escapes, absolute paths and `..` escapes are rejected. Shared multi-repo
  wikis link remote responsibility pages rather than escaping the source root.
- `docs` are Markdown paths with optional real headings/explicit HTML anchors.
  `rules` reference source IDs and optional test files, not just prose with no anchor.
  A rule row is the schema's invariant: `statement` is the rule, `source_ids` with
  role implementation enforce it and role consumer depend on it, `tests`/`checks`
  verify it, and the `docs` anchor declares it. Rule IDs are unique within a route,
  not site-wide, and there is no per-rule status, ledger citation or generated
  reverse projection; see [route by rule](change-navigation.md#route-by-rule-not-only-by-file)
  before using rules to key a gate.
- `interface` records inputs, outputs, errors and compatibility as understood by a
  caller. Lack of a supported cancellation or global budget port belongs in unknowns,
  not in a fabricated declaration.
- Interface routes also require `failure_modes.returned`, `thrown`, and `unsupported`
  as nonempty string arrays. State not applicable or not yet verified explicitly,
  rather than silently assuming exceptions are caught or optional methods exist.
- `checks` describe commands and their evidentiary scope. The helper never runs them.
  An existing test path does not prove its assertions cover the documented rule.
- Evidence has two axes: implementation (planned/implemented/mixed/unknown) and
  observations (source/offline-tested/installed/live-verified). They are not one
  progress percentage. Evidence references must exist; the helper does not certify
  their claims. Revision/date bind a review but do not turn it into runtime proof.
- Plans may have no sources and no completed observations; they must remain planned.
  Keep a plan's proposed interfaces apart from existing implementation records.
- A `kind: plan` route additionally requires a `plan` object with string arrays:
  `outcomes`, `dependencies`, `interfaces`, `deliverables`, `exit_evidence`, `unknowns`.
  Dependencies and unknowns may be explicitly empty; the other four must be nonempty.
  Audit reports 6/6 **field coverage**, not that a reviewer approved the plan's content.
- `unknowns: []` explicitly states none identified during this review. It does not
  prove none exist. `reviewed_at` records human/agent review, not CI generation time.
- Optional `diagrams`: objects with path (Markdown anchor), kind, question and scope.
  Choose architecture, flow, sequence, data-model, deployment or state-machine only
  when it clarifies the task. Do not demand six diagrams for every feature.
- Optional `engineering` profiles and diagram `source_ids` are specified in
  [engineering depth](engineering-depth.md). They add checkable lifecycle, data,
  execution and decision detail without making hardware constraints universal.

Optional route `diagram_requirement` declares `level` (project/section/page), a
boolean `required` and a nonempty `reason`. Required routes must have valid existing
`diagrams` references; explicit exemptions retain their reason. This is an opt-in
presence check, not automatic discovery of new pages or semantic classification.
See [diagram authoring and review](diagram-framework.md#author-at-project-section-and-page-scope).

The optional root `diagram_policy` declares required view kinds and explicit
not_applicable reasons. See the [six-view framework](diagram-framework.md). Coverage
counts only diagrams on structurally valid routes; it is not render or semantic proof.

Optional root `task_maps` declare compound work surfaces and existing route IDs;
their docs/scope are checked and enter snapshots. Use `task` to list them and
`task <id>` to expand all declared surfaces without application source reads.
See [change navigation](change-navigation.md) for schema and scope evaluation.


## Opt-in section evidence review

Use this only when a stable rule needs a retained evidence-review baseline. A fresh
index says locations were rebuilt; it does not say the authored rule was reviewed.
On an **existing schema 2 rule**, add a `review.section` pointing to one of that
route's existing `docs` anchors. Reuse the rule's `source_ids` and `tests`; do not
create a parallel registry. For the public offline fixture's `failure-not-empty`:

```json
"review": {"section": "docs/wiki/interfaces.md#public-api"}
```

Review that exact section, rule statement, selected source/config and tests yourself.
Commit the opt-in, exact `review.section`, reviewed content and bindings, then
explicitly record its **full Git
commit ID**. For example, from the repository checkout (replace `FULL_COMMIT`):

```sh
python project-wiki/scripts/wiki.py review --root evals/fixture-project public-api failure-not-empty --revision FULL_COMMIT --repository-url https://github.com/sairaisaika/projectWikiSkill
python project-wiki/scripts/wiki.py build --root evals/fixture-project
python project-wiki/scripts/wiki.py find --root evals/fixture-project "client failures"
python project-wiki/scripts/wiki.py check --root evals/fixture-project --reviews
```

`review` writes only a `baseline` receipt under that rule in `routes.json`: the
explicitly reviewed commit, rule/section/evidence SHA256 fingerprints and reviewed
locations. Inspect that receipt diff before committing. It refuses selected content
or bindings that do not match the supplied commit. It does **not** assess truth,
run tests, change authored prose or repair code. A reviewer may verify an unchanged
rule against changed evidence, or revise it first; either requires this explicit
recording step. `build` only regenerates indexes and never clears a review baseline.

`find` reports `needs_review` for a selected rule whose prose, statement, evidence
or selection changed, including after rebuilding. `status` exposes outstanding
opted-in rules. Only `check --reviews` adds the review condition to the existing
check; plain `check` keeps its structure/index contract. Rules without `review`
retain their existing behavior and need no Git history. There is no automatic hook,
background collection or adoption/migration requirement.

Fingerprint boundaries are deliberately explicit:

- The exact ATX section (including its subsections) ends at the next same/higher
  heading. Unrelated neighboring prose does not invalidate it. Missing or ambiguous
  headings/attached anchors fail closed.
- A Python source symbol hashes its text including decorators and body, independent
  of its file/line position. A pure move remains reviewed after the project updates
  the declared source path and rebuilds; no scanner guesses new paths. Dependencies
  outside that body must be selected separately through existing route sources.
- Other languages/config use the existing unique `needle` locator and hash the
  **whole selected file**, conservatively; no universal syntax parser is implied.
  Selected tests also hash their whole file. UTF-8 and normalized newlines are used;
  same line/function counts cannot hide content changes.

Both text and JSON `find` retain a current path/line locator and the immutable
reviewed Git object/line. Optional `--repository-url` supplies GitHub-compatible
`/blob/COMMIT/PATH#L…` links; it is caller-declared, never inferred from a remote or
proof of repository identity/access. Without it, use the recorded Git object with
`git show`. The opt-in path requires Git 2.45+ with `--no-lazy-fetch` support. It disables optional
locks, replace refs and lazy object downloads, and bounds each Git lookup to 15 seconds.
The reviewed commit must remain available locally (including in CI);
missing history, evidence, duplicate targets or damaged receipts remain unresolved,
not fresh. Receipts are review records, not signatures or semantic/runtime proof.

The opt-in pilot runs on isolated copies of the public offline fixture in
`tests/test_section_review.py`; the shipped fixture's normal route behavior remains
unchanged. Projects choose their own small set of rules and PR check invocation.

## Existing schema 1 wikis

`audit` reads schema 1 as a **legacy gap analysis** and lists missing precision
fields. It does not silently upgrade, manufacture rule provenance, or award schema-2
readiness. Schema 1 can still be queried using its original sources/docs/checks.
`build`, `check`, and schema-2 quality gates require schema 2. Migrate a small set of
high-value routes by inspecting their declaration/implementation/consumer and
recording real contracts, rules, checks and evidence. Leave unreviewed routes explicit.

## Generated artifacts

`build` writes only `docs/wiki/route-index.json` and `route-index.md`, never source
or curated routes. Locations use current line numbers and UTF-8/LF-normalized SHA-256;
CRLF/LF changes alone do not cause drift. A changed source file flags all routes
referencing that file: this is a conservative review signal, not semantic diffing.

`check` fails for malformed records, broken/ambiguous source positions, missing
docs/anchors/tests/evidence, stale snapshots or a structural score below the configured
floor. No command is inferred or run to repair a failure. Queries tolerate unrelated
broken routes and return selected-route warnings plus their remaining doc pointers.
