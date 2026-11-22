<div align="center">

# ProjectWikiSkill

**一个可独立使用的 Skill，让工程问题连到项目自己的 Wiki、源码与检查。**

[English](README.md) · **简体中文**

[快速试用](README.zh-CN.md#quick-start) · [安装 Skill](README.zh-CN.md#install) · [PWS 自用 Wiki](docs/wiki/engineering-entry.md)

</div>

---

<a name="quick-start"></a>
## 快速开始

无需 Agent、插件或 API key。准备 **Python 3.10+**，在本仓库的检出目录运行：

```sh
python3 project-wiki/scripts/wiki.py query \
  --root evals/fixture-project \
  "service client failures" --limit 1
```

仓内离线样例的部分实际输出：

```text
public-api: Public article service and legacy client
  rule: Unavailable must not become an empty article list.
  tests: tests/test_contracts.py tests/test_diagnostic_evidence.py
```

一个问题，找到[契约](evals/fixture-project/docs/wiki/interfaces.md#public-api) → [实现](evals/fixture-project/src/service.py) → [调用方](evals/fixture-project/src/client.py) → [检查](evals/fixture-project/tests/test_contracts.py)。[样例契约](evals/fixture-project/docs/wiki/interfaces.md#public-api)保留了 `None`（不可用）和 `[]`（成功但没有结果）的区别。查询负责定位证据，不会替你执行检查，也不证明真实服务的运行情况。

Python 工具只使用标准库。先用 `python3 --version` 确认版本；低于 3.10 时，换用机器上已安装的兼容解释器。

<a name="install"></a>
<a name="使用"></a>
<a name="独立-skill-与-python-工具"></a>
## 安装

可移植的单元是**整个 [`project-wiki/` 目录](project-wiki/SKILL.md)**。保留其中的 `SKILL.md`、`references/`、`scripts/` 和配套元数据，按宿主文档复制到 Skill 目录；只复制 `SKILL.md` 会缺少指南和工具。

<a name="codex作为独立-skill-安装"></a>

| 宿主 | 项目内位置 | 调用方式 |
| --- | --- | --- |
| [Codex](https://developers.openai.com/codex/skills) | `.agents/skills/project-wiki/` | `$project-wiki` |
| [Claude Code](https://code.claude.com/docs/en/skills) | `.claude/skills/project-wiki/` | `/project-wiki` |

用户级目录和发现机制以各宿主的上述文档为准。其他宿主在**其文档明确支持 Skill 的范围内**可使用同一目录；这不代表特定宿主的安装或 hooks 已经过验证。独立 Skill 路径不添加 hooks，也不修改宿主配置。

<a name="在-claude-code-安装插件"></a>
<a name="claude-code通过插件市场安装"></a>
<details>
<summary><strong>另一种方式：Claude Code Marketplace</strong></summary>

```sh
claude plugin marketplace add sairaisaika/projectWikiSkill
claude plugin install project-wiki@project-wiki
```

在新会话中调用 `/project-wiki:project-wiki`。本仓库的市场入口提供一个 Skill，不含 hooks。用 `/plugin` 查看组件；若已从其他市场装过同名插件，先用 `claude plugin list` 确认再选择来源。详见 [Claude 插件指南](https://code.claude.com/docs/en/discover-plugins)。

</details>

## 用到自己的项目

从[任务菜单](project-wiki/SKILL.md#choose-the-work)开始：可以直接阅读 Markdown，也可以通过宿主的 Skill 入口使用。例如：

> 修改这个 API 的错误处理之前，先找出它的 Wiki 契约、生产者、调用方和检查。核对相关源码，再把决策和证据回写到原来的负责页面。

**提问 → 定位 → 核对 → 回写。** 项目自己的 Wiki 仍是事实来源。[沿用已有导航和检查](project-wiki/references/native-wiki-adoption.md)，不必另造 Wiki、维护第二套索引或采用固定文档结构。已知文件里的小改动，继续走项目原有的轻量路径。

上面的 demo 使用本仓库的路由格式。接入自己的 Wiki 时，先按接入指南选择工具；缺少 `routes.json` 不意味着应该替换项目已有的导航。

<a name="guides"></a>
## 阅读指南

| 当前任务 | 接着读 |
| --- | --- |
| 理解项目、规划改动 | [项目导读](project-wiki/references/learning-and-orientation.md) · [改动定位](project-wiki/references/change-navigation.md) |
| 说明行为、契约或图表 | [工程深度](project-wiki/references/engineering-depth.md) · [图表视角](project-wiki/references/diagram-framework.md) |
| 维护知识、安排新文件 | [Wiki 演进](project-wiki/references/wiki-evolution.md) · [持续维护](project-wiki/references/maintenance.md) · [文件归位](project-wiki/references/repository-hygiene.md#file-placement) |
| 交接任务、核对交付结果 | [协作流程](project-wiki/references/collaboration-workflow.md) · [功能闭环](project-wiki/references/feature-completeness.md) |

<a name="cli-reference"></a>
## 命令行工具

需要细节时，直接查已有参考：

- **查询、审计和检查 Wiki：** [Wiki 工具契约](docs/wiki/architecture.md#wiki-helper)与[路由格式](project-wiki/references/route-contract.md)。
- **准备上下文或交接任务：** [工作流命令](project-wiki/references/collaboration-workflow.md)。
- **盘点存储、打包或校验来源：** [存储盘点](project-wiki/references/maintenance.md#inventory-storage-without-cleaning-it)、[打包](docs/wiki/architecture.md#packaging)与[doctor](docs/wiki/architecture.md#doctor)。

<details>
<summary><strong>可选 hooks 与进一步检查</strong></summary>

[生命周期投递](project-wiki/references/collaboration-workflow.md#optional-lifecycle-delivery)说明可选的 `SessionStart` 集成和仅适用于 Claude 的 `PreToolUse` 编辑闸。它们与独立 Skill、Python demo 分开；打包不等于安装或授予 hooks 信任。

继续运行样例的结构检查：

```sh
python3 project-wiki/scripts/wiki.py check --root evals/fixture-project
python3 project-wiki/scripts/wiki.py evaluate --root evals/fixture-project --tasks evals/tasks.json
```

进一步验证见[仓库检查入口](docs/wiki/engineering-entry.md#per-change-surface-convention)、[可选图表渲染](evals/render-diagrams.mjs)和[质量模型](project-wiki/references/quality-model.md)。结构、源码正确性和实际使用是不同层次的证据。

</details>

<a name="repository-status"></a>
## 仓库状态

PWS 用自己的[维护者 Wiki](docs/wiki/engineering-entry.md)记录架构、契约、维护与检查。参与本仓库开发，从这里进入。

[版本状态](docs/wiki/status.md#current-state) · [权威 manifest](plugin.json) · [更新记录](CHANGELOG.md) · [验证报告](evals/reports/README.md)
