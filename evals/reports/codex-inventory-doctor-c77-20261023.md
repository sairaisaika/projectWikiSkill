# Read-only Codex inventory observations and bounded0.2.6 host adoption

## Observed gap and change

Actual0.2.5 package inspection and a separate official Codex inventory could not
be represented in a single doctor result. The package/source check correctly
left host installation unverified; it had no argument to inspect the real
inventory. The new optional inputs carry a marketplace-specific installation
observation and separately captured host version, without executing host commands
or conflating the result with source, hooks or agent adoption.

The caller still performs the official CLI capture and chooses private input
files. No repository, account, credential, source path, scoped execution log or
clinical data is embedded in this public report.

## Actual bounded host check

On one Windows host, actual official marketplace-scoped JSON and version stdout
were saved with process exit codes and SHA256 receipts. The new inspector read
the same snapshots against two selected packages:

| Selected package | Package/source integrity | Inventory observation | Version match |
|---|---|---|---|
| Existing installed0.2.5 | Passed |0.2.5 installed/enabled | true |
| Newly built0.2.6 candidate | Passed | Still0.2.5 installed/enabled | false |

Host version stdout reported `codex-cli 0.160.0`; it is a separate CLI observation,
not an assertion about the desktop app build. Candidate build did not install or
upgrade anything. The existing scoped worker stayed unchanged. The real version
disagreement demonstrates why a valid candidate package is not an installed
candidate. Top-level trust/use/semantic/business layers stayed unverified.

## Checks and failures retained

- Before implementation,8 new cases errored because the inventory entry point was
  absent (17 errors including subtests). This demonstrates missing capability,
  not8 independently proven product defects.
- After implementation,11 tests passed: exact marketplace identity, stale version,
  other-marketplace exclusion, available/model-claim exclusion, disabled state,
  duplicate ambiguity, malformed/oversized input, strict booleans/identity,
  bounded version stdout, real CLI integration and corrupt-package refusal.
- The first full suite ran142 tests with one Markdown-anchor failure and one
  existing platform skip. README used the wrong anchor spelling; correcting the
  link preserved the original verifier. No assertion or gate was weakened.
- Corrected full-suite run:142 tests, exit0, one existing platform skip. After
  adding the discoverable Skill→workflow host-observation route, the6 package/link
  checks passed again. Exact final-head remote CI is still required; these local
  runs do not establish source adoption or distribution.

## Evidence boundary and remaining work

The input snapshots are caller-supplied and unsigned. Freshness, origin and
completeness are not authenticated. A matching version cannot bind the host's
cached bytes; the existing package/source inspector is still necessary. An
omitted record means only not listed in this snapshot. A positive installed or
enabled flag does not prove hook trust/execution, context delivery, actual agent
use, semantic correctness, product acceptance, efficiency or complete
cross-host collaboration. Host update and actual native-task use remain separate
checks after normal source adoption; no running scoped execution is upgraded.

## Host adoption after source merge

The preceding table preserves the pre-adoption observation. Afterwards:

- PR18 source `fe6d8d11b87d0548c3d59366015542d310cfc4d8` normally merged to
  main `8c24a8a9ed77eb20c32a9aac965b1cac834f60f3`; their trees match. Both exact
  source workflow runs39935263430/39935310648 and exact main39935649839 passed
  Ubuntu/Windows Python3.10/3.13 checks. The clean canonical checkout fast-forwarded.
- The immutable package was rebuilt from that clean main; its existing official
  marketplace entry was updated after backing up the catalog. Official CLI
  installation and subsequent inventory reported0.2.6 installed/enabled.
- Actual cached package, canonical skill/support/identity and explicit inventory
  version match passed independently. The newly installed doctor was invoked
  directly, and its installed Skill entry route was read. These are bounded
  tool/source consumption observations, not automatic discovery or a fresh model
  session adopting its task context.
- Before the official update removed the prior0.2.5 cache, all23 package/receipt
  files were copied and hash-checked in a private recovery directory. The archive
  stayed identical afterwards. The older immutable distribution remains available;
  do not claim the old cache path still exists or unchanged-in-place.
- The scoped Linux worker was not upgraded/restarted. Desktop current-chat
  refresh, hook trust/execution, full cross-host implementation/recovery,
  semantic accuracy, efficiency and business acceptance remain unestablished.

This return changes documentation only. It does not change packaged payload,
version, hook/controller code, installation state or the archived raw evidence.
