# Validation scope

These reports describe measured runs, not expected scores to copy into a new project.

| Artifact | What it establishes | Limits |
|---|---|---|
| fixture-structure.json | Seven schema-2 routes resolve; structural average 98.86, minimum 92; six view kinds and optional engineering metrics | A missing TS test deliberately loses points; field completeness is not semantic truth |
| fixture-routing.json | 20/20 known questions top-1/top-2; 4/4 unknown controls rejected | Author-curated synthetic self-test, not independent adoption |
| forward-trial.md | One fresh evaluator drafted a six-category plan wiki-first with no exploratory search, then checked cited source | One synthetic trial before corrections; no speedup baseline |
| smv-legacy-audit.json | Existing real project's 10 schema-1 routes resolve; schema-2 precision gaps are reported | Read-only audit; not migrated, not awarded a schema-2 score |
| engineering-and-six-view-trials.md | Two fresh read-only trials used wiki-first plans and surfaced concrete missing constraints | Synthetic tasks; no time/speedup baseline or live product acceptance |
| diagram-rendering.json | Six current Mermaid sources parsed/rendered; source hashes checked in tests | Screenshots are temporary; core Python helper does not render or prove diagram semantics |

The current fixture also declares a four-surface task map. One expected-scope case
checks all four surfaces/routes separately from ranking. Eight mutation/read-boundary
tests cover omitted/replaced surfaces, duplicate/missing references, document gaps,
snapshot drift and internal edit-target metadata. A task outline works even after
fixture source files are removed; queries still require source to resolve positions.
These results do not constitute a new independent adoption trial.

Local validation of this skill: 66 helper/package test cases, 65 passing and one
symlink case skipped because Windows disallows unprivileged symlink creation;
12 fixture application contract tests pass. Skill Creator's frontmatter validator
passes. Python 3.13 on Windows was executed locally; the GitHub workflow configures
Python 3.10/3.13 on Linux/Windows, but configuration is not remote CI success.

First remote run `38672382210` passed Linux but exposed Windows redirected stdout
using a legacy code page, which could not emit CJK evaluation JSON. The CLI now
sets UTF-8 output explicitly; a subprocess regression starts with cp1252 stdout
and verifies valid UTF-8 JSON. This fixes report transport, not application behavior.

Regenerate synthetic JSON reports by importing `wiki.py` and calling audit/evaluate,
or capture their CLI JSON output. Preserve UTF-8; reports intentionally exclude
host paths, credentials, private project facts and raw operational logs. Do not
overwrite the historical independent trial with an inferred new result.
