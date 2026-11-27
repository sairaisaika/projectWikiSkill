# Engineering depth: constraints that can be checked

> Reviewed: 2026-11-27 for sender-asserted identity fields and multi-writer ordering (2dec093 base); 2026-11-20 against 6639e41 for the diagnostic workflow; other profiles retain their prior scope.

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

## Debug from evidence to a technical contract

Use this at a touched production-facing boundary when a small diagnostic agreement
helps locate a failure. Contracts here mean schema/API/events/CLI, client-server
behavior or invariants, not legal or commercial agreements. This skill owns the
navigation and evidence discipline, not a logging platform or a new enforcement
hook. A pure offline function or a project with adequate native diagnostics may
link existing checks and explain why no logging contract is needed. Do not require
a retrofit, universal event schema or a new general-purpose LOG.md/Wiki ledger.

| Record | Keep its native authority |
|---|---|
| Change, decision, handoff receipt | Version history, ADR, task/incident record; return durable rules to their existing owner rather than accumulating another session diary. |
| Runtime diagnostic event | Project logger/metrics and approved query/runbook; describes an observation at a boundary or meaningful transition, not every source line. |
| Audit trail | The project's separately governed audit source, authorized reader and retention; a diagnostic line is not proof of a committed action or a complete audit record. |

Follow the existing Maintenance and contract-owner entries:

1. **Locate the claim.** From the symptom, name the component and stable operation,
   its known source producer and consumers, and the exact contract/schema/API
   version or source revision. Separate claimed behavior from observed behavior;
   unknown ownership/version stays unresolved rather than guessed from a message.
2. **Select safe evidence.** At the owning boundary, use the project's small logging
   contract only for fields needed to diagnose: stable event/operation, observed
   outcome and error code; timestamp, service/build/environment; one safe opaque
   correlation ID when crossing components; categorical failure cause and known
   retryability versus unknown; and allowlisted safe context. Do not derive IDs
   from customers or payloads. Record only meaningful transitions; avoid duplicate
   spam. A stable code identifies a known failure category, not necessarily its
   underlying cause or permission to retry.
3. **Check the evidence path.** Where relevant, link producer → configured sink/query
   entry → authorized reader/runbook, plus coverage, retention and sampling/drop
   limits, in that same owner. Configuration is not observed delivery. Preserve
   actual observed states: accepted/queued is not succeeded. Missing, filtered,
   sampled or dropped logs mean unknown, not proof the operation never happened.
   Check whether one operation can be joined without conflating attempts or users;
   do not fill missing terminal events with an inferred success or failure.
4. **Compare and return.** Put the exact contract/version, sanitized observation,
   producer/consumer locations, test owner, current finding and unresolved/next
   check together on the existing task/incident receipt, linking the owning page.
   Distinguish consistent success, known error, contract mismatch and insufficient
   evidence. Logs are evidence, not the specification. Reproduce with a focused
   positive and negative check at the contract boundary; keep missing runtime
   evidence explicit. A synthetic replay, passing gate or source fix is not
   deployment or observed production behavior.

For a contract edit, follow producer → contract/invariants and failure semantics →
consumers → version/compatibility/rollout → positive and negative checks. Reuse the
native typed schema, implementation and tests as authority; update the contract's
link to diagnostic events/sink only where applicable, including renamed codes or
changed outcome semantics. Do not silently reinterpret old events as a new version.

Apply [destination/ref and audience review](repository-hygiene.md#visibility-and-publication-scope)
and [retention protections](maintenance.md#inventory-storage-without-cleaning-it).
Credentials, client payloads, raw logs and sensitive identifiers stay outside the
Wiki/repository, including private repositories, in an approved protected store.
Use allowlisting/redaction before excerpts or assertions; failures must not echo
sensitive values. Safe pointers must not reveal private paths or identities.
Synthetic public samples may be committed when clearly labeled; they are not raw
production evidence. Do not start new production collection to satisfy this guide.
Keep synthetic examples, executable checks and actual project behavior as three
separate claims; if access or runtime evidence is absent, name the next authorized
check rather than fabricating a result.

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

#### Who asserts an identity or role field

For every field a consumer uses to decide who may do something (actor, role,
owner, sender), record in its `constraints` whether the value is asserted by the
sender inside the payload or attested by the transport or server (a session, a
signed token, the connection's identity), and name the check that reads it.

A sentence such as "this field is not authorization" records an intent. A boundary
needs a named enforcement point and the asset that point protects. Then follow the
unprotected path: if a consumer that trusts the payload value can still write the
protected asset (for example it persists whatever state the accepted messages
produced), the boundary named elsewhere does not protect it. Record that as a gap
with the project's tracking destination; do not leave the disclaimer standing as
if it were the control.

Ask the same question of lifecycle and control messages (open, close, replace
state, grant) as of data messages. They are usually fewer, rarely fuzzed, and can
overwrite everything the data messages built.

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

For state that several actors write at the same time, an `ordering` entry states
whether the result depends on the order in which different senders' operations
arrive. "The parties take turns" is a valid design only when it is written down
together with what each party sees when two act at once. A claim of order
independence needs a test that replays interleavings with each sender's own order
kept, and a control showing that test fails when the rule is removed.

A limit can also refuse an authorized actor: a cap of N admits the next one
nowhere. When its unit is people, sessions or seats, treat it as part of the
access path described in
[feature completeness](feature-completeness.md#reachability-is-a-chain-of-gates).

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

For recovery flows, examine SDK initialization before the page-level guard: an
initializer may consume a URL or clear stored sessions before the intended identity
check runs. Test the existing different-identity case as well as an empty browser,
then refresh the recovered page with a new account that has not completed business
onboarding or consent. Do not auto-complete those prerequisites to hide an identity
recovery dead end. Distinguish a usable recovery form from a completed password
change and a headless Web result from a system-browser handoff on an actual device.

Pin the provider's actual wire semantics, including signed claims and error wrapping,
before strengthening a predicate. A stricter negative test can reject a legitimate
provider response; require a known-good end-to-end positive at that boundary. A
verified generic OTP claim is not automatically proof of a specific recovery purpose
or a current email channel. Record that distinction rather than renaming the claim.

For an intermittent save, distinguish no accepted input, no emitted request, a
failed or unfinished transport/body, a test's unmatched-response wait, and a saved
value later overwritten by a reader. Capture the action's enabled/owner readiness,
change event, request, response/failure and persisted/rendered result using bounded,
non-secret traces. An old response-wait timeout without that timeline cannot be
retroactively assigned to a later reproduced race. Keep both receipts and state
what the counterexample actually proves. Bound a real request and its response
body; define visible failure, retained latest intent, explicit retry and disposal.
Client abort or timeout does not prove the server rolled back or never committed.

For dense responsive interfaces, review text size together with available column
width, row height, clipping and navigation. Do not compress a wide time grid until
labels become unreadable, or call a no-overflow assertion a usability acceptance.
If using a local scroll viewport, verify pinned context, keyboard/touch access,
pointer geometry after scrolling and absence of accidental business writes. Keep
configured minimum dimensions separate from measured rendered values and label
which roles, languages, fonts, device/browser modes and legacy variants were tested.
