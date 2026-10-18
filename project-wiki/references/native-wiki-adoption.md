# Audit an established wiki without building a parallel truth system

An existing wiki can already have stronger domain coverage than this skill's
fixture: responsibility chapters, diagrams, producer/consumer tables, a reverse
source index, cross-repository contracts and change-touch gates. Keep those assets.
`routes.json` is the bundled helper's input format, not a prerequisite for a useful
wiki. Without that manifest, report the native audit results; do not call the wiki
invalid merely because `wiki.py` cannot ingest it. An adapter is a separate design
choice and must reuse native metadata rather than introduce hand-maintained copies.

## Recover the actual review baseline

Before taking over interrupted work, compare working tree, local commits, remote
branch, worktrees and durable handoff. A clean main checkout can coexist with a
complete uncommitted review in another worktree. For each changed page compare
base, current main and review output; preserve overlapping edits and already-merged
work. Record recovered edits separately from claims independently rechecked now.
Do not inherit an earlier reviewer's stamp as evidence of your own semantic audit.

## Verify a claim through its whole chain

Choose representative questions before reading implementation. Draft the plan
from the native entry and relevant pages, record missing facts, then inspect code.
Use a compact claim ledger:

| Question | Evidence to inspect | Common false positive |
|---|---|---|
| Does this state actually occur? | Declaration, reachable writer, caller, consumer and guards | State exists only in a union or constant set |
| Does this reminder ever appear? | Producer field, serializer/storage, consumer query and display | Reader uses a column while writer only fills metadata |
| Does this setting change behavior? | Write target and the rule's real downstream read | Admin updates a cache the decision never reads |
| Is this privacy rule active? | Application projection, direct access grants, migration ledger, deployed revision | A rolled-back dry run described as production enforcement |
| Does every caller behave alike? | Return/throw/catch boundaries, bypasses and deliberate exceptions | Matching function name treated as equivalent behavior |
| Will this tool survive packaging? | Import closure, build exclusions and real build context | Local type-check succeeds because omitted files exist locally |

Record individual source-backed findings, not a single confidence percentage.
Separate proposed, written, tested, built, deployed and observed. An older live
observation remains tied to its older revision; neither a review date nor a source
hash upgrades it. Direct database grants and app projection are separate controls.

## Learn from native strengths

- Producer/consumer matrices expose features with no write path or no client.
- Reverse source-to-page indexes reveal affected diagrams; they do not enumerate
  every behavioral dependency. Related-page top-N results are explicitly truncated.
- Change-touch gates can require a changed page or a concrete reviewed-no-change
  reason. They prove review acknowledgement, not that the prose is true.
- Coverage ratchets can count unmentioned routes/tables/registries. A name appearing
  in prose is mention coverage; it is not semantic coverage or an acceptance test.
- Multi-repo wikis need explicit repository aliases and separate skip reporting.
  A missing sibling checkout is NOT RUN, even if the native gate exits zero.
- Exact declaration resolution and useful local interaction contracts can improve
  native substring checks, but do not replace an existing source index by default.

Report four separate outcomes: native structural checks, navigation trials,
source-reviewed claims and runtime observations. Distinguish carried-forward
review work from fresh sampling. Keep safety and workflow rules already authorized
by the project; do not turn a generic preference for light process into authority
to erase a founder's existing review requirements.

For a concrete application and remaining limits, see the repository's
`evals/reports/soulnest-native-audit.md`.

## Verify the reading surface

When a wiki has a generated reading site, identify the serving process/repository,
build input and page revision before concluding that edits reach the reader. A Git
Markdown file and a local or hosted wiki may be projections of one source or divergent
copies; verify which. After a relevant update, inspect a changed rendered page,
diagram and source-view link. Record stale server/build state separately from wrong
content; successful parsing or indexing alone does not prove the displayed revision.
If source-view pages depend on a provenance registry, check that the exact path is
registered in a parser-recognized source section. A valid filesystem or Markdown
link alone does not establish that the reading site has generated that source page.

For paired worktrees, bind the reader, source validator and test runner to the same
explicit companion checkout. A convenient sibling-directory default can silently
show main while documenting a candidate branch. Record both revisions, use the
native checkout override if available, and test an added companion-source link;
do not modify the canonical checkout merely to make documentation tests pass.

Verify the generated link closure as well: every emitted source-view URL must
have a generated destination. Ordinary body/fact-source links may need reader
pages even when they are not architecture dependencies; generating their views
must not silently add them to the impact registry. Detect provenance-shaped
entries accidentally placed in unrelated sections before they vanish from the
native parser. Keep prose references and fenced examples distinguishable from
actual registration. A passing file-existence check does not cover these cases.

An explicitly declared fact-source header is different from an ordinary body link:
it states authority for the page and should participate in the same native impact
model even without a duplicated symbol entry. Test a real contract edit against
its feature page; a viewer page alone does not establish that dependency.

If agents bypass the wiki, first investigate its task-facing cost: guessed search
terms, competing entrances, long rule preambles, late impact reports, incomplete
satellites, broken reader links or prose that confuses a target with implemented
behavior. Improve the useful default path and test it before prescribing more
attestations. Preserve authorized project requirements; the improvement is to
make them executable and informative, not to remove truthful review.

An engineering reader can expose source text as well as prose. Record its actual
listener addresses, SSH or proxy path, authentication boundary and exported-file
policy; a localhost URL, noindex or a product's admin session alone establishes
none of the other controls. Check runtime proxy/tunnel routes separately from
repository configuration. Export only intended, version-controlled sources within
the selected checkouts, resolving symlinks and excluding credential paths; being
tracked is not proof that a file contains no secrets. Exercise wrong Host/Origin,
write methods and traversal alongside normal reading. Use metadata-only process
and configuration probes: raw arguments, environment dumps and connector logs may
contain credentials. A test passing through an outer 403 does not establish the
origin's authorization behavior.
