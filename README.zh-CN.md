# ProjectWikiSkill

[English](README.md) · **简体中文**

**从一个工程问题出发，找到它实际涉及的源码、契约和检查。**

ProjectWikiSkill（PWS）是一个帮助你建设和使用工程 Wiki 的 Skill。项目自己的 Wiki 仍是事实来源；PWS 帮团队和 Agent 找对页面、核对源码，也帮下一位接手的人知道该从哪继续。已有 Wiki 不必重建，不需要维护第二套索引，也不用换掉项目原有的检查。

[试跑样例](README.zh-CN.md#quick-start) · [安装](README.zh-CN.md#install) · [命令行工具](README.zh-CN.md#cli-reference) · [维护本仓库](docs/wiki/engineering-entry.md)

<a name="quick-start"></a>
## 快速开始

**不装插件也能试跑。** 在本仓库的检出目录运行：

```sh
python project-wiki/scripts/wiki.py query --root evals/fixture-project "service client failures" --limit 1
```

样例返回 `public-api`，定位到[接口契约](evals/fixture-project/docs/wiki/interfaces.md#public-api)、[接口声明](evals/fixture-project/src/ports.py)、[服务实现](evals/fixture-project/src/service.py)和[旧版调用方](evals/fixture-project/src/client.py)。动手前就能看到该保留的区别：源返回 `None` 是**不可用**，返回 `[]` 是**查询成功但没有结果**。查询会指出离线检查在哪里，不会替你执行检查，也不代表真实服务通过验证。

**在自己的项目里**，先从 [Skill 的任务入口](project-wiki/SKILL.md#choose-the-work)提出一个具体工程问题，读相关 Wiki 章节，再核对它指向的实现。如果项目已有导航和检查，就[沿用现有做法](project-wiki/references/native-wiki-adoption.md)。已知文件里改个错字，不必再跑一遍 PWS 专项流程。

<a name="install"></a>
## 使用

### Claude Code：通过插件市场安装

```sh
claude plugin marketplace add sairaisaika/projectWikiSkill
claude plugin install project-wiki@project-wiki
```

在新的 Claude Code 会话中调用 `/project-wiki:project-wiki`。用 Claude Code 的 `/plugin` 面板查看已安装的组件。如果已从本地市场装过同名插件，先用 `claude plugin list` 确认，再选择安装来源。本仓库的市场入口只包含一个 Skill，不含 hooks。详见 [Claude Code 插件文档](https://code.claude.com/docs/en/discover-plugins)。

### Codex：作为独立 Skill 安装

把[整个 `project-wiki/` 目录](project-wiki/SKILL.md)复制到以下任一 [Codex Skill 目录](https://developers.openai.com/codex/skills)：

| 生效范围 | 目标位置 |
| --- | --- |
| 单个项目 | `<project>/.agents/skills/project-wiki/` |
| 当前用户 | `~/.agents/skills/project-wiki/` |

保留目录里的 `SKILL.md`、`references/` 和 `scripts/`。在 Codex 中调用 `$project-wiki`；如果未出现，重启 Codex。其他支持独立 Skill 的工具可按自己的文档放置同一目录。这种方式不安装 hooks，也不管理宿主配置。

<a name="cli-reference"></a>
## 命令行工具

需要 **Python 3.10 或更高版本**，无需第三方 Python 依赖。macOS 自带的 `python3` 可能低于最低要求，可先运行 `python3 --version`，再用已安装且兼容的解释器替换示例中的 `python`。各平台实际核验过什么，见[版本状态](docs/wiki/status.md#current-state)。

| 工具 | 命令与边界 |
| --- | --- |
| [`wiki.py`](project-wiki/scripts/wiki.py) | `query`、`task [id]`、`list`、`audit`、`build`、`check`、`evaluate`。读取目标根目录下的 `docs/wiki/routes.json`（schema 1 或 2）。只有 `build` 写入生成的路由索引；工具不执行 Wiki 列出的检查命令。 |
| [`workflow.py`](project-wiki/scripts/workflow.py) | `prepare`、`capture`、`capture-return`、`start`、`delegate`、`show`、`review-template`、`finish`、`update-state`、`show-state`、`apply-state`。只有明确提供项目原生命令的参数列表并允许执行，工具才会运行它。用 `show --snapshot-only` 读取已保存的上下文，不读取当前项目。显式应用状态更新时，只改动已绑定到保存计划且未发生变化的 Wiki 页面。详见[协作流程](project-wiki/references/collaboration-workflow.md)。 |
| [`storage_inventory.py`](project-wiki/scripts/storage_inventory.py) | `--root PATH`；可选 `--exclude PATH`、`--max-entries N`、`--max-depth N`。有范围限制的只读元数据盘点；统计大小不是可回收空间，也不判断哪些内容可以删。 |
| [`package_plugin.py`](scripts/package_plugin.py) | `--output <new-directory>`；可选 `--with-lifecycle-hooks` 和 `--hook-layout legacy\|portable`。默认只打包 Skill，不写入宿主配置。 |
| [`plugin_doctor.py`](scripts/plugin_doctor.py) | `--package <package>`，可选 `--source <checkout>` 和已保存的宿主信息（`--claude-transcript`、`--codex-inventory`、`--codex-marketplace`、`--codex-version-file`、`--codex-hooks`、`--codex-hooks-cwd`）。检查包、源码和提供的证据，不启用、信任或执行 hooks。 |
| [`edit_gate.py`](project-wiki/scripts/edit_gate.py) | 从标准输入读取一条 Claude `PreToolUse` 事件。可选，只在含有 `.project-wiki/edit-gate.json` 的检出目录中生效。 |

[可选 hooks 打包配置](project-wiki/references/collaboration-workflow.md#optional-lifecycle-delivery)为 Codex 和 Claude 加入 `SessionStart` 已保存上下文投递，另为 Claude 加入 `PreToolUse` 编辑闸。打包不等于安装、受信任或执行成功。

继续验证本地样例：

```sh
python project-wiki/scripts/wiki.py check --root evals/fixture-project
python project-wiki/scripts/wiki.py evaluate --root evals/fixture-project --tasks evals/tasks.json
python -m unittest discover -s tests -v
```

[图表渲染](evals/render-diagrams.mjs)是可选检查。已有 Playwright 和 Chrome 时，运行 `node evals/render-diagrams.mjs`。`WIKI_PLAYWRIGHT_MODULE`、`WIKI_BROWSER_CHANNEL`、`WIKI_MERMAID_URL` 分别指定模块、浏览器渠道和 Mermaid 地址。默认输出到临时目录，不安装任何依赖；能渲染不等于图表内容准确。

## 阅读指南

| 我想…… | 从这里开始 |
| --- | --- |
| 理解项目，或者定位跨文件改动 | [项目导读](project-wiki/references/learning-and-orientation.md) · [复合改动定位](project-wiki/references/change-navigation.md) |
| 描述接口、失败方式和系统视图 | [路由契约](project-wiki/references/route-contract.md) · [工程深度](project-wiki/references/engineering-depth.md) · [六种图表视角](project-wiki/references/diagram-framework.md) |
| 接入、更新或维护现有 Wiki | [接入既有 Wiki](project-wiki/references/native-wiki-adoption.md) · [Wiki 演进](project-wiki/references/wiki-evolution.md) · [持续维护](project-wiki/references/maintenance.md) |
| 确认设计记录与开发资源分别放哪 | [文件归位](project-wiki/references/repository-hygiene.md#file-placement) |
| 交接任务，或者核对功能是否真正交付 | [协作流程](project-wiki/references/collaboration-workflow.md) · [功能闭环规则](project-wiki/references/feature-completeness.md) |
| 评估 Wiki 质量和实际使用 | [量化模型](project-wiki/references/quality-model.md) · [验证记录](evals/reports/README.md) |

PWS 不限定技术栈、页面数，也不要求每个功能画六张图。结构检查、任务路由、源码核验和观察到的实际使用，是不同层次的证据。

## 仓库状态

维护 PWS 本身，请从[维护者 Wiki](docs/wiki/engineering-entry.md)进入。[版本状态](docs/wiki/status.md#current-state)分别记录已核验的源码、CI、包、宿主安装和实际使用。当前检出声明的版本看 [`plugin.json`](plugin.json)，历史改动看 [CHANGELOG](CHANGELOG.md)。
