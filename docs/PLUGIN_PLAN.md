# Internal collaboration plugin, v0.2.1 candidate

Status: packaging, doctor and a native JSON workflow implemented. Linux Claude
manifest validation and one instructed v0.1 skill invocation passed. The native
workflow has a real Syleli recovery trial in progress. Automatic lifecycle behavior
is not fully tested, and this is not publicly released. Codex CLI 0.160.0 installed v0.2.1
through a private local marketplace; its inventory and cached payload were checked.
Desktop fresh-session component discovery is still pending.
The skill and its Python helper remain the canonical method and tool sources.
Generated packages are projections, never another editable wiki.

## Intended result

A successor agent can locate a change, receive its boundaries, implement it and
return evidence to the same feature entry without reconstructing the preceding
conversation. Packaging alone does not establish this result.

Codex owns this plugin's implementation and independent project review. Engineering
workers own the feature-local wiki changes accompanying their implementation.
The coordinator reconciles shared files and verifies their return. This is not a
separate documentation worker writing every other agent's documentation.

## Architecture and ownership

```mermaid
flowchart LR
  S[Canonical skill and Python tools] --> B[Versioned package builder]
  B --> C[Codex adapter]
  B --> L[Claude Code adapter]
  S --> F[Standalone CLI fallback]
  W[Project native wiki and source] --> T[Task context and full file impacts]
  T --> A[Agent implementation]
  A --> R[Diff and evidence reconciliation]
  R --> W
  R --> H[Revision-bound handoff]
  D[Read-only doctor] --> C
  D --> L
```

The native project's metadata, rules and debt ledger remain authoritative within
their existing responsibilities. Source and runtime evidence can contradict prose.
No project data, credential or runtime log is copied into a published plugin.
MCP is optional transport over the same tools, not a prerequisite or another core.

## Delivery slices and exit evidence

| Slice | Inputs and producers | Consumer and result | Exit evidence | Current state |
|---|---|---|---|---|
| Package | canonical skill, versioned identity, explicit payload policy | Codex/Claude package with the same skill bytes | payload hashes, self-contained links, rejection of symlink/unsafe outputs, real host manifest validation | v0.1/v0.2 Linux validated; v0.2 packaged Skill and scoped workflow reads observed |
| Doctor | selected package and optional canonical source/transcript | component/version/source-closure and scoped CLI observations | tampered/missing/extra files detected; installation, trust and runtime remain unknown unless actually inspected | payload/skill/support-source inspection and real Claude transcript observation implemented; Codex inventory currently checked separately |
| Start/delegate | user task, source pair, planned files, native task route | bounded context packet: actors, fields, producers/consumers, failures, checks and allowed edits | existing native indexes reused; all file satellites retained; missing/dirty/mismatched peers reported | real capture/start/delegate and worker show/read observed |
| Finish/handoff | actual diff, observed checks, selected source pair | updates or justified no-update result at the original entry; exact revision and remaining work | omission mutants and real successor recovery; no inference from delivered packet to read/used | real 16-file return reconciled; two omitted-review counterexamples rejected; viewport runtime gap retained |
| Host lifecycle | actual supported events and reviewed hook definitions | scoped entry/recovery prompts | current Codex and Linux Claude runtime receipts; unsupported host gets explicit CLI fallback | pending |
| Project pilot | independent theme and scratch-composer engineering tasks | project repair and reusable rule improvement | real worker output/source review, missed capability and wrong schema assumptions retained as negatives | in progress, no efficiency result |

## Evidence layers

Report these independently: package validation; installation/enabling; hook trust
and execution; context delivery; actual agent use and semantic correctness; product
runtime acceptance. None implies the next. Do not create an always-loaded roster of
commands or require full-wiki reading on every turn. A receipt is not a reading test.

First counterexamples: an old installed skill copy may diverge from its repository;
a task packet may never be used; a shared HTTP endpoint may have a separate reduced
editor; a named migration constraint may exist with a different definition. The
plugin must help expose these distinctions rather than give them passing stamps.

## Host references inspected

- [OpenAI packaging](https://developers.openai.com/plugins/build/plugins): portable
  root manifest and conventional skills directory; compatibility manifest supported.
  Manually installed desktop hooks require separate review/trust; not automatic.
- [Claude manifest](https://code.claude.com/docs/en/plugins-reference): custom skill
  paths supported, validator is authoritative. Host adapters must not silently rely
  on unsupported fields or claim equivalent hook availability.

## Verification still required

- Actual package build and eight adversarial packaging/doctor cases passed locally;
  see [bounded receipt](../evals/reports/internal-plugin-package-20261021.md).
- Linux Claude manifest validation and one real packaged-skill invocation passed;
  v0.2 also loaded its packaged Skill and read the native index/selected records.
  Complete automatic host lifecycle behavior remains unverified.
- Codex desktop fresh-session component discovery and current hook trust behavior.
  Official CLI installation/inventory and cached source identity passed separately.
- Full start/delegate/finish/recovery cycle, runtime source closure and task latency.
- Fresh agent comparison; the current coordinator's familiar self-review is not a
  blind trial, independent adoption or proof of speedup.

## Local candidate commands

```text
python scripts/package_plugin.py --output <new-directory-outside-this-checkout>
python scripts/plugin_doctor.py --package <built-directory> --source <canonical-checkout>
python project-wiki/scripts/workflow.py --help
```

The build does not modify host configuration or overwrite an existing output.
Interrupted builds have no complete receipt and fail inspection. Hash receipts
detect accidental drift, not package authorship or an attacker replacing both the
payload and its receipt. Versioned distribution and trusted origin remain separate.
Doctor does not execute hook scripts, scan project secrets or claim host installation.
It is also distributed in the built package. The native JSON task-card bridge now
has capture/start/show/delegate/finish commands and explicit peer selection; see
[workflow instructions](../project-wiki/references/collaboration-workflow.md).
Its isolated scenarios are mechanism tests, not a host lifecycle or independent
adoption result. The real recovery trial and host lifecycle hooks remain
required; a valid archive alone does not satisfy this plan's exit criteria.

The native Syleli trial retains 16 planned files, 14 satellite references, one
omitted candidate and explicit Web/App revisions. The worker invoked `show` and
read the host-persisted full output after its 2 KiB preview was clipped. This exposed
an ergonomics failure: complete transport does not guarantee convenient reading.
The CLI now defaults to an explicit index and offers exact feature/file expansion;
all records remain available. This is a guided same-worker recovery, not measured
speedup or blind adoption. The actual return now reconciles structurally and keeps
viewport acceptance as a gap; it does not certify the worker's semantic claims.
See the [workflow receipt](../evals/reports/native-workflow-20261021.md).
