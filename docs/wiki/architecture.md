# Architecture

> Reviewed: 2026-11-17; saved current-section view in task-views only. 2026-11-16: narrow packet text, capture record text, qualified history boundaries and text_page line-boundary parts in task-views/bounded continuation only; other sections retain their earlier review scope.

These are module contracts read from code. All scripts use only the standard library.
The CLIs primarily print JSON; `wiki.py list`, non-JSON queries and the new
workflow preparation/reading views print text by default. Reported errors normally
exit 1; missing helper format exits 2 with adoption guidance. The two hooks exit 0 on their own errors once loaded (see their
summaries). Rationale and dated evidence live in
[collaboration-workflow.md](../../project-wiki/references/collaboration-workflow.md) and
[evals/reports](../../evals/reports/README.md). Start at [engineering-entry.md](engineering-entry.md).

## wiki-helper

`project-wiki/scripts/wiki.py` validates and navigates a project's route manifest.

- **CLI**: `query|task|list|audit|build|check|evaluate`. Missing this helper’s manifest returns actionable adoption guidance and exit 2, without invoking a native router or creating a manifest. A malformed existing manifest still fails. Every command takes `--root PATH` (default: cwd). `query QUESTION [--limit {1..5}] [--json]` (limit defaults to 2). `task [TASK_ID]`. `evaluate --tasks PATH`.
- **Inputs**: `<root>/docs/wiki/routes.json` (`schema_version` 1 or 2; see [route-contract.md](../../project-wiki/references/route-contract.md)) and the source files and Markdown anchors it references.
- **Outputs**: `build` writes `docs/wiki/route-index.json` and `route-index.md`. `build` and `check` print the audit report and exit 1 when the audit is not ready (nothing is written). Otherwise `check` reports `snapshot_stale` and exits 1 when the index is stale. `audit` exits 1 when not ready. `query` exits 1 when a hit carries a warning. `evaluate` exits 1 below its thresholds.
- **Never**: executes recorded commands or project code, or writes any file except through `build`.

## File-first preparation and state reading

`workflow.py prepare` reuses the native `capture` validation and stores a
`prepared_reading` projection plus integrity digest. There is no new gate or
manifest: every requested file keeps all native owners and all omissions remain
explicit. `prepare` needs the original execution opt-in. Without files it saves the
native query (`query --json --files` with no paths, `impact: []`) so matched cards
and omissions are read through the bounded summary; its index prints that file owners
are unknown, not none. A later file-scoped request is a different request (new output,
one more native run); it is not merged into the query-only capture.
It records tracked/untracked selected changes without attributing authorship or
claiming pre-edit reading. New captures are transport-budget bounded. An identical prepare request may reuse its current existing output without native execution or rewriting; different/stale artifacts remain immutable. Other capture/packet outputs remain write-new-only.

A selected `.md` file under the configured Wiki root is saved as a reading page
without changing the native source-owner inventory. `prepared_reading.selected_wiki_pages`
records its source-relative file, Wiki-relative page and captured/missing status;
the compact index labels these as direct selections, not owner declarations.
Explicit history presence is shown separately from older top-level note counts;
moving a note into history cannot make the index claim there is no history.
Missing planned pages remain explicit and are not created. Existing native pages
are deduplicated, and snapshot-only views still use only saved text. Paths outside
the selected Wiki root are not inferred to be Wiki pages.

`context_reading.py` separates authored current-state sections, the first listed
verification note, older notes and explicit history. Ambiguous body qualifiers
are review candidates, never auto-promoted from Git ancestry. Explicit `Verification history`, `Review history` and `核验历史` headings are
also historical sections. This is an exact heading convention, not a semantic
classifier: a current product feature with an identical heading would also move
to the history view. Give such a feature an unambiguous heading. A trailing
verification note under a final history section belongs to that history. Quoted verification notes inside explicit history remain
there and cannot become the latest top-level verification note. Product headings such as "History editor" remain body content. All captured body/history text is
preserved for explicit reading; snapshots do not reopen live pages or invoke Git.

`show --capture` defaults to the summary; impact/feature show one complete native
record, page shows saved authored body, history shows older material. Long CLI text views are continued within 4000 UTF-8 bytes and 40 stdout lines; the exact NEXT command is bound to saved text and preserves view/path/section/format/snapshot mode. Large sections and Unicode single lines remain reachable. CLI budgets include Windows text stdout newline expansion and regressions measure raw bytes; CLI renderers opt into early_continuation; programmatic defaults retain footer-only continuation and explicit small-byte-budget compatibility, including long CI runner paths. Explicit JSON export remains complete. New views also accept a work
packet through its existing saved context. Legacy captures without prepared
pages have no invented page view. Live selected-source drift is historical data,
not current context. Caller-declared revision observations are not production
or capability verification. See [the command](../../project-wiki/references/collaboration-workflow.md#file-first-preparation).

## Bounded continuation, reuse and authored-state updates

`context_reading.text_page` emits an explicit character range and COMPLETE/PARTIAL
status, within 6000 UTF-8 bytes and 60 lines by default for programmatic callers. Every CLI
text part (prepare, show, show-state, locator, section outline) uses `workflow.cli_budget`:
`context_reading.CLI_TEXT_BYTES` 4000 / `CLI_TEXT_LINES` 40 measured on stdout, including
print's newline and the prepare REUSED prefix. A partial part repeats its exact continuation on
line 2 (`NEXT PART:`) and at the end (`NEXT:`), so a caller keeping only the first lines
(observed: `| head -45`) still sees it; a caller clipping to one line can still lose it. CLI stdout explicitly uses UTF-8/LF so Windows newline translation does not inflate the wire budget. A digest-bound cursor resumes the exact
saved view; text changes or a different capture/view/path/section reject the cursor.
A partial part first takes the largest prefix within both budgets, then ends after the last
`\n` in that prefix when the prefix holds at least one complete nonempty line and the shorter
part still fits; the cut is recorded as the cursor offset, so concatenated parts and
offsets stay exact. This applies to every text view (it is the one pager, not a capture-only
seam). A single line that cannot fit with the required display metadata still continues mid-line at a character
boundary; whole records are not atomic, and a line budget can cost one line per part.
The printed command preserves snapshot-only mode and explicit text format. Shell
commands are quoted for POSIX or PowerShell on the running host; PowerShell quoting
doubles ASCII and typographic single quotes, which it also treats as delimiters. Scope is neither
silently clipped nor falsely called fully delivered; a cursor never certifies reading.
New prepared captures carry the additive text_display=bounded-v1 marker and
default to bounded text, including impact/feature/all. Older captures, raw native
captures and packet views retain default JSON for active clients; `--format text` bounds them too.
Explicit `--format json` is an unpaginated machine export, not a bounded display.

`prepare_request` binds root/query/selected files/native prefix/runtime inputs,
Wiki root, peers, observed refs, preserved artifacts and reader implementation.
Repeated prepare at the same output validates the request and current declared
inputs, selected-source baseline and observed refs, then reuses original bytes and
capture time without calling the native router. A valid hit returns a bounded
`locator` (scope counts, missing-input counts and an exact `show --view summary`
command), not another copy of the file/owner index. The complete summary and JSON
exports remain available; snapshot-only locators still make no currentness claim.
It never silently refreshes stale
or differently scoped evidence. This is reuse over a declared closure, not a cache
of the entire project or a check of external host task-stamp existence.

`update-state --capture --path --state-file --output [--apply]` previews an authored
current-section replacement and original/proposed hashes. `state_update` requires
the selected captured page still match its original bytes; unrelated code edits
are allowed at finish. `apply_state` atomically replaces that unchanged Markdown
page inside the selected Wiki root, preserving mode and refusing symlink targets.
Previous current sections and older verification lines are retained verbatim
in fenced history; one latest recorded note remains for native provenance readers.
Optional --verification supplies a new caller-authored single note and archives
the previous one, never inventing a verification from Git. Recognized current headings accept an optional ISO date in ASCII or full-width parentheses; the reader displays a dated declared heading without certifying its date or claims; undated page output stays unchanged. On changed-state rotation a dated heading loses its old date while its original dated heading/body are archived verbatim. Nondate qualifiers, historical sections and fenced examples are not promoted. Older saved unknown projections remain unknown until a new preparation. Undated current
headings and preamble/keyword metadata positions are retained; native section links
are checked separately. Existing history/body stay intact, repeated identical updates
are no-ops. ATX closing hashes/indentation are normalized consistently for projection,
section selection and rotation; fenced examples stay literal. The new state body
cannot inject top-level/history sections, temporal verification notes or an unclosed
code fence. These are local transform input checks, not completion gates.

Caller-authored state remains claims. The tool cannot infer business correctness,
deployment, rollout, or acceptance from source/Git. Applying is an optimistic byte
check in an owned isolated checkout, not a concurrent-writer lease. No background
updater, new registry or task gate is introduced. Regression and adoption evidence:
[reading-flow report](../../evals/reports/reading-flow-20261107.md).

## workflow-capture

`workflow.py capture` turns one native task-context report into a `native-wiki-capture`.

- **CLI**: `capture --root PATH --query TEXT --native-argv JSON --output NEW [--wiki-root PATH] [--files PATH ...]... [--runtime-input PATH]... [--allow-native-execution] [--peer ALIAS=CHECKOUT]... [--native-source-context JSON_POINTER] [--preserve-artifact ABS_PATH]...`. `--wiki-root` defaults to `docs/wiki`. Repeated `--files` groups accumulate.
- **Behavior**: refuses to run without `--allow-native-execution` and at least one `--runtime-input`. It records the root HEAD, hashes the wiki `*.md` files and runtime inputs, records each peer's resolved root/availability/HEAD, and hashes selected artifacts, then runs `[*argv, query, '--json', '--files', *files]` with `cwd=root` and no shell (60 s timeout, 4 MiB budget). It rejects the capture if any input changed during the run. It validates the report shape (see [#ownership-boundary](#ownership-boundary)) and, when a pointer is given, compares native `{root, revision}` observations with every selected checkout.
- **Never**: takes argv from wiki text, copies native stderr (only its byte count), truncates, or overwrites `--output` (exclusive create).

## workflow-delegate

`workflow.py start` and `delegate` produce a `wiki-work-packet`.

- **CLI**: `start --capture PATH --task-id ID --owner NAME --outcome TEXT --acceptance TEXT... --capability TEXT... --output NEW [--allow-file PATH]... [--read-only]`. `delegate --packet PATH --task-id ID --owner NAME --output NEW [--allow-file PATH]... [--read-only]`. Both `--acceptance` and `--capability` are repeatable and required.
- **Behavior**: both recheck that the capture is current. An edit task's `allowed_files` must cover the planned files. A read-only task grants no paths and records a `read_only_baseline` observation. A delegated child keeps the same kind, adds `parent_task_id`, and may only narrow `allowed_files`.
- **Never**: dispatches anything (`dispatch: "not performed"`) or acts as a filesystem sandbox. Access is task scope only.

## task-views

For `--capture`, explicit `--view index` aliases the compact `summary` projection.
Its bounded text continuation keeps the requested `index` view and snapshot mode;
explicit JSON contains the same complete scope as summary. The legacy `--packet`
index shape/default format and lifecycle delivery remain unchanged.

Capture page/history and current-state input paths accept an exact saved Wiki key
or that page’s repository-relative Wiki path. `captured_page_key` resolves stored
keys only, rejects ambiguity, and performs no filesystem/Git lookup. State previews
use the resolved canonical key before constructing the existing protected target.
An unknown key in a populated capture is distinct from an older capture without
saved page views; existing integrity and source-byte checks remain unchanged.

The text outline lists its complete heading/status inventory before the exact open-command appendix. Long capture/CLI paths no longer interrupt heading discovery. All commands remain in bounded continuation; JSON/open argv and current/history semantics are unchanged. The long-path first-viewport regression and continuation/quoting tests cover this ordering; actual installation/adoption is separate.

`show --view page|history --path PAGE --section-index` (capture or packet) prints a
saved heading outline instead of page text. `context_reading.section_outline` lists
the page's saved `section_index` rows for that view (body headings for `page`, explicit
history headings for `history`; fenced snapshot headings were never indexed) and
checks each title against the same saved text `--section` reads via `saved_headings`.
Only a unique titled heading gets an exact open argv (`--section=TITLE` when the title
starts with `-`); duplicates are marked AMBIGUOUS and empty headings UNTITLED, with no
selector. Missing or malformed metadata is reported UNKNOWN and is not rebuilt from
live files. Text output uses the same bounded `text_page` continuation, whose NEXT
keeps `--section-index`, view, path, capture and snapshot mode; `--format json`
returns the outline with `open_argv` lists. It cannot be combined with `--section` or
other views. The default page/history/JSON outputs are unchanged; the summary `Expand`
line and a failed `--section` error point to the option. Listing is not reading.

`show --capture|--packet PATH --view current --path PAGE [--snapshot-only] [--format json]`
reads only the saved authored current section, without guessing its heading.
`context_reading.current_section` (shared by capture and packet through `capture_view`)
takes the page's saved non-history `section_index` rows whose title matches the existing
`CURRENT` labels (`Current`, `Current state|status`, `当前`, `当前状态`, `现状`, optionally
dated), cross-checks them against the same saved `body_markdown` headings `--section`
reads, and returns `selected` only for exactly one authored heading. Generated markers are balanced by their saved marker name (including nested blocks); a mismatched close never exposes generated text as authored. This affects only this new read view. A heading inside an
unfenced generated block (`<!-- name:begin -->`/`<!-- BEGIN -->` through its `end` marker, or
to the end of the body when unclosed) is not authored and is not a candidate. The selected
text runs from the heading to the next heading at the same or a higher level or, as in the
state planner, the first unfenced generated opener; fenced marker examples stay literal
text. A generated block's internal comment matching an `end` marker would close it early;
this is a saved-text convention, not a generator parser. The result carries path, declared heading/level/line, any declared date (not
certified), freshness and an authored-not-verified label. Zero matches, metadata missing
or not aligned with the saved body, or only generated current headings (counted in
`generated_current_headings`) → `unknown`; several authored (siblings, nested, or one after
a generated-block reset) → `ambiguous` with the candidate list and no text. Neither is
reconstructed from live files, from the latest verification note or from history, and
duplicates are never merged or picked. Both include exact outline/page/history reader
commands. Text uses the existing `text_page` pager and CLI budget with its own
`[source, 'current', path]` cursor identity; it is not a whole-page read and records no
acknowledgement. `--section` and `--section-index` are rejected with this view. Default
views, page/history text and cursors, JSON exports and capture bytes are unchanged; the
summary `Expand` line names the generic option once. Older captures without saved page
views keep the existing explicit error.

`workflow.py show` renders a saved capture or packet for a reader; new capture
reading views are described above, with legacy packet views retained below.

- **CLI**: `show --packet PATH [--view {index,feature,impact,all}] [--path KEY] [--snapshot-only]`. The default view is `index`. `feature` and `impact` need one exact `--path` taken from the index. Output goes to stdout; there is no `--output`.
- **Behavior**: without `--snapshot-only` it re-runs the capture currentness check and reports `freshness`. With `--snapshot-only` it renders saved records only. The legacy index/feature/impact/all packet views carry `path_bases`, `native_workflow` (quoted, not executed), `view_observation` and `review_preparation`. New summary/page/history views expose saved reading projections and freshness, plus task scope when invoked with a packet; the complete native return contract remains in the saved capture. `lifecycle.py` consumes the snapshot index view.
- **Never**: calls Git in snapshot-only mode, clips native records silently, or authorizes dispatch. The separate explicit update-state --apply operation can edit its selected Wiki page; show never writes.
- **Qualified history continuation**: only inside an already explicit history container, a same-level heading using an existing label plus an ASCII/fullwidth colon continues that archive (including a bare colon). Standalone product headings such as History: back-button support or Archive: supported export remain body text when no explicit history container is active; placed directly after an archive at the same level, that labelled heading continues the archive. Fences and later unrelated siblings keep their original behaviour. The shared contextual helper is used by page_projection and heading_rows; the exact HISTORY matcher for write-target selection and current-body validation is unchanged. Both scanners reset history at an unfenced generated-block opener, so a continuation after that boundary cannot retain stale planner context. New capture projections use this rule; saved older projections are not rewritten. Guarded by the qualified-history, state-snapshot owner and current-product controls in test_context_reading.py.
- **Narrow packet text**: packet `feature`/`impact` with `--format text` prints `narrow_text_projection`, not the whole `task_view`. It keeps the selected `native_context` (every satellite, unregistered flag and native limits) and `expansion` unchanged, plus task id, access, freshness, `current_inputs_checked`, path bases, wiki root, root, base, each peer's captured root/availability/head (a missing head is `unknown`; nothing is re-observed), `access_scope` (packet metadata-not-sandbox limits, `edit_scope_file_count`, and for impact `selected_file_writable`, which is false for read-only review) and the read-only baseline status fields. The other envelope keys are listed once in `not_repeated`; its readers are exact commands built from the same show argv (resolved packet path, selected path, snapshot mode) and quoted with `context_reading.shell_command`: the packet index with `--format text` (bounded) and this view with `--format json`. The concatenated text is therefore a projection, not the JSON object. `--format json` is unchanged, byte for byte. Paging, cursors and the byte/line limits are the existing `text_page`; a cursor from the earlier full-envelope text fails as a changed cursor. Lifecycle delivery names this command but keeps its own deferred keys pointing at `all`/`summary`, not at impact text. Guarded by `test_packet_narrow_text_is_a_compact_projection_and_json_stays_complete`.
- **Capture record text**: capture `feature`/`impact` text (the default for prepared `bounded-v1` captures; explicit `--format text` for older ones) is `capture_record_text`, not indented JSON of `capture_view`. Its first lines name the selected record and state that a raw capture is not a task packet: no task, owner, access mode, edit scope or capability is recorded, so the view grants no permission and marks no file writable. It then gives freshness and `current_inputs_checked`, root, Wiki root and the captured base head, each captured peer's root/availability/head (a missing head is `unknown`; nothing is re-observed) and the shared `PATH_BASES` text the packet views also use. The selected record follows with every key in saved order; a non-empty list of objects (satellites, card sections) prints one exact compact-JSON line per item, and other values print as exact compact JSON, so the record reconstructs exactly and is never reduced to matching anchors. Native and capture limits follow, then exact summary and `--format json` reader commands quoted with `shell_command`. `--format json`, the capture bytes, `all`, packet views and `text_page` paging/budgets are unchanged; a cursor from the earlier JSON-shaped text fails as a changed cursor. Guarded by `CaptureRecordTextTests` in `test_reading_flow.py`.
- **Implemented candidate**: packet index puts native_index first and omitted candidates first inside it. `prepare` defaults to a compact scope index: declared files/owners precede broad candidates, while query-only views start with actual matched cards; candidate counts remain early and the complete inventory uses explicit bounded continuation. Behavioral coverage is in `tests/test_context_reading.py`; installation/adoption is separate.

## capture-return

`workflow.py capture-return` recaptures the complete actual return for the coordinator.

- **CLI**: `capture-return --packet PATH --native-argv JSON --output NEW [--allow-native-execution]`. Without the flag it refuses to run.
- **Behavior**: `--native-argv` must equal the saved `native_argv`, and saved runtime inputs, source comparison and artifacts must be unchanged. It collects every actual diff file across the root and peers with `repository_changes` (the predicate `finish` also uses), re-runs `capture` over that list, and rejects any source, peer or head movement during the run. The result is a `native-wiki-capture` with an added `return_scope`.
- **Never**: filters the list by `allowed_files` or the planned files, retries, or replaces `finish`.

## finish-reconciliation

`workflow.py review-template` and `finish` reconcile a return against the final capture.

- **CLI**: `review-template --packet PATH --after-capture PATH --output NEW`. `finish --packet PATH --after-capture PATH --review PATH --output NEW`.
- **review-template**: writes a `wiki-review-template` in which every satellite page, capability and unregistered file is `unreviewed`.
- **finish**: rejects a review whose `pages`, `capabilities` or `unregistered` is a list rather than an object. It recomputes the actual diff and reports `issues`: uncovered diff, unplanned files, a page marked `updated` without a real change, `no_update` without a reason, an unreviewed capability, a verified capability without reachable references, an unjustified unregistered file, a satellite page left unreviewed, a capability decision without a reason, unavailable peer sources, a native nonzero exit or placement issues, a missing handoff, or a read-only task with differences. It exits 1 when `structural_reconciliation` is false.
- **Never**: edits project files, runs checks, or certifies semantic review, runtime or product completion.

## lifecycle.py summary

Optional SessionStart adapter. With `PROJECT_WIKI_PACKET` set to an absolute packet path
whose `root` contains the session `cwd`, it injects a compact projection of the
`show --snapshot-only` index view with every file→owner-page edge (6 KiB budget). Over budget it delivers that
complete routing with every other record named by key path in the `--view index` reader, or, when routing
itself cannot fit, no inventory and an exact reader argv. Once the module has loaded, it always exits 0; a missing or broken sibling
`workflow.py` fails at import with a traceback. Full contract: [hooks-and-gates.md#lifecycle-delivery](hooks-and-gates.md#lifecycle-delivery).

## edit_gate.py summary

Optional Claude PreToolUse gate for `Edit|Write|MultiEdit`. It is active only in a checkout
with `.project-wiki/edit-gate.json`. It blocks (exit 2) a locked path that lacks a fresh
context stamp or a design-first wiki change, and passes on its own defects. Full contract: [hooks-and-gates.md#edit-gate](hooks-and-gates.md#edit-gate).

## packaging

> Release/check extension reviewed: 2026-11-21 against the candidate based on `68f6a6c`; other sections retain their prior scope.

`scripts/package_plugin.py` builds a plugin directory from the canonical skill.

Claude Code can also install from the GitHub checkout. [The marketplace catalog](../../.claude-plugin/marketplace.json)
points to the repository root and explicitly loads the canonical `project-wiki/` skill directory. The catalog mirrors
the name, description and version in `plugin.json`; the package test checks that they agree. Direct installation
exposes the skill. The separately built package provides provenance receipts and the optional hook profile.

- **CLI**: `package_plugin.py --output NEW_DIR [--with-lifecycle-hooks] [--hook-layout {legacy,portable}]`. The layout defaults to `legacy`. `portable` is allowed only together with `--with-lifecycle-hooks`.
- **Outputs**: `skills/project-wiki/**` (only `.md/.py/.yaml/.yml/.json`; `__pycache__` and `.pytest_cache` are skipped; any other suffix or a hidden path fails the build), `LICENSE`, `scripts/plugin_doctor.py`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, plus `hooks/{codex,claude}.json` when hooks are included, and the receipt `PACKAGE-SOURCES.json` (`schema_version` 2, `source_byte_policy` `utf8-crlf-to-lf-v1`). `root_manifest_projection` is `canonical-identity-v1` without hooks, `legacy-host-hooks-v1` for the legacy layout (no root `plugin.json`), or `portable-openai-hooks-v1` (root `plugin.json` whose `extensions["com.openai"].hooks` is `./hooks/codex.json`).
- **Never**: installs, enables or trusts anything, writes inside the source checkout, overwrites an existing output, follows symlinks or junction aliases, or packages hidden or unlisted files.

### Release gate and offline comparison

[`release_plugin.py`](../../scripts/release_plugin.py) orchestrates the existing
builder/doctor; it does not define another payload inventory. The no-hooks default
is the only automatic-release profile. Maintainer Wiki/tests and release/check
orchestration are not package inputs; changes under the **shipped** `project-wiki/`
method are inputs. The release comparison derives canonical input hashes from the
builder receipt, adds its projection implementation and marketplace catalog, and
removes only version fields. Actual distribution changes require a numeric,
increasing `plugin.json` version mirrored in the Claude marketplace, in the
current push. Version-only edits are rejected. This infrastructure PR changes no
payload and does not bump either manifest.

The `release` job in [check.yml](../../.github/workflows/check.yml) depends on all six
OS/Python checks in the **same run**. It accepts only a non-forced canonical
`push` to `main`, repository ID `1466210381`, an exact commit confirmed as a merged
PR into that main, and the still-current main SHA. It rechecks the workflow/run
identity and all six successful jobs through the API. The job-level condition starts with literal `false`, so no runner or write token
is provisioned until a separate reviewed enable change. Only this serialized job
has `contents: write` (plus read access to Actions/PR metadata); no added secret,
`workflow_run`, PR artifact download or execution of release contents is involved.
The normal project review must approve each payload/version change; this does not
claim a server-enforced review or branch-protection policy.

**Default off:** the leading `false &&` in the job's `if` is the reviewed enable
switch. Inside the enabled-only job, `PWS_RELEASE_ENABLED` also gates the script.
Dry-run planning remains an explicit read-only script path, not a writable CI job.
Even when enabled in a future reviewed change, absence of a formal release returns
`bootstrap_required`. There is no automatic first release, baseline inference from
`0.2.39`, or bootstrap flag. A separately authorized bootstrap must establish an
exact main tag and complete receipt/assets accepted by this gate; it is outside
this PR. A missing or incompatible baseline, ambiguous inventory, ancestry gap,
changed audience, stale main or failed matrix blocks publication.

After bootstrap, compare against the highest numeric formal release, not the
previous commit alone. Verify its exact lightweight tag, commit, version and asset
digests and reproduce its package using the **current trusted builder**, without
executing historical code. Both description and bundle materialize exact tracked
Git blobs through `ls-tree`/`cat-file`; ignored checkout files cannot enter them.
Git archive `export-ignore`/`export-subst` are deliberately not applied. Aliases and
submodules in the tracked tree fail closed. The bundle descriptor must equal the
preflight descriptor before any write. Multi-commit pushes compare aggregate inputs both to
that formal baseline and to the event's `before` commit. Earlier unreleased input
changes cannot be silently backfilled by a Wiki-only push. The new push must
contain a real input change and version increase. A complete same-version,
same-commit release is a no-op; other existing versions/tags/drafts block rather
than overwrite. API inventories are bounded at 100 and fail closed at the bound.

Before writing and again before publishing, recheck live main, CI and the release
inventory/formal baseline; external publication changes stop this attempt. Create a new
exact tag and draft, upload `package.zip` and `release-receipt.json`, verify both
asset digests plus the complete draft receipt, then publish. Report success only
after reading back the published release, tag and receipt. Failures can leave a
tag/draft: automatic retry will not overwrite, delete or resume it; an owner must
inspect it under separate recovery authorization. A failed write response can be
uncertain (including publication); inspect remote state before retrying. Serialization is not a promise
of transactional publication or immunity to concurrent administrator changes;
GitHub provides no compare-and-swap transaction across these API writes. This
script refuses overwrites but does not assert or enable GitHub Immutable Releases.
The receipt binds repository ID/name, source commit, version, SHA256 archive and
the existing complete package receipt. GitHub metadata/access and independent
receipt authentication are the trust boundary; hashes alone are not signatures.

[`pws-sync`](../../scripts/pws-sync) is a repository-local **check-only** CLI. Run
it from a reviewed checkout with Python 3.10+, never from candidate package code:

```sh
python3 -B scripts/release_plugin.py --bundle /approved/scratch/new-bundle
python3 -B scripts/pws-sync --check --target /explicit/local/package \
  --candidate /approved/scratch/new-bundle \
  --trusted-receipt-sha256 DIGEST_FROM_INDEPENDENTLY_TRUSTED_RECEIPT
```

These paths are illustrative handles, not required directories. `--bundle` requires
a clean exact checkout, writes a new scratch bundle only and prints its digest.
For a local experiment, independently review that checkout and its output before
trusting that digest. A published candidate's receipt digest must come from the
verified canonical release or another approved channel, not from an untrusted
file merely accompanying the download. No network fetch is performed by `--check`.

`--candidate` accepts the complete bundle directory or just a pinned
`release-receipt.json`. Directory mode requires the archive and actual package to
validate. Receipt-only mode compares the complete pinned receipt against the
explicit target validated by the trusted doctor; it does **not** claim to have
inspected absent candidate bytes. No argument is inferred from host caches or
configuration. The default target kind is a package produced by the existing builder.
For an independently installed skill directory, explicitly select
`--target-kind standalone-skill --target APPROVED_SKILL_DIRECTORY`. It projects
`canonical_skill_files` from the same authenticated receipt and uses the existing
`utf8-crlf-to-lf-v1` byte policy. Coverage must match exactly: missing/extra files,
symlinks/junction aliases or escapes fail. Only the builder's existing
`__pycache__` and `.pytest_cache` noise is excluded (reported, never removed), and
aliases even inside those caches are refused. Unexpected files are not read.
A complete differing skill reports `different`; `same` means these files match,
not that a particular host installed, selected or loaded them. No host discovery
or client connection is performed.

| Report | Meaning / exit |
|---|---|
| `same` | Valid target and complete candidate receipt match, exit 0; no session-load claim |
| `different` | Valid target differs, including equal-version/different-byte cases, exit 1; not necessarily a newer version |
| `not_installed` | Explicit target path is absent, exit 1; no global installation claim |
| `no_trusted_input` | Candidate or independently authenticated receipt pin missing, exit 2 |
| `invalid_candidate` / `invalid_target` | Corrupt/incomplete/aliased input, exit 2; never equal or updated |

Checking does not install, replace, cache, enable hooks, change configuration,
execute/download candidate content or report a successful update. Host loading,
trust, active sessions and adoption remain unverified. Linux handoff commands and
measured limits are in the [offline release/check evidence](../../evals/reports/release-sync-20261121.md).

## doctor

`scripts/plugin_doctor.py` inspects a built package and, optionally, evidence the caller supplies.

- **CLI**: `--package PATH [--source PATH] [--claude-transcript PATH] [--codex-inventory PATH --codex-marketplace NAME [--codex-version-file PATH] [--codex-hooks PATH --codex-hooks-cwd PATH_STRING]]`. The pairings are enforced by `parser.error`.
- **Outputs**: one report (`schema_version` 1) with `package_valid`, `issues`, source/support/identity match flags, and `codex_observation`, `codex_hooks_observation` and `cli_observation` with kinds `provided-codex-plugin-inventory`, `provided-codex-hooks-list` and `provided-local-cli-transcript`. Install, trust, execution, delivery and use stay `unverified` or `not established`. It exits 0 only when the package and any source comparison are valid.
- **Never**: runs host commands, grants trust, or stats or resolves host path strings (they are compared lexically).

## host-manifests

| File | Declares | Included when |
|---|---|---|
| `plugin.json` | Canonical identity: `name`, `version` (the version source), `description`, `author`, `license` | Always (projected into both host manifests; omitted at the root only with `--with-lifecycle-hooks --hook-layout legacy`) |
| `hooks/claude.json` | SessionStart (`startup\|resume\|clear\|compact\|fork`) → `lifecycle.py`; PreToolUse `Edit\|Write\|MultiEdit` → `edit_gate.py`; 10 s timeout | `--with-lifecycle-hooks` |
| `hooks/codex.json` | SessionStart only → `lifecycle.py`, with `commandWindows`, `additionalContextLimit` 8000 and a status message | `--with-lifecycle-hooks` |

Both hook files start scripts through `runpy` under `$CLAUDE_PLUGIN_ROOT/skills/project-wiki/scripts/`.

## packet-kinds

All come from `workflow.py`. Each written file is new-only and at most 4 MiB.

| `kind` | `schema_version` | Producer | Consumers | Key fields |
|---|---|---|---|---|
| `native-wiki-capture` | 1 | `capture`; `capture-return` (adds `return_scope`) | `start --capture`; `review-template`/`finish --after-capture`; embedded as packet `context` | `root`, `wiki_root`, `query`, `files`, `base{head,inputs}`, `runtime_inputs`, `native_argv`, `native_exit_code`, `peers`, `baseline_untracked`, `baseline_peer_untracked`, `native_report` (+ raw and canonical sha256), `native_source_context`, `native_source_comparison`, `preserve_artifacts`, `preserved_artifact_hashes`, `planned_source_hashes`, `evidence`, `limits` |
| `wiki-work-packet` | 1 | `start`; `delegate` (child: same kind + `parent_task_id`) | `delegate`, `show`, `capture-return`, `review-template`, `finish`, `lifecycle.py` | `task_id`, `owner`, `root`, `base_sha`, `outcome`, `access` (`edit`/`read_only`), `allowed_files`, `acceptance`, `capabilities`, `context`, `dispatch`, `return_requirements`, `limits`, optional `read_only_baseline` |
| `wiki-review-template` | none | `review-template` | Filled by a reviewer, then passed as `finish --review` (`finish` checks the shape, not `kind`) | `task_id`, `artifact_preservation`, `pages`, `capabilities`, `unregistered`, `handoff`, `guidance` |
| `wiki-work-reconciliation` | 1 | `finish` | The coordinator or a human; no in-repo consumer | `task_id`, `access`, `base_sha`, `head_sha`, `actual_files`, `structural_reconciliation`, `issues`, `capability_gaps`, `review`, `native_omitted_candidates`, `source_state`, `handoff`, `artifact_preservation`, `native_source_comparison`, `limits` |

`show` output has no `kind`. The package receipt (`PACKAGE-SOURCES.json`) and the doctor
observations are separate formats, covered in [#packaging](#packaging) and [#doctor](#doctor).

## path-kinds

| Kind | Meaning | Where it appears |
|---|---|---|
| Native page key | The string the native router emits for a page. It is used unchanged as a key. | `native_report.cards[].path`, `impact[].pages[].path`, review `pages` keys, `show --path` for `feature` |
| wiki_root-relative | A page key resolved under `root/wiki_root`. `validate_native` requires keys to be normalized POSIX relative paths (no `..`, `\`, `:`). | `within(root/wiki_root, key)` checks; `finish` prefixes `wiki_root + '/'` to compare against the diff; edit-gate `generated` globs |
| Checkout-relative | A normalized POSIX path from the task root. A peer file uses an `alias/` prefix. | `files`, `allowed_files`, `actual_files`, `runtime_inputs`, `planned_source_hashes`, `impact[].file`, capability `references`, `wiki_root` itself; `wiki.py` manifest paths; edit-gate `locked` globs, `stamp.path`, `map_file`, `skip_file` |
| Resolved absolute | `Path.resolve()` on the capturing host | Capture/packet `root`, `peers[alias].root`, `preserve_artifacts` (must already equal their resolved form) |
| Host-received string | Data a host supplied, never validated against the local filesystem unless stated | `PROJECT_WIKI_PACKET` (must be absolute, not a symlink); hook event `cwd` and `tool_input.file_path` (edit gate resolves a relative one against `cwd`); doctor `--codex-hooks-cwd` and hooks/list `cwd`/`sourcePath` (compared lexically); artifact paths in `show --snapshot-only` (`local_path_validation: not performed`) |

`show` reports the bases in `path_bases`. A missing `wiki_root` is unknown, not a default.

## ownership-boundary

| Concern | Owner |
|---|---|
| Pages, routing metadata, rules, debt ledger, finish and commit gates | The consumer project's native wiki and tooling. These stay **authoritative**. |
| Task-context command (argv) and its runtime inputs | The consumer project. The caller passes them explicitly, and the skill never reads them from wiki text. |
| Capture, packet, task view, actual-diff reconciliation, handoff | The skill (`workflow.py`) |
| Packaging and package/host-evidence inspection | The skill (`package_plugin.py`, `plugin_doctor.py`) |
| Installation, hook trust, enabling | The host and the human. The skill never performs them. |

The native report must hold `query` (equal to the task query) and the lists `cards`,
`impact`, `omitted` and `placementIssues`, plus a nonempty `limits` string. Each `impact`
row needs `file`, a boolean `unregistered` and `pages`, and the `impact` files must equal the
requested files exactly. A registered row with empty
`pages` is rejected, and every page must exist under `wiki_root`. Each `cards` entry needs a
string `title` and a `path` that exists under `wiki_root`. An optional `workflow` object is
quoted to readers. Rationale:
[PLUGIN_PLAN.md#architecture-and-ownership](../PLUGIN_PLAN.md#architecture-and-ownership).

## Historical evidence

> Reviewed: 2026-11-03 against 5056787; task-views known gap verified against b8dd295


### Saved state-preview reader (0.2.23)

The first guided0.2.22 task read bounded impact views, then inspected a saved state
proposal by printing its diff directly. Initial attribution to operation stdout
was corrected by source inspection: `update-state` already returns compact JSON,
not the page-sized plan. Keep that receipt contract and add a bounded reader for
the saved proposal instead of adding reminders, gates or another workflow.

New plans retain the exact original page bytes alongside the existing
proposal. Pure `show-state --plan PATH --view diff|proposed` validates saved
hashes and uses the existing byte/line cursor mechanism. Continuation must not
inspect live project inputs, rerun native collection or apply writes. Old plans
remain readable in proposed mode; diff requires a saved original, never an
inferred reconstruction. Explicit JSON remains a deliberate complete export.
The existing compact operation receipt will add an exact preview-reader command.
Test large Unicode previews, complete reconstruction, changed-plan/cross-view
cursors, legacy proposals, explicit JSON, and read-only behavior after apply.

The earlier initial design assumption is superseded by this source verification;
there was no implementation of that assumption. An unrelated remaining boundary:
a newly planned file triggered the host's old native-command hint, and the worker
piped that query to `tail`. A saved-preview reader cannot prevent arbitrary raw
native calls; that external route stays separate evidence.


### Archive placement follow-up (design checkpoint)

Independent reconciliation of the first real state update found that its saved
proposal contained the old current section, but the consumer's subsequent native
generation removed it. The archive entry had been inserted immediately before the
next heading, after the opening generated-block comment that precedes that heading.
Structural/anchor checks did not prove byte preservation through regeneration.

Insert new entries immediately after an existing authored history heading instead
of at the next heading boundary. This keeps the previous history unchanged and
avoids consuming the next section's leading generated-block marker. With no history,
continue appending a new history section after the full page. Test both exact
insertion and a simulated native generated-block rewrite, then rerun a real native
generator before claiming preservation. No new reminder, gate or status inference.

The same next-heading boundary can also consume a generated opener when replacing
an old current section. Recognized `name:begin` / `BEGIN` HTML block markers must
bound authored current/history projection and current replacement; markers inside
fenced examples remain literal. Preserve the generated block itself and verify its
regeneration independently from the archived old state.


### Applying the reviewed saved plan (0.2.24)

The second guided task reviewed saved previews but had to reconstruct the body and
verification arguments for `update-state --apply`, producing a new plan rather
than applying the reviewed one. Add `apply-state --plan PATH` as an explicit write
operation over the existing saved-plan applier. It must not rerun collection,
re-read a body file, reconstruct verification text or overwrite the reviewed plan.
Reuse the existing kind/hash, target-root, symlink and original-source-byte checks.
Expose an exact apply argv in the compact preview receipt; keep the original
single-operation `update-state --apply` compatible. A stale source still refuses
application rather than silently refreshing. The operation is not a business or
human approval certificate. Test exact reviewed bytes, changed external body,
stale/tampered plans, no-op, legacy plans and no native/Git/recomputation calls.
