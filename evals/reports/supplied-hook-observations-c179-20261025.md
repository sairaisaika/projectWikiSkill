# Supplied hook observations: bounded doctor follow-through

A coordinator had valid installed-package and inventory reports plus a separate
official host hook listing. The host listed this plugin's SessionStart as trusted,
but the doctor had no input for that listing. Its old CLI rejected the proposed
hook options before inspecting anything. This was a missing evidence consumer;
it did not establish a broken hook, missing installation or failed trust review.

The candidate adds optional saved `hooks/list` JSON plus explicit working-directory
selection to the existing doctor. Valid package integrity, declared hook support,
an exact plugin/marketplace identity and a matching installed version are required.
Only the chosen cwd's command SessionStart is considered. Its source path must
lexically match the selected package. Captured paths and commands are not used as
I/O or execution targets. Reads have a fixed byte budget. Duplicate, malformed,
partial-error, mismatched-version/source/cwd and missing records remain distinct
from positive observations; disabled/untrusted/modified values are retained.

The report carries the supplied snapshot digest and opaque host definition hash.
Neither authenticates the snapshot's time, freshness or completeness. Lexical path
association does not bind cache bytes or attest the command. Host-reported trust
does not grant trust, run a hook, deliver context or establish agent use. Existing
top-level evidence fields and package-validity exit semantics remain unchanged.

Twelve focused cases passed after an initial test fixture used the wrong existing
builder keyword. That error occurred in the harness before package creation;
the fixture was corrected to the actual builder interface. The whole local suite
ran 234 cases with two host symlink skips; the original twelve fixture checks and
24-task curated navigation evaluation also passed. These are self-tests, not an
independent agent trial or proof of measured time savings.

The first remote Windows matrix rejected the fixture's source path while both
Linux matrices passed. The fixture constructed its received path from the raw
temporary-directory spelling but the selected package was resolved. The fixture
now uses its canonical temporary root, and an additional control explicitly
refuses to guess short-name or symlink aliases from received path strings.
The parser's source association remains lexical and unchanged. The original
remote failure is retained; corrected final cross-host CI needs a new exact run.

The candidate doctor also read a previously captured real Codex0.160 listing,
matching installation inventory and a valid installed0.2.14 package. It reported
the selected SessionStart's enabled/trusted state while leaving all higher layers
unverified. All selected input hashes were unchanged. The source candidate is
0.2.17, so this replay is explicitly not installation or automatic execution of
0.2.17. A separately built candidate hook package passed source, support, raw-input
and payload closure checks. No host was updated, no trust was changed and no
project-native router, worker or product runtime was modified by this change.

Normal source/main CI, a later host update and actual automatic delivery require
separate evidence. The real raw host snapshots remain private; this report contains
no account, private project path, session, command log or application data.
