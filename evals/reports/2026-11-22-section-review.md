# Section evidence review pilot

Scope: issue #8, public offline fixture copied into isolated temporary Git repositories.
The shipped fixture stays non-opted-in; no downstream project, installed host or live
runtime is exercised. Review records attest an explicit review step, not semantic truth.

`tests/test_section_review.py` reproduces same-count service behavior drift and checks
that the actual fixture contract tests fail. `find` and `check --reviews` retain
`needs_review` after build, which leaves the baseline unchanged. Explicit review of
an available committed revision alone replaces the baseline; dirty selected content
or bindings cannot be attributed to an older commit.

Additional controls cover authored-section-only drift, test-only drift, selected
config evidence, missing/duplicate source and section, corrupt/missing receipts and
Git commits, changed evidence selection, current/immutable text+JSON locators,
normalized CRLF, adjacent prose, unselected source bodies, declared pure symbol move,
read-only queries and projects without opt-in or Git history. Tests execute only
synthetic code; the helper never executes recorded check commands.

Validation commands:

```sh
python -m unittest discover -s tests -p test_section_review.py -v
python -m unittest discover -s tests -v
python -m unittest discover -s evals/fixture-project/tests -v
python project-wiki/scripts/wiki.py check --root evals/fixture-project
python project-wiki/scripts/wiki.py evaluate --root evals/fixture-project --tasks evals/tasks.json
python project-wiki/scripts/wiki.py check --root .
```

The 18 focused review regressions and 540 repository tests pass locally (one existing
platform skip), as do 19 fixture tests, both Wiki checks and 28 routing tasks. A default
package build and doctor source comparison pass; nothing is installed. Exact-head CI
results are recorded in the draft PR after publication; a fresh generated index alone
is not those results. No automatic hooks, daemon, network fetch, authored prose repair,
installation or release were added. Whole-file needle/test boundaries are conservative;
only selected Python symbols have a bounded syntax-aware fingerprint in this pilot.

The first candidate CI exposed a Windows-only test setup error: directly removing
read-only Git objects failed. The no-Git negative control now moves the temporary
Git directory outside the fixture instead; no permission or production behavior
is changed. Final exact-head matrix results are retained in the PR.

Recording also requires the exact opted-in section in the supplied committed rule;
dirty opt-in additions and switches to another existing anchor are rejected. Fresh
non-opt-in controls require no Git executable; only opt-in cases capability-skip
when Git 2.45+ / `--no-lazy-fetch` is unavailable. The no-fetch guard is not relaxed.
