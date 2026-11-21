# ProjectWikiSkill (PWS): log-to-contract debugging — 2026-11-20

Baseline: main `6639e41c28a957ec49ef3ac29f2f238681b7ebf5`, in a fresh isolated
checkout. No root AGENTS.md or .agents skills are present; the fixture's AGENTS
and maintainer engineering entry supplied the applicable native routes and checks.

## Assessment before editing

Maintenance already covers change/handoff/incident receipts and retained evidence;
engineering-depth and route-contract already locate native API/schema/invariant
sources, consumers and positive/negative checks. The missing seam is a concise
symptom → safe event → exact technical contract → consumer/check/unknown path.
That navigation belongs to PWS; installing a logging stack, collecting production
logs or imposing a schema/gate does not. This change extends the existing
[engineering-depth owner](../../project-wiki/references/engineering-depth.md#debug-from-evidence-to-a-technical-contract)
and its SKILL/Maintenance/contract entry links. It creates no generic LOG.md or
second decision/audit ledger, and does not alter consumer or production code.

## Synthetic evidence and executable acceptance

The [existing article contract owner](../fixture-project/docs/wiki/interfaces.md#diagnostic-evidence)
links six authored packets to ArticleSource → get_articles → read_articles and
to exact source hashes. `article-result/v1` is a synthetic snapshot label, not a
deployed protocol/version. The helper and event shape are fixture-specific and
are not included as a logging runtime or redactor in the shipped skill.

Seven focused tests cover source-byte binding; actual offline empty/present/error
mapping and propagated exceptions; sample success/error/mismatch; noisy, wrong
version or unjoined observations; accepted/queued without terminal evidence;
missing/filtered/sampled/dropped evidence; and exclusion of invented unsafe fields
and identifiers without printing their values in failure assertions. The result
always keeps runtime unverified. No real sensitive data or runtime logs were used.

The example records producer → synthetic sink/query → authorized fixture reader,
with coverage/retention/sampling limits and an explicit absence of runtime sink
configuration/delivery. Accepted does not mean succeeded; absence under sampling
is unknown, not evidence an operation never happened. Raw logs remain in approved
protected stores even for private repositories; safe pointers inherit PR75
publication/ref/audience and retention rules.

Two default-package navigation tests walk the actual packaged entry link, use its
Wiki query to resolve source roles, follow sample/check links and run the focused
fixture check. Counterfactual ordinary-edit queries return no diagnostic match;
an early skip cue preserves native mandatory gates and triggered hygiene. These
mechanical checks establish reachability/off-topic control, not agent behavior.

## Cold synthetic navigation

Two independent fresh-context readers received only the candidate default-package
entry and native project entry plus a task; no expected owner or packet answers.
The diagnostic reader recorded conclusions before reading the test implementation:

| Packet | Initial finding |
|---|---|
| a / operation 1 | Joined empty success, consistent with the contract |
| b / operation 2 | Known service-unavailable error; legacy consumer loses precise cause; retry unknown |
| c / operation 3 | Joined service-error/client-empty mismatch |
| d / operation 4 | Acceptance only; completion unknown |
| e | Sampled absence; occurrence/outcome unknown |
| f | Missing correlation/consumer evidence; cannot join (the check calls it unusable) |

It read the packaged entry, project entry, one specialist (`engineering-depth`),
contract owner, samples, three native source files, and then helper/test source.
The discovered focused command passed all seven tests with bytecode writes off.
It kept actual build, sink coverage and runtime evidence pending. No broad search,
remote access, event-instruction execution or production collection occurred.

The ordinary spelling-only scenario read the packaged entry, native AGENTS and
known target source, and checked only for a scoped child AGENTS (absent). It read
zero specialist references and required no PWS-only record or Wiki update. It
preserved native gates and explained that new artifacts, stage/publish work,
behavior/contract changes or uncertainty would change the route. This was a
hypothetical navigation control, not a completed spelling fix or speed benchmark.

Observed friction: the diagnostic cue was late in SKILL.md; its single canonical
link was moved into Choose the work after the trial. The example's method link
points to the repository source copy, while the reader used the matching packaged
copy. No second cold trial of the moved cue is claimed; the final packaged
navigation checks cover its link. Root's independent draft review remains separate.

## Validation closure

| Check | Result |
|---|---|
| Focused synthetic diagnostics | 7 passed (included in fixture suite) |
| Default-package navigation | 2 passed (included in unit suite) |
| Full unit suite | 494 tests, OK, 1 existing platform skip |
| Fixture suite | 19 passed |
| Fixture Wiki check / evaluation | Passed; existing 24 known queries and 4 unknown controls, plus task-map case |
| Maintainer Wiki check | Passed; 11 routes ready |
| Default / legacy / portable package doctor | All passed: package_valid, source_match, source_support_match, source_input_bytes_match and source_identity_match true |
| Whitespace validation | git diff --check passed |

A post-implementation counterfactual ran the two new packaged-navigation guards on
an archived baseline tree with only the new test copied in: both failed at the
missing entry link/skip cue. The candidate passes both. This is regression evidence,
not a claim that the tests were written before the method or proof of agent use.

Exact-head remote CI and independent review remain pending; the draft PR carries
the immutable head and CI run receipt. No install, release, merge to main, production
collection, downstream mutation, ignore/security change, broad hook or new universal
gate is authorized.


## Main integration and assertion precision — 2026-11-21

The existing draft integrates verified main
`08bc35b5e4dde8bb1396971e800f5a2b822f9828`, including the approved native section
placement and marketplace changes. Their canonical guide/report and marketplace
files/test helper are byte-identical to main; both changelog and report-index rows
are retained. Only Current task changes in PROJECT; history/conventions stay intact.
The earlier merge preparation against `90f131a` was unpublished and superseded
when main advanced, rather than publishing against a stale base.

Independent review found that the offline event check inferred unavailable from
`result.get('data')`, allowing a wrong actual service error code to go unnoticed.
The check now asserts the complete actual success/error result and legacy consumer
output before building synthetic events, then copies the observed error code.
Assertions use categorical failure messages without echoing supplied values.
An in-memory synthetic wrong-error substitution passed the old focused test and
failed the corrected test with one assertion failure; no production source changed.
The seven normal diagnostic tests pass. This is a test-precision correction, not
new runtime evidence, a new contract or a production fix.

Combined validation passes: 495 unit tests (one existing platform skip), 19
fixture tests, both Wiki checks/evaluation and all five identity/source checks in
default/legacy/portable package doctors. The two navigation tests and twelve
package tests run together (14 passed), proving the existing imported helper and
marketplace check coexist in this tree. The normal diagnostic suite remains seven
passing tests. Exact-head remote CI is pending publication; the PR will record the
new immutable head, base and CI receipt. This is a normal merge into the existing feature branch, not a merge
to main, install, release or update to another PR.
