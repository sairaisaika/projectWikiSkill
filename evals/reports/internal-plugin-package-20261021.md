# Internal plugin first slice, 2026-10-21

Scope: package construction and read-only payload/source inspection. The existing
skill and CLI are unchanged. This is a familiar maintainer's test, not blind use.

- Local Python unittest discovery: 74 cases, 73 passed, one existing symlink test
  skipped because Windows did not permit unprivileged symlink creation.
- Eight new packaging/doctor cases cover both host manifests, byte equality with
  the canonical skill, existing-output protection, source-tree output rejection,
  altered/extra payload, stale canonical skill, missing/unsafe/empty receipts and
  hidden source files. The hidden-file test is not a symlink runtime test.
- Actual generated candidate: 20 payload files; doctor reported package integrity
  and canonical skill equality, while all installation/use/semantic/runtime layers
  remained unverified.
- The same candidate was transferred privately to Linux. Its bundled doctor ran
  successfully. The installed official Claude CLI's `plugin validate` returned
  exit 0 and `Validation passed` for the generated Claude manifest.
- A separate bounded, read-only `--plugin-dir` smoke invocation completed. The
  actual initialization transcript lists this candidate as `project-wiki` version
  `0.1.0`, source `inline`. The assistant made a real `Skill` call naming
  `project-wiki:project-wiki`; its tool result was `Launching skill`, and the final
  result was non-error and identified the packaged skill directory. The response
  correctly distinguished structural enforcement from semantic/runtime review.
  This verifies one instructed component load, not permanent installation, native
  project routing, lifecycle compliance, independent adoption or efficiency.

No host configuration was changed, no hook installed or trusted, no MCP server
created and no package publicly released. There is no lifecycle/efficiency or
product-acceptance result yet. Package hashes are not signatures or trust proofs.

Remaining work is owned by the [plugin plan](../../docs/PLUGIN_PLAN.md). Native
wiki adapters and actual start/delegate/finish/recovery remain required. Do not
convert these static results into a claim that all agents now follow the wiki.
