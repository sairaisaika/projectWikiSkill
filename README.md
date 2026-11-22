# ProjectWikiSkill

Find the Wiki, code and tests behind an engineering question — and keep what you learn with the project.

**English** · [简体中文](README.zh-CN.md)

[Try the example](README.md#quick-start) · [Use with your agent](README.md#install) · [Explore PWS's Wiki](docs/wiki/engineering-entry.md)

## One question, a useful starting point

> How are service client failures handled?

In the included example, that question leads to:

- **Wiki →** [the public API contract](evals/fixture-project/docs/wiki/interfaces.md#public-api): unavailable is different from a successful empty result.
- **Code →** [the service](evals/fixture-project/src/service.py) that reports the error, and [the client](evals/fixture-project/src/client.py) that consumes it.
- **Tests →** [contract checks](evals/fixture-project/tests/test_contracts.py) and [diagnostic evidence](evals/fixture-project/tests/test_diagnostic_evidence.py) to verify before changing the behavior.

PWS provides a reusable Skill for following this path in your project's own Wiki. You can read it directly, give it to a coding agent, or run the optional Python helpers yourself.

## Quick start

**Run the offline example.** No agent, plugin or API key is needed. From a checkout of this repository, confirm **Python 3.10+** with `python --version`, then paste this single line (also suitable for Windows PowerShell):

```sh
python project-wiki/scripts/wiki.py query --root evals/fixture-project "How are service client failures handled?" --limit 1
```

The result names `public-api`, links the contract and source locations above, and identifies the two test files. It locates checks; it does not execute them or prove live service behavior.

The helpers use only the Python standard library. On macOS/Linux, if your compatible interpreter is named `python3`, confirm `python3 --version` and use `python3` instead.

<a name="使用"></a>
<a name="独立-skill-与-python-工具"></a>
## Install

The reusable unit is the **whole [`project-wiki/` directory](project-wiki/SKILL.md)**, including its references, scripts and metadata. Choose the path your tools support:

### Any coding agent that can read project files

Check out this repository where your agent can read it, or copy the whole directory into a project-approved, shareable location. Then explicitly ask the agent to use it:

> Read `project-wiki/SKILL.md` first. For this task, follow the relevant linked references and the project's existing Wiki. Find the owning pages, verify the source and checks, and return durable decisions and evidence to their existing owner.

Adjust that entry path to its actual location. This is **explicit use** of project files; it does not register the Skill or promise automatic discovery.

### A host with a Skill loader

Place the same whole directory in the host's **documented Skill discovery path**, then use its documented invocation. Discovery and compatibility depend on the host; no universal installer is assumed.

<a name="codex-standalone-skill"></a>
<a name="在-claude-code-安装插件"></a>
<a name="claude-code-marketplace-plugin"></a>
<details>
<summary><strong>Optional host setup: Codex, Claude Code, Marketplace and hooks</strong></summary>

- **[Codex](https://developers.openai.com/codex/skills):** project-local `.agents/skills/project-wiki/`; invoke `$project-wiki`.
- **[Claude Code](https://code.claude.com/docs/en/skills):** project-local `.claude/skills/project-wiki/`; invoke `/project-wiki`.

Follow each host's documentation for user-wide paths and discovery. These examples do not establish support for other hosts or their hooks.

**Claude Code Marketplace** is another optional entry:

```sh
claude plugin marketplace add sairaisaika/projectWikiSkill
claude plugin install project-wiki@project-wiki
```

In a new session, invoke `/project-wiki:project-wiki`. This marketplace entry exposes one Skill, without hooks. Inspect components with `/plugin`; if another marketplace supplies the same name, check `claude plugin list` before choosing a source. See [Claude's plugin guide](https://code.claude.com/docs/en/discover-plugins).

Optional `SessionStart` integration and the Claude-only `PreToolUse` gate are documented in [lifecycle delivery](project-wiki/references/collaboration-workflow.md#optional-lifecycle-delivery). They are separate from explicit use and the Python demo; packaging does not install or grant trust to hooks.

</details>

## Use it on your project

**Ask → locate → verify → return.** Start at the [task menu](project-wiki/SKILL.md#choose-the-work). Your native Wiki stays the authority: [reuse its navigation and checks](project-wiki/references/native-wiki-adoption.md), and leave a small edit in a known file on the project's lightweight path.

The runnable example uses PWS's route format. For an existing project, choose helpers through the adoption guide; a missing `routes.json` is not a reason to replace the project's own navigation.

<a name="cli-reference"></a>
## Guides

- **Choose a task:** the [Skill's task menu](project-wiki/SKILL.md#choose-the-work) links to the relevant method, from orientation to maintenance and handoff.
- **Use the Python tools:** the [Wiki helper contract](docs/wiki/architecture.md#wiki-helper) and [workflow commands](project-wiki/references/collaboration-workflow.md) explain inputs, outputs and limits.
- **Contribute to PWS:** the [maintainer entry](docs/wiki/engineering-entry.md) owns architecture, packaging and repository checks.

## Repository status

For verified versions and evidence, see [status](docs/wiki/status.md#current-state), the [canonical manifest](plugin.json), [changelog](CHANGELOG.md) and [evaluation reports](evals/reports/README.md).
