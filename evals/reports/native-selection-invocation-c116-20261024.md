# Native selection controls must be consumed, not merely printed

This is a 2026-10-24 coordinator self-audit in a coupled engineering project.
It records a usage failure and exercised recovery with existing0.2.9 behavior,
not a new helper defect, blind trial or host installation.

## Actual failure

The coordinator supplied an environment-variable name that the native task
router did not consume. The router exited successfully, while its reported peer
root identified the default older checkout. An earlier summary incorrectly said
the intended peer had been selected. The original packet was retained rather
than relabelled or rewritten.

The native parser and actual report were then inspected. Successful execution,
an entry stamp and visible provenance were insufficient: the coordinator had not
compared that provenance with the intended task pair.

## Existing guard, exercised on the real adapter

The installed Windows0.2.9 workflow helper's bytes matched repository source. An
identical private CLI copy ran on Linux; the active scoped Claude0.2.4 worker was
not upgraded. Native execution used the already available Node22 runtime and an
explicit installed loader. No dependencies were installed.

The coordinator selected an isolated clean review checkout and its declared peer,
then enabled the existing `--native-source-context` comparison:

| Observation | Actual result |
|---|---|
| Unrecognized native selection variable, declared intended peer | Capture exited1 with an identity mismatch; no capture file was created |
| Correct selection control from the native parser | Capture exited0 and reported matched selected roots and full revisions |
| Read-only task start and feature/impact expansion | Empty edit scope, native workflow, omitted candidates and comparison retained |
| Fresh final capture and reviewed return | Same revisions, no actual repository changes, no structural issues |
| Selected original failed-capture log | Hash unchanged at review preparation and finish |

The task index was expanded and the relevant original wiki sections and source
producer were read. This is a bounded consumption observation, not a trace of
every physical read. Private raw records retain command arguments, source
identities and the failed capture; this public report omits project identifiers,
checkout paths, sessions, accounts and raw logs.

## Operator correction and limits

Read the native adapter's actual selection controls before constructing its
invocation. When it reports checkout identities, compare them against the task's
selected root and peers before dispatch, and retain that policy at return.
Do not rewrite a report or substitute another checkout to obtain a match.
Legacy adapters without source observations keep their explicit limitations.

This correction uses the existing comparison documented in the
[collaboration workflow](../../project-wiki/references/collaboration-workflow.md#context-capture).
It does not change packaged instructions, helpers, manifests, hooks or versions,
and does not require reinstalling a host. Reported identity matching still does
not establish a correct deployment pair, semantic completeness or business
acceptance. No speedup, automatic lifecycle or independent agent-adoption result
was measured. Product findings from the same engineering review remain in that
project's original wiki and work records.
