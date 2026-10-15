# Engineering depth: constraints that can be checked

Use this reference when a route involves lifecycle, wire/data contracts, scheduling,
resources or choices whose rationale is easy to lose. The user's reference material
motivates these profiles; its praise and claims of mathematical completeness are
not technical evidence. Do not copy domain-specific numbers into a new system.

## Choose detail by the engineering question

| Question | Profile / view | Record | Avoid |
|---|---|---|---|
| What is serialized or persisted? | data_contract; field table/data model | Type, unit, nullability, constraints, authoritative schema and version; ABI offset/order only if relevant | Invented physical layout for ordinary JSON |
| What happens after timeout, invalid input or late response? | lifecycle; state machine + transition table | States, events, guards, actions, rejection, unknowns, retry/terminal behavior | A happy-path arrow diagram called a complete FSM |
| Who calls whom and in what order? | Sequence diagram + execution.ordering | Participants mapped to real interfaces; request, callback, failure, cancellation and ordering | Long lifelines with no checked interface or failure semantics |
| Who owns data and what bounds execution? | execution | Ownership/lifetime/release, concurrency boundary, units and limit classification | A target latency reported as a benchmark |
| Why this threshold, order or layout? | decisions; lightweight ADR | Context, selected option, alternatives, consequences, revisit trigger, source binding | Deleting Why for density or freezing a proposal as current |

Three layers keep a dense wiki usable: task entry → local contract/diagram → deep
tables and rationale. Reuse the authoritative type/IDL/serializer, generate tables
where practical, and test actual bytes/transitions independently. A diagram is a
projection of that model; identify what it omits. The helper validates declared
references and model consistency, not Mermaid rendering, code equivalence or timing.

## Optional schema-2 engineering block

An existing route remains valid without this block. Add `engineering` with `scope`,
`status` (current/proposed/partial), and one or more of `data_contract`, `lifecycle`,
`execution`, `decisions`. Current/partial claims cite route `source_ids`; proposed
claims remain visibly proposed. Unknown profile names fail instead of being ignored.
Deep metrics are reported separately, never added to the base 100-point score.

### Data / binary contract

`data_contract.authority` has `kind` (typed-source/idl/schema/manual), local `path`,
and `source_ids`. `fields` contain unique `name`, `type`, `unit`, boolean `nullable`,
nonempty `constraints` and `source_ids`. State dimensionless explicitly when relevant.

Optional `layout` has positive integer `size_bytes` and `byte_order` (big/little).
When present, every field also declares nonnegative `offset_bytes` and positive
`size_bytes`. The helper rejects overlap and out-of-bounds spans. This simple geometry
model does not support unions or shared bitfields: use a specialized authoritative
schema/compiler and report that limitation rather than force-fit it. Do not infer C
padding, actual ABI, endian behavior or mask correctness from geometry alone.

Binding to the serializer and running a known byte-vector round trip provides
stronger evidence than a matching filename. That validation must actually run and
have a recorded scope; `authority.kind` alone does not prove generated conformance.

### Lifecycle and recovery

`lifecycle` declares unique `states`, unique `events`, `initial`, explicit `terminal`,
`coverage_claim` (partial/complete), and three arrays:

- `transitions`: unique id, from, event, guard, to, action, source_ids, optional tests.
- `rejected`: from, event, reason, source_ids, optional tests. Specify whether ignored,
  refused or error; a rejected transition does not imply an exception.
- `unknown`: from, event, reason. These are identified gaps, not default fallbacks.

Every (state,event) pair is classified at most once across these arrays. Multiple
guarded transitions for one pair are allowed when guard strings are distinct, but
their exhaustiveness/disjointness is **not** automatically proved. `complete` requires
all declared pairs to be transitions or rejected, with no unknown/unclassified pairs.
That is enumeration coverage over the declared model, not mathematical completeness:
the code may have additional states, races, exceptions, retries or invalid inputs.

Report specified pairs / total pairs, unknown/unclassified counts, transition count
and states unreachable in the declared graph. A transition table without guards or
with unknown target states fails validation. Terminal behavior and late callbacks
need explicit entries; include a deadline/cancel/retry path when present in real code.
Test bounds and recovery using the actual implementation, not a test generated only
from the same transition table. Symbol existence is not model/code equivalence.

Optional `parameters` records have unique name, domain, validation_scope and source_ids.
Use these for counters, generations, identities or similar context that changes a
guard. Record whether inputs are checked globally or only in one branch; terminal
events may deliberately ignore context. State/event pair counts exclude parameter
combinations and invalid-input categories. Late replies during backoff and after a
retry resumes need separate discussion; if request/generation correlation is absent,
say so. A caller-owned attempt limit does not prove a cumulative retry bound if the
caller can keep passing zero. Record that conditional guarantee and the missing owner.

### Execution limits, ownership and order

At least one of the following arrays is nonempty:

- `ownership`: resource, owner, lifetime, release, source_ids. Include alias/copy,
  shared access and reclamation rules in descriptions when they matter.
- `ordering`: before, after, reason, source_ids. Use real operations, not invented
  runtime services; mark a diagram that omits internal operations as a projection.
- `limits`: id, finite numeric value, nonempty unit, kind (configured/target/measured),
  scope, source_ids. Measured values also require method and existing evidence_refs.

Configured values describe code/settings, targets describe desired behavior, and
measured values need an actual workload/environment/revision/method receipt. A file
that exists does not prove it contains the measurement. The helper only verifies
reference presence. No inferred global budget from a per-instance counter; no
performance claim from a constant, synthetic benchmark or diagram annotation.

### Decisions / lightweight ADR

Each record has id, path, status (proposed/accepted/superseded), context, decision,
nonempty alternatives/consequences, revisit_when and source_ids. The local document
preserves Why beside the contract. Accepted means a documented project choice,
not an experiment proving it optimal. Revise or supersede after code/hardware changes;
do not increase determinism by silently turning an unsettled choice into a guarantee.

## Sequence diagram review

For every diagram, retain `question`, `scope`, the local path/anchor, and optional
`source_ids` referring to the route. Check that its participants, messages and branch
labels match the named calls/ports; include failure/timeout or state clearly that it
shows only the happy path. Add data ownership and ordering only where they clarify
correctness. A diagram that is too large to read should be split by scenario and
linked to a table, not simply shrunk.

Do not claim rendering from Markdown existence. Parse/render with an available
Mermaid renderer, and inspect readability separately. Neither is behavioral proof.

## Quantitative depth review and maintenance

Keep numerators/denominators: field provenance, specified state-event pairs, unknowns,
source-linked transitions, limit types/evidence references and decision records.
No entropy estimate, arbitrary “industrial-grade” label or inference of developer
seniority belongs in the score. Manual review still checks whether modeled events
cover the real code and whether each rule actually matches its cited implementation.

Change propagation: type/IDL/serializer → field table/tests; event/guard/callback →
transition table + state/sequence views; timeout/buffer/capacity → configured vs
measured limits + test receipt; rationale change → ADR + compatibility/migration.
Rebuild indexes after reviewing these affected slices, not by refreshing dates to
silence CI. Retain simple routes for tasks that do not need deep profiles.

Runnable examples in the repository fixture are `recovery` (bounded pure action
selection) and `wire-format` (8-byte serializer). Their diagrams, byte vectors and
recovery tests are synthetic demonstrations, not a specification of any user's device.
