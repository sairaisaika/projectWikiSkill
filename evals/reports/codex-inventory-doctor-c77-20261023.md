# Read-only Codex inventory observations, 0.2.6 candidate

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
