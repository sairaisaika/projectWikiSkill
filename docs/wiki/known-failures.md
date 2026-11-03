# Known failures

> Reviewed: 2026-11-03 against c062224

Recurring failure classes seen while building and piloting the skill, each attributed to the
owner that had to change. Evidence is skill-repo commits (`git show <sha>`) and
[evals/reports](../../evals/reports/README.md); the reports carry the details and limits, so
rows do not restate them. This checkout is shallow (grafted at `5c85d0c`, 2026-10-19). Older
commits exist upstream and need `git fetch --unshallow` to show.

## Fix owners

The miss layer ([wiki-evolution.md section 4](../../project-wiki/references/wiki-evolution.md#4-diagnose-a-miss-before-repairing-it))
says why something was missed; the fix owner below says which repo or actor changes.

| Fix owner | Means the fix belongs in |
|---|---|
| skill logic | `project-wiki/scripts/*.py`, `scripts/*.py` or their tests |
| skill docs-claims | SKILL.md, references, README, PLUGIN_PLAN, report wording or status labels |
| host platform | Codex/Claude loader, trust, cache or OS/filesystem behaviour; observe and adapt only |
| consumer native tooling | the consuming project's own router, generators and touch gate; not this repo |
| process-caller | how a coordinator invoked the skill (inputs, checkout, output paths) |
| agent adoption | a worker had the right text and did not use it |

## Attribution table

| Symptom | Fix owner | Example | Fix or status | Would a doc have helped? |
|---|---|---|---|---|
| A status label or summary no longer matches the evidence ("pending", "candidate", a mixed-up replay cutoff, a provenance correction) | skill docs-claims | `6e07e70`, `60fa78a`, `613a5f5` | Each corrected by hand; still recurring, see [open drift](#open-drift-found-2026-11-03) | Yes. One status table plus a separate changelog removes the restated caveats; flag and index drift needs a test, prose drifts too |
| Readers of a saved packet resolved page paths against the wrong base; `wiki_root` was saved but not shown | skill logic | `0477d69`, [saved path basis](../../evals/reports/wiki-path-basis-c122-20261024.md) | Fixed: reading views expose the saved path basis | Partly. The [path kinds](architecture.md#path-kinds) glossary names the gap |
| A source path one OS cannot resolve (an embedded NUL on Linux) aborted the native source-context comparison (`compare_native_sources`); Windows temp short names and Linux path byte limits broke fixtures | host platform, then skill logic | `22b0a84` (fix), `adc23ca`, `c0f2872` (fixtures) | Fixed: unresolvable paths cannot satisfy a selected identity and are skipped; CI runs ubuntu and windows on Python 3.10 and 3.13 (`.github/workflows/check.yml`) | Little. Only the OS matrix catches these |
| Packaged hooks installed, but the host listed zero hooks; a guessed portable declaration did not help | host platform | `3bd725d` then `5e23169`; [portable declaration](../../evals/reports/portable-hook-declaration-c119-20261024.md), [hook layout](../../evals/reports/runtime-hook-layout-c120-20261024.md) | Fixed for the observed loader: the legacy hook layout matches its format branch (`package_plugin.py --hook-layout`) | Not for the cause. A rule "check the host loader source before shipping a declaration change" would have saved the guessed release |
| After an update, a trusted hook reads as modified and waits for review; an official update removed the older cache directory | host platform | `26a7d8e`; [host adoption](../../evals/reports/host-adoption-v025-20261022.md), [supplied hook observations](../../evals/reports/supplied-hook-observations-c179-20261025.md) | Accepted host behaviour. `plugin_doctor.py --codex-hooks` reads a saved listing and never grants trust | Partly. Stops "installed" being read as "trusted"; see [hooks-and-gates](hooks-and-gates.md#field-evidence) |
| The host clipped `show` output to a 2 KiB preview | host platform, skill logic | [native workflow](../../evals/reports/native-workflow-20261021.md) | Fixed: `show` defaults to `--view index` with exact expansion; SessionStart emits an `index_delivered: false` notice above 6 KiB instead of truncating | No. Only real use showed it |
| Evidence came from a stale checkout or the wrong peer; a coordinator set the wrong selection variable | consumer native tooling (C60), process-caller (C116) | [source selection](../../evals/reports/evidence-source-selection-c60-20261022.md), [selection invocation](../../evals/reports/native-selection-invocation-c116-20261024.md) | C60 repaired in the consumer's native gate; C116 was a caller error, and the skill's strict comparison rejected the wrong peer before a capture was written | Partly. A CLI reference with the selection inputs shortens diagnosis |
| A selected source policy or source qualifier was lost between capture and later steps; peers could collide | skill logic | `0c87147`, `21b4ba5`, `dfc576d`; [source consistency](../../evals/reports/native-source-consistency-c91-20261023.md) | Fixed | Yes. An invariant with no test; now tracked in [invariants](invariants.md) |
| Repeating `--files` kept only the last group | skill logic | `f9395af` (`nargs='*'` became `action='extend'`); [repeated file groups](../../evals/reports/repeated-file-groups-c126-20261024.md) | Fixed | Partly. A CLI reference stating repeat and empty semantics, plus the guarding test |
| Read-only tasks needed edit paths; a worker's return shape was rejected | skill logic | `48812f3`, `9296de8`; [read-only return](../../evals/reports/native-readonly-return-20261022.md) | Fixed: `start`/`delegate --read-only`; `review-template` prepares unreviewed return fields | No. Found only through real delegation |
| Bundled support sources were verified only through the skill copy; newline-only differences in an installed cache; a Windows junction escaped the source tree | skill logic, host platform | `7618876`, `ec1fdf2`; [newline provenance](../../evals/reports/package-newline-provenance-20261022.md), [lifecycle delivery](../../evals/reports/lifecycle-delivery-c118-20261024.md) | Fixed: independent support-source checks, schema-2 text canonicalisation, junction regression test | Partly. Each was an invariant with no test |
| A coordinator reused an output path and overwrote selected evidence outside Git | process-caller | [preserved evidence](../../evals/reports/preserved-evidence-c96-20261023.md); guard in `b2200cd` | Optional `--preserve-artifact` hash checks; no write prevention | No. Operator mistake; the code guard was the right response |
| Test-only follow-ups after remote CI: fixture paths not canonical on Windows checkouts, assertions not portable | skill logic (tests) | `50039f0`, `d9a734c`, `6573e0a`, `3276f71` | Fixed per commit | Little. Normal red-green noise; a canonical-temp-root note would cut a few |
| Generated views committed in a consumer repo conflicted across parallel branches and needed regeneration commits | consumer native tooling | [evolution pipeline](../../evals/reports/wiki-evolution-pipeline-20261029.md) (miss layer 4) | Outside this repo. The skill classifies it as process and architecture | No for the skill |
| A consumer's native touch gate rejected a push for unacknowledged unchanged satellites, forcing follow-up acknowledgement commits | consumer native tooling | [native return context](../../evals/reports/native-return-context-20261022.md); code `9dd9df7`; later route-by-rule guidance `16cad6d` | The skill copies the consumer's native `workflow` object into every reading view so the requirement is known early; the gate is the consumer's | No for the gate. Route-by-rule guidance reduces the page fan-out |
| A worker coded first despite a wiki-first prompt | host platform/delivery + skill logic (no design predicate); repeated adoption | `dd724b8` | Optional Claude pre-edit gate (`edit_gate.py`, `design_first`) | No. Another reminder line is not a repair |
| An acknowledgement line written as a free-form list was not parsed | agent adoption | [evolution pipeline](../../evals/reports/wiki-evolution-pipeline-20261029.md) (miss layer 2) | Caught by the consumer's native gate; the corrected format passed; no skill change | Partly. See [hooks-and-gates lesson 5](hooks-and-gates.md#lessons-for-the-skill) |

## How to attribute a new failure

1. Start from execution evidence: the command line, the packet, the hook output, CI logs,
   the commit. Do not start from the page the worker should have read.
2. Classify with the miss layers in
   [wiki-evolution.md section 4](../../project-wiki/references/wiki-evolution.md#4-diagnose-a-miss-before-repairing-it).
   Several layers can hold; record each. Unknown delivery stays unknown.
3. Map to the fix-owner column above. If the fix needs the consumer repo or the host, record it
   here and stop; do not patch around it in skill text.
4. Name the repair in one place: code plus test (skill logic), one owner doc (docs-claims),
   or a report row (host platform, process-caller, adoption).
5. Add a row only for a new class. Otherwise add the sha or report to the existing row.
   Keep pilot names, paths and revisions out (public repo).

## Open drift found 2026-11-03

Checked against the working tree at `c062224` plus the change that added this wiki.

| Where | Says | Code says |
|---|---|---|
| Shipped references (`project-wiki/`) | No mention of `--codex-hooks` or `--codex-hooks-cwd`; [Host observations](../../project-wiki/references/collaboration-workflow.md#host-observations) lists only `--codex-inventory`/`--codex-version-file` | `scripts/plugin_doctor.py` defines both flags (lines 422-423); documented in `README.md` and `docs/PLUGIN_PLAN.md`; absent from `project-wiki/` |
| `project-wiki/SKILL.md:214` | "Startup/resume/compaction delivery" | `lifecycle.py` `START_SOURCES` and both `hooks/*.json` matchers accept `startup, resume, clear, compact, fork` |
| [evals/reports/README.md](../../evals/reports/README.md) | Index omits 6 reports: `evidence-selection-diagnostics-20261029`, `live-collaboration-c22-20261022`, `native-return-context-20261022`, `source-delta-and-child-adoption-c23-20261022`, `source-structure-readonly-adoption-c22-20261022`, `wiki-evolution-pipeline-20261029` | The files exist; 2 JSON inputs (`stream-input-20261022.json`, `host-skill-only-20261030.json`) are reachable only from their reports |
| `docs/PLUGIN_PLAN.md` "Local candidate commands" | `package_plugin.py --output` only | `--with-lifecycle-hooks` and `--hook-layout {legacy,portable}` exist; `--hook-layout` is documented in collaboration-workflow.md and README.md |
| `docs/PLUGIN_PLAN.md` headings and slices | 0.2.10 to 0.2.17 headed "candidate" (0.2.14 is recorded as adopted at the bottom); no 0.2.15, 0.2.18 or 0.2.19 section; "Host lifecycle" slice reads `pending` | `plugin.json` is 0.2.19; the reports index records a trusted controlled startup delivery ([saved path basis](../../evals/reports/wiki-path-basis-c122-20261024.md)) |
| Undocumented flags | `workflow.py capture --wiki-root` and `wiki.py query --limit` appear in no doc | Both are defined (`workflow.py:777`, `wiki.py:804`) |
