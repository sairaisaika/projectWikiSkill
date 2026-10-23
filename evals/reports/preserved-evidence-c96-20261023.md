# Selected evidence observations — candidate0.2.8

This is a bounded, familiar coordinator exercise. It is neither a blind agent
trial nor evidence that all project work, hosts, hooks or business flows passed.
The candidate source is separate from the installed0.2.7 host and scoped0.2.4
worker. Private paths, project revisions, accounts and original raw files are
not published in this report.

## Observed gap

A real coordinator reused a probe with a different selected source but missed an
output path derived from the probe's own directory. A private historical result
was overwritten while Git showed no repository changes. The earlier command
capture contained its original stdout; exact saved bytes matching the prior hash
were recovered, while the mistaken new run and recovery record were retained.
This was an output-path mistake, not proof of a product incident or lost chat.

An original-helper synthetic characterization at source `b469455` reproduced the
scope gap: a private file outside Git changed from a failing result to a passing
result, `actual_files` remained empty and structural reconciliation succeeded.
The helper still retained a capability gap and did **not** certify business
completion. Private files outside its declared inputs simply were not observed.

## Candidate behavior

`capture --preserve-artifact <absolute-existing-real-file>` explicitly selects
files to hash. Capture checks before/after the native command, start/delegation
check current bytes, every view retains the selection, and both review preparation
and final reconciliation require the original selection and hashes. Omitting or
replacing the final selection is refused, as is an observed mutation even when
Git has no differences. Unselected legacy tasks remain `not_requested`.

This records observations only. It does not prevent writes, continuously monitor
files, authenticate their original provenance, enforce a sandbox or prove physical
reading, semantic correctness or business success. Changes restored between
observations are undetected. A verified saved preimage may match honestly after
restoration. Inspecting every embedded output path and giving each new raw run
a distinct destination remains required practice.

## Actual local checks

Canonical implementation checkpoint: `b2200cd`. The new workflow helper bytes
were copied to Linux and independently matched SHA256
`b512193b590950637325df84f85686595df15de996c95cab9220f210e0b825d4`.

Windows Python3.13 ran:

```text
python -m unittest discover -s tests -p test_workflow.py -k PreservedEvidenceTests -v
python -m unittest discover -s tests -v
python scripts/package_plugin.py --output <new-private-package>
python scripts/plugin_doctor.py --package <same-package> --source <candidate>
```

- Focused:13 run,12 passed,1 skipped because this host could not create symlinks.
- Full:167 run,165 passed,2 skipped. Both skips were explicit host symlink
  capabilities: the existing Wiki escape check and the new evidence-alias check.
- Package:22 payload files, source identity0.2.8, exit0.
- Doctor:exit0 for the selected package/source. No host installation was performed.

The initial new-interface checks failed on the old helper because the option/API
was absent; those are not separately demonstrated production defects. The
original synthetic overwrite characterization above establishes the actual gap.
Cross-platform source CI and independent candidate review were still pending at
this checkpoint; the local skips are not silently counted as passed coverage.

## Actual paired-project CLI replay

The candidate helper ran against explicit fixed project/peer source snapshots
through the project's existing native router. Its selected-source comparison was
`matched`; this is metadata consistency, not proof of physical reading or a
correct deployment pair. No source files were edited in those fixed snapshots.

The exercise selected one actual retained historical result and one clearly
synthetic private control file. The original file's prior hash was checked before
and after. Only the synthetic copy was intentionally changed:

| Observation | Actual result |
|---|---|
| Original capture/start/delegate/index/feature/impact calls | Succeeded; selection retained |
| Changed synthetic copy, otherwise empty Git diff | New delegation refused, exit1, no success output |
| Fresh capture of that changed copy, same path selection | Review preparation and finish both refused, exit1, no success output |
| Explicit restoration of the synthetic copy's saved bytes | Final observation accepted as `unchanged_at_finish` |
| Real historical result | Original hash unchanged; original failing result retained |
| Read-only return | Structural reconciliation true, `actual_files=[]`, capability gap retained |

The controlled restoration deliberately illustrates the boundary: equality at
finish is not a claim that every intermediate byte was continuously unchanged.
The return did not invent product completion or reachable repository references
for an external helper. Original source implementation/runtime work remains
separate from this mechanism replay.

## Remaining layers

The first pushed source CI failed in hosted Windows Python3.13: the new fixture
passed its unresolved temporary path to a policy that requires a real path.
Eight tests errored at that check and one CLI test failed; Linux jobs passed and
Windows3.10 was cancelled by matrix fail-fast. The fixture now explicitly selects
its resolved real temporary path. The alias rejection in the product helper is
unchanged. Final cross-platform CI remains required; the earlier red run is kept.

An independent, framework-familiar reviewer inspected the original candidate
helper and its lifecycle callers, then executed the actual pure artifact helpers:
17 checks passed and two real symlink probes were skipped for Windows privilege
limitations. The reviewer did not run Git-dependent lifecycle routes. Their first
probe failed in its own result summarizer; that traceback and the corrected run
in a new output directory were retained. The coordinator read the raw result and
verified all 22 declared source/generated-file hashes and the clean fixed source
checkouts. No additional supported source blocker was found within that scope;
this is not a blind trial or a substitute for the Linux lifecycle replay above.

Normal exact source/main CI and any deliberate host adoption remain separate.
Explicit candidate CLI use on Linux does not upgrade a scoped
plugin, prove automatic hooks, prove another agent applied the context correctly
or establish comparative efficiency. No private project data was transferred into
the public report, and no project-specific repository label or path is built into
the helper.
