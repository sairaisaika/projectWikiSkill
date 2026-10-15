# Independent read-only forward trial

Date: 2026-10-14. Scope: the first-draft skill and synthetic fixture, before the
failure-mode and compound-query corrections. The evaluator had no parent history,
expected task IDs, prior implementation knowledge or other repository context.
The request covered improving public interfaces, dependency interfaces, model
tagging and conflict rules, with a plan before direct source verification.

## Actual use receipt

- Followed fixture AGENTS → engineering-entry → the four interfaces sections.
- Ran one combined query, then separate public API and external-source queries.
  The combined query's top two results omitted two relevant task surfaces.
- Drafted the wiki-based plan before opening the cited implementation.
- Exploratory source searches: 0 before the plan, 0 after. Direct source/test file
  reads for verification: 6. Helper queries themselves read curated files.
- Fixture documentation consumed: 3,376 bytes at that draft: AGENTS 276,
  engineering entry 875, interfaces 2,225, as measured by the evaluator. The evaluator
  also read the skill, quality model and maintenance reference; those are not included
  in this fixture-only byte count.
- Plan addressed 6/6 categories: outcome, dependencies, interfaces, deliverables,
  exit evidence and unknowns. This is reviewed category coverage, not an automated
  claim that implementation is correct.
- No application changes, test execution, deployment or publication by the evaluator.
- Elapsed time, comparative speedup and general adoption rate: not measured.

## Plan produced

1. Add a proposed result-returning article client while preserving legacy data/None.
   Define the error shape before implementation; test empty, unavailable, populated
   results and legacy callers. No HTTP/auth server exists in the fixture.
2. Specify replacement ExternalSource requirements; preserve suggestions when counts
   is missing. Add a TypeScript contract runner/tests, which the fixture lacks. A
   real provider adapter is new work, not already implemented.
3. Define suggested-tag fields before evolving Tagger/sanitize_suggestions. Preserve
   None vs [] and normalization unless intentionally migrating. Confidence and
   assertion integration need design.
4. Specify intended conflict precedence before changing resolve_tags/effective_tag.
   Cover no assertions, differing/equal tiers, conflicts and malformed assertions.
5. Update interface contracts, compatibility notes, checks and routes together.

Error/schema/policy decisions precede implementation; client and TS-capability work
are otherwise independent. Exit evidence is offline only. Desired provider/model
shape, error detail, confidence, conflict rules and persistence/migration remain open.

## Verified source findings and corrections

The evaluator confirmed the four change surfaces and found limitations omitted from
the initial prose: dependency/model exceptions propagate; sanitizer assumes strings;
assertion keys/operations lack explicit validation. These were added to fixture docs
and structured returned/thrown/unsupported failure-mode fields, now required for
interface routes. No fixture application behavior was changed.

The evaluator also found that a compound query silently showing top-two candidates
could be mistaken for full impact coverage. The helper now reports truncation and
the skill instructs decomposition by task surface. The two-section reading target
is now per distinct task surface rather than per arbitrarily broad user request.

This was one independent fixture trial. Later tests of the corrected behavior are
regressions, not a second blind trial. The synthetic routing report is a self-test;
neither it nor this one trial proves live product behavior or universal adoption.
