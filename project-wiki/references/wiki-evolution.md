# Evolve wiki structure from real changes

Use this when a task changes what the project knows: a rule moves, a feature gains a
variant, evidence arrives, or a worker missed something it should have read. The aim
is that the next task finds the right knowledge **at the right grain**, not that each
task appends another paragraph. Appending is often correct; it should be a decision,
not the default.

Proportionality here never overrides a project's own requirements. If the project
asks every task for a wiki start, end or efficiency note, a task that changes no
knowledge still records it; a short "no wiki change" with its reason is enough.

This guide complements [maintenance](maintenance.md) (what to update when source
changes), [change navigation](change-navigation.md) (first task read, satellites,
task maps), [page anatomy](page-anatomy.md) (how a page is composed) and
[native wiki adoption](native-wiki-adoption.md) (reuse the project's own parser,
indexes and gates). It adds four things: closing the required reading, deciding
placement, diagnosing a miss at the right layer, and migrating structure safely.

## 1. Close the required reading before deciding anything

Registered satellites and links are a starting set, not the boundary. Derive what
must be read from the task itself, then check each item is reached:

| Derive from | Read |
|---|---|
| Capabilities the user expects | Each feature entrance that owns one of them, including ones the user did not name |
| Invariants the change relies on ("X is always true") | The writer and the paths that can violate it: degraded identity, fallback, missing data, alternate client |
| Producers and consumers | Callers of the changed seam and readers of its output whose behavior depends on what changed; confirm by searching source, not by the page's list alone |
| Identity, state and environment axes | Owner/viewer, role/partition, rollout/deployment, build profile; the page that defines each axis and where it is enforced |
| Shared rules touched | The rule's owning page, plus overview pages and diagrams that restate it |
| Assets, terms and links the change emits or edits | The actual consumer: the reader that renders an image or heading ID, the glossary or term index, the generator that projects links |

Follow causality, not reachability. Name what the change alters: a field, a
predicate, a state transition, an error or its meaning, an emitted artifact. Trace
the consumers of that, including indirect and cross-client ones. Stop at a consumer
when the contract it uses is unchanged and nothing it observes differs, and say so;
a diagnostics-only change that keeps every status, field and error meaning stops
early. Do not recursively expand shared infrastructure into an impact list (see
[change navigation](change-navigation.md#make-the-first-wiki-read-useful)).

A complete candidate inventory, such as every registered satellite of a planned
file, is not a duty to read every page in full. Keep every candidate and give each a
disposition: read the relevant section, checked and unaffected with the reason, or
unread with the reason. Never drop a candidate silently or treat an absent inventory
as no consumers. An unregistered file or page is a routing gap, never evidence of
no impact. Prefer the native index and task entry over guessed file names; a guessed
path that happens to exist is still an unverified route.

Write this closure in the existing task record before editing: what the change
alters, the derived items, their dispositions and where tracing stopped. It is
short; it is not a second manifest.

## 2. Decide where the knowledge belongs

Make two separate judgements. The first decides what happens to the fact; the
second decides whether the structure around it is still right. The first never
ends the second: editing a sentence in place does not answer whether that sentence
should exist in three places.

### A. Handle the fact

1. **Does it change what any reader should conclude?** If not — a re-run with the
   same result, a log, a mechanical rename already covered by generated indexes —
   no factual rewrite. Record the observation and reason in the task record; still
   consider B when this task exposed a placement, discovery, duplication or consumer
   problem. An unchanged fact can be poorly organized.
2. **Is it evidence about a fixed revision or artifact?** Put it beside the claim it
   supports, bound to that identity, in the page's evidence or history area. Do not
   rewrite the current-state statement unless the evidence changes it.
3. **Does it change or add a current statement?** Edit the current statement, keep
   the superseded version as dated history when readers or receipts may rely on it,
   and list every restatement found during closure (section 1). Before editing,
   check what kind of statement it is (section 4, wiki and source disagree): a
   confirmed rule is not corrected merely because source differs.

### B. Review the structure

Run this when A changes or adds knowledge, or the task exposes a structural or
discovery problem even if every fact stays true. Repeated identical evidence alone,
with no such signal, needs only a short no-structural-change reason. Evidence arrival
does not bypass review of its placement or actual consumer.

- **Owner.** Is the same rule stated in more than one place, or needed by several
  features? Give it one owner (section 3); other places link and keep only their
  local condition. Copies that drift are a structural problem, not several edits.
- **Grain.** Is it a branch, variant or exception of an existing mechanism? Put it in
  that mechanism's section next to the general rule, with its condition. Is it a
  distinct responsibility or user capability with its own producers, consumers,
  states or verification? That is a feature entrance following the feature
  completeness contract. A new page is right when the knowledge has a different
  owner, lifecycle or audience; it is wrong when it only avoids editing a long page.
  A new chapter or index section is justified when navigation repeatedly fails
  across a group of pages, not when page count grows.
- **Entrances.** Does any of this move, rename, merge or archive something readers
  already use? Then migrate (section 5); archived content keeps a dated pointer to
  its current owner.

Indicators that structure should change: readers repeatedly land in the wrong
place; one page is the first stop for unrelated tasks; a rule is restated in several
places and the copies disagree; a diagram is wrong for a variant it does not
mention; or one fact needs edits in many places to stay true. None of these is a
count; weigh them against the cost of moving links and readers' habits.

No structural change is a correct outcome of B when the existing page already owns
the fact at the right grain, summaries retain its conditions and link its owner,
and readers' entry points stay valid. Record that with the reason; it is evidence of judgement, not an
omission.

## 3. Shared rules versus feature mechanisms

A **shared rule** constrains several features (an access predicate, an update
channel policy, a release gate). A **feature mechanism** is how one capability works.
Keep one owner for each shared rule: state it once, with its scope and exceptions,
and let feature pages link to it and add only their local condition.

Overview pages and summary diagrams are the most common hidden copies. A summary edge
or sentence that omits a condition is a restatement with a narrower truth. When a
variant makes it false, either qualify it with its condition and link the owner, or
remove the claim from the overview. Do not widen an overview until it duplicates the
owner.

Preserve legal exceptions. When features legitimately differ (an administrator
exemption, a self-access case, a build variant with a capability disabled), the shared
rule names the exception and its owner; the feature states that it relies on it.
Unifying wording must not erase a real difference, and a difference observed in code
is not automatically a bug — check the owner's stated rule and decision record first.

## 4. Diagnose a miss before repairing it

When a worker missed or misused knowledge, classify the failure before editing. Each
layer has a different repair; fixing the wrong one hides the real cause.

| Observed | Likely layer | Repair at that layer | Not a repair |
|---|---|---|---|
| The fact is not written anywhere authoritative | Rule absent | Write it at its owner (section 2), with its authority and evidence | Adding a reminder elsewhere |
| The fact exists but no route from the task reaches it, or it sits in an overview that hides its condition | Linking or granularity | Add the route from the entry readers use; move or qualify the statement; register native sources | Copying the fact into the task page |
| The route exists but the index, ranking, satellite projection or generated view drops it | Retrieval or projection | Fix native metadata or the selector; test with the original failing query | Telling agents to read more |
| What the worker actually received omitted the relevant section, or was truncated, or came from another revision or checkout | Delivery (helper input, packet, hook, handoff) | Fix the delivery path or its inputs (checkout, peer, selected evidence, size limits); record what was delivered | Rewriting the page |
| The right revision's relevant section was demonstrably delivered or opened, and the worker did not use it | Adoption | Record it as an adoption miss; improve the task-facing cost (shorter entry, earlier impact, clearer scope) only if repeated | Assuming the wiki was wrong |
| The consumer cannot use a correct artifact (reader does not render an image, heading IDs differ from authored links) | Consumer capability | Record the gap at the consumer's owner; verify against the actual consumer | Declaring the link "done" because the file exists |
| The wiki and source disagree | Conflict to investigate (below) | Depends on the statement's kind | Editing either side by default |

Delivery and adoption need evidence, not inference. Before calling a miss adoption,
check: which wiki revision the worker had; which entry or query it used and what
that returned; whether the relevant section was in the delivered text or only
reachable by a further read; whether output was truncated, paginated or cut by a
size limit; and whether access controls hid it. Permission to open a file is not
delivery. When these cannot be established, record the layer as unknown rather than
choosing the one that blames the reader.

**Wiki and source disagree.** First classify the wiki statement:

- a **confirmed rule** — an adopted product, access, privacy or release decision with
  an owner or decision record;
- a **description of implementation or runtime behavior**;
- a **proposal** not yet adopted.

Then investigate. Source and runtime show what the system does; they do not approve
it. If a description is wrong, correct it against source and recheck restatements.
If source violates a confirmed rule, the defect is in the implementation: keep the
rule, record the observed violation with its evidence, and report it to the rule's
owner; do not rewrite the rule to match the leak. If a proposal is described as
current, mark it as proposed. If the authority of the statement is unclear, record
the conflict as unresolved and ask its owner instead of picking a side.

Several layers can fail at once; record each. Many misses are not "did not read the
wiki": the fact may live only in source, a wrong companion checkout may have been
selected, or a guessed path may have been used instead of the index. Name who
corrected the miss and whether the retry was informed; an informed recovery is not
an independent success.

## 5. When structure changes, migrate everything that depends on it

A split, move, rename, merge or archive changes more than the page. Before the change,
list and then verify:

- **Old entrances.** Every existing heading, anchor and path that readers, other pages,
  task records or external notes use still resolves, by redirect page, retained
  heading or explicit pointer. Verify with the actual reader's ID rules, not a guessed
  slug.
- **Single owner.** Which page now owns each moved fact; remove or convert copies.
- **Consumers and back-links.** Pages, task maps and indexes that link to the moved
  content; reverse source indexes and satellites.
- **Diagrams and their source blocks.** Nodes, edges and labels that reference the moved
  scope, with their diagram sources kept beside them.
- **Terms.** Glossary or term entries and their targets.
- **Assets.** Images and evidence files: paths relative to the new location, the file
  actually present, its digest matching the receipt, and the consumer able to display
  or serve it.
- **Generators and gates.** Native generators, parsers and checks that read the old
  structure; regenerate with the native command and confirm the parser adopted the
  new records rather than skipping them.
- **Semantic check.** Re-read the moved statements in their new context: conditions,
  exceptions and history still attached to the right claim.

If the project's generated indexes are owned by another role, hand them the list; do
not hand-edit generated output.

## 6. Keep current state and historical evidence apart

Logs, run receipts and past checkpoints are evidence about a time and revision, not
current rules. When adding evidence, keep it beside the claim with its identity. When
the current state changes, edit the single current statement and mark older ones as
history pointing to it, following the one-authoritative-checkpoint rule in
[maintenance](maintenance.md#ci-and-ownership). A newer passing run does
not explain an older failure, and a failed run does not invalidate a later verified
artifact. Do not promote an observation from one environment, profile or audience to
others.

### When planning, Wiki editing and implementation have different owners

Use this optional handoff when the task deliberately separates those roles; a
single worker can keep the same transitions without extra delegation. Preserve the
planner's original proposal. The Wiki owner records the reviewed contract and
acceptance boundaries in the existing owning section or task, explicitly as
accepted but not implemented, alongside the observed current behavior.

Return that reviewed section to the implementer with the source/peer identities,
changed constraints and file ownership. Confirm what was actually read; a hash
identifies bytes but does not prove adoption. Late reading remains late reading.
If source discovery changes the contract, return the specific difference to its
owner before implementing a conflicting interpretation. After independent checks,
the Wiki owner promotes only evidenced behavior to current candidate state, names
remaining boundaries, and preserves the earlier proposal as history. Source,
artifact and deployed state remain separate. Do not create a second specification
registry or impose this division on routine work.

## 7. Keep the per-task record light

Use the project's existing task record and its required sections; add no new
manifest. A task that changes no knowledge records a short no-change reason where
the project asks for one. For tasks that change knowledge, four short entries
suffice:

1. **Fact and structure decisions** — outcome of judgements A and B in section 2
   (including "no structural change") and why.
2. **Reading closure** — what the change alters, derived items with dispositions,
   and where tracing stopped (section 1).
3. **Change return** — what changed in the wiki, including diagrams, terms, assets and
   links, and what was checked and found not to need change, with the reason.
4. **Coverage and efficiency** — what was read and missed, corrections received and by
   whom, which miss layers occurred (section 4), and what remains unmeasured. Report
   bytes or counts only from actual tool output; do not estimate effort or tokens.

## 8. Limits

This is guidance. It cannot detect by itself that required reading was skipped, that
a placement decision was wrong, that a conflict was resolved in the wrong direction,
or that a migrated entrance broke. Native gates,
navigation trials with the original failing query, consumer checks and independent
review provide that evidence. A structurally green wiki is not a semantically correct
one, and a task record that lists closure is not proof of reading.
