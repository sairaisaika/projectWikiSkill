# Learning a system through its wiki

Use when the goal is understanding a project without a predetermined change, or
when a wiki is precise as a reference but difficult to enter. Do not grade this
mode only by search rank, symbol coverage or diagram count.

## Read before repairing

Read the existing opening as a reader would encounter it. Record what mental model
it gives before opening implementation. Then traverse chapter introductions in
order and follow mechanisms where the explanation raises questions. If the user
requests every page in full, read them in bounded batches and maintain a coverage
ledger; a table of contents or extracted lead paragraphs is a survey, not full reading.
Report partial coverage explicitly and keep unread work outstanding. Do not claim
an independent newcomer trial when the reviewer already knows the repository.

Look for concrete learning friction: product purpose appears after workflow rules;
terms presuppose another chapter; a long “one sentence” mixes normal behavior with
exceptions and audit history; similar names denote unrelated concepts; chapters
list components without explaining why they belong to one product. Record the
confusion and the page, not a subjective numeric score with no reader evidence.

## Build a short entrance to the existing wiki

Choose only what helps this project's readers:

1. Purpose, actors and normal activities in the project's own terms.
2. A small conceptual map with an explicit arrow legend. Concept association,
   navigation, data projection, function call and deployment are different relations.
3. A few easily confused concepts, with links to their authoritative definitions.
4. Connected examples showing who produces facts, who owns changes, who consumes
   projections, and where access or failure boundaries intervene.
5. A reading trail with a question each stage answers, then links to mechanisms.

Use plain language before identifiers; keep identifiers as precise anchors in the
mechanism layer. Preserve exceptions that would reverse the reader's understanding,
such as a shared backend with missing mobile consumers, a declared-but-unused
setting, or a UI-only gate. Do not simplify a scenario into a falsely universal
happy path. Do not duplicate full contracts, states or operational snapshots in the
intro. A conceptual figure needs its own evidence even when it is intentionally
less detailed than a call graph.

Keep the task entrance beside the learning entrance. Learning order is not a
mandatory checklist for every future edit. Retain native indexes and parsers;
register the new entry so real site navigation and source links can reach it.

## Review comprehension and truth separately

Ask the reader or reviewer to retell the product, trace one cross-domain activity,
and distinguish state ownership from display, identity from UI mode, and code
presence from deployment. Verify the resulting causal explanation against selected
writers, consumers and guards. Source checks should resolve concrete uncertainties,
not replace the initial reading with a repository search report.

When correcting a claim, check its lead paragraph, figure, table, status summary,
related-page wording and pending tests. A corrected body with a stale introduction
still teaches the wrong model. Label partial source rechecks without refreshing a
whole page's review stamp as though all its claims had been re-audited.

Evidence to report separately:

- Actual full-read pages/ranges, surveyed entries, unread material and revisions.
- Reader confusions and repairs, with a before/after explanation.
- Selected semantic checks and their limits.
- Real navigation, links and rendered diagrams after the edits.
- Familiar self-review versus independent retelling, with no invented timings.

SoulNest supplied a useful reciprocal example: its producer/consumer pages and
cross-feature bridge tables explain responsibility well; the missing learning
entrance exposed this skill's earlier overemphasis on finding edit locations.
Adopt the principle without prescribing SoulNest's 26 chapters or terminology to
other projects.
