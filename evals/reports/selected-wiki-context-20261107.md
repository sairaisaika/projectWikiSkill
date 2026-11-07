# Directly selected Wiki context, 2026-11-07

## Observation

An installed 0.2.20 copy reached a fresh Claude implementation session. The first
guided real task still used native long-text output: three file queries recovered
the owner tail, but did not establish all original owner-page reading before the
first edit. Source-level behavior passed independent acceptance; its Wiki return
was sent back because current status and historical verification remained mixed.
Neither installation nor structural documentation checks established successful
semantic adoption. The return was accepted only after original current-state
sections, separate historical notes and accurate execution timestamps were added.
A separate long-running worker resumed its pre-installation task; no new Skill
content delivery was observed there. That continuation is not counted as a fresh
adoption sample merely because the account limit reset.

In that guided maintenance return, prepare/show delivered both source-file owner
records in one call. However, a Wiki file explicitly included in `--files` was
unregistered by the native source-owner index and absent from saved reading views.
A coordinator probe of `show --view page` reproduced the missing selected page.
This is an actual workflow gap, not a request for another acknowledgement gate.

Consumer identifiers, paths, source and session transcripts stay private. Only
filtered tool metadata and necessary visible results were reviewed; this report
does not publish hidden reasoning, credentials or product data.

## Change and regression scope

Prepare additionally captures explicitly selected Markdown under the configured
Wiki root. A separate selected-page list records captured or absent snapshot state;
native unregistered files and owner edges are untouched. Page views retain source
freshness, immutable-snapshot reading and display-budget refusal. Native/query
pages deduplicate with direct selections. No new manifest, gate, installation or
implicit execution was added. Exact verification-history headings are recognized;
product headings such as History editor remain current body content.

Nine new behavior tests failed before their implementation: selected-page cases,
three explicit history-label subcases, and a quoted verification note inside an
explicit history section. That last note had been promoted to latest verification
and disappeared from the history view; it now stays in saved historical text.
All 34 focused cases pass afterward.
Controls include unknown query, absent native ownership, missing future page,
nondefault Wiki root, similarly named outside directory, post-deletion snapshot
reading and explicit section selection for an oversized page.

## Real native replay

A separate stable consumer checkout was replayed with its actual reviewed native
router and explicit execution opt-in. With one selected Wiki file and no native
owner edge, installed 0.2.20 saved zero pages and could not open the selected page.
The candidate saved one page (43,678 authored body characters) and returned it
through the saved-page API while retaining the empty owner list and unregistered
input. This is a coordinator replay, not worker adoption of the candidate.

## Acceptance boundary

The active worker continues using installed 0.2.20. This candidate has not replaced
that installation, been merged, or established better delivery across independent
workers. Guided tasks, semantic rework, source tests and the native replay are
separate evidence. Token/time savings and causal improvement are unmeasured.

## Source verification

- Full Python source suite: 289 tests run, one explicit platform skip.
- Focused reading suite: 34 cases pass, including the nine new regressions.
- Fixture suite: 12 tests; fixture check and route evaluation pass.
- Maintainer Wiki build/check pass. An initial new rule used the wrong manifest
  shape; the native check rejected it. It now has a stable ID, explicit source
  references and the guarding test; the failed check was retained privately.
- Plain, legacy-hook and portable-hook packages each pass doctor with matching
  source, support files, input bytes and identity. No host settings were changed.
- The packaged skill also passes the standard skill-format validator on Windows.
- Cross-platform PR CI remains pending until a run is observed; local Linux
  tests do not stand in for Windows/Python matrix results.
