# Changelog

> Reviewed: 2026-11-03 against c062224

Version history, newest first. Current per-version status (CI, main, package,
installation, hooks, use) is one table in [docs/wiki/status.md](docs/wiki/status.md);
evidence lives in [evals/reports/](evals/reports/README.md). The fuller per-version
plan narrative stays in [docs/PLUGIN_PLAN.md](docs/PLUGIN_PLAN.md) and the session
log in [PROJECT.md » History](PROJECT.md#history); entries below point to them
instead of copying them.

The version entries from 0.2.19 down to 0.2.6 were moved from README.md on 2026-11-03
(spacing normalized); the former README section "Historical source and host observations"
became these version entries. The following notes describe their own revisions and host
scopes, not the current installation state of every reader.

## 0.2.27

Recognize dated current-state headings through the existing common projection and state rotation. Keep their dates visible as authored labels, archive replaced headings verbatim, and remove the old heading date from new state. Fenced/history/nondate headings and older saved projections retain their boundaries. Evidence and verification layers: [status](docs/wiki/status.md#current-state).

## 0.2.26

Captured page/history reads and state updates accept a saved Wiki key or its
repository-relative path, without probing new files. Both target the same saved
page; ambiguity is rejected. Missing keys now differ from captures without page
views. [Actual-task failure and replay](evals/reports/captured-page-path-20261107.md).

## 0.2.25

Identical current `prepare` calls now return a small saved-context locator instead
of repeating the file/owner index. First preparation and explicit summary/JSON
reading keep complete scope; locator continuations and snapshot-only remain bounded.
See [the measured task and counterexamples](evals/reports/reuse-locator-20261107.md).

## 0.2.24

- Add `apply-state --plan` to apply the exact reviewed state proposal without
  repeating body/verification arguments or regenerating the plan. Existing
  source-byte and target checks remain; receipts expose the exact command.
- Clarify the verification-line input shape; retain the existing combined apply.

## 0.2.23

- Keep state snapshots outside following generated blocks and preserve recognized
  generated openers when replacing current sections; verify native regeneration.
- Add a bounded, read-only `show-state` view of saved state proposals and diffs,
  with resumable byte/line cursors and explicit complete JSON export.
- Retain exact original page bytes in new preview artifacts and add a reader
  command to the existing compact receipt. Older plans stay readable as proposals;
  source checks and application semantics are unchanged.

## 0.2.22

Bounded capture text continuations (bytes and lines), current exact-request prepare
reuse, and explicit source-bound authored-state replacement with retained history.
Evidence and limits: [reading-flow report](evals/reports/reading-flow-20261107.md).
Current source/host/use status remains in [status](docs/wiki/status.md#current-state).

## 0.2.21 source candidate

Selected Wiki documents now enter prepared page/history views even without native
source-owner registration. Native ownership gaps remain unchanged; missing planned
pages are explicit. Exact verification-history headings are separated from current
body content. The compact index signals explicit history independently of legacy
note counts; missing selected-page errors identify the actual snapshot gap. [Regression and native replay evidence](evals/reports/selected-wiki-context-20261107.md).

## 0.2.20 source candidate

File-first native preparation without packet ceremony; complete compact indexes
with explicit display overflow; captured page/current/history reading; existing
selected-change observations; actionable missing-format diagnostics. Native
execution opt-in, scope validation and old packet APIs retained. No host update,
new hook, gate activation or adoption claim. See [current state](docs/wiki/status.md#current-state).

## Earlier source changes under 0.2.19

Payload changes after the pinned ee6c065 copies, with no version bump: split-owner
handoff guidance (2026-10-30); rule-based routing, invariant tables and five-layer miss
classification (2026-10-31); the optional Claude pre-edit gate
`project-wiki/scripts/edit_gate.py` with `PreToolUse` in `hooks/claude.json`
(2026-11-02, see [maintenance.md » Pre-edit gate](project-wiki/references/maintenance.md#pre-edit-gate-host-delivery-of-wiki-first));
consumer matrices and probe validation (2026-11-02); pilot-project references
neutralized in the guides (2026-11-01); wiki-usage lessons (2026-11-03): generated
blocks inside authored pages (stable row keys, authored-text change predicates,
hunk-by-hunk merges and a post-merge authored-line guard, see
[maintenance.md » Generated blocks](project-wiki/references/maintenance.md#generated-blocks-inside-authored-pages)),
pre-edit gate boundaries (shell writes, stamp writers, waiver binding, shell-hook
pitfalls), acknowledgement, keyword and stamp-freshness rules, selector exactness,
and a designed-not-implemented state for design-first pages. Session log:
[PROJECT.md » History](PROJECT.md#history) (2026-10-30 to 2026-11-03).

## 0.2.19

0.2.19 is a source candidate for the evolution workflow, exercised in real
product and Wiki-maintenance tasks with independent rework retained. Skill-only
copies pinned to ee6c065 now match all 19 source files on the selected Mac Codex
and Linux Claude hosts; the new Claude invocation advertised and natively loaded
the skill. The subsequent Mac catalog also advertises it and Root read the
installed entry. Correct adoption and lower rework/context cost remain separate checks. No plugin hooks, trust or access settings changed.
See the [plan](docs/WIKI_EVOLUTION_PIPELINE_PLAN_20261029.md) and
[evaluation](evals/reports/wiki-evolution-pipeline-20261029.md).

- Session log: [PROJECT.md » History](PROJECT.md#history) (2026-10-29 to 2026-10-31).

## 0.2.18

0.2.18 source candidate adds a private-safe item ordinal to selected-evidence
file refusals, preserving their existing prefix and refusal policy. The ordinal
follows the current checkpoint list, not always original CLI order; see
[selected evidence](project-wiki/references/collaboration-workflow.md#selected-evidence-files)
and the [bounded evaluation](evals/reports/evidence-selection-diagnostics-20261029.md).
At its initial checkpoint, installation/publication and independent real-task
adoption remained pending. The linked evaluation and this repository's PR #40 record the later scoped
mobile adoption and cross-platform CI. That change did not alter skill instructions,
hooks or host trust settings.

- Plan: [docs/EVIDENCE_SELECTION_DIAGNOSTICS_PLAN.md](docs/EVIDENCE_SELECTION_DIAGNOSTICS_PLAN.md); session log: [PROJECT.md » History](PROJECT.md#history) (2026-10-29).

## 0.2.17

0.2.17 candidate lets doctor read an explicitly supplied Codex `hooks/list`
snapshot alongside matching installation inventory. It reports one working
directory's plugin SessionStart enabled/trust state and lexical source association;
it never grants trust or claims execution, context delivery or use. Received paths
and commands are not opened or executed. See the
[bounded design and acceptance plan](docs/DOCTOR_HOOK_OBSERVATION_PLAN.md).
The [bounded replay](evals/reports/supplied-hook-observations-c179-20261025.md)
separates package/source checks from a supplied real host observation.
Source, package, installed host and actual lifecycle acceptance remain separate.

Normal source/main CI and one official Windows installation of 0.2.17 are now
verified. The installed doctor consumed a fresh host listing and reported the
selected SessionStart as enabled/trusted while leaving execution/delivery/use
unverified. Hook definitions and the delivery script were unchanged; no trust
settings or running scoped worker were modified. See the
[bounded host adoption return](evals/reports/supplied-hook-observations-c179-20261025.md#normal-source-and-bounded-host-adoption).

- Plan: [docs/PLUGIN_PLAN.md » 0.2.17](docs/PLUGIN_PLAN.md#0217-candidate-supplied-hook-listing-observations).

## 0.2.16

0.2.16 candidate adds an explicit coordinator `capture-return` command. It derives
every actual root/peer diff file through the same collector as final reconciliation,
then invokes the reviewed native router with explicit opt-in. Unplanned files,
missing peers and selected evidence remain visible to the original gates; source
or scope drift during capture refuses the operation without automatic retry.
Review, source/main adoption, host installation and product acceptance remain separate.
See [the bounded actual-return case](evals/reports/actual-return-capture-c134-20261024.md).

- Plan: [docs/PLUGIN_PLAN.md » 0.2.16](docs/PLUGIN_PLAN.md#0216-candidate-capture-the-complete-actual-return).

## 0.2.15

0.2.15 candidate shows the existing unchanged-return predicate at read-only
task creation and delegation. A dirty baseline now receives an early advisory;
final reconciliation, permissions and snapshot-only reader limits stay intact.
Source tests and package checks are separate from installation and host delivery.

- Evidence: [read-only baseline advice, C130](evals/reports/readonly-baseline-c130-20261024.md). PLUGIN_PLAN has no 0.2.15 section.

## 0.2.14

0.2.14 makes repeated capture `--files` groups accumulate instead of
silently replacing earlier paths. The native router receives the complete
normalized selection; permissions and semantic completion remain separate.
See [the retained CLI counterexample](evals/reports/repeated-file-groups-c126-20261024.md).
Source/main CI and one official Windows installation are verified. The actual
installed CLI preserves repeated and later-empty groups; the prior installed
copy loses them. At the recorded host cutoff, the new hook is **modified** and
awaits normal user review; installation does not imply trust or automatic context
delivery. The same report separates these observations from semantic use.

- Plan: [docs/PLUGIN_PLAN.md » 0.2.14](docs/PLUGIN_PLAN.md#0214-candidate-complete-explicit-file-groups) and [» installed CLI adoption](docs/PLUGIN_PLAN.md#repeated-file-groups-source-and-installed-cli-adoption-2026-10-24).

## 0.2.13

0.2.13 candidate exposes the saved Wiki path base in every reading view. A normal
trusted host delivery exercise succeeded, but its reader initially opened native
page keys at the checkout root instead of the Wiki root. The new metadata uses
the existing captured base, retains native keys and snapshot-only limits, and
does not add a new router. See [the bounded case and scope](evals/reports/wiki-path-basis-c122-20261024.md).

- Plan: [docs/PLUGIN_PLAN.md » 0.2.13](docs/PLUGIN_PLAN.md#0213-candidate-saved-wiki-path-basis).

## 0.2.12

0.2.12 candidate adapts the optional hook package container to the observed
Codex 0.160 loader: `--with-lifecycle-hooks` emits legacy host manifests, while
plain packages stay portable. One canonical identity/skill/workflow is retained.
The version-matched upstream loader explicitly skips portable AgentPlugin hooks;
the actual installed old/new-declaration probes both returned no hooks. See
[the evidence and remaining runtime acceptance](evals/reports/runtime-hook-layout-c120-20261024.md).
Normal source/main adoption and official Windows installation are now verified.
At that 0.2.12 checkpoint, the host discovered SessionStart as **untrusted**;
automatic execution and use are still awaiting normal review and their own
evidence. See [the bounded adoption return](evals/reports/runtime-hook-layout-c120-20261024.md#normal-adoption-and-actual-discovery).

- Plan: [docs/PLUGIN_PLAN.md » 0.2.12](docs/PLUGIN_PLAN.md#0212-candidate-observed-host-compatibility-container).

## 0.2.11

0.2.11 candidate declares optional Codex hooks explicitly in the portable root
manifest, with a named source-to-package projection and legacy receipt support.
This follows an actual 0.2.10 installation whose hook list was empty; source/package
checks are not runtime discovery. See the [observation and remaining acceptance](evals/reports/portable-hook-declaration-c119-20261024.md).

- Plan: [docs/PLUGIN_PLAN.md » 0.2.11](docs/PLUGIN_PLAN.md#0211-candidate-explicit-portable-hook-declaration).

## 0.2.10

0.2.10 candidate adds an **optional** internal lifecycle-delivery package profile:
`python scripts/package_plugin.py --with-lifecycle-hooks --output <new-directory>`.
Startup/resume/compaction can deliver an explicitly selected saved task through
the existing snapshot reader. The default package stays skill-only; no trust,
installation, native execution or completion policy is changed by packaging.
See [scope and host requirements](project-wiki/references/collaboration-workflow.md#optional-lifecycle-delivery).
Source tests, package closure and actual trusted host triggering remain separate.

- Plan: [docs/PLUGIN_PLAN.md » 0.2.10](docs/PLUGIN_PLAN.md#0210-candidate-optional-saved-task-lifecycle-delivery).

## 0.2.9

0.2.9 adds explicit `show --snapshot-only` for readers forbidden to invoke
Git. It renders the saved task records without live input checks and clearly
labels currentness as unchecked; default display, dispatch and return guards stay
in place. See [permission-separated reading](project-wiki/references/collaboration-workflow.md#reading-when-the-worker-cannot-invoke-git)
and the [bounded evaluation](evals/reports/snapshot-reading-c103-20261024.md).
Source/main adoption and one official Windows update to 0.2.9 are now recorded in
the [bounded adoption return](evals/reports/snapshot-reading-c103-20261024.md#normal-adoption-and-bounded-host-observation).
Installed doctor/helper use and a delivered skill-catalog entry were observed;
hooks, trust, automatic lifecycle and business acceptance remain separate. The
active scoped Claude worker remains 0.2.4.

The following README overview paragraphs were last revised at the 0.2.9 identity
and are kept here as written:

[内部协作插件计划](docs/PLUGIN_PLAN.md)：以现有 Skill/工具为唯一内核，补可复现打包、来源自检与宿主接线，再用真实工程验证开工、委派、收尾与接管。内部插件已在一台 Codex 主机通过官方 CLI 安装并核对缓存，Linux Claude 已做临时加载与真实任务试用；桌面自动生命周期、hooks 与完整跨宿主验收仍待，未公开发布到插件目录。根 `plugin.json` 是身份源，不能单凭它声称运行已验证。0.2.9源码已正常采用，一台 Windows 宿主已更新并实际调用；目录送达、主动读取、hooks 与自动接管分别核验；[换行来源机制](evals/reports/package-newline-provenance-20261022.md)保留原始输入指纹，区分规范文本来源一致与包文件字节完整；[有限宿主采用记录](evals/reports/host-adoption-v025-20261022.md)另证历史官方 Windows CLI 安装0.2.5及实际有限使用。既有 scoped 0.2.4 工程任务不由此自动升级。

[协作工作流](project-wiki/references/collaboration-workflow.md)提供原生任务 JSON 的快照、任务包、范围受限的委派和真实 diff 收尾；全部卫星、能力缺口、未展开候选与跨仓版本保留。脚本不派 agent、不自动执行页内检查，也不把结构闭环认证成业务完成。内部插件已有限采用，宿主生命周期与项目试用按计划分别验收。

协同仓库开工时，先核项目实际支持的来源选择参数。原生命令退出成功或印记有效，仍可能读了默认旧仓库；若原生报告提供来源身份，声明 peer 后使用[所选来源核对](project-wiki/references/collaboration-workflow.md#context-capture)，在派工前比较真实 root / HEAD。[C116 使用复盘](evals/reports/native-selection-invocation-c116-20261024.md)保留一次协调者误传环境变量的失败与已有核对能力的实际拒收；这是调用方法修正，没有新增插件或修改宿主。

- Plan: [docs/PLUGIN_PLAN.md » 0.2.9](docs/PLUGIN_PLAN.md#adopted029-saved-record-reading-under-command-restrictions).

## 0.2.8

0.2.8 adds optional checkpoint hash observations for explicitly selected
historical evidence files, including private files outside Git. The original
capture/delegate/return workflow refuses a changed or dropped selection; it does
not prevent writes, continuously monitor files or certify business completion.
See [selected evidence](project-wiki/references/collaboration-workflow.md#selected-evidence-files).
Source/package/host adoption remain separate. Its later bounded 0.2.8 host receipt
is distinguished from the historical 0.2.7 exercise below.

- Plan: [docs/PLUGIN_PLAN.md » 0.2.8](docs/PLUGIN_PLAN.md#historical028-candidate-explicit-preservation-observations-for-selected-evidence).

## 0.2.7

0.2.7 adds an optional comparison between the native router's reported
checkout identities and explicitly selected task peers. The
[C91 exercise](evals/reports/native-source-consistency-c91-20261023.md) preserves
the real mismatch and first policy-retention failure, then records the actual
CLI/full-suite/package checks, normal source/main adoption and one official
Windows update to 0.2.7. A real task started using the installed helper's bytes
with strict native-source comparison. Scoped 0.2.4 workers remain pinned;
automatic host lifecycle, physical reads and semantic adoption stay separate.

- Plan: [docs/PLUGIN_PLAN.md » 0.2.7](docs/PLUGIN_PLAN.md#adopted027-native-selected-source-identity-comparison-c91).

## 0.2.6

Historical 0.2.6 source was normally adopted and one Windows host was updated through the
official CLI, with installed bytes/source and inventory/version observations
checked separately. The new doctor only reads caller-captured host evidence;
installation/enabling does not establish hook execution or agent adoption.
Running scoped workers were not upgraded. See [actual host adoption](evals/reports/codex-inventory-doctor-c77-20261023.md#host-adoption-after-source-merge)
and [doctor observations](docs/PLUGIN_PLAN.md#codex-inventory-observations-026-candidate).

- Plan: [docs/PLUGIN_PLAN.md » 0.2.6](docs/PLUGIN_PLAN.md#codex-inventory-observations-026-candidate).

## 0.2.5 and earlier

README carried no separate entry for these versions. Pointers only:

- 0.2.5 newline provenance and host adoption: [docs/PLUGIN_PLAN.md » 0.2.6 section, historical checkpoints](docs/PLUGIN_PLAN.md#codex-inventory-observations-026-candidate),
  [package newline provenance](evals/reports/package-newline-provenance-20261022.md),
  [actual 0.2.5 host adoption](evals/reports/host-adoption-v025-20261022.md).
- 0.2.4 review-template return preparation: [docs/PLUGIN_PLAN.md » 0.2.6 section, 2026-10-22 review checkpoint](docs/PLUGIN_PLAN.md#codex-inventory-observations-026-candidate).
- 0.2.3 read-only task packets: [docs/PLUGIN_PLAN.md » read-only task packets](docs/PLUGIN_PLAN.md#read-only-task-packets-023-source-adopted-2026-10-22).
- 0.2.2 native return context: [docs/PLUGIN_PLAN.md » native return context](docs/PLUGIN_PLAN.md#native-return-context-candidate-v022).
- 0.1.0 to 0.2.1 internal plugin and native workflow: [internal plugin package](evals/reports/internal-plugin-package-20261021.md),
  [native workflow](evals/reports/native-workflow-20261021.md).
