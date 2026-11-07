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
| Rule scoped to a whole element family or site (base layer, global middleware, default configuration) | Consumer × environment matrix on the rule's owner page; cells not run are recorded as "verified only in …" and pending, never as verified. See [cross-cutting rules](maintenance.md#cross-cutting-rules-need-a-consumer-matrix) |
| A generator writes blocks into authored pages | Stable row keys; change predicates compare authored text; merges resolved hunk by hunk and checked for lost authored lines. See [generated blocks](maintenance.md#generated-blocks-inside-authored-pages) |

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

### Audit the execution surface before adding a rule

A mechanism that exists is not a mechanism that runs. Before diagnosing any miss
([wiki evolution](wiki-evolution.md#4-diagnose-a-miss-before-repairing-it)) and
once per review period, record for every wiki mechanism where it actually executes
and what the last period's evidence showed:

| Mechanism | Runs at (record the actual one) | Evidence to record |
|---|---|---|
| Task router (entry, satellites, rule paths) | manual, at task start | Wrong entries, if any; whether its planned-file input covers the same change range as the gate |
| Touch gate (changed file ⇒ page changed or acknowledged) | pre-push hook / aggregate check / CI | Required versus acknowledged pages per commit; false refusals |
| Generated-view consistency tests | CI only / pre-push hook / finish script | First-run CI failures for stale views; "regenerate" commits per branch |
| Anchor test (authored links resolve against the site renderer) | CI only / pre-push hook | Failures and how each was repaired (link edited, heading renamed) |
| Header ratchet (keywords, verification stamps) | CI only / pre-push hook | Failures; whether the failure named the page |
| Invariant tables and their gates | CI / pre-push hook | Rows added; real gaps exposed |
| Finish script (regenerate, test, stage) | manual | Pages edited after it ran without rerunning it |
| Editor or session hooks | editor; wiring may be untracked | Whether the repository can prove a worker session had it; which checkout's copy of the hook each worktree executes |

Take counts from run logs and branch history, not memory, and state the basis
beside each number. Expensive failures cluster where a check runs only in CI: on
one recorded day the three most costly docs failures (stale generated views,
guessed anchors, unparseable verification stamps) each cost a serial CI round of
roughly forty minutes plus a repair commit, while the same checks take about
twenty seconds in a pre-push hook. The repair is to run the check earlier, keep CI
as the final gate, and offer an explicit, logged skip; it is not another reminder.
A hook runs only on machines that installed it; record that boundary with the
audit. Record what the audit found working as well (correct entry on every task,
a gate that exposed a real gap): a negative control keeps "nothing to change"
available as an outcome.

### Cross-cutting rules need a consumer matrix

A rule that acts on a whole element family or the whole site — a style base
layer, a global middleware, a default configuration — has every member of that
family as its consumer, not only the page where it was first wanted, so its
acceptance is a matrix: consumers (each element kind or route the rule reaches)
× running environments (rendering engine or runtime, viewport or device class,
platform, language or script). Implementation difference is one axis of that
matrix, not a footnote: the same property or option can carry a different limit,
default or fallback in another engine, so a rule verified under one engine's cap
is unverified where that cap does not exist. One recorded example (one project,
2026-11-02): a site-wide typographic rule, added after a walkthrough found about
forty short last lines, was verified in one engine at one viewport and shipped on
that single cell; a month later the product owner, on a mobile engine with no
line-count limit for the same property, saw every short paragraph spread to the
margin and reported the layout as broken. The repair split the rule by consumer,
pinned each part to its source and added a reproducible probe per cell. Before
enabling such a rule: write the matrix on the rule's owner page; mark a cell only
after running it; record every other cell as "verified only in …" and register
it as pending, never as verified by extension; and keep the probe that filled
each cell with the cell, validated first
([quality model](quality-model.md#validate-the-probe-before-trusting-or-ratcheting-its-numbers)).
When the code can apply two states to one element at once (an emphasis mode and a
highlight, a selection and a hover), add those combinations as consumers: a claim
proven for each state alone is unverified for the combination, where the effective
value can depend on rule order in the compiled output rather than on what the
component intended. Name the combinations the code makes possible and test each.
A rule whose reason lives only in a code comment or commit message has no owner
page to hold that matrix; see
[wiki evolution](wiki-evolution.md#2-decide-where-the-knowledge-belongs).

### Generated blocks inside authored pages

When a generator writes blocks between markers inside authored pages (satellite
lists, reverse indexes, invariant projections), three rules keep regeneration from
hiding or destroying authored text. Each has an acceptance test; run it on a
synthetic change before trusting the generator or a gate that reads its pages.
Not committing generated views at all (computing them in CI or in the reader) is
the structural alternative and a decision for the owner
([wiki evolution](wiki-evolution.md#4-diagnose-a-miss-before-repairing-it)); these
rules apply while they are committed.

#### Key derived rows on stable identities

A block written into many pages keys its rows on stable identities (item ID,
anchor slug), never on source line numbers or positions. A position key turns one
row inserted in the middle of a ledger into a rewrite of every page that cites a
later item: every open branch conflicts and every page looks changed to
change-based gates. Keep positions only in one aggregate view (this helper's
`route-index` is one) or compute them at render time. Acceptance: insert one row
in the middle of the source and regenerate; only the aggregate view may change.

#### Compare authored text, not files

A predicate that decides "this page changed" — a touch gate counting a page as
updated, a design-first check counting a wiki change as a written design —
compares the page's authored text at base and at head, with generated blocks
removed by their markers and whole generated files removed by path. Comparing
files lets regeneration alone satisfy it: one regeneration that touches every
page makes the touch gate require nothing and the design check pass on every
branch. Acceptance: a self-test in which hundreds of pages change only inside
generated blocks; the predicate must report none of them as changed.

#### Merging files that mix authored and generated text

Never resolve such a file by taking one side's whole file and regenerating: that
discards the other side's non-conflicting authored lines, and gates stay green
because generated drift satisfies them. The decision is mechanical:

1. Build the two candidate resolutions that keep every auto-merged hunk and
   resolve each conflict hunk to one side (with Git, `git merge-file -p --ours`
   and `--theirs` over the three index stages; `checkout --ours` takes the whole
   side and is the failure above). Strip generated blocks from both.
2. Equal ⇒ every conflict lies inside generated blocks: keep either candidate and
   regenerate with the native command.
3. Different ⇒ resolve the remaining authored hunks by hand, one hunk at a time,
   from both parents.
4. Append-only ledgers (debt lists, changelogs, logs) where both sides added
   entries at the same position keep both sides' entries; then check for
   colliding IDs.
5. Code and tests are never resolved by de-duplicating lines that share a prefix;
   lines that look identical are often distinct. Run the type check and the
   related tests before committing the merge.

Guard every merge for lost authored lines: for each file, take the authored lines
(generated blocks stripped) that each parent added since the merge base, and
require every one to be present in the merge result, or listed as a deliberate
removal with its reason. Run it before pushing a merge. When auditing historical
merges, add the current HEAD as a second view: a line missing from the merge but
present again at HEAD is reported as restored; only lines still missing at HEAD
fail. Acceptance: a synthetic merge in which one side edits a page's generated
block and the other adds an authored line elsewhere on that page; a whole-side
resolution must fail the guard and the stepwise resolution must pass it.

### Pre-edit gate (host delivery of Wiki-first)

When workers repeatedly write code first and the page last although the prompt
says Wiki-first, the repair is a mechanism, not another reminder. The package
ships an optional Claude `PreToolUse` hook (`Edit|Write|MultiEdit`) running
`scripts/edit_gate.py`; Codex hooks carry delivery only. It judges a checkout
only when `.project-wiki/edit-gate.json` exists at its root, and for a path that
matches `locked` (or appears in `map_file` as `map_row_format`, default
``| `{path}` |``) it checks two predicates and reports each with its own fix:

- **(a) context** — the `stamp` file (JSON with `files`) is younger than
  `max_age_hours` and lists the path's repository-relative form; `stamp_command`
  is printed as the fix with `{file}` filled in;
- **(b) design** (only with `design_first`) — a handwritten file under `wiki_root`
  changed since `merge-base(HEAD, base_ref)` (default `origin/main`), in the
  working tree or untracked, after removing `generated` views. `generated` holds
  file globs only: a page whose only change is a regenerated in-page block still
  counts as handwritten here, unlike the
  [authored-text rule](maintenance.md#compare-authored-text-not-files). Without a
  merge-base (b) is not judged and says so. A non-empty `skip_file` waives (b)
  only and is echoed; an empty one fails (b).

Exit 2 blocks the edit with the reasons on stderr. The gate runs only read-only
Git subcommands (optional locks off, inherited repository variables dropped),
executes no project code and writes nothing. Any defect of its own — unreadable
or malformed config, malformed event, Git failure — passes the edit with
"gate unavailable" on stderr.

What it proves: the route was expanded for this file, and some handwritten page
moved on this branch first. What it does not prove: that the worker read the
page, that the moved page is the owning one, or that the design is right. One
unrelated line satisfies (b); review and the finish/touch gate stay responsible
for that. What it does not see: writes made through a shell (redirections,
heredocs, generators, formatters) never pass through the editor tools the hook
matches. State that boundary on the project's gate page; the touch gate is the
backstop. The two gates split the work: this one runs **before** the first edit
of a locked file; the touch gate runs at **finish or push** and checks that every
changed file's owning page changed or was acknowledged.

Keep both inputs honest:

- **The stamp is evidence only if the worker's routing wrote it.** Test suites
  that run the router from the repository root refresh the stamp, extend its age,
  overwrite its query and add fixture paths. Give the router a no-stamp switch or
  environment variable that every test sets, or run those tests in a temporary
  directory, and record the writer in the stamp. Acceptance: a full test run
  leaves the stamp's bytes and modification time unchanged.
- **A design written before the code is a proposal.** Mark it designed, not
  implemented, until the evidence exists
  ([wiki evolution](wiki-evolution.md#6-keep-current-state-and-historical-evidence-apart)).
- **A design waiver is bound and narrow.** The shipped `skip_file` is checked only
  for non-empty text; it carries no revision or age, so remove it when the task
  ends. A project gate binds a waiver to `{reason, head, at}`, voids it when HEAD
  moves or after the stamp lifetime, echoes it at finish as a proposed
  acknowledgement, and accepts it only for "no design needed". A defect in the
  gate itself takes a separate, logged override, not the design waiver.

```json
{
  "wiki_root": "docs/wiki",
  "locked": ["src/**", "api/**", "migrations/**"],
  "map_file": "docs/wiki/file-map.md",
  "stamp": {"path": ".project-wiki/stamp.json", "max_age_hours": 8},
  "stamp_command": "<router command> --files {file}",
  "design_first": true,
  "generated": ["file-map.md", "index.md"],
  "base_ref": "origin/main",
  "skip_file": ".project-wiki/design.skip"
}
```

A project that already has its own pre-edit hook keeps it and does not also
enable this one: two gates with different predicates give two answers. Either
way, record in the audit above whether the hook is wired on the machines that run
workers; wiring kept outside the repository is an unproven delivery.

A hook a project writes in a shell must survive large input. Under
`set -o pipefail`, never end a pipeline over many lines with an early-exit
consumer (`grep -q`, `head`): the consumer exits at the first match, the producer
receives SIGPIPE (status 141), and the pipeline reports failure exactly when there
is a lot of input. Collect the output into a variable, then test it for
emptiness; treat a failed producer as "gate unavailable", never as empty output.
Automate the hook's self-tests, including hundreds of dirty files and a failing
Git command. A hook executed from each worktree's own copy is fixed only where the
fix has been merged: pin the hook command to one stable checkout, or notify open
worktrees when the gate changes.

### Checkable rules beat examples

A template line or an example in a README teaches a format once; a rule a gate can
check and name teaches it every time. Recurring cases:

- **Verification stamps.** Fix the parseable form: date · commit sha, optionally
  followed by scope ("verified X; Y not re-verified") and older stamps. A branch
  or worktree name is not a revision; for uncommitted work write the base commit
  the tree was verified on plus "worktree (branch)". Put the rule where authors
  look, beside the template, and make the parser the authority. Deployment
  qualifiers ("not deployed", "branch", "worktree") expire silently once the
  change merges and ships: after each release, list the stamps whose commit is an
  ancestor of the deployed revision while they still carry such a qualifier.
  Keep one current stamp per page and move superseded segments to history; a
  dozen segments on one line hide the current state.
- **Acknowledgement lines.** If the syntax allows a reason per page, the parser
  accepts `page (reason), page (reason)` or fails naming the line; dropping
  everything after the first bracket acknowledges one page and reports the rest
  as missing. Test the parser with a line that gives several pages each a reason.
- **Feature-entrance keywords.** An entrance carries both the words users and
  reporters use and the code symbols, as two kinds a header check can tell
  apart; the check names the page that lacks either kind. A symbol-only keyword
  line is invisible to a symptom phrased in user words.
- **Heading anchors.** The site renderer's slug is not GitHub's slug (full-width
  punctuation, backticks, underscores and brackets differ). Prefer slug-safe
  headings, without brackets, backticks or underscores, so others cannot guess
  wrong. When a complex heading must be linked, copy the ID from a CLI that lists
  the renderer's real ids for a page; do not derive it by habit.

A ratchet or format gate that fails must name the offending page and distinguish
"no line" from "malformed line"; a bare `false` sends the worker back to CI logs.
Keep the numeric baseline unchanged when a check gains names: naming is a
reporting improvement, neither a relaxation nor a tightening.

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
