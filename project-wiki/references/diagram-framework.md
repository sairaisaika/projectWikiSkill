# Six complementary views of one project

Use these six views as a project-level reasoning framework. The stages/complexities
below are typical guidance, not a schedule that blocks useful work. Cover the six
questions across the wiki; select local views by task rather than requiring every
small feature or patch to repeat all six.

| View / manifest kind | Focus | Typical stage | Typical complexity | Minimum engineering question |
|---|---|---|---|---|
| 架构图 / architecture | System structure | Design | Medium–high | Which components own which responsibilities and depend on which interfaces? |
| 流程图 / flow | Business flow | Requirements/design | Low–medium | Which branch, failure or recovery action happens next? |
| 时序图 / sequence | Interaction order | Detailed design | Medium | In which order do real participants call, return, fail or callback? |
| 数据模型图 / data-model | Data structure | Design | Medium | Which records/fields/relations carry the facts, with which constraints? |
| 部署图 / deployment | Runtime environment | Before deployment, or current runtime review | Medium | What runs in each process/environment and where do connections cross boundaries? |
| 状态图 / state-machine | State transitions | Stateful/complex behavior | Medium | Which events and guards permit, reject or leave a transition unknown? |

## Architecture

Locate responsibilities, module/service boundaries, dependency direction and public
ports. Distinguish in-process libraries from separate processes. Link real declarations,
implementations and consumers; identify optional/unimplemented dependencies. A folder
tree without interface direction is not an architecture explanation.

## Flow

Show trigger, actor, decisions, successful and failed outcomes, recovery and exit.
Label branch conditions and side effects; distinguish retrying from committed
success. Avoid implying that any exception is caught just because the diagram has
an error arrow. Useful for deciding where a business rule or validation belongs.

## Sequence

Bind lifelines/messages to actual callable boundaries, not guessed services. Show
request/response, async completion/callback, timeout/cancellation, alt/loop and ordering
where relevant; otherwise explicitly label the limited scenario. Capture which side
owns an attempt, transaction or reference. A sequence is not a deployment map.

## Data model

Show entities/value records, IDs and relations/cardinalities where they exist. Give
field types, units, nullability, constraints and authoritative type/schema links.
Declare conceptual vs persisted vs serialized records. A class diagram is acceptable
for a wire value record; it does not imply an ORM class, database table or native ABI.
Use ER relations only when backed by real storage/contract facts. Use the optional
data-contract profile for checkable field and byte geometry.

## Deployment

Show hosts/environments, processes, containers or device boundaries, runtime versions
where verified, protocols/ports and resource placement where relevant. Do not draw
every source module as a microservice. A proposed production layout stays proposed;
an offline test process can be the current deployment view for a library fixture.
Diagramming an environment does not prove it is installed, reachable or live-verified.

## State machine

Name states, events, guards, actions and terminal/rejected/unknown outcomes. Include
retry bounds and late responses when implemented. Put context such as attempt,
generation or response identity beside the graph: a state/event projection may hide
critical guard domains. Link the transition table and code. Use the lifecycle profile
for enumeration checks; do not claim formal completeness from a closed-looking graph.

## Structure and cross-view review

Each diagram record has kind, local path/anchor, question, scope and preferably
source_ids. Use one stable feature/route ID across views. A project-level record may
link architecture/deployment while feature routes link local flow/state/sequence/data.
Names and arrows must agree across these views:

- Architecture dependency ↔ sequence participant and actual call.
- Flow branch ↔ state event/guard and returned/thrown error behavior.
- Data record ↔ interface payload/serializer, not a fictitious persistence layer.
- Deployment process boundary ↔ actual IO/IPC; in-process calls stay in-process.
- State outcome ↔ visible completion/commit rule and recovery acceptance.

The helper validates source/doc references and declared type coverage. It does not
parse Mermaid, infer semantic edges or prove cross-view consistency. Render available
diagrams and inspect labels/clipping; review semantics against cited code separately.
Split crowded diagrams by scenario instead of shrinking them into unreadable images.
Use [page anatomy](page-anatomy.md) for local diagram versus section source blocks,
message-level traceability, polling/cursor contracts and manual review counts.

## Project-level coverage policy

The optional root policy makes the selected project's coverage executable:

```json
{
  "diagram_policy": {
    "scope": "Project-level engineering views; not six diagrams per route",
    "required_kinds": ["architecture", "flow", "sequence", "data-model", "deployment", "state-machine"],
    "not_applicable": []
  }
}
```

`audit` reports documented kinds, per-kind counts, missing kinds and explicit
not_applicable reasons separately. `check` fails for missing required views. A waiver
is `{ "kind": "deployment", "reason": "Concrete task-scoped rationale" }`; it is
reported as not applicable, never as a rendered diagram. Do not waive a hard question
merely to get a green check. Existing wikis without a policy stay compatible.

The fixture demonstrates all six with a shared vocabulary. They describe synthetic
offline code; its deployment view does not claim a production system exists.


## Author at project, section and page scope

Diagrams are required engineering content when a boundary, interaction, branch,
state or data relationship needs explaining, not optional decoration. Make the
question-to-view decision when creating the Wiki or opening a new scope, before
writing a large prose page. Record question → one of the six kinds → canonical
page anchor → relevant source anchors. Do not infer implementation from the drawing.

| New scope | Authoring acceptance |
|---|---|
| Project Wiki entry | A system-boundary architecture diagram identifies actors, system ownership and external dependencies. Review all six project questions: provide a canonical view, link an existing view, or justify why that question is inapplicable. Missing evidence stays pending, not implicitly waived. |
| Section introducing a domain, subsystem or cross-role flow | A scope diagram shows its entrance, responsibility boundary, upstream and downstream relationships. Choose architecture, flow or sequence by the actual question; add other views when they answer distinct questions. |
| Feature page | Select local views for the decision: branches → flow; calls/order → sequence; events/guards → state-machine; fields/relations → data-model; runtime placement → deployment; responsibilities → architecture. Explain why a view is unnecessary when no such question exists. |
| Pure index, FAQ, glossary or historical log | Link the owning canonical views rather than copying them. A short exemption reason is sufficient when the page introduces no new behavior or boundary; the label FAQ alone does not exempt a new domain design. |

A section diagram may live on another canonical page. Link that anchor from the
section and register the same existing diagram reference, rather than maintaining
another rendering. Reuse project vocabulary and stable source IDs. Beside each
figure state the question, a short conclusion, scenario limits, source links and
whether it is proposed, implemented or observed. Keep local figure provenance
separate from the provenance of the whole chapter; see [page anatomy](page-anatomy.md).
A planned drawing is useful, but is not proof of installation or runtime acceptance.

Trend, bar and other quantitative charts answer measurement questions outside
these six engineering kinds. Use them when data warrants it, name units, source,
period and uncertainty, and keep their data verification separate. Do not invent
a seventh engineering kind or force a chart onto a relationship question.

## Optional mechanical authoring declaration

For schema-2 helper adopters, put the decision on the existing route, not in a
second manifest. Existing diagrams and their path/question/scope/source_ids stay
the only diagram inventory:

```json
"diagram_requirement": {
  "level": "section",
  "required": true,
  "reason": "New scheduling domain: explain entrance, ownership and downstream effects"
}
```

`audit` and `check` reject a declared required scope with no diagram references,
invalid references or broken source IDs. For opted-in required scopes, each selected
section must contain a closed nonempty Mermaid fence. A canonical link on another
page counts; a drawing elsewhere on that page does not satisfy an empty section.
For a pure FAQ use `required: false` with a concrete reason and `level: page`.
The declaration does not judge that reason or classify Markdown automatically.
Presence parsing supports ATX heading sections (including their subsections), duplicate
heading slugs and standalone `<a id="name"></a>` immediately before a heading,
with optional blank lines. A whole-page reference checks that page. This is bounded
to 1 MiB per page, does not parse Mermaid syntax, and does not accept image/assets,
Setext headings or arbitrary HTML anchors as mechanically checked diagrams. Those
formats need native/manual review rather than opting into this Mermaid check.
It does not discover unregistered pages or require a new manifest in native projects. Keep their parser and review records.
The root `diagram_policy` remains the six-view coverage mechanism. Required
presence is not semantic completeness, and a green structural check is not approval.

## Change review and finish

From the actual reviewed diff, pass selected repository-relative changed paths to
existing audit; the helper neither invokes Git nor reads changed source contents
for these suggestions. Include both old and new names of renamed files. Deleted
paths can still locate declared relationships. For example:

```sh
python <skill>/scripts/wiki.py audit --root <project> --changed-file src/service.py --changed-file docs/wiki/project-views.md --diagram-limit 20
```

The `diagram_review` field follows `diagram.source_ids` through the route's sources
and matches diagram page paths. Missing source IDs use an explicitly labelled
conservative route fallback; routes with no diagrams request an authoring decision.
Unmapped paths are counted, not declared safe. Malformed route shapes are skipped
with `unavailable_route_count`; the normal audit retains their errors, not a clean
review claim. Results are deterministic, bounded
to 50 candidates and 10,000 candidate JSON bytes per page. Repeat the identical
file list with `--diagram-offset NEXT_OFFSET` until `next_offset` is null. The rest
of audit retains its existing full structural report; this is not a new whole-report
byte limit. Inputs are limited to 256 paths of at most 1,024 characters; partition
larger diffs deliberately and record that review coverage, never silently drop files.

Both a business-rule change and a copy-only edit in the same source file may flag
the same drawing. A path match suggests review, not a required redraw. Inspect the
actual source hunk and existing drawing before choosing a disposition in the native
task return, bound to the reviewed base/head and any working-tree changes:

- **updated**: link the corrected canonical anchor, changed relationship and checks.
- **reviewed unchanged**: link the anchor and explain why the source/text change
  leaves its depicted contracts unchanged, for example only message wording changed.
- **pending**: name missing information, unavailable render check or unresolved design.

All suggestions start pending; a previous task's completion is not carried forward.
The helper does not save or enforce these prose dispositions, rewrite diagrams,
mark a task finished or override the existing workflow.py finish protocol. There is
no section/page generator here: create and finish are authoring/review steps, not
new commands. Return these outcomes with the existing task's checks and evidence.

Run existing reference/structural checks, then the project's usable renderer and
inspect clipping/labels when available. A renderer failure can block that project's
configured render check; this helper does not install or invoke a renderer. An absent
renderer is explicitly unverified, not passed. Compare the picture with source and
prose separately; never turn an inferred semantic disagreement into an automatic
write or generic blocking gate.
