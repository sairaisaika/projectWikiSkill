# ProjectWikiSkill

**English** · [简体中文](README.zh-CN.md)

**Go from an engineering question to the exact code, contracts, and checks it touches.**

ProjectWikiSkill (PWS) is a skill for building and using a source-backed project Wiki. The project's own Wiki remains the source of truth; PWS helps people and agents find the right page, verify the relevant source, and leave a useful handoff. It works with an existing Wiki without requiring a second index or replacing the project's checks.

[Try the example](README.md#quick-start) · [Install](README.md#install) · [CLI reference](README.md#cli-reference) · [Maintain this repository](docs/wiki/engineering-entry.md)

## Quick start

**Try it without installing a plugin.** From a checkout of this repository, run:

```sh
python project-wiki/scripts/wiki.py query --root evals/fixture-project "service client failures" --limit 1
```

The example returns `public-api` and points to the [contract](evals/fixture-project/docs/wiki/interfaces.md#public-api), the [declaration](evals/fixture-project/src/ports.py), the [service](evals/fixture-project/src/service.py), and the [legacy caller](evals/fixture-project/src/client.py). It exposes a distinction worth preserving before editing: a source returning `None` means **unavailable**; returning `[]` means **success with no results**. The query points to offline checks. It does not run them or verify a live service.

**In your own project**, [start with the skill](project-wiki/SKILL.md#choose-the-work), ask a concrete engineering question, and read the relevant Wiki section before inspecting the named implementation. If your Wiki already has its own navigation and checks, [reuse those](project-wiki/references/native-wiki-adoption.md). A routine edit in a known file does not need an extra PWS workflow.

<a name="使用"></a>
## Install

### Claude Code: marketplace plugin

```sh
claude plugin marketplace add sairaisaika/projectWikiSkill
claude plugin install project-wiki@project-wiki
```

In a new Claude Code session, invoke `/project-wiki:project-wiki`. Use Claude Code’s `/plugin` panel to inspect the installed components. If a local marketplace already provides a plugin with this name, check `claude plugin list` before choosing an installation source. This repository's marketplace entry includes one skill and no hooks. See [Claude Code's plugin guide](https://code.claude.com/docs/en/discover-plugins).

### Codex: standalone skill

Copy the [entire `project-wiki/` directory](project-wiki/SKILL.md) into one of these [Codex skill locations](https://developers.openai.com/codex/skills):

| Scope | Destination |
| --- | --- |
| One project | `<project>/.agents/skills/project-wiki/` |
| Your user account | `~/.agents/skills/project-wiki/` |

Keep `SKILL.md`, `references/`, and `scripts/` together. Invoke `$project-wiki` in Codex; if it doesn't appear, restart Codex. For another host that supports standalone skills, copy the same directory to that host's documented skill location. This option does not install hooks or manage host configuration.

## CLI reference

**Python 3.10+**, with no third-party Python dependencies. Use an interpreter that meets the minimum; on macOS, the system `python3` may be older. Check with `python3 --version`, and replace `python` below with an installed compatible interpreter if needed. See [version status](docs/wiki/status.md#current-state) for what was verified on each platform.

| Tool | Commands and boundaries |
| --- | --- |
| [`wiki.py`](project-wiki/scripts/wiki.py) | `query`, `task [id]`, `list`, `audit`, `build`, `check`, `evaluate`. Reads schema 1 or 2 at `docs/wiki/routes.json` under the chosen root. Only `build` writes its generated route index; the helper never runs checks listed in the Wiki. |
| [`workflow.py`](project-wiki/scripts/workflow.py) | `prepare`, `capture`, `capture-return`, `start`, `delegate`, `show`, `review-template`, `finish`, `update-state`, `show-state`, `apply-state`. A native program runs only when its argument list and execution are explicitly supplied and approved. Use `show --snapshot-only` for saved context without live reads. Explicit state apply is scoped to the unchanged Wiki page bound to the saved plan. See [the collaboration guide](project-wiki/references/collaboration-workflow.md). |
| [`storage_inventory.py`](project-wiki/scripts/storage_inventory.py) | `--root PATH`, optional `--exclude PATH`, `--max-entries N`, `--max-depth N`. Bounded, read-only metadata inventory; reported sizes are not reclaimable space, and the tool does not decide what may be deleted. |
| [`package_plugin.py`](scripts/package_plugin.py) | `--output <new-directory>`; optional `--with-lifecycle-hooks` and `--hook-layout legacy\|portable`. Builds a skill-only package by default and does not write host configuration. |
| [`plugin_doctor.py`](scripts/plugin_doctor.py) | `--package <package>`, optional `--source <checkout>` and saved host inputs (`--claude-transcript`, `--codex-inventory`, `--codex-marketplace`, `--codex-version-file`, `--codex-hooks`, `--codex-hooks-cwd`). Inspects the package, source, and supplied evidence; does not enable, trust, or run hooks. |
| [`edit_gate.py`](project-wiki/scripts/edit_gate.py) | Reads one Claude `PreToolUse` event from stdin. Optional, and active only in a checkout with `.project-wiki/edit-gate.json`. |

The [optional hook profile](project-wiki/references/collaboration-workflow.md#optional-lifecycle-delivery) adds Codex and Claude `SessionStart` saved-context delivery and the Claude-only `PreToolUse` gate. Packaging is not installation, host trust, or proof the hook ran.

To try the rest of the local fixture workflow:

```sh
python project-wiki/scripts/wiki.py check --root evals/fixture-project
python project-wiki/scripts/wiki.py evaluate --root evals/fixture-project --tasks evals/tasks.json
python -m unittest discover -s tests -v
```

For [optional diagram rendering](evals/render-diagrams.mjs), run `node evals/render-diagrams.mjs` with Playwright and Chrome already available. `WIKI_PLAYWRIGHT_MODULE`, `WIKI_BROWSER_CHANNEL`, and `WIKI_MERMAID_URL` select the module, browser channel, and Mermaid URL. Output goes to a temporary directory by default; the script installs nothing. Rendering does not verify diagram accuracy.

## Guides

| I want to… | Start here |
| --- | --- |
| Learn a project or locate a multi-file change | [Orientation](project-wiki/references/learning-and-orientation.md) · [Change navigation](project-wiki/references/change-navigation.md) |
| Describe an interface, failure mode, or system view | [Route contract](project-wiki/references/route-contract.md) · [Engineering depth](project-wiki/references/engineering-depth.md) · [Six diagram views](project-wiki/references/diagram-framework.md) |
| Reuse, update, or maintain an existing Wiki | [Native Wiki adoption](project-wiki/references/native-wiki-adoption.md) · [Wiki evolution](project-wiki/references/wiki-evolution.md) · [Maintenance](project-wiki/references/maintenance.md) |
| Decide where design records and development resources belong | [File placement](project-wiki/references/repository-hygiene.md#file-placement) |
| Hand work off or check what a feature actually delivers | [Collaboration workflow](project-wiki/references/collaboration-workflow.md) · [Feature completeness](project-wiki/references/feature-completeness.md) |
| Judge Wiki quality or actual use | [Quality model](project-wiki/references/quality-model.md) · [Evaluation reports](evals/reports/README.md) |

PWS does not require a particular stack, a fixed number of pages, or six diagrams per feature. Structural checks, routing results, source verification, and observed use are different kinds of evidence.

## Repository status

For work on PWS itself, start at the [maintainer Wiki](docs/wiki/engineering-entry.md). [Version status](docs/wiki/status.md#current-state) separates verified source, CI, packages, host installations, and observed use. See [`plugin.json`](plugin.json) for the version declared by this checkout and [CHANGELOG](CHANGELOG.md) for history.
