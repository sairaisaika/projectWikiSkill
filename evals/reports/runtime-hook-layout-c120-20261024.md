# Runtime hook format boundary and compatibility container

## What changed the next action

The 0.2.11 optional portable declaration passed all exact source/PR/main matrices
and was installed through the normal official entry on the observed Windows
host. Cache/source/identity closure matched, after backing up the prior cache.
Fresh read-only `hooks/list` responses in two workspace roots still contained no
target hooks and no entry errors. Installation was not promoted to discovery,
trust or execution. Earlier0.2.10 failures and uninstalled diagnostic variants
remain intact. No host trust files, bypass flags, model turns or active scoped
engineering workers were changed.

The coordinator then inspected the official upstream source tag matching the
reported CLI version 0.160.0. In the plugin loader, the selected AgentPlugin format
explicitly returns empty hook sources; only the legacy branch calls
`load_plugin_hooks`. The portable manifest parser does recognize the OpenAI
extension and its hook path, so another spelling/path change would not address
that loader branch. The binary contains the corresponding loader/manifest
identifiers, and its observed behavior is consistent with the branch. This is
not proof of the installed binary's exact source commit or build attestation.

Primary source locations:

- [Matching runtime tag: format-dependent hook loading](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/core-plugins/src/loader.rs#L952).
- [Matching runtime tag: portable extension/overlay parsing](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/core-plugins/src/agent_plugin_manifest.rs#L184).
- [Public plugin packaging guidance](https://developers.openai.com/plugins/build/plugins).

## Adaptation and evidence limits

The internal hook profile now emits only generated legacy host manifests at the
root, leaving the portable `plugin.json` out of that output. The source identity
is still a single canonical input, retained in the source-bound receipt. Doctor
validates that identity against both host manifests and the closed payload, and
rejects a mixed root layout or a new projection without schema2/hook opt-in.
This is an explicit `legacy-host-hooks-v1` container projection, not new business
configuration, a second Wiki, model policy or trust authority. The lifecycle
reader and hook definition bytes do not change.

Plain packages stay portable. The prior portable hook projection remains an
explicit option for hosts that support it; older identity/portable receipts stay
inspectable. The compatibility choice follows actual runtime capability rather
than claiming public documentation alone proves every local version supports
the same behavior.

Five focused legacy-container checks and four existing portable checks passed.
The full local suite ran 196 tests: 194 passed and two Windows symlink cases
were skipped. The engineering fixture suite ran 12 checks successfully; Wiki
structure/drift, navigation evaluation and diff validation also passed. Actual
plain, legacy-hook and explicit portable-hook packages passed payload/source
closure. The new doctor also accepted the real prior portable installation
against its matching source checkout. Another checkout had four raw line-ending
differences while normalized source equality still passed; the raw mismatch was
retained rather than presented as exact byte equality.

Full final CI, normal adoption, installed discovery, exact-definition trust,
actual triggering, delivered context, agent expansion/use and semantic/business
acceptance still require their own evidence. A compatibility manifest alone does
not establish any of those layers. No installed cache was patched to simulate
the new format.
