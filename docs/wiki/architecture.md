# Architecture

> Reviewed: 2026-11-07 against reading-flow source; file-first preparation, bounded text continuations and explicit authored-state updates rechecked. Host/adoption status lives in status.md.

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
explicit. `prepare` needs a nonempty file list and the original execution opt-in.
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
record, page shows saved authored body, history shows older material. Long text views are continued within 6000 UTF-8 bytes and 60 lines; the exact NEXT command is bound to saved text and preserves view/path/section/format/snapshot mode. Large sections and Unicode single lines remain reachable. Explicit JSON export remains complete. New views also accept a work
packet through its existing saved context. Legacy captures without prepared
pages have no invented page view. Live selected-source drift is historical data,
not current context. Caller-declared revision observations are not production
or capability verification. See [the command](../../project-wiki/references/collaboration-workflow.md#file-first-preparation).

## Bounded continuation, reuse and authored-state updates

`context_reading.text_page` emits an explicit character range and COMPLETE/PARTIAL
status, within 6000 UTF-8 bytes and 60 lines. CLI stdout explicitly uses UTF-8/LF so Windows newline translation does not inflate the wire budget. A digest-bound cursor resumes the exact
saved view; text changes or a different capture/view/path/section reject the cursor.
The printed command preserves snapshot-only mode and explicit text format. Shell
commands are quoted for POSIX or PowerShell on the running host. Scope is neither
silently clipped nor falsely called fully delivered; a cursor never certifies reading.
New prepared captures carry the additive text_display=bounded-v1 marker and
default to bounded text, including impact/feature/all. Older captures, raw native
captures and packet views retain default JSON for active clients; `--format text` bounds them too.
Explicit `--format json` is an unpaginated machine export, not a bounded display.

`prepare_request` binds root/query/selected files/native prefix/runtime inputs,
Wiki root, peers, observed refs, preserved artifacts and reader implementation.
Repeated prepare at the same output validates the request and current declared
inputs, selected-source baseline and observed refs, then reuses original bytes and
capture time without calling the native router. It never silently refreshes stale
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
the previous one, never inventing a verification from Git. The original current
heading and preamble/keyword metadata positions are retained; native section links
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

`workflow.py show` renders a saved capture or packet for a reader; new capture
reading views are described above, with legacy packet views retained below.

- **CLI**: `show --packet PATH [--view {index,feature,impact,all}] [--path KEY] [--snapshot-only]`. The default view is `index`. `feature` and `impact` need one exact `--path` taken from the index. Output goes to stdout; there is no `--output`.
- **Behavior**: without `--snapshot-only` it re-runs the capture currentness check and reports `freshness`. With `--snapshot-only` it renders saved records only. The legacy index/feature/impact/all packet views carry `path_bases`, `native_workflow` (quoted, not executed), `view_observation` and `review_preparation`. New summary/page/history views expose saved reading projections and freshness, plus task scope when invoked with a packet; the complete native return contract remains in the saved capture. `lifecycle.py` consumes the snapshot index view.
- **Never**: calls Git in snapshot-only mode, clips native records silently, or authorizes dispatch. The separate explicit update-state --apply operation can edit its selected Wiki page; show never writes.
- **Implemented candidate**: packet index puts native_index first and omitted candidates first inside it. `prepare` defaults to a compact scope index; oversized indexes use explicit bounded continuation. Behavioral coverage is in `tests/test_context_reading.py`; installation/adoption is separate.

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
whose `root` contains the session `cwd`, it injects the `show --snapshot-only` index view
(6 KiB budget). Once the module has loaded, it always exits 0; a missing or broken sibling
`workflow.py` fails at import with a traceback. Full contract: [hooks-and-gates.md#lifecycle-delivery](hooks-and-gates.md#lifecycle-delivery).

## edit_gate.py summary

Optional Claude PreToolUse gate for `Edit|Write|MultiEdit`. It is active only in a checkout
with `.project-wiki/edit-gate.json`. It blocks (exit 2) a locked path that lacks a fresh
context stamp or a design-first wiki change, and passes on its own defects. Full contract: [hooks-and-gates.md#edit-gate](hooks-and-gates.md#edit-gate).

## packaging

`scripts/package_plugin.py` builds a plugin directory from the canonical skill.

- **CLI**: `package_plugin.py --output NEW_DIR [--with-lifecycle-hooks] [--hook-layout {legacy,portable}]`. The layout defaults to `legacy`. `portable` is allowed only together with `--with-lifecycle-hooks`.
- **Outputs**: `skills/project-wiki/**` (only `.md/.py/.yaml/.yml/.json`; `__pycache__` and `.pytest_cache` are skipped; any other suffix or a hidden path fails the build), `LICENSE`, `scripts/plugin_doctor.py`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, plus `hooks/{codex,claude}.json` when hooks are included, and the receipt `PACKAGE-SOURCES.json` (`schema_version` 2, `source_byte_policy` `utf8-crlf-to-lf-v1`). `root_manifest_projection` is `canonical-identity-v1` without hooks, `legacy-host-hooks-v1` for the legacy layout (no root `plugin.json`), or `portable-openai-hooks-v1` (root `plugin.json` whose `extensions["com.openai"].hooks` is `./hooks/codex.json`).
- **Never**: installs, enables or trusts anything, writes inside the source checkout, overwrites an existing output, follows symlinks or junction aliases, or packages hidden or unlisted files.

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

> Reviewed: 2026-11-03 against c062224; task-views known gap verified against fc310fe


### Saved state-preview reader (design; not implemented)

The first guided0.2.22 task read bounded impact views, then inspected a saved state
proposal by printing its diff directly. Initial attribution to operation stdout
was corrected by source inspection: `update-state` already returns compact JSON,
not the page-sized plan. Keep that receipt contract and add a bounded reader for
the saved proposal instead of adding reminders, gates or another workflow.

New plans will retain the exact original page bytes alongside the existing
proposal. A pure `show-state --plan PATH --view diff|proposed` will validate saved
hashes and use the existing byte/line cursor mechanism. Continuation must not
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
