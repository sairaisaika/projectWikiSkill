# Installed-version drift and fresh-host discovery, 2026-10-22

Scope: internal 0.2.3 payload at source revision `9f2a504`, one local Codex
installation update and one instructed fresh read-only CLI session. This is not
desktop GUI discovery, automatic hooks, a native start/finish cycle, a blind
efficiency comparison or product acceptance. Raw host files/transcripts stay private.

## Negative observation and actual update

Canonical source and a separately selected Linux package were 0.2.3, but the
installed Codex cache and its configured local marketplace still selected 0.2.2.
Old-package integrity passed; source comparison separately rejected the workflow
implementation/reference, identity and version match. It was a valid old package,
not a corrupt new one. Repository adoption and another host's package did not
prove this host was current. The existing doctor detected this without a second
version registry or payload change.

The existing builder produced a new self-contained 22-file package from clean
source. Source, bundled support and identity matched. The one existing private
marketplace entry was advanced to it, retaining the old entry privately. The
official CLI's `codex plugin add project-wiki@project-wiki-internal --json`
returned 0.2.3 and its installed path. Marketplace-scoped JSON inventory reported
installed/enabled 0.2.3. Independently inspecting the resulting cache matched
canonical skill bytes, support files and identity.

Only selected package/catalog/install state changed. No hooks were enabled or
trusted, MCP registered, model changed or product deployed. Doctor still labels
installation unverified by itself: official inventory is separate evidence.
Current [official packaging guidance](https://developers.openai.com/plugins/build/plugins)
also distinguishes installed cache from source and calls for app restart and a
new chat. This test used the installed CLI's supported commands; it does not prove
the running desktop conversation refreshed or has identical update behavior.

## Fresh-session observation

A fresh Codex CLI 0.160.0 ephemeral session used its real read-only sandbox. Its
task named the plugin/Skill without a cache path and required stopping if absent
or older. No sandbox or hook-trust bypass was used. Root inspected completed
command/result events, rather than accepting only the model's final statement:

- It read the discovered installed `skills/project-wiki/SKILL.md` and package
  compatibility manifest containing version 0.2.3.
- Its bundled `wiki.py query` for `external source` returned exit 0, identifying
  declaration/implementation/consumer at fixture `provider.ts` lines 2/7/11 and
  the interface wiki anchor. It also read that cited source, preserving suggestions
  when optional counts are absent rather than interpreting absence as zero.
- Its bundled `workflow.py start --help` returned exit 0 and exposed explicit
  read-only scope with optional edit paths. Help is **not** a successful read-only
  start/delegate/finish trial.
- The turn completed. No source/config/Git write or network-tool use appeared in
  its command events. Unrelated preconfigured MCP clients attempted startup and
  some handshakes failed; zero ambient network activity and host-wide health are
  not established.

The existing source suite ran 108 cases: 107 passed and one existing Windows
symlink-privilege case skipped. No mechanism or payload changed for this report;
final documentation and remote CI require separate exact-revision checks.

## Unequal evidence in live Linux tasks

The existing doctor inspected scoped Claude transcripts against the selected
0.2.3 package. A creative task has matching init and a successful Skill launch.
An engineering task's retained pre-resume segment matches init but has no
observed completed Skill launch. Both have independent native wiki reads, which
are a different observation. Neither live segment proves completed engineering,
trusted hooks or product behavior. Later segments may add evidence.

Do not require ceremonial Skill calls merely to collect a stamp. Inspect actual
context, native-rule use and return/diff reconciliation. Saving new user steering
to a file also does not establish delivery into an active model conversation.
The coordinator remains task transport; the plugin does not restart models or
acquire publishing authority.

Desktop new-chat discovery, trusted lifecycle hooks, full real-project successor
recovery and measured efficiency remain open. Keep them separate from this
bounded CLI/cache result.
