# Synthetic interface fixture: engineering routes

Generated positions; source wins over stale prose. Read only the relevant route.

| Task / ID | Current source and role | Local explanation |
| --- | --- | --- |
| public-api: Public article service and legacy client | `src/ports.py:6` (declaration)<br>`src/service.py:4` (implementation)<br>`src/client.py:4` (consumer) | [interfaces.md#public-api](interfaces.md#public-api) |
| external-source: External provider capabilities | `src/provider.ts:2` (declaration)<br>`src/provider.ts:7` (implementation)<br>`src/provider.ts:11` (consumer) | [interfaces.md#external-source](interfaces.md#external-source) |
| tagger: Model suggestion interface | `src/tagging.py:5` (declaration)<br>`src/tagging.py:9` (implementation)<br>`tests/test_contracts.py:44` (consumer) | [interfaces.md#tagger](interfaces.md#tagger) |
| tag-rules: Effective tags and trust policy | `src/tagging.py:16` (declaration)<br>`src/tagging.py:16` (implementation)<br>`src/tagging.py:27` (consumer) | [interfaces.md#tag-rules](interfaces.md#tag-rules) |
| recovery: Timeout and bounded recovery decisions | `src/recovery.py:23` (implementation)<br>`src/recovery.py:17` (contract)<br>`src/recovery.py:5` (contract)<br>`src/recovery.py:6` (contract)<br>`tests/test_engineering_contracts.py:25` (consumer) | [engineering-contracts.md#recovery](engineering-contracts.md#recovery) |
| wire-format: Heartbeat serializer layout | `src/heartbeat.py:4` (declaration)<br>`src/heartbeat.py:8` (implementation)<br>`src/heartbeat.py:14` (consumer) | [engineering-contracts.md#wire-format](engineering-contracts.md#wire-format) |
| project-views: Fixture architecture and offline deployment | `src/service.py:4` (implementation)<br>`src/ports.py:5` (declaration)<br>`src/client.py:4` (consumer)<br>`src/tagging.py:9` (implementation)<br>`src/tagging.py:27` (implementation)<br>`src/recovery.py:23` (implementation)<br>`src/heartbeat.py:8` (implementation)<br>`tests/test_contracts.py:12` (caller)<br>`tests/test_engineering_contracts.py:11` (caller)<br>`src/provider.ts:2` (contract) | [project-views.md#architecture](project-views.md#architecture)<br>[project-views.md#deployment](project-views.md#deployment) |
