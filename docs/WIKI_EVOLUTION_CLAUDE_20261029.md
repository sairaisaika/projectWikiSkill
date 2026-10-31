---
type: Plan
owner: Claude (original iOS C285 owner context)
base: 3276f7182ef04e7d1297ebb0a08696b96cd09731
---
# Wiki evolution guide — Claude plan and result

## Prior real dispatch record used as reference (not new history)

Product workspace task record for the iOS simulator QA continuation, repository-relative
`.context/work/active/20261028-ios-simulator-qa-c285.md` in the mobile checkout, with its Web pointer
`.context/work/active/20261029-ios-main-qa-wiki.md`. Input method: Root sends a dispatch message (scope,
allowed paths, forbidden actions, evidence locations) and writes its own "Wiki start / plan" section in
the task file; the owner appends "Wiki start → plan → execution → evidence → Wiki end / coverage /
efficiency" sections to the same file before and after editing, and returns a chat report with file
hashes. Return method: Root performs independent review, generation, PROJECT and Git. Several rounds
in that record were independent corrections (overclaimed wording, misattributed gaps); they are
evidence for this guide, not a template to copy verbatim.

## Wiki start (what was actually read)

- `PROJECT.md` (2087 B; current task line from the uncommitted Root diff), this plan's parent
  `docs/WIKI_EVOLUTION_PIPELINE_PLAN_20261029.md` (2620 B). No `CONTEXT.md` exists; none created.
- Formal `project-wiki/SKILL.md` (15455 B) and references `maintenance.md` (15030 B), `page-anatomy.md`
  (6119 B), `change-navigation.md` (10335 B), `native-wiki-adoption.md` (13433 B), all read in full.
- Already covered there, therefore **not** rewritten: change trigger table, delegated-work context and
  return comparison, one authoritative current checkpoint (maintenance); responsibility hierarchy,
  chapter/diagram sources, interaction table (page anatomy); first task read, per-file satellites, task
  maps, variants (change navigation); native parser adoption, terminology routes, reader link closure,
  source identity (native adoption); feature completeness and producer/consumer views (via SKILL).
- Missing: a decision procedure for **where knowledge belongs** (update / section / split / new page /
  new chapter / shared concept / archive / no structural change), **required-reading closure** derived
  from the task rather than from registered links, a **miss-diagnosis taxonomy** that selects the
  layer to repair, and a **structural-change migration checklist**.

## Evidence located with bounded searches (de-duplicated incidents)

1. Overview diagram stated an unconditional "app pulls OTA" edge; a variant build with updates
   disabled made it wrong. Found by satellite review, not by a broken link. Class: shared rule placed
   in an overview without its scope (granularity), not "did not read".
2. Reader heading IDs kept full-width parentheses; authored links assumed another slug. Class:
   projection/consumer not used for verification.
3. Evidence JSON referenced a screenshot that was never copied with it; the helper refused capture with
   a selection ordinal; a human mapped the ordinal to the file and copied the original. Later the reader
   rendered image syntax as a link (no image element). Classes: asset handoff omission; consumer
   capability gap; and an owner claim ("inline image") that assumed rendering without checking the
   consumer.
4. A shared rule ("booking gate is not partitioned") remained in two overview pages after the
   implementation and design ledger changed. Class: duplicated statements of one rule, no single owner.
5. A first fix plan asserted an invariant (an owner always has the same account flag) and a scope
   limit (a step is not in scope) without checking the identity-degradation path and real callers.
   Class: required-reading closure from invariants and producer/consumer not derived; the Wiki did not
   hold the fact — not a "did not read the Wiki" miss.
6. A companion checkout for source verification was wrong, producing false failures. Class: input /
   peer identity (helper/route input), not missing knowledge.
7. File names guessed from page numbers. Class: retrieval — native index not used.
8. A worker reported a boundary row as missing although the page already had it. Class: the agent had
   access and did not adopt (partial section read).

Counted once each even where one incident produced several counterexamples. Hook delivery is listed as
a class in the guide without claiming an observed incident here.

## Plan (before editing)

1. Create `project-wiki/references/wiki-evolution.md`: placement decision (with "no structural change"
   as a normal outcome), shared-rule vs feature-mechanism granularity with preserved legal exceptions,
   required-reading closure sources, miss taxonomy → repair layer, structural-change migration
   checklist, current vs historical evidence, lightweight per-task record in the existing task file.
   Generic wording only; no product rules, private paths or quotas; criteria instead of thresholds.
2. `maintenance.md`: add one inbound link at the trigger table and avoid restating the guide.
3. Self-check: link targets exist and anchors resolve; scope confined to the three allowed files;
   produce discriminating cases for Root (input → expected decision class, how to observe) without
   fixed-text assertions.
4. Record result, coverage and efficiency below. No SKILL/README/PROJECT/version/code/test changes, no
   product repository edits, no commit/push.

## Result

- New `project-wiki/references/wiki-evolution.md` (12 KB, blob d6464c04): §1 required-reading closure
  derived from capabilities / invariants / producers-consumers / identity-state-environment axes /
  shared rules / emitted assets-terms-links; §2 ordered placement questions ending in update, evidence
  beside claim, in-place edit with history, variant in mechanism section, feature entrance, shared
  concept, chapter, archive — with "no structural change" as a stated normal outcome and qualitative
  indicators instead of thresholds; §3 shared rule vs feature mechanism, overview restatements, legal
  exceptions preserved; §4 miss taxonomy → repair layer (rule absent, linking/granularity,
  retrieval/projection, delivery incl. hook/helper/peer, adoption, consumer capability, staleness);
  §5 structural migration checklist (old entrances via the reader's real IDs, single owner, back-links,
  diagrams + sources, terms, assets with digest and consumer, generators/parsers, semantic re-read);
  §6 current vs history (points to maintenance's single-checkpoint rule instead of restating it);
  §7 four-entry light task record in the existing task file; §8 limits.
- `maintenance.md` (blob 03ed6db0): one paragraph after the trigger table linking the guide; no
  existing text removed or reworded.
- Not changed: SKILL, README, PROJECT, plugin version, code, tests, any product repository.
  (`SKILL.md` and `PROJECT.md` show uncommitted Root edits in this worktree; not touched here.)

### Observed failure → guide section (not all are "did not read the wiki")

| Incident (de-duplicated) | Layer | Guide |
|---|---|---|
| Overview diagram edge unconditional, false for a variant | Linking/granularity of a shared rule | §3 overview restatements; §2 q3/q6 |
| Authored anchor slug differs from reader IDs | Consumer/projection verification | §5 old entrances via reader IDs; §4 consumer capability |
| Evidence JSON referenced an un-copied image; reader then rendered the image as a link; owner had claimed an inline image | Delivery (asset handoff) + consumer capability + adoption (claim without consumer check) | §4 rows delivery / consumer / adoption; §5 assets |
| One rule restated in two overview pages, stale after redesign | Duplicated shared rule, no single owner | §3; §2 q6; §6 |
| Plan asserted an invariant and scope limit without degraded-identity path and callers | Required-reading closure (fact lived in source, not wiki) | §1 invariants, producers/consumers |
| Wrong companion checkout → false failures | Delivery / helper input | §4 delivery row |
| File names guessed from page numbers | Retrieval (index not used) | §1 last paragraph; §4 retrieval |
| Existing boundary row reported missing | Adoption (partial read) | §4 adoption row |

## Self-check

- Scope: only the three allowed paths changed by me (`git status` also shows Root's SKILL/PROJECT/plan
  edits). Six relative links and one anchor (`maintenance.md#ci-and-ownership`) resolve against file
  headings. Privacy grep of the guide for product names / home paths: 0 hits.
- `python3 -m unittest discover -s tests`: 239 tests OK (1 skipped); package-specific
  `test_skill_package`, `test_package_newlines`, `test_package_integrity`, `test_plugin_package`
  each OK. Logs: `/tmp/wiki-evolution-*.log`. A first invocation as `tests.<module>` failed with
  import errors (wrong invocation, tests is not a package) and was rerun with the project's discover
  command.
- The tests check package links/newlines; they do **not** test whether an agent applies the guide.

## Discriminating cases for Root (observe decisions, not wording)

Give a fresh worker the guide, the task and the relevant wiki checkout only. Compare its recorded
**decision class and repair layer**, and the actual diff, to the expected column. Do not grep for
sentences from the guide.

| # | Input situation | Expected decision / layer | Observable |
|---|---|---|---|
| 1 | Acceptance rerun with the same result as recorded | No wiki change; evidence in task record | No wiki page in diff; reason recorded |
| 2 | New build variant makes an overview diagram edge false | Qualify or remove at overview, link owner; edit owner once | Overview edge carries condition or is gone; one owner statement; no conflicting copy found by search |
| 3 | Evidence receipt names an asset absent from the checkout | Delivery miss; copy original with digest; check consumer | Digest equals receipt; reader output inspected (image shown or gap recorded at reader owner) |
| 4 | Worker claims a page lacks a rule that it already states | Adoption miss; no new text | No duplicate rule added; record classifies adoption |
| 5 | Fix relies on "owner always has same flag" | Closure must include identity resolver and callers before planning | Task record closure lists them before the plan |
| 6 | Source checks fail against a mismatched companion checkout | Delivery/input; fix selection | No page edit; revisions recorded |
| 7 | Same rule stated in two overview pages, both stale | Shared concept, single owner, copies → links + history note | One owner; other pages link; dated history kept |
| 8 | New internal build profile under an existing release feature | Section in existing feature, not new page | Diff adds section; no new page; entry links unchanged |
| 9 | Heading renamed during a split | Migration: old entrance kept, reader IDs verified | Old anchor resolves in generated reader output |
| 10 | Shared access rule with an administrator exemption | Exception kept and named at owner | Exemption still present; feature page links rather than restates |

These are forward tests; this document does not claim they pass.

## Wiki coverage

- Read in full: PROJECT, pipeline plan, SKILL, maintenance, page-anatomy, change-navigation,
  native-wiki-adoption. Not read: diagram-framework, feature-completeness, producer-consumer-views,
  route-contract, quality-model, learning-and-orientation, engineering-depth,
  systematic-design-review, collaboration-workflow (only the selected-evidence section was read in an
  earlier task) — the guide links only to the four read references and does not restate the others.
- Evidence records: bounded grep of the two product task records (18779 B Web record: lines on OTA,
  anchors, image/reader; booking record: lines on guessed paths, peer, plan rework, read-only and
  corrections), plus the selected-evidence eval's headings only (10188 B, conclusions not re-read).
- No CONTEXT.md exists; none created.

## Usage efficiency review

- Hits: the four named references already contained most adjacent rules; reading them first prevented
  rewriting triggers, satellites, checkpoints and reader closure.
- Misses / context: no dedicated placement or miss-diagnosis guidance existed; evidence required
  reading two long task records by bounded search (not full reads). Several incidents in those records
  were my own earlier mistakes (overclaimed inline image, reported-missing existing row), included as
  adoption-layer evidence.
- Rework: one test invocation error (module path) corrected; no guide rewrite.
- Unmeasured: tokens, time, and whether a worker using the guide makes better decisions — that needs
  Root's forward cases.

## Raw sources

- Web task record (product workspace), mobile C285 task record, booking precheck task record (product
  workspace); evaluation `evals/reports/evidence-selection-diagnostics-20261029.md` (headings only).
- Test logs `/tmp/wiki-evolution-*.log` (local, not committed).

## Unresolved

- A guide cannot block a skipped closure, a wrong placement or a broken migrated entrance; native gates,
  original-query navigation trials, consumer checks and independent review must show that.
- Hook-delivery misses are described as a class; no incident from these records was attributed to a
  hook.
- Root owns SKILL entry wiring, evaluation and PROJECT; no commit/push here.

## Review round 1 — rejected; counterexamples and rework plan (before editing)

Reviewed snapshot: guide SHA-256 `045eaf5c4514329f5076bd2f50a454ce837a74e2d44719b2b5caac6f0ae57f31`
(re-hashed locally before rework: same). The "Result" above describes that rejected draft and is kept
as history; the current state is the section after this one.

Counterexamples accepted:

1. §2 "stop at the first answer": three pages drifting on one rule need their current sentence edited,
   so question 3 fires first and question 6 (shared owner) is never reached. Ordering is not the fix:
   the fact handling (current / history / evidence) and the structural review (owner, grain, entrances)
   are two separate decisions, and the first must not skip the second.
2. §4 "Staleness → correct against source": when a confirmed access invariant forbids cross-partition
   links and source lacks the gate, rewriting the wiki to match source documents a leak as policy.
   Source shows behavior, it does not approve it. Conflicts must first separate confirmed product rule,
   actual implementation / runtime, and unadopted proposal, then be investigated.
3. §4 adoption row "received or could have opened it": readable permissions with a query that missed,
   or a truncated packet, would be misfiled as adoption. Check the right revision, real entry, whether
   the relevant section was delivered, truncation and limits; unknown stays unknown; read permission is
   not effective delivery.
4. §1 "every caller and indirect reader" has no causal stop; a diagnostics-only change could expand to
   the whole site, contradicting change-navigation's "do not recursively expand all common
   infrastructure". Trace by affected field / predicate / state / error meaning; stop with a stated
   reason when the contract is unchanged and there is no causal effect; a complete candidate satellite
   inventory does not mean reading every page in full, and candidates are not silently dropped.

Consistency fixes accepted:

- Intro "Ordinary edits that change no knowledge need none of this" can be read as exempting a
  project's own per-task wiki start / end / efficiency requirement. Replace: those requirements still
  apply; a short no-change reason satisfies them; this guide's proportionality never overrides them.
- Evidence counting: "eight de-duplicated incidents" is not supported by eight independent original
  records (some items are one task's several corrections; the wrong-peer item is only referenced as an
  earlier occurrence). Re-present as observed categories with record pointers, no incident count, and
  no frequency claims.

Out of scope (owned elsewhere): the project protocol conflict "not found = hole → add page first" vs
"on conflict always change the wiki" (another owner, separate Web worktree); README '#使用' link check
failure (Root). Not touched.

Plan:

1. §2 → two judgements: (A) fact handling: no change / evidence beside claim / edit current statement
   with history; (B) structural review, always run after A when A changes knowledge: does a shared rule
   need one owner, is the grain right (variant section, feature entrance, chapter), do entrances or
   archives need migration; "no structural change" recorded with reason. Neither short-circuits the other.
2. §4 → replace "Staleness" with "Wiki and source disagree": classify the wiki statement (confirmed rule
   / description of implementation / proposal) with its authority, investigate; source wins only for
   descriptions of behavior; a confirmed rule violated by source is a defect to report to its owner, not
   a wiki edit; unresolved stays a recorded conflict.
3. §4 → split delivery vs adoption with verification steps; adoption only when the right revision and
   the relevant section were demonstrably delivered or opened; otherwise delivery / retrieval / unknown.
4. §1 → causal tracing by changed field, predicate, state, error meaning; explicit stop rule; candidate
   inventory kept and dispositioned (read / skimmed / stopped with reason), not deleted.
5. Intro and §7 → project per-task requirements apply; short no-change reason.
6. Record → replace incident count with observed categories and pointers.
7. Walk-through of the four counterexamples plus a no-structural-change negative control against the
   revised text, recording the actual step-by-step outcome; rerun link and package tests.

## Current result (after review round 1) — supersedes "Result" above

Changes (only the three allowed files):

- Guide: intro states project per-task wiki requirements still apply (short no-change reason); §1
  causal tracing by changed field / predicate / state / error meaning / artifact, explicit stop rule,
  link to change-navigation's no-recursive-infrastructure rule, candidate inventory kept with
  dispositions; §2 split into **A. Handle the fact** and **B. Review the structure** (owner / grain /
  entrances), B mandatory whenever A changes a current statement; §4 delivery vs adoption with required
  evidence and "unknown" fallback, staleness row replaced by **wiki and source disagree** (confirmed
  rule / implementation description / proposal; source shows, does not approve); §7 and §8 aligned.
- maintenance.md: the existing inbound sentence now also names the wiki/source-conflict guidance.
  Observed, not changed: its example entry text says "Source wins over stale prose"; read as applying
  to descriptions it is consistent with the guide, but Root may want to qualify it for confirmed rules.

### Walk-through against the revised text (author's own trial, not an independent pass)

Each case was applied to the current guide text step by step by me, the author. This shows the text no
longer produces the rejected outcome; it does not show that an independent worker will follow it.

1. **Three pages drift on one rule.** §1 shared-rules row → read owner page and restatements (three
   found). §2 A1: changes conclusions → continue. A2: not evidence. A3: edit the current statement,
   keep history, list the three restatements, check kind via §4 (confirmed rule, unchanged authority).
   A changed a current statement → **B runs**. B Owner: stated in three places and copies disagree →
   one owner; the other two link with local condition. Result: shared-concept decision reached; the old
   "stop at A3" outcome no longer possible.
2. **Confirmed partition invariant, source lacks the gate.** §4 last row → classify: confirmed access
   rule with owner. Investigate: source allows cross-partition link. Rule "source violates a confirmed
   rule" → keep the rule, record violation with evidence, report to owner. A3 says a confirmed rule is
   not corrected merely because source differs. Result: wiki not rewritten to allow the leak.
3. **Readable page, query missed / packet truncated.** §4 delivery-vs-adoption checklist: revision?
   query result? section in delivered text? truncated? Query returned another page → retrieval;
   packet cut before the section → delivery; neither establishable → unknown. Adoption requires the
   relevant section of the right revision demonstrably delivered or opened. Result: not filed as
   adoption.
4. **Diagnostics-only change in a widely used helper.** §1: name what changes — log text only; no
   status, field, error or error meaning changes. Trace consumers of log output (the log reader only);
   other callers use an unchanged contract → stop with that reason; satellites listed with disposition
   "checked, unaffected: contract unchanged" rather than full reads or deletion. Result: no site-wide
   expansion; inventory preserved.
5. **Negative control — acceptance rerun with same result.** A1: no reader conclusion changes → no wiki
   change, reason recorded, B skipped. Intro: project still requires its wiki start/end note → short
   no-change reason. Result: no wiki diff, no exemption from project requirement.

Second negative control (structure): a new internal build profile under an existing release feature,
stated nowhere else. A3 adds the statement → B: Owner — single place; Grain — variant of an existing
mechanism → its section; Entrances — none moved → **no structural change**, recorded with reason.

### Evidence, re-presented as observed categories (no incident count)

Earlier "eight incidents" withdrawn: several items are corrections within one task, and one is only
referenced as an earlier occurrence. Categories with original pointers (product workspace,
repository-relative task records; line numbers at time of reading):

| Category observed | Original pointer | Note |
|---|---|---|
| Overview edge without variant condition | Web QA wiki record L42–L51 | Found by satellite review |
| Authored fragment vs reader heading ID | same record L55 | Projection / consumer |
| Missing evidence asset, ordinal-only refusal, reader shows image as link | same record L59–L80 | One chain, several layers |
| Owner claimed an embedded image without checking the consumer | mobile C285 record L220 vs Web record L80 | Same chain as above, not separate |
| Plan asserted invariant / scope without degraded identity and real callers | booking precheck record L57–L58, L114, L173 | One task, two reasoning gaps |
| Guessed file names; truncated batch reads | booking precheck record L174 | Retrieval; truncation was self-reported |
| Wrong companion source | booking precheck record L112, L130, L172 | Only referenced as an earlier occurrence; original not re-read here |
| Existing boundary row first described as a gap | mobile C285 record L277 | Recorded with correction in the same entry |
| Hook delivery | — | Category only; nothing observed |

These support the categories in §4; they are not frequencies and not independent of each other.

### Checks (this round)

- Guide SHA-256 `b026d21bb875bcd4b2bed12ee921d5a005b7cda597fac6df8e4cd3e8c50b2fc0`; maintenance SHA-256 `df04bebb66c895c111845cde4f921ff14720903b37d19cdca14d162db5dd2779`.
- Links: 7 relative links, 2 anchors (`change-navigation.md#make-the-first-wiki-read-useful`,
  `maintenance.md#ci-and-ownership`) resolve. Privacy grep: 0 hits.
- Package tests rerun: test_skill_package, test_package_newlines, test_package_integrity,
  test_plugin_package — all OK (`/tmp/wiki-evolution-r1-*.log`). Full suite not rerun (text-only
  change; earlier 239 OK / 1 skipped applies to the previous draft).

### Coverage and efficiency (this round)

- Read: review counterexamples; change-navigation first-read section (L1–L36) to cite the stop rule;
  bounded greps of three original records to replace the incident count with pointers.
- Rework cause: my draft let one decision short-circuit another and treated reachability as causality
  and permission as delivery — the same class of reasoning gap the guide describes.
- Unmeasured: tokens, time; whether a fresh worker reaches the same outcomes.

### Unresolved

- Guidance cannot prove a miss is blocked; Root's forward trial with a fresh worker is the evidence.
- Project protocol conflict ("not found = add page" vs "conflict = change wiki") is owned by another
  owner; the guide's conflict rule is generic and does not resolve that project's text.
- No commit / push.
