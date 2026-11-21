# Destination visibility and publication scope — 2026-11-20

Baseline: main `32836274c9fb296e6ce38300b6cab8fb495ea80a` after PR74.
The prior checkout was unavailable; work used a fresh isolated temporary clone.
The connected account and destination repository metadata were read explicitly:
account `sairaisaika`, repository `sairaisaika/projectWikiSkill` (id 1420071963),
visibility public, read/write permission available. This observation supports only
this task's named destination and date; it is not inferred from the clone URL.

## Method and scope

The one [owning hygiene method](../../project-wiki/references/repository-hygiene.md#visibility-and-publication-scope)
now applies visibility and audience checks before creation, after generation,
before staging, before commit and immediately before publication. Public/private
AGENTS/PROJECT/PRODUCT templates share that method: public-safe bodies, authorized
shared internal decisions, no secret/customer content and no automatic moves or
claim that private visibility repairs history. Existing Wiki
entries and the new-Wiki boundary link the same table. No scanner, executable
policy checker, second registry, hook or visibility/ignore/security setting change.

Public material needs explicit disclosure approval. Private/internal can hold
business-authorized internal Wiki content only for matching actual audiences;
internal is not assumed to be personal/private. Unknown destinations receive
public preparation restrictions and block publication. Multiple targets, forks and
PR/diff, attachments, logs, CI artifacts or release surfaces must each satisfy the
strictest applicable content limit. Credentials, raw personal/user data, private
logs and backups remain outside the repository workflow regardless of visibility.
Ignore, retention and authorization remain separate; tracked files stay tracked.

## Synthetic acceptance

The original eight focused tests initially fail against the prior method, then pass after the
visibility section and routes are added. The suite uses invented public metadata
and disposable real Git repositories, never remote writes or real sensitive data.

| Exercise | Observed control |
|---|---|
| Four checkpoints and Wiki discovery | Each checkpoint names destination/visibility; new Wiki template and existing native path reach the one table; English/Chinese queries select the existing hygiene route |
| public/private/internal/unknown | Synthetic metadata binds to the four authored rows; public disclosure approval, business authorization/actual audience and unknown publication block remain explicit |
| Missing/denied/mismatched evidence | Empty/denied response, URL or clone success, wrong account/repository, missing id/permissions and unknown visibility use unknown; a repository without configured publication target does not invent origin |
| Actual push destination | Real Git resolves branch pushRemote, pushDefault and explicit remote precedence; pushInsteadOf rewrite is honored without contacting a remote |
| Multiple destinations and fork/PR | Multiple real push URLs are retained; synthetic private source and public upstream require the public row, not source visibility alone |
| Changes require new evidence | Changing a real push URL invalidates the old private repository observation; fresh public metadata binds the new target; unverified account remains unknown |
| Wider release audience | Synthetic public release destination from private source requires public approval; all publication surfaces and invariant sensitive-data exclusions are present |
| New setup scaffolds | All three filenames can be tracked; public/unknown choose public-safe template bodies, private/internal choose the shared authorized bodies; no filename-based ban |
| Existing scaffold conflict | Synthetic existing internal decisions remain unchanged, tracked and at the same HEAD/index even after public/private metadata review; ignore rules are not changed by the review |
| Same repository, different publication refs | One authorized source→target branch passes the synthetic review record; wrong source/target branch, extra branch/tag, unresolved expansion, mirror action, unreviewed history and changed target policy fail despite identical public repository metadata. No parser or publication is executed |
| Tracking is independent | A tracked synthetic file remains indexed and unchanged for all four metadata classes even when matching ignore |

The metadata binder in the tests is a test-only interpretation of the documented
identity/account preconditions, not shipped enforcement or a live-provider access
validation. Prose/route assertions and Git semantics do not demonstrate natural
agent adoption, automatic detection of sensitive content, real audience membership
or publication authorization. Those remain task-specific human/agent review.

The first full run found two same-page links incompatible with this repository's
package link checker. They now use explicit `repository-hygiene.md#...` paths;
the checker was not changed or bypassed.

Independent review then identified missing publication ref/history scope. The
method now confirms the authorized action, exact source/target refs including PR
branches, every exposed branch/tag and relevant history, and refuses implicit or
unresolved expansion. Literal URL targets remain URLs rather than remote names.
One synthetic regression covers approved versus wrong/extra refs and stale action,
history or policy evidence; it adds no runtime Git parser or publication call.

## Validation closure

Local environment: Linux, Python 3.12.14 and Git 2.56.1.

- Focused hygiene/visibility suites: 23/23 (12 retained hygiene and 11 visibility/scaffold/ref-scope).
- Full suite: 492 collected, 491 passed, one existing Windows-junction skip.
- Fixture contracts: 12/12 passed.
- Fixture and maintainer Wiki checks: ready, no drift; 9 and 11 routes respectively.
- Fixture routing: 24/24 known queries top-1/top-2, 4/4 unknown controls rejected;
  compound task-map case passes and saved reports still equal live output.
- Default, legacy-hook and portable-hook package/source doctor: package valid and
  source/support/input-byte/identity checks pass; all outputs were temporary.
- Diff whitespace check clean; no changes to ignore, hooks, workflow/security
  configuration, plugin version or downstream repositories.

The destination identity, public visibility and connected account were checked
again before committing/publication. Remote exact-head CI and independent review
are pending. No release, installation, merge or consumer-project
changes are part of this work.
