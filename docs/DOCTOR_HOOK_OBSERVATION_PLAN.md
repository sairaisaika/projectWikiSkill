# Supplied Codex hook observations

The existing doctor verifies package bytes, optional canonical source, supplied
installation inventory and supplied host version separately. It cannot currently
describe a supplied `hooks/list` result. A real host can therefore list a trusted
SessionStart while the combined doctor still has no way to carry that observation.
This is a missing evidence consumer, not a missing hook engine or a trust defect.

The candidate adds one optional read-only adapter in `scripts/plugin_doctor.py`, alongside
the existing supplied inventory adapter. Require an explicit marketplace, matching
installed package version, selected working directory and valid package containing
the hook definition. Match only this plugin's command SessionStart and the selected
package's lexical `hooks/codex.json` source path. Do not resolve or open any path
received from the host snapshot. Windows and POSIX paths must be unambiguous local
absolute paths; reject UNC, traversal, relative paths and control characters.

The output retains the snapshot digest and reported enabled/trust state per chosen
working directory. Missing, duplicate, malformed, mismatched or stale-version
evidence cannot become a positive observation. Host definition hashes are opaque;
they are not package-file checksums. Supplied snapshots are unsigned and their
capture time/freshness is unverified. No command, credential, other plugin record
or unrelated working directory is copied into the report. Package validity and
existing doctor exit semantics remain separate from host observations.

Keep top-level installation, trust, execution, delivery, use, semantics and business
acceptance unverified. The nested observation describes what a supplied listing
reports, not execution or a new trust grant. No installer, hook definition,
host configuration, automatic retry, MCP service or project-native router changes.

Before implementation, retain the old CLI's rejection of the new option against
a synthetic fixture. Add adversarial tests for identity/cwd/source/version mismatch,
duplicates, booleans, malformed/oversized inputs, disabled/untrusted/modified states,
path safety and a matching report that still leaves higher layers unverified.
Run the whole original suite/fixture/navigation gates, package source-closure and
a bounded real supplied host replay. Source/main adoption, installation, trust,
actual hook execution and project business acceptance remain separate deliverables.

The [bounded implementation and replay report](../evals/reports/supplied-hook-observations-c179-20261025.md)
records observed tests and the installed-version/source-candidate distinction.
