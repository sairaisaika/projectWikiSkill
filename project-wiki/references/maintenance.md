# Sustainable maintenance and change planning

## Adoption

1. Identify the highest-value recurring change/debug questions and authoritative
   code/design constraints. Start with useful coverage, not every file in the repo.
2. Keep one shared wiki for coupled projects; document which repository actually
   implements each package/service. Put short pointers in existing entry documents.
3. Create schema-2 routes with declarations, implementations, consumers, contracts,
   rules and checks. Add a local explanation/diagram where a task needs one.
4. Build and audit; run scenario evaluation. Inspect semantics and acknowledge gaps.
5. Offer a concise default path: engineering entry → query → local section. Avoid
   global locks or forcing users through an entire documentation tree.

Example entry text (adapt to the project's existing instructions):

> For interface or tagging changes, the engineering wiki maps tasks to current
> declarations, implementations, impacts and focused checks. Start there when it
> saves discovery; verify the cited implementation before editing. If a route is
> missing/stale, use a targeted search and repair it. Source establishes actual
> implementation behavior; resolve conflicts with accepted rules or proposals
> through the evolution guide before changing either.

## When a change happens

| Trigger | Update and verify |
|---|---|
| File/symbol moves | Route location and index; moved/missing/ambiguous-location tests |
| Public API/contract changes | Declaration → implementation → consumers/guards → compatibility/migration → tests → wiki |
| Rule/default changes | Stated rule, provenance, historical behavior, config propagation, regression evidence |
| Dependency replaced | Required/optional capabilities, failure meanings, cache/transaction/runtime responsibility |
| New feature proposed | Planned record and exit evidence; no fabricated source or installation proof |
| Test/install/live result observed | Append the actual claim, revision/date and durable reference; preserve old scope |
| New query misses | Add a supported synonym/route after evidence-based discovery; keep unknown-query controls |
| False-positive route | Narrow aliases or split layers; do not just lower acceptance thresholds |
| Compound scope is missing | Update the playbook/task map and independent expected-scope cases; single-route accuracy is not completeness |
| Location stops at a large factory | Add the relevant internal edit seam, purpose and consumer; verify catch/commit/shared-rule boundaries |
| Query grows over budget | Remove duplicate locations/prose or split concerns; preserve scope and rerun all questions without raising limits just to pass |
| Human summary disagrees with JSON | Recompute counts/maxima from the report; preserve historical trial scope instead of silently relabeling old results |
| Endpoint or relation added | Regenerate all local projections and counts from native IDs; verify full-set retention with an independent oracle rather than editing duplicated test constants |
| Serialization/state/timing changes | Update authoritative schema, field/transition tables, source-linked local diagrams and relevant decision rationale; rerun actual conformance/recovery tests |
| One commit's acknowledgement list exceeds ~10 pages | Give the shared file's rules identity and key routing/gate on rule edges; keep uncovered files on the file rule; measure required pages per commit before and after. See [route by rule](change-navigation.md#route-by-rule-not-only-by-file) |

These rows say what to update. Where the knowledge should live (edit in place, new
section, split, new page, shared concept, archive or no structural change), which
reading the task must close first, how to diagnose a missed read before repairing
it, and what to do when wiki and source disagree are in [wiki evolution](wiki-evolution.md).

Review changed source as a signal, not as proof that all prose is stale. Normalized
whole-file hashes intentionally flag conservative review; only update reviewed_at
after reading the affected rule/caller. Build timestamps are not review evidence.

## An actionable plan

For each work item, record:

- Outcome: concrete before/after behavior.
- Dependencies: actual technical causality; independent work need not wait.
- Interfaces: exact declaration, implementation and consumer route IDs.
- Deliverables: code, migration/compatibility notes, checks, documentation.
- Exit evidence: observable acceptance and what it does not prove.
- Unknowns: undecided behavior, missing runtime access or unverified provider shapes.

Track planned, implemented, offline-tested, installed and live-verified as distinct
claims. Reconcile final code against the plan and remove abandoned promises from
current documentation. Do not turn source completeness into deployment acceptance.

### Keep delegated work connected to the feature

A worker needs a short answer to "where do I change this safely?", not just a
large design document. Reuse the native task handoff to provide:

| Needed answer | Minimum useful context |
|---|---|
| What do I read now? | Existing feature route, relevant section/diagram and exact wiki checkout/revision; mark an exported snapshot as a projection |
| Does it apply to my checkout? | Implementation base plus the relevant difference from the wiki candidate; identify referenced sources absent from this checkout |
| What should change? | Intended outcome, actual edit seams, caller-owned guards and affected producer/consumer IDs; distinguish existing behavior from the selected proposal |
| Where does the result go? | Same feature route, existing debt/task record, focused exit evidence and who owns shared-document updates |

Before implementation, check that the supplied inputs are reachable and summarize
the applicable boundary and any missing source in the existing task response.
Do not require a second manifest, a full-wiki recap or a ceremonial read receipt.
If a candidate source is unavailable, obtain a revision-bound excerpt or report
that dependency; do not silently replace it with a similarly named local file.

At return, compare the actual diff with the same feature's producers/consumers:
what is connected, what is still absent, and what was observed. Verify cited input
files and reused-symbol locations against the actual checkout; repair invented
page paths or duplicate debt suggestions before
adoption. If the worker cannot edit shared documentation, the coordinator owns
that update before calling the work package complete. Link a new feature from
the old entry users already follow; state whether its reader shows main or a
candidate checkout. A report or local preview alone does not establish adoption.

Evaluate the repair on an actual handoff: can the worker find the right route,
notice the checkout mismatch, retain the original policy and return changes to
the same entry without inventing a page or debt? Record observed corrections and
remaining errors. An instructed retry by the same worker is a recovery trial,
not an independent blind evaluation or proof of lower effort.

Keep fixed audit/test receipts separate from current release and rollout state.
Point feature pages to the existing owner of that state, rather than copying a
mutable "awaiting deployment" claim into every satellite. File-change gates do
not cover a deployment, activation or rollback that changes behavior without a
source edit; review the relevant feature routes and consumers for those events too.

For a live generated reader, check source closure and input stability before replacing
the last complete output. Test a failed generation and recovery, not only a healthy
page. Choose whether failure serves an explicitly stale snapshot or refuses it;
retaining old files does not itself communicate freshness. Give actionable errors
without reflecting raw exceptions or credentials. Distinguish a synchronous
single-process promotion from cross-process or crash-atomic publication.

Across source/wiki repositories, include each selected checkout and change range in
the impact inventory. A gate scanning only the wiki repository does not cover edits
in its sibling source repository; a missing peer is unverified, not an empty diff.
Keep complete developer-facing impacts visible when saving machine JSON, without
contaminating its stdout contract. Saving a report does not establish that it was read.

For a CI or deployment consumer, verify its actual invocation, selected sources and
step output, not only the aggregate green result or the fact that jobs share a host.
Different users, HOME directories and permissions can make a peer unavailable; a
skip that exits successfully is still unverified. Record NOTRUN separately and
bind cross-repository comparisons to the exact source pair. A matching historical
version or a commit-time approximation is not exact equivalence. A real local
paired check remains useful evidence, but cannot be relabelled as a CI execution.
An exact commit label also requires the compared inputs to match that commit;
equal dirty copies do not prove a fixed revision pair. A cached matching directory
does not prove this run obtained its intended source. Exercise absent/empty sources,
wrong revisions, read errors, real byte drift and a real matching pair, checking
both the script's exit status and its consumer's classification. Repair the source
and reporting boundary without widening unrelated credentials or host access.
Before asking for new credentials, inspect the actual consumer identity and existing
scoped source access; a private peer need not require another token. Prefer the
smallest authorized source path and document its ownership/read boundary. For PR
jobs, distinguish branch head from the actual synthetic merge checkout; record
the compared commit, not a convenient label from the run summary.

For live stateful checks, persist a scoped restorable baseline before the first
write, and clean independent subjects even if an earlier cleanup fails. Reversing
one UI choice may materialize defaults in companion fields; read back the actual
scope before reporting restoration. Lost before-state followed by an explicit
fixture reset is not recovery of that state. Preserve functional success and
cleanup failure as separate evidence.

Choose runtime witnesses with explicit actor, flag and data predicates. A
conditional consumer that is absent because its list contains data is not a
rendering failure. Preflight the actual state, keep that failed assumption as
negative evidence, and use a reachable consumer for the intended boundary; do not
delete content or change unrelated flags merely to force the expected picture.
Document concrete consumer locations and their predicates beside an aggregate
resource interface, so the next agent can select a valid integration check.

Separate an exposed interface from the readiness of its consumer. A visible
control, mounted subscription or replayed input can run before an owner-bound
writer or service is installed. Exercise that real lifecycle window and show the
readiness/ownership transition; then verify the built artifact rather than only
an isolated handler. Also test transformations at the consuming seam: a valid
producer token can fail after opacity, composition, truncation or normalization.
Do not compare a default selector key directly with its resolved effective value.

For a multi-commit change, exercise the same base/range that CI will inspect, not
only the final incremental diff. Keep machine-parsed section keys intact and put
historical or current-status qualifiers in their prose; do not relax the parser
to accommodate an editorial rename.

Bind release acceptance to the actual artifact and evidence bytes. Rebuilding after
QA can change the result despite an unchanged source/version label; use the verified
artifact or retest the final one. Trace draft promotion and downstream Latest/public
distribution separately, and reject overwriting a published identity with new bytes.

When a release or acceptance rerun reuses an output path, retain the earlier
attempt's report and relevant failure detail before replacement. Give each attempt
its own source/artifact identity, outcome and digest. A later green run is another
witness, not an explanation of the earlier failure. If the earlier detail was lost,
record its cause as unknown rather than borrowing a similar failure's diagnosis.

For asynchronous state or preference links, document who owns the decision when an
older read arrives after a newer choice, including time spent waiting on upstream
locks. A successful persistence response does not prove that the visible state and
device cache converge to it. Vary delivery order using actual bounded payloads and
check stored, cached and rendered values separately; include change-back sequences
and independent fields when relevant. A held-response reproduction is controlled
timing evidence, not a real-network or outage test. Preserve that counterexample
even if an ordinary flow passes after adding a read-back or synchronization barrier.

Resolve referenced debt/decision IDs to their actual title and scope before carrying
them into another page or handoff. Existence alone is insufficient: a valid ticket
number can belong to an unrelated feature. Separate a supported topology from an
observed active route; a Compose network named for ingress does not establish a
remote-managed tunnel hostname, DNS record or public reachability.

Configuration also has consumers at parse/build time. A Compose file may interpolate
all services during an app-only build: a required production connector credential
can therefore break isolated staging before that connector ever starts. Check the
actual build without unrelated production secrets, then separately validate the
running service's required credentials. Never satisfy a build-only dependency by
borrowing a production credential or inventing a dummy value.

## CI and ownership

Use a stable feature/route ID as the lightweight ownership unit. Coordinate only
when edits overlap. A worker receipt should list routes used, exact symbols checked,
checks run, findings and deviations. Sending a link is not evidence it was read.

Make the helper available in the repository or a pinned dependency accessible to CI.
If copying it, record the upstream skill revision and review updates rather than
silently mutating a user's installed tools. A typical job (Python 3.10+) runs:

```sh
python tools/wiki.py check --root .
python tools/wiki.py evaluate --root . --tasks docs/wiki/eval-tasks.json
```

`build` is an explicit authoring action, not an auto-repair step in CI: CI must fail
on stale committed snapshots instead of overwriting them and passing. Keep commands
read-only except the documented index generation. The helper does not render Mermaid,
verify domain truth, run commands listed in a manifest, or validate live systems.

Independent trials, if authorized, use fresh workers and isolated outputs. Give the
task, entry and skill without expected route IDs, suspected bug or proposed answer.
Maintain a small regression set plus held-out paraphrases; distinguish fitting an
alias from an independent behavior improvement. A review cadence or automation must
follow the user's project preferences, not be scheduled silently by this skill.

Maintain one clearly authoritative current checkpoint per active goal or feature.
Older appended checkpoints keep their evidence but must not still say they outrank
newer state. Separate current source/CI, the built and installed artifact, observed
behavior and pending capabilities in that checkpoint. A new reader should not need
to reconcile several contradictory “current” sections before deciding what to do.
