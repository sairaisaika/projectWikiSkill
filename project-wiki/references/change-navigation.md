# Compound changes and actual edit locations

Use this when a request spans multiple interfaces or a route stops at a large
factory. Keep ordinary one-surface queries simple.

## Declare the work surfaces before writing a plan

A top-two result can be accurate while omitting most of a compound task. For a
recurring change, provide a compact playbook and optional root `task_maps` record:

```json
{
  "task_maps": [{
    "id": "interface-change",
    "title": "Change interfaces and their rules",
    "scope": "Declared public/dependency/model/policy surfaces for this task",
    "docs": ["docs/wiki/change-playbook.md"],
    "surfaces": [{
      "id": "public",
      "question": "Which public failure contract changes?",
      "route_ids": ["public-api"],
      "why": "Align declaration, implementation and consumers."
    }]
  }]
}
```

Adapt surfaces to the project; the example is not a required four-part taxonomy.
Each surface identifies its question, relevant route IDs and why they belong.
Include cross-cutting compatibility/configuration work where applicable. State
technical dependencies inside the linked plan, without making independent work wait.

`task` lists maps; `task <id>` returns **all declared surfaces**, their route IDs
and doc pointers. It reads manifest/docs, not application source. `query` then
resolves selected source locations. A map is a curated task scope, not an inferred
whole-project dependency graph or proof that every consequence has been found.
Missing/duplicate route references and broken local map links fail checks. Map
changes enter the generated snapshot, so CI detects drift without auto-repair.

## Distinguish a declaration from a usable edit seam

For a concrete change, register the smallest useful existing helper, method,
serializer, guard or decision branch. Keep its declaration and real consumer too;
do not replace a public port with an internal helper as the supposed public API.
For a factory closure, an exact unique declaration-line needle is sufficient.

Optional source fields:

```json
{
  "id": "sanitize",
  "path": "src/model.py",
  "symbol": "sanitize_suggestions",
  "role": "implementation",
  "reason": "Shared rule implementation, not the model port",
  "visibility": "internal",
  "edit_for": ["Change confidence filtering and dropped-reason accounting"]
}
```

`edit_for` records what change this locator supports; `visibility` is `public` or
`internal` when verified. Omit unknown visibility. The helper validates fields and
counts located declared edit targets separately, without raising the base score.
It cannot determine whether the chosen helper is sufficient or really public.
Keep per-route query size bounded: remove redundant positions and duplicate prose,
or split a genuine concern into a focused route. Do not hide missing impact by
removing relevant routes or raising the response budget merely to pass.

## Review the boundaries that declarations cannot explain

- **Exception scope:** identify the exact operations inside each try/catch and
  those before/after it, including property access, serialization and host callbacks.
  Catching an awaited model call does not mean all later validation failures map
  to the same result. Link the wrapper and conversion seam where a plan needs it.
- **Shared rules:** locate every known caller of a common sanitizer/validator and
  record its distinct input, output and failure behavior. Update the model and
  imported-contribution paths together when both use the same rule.
- **Stage accounting:** candidate dropped counts, accepted suggestions, refused or
  unchanged writes, resolved labels and final counted records are different stages.
  Document conversion/commit points; do not present one stage's count as another's.
- **Ownership and commit:** a pure accepted result, append and status persistence
  are separate operations unless source establishes an atomic boundary. Record
  partial failure and required host guarantees as unknown/design work.

## Evaluate scope and usability independently

Add optional `task_map_cases` to the existing evaluation file, alongside ordinary
`tasks` (which retain ranking, unknown controls and response-budget checks):

```json
{
  "task_map_cases": [{
    "id": "compound-scope",
    "task_map": "interface-change",
    "expected_surfaces": ["public"],
    "expected_routes": ["public-api"]
  }]
}
```

Use the full independently reviewed scope for that task, not a list copied from
current output merely to get green results. Evaluation reports missing and
unexpected IDs; any mismatch fails even when top-1 still passes. This verifies
declared scope against expected scope, not semantic impact completeness.

In an actual trial, save a wiki-only first plan and missing facts **before** opening
source, then record targeted verification, corrections and rerun results separately.
Track prior familiarity, exploratory searches, full pages versus local sections,
truncated reads and six plan fields. Do not count hidden/truncated text as read.
The helper's source reads for line resolution differ from exploratory source search.
Report both accurately. Prefer fewer relevant reads to a full-wiki ceremonial pass.
Generate numeric summaries from report fields or check them against saved reports;
handwritten maximums and counts can drift even when code locations remain valid.


## Can a feature entrance reveal its important variants?

Start from the user's words and one real feature entrance, without supplying the
hidden file/symbol or the expected variants. Before code search, write what a
worker can infer about the path, data ownership, fields, partial success and scope.
Then verify against the actual writer and consumer. Familiar self-review is useful
but is not an independent developer trial.

For each relevant feature, ask whether its own page reveals distinctions that
change a plan: resource owner versus viewer, producer versus consumer, role versus
account partition, deployment environment versus rollout audience, and Web versus
mobile implementation. Do not demand every axis for every feature or turn the
list into a permission checklist. Link to the existing authority and put a compact
comparison where the user enters; definitions buried in another chapter are not
sufficient discoverability.

Trace user-visible fields individually. “Share to blog” may mean automatic abstract
crossposting, independent link citation, or opening a prefilled text-and-image
composer. Existing pieces do not prove the combined entry exists. Show which
fields are copied, entered, uploaded, omitted and actually rendered, and distinguish
primary success, secondary write success and backlink persistence. A fallback or
rollback rule for a linked derivative does not apply to every independent citation.

Evaluate the entry-to-explanation path, not only search ranking. A reader starting
at a public calendar should discover whose calendar it is, who can view it, where
each role edits its own time, and how test partitions and rollout gates combine.
A passing source-presence test or admin observation cannot prove another viewer's
access. Keep source checks, browser navigation, unit tests and real workflow
acceptance separate; document missing product capability instead of inventing it.
