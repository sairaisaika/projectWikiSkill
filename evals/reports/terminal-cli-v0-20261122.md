# Terminal CLI v0: find / status / eval (synthetic evidence, 2026-11-22)

Base: `main` at `68f6a6c188e7eca3287543b8d0af0e7f987f5b87`, local working diff only.
Interpreter: Python 3.12.14 (macOS `/usr/bin/python3` is 3.9 and is refused by the
existing floor). All runs are offline against `evals/fixture-project` and this
repository's own wiki; nothing was published, installed, captured or sent.

## What was added (and what was not)

`wiki.py` gains three subcommands that reuse `load`, `audit`, `snapshot`,
`is_stale`, `rank`, `resolve_route` and `evaluate`. Existing commands and the
`evaluate` report are byte-for-byte unchanged (`tests/test_terminal_cli.py::test_existing_commands_and_import_surface_are_unchanged`;
`evals/reports/fixture-structure.json` and `fixture-routing.json` still equal live output).

| Command | Gate / basis | Outcome |
|---|---|---|
| `find QUESTION [--json]` | manifest present → audit ready → on-disk index not stale → one leading candidate that resolves | owner route, sections, `path:line` + sha256 per source, rules, observations, boundary, unknowns; otherwise `{"determinable": false, "reason": ...}` |
| `status` | same gate | `find_gate: open|closed` with reason; `measurement: not measured` |
| `eval --tasks T [--ledger L]` | `evaluate` self-test = `fixture_reachability`; ledger opt-in = witnessed tiers | tiers reported separately; ledger defects reject the whole file |

Not added: telemetry, hooks, embeddings, server/daemon, auto-capture, uploads, raw
transcripts, `.gitignore` changes. `wiki.py` still imports neither `os` nor `subprocess`.

## find: observed outcomes

| Condition | Command | Exit | Result |
|---|---|---|---|
| Known question, fresh index | `find --root evals/fixture-project "Change the ArticleSource failure contract"` | 0 | `OWNER public-api` with 2 sections, 3 hashed locations (declaration/implementation/consumer), 1 rule, 1 candidate |
| Unknown question | `find --root evals/fixture-project "deploy kubernetes helm chart"` | 1 | `NOT DETERMINABLE (unknown)`; no owner field |
| Source edited, index not rebuilt | test `test_find_fails_closed_on_stale_index_until_build` | 1 | `stale_index`; after `build` the same question is determinable again |
| Route symbol missing | test `test_find_fails_closed_on_invalid_wiki` | 1 | `invalid_wiki` naming the broken route |
| Two routes tie | test `test_find_tie_is_ambiguous_not_first_match` | 1 | `ambiguous` with both candidate IDs; no first match returned |
| No `docs/wiki/routes.json` | `find --root /tmp "x"` | 2 | `helper_manifest_missing` plus `determinable: false, reason: no_wiki` |
| This repository | `find --root . "stale snapshot wiki 检查"` | 0 | `OWNER wiki-helper`, 7 hashed locations, match 26.1 vs runner-up `task-views` 2 of 6 candidates |

## eval: tiers with explicit denominators

Without a ledger (`eval --root evals/fixture-project --tasks evals/tasks.json`):
`passed: true`; `fixture_reachability.top1` 24/24, `top2` 24/24, `unknown_rejection` 4/4;
`cold_discovery`, `eligible_use`, `time_savings`, `negative_controls` = `not measured`.

With a six-line synthetic ledger (header, one baseline, four trials; kept outside
the repository), the same command reported:

| Tier | Numerator / denominator | Note |
|---|---|---|
| cold_discovery (independent, eligible, wiki condition) | 1 / 1 | one witnessed trial only |
| eligible_use | 1 / 1 | based on explicit use; discovery alone is insufficient |
| time_savings | not measured | same query alone does not establish matching task, model, conditions or correctness |
| negative_controls | stale 1/1 fail-closed, no-wiki 1/1 fail-closed | `probe_validated: true` requires independent cold discovery and both negative controls |
| routing_agreement | 1 / 1 | recorded route equals current `rank` top for the same query |

These numbers describe a hand-written synthetic ledger. They are a demonstration of
the report shape, not evidence of adoption or time savings.

Rejected whole, exit 1, no tiers printed (`test_eval_rejects_defective_ledgers_without_partial_results`,
20 cases): empty file, missing/second header, project mismatch, `data_class`
other than synthetic/public, unexpected field (`transcript`), missing field,
duplicate ID, ID shared between baseline and trial, unknown `route_id`,
`found`/`route_id` contradiction, dangling `baseline_id`, baseline query mismatch,
unknown record kind, bad condition, negative or boolean seconds, blank line,
invalid JSON. Errors name the line and field without echoing ledger values.

## Checks run

- `python -m unittest discover -s tests`: 518 tests in the prior candidate, OK (1 skipped, Windows-only); 15 then in `tests/test_terminal_cli.py`.
- `wiki.py check --root evals/fixture-project` and `wiki.py check --root .`: `snapshot_stale: false` after `wiki.py build --root .` refreshed this repository's `route-index.*` (the `wiki-helper` route hashes `wiki.py`).
- `wiki.py evaluate --root evals/fixture-project --tasks evals/tasks.json`: passed, unchanged.

## Limitations

- `find` authority means "on-disk index matches current sources"; semantic accuracy is still not verified.
- Ambiguity is detected only as an exact top-two tie; near-ties return the leader with `runner_up_score` for the reader to judge.
- The ledger format is v0 and self-declared: the helper cannot verify witness independence, timing method or that `data_class` is honest.
- No independent cold discovery, real eligible use or paired time saving has been observed for this change; witnessed rates require vetted input and time savings remain `not measured`.
- `find` runs a full `audit` and `snapshot` on every call (reads every route's sources); acceptable for manifests of this size, unmeasured for large ones.
