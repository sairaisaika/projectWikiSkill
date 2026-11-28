# Page status, plans and retirement

A reader arriving at a page — a person or an agent starting a task — should be able to
see three things without searching: how complete the documented feature is, what work
is planned for it, and which old implementation is waiting to be removed. This guide
defines one derived status line and two structured sections that make those visible,
keep them connected, and keep them honest.

Use it for an established native wiki that already keeps feature completion records
and a debt ledger. A small wiki can adopt the retirement ledger alone. Do not add any
of this to a page that has nothing to say; an empty table is noise.

## The status line is derived, never typed

Each page may carry one generated line under its title. Every figure on it is computed
from records the page already owns. Nobody types a percentage.

| Figure | Numerator / denominator | Source on the page |
|---|---|---|
| Completion | dimensions reviewed with evidence / applicable dimensions | the feature completion record ([feature completeness](feature-completeness.md)) |
| Debt recovery | closed ledger items / all ledger items located on this page | the project's debt ledger, by its declared page location |
| Plan | plan rows deployed or verified / plan rows not dropped | the page's plan section (below) |
| Retirement | rows awaiting removal, and how many are removable now | the page's retirement ledger (below) |
| Verified | the date and revision of the page's current verification stamp | the page's stamp |

Rules that keep the line meaningful:

- Show counts. A percentage may sit beside the counts and never replaces them.
- Name the basis once, in the wiki's manual: what each numerator and denominator
  counts, and what is excluded. A dimension marked not applicable leaves the denominator.
- A page without an adopted completion record shows **not assessed**. It is not 0% and
  not 100%. A page with no ledger items shows **no ledger items**, not "100% recovered".
- A reviewed dimension means its explanation and cited evidence were reviewed. It does
  not mean the product is deployed or accepted. Eight of eight is not acceptance; keep
  the acceptance evidence in the project's own receipts.
- Do not blend the figures into one score, and do not sum pages into a site score
  ([quality model](quality-model.md)). A generated index may list pages with their counts.
- Validate the probe before trusting it: change one record (flip one dimension, close
  one ledger item) and confirm the line moves. A figure that does not move across such a
  control is not measuring what its label says.

## Plan section: planned work lives on the owning page

Plans kept in chat or in a side document are lost at the next handoff. Put planned work
for a feature on the page that owns the feature, as rows:

| Column | Content |
|---|---|
| ID | stable within the page |
| Outcome | the user-visible result, not the task list |
| Lands in | owner section, interfaces or files expected to change |
| Depends on | other rows, decisions, external preconditions |
| State | proposed → accepted → in source → deployed → verified; or dropped, with the reason |
| Evidence | the decision record, change, revision or receipt that supports the state |

- A proposal is marked proposed until its owner accepts it; record who decided and when.
- A row cannot be deployed or verified without naming the revision or receipt.
- A row that replaces an existing implementation names the retirement row it will
  release. This is the link that makes removal follow delivery.
- When a row is verified, move its lasting facts into the page's current-state text and
  keep the row as a dated one-line history entry, so the plan does not become a second
  description of the system.

## Retirement ledger: old implementations awaiting removal

Replaced code, flags, routes, columns, generated outputs and build products linger
because nothing states when they may go. Give each one a row on the page that owns the
replacement:

| Column | Content |
|---|---|
| ID | stable within the page |
| What | path and symbol, route, table and column, flag, or stored artifact |
| Replaced by | the current implementation, or the plan row that will deliver it |
| Still used by | consumers that keep it alive, each with its source |
| Removable when | a condition someone can check (a flag at 100%, a minimum client version passed, zero rows, a date) |
| State | in use → removable → removed, with the date and the deletion record |

- Establish consumers from evidence before marking a row removable: actual callers,
  clients on older versions, scheduled jobs, stored data, external links. "No one seems
  to use it" is not evidence.
- Size, age and ignore status never grant removal authority
  ([maintenance](maintenance.md#inventory-storage-without-cleaning-it)). Protected
  retention overrides a satisfied condition.
- Removal is an ordinary reviewed change with the project's deletion record and focused
  checks. The ledger never wires deletion into a hook, gate or agent startup.
- An opt-in structural check may require that a row not yet removed names something that
  exists, and that a removed row names something absent. That proves the bookkeeping,
  not that removal was safe.
- When the plan row that replaces something reaches deployed and the condition holds,
  move the retirement row to removable in the same change. When the removal lands, close
  both.

## Make it reachable at task start

The sections only help if the task entrance shows them. When a task selects a page, the
first bounded response should include its status line, its open plan rows and its
retirement rows. When a task names files, any retirement row that lists one of those
files should appear before the edit: the agent learns that the file is scheduled for
removal and what replaces it, instead of improving code that is about to go.

Generate one index of all plan rows and one of all retirement rows, removable items
first. These indexes are the reclamation plan. They are projections; the rows on the
pages remain the only source.

## Anti-patterns

- A typed percentage, or a percentage without its counts.
- Treating a full completion record as acceptance.
- Counting unknown, pending or not-assessed as done.
- One blended score for a page or for the whole wiki.
- Marking something removable because it is old or large.
- Deleting because the ledger says removable, without re-checking consumers at that time.
- A plan document that the owning pages do not link, or plan rows that restate current
  behaviour after delivery.

## Minimal shape

```text
> Status: completion 5/8 reviewed (2 gaps, 1 to verify) · debt 3/5 closed · plan 1/3 deployed · retirement 2 waiting (1 removable) · verified <date> <revision>

## Plan
| ID | Outcome | Lands in | Depends on | State | Evidence |

## Retirement
| ID | What | Replaced by | Still used by | Removable when | State |
```

Adopt the shape in the project's own language and native representation
([native wiki adoption](native-wiki-adoption.md)); the column meanings matter, not the
headings.
