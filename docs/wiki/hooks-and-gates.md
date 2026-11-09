# Hooks and gates

> Reviewed: 2026-11-03 against c062224; lessons-for-the-skill 5, 7, 11 and 12 re-verified against fc310fe

The skill ships two optional host hooks: SessionStart delivery (`lifecycle.py`) and a Claude
pre-edit gate (`edit_gate.py`). It recommends, but does not ship, after-edit gates. This page
gives the current contracts, the field evidence from the pilot project, and what that evidence
implies for the skill. Guarding tests are listed in [invariants.md](invariants.md). Package
layouts are in [architecture.md#packaging](architecture.md#packaging) and
[#host-manifests](architecture.md#host-manifests).

## lifecycle-delivery

| Item | Contract (from `project-wiki/scripts/lifecycle.py`, `hooks/*.json`) |
|---|---|
| Declared in | `hooks/claude.json` and `hooks/codex.json`, SessionStart, matcher `^(startup\|resume\|clear\|compact\|fork)$`, 10 s timeout. Codex adds `commandWindows`, `additionalContextLimit` 8000 and a status message. Both start the script through `runpy` under `$CLAUDE_PLUGIN_ROOT/skills/project-wiki/scripts/`. |
| Accepted sources | `START_SOURCES = {startup, resume, clear, compact, fork}`. Any other source is a visible delivery failure. |
| Selection | `PROJECT_WIKI_PACKET` = absolute path of an existing work packet (regular file, not a symlink, ≤ 4096 chars). Unset: exit 0, stdin not read. There is no second task registry. |
| Workspace check | Event `cwd` and packet `root` must both be absolute, and `cwd` must resolve inside `root`. |
| Rendering | `lifecycle.py:compact_index(workflow.task_view(packet, 'index', snapshot_only=True), packet)`: saved records only. No Git, native router, page command, model call, write or dispatch check. Owner pages, features and omitted candidates share one `pages` registry of `[path, title]`; `files[].owners` keeps every file→owner edge; non-owner row keys (`unregistered`, `invariants`, unknown) are kept; `selected: false` / `selected_without_record` mark impact rows outside, or selected files missing from, `context.files`. Snapshot-mode statements merge into `reading`; reader commands share `reader.prefix`. Access/`allowed_files`, `path_bases`, peers, `freshness` and `native_workflow` identity plus its `context` (capture time/status, source and runtime observations) stay verbatim. Native operational keys (`finish`, `acknowledgement`, `pushGate`, `reader`, `limits` and any other key), `return_requirements` and repeated limit prose are listed under `not_delivered` (`status: NOT DELIVERED`) by key path in the existing `--view all` or `--view summary` reader; the packet and public views are unchanged. Over 6 KiB of ASCII JSON, it emits `index_delivered: false`, `index_bytes`, `budget_bytes` and a pointer to `workflow.py show --snapshot-only` instead of truncating. |
| Output | `hookSpecificOutput.additionalContext`, prefixed as UNTRUSTED TASK DATA that does not establish currentness, reading or completion. On any error: a fixed `systemMessage` with no packet contents, path or raw error. Once the module has loaded, exits 0; a missing or broken sibling `workflow.py` fails at import. |
| Layouts | `legacy` (default with `--with-lifecycle-hooks`): no root `plugin.json`, hooks referenced from both host manifests. `portable`: root `plugin.json` carries `extensions["com.openai"].hooks` = `./hooks/codex.json`. Method text: [collaboration-workflow.md#optional-lifecycle-delivery](../../project-wiki/references/collaboration-workflow.md#optional-lifecycle-delivery). |

What is verified and what is not:

| Claim | Status | Evidence |
|---|---|---|
| Both layouts build, close over their inputs and pass the doctor; forged or mixed profiles fail | Verified by tests | `tests/test_legacy_hooks.py`, `tests/test_portable_hooks.py`, `tests/test_lifecycle.py` |
| The compact index keeps every file→owner edge, shared owners once, Unicode/missing titles, unknown row metadata and selected-file indicators; overflow and malformed rows opt out visibly | Verified by tests | `tests/test_lifecycle.py::LifecycleTests.test_compact_index_keeps_every_file_owner_edge_once_and_all_saved_records`, `test_same_path_with_different_saved_titles_is_not_merged`, `test_many_owners_overflow_opts_out_without_listing_selected_paths`, `test_malformed_native_rows_fail_visibly_without_contents`, `test_operational_instructions_are_named_not_delivered_and_resolve_in_existing_views`, `test_large_operational_contract_alone_does_not_block_routing_delivery`, `test_oversized_source_observations_still_opt_out` |
| A real two-file readonly packet fits the budget | Source replay only: 6,061 bytes with all six edges and source observations after deferring operational instructions (8,704 with them inline); host delivery not observed | [compact lifecycle index](../../evals/reports/compact-lifecycle-index-20261109.md#implementation-result) |
| The packaged `runpy` command finds its sibling `workflow.py` and writes nothing | Verified by tests | `tests/test_lifecycle.py::LifecycleTests.test_packaged_runpy_entry_resolves_sibling_and_keeps_package_readonly` |
| Codex 0.160 loads hooks from the portable layout | Refuted on one installed host: zero hooks listed. This is why `legacy` is the default. | [C119](../../evals/reports/portable-hook-declaration-c119-20261024.md), [C120](../../evals/reports/runtime-hook-layout-c120-20261024.md) |
| A trusted host runs the hook and an agent uses the delivered index | Observed once: a synthetic fixture on an installed desktop host. Hook execution was inferred, not exported. | [C122](../../evals/reports/wiki-path-basis-c122-20261024.md) |
| A host lists the SessionStart hook as trusted | Supplied snapshot only. The doctor keeps it as data and grants nothing. | [C179](../../evals/reports/supplied-hook-observations-c179-20261025.md) |
| Linux Claude SessionStart delivery, efficiency, business acceptance | Not observed | [C118](../../evals/reports/lifecycle-delivery-c118-20261024.md#remaining-acceptance) |

## edit-gate

`project-wiki/scripts/edit_gate.py` runs as Claude `PreToolUse` on `Edit|Write|MultiEdit`
(`hooks/claude.json` only; `hooks/codex.json` declares no PreToolUse). Exit 2 blocks the edit
and puts the reasons on stderr; exit 0 passes. The method and an example config are in
[maintenance.md#pre-edit-gate-host-delivery-of-wiki-first](../../project-wiki/references/maintenance.md#pre-edit-gate-host-delivery-of-wiki-first).

Config: `.project-wiki/edit-gate.json` at the checkout root (the nearest ancestor with `.git`).
Without it, every edit passes silently. A key of the wrong type makes the gate unavailable.

| Key | Type | Default / meaning |
|---|---|---|
| `wiki_root` | str | **Required.** Directory scanned by predicate (b). |
| `locked` | list[str] | Globs (`**`, `*`, `?`; `*` does not cross `/`) for the paths the gate judges. |
| `map_file`, `map_row_format` | str | A path is also locked when `map_file` contains `map_row_format` with `{path}` filled. Default row: ``\| `{path}` \|``. |
| `stamp` | object | `{path, max_age_hours}`; age defaults to 8 h, measured from file mtime. With no `stamp.path`, (a) passes. |
| `stamp_command` | str | Fix text printed on an (a) failure; `{file}` and `{root}` are substituted. |
| `design_first` | bool | Turns on predicate (b). |
| `generated` | list[str] | Globs, relative to `wiki_root`, removed before (b) looks for handwritten changes. |
| `base_ref` | str | Default `origin/main`. |
| `skip_file` | str | A file with non-whitespace text waives (b) only, and its first 200 chars (whitespace collapsed) are echoed; an empty or whitespace-only file fails (b). |
| `design_hint` | str | Fix text for a (b) failure. |

| Outcome | When |
|---|---|
| Pass silently | Not a PreToolUse Edit/Write/MultiEdit event; no `file_path`; outside any checkout; no config; path not locked; both predicates hold. |
| **(a) context** fails | No stamp, a stamp ≥ `max_age_hours` old, a stamp that is not JSON with `files[]`, or one that does not list the repo-relative path. |
| **(b) design** fails | With `design_first`: no handwritten file under `wiki_root` in `git diff --name-only <merge-base>` ∪ untracked, after removing `generated`. |
| Pass with a stderr note | (b) waived by the skip file, or not judged because `merge-base(HEAD, base_ref)` failed. |
| Pass as "gate unavailable" | Malformed or over-budget (64 KiB) event or config, relative `file_path` without an absolute `cwd`, Git missing or timing out (5 s), or a caught runtime error. |

Git runs read-only (`GIT_OPTIONAL_LOCKS=0`, inherited `GIT_DIR`/`GIT_WORK_TREE`/… dropped).
The gate never reads the edited content or writes a file. Both predicates are reported
together, each with its own fix. Tests: 16 in `tests/test_edit_gate.py`
([invariants.md#edit-gate-edit_gatepy](invariants.md#edit-gate-edit_gatepy)). Adoption: see
[status.md](status.md).

## after-gates

The skill ships no post-edit or pre-push gate. A project's own gates own commits. The
skill quotes their declared finish command and acknowledgement format as `native_workflow`
and never runs them ([collaboration-workflow.md](../../project-wiki/references/collaboration-workflow.md#native-wiki-collaboration-workflow)).
The recommended pattern:

| Gate | Checks | Where the skill says it belongs |
|---|---|---|
| Touch gate | Each file changed in `merge-base..HEAD` has its owning pages changed or acknowledged with a reason. A rule-level token can acknowledge a whole invariant path. | [change-navigation.md#gate-two-layer-criterion](../../project-wiki/references/change-navigation.md#gate-two-layer-criterion). It must read the same range as the planning aid: [#make-the-first-wiki-read-useful](../../project-wiki/references/change-navigation.md#make-the-first-wiki-read-useful). |
| Generated-view freshness, anchors, verification stamps | Views match a fresh computation; links resolve against the real renderer; stamps parse | Pre-push hook, with CI as the final gate and an explicit logged skip: [maintenance.md#audit-the-execution-surface-before-adding-a-rule](../../project-wiki/references/maintenance.md#audit-the-execution-surface-before-adding-a-rule) |
| Acknowledgement fan-out | Required pages per commit before and after a change | [quality-model.md#required-pages-per-commit](../../project-wiki/references/quality-model.md#required-pages-per-commit) |

The pre-edit gate runs **before** the first edit of a locked file. The touch gate runs at
**finish or push**.

## field-evidence

Source: a private transcript sample of one pilot-project coordination session (2026-11-02 to
11-03, about 33.5 h, 7,498 events, a coordinator plus 20 subagent contexts), not committed;
the numbers are not reproducible from this repo. The earlier part of the session was **not**
covered. Counts come from string
matches on the transcript. The pilot runs its **own native** pre-edit hook with the same two
predicates, not `edit_gate.py` (one gate per checkout). These numbers measure the pattern,
not this repo's code.

Pre-edit blocks (all on Edit/Write, all in subagents, 6 itemized (7 recorded) of 20 contexts; the coordinator was never blocked):

| Reason | Blocks | Real catch / false positive | Time to unblock |
|---|---|---|---|
| Path not in stamp | 14 | Procedural. The agent re-ran the task-context command with `--files`. | median ≈ 25 s; worst ≈ 108 s (parallel batch) |
| No stamp | 8 | Procedural. One agent made 8 blocked attempts on 5 files before fetching context. | ≈ 2.5 min (137–157 s) |
| Design-first | 9 recorded (8 itemized) | 1 real catch (the page was written before the code); 6 confirmed false positives and 1–2 probable. The confirmed ones came from a `pipefail` pipeline whose early-exit `grep -q` sent SIGPIPE upstream, so the hook read "no handwritten change". | 22 s (skip file) to 209 s (page written); 1 never: the agent dropped the edit and reported the bug |
| **Total** | **31 recorded (30 itemized)** | | |

Bypass usage: the hook's off-switch 0, the touch-gate skip 0, `--no-verify` 0. The skip file was
written 2 times, both after false positives. Agents explicitly declined to bypass.

After-gates (the pilot's native pre-push touch gate plus its docs test gate, and its finish script):

| Measure | Count | Notes |
|---|---|---|
| Pushes | 37 | All from the coordinator; subagents never pushed |
| Rejected by the touch gate | 3 | 1 real catch: a page stated a stale baseline count, which was fixed within ≈ 1.5 min. 1 acknowledgement-format trap: a comma-separated list with a reason per id parsed only the first id; it passed ≈ 50 s later. 1 fan-out case: two empty acknowledgement commits (4, then 14 more pages); it passed ≈ 1 min later. |
| Rejected by the docs gate | 0 | — |
| Standalone touch-gate runs | 32 pass / 19 fail | Mostly the coordinator's pre-commit dry runs |
| Acknowledgement lines | 35 | 14 in empty commits, 21 in real commits. Some lines covered 16–43 pages; the largest (43) carried one blanket reason. Subagents pre-drafted them. |
| Finish-script runs | 51 | Typically 37–103 s. 4 hit the 600 s foreground timeout, queued on a shared lock behind the full check. The docs step was red 6 times, each fixed and rerun green. |
| Touch step in subagent worktrees | skipped 6×, red 1× | Skipped with nothing committed; red on uncommitted work |
| Post-merge "regenerate" commits | ≈ 17 | ≈ 200 per-page generated-block conflicts per merge |

The pilot's synthetic pre-push benchmark (2026-11-01) is recorded in
[quality-model.md#required-pages-per-commit](../../project-wiki/references/quality-model.md#required-pages-per-commit).

| Friction | Layer |
|---|---|
| SIGPIPE false positive; acknowledgement parser silently took the first id; lock scope wider than the pilot's own docs claimed (docs paths were documented as exempt); line-number-keyed generated blocks shifting ≈ 200 pages | consumer native tooling |
| Generated views committed, so every merge conflicts; acknowledgements in empty commits; only the coordinator commits, so commit-range gates never see subagent work | process |
| 600 s foreground timeout; an auto-mode classifier denied one bug repro; each parallel edit is judged separately | host |
| Edits fired before context was fetched; gate output hidden by the agent's own `grep` filter | agent adoption |
| None of the observed incidents ran skill code; the lessons below are gaps the skill's gate or guidance shares | skill |

## lessons-for-the-skill

1. **Collect Git output fully.** `git_lines` uses `subprocess.run(capture_output=True)`: no pipe and no early exit. An unrecorded ad-hoc run with 300 modified and 3,000 untracked generated files blocked correctly in ≈ 0.1 s, and passed once 1 handwritten page changed. *Status: already in edit_gate.py; gap: no test covers many dirty files.*
2. **A failing Git command must not read as "no change".** `git_lines` returns `None` on a non-zero exit, and `design_ok` treats that as empty (`or []`). Reproduced: a `wiki_root` outside the checkout makes `git diff` exit 128, and the gate blocks with "no handwritten change" instead of "gate unavailable". This contradicts maintenance.md, which lists "Git failure" among the defects that pass. It is the same class as the pilot's SIGPIPE bug. *Status: gap.*
3. **Quoted paths defeat `generated`.** With the default `core.quotePath`, Git prints a non-ASCII file as `"docs/wiki/\347…"`, so the glob misses and a generated file counts as handwritten ((b) passes falsely; reproduced). Use `-z` or `-c core.quotePath=false`. *Status: gap.*
4. **Commit-range gates are blind inside subagents that never commit.** The pre-edit gate reads the working tree and untracked files, so it does see subagent work. A touch gate over `merge-base..HEAD` does not. *Status: consumer-side only. Guidance on same-range reading exists in change-navigation.*
5. **One acknowledgement id per token, or reject ambiguous lists.** A parser that keeps the first id of a comma list cost a rejected push. [maintenance.md#checkable-rules-beat-examples](../../project-wiki/references/maintenance.md#checkable-rules-beat-examples) now requires a parser to accept `page (reason), page (reason)` or fail naming the line. *Status: reference guidance added 2026-11-03; the parser itself is consumer-side.*
6. **Acknowledgement rides in the feature commit, not in empty commits.** 14 of 35 were empty commits. *Status: gap (no reference says so).*
7. **Do not commit generated views.** Compute them in CI or the reader, or add a merge driver plus post-merge regeneration. [maintenance.md#generated-blocks-inside-authored-pages](../../project-wiki/references/maintenance.md#generated-blocks-inside-authored-pages) now names this as the owner's structural decision and, while views stay committed, requires stable row keys, authored-text change predicates, a hunk-by-hunk merge and a post-merge authored-line guard. *Status: reference guidance added 2026-11-03; consumer-side to implement.*
8. **Lock scope and documented scope come from one source.** `edit_gate.py` derives scope only from config (`locked` plus `map_file`) and names that file in every block. *Status: already in edit_gate.py.*
9. **Drop inherited repository variables.** Git hooks and the pilot's worktree wrappers run with `GIT_DIR`/`GIT_WORK_TREE` set, and inheriting them points Git at another repository. *Status: already in edit_gate.py (`REPO_ENV`, `test_inherited_git_dir_does_not_redirect_the_gate`).*
10. **A stamp proves context was fetched, not understood. Watch real catches against false positives.** The sample shows 1 real catch to 7–8 false positives for design-first, and 1 real catch in 3 touch rejections. The docstring states the limit. The audit table's hook row records only wiring, not this ratio. *Status: limit already in edit_gate.py; gap: metric not in the maintenance audit.*
11. **In-page generated blocks count as handwritten in (b).** `design_ok` applies the `generated` globs to whole paths from `git diff --name-only`, so a page whose only change is a regenerated in-page block satisfies (b). The reference states this boundary ([maintenance.md#pre-edit-gate-host-delivery-of-wiki-first](../../project-wiki/references/maintenance.md#pre-edit-gate-host-delivery-of-wiki-first)) and the rule it falls short of ([#compare-authored-text-not-files](../../project-wiki/references/maintenance.md#compare-authored-text-not-files)). *Status: gap (code); no test.*
12. **The design waiver is unbound.** `design_ok` checks `skip_file` only for non-whitespace text; it carries no revision or age, so a waiver left from one task keeps waiving (b) after HEAD moves. The reference tells users to remove it when the task ends and recommends `{reason, head, at}` binding for project gates. *Status: gap (code).*
