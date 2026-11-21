# Release gate and offline check — 2026-11-21

Scope: current public `sairaisaika/projectWikiSkill`, repository ID `1466210381`,
fresh isolated branch based on `68f6a6c188e7eca3287543b8d0af0e7f987f5b87`.
Only open PR at initial discovery was the separate maintainer-Wiki PR; untouched.
The new repository's release inventory was empty. No prior archived checkout or
repository objects were used. This candidate is infrastructure only; canonical
payload/version `0.2.39` and the marketplace version are unchanged.

The [canonical maintainer section](../../docs/wiki/architecture.md#release-gate-and-offline-comparison)
owns behavior, trust assumptions, statuses and recovery boundaries.

## Executed evidence

- Thirteen initial offline regressions passed: real temporary Git snapshots for
  maintainer-Wiki/test-only changes, canonical input change and synchronized version
  requirement; numeric semver; no bootstrap/backfill; live-metadata guard negatives;
  disabled/dry-run, complete duplicate, dangling tag/draft and failed upload cases.
- All API writes in those tests were in-memory synthetic operations. The positive
  path creates a synthetic draft/assets and publishes only into the fake adapter;
  a repeated event performs no new write. No GitHub release/tag API was called.
- Builder/doctor produce identical repeated local bundles; no hooks. Corruption,
  missing archive/coverage, wrong trust pin and invalid target never report same.
  Same-version/different-byte target reports different. Candidate Python containing
  an unconditional exception is only hashed, never executed. Explicit file
  snapshots show check leaves bytes/mtime/inventory unchanged; no candidate cache.
- Local full suite: 516 tests passed (one existing platform skip); 19 fixture tests
  passed. Fixture Wiki check/evaluation (28 curated tasks and one task-map case),
  maintainer Wiki check and all five package/source flags for default, legacy and
  portable profiles passed. The draft PR records exact-head CI separately.
- A final hardening pass retained explicit unknown publication state after failed
  write responses and made fixture versions independent of future canonical bumps.

## Review corrections and first CI failure

The initial PR head `bc8acd58c23b19d8a3dcd11c984a6ea9d038b2de` passed both Linux
cells but failed macOS 3.13: the new archive snapshot compared a resolved member
to an unresolved temporary root. Other pending matrix jobs were cancelled by
matrix fail-fast. This is a candidate defect, not the unrelated Git maintenance
lock race; no unrelated test fix was included. [Initial run](https://github.com/sairaisaika/projectWikiSkill/actions/runs/44881999893).

Independent review also found that script-only disabling still provisioned a
write-capable job and that ignored working-directory files could contaminate an
"exact commit" bundle. The correction moves default-off into the job condition,
uses exact tracked Git blobs for both descriptor and bundle (no archive-attribute
filtering), and compares them before writing. Recheck the release inventory and
formal baseline before first write and publication; verify successful publication
by readback. Concurrency with administrators is not an atomic transaction or an
Immutable Releases setting. Nineteen focused regressions now pass locally,
including export-ignore, ignored checkout input, mismatched descriptors, external
baseline changes at both boundaries and failed publication readback.

The explicitly requested standalone target reuses canonical skill inventory and
byte policy. Two synthetic standalone copies distinguish matching versus changed
files, CRLF normalization, exact coverage, cache exclusions and alias refusal;
no real client is contacted. The revised local full suite passes 522 tests (one existing platform skip),
19 fixture tests, both Wiki checks/evaluation and all three package doctors.
The final exact-head PR holds CI and transfer hashes.

## Linux handoff

Use a reviewed exact candidate checkout and an approved fresh scratch directory:

```sh
python3 -B -m unittest discover -s tests -p test_release_sync.py -v
python3 -B scripts/release_plugin.py --bundle /approved/scratch/new-bundle
python3 -B scripts/pws-sync --check --target /approved/scratch/new-bundle/package \
  --candidate /approved/scratch/new-bundle --trusted-receipt-sha256 REVIEWED_DIGEST
python3 -B scripts/pws-sync --check --target /approved/scratch/absent-package \
  --candidate /approved/scratch/new-bundle/release-receipt.json \
  --trusted-receipt-sha256 REVIEWED_DIGEST
```

First comparison should report `same` / exit 0; absent target reports
`not_installed` / exit 1. For this local experiment, trust the digest only after
reviewing the source checkout and bundle provenance; computing a hash does not
by itself authenticate a downloaded release. Transfer `package.zip`,
`release-receipt.json` and the candidate source's trusted checker/doctor together
through an approved channel. The checkout tools are not installed into a host.
For two **explicitly supplied** standalone installation paths, run separately:

```sh
python3 -B scripts/pws-sync --check --target-kind standalone-skill \
  --target "$SKILL_ONE" --candidate /approved/scratch/new-bundle/release-receipt.json \
  --trusted-receipt-sha256 REVIEWED_DIGEST
python3 -B scripts/pws-sync --check --target-kind standalone-skill \
  --target "$SKILL_TWO" --candidate /approved/scratch/new-bundle/release-receipt.json \
  --trusted-receipt-sha256 REVIEWED_DIGEST
```

The operator supplies both path variables; the CLI does not discover them. The
receipt/hash must be independently authenticated as above. `same` establishes
file equality only, while `different` is a comparison result, not an update.

The source commit and receipt/archive SHA256 make the candidate independently
checkable; no output in this report refers to a live client or loaded session.

## Unrun and limits

No bootstrap, release/tag creation, real upload, secrets, client edits, installs,
automatic updates, settings or hooks were performed. Publication remains disabled.
The first real release requires separate authorization/bootstrap and a reviewed
workflow enable change; no production success is inferred from synthetic APIs.
Server enforcement, real upload failure recovery, concurrent administrator races,
host discovery, real standalone installations, and active-session loading are unverified.
GitHub's API/job/asset formats and minimum token permission assumptions need the
first separately authorized integration observation. The workflow is not a claim
of branch protection. No generic updater or network-enabled checker was added.
