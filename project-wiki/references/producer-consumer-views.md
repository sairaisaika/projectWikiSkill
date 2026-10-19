# Producer and consumer views

Apply when documenting a functional partition, feature, subfeature or cross-domain
bridge. Goal: an agent can trace who creates what, who persists/transforms it, and
all known direct/indirect readers, displays and effects, then find the edit seams.

## Representation decision

Use a hybrid, progressively disclosed view: a short responsibility overview → typed
relation ledger plus its local rendered graph → exact source and failure detail.
Keep Mermaid text accessible to text-only agents. Render it for visual readers;
Mermaid source alone is not image verification. No evidence establishes one
universally fastest notation, or that Mermaid outperforms Graphviz for agents.

Research checked 2026-10-15; distinguish evidence from the proposed method:

- [SeeRepo, 2026, paper v1](https://arxiv.org/html/2606.14061v1): repository issue
  resolution experiments support supplementary structural images with text; image-only
  access degraded results. Effects vary by model and layout, and include accuracy
  tradeoffs. This is evidence for trying hybrid local views, not a wiki benchmark,
  complete runtime dataflow extraction, or a promised saving on this project.
- [Talk like a Graph, ICLR 2024](https://research.google/pubs/talk-like-a-graph-encoding-graphs-for-large-language-models/):
  graph encoding affects reasoning and depends on task/structure. Explicit typed text
  relations are a candidate, not a proven universal optimum for current coding agents.
- [C4 notation](https://c4model.com/diagrams/notation): explicit responsibilities,
  directional labelled relations and a legend inform readable engineering diagrams.
  This is notation guidance, not measured agent performance.
- [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents):
  compact references and just-in-time retrieval inform progressive disclosure;
  vendor guidance is not an independent comparison of wiki formats.

The ledger and generated projection below are our engineering hypothesis. Evaluate
them locally; do not copy these sources' percentages into project claims.

## Shared identity, one editable representation

Use native wiki tables/schema when available. Do not introduce a parallel manifest
or duplicate business types. Assign stable IDs within each functional scope:

- **Endpoint ledger:** ID, type (producer/interface/store/consumer/gap), short name,
  responsibility and actor/environment/client conditions, exact evidence locator.
- **Relation ledger:** ID, source ID, target ID, relation type, data/event, conditions
  and failure/delivery semantics, source-reviewed/gap/unverified status, evidence.
- **Local graph:** the same endpoint IDs and relation IDs, direction, meaningful data
  labels and types. Show unimplemented/unverified relations distinctly with a legend.
  Shared-rule edges, calls, events and navigation are different relationships.

Prefer generating the graph from the ledger with the project's own model. Otherwise
check set equality of endpoint IDs and typed relations, including gap edges. IDs do
not substitute for readable names. Graph metadata links to table/source detail;
expand a local subgraph rather than drawing an unreadable site-wide graph. Each
partition overview must index its child functional scopes, cross-partition bridges
and their ledgers; split large scopes without hiding endpoints from the inventory.
Inspect the rendered diagram at the intended reading width, not just its SVG node
count. Wide fan-in/fan-out can shrink every label into unreadable text; choose a
suitable direction, scrollable readable export or smaller linked scopes. If layout
is generated, make the choice explicit and validate allowed values while preserving
node/edge identities. Layout choice is a readability decision, not a claimed agent
speed improvement.

A sequence diagram supplements ordering/partial-commit detail; it does not replace
an exhaustive relationship inventory.

## Source discovery and completeness

1. Declare the functional result, boundary, reviewed revision/repositories, parent and
   child scopes. Define what "all" covers. APIs/types alone are not the inventory.
2. Walk producers → reachable writers → store/transport → readers → visible/effect
   consumers. Also reverse-search each output field, table/topic and shared rule.
   Search actual calls/imports/routes/registries and dynamic hooks; inspect call sites,
   not just symbol presence. Record commands and exclusions for reproduction.
3. Consider relevant web owner/viewer roles, anonymous users, test partition versus
   deployment, rollout, mobile, cron, webhook, notification, export, MCP and external
   clients. These are discovery prompts, not a requirement to invent each one.
   A direct API consumer and a rendered UI consumer may be distinct endpoints.
4. For missing capability draw the missing end/edge and link debt. For unverified
   consumers show uncertainty and a ledger item; for inapplicable categories state
   why. Never mark an unexamined client absent. Put other-domain details behind a
   bridge with an exact link; external boundary endpoints remain visible locally.
5. For shared state, distinguish **snapshot producers**, **invalidation/refresh
   triggers** and **local cache writers**. An event asking for a refresh does not
   produce the refreshed value; a successful local patch does not prove persistence.
   Inspect optimistic-before-request versus patch-after-success ordering. A GET or
   polling endpoint can write heartbeats, streaks or receipts: inspect its complete
   call path before treating it as a read-only runtime probe.
6. Scope failure claims to the layer: source fallback, HTTP failure, cached stale
   data and caller-level rejection handling are different. A contract comment saying
   "IDs only" or "no sensitive text" needs actual projection/allowlist verification;
   excluding top-level fields does not establish that nested metadata is filtered.
7. At producer/consumer handoffs, compare the full match: message/event discriminator,
   field path (top-level versus nested metadata), identifier domain, required joins
   and guards. A counter and detail card with the same feature name may query
   different sets. No current application writer is not proof that historical or
   manually inserted runtime rows are absent.
8. Name the acknowledgement stage precisely: accepted, queued, persisted, transport
   accepted, delivered and read are distinct. Inspect the actual success predicate,
   not a field called "sent" or "delivered". Check independent channel idempotency:
   a failed/disabled external channel can leave a successful in-app channel retrying,
   while queued success may suppress retries before final delivery. A mocked caller
   probe can verify these branches; label transport/runtime behavior untested.
9. Reconcile discovered evidence against both ledgers and diagram. Manual review
   still checks guards, transformations, failures and stale output. Static references
   and matched IDs cannot establish all dynamic/external consumers or live behavior.

For state-bearing helpers, follow every caller, including settings and consent pages,
not only the callers mentioned in comments. Record each consumer's predicate: the
same enrollment state can require a challenge for one consumer and prohibit another
capability even after the challenge. Do not unify distinct policies merely because
they read the same property. Separate absent, pending, enabled and completed states;
identify whether a snapshot belongs to the current identity and whether it comes
from validated remote state or an older session cache. An SDK method name is not
evidence of freshness. Register newly found helper dependencies in the native source
index so the next change's satellite list includes them.

"Complete" means complete within the declared reviewed scope and evidence. If scope
still excludes necessary consumers, say the inventory is partial. Keep migration
coverage, source semantic review, runtime acceptance and agent efficiency separate.
Old pages require an explicit migration inventory; no blind backfilling of "verified".

## Experiment protocol

Freeze source revision, questions and expected evidence before changing presentation.
Compare the existing view with ledger-only and ledger-plus-local-image when a genuine
independent model trial is available and authorized. Use matched tasks/models/budgets,
repeat trials and record failures, not just successes. Score endpoint/typed-edge recall,
false relationships, correct edit locations and failure/role/environment answers;
measure actual tool calls, input tokens/cost and wall time only when logged.

Without independent trials, run an explicitly labelled familiar-reader semantic audit
and structural experiment: count discovered endpoints/relations, inject missing-node,
missing-edge, wrong-target/type/status, duplicate-ID and removed-projection mutants;
check that the real gate rejects them. Render and inspect images and source links.
Record UTF-8 bytes and graph size as context-size proxies, not token savings or agent
speed. Preserve baseline artifacts, raw results and unresolved discovery scope.
Do not infer that generated equality makes the author-written ledger complete.

## SoulNest pilot feedback (2026-10-15)

Two local scopes (journal sharing and public calendar) adopted 30 endpoints and 35
relations, retaining missing/unverified edges. Reverse call-site search found an
additional slots consumer (AvailabilityEditor), and payload inspection corrected
an old "prefilled interval" claim to a date-only event. Thus checking image/text
agreement must be followed by inspecting actual producer and consumer bodies.

Native checks rejected node/edge omissions, bad IDs/types/evidence and removed
records; six real Git-gate fixtures included five rejections and a valid control.
Browser SVG and links were checked. This tests enforcement and exposes real wiki
errors, but is a familiar-reader pilot: no independent agent timing/token experiment.
The added text increases page size. Keep local extraction and evaluate that tradeoff;
do not market diagram coverage as efficiency. 212 other pages remain unreviewed for
this representation, including non-functional pages needing applicability decisions.

Further SoulNest review split state assembly from client consumers. The polling GET
also triggers heartbeat/streak writes; direct client imports include readers,
refresh-only callers and local patch writers. The server forwards nested metadata
and announcement text, contradicting an overly broad small-signal description.
These findings motivated the layer and cache-writer checks above; they are source
facts and documentation corrections, not proof of an unauthorized disclosure or an
independent-agent efficiency gain. Native coverage remains the current migration
inventory; the earlier 212-page number is a historical pilot snapshot.

Reminder follow-up (SoulNest): the detail query required a different message type,
field location and appointment link from the questionnaire writer. The reminder
engine treated deferred queue acceptance as success and independently attempted an
in-app bell even when external channels were disabled. Two isolated mocked caller
probes confirmed the branch behavior, without live messages. This reinforces the
handoff and acknowledgement checks; it does not establish real delivery or database
contents. The migration counts above remain historical snapshots.
## Interactive reading projections

For dense connection maps, offer local exploration over the same endpoint/edge
ledger: choose a node, see immediate neighbors, filter relation kinds, and inspect
conditions, failure, state and evidence. Reflow the local graph instead of merely
shrinking the whole graph; keep stable IDs, full text/JSON and the complete graph.
Display visible/total node and edge counts so a projection cannot impersonate full
coverage. Keyboard controls, reset, empty filters and mobile source-path wrapping
belong in the rendered trial. Static parsing alone misses graph framing and SVG
integration errors. These are optional reader projections, not another truth store.

Derive projection counts and current ID-set expectations from the native ledger;
do not maintain another list of counts in captions or browser tests. Keep an
independent extraction/oracle and omission mutants so a shared clipping bug cannot
make producer and checker agree. Historical trial counts stay attached to their
original revision; append current evidence instead of rewriting the old result.

When reviewing a platform rule, reverse-search the intercepted protocol operation
as well as the shared SDK/helper. Raw HTTP requests and settings reauthentication
can bypass the expected helper while remaining consumers of the same policy.
Register their real paths in the native impact index and show the current missing
handoffs explicitly; a diagram of the proposed chain must not replace current
connection status. Keep resource provisioning and effective activation separate.

For visual preferences, trace preference → resolved role → delivered resource →
actual rendered glyph/image → failure fallback. A selected font-family string does
not prove the font supplies the language's glyphs: a Latin-only face can leave CJK
silently using the same system fallback as another choice. Where this is the reported
failure, inspect actual browser font use and missing-glyph fallback, alongside scoped
owner/viewer rules. Treat asset coverage, licensing, delivered-byte integrity and
measured page downloads as different evidence. Demand-loaded subsets can still be
expensive when a short phrase spans many ranges; whole-font bytes are not page cost.
An isolated resource browser probe does not establish deployed settings or native
client adoption. Preserve that boundary when linking the result back to the graph.

