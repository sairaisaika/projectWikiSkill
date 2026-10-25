# Browser request ownership and controlled evidence, C165

This is an anonymous, familiar-coordinator browser fixture. It tests how acceptance
evidence can become invalid when the request owner changes. It is not a new plugin
feature, an independent agent trial, or a product incident report.

## Question and existing design

The existing [systematic review](../../project-wiki/references/systematic-design-review.md)
separates design fitness, caller adoption and runtime evidence, and requires the
relevant client/environment boundaries. A shared component or passing isolated
test does not establish that a whole browser journey uses the same transport.

The missing step in this case was applying that existing distinction to the
acceptance harness: does the intended request control still reach the request
after a service worker becomes the client? No additional configuration authority,
Wiki format or global application abstraction was needed.

## Reproducible observations

The [standalone fixture](../fixtures/browser-request-ownership.mjs) serves only
synthetic HTML, a pass-through worker, one JSON endpoint and one JavaScript asset
from an ephemeral loopback server. It uses fresh browser contexts, no accounts,
and no project data. The worker remains enabled in every browser case.

| Case | Observed result | What it establishes |
|---|---|---|
| Exact endpoint, page-scoped route | Before worker control the value is `controlled`; afterward it is the actual `server` value, with no page error | Correct URL matching alone does not prove interception at the actual request owner |
| Context-scoped broad glob | The matcher sees both `/api/status` and worker-fetched `/assets/api/status.js`; the asset rejects JSON parsing | Widening interception scope can also widen the matched resource set; a substring is not a semantic endpoint identity |
| Context-scoped exact pathname | Both values are `controlled`; observations include a worker-owned request and only the intended endpoint, with no page error | This selected control reaches the intended synthetic endpoint through the actual worker on the observed browser |

The broad-match case catches and records the parse rejection, then returns the
original response. This preserves the negative observation without leaving an
unhandled harness exception. It does not make the broad matcher correct.

The final candidate ran all three cases successfully on Windows with Node
24.19.0, Playwright 1.62.1 and Chromium 156.0.8078.47. Success here means that the
two counterexamples and one positive control were observed; it does not mean that
the two incorrect strategies passed their intended application contract. These
observations have not been repeated on other browser engines or operating systems.

An earlier setup attempt found no executable at Playwright's default browser
location. No browser cases ran in that attempt. Selecting an already installed
Chromium executable in a new ephemeral context resolved setup; no browser download
or existing user profile was used. The final fixture records startup failures and
closes its server/browser in `finally`.
An explicit missing-executable control against that final fixture exited with a
recorded startup failure and zero browser cases, rather than reporting acceptance.

## Re-run without changing the Python toolchain

Use an existing Node installation and a separately available Playwright module:

```sh
node evals/fixtures/browser-request-ownership.mjs --playwright /absolute/path/to/playwright --out /new/output/directory
```

If its default browser executable is absent, supply `--executable` followed by the
path of an existing compatible Chromium executable. The output directory must not
exist. The script writes its observed result or failure there. This optional
browser evaluation is not part of the dependency-free Python unit/fixture CI; a
green Python matrix does not claim that these browser cases ran.

## Review consequences and limits

- Include the actual request owner and transport state when controlled browser
  evidence is material to a feature. Check that the controlled field reaches the
  UI before treating later actions as evidence about it.
- Match the intended endpoint structurally and verify its actual response
  contract. Do not parse every similarly named resource as the same type.
- Preserve the initial failure and separate setup, harness-control, component,
  full-client and backend outcomes. Disabling a worker can change the scenario;
  filtering resulting page errors would not establish normal-client acceptance.
- Bind a successful acceptance result to its source, artifact, actor and viewport
  scope. Do not infer persistent backend writes or broad PWA/offline behavior from
  controlled responses, screenshots, or this fixture.

No helper, packaged reference, manifest, version, hook, installation, trust or
permission boundary changes in this return. It adds a reproducible evaluation of
evidence construction. It provides no measured token/time savings, automatic
reader adoption, semantic certification, production acceptance or full-framework
completion claim.
