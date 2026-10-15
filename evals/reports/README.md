# Validation scope

These reports describe measured runs, not expected scores to copy into a new project.

| Artifact | What it establishes | Limits |
|---|---|---|
| fixture-structure.json | Four schema-2 routes resolve; structural average 98, minimum 92 | A missing TS test deliberately loses points; field completeness is not semantic truth |
| fixture-routing.json | 10/10 known questions top-1/top-2; 2/2 unknown controls rejected | Author-curated synthetic self-test, not independent adoption |
| forward-trial.md | One fresh evaluator drafted a six-category plan wiki-first with no exploratory search, then checked cited source | One synthetic trial before corrections; no speedup baseline |
| smv-legacy-audit.json | Existing real project's 10 schema-1 routes resolve; schema-2 precision gaps are reported | Read-only audit; not migrated, not awarded a schema-2 score |

Local validation of this skill: 33 helper/package test cases, 32 passing and one
symlink case skipped because Windows disallows unprivileged symlink creation;
3 fixture application contract tests pass. Skill Creator's frontmatter validator
passes. Python 3.13 on Windows was executed locally; the GitHub workflow configures
Python 3.10/3.13 on Linux/Windows, but configuration is not remote CI success.

Regenerate synthetic JSON reports by importing `wiki.py` and calling audit/evaluate,
or capture their CLI JSON output. Preserve UTF-8; reports intentionally exclude
host paths, credentials, private project facts and raw operational logs. Do not
overwrite the historical independent trial with an inferred new result.
