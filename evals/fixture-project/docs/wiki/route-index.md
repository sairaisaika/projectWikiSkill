# Synthetic interface fixture: engineering routes

Generated positions; source wins over stale prose. Read only the relevant route.

| Task / ID | Current source and role | Local explanation |
| --- | --- | --- |
| public-api: Public article service and legacy client | `src/ports.py:6` (declaration)<br>`src/service.py:4` (implementation)<br>`src/client.py:4` (consumer) | [interfaces.md#public-api](interfaces.md#public-api) |
| external-source: External provider capabilities | `src/provider.ts:2` (declaration)<br>`src/provider.ts:7` (implementation)<br>`src/provider.ts:11` (consumer) | [interfaces.md#external-source](interfaces.md#external-source) |
| tagger: Model suggestion interface | `src/tagging.py:5` (declaration)<br>`src/tagging.py:9` (implementation)<br>`tests/test_contracts.py:31` (consumer) | [interfaces.md#tagger](interfaces.md#tagger) |
| tag-rules: Effective tags and trust policy | `src/tagging.py:16` (declaration)<br>`src/tagging.py:16` (implementation)<br>`src/tagging.py:27` (consumer) | [interfaces.md#tag-rules](interfaces.md#tag-rules) |
