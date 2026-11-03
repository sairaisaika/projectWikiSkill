# Engineering entry

> Reviewed: 2026-11-03 against c062224

This repository ships **project-wiki**, an agent skill plus an optional host plugin.
The skill teaches an agent to keep a project's wiki source-backed: route a task to its
owning pages, expand every satellite a file change touches, and reconcile the actual
diff against the wiki before handing work back. Its executable part is a set of
dependency-free Python 3.10+ scripts: `wiki.py` queries and audits a schema 1 or 2 route
manifest and builds/checks a schema 2 index, `workflow.py` captures a consumer project's native wiki context into
revision-bound JSON packets and reconciles returns, `lifecycle.py` and `edit_gate.py`
are optional host hooks, and `scripts/package_plugin.py` plus `scripts/plugin_doctor.py`
build and inspect the plugin package. This wiki covers maintaining the skill itself. It
is not the user method; that ships in [SKILL.md](../../project-wiki/SKILL.md).

## Start from your question

Run `python project-wiki/scripts/wiki.py query --root . "<question>"` first. Use the
table when you already know the area.

| If you need to know… | Route id | Page |
|---|---|---|
| How routes.json is validated, queried, indexed, checked or evaluated | `wiki-helper` | [architecture.md#wiki-helper](architecture.md#wiki-helper) |
| How native wiki context becomes a `native-wiki-capture` | `workflow-capture` | [architecture.md#workflow-capture](architecture.md#workflow-capture) |
| How a task packet is started, scoped, made read-only or delegated | `workflow-delegate` | [architecture.md#workflow-delegate](architecture.md#workflow-delegate) |
| What `show` renders, and what `--snapshot-only` skips | `task-views` | [architecture.md#task-views](architecture.md#task-views) |
| How the coordinator recaptures the complete actual return | `capture-return` | [architecture.md#capture-return](architecture.md#capture-return) |
| What `review-template` and `finish` accept or reject | `finish-reconciliation` | [architecture.md#finish-reconciliation](architecture.md#finish-reconciliation) |
| How a saved packet reaches a session at SessionStart | `lifecycle-delivery` | [hooks-and-gates.md#lifecycle-delivery](hooks-and-gates.md#lifecycle-delivery) |
| When the optional pre-edit gate blocks an edit | `edit-gate` | [hooks-and-gates.md#edit-gate](hooks-and-gates.md#edit-gate) |
| What a package contains, and what the hook layouts are | `packaging` | [architecture.md#packaging](architecture.md#packaging) |
| What the doctor verifies, and which host evidence it reads | `doctor` | [architecture.md#doctor](architecture.md#doctor) |
| Which JSON kind each command reads or writes | — | [architecture.md#packet-kinds](architecture.md#packet-kinds) |
| Which path basis a field uses | — | [architecture.md#path-kinds](architecture.md#path-kinds) |
| What the skill owns and what the consumer project owns | — | [architecture.md#ownership-boundary](architecture.md#ownership-boundary) |
| What each host hook file declares | — | [architecture.md#host-manifests](architecture.md#host-manifests) |
| What is verified for each version | — | [status.md](status.md) |
| Which test guards a behavior, and which gaps are untested | — | [invariants.md](invariants.md) |
| Which failure classes recur and who fixed them | — | [known-failures.md](known-failures.md) |
| The generated route index (do not edit by hand) | — | [route-index.md](route-index.md) |

## Where knowledge lives

Each fact has one home. Other surfaces link to that home and do not restate it.

| Surface | Holds | Audience | Do not put here |
|---|---|---|---|
| [project-wiki/SKILL.md](../../project-wiki/SKILL.md) and [project-wiki/references/](../../project-wiki/references/) | The shipped user method: how to build, route, maintain and evolve a project wiki, and how to drive the workflow CLI | Agents in consumer projects (this is packaged) | Maintainer internals, version narrative, evidence |
| `docs/wiki/` (this wiki) | Current engineering facts about the skill itself: modules, CLIs, packet kinds, path kinds, hooks, ownership; the invariant → test index; known failure classes | Maintainers of this repo | User method; history narrative; raw dated evidence (summarize in one row and link the report) |
| [docs/wiki/status.md](status.md) | Per-version status (CI, main, package, installed hosts, hooks, delivery, use): one table with links to evidence | Anyone asking "is X verified?" | Caveat paragraphs (link the report) |
| [evals/reports/](../../evals/reports/README.md) | Dated evidence: trials, host observations, adoption reviews | Anyone checking a claim | Current-state instructions |
| [CHANGELOG.md](../../CHANGELOG.md) | Version history: what changed, when, with links to reports | Release readers | Current state |
| [PROJECT.md](../../PROJECT.md) | Agent session state: current task, checks, recent session log | The next agent session | Durable facts, version history or caveats (CHANGELOG.md, the report or a page here) |

`README.md` is a current-state introduction: what the tool is, how to install it, the
commands, and links; it carries no version number or status. `docs/PLUGIN_PLAN.md` is meant
to hold only the plan and its open verification items; its current per-version narrative is
recorded drift (see [known-failures.md](known-failures.md#open-drift-found-2026-11-03)).
Version narrative belongs in CHANGELOG.md.

## Per-change surface convention

A change touches at most these surfaces:

1. **Code**: the module that implements the behavior.
2. **Route manifest**: if a routed source, symbol, needle or test changed, update
   `docs/wiki/routes.json`, then run `python project-wiki/scripts/wiki.py build --root .` and
   commit the regenerated `route-index.json`/`route-index.md`. The index stores source line
   numbers, so a line shift alone makes `check` report stale.
3. **Test**: the guarding test file under `tests/` (table below), red before green.
4. **CHANGELOG.md**: one entry, with a link to a report if new evidence was produced.
5. **The one owning page**: the `docs/wiki/` section for an engineering fact, or the
   `project-wiki/references/` file for a user-method change. Update its `> Reviewed:` line.
6. **Evidence (only if produced)**: one dated report under `evals/reports/` plus its
   index line in `evals/reports/README.md`.
7. **Version (only for a release)**: `plugin.json` `version`, a new row in
   [status.md](status.md), and the CHANGELOG heading that replaces "Unreleased".
8. **PROJECT.md**: update Current task and Checks only; new History lines link
   [status.md](status.md) instead of restating status or caveats.

Do not add a version paragraph to `README.md`, `docs/PLUGIN_PLAN.md` or the top of
`SKILL.md`. Do not restate caveats. Link to the report that measured them.

| If you change… | Guarding tests | Also check |
|---|---|---|
| `project-wiki/scripts/wiki.py` | `test_wiki.py`, `test_task_maps.py`, `test_engineering_depth.py`, `test_skill_package.py` | `evals/fixture-project` (CI runs `check` and `evaluate` on it); `evals/reports/fixture-structure.json` and `fixture-routing.json` (must equal live `audit`/`evaluate` on the fixture); the fixture's `route-index.*` (`wiki.py build --root evals/fixture-project`); [route-contract.md](../../project-wiki/references/route-contract.md) |
| `project-wiki/scripts/workflow.py` | `test_workflow.py`, `test_readonly_baseline.py`, `test_lifecycle.py` (lifecycle loads workflow.py) | [collaboration-workflow.md](../../project-wiki/references/collaboration-workflow.md), [#packet-kinds](architecture.md#packet-kinds) |
| `project-wiki/scripts/lifecycle.py` | `test_lifecycle.py` | `hooks/claude.json`, `hooks/codex.json`, [hooks-and-gates.md](hooks-and-gates.md) |
| `project-wiki/scripts/edit_gate.py` | `test_edit_gate.py` | `hooks/claude.json`, [maintenance.md#pre-edit-gate-host-delivery-of-wiki-first](../../project-wiki/references/maintenance.md#pre-edit-gate-host-delivery-of-wiki-first) |
| `scripts/package_plugin.py` | `test_plugin_package.py`, `test_legacy_hooks.py`, `test_portable_hooks.py`, `test_package_newlines.py`, `test_package_integrity.py` | `scripts/plugin_doctor.py` (it re-derives the receipt) |
| `scripts/plugin_doctor.py` | `test_plugin_package.py`, `test_package_integrity.py`, `test_package_newlines.py`, `test_codex_inventory.py`, `test_codex_hooks.py`, `test_lifecycle.py` | Receipt fields in `package_plugin.py` |
| `hooks/*.json` | `test_lifecycle.py`, `test_legacy_hooks.py`, `test_edit_gate.py`, `test_portable_hooks.py`, `test_codex_hooks.py` | Packaging profile, [hooks-and-gates.md](hooks-and-gates.md) |
| `project-wiki/SKILL.md`, `project-wiki/references/*.md`, `project-wiki/agents/openai.yaml`, `README.md` | `test_skill_package.py` (metadata; every link and anchor resolves inside the repo) | The owning reference only; no version or caveat paragraph |

Before handing back, run the steps of
[.github/workflows/check.yml](../../.github/workflows/check.yml) (CI runs them on
ubuntu and windows × Python 3.10 and 3.13):

```sh
python -m unittest discover -s tests -v
python -m unittest discover -s evals/fixture-project/tests -v
python project-wiki/scripts/wiki.py check --root evals/fixture-project
python project-wiki/scripts/wiki.py evaluate --root evals/fixture-project --tasks evals/tasks.json
python project-wiki/scripts/wiki.py check --root .
```

This is a public repository. Never name a consumer project, its paths, page numbers,
pull requests, commits or task names. Write "the pilot project" or describe the
mechanism generically.
