# Systematic design review and incomplete frameworks

Use for architectural reviews, broad feature audits and changes with cross-domain
consequences. Source audit answers what exists; design review must also ask whether
that arrangement can satisfy the intended user outcome, and provide a reasoned
path from the actual system to the necessary capabilities. Reuse native conventions,
ADRs, debt tracking and decision records; do not create parallel truth registries.

## Four independent conclusions

| Axis | Record | Never infer |
|---|---|---|
| Design fitness | retain / local correction / refactor / insufficient evidence / justified non-applicability, with invariant and rationale | Working code proves a good boundary; missing code proves bad architecture |
| Implementation | complete / partial / absent / diverges from design; list missing producers, consumers, skins, migrations, adoption and validation | A framework API/type exists so every caller uses it |
| Evidence | exact source, offline, environment workflow or production observation and limits | A diagram, mock or design decision proves runtime acceptance |
| Decision maturity | established rule / recommendation / proposed / selected / deferred / superseded | An ADR is implemented because it is accepted, or a proposal becomes mandatory through repetition |

A sensible architecture with unfinished code needs an implementation/adoption plan,
not automatic redesign. An operational but poorly owned lifecycle needs compatible
refactoring. A poor/incomplete design with incomplete code needs its missing
responsibility/state decisions settled before more feature branches are added.
Evidence-limited cases need targeted discovery, not a negative verdict disguised
as rigor. These judgments may differ within a feature: retain the core while fixing
an adapter, caller, stale cache, or omitted consumer.

## Reason from goals to options

1. Define the user's observable result and necessary capabilities, including failure
   and relevant actor/client variants. Compare against confirmed product decisions
   and existing architectural rules; mark any proposed change of policy explicitly.
2. Trace responsibilities: business policy, persistence, projections, commands,
   events, local state and platform skins. Identify the owner of identity, lifecycle,
   retries, concurrency, access, freshness, limits and observable completion.
3. Find the smallest counterexample to the intended invariant. Distinguish a missing
   implementation/caller migration from a weak abstraction. Same names do not prove
   equal sets; duplicate-looking adapters can express valid platform differences.
4. Compare retaining-and-completing with a local framework correction; add a new
   shared abstraction only when actual consumers justify it. Explain benefits,
   coupling, compatibility, migration/rollback, operational and verification costs.
   Give a recommendation and what evidence could falsify it. Do not invent benchmark
   numbers or justify a framework only by elegance.
5. Describe the necessary target contract/lifecycle/interaction diagram, clearly
   proposed versus current. Prefer deriving from existing authorities. If a new
   schema/API is a candidate, do not give it a source locator implying it exists.
6. Split the path into concrete deliverables: edit seams, dependencies, preserved
   invariants, migration/adoption, exit tests and runtime acceptance limits. Track
   execution only in the project's work/debt system; link rather than clone status.

Check design incompleteness explicitly: absent owner of retries/freshness/identity,
underspecified partial success and cancellation, incompatible client capability,
missing privacy/role/partition boundary, migration without a backward path, and
observability that cannot distinguish failure from empty or accepted from delivered.
These are review prompts, not universal requirements for every trivial mechanism.

For a server policy shared by Web and native clients, distinguish implementation,
deployment, activation and acceptance. Include already-distributed clients and their
actual update path in the consumer inventory: wiring the new App does not make an
old App compatible with a global authentication switch. Derive activation order
from that matrix and preserve independent authentication flows. A vendor's dummy
success fixture establishes integration behavior, not real challenge acceptance,
replay rejection or availability under a vendor outage.

Trace cross-client flows through the storage that owns each proof, not just their
HTTP endpoints: a verifier generated in an App cannot automatically be redeemed
by a browser with different storage. Include runtime capability requirements and
native binary fingerprints where a JS dependency needs native support. Verify the
entire user outcome (for example, mail request, delivered link and usable recovery
form), and record exactly where the observed journey stops. A successful login
does not establish that signup or password recovery uses the same primitives.
Check fixture semantics against actual behavior: an always-pass provider key may
accept arbitrary responses, and a forced duplicate-error fixture does not prove
that a real token was consumed once. Keep these assertions separate in the wiki.

Keep historical incident reports as dated evidence. Route readers first to current
implementation and deployment observations; do not reuse old content counts,
ownership-verification claims, causal percentages or search-index snapshots as a
current diagnosis. Technical output and an external consumer's acceptance require
different evidence, for example rendered SEO metadata versus search-console coverage.

## Ready work, decisions and re-entry

Separate documentation correction, implementation under established design,
architectural proposal, product-policy choice, and evidence-dependent deferral.
Each action or unresolved decision needs a concrete artifact or existing tracking
ID. A TODO must name a deliverable and success evidence, not just "improve framework".

A deferred record includes:

- the precise question and reason the missing evidence could change the answer;
- bounded dependency scopes and expected evidence artifact;
- current options/recommendation, decision responsibility and safe work that can
  proceed independently;
- a specific revisit trigger, such as completion of the named caller matrix, plus
  an audit-closeout sweep; upstream contract/role/goal changes reopen it;
- a recorded outcome: select, adjust, reject, or list remaining concrete evidence.

Do not defer everything until a whole-repository review ends. Do not let a deferred
shared-package choice block a proven local freshness fix. When dependencies become
ready, return in the next related review; if still blocked at closeout, preserve the
unresolved decision and next evidence step. Elapsed time is not a decision.

Keep design adoption and implementation status separate in ADRs and handoffs. A
selected design may be unimplemented, partially adopted, awaiting migration, or
implemented but unverified. Never close product debt merely because its design was
written or accepted. Existing legacy ADR status definitions must be read in context,
not silently reinterpreted as proof that code or deployment exists.

## Report and validate

A feature entrance can summarize design judgment, actual implementation gap,
linked proposal/work package and revisit condition. Keep full rationale in the
native design document; keep the short route usable. A minimal design note is
usually enough; create a formal ADR for an actual cross-cutting tradeoff, not as
bureaucracy for every page.

Validate source bindings, consistency of current/proposed labels, preservation of
confirmed rules, traceability from gaps to work and from deferred decisions to
triggers, and representative negative scenarios. Structural parsers can check
record shape, never design fitness. Avoid introducing a new mandatory schema before
trying it on real cases and observing that it helps the engineering decision.

SoulNest example: existing NotifyResult explicitly treats deferred queue acceptance
as success. That core contract can be sensible while a caller's delivered counter
and independent bell idempotency remain unfinished. Preserve the queue owner;
compare a local caller fix against a full receipt ledger before choosing the latter.
G-72 deliberately retains two questionnaire sets: a broken producer/consumer match
is a wiring gap, not automatic authorization to merge the sets. Keep these as source-
bounded examples, not rules imposing SoulNest's architecture on other projects.

## Re-enter a decision with evidence, not another deferral

For fan-out, queues or side-effect dispatch, enumerate actual production call sites,
including dynamic imports, aliases and wrappers; separately inspect unused imports,
non-call references and registry-only entries. Record the discovery scope and
snapshot. Syntax counts establish an inventory, not runtime reachability. Follow
results through wrappers and caller writes/counters as well as through catches:
a fulfilled failure value, an empty result, a rejection and an ignored promise have
different effects. Ignoring a best-effort notification must not automatically cause
an already committed payment or message to be replayed.

Validate the bottom of the result chain before designing a shared status model.
Local spool/log success, queue acceptance, provider acceptance, partial-device
success and user receipt/read are different evidence. Require positive response
shape where the adapter contract needs it; read failures are unknown, not empty.
Compare the actual serializer with the client consumer: a declared deep-link field
may live at the wrong nesting level and never survive to the click handler.

For coalescing queues, distinguish business occurrence identity, coalescing key,
message version, send attempt and consumer claim. A unique pending-row key is not
proof of single delivery. Review concurrent drains, upsert during an in-flight send,
stale acknowledgements deleting a newer version, post-send persistence failure,
lease recovery and uncertain provider outcomes. A process lock can reduce overlapping
workers while failing to protect a row replaced by a producer; compare costs before
choosing a claim/version protocol. Avoid holding a DB transaction across network IO
or claiming exactly-once from an atomic claim alone.

When named dependencies finish, replace the old pending question with the actual
finding and recommendation. A wider ledger can be unwarranted even when local
protocol fixes are necessary. Reuse existing domain ledgers and logs; reopen the
wider option for named consumer needs or a concrete insufficiency, not because a
proposal remains in a document. Keep formal adoption and implementation separate.

## Compare the user's workflow before retiring an implementation

Use the existing role's business tasks and conveniences as the baseline, not the
name of a Legacy file or a list of newly implemented CRUD controls. Route to the
product journey and cross-domain map before selecting the old/new components.
For each actor record a starting state, intent, command, authoritative result,
other party's visible state/next action, and the failure or unanswered path.
Trace connected messaging, preparation, reminders and completion where required;
a page opening or a queue accepting work is only one edge of that journey.

When authorized and source evidence is insufficient, actually use the legacy
workflow in the appropriate role/environment and preserve a same-data comparison.
Classify parity per capability as equivalent, improved, missing or deliberately
inapplicable with a reason. Opposite sides of one workflow need connected outcomes,
not identical permissions. Retiring a redundant adapter and completing the whole
feature are separate claims; do not delete until the scoped retirement evidence
is met. Mark role-playing/design scenarios as analysis, not user-study evidence.
