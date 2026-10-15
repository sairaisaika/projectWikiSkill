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
