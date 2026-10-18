# Pages that support a precise engineering plan

Use this guide when writing pages or reviewing a wiki reference. A screenshot can
demonstrate presentation and specificity; its visible endpoint names, timings and
architecture are not verified facts about the target repository.

## Navigation and reading order

For a large wiki, organize the contents by responsibility: system/layer → feature →
mechanism, such as UI integration → request routing → capability injection. Add
task aliases and cross-links for changes that span layers. Keep a short question-led
entry; the hierarchy is an alternate route, not a requirement to read every parent.
Avoid mirroring the folder tree or repeating the same architecture chapter under
different headings. Small projects can retain a flat task map.

Feature entrances follow the mandatory [feature completion contract](feature-completeness.md); mechanism leaves may link to their parent contract. This is the minimum content standard even when no automatic validator is installed.

A useful feature section provides:

1. Responsibility and current implementation status, with a brief component/file map.
2. The scenario's contract and a relevant diagram.
3. Local source references and explanation of branches, ownership and exceptions.
4. Downstream impacts, focused verification and unresolved behavior.

For dense connections, combine a local explanatory view with the existing full
inventory and, where available, endpoint/type filtering. Zoom makes labels readable;
filtering narrows the question. Neither replaces conditions, failure states and
source evidence. Preserve shared IDs, show the subset against the full counts and
provide a clear reset and route back to prose. Reuse an existing reader/model before
adding another graph index. Inspect the actual viewport and keyboard return path;
rendering and diagram counts alone do not establish usability.

## Keep chapter and diagram evidence distinct

Place a **diagram sources / 图表来源** block immediately beside each diagram, and
a **section sources / 章节来源** block beside the prose it supports. They can cite
the same source when appropriate, but a chapter's broad reference list does not
automatically substantiate every arrow. For a long diagram, map important messages
and branches to source IDs or symbols in a compact table.

Each reference should identify the repository/path, stable symbol or unique needle,
and what it supports. Resolve current line positions using the route helper rather
than preserving copied line numbers. Published code links should identify their
revision; label a link to a moving branch accordingly. Retain symbols as navigation
keys when line anchors move. Proposed interactions need proposed status and a
decision/plan reference rather than a fabricated implementation citation.

Example source block, with positions resolved at publication time:

| Claim | Source locator | Evidence role |
|---|---|---|
| Request dispatch | repository/path :: Router.handle | implementation |
| Optional capability | repository/path :: Provider | declaration only |
| Consumer fallback | repository/path :: Client.read | caller behavior |

The helper validates route/diagram references; it does **not** verify that these
human-authored blocks substantiate prose or every message. Review that separately.

## Interaction details that change an implementation plan

Use only the applicable rows; record missing facts as unknown rather than filling
them with conventional behavior.

| Interaction | Facts to locate and document |
|---|---|
| Request and response | Method/event, route or callable, relevant input fields, returned fields and units, returned errors versus thrown exceptions |
| Startup and health | Initialization order, version compatibility decision, readiness conditions; a health response alone does not prove the feature works |
| Polling or subscription | Owner, start/stop conditions, foreground/background policy, interval and units, cancellation/unsubscribe and resource release |
| Incremental updates | Cursor/sequence owner, advancement and reset rules, empty updates, duplicate/out-of-order handling; unknown handling stays unknown |
| Optional bridge or accelerator | Availability detection, which failure triggers fallback, which component owns it, output compatibility and propagated errors |
| Language/runtime boundary | In-process call, virtual-host interception, IPC, actual network or FFI; serializer/type authority and ownership across the boundary |
| Reserved integration | Existing declaration versus active caller/implementation; mark future hooks as reserved or proposed |

Show applicable `alt`, `loop`, callbacks and self-updates with meaningful conditions.
An unused lifeline does not prove a database read or dependency call. A virtual URL
does not prove a remote HTTP service; FFI does not imply a separate process. A
fallback arrow does not establish that fallback is behaviorally equivalent. Keep
these distinctions consistent with architecture and deployment views.

## Manual review record

For the selected pages, report raw counts and findings independently of structural
scores. Count only applicable items; explain exclusions. These are review metrics,
not new automatic guarantees from `wiki.py`:

- Navigation: representative questions reaching the relevant section / questions tried.
- Local provenance: diagrams with reviewed local source blocks / diagrams reviewed;
  sections with reviewed local source blocks / factual sections reviewed.
- Traceability: source-verified important interactions/branches / interactions sampled;
  list unsupported ones even when paths resolve.
- Interaction completeness: applicable table rows answered with evidence / applicable
  rows; list unknowns separately, not as completed rows.
- Planning usability: outcome, dependencies, interfaces, deliverables, exit evidence
  and unknowns, using the existing 0–6 plan rubric.

Record reviewer familiarity, inspected page IDs and source revision. Rendering,
reference resolution, semantic review and runtime observation remain separate.
