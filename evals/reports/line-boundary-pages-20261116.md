# Line-boundary text parts — 2026-11-16

## Concrete failure

After default capture impact text became compact line records, a real multi-owner impact record still split into two bounded parts whose first part ended in the middle of a page-owner title, although several complete earlier lines fitted. All content was retained and the printed continuation reassembled it exactly, but a reader holding only one part could not reliably interpret the last record. Readers that clip or skip parts themselves are a separate failure, not caused by the pager.

## Scope decision

`context_reading.text_page` is the single pager for every bounded text view (summary, locator, page/section, history, outline, packet and capture record text). The cut was chosen there by a byte/line binary search with no line awareness, so the defect is in the pager, not in capture record formatting. The change stays in that function: after the existing maximal prefix is found, the part ends after the last newline inside it when that prefix holds at least one complete nonempty line and the shorter part still fits. The cursor records that offset. Render format, headers, NEXT commands, digests, byte/line budgets, JSON exports and capture bytes are unchanged; no flag, gate or second pager was added.

## Red/green evidence

Four synthetic regressions (`LineBoundaryPageTests`, multibyte owner-like compact records, no consumer data) fail against unchanged source with 8 failures across six byte/line budgets plus the oversized-line and `--section` cases; the blank-prefix no-stall control passes before and after. With the change all pass. One existing CLI snapshot-only test assumed the second part was complete; it now follows each printed NEXT until COMPLETE, keeping its snapshot-only and path assertions.

A synthetic 11-owner impact-like text (2920 characters) at the CLI 4000-byte/40-line budget: unchanged source splits 1753+1167 and part 1 ends mid-title; the candidate splits 1720+1200 and part 1 ends after a complete record. Both reassemble exactly. This is one synthetic replay, not the original record.

## Platform fixture correction

The first PR matrix at6c331c4 reported one Windows3.10 failure in the700-byte subcase; its other Windows job was cancelled by fail-fast, while both Ubuntu jobs passed. The synthetic owner line, including unnecessary role/satellite fields, could not fit with the longer PowerShell continuation envelope, so the test incorrectly demanded a complete line where the documented oversized-line fallback applied.

The fixture now retains its multibyte page/title and the same budgets and assertions; oversized-line coverage remains separate. Root replays all four controls against old/new source under both POSIX and PowerShell command formatting: each old-source branch produces8failed subcases and each candidate branch passes all4tests. This exercises quoting branches locally, not a replacement for actual Windows CI. Source pager logic is unchanged by the fixture correction; the failed remote run is retained as evidence: [first PR matrix](https://github.com/sairaisaika/projectWikiSkill/actions/runs/43966344896).

## Root same-capture replay

Root independently replays one saved real Native impact record with11declared owners through the old and candidate scripts at the **same helper path**, with the same capture and 4000-byte/40-line CLI limits. Complete content is3859characters. Old parts contain2623+1236characters (4000+1621stdout bytes), with the first part ending mid-line; candidate parts contain2590+1269characters (3967+1654bytes), both ending on complete lines. Both still need two parts. Content reconstructs exactly, the4026-byte machine JSON is byte-identical, and the captured file hash is unchanged. The input remains private; only aggregate results are reported here.

This is one controlled real-input replay, not a new native capture or natural adoption; no cost saving is claimed.

## Limits

A single line that cannot fit with the required display metadata still continues mid-line at a character boundary, so records are not atomic. When the line budget binds, a part may carry one line fewer than before. Parts may be slightly more numerous for some texts. Whether readers follow continuations, read every part or understand records is not measured; no adoption, token or time saving is claimed. Installation and platform CI are separate.

## Installation and guided-use follow-up

After the corrected fixture, exact PR and merged-main matrices both pass in all four platform/Python jobs; links and source identity live in [version status](../../docs/wiki/status.md). The earlier failed Windows matrix remains above. No pager-source change was needed for that fixture correction.

Root verifies a quiet Linux static refresh against the merged canonical payload:21of21 tracked file hashes match, and the prior copy remains outside Skill discovery. Hooks, settings and the original development session are unchanged. This installation is manual; it does not add automatic updates.

A fresh genuine engineering task invokes installed38 preparation for known source files, reads the complete two-part summary and a two-part section outline before implementation. Relevant local Context and owner-page bodies are still only partially read, and some are read by bounded raw commands rather than the captured page reader. This is guided partial use, not complete pre-edit context coverage or independent R7. Root also still exceeds host output budgets when combining unrelated raw reads; that is a caller orchestration failure and does not establish a lost NEXT or dropped capture content. No general efficiency or semantic-adoption result is claimed.
