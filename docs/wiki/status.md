# Version status

## Current state

| Version | Source CI | main adopted | package closure | installed hosts | context delivered | actual agent use | business acceptance |
|---|---|---|---|---|---|---|---|
| 0.2.20 | [PR head: passed](https://github.com/sairaisaika/projectWikiSkill/actions/runs/42335123267); merge-head CI checked separately | [PR45](https://github.com/sairaisaika/projectWikiSkill/pull/45), [PR46](https://github.com/sairaisaika/projectWikiSkill/pull/46), merge cc2bfa0 | [three source-matching profiles](../../evals/reports/context-reading-20261106.md#source-verification-receipts) | [one Linux Claude skill-only copy, 21/21 bytes matched](../../evals/reports/context-reading-20261106.md#merged-source-and-bounded-installation) | not observed for the new copy | no post-update eligible sample observed | unmeasured |

The installed payload is bound to cc2bfa0 (same tree as reviewed 5dbacfa).
Installation and a coordinator snapshot smoke test are separate from delivery,
real worker use and improved task outcomes. See the scoped evidence below.

## Historical evidence

Earlier status and installation observations are preserved below as records;
read their original dates and evidence scopes. They do not override current state.

### Status table

| Version | Source CI | main adopted | package closure | installed host(s) | hook discovered | trusted | delivered | agent use observed | business acceptance |
|---|---|---|---|---|---|---|---|---|---|
| post-ee6c065 payload (unreleased, still 0.2.19) | unknown | pending | [yes](../../PROJECT.md#history) (2026-11-03, at c062224) | [no](../../PROJECT.md#history) | n/a | n/a | n/a | unknown | unknown |
| 0.2.19 | [yes](../../evals/reports/wiki-evolution-pipeline-20261029.md#source-verification-and-remaining-limitations) | pending | [yes](../../evals/reports/wiki-evolution-pipeline-20261029.md#distribution-verification-and-wiki-end) | [yes](../../evals/reports/host-skill-only-20261030.json) | n/a | n/a | [yes](../../evals/reports/wiki-evolution-pipeline-20261029.md#scoped-skill-only-installation-and-native-delivery) | [yes](../../evals/reports/wiki-evolution-pipeline-20261029.md#following-real-integration-task-adoption-with-failed-first-pass-use) | pending |
| 0.2.18 | [yes](../../PROJECT.md#history) | pending | [yes](../../evals/reports/evidence-selection-diagnostics-20261029.md#independent-review-and-next-real-handoff) | [no](../../evals/reports/evidence-selection-diagnostics-20261029.md#independent-review-and-next-real-handoff) | n/a | n/a | n/a | [yes](../../evals/reports/evidence-selection-diagnostics-20261029.md#actual-task-return-and-efficiency-review) | pending |
| 0.2.17 | [yes](../../evals/reports/supplied-hook-observations-c179-20261025.md#normal-source-and-bounded-host-adoption) | [yes](../../evals/reports/supplied-hook-observations-c179-20261025.md#normal-source-and-bounded-host-adoption) | [yes](../../evals/reports/supplied-hook-observations-c179-20261025.md#normal-source-and-bounded-host-adoption) | [yes](../../evals/reports/supplied-hook-observations-c179-20261025.md#normal-source-and-bounded-host-adoption) | [yes](../../evals/reports/supplied-hook-observations-c179-20261025.md#normal-source-and-bounded-host-adoption) | [yes](../../evals/reports/supplied-hook-observations-c179-20261025.md#normal-source-and-bounded-host-adoption) | pending | unknown | pending |
| 0.2.16 | pending | [yes](#notes-on-specific-cells) | pending | [no](../../evals/reports/supplied-hook-observations-c179-20261025.md#normal-source-and-bounded-host-adoption) | n/a | n/a | n/a | [yes](../../evals/reports/actual-return-capture-c134-20261024.md#actual-paired-project-use) | pending |
| 0.2.15 | pending | [yes](#notes-on-specific-cells) | unknown | [no](../../evals/reports/supplied-hook-observations-c179-20261025.md#normal-source-and-bounded-host-adoption) | n/a | n/a | n/a | unknown | pending |
| 0.2.14 | [yes](../../evals/reports/repeated-file-groups-c126-20261024.md#subsequent-official-host-adoption-2026-10-24) | [yes](../../evals/reports/repeated-file-groups-c126-20261024.md#subsequent-official-host-adoption-2026-10-24) | [yes](../../evals/reports/repeated-file-groups-c126-20261024.md#subsequent-official-host-adoption-2026-10-24) | [yes](../../evals/reports/repeated-file-groups-c126-20261024.md#subsequent-official-host-adoption-2026-10-24) | [yes](../../evals/reports/repeated-file-groups-c126-20261024.md#subsequent-official-host-adoption-2026-10-24) | [yes](../../evals/reports/supplied-hook-observations-c179-20261025.md) | pending | [yes](../../evals/reports/repeated-file-groups-c126-20261024.md#subsequent-official-host-adoption-2026-10-24) | pending |
| 0.2.13 | pending | [yes](#notes-on-specific-cells) | [yes](../../evals/reports/wiki-path-basis-c122-20261024.md#change-boundary) | unknown | unknown | unknown | unknown | unknown | pending |
| 0.2.12 | [yes](../../evals/reports/runtime-hook-layout-c120-20261024.md#normal-adoption-and-actual-discovery) | [yes](../../evals/reports/runtime-hook-layout-c120-20261024.md#normal-adoption-and-actual-discovery) | [yes](../../evals/reports/runtime-hook-layout-c120-20261024.md#normal-adoption-and-actual-discovery) | [yes](../../evals/reports/runtime-hook-layout-c120-20261024.md#normal-adoption-and-actual-discovery) | [yes](../../evals/reports/runtime-hook-layout-c120-20261024.md#normal-adoption-and-actual-discovery) | [yes](../../evals/reports/wiki-path-basis-c122-20261024.md#observation) | [yes](../../evals/reports/wiki-path-basis-c122-20261024.md#observation) | [yes](../../evals/reports/wiki-path-basis-c122-20261024.md#observation) | pending |
| 0.2.11 | [yes](../../evals/reports/runtime-hook-layout-c120-20261024.md#what-changed-the-next-action) | [yes](../../evals/reports/runtime-hook-layout-c120-20261024.md#what-changed-the-next-action) | [yes](../../evals/reports/runtime-hook-layout-c120-20261024.md#what-changed-the-next-action) | [yes](../../evals/reports/runtime-hook-layout-c120-20261024.md#what-changed-the-next-action) | [no](../../evals/reports/runtime-hook-layout-c120-20261024.md#what-changed-the-next-action) | n/a | unknown | unknown | pending |
| 0.2.10 | [yes](../../evals/reports/portable-hook-declaration-c119-20261024.md) | [yes](../../evals/reports/portable-hook-declaration-c119-20261024.md) | [yes](../../evals/reports/portable-hook-declaration-c119-20261024.md) | [yes](../../evals/reports/portable-hook-declaration-c119-20261024.md) | [no](../../evals/reports/portable-hook-declaration-c119-20261024.md) | n/a | unknown | unknown | pending |
| 0.2.9 | [yes](../../evals/reports/snapshot-reading-c103-20261024.md#normal-adoption-and-bounded-host-observation) | [yes](../../evals/reports/snapshot-reading-c103-20261024.md#normal-adoption-and-bounded-host-observation) | [yes](../../evals/reports/snapshot-reading-c103-20261024.md#normal-adoption-and-bounded-host-observation) | [yes](../../evals/reports/snapshot-reading-c103-20261024.md#normal-adoption-and-bounded-host-observation) | n/a | n/a | [yes](../../evals/reports/snapshot-reading-c103-20261024.md#normal-adoption-and-bounded-host-observation) | [yes](../../evals/reports/readonly-acceptance-review-c110-20261024.md) | pending |
| 0.2.8 | pending | [yes](#notes-on-specific-cells) | [yes](../../evals/reports/preserved-evidence-c96-20261023.md#actual-local-checks) | [yes](../../evals/reports/snapshot-reading-c103-20261024.md#normal-adoption-and-bounded-host-observation) | n/a | n/a | unknown | unknown | pending |
| 0.2.7 | [yes](../../evals/reports/native-source-consistency-c91-20261023.md#adoption-after-the-candidate-checkpoint) | [yes](../../evals/reports/native-source-consistency-c91-20261023.md#adoption-after-the-candidate-checkpoint) | [yes](../../evals/reports/native-source-consistency-c91-20261023.md#adoption-after-the-candidate-checkpoint) | [yes](../../evals/reports/native-source-consistency-c91-20261023.md#adoption-after-the-candidate-checkpoint) | n/a | n/a | unknown | [yes](../../evals/reports/native-source-consistency-c91-20261023.md#adoption-after-the-candidate-checkpoint) | pending |
| 0.2.6 | [yes](../../evals/reports/codex-inventory-doctor-c77-20261023.md#host-adoption-after-source-merge) | [yes](../../evals/reports/codex-inventory-doctor-c77-20261023.md#host-adoption-after-source-merge) | [yes](../../evals/reports/codex-inventory-doctor-c77-20261023.md#host-adoption-after-source-merge) | [yes](../../evals/reports/codex-inventory-doctor-c77-20261023.md#host-adoption-after-source-merge) | n/a | n/a | unknown | [yes](../../evals/reports/source-sdk-boundaries-c80-20261023.md) | pending |
| 0.2.5 | [yes](../../docs/PLUGIN_PLAN.md#codex-inventory-observations-026-candidate) | [yes](../../evals/reports/host-adoption-v025-20261022.md) | [yes](../../evals/reports/host-adoption-v025-20261022.md#official-windows-update-and-observed-cache-replacement) | [yes](../../evals/reports/host-adoption-v025-20261022.md#official-windows-update-and-observed-cache-replacement) | n/a | n/a | [yes](../../evals/reports/host-adoption-v025-20261022.md#fresh-codex-cli-observation) | [yes](../../evals/reports/host-adoption-v025-20261022.md#fresh-codex-cli-observation) | pending |

### Legend

| Cell | Meaning |
|---|---|
| yes | A record shows the layer happened for this version; the link is that record. Scope is whatever the record says (often one host, one task) |
| no | A record shows it was checked and did not happen, or that this version was skipped (for example, the host went from 0.2.14 straight to 0.2.17) |
| pending | The latest record names the layer as still open, and no later record closes it |
| n/a | The layer cannot apply: no hook profile existed before 0.2.10 (no `hooks/` in the tree), the copy is skill-only, or the version was not installed |
| unknown | No record either way |

Column meanings:

- **Source CI**: the Ubuntu/Windows × Python 3.10/3.13 workflow passed on this version's source, PR or main head.
- **main adopted**: a record says the version was merged to main.
- **package closure**: `package_plugin.py` built it and `plugin_doctor.py` matched package, source and identity.
- **installed host(s)**: placed on a real host through its official plugin or skill installer.
- **hook discovered / trusted**: the host's own hook listing showed the plugin's hook, and as trusted.
- **delivered**: the installed skill (host catalog) or hook-injected context reached a fresh session.
- **agent use observed**: an agent used this version's skill, helper or delivered context in recorded work. Test suites, command replays and doctor runs do not count. Not proof of correct or efficient use.
- **business acceptance**: the consumer project's own outcome was accepted. No version has this; every report keeps it separate.

### Notes on specific cells

- Installed hosts: 0.2.5 to 0.2.17 "yes" means one Windows Codex host via the official plugin CLI. 0.2.19 "yes" means skill-only copies (no hooks) on a Mac Codex and a Linux Claude host.
- 0.2.5 Source CI: recorded in PLUGIN_PLAN ("exact main CI green"), not in a report.
- main adopted for 0.2.8, 0.2.13, 0.2.15 and 0.2.16 comes from `git log --merges origin/main` (8679084, 58073d4, 6de3f3e, dc771f3); no report records it and their CI result is unrecorded. origin/main is at 0.2.17 (b8a1782), so 0.2.18, 0.2.19 and the post-ee6c065 payload are not on main.

### Canonical copies

| Copy | What it is | Last recorded state |
|---|---|---|
| This repository, [`project-wiki/`](../../project-wiki/SKILL.md) + [`plugin.json`](../../plugin.json) | The only editable source. `plugin.json` is the version identity; packages are generated projections | HEAD c062224, identity 0.2.19 |
| Linux Claude `~/.claude/skills/project-wiki` | Skill-only copy, pinned | Matching all 19 payload files of the ee6c065 / be9f68e tree ([receipt](../../evals/reports/host-skill-only-20261030.json); unchanged at [PROJECT.md » History](../../PROJECT.md#history) 2026-10-31) |
| Mac Codex `~/.codex/skills/project-wiki` | Skill-only copy, pinned | 19 files from ee6c065 ([receipt](../../evals/reports/host-skill-only-20261030.json)) |
| Windows Codex plugin install | Official plugin CLI install with hook profile | 0.2.17 ([report](../../evals/reports/supplied-hook-observations-c179-20261025.md#normal-source-and-bounded-host-adoption)) |

The pinned skill-only copies lag HEAD. Since ee6c065, HEAD has changed 11
`project-wiki/` files (SKILL.md and 10 references) and added
`scripts/edit_gate.py`. Check with `git diff --stat ee6c065 HEAD -- project-wiki`.
