# Fresh Codex CLI component discovery, 2026-10-21 local time

Scope: one instructed, read-only fresh CLI session using the already installed
private `project-wiki@project-wiki-internal` v0.2.1 package. This is a synthetic
fixture query, not Syleli feature implementation, desktop GUI validation, hooks,
independent workflow adoption or an efficiency comparison.

## Inputs and observed actions

The prompt named the installed plugin and `$project-wiki`, without giving its
cache path. It required the worker to stop if that skill was absent rather than
substitute the older `multi-agent-wiki` copy. The fixture root and query were
explicit. Codex CLI 0.160.0 ran with a read-only sandbox and ephemeral session;
neither hook trust nor configuration was bypassed.

The actual `item.completed` command-execution events record:

1. A successful `Get-Content` of `skills/project-wiki/SKILL.md` under the installed
   versioned plugin cache. Its returned bytes include the canonical skill name and
   instructions.
2. A successful invocation of that same package's `scripts/wiki.py query`, using
   `evals/fixture-project` and `external source`. Exit code 0; the returned route is
   `external-source`, with `ExternalSource`, `providerCapabilities` and
   `nodeFeatures` source locations and the interface wiki anchor.
3. A terminal non-error result that preserves the fixture's optional-count rule
   and explicitly leaves runtime/Syleli adoption/hook execution unverified.

This establishes discovery and recorded component/tool use in a fresh Codex CLI
session. It is stronger than an inventory-only installation result, but does not
establish that every instruction was understood or that a desktop GUI conversation
has refreshed. The root independently inspected command/result events; the final
model statement alone is not the receipt. Raw session output stays private.

## Environment limits

The CLI also attempted startup of preconfigured, unrelated local MCP clients;
some handshakes failed. No such service was requested by the worker, and no
configuration was changed. Therefore this report does not claim the entire host
made zero network attempts or that ambient MCP readiness passed. The scoped skill
read and query still returned successfully. No source/config writes, installation,
Git mutation or publication was part of the worker task.

## Next evidence

Keep this result separate from the Linux Claude native-task recovery. A real
cross-host successor task, current desktop component discovery, reviewed lifecycle
hooks and measured omitted-work/recovery cost remain open in the plugin plan.

## Project feedback retained alongside this trial

The theme integration's exact CI later rejected one stale generated satellite
block: a final manual documentation repair added a backlink after generation.
The preceding local green run did not cover that final file graph. Rerunning the
native generator changed precisely that backlink; the full new-head CI remains
required. This supports reconciling the final diff and final generated projections,
not creating a global full-wiki read rule or trusting a previous green receipt.
