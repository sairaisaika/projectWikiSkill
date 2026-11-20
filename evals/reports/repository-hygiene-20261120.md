# Repository hygiene and Git boundaries — 2026-11-20

Source baseline: main `71c9c2301679abc096c94e7e5d95f1eec45ba1bd` (#73).
Scope: shipped agent guidance, native Wiki discovery and real temporary Git
repositories with synthetic public bytes. No consumer project or local user tree
was touched. No hooks, automatic ignore/staging/cleanup, release or installation.

## Design and boundary

The [owning method](../../project-wiki/references/repository-hygiene.md) connects
pre-creation, post-generation, pre-staging and pre-commit review. Shared precise
ignore suggestions, repository-local excludes (shared by linked worktrees) and cross-repository personal
preferences remain distinct from project tracking and protected retention.
The existing Maintenance section supplies the canonical/private Wiki boundary
and path/configuration index; new Wiki setup uses the same template. The fixture
and maintainer query indexes route hygiene and staged-diff questions there.

This is an authored decision workflow, not a filename classifier or secrets
scanner. Tests verify commands and discoverability; they do not certify natural
agent adoption, sensitive data safety, remote gate enforcement or authorization.
The added routes intentionally carry planned evidence for their review plans.

## Synthetic acceptance

`python -m unittest discover -s tests -p test_repository_hygiene.py -v`: 12/12 pass.
Every case creates its own real Git repository with global/system configuration
isolated. Git mutating commands exist only to arrange disposable test state.

| Case | Observed evidence |
|---|---|
| Skill → native entry/query → owning procedure | English, Chinese and staged-diff queries select the hygiene route in both Wiki roots; the fixture's link resolves to the one packaged method |
| Shared output vs repository-local noise | Exact `.gitignore` and Git-resolved `info/exclude` report different rule provenance; no global exclude configuration is invented |
| Linked-worktree exclude scope | Both worktrees resolve the same `info/exclude`; a rule written from either side affects both. These rules cannot provide worktree isolation |
| Excluded ancestor and child negation | `/tests/` defeats the child exception; the documented traversable-ancestor pattern includes the public fixture while both sibling controls remain ignored |
| Required lockfile, example and fixture | Overbroad `*.json`/`.env.*` hide required paths; negated public fixture reports a matching rule yet remains untracked rather than ignored |
| Tracked-but-ignored | Default check-ignore omits the tracked path; no-index reveals the rule; index bytes and HEAD stay unchanged |
| Index vs worktree and late staged arrival | Cached patch contains the staged version only; repeated name/status changes when a new path is staged; configured external diff/textconv/fsmonitor do not run |
| Rename | NUL-delimited status retains both old and new paths including spaces |
| Literal path | Wildcard-looking path does not expand to a different known file |
| New and existing Wiki | Boundary template creates a canonical entry; missing configuration fields extend that same page without replacing original text or a second Wiki |
| Ignored retained archive | Hold-bearing synthetic archive remains intact; explicit storage exclusion emits no private filename and counts zero bytes |
| Missing history / Git failure | Fresh repository HEAD failure and absent-root error remain distinguishable from no ignore match |

First run retained a real defect: applying `--literal-pathspecs` to check-ignore
returned 128. The command examples now apply it only to pathspec-aware commands;
tests execute argv extracted from those examples and pass. The first full suite exposed three stale fixture-count assertions (8 routes / 21
known queries); these now expect 9 routes / 24 known queries and preserve the
intentional one-wrong-answer control (23/24). No threshold was relaxed. No real secret was
used or echoed. This is a self-authored regression exercise, not a blind agent trial.

## Independent review follow-up

Review of the first candidate found that the original exclude-scope wording
incorrectly implied isolation to one worktree. Corrected the method, fixture and
summary to describe repository-local scope shared by linked worktrees, with a
scope check before proposals and an explicit warning against relying on it for
true worktree isolation. A bidirectional real linked-worktree regression now
checks that finding. Added the excluded-parent negation counterexample and a
traversable-ancestor control with two still-ignored sibling files. No ignore
configuration in this repository or a consumer repository was changed.

## Validation closure

Local environment: Linux, Python 3.12.14, Git 2.56.1.

- Full unit suite: 481 collected, 480 passed, one existing Windows-junction skip.
- Fixture contracts: 12/12 passed.
- Fixture Wiki check: ready, no drift, 9 routes, minimum structural score 92.
- Fixture evaluation: 24/24 known queries top-1/top-2, 4/4 unknown controls rejected;
  declared compound task-map case passes. Saved reports equal live results.
- Maintainer Wiki check: ready, no drift, 11 routes, minimum structural score 92.
- Default, legacy-hook and portable-hook package builds plus source doctor:
  package valid; source, support, input bytes and identity match in all three.
  Packages were temporary and no profile was installed or activated.
- `git diff --check`: clean. Only canonical method/Wiki, synthetic tests,
  generated route projections and sanitized evidence are proposed for tracking.

Exact-head remote CI and independent review are pending; the coordinating thread owns review and merge. Remote branch
protection and release gates were not inspected and are not inferred from CI files.
