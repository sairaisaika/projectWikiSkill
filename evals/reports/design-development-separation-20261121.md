# Design records versus development resources — 2026-11-21

Baseline: public `sairaisaika/projectWikiSkill` main `dac028902561bec4df1bc752f6320c6b7cef95a6`. Synthetic fixture
and self-test only; no downstream repository was inspected.

## Assessment

Before this change the skill split files by sensitivity/visibility (repository
boundary), by Git disposition (File placement) and by time (current state versus
historical evidence), and told closeout to return durable lessons to their owner.
It did not state the purpose/lifecycle split itself: what the software is and why
(design records to preserve) versus by-products of building it (development
resources). Nothing said the two need separate homes and retention, that a design
statement must not cite task scratch as authority, or that development material
reaches a design record only by distillation.

## Change

- One subsection in the existing File placement owner
  (`repository-hygiene.md#separate-design-records-from-development-resources`):
  definitions, separate homes and retention, no dated plans/diaries/run output in
  the canonical design area, distillation at closeout via Wiki evolution, prototype
  code only through reviewed change, and independence from tracking/ignore/visibility.
- Two template rows (design record, development working material); the "repo-safe
  truth" row now lists source/config inputs rather than the Wiki.
- Skill entry: the existing Place a file item links the subsection.
- Synthetic fixture: `docs/wiki/` design row and `work/` task row in its existing
  table, plus scoped aliases on the existing `repository-hygiene` route.

No new route, owner, manifest, query algorithm, scanner, hook or migration.

## Checks

- New focused test failed before the change (1 error, 4 existing placement tests
  passing) and passes after it.
- Full unit suite: 502 tests on Python 3.13/macOS, OK (1 existing platform skip). Fixture tests 19 OK. Both Wiki checks pass. Fixture
  evaluation: 28 curated tasks pass.
- Directed queries: 开发资源和设计资源应该分开放在哪里？, 开发过程文件和设计文档分别放哪里？,
  任务草稿和设计文档分别放哪里？, "Where do development resources go versus design
  records?", "Should a dated plan live in the design wiki?" and 设计资源要保存在哪里？
  reach `repository-hygiene` with the File placement anchor. Typo controls return
  no route.

## Limits

Curated alias coverage and a self-test by the author; no blind reader, independent
adoption or downstream migration. This repository's own `docs/` still holds dated
plan files beside `docs/wiki/`; applying the rule here is a separate change.
