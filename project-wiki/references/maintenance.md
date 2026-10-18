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
> missing/stale, use a targeted search and repair it. Source wins over stale prose.

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
