# Captured page paths — 2026-11-07

In the fresh post-reset CI audit under installed0.2.25, Claude invoked the Skill,
prepared file context, then requested `docs/wiki/22-testing-gates/05-gate-tristate.md`.
That page existed in the capture as `22-testing-gates/05-gate-tristate.md`, but the
error misleadingly blamed older captures. It retried the saved key and used NEXT
before updating Wiki state. The transcript is an actual guided task observation,
not an independent blind comparison.

The repair resolves only exact saved keys with the configured Wiki-root prefix.
Unknown/escaping selections are not inferred; ambiguous spellings reject. Page
and history reads remain snapshot-only without live lookup. `state_update` uses
the resolved canonical key for its existing source-byte/target checks, preventing
a doubled Wiki-root path. No new module, registry, gate or host setting is added.

Four new regressions failed on0.2.25 and pass on the repair: read/history identity,
identical state plans and actual application, unknown/ambiguous/no-page errors,
and a CLI continuation from another cwd with Git unavailable and snapshot-only
preserved. Replaying the exact bad path against the same saved real capture gives
exit1 on installed0.2.25 and exit0 on the candidate; capture bytes stay unchanged.
The replay is snapshot evidence, not a certificate of current project facts.

Source/CI/install/adoption remain separate in [status](../../docs/wiki/status.md#current-state).

Local source acceptance:365 collected /364 executed /1 platform skip,48 focused; fixture tests, fixture check/evaluation and maintainer Wiki build/check passed. Unknown-path errors do not echo oversized caller input.
