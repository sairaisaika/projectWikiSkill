# Compound changes and actual edit locations

## Make the first wiki read useful

An instruction to read a wiki is not a usable task entrance. Starting from the
user's words, the native entry should return the functional page, its local
sections/diagrams, ownership and variant constraints, recorded producers and
consumers, gaps, and the next verification seam. Once planned files are known,
return **every registered satellite per file**, with the relation that brought it
into scope. Recheck the actual working delta during development; a post-commit
touch gate cannot substitute for this planning aid. Keep the ordinary first read
short and make the deeper records directly reachable.

An actor dictionary link alone may leave the task response ambiguous. When the
feature has an authored behavior-scope section, project its actual resource,
operator/owner/viewer relationship, relevant axes and unverified limits into the
first task card and machine output. Reuse the native prose/table; do not infer
permissions from role labels or create a second actor registry. A missing scope
must remain visible. Test that a real feature scope, including its limits, survives
the projection and that headings inside fenced examples do not become declarations.

For an established wiki, derive this view from native metadata and prose rather
than maintaining a second task manifest. Distinguish functional relations,
explicit source dependencies, ordinary prose links and shared-file similarity.
Do not recursively expand all common infrastructure and call that a causal impact
graph. State when candidates are truncated; never silently truncate a file's
registered satellite inventory or treat an absent inventory as no consumers.

Test real task phrasing as well as canonical keywords. Domain nouns and action
terms are useful anchors alongside long exact phrases and identifiers. Unknown
queries must expose missing navigation, not produce a plausible guess. Save the
first failed query before repairing metadata; adding the same query to regression
is a self-test, not an independent usability trial. Include compound tasks,
negative controls, a high-fan-out change and variants the user did not explicitly
name. A tool call proves neither reading nor semantic coverage.

Use this when a request spans multiple interfaces or a route stops at a large
factory. Keep ordinary one-surface queries simple.

## Route by rule, not only by file

When the only machine-readable edge is file → page, a shared file with high
fan-out (a config registry, a scheduling data layer, a notification dispatcher)
turns every commit that touches it into a 20–50 page acknowledgement list. The
observed signature: workers stamp pages they did not read; the gate accepts the
stamp; the parser discards the reason written beside each page; rules exist only
as prose restated in several places with no identity or anchor; the typed edges
that do exist describe data flow (producer → consumer) but not rule flow
(rule → enforcer → consumer → check); task routing selects an entry by keyword and
lists impact by file. This is a granularity and gate-keying failure of the wiki,
not a discipline failure of the worker. More reminders or a stricter stamp format
make stamping cheaper, not reading. A wiki should behave like a chip — layered,
with typed cross-links that can be followed in both directions — not like a
check-in point.

### Four node kinds, four forward edges

| Node | What it is | Identity |
|---|---|---|
| invariant | One falsifiable statement, numbers with their basis, no adjectives | Site-unique ASCII ID with a fixed prefix |
| mechanism | The code that enforces it, usually the registered single write path | `path » symbol` |
| consumer | A page, or an endpoint/relation ID on another page, whose behavior depends on the rule | Page ID or native endpoint ID |
| gate | The test, ratchet or check script that verifies it | `path » symbol` |

Forward edges are authored once, on the one page that declares the invariant:
**declared-in** (the rule's authority: a file header, decision record or link),
**enforced-by** (mechanisms), **consumed-by** (consumers) and **verified-by** (gates).
Reverse edges — symbol → invariants it enforces, test → invariants it verifies,
file → invariants it participates in — are generated projections, never written by
hand. The authored form is one fixed-column table on the declaring page; a
consuming page points back by ID in a short table and does not restate the rule.
The generator projects a site-wide invariant → mechanism / consumer / gate section
plus both reverse tables beside the existing producer/consumer projection, using
the same parser and the same generated-block discipline.

Each row carries a status: verified against source, gap, or unverified. A gap or
unverified row must cite the project's debt or decision ledger; a verified row must
have a gate. Verified means the mechanism and gate symbols resolve, not that the
rule is obeyed — the gate command still has to run. A ratchet on the invariant
count (it only rises) makes migration progressive: a file no invariant covers keeps
the old file-keyed rule, so coverage is never relaxed while rows are added. A
gap row records the current write path and says it does not enforce the rule; it
does not invent a mechanism.

### Routing follows the edges

Task entry: entry page → the invariants declared on it → each one's chip path
(mechanism, with the page that explains it → consumer pages → gate command,
displayed and not executed) → only then the prose sections. For a reverse lookup
from planned files, a file that is a mechanism or gate of an invariant puts that
whole path first; the file's registered satellites are kept but become a hint
("N more pages reached through this shared file"). The full inventory above
remains visible; what changes is the order and what is required.

### Gate: two-layer criterion

Concept layer, required: for each changed file that is a mechanism or gate of an
invariant, the required set is the declaring page plus its consumer pages in both
directions (listed on the declaring row, or pointing back by ID). One rule-ID
token with its reason acknowledges the whole path; tokens may mix with page IDs,
and the parser keeps the reason instead of discarding it. File layer, hint: the
remaining file → page satellites are printed grouped by invariant, not required.
Files no invariant covers keep the old criterion. A hit is by file path, not by
whether the diff touched the symbol: an unrelated line in the same file still
raises the path. Prefer one extra chip path to a missed one, and record the cost.

### Mapping onto the route contract

In the [route contract](route-contract.md), `rules[{id, statement, source_ids,
tests}]` already carries these edges: `statement` is the invariant, `source_ids`
with role implementation are enforced-by, role consumer are consumed-by, `tests`
and `checks` are verified-by, and the route's `docs` anchor is declared-in.
Schema 2 lacks a site-unique rule ID (rule IDs are unique within a route), a
per-rule status with ledger citation, and the reverse projections. Record those
in the native pages until the schema gains them; do not fork a second manifest.

### When to introduce invariant tables

The first time one commit's acknowledgement list exceeds roughly ten pages, or
the reverse source index shows one shared file registered on more than roughly
ten pages. Start with rules already restated on several pages without an anchor
and with the highest-fan-out shared files. Do not convert every hard-boundary row
into an invariant; each row needs one falsifiable rule, a real mechanism and a
real consumer. Measure required pages per commit before and after on the same
synthetic single-file commits; see the
[quality model](quality-model.md#required-pages-per-commit).

## Rank the requested work, not keyword density

When native lookup repeatedly returns a narrow leaf for a whole workflow, inspect
ranking as well as missing metadata. Many aliases for one noun must not overwhelm
a page covering several distinct requested capabilities. Preserve exact route-ID
selection, unknown-query disclosure, and seeds for every recognized surface in a
compound request; improve the native selector rather than creating a parallel index.

Save the original failure, test a dense single-topic negative against a sparse
multi-topic route, and retain generic-entry and unrelated compound regressions.
Verify the actual CLI or UI surface that uses the selector. Fixing CLI ranking
does not prove browser search changed; a known-source regression is not a blind
trial or a measured efficiency improvement.

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
