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
