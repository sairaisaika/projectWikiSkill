# projectWikiSkill

0.2.12 candidate adapts the optional hook package container to the observed
Codex0.160 loader: `--with-lifecycle-hooks` emits legacy host manifests, while
plain packages stay portable. One canonical identity/skill/workflow is retained.
The version-matched upstream loader explicitly skips portable AgentPlugin hooks;
the actual installed old/new-declaration probes both returned no hooks. See
[the evidence and remaining runtime acceptance](evals/reports/runtime-hook-layout-c120-20261024.md).

0.2.11 candidate declares optional Codex hooks explicitly in the portable root
manifest, with a named source-to-package projection and legacy receipt support.
This follows an actual0.2.10 installation whose hook list was empty; source/package
checks are not runtime discovery. See the [observation and remaining acceptance](evals/reports/portable-hook-declaration-c119-20261024.md).

0.2.10 candidate adds an **optional** internal lifecycle-delivery package profile:
`python scripts/package_plugin.py --with-lifecycle-hooks --output <new-directory>`.
Startup/resume/compaction can deliver an explicitly selected saved task through
the existing snapshot reader. The default package stays skill-only; no trust,
installation, native execution or completion policy is changed by packaging.
See [scope and host requirements](project-wiki/references/collaboration-workflow.md#optional-lifecycle-delivery).
Source tests, package closure and actual trusted host triggering remain separate.

0.2.9 adds explicit `show --snapshot-only` for readers forbidden to invoke
Git. It renders the saved task records without live input checks and clearly
labels currentness as unchecked; default display, dispatch and return guards stay
in place. See [permission-separated reading](project-wiki/references/collaboration-workflow.md#reading-when-the-worker-cannot-invoke-git)
and the [bounded evaluation](evals/reports/snapshot-reading-c103-20261024.md).
Source/main adoption and one official Windows update to0.2.9 are now recorded in
the [bounded adoption return](evals/reports/snapshot-reading-c103-20261024.md#normal-adoption-and-bounded-host-observation).
Installed doctor/helper use and a delivered skill-catalog entry were observed;
hooks, trust, automatic lifecycle and business acceptance remain separate. The
active scoped Claude worker remains0.2.4.

0.2.8 adds optional checkpoint hash observations for explicitly selected
historical evidence files, including private files outside Git. The original
capture/delegate/return workflow refuses a changed or dropped selection; it does
not prevent writes, continuously monitor files or certify business completion.
See [selected evidence](project-wiki/references/collaboration-workflow.md#selected-evidence-files).
Source/package/host adoption remain separate. Its later bounded0.2.8 host receipt
is distinguished from the historical0.2.7 exercise below.

0.2.7 adds an optional comparison between the native router's reported
checkout identities and explicitly selected task peers. The
[C91 exercise](evals/reports/native-source-consistency-c91-20261023.md) preserves
the real mismatch and first policy-retention failure, then records the actual
CLI/full-suite/package checks, normal source/main adoption and one official
Windows update to0.2.7. A real task started using the installed helper's bytes
with strict native-source comparison. Scoped0.2.4 workers remain pinned;
automatic host lifecycle, physical reads and semantic adoption stay separate.

Historical0.2.6 source was normally adopted and one Windows host was updated through the
official CLI, with installed bytes/source and inventory/version observations
checked separately. The new doctor only reads caller-captured host evidence;
installation/enabling does not establish hook execution or agent adoption.
Running scoped workers were not upgraded. See [actual host adoption](evals/reports/codex-inventory-doctor-c77-20261023.md#host-adoption-after-source-merge)
and [doctor observations](docs/PLUGIN_PLAN.md#codex-inventory-observations-026-candidate).

[内部协作插件计划](docs/PLUGIN_PLAN.md)：以现有 Skill/工具为唯一内核，补可复现打包、来源自检与宿主接线，再用真实工程验证开工、委派、收尾与接管。内部插件已在一台 Codex 主机通过官方 CLI 安装并核对缓存，Linux Claude 已做临时加载与真实任务试用；桌面自动生命周期、hooks 与完整跨宿主验收仍待，未公开发布到插件目录。根 `plugin.json` 是身份源，不能单凭它声称运行已验证。0.2.9源码已正常采用，一台 Windows 宿主已更新并实际调用；目录送达、主动读取、hooks 与自动接管分别核验；[换行来源机制](evals/reports/package-newline-provenance-20261022.md)保留原始输入指纹，区分规范文本来源一致与包文件字节完整；[有限宿主采用记录](evals/reports/host-adoption-v025-20261022.md)另证历史官方 Windows CLI 安装0.2.5及实际有限使用。既有 scoped0.2.4 工程任务不由此自动升级。

[协作工作流](project-wiki/references/collaboration-workflow.md)提供原生任务 JSON 的快照、任务包、范围受限的委派和真实 diff 收尾；全部卫星、能力缺口、未展开候选与跨仓版本保留。脚本不派 agent、不自动执行页内检查，也不把结构闭环认证成业务完成。内部插件已有限采用，宿主生命周期与项目试用按计划分别验收。

协同仓库开工时，先核项目实际支持的来源选择参数。原生命令退出成功或印记有效，仍可能读了默认旧仓库；若原生报告提供来源身份，声明 peer 后使用[所选来源核对](project-wiki/references/collaboration-workflow.md#context-capture)，在派工前比较真实 root / HEAD。[C116 使用复盘](evals/reports/native-selection-invocation-c116-20261024.md)保留一次协调者误传环境变量的失败与已有核对能力的实际拒收；这是调用方法修正，没有新增插件或修改宿主。

让项目 Wiki 成为比猜文件名、全仓搜索更省事的工程入口。

可安装 skill 在 [`project-wiki/`](project-wiki/SKILL.md)，名称为 `$project-wiki`。它将问题、精确源码位置、接口契约、规则、影响面、检查与证据边界连接起来；分别量化结构完整度、任务路由表现、语义核验和实际使用效果，避免一个总分掩盖未知。

- [了解项目与导读](project-wiki/references/learning-and-orientation.md)：从产品、角色和跨域例子建立理解；区分全文阅读与导语巡读，理解验收与任务定位分别评价。
- [功能闭环规则](project-wiki/references/feature-completeness.md)：所有功能按用户结果核必要能力与八维证据；文档结构、实现接通、运行验收分别判，缺口不能当完成。
- [结构契约](project-wiki/references/route-contract.md)：接口声明、实现、消费者、规则来源、失败与兼容、精确定位。
- [量化模型](project-wiki/references/quality-model.md)：100 分结构量表、任务命中率与独立演练指标。
- [持续维护](project-wiki/references/maintenance.md)：改动触发、计划交付、漂移检查、CI 与交接。
- [既有 Wiki 接入](project-wiki/references/native-wiki-adoption.md)：复用原生索引与闸，恢复中断审阅，沿生产者、消费者、部署证据核验事实；不强制迁移到第二套 manifest。
- [六图框架](project-wiki/references/diagram-framework.md)：架构、流程、时序、数据模型、部署、状态六种视角的职责与项目级覆盖检查。
- [工程深度](project-wiki/references/engineering-depth.md)：字段/单位/字节布局、状态守卫与上下文、重试和资源边界、轻量决策记录。
- [复合改动定位](project-wiki/references/change-navigation.md)：任务地图、内部编辑接缝、捕获范围、共用规则与完整工作面验收。

## 使用

将整个 `project-wiki` 文件夹放入目标工具支持的 skills 目录，或通过支持 GitHub 子目录的 skill 安装器从本仓 `project-wiki` 子目录安装。安装位置由用户决定，仓库内容不自动修改本机配置。

Python 3.10+ 即可运行工具，无第三方依赖：

```sh
python project-wiki/scripts/wiki.py query --root <project> "外部源端口"
python project-wiki/scripts/wiki.py task --root <project>
python project-wiki/scripts/wiki.py task <task-id> --root <project>
python project-wiki/scripts/wiki.py audit --root <project>
python project-wiki/scripts/wiki.py build --root <project>
python project-wiki/scripts/wiki.py check --root <project>
python project-wiki/scripts/wiki.py evaluate --root <project> --tasks <tasks.json>
```

可以先在本仓完整样例上运行：

```sh
python project-wiki/scripts/wiki.py build --root evals/fixture-project
python project-wiki/scripts/wiki.py evaluate --root evals/fixture-project --tasks evals/tasks.json
python -m unittest discover -s tests -v
```

六图样例的可选渲染验收使用 `node evals/render-diagrams.mjs`，需要可用的 Playwright 与 Chrome；可用 `WIKI_PLAYWRIGHT_MODULE` 指向已有模块、`WIKI_BROWSER_CHANNEL` 选择浏览器。工具不自动安装依赖，默认输出到临时目录；Mermaid CDN 可由 `WIKI_MERMAID_URL` 指定固定版本。核心 Python 工具仍无第三方依赖。

结构分、合成样例、自己演练和陌生执行者盲测分别报告；它们均不等于真实业务、部署或外部 API 已验证。仅 `build` 写生成索引；其余命令不执行目标项目或清单中的检查命令。

项目起源于两个共用 Wiki 的开源仓库的接口改进演练；skill 是通用工程方法，不要求固定技术栈、固定页数或每个功能画六张图。

[验证记录](evals/reports/README.md)包含结构评分、任务自测、一次独立只读试用及已有真实项目的兼容审计。试用发现的“复合查询截断”和“失败模式不够细”已经反馈到 skill、结构字段与回归测试。
