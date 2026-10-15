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
