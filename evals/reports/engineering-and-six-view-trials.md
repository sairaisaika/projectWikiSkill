# Reference-driven engineering depth and six-view trials

Date: 2026-10-14. These are two independent read-only fixture trials after the
original skill, plus author-run structural, rendering and selected behavior checks.
No expected task IDs, parent conversation or prior reports were given to evaluators.

## What was adopted from the user reference

The first two supplied source images are only 176×176; fine labels cannot be reliably
read. Only their visible diagram/text organization was used. The third image was
read at original resolution in sections. The user subsequently supplied the explicit
six-view table, which is the framework's direct requirement.

Adopted: precise fields/units, explicit state/recovery guards, interaction ordering,
resource ownership, source/schema binding, and lightweight decision rationale. Not
adopted as evidence: praise about developer seniority, claims of maximal information
entropy, or mathematical completeness inferred from presentation. No reference image
or private project detail is redistributed in this repository.

## Trial 1: recovery and field evolution

Fresh evaluator followed AGENTS → engineering entry → recovery/wire pages and
queried `retry late response` and `heartbeat fields`. Drafted a six-part plan before
reading cited source. Exploratory source-content searches before/after: 0/0;
two directory inventories and two curated queries before the plan. Then directly
read cited recovery/heartbeat source and the feature tests; ran the then-five feature
cases. Documentation before plan: 5,442 fixture bytes, excluding helper/reference
output. Elapsed time and baseline speedup were not measured.

The plan located contracts, ordering, failure/retry changes, consumers, offline exit
evidence and unknowns. Source verification exposed limitations: the retry bound is
conditional on caller bookkeeping; attempt validation is branch-local; there is no
request/generation correlation after retry resumes; Python bool is accepted as a
sequence integer. These were added to scenario tables, parameter domains, rationale
and independent boundary tests without changing fixture application behavior.

Ordinary article-interface work stayed on its short route and did not require ABI
or lifecycle detail. The evaluator did not render diagrams or claim live behavior.

## Trial 2: all six views and a small change plan

Another fresh evaluator followed AGENTS → engineering entry → project-views,
public-api, engineering-contracts and the route index. It drafted the six-view
interpretation and article-error/heartbeat-compatibility plan before reading code.
Then directly checked seven source files and two fixture test files. One documentation
filename inventory, zero source-content or fallback searches; no measured elapsed time.

The evaluator matched all six questions to concrete views and source, confirmed no
invented services or persistence, and distinguished offline execution from deployment
acceptance. It found a fixture-level Linux/Windows CI claim could not be verified
from fixture source; that claim was removed from the deployment page rather than
pretending a local diagram verifies root CI. It also noted missing populated-result
and thrown-exception article tests, which were added as selected actual behavior checks.

The plan preserved legacy clients, kept v1 bytes stable until migration is designed,
and proposed only affected contract/diagram/test updates. The trial did not measure
rendering, speedup or broad adoption.

## Current measured results

- Seven valid routes; baseline structural average 98.86, minimum 92. The absent TS
  capability runner remains an explicit gap and loses points. These are field scores.
- Twenty known questions top-1/top-2 20/20; four unrouteable controls 4/4. This is an
  author-curated regression set, not another independent blind trial.
- Six view kinds, one each, with no applicability waivers. Missing required kinds
  fail check; a waiver is never counted as a diagram.
- Recovery model: 25/25 declared state/event pairs classified, seven guarded outcomes;
  parameter/input/race coverage and guard exhaustiveness remain unproved.
- Wire model: 4/4 fields have source provenance; geometry is bounded/non-overlapping.
  Actual fixed bytes and rejection cases are tested; native ABI/peer compatibility is not.
- Mermaid 11.17.2 parsed/rendered all six diagrams in isolated headless Chrome. The
  author inspected images for labels/readability and separated the static TS node
  from runtime dependency arrows. Receipt hashes bind these diagram sources.
  Screenshots are temporary local artifacts; rerun `evals/render-diagrams.mjs` to
  regenerate them. Syntax/rendering and semantic correctness are different checks.
- 58 helper/package test cases: 57 pass, one Windows symlink-permission skip; 12
  actual fixture contract tests pass. No external transport or physical device ran.

The core Python check does not render Mermaid. It checks declared references and
coverage, plus tests bind the saved rendering receipt to current source so future
diagram edits require an explicit re-render. Optional renderer dependencies do not
become runtime dependencies of the skill helper.
