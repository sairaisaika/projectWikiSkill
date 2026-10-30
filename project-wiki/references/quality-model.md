# Precision and effectiveness scorecard

## Report four dimensions separately

| Dimension | What is measured | What it cannot prove |
|---|---|---|
| Structural readiness | Paths, unique declarations, contracts/rules/impact/check fields, provenance, freshness | Semantic accuracy or implementation correctness |
| Routing evaluation | Known questions' top-1/top-2 IDs, resolved locations, unknown-query rejection, response size | A new agent will choose the wiki or edit correctly |
| Semantic review | Reviewer verifies relevant rule, caller and failure behavior against cited source/test | Installed or live operation without runtime evidence |
| Observed usability | Time, wiki-first use, search count, plan completeness from actual trials | Causal speedup without a controlled comparison |

No blended “wiki quality = 97%” across measured and unmeasured dimensions. Show each
numerator/denominator and mark missing observations **not measured**, never zero or pass.

## Structural rubric (100 per route)

| Category | Weight | Full-credit criteria |
|---|---:|---|
| Exact location | 20 | Resolved implementation; interface routes also resolve a declaration. Planned routes have justified plan-only status and no fake implementation. |
| Caller contract | 15 | Inputs, outputs, errors, compatibility, and returned/thrown/unsupported failure modes are concrete fields. |
| Source-backed rules | 15 | At least one stated rule with valid source references; planned rules are explicitly proposed. |
| Impact | 15 | Named downstream changes plus located caller/consumer (plan: intended impact). |
| Focused validation | 15 | Existing test references plus commands and evidence scope (plan: proposed checks, with honest missing test evidence). |
| Evidence boundary | 10 | Boundary, explicit unknowns, evidence status, reference-backed observations appropriate to that status. |
| Findability | 5 | Task aliases and a real local explanation/anchor. |
| Freshness | 5 | Review date, resolved locations (or plan status); generated snapshot checked separately. |

The helper splits categories into observable subcriteria (see audit output). A
well-filled but inaccurate sentence can still score; semantic review is a separate
gate. Hard location/path/schema failures override the score. Do not add filler or
invent a caller/test/evidence claim to earn points. Report a justified N/A with a
lower score or adapt the project rubric transparently.

Default structural floor **85/100 per route**, adjustable by `quality.min_structural_score`.
The report includes average and minimum; a high average never hides one failing route.
Generated timestamps do not reset reviewed_at. Dates are validated, not assumed current;
scheduled review cadence is a project choice, not automatically imposed.

Optional engineering profiles have a separate depth report: source-linked fields,
declared state/event-pair coverage and gaps, configured/target/measured limits, and
decision records. They do not inflate the 100-point baseline or penalize routes
where they are irrelevant. “Complete” pair enumeration is scoped to the declared
model; it is not proof that implementation, races or timing are complete. See
[engineering depth](engineering-depth.md) for the exact criteria and limits.

Six-view coverage is another separate metric: required vs documented diagram kinds,
missing views and explicit applicability waivers. Do not count a waiver as a drawn
view or six diagram files as evidence of six correct perspectives. Rendering and
cross-view semantic review remain separate; see [the diagram framework](diagram-framework.md).

## Pilot routing thresholds

Start with at least **10 representative change/debug questions**, including ambiguity
between interface layers and at least **2 unrouteable questions**. Expected IDs belong
in the evaluation task file, not in evaluator instructions or query aliases copied
verbatim solely to make a test pass. Reserve unseen paraphrases for independent trials.

Suggested pilot criteria, configurable per task file:

- Top-1 correct route >= 80%; top-2 >= 90%, with raw counts and routeable denominator.
- 100% selected source positions resolve; 100% unknown questions return no route.
- No selected stale/broken declaration; ambiguous needles never pick a random match.
- Query response <= 450 whitespace words by default; this is a portable size proxy,
  not a tokenizer count. CJK segmentation is not comparable to English word counts.
- No mandatory full-site read. For a human/agent trial, aim for entry + at most two
  focused sections **per distinct task surface** before a plan, and record actual
  pages/bytes consumed. A request covering four different surfaces may need four
  sections. Split compound queries; truncated top-two results are not total coverage.

`evaluate` reports ranking and structural location checks using curated expected IDs.
Optional task-map cases compare all expected surfaces/routes, separately from
top-1/top-2. A missing or unexpected work surface fails even when every individual
query ranks correctly. Located `edit_for` targets are reported separately and do
not inflate the baseline score. Neither metric proves semantic sufficiency; see
[change navigation](change-navigation.md).
It does not label those results independent or semantic. Alias-based routing has no
semantic model: a known synonym may fail until added; an absent match is preferable
to a made-up location. Record failures rather than relaxing thresholds to claim success.

### Relevant targets do not excuse irrelevant results

A target in the top results measures recall/ranking, not whether the other returned
pages are useful. Regular query cases in the helper's current `evaluate` do not
reject extra results merely because the expected route ranks correctly; task-map
scope checks are separate. For a native-selector repair, preserve the actual
consumer output and check both required routes and demonstrated unrelated routes.
Keep plausible but unreviewed results explicitly unclassified instead of treating
every extra result as an error. Use the project's existing tests or evaluation
record; this guidance adds no helper task-file fields.

Include a positive control where an otherwise irrelevant page is explicitly wanted,
along with the failing query and unseen paraphrases. Compare selected and omitted
results, ordering and output size separately. Replaying a declared keyword corpus
measures compatibility/self-recall, not semantic precision or a user's reading cost.

Task file:

```json
{
  "schema_version": 1,
  "thresholds": {"min_top1": 0.8, "min_top2": 0.9, "min_tasks": 10, "min_unknown": 2},
  "tasks": [
    {"id": "read-errors", "query": "How does the client preserve HTTP errors?", "expected_routes": ["public-api"]},
    {"id": "unknown", "query": "unmapped invoicing workflow", "expected_routes": []}
  ]
}
```

## Actual wiki-first trial

Record in a project-local evaluation report (only real observations):

| Field | Definition |
|---|---|
| familiarity | fresh evaluator / previously read source / unknown |
| start/end and elapsed | Observed time, excluding explicit interruptions; no invented baseline |
| entry_used | Whether AGENTS/README led to the wiki before exploratory source search |
| route_ids and source positions | Exact route and whether it was the correct edit surface |
| docs consumed | Actual entry/sections and bytes or words, measurement method included |
| read completeness | Local sections vs whole pages; truncated output remains unread |
| compound scope | Expected vs declared work surfaces/routes; missing or extra IDs |
| edit seams | Declared change concern, exact located helper and internal/public boundary |
| exploratory searches | Repo-wide/targeted searches before and after plan |
| plan coverage | 0–6: outcome, dependencies, interfaces, deliverables, exit evidence, unknowns |
| semantic findings | Wrong rule/caller, missing failure mode, invented implementation |
| outcome | usable plan / targeted verification needed / blocked by missing route |

“Wiki-only” means plan drafting used wiki facts; the helper itself reads curated
source files to update locations. Before editing code, inspect the cited implementation.
Do not market that necessary inspection as a failure of the wiki.

A self-test can establish structural/routing behavior. Only a fresh observed trial
can support a claim about independent navigation. Time savings require a comparable
baseline; otherwise report elapsed time alone. Favor fixing concrete failed routes
over multiplying universal rules.
