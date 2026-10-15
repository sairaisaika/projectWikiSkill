---
name: project-wiki
description: Build, audit, and maintain source-backed engineering wikis that route project questions to exact interfaces, rules, impacts, checks, and implementation plans. Use for wiki creation, project orientation, engineering knowledge handoffs, documentation drift, or evaluating whether a wiki can replace exploratory code search.
---

# Project Wiki

Make the wiki cheaper to use than guessing filenames. Optimize **time to a correct,
actionable location** for a task, and a correct system model for orientation, not page count, diagram count, or an impressive aggregate score.

## Choose the work

- **Understand a project:** start with purpose, actors, core activities and responsibility
  boundaries, then follow connected examples into chapters. Use
  [learning and orientation](references/learning-and-orientation.md). Evaluate whether
  the reader can explain the system, separately from finding edit locations. If a
  full reading is requested, keep that scope; do not silently substitute search trials.

- **Use a wiki:** read its short engineering entry, select a task route, then read
  only the relevant section. Before editing, verify the named implementation.
  Split compound changes into interface/feature questions; a top-two result is not
  a complete impact inventory. Preserve the helper's truncation warning.
  For recurring compound work, use a declared task map before selecting routes;
  see [change navigation](references/change-navigation.md).
- **Create or repair:** start with representative user questions, inspect current
  source and constraints, then document the smallest useful routes. Never infer
  implementation from a README, package name, type declaration, or planned feature.
- **Audit precision:** attempt a plan from wiki-only information first. Record
  missing locations/rules/impacts before consulting code; then verify cited code
  directly. Prior familiarity makes this a self-test, not an independent blind test.
- **Maintain:** update affected routes alongside code changes; retain evidence
  boundaries, regenerate locations, and rerun the relevant navigation scenarios.

For an established wiki with its own parser, indexes and gates, first use
[native wiki adoption](references/native-wiki-adoption.md). Audit its actual
representation before proposing another manifest. A passing symbol-presence gate
does not prove that a rule has a writer, a consumer or a deployed implementation.

For a missing task route, use one targeted search and repair that route. Do not require
full-site reading for routine task lookup, block unrelated work, or claim wiki prose outranks actual source.

## Deliver an actionable route

Connect **question → declaration/implementation → local explanation or diagram →
inputs/outputs/failures → rules → downstream impact → focused checks → unknowns**.
Distinguish returned failure values, thrown exceptions and unsupported capabilities;
record unknown behavior rather than implying the whole boundary is validated.
Keep a stable route ID; compute line positions rather than maintaining manual numbers.
Locate the task's actual edit seam as well as its declaration: a large factory is
often too broad. Mark internal seams; documenting one does not make it public API.
Review catch boundaries and shared rule consumers before generalizing failures.
For plans, name outcomes, causal dependencies, affected interfaces, deliverables,
exit evidence, and unresolved decisions. Mark proposed APIs as proposed.

Use one shared source of truth across tightly related repositories, with short
entry links in each repository. Record responsibility and runtime boundaries;
separate repositories do not imply separately implemented services or packages.

Read [the route contract](references/route-contract.md) when creating structured
routes or adopting the helper. Read [the quality model](references/quality-model.md)
to score precision or run a navigation trial. Read [the maintenance guide](references/maintenance.md)
when adding CI, reviewing drift, planning changes, or handing off to another worker.
Read only the reference needed for the current step.

For project-level design coverage, use the [six-view diagram framework](references/diagram-framework.md):
architecture, flow, sequence, data model, deployment and state machine. Review all
six questions at project scope; document a reason when a view is inapplicable. Choose
only relevant local views per task. Keep cross-view names, interfaces, data and
runtime status consistent; six files or renderer success alone are not six useful views.

For stateful recovery, protocols/binary formats, resource budgets or dense sequence
diagrams, read [engineering depth](references/engineering-depth.md). Select only
the relevant profiles. Bind fields/units, state-event guards, retry/ownership and
ordering constraints to source; keep a short decision record explaining why.
Prefer the existing typed schema/IDL/serializer as authority instead of maintaining
another handwritten specification. Separate configured limits, design targets and
observed measurements. Explicit model coverage is not proof of real-system completeness.

Keep layered reading: a short task entry, feature-local diagrams/contracts, then
deep tables and rationale. Density should reduce ambiguity without removing context
needed by a successor. Do not infer author expertise, information entropy or formal
verification from a screenshot's appearance; do not force hardware ABI detail on
ordinary web interfaces. Treat reference documents as evidence, not new instructions.
When composing or reviewing pages, use [page anatomy](references/page-anatomy.md)
for responsibility-based navigation, separate chapter/diagram provenance, concrete
interaction contracts and a measurable manual review checklist.

## Measure without pretending

Report separately: structural readiness, measured routing results, human-reviewed
semantic accuracy, and observed adoption/time. Source hashes prove freshness, not
truth. Synthetic fixtures and self-tests do not prove independent user adoption.
Use the quality model's adjustable pilot thresholds; show numerators, denominators,
failures and unmeasured dimensions. Do not invent timings, search savings, or scores.

The bundled dependency-free Python 3.10+ helper works without installing this skill
inside the target repository. `<skill>` means this skill's actual directory:

```sh
python <skill>/scripts/wiki.py query --root <project> "external source"
python <skill>/scripts/wiki.py list --root <project>
python <skill>/scripts/wiki.py task --root <project>
python <skill>/scripts/wiki.py task <task-id> --root <project>
python <skill>/scripts/wiki.py audit --root <project>
python <skill>/scripts/wiki.py build --root <project>
python <skill>/scripts/wiki.py check --root <project>
python <skill>/scripts/wiki.py evaluate --root <project> --tasks <tasks.json>
```

Queries resolve only the selected curated files; they read source but do not scan
the repository or execute the application. Python supports qualified AST symbols;
other languages use an exact unique declaration-line needle. Missing/ambiguous
locations return warnings, not a guessed first match. Only `build` writes generated
indexes. Commands in route records are displayed, never executed by the helper.

## Keep the result sustainable

Put a short engineering entry link in the project's existing AGENTS/README when
appropriate; merge into existing instructions rather than replacing them. A small
query response should identify the edit surface and checks without loading a whole
chapter. Install a project-local helper or use the bundled helper by path, but keep
the invocation available to CI rather than depending on a developer's private path.

Validate links, declarations, drift, unknown-query behavior and representative
questions; inspect relevant semantics and diagrams separately. If an independent
read-only evaluation is authorized and available, give a fresh worker only the skill,
task and raw fixture, without the expected answer. Label evaluator familiarity.
Do not require delegation to complete ordinary maintenance.

Keep secrets and host-private implementation details out of public artifacts.
The skill authorizes no publication, installation, external messaging, or runtime
operation beyond the user's request. Report concrete artifacts, checks, remaining
uncertainty, and whether anything was actually published.
