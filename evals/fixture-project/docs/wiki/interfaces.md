# Fixture interface map

<a id="public-api"></a>
## Article service and legacy client

Declaration: `ports.py::ArticleSource.list_articles`. Implementation:
`service.py::get_articles`. Consumer: `client.py::read_articles`.

Inputs are the injected source and query; output is Result(data/error).
`None` from the source means unavailable; `[]` is successful empty data. The client
currently returns data/None and loses the precise error. A result-style client
could be added compatibly; it does not exist yet. Do not change old callers silently.
The service does not catch dependency exceptions: returned None maps to unavailable,
but a thrown exception propagates through both get_articles and the legacy client.
The fixture has no HTTP layer or authorization. Offline tests cover this mapping,
not a provider connection. Checks: `python -m unittest discover -s tests`.
For a diagnostic symptom, follow [the evidence exercise](interfaces.md#diagnostic-evidence).

<a id="external-source"></a>
## External provider capabilities

`provider.ts::ExternalSource` requires suggestTopics; counts is optional.
`providerCapabilities` reports available features, and `nodeFeatures` consumes it.
A provider without counts must still support suggestions. Null means unavailable,
not zero. This file is TypeScript shape logic only, not an external API adapter.
Thrown/rejected provider behavior is not specified by this shape. Unsupported counts
is a capability gap, not a zero result. No actual budget, retry or cancellation implementation exists. There is no TS test
runner in this fixture; a full provider contract test is an explicit gap.

<a id="tagger"></a>
## Model suggestions

Declaration: `tagging.py::Tagger.suggest`. `sanitize_suggestions` lowercases,
trims and deduplicates suggestions. It does not call resolve_tags or write a ledger.
None means failure, [] means no suggestions. Model exceptions propagate, and the
sanitizer assumes string elements; it does not validate arbitrary JSON suggestions.
An actual hosted model is not included.
Changing suggestion fields needs a caller contract; introducing confidence is a
proposal requiring schema and policy work, not just a new model string.

<a id="tag-rules"></a>
## Effective tags and conflicts

`resolve_tags` returns absent on no assertions. Highest numeric tier wins; a conflict
of add/remove at that tier is disputed. `effective_tag` counts only present.
Malformed assertions are not explicitly validated: missing keys may throw, and one
unknown operation maps to absent. The fixture does not implement timestamps, per-person latest stance, review requests,
authentication or persistence. A plan may propose those capabilities but must not
describe them as current features. Any conflict-policy change affects effective_tag
and the offline tests. No majority vote is currently implemented.

## Diagnostic evidence

A report says that one article operation returned empty data despite an unavailable
source; another says that acceptance proves completion. Start with the
[shipped debugging method](../../../../project-wiki/references/engineering-depth.md#debug-from-evidence-to-a-technical-contract)
and the [existing article contract](interfaces.md#public-api). This is a synthetic
offline exercise; there is no runtime logger, remote provider or deployment.

The sample label `article-result/v1` describes the current fixture contract only,
not a deployed protocol version. Exact authority is `src/ports.py::ArticleSource`,
producer `src/service.py::get_articles` and consumer `src/client.py::read_articles`;
source hashes in `tests/diagnostic_example.py` bind that label to their bytes.
The legacy consumer loses precise error information: its None result does not
establish a retryable cause. A dependency exception still propagates. A future
result-style client needs compatibility and rollout review before changing callers.

Use [the synthetic packets](diagnostic-samples.json) to join one operation by its
opaque synthetic ID. Events retain timestamp, service/build/environment, stable
operation/event/outcome/error codes, failure class, retry knowledge and a safe
categorical data state. No query, client payload or customer identity is captured.
Judge each packet from the contract rather than the reporter's claimed outcome.
Packet labels are identifiers, not expected answers.

| Evidence path | Scope and limit |
|---|---|
| Producer → sink/query | The test wrapper observes the actual offline service and client; the JSON packets are authored synthetic examples queried by operation/ID, not a configured production sink. |
| Authorized reader/runbook | Fixture maintainer follows this owner and runs `python -m unittest discover -s tests -p test_diagnostic_evidence.py -v` from the fixture root. |
| Coverage / retention / sampling | Packet metadata describes complete, sampled or unknown coverage of the sample only. Repository retention applies to these public examples; real log retention, sink delivery and access are unverified. No runtime collection is authorized. |
| Test owner and next check | `tests/test_diagnostic_evidence.py` compares the offline mapping and diagnostic controls. To assess a real incident, the project owner must first verify the actual build/contract and approved sink/query coverage, then supply authorized sanitized observations. |

For each packet report producer/consumer, the joined operation (if possible),
claimed versus observed outcome, contract consistency and next missing check.
Accepted/queued and absent/sampled terminal records need their own evidence;
a passing fixture check cannot establish that a production operation completed.
Keep raw evidence in an approved protected store and only safe pointers here,
following the existing Maintenance retention and publication boundaries.
