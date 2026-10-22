# Actual0.2.5 host update and bounded use, 2026-10-22

Scope: source main `3cac3ef`, one official Windows Codex CLI update, a fresh
read-only CLI source-maintenance review and fixture query, and a separately
scoped Linux Claude native-source review. These are separate evidence layers;
neither package/source checks nor a review establishes product/device acceptance.

## Official Windows update and observed cache replacement

Before the update, the existing private marketplace selected0.2.4. Root built
the22-file0.2.5 package from a clean checkout of the adopted source, verified its
canonical source/support/identity, retained the old catalog, and advanced that
same entry. The official `codex plugin add project-wiki@project-wiki-internal --json`
returned0.2.5 and its installed path. Marketplace-scoped inventory separately
reported installed/enabled0.2.5. Inspecting the resulting cache matched package
bytes, canonical source/support/identity and raw build input bytes.

The update removed the older0.2.4 **cache directory**. Root's initial wrapper
incorrectly asserted that the old cache would remain byte-identical; it failed
after installation and new-package inspection had already succeeded. Root
inspected the actual state without repeating installation or manually restoring
the cache. The separately retained0.2.4 source package still exists. A live Linux
engineer uses a different explicitly scoped0.2.4 package; that package and process
were not updated or restarted. Future tasks must resolve a fresh installed path
instead of assuming the old path survives an official host update.

Only this selected catalog/install changed. No hooks were enabled or trusted,
no MCP service registered, no model selected, no product deployed, and the active
desktop conversation was not restarted. Current
[official packaging guidance](https://developers.openai.com/plugins/build/plugins)
also treats desktop refresh/new-session behavior separately from source files.

## Fresh Codex CLI observation

One ephemeral session used the actual read-only sandbox and default configured
model. The task named the plugin/Skill without a cache path and required stopping
if missing or older. Root inspected six successful completed command events:

- Read the discovered installed Skill, relevant maintenance reference and both
  manifests identifying0.2.5.
- Ran the bundled `wiki.py query` exactly once for `external source` against the
  synthetic fixture. It returned the declaration/implementation/consumer at
  `provider.ts` lines2/7/11, and the agent read that actual source and wiki seam.
- Inspected the package builder and doctor in the real repository. Its actual
  doctor invocation confirmed the installed package/source closure while leaving
  installation, hooks and business acceptance unverified by doctor itself.
- Completed a bounded report that separated its observed byte/query use from
  uninspected official inventory, merge/CI history, lifecycle and business state.
  It correctly flagged stale current-status wording in the original plugin plan.

The source worktree remained clean after the session. The root's first event
reconciler counted a mere source-file read as a doctor invocation; restricting
the match to the actual invocation argument corrected this harness error without
rerunning the agent. Ambient startup attempted preconfigured local MCP clients
and several failed. There was no requested MCP/network tool use in the completed
commands; this is **not** a zero-network or whole-host-health result.

This is instructed use, not blind discovery efficiency. The fixture's wiki is
not an engineering wiki for this repository, and its result is not a real provider
or Syleli business test. The scoped source-maintenance review is a separate task
from the Linux native-project review below.

## Linux scoped use

The same canonical22-file0.2.5 payload passed Linux package inspection and the
installed Claude host's manifest validator. A fresh bounded review used the
explicitly scoped package and a native read-only task packet on the committed
Web documentation/mobile source pair. Doctor observed the matching plugin init,
a successful packaged Skill launch and a non-error result. After explicit input
EOF, root verified process termination. Plan permission mode is not a filesystem
sandbox. The ongoing engineer retained its independent0.2.4 package.

The reviewer read the packet's native views, seven original wiki pages and actual
source seams. It retained a capability gap: server-clock display/focus metadata
does not prove outbound booking intent, complete receiving-care access or device
behavior. It located device-derived rebook conversion and slot labels, ambiguous
notification actor/historical lookup, and client time gates still reading the
device clock. It also correctly distinguished this documentation/source pair
from the separate producer candidate; a commit's presence is not runtime delivery.
These findings require source-owner follow-up, not automatic product certification.

Root independently matched three planned source hashes,245 declared wiki/runtime
input hashes and both checkout heads before/after. All seven page decisions and
the original worker review were retained. Root first supplied the planned read
files as the final actual diff; the existing gate rejected that unchanged
read-only return. The documented rule requires an empty actual-file query when
there are no edits. Root corrected only the after-capture and reran finish with
the **unchanged** worker review. Structural reconciliation then passed with zero
actual files and the capability gap still open. The first refusal remains evidence
of correct enforcement and coordinator misuse, not a new helper bug or a reason
to relax the gate. The original review reasons were checked separately; an empty
actual diff alone does not validate their semantics.

## Remaining acceptance

Desktop GUI fresh-session discovery, actual reviewed/trusted lifecycle hooks,
independent comparative task cost/omissions, complete receiving-care and booking
flows, new APK/device acceptance and product behavior remain unverified. Earlier
source implementation-through-return receipts remain valid within their own
revisions; this package update does not expand their scope or complete the goal.
