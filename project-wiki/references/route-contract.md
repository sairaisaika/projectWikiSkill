# Structured engineering routes (schema 2)

Use `docs/wiki/routes.json` as the curated manifest. Use a small engineering entry
to explain query vocabulary; keep large explanations feature-local. Source declarations
and explanations have different jobs: a file list alone is not an engineering wiki.

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

The optional root `diagram_policy` declares required view kinds and explicit
not_applicable reasons. See the [six-view framework](diagram-framework.md). Coverage
counts only diagrams on structurally valid routes; it is not render or semantic proof.

Optional root `task_maps` declare compound work surfaces and existing route IDs;
their docs/scope are checked and enter snapshots. Use `task` to list them and
`task <id>` to expand all declared surfaces without application source reads.
See [change navigation](change-navigation.md) for schema and scope evaluation.

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
