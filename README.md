<div align="center">

# ProjectWikiSkill

**A portable Skill that connects engineering questions to your project's Wiki, code and checks.**

**English** · [简体中文](README.zh-CN.md)

[Quick start](README.md#quick-start) · [Install the Skill](README.md#install) · [PWS's own Wiki](docs/wiki/engineering-entry.md)

</div>

---

## Quick start

No Agent, plugin or API key needed. Confirm **Python 3.10+** with `python --version`, then run this single line from a checkout of the repository. For Windows PowerShell, use this same command:

```sh
python project-wiki/scripts/wiki.py query --root evals/fixture-project "service client failures" --limit 1
```

Selected output from the included offline example:

```text
public-api: Public article service and legacy client
  rule: Unavailable must not become an empty article list.
  tests: tests/test_contracts.py tests/test_diagnostic_evidence.py
```

One question leads to the [contract](evals/fixture-project/docs/wiki/interfaces.md#public-api) → [implementation](evals/fixture-project/src/service.py) → [consumer](evals/fixture-project/src/client.py) → [checks](evals/fixture-project/tests/test_contracts.py). The [example contract](evals/fixture-project/docs/wiki/interfaces.md#public-api) keeps `None` (unavailable) distinct from `[]` (successful, empty result). The query locates evidence; it does not run the checks or prove live service behavior.

The Python helpers use only the standard library. On macOS/Linux, if your compatible interpreter is named `python3`, check `python3 --version` and replace `python` above with `python3`.

<a name="使用"></a>
<a name="独立-skill-与-python-工具"></a>
## Install

The portable unit is the **entire [`project-wiki/` directory](project-wiki/SKILL.md)**. Keep `SKILL.md`, `references/`, `scripts/` and the bundled metadata together. Copy that directory to your host's documented Skill location; copying `SKILL.md` alone loses its guides and tools.

<a name="codex-standalone-skill"></a>

| Host | Project-local location | Invoke |
| --- | --- | --- |
| [Codex](https://developers.openai.com/codex/skills) | `.agents/skills/project-wiki/` | `$project-wiki` |
| [Claude Code](https://code.claude.com/docs/en/skills) | `.claude/skills/project-wiki/` | `/project-wiki` |

For user-wide locations and discovery behavior, follow the linked host documentation. Other hosts can use the same directory **where their documented Skill support allows it**; that does not establish host-specific installation or hook compatibility. This standalone path adds no hooks or host configuration.

<a name="在-claude-code-安装插件"></a>
<a name="claude-code-marketplace-plugin"></a>
<details>
<summary><strong>Alternative: Claude Code Marketplace</strong></summary>

```sh
claude plugin marketplace add sairaisaika/projectWikiSkill
claude plugin install project-wiki@project-wiki
```

In a new session, invoke `/project-wiki:project-wiki`. This repository's marketplace entry exposes one Skill, without hooks. Use `/plugin` to inspect components; if another marketplace already supplies the same name, check `claude plugin list` before choosing a source. See [Claude's plugin guide](https://code.claude.com/docs/en/discover-plugins).

</details>

## Use it on your project

Start with the [task menu](project-wiki/SKILL.md#choose-the-work), either directly in Markdown or through your host's Skill entry. For example:

> Before changing this API's error handling, find its Wiki contract, producer, consumers and checks. Verify the relevant source, then return the decision and evidence to the existing owner.

**Ask → locate → verify → return.** Your project's Wiki remains the authority. [Reuse its existing navigation and checks](project-wiki/references/native-wiki-adoption.md); PWS does not require a parallel Wiki, another index or a fixed documentation layout. A small edit in a known file stays on the project's lightweight path.

The demo uses this repository's route format. For your own Wiki, follow the adoption guide before choosing a helper; a missing `routes.json` is not a reason to replace an existing native router.

## Guides

| Your task | Read next |
| --- | --- |
| Understand a project or plan a change | [Orientation](project-wiki/references/learning-and-orientation.md) · [Change navigation](project-wiki/references/change-navigation.md) |
| Explain behavior, contracts or diagrams | [Engineering depth](project-wiki/references/engineering-depth.md) · [Diagram views](project-wiki/references/diagram-framework.md) |
| Maintain knowledge and place new files | [Wiki evolution](project-wiki/references/wiki-evolution.md) · [Maintenance](project-wiki/references/maintenance.md) · [File placement](project-wiki/references/repository-hygiene.md#file-placement) |
| Hand work off and verify what was delivered | [Collaboration](project-wiki/references/collaboration-workflow.md) · [Feature completeness](project-wiki/references/feature-completeness.md) |

## CLI reference

Use the existing references when you need details:

- **Query, audit and check a Wiki:** [Wiki helper contract](docs/wiki/architecture.md#wiki-helper) and [route format](project-wiki/references/route-contract.md).
- **Prepare context or hand work off:** [workflow commands](project-wiki/references/collaboration-workflow.md).
- **Inspect storage, build a package or check its provenance:** [storage inventory](project-wiki/references/maintenance.md#inventory-storage-without-cleaning-it), [packaging](docs/wiki/architecture.md#packaging) and [doctor](docs/wiki/architecture.md#doctor).

<details>
<summary><strong>Optional hooks and additional checks</strong></summary>

[Lifecycle delivery](project-wiki/references/collaboration-workflow.md#optional-lifecycle-delivery) describes optional `SessionStart` integration and the Claude-only `PreToolUse` gate. These are separate from the standalone Skill and Python demo; packaging does not install or grant trust to hooks.

Run the example's structural checks with:

```sh
python3 project-wiki/scripts/wiki.py check --root evals/fixture-project
python3 project-wiki/scripts/wiki.py evaluate --root evals/fixture-project --tasks evals/tasks.json
```

[Repository checks](docs/wiki/engineering-entry.md#per-change-surface-convention), [optional diagram rendering](evals/render-diagrams.mjs) and the [quality model](project-wiki/references/quality-model.md) cover deeper validation. Structure, source correctness and actual use are separate evidence.

</details>

## Repository status

PWS uses its own [maintainer Wiki](docs/wiki/engineering-entry.md) for architecture, contracts, maintenance and checks. Start there when contributing to this repository.

[Version status](docs/wiki/status.md#current-state) · [Canonical manifest](plugin.json) · [Changelog](CHANGELOG.md) · [Evaluation reports](evals/reports/README.md)
